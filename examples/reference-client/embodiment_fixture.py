#!/usr/bin/env python3
"""
ARC embodiment fixture — the custody boundary as a process boundary.

What this is
------------
Every probe before this one asked what the LOG can hold. This one asks where the
KEY lives at runtime. key-custody.md says signing is a capability, not a
possession (D3), and that scope enforcement lives in the signer's trusted base,
with the key, not the agent (D1). canon-ts LOCK A made "a hot key cannot mint
authority beyond its mandate" a compiler fact. compromise_fixture made the
runtime cost visible: if the hot key is RESIDENT in the agent, stealing the agent
steals signing power, bounded only by the mandate scope x detection latency.

This fixture asks the question that leaves open: what if the key is NOT in the
agent — what if it lives behind a separate SIGNER process the agent can only talk
to? The constitution stops being a check and becomes a fact about which process
holds which bytes:

  * the agent holds NO key. It can only PROPOSE. A compromised agent yields
    proposals, never signatures.
  * the signer holds ONLY the hot key. It cannot mint root authority, because the
    cold root key is not in the process — the tier line as a structural ABSENCE,
    not a policy check.
  * escalation (over-ceiling, widening the mandate) cannot be auto-signed. It
    routes to a human approval inbox, where the cold root signs in a separate
    ceremony.

What the runtime split moves, and what it cannot:

  * mandate enforcement moves from FOLD-time to SIGN-time. In compromise_fixture
    the out-of-scope forgeries existed ON the log and every reader's fold rejected
    them (bounded, but present). Here the signer refuses to sign them, so they
    NEVER BECOME EVENTS. The log stays clean of out-of-scope forgeries, and so do
    post-revocation ones: the signer holds the key and stops signing once it
    learns of the withdrawal.
  * the IN-SCOPE window is untouched. The signer auto-signs in-scope proposals
    whoever proposed them — a compromised agent still gets in-scope acts signed,
    byte-indistinguishable from honest ones, exactly as in compromise_fixture.
    finding I survives the split intact: revocation bounds the future, the
    pre-detection in-scope acts stay, and excising only the compromised one still
    needs per-act CHALLENGE + ADJUDICATE — the root disputes, the COMMUNITY
    adjudicator rules (registry §4.5: adjudication's authority source is a
    community process, not an individual key; the disputant does not judge its
    own challenge), and the fold counts only rulings from an adjudicator the
    reader honors.
  * the trusted base shrinks to exactly ONE process — the signer. Its compromise
    is compromise_fixture's world again: key-custody.md §8's open "compromised
    signer," now localized to a single boundary instead of spread across the
    agent.
  * the boundary gains a SECOND seam. reference-client v1 proposed ONE closed
    seam: propose_event(type, payload), agent -> signer. That is enough for
    auto-signed acts. Escalation is not: it needs an approval RETURN path
    (inbox -> a human's signed approval -> the log) the proposal seam never had.

Real Ed25519 (RFC 8032, pure stdlib, reused from compromise_fixture) because the
whole question is whether custody separation is REAL at runtime, and a mock
signature cannot fail to be possessed. Only `signer` holds the agent secret; only
the cold-root ceremony holds the root secret; the agent holds neither. The object
graph IS the boundary.

Refusals (as deliberate as the content):
  * not a daemon, not a wallet, not a security product. "Processes" are objects
    sharing only a serializable seam; there is no network, no persistence, no
    real isolation. The crypto is ILLUSTRATIVE — this probes constitutional
    boundary visibility, not cryptographic assurance.
  * no new event type. A proposal is not an event (it carries no signature and
    never reaches the log unless the signer signs it). Approval is the existing
    consent.approval; revocation is consent.withdraw + nullifies; the dispute is
    CHALLENGE (the disputant) + ADJUDICATE (the community adjudicator).
  * who drives the agent is GROUND TRUTH the generator holds. It is rendered as
    "the omniscient view, available to no observer"; the signer never reads it. A
    valid in-scope proposal is the same object whether the agent or an attacker
    composed it.

A fixture for the viewer; a probe when run directly. Not a custody spec, not
doctrine — the runtime expression of the custody axis canon-ts and
compromise_fixture explored, offered as a probe finding.

Run:  python3 embodiment_fixture.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}


# ===========================================================================
# Real Ed25519 — the RFC 8032 reference, pure stdlib (reused verbatim from
# compromise_fixture.py). A secret signs, a public value verifies, and you cannot
# produce a passing signature without the secret. That is exactly what makes
# "the key is not in this process" mean something.
# ===========================================================================

_b = 256
_q = 2 ** 255 - 19
_l = 2 ** 252 + 27742317777372353535851937790883648493


def _H(m: bytes) -> bytes:
    return hashlib.sha512(m).digest()


def _inv(x: int) -> int:
    return pow(x, _q - 2, _q)


_d = -121665 * _inv(121666) % _q
_I = pow(2, (_q - 1) // 4, _q)


def _xrecover(y: int) -> int:
    xx = (y * y - 1) * _inv(_d * y * y + 1)
    x = pow(xx, (_q + 3) // 8, _q)
    if (x * x - xx) % _q != 0:
        x = (x * _I) % _q
    if x % 2 != 0:
        x = _q - x
    return x


_By = 4 * _inv(5)
_Bx = _xrecover(_By)
_B = [_Bx % _q, _By % _q]


def _edwards(P, Q):
    x1, y1 = P
    x2, y2 = Q
    x3 = (x1 * y2 + x2 * y1) * _inv(1 + _d * x1 * x2 * y1 * y2)
    y3 = (y1 * y2 + x1 * x2) * _inv(1 - _d * x1 * x2 * y1 * y2)
    return [x3 % _q, y3 % _q]


def _scalarmult(P, e):
    if e == 0:
        return [0, 1]
    Q = _scalarmult(P, e // 2)
    Q = _edwards(Q, Q)
    if e & 1:
        Q = _edwards(Q, P)
    return Q


def _bit(h: bytes, i: int) -> int:
    return (h[i // 8] >> (i % 8)) & 1


def _encodeint(y: int) -> bytes:
    return bytes((y >> (8 * i)) & 0xFF for i in range(_b // 8))


def _encodepoint(P) -> bytes:
    x, y = P
    val = (y & ((1 << (_b - 1)) - 1)) | ((x & 1) << (_b - 1))
    return bytes((val >> (8 * i)) & 0xFF for i in range(_b // 8))


def _Hint(m: bytes) -> int:
    h = _H(m)
    return sum(2 ** i * _bit(h, i) for i in range(2 * _b))


def ed25519_publickey(sk: bytes) -> bytes:
    h = _H(sk)
    a = 2 ** (_b - 2) + sum(2 ** i * _bit(h, i) for i in range(3, _b - 2))
    return _encodepoint(_scalarmult(_B, a))


def ed25519_sign(m: bytes, sk: bytes, pk: bytes) -> bytes:
    h = _H(sk)
    a = 2 ** (_b - 2) + sum(2 ** i * _bit(h, i) for i in range(3, _b - 2))
    r = _Hint(h[_b // 8:_b // 4] + m)
    R = _scalarmult(_B, r)
    S = (r + _Hint(_encodepoint(R) + pk + m) * a) % _l
    return _encodepoint(R) + _encodeint(S)


def _decodeint(s: bytes) -> int:
    return sum(2 ** i * _bit(s, i) for i in range(0, _b))


def _isoncurve(P) -> bool:
    x, y = P
    return (-x * x + y * y - 1 - _d * x * x * y * y) % _q == 0


def _decodepoint(s: bytes):
    y = sum(2 ** i * _bit(s, i) for i in range(0, _b - 1))
    x = _xrecover(y)
    if x & 1 != _bit(s, _b - 1):
        x = _q - x
    P = [x, y]
    if not _isoncurve(P):
        raise ValueError("point not on curve")
    return P


def ed25519_verify(sig: bytes, m: bytes, pk: bytes) -> bool:
    if len(sig) != _b // 4 or len(pk) != _b // 8:
        return False
    try:
        R = _decodepoint(sig[0:_b // 8])
        A = _decodepoint(pk)
        S = _decodeint(sig[_b // 8:_b // 4])
    except ValueError:
        return False
    return _scalarmult(_B, S) == _edwards(R, _scalarmult(A, _Hint(_encodepoint(R) + pk + m)))


# ===========================================================================
# The Event — same lean shape as the other probes. An event only exists once it
# is signed; before that it is a Proposal (below), which carries no signature.
# ===========================================================================

@dataclass(frozen=True)
class Event:
    id: str
    type: str
    signer: str                              # public key hex
    predicate: str
    timestamp: str
    refs: tuple[str, ...] = ()
    nullifies: tuple[str, ...] = ()
    scope: dict[str, Any] | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    signature: str = ""

    def signing_bytes(self) -> bytes:
        body = {
            "type": self.type, "signer": self.signer, "predicate": self.predicate,
            "timestamp": self.timestamp, "refs": self.refs, "nullifies": self.nullifies,
            "scope": self.scope, "payload": self.payload,
        }
        return json.dumps(body, sort_keys=True, default=list).encode()


@dataclass(frozen=True)
class Proposal:
    """What the agent emits. NOT an event: no signer, no signature, no id. It is a
    request to the signer to mint an event. The agent holds no key, so this is the
    most it can produce. A compromised agent can produce nothing more."""
    type: str
    predicate: str
    refs: tuple[str, ...] = ()
    scope: dict[str, Any] | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    as_role: str = "agent"                   # whose authority the proposal claims


def verify_log(events: list[Event]) -> None:
    """Verification IS replay: real Ed25519 + signer anchored by a prior KEY
    register. Note what is NOT on this log that was on compromise_fixture's: any
    out-of-scope forgery. The signer refused those before they could be signed, so
    they never became events to verify."""
    registered: set[str] = set()
    for ev in events:
        if not ed25519_verify(bytes.fromhex(ev.signature), ev.signing_bytes(),
                              bytes.fromhex(ev.signer)):
            raise ValueError(f"bad signature on {ev.id}")
        is_reg = ev.type == "KEY" and ev.predicate == "id.key_register"
        if not is_reg and ev.signer not in registered:
            raise ValueError(f"signer not anchored by a KEY register ({ev.id})")
        if is_reg:
            registered.add(ev.payload["key"])


# ===========================================================================
# The processes. The separation is in the object graph: only the signer holds the
# agent secret; only the cold-root ceremony holds the root secret; the agent holds
# neither. Passing the wrong bytes into the wrong object would BREAK the probe —
# which is the point.
# ===========================================================================

@dataclass
class Decision:
    kind: str                                # "signed" | "routed" | "refused"
    reason: str
    event: Event | None = None               # present only when kind == "signed"


class Clock:
    def __init__(self) -> None:
        self._n = 0
        self.revoke_tick = 90                # ticks >= this are "afternoon"

    def now(self) -> str:
        self._n += 1
        hour = 10 if self._n < self.revoke_tick else 16
        return f"2026-06-09T{hour:02d}:{self._n:02d}:00Z"


def _mint(secret: bytes, pub_hex: str, ts: str, *, type_: str, predicate: str,
          **kw) -> Event:
    """Build and sign one event with `secret`, asserting authorship by `pub_hex`.
    The ONLY way an Event comes into being in this fixture."""
    assert type_ in CANONICAL_TYPES, f"non-canonical type {type_!r}"
    partial = Event(id="", type=type_, signer=pub_hex, predicate=predicate,
                    timestamp=ts, **kw)
    body = partial.signing_bytes()
    sig = ed25519_sign(body, secret, bytes.fromhex(pub_hex)).hex()
    return Event(id="ev:" + hashlib.sha256(body).hexdigest()[:12], type=type_,
                 signer=pub_hex, predicate=predicate, timestamp=ts, signature=sig, **kw)


class SignerProcess:
    """Holds the HOT key and a copy of the mandate (its trusted base). Receives a
    Proposal, decides in its OWN process whether to sign it, and signs only what
    the mandate covers. It does not hold the cold root key, so it physically
    cannot mint root authority — refusal there is an absence, not a check."""

    def __init__(self, *, hot_pub: str, hot_secret: bytes, mandate: Event,
                 clock: Clock, log: list[Event]) -> None:
        self._hot_secret = hot_secret        # the ONE secret this process holds
        self.hot_pub = hot_pub
        self.mandate = mandate
        self.clock = clock
        self.log = log
        self.known_withdrawals: set[str] = set()   # mandate ids the root has revoked

    @property
    def _ceiling(self) -> int:
        return (self.mandate.scope or {}).get("max_total_krw")

    @property
    def _context(self) -> str:
        return (self.mandate.scope or {}).get("context")

    def learn_withdrawal(self, mandate_id: str) -> None:
        """Control-plane delivery: the cold root signed a withdrawal and it reached
        the signer. From here the signer stops signing under that mandate — sign-
        time time-scoping, the live counterpart of the fold's time_scoped read."""
        self.known_withdrawals.add(mandate_id)

    def handle(self, p: Proposal, *, approval: Event | None = None) -> Decision:
        """The trusted base, exercised. `approval` is an optional cold-root
        consent.approval delivered from the inbox; it rides above the mandate
        ceiling exactly as in compromise_fixture's fold."""
        # Structural: the signer can only sign as the key it holds. A proposal
        # claiming the root's authority cannot be signed here at all — the cold
        # key is not in this process. This is the tier line, embodied.
        if p.as_role != "agent":
            return Decision("refused", f"this process holds only the hot key; it "
                            f"cannot sign as '{p.as_role}' (the cold key is not here)")

        ctx = p.payload.get("context") or (p.scope or {}).get("context")
        amount = p.payload.get("amount_krw")

        # A delivered root approval rides above the mandate — the human already said
        # yes, off the hot key's authority.
        if approval is not None:
            cap = (approval.scope or {}).get("max_total_krw")
            if amount is None or cap is None or amount <= cap:
                ev = self._sign(p, refs=tuple(p.refs) + (approval.id,))
                return Decision("signed", "signed under an explicit cold-root approval "
                                "(above the mandate ceiling)", ev)
            return Decision("refused", "the root approval does not cover this amount")

        # Sign-time time-scoping: a withdrawn mandate stops the signer.
        if self.mandate.id in self.known_withdrawals:
            return Decision("refused", "the mandate was withdrawn — the signer no longer "
                            "signs under it (the key still works; the trusted base refuses)")

        # Out of the mandate's domain: not the hot key's authority. The signer will
        # not sign and does not pretend a human at this signer could grant it.
        if self._context is not None and ctx is not None and ctx != self._context:
            return Decision("refused", f"out of mandate domain ({ctx} != {self._context}) — "
                            "not the hot key's authority")

        # Widening the mandate needs the root; the hot key cannot grant it. This is
        # legitimate to ASK, so it routes to the human, not refused.
        if p.type == "AUTHORIZE":
            return Decision("routed", "widening or delegating the mandate needs the root "
                            "— routed to the approval inbox (the hot key cannot self-elevate)")

        # Over the ceiling: legitimate to ask, beyond the hot key's authority.
        if amount is not None and self._ceiling is not None and amount > self._ceiling:
            return Decision("routed", f"over the mandate ceiling ({amount} > {self._ceiling}) "
                            "— routed to the approval inbox for a human")

        # Within the live mandate: auto-signed, no human in the loop.
        ev = self._sign(p)
        return Decision("signed", "within the live mandate (right domain, within ceiling)", ev)

    def _sign(self, p: Proposal, *, refs: tuple[str, ...] | None = None) -> Event:
        ev = _mint(self._hot_secret, self.hot_pub, self.clock.now(), type_=p.type,
                   predicate=p.predicate, refs=refs if refs is not None else tuple(p.refs),
                   scope=p.scope, payload=p.payload)
        self.log.append(ev)
        return ev


class ApprovalInbox:
    """Where routed proposals wait for a human. The SECOND seam: the proposal seam
    carried agent -> signer; this carries signer -> human -> back to a signed
    event. It exists only because escalation does."""

    def __init__(self) -> None:
        self.pending: list[Proposal] = []

    def receive(self, p: Proposal) -> None:
        self.pending.append(p)


class AgentProcess:
    """Proposes events. Holds NO key — there is no signing method here to call.
    Whoever drives it (the honest operator or an attacker who has taken the
    process over) can do exactly one thing: emit a Proposal."""

    def __init__(self, *, signer: SignerProcess, inbox: ApprovalInbox) -> None:
        self._signer = signer
        self._inbox = inbox

    def propose(self, p: Proposal, *, approval: Event | None = None) -> Decision:
        d = self._signer.handle(p, approval=approval)
        if d.kind == "routed":
            self._inbox.receive(p)
        return d


class ColdRootCeremony:
    """The human with the cold key. NOT resident in the agent or the signer — it
    is invoked for the rare ceremonial acts (mandate, approval, withdrawal,
    dispute) and otherwise absent. Modeled as a separate object holding the only
    copy of the root secret. It DISPUTES; it does not rule — adjudication
    belongs to the community (registry §4.5), never to the disputant."""

    def __init__(self, *, root_pub: str, root_secret: bytes, clock: Clock,
                 log: list[Event]) -> None:
        self._root_secret = root_secret
        self.root_pub = root_pub
        self.clock = clock
        self.log = log

    def _emit(self, **kw) -> Event:
        ev = _mint(self._root_secret, self.root_pub, self.clock.now(), **kw)
        self.log.append(ev)
        return ev

    def register(self, pub: str) -> Event:
        return self._emit(type_="KEY", predicate="id.key_register", payload={"key": pub})

    def grant_mandate(self, agent_pub: str, *, context: str, ceiling: int) -> Event:
        return self._emit(type_="AUTHORIZE", predicate="consent.mandate",
                          refs=(agent_pub,), scope={"context": context, "max_total_krw": ceiling})

    def approve(self, amount: int, context: str) -> Event:
        return self._emit(type_="AUTHORIZE", predicate="consent.approval",
                          scope={"context": context, "max_total_krw": amount})

    def withdraw(self, mandate_id: str, agent_pub: str) -> Event:
        return self._emit(type_="AUTHORIZE", predicate="consent.withdraw",
                          refs=(agent_pub,), nullifies=(mandate_id,),
                          payload={"reason": "key_compromise"})

    def dispute(self, event_id: str) -> Event:
        return self._emit(type_="CHALLENGE", predicate="dispute.open", refs=(event_id,),
                          payload={"reason": "not_authorized_by_holder"})


class CommunityAdjudicator:
    """The commons authority — the market community's adjudicating key, held by
    its own process (registry §4.5: ADJUDICATE's authority source is a community
    process, not an individual key). It rules on disputed acts; it grants
    nothing and spends nothing. The disputant (the root) is a different key: a
    party does not judge its own challenge."""

    def __init__(self, *, pub: str, secret: bytes, clock: Clock,
                 log: list[Event]) -> None:
        self._secret = secret
        self.pub = pub
        self.clock = clock
        self.log = log

    def rule_void(self, event_id: str) -> Event:
        ev = _mint(self._secret, self.pub, self.clock.now(), type_="ADJUDICATE",
                   predicate="gov.ruling", refs=(event_id,),
                   payload={"ruling": "void", "context": "market"})
        self.log.append(ev)
        return ev


# ===========================================================================
# A light fold — only to show that what reached the log is honored, and that the
# in-scope compromised act still needs adjudication to excise. Nothing here reads
# ground truth.
# ===========================================================================

def honored_from_root(events: list[Event], *, root: str, agent: str,
                      honored_adjudicators: tuple[str, ...] = ()) -> dict:
    """Fold the log into per-act honoring from `root`, time-scoped. Because the
    signer already enforced scope at sign-time, almost everything on the log is in
    bounds; the one thing the fold still decides is whether a per-act ADJUDICATE
    from an adjudicator this reader HONORS has voided a specific event.
    `honored_adjudicators` is the reader's policy choice (A&C §9); an ADJUDICATE
    from anyone else — the disputant included — is evidence, not authority."""
    by_id = {e.id: e for e in events}
    mandate = next((e for e in events if e.type == "AUTHORIZE"
                    and e.predicate == "consent.mandate" and e.signer == root), None)
    revoke = next((e for e in events if e.type == "AUTHORIZE"
                   and e.predicate == "consent.withdraw" and e.signer == root), None)
    voided = {e.refs[0] for e in events if e.type == "ADJUDICATE"
              and e.payload.get("ruling") == "void" and e.refs
              and e.signer in honored_adjudicators}
    ceiling = (mandate.scope or {}).get("max_total_krw") if mandate else None
    mctx = (mandate.scope or {}).get("context") if mandate else None

    def honor(ev: Event) -> dict:
        if ev.id in voided:
            return {"honored": False, "basis": "adjudicated void — an honored ADJUDICATE "
                    "ruled on this specific event (authority layer)"}
        if ev.signer == root:
            return {"honored": True, "basis": "the root's own act"}
        appr = next((by_id[r] for r in ev.refs if r in by_id
                     and by_id[r].predicate == "consent.approval" and by_id[r].signer == root), None)
        if appr is not None:
            return {"honored": True, "basis": "rode an explicit cold-root approval"}
        amount = ev.payload.get("amount_krw")
        ctx = ev.payload.get("context") or (ev.scope or {}).get("context")
        if mctx is not None and ctx is not None and ctx != mctx:
            return {"honored": False, "basis": "out of mandate domain"}
        if amount is not None and ceiling is not None and amount > ceiling:
            return {"honored": False, "basis": "over the mandate ceiling"}
        if revoke is not None and ev.timestamp >= revoke.timestamp:
            return {"honored": False, "basis": "after the withdrawal (time-scoped)"}
        return {"honored": True, "basis": "within the live mandate"}

    rows = []
    for e in events:
        if e.signer == agent and e.type in ("ATTEST", "AUTHORIZE"):
            rows.append({"id": e.id, "predicate": e.predicate,
                         "amount": e.payload.get("amount_krw"), **honor(e)})
    return {"ceiling": ceiling, "context": mctx, "rows": rows}


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


def show(label: str, d: Decision, *, attacker: bool = False) -> None:
    glyph = {"signed": "SIGNED ", "routed": "ROUTED ", "refused": "REFUSED"}[d.kind]
    tag = "  <-- attacker drove the agent" if attacker else ""
    eid = f"  [{d.event.id}]" if d.event else ""
    print(f"    {glyph}  {label:<34} {d.reason}{eid}{tag}")


# ===========================================================================
# The generated flow — run once, top to bottom.
# ===========================================================================

def generate() -> dict:
    clock = Clock()
    log: list[Event] = []

    # Keys are generated here, then handed to processes SEPARATELY. After this
    # block, no single object holds more than its share. The attacker, later,
    # takes over the agent — which holds nothing.
    def keypair(name: str) -> tuple[bytes, str]:
        sk = hashlib.sha256(b"arc-embodiment/" + name.encode()).digest()
        return sk, ed25519_publickey(sk).hex()

    root_secret, root_pub = keypair("root")
    agent_secret, agent_pub = keypair("agent")
    community_secret, community_pub = keypair("community")

    print("\n1. OFFLINE CEREMONY — the cold root anchors keys and grants a mandate,")
    print("   then goes away. From here the cold key is NOT in any running process.")
    ceremony = ColdRootCeremony(root_pub=root_pub, root_secret=root_secret,
                                clock=clock, log=log)
    ceremony.register(root_pub)
    ceremony.register(agent_pub)
    mandate = ceremony.grant_mandate(agent_pub, context="market", ceiling=30000)
    say("custody", "root key = COLD (held only by the ceremony); agent has NO key")
    say("custody", f"mandate: hot key may sign 'market' acts up to 30000  [{mandate.id}]")

    print("\n2. BOOT — the signer holds the hot key + the mandate; the agent holds")
    print("   only a line to the signer. There is no signing method on the agent.")
    inbox = ApprovalInbox()
    signer = SignerProcess(hot_pub=agent_pub, hot_secret=agent_secret, mandate=mandate,
                           clock=clock, log=log)
    agent = AgentProcess(signer=signer, inbox=inbox)

    def market_payment(amount: int, context: str = "market") -> Proposal:
        return Proposal(type="ATTEST", predicate="commerce.payment_result", refs=(mandate.id,),
                        payload={"result": "confirmed", "amount_krw": amount,
                                 "context": context, "provider": "mock_pay"})

    print("\n3. HONEST OPERATION — the operator drives the agent")
    show("in-scope payment 20000", agent.propose(market_payment(20000)))

    over = market_payment(90000)
    show("over-ceiling payment 90000", agent.propose(over))
    say("inbox", "the over-ceiling proposal is waiting for a human")
    say("human", "reviews it, recognizes it, and approves with the COLD key")
    approval = ceremony.approve(90000, "market")
    show("  (re-submitted with approval)", agent.propose(over, approval=approval))

    widen = Proposal(type="AUTHORIZE", predicate="consent.mandate", refs=(agent_pub,),
                     scope={"context": "market", "max_total_krw": 100000})
    show("agent asks to widen its mandate", agent.propose(widen))
    say("human", "reviews the widening request at the inbox and REJECTS it")
    say("inbox", "rejected — an agent does not get to grant itself more authority")

    print("\n4. THE AGENT IS COMPROMISED — an attacker takes over the agent process.")
    print("   It gained a PROPOSER, not a key. Watch where each forgery attempt dies.")
    comp = market_payment(25000)
    d_inscope = agent.propose(comp)
    show("in-scope forgery 25000", d_inscope, attacker=True)
    show("over-ceiling forgery 90000", agent.propose(market_payment(90000)), attacker=True)
    show("out-of-context forgery", agent.propose(
        Proposal(type="ATTEST", predicate="identity.binding", refs=(mandate.id,),
                 payload={"claim": "controls_external_account", "context": "identity"})),
        attacker=True)
    show("self-mint as root", agent.propose(
        Proposal(type="AUTHORIZE", predicate="consent.mandate", as_role="root",
                 refs=(agent_pub,), scope={"context": "market", "max_total_krw": 1000000})),
        attacker=True)
    say("omniscient", "only the IN-SCOPE forgery (25000) reached the log; the other three")
    say("omniscient", "never became events — the signer refused them BEFORE signing")

    print("\n5. DETECTION + REVOCATION — the cold root withdraws; the signer learns it")
    revoke = ceremony.withdraw(mandate.id, agent_pub)
    signer.learn_withdrawal(mandate.id)
    say("root", f"withdrawal signed from the cold ceremony  [{revoke.id}]")
    show("post-revoke forgery 25000", agent.propose(market_payment(25000)), attacker=True)
    say("omniscient", "refused at SIGN-TIME — the signer holds the key and stopped. In")
    say("omniscient", "compromise_fixture the thief HELD the key and this one got signed.")

    print("\n6. THE RESIDUE REVOCATION COULD NOT REACH — the in-scope 25000 is on the")
    print("   log, honored, byte-indistinguishable from honest acts. Per-act dispute:")
    print("   the dispute routes to the commons — the community's key anchors, the")
    print("   root disputes, and the COMMUNITY rules (registry §4.5: not the disputant).")
    ceremony.register(community_pub)
    community = CommunityAdjudicator(pub=community_pub, secret=community_secret,
                                     clock=clock, log=log)
    ch = ceremony.dispute(d_inscope.event.id)
    ruling = community.rule_void(d_inscope.event.id)
    say("root", f"CHALLENGE [{ch.id}] filed on that ONE event — the disputant's move")
    say("community", f"ADJUDICATE void [{ruling.id}] — the commons' ruling, not the root's")

    verify_log(log)
    return {"log": log, "root": root_pub, "agent": agent_pub,
            "community": community_pub,
            "inscope_id": d_inscope.event.id, "mandate_id": mandate.id}


# ===========================================================================
# Standalone run — narrate the flow, then state what the runtime split moved.
# ===========================================================================

def main() -> None:
    ctx = generate()
    log, root, agent = ctx["log"], ctx["root"], ctx["agent"]
    inscope_id = ctx["inscope_id"]

    print("\n" + "=" * 72)
    print("WHAT ACTUALLY REACHED THE LOG — every event here has a valid signature")
    print("and is in bounds, because the signer enforced scope BEFORE signing.")
    print("=" * 72)
    proj = honored_from_root(log, root=root, agent=agent,
                             honored_adjudicators=(ctx["community"],))
    print(f"\n  mandate: {proj['context']} <= {proj['ceiling']}")
    for r in proj["rows"]:
        amt = f"{r['amount']} KRW" if r["amount"] else "-"
        verdict = "HONORED" if r["honored"] else "voided "
        print(f"    {verdict}  {r['predicate']:<26} {amt:>11} [{r['id']}] — {r['basis']}")

    print("\n" + "=" * 72)
    print("THE FINDING — a scope-enforcing signer moves enforcement to SIGN-TIME")
    print("=" * 72)
    print("""
  Compare the log to compromise_fixture's. There, the hot key was RESIDENT in the
  agent; the thief stole it and signed four forgeries — over-ceiling, out-of-
  context, self-elevation — that all LANDED on the log and were rejected only
  later, by every reader's fold. Here the key lives behind a separate signer, and
  the agent — compromised or not — can only PROPOSE. Three of the four forgeries
  never became events at all:

    * over-ceiling 90000   -> ROUTED, not signed   (a human would have to approve)
    * out-of-context       -> REFUSED              (not the hot key's domain)
    * self-mint as root    -> REFUSED              (the cold key is not in the process)
    * post-revoke 25000    -> REFUSED              (the signer stopped at sign-time)

  Enforcement moved from fold-time to sign-time. The log never holds the out-of-
  scope forgeries, so no reader has to reject them. The tier line — a hot key
  cannot mint root authority — is now a structural ABSENCE (the cold key is not
  there to sign with), not a rule the fold applies after the fact.

  But the IN-SCOPE window is untouched. The signer auto-signs in-scope proposals
  whoever composed them, so the attacker's 25000 was signed exactly like the
  honest 20000 — finding I, intact at runtime. Revocation bounds the future; the
  acts signed before detection stay; excising only the compromised one still needs
  the human to supply, off the log, the one fact it never held (the root's
  CHALLENGE + the community adjudicator's ADJUDICATE void — the disputant does
  not judge its own challenge, and the fold counts only rulings from an
  adjudicator the reader honors). The runtime split cleans up the out-of-scope
  blast radius; it cannot shrink the in-scope one.

  Two residues the split surfaces:

    * the trusted base is now exactly ONE process — the signer. Compromise it and
      you are back in compromise_fixture's world. key-custody.md §8's open
      "compromised signer" is not answered here; it is LOCALIZED — narrowed from
      "wherever the agent ran" to a single boundary.
    * the boundary needed a SECOND seam. reference-client v1's one closed verb,
      propose_event, carried agent -> signer and was enough for auto-signed acts.
      Escalation forced an approval RETURN path (inbox -> a cold-root approval ->
      the log). The proposal seam alone cannot express "a human said yes."

  Offered as a probe finding — the runtime expression of canon-ts LOCK A and
  compromise_fixture's custody work, not settled doctrine. The crypto is real so
  that "the key is not in this process" is a fact, not a claim; it is not a
  security product.
""")


if __name__ == "__main__":
    main()

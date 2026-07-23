#!/usr/bin/env python3
"""
ARC embodiment fixture — signer and agent as separate fixture objects.

What this is
------------
Earlier fixtures focused on records and folds. This one models where signing key
bytes reside at runtime. The agent and signer are separate Python objects: the
agent constructs proposals, while the signer holds the hot key and applies this
fixture's mandate checks.

The object split produces these authored fixture behaviors:

  * the agent object holds no key and submits proposals to the signer object;
  * the signer object holds the hot key but not the root key, so it cannot
    produce a root-signed Event through its signing method;
  * escalation (over-ceiling, widening the mandate) is routed to an approval
    inbox; the scripted cold-root ceremony can emit a separate approval record.

What this fixture compares:

  * mandate checks run at sign time. In compromise_fixture
    attacker-authored records are evaluated by a fold. Here the signer does not
    sign the authored out-of-scope proposals; they are routed or refused and are
    not appended as Events. Post-withdrawal proposals are also refused after
    the signer receives the withdrawal.
  * the signer auto-signs the authored in-scope proposals
    regardless of who composed them, so attacker-authored and operator-authored
    proposals can receive the same signer and fold treatment.
    Under this fixture policy, revocation bounds later signer decisions while
    pre-detection in-scope records remain in the log. The fixture later adds a
    CHALLENGE and an ADJUDICATE for one record and counts rulings only from its
    configured adjudicator set.
  * scope enforcement is localized in the signer object, while custody, process
    isolation, persistence, review, and deployment dependencies remain outside
    this fixture. Signer compromise remains open.
  * escalation adds an approval return path from the inbox and scripted cold-root
    ceremony back to the signer.

Illustrative Ed25519 (RFC 8032, pure stdlib, reused from compromise_fixture) is
used for the named record checks. Only `signer` holds the agent secret in this
object graph; the fixture provides no real process isolation or custody proof.

Limits:
  * the "processes" are objects sharing serializable data; there is no network,
    persistence, or process isolation. The Ed25519 implementation is illustrative.
  * no new event type. A proposal is not an event (it carries no signature and
    never reaches the log unless the signer signs it). Approval is the existing
    consent.approval; revocation is consent.withdraw + nullifies; the dispute is
    CHALLENGE (the disputant) + ADJUDICATE (the community adjudicator).
  * who drives the agent is a private fixture stipulation rendered separately;
    the signer never reads it. A
    signer evaluates proposal fields rather than this private author label.

A fixture for the viewer; a probe when run directly. It is not a custody
specification.

Run:  python3 embodiment_fixture.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}


# ===========================================================================
# Illustrative Ed25519 — the RFC 8032 reference, pure stdlib (reused from
# compromise_fixture.py). This is not a production cryptographic profile.
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
    """What the fixture agent emits. This is not an Event: it has no signer,
    signature, or id. The fixture passes it to the signer object for evaluation."""
    type: str
    predicate: str
    refs: tuple[str, ...] = ()
    scope: dict[str, Any] | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    as_role: str = "agent"                   # whose authority the proposal claims


def verify_log(events: list[Event]) -> None:
    """Fixture replay check: Ed25519 signature and prior KEY registration only.
    It cannot establish custody, process isolation, authorship, or conformance."""
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
# The processes. The separation is in the object graph: only the signer object
# holds the agent secret; only the cold-root ceremony object holds the root secret;
# the agent object holds neither.
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
    """Build an Event with `pub_hex` in the signer field and sign it with `secret`."""
    assert type_ in CANONICAL_TYPES, f"non-canonical type {type_!r}"
    partial = Event(id="", type=type_, signer=pub_hex, predicate=predicate,
                    timestamp=ts, **kw)
    body = partial.signing_bytes()
    sig = ed25519_sign(body, secret, bytes.fromhex(pub_hex)).hex()
    return Event(id="ev:" + hashlib.sha256(body).hexdigest()[:12], type=type_,
                 signer=pub_hex, predicate=predicate, timestamp=ts, signature=sig, **kw)


class SignerProcess:
    """Holds the hot key and a copy of the mandate. It applies this fixture's
    proposal checks and optional approval branch. It does not hold the root key
    and cannot produce a root-signed Event through this object."""

    def __init__(self, *, hot_pub: str, hot_secret: bytes, mandate: Event,
                 clock: Clock, log: list[Event]) -> None:
        self._hot_secret = hot_secret        # the secret held by this fixture signer
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
        """Apply this fixture's signer checks. `approval` is an optional cold-root
        consent.approval delivered from the inbox; this fixture permits it above
        the mandate ceiling."""
        # The signer can produce Events only with its hot key. The authored
        # root-role proposal is therefore refused here.
        if p.as_role != "agent":
            return Decision("refused", f"this process holds only the hot key; it "
                            f"cannot sign as '{p.as_role}' (the cold key is not here)")

        ctx = p.payload.get("context") or (p.scope or {}).get("context")
        amount = p.payload.get("amount_krw")

        # This older fixture treats the directly supplied ceremony approval as
        # separate authority above the hot-key mandate. It does not authenticate a
        # carried approval; approval_seam_fixture.py tests those additional checks.
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
                            "signs under it (the key still works; this signer refuses)")

        # Out of the mandate's domain: not the hot key's authority. The signer will
        # not sign and does not treat the hot key as cold-root authority.
        if self._context is not None and ctx is not None and ctx != self._context:
            return Decision("refused", f"out of mandate domain ({ctx} != {self._context}) — "
                            "not the hot key's authority")

        # Widening the mandate needs the root; the hot key cannot grant it. This is
        # configured to route to the approval inbox rather than refuse.
        if p.type == "AUTHORIZE":
            return Decision("routed", "widening or delegating the mandate needs the root "
                            "— routed to the approval inbox (the hot key cannot self-elevate)")

        # Over the ceiling: configured to route, beyond the hot key's mandate.
        if amount is not None and self._ceiling is not None and amount > self._ceiling:
            return Decision("routed", f"over the mandate ceiling ({amount} > {self._ceiling}) "
                            "— routed to the approval inbox")

        # Within the live mandate: signed without another approval record.
        ev = self._sign(p)
        return Decision("signed", "within the live mandate (right domain, within ceiling)", ev)

    def _sign(self, p: Proposal, *, refs: tuple[str, ...] | None = None) -> Event:
        ev = _mint(self._hot_secret, self.hot_pub, self.clock.now(), type_=p.type,
                   predicate=p.predicate, refs=refs if refs is not None else tuple(p.refs),
                   scope=p.scope, payload=p.payload)
        self.log.append(ev)
        return ev


class ApprovalInbox:
    """Where routed proposals wait for the scripted cold-root ceremony."""

    def __init__(self) -> None:
        self.pending: list[Proposal] = []

    def receive(self, p: Proposal) -> None:
        self.pending.append(p)


class AgentProcess:
    """Proposes Events and exposes no signing method. The configured operator or
    attacker label can submit a Proposal to the signer object."""

    def __init__(self, *, signer: SignerProcess, inbox: ApprovalInbox) -> None:
        self._signer = signer
        self._inbox = inbox

    def propose(self, p: Proposal, *, approval: Event | None = None) -> Decision:
        d = self._signer.handle(p, approval=approval)
        if d.kind == "routed":
            self._inbox.receive(p)
        return d


class ColdRootCeremony:
    """Scripted holder of the cold key. It is not resident in the agent or signer
    and is invoked for mandate, approval, withdrawal, and challenge records. It
    is a separate object in this fixture, not a process-isolation guarantee. The
    configured community adjudicator emits the ruling counted by the fold."""

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
    """The adjudicator key configured for this fixture. The fold counts rulings
    from this key and does not count the disputant root's self-ruling. This is a
    fixture-policy choice, not a base-protocol authority rule."""

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
# private fixture stipulations.
# ===========================================================================

def honored_from_root(events: list[Event], *, root: str, agent: str,
                      honored_adjudicators: tuple[str, ...] = ()) -> dict:
    """Fold the log into per-act honoring from `root`, time-scoped. Because the
    signer already enforced scope at sign-time, almost everything on the log is in
    bounds. The fold also checks whether a per-act ADJUDICATE from an adjudicator
    configured for this reader has voided a specific event.
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

    # Keys are generated here, then passed to separate fixture objects. The
    # attacker label is later assigned to proposals submitted through the agent.
    def keypair(name: str) -> tuple[bytes, str]:
        sk = hashlib.sha256(b"arc-embodiment/" + name.encode()).digest()
        return sk, ed25519_publickey(sk).hex()

    root_secret, root_pub = keypair("root")
    agent_secret, agent_pub = keypair("agent")
    community_secret, community_pub = keypair("community")

    print("\n1. Offline ceremony — the cold root anchors keys and grants a mandate.")
    print("   The root secret remains in the ceremony object and is not passed to the agent or signer.")
    ceremony = ColdRootCeremony(root_pub=root_pub, root_secret=root_secret,
                                clock=clock, log=log)
    ceremony.register(root_pub)
    ceremony.register(agent_pub)
    mandate = ceremony.grant_mandate(agent_pub, context="market", ceiling=30000)
    say("custody", "root secret is held by the ceremony object; the agent object has no key")
    say("custody", f"mandate: hot key may sign 'market' acts up to 30000  [{mandate.id}]")

    print("\n2. Signer setup — the signer holds the hot key + the mandate; the agent holds")
    print("   only a line to the signer. There is no signing method on the agent.")
    inbox = ApprovalInbox()
    signer = SignerProcess(hot_pub=agent_pub, hot_secret=agent_secret, mandate=mandate,
                           clock=clock, log=log)
    agent = AgentProcess(signer=signer, inbox=inbox)

    def market_payment(amount: int, context: str = "market") -> Proposal:
        return Proposal(type="ATTEST", predicate="commerce.payment_result", refs=(mandate.id,),
                        payload={"result": "confirmed", "amount_krw": amount,
                                 "context": context, "provider": "mock_pay"})

    print("\n3. Configured operator proposals")
    show("in-scope payment 20000", agent.propose(market_payment(20000)))

    over = market_payment(90000)
    show("over-ceiling payment 90000", agent.propose(over))
    say("inbox", "the over-ceiling proposal is waiting for the scripted ceremony")
    say("ceremony", "emits a cold-root approval for the configured amount and context")
    approval = ceremony.approve(90000, "market")
    show("  (re-submitted with approval)", agent.propose(over, approval=approval))

    widen = Proposal(type="AUTHORIZE", predicate="consent.mandate", refs=(agent_pub,),
                     scope={"context": "market", "max_total_krw": 100000})
    show("agent asks to widen its mandate", agent.propose(widen))
    say("ceremony", "the scripted widening path records no approval")
    say("inbox", "the widening proposal remains routed; no approval is issued")

    print("\n4. Private fixture stipulation — the attacker label submits proposals")
    comp = market_payment(25000)
    d_inscope = agent.propose(comp)
    show("in-scope attacker proposal 25000", d_inscope, attacker=True)
    show("over-ceiling attacker proposal 90000", agent.propose(market_payment(90000)), attacker=True)
    show("out-of-context attacker proposal", agent.propose(
        Proposal(type="ATTEST", predicate="identity.binding", refs=(mandate.id,),
                 payload={"claim": "controls_external_account", "context": "identity"})),
        attacker=True)
    show("self-mint as root", agent.propose(
        Proposal(type="AUTHORIZE", predicate="consent.mandate", as_role="root",
                 refs=(agent_pub,), scope={"context": "market", "max_total_krw": 1000000})),
        attacker=True)
    say("generator", "only the in-scope attacker-authored proposal (25000) reached the log;")
    say("generator", "the signer refused the other three before signing")

    print("\n5. Detection and revocation — the cold root withdraws; the signer learns it")
    revoke = ceremony.withdraw(mandate.id, agent_pub)
    signer.learn_withdrawal(mandate.id)
    say("root", f"withdrawal signed from the cold ceremony  [{revoke.id}]")
    show("post-withdrawal attacker proposal 25000", agent.propose(market_payment(25000)), attacker=True)
    say("generator", "refused at sign time after the signer received the withdrawal;")
    say("generator", "the compromise fixture instead stipulates loss of the key bytes")

    print("\n6. Pre-withdrawal in-scope record — the 25000 record is on the")
    print("   log and honored under this fold like an operator-authored in-scope act.")
    print("   the root emits a CHALLENGE and the configured community adjudicator")
    print("   emits ADJUDICATE; this fixture policy does not count the disputant's self-ruling.")
    ceremony.register(community_pub)
    community = CommunityAdjudicator(pub=community_pub, secret=community_secret,
                                     clock=clock, log=log)
    ch = ceremony.dispute(d_inscope.event.id)
    ruling = community.rule_void(d_inscope.event.id)
    say("root", f"CHALLENGE [{ch.id}] targets the attacker-authored Event")
    say("community", f"ADJUDICATE void [{ruling.id}] is counted by this fold")

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
    print("Records appended to the log — every record passes the illustrative signature check")
    print("and the signer-side checks named by this fixture.")
    print("=" * 72)
    proj = honored_from_root(log, root=root, agent=agent,
                             honored_adjudicators=(ctx["community"],))
    print(f"\n  mandate: {proj['context']} <= {proj['ceiling']}")
    for r in proj["rows"]:
        amt = f"{r['amount']} KRW" if r["amount"] else "-"
        verdict = "HONORED" if r["honored"] else "voided "
        print(f"    {verdict}  {r['predicate']:<26} {amt:>11} [{r['id']}] — {r['basis']}")

    print("\n" + "=" * 72)
    print("Fixture result — signer-side mandate checks run before Event creation")
    print("=" * 72)
    print("""
  In compromise_fixture, the generator stipulates loss of the hot-key bytes, so
  attacker-authored records can pass its signature check and are evaluated by a
  fold. Here only the signer object holds the hot-key bytes. The agent can propose,
  and the signer produces these configured outcomes:

    * over-ceiling 90000   -> ROUTED, not signed   (cold-root approval path)
    * out-of-context       -> REFUSED              (not the hot key's domain)
    * self-mint as root    -> REFUSED              (the signer object lacks the root key)
    * post-revoke 25000    -> REFUSED              (the signer stopped at sign-time)

  The refused proposals are not appended as Events. The self-mint proposal also
  cannot be signed as the cold root because that key is absent from the signer
  object.

  For the authored in-scope cases, the signer applies the same checks without
  reading the private author label. The attacker-authored 25000 therefore receives
  the same signer and fold treatment as the configured operator's 20000 here.
  Withdrawal bounds later signer decisions; the
  acts signed before detection stay. This fixture distinguishes one record only
  after adding a root CHALLENGE and a community adjudicator's ADJUDICATE void.
  This fold does not count the disputant's self-ruling and counts only rulings
  from an adjudicator configured for the reader. In the authored cases, the signer refuses the
  out-of-scope attacker proposals but signs the in-scope proposal.

  Two limitations remain:

    * scope enforcement is localized in the signer object; broader custody and
      deployment dependencies remain outside this fixture. Compromised-signer
      behavior is not answered here.
    * escalation uses a separate approval return path (inbox -> scripted
      cold-root approval -> signer). The proposal path alone does not provide that
      approval record.

  The Ed25519 implementation and object boundaries are illustrative. This fixture
  does not establish process isolation, custody assurance, or deployment security.
""")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
ARC approval-return fixture — proposal-bound approvals and a scope-only counterfactual.

What this is
------------
embodiment_fixture.py split the agent from the signer and routed over-ceiling
proposals to an inbox. This fixture adds a simulated cold-root ceremony and an
approval return path from the inbox back to the signer.

  * embodiment_fixture's approval was a scope token: consent.approval scoped by
    {context, max_total_krw}. The signer's approval branch checked only
    `amount <= cap`. Nothing bound it to one reviewed proposal.
  * So a scope-token approval acts as a bearer token. A compromised agent, handed an
    approval for "a 90000 market payment", could bind it to a different 90000
    market payment or reuse it.

Comparison and limitations:

  * bind the approval to the proposal's reviewable fields. The signer adds
    envelope fields such as signer and timestamp, so the review and Event signing
    byte domains are not identical. The in-process consumed set makes the tested
    approval single-use only for this fixture run.
  * the signer checks the approval's own illustrative Ed25519 signature, that its signer is the
    mandate's granter (the cold root), and that it is on the log — an approval
    is a record in this fixture, not a transport message. A self-constructed approval object naming the
    right hash, or an approval that was not appended to the fixture log, is
    refused before its binding is read.
  * the approval is a separately signed record. The fixture cannot establish what
    a person saw or understood; it checks only the reviewable-field binding named
    above.

The fixture compares the proposal-bound signer with a scope-only counterfactual.
It does not establish what a person saw, understood, or intended.

Illustrative Ed25519 (RFC 8032, pure stdlib, reused from the prior fixtures) is
used for the named record checks. Only the cold-root ceremony
holds the root secret; only the signer holds the hot secret; the agent holds
neither. The signer refuses the invalid-signature and re-aim cases described below.

Limits:
  * the "processes" are objects sharing serializable data; there is no network,
    persistence, or process isolation. The Ed25519 implementation is illustrative.
  * no new event type. The approval is the existing consent.approval; the binding
    rides in its refs (the proposal hash) — evidence the canon already holds, used
    as a proposal binding. The replay defense is consumption tracked in the
    signer object's in-memory state, not a new primitive.
  * the counterfactual is computed by the fixture. The fixture carries a
    `scope_only_would_sign` that replays embodiment_fixture's amount-only check, so
    "a bearer token would have signed this" is shown by running it, not claimed.
  * who drives the agent is a private fixture stipulation rendered separately;
    the signer and approval ceremony never read it.

A fixture for the viewer and a standalone probe, not a custody specification.

Run:  python3 approval_seam_fixture.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}


# ===========================================================================
# Illustrative Ed25519 — the RFC 8032 reference, pure stdlib (reused from the
# compromise / embodiment fixtures). This fixture tests only the named record
# checks and is not a production cryptographic profile.
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
# Event + Proposal — the lean shapes from embodiment_fixture. The new thing here
# is that a Proposal has a stable hash over its reviewable fields. The approval
# binds to that hash; Event signing later adds signer and timestamp fields.
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
    """What the agent emits. This is not an Event: it has no signer or signature.
    The fixture agent holds no key. Its `content_hash` is the binding
    surface: the reviewable proposal fields presented by the fixture. Two
    proposals that differ in any such field (recipient, amount,
    context) hash differently — that is what makes a bound approval refuse to
    travel from one to another."""
    type: str
    predicate: str
    refs: tuple[str, ...] = ()
    scope: dict[str, Any] | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    as_role: str = "agent"

    def review_body(self) -> dict[str, Any]:
        """The fixture's reviewable proposal fields. Event signing separately
        adds envelope fields including signer and timestamp."""
        return {"type": self.type, "predicate": self.predicate, "refs": list(self.refs),
                "scope": self.scope, "payload": self.payload, "as_role": self.as_role}

    def content_hash(self) -> str:
        return "ph:" + hashlib.sha256(
            json.dumps(self.review_body(), sort_keys=True).encode()).hexdigest()[:16]


def verify_log(events: list[Event]) -> None:
    """Fixture replay check: Ed25519 signature and prior KEY registration only.
    Proposal binding and in-process consumption are signer.handle checks; this
    function does not validate them or establish complete conformance."""
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
# The processes. Custody is in the object graph: only the ceremony holds the root
# secret, only the signer holds the hot secret. The agent holds neither and
# carries approval records back to the signer for the named checks.
# ===========================================================================

@dataclass
class Decision:
    kind: str                                # "signed" | "routed" | "refused"
    reason: str
    event: Event | None = None
    ticket: str | None = None                # set when kind == "routed"


class Clock:
    def __init__(self) -> None:
        self._n = 0

    def now(self) -> str:
        self._n += 1
        return f"2026-06-10T10:{self._n:02d}:00Z"


def _mint(secret: bytes, pub_hex: str, ts: str, *, type_: str, predicate: str,
          **kw) -> Event:
    assert type_ in CANONICAL_TYPES, f"non-canonical type {type_!r}"
    partial = Event(id="", type=type_, signer=pub_hex, predicate=predicate,
                    timestamp=ts, **kw)
    body = partial.signing_bytes()
    sig = ed25519_sign(body, secret, bytes.fromhex(pub_hex)).hex()
    return Event(id="ev:" + hashlib.sha256(body).hexdigest()[:12], type=type_,
                 signer=pub_hex, predicate=predicate, timestamp=ts, signature=sig, **kw)


def scope_only_would_sign(p: Proposal, approval: Event) -> bool:
    """Apply embodiment_fixture's amount-and-context-only counterfactual. This
    function intentionally ignores proposal binding and the consumed set."""
    cap = (approval.scope or {}).get("max_total_krw")
    actx = (approval.scope or {}).get("context")
    amount = p.payload.get("amount_krw")
    pctx = p.payload.get("context") or (p.scope or {}).get("context")
    amount_ok = amount is None or cap is None or amount <= cap
    ctx_ok = actx is None or pctx is None or pctx == actx
    return amount_ok and ctx_ok


class SignerProcess:
    """Holds the hot key and mandate. Auto-signs in-scope proposals and routes
    over-ceiling ones to the inbox. For a returned approval, it checks the
    approval's Ed25519 signature, signer, and fixture-log membership before
    checking its proposal hash and in-process consumed set.
    Authentication, binding, and consumption are signer-side fixture checks;
    a carried approval is not used until they pass."""

    def __init__(self, *, hot_pub: str, hot_secret: bytes, mandate: Event,
                 clock: Clock, log: list[Event]) -> None:
        self._hot_secret = hot_secret
        self.hot_pub = hot_pub
        self.mandate = mandate
        self.clock = clock
        self.log = log
        self.spent_approvals: set[str] = set()   # approval ids already consumed

    @property
    def _ceiling(self) -> int:
        return (self.mandate.scope or {}).get("max_total_krw")

    @property
    def _context(self) -> str:
        return (self.mandate.scope or {}).get("context")

    def _approved_hash(self, approval: Event) -> str | None:
        """The proposal hash this approval is bound to — carried in its refs as the
        ph:... entry. A scope-only approval (no ph: ref) returns None."""
        return next((r for r in approval.refs if r.startswith("ph:")), None)

    def handle(self, p: Proposal, *, approval: Event | None = None) -> Decision:
        if p.as_role != "agent":
            return Decision("refused", "this process holds only the hot key; it cannot "
                            f"sign as '{p.as_role}' (the cold key is not here)")

        ctx = p.payload.get("context") or (p.scope or {}).get("context")
        amount = p.payload.get("amount_krw")

        if approval is not None:
            # Check the carried approval's signature, signer, and fixture-log
            # membership before reading its proposal binding —
            # only then read its binding. Without these, a compromised agent
            # could hand a self-constructed approval object naming the right
            # ph: hash and be signed at sign-time.
            try:
                sig_ok = ed25519_verify(bytes.fromhex(approval.signature),
                                        approval.signing_bytes(),
                                        bytes.fromhex(approval.signer))
            except ValueError:
                sig_ok = False
            if not sig_ok:
                return Decision("refused", "the approval's illustrative signature check fails")
            if approval.signer != self.mandate.signer:
                return Decision("refused", "the approval is not signed by the mandate's granter "
                                "— the hot key honors approvals from the cold root only")
            on_log = next((e for e in self.log if e.id == approval.id), None)
            if on_log is None or on_log != approval:
                return Decision("refused", "the approval is not present in this fixture log")
            # This fixture consumes an approval once in this process.
            bound = self._approved_hash(approval)
            if bound is None:
                return Decision("refused", "the approval is scope-only (a bearer token) — "
                                "it names no proposal; this signer reading refuses it")
            if bound != p.content_hash():
                return Decision("refused", "the approval references a different proposal hash "
                                f"({bound} != {p.content_hash()})")
            if approval.id in self.spent_approvals:
                return Decision("refused", "the approval already appears in this process's consumed set")
            self.spent_approvals.add(approval.id)
            ev = self._sign(p, refs=tuple(p.refs) + (approval.id,))
            return Decision("signed", "signed after the proposal-bound approval passed the "
                            "fixture's in-process checks", ev)

        if self._context is not None and ctx is not None and ctx != self._context:
            return Decision("refused", f"out of mandate domain ({ctx} != {self._context}) — "
                            "not the hot key's authority")
        if amount is not None and self._ceiling is not None and amount > self._ceiling:
            return Decision("routed", f"over the mandate ceiling ({amount} > {self._ceiling}) "
                            "— routed to the approval inbox", ticket=p.content_hash())

        ev = self._sign(p)
        return Decision("signed", "within the live mandate (right domain, within ceiling)", ev)

    def _sign(self, p: Proposal, *, refs: tuple[str, ...] | None = None) -> Event:
        ev = _mint(self._hot_secret, self.hot_pub, self.clock.now(), type_=p.type,
                   predicate=p.predicate, refs=refs if refs is not None else tuple(p.refs),
                   scope=p.scope, payload=p.payload)
        self.log.append(ev)
        return ev


@dataclass
class Ticket:
    """A routed proposal waiting at the inbox. It holds the proposal fields that
    the ceremony reviews; Event signing later adds envelope fields."""
    id: str
    proposal: Proposal
    decided: bool = False


class ApprovalInbox:
    """Stores routed proposals for the simulated cold-root ceremony. The ceremony
    emits a proposal-bound approval that returns to the signer through the agent."""

    def __init__(self) -> None:
        self.tickets: dict[str, Ticket] = {}

    def file(self, p: Proposal) -> str:
        t = Ticket(id=p.content_hash(), proposal=p)
        self.tickets[t.id] = t
        return t.id

    def pending(self) -> list[Ticket]:
        return [t for t in self.tickets.values() if not t.decided]

    def review(self, ticket_id: str) -> dict[str, Any]:
        """Return the fixture's reviewable body and the hash an approval binds to.
        This does not establish what a person actually saw or understood."""
        t = self.tickets[ticket_id]
        return {"hash": t.proposal.content_hash(), "body": t.proposal.review_body()}

    def mark_decided(self, ticket_id: str) -> None:
        self.tickets[ticket_id].decided = True


class AgentProcess:
    """Proposes events and carries approvals back. Holds NO key. Whoever drives it
    — the configured operator or an attacker — can emit a Proposal and relay an
    approval. The signer evaluates the returned record and proposal fields."""

    def __init__(self, *, signer: SignerProcess, inbox: ApprovalInbox) -> None:
        self._signer = signer
        self._inbox = inbox

    def propose(self, p: Proposal, *, approval: Event | None = None) -> Decision:
        d = self._signer.handle(p, approval=approval)
        if d.kind == "routed":
            self._inbox.file(p)
        return d


class ColdRootCeremony:
    """Scripted cold-key holder. It reads routed proposal fields and emits
    proposal-bound approvals whose refs name the reviewable proposal hash."""

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

    def review_and_approve(self, inbox: ApprovalInbox, ticket_id: str, amount: int,
                           context: str) -> Event:
        """The simulated ceremony pulls the ticket and binds the approval to the
        reviewable proposal hash. Signer/timestamp envelope fields are added later."""
        seen = inbox.review(ticket_id)
        inbox.mark_decided(ticket_id)
        return self._emit(type_="AUTHORIZE", predicate="consent.approval",
                          refs=(seen["hash"],),
                          scope={"context": context, "max_total_krw": amount})

    def approve_scope_only(self, amount: int, context: str) -> Event:
        """embodiment_fixture's approval, reproduced for the counterfactual: a
        scope token bound to no proposal, evaluated only as fixture input."""
        return self._emit(type_="AUTHORIZE", predicate="consent.approval",
                          scope={"context": context, "max_total_krw": amount})


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


def show(label: str, d: Decision, *, attacker: bool = False) -> None:
    glyph = {"signed": "SIGNED ", "routed": "ROUTED ", "refused": "REFUSED"}[d.kind]
    tag = "  <-- attacker drove the agent" if attacker else ""
    eid = f"  [{d.event.id}]" if d.event else ""
    print(f"    {glyph}  {label:<36} {d.reason}{eid}{tag}")


# ===========================================================================
# The generated flow — run once, top to bottom.
# ===========================================================================

def generate() -> dict:
    clock = Clock()
    log: list[Event] = []

    def keypair(name: str) -> tuple[bytes, str]:
        sk = hashlib.sha256(b"arc-approval-seam/" + name.encode()).digest()
        return sk, ed25519_publickey(sk).hex()

    root_secret, root_pub = keypair("root")
    agent_secret, agent_pub = keypair("agent")

    print("\n1. Offline ceremony — the cold root anchors keys, grants a mandate, then")
    print("   goes away. The hot key may sign 'market' acts up to 30000.")
    ceremony = ColdRootCeremony(root_pub=root_pub, root_secret=root_secret,
                                clock=clock, log=log)
    ceremony.register(root_pub)
    ceremony.register(agent_pub)
    mandate = ceremony.grant_mandate(agent_pub, context="market", ceiling=30000)
    say("custody", f"mandate: hot key signs 'market' <= 30000  [{mandate.id}]")

    print("\n2. Signer setup — signer holds the hot key + mandate; agent has references to")
    print("   the signer and the inbox. The simulated ceremony can review routed tickets.")
    inbox = ApprovalInbox()
    signer = SignerProcess(hot_pub=agent_pub, hot_secret=agent_secret, mandate=mandate,
                           clock=clock, log=log)
    agent = AgentProcess(signer=signer, inbox=inbox)

    def payment(amount: int, payee: str, context: str = "market") -> Proposal:
        return Proposal(type="ATTEST", predicate="commerce.payment_result", refs=(mandate.id,),
                        payload={"result": "confirmed", "amount_krw": amount,
                                 "payee": payee, "context": context, "provider": "mock_pay"})

    print("\n3. Configured escalation — over the ceiling, so it routes; the simulated")
    print("   ceremony reviews the proposal fields and binds their hash.")
    approved_target = payment(90000, payee="merchant-rho")
    d_route = agent.propose(approved_target)
    show("over-ceiling payment 90000", d_route)
    say("inbox", f"ticket {d_route.ticket} pending for the simulated ceremony")
    seen = inbox.review(d_route.ticket)
    say("ceremony", f"reads ticket fields: pay {seen['body']['payload']['amount_krw']} to "
        f"{seen['body']['payload']['payee']}; emits an approval with the cold key")
    approval = ceremony.review_and_approve(inbox, d_route.ticket, 90000, "market")
    show("  (re-submitted, bound approval)", agent.propose(approved_target, approval=approval))

    print("\n4. Attacker-controlled agent label — the attacker now holds the approval in flight.")
    print("   The tested constructed approval fails the cold-root signature check. The comparison concerns approval reuse.")

    print("\n   (a) Re-aim: submit the approval with a different payee, same amount.")
    reaimed = payment(90000, payee="attacker-self")
    cf = scope_only_would_sign(reaimed, approval)
    say("generator", f"scope-only counterfactual would sign this: {cf}")
    show("re-aimed payment 90000", agent.propose(reaimed, approval=approval), attacker=True)

    print("\n   (b) Replay: submit the approved proposal a second time.")
    show("replay approved payment", agent.propose(approved_target, approval=approval), attacker=True)

    print("\n   (c) Scope-only: submit a fixture cold-root approval that names no proposal.")
    bearer = ceremony.approve_scope_only(90000, "market")  # a token bound to nothing
    say("generator", "mints a scope-only approval as a counterfactual input")
    show("scope-only bearer 90000", agent.propose(payment(90000, "attacker-self"),
                                                  approval=bearer), attacker=True)

    print("\n   (d) Invalid signature: construct an approval object naming the target hash.")
    target = payment(90000, payee="attacker-self")
    forged = Event(id="ev:forged", type="AUTHORIZE", signer=root_pub,
                   predicate="consent.approval", timestamp="2026-06-10T10:59:00Z",
                   refs=(target.content_hash(),),
                   scope={"context": "market", "max_total_krw": 90000},
                   signature="00" * 64)
    say("generator", "constructs the target hash without the root secret; the")
    say("generator", "illustrative signature check fails")
    show("invalid-signature approval", agent.propose(target, approval=forged), attacker=True)

    print("\n   (e) Off-log: an illustrative-Ed25519 approval not appended to the log.")
    offlog = _mint(root_secret, root_pub, "2026-06-10T10:58:00Z", type_="AUTHORIZE",
                   predicate="consent.approval", refs=(target.content_hash(),),
                   scope={"context": "market", "max_total_krw": 90000})
    say("generator", "mints one with the root secret and does not append it")
    show("off-log bound approval", agent.propose(target, approval=offlog), attacker=True)

    say("fixture", "all five are refused by the named in-process checks.")
    say("fixture", "The approval binds reviewable proposal fields, not Event envelope bytes.")

    verify_log(log)
    return {"log": log, "root": root_pub, "agent": agent_pub,
            "approval_id": approval.id, "approved_target_hash": approved_target.content_hash()}


# ===========================================================================
# Band data — the same scenario, returned as structure for the reference
# client's seventh band. The signer's verdicts and computed counterfactual are
# produced here; build.py only renders them. The two readings compare the actual
# proposal-bound signer with the scope-only policy used by embodiment_fixture.
# ===========================================================================

READINGS = ["proposal_bound", "scope_only"]   # the actual signer / the counterfactual
NAMES: dict[str, str] = {}                     # payees are plain strings; no key display


def band_data() -> dict:
    """Run the approval-return scenario once and return what the band renders:
    signer-boundary decisions, one routed approval, and attempts judged under
    both readings (proposal-bound refuses; scope-only may sign).
    No stdout; build.py re-verifies the log it returns."""
    clock = Clock()
    log: list[Event] = []

    def keypair(name: str) -> tuple[bytes, str]:
        sk = hashlib.sha256(b"arc-approval-seam/" + name.encode()).digest()
        return sk, ed25519_publickey(sk).hex()

    root_secret, root_pub = keypair("root")
    agent_secret, agent_pub = keypair("agent")
    ceremony = ColdRootCeremony(root_pub=root_pub, root_secret=root_secret,
                                clock=clock, log=log)
    ceremony.register(root_pub)
    ceremony.register(agent_pub)
    mandate = ceremony.grant_mandate(agent_pub, context="market", ceiling=30000)
    inbox = ApprovalInbox()
    signer = SignerProcess(hot_pub=agent_pub, hot_secret=agent_secret, mandate=mandate,
                           clock=clock, log=log)
    agent = AgentProcess(signer=signer, inbox=inbox)

    def payment(amount: int, payee: str, context: str = "market") -> Proposal:
        return Proposal(type="ATTEST", predicate="commerce.payment_result", refs=(mandate.id,),
                        payload={"result": "confirmed", "amount_krw": amount,
                                 "payee": payee, "context": context, "provider": "mock_pay"})

    def record(label: str, by: str, d: Decision, amount, payee: str) -> dict:
        return {"label": label, "by": by, "verdict": d.kind, "reason": d.reason,
                "amount": amount, "payee": payee,
                "id": d.event.id if d.event else None}

    # --- signer boundary: the agent holds no key ---
    signer_boundary = [
        record("in-scope payment", "operator",
               agent.propose(payment(20000, "merchant-rho")), 20000, "merchant-rho"),
    ]
    approved_target = payment(90000, "merchant-rho")
    d_route = agent.propose(approved_target)
    signer_boundary.append(record("over-ceiling payment", "operator", d_route, 90000, "merchant-rho"))
    signer_boundary.append(record("out-of-domain attacker proposal", "attacker", agent.propose(
        Proposal(type="ATTEST", predicate="identity.binding", refs=(mandate.id,),
                 payload={"claim": "controls_external_account", "context": "identity"})),
        None, "—"))
    signer_boundary.append(record("self-mint as root", "attacker", agent.propose(
        Proposal(type="AUTHORIZE", predicate="consent.mandate", as_role="root",
                 refs=(agent_pub,), scope={"context": "market", "max_total_krw": 1000000})),
        1000000, "—"))

    # --- escalation: the ceremony binds the reviewable proposal-field hash ---
    seen = inbox.review(d_route.ticket)
    approval = ceremony.review_and_approve(inbox, d_route.ticket, 90000, "market")
    d_signed = agent.propose(approved_target, approval=approval)   # SIGNED; spends the approval
    escalation = {"ticket": d_route.ticket, "payee": "merchant-rho", "amount": 90000,
                  "approval_id": approval.id, "signed_id": d_signed.event.id,
                  "review_payee": seen["body"]["payload"]["payee"],
                  "review_amount": seen["body"]["payload"]["amount_krw"]}

    # --- the attempts: the approval returning through the agent, each
    #     judged under both readings. proposal_bound = the actual signer (calling
    #     handle has no side effect since all three refuse); scope_only = the
    #     computed counterfactual (the bearer-token signer that would sign). ---
    def attempt(label: str, p: Proposal, appr: Event, *, kind: str) -> dict:
        d = signer.handle(p, approval=appr)               # actual, proposal-bound
        cf = scope_only_would_sign(p, appr)               # counterfactual, scope-only
        cf_reason = ("a scope token (context + amount) signs this — the return path "
                     "is a bearer token") if cf else "outside even the scope token's cap/context"
        return {"label": label, "kind": kind,
                "payee": p.payload.get("payee"), "amount": p.payload.get("amount_krw"),
                "readings": {
                    "proposal_bound": {"verdict": d.kind, "reason": d.reason},
                    "scope_only": {"verdict": "signed" if cf else "refused",
                                   "reason": cf_reason}}}

    # The bearer token is a fixture cold-root record on the log — a scope-only approval
    # an attacker might obtain. It passes the return-path checks (signature,
    # granter, log membership); what the signer refuses is its shape: it names no
    # proposal, so it is consent to a class of acts, not to one. (handle now
    # authenticates every carried approval, so an unsigned stand-in would be
    # refused for the wrong reason.)
    bearer = ceremony.approve_scope_only(90000, "market")
    attempts = [
        attempt("re-aim to a new payee", payment(90000, "attacker-self"), approval, kind="reaim"),
        attempt("replay the approved act", approved_target, approval, kind="replay"),
        attempt("scope-only bearer token", payment(90000, "attacker-self"), bearer, kind="bearer"),
    ]

    # Generator-only stipulations; the signer-boundary and attempt rows do not use them.
    generator_only = [
        {"label": "in-scope + over-ceiling payments", "who": "the configured operator"},
        {"label": "out-of-domain, self-mint, re-aim, replay, bearer", "who": "the attacker"},
        {"note": "the signer evaluates proposal fields and does not receive this "
                 "private author label"},
    ]

    verify_log(log)
    return {"events": log, "signer_boundary": signer_boundary,
            "escalation": escalation, "attempts": attempts,
            "generator_only": generator_only, "ceiling": 30000, "context": "market",
            "root": root_pub, "agent": agent_pub}


# ===========================================================================
# Standalone run.
# ===========================================================================

def main() -> None:
    ctx = generate()
    log = ctx["log"]

    print("\n" + "=" * 74)
    print("Records appended to the log — every payment over the ceiling refs the approval")
    print("that authorized it, and every approval refs the one proposal it covered.")
    print("=" * 74)
    by_id = {e.id: e for e in log}
    for e in log:
        if e.predicate == "commerce.payment_result":
            appr = next((r for r in e.refs if r in by_id
                         and by_id[r].predicate == "consent.approval"), None)
            bound = by_id[appr].refs[0] if appr else "-"
            payee = e.payload.get("payee")
            print(f"    [{e.id}]  pays {e.payload['amount_krw']:>6} to {payee:<14} "
                  f"approval={appr or '(none, in-mandate)'}  bound={bound}")

    print("\n" + "=" * 74)
    print("Fixture result — proposal-bound and scope-only approval readings")
    print("=" * 74)
    print("""
  The signer holds the hot key, while the agent carries proposals and approval
  records. The scope-only counterfactual checks context and amount but does not
  bind an approval to one proposal. scope_only_would_sign() therefore returns
  True for the authored re-aim and replay cases.

  Binding the approval to the proposal's content hash closes the tested re-aim
  path. The hash covers reviewable proposal fields; the Event signer adds envelope
  fields. This fixture refuses a replay through an in-memory consumed set and,
  before applying that check, authenticates
  the carried approval itself: its own signature verifies, its signer is the
  mandate's granter, and it is a record on the log. The five authored cases are
  refused at sign time:

    * re-aim to a new payee   -> REFUSED  (bound to a different proposal hash)
    * replay the approved act  -> REFUSED  (the approval was already spent)
    * a scope-only bearer token-> REFUSED  (names no proposal; not honored)
    * an invalid-signature approval -> REFUSED  (its own signature does not verify)
    * an off-log approval      -> REFUSED  (not present in this fixture log)

  The approval is a separately signed record. This fixture cannot establish what
  a person saw or understood; it checks only that the approval references the hash
  over review_body() and that the signer applies the named in-process checks.

  Two limitations remain:

    * availability. A return path is a new place to stall: an approval can be
      dropped or withheld, and escalation blocks. The one-way proposal path does
      not model this return-path dependency.
    * review reliability. Binding does not establish comprehension or protect
      against a misleading presentation; those questions remain outside the fixture.

  The Ed25519 implementation is illustrative, and the consumed set is in-process
  fixture state. This is not a complete verifier or deployment model.
""")


if __name__ == "__main__":
    main()

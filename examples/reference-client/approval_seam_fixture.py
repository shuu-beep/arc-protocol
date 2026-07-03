#!/usr/bin/env python3
"""
ARC approval-seam fixture — the escalation return path as a custody surface.

What this is
------------
embodiment_fixture.py split the agent from the signer into two processes and
found that escalation forces a SECOND seam: the proposal seam carries
agent -> signer, but a routed proposal needs an approval RETURN path
(inbox -> a human -> back to a signed event) the proposal seam never had. That
fixture named the seam (an `ApprovalInbox` class) but left it DEAD: nothing
drained it, and the human's approval was hand-fed at the call site, riding back
to the signer bypassing the inbox entirely.

This fixture makes the second seam LIVE — a human actually pulls a routed
proposal, reviews it, and decides — and asks the question that exposes: what does
the return path carry, and who can carry it?

The first seam moved the KEY behind the signer, so a compromised agent yields
proposals, never signatures. But the return path runs back through the SAME
untrusted agent. So the approval is a capability in flight, and the question
custody always asks returns: whoever HOLDS it, can spend it.

  * embodiment_fixture's approval was a SCOPE token: consent.approval scoped by
    {context, max_total_krw}. The signer's approval branch checked only
    `amount <= cap`. Nothing bound it to the proposal the human saw.
  * So a scope-token approval is a BEARER token. A compromised agent, handed an
    approval for "a 90000 market payment", can bind it to a DIFFERENT 90000
    market payment (a different recipient), or REPLAY it for several. The human
    reviewed one act; the return path can spend the approval on others.

The fix, and its residue:

  * bind the approval to the PROPOSAL the human actually reviewed — to a hash of
    the exact bytes shown at the inbox. Now the approval is single-use and
    non-transferable: it validates against that one proposal and no other. A
    compromised agent can at most cause the act the human already consented to.
  * and trust no carried approval until the seam AUTHENTICATES it: the signer
    verifies the approval's own Ed25519 signature, that its signer is the
    mandate's granter (the cold root), and that it is on the log — an approval
    is a RECORD, not a message. A self-constructed approval object naming the
    right hash, or a validly signed one that never became a record, dies before
    its binding is even read.
  * but this makes the HUMAN a second signer. The approval is only as good as
    what the human SAW. The inbox must show the human the same bytes the signer
    would sign; if it shows less (a friendly summary that omits the recipient),
    the human's consent does not cover the difference — a confused deputy. The
    second seam needs the first seam's "sign what you saw" guarantee, now for a
    human's eyes instead of a signer's bytes.

So SIGN/ROUTE/REFUSE deepens. ROUTE is not "defer to a human." It opens a second
custody boundary where the human is the signer, the proposal-binding is the
mandate, and the human's review is the trusted base. The minimal slice moved the
key off the agent; it did not move the approval off the agent — this one does, and
finds the human standing where the signer stood.

Real Ed25519 (RFC 8032, pure stdlib, reused verbatim from the prior fixtures)
because the whole point is that "this approval validates against that one
proposal" is a cryptographic FACT, not a policy claim. Only the cold-root ceremony
holds the root secret; only the signer holds the hot secret; the agent holds
neither and carries the approval without being able to forge or re-aim it.

Refusals (as deliberate as the content):
  * not a daemon, not a wallet, not a security product. "Processes" are objects
    sharing serializable seams; no network, no persistence, no real isolation.
    The crypto is ILLUSTRATIVE — this probes constitutional boundary visibility.
  * no new event type. The approval is the existing consent.approval; the binding
    rides in its refs (the proposal hash) — evidence the canon already holds, used
    one notch more tightly. The replay defense is consumption tracked in the
    signer's trusted base, not a new primitive.
  * the counterfactual is COMPUTED, not asserted. The fixture carries a
    `scope_only_would_sign` that replays embodiment_fixture's amount-only check, so
    "a bearer token would have signed this" is shown by running it, not claimed.
  * who drives the agent is GROUND TRUTH the generator holds, rendered as the
    omniscient view; the signer and the human never read it.

A probe, not doctrine — the runtime expression of the second seam embodiment_
fixture left dead. Not a custody spec.

Run:  python3 approval_seam_fixture.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}


# ===========================================================================
# Real Ed25519 — the RFC 8032 reference, pure stdlib (reused verbatim from the
# compromise / embodiment fixtures). A secret signs, a public value verifies, and
# you cannot produce a passing signature without the secret. That is what makes
# "this approval is bound to that one proposal" a fact and not a claim.
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
# is that a Proposal has a stable IDENTITY: the hash of the exact bytes a human
# would review and a signer would sign. The approval binds to that identity.
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
    """What the agent emits. NOT an event: no signer, no signature. The agent holds
    no key, so this is the most it can produce. Its `content_hash` is the binding
    surface: the exact bytes a human reviews at the inbox and the signer would
    sign. Two proposals that differ in ANY reviewable field (recipient, amount,
    context) hash differently — that is what makes a bound approval refuse to
    travel from one to another."""
    type: str
    predicate: str
    refs: tuple[str, ...] = ()
    scope: dict[str, Any] | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    as_role: str = "agent"

    def review_body(self) -> dict[str, Any]:
        """The bytes a human sees and the signer signs — everything reviewable.
        Deliberately the SAME projection for both, so "what the human saw" and
        "what the signer signs" cannot diverge silently."""
        return {"type": self.type, "predicate": self.predicate, "refs": list(self.refs),
                "scope": self.scope, "payload": self.payload, "as_role": self.as_role}

    def content_hash(self) -> str:
        return "ph:" + hashlib.sha256(
            json.dumps(self.review_body(), sort_keys=True).encode()).hexdigest()[:16]


def verify_log(events: list[Event]) -> None:
    """Verification IS replay: real Ed25519 + signer anchored by a prior KEY
    register. Every approval-backed payment on the log refs an approval whose own
    refs name the payment's proposal hash — the binding is checkable from the log
    alone, by anyone, after the fact."""
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
# secret, only the signer holds the hot secret. The agent holds neither — and now
# also carries the approval back, holding a capability it cannot forge or re-aim.
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
    """The COUNTERFACTUAL, run rather than asserted: embodiment_fixture's
    amount-only approval check. A scope token says yes to any proposal within its
    cap and context, whatever its content hash. This is what makes that approval a
    bearer token — and what this fixture's signer refuses to be."""
    cap = (approval.scope or {}).get("max_total_krw")
    actx = (approval.scope or {}).get("context")
    amount = p.payload.get("amount_krw")
    pctx = p.payload.get("context") or (p.scope or {}).get("context")
    amount_ok = amount is None or cap is None or amount <= cap
    ctx_ok = actx is None or pctx is None or pctx == actx
    return amount_ok and ctx_ok


class SignerProcess:
    """Holds the HOT key and the mandate. Auto-signs in-scope proposals; routes
    over-ceiling ones to the inbox. When an approval rides back, it first
    AUTHENTICATES it — the approval's own Ed25519 signature, signer == the
    mandate's granter, membership on the log — and only then signs, and ONLY if
    the approval is bound to THIS proposal's content hash and has not been spent.
    Authentication, binding, and consumption all live in the signer's trusted
    base; a carried approval is untrusted bytes until they pass."""

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
            # A carried approval is untrusted bytes until authenticated: verify
            # its signature, its signer, and that it is a RECORD on the log —
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
                return Decision("refused", "the approval's own signature does not verify — "
                                "a carried approval is a claim until its bytes prove their signer")
            if approval.signer != self.mandate.signer:
                return Decision("refused", "the approval is not signed by the mandate's granter "
                                "— the hot key honors approvals from the cold root only")
            on_log = next((e for e in self.log if e.id == approval.id), None)
            if on_log is None or on_log != approval:
                return Decision("refused", "the approval is not on the log — consent that never "
                                "became a record is a message, not an approval")
            # The whole point of the fixture: an approval is consent to ONE act.
            bound = self._approved_hash(approval)
            if bound is None:
                return Decision("refused", "the approval is scope-only (a bearer token) — "
                                "it names no proposal; this signer will not honor it")
            if bound != p.content_hash():
                return Decision("refused", "the approval is bound to a DIFFERENT proposal "
                                f"({bound} != {p.content_hash()}) — the human did not consent to this act")
            if approval.id in self.spent_approvals:
                return Decision("refused", "the approval was already spent — consent to one "
                                "act is not a standing allowance")
            self.spent_approvals.add(approval.id)
            ev = self._sign(p, refs=tuple(p.refs) + (approval.id,))
            return Decision("signed", "signed under a proposal-bound, single-use cold-root "
                            "approval (the human consented to exactly this act)", ev)

        if self._context is not None and ctx is not None and ctx != self._context:
            return Decision("refused", f"out of mandate domain ({ctx} != {self._context}) — "
                            "not the hot key's authority")
        if amount is not None and self._ceiling is not None and amount > self._ceiling:
            return Decision("routed", f"over the mandate ceiling ({amount} > {self._ceiling}) "
                            "— routed to the approval inbox for a human", ticket=p.content_hash())

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
    """A routed proposal waiting at the inbox. Holds the FULL proposal, so the
    human reviews the same bytes the signer would sign — not a summary."""
    id: str
    proposal: Proposal
    decided: bool = False


class ApprovalInbox:
    """The second seam, made LIVE. The proposal seam carried agent -> signer; this
    carries signer -> human -> back. A routed proposal becomes a Ticket the human
    can pull and review; the human's decision produces a proposal-BOUND approval
    that travels back through the (untrusted) agent without being re-aimable."""

    def __init__(self) -> None:
        self.tickets: dict[str, Ticket] = {}

    def file(self, p: Proposal) -> str:
        t = Ticket(id=p.content_hash(), proposal=p)
        self.tickets[t.id] = t
        return t.id

    def pending(self) -> list[Ticket]:
        return [t for t in self.tickets.values() if not t.decided]

    def review(self, ticket_id: str) -> dict[str, Any]:
        """What the human SEES — the exact reviewable body and the hash that an
        approval will bind to. This projection IS the human's trusted base; if it
        omitted a field, the human's consent would not cover it."""
        t = self.tickets[ticket_id]
        return {"hash": t.proposal.content_hash(), "body": t.proposal.review_body()}

    def mark_decided(self, ticket_id: str) -> None:
        self.tickets[ticket_id].decided = True


class AgentProcess:
    """Proposes events and carries approvals back. Holds NO key. Whoever drives it
    — the honest operator or an attacker — can emit a Proposal and relay an
    approval, but cannot forge a signature or re-aim a bound approval."""

    def __init__(self, *, signer: SignerProcess, inbox: ApprovalInbox) -> None:
        self._signer = signer
        self._inbox = inbox

    def propose(self, p: Proposal, *, approval: Event | None = None) -> Decision:
        d = self._signer.handle(p, approval=approval)
        if d.kind == "routed":
            self._inbox.file(p)
        return d


class ColdRootCeremony:
    """The human with the cold key. Reviews routed proposals at the inbox and signs
    proposal-BOUND approvals: an approval whose refs name the exact proposal hash
    the human saw. Absent otherwise — invoked only for ceremony."""

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
        """The human pulls the ticket, sees the exact bytes, and binds the approval
        to THAT proposal hash. The approval is minted off the cold key, above the
        mandate — but it names one act, not a class of acts."""
        seen = inbox.review(ticket_id)
        inbox.mark_decided(ticket_id)
        return self._emit(type_="AUTHORIZE", predicate="consent.approval",
                          refs=(seen["hash"],),
                          scope={"context": context, "max_total_krw": amount})

    def approve_scope_only(self, amount: int, context: str) -> Event:
        """embodiment_fixture's approval, reproduced for the counterfactual: a
        scope token, bound to no proposal. Shown to be refused, not used in anger."""
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

    print("\n1. OFFLINE CEREMONY — the cold root anchors keys, grants a mandate, then")
    print("   goes away. The hot key may sign 'market' acts up to 30000.")
    ceremony = ColdRootCeremony(root_pub=root_pub, root_secret=root_secret,
                                clock=clock, log=log)
    ceremony.register(root_pub)
    ceremony.register(agent_pub)
    mandate = ceremony.grant_mandate(agent_pub, context="market", ceiling=30000)
    say("custody", f"mandate: hot key signs 'market' <= 30000  [{mandate.id}]")

    print("\n2. BOOT — signer holds the hot key + mandate; agent holds only lines to")
    print("   the signer and the inbox. The inbox is LIVE: a human will pull from it.")
    inbox = ApprovalInbox()
    signer = SignerProcess(hot_pub=agent_pub, hot_secret=agent_secret, mandate=mandate,
                           clock=clock, log=log)
    agent = AgentProcess(signer=signer, inbox=inbox)

    def payment(amount: int, payee: str, context: str = "market") -> Proposal:
        return Proposal(type="ATTEST", predicate="commerce.payment_result", refs=(mandate.id,),
                        payload={"result": "confirmed", "amount_krw": amount,
                                 "payee": payee, "context": context, "provider": "mock_pay"})

    print("\n3. HONEST ESCALATION — over the ceiling, so it routes; the human pulls the")
    print("   ticket, sees the EXACT proposal, and approves THAT act.")
    honest = payment(90000, payee="merchant-rho")
    d_route = agent.propose(honest)
    show("over-ceiling payment 90000", d_route)
    say("inbox", f"ticket {d_route.ticket} pending for a human")
    seen = inbox.review(d_route.ticket)
    say("human", f"reviews ticket: pays {seen['body']['payload']['amount_krw']} to "
        f"{seen['body']['payload']['payee']} — recognizes it, approves with the COLD key")
    approval = ceremony.review_and_approve(inbox, d_route.ticket, 90000, "market")
    show("  (re-submitted, bound approval)", agent.propose(honest, approval=approval))

    print("\n4. THE AGENT IS COMPROMISED — the attacker now holds the approval in flight.")
    print("   It cannot forge a signature. The question is what it can do with consent.")

    print("\n   (a) RE-AIM: bind the human's approval to a DIFFERENT payee, same amount.")
    reaimed = payment(90000, payee="attacker-self")
    cf = scope_only_would_sign(reaimed, approval)
    say("omniscient", f"a scope-only (bearer) approval WOULD sign this: {cf}  <-- the leak")
    show("re-aimed payment 90000", agent.propose(reaimed, approval=approval), attacker=True)

    print("\n   (b) REPLAY: spend the SAME approved act a second time.")
    show("replay approved payment", agent.propose(honest, approval=approval), attacker=True)

    print("\n   (c) BEARER: forge a fresh scope-only approval shape and ride it.")
    bearer = ceremony.approve_scope_only(90000, "market")  # a token bound to nothing
    say("omniscient", "(generator mints a scope-only token to stand in for one an")
    say("omniscient", " attacker might harvest; the signer's reaction is the point)")
    show("scope-only bearer 90000", agent.propose(payment(90000, "attacker-self"),
                                                  approval=bearer), attacker=True)

    print("\n   (d) FORGE: self-construct an approval OBJECT naming the right hash.")
    target = payment(90000, payee="attacker-self")
    forged = Event(id="ev:forged", type="AUTHORIZE", signer=root_pub,
                   predicate="consent.approval", timestamp="2026-06-10T10:59:00Z",
                   refs=(target.content_hash(),),
                   scope={"context": "market", "max_total_krw": 90000},
                   signature="00" * 64)
    say("omniscient", "the attacker knows the hash it wants approved; it does not know")
    say("omniscient", "the root secret — the object is right-shaped, the bytes are not")
    show("forged bound approval", agent.propose(target, approval=forged), attacker=True)

    print("\n   (e) OFF-LOG: a validly signed approval that never became a record.")
    offlog = _mint(root_secret, root_pub, "2026-06-10T10:58:00Z", type_="AUTHORIZE",
                   predicate="consent.approval", refs=(target.content_hash(),),
                   scope={"context": "market", "max_total_krw": 90000})
    say("omniscient", "(generator mints one with the root secret and does NOT append it —")
    say("omniscient", " standing in for consent captured out-of-band, off the log)")
    show("off-log bound approval", agent.propose(target, approval=offlog), attacker=True)

    say("omniscient", "all five refused at SIGN-TIME. The approval is consent to ONE act:")
    say("omniscient", "the human's, on the log, byte-for-byte what they reviewed.")

    verify_log(log)
    return {"log": log, "root": root_pub, "agent": agent_pub,
            "approval_id": approval.id, "honest_hash": honest.content_hash()}


# ===========================================================================
# Band data — the same scenario, returned as structure for the reference
# client's seventh band. The signer's verdicts and the computed counterfactual
# are produced HERE (the fixture's trusted base); build.py only renders them.
# The two READINGS are the real toggle finding L exposes: the actual proposal-
# bound signer vs the scope-only bearer-token signer embodiment_fixture carried.
# ===========================================================================

READINGS = ["proposal_bound", "scope_only"]   # the actual signer / the counterfactual
NAMES: dict[str, str] = {}                     # payees are plain strings; no key display


def band_data() -> dict:
    """Run the custody-seam scenario once and return what the band renders:
    the sign-time WALL (finding K's trichotomy), the live ESCALATION through the
    second seam, and the ATTEMPTS each judged under BOTH readings (proposal-bound
    refuses; scope-only would sign — the bearer-token leak, computed not asserted).
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

    # --- the wall: the signer's trichotomy (K), agent holds no key ---
    wall = [
        record("in-scope payment", "operator",
               agent.propose(payment(20000, "merchant-rho")), 20000, "merchant-rho"),
    ]
    honest = payment(90000, "merchant-rho")
    d_route = agent.propose(honest)
    wall.append(record("over-ceiling payment", "operator", d_route, 90000, "merchant-rho"))
    wall.append(record("out-of-domain forgery", "attacker", agent.propose(
        Proposal(type="ATTEST", predicate="identity.binding", refs=(mandate.id,),
                 payload={"claim": "controls_external_account", "context": "identity"})),
        None, "—"))
    wall.append(record("self-mint as root", "attacker", agent.propose(
        Proposal(type="AUTHORIZE", predicate="consent.mandate", as_role="root",
                 refs=(agent_pub,), scope={"context": "market", "max_total_krw": 1000000})),
        1000000, "—"))

    # --- the escalation: the human reviews the exact bytes, approves bound ---
    seen = inbox.review(d_route.ticket)
    approval = ceremony.review_and_approve(inbox, d_route.ticket, 90000, "market")
    d_signed = agent.propose(honest, approval=approval)   # SIGNED; spends the approval
    escalation = {"ticket": d_route.ticket, "payee": "merchant-rho", "amount": 90000,
                  "approval_id": approval.id, "signed_id": d_signed.event.id,
                  "review_payee": seen["body"]["payload"]["payee"],
                  "review_amount": seen["body"]["payload"]["amount_krw"]}

    # --- the attempts: the approval in flight through the untrusted agent, each
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

    # the bearer token is a REAL cold-root act on the log — a scope-only approval
    # an attacker might harvest. It passes the seam's authentication (signature,
    # granter, log membership); what the signer refuses is its SHAPE: it names no
    # proposal, so it is consent to a class of acts, not to one. (handle now
    # authenticates every carried approval, so an unsigned stand-in would be
    # refused for the wrong reason — the bearer leak is the reason under test.)
    bearer = ceremony.approve_scope_only(90000, "market")
    attempts = [
        attempt("re-aim to a new payee", payment(90000, "attacker-self"), approval, kind="reaim"),
        attempt("replay the approved act", honest, approval, kind="replay"),
        attempt("scope-only bearer token", payment(90000, "attacker-self"), bearer, kind="bearer"),
    ]

    # omniscient: who actually drove each act. The wall/attempt rows never see it.
    omniscient = [
        {"label": "in-scope + over-ceiling payments", "who": "the honest operator"},
        {"label": "out-of-domain, self-mint, re-aim, replay, bearer", "who": "the attacker"},
        {"note": "a valid in-scope proposal is the SAME object whoever composed it — "
                 "the signer never reads this strip"},
    ]

    verify_log(log)
    return {"events": log, "wall": wall, "escalation": escalation, "attempts": attempts,
            "omniscient": omniscient, "ceiling": 30000, "context": "market",
            "root": root_pub, "agent": agent_pub}


# ===========================================================================
# Standalone run — narrate, then state what making the seam live revealed.
# ===========================================================================

def main() -> None:
    ctx = generate()
    log = ctx["log"]

    print("\n" + "=" * 74)
    print("WHAT REACHED THE LOG — every payment over the ceiling refs the approval")
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
    print("THE FINDING — the escalation return path is a second custody surface")
    print("=" * 74)
    print("""
  embodiment_fixture moved the KEY behind the signer: a compromised agent yields
  proposals, never signatures. But escalation forced a return path, and that path
  runs back through the same untrusted agent. So the approval is a capability in
  flight — and custody's question returns: whoever holds it, can spend it.

  embodiment_fixture's approval was a SCOPE token (context + amount); its signer
  checked only `amount <= cap`. Run forward to a live inbox, that token is a BEARER
  token. The counterfactual is computed, not claimed: scope_only_would_sign()
  returns True for a re-aimed payment to the attacker's own payee. The human
  reviewed ONE act; a scope token lets the return path spend their consent on
  others, and replay it.

  Binding the approval to the proposal's content hash closes it. The approval names
  the exact bytes the human saw; the signer signs only the proposal that matches,
  exactly once (consumption in its trusted base) — and only after AUTHENTICATING
  the carried approval itself: its own signature verifies, its signer is the
  mandate's granter, and it is a record on the log. All five attacks die at sign-
  time:

    * re-aim to a new payee   -> REFUSED  (bound to a different proposal hash)
    * replay the approved act  -> REFUSED  (the approval was already spent)
    * a scope-only bearer token-> REFUSED  (names no proposal; not honored)
    * a forged approval object -> REFUSED  (its own signature does not verify)
    * an off-log approval      -> REFUSED  (consent that never became a record
                                            is a message, not an approval)

  The residue is where it lands. Binding makes the HUMAN a second signer. The
  approval is only as good as what the human SAW — so the inbox must show the human
  the same bytes the signer signs (review_body() is one projection, used for both).
  Show them less — a summary that hides the payee — and their consent does not
  cover the difference: a confused deputy, the first seam's "sign what you saw"
  property now owed to a human's eyes. ROUTE is not "defer to a human"; it opens a
  second custody boundary where the human is the signer and the proposal-binding is
  the mandate.

  Two boundaries the live seam does NOT remove:

    * availability. A return path is a new place to stall: an approval can be
      dropped or withheld, and escalation blocks. The minimal slice's one-way
      proposal seam could not be starved this way.
    * the human's trusted base. Binding moves the question from the key to the
      review, it does not shrink it — a human who rubber-stamps the inbox is the
      ceremony fatigue key-custody.md §8 already names, now on the second seam.

  Offered as a probe finding — the runtime expression of the second seam
  embodiment_fixture left dead, not settled doctrine. The crypto is real so
  "this approval validates against that one proposal" is a fact; not a security
  product.
""")


if __name__ == "__main__":
    main()

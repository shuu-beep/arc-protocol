#!/usr/bin/env python3
"""
ARC signer-interpretation fixture — two scope readings over one mandate.

What this is
------------
embodiment_fixture applies mandate checks in the signer before Event creation.
This fixture compares two signer interpretation functions over the same mandate,
proposals, and illustrative Ed25519 key.

The strict reading uses an exact category and hard ceiling. The permissive
reading treats subcategories as matching the category prefix and uses a 1.5x
ceiling. These are application-policy functions, and both can produce records
that pass the same illustrative signature check.

The resulting log exposes the proposal outcomes but does not encode which
interpretation function ran. Named observer folds can also return different scope
readings for the same records. For the in-scope proposal, both signer functions
produce the same record bytes because the reading is not a signed field.

Limits:
  * an additional signer ATTEST would be another record under a named evidence
    policy; this fixture does not treat it as independent proof of interpretation;
  * no new event type or primitive. The mandate is the existing
    AUTHORIZE consent.mandate; acts are ATTEST; the difference is in the
    signer process's reading of scope, which is not recorded in the log;
  * no global verifier or meta-authority. Each observer folds locally with its
    own configured reading; the fixture does not designate one as protocol state
    or as proof of the signer's implementation.
  * who actually ran, and what reading it applied, is a private fixture
    stipulation rendered separately; observer folds do not receive it.

A standalone probe, not a custody specification.

Run:  python3 signer_fidelity_fixture.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}


# ===========================================================================
# Illustrative Ed25519 — the RFC 8032 reference, pure stdlib (reused from the
# compromise / embodiment / approval-return fixtures). Deterministic signing lets
# the fixture compare the output bytes produced by its two reading functions.
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
# Event + Proposal — the lean shapes from the prior fixtures.
# ===========================================================================

@dataclass(frozen=True)
class Event:
    id: str
    type: str
    signer: str
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
    """What the agent emits. The signer's reading decides whether to sign it; the
    reading never touches the bytes, so two signers that both sign it emit the
    identical event."""
    predicate: str
    refs: tuple[str, ...] = ()
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""


def verify_log(events: list[Event]) -> None:
    """Fixture replay check: Ed25519 signature and prior KEY registration only.
    It cannot establish signer implementation, mandate reading, or conformance."""
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


def _mint(secret: bytes, pub_hex: str, ts: str, *, type_: str, predicate: str,
          **kw) -> Event:
    """Build and sign one Event. The reading function is not an input; callers
    using the same key, timestamp, and payload produce the same bytes."""
    assert type_ in CANONICAL_TYPES, f"non-canonical type {type_!r}"
    partial = Event(id="", type=type_, signer=pub_hex, predicate=predicate,
                    timestamp=ts, **kw)
    body = partial.signing_bytes()
    sig = ed25519_sign(body, secret, bytes.fromhex(pub_hex)).hex()
    return Event(id="ev:" + hashlib.sha256(body).hexdigest()[:12], type=type_,
                 signer=pub_hex, predicate=predicate, timestamp=ts, signature=sig, **kw)


# ===========================================================================
# The ceremony — mints the mandate the two signers will read differently.
# ===========================================================================

class ColdRootCeremony:
    def __init__(self, *, root_pub: str, root_secret: bytes, log: list[Event]) -> None:
        self._root_secret = root_secret
        self.root_pub = root_pub
        self.log = log

    def _emit(self, ts: str, **kw) -> Event:
        ev = _mint(self._root_secret, self.root_pub, ts, **kw)
        self.log.append(ev)
        return ev

    def register(self, pub: str, ts: str) -> Event:
        return self._emit(ts, type_="KEY", predicate="id.key_register", payload={"key": pub})

    def grant_mandate(self, agent_pub: str, *, context: str, ceiling: int, ts: str) -> Event:
        return self._emit(ts, type_="AUTHORIZE", predicate="consent.mandate",
                          refs=(agent_pub,), scope={"context": context, "max_total_krw": ceiling})


# ===========================================================================
# The two signers use the same key and mandate. They differ only in `reads()` — the
# private interpretation each applies. Neither reading is written anywhere the log
# or a fold can see; only the decision and the resulting bytes are.
# ===========================================================================

@dataclass
class Decision:
    kind: str                          # "signed" | "routed"
    reason: str
    event: Event | None = None


class Signer:
    """Holds the hot key and mandate. `category_ok` and `ceiling_ok` implement
    this fixture's signer-side reading of that mandate."""

    def __init__(self, name: str, reading: str, *, hot_pub: str, hot_secret: bytes,
                 mandate: Event, category_ok: Callable[[str, str], bool],
                 ceiling_ok: Callable[[int, int], bool], log: list[Event]) -> None:
        self.name = name
        self.reading = reading
        self._hot_secret = hot_secret
        self.hot_pub = hot_pub
        self.mandate = mandate
        self._category_ok = category_ok
        self._ceiling_ok = ceiling_ok
        self.log = log

    @property
    def _ceiling(self) -> int:
        return (self.mandate.scope or {}).get("max_total_krw")

    @property
    def _context(self) -> str:
        return (self.mandate.scope or {}).get("context")

    def handle(self, p: Proposal, *, append: bool = True) -> Decision:
        ctx = p.payload.get("context")
        amount = p.payload.get("amount_krw")
        if ctx is not None and not self._category_ok(ctx, self._context):
            return Decision("routed", f"out of the mandate's domain under {self.name}'s "
                            f"reading ({ctx!r} not in {self._context!r})")
        if amount is not None and not self._ceiling_ok(amount, self._ceiling):
            return Decision("routed", f"over the ceiling under {self.name}'s reading "
                            f"({amount} vs {self._ceiling})")
        ev = self._sign(p, append=append)
        return Decision("signed", f"within the mandate under {self.name}'s reading", ev)

    def _sign(self, p: Proposal, *, append: bool = True) -> Event:
        ev = _mint(self._hot_secret, self.hot_pub, p.timestamp, type_="ATTEST",
                   predicate=p.predicate, refs=tuple(p.refs), payload=p.payload)
        if append:
            self.log.append(ev)
        return ev


# Strict reading: exact category, hard ceiling.
def exact_category(ctx: str, mctx: str) -> bool:
    return ctx == mctx


def hard_ceiling(amount: int, cap: int) -> bool:
    return amount <= cap


# Permissive reading: prefix category and 1.5x ceiling.
def prefix_category(ctx: str, mctx: str) -> bool:
    return ctx == mctx or ctx.startswith(mctx + ".")


def soft_ceiling(amount: int, cap: int) -> bool:
    return amount <= int(cap * 1.5)


# ===========================================================================
# An observer's fold — honoring read from the log with the observer's configured reading
# of the mandate. It can re-judge what reached the log; it cannot read which
# reading the signer applied. Note this is the observer interpreting, not the
# signer's interpretation recovered.
# ===========================================================================

def project_honoring(events: list[Event], *, root: str, agent: str,
                     category_ok: Callable[[str, str], bool]) -> list[dict]:
    mandate = next((e for e in events if e.type == "AUTHORIZE"
                    and e.predicate == "consent.mandate" and e.signer == root), None)
    mctx = (mandate.scope or {}).get("context") if mandate else None
    ceiling = (mandate.scope or {}).get("max_total_krw") if mandate else None
    rows = []
    for e in events:
        if e.signer != agent or e.type != "ATTEST":
            continue
        ctx = e.payload.get("context")
        amount = e.payload.get("amount_krw")
        if ctx is not None and not category_ok(ctx, mctx):
            honored, basis = False, "out of the mandate's domain under this observer's reading"
        elif amount is not None and amount > ceiling:
            honored, basis = False, "over the mandate ceiling — signature check passes; fold declines"
        else:
            honored, basis = True, "within this observer's reading of the mandate"
        rows.append({"id": e.id, "context": ctx, "amount": amount,
                     "honored": honored, "basis": basis})
    return rows


# ===========================================================================
# The generated flow — run once, top to bottom.
# ===========================================================================

def generate() -> dict:
    log: list[Event] = []

    def keypair(name: str) -> tuple[bytes, str]:
        sk = hashlib.sha256(b"arc-signer-fidelity/" + name.encode()).digest()
        return sk, ed25519_publickey(sk).hex()

    root_secret, root_pub = keypair("root")
    agent_secret, agent_pub = keypair("agent")

    print("\n1. Fixture setup — one mandate: 'market' acts up to 30000. One hot key is")
    print("   used by two fixture signer functions with different readings.")
    ceremony = ColdRootCeremony(root_pub=root_pub, root_secret=root_secret, log=log)
    ceremony.register(root_pub, "2026-06-11T09:00:00Z")
    ceremony.register(agent_pub, "2026-06-11T09:01:00Z")
    mandate = ceremony.grant_mandate(agent_pub, context="market", ceiling=30000,
                                     ts="2026-06-11T09:02:00Z")

    # Two signers, same key and mandate, different readings. The strict signer
    # writes to a scratch log; the permissive signer writes the displayed log.
    strict = Signer("the strict signer", "exact category · hard ceiling",
                    hot_pub=agent_pub, hot_secret=agent_secret, mandate=mandate,
                    category_ok=exact_category, ceiling_ok=hard_ceiling, log=[])
    permissive = Signer("the permissive signer", "prefix category · soft ceiling (1.5x)",
                        hot_pub=agent_pub, hot_secret=agent_secret, mandate=mandate,
                        category_ok=prefix_category, ceiling_ok=soft_ceiling, log=log)

    proposals = [
        ("in-scope payment", Proposal(
            predicate="commerce.payment_result", refs=(mandate.id,),
            payload={"result": "confirmed", "amount_krw": 20000, "context": "market"},
            timestamp="2026-06-11T10:00:00Z")),
        ("over-ceiling payment", Proposal(
            predicate="commerce.payment_result", refs=(mandate.id,),
            payload={"result": "confirmed", "amount_krw": 40000, "context": "market"},
            timestamp="2026-06-11T10:01:00Z")),
        ("adjacent-category payment", Proposal(
            predicate="commerce.payment_result", refs=(mandate.id,),
            payload={"result": "confirmed", "amount_krw": 15000, "context": "market.giftcard"},
            timestamp="2026-06-11T10:02:00Z")),
    ]

    print("\n2. The same proposals under strict and permissive readings")
    print("   functions use the same mandate and illustrative key.")
    rows = []
    for label, p in proposals:
        ds = strict.handle(p, append=False)               # comparison reading
        dp = permissive.handle(p, append=True)            # displayed log
        rows.append({"label": label, "strict": ds, "permissive": dp,
                     "amount": p.payload.get("amount_krw"),
                     "context": p.payload.get("context")})
        print(f"   {label:<28} strict={ds.kind.upper():<7} permissive={dp.kind.upper()}")

    # For the in-scope act both readings sign and produce identical bytes.
    p_inscope = proposals[0][1]
    ev_strict = strict._sign(p_inscope, append=False)
    ev_permissive = next(r["permissive"].event for r in rows
                         if r["label"] == "in-scope payment")
    identical = (ev_strict.signature == ev_permissive.signature
                 and ev_strict.id == ev_permissive.id)

    verify_log(log)
    return {"log": log, "root": root_pub, "agent": agent_pub, "rows": rows,
            "inscope_identical": identical, "inscope_id": ev_permissive.id,
            "mandate_id": mandate.id}


# ===========================================================================
# Observers — two readings of the same displayed log.
# ===========================================================================

OBSERVERS = [
    {"name": "strict observer", "category_ok": exact_category,
     "blurb": "reads 'market' exactly"},
    {"name": "lenient observer", "category_ok": prefix_category,
     "blurb": "reads 'market' as a prefix"},
]


def main() -> None:
    ctx = generate()
    log, root, agent = ctx["log"], ctx["root"], ctx["agent"]

    print("\n3. Records appended to the log — each displayed act passes the illustrative")
    print("   signature and key-registration checks; the signer reading is not encoded.")
    for e in log:
        if e.signer == agent and e.type == "ATTEST":
            print(f"     [{e.id}]  {e.payload.get('context'):<16} "
                  f"{e.payload.get('amount_krw')} KRW")

    print("\n4. Two observers fold the same log using their configured readings of the")
    print("   mandate. This is the observer's configured interpretation; the displayed")
    print("   record does not identify which signer reading ran.")
    projs = {o["name"]: project_honoring(log, root=root, agent=agent,
                                         category_ok=o["category_ok"]) for o in OBSERVERS}
    for o in OBSERVERS:
        print(f"\n   {o['name']} ({o['blurb']}):")
        for r in projs[o["name"]]:
            verdict = "HONORED" if r["honored"] else "declined"
            print(f"     {verdict:<8} {r['context']:<16} {r['amount']} KRW — {r['basis']}")

    print("\n" + "=" * 74)
    print("Fixture result — signer and observer readings remain separate")
    print("=" * 74)
    print(f"""
  The permissive signer appends the 40000 record, and both observer folds decline
  to honor it because the recorded amount exceeds the mandate ceiling. For the
  adjacent category, the strict observer declines while the prefix observer
  honors. These are named fixture-policy results.

  The strict and permissive signer functions produce the same in-scope Event
  ({ctx['inscope_id']}, identical = {ctx['inscope_identical']}) because the signed
  fields contain the key and payload, not the interpretation function. The
  illustrative signature check therefore does not identify which reading ran.

  This fixture does not evaluate process isolation, signer compromise, enclave
  attestation, or a production signature profile.
""")


if __name__ == "__main__":
    main()

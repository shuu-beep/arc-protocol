#!/usr/bin/env python3
"""
ARC signer-fidelity fixture — the sign-time wall rests on a trusted reading.

What this is
------------
embodiment_fixture (finding K) moved mandate enforcement from FOLD-time to
SIGN-time: with no key in the agent, the signer refuses out-of-scope proposals
before they become events, so "out-of-scope forgeries never reach the log." That
guarantee has a silent premise — that the signer reads the mandate FAITHFULLY.
custody.ts §8 already names where the premise lives: "ceiling arithmetic stays in
the signer's trusted base, with the key, checked at proposal time." The type
layer cannot hold it; the log cannot witness it. This probe asks what is left
when that reading DRIFTS.

The "lie" here is not a forged signature. The crypto is intact: one real Ed25519
hot key, every act genuinely signed, verify_log passes. The lie is an
INTERPRETATION — a signer that reads the same mandate more loosely than a faithful
one would. Not an evil caricature (that was compromise_fixture's thief); an
ordinary operational drift, the kind that accretes in real systems:

  * a "soft" ceiling — the cap read as operational guidance, not a hard stop, so
    the signer signs a little over "to avoid blocking the operator";
  * a "prefix" category — "market" read as covering "market.giftcard", because
    surely a gift card is a market thing.

Two signers, the SAME hot key, the SAME mandate, the SAME proposals. The faithful
one refuses what the drift admits. Both produce valid signatures. The probe shows
the residue in two honest layers:

  LAYER 1 — observable, as a HONORING DISAGREEMENT, not invisibly. Where the
  act's terms are on the log (an over-ceiling amount), any observer's fold can
  re-read the mandate and decline to honor it: signature valid, fold refuses —
  finding I/G's three layers. So K's clean log was CONTINGENT: a drifted signer
  puts the out-of-scope act on the log, and the observer is back to fold-rejecting
  it. Sign-time enforcement did not REPLACE fold-time interpretation; it added a
  layer that is trustworthy only if the signer is faithful. And where the term is
  AMBIGUOUS (the category), observers legitimately disagree — strict declines,
  lenient honors — with no fact on the log to decide between them.

  LAYER 2 — unobservable: the signer's FIDELITY itself. The reading is applied at
  sign-time and leaves no trace. A faithful signer and a drifted one that both
  sign the same in-scope act produce the BYTE-IDENTICAL event — the bytes are a
  function of key and payload, never of the reading. So a valid signature proves
  the key signed; it does not prove the mandate was read faithfully. Sign-time
  enforcement relocated the interpretation into a private trusted base; it did not
  remove the interpretation residue — it inherited it.

Refusals (as deliberate as the content):
  * NO attested-signer salvation. The fix that suggests itself — have the signer
    ATTEST which reading it applied, or prove it in an enclave — imports a trust
    root ARC does not govern (key-custody §8 enclave attestation; custody.ts §8),
    and a drifted signer would simply attest the drifted reading as if faithful.
    The probe leaves the residue standing; it does not close it.
  * NO new event type or primitive. The mandate is the existing
    AUTHORIZE consent.mandate; acts are ATTEST; the drift lives ENTIRELY in the
    signer process's reading of scope — runtime trusted-base behavior, nothing on
    the log. (The same shape covers a signer that skips approval_seam's binding
    check, or "operationally allows" a self-mint: more readings, same residue.)
  * NO global verifier, NO meta-authority. Each observer folds locally with its
    own reading; none is privileged, none certifies the signer's reading.
  * who actually ran, and what reading it applied, is GROUND TRUTH the generator
    holds, rendered as the omniscient view no observer sees.

A probe, not doctrine — the runtime expression of custody.ts §8's deferral, the
third slice of the embodiment axis (K behind the wall, L the return path, now the
wall's own footing). Not a custody spec.

Run:  python3 signer_fidelity_fixture.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}


# ===========================================================================
# Real Ed25519 — the RFC 8032 reference, pure stdlib (reused verbatim from the
# compromise / embodiment / approval-seam fixtures). Determinism matters here: the
# same key signing the same bytes yields the SAME signature, which is exactly what
# makes "you cannot tell a faithful signer from a drifted one by the bytes" a fact.
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
    """What the agent emits. The signer's READING decides whether to sign it; the
    reading never touches the bytes, so two signers that both sign it emit the
    identical event."""
    predicate: str
    refs: tuple[str, ...] = ()
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""


def verify_log(events: list[Event]) -> None:
    """Verification IS replay: real Ed25519 + signer anchored by a prior KEY
    register. Note what this CANNOT check: which reading the signer applied. Every
    drifted act here verifies — the signature is blind to the interpretation."""
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
    """Build and sign one event. Takes a key, a timestamp, and a payload — NOT a
    reading. Two callers with different readings but the same arguments get the
    same bytes. That is the whole point of LAYER 2."""
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
# The two signers. SAME key, SAME mandate. They differ only in `reads()` — the
# private interpretation each applies. Neither reading is written anywhere the log
# or a fold can see; only the SIGN/ROUTE outcome and the resulting bytes are.
# ===========================================================================

@dataclass
class Decision:
    kind: str                          # "signed" | "routed"
    reason: str
    event: Event | None = None


class Signer:
    """A custody process behind the wall. Holds the hot key + the mandate. Its
    `category_ok` and `ceiling_ok` ARE its reading of the mandate — the trusted
    interpretation surface custody.ts §8 left in the signer's trusted base."""

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


# Faithful readings: exact category, hard ceiling.
def exact_category(ctx: str, mctx: str) -> bool:
    return ctx == mctx


def hard_ceiling(amount: int, cap: int) -> bool:
    return amount <= cap


# Drifted readings: a prefix category and a "soft" ceiling, each a plausible
# operational reinterpretation — not malice, convenience.
def prefix_category(ctx: str, mctx: str) -> bool:
    return ctx == mctx or ctx.startswith(mctx + ".")


def soft_ceiling(amount: int, cap: int) -> bool:
    return amount <= int(cap * 1.5)        # "the cap is guidance; don't block the operator"


# ===========================================================================
# An observer's fold — honoring read off the LOG, with the observer's OWN reading
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
            honored, basis = False, "over the mandate ceiling — valid signature, fold declines"
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

    print("\n1. CEREMONY — one mandate: 'market' acts up to 30000. One hot key behind")
    print("   the wall. The mandate's words are fixed; their READING is not.")
    ceremony = ColdRootCeremony(root_pub=root_pub, root_secret=root_secret, log=log)
    ceremony.register(root_pub, "2026-06-11T09:00:00Z")
    ceremony.register(agent_pub, "2026-06-11T09:01:00Z")
    mandate = ceremony.grant_mandate(agent_pub, context="market", ceiling=30000,
                                     ts="2026-06-11T09:02:00Z")

    # Two signers, SAME key, SAME mandate, different readings. The faithful one
    # writes to a scratch log (its refusals are counterfactual here); the drifted
    # one is the signer that actually ran, writing to the real log.
    faithful = Signer("the faithful signer", "exact category · hard ceiling",
                      hot_pub=agent_pub, hot_secret=agent_secret, mandate=mandate,
                      category_ok=exact_category, ceiling_ok=hard_ceiling, log=[])
    drifted = Signer("the drifted signer", "prefix category · soft ceiling (1.5x)",
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

    print("\n2. THE SAME PROPOSALS, THE TWO READINGS — faithful refuses what the drift")
    print("   admits. Both readings, when they DO sign, sign with the same key.")
    rows = []
    for label, p in proposals:
        df = faithful.handle(p, append=False)            # counterfactual reading
        dd = drifted.handle(p, append=True)              # the signer that ran
        rows.append({"label": label, "faithful": df, "drifted": dd,
                     "amount": p.payload.get("amount_krw"),
                     "context": p.payload.get("context")})
        print(f"   {label:<28} faithful={df.kind.upper():<7} drifted={dd.kind.upper()}")

    # LAYER 2, demonstrated: for the in-scope act both readings sign, the bytes are
    # identical — the signature carries the key, never the reading.
    p_inscope = proposals[0][1]
    ev_faithful = faithful._sign(p_inscope, append=False)
    ev_drifted = next(r["drifted"].event for r in rows if r["label"] == "in-scope payment")
    identical = (ev_faithful.signature == ev_drifted.signature
                 and ev_faithful.id == ev_drifted.id)

    verify_log(log)
    return {"log": log, "root": root_pub, "agent": agent_pub, "rows": rows,
            "inscope_identical": identical, "inscope_id": ev_drifted.id,
            "mandate_id": mandate.id}


# ===========================================================================
# Observers — two readings of the same drifted log.
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

    print("\n3. WHAT REACHED THE LOG — every act here is genuinely signed by the agent")
    print("   key; verify_log passed. The drifted reading is NOT among these bytes.")
    for e in log:
        if e.signer == agent and e.type == "ATTEST":
            print(f"     [{e.id}]  {e.payload.get('context'):<16} "
                  f"{e.payload.get('amount_krw')} KRW")

    print("\n4. TWO OBSERVERS FOLD THE SAME LOG — each with its OWN reading of the")
    print("   mandate. This is the observer interpreting, not the signer's reading")
    print("   recovered (that is gone).")
    projs = {o["name"]: project_honoring(log, root=root, agent=agent,
                                         category_ok=o["category_ok"]) for o in OBSERVERS}
    for o in OBSERVERS:
        print(f"\n   {o['name']} ({o['blurb']}):")
        for r in projs[o["name"]]:
            verdict = "HONORED" if r["honored"] else "declined"
            print(f"     {verdict:<8} {r['context']:<16} {r['amount']} KRW — {r['basis']}")

    print("\n" + "=" * 74)
    print("THE FINDING — sign-time enforcement rests on the signer's reading")
    print("=" * 74)
    print(f"""
  embodiment_fixture (finding K) promised that out-of-scope acts never reach the
  log, because the signer refuses them before they become events. That holds only
  if the signer reads the mandate faithfully. Here the same hot key, behind the
  same mandate, is read with an ordinary operational drift — a soft ceiling, a
  prefix category — and the wall moves. Two honest layers:

  LAYER 1 — observable, as a honoring disagreement (not invisibly):
    * the over-ceiling 40000 IS on the log now, genuinely signed. Both observers'
      folds decline to honor it — signature valid, fold refuses. K's clean log was
      CONTINGENT on the signer's fidelity; lose it and the out-of-scope act is back
      in front of every reader's fold, exactly the fold-time work K moved away from.
      Sign-time enforcement did not replace fold-time interpretation — it added a
      layer trustworthy only while the signer is faithful.
    * the adjacent-category 'market.giftcard' splits the observers: the strict one
      declines, the lenient one honors. The mandate's word is ambiguous and no fact
      on the log decides — signer legitimacy is observer-relative, the cold-start
      and federation relativity arriving on the enforcement side.

  LAYER 2 — unobservable: the signer's fidelity itself. The in-scope 20000 signed
  by the faithful reading and by the drifted reading is the byte-identical event
  ({ctx['inscope_id']}, identical = {ctx['inscope_identical']}): the bytes are a
  function of the key and the payload, never of the reading. A valid signature
  proves the key signed; it does NOT prove the mandate was read faithfully. You
  cannot tell a faithful signer from a drifted one — or from a compromised one —
  by an event it produced.

  So process separation (K) narrows custody EXPOSURE — fewer places hold the key —
  but it does not CERTIFY the mandate's interpretation. Sign-time enforcement
  relocated the reading into the signer's private trusted base; it did not remove
  the interpretation residue, it inherited it. The tempting fix — make the signer
  ATTEST or attest-in-hardware which reading it applied — only imports a trust root
  ARC does not govern (key-custody §8), and a drifted signer would attest its drift
  as faithful. The residue is left standing, not closed.

  Offered as a probe finding, not doctrine — the third slice of the embodiment
  axis: K put the key behind the wall, L found the return path was a second
  custody surface, and this finds the wall itself standing on a reading no
  observer can audit. The crypto is real so "the signature carries the key, not
  the reading" is a fact, not a claim; it is not a security product.
""")


if __name__ == "__main__":
    main()

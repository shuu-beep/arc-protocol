#!/usr/bin/env python3
"""
ARC compromise fixture — a stipulated stolen hot key under one fold policy.

What this is
------------
This fixture uses illustrative Ed25519 so it can exercise possession of signing
key material rather than a deterministic hash stub. It tests one mandate and
withdrawal policy; it does not establish custody, payment execution, or a general
damage bound.

This fixture uses an illustrative Ed25519 reference (RFC 8032, pure stdlib).
Compromise is a fixture stipulation: the generator copies the agent's secret
bytes to an attacker label, which can then produce signatures that
pass the fixture verifier against the agent's public key. No payment is executed.

The cast (illustrative keypairs):

    root      fixture key for the mandate, withdrawal, and challenge. The
              generator does not copy this secret to the attacker label.
    agent     hot device key — narrow mandate (context "market", <= 30000).
              Signs the in-scope records the fixture permits.
    attacker  a generator label that uses a copy of the agent secret.
    community the configured adjudicator key honored by this fold. Which
              adjudicator a reader honors is a policy choice (A&C §9).

The flow:

    1. root anchors keys and grants the agent a narrow mandate.
    2. the agent records one pre-compromise in-scope act (20000).
    3. the generator copies the agent secret to the attacker label.
    4. the attacker authors four records whose signatures pass the fixture verifier:
         (a) in-scope      25000, market         -> within the mandate
         (b) over-ceiling   90000, market         -> above the mandate
         (c) out-of-context a non-market act      -> outside the mandate
         (d) an AUTHORIZE naming a fresh attacker key
       This fold honors (a) and declines (b), (c), and (d) under its configured
       scope and signer rules.
    5. root records a withdrawal, read time-scoped.
    6. the attacker label authors one more in-scope record after withdrawal.

What the fold computes:

  * verify_log checks Ed25519 signatures and prior key registration; it cannot
    establish who controlled a secret or whether a payment occurred.
  * fixture-classified honored exposure is the attacker-authored records this
    fold honors: in-scope records inside the stipulated pre-withdrawal window.
    (b)(c)(d) and
    the post-revoke act are each excluded, each with a reason printed.
  * the attacker-authored in-scope record (25000) is different from the
    pre-compromise record (20000), but this fold returns
    the same verdict for both. Scope and the pre-withdrawal window are two modeled
    controls; this is not an exact general damage formula. The in-scope
    pre-withdrawal records are not changed by withdrawal under the time-scoped
    policy; cascade also excludes the pre-compromise history.
    A later CHALLENGE and an ADJUDICATE from the configured adjudicator target
    that record. Under this fold, the root's separate self-ruling remains a
    recorded claim but is not counted because the root is not in the configured
    adjudicator set (registry §4.5, A&C §5).

Limits:
  * who is the attacker is a private fixture classification the generator holds.
    It is rendered separately as generator-only information, and the fold never
    reads it. The
    log alone cannot mark a valid in-scope signature as compromised.
  * no new event type. Theft is not an event (it is the absence of custody);
    revocation is the existing AUTHORIZE consent.withdraw + nullifies; the
    dispute is CHALLENGE + ADJUDICATE.

This is an illustrative viewer fixture, not a custody specification.

Run:  python3 compromise_fixture.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}
READINGS = ("time_scoped", "cascade")


# ===========================================================================
# Illustrative Ed25519 — the RFC 8032 reference, pure stdlib. This is not a
# production cryptographic profile or custody proof.
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
# Keyring — illustrative keypairs. Secrets are derived deterministically from a
# seed so a run is reproducible; a production profile would define key generation.
# distinction this whole probe rests on: holding the SECRET is the power to
# sign. Custody is the question of who holds it. Compromise is the secret moving.
# ===========================================================================

class Keyring:
    """Maps a fixture party name to illustrative Ed25519 key material. The public
    key hex is the record's signer field; secrets are not included in Events."""

    def __init__(self) -> None:
        self._secret: dict[str, bytes] = {}
        self._public: dict[str, bytes] = {}
        self.name_of: dict[str, str] = {}     # pubkey-hex -> readable name

    def generate(self, name: str) -> str:
        sk = hashlib.sha256(b"arc-compromise/" + name.encode()).digest()
        pk = ed25519_publickey(sk)
        self._secret[name] = sk
        self._public[name] = pk
        self.name_of[pk.hex()] = name
        return pk.hex()

    def pub(self, name: str) -> str:
        return self._public[name].hex()

    def steal(self, victim: str, thief: str) -> None:
        """Copy the victim's secret bytes under a new fixture holder label. The
        public key is unchanged, so signatures made with the copy verify against
        the victim's public key."""
        self._secret[thief] = self._secret[victim]
        self._public[thief] = self._public[victim]

    def sign_as(self, holder_secret_of: str, body: bytes, signer_pub_hex: str) -> str:
        """Sign `body` with the secret named by `holder_secret_of` and place
        `signer_pub_hex` in the Event. The fixture separately classifies who invoked
        this operation; the signature check cannot recover that classification."""
        sk = self._secret[holder_secret_of]
        pk = bytes.fromhex(signer_pub_hex)
        return ed25519_sign(body, sk, pk).hex()


# ===========================================================================
# The Event — the same fixture shape over illustrative Ed25519.
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


def verify_log(events: list[Event]) -> None:
    """Fixture replay check: Ed25519 signature and prior KEY registration only.
    It cannot establish secret custody, human authorship, execution, or complete
    conformance."""
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
# The fold: log -> honoring. Parameterized by the revocation reading. This is
# the boundary logic the viewer would render; nothing here reads the private
# generator classification.
# ===========================================================================

def project_compromise(events: list[Event], *, root: str, agent: str,
                       reading: str = "time_scoped",
                       honored_adjudicators: tuple[str, ...] = ()) -> dict:
    """Fold the log into a per-event honoring decision, as seen from `root`.

    `honored_adjudicators` is the reader's POLICY-layer choice (A&C §9) of whose
    ADJUDICATE rulings count — the same honored-adjudicator knob the cold-start
    fixture folds by. Default is none: a per-act void moves nothing unless the
    reader honors its signer. In particular a disputant's ruling on its own
    challenge is just an event on the log — evidence, not authority (registry
    §4.5: ADJUDICATE's authority source is a community process, not an
    individual key).

    `honored` means: a counterparty folding from this root would treat the act as
    carrying the root's authority. The rule, in order:
      * the root's own signature is honored on its own authority;
      * an act bearing a live, sufficient root consent.approval is honored;
      * otherwise the act must sit within the agent's mandate — right context,
        amount within the ceiling — and the mandate must be live at the act's
        time. "Live" is where the two readings split (key-custody §5, the same
        divergence finding G drew on the delegation graph):
          time_scoped  a withdrawal ends mandate force at/after its timestamp;
                       acts the key signed before withdrawal stay honored;
          cascade      acts depending on the withdrawn mandate are not honored
                       by this projection.
      * anything else is not honored under this fixture policy.

    Crucially, this fold cannot see who is the attacker. Different records can
    receive the same verdict. Nothing here is stored; recomputed
    from the log on demand."""
    assert reading in READINGS, f"unknown reading {reading!r}"
    by_id = {e.id: e for e in events}

    # the agent's first mandate from this root, and its withdrawal (if any)
    mandate = next((e for e in events
                    if e.type == "AUTHORIZE" and e.predicate == "consent.mandate"
                    and e.signer == root and e.refs and e.refs[0] == agent), None)
    revoke = next((e for e in events
                   if e.type == "AUTHORIZE" and e.predicate == "consent.withdraw"
                   and e.signer == root and mandate and mandate.id in e.nullifies), None)
    # per-event adjudications: an HONORED ADJUDICATE that voids a specific event.
    # Honored = signed by an adjudicator this reader's policy names; any other
    # ADJUDICATE (including the disputant ruling on its own challenge) stays on
    # the log as evidence and moves nothing here.
    adjudicated_void = {e.refs[0] for e in events
                        if e.type == "ADJUDICATE" and e.predicate == "gov.ruling"
                        and e.payload.get("ruling") == "void" and e.refs
                        and e.signer in honored_adjudicators}

    mscope = (mandate.scope or {}) if mandate else {}
    ceiling = mscope.get("max_total_krw")
    mcontext = mscope.get("context")

    def mandate_live(t: str) -> bool:
        if revoke is None:
            return True
        if reading == "cascade":
            return False
        return t < revoke.timestamp

    def honor(ev: Event) -> dict:
        amount = ev.payload.get("amount_krw")
        ctx = ev.payload.get("context") or (ev.scope or {}).get("context")
        # layer 3: an explicit adjudication can void a specific act outright
        if ev.id in adjudicated_void:
            return {"honored": False, "basis": "adjudicated void — an honored ADJUDICATE "
                    "ruled on this specific event (authority layer, above the fold)"}
        if ev.signer == root:
            return {"honored": True, "basis": "the root's own act, on its own authority"}
        # explicit root approval rides above the mandate chain
        appr = next((by_id[r] for r in ev.refs if r in by_id
                     and by_id[r].predicate == "consent.approval"
                     and by_id[r].signer == root), None)
        if appr is not None:
            c = (appr.scope or {}).get("max_total_krw")
            if amount is None or (c is not None and amount <= c):
                return {"honored": True, "basis": "explicit root approval — independent of the mandate"}
            return {"honored": False, "basis": "root approval exceeded"}
        if ev.signer != agent:
            return {"honored": False, "basis": "no mandate from this root — escalates (weight 0)"}
        if mandate is None:
            return {"honored": False, "basis": "agent holds no mandate from this root"}
        # the agent's own act, judged against its mandate
        if mcontext is not None and ctx is not None and ctx != mcontext:
            return {"honored": False, "basis": f"out of mandate context ({ctx} != {mcontext}) — escalates"}
        if ev.type == "AUTHORIZE":
            return {"honored": False, "basis": "the mandate grants spending, not delegation; "
                    "this agent-signed AUTHORIZE is not root-signed (escalates)"}
        if amount is not None and ceiling is not None and amount > ceiling:
            return {"honored": False, "basis": f"exceeds the mandate ceiling {ceiling} — escalates"}
        if not mandate_live(ev.timestamp):
            if reading == "cascade":
                return {"honored": False, "basis": "mandate withdrawn — not honored by the cascade projection"}
            return {"honored": False, "basis": "after the revocation — mandate no longer live"}
        return {"honored": True, "basis": "within the live mandate (right context, within ceiling)"}

    rows = []
    for e in events:
        if e.signer != agent or e.type not in ("ATTEST", "AUTHORIZE"):
            continue                     # evaluate the agent's pre-compromise and attacker-authored acts;
                                         # root-authored records are handled separately
        h = honor(e)
        rows.append({"id": e.id, "signer": e.signer, "type": e.type,
                     "predicate": e.predicate, "amount": e.payload.get("amount_krw"),
                     "context": e.payload.get("context") or (e.scope or {}).get("context"),
                     "timestamp": e.timestamp, **h})
    return {"reading": reading, "root": root, "agent": agent,
            "mandate_ceiling": ceiling, "mandate_context": mcontext,
            "revoke_ts": revoke.timestamp if revoke else None, "rows": rows}


def modeled_exposure(events: list[Event], fixture_attacker_authored: set[str], *,
                     root: str, agent: str, reading: str = "time_scoped",
                     honored_adjudicators: tuple[str, ...] = ()) -> dict:
    """Fixture-classified honored exposure. This intersects the fold, which does
    not receive `fixture_attacker_authored`, with the generator's private
    classification. An observer folding the log gets the `honored` column without
    that authorship classification and cannot infer secret custody from these
    records."""
    proj = project_compromise(events, root=root, agent=agent, reading=reading,
                              honored_adjudicators=honored_adjudicators)
    forged_rows = [r for r in proj["rows"] if r["id"] in fixture_attacker_authored]
    honored_attacker_authored = [r for r in forged_rows if r["honored"]]
    krw = sum(r["amount"] or 0 for r in honored_attacker_authored)
    return {"reading": reading, "forged_rows": forged_rows,
            "honored_attacker_authored": honored_attacker_authored, "honored_krw": krw,
            "ceiling": proj["mandate_ceiling"], "revoke_ts": proj["revoke_ts"]}


# ===========================================================================
# Participants — each holds one illustrative keypair and emits its own Events. The
# attacker is the exception: it emits with the agent signer field and copied
# secret. `forged` is a stable internal name for a private fixture classification
# that is not passed to the fold.
# ===========================================================================

class Ledger:
    def __init__(self, keyring: Keyring) -> None:
        self.events: list[Event] = []
        self.keyring = keyring
        self.forged: set[str] = set()        # private fixture classification
        self._clock = 0
        self._revoke_clock = 9               # events at/after this are "afternoon"

    def now(self) -> str:
        self._clock += 1
        hour = 10 if self._clock < self._revoke_clock else 16
        return f"2026-06-09T{hour:02d}:{self._clock:02d}:00Z"

    def emit(self, *, holder: str, signer_name: str, type_: str, predicate: str,
             forged: bool = False, **kw) -> Event:
        assert type_ in CANONICAL_TYPES, f"non-canonical type {type_!r}"
        signer_pub = self.keyring.pub(signer_name)
        partial = Event(id="", type=type_, signer=signer_pub, predicate=predicate,
                        timestamp=self.now(), **kw)
        body = partial.signing_bytes()
        sig = self.keyring.sign_as(holder, body, signer_pub)
        ev = Event(id="ev:" + hashlib.sha256(body).hexdigest()[:12], type=type_,
                   signer=signer_pub, predicate=predicate, timestamp=partial.timestamp,
                   signature=sig, **kw)
        self.events.append(ev)
        if forged:
            self.forged.add(ev.id)
        tag = "  <-- ATTACKER-AUTHORED (uses the copied agent secret)" if forged else ""
        who = self.keyring.name_of[signer_pub]
        print(f"    -> {who:<8} {type_} {predicate}  [{ev.id}] @ {ev.timestamp}{tag}")
        return ev


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


# ===========================================================================
# The generated flow — run once, top to bottom.
# ===========================================================================

def generate_log() -> tuple[list[Event], set[str], Keyring, dict]:
    kr = Keyring()
    for name in ("root", "agent", "attacker_key", "community"):
        kr.generate(name)
    led = Ledger(kr)
    root_pub, agent_pub = kr.pub("root"), kr.pub("agent")
    community_pub = kr.pub("community")

    print("\n1. Identity — the cold root anchors itself and its hot agent key")
    led.emit(holder="root", signer_name="root", type_="KEY", predicate="id.key_register",
             payload={"key": root_pub})
    led.emit(holder="agent", signer_name="agent", type_="KEY", predicate="id.key_register",
             payload={"key": agent_pub})
    say("fixture", "the generator keeps separate root and agent key material")

    print("\n2. A narrow mandate — the hot key may sign market acts up to 30000")
    mandate = led.emit(holder="root", signer_name="root", type_="AUTHORIZE",
                       predicate="consent.mandate", refs=(agent_pub,),
                       scope={"context": "market", "max_total_krw": 30000})

    print("\n3. The agent records a pre-compromise in-scope act")
    legit = led.emit(holder="agent", signer_name="agent", type_="ATTEST",
                     predicate="commerce.payment_result", refs=(mandate.id,),
                     payload={"result": "confirmed", "amount_krw": 20000,
                              "context": "market", "provider": "mock_pay"})

    print("\n4. Private fixture stipulation — copy the agent secret to the attacker label")
    kr.steal(victim="agent", thief="agent_stolen")
    say("fixture", "from here the stipulated attacker uses the agent secret")

    print("\n5. The attacker authors four records — each passes the fixture verifier")
    forge_a = led.emit(holder="agent_stolen", signer_name="agent", type_="ATTEST",
                       predicate="commerce.payment_result", refs=(mandate.id,), forged=True,
                       payload={"result": "confirmed", "amount_krw": 25000,
                                "context": "market", "provider": "mock_pay"})
    led.emit(holder="agent_stolen", signer_name="agent", type_="ATTEST",
             predicate="commerce.payment_result", refs=(mandate.id,), forged=True,
             payload={"result": "confirmed", "amount_krw": 90000,
                      "context": "market", "provider": "mock_pay"})
    led.emit(holder="agent_stolen", signer_name="agent", type_="ATTEST",
             predicate="identity.binding", refs=(mandate.id,), forged=True,
             payload={"claim": "controls_external_account", "context": "identity"})
    led.emit(holder="agent_stolen", signer_name="agent", type_="AUTHORIZE",
             predicate="consent.mandate", refs=(kr.pub("attacker_key"),), forged=True,
             scope={"context": "market", "max_total_krw": 1000000})
    say("attacker", "the authored AUTHORIZE uses the agent signer, not the root signer")

    print("\n6. The root records a withdrawal (time-scoped read)")
    say("root", "the fixture signs the withdrawal with the separate root key")
    led.emit(holder="root", signer_name="root", type_="AUTHORIZE", predicate="consent.withdraw",
             refs=(agent_pub,), nullifies=(mandate.id,),
             payload={"reason": "key_compromise"})

    print("\n7. The attacker label authors one more in-scope record after withdrawal")
    led.emit(holder="agent_stolen", signer_name="agent", type_="ATTEST",
             predicate="commerce.payment_result", refs=(mandate.id,), forged=True,
             payload={"result": "confirmed", "amount_krw": 25000,
                      "context": "market", "provider": "mock_pay"})

    print("\n8. The fixture adds a challenge targeting the attacker-authored record")
    print("   and a ruling from the configured community adjudicator.")
    led.emit(holder="community", signer_name="community", type_="KEY",
             predicate="id.key_register", payload={"key": community_pub})
    led.emit(holder="root", signer_name="root", type_="CHALLENGE", predicate="dispute.open",
             refs=(forge_a.id,), payload={"reason": "not_authorized_by_holder"})
    say("root", "also records a self-ruling; this fold does not count its signer")
    self_ruling = led.emit(holder="root", signer_name="root", type_="ADJUDICATE",
                           predicate="gov.ruling", refs=(forge_a.id,),
                           payload={"ruling": "void", "context": "market"})
    say("community", "records the ruling counted by this fixture's adjudicator policy")
    ruling = led.emit(holder="community", signer_name="community", type_="ADJUDICATE",
                      predicate="gov.ruling", refs=(forge_a.id,),
                      payload={"ruling": "void", "context": "market"})

    verify_log(led.events)
    print(f"\nGenerated log: {len(led.events)} hand-authored fixture events, illustrative Ed25519.")
    print("verify_log checks signatures and prior key registration only; it cannot")
    print("establish secret custody, authorship, or payment execution.")
    meta = {"root": root_pub, "agent": agent_pub, "community": community_pub,
            "legit_id": legit.id, "forge_a_id": forge_a.id,
            "self_ruling_id": self_ruling.id, "ruling_id": ruling.id}
    return led.events, led.forged, kr, meta


# ===========================================================================
# Standalone run — run the fixture checks, compare both fold readings, and report
# fixture-classified exposure before per-act adjudication.
# ===========================================================================

def _verdict(honored: bool) -> str:
    return "HONORED" if honored else "rejected"


def main() -> None:
    events, forged, kr, meta = generate_log()
    root, agent = meta["root"], meta["agent"]
    legit_id, forge_a_id = meta["legit_id"], meta["forge_a_id"]
    # this reader's policy-layer choice (A&C §9): whose ADJUDICATE counts
    honors = (meta["community"],)

    # Two views of the same log. `pre` is the fixture record set immediately after
    # withdrawal and before the individual challenge; `events` includes the later
    # adjudication. The two mechanisms affect different records under this policy.
    pre = [e for e in events if e.type not in ("CHALLENGE", "ADJUDICATE")]

    print("\n" + "=" * 72)
    print("Generator-only classification — not supplied to the observer fold")
    print("=" * 72)
    name = lambda pk: kr.name_of.get(pk, pk[:8])
    for e in events:
        if e.signer == agent and e.type in ("ATTEST", "AUTHORIZE"):
            mark = "ATTACKER-AUTHORED" if e.id in forged else "PRE-COMPROMISE"
            amt = f"{e.payload.get('amount_krw')} KRW" if e.payload.get("amount_krw") else "-"
            print(f"    {mark} {name(e.signer):<8} {e.predicate:<26} {amt:>11}  [{e.id}]")

    print("\n" + "=" * 72)
    print("Selected fold, just after the revocation — what an observer folding from the")
    print("root actually sees. No authorship-classification column exists here. A record")
    print("passing the signature check is then read under the selected scope policy.")
    print("=" * 72)
    for reading in READINGS:
        proj = project_compromise(pre, root=root, agent=agent, reading=reading,
                                  honored_adjudicators=honors)
        print(f"\n  reading = {reading}   (mandate: {proj['mandate_context']} <= "
              f"{proj['mandate_ceiling']}; revoked @ {proj['revoke_ts']})")
        for r in proj["rows"]:
            amt = f"{r['amount']} KRW" if r["amount"] else "-"
            print(f"    {_verdict(r['honored']):<8} {r['predicate']:<26} {amt:>11} "
                  f"[{r['id']}] — {r['basis']}")

    print("\n" + "=" * 72)
    print("Fixture-classified honored exposure — attacker-authored records this")
    print("fold honors; no payment or exact damage is established.")
    print("=" * 72)
    for reading in READINGS:
        exposure = modeled_exposure(pre, forged, root=root, agent=agent, reading=reading,
                                    honored_adjudicators=honors)
        print(f"\n  reading = {reading}")
        for r in exposure["forged_rows"]:
            amt = f"{r['amount']} KRW" if r["amount"] else "-"
            flag = "==> HONORED" if r["honored"] else "not honored"
            print(f"    {flag} {r['predicate']:<26} {amt:>11} [{r['id']}] — {r['basis']}")
        print(f"    --> honored attacker-authored fixture records: "
              f"{len(exposure['honored_attacker_authored'])} event(s), "
              f"{exposure['honored_krw']} KRW in recorded claims "
              f"(mandate ceiling {exposure['ceiling']} per act)")

    print("\n" + "=" * 72)
    print("Modeled controls — scope and pre-withdrawal time")
    print("=" * 72)
    ts = project_compromise(pre, root=root, agent=agent, reading="time_scoped",
                            honored_adjudicators=honors)
    cas = project_compromise(pre, root=root, agent=agent, reading="cascade",
                             honored_adjudicators=honors)
    row = lambda proj, eid: next(r for r in proj["rows"] if r["id"] == eid)
    print("\n  Pre-compromise and attacker-authored records, side by side (pre-dispute):")
    for label, eid in (("pre-compromise (20000)", legit_id),
                       ("attacker-authored (25000)", forge_a_id)):
        t, c = row(ts, eid), row(cas, eid)
        print(f"    {label:<26} time_scoped={_verdict(t['honored'])}, "
              f"cascade={_verdict(c['honored'])}  [{eid}]")
    print("""
  The fold returns the same pair of verdicts for both records,
  even though the records have different payloads, IDs, and bytes. Both carry an
  agent signature, are in context, within the ceiling, and precede withdrawal.
  The private generator classification assigns their authors differently.

  Under this policy the honored exposure is limited by
  the mandate's per-record scope (the 90000 and out-of-context records were declined
  by scope alone; the self-elevation is not root-signed). The number of in-scope
  attacker-authored records honored is
  affected by how many records precede withdrawal. This is not a general
  damage formula and no payment is executed.

  The time-scoped policy preserves pre-withdrawal records, including both fixture
  classes. The cascade policy excludes both from its current honoring result.
  Neither reading excludes only the attacker-authored class, because the fold is
  not given the private authorship classification.""")

    print("\n" + "=" * 72)
    print("Per-act adjudication after withdrawal")
    print("=" * 72)
    upto_self = events[:next(i for i, e in enumerate(events)
                             if e.id == meta["self_ruling_id"]) + 1]
    mid = project_compromise(upto_self, root=root, agent=agent, reading="time_scoped",
                             honored_adjudicators=honors)
    fm = row(mid, forge_a_id)
    print("\n  First, the root's self-ruling is present but its signer is not in the")
    print("  configured adjudicator set (registry §4.5):")
    print(f"    attacker-authored (25000)  {_verdict(fm['honored'])}  [{forge_a_id}] — {fm['basis']}")
    print(f"    (the root's self-ruling [{meta['self_ruling_id']}] passes the fixture checks;")
    print(f"     it is not an honored adjudicator, so the fold does not count it)")
    full_ts = project_compromise(events, root=root, agent=agent, reading="time_scoped",
                                 honored_adjudicators=honors)
    lt, ft = row(full_ts, legit_id), row(full_ts, forge_a_id)
    print(f"\n  Then the configured community ruling is included (full log, time_scoped):")
    print(f"    pre-compromise (20000)     {_verdict(lt['honored'])}  [{legit_id}] — {lt['basis']}")
    print(f"    attacker-authored (25000)  {_verdict(ft['honored'])}  [{forge_a_id}] — {ft['basis']}")
    print("""
  Now they separate because a CHALLENGE and honored ADJUDICATE target the 25000
  record using the fixture's off-log authorship stipulation. The 20000 record is
  not targeted and remains honored under this policy.
  The root's self-ruling is not counted because its signer is outside this
  fixture's configured adjudicator set. Which adjudicator a reader honors is a
  policy choice (registry §4.5, A&C §9).

  This fixture represents withdrawal and dispute with the current Event types;
  theft remains a private fixture stipulation rather than an Event.
""")


if __name__ == "__main__":
    main()

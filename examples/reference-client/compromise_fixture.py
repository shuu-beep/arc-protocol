#!/usr/bin/env python3
"""
ARC compromise fixture — a stolen hot key, and the exact size of the damage.

What this is
------------
Every probe before this one ran on a mock signature, because every question
before this one lived INSIDE the log. Custody lives outside it: the open claim
in key-custody.md §5 is that a compromised hot key can do *exactly* what its
mandate covers — nothing more — and that recovery is the composition of two
mechanisms the canon already has (time-scoped revocation + mandate death). That
claim cannot be tested on a hash that pretends to be a signature. It needs a
real one.

So this fixture uses REAL Ed25519 (the RFC 8032 reference, pure stdlib — no
dependency, still standalone-runnable). Keys are genuine keypairs: a secret that
signs, a public value that verifies. Compromise is modeled honestly — the
attacker EXFILTRATES the agent's secret bytes (the custody failure: a hot key
was resident on a device and stolen) and from then on produces signatures that
genuinely verify against the agent's public key. No forgery of math; a real
theft of the thing custody is supposed to protect.

The cast (real keys):

    root      cold ceremonial key — the human. Signs rarely: the mandate, the
              revocation, the challenge. NEVER resident where a runtime reaches
              it, so the attacker never holds it. The DISPUTANT — it invokes the
              commons; it does not judge its own challenge.
    agent     hot device key — narrow mandate (context "market", <= 30000).
              Signs the in-scope acts the mandate covers, without re-asking.
    attacker  holds NO key of its own that matters — it holds the agent's
              stolen secret, and signs AS the agent.
    community the market community's adjudicating key — the commons authority
              (event-registry §4.5: ADJUDICATE's authority source is a community
              process, not an individual key). The only signer whose per-act
              void the fold honors, and WHICH adjudicator a reader honors is the
              reader's policy choice (A&C §9), exactly like coldstart's
              honored-adjudicator knob.

The flow:

    1. root anchors keys and grants the agent a narrow mandate.
    2. the agent acts once, legitimately, in scope (20000).
    3. COMPROMISE — an out-of-log fact. The attacker now has the agent's secret.
    4. the attacker forges four events, each a real valid signature:
         (a) in-scope      25000, market         -> within the mandate
         (b) over-ceiling   90000, market         -> above the mandate
         (c) out-of-context a non-market act      -> outside the mandate
         (d) self-elevation AUTHORIZE to a fresh attacker key -> tries to escape
       (a) is the dangerous one. (b)(c) are bounded by scope. (d) fails on the
       tier line: the attacker has the HOT key, not the cold root, and cannot
       forge the root's signature, so it cannot grant itself authority.
    5. root (cold key) REVOKES, read time-scoped.
    6. the attacker, still holding the secret, forges one more in-scope act
       AFTER the revoke (25000 again).

What the fold computes, and what it forces:

  * verify_log PASSES on every forgery. A valid signature is a LOG FACT; it says
    a key signed, and the key did. Custody failure is invisible at the signature
    layer. What bounds the damage is not the signature — it is the mandate fold.
  * blast radius = the set of forged events the fold HONORS = exactly the
    in-scope forgeries inside the window (compromise, revocation). (b)(c)(d) and
    the post-revoke act are each excluded, each with a reason printed.
  * the sharpening of §5 this probe surfaces: the in-scope forgery (25000) is
    BYTE-INDISTINGUISHABLE from the legitimate act (20000) — same scope, both
    honored under the time-scoped reading, neither honored under cascade. The fold
    returns the SAME verdict for both. So the blast radius is not "mandate scope"
    alone; it is mandate scope x detection latency, and the in-scope
    pre-revocation window is UNRECOVERABLE BY REVOCATION ALONE. Time-scoped
    revocation preserves the forgery; cascade declines to honor the honest history too.
    Surgically removing only the compromised act needs per-act ADJUDICATION — the
    human files a CHALLENGE, and an ADJUDICATE from the community adjudicator the
    reader honors voids that one event. The disputant cannot be the judge: the
    root's own ADJUDICATE lands on the log and verifies (events are evidence),
    but the fold counts rulings only from an honored adjudicator, so a
    self-ruling moves nothing (registry §4.5, A&C §5). The three-layer split
    again: signature valid (log) / scope honored (fold) / adjudicated void
    (authority).

Refusals (as deliberate as the content):
  * who is the attacker is GROUND TRUTH the generator holds because it wrote the
    flow. It is rendered as "the omniscient view, available to no observer" and
    the fold never reads it — exactly the cold-start fixture's discipline. The
    log alone cannot mark a valid in-scope signature as compromised.
  * no new event type. Theft is not an event (it is the absence of custody);
    revocation is the existing AUTHORIZE consent.withdraw + nullifies; the
    dispute is CHALLENGE + ADJUDICATE.

Deliberately small, real where it must be (the keys), mock nowhere that matters.
A fixture for the viewer; a probe when run directly. Not a custody spec, not
doctrine — the adversarial test key-custody.md §5 marked as owed, now run.

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
# Real Ed25519 — the RFC 8032 reference, pure stdlib. Slow but genuine: a
# secret signs, a public value verifies, and you cannot produce a passing
# signature without the secret. This is the whole point of a CUSTODY probe —
# the signature has to mean something for "a stolen key" to mean anything.
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
# Keyring — real keypairs. Secrets are derived deterministically from a seed so
# a run is reproducible; in the real world they would be 32 random bytes. The
# distinction this whole probe rests on: holding the SECRET is the power to
# sign. Custody is the question of who holds it. Compromise is the secret moving.
# ===========================================================================

class Keyring:
    """Maps a party name -> its real Ed25519 (secret, public). The public key
    hex IS the signer identity on the log; secrets never appear on the log."""

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
        """The compromise, made literal: the victim's SECRET bytes are copied
        into the thief's possession. Nothing else changes — same secret, so the
        thief now produces signatures indistinguishable from the victim's. This
        is the only line in the file that models custody failing."""
        self._secret[thief] = self._secret[victim]
        self._public[thief] = self._public[victim]

    def sign_as(self, holder_secret_of: str, body: bytes, signer_pub_hex: str) -> str:
        """Sign `body` with the secret of `holder_secret_of`, asserting authorship
        by `signer_pub_hex`. For an honest signer the two refer to the same key.
        For the ATTACKER they also refer to the same key — because the attacker
        STOLE the agent's secret. That is exactly why the forgery verifies."""
        sk = self._secret[holder_secret_of]
        pk = bytes.fromhex(signer_pub_hex)
        return ed25519_sign(body, sk, pk).hex()


# ===========================================================================
# The Event — same lean shape as the other probes, now over a real signature.
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
    """Verification IS replay: real Ed25519 check + signer anchored by a prior
    KEY register. Note what it CANNOT check: whether the secret was stolen. The
    attacker's forgeries pass here in full — a valid signature proves a key
    signed, and the agent's key really did. Custody is invisible to this layer."""
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
# the boundary logic the viewer would render; nothing here reads ground truth.
# ===========================================================================

def project_compromise(events: list[Event], *, root: str, agent: str,
                       reading: str = "time_scoped",
                       honored_adjudicators: tuple[str, ...] = ()) -> dict:
    """Fold the log into a per-event honoring decision, as seen from `root`.

    `honored_adjudicators` is the reader's POLICY-layer choice (A&C §9) of whose
    ADJUDICATE rulings count — the same honored-adjudicator knob the cold-start
    fixture folds by. Default is none: a per-act void moves nothing unless the
    reader honors its signer. In particular a disputant's ruling on its OWN
    challenge is just an event on the log — evidence, not authority (registry
    §4.5: ADJUDICATE's authority source is a community process, not an
    individual key).

    `honored` means: a counterparty folding from this root would treat the act as
    carrying the root's authority. The rule, in order:
      * the root's own signature is honored on its own authority;
      * an act bearing a live, sufficient root consent.approval is honored;
      * otherwise the act must sit within the agent's mandate — right context,
        amount within the ceiling — AND the mandate must be LIVE at the act's
        time. "Live" is where the two readings split (key-custody §5, the same
        divergence finding G drew on the delegation graph):
          time_scoped  a withdrawal ends mandate force at/after its timestamp;
                       acts the key signed BEFORE the revoke stay honored;
          cascade      acts depending on the withdrawn mandate are not honored
                       by this projection.
      * anything else ESCALATES — i.e. is not honored without a human.

    Crucially, this fold cannot see who is the attacker. An in-scope forgery and
    a genuine act are the same object to it. Nothing here is stored; recomputed
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
            return {"honored": False, "basis": "the mandate grants spending, not the power to "
                    "delegate — a hot key cannot mint authority (escalates)"}
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
            continue                     # judge the agent's acts (genuine and forged); the
                                         # root's own grants/revokes/rulings ARE the authority
        h = honor(e)
        rows.append({"id": e.id, "signer": e.signer, "type": e.type,
                     "predicate": e.predicate, "amount": e.payload.get("amount_krw"),
                     "context": e.payload.get("context") or (e.scope or {}).get("context"),
                     "timestamp": e.timestamp, **h})
    return {"reading": reading, "root": root, "agent": agent,
            "mandate_ceiling": ceiling, "mandate_context": mcontext,
            "revoke_ts": revoke.timestamp if revoke else None, "rows": rows}


def blast_radius(events: list[Event], ground_truth_forged: set[str], *,
                 root: str, agent: str, reading: str = "time_scoped",
                 honored_adjudicators: tuple[str, ...] = ()) -> dict:
    """The actual damage: forged events the fold HONORS. Computed by INTERSECTING
    the fold (which cannot see `ground_truth_forged`) with the omniscient set
    (which no observer can see). The point of separating them: an observer
    folding the log gets the `honored` column WITHOUT the `forged` column — it
    cannot tell a compromised honored act from a legitimate one."""
    proj = project_compromise(events, root=root, agent=agent, reading=reading,
                              honored_adjudicators=honored_adjudicators)
    forged_rows = [r for r in proj["rows"] if r["id"] in ground_truth_forged]
    honored_damage = [r for r in forged_rows if r["honored"]]
    krw = sum(r["amount"] or 0 for r in honored_damage)
    return {"reading": reading, "forged_rows": forged_rows,
            "honored_damage": honored_damage, "honored_krw": krw,
            "ceiling": proj["mandate_ceiling"], "revoke_ts": proj["revoke_ts"]}


# ===========================================================================
# Participants — each holds one keypair and emits its OWN signed events. The
# attacker is the exception: it emits AS the agent, with the agent's stolen
# secret. `forged` records ground truth — who actually held the pen — and is
# NEVER passed to the fold.
# ===========================================================================

class Ledger:
    def __init__(self, keyring: Keyring) -> None:
        self.events: list[Event] = []
        self.keyring = keyring
        self.forged: set[str] = set()        # GROUND TRUTH — omniscient only
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
        tag = "  <-- FORGED (attacker holds the agent's stolen secret)" if forged else ""
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
    say("custody", "root key is COLD (ceremonial); agent key is HOT (resident on the device)")

    print("\n2. A narrow mandate — the hot key may sign market acts up to 30000")
    mandate = led.emit(holder="root", signer_name="root", type_="AUTHORIZE",
                       predicate="consent.mandate", refs=(agent_pub,),
                       scope={"context": "market", "max_total_krw": 30000})

    print("\n3. The agent acts legitimately, in scope")
    legit = led.emit(holder="agent", signer_name="agent", type_="ATTEST",
                     predicate="commerce.payment_result", refs=(mandate.id,),
                     payload={"result": "confirmed", "amount_krw": 20000,
                              "context": "market", "provider": "mock_pay"})

    print("\n4. COMPROMISE (an out-of-log fact) — the attacker exfiltrates the")
    print("   agent's secret. No event marks this; theft is the ABSENCE of custody.")
    kr.steal(victim="agent", thief="agent_stolen")
    say("omniscient", "from here the attacker signs AS the agent, with valid signatures")

    print("\n5. The attacker forges four events — every signature genuinely verifies")
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
    say("attacker", "(d) tries to grant ITSELF a mandate — but cannot forge the COLD root")

    print("\n6. Detection + recovery — the COLD root revokes (time-scoped read)")
    say("root", "the attacker never had this key; revocation is signed from the cold ceremony")
    led.emit(holder="root", signer_name="root", type_="AUTHORIZE", predicate="consent.withdraw",
             refs=(agent_pub,), nullifies=(mandate.id,),
             payload={"reason": "key_compromise"})

    print("\n7. The attacker still holds the secret — forges one more in-scope act")
    led.emit(holder="agent_stolen", signer_name="agent", type_="ATTEST",
             predicate="commerce.payment_result", refs=(mandate.id,), forged=True,
             payload={"result": "confirmed", "amount_krw": 25000,
                      "context": "market", "provider": "mock_pay"})

    print("\n8. The residue — the human KNOWS (out of band) that (a) was not theirs,")
    print("   and disputes that ONE event. Revocation could not reach it; adjudication can.")
    print("   The dispute routes to the commons: the market community anchors its key.")
    led.emit(holder="community", signer_name="community", type_="KEY",
             predicate="id.key_register", payload={"key": community_pub})
    led.emit(holder="root", signer_name="root", type_="CHALLENGE", predicate="dispute.open",
             refs=(forge_a.id,), payload={"reason": "not_authorized_by_holder"})
    say("root", "tempted to close its own case, the disputant signs a ruling itself —")
    say("root", "it verifies (events are evidence), but no honoring fold will count it")
    self_ruling = led.emit(holder="root", signer_name="root", type_="ADJUDICATE",
                           predicate="gov.ruling", refs=(forge_a.id,),
                           payload={"ruling": "void", "context": "market"})
    say("community", "the commons rules on the disputed act (registry §4.5: community")
    say("community", "process, not an individual key — and not the disputant)")
    ruling = led.emit(holder="community", signer_name="community", type_="ADJUDICATE",
                      predicate="gov.ruling", refs=(forge_a.id,),
                      payload={"ruling": "void", "context": "market"})

    verify_log(led.events)
    print(f"\nGenerated log: {len(led.events)} signed events, real Ed25519, none hand-written.")
    print("verify_log PASSES — every forgery included. A valid signature is a log fact;")
    print("it proves the agent's key signed. It cannot prove the human held the key.")
    meta = {"root": root_pub, "agent": agent_pub, "community": community_pub,
            "legit_id": legit.id, "forge_a_id": forge_a.id,
            "self_ruling_id": self_ruling.id, "ruling_id": ruling.id}
    return led.events, led.forged, kr, meta


# ===========================================================================
# Standalone run — verify, fold both ways, size the blast radius, and show the
# residue revocation cannot reach.
# ===========================================================================

def _verdict(honored: bool) -> str:
    return "HONORED" if honored else "rejected"


def main() -> None:
    events, forged, kr, meta = generate_log()
    root, agent = meta["root"], meta["agent"]
    legit_id, forge_a_id = meta["legit_id"], meta["forge_a_id"]
    # this reader's policy-layer choice (A&C §9): whose ADJUDICATE counts
    honors = (meta["community"],)

    # Two views of the same log. `pre` is the world right after the revocation,
    # before the human disputes individual acts — this is where the blast radius
    # is actually measured. `events` is the full log, where adjudication closes
    # the residue. Splitting them is the whole demonstration: revocation and
    # adjudication reach DIFFERENT damage.
    pre = [e for e in events if e.type not in ("CHALLENGE", "ADJUDICATE")]

    print("\n" + "=" * 72)
    print("THE OMNISCIENT VIEW — available to NO observer (the generator wrote the")
    print("flow, so it knows who held the pen; the fold below never sees this).")
    print("=" * 72)
    name = lambda pk: kr.name_of.get(pk, pk[:8])
    for e in events:
        if e.signer == agent and e.type in ("ATTEST", "AUTHORIZE"):
            mark = "FORGED   " if e.id in forged else "genuine  "
            amt = f"{e.payload.get('amount_krw')} KRW" if e.payload.get("amount_krw") else "-"
            print(f"    {mark} {name(e.signer):<8} {e.predicate:<26} {amt:>11}  [{e.id}]")

    print("\n" + "=" * 72)
    print("THE FOLD, just after the revocation — what an observer folding from the")
    print("root actually sees. No 'forged' column exists here. A valid signature in")
    print("scope is honored, whoever held the secret.")
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
    print("BLAST RADIUS — forged events the fold HONORS (the actual damage),")
    print("intersecting the fold with the omniscient set the observer cannot see.")
    print("=" * 72)
    for reading in READINGS:
        br = blast_radius(pre, forged, root=root, agent=agent, reading=reading,
                          honored_adjudicators=honors)
        print(f"\n  reading = {reading}")
        for r in br["forged_rows"]:
            amt = f"{r['amount']} KRW" if r["amount"] else "-"
            flag = "==> DAMAGE" if r["honored"] else "blocked   "
            print(f"    {flag} {r['predicate']:<26} {amt:>11} [{r['id']}] — {r['basis']}")
        print(f"    --> honored damage: {len(br['honored_damage'])} event(s), "
              f"{br['honored_krw']} KRW  (mandate ceiling {br['ceiling']} per act)")

    print("\n" + "=" * 72)
    print("THE FINDING — blast radius = mandate scope x DETECTION LATENCY")
    print("=" * 72)
    ts = project_compromise(pre, root=root, agent=agent, reading="time_scoped",
                            honored_adjudicators=honors)
    cas = project_compromise(pre, root=root, agent=agent, reading="cascade",
                             honored_adjudicators=honors)
    row = lambda proj, eid: next(r for r in proj["rows"] if r["id"] == eid)
    print("\n  The legitimate act and the in-scope forgery, side by side (pre-dispute):")
    for label, eid in (("legitimate (20000)", legit_id), ("FORGED in-scope (25000)", forge_a_id)):
        t, c = row(ts, eid), row(cas, eid)
        print(f"    {label:<26} time_scoped={_verdict(t['honored'])}, "
              f"cascade={_verdict(c['honored'])}  [{eid}]")
    print("""
  Read those two rows. The fold returns the SAME pair of verdicts for both —
  because on the log they ARE the same: a valid agent signature, in context,
  within the ceiling, before the revoke. The only difference lives in the
  omniscient strip the observer cannot see. The honored 25000 IS the blast
  radius — bounded, but not zero.

  So key-custody.md §5 is right but incomplete. The blast radius is bounded by
  the mandate's scope PER ACT (the 90000 and the out-of-context act were rejected
  by scope alone; the self-elevation by the tier line — a hot key cannot mint
  authority) — but the NUMBER of in-scope acts the attacker gets honored is
  bounded only by how long until the revoke. Scope sets the height of the damage;
  detection latency sets its width. The product is the blast radius.

  And the pre-revoke in-scope window is UNRECOVERABLE BY REVOCATION ALONE:
    * time_scoped revocation preserves it (keeps the honest history — and the
      forgery riding inside it);
    * cascade revocation declines to honor it (rejecting the forgery — and the
      honest 20000 act with it in that projection).
  Neither reading excises only the compromise, because the log gives no basis to
  tell the two apart.""")

    print("\n" + "=" * 72)
    print("RECOVERY THE REVOCATION COULD NOT REACH — per-act adjudication")
    print("=" * 72)
    upto_self = events[:next(i for i, e in enumerate(events)
                             if e.id == meta["self_ruling_id"]) + 1]
    mid = project_compromise(upto_self, root=root, agent=agent, reading="time_scoped",
                             honored_adjudicators=honors)
    fm = row(mid, forge_a_id)
    print("\n  First, the guard: the DISPUTANT'S OWN ruling is on the log — and moves")
    print("  nothing (registry §4.5: adjudication is honored by WHO signed it):")
    print(f"    FORGED in-scope (25000)    {_verdict(fm['honored'])}  [{forge_a_id}] — {fm['basis']}")
    print(f"    (the root's self-ruling [{meta['self_ruling_id']}] verifies as an event;")
    print(f"     it is not an honored adjudicator, so the fold does not count it)")
    full_ts = project_compromise(events, root=root, agent=agent, reading="time_scoped",
                                 honored_adjudicators=honors)
    lt, ft = row(full_ts, legit_id), row(full_ts, forge_a_id)
    print(f"\n  Then the COMMUNITY rules on the disputed event (full log, time_scoped):")
    print(f"    legitimate (20000)         {_verdict(lt['honored'])}  [{legit_id}] — {lt['basis']}")
    print(f"    FORGED in-scope (25000)    {_verdict(ft['honored'])}  [{forge_a_id}] — {ft['basis']}")
    print("""
  Now they separate — but only because the human supplied, off the log, the one
  fact the log never held (that 25000 was not theirs), and because the COMMONS
  ruled on it: the root's CHALLENGE invoked the community, and the community's
  ADJUDICATE voids exactly that event while the genuine 20000 stays honored.
  The root's own attempted self-ruling counted for nothing — an adjudication is
  honored by WHO signed it, not by its shape (registry §4.5; which adjudicator a
  reader honors is the reader's policy choice, A&C §9). Three layers, the same
  split every ARC probe finds: signature valid (log) / scope honored (fold) /
  void (authority).

  No new event type was needed — theft is the absence of custody, revocation is
  consent.withdraw + nullifies, the dispute is CHALLENGE + ADJUDICATE. Offered as
  a probe finding extending key-custody.md §5/§8, not as settled doctrine.
""")


if __name__ == "__main__":
    main()

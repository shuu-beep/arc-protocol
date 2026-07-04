#!/usr/bin/env python3
"""
ARC federation fidelity-laundering probe — single file, stdlib only.

What this isolates
------------------
Two earlier probes meet here:

  * finding J (federation bridge, federation_fixture): a community recognizes
    another's authority with a scoped `AUTHORIZE fed.recognition`. The bridge
    *routes* authority, it does not *mint* it; a recognizing fold reads the
    bridge categorically — binding / advisory / ignored — and CONTESTED is an
    honest terminal output.
  * finding M (signer fidelity, signer_fidelity_fixture): a valid signature
    proves a key signed; it does NOT prove the signer read its mandate
    faithfully. Two signers on the same key and the same mandate can DRIFT
    apart in their private reading; the in-scope acts are indistinguishable,
    and the drift only surfaces as honoring-disagreement.

The composition question:

  > When a drifted signer's act crosses a federation bridge, does the bridge
  > LAUNDER the drift?

The setup is two communities. **harbor** grants its agent a market mandate with
an on-log ceiling of 30000. harbor's signer is DRIFTED — it signs acts harbor's
own mandate, as written, would not authorize. **orchard** recognizes harbor's
market authority over a bridge, then folds harbor's acts three ways:

    orchard --AUTHORIZE fed.recognition--> scope={domain:market, community:harbor}
    harbor  --AUTHORIZE consent.mandate--> scope={category:market, max:30000}
    harbor  --AUTHORIZE consent.execute--> three acts, signed under harbor's drift

Nothing here is a new event type. The bridge is one `AUTHORIZE fed.recognition`
(finding J); severance is the existing `nullifies` field; the drift is a signer's
reading (finding M), never an event and never a stored "fidelity score".

The core finding
----------------
Interpretation does not travel on the wire — only events do. So orchard's choice
of how to read the bridge IS the choice of whose interpretation to trust:

  * binding   -> orchard HONORS whatever harbor's signer signed, deferring to
                 harbor's authority WITHOUT re-folding against the on-log mandate.
                 harbor's drift is imported invisibly. The act is LAUNDERED.
  * advisory  -> orchard RE-FOLDS each act under its own faithful reading of the
                 same on-log mandate. The numeric drift (over the recorded
                 ceiling) is caught and DECLINED. The drift is EXPOSED.
  * ignored   -> the act is NOT_RECOGNIZED; nothing transmits.

So finding J's categorical bridge-reading maps exactly onto finding M's fidelity
axis: **binding = import the remote reading (and its drift); advisory = substitute
your own reading (and expose numeric drift); ignored = no transmission.**

But the M residue survives the bridge in BOTH directions. The probe crosses two
drift kinds:

  * NUMERIC drift (an amount over the on-log ceiling): advisory catches it,
    because the violated bound is recorded. binding launders it.
  * CATEGORICAL drift (an ambiguous item harbor calls "market" and orchard would
    not): advisory does not "catch" it — it only DISAGREES (CONTESTED). Two
    faithful folds legitimately read the category differently; neither certifies
    the other. So even advisory does not OBSERVE harbor's faithfulness; it only
    substitutes orchard's judgment. The truly unobservable layer of finding M
    is not closed by re-folding — it is relocated to orchard.

And severance inherits finding J's preserve/cascade asymmetry: orchard can sever
the bridge (`fed.severance` + `nullifies`), but an act already HONORED under
binding — and the payment orchard recorded on its basis — STAYS in orchard's
history. Severance bounds the future; it does not un-launder the past. The
laundered act outlives the bridge.

Deliberately dirty and small. Explicitly:
  * stdlib only, single process, no network, no transport, no storage;
  * signatures are MOCK (a hash, not Ed25519). finding M used real Ed25519 to
    make its in-scope acts BYTE-identical; here the point is reading-semantics
    across the bridge, not custody, so the control asserts EVENT-identity (the
    recognized event is the same object whatever harbor's signer privately read).
    Lifting this to a real-signer fixture is a later upgrade, not this probe;
  * the five canonical types are reused as-is — no new primitive, no stored
    authority object, no stored fidelity score;
  * this is a probe, not a federation spec and not doctrine.

Run:  python3 probe.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}


# ---------------------------------------------------------------------------
# The Event and its mock signing — same lean shape as the other probes.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Event:
    id: str
    type: str
    signer: str
    predicate: str
    timestamp: str
    refs: tuple[str, ...] = ()
    nullifies: tuple[str, ...] = ()      # prior event ids withdrawn (event-registry §4.6)
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


def stub_sign(signer: str, body: bytes) -> str:
    """MOCK. Real ARC uses Ed25519; a hash stands in so replay still verifies.

    Note: a faithful and a drifted signer on the SAME key produce the SAME
    signature on the SAME act — exactly finding M's point. The mock makes that
    free: the signature is a function of (signer, bytes), never of the reading.
    """
    return "stub:" + hashlib.sha256(signer.encode() + body).hexdigest()[:16]


def make(type_: str, signer: str, predicate: str, ts: str, **kw) -> Event:
    assert type_ in CANONICAL_TYPES, f"non-canonical type {type_!r} — forbidden"
    partial = Event(id="", type=type_, signer=signer, predicate=predicate, timestamp=ts, **kw)
    body = partial.signing_bytes()
    return Event(
        id="ev:" + hashlib.sha256(body).hexdigest()[:12],
        type=type_, signer=signer, predicate=predicate, timestamp=ts,
        signature=stub_sign(signer, body), **kw,
    )


def verify_log(events: list[Event]) -> None:
    """Verification IS replay: signature check + signer anchored by a prior KEY.

    Note what verify_log CANNOT see: that harbor's signer drifted. Every act
    below verifies — the signature is honest. Fidelity is not a signature
    property (finding M), and federation does not add one.
    """
    registered: set[str] = set()
    for ev in events:
        if ev.signature != stub_sign(ev.signer, ev.signing_bytes()):
            raise ValueError(f"bad signature on {ev.id}")
        is_root = ev.type == "KEY" and ev.predicate == "id.key_register"
        if not is_root and ev.signer not in registered:
            raise ValueError(f"signer {ev.signer} not anchored by a KEY register ({ev.id})")
        if is_root:
            registered.add(ev.payload["key"])


def as_of(events: list[Event], t: str) -> list[Event]:
    """Replay restricted to events at or before `t` (object-model §5). A fold is
    over whatever event subset the reader holds — no new mechanism."""
    return [e for e in events if e.timestamp <= t]


# ---------------------------------------------------------------------------
# orchard's reading of a market item. This is orchard's OWN classifier — a fold
# policy, not anything on the log. harbor never published how it classifies.
#   in        — orchard agrees this is a consumer-market good
#   out       — orchard is sure this is outside its recognized domain
#   ambiguous — a judgment call; orchard's reading and harbor's legitimately
#               differ, and neither is provably the faithful one (finding M).
# ---------------------------------------------------------------------------

def orchard_reads_domain(item: str) -> str:
    clearly_market = {"groceries", "books", "household"}
    clearly_outside = {"firearms", "securities"}
    if item in clearly_market:
        return "in"
    if item in clearly_outside:
        return "out"
    return "ambiguous"


# ---------------------------------------------------------------------------
# The projection at stake: how does orchard fold one of harbor's acts, under a
# chosen bridge-reading? Nothing is stored; recomputed on demand.
#
# Verdicts:
#   HONORED         — orchard treats the act as authorized
#   DECLINED        — orchard rejects it (a bound it can prove was crossed)
#   CONTESTED       — orchard disagrees on an ambiguous reading; cannot certify
#   NOT_RECOGNIZED  — no live bridge, or reading == ignored
# ---------------------------------------------------------------------------

def project_fidelity(events: list[Event], act_id: str, *, reading: str) -> dict:
    by_id = {e.id: e for e in events}
    act = by_id.get(act_id)
    if act is None:
        return {"act": act_id, "verdict": "NOT_FOUND", "reason": "no such act"}

    # harbor's mandate this act relied on (the consent.mandate it refs)
    mandate = next((by_id[r] for r in act.refs
                    if r in by_id and by_id[r].predicate == "consent.mandate"), None)

    # orchard's live recognition of harbor's domain (a fed.recognition, not later
    # severed). Severance bounds the FUTURE: a recognition severed after this act
    # was honored does not retroactively un-recognize it.
    domain = (mandate.scope or {}).get("category") if mandate and mandate.scope else None
    recognition = None
    for e in events:
        if e.type == "AUTHORIZE" and e.predicate == "fed.recognition":
            # A bridge routes ONE community's authority: the recognition must
            # name the mandate's granter (its refs carry the recognized
            # community's principal), not merely share a domain string — a
            # third community's market mandate does not ride this bridge (the
            # same community==signer check federation_fixture makes).
            if mandate is None or mandate.signer not in e.refs:
                continue
            sev = next((s for s in events
                        if s.type == "AUTHORIZE" and s.predicate == "fed.severance"
                        and e.id in s.nullifies and s.timestamp <= act.timestamp), None)
            if sev is None and (e.scope or {}).get("domain") == domain:
                recognition = e

    if reading == "ignored" or recognition is None:
        why = "reading=ignored" if reading == "ignored" else "no live bridge for this domain"
        return {"act": act_id, "verdict": "NOT_RECOGNIZED", "reason": why}

    amount = (act.scope or {}).get("total_krw")
    ceiling = (mandate.scope or {}).get("max_total_krw") if mandate and mandate.scope else None
    item = act.payload.get("item", "?")

    if reading == "binding":
        # orchard defers to harbor's authority. It does NOT re-fold against the
        # on-log mandate — that is what "binding" means. Whatever harbor's signer
        # signed under the recognized mandate, orchard honors. The drift, of
        # either kind, is imported here and is invisible at this fold.
        return {"act": act_id, "verdict": "HONORED",
                "reason": f"defers to harbor; on-log mandate NOT re-folded "
                          f"(amount={amount}, item={item})"}

    if reading == "advisory":
        # orchard re-folds under its OWN faithful reading of the same on-log
        # mandate. Two independent checks:
        if ceiling is not None and amount is not None and amount > ceiling:
            # NUMERIC drift — the violated bound is recorded, so orchard catches it.
            return {"act": act_id, "verdict": "DECLINED",
                    "reason": f"{amount} > on-log ceiling {ceiling} — harbor's "
                              f"signer exceeded the recorded mandate"}
        dom = orchard_reads_domain(item)
        if dom == "out":
            return {"act": act_id, "verdict": "DECLINED",
                    "reason": f"item '{item}' is outside orchard's recognized market domain"}
        if dom == "ambiguous":
            # CATEGORICAL drift — orchard's reading differs from harbor's, but
            # neither is provably faithful. Re-folding only substitutes judgment.
            return {"act": act_id, "verdict": "CONTESTED",
                    "reason": f"item '{item}': orchard reads it outside market, harbor "
                              f"inside — neither fold certifies the other (finding M)"}
        return {"act": act_id, "verdict": "HONORED",
                "reason": f"within on-log ceiling and orchard's market reading "
                          f"(amount={amount}, item={item})"}

    raise ValueError(f"unknown bridge-reading {reading!r}")


# ---------------------------------------------------------------------------
# Participants — each holds one key and emits its OWN events into the ledger.
# ---------------------------------------------------------------------------

class Party:
    def __init__(self, ledger: "Ledger", name: str, key: str):
        self.ledger, self.name, self.key = ledger, name, key

    def emit(self, type_: str, predicate: str, **kw) -> Event:
        ev = make(type_, self.key, predicate, self.ledger.now(), **kw)
        self.ledger.append(ev)
        print(f"    -> {self.name} emits {type_} {predicate}  [{ev.id}] @ {ev.timestamp}")
        return ev


class Ledger:
    def __init__(self) -> None:
        self.events: list[Event] = []
        self._clock = 0

    def now(self) -> str:
        self._clock += 1
        # This log holds 11 events, so everything lands in the morning (hour 10)
        # and the hour-16 branch below never trips — ordering is carried by the
        # MINUTE, and severance-vs-act order is what the folds read. The branch
        # is kept only for shape parity with the sibling fixtures' clocks.
        hour = 10 if self._clock <= 12 else 16
        return f"2026-06-10T{hour:02d}:{self._clock:02d}:00Z"

    def append(self, ev: Event) -> None:
        self.events.append(ev)


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


# the omniscient ground truth — which acts came from harbor's drifted reading.
# It is rendered in a strip "available to NO observer"; no fold ever reads it.
GROUND_TRUTH = {
    "act_in":  "faithful — 20000 groceries, within the mandate under any reading",
    "act_num": "DRIFT (numeric) — 40000 over the on-log 30000 ceiling; harbor's "
               "signer honored it as if the ceiling were soft",
    "act_cat": "DRIFT (categorical) — harbor's signer classified an ambiguous item "
               "as 'market'; faithful folds may legitimately disagree",
}


# ---------------------------------------------------------------------------
# The flow — run once, top to bottom.
# ---------------------------------------------------------------------------

def run() -> None:
    led = Ledger()
    harbor_p = Party(led, "harbor-principal", "k:harbor_p")  # grants the mandate
    harbor_a = Party(led, "harbor-agent",     "k:harbor_a")  # the DRIFTED signer
    orchard  = Party(led, "orchard",          "k:orchard")   # the recognizing community

    print("\n1. Identity — harbor's principal and agent, and orchard, each anchor a key")
    for p in (harbor_p, harbor_a, orchard):
        p.emit("KEY", "id.key_register", payload={"key": p.key})

    print("\n2. harbor mandate — principal grants the agent a market mandate, ceiling 30000")
    say("harbor-principal", "agent may transact in 'market' up to 30000 (recorded on-log)")
    mandate = harbor_p.emit("AUTHORIZE", "consent.mandate", refs=("k:harbor_a",),
                            scope={"category": "market", "max_total_krw": 30000})

    print("\n3. Bridge — orchard recognizes harbor's market authority (finding J)")
    say("orchard", "I recognize harbor's authority over the 'market' domain")
    bridge = orchard.emit("AUTHORIZE", "fed.recognition", refs=("k:harbor_p",),
                          scope={"domain": "market", "community": "harbor"})

    print("\n4. harbor's agent signs three acts — under harbor's OWN (drifted) reading")
    print("   Every one of them verifies. The signature is honest; the reading is not.")
    acts = {}
    acts["act_in"] = harbor_a.emit("AUTHORIZE", "consent.execute", refs=(mandate.id,),
                                   scope={"total_krw": 20000, "category": "market"},
                                   payload={"item": "groceries"})
    acts["act_num"] = harbor_a.emit("AUTHORIZE", "consent.execute", refs=(mandate.id,),
                                    scope={"total_krw": 40000, "category": "market"},
                                    payload={"item": "bulk_order"})
    acts["act_cat"] = harbor_a.emit("AUTHORIZE", "consent.execute", refs=(mandate.id,),
                                    scope={"total_krw": 15000, "category": "market"},
                                    payload={"item": "industrial_solvent"})

    print("\n5. The fold matrix — orchard reads each act under three bridge-readings")
    print("   (binding = defer to harbor / advisory = re-fold locally / ignored = drop)\n")
    labels = {"act_in":  "act_in  — 20000 groceries (in-scope)",
              "act_num": "act_num — 40000 bulk_order (NUMERIC drift)",
              "act_cat": "act_cat — 15000 solvent (CATEGORICAL drift)"}
    print(f"    {'act':<46}{'binding':<12}{'advisory':<12}{'ignored':<8}")
    print(f"    {'-'*46}{'-'*12}{'-'*12}{'-'*8}")
    for name in ("act_in", "act_num", "act_cat"):
        cells = [project_fidelity(led.events, acts[name].id, reading=r)["verdict"]
                 for r in ("binding", "advisory", "ignored")]
        print(f"    {labels[name]:<46}{cells[0]:<12}{cells[1]:<12}{cells[2]:<8}")

    print("\n   Reading the rows:")
    print("     act_in  — HONORED under binding AND advisory: in-scope, the laundering")
    print("               is invisible here (the finding-M byte/event-identity control).")
    print("     act_num — binding HONORED, advisory DECLINED: binding LAUNDERED a spend")
    print("               over the recorded ceiling; the local re-fold caught it.")
    print("     act_cat — binding HONORED, advisory CONTESTED: advisory did not 'catch'")
    print("               a violation, it only DISAGREED; harbor's fidelity stays unobserved.")

    print("\n6. orchard, operating BINDING, honors act_num and records a payment on its basis")
    say("orchard", "binding recognition → act_num is authorized → paying")
    pay = orchard.emit("ATTEST", "commerce.payment_result", refs=(acts["act_num"].id,),
                       payload={"result": "confirmed", "amount_krw": 40000, "provider": "mock_pay"})

    print("\n7. Severance — orchard severs the bridge (fed.severance + nullifies)")
    say("orchard", "I no longer recognize harbor's market authority going forward")
    orchard.emit("AUTHORIZE", "fed.severance", refs=("k:harbor_p",), nullifies=(bridge.id,),
                 payload={"reason": "standards_divergence"})

    print("\n8. After severance — a NEW harbor act is dropped, but the laundered past persists")
    act_late = harbor_a.emit("AUTHORIZE", "consent.execute", refs=(mandate.id,),
                             scope={"total_krw": 18000, "category": "market"},
                             payload={"item": "groceries"})
    late = project_fidelity(led.events, act_late.id, reading="binding")
    print(f"\n   new act_late under binding: {late['verdict']}  ({late['reason']})")
    still = project_fidelity(led.events, acts["act_num"].id, reading="binding")
    print(f"   already-honored act_num under binding: {still['verdict']}  "
          f"(severance moved 0 past cells; recognition was live when honored)")
    print(f"   orchard's payment on act_num [{pay.id}] is NOT nullified by the severance —")
    print(f"   the laundered act, and the money paid on it, outlive the bridge.")

    print(f"\nGenerated log: {len(led.events)} signed events. verify_log passes.")
    verify_log(led.events)

    print("\n--- omniscient view — available to NO observer (folds never read this) ---")
    for name, truth in GROUND_TRUTH.items():
        print(f"    {name}: {truth}")
    print("    The log carries the acts and the bridge. It does NOT carry harbor's")
    print("    signer's reading. binding imports it unseen; advisory substitutes its own.")

    print_finding()


def print_finding() -> None:
    print("""
What this probe exposes
-----------------------
  * Does federation launder a drifted signer's act?
      It depends on how the recognizing community READS the bridge — and that
      categorical choice (finding J: binding / advisory / ignored) IS the choice
      of whose interpretation to trust (finding M: faithful vs drifted reading).
        - binding  defers to harbor without re-folding the on-log mandate, so it
                   IMPORTS harbor's reading and LAUNDERS the drift;
        - advisory re-folds locally and EXPOSES numeric drift (a crossed bound
                   that the mandate recorded);
        - ignored  transmits nothing.
  * Does re-folding (advisory) recover harbor's fidelity?
      Only for drift against a RECORDED bound (the numeric ceiling). For an
      ambiguous category, advisory does not catch a violation — it only
      DISAGREES (CONTESTED). Two faithful folds may read the category differently;
      neither certifies the other. Re-folding substitutes orchard's judgment for
      harbor's; it does not OBSERVE harbor's faithfulness. Finding M's unobservable
      layer is not closed by the bridge — it is relocated to the recognizer.
  * What does binding recognition actually cost?
      It makes orchard's clean log contingent on a signer it can observe even less
      than its own — harbor's. finding K's clean log rested on the local signer's
      fidelity; binding recognition extends that dependency across the bridge to a
      remote one. "Binding" is not free deference; it is importing an unobservable
      trust assumption one community further away.
  * Does severing the bridge undo the laundering?
      No. Severance bounds the future (a new harbor act is NOT_RECOGNIZED) but the
      act already honored under binding — and the payment recorded on it — stay in
      orchard's history. Severance is finding J's "resolution by amnesia": it does
      not un-launder the past.

No sixth type was required. The bridge is one AUTHORIZE fed.recognition; severance
is the nullifies field; the drift is a signer's reading, never an event and never a
stored fidelity score. The laundering is a fold-policy residue at the composition of
findings J and M — binding recognition routes not just authority but unobservable
interpretation. This is a probe, not a federation spec and not doctrine.
""")


if __name__ == "__main__":
    run()

#!/usr/bin/env python3
"""
ARC federation bridge-reading probe — single file, stdlib only.

What this isolates
------------------
Two earlier probes meet here:

  * finding J (federation bridge, federation_fixture): a scoped `AUTHORIZE
    fed.recognition` is read as binding, advisory, or ignored by this fixture.
  * finding M (signer fidelity, signer_fidelity_fixture): verification under a
    declared signature profile can check record bytes against a configured public
    key, but it does not establish who controlled that key or how the signer label's
    associated party interpreted its mandate.

The composition question:

  > When an act produced under a stipulated drifted reading crosses a federation
  > bridge, does the receiver re-evaluate the recorded scope locally?

The setup is two communities. **harbor** grants its agent a market mandate with
an on-log ceiling of 30000. harbor's signer has a stipulated drifted reading and
mock-signs acts harbor's
own mandate, as written, would not authorize. **orchard** recognizes harbor's
market authority over a bridge, then folds harbor's acts three ways:

    orchard --AUTHORIZE fed.recognition--> scope={domain:market, community:harbor}
    harbor  --AUTHORIZE consent.mandate--> scope={category:market, max:30000}
    harbor  --AUTHORIZE consent.execute--> three mock-signed acts

Nothing here is a new event type. The bridge is one `AUTHORIZE fed.recognition`
(finding J); severance is the existing `nullifies` field; the drift is a signer's
reading (finding M), never an event and never a stored "fidelity score".

Configured bridge readings
--------------------------
The Event does not record the signer's private interpretation. This fixture applies
three bridge readings:

  * binding   -> after finding a live matching recognition, this branch returns
                 HONORED without checking the act against the recorded mandate
                 ceiling or orchard classifier. No remote verdict is represented.
  * advisory  -> orchard re-folds each act under its own configured reading of the
                 same on-log mandate. The numeric drift (over the recorded
                 ceiling) is reported and DECLINED.
  * ignored   -> the act is NOT_RECOGNIZED; nothing transmits.

The probe crosses two stipulated interpretation differences:

  * NUMERIC drift (an amount over the on-log ceiling): advisory reports it,
    because the violated bound is recorded. binding skips the local mandate checks.
  * CATEGORICAL drift (an ambiguous item harbor calls "market" and orchard would
    not): advisory returns CONTESTED. The fixture does not establish which category
    interpretation is preferable; it only applies orchard's configured classifier.

And severance inherits finding J's preserve/cascade asymmetry: orchard can sever
the bridge (`fed.severance` + `nullifies`), but an act already HONORED under
binding — and the payment orchard recorded on its basis — remains in orchard's
history under this preserve-style policy. Severance bounds the future; it does
not remove the earlier act from the Event set.

Fixture limits:
  * stdlib only, single process, no network, no transport, no storage;
  * signatures are MOCK (a hash, not Ed25519). finding M used illustrative
    Ed25519; here the point is reading-semantics
    across the bridge, not custody, so the control asserts EVENT-identity (the
    recognized event is the same object whatever harbor's signer privately read).
  * the five canonical types are reused as-is — no new primitive, no stored
    authority object, no stored fidelity score;
  * this is a probe, not a federation specification.

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
    """Deterministic fixture hash, not a signature or proof of key possession.

    The hash is a function of the signer label and bytes, not the fixture's
    stipulated interpretation. A production profile must declare its suite.
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
    """Fixture replay check: deterministic mock signature and key registration.

    Deliberately no signer-reading check exists here. This is not production
    signature verification, completeness checking, or a fidelity determination.
    """
    registered: set[str] = set()
    for ev in events:
        if ev.signature != stub_sign(ev.signer, ev.signing_bytes()):
            raise ValueError(f"bad mock signature on {ev.id}")
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
#   ambiguous — the configured orchard and harbor readings differ; this fixture
#               does not select a preferred classifier.
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
#   DECLINED        — orchard rejects it (a recorded bound is crossed)
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
        # This branch returns HONORED once a matching live recognition exists. It
        # does not inspect the recorded mandate ceiling/category or consume a
        # remote verdict.
        return {"act": act_id, "verdict": "HONORED",
                "reason": f"matching recognition; local mandate checks skipped "
                          f"(amount={amount}, item={item})"}

    if reading == "advisory":
        # orchard re-folds under its OWN configured reading of the same on-log
        # mandate. Two independent checks:
        if ceiling is not None and amount is not None and amount > ceiling:
            # NUMERIC drift — the violated bound is recorded, so this policy reports it.
            return {"act": act_id, "verdict": "DECLINED",
                    "reason": f"{amount} > on-log ceiling {ceiling} — harbor's "
                              f"signer exceeded the recorded mandate"}
        dom = orchard_reads_domain(item)
        if dom == "out":
            return {"act": act_id, "verdict": "DECLINED",
                    "reason": f"item '{item}' is outside orchard's recognized market domain"}
        if dom == "ambiguous":
            # CATEGORICAL drift — orchard's reading differs from harbor's, but
            # this fixture does not establish a preferred interpretation.
            return {"act": act_id, "verdict": "CONTESTED",
                    "reason": f"item '{item}': orchard reads it outside market, harbor "
                              f"inside — this policy returns CONTESTED"}
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


# Generator-only stipulations — which acts use harbor's drifted reading.
# Observer folds do not receive this mapping.
FIXTURE_STIPULATIONS = {
    "act_in":  "20000 groceries, within the mandate under either configured reading",
    "act_num": "DRIFT (numeric) — 40000 over the on-log 30000 ceiling; harbor's "
               "signer honored it as if the ceiling were soft",
    "act_cat": "DRIFT (categorical) — harbor's signer classified an ambiguous item "
               "as 'market'; the configured classifiers disagree",
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

    print("\n4. harbor's agent mock-signs three acts — stipulated drifted reading")
    print("   Every one passes this fixture's mock-signature/key-registration check.")
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
    print("   (binding = recognize without local mandate checks / "
          "advisory = re-fold locally / ignored = drop)\n")
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
    print("     act_in  — HONORED under binding AND advisory: both configured readings")
    print("               accept the same Event.")
    print("     act_num — binding HONORED, advisory DECLINED: binding skips the recorded")
    print("               ceiling check; the advisory re-fold applies it.")
    print("     act_cat — binding HONORED, advisory CONTESTED: advisory did not 'catch'")
    print("               a recorded violation; the configured classifiers disagree.")

    print("\n6. orchard uses the binding reading for act_num and records a payment-result claim")
    say("orchard", "binding recognition → recording the fixture payment-result claim")
    pay = orchard.emit("ATTEST", "commerce.payment_result", refs=(acts["act_num"].id,),
                       payload={"result": "confirmed", "amount_krw": 40000, "provider": "mock_pay"})

    print("\n7. Severance — orchard severs the bridge (fed.severance + nullifies)")
    say("orchard", "I no longer recognize harbor's market authority going forward")
    orchard.emit("AUTHORIZE", "fed.severance", refs=("k:harbor_p",), nullifies=(bridge.id,),
                 payload={"reason": "standards_divergence"})

    print("\n8. After severance — a new harbor act is dropped; earlier records remain")
    act_late = harbor_a.emit("AUTHORIZE", "consent.execute", refs=(mandate.id,),
                             scope={"total_krw": 18000, "category": "market"},
                             payload={"item": "groceries"})
    late = project_fidelity(led.events, act_late.id, reading="binding")
    print(f"\n   new act_late under binding: {late['verdict']}  ({late['reason']})")
    still = project_fidelity(led.events, acts["act_num"].id, reading="binding")
    print(f"   already-honored act_num under binding: {still['verdict']}  "
          f"(severance moved 0 past cells; recognition was live when honored)")
    print(f"   orchard's payment on act_num [{pay.id}] is not nullified by the severance —")
    print("   the earlier act and mock payment-result record remain in the Event set.")

    print(f"\nGenerated log: {len(led.events)} mock-signed fixture Events; replay checks pass.")
    verify_log(led.events)

    print("\n--- generator-only stipulations (observer folds do not receive these) ---")
    for name, truth in FIXTURE_STIPULATIONS.items():
        print(f"    {name}: {truth}")
    print("    The log carries the acts and the bridge. It does not carry harbor's")
    print("    signer's private reading or a remote verdict. The binding branch does not")
    print("    inspect that reading; advisory applies orchard's configured checks.")

    print_finding()


def print_finding() -> None:
    print("""
What this probe exposes
-----------------------
  * Does the receiving policy re-evaluate the recorded scope locally?
      It depends on the configured bridge reading in this fixture:
        - binding  returns HONORED after a matching live recognition without
                   checking the recorded mandate ceiling or orchard classifier;
        - advisory re-folds locally and reports numeric drift (a crossed bound
                   that the mandate recorded);
        - ignored  transmits nothing.
  * Does re-folding (advisory) recover harbor's fidelity?
      Only for drift against a recorded bound (the numeric ceiling). For an
      ambiguous category, advisory returns CONTESTED because the configured
      classifiers disagree. Re-folding substitutes orchard's policy; it does not
      establish harbor's private interpretation.
  * What does binding recognition do?
      In this fixture, it treats a matching live recognition as sufficient for
      HONORED and skips the recorded-ceiling and orchard-classifier checks. The
      fixture does not represent or consume a remote verdict.
  * What does severing the bridge do under this preserve-style policy?
      It bounds future recognition. The earlier act and mock payment-result record
      remain in the Event set and keep their prior fixture treatment.

No sixth type was required. The bridge is one AUTHORIZE fed.recognition; severance
is the nullifies field; the drift is a signer's reading, never an event and never a
stored fidelity score. This is one bridge encoding with three configured readings;
base ARC does not select a federation policy. This is a probe, not a federation specification.
""")


if __name__ == "__main__":
    run()

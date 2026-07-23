#!/usr/bin/env python3
"""
ARC temporal fidelity probe — single file, stdlib only.

What this isolates
------------------
Finding M (signer_fidelity_fixture) said that a configured signature check does
not establish a signer's mandate interpretation. This probe is M's twin
one layer down — on the EVIDENCE layer rather than the custody/signer layer.

  > This fixture's deterministic mock-signature check detects byte changes. It
  > does not establish key possession or timestamp accuracy.

The timestamp lives inside `signing_bytes`, so it is baked into the event id and
the signature. That cuts two ways, and the cut is the whole finding:

  * Changing a timestamp AFTER mock-signing changes the id and fails this
    fixture's deterministic hash check. It is post-signature mutation, not a
    temporal lie.
  * Stamping a false timestamp before this fixture's mock-signing still passes
    its deterministic hash check. That check does not establish clock truth.

Why it matters: `as_of`, revocation, challenge windows, adjudication, and standing
all depend on `event.timestamp`. A false timestamp can therefore affect policies
that rely on it.

The dependency signal carried by refs
-------------------------------------
`B refs A` places A's exact identifier in B and records a declared dependency or
prior-knowledge claim. Because an identifier can be computed before A is appended
or published, the reference alone does not prove append, publication, or wall-clock
issuance order.

A timestamp conflict is reported only when an event's claimed time is earlier
than the claimed time of a referenced Event. This check does not establish which
claim is accurate or whether either corresponds to wall-clock order. A false stamp
that remains compatible with referenced claimed times passes the check.

Refs let this fixture check timestamp consistency with declared references. When
neither Event references the other, this reference-only check does not resolve
their wall-clock order; only their timestamps claim one.

The five readouts
-----------------
  1. post-signature mutation — this fixture catches the id/mock-signature mismatch.
  2. dependency conflict     — claimed time precedes a referenced claimed time.
  3. careful backdate        — refs compatible identifiers; passes listed checks.
  4. revocation race         — a careful backdate stamped before a revocation it
                               never refs; a claimed-timestamp time-scoped fold
                               honors an act the fixture stipulates was created later.
  5. concurrent -> CONTESTED — neither Event references the other; only the
                               timestamps claim an order. Without accepting that
                               order, this fixture's reference-only policy returns
                               CONTESTED.

Configured recent-head source:
  requiring each event to ref a recent head makes the act descend from the
  revocation under this authored scenario. The fixture does not validate that
  source or establish that a signer consulted it.

Limits:
  * stdlib only, single process, no network, no transport, no storage;
  * signatures are MOCK (a hash, not Ed25519) — the point is the FOLD over the
    timestamp, not custody. IDs and refs use deterministic content hashes, so the
    dependency check flags a timestamp inconsistent with a named reference;
  * the five current Event types are reused as-is — no new primitive, no stored clock,
    no trusted-timestamp object, no stored "temporal score";
  * this fixture does not define a protocol specification.

Run:  python3 probe.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from typing import Any

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}


# ---------------------------------------------------------------------------
# The Event and its mock signing — same lean shape as the other probes. The
# timestamp is part of signing_bytes, so it is baked into both the id and the
# signature. That is the hinge of the whole probe.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Event:
    id: str
    type: str
    signer: str
    predicate: str
    timestamp: str                       # the claim; mock-signed, not established as true.
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


def stub_sign(signer: str, body: bytes) -> str:
    """Deterministic fixture hash, not a signature or proof of key possession.

    It covers the signer label and timestamp bytes so mutation is detectable.
    A production security profile must define its own signature suite.
    """
    return "stub:" + hashlib.sha256(signer.encode() + body).hexdigest()[:16]


def content_id(body: bytes) -> str:
    return "ev:" + hashlib.sha256(body).hexdigest()[:12]


def make(type_: str, signer: str, predicate: str, ts: str, **kw) -> Event:
    assert type_ in CANONICAL_TYPES, f"non-canonical type {type_!r} — forbidden"
    partial = Event(id="", type=type_, signer=signer, predicate=predicate, timestamp=ts, **kw)
    body = partial.signing_bytes()
    return Event(id=content_id(body), type=type_, signer=signer, predicate=predicate,
                 timestamp=ts, signature=stub_sign(signer, body), **kw)


def verify_log(events: list[Event]) -> None:
    """Fixture replay check: id, deterministic mock signature, key registration.

    It does not establish timestamp truth, Event-set completeness, or production
    signature conformance.
    """
    registered: set[str] = set()
    for ev in events:
        body = ev.signing_bytes()
        if ev.id != content_id(body):
            raise ValueError(f"id does not match content on {ev.id} (post-signature mutation)")
        if ev.signature != stub_sign(ev.signer, body):
            raise ValueError(f"bad mock signature on {ev.id}")
        is_root = ev.type == "KEY" and ev.predicate == "id.key_register"
        if not is_root and ev.signer not in registered:
            raise ValueError(f"signer {ev.signer} not anchored by a KEY register ({ev.id})")
        if is_root:
            registered.add(ev.payload["key"])


# ---------------------------------------------------------------------------
# Reference closure derived from refs, never from timestamps. B refs A places A's
# identifier in B; it does not independently prove append or wall-clock order.
# ---------------------------------------------------------------------------

def causal_ancestors(by_id: dict[str, Event], ev_id: str) -> set[str]:
    """Transitive closure of referenced identifiers known to this Event."""
    seen: set[str] = set()
    stack = list(by_id[ev_id].refs)
    while stack:
        r = stack.pop()
        if r in seen or r not in by_id:
            continue
        seen.add(r)
        stack.extend(by_id[r].refs)
    return seen


def causal_violations(events: list[Event]) -> list[tuple[str, str]]:
    """Apply this fixture's rule that an Event's claimed time must be strictly
    later than every Event it transitively refs. Return pairs that violate that
    declared-reference timestamp rule."""
    by_id = {e.id: e for e in events}
    bad: list[tuple[str, str]] = []
    for e in events:
        for a in causal_ancestors(by_id, e.id):
            if not (by_id[a].timestamp < e.timestamp):
                bad.append((e.id, a))
    return bad


def concurrent(by_id: dict[str, Event], a_id: str, b_id: str) -> bool:
    """Return True when neither Event is in the other's reference closure."""
    return (a_id not in causal_ancestors(by_id, b_id)
            and b_id not in causal_ancestors(by_id, a_id))


# ---------------------------------------------------------------------------
# The folds at stake. Both stand on `event.timestamp` — which is the exposure.
# ---------------------------------------------------------------------------

def honoring_by_claimed_act_time(events: list[Event], act_id: str) -> dict:
    """Read the full log, trust the act's CLAIMED timestamp, and decide whether
    this time-scoped policy honors the act. This is not the earlier-event-subset
    historical baseline in authority-revocation-demo — and that distinction is
    exactly what a careful backdate exploits."""
    by_id = {e.id: e for e in events}
    act = by_id[act_id]
    mandate = next((by_id[r] for r in act.refs
                    if r in by_id and by_id[r].predicate == "consent.mandate"), None)
    if mandate is None:
        return {"verdict": "NO_MANDATE", "reason": "act refs no mandate"}
    revoked = next((r for r in events
                    if mandate.id in r.nullifies and r.timestamp <= act.timestamp), None)
    if revoked is None:
        return {"verdict": "HONORED",
                "reason": f"at claimed {act.timestamp} the mandate was live "
                          f"(no revocation stamped at or before the claim)"}
    return {"verdict": "DECLINED", "reason": f"revoked by {revoked.id} @ {revoked.timestamp}"}


def honoring_by_causality(events: list[Event], act_id: str, rev_id: str) -> dict:
    """Apply the fixture's reference-only ordering policy. If neither Event is in
    the other's reference closure, this policy returns CONTESTED."""
    by_id = {e.id: e for e in events}
    if rev_id in causal_ancestors(by_id, act_id):
        return {"verdict": "DECLINED", "reason": "act references the revocation transitively"}
    if act_id in causal_ancestors(by_id, rev_id):
        return {"verdict": "HONORED", "reason": "revocation references the act transitively"}
    return {"verdict": "CONTESTED",
            "reason": "neither Event references the other transitively; only their "
                      "timestamps claim an order"}


# ---------------------------------------------------------------------------
# Participants and ledger. Unlike the other probes, the ledger here lets a party
# STAMP a chosen time. A private generator stipulation is tracked separately and
# is never supplied to the observer folds.
# ---------------------------------------------------------------------------

class Party:
    def __init__(self, ledger: "Ledger", name: str, key: str):
        self.ledger, self.name, self.key = ledger, name, key

    def emit(self, type_: str, predicate: str, *, claim: str, stipulated: str, **kw) -> Event:
        ev = make(type_, self.key, predicate, claim, **kw)
        self.ledger.append(ev, stipulated)
        flag = "" if claim == stipulated else f"   << claims {claim}, generator stipulates {stipulated}"
        print(f"    -> {self.name} {type_} {predicate}  [{ev.id}] @ {claim}{flag}")
        return ev


class Ledger:
    def __init__(self) -> None:
        self.events: list[Event] = []
        self.stipulated_mint: dict[str, str] = {}  # private fixture input

    def append(self, ev: Event, stipulated: str) -> None:
        self.events.append(ev)
        self.stipulated_mint[ev.id] = stipulated

    def events_by_id(self) -> dict[str, Event]:
        return {e.id: e for e in self.events}


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


# ---------------------------------------------------------------------------
# The flow — run once, top to bottom.
# ---------------------------------------------------------------------------

def run() -> None:
    led = Ledger()
    principal = Party(led, "principal", "k:principal")   # grants and revokes the mandate
    agent     = Party(led, "agent",     "k:agent")       # the backdating signer

    print("\n1. Identity — principal and agent each anchor a key")
    principal.emit("KEY", "id.key_register", claim="2026-06-10T09:50:00Z",
                   stipulated="2026-06-10T09:50:00Z", payload={"key": principal.key})
    agent.emit("KEY", "id.key_register", claim="2026-06-10T09:51:00Z",
               stipulated="2026-06-10T09:51:00Z", payload={"key": agent.key})

    print("\n2. Mandate — principal grants the agent a market mandate (stipulated 10:00)")
    mandate = principal.emit("AUTHORIZE", "consent.mandate", claim="2026-06-10T10:00:00Z",
                             stipulated="2026-06-10T10:00:00Z", refs=("k:agent",),
                             scope={"category": "market", "max_total_krw": 30000})

    print("\n3. Revocation — principal revokes the mandate (stipulated 10:05)")
    say("principal", "the agent's mandate is withdrawn as of now")
    revocation = principal.emit("AUTHORIZE", "consent.withdraw", claim="2026-06-10T10:05:00Z",
                                stipulated="2026-06-10T10:05:00Z", refs=(mandate.id,),
                                nullifies=(mandate.id,))

    # -- Readout 1: post-mock-signature mutation --------------------------------
    print("\n4. Readout 1 — POST-MOCK-SIGNATURE MUTATION")
    baseline = make("ATTEST", agent.key, "commerce.receipt", "2026-06-10T10:02:00Z",
                  refs=(mandate.id,), payload={"item": "groceries"})
    tampered = replace(baseline, timestamp="2026-06-10T09:30:00Z")  # rewrite clock, keep id/sig
    print(f"    authored [{baseline.id}] @ {baseline.timestamp}, then rewrote its timestamp to "
          f"{tampered.timestamp} keeping the old id/sig")
    try:
        verify_log(led.events + [tampered])
        print("    verify_log PASSED — (should not happen)")
    except ValueError as exc:
        print(f"    verify_log REJECTS it: {exc}")
    print("    Changing a stamped time after signing breaks the content hash. This is the")
    print("    mutation check; it says nothing about the original timestamp's truth.")

    # -- Readout 2: timestamp conflicts with a declared reference ---------------
    print("\n5. Readout 2 — DEPENDENCY-INCONSISTENT TIMESTAMP")
    careless = agent.emit("ATTEST", "commerce.receipt", claim="2026-06-10T09:55:00Z",
                          stipulated="2026-06-10T10:06:00Z", refs=(mandate.id,),
                          payload={"item": "groceries", "note": "stamped before the mandate it refs"})
    viol = [(e, a) for (e, a) in causal_violations(led.events) if e == careless.id]
    for e, a in viol:
        print(f"    causal check: {e} claims {careless.timestamp} but refs {a} "
              f"(@ {led.events_by_id()[a].timestamp}) — inconsistent with this dependency policy")
    print("    The named reference and the two claimed timestamps conflict under this check.")

    # -- Readout 3: careful backdate — undetectable ----------------------------
    print("\n6. Readout 3 — DEPENDENCY-COMPATIBLE FALSE STAMP (fixture stipulation)")
    careful = agent.emit("AUTHORIZE", "consent.execute", claim="2026-06-10T10:01:00Z",
                         stipulated="2026-06-10T10:06:00Z", refs=(mandate.id,),
                         scope={"total_krw": 20000, "category": "market"},
                         payload={"item": "groceries"})
    cv = [(e, a) for (e, a) in causal_violations(led.events) if e == careful.id]
    print(f"    causal check on {careful.id}: {'VIOLATION' if cv else 'no violation — passes'}")
    print(f"    It claims 10:01 (after the mandate it refs @ 10:00) and refs nothing newer.")
    print(f"    verify_log: ", end="")
    verify_log(led.events)
    print("passes the listed fixture checks; none establishes the timestamp's truth.")

    # -- Readout 4: revocation race --------------------------------------------
    print("\n7. Readout 4 — REVOCATION ORDERING (generator stipulates act at 10:06)")
    say("agent", "fixture stipulation: create at 10:06, stamp 10:01")
    claimed_time_fold = honoring_by_claimed_act_time(led.events, careful.id)
    print(f"    claimed-timestamp time-scoped fold: {claimed_time_fold['verdict']}  "
          f"({claimed_time_fold['reason']})")
    print("    The withdrawal record claims 10:05; the act never refs it and claims 10:01,")
    print("    so this policy honors the act despite the generator's later-time stipulation.")

    # -- Readout 5: concurrent -> CONTESTED ------------------------------------
    print("\n8. Readout 5 — CONCURRENT -> CONTESTED")
    by_id = led.events_by_id()
    print(f"    Does either Event reference the other [{careful.id}] / [{revocation.id}]?")
    print(f"      act refs:        {careful.refs}")
    print(f"      revocation refs: {revocation.refs}")
    print(f"      concurrent? {concurrent(by_id, careful.id, revocation.id)} "
          f"(both ref the mandate; neither refs the other)")
    c_fold = honoring_by_causality(led.events, careful.id, revocation.id)
    print(f"    reference-only fold: {c_fold['verdict']}  ({c_fold['reason']})")
    print("    The only supplied field ordering the act before the revocation is its")
    print("    claimed timestamp; the supplied reference graph does not order them.")
    print("    Without a policy accepting the timestamp order, this reference-only fold")
    print("    returns CONTESTED.")

    # -- The mitigation, and its price -----------------------------------------
    print("\n9. Configured recent-head source")
    head_at_stipulated_mint = revocation.id
    anchored = head_at_stipulated_mint in careful.refs
    print(f"    A head-anchor rule requires each event to ref a recent head.")
    print(f"    Under the generator's 10:06 stipulation, the configured head is [{revocation.id}].")
    print(f"    Does the careful backdate ref it? {anchored}.")
    print(f"    A signer using that source would ref the revocation -> the revocation")
    print(f"    enters the act's reference closure -> claim 10:01 < 10:05 fails this check -> CAUGHT.")
    print(f"    This fixture does not validate the recent-head source or establish that the")
    print(f"    signer consulted it.")

    print(f"\nGenerated log: {len(led.events)} mock-signed fixture Events; the listed replay checks pass.")
    verify_log(led.events)

    print("\n--- generator-only time stipulations (observer folds do not receive these) ---")
    for ev in led.events:
        claim, stipulated = ev.timestamp, led.stipulated_mint[ev.id]
        mark = "  <-- differs" if claim != stipulated else ""
        print(f"    [{ev.id}] {ev.predicate:<18} claims {claim}  | stipulated {stipulated}{mark}")
    print("    The Event set carries the claimed times, not the generator stipulations.")
    print("    The supplied reference graph constrains only some claimed-time comparisons.")

    print_finding()


def print_finding() -> None:
    print("""
What this probe exposes
-----------------------
  * Can this fixture establish timestamp truth from its mock signature?
      No. The deterministic hash covers the timestamp bytes and detects mutation;
      it does not authenticate a key or establish a clock.
  * What does this fixture check?
      - post-signature mutation: rewriting a stamped time breaks the content hash;
      - dependency conflict: an event whose claimed time precedes the claimed time
        of a referenced record conflicts under this policy;
      - revocations, nullifications, and conflicting attestations remain separate
        Events whose declared dependencies and claimed timestamps can be compared.
      Refs therefore support dependency-consistency checks over supplied records.
  * What does this fixture not establish?
      - whether the signer accurately observed the claimed time;
      - whether `as_of` corresponds to real-world time;
      - a dependency-compatible false stamp, as stipulated by this generator.
        It passes verify_log and the reference check, and a claimed-timestamp
        time-scoped fold honors the act despite the generator's later-time stipulation.
  * When does the supplied reference graph leave order unresolved?
      When neither Event refs the other, the graph gives no order; only the
      timestamps claim one. Without accepting that timestamp order, this
      reference-only policy returns CONTESTED. In the revocation case, the act
      and the revocation are concurrent, and only the claimed
      stamp put the act "before" the revocation.
  * What changes with a configured recent-head source?
      Requiring a recent-head reference orders these authored records, but the
      fixture does not validate that source or establish that a signer used it.

Conclusion: an Event can record a temporal claim under a declared security
profile, and refs can express dependencies among named records. Neither mechanism
alone establishes wall-clock issuance order or timestamp truth.

These authored scenarios use the current Event types and store no clock object or
temporal score. They leave wall-clock accuracy outside the dependency check.
""")


if __name__ == "__main__":
    run()

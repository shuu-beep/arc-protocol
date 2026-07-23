#!/usr/bin/env python3
"""
ARC execution / outcome fidelity probe — single file, stdlib only.

What this isolates
------------------
This is a third fixture examining the same record/referent distinction:

  * Finding M (signer_fidelity_fixture) — a configured signature check does not
    establish that a signer interpreted its mandate faithfully.
  * Finding O (temporal-fidelity-demo)  — it does not establish timestamp truth.
  * This probe                          — it does not establish the world referent.

  > Under a declared security profile, verification can check a signature over
  > the covered bytes against the configured public key. It does not establish
  > that delivery occurred.

ARC executes no payment and performs no delivery (architecture.md §4.2,
liability-boundaries.md). This fixture examines what its counter-attestations,
receipts, CHALLENGE, ADJUDICATE, and named policies establish after that boundary.

Recorded claims and authority policy
------------------------------------
  * Two contradictory claims about one referent (agent: "delivered"; principal:
    "not received") both pass the fixture replay check, and the comparison reports
    the contradiction. This is the event-registry's "partially exposed" case.
  * But exposing a contradiction is not resolving it. Every instrument that looks
    like proof of the outcome — a carrier receipt, a witness attestation, even a
    second counter-claim — is another record whose evidentiary weight depends on
    the declared profile and observer policy. Additional receipts do not by
    themselves establish the referent.
  * Under this fixture's authority policy, ADJUDICATE selects a terminal ruling.
    The ruling remains a recorded claim and does not establish the external outcome.
  * Without a policy that gives one signer decisive weight, this fixture returns
    CONTESTED — finding J, on the world axis.

External-attestor policy
------------------------
  privileged external attestor — give one signer's ATTEST decisive weight under a
  named policy (an escrow release, an IoT delivery sensor, a
  payment provider's settlement webhook). The dispute then resolves deterministically.
  The resulting value is deterministic under that policy, but the attestor's record
  remains a claim and may be inaccurate.

Fixture limits:
  * stdlib only, single process, no network, no transport, no storage;
  * signatures are MOCK (a hash, not Ed25519) — the point is the fold over the
    authored claims, not custody. IDs and refs use deterministic content hashes;
  * the five canonical types are reused as-is — no new primitive, no stored
    "delivery oracle" object, no stored "outcome score";
  * a stipulated state (was it delivered?) lives in a generator-only strip not
    supplied to observer folds;
  * this is a probe, not a protocol specification.

Run:  python3 probe.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}


# ---------------------------------------------------------------------------
# The Event and its mock signing — the same lean shape as the other probes.
# The claim about the world lives in `payload`, so the deterministic fixture hash
# covers the payload bytes whether or not the external claim is accurate.
# ---------------------------------------------------------------------------

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
    payload: dict[str, Any] = field(default_factory=dict)   # the CLAIM about the world
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

    The hash covers the signer label and payload bytes so the fixture can detect
    mutation. A production security profile must define its own signature suite.
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

    Deliberately no outcome check exists here. This is not production signature
    verification, completeness checking, or proof of the payload's referent.
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
# Claims about a referent. A "claim" is any ATTEST whose payload names a referent
# and asserts a state for it. Contradiction is decidable from the log; truth is not.
# ---------------------------------------------------------------------------

def claims_about(events: list[Event], referent: str) -> list[Event]:
    return [e for e in events
            if e.type == "ATTEST" and e.payload.get("referent") == referent
            and "state" in e.payload]


def contradiction(events: list[Event], referent: str) -> list[tuple[str, str]]:
    """Pairs of claims about one referent that assert different states. This is what
    the log CAN see: not which is true, only that they cannot both be."""
    cl = claims_about(events, referent)
    bad: list[tuple[str, str]] = []
    for i in range(len(cl)):
        for j in range(i + 1, len(cl)):
            if cl[i].payload["state"] != cl[j].payload["state"]:
                bad.append((cl[i].id, cl[j].id))
    return bad


# ---------------------------------------------------------------------------
# The three ways to "resolve" the outcome — each reads the same log and answers
# differently. The gap between them is the finding.
# ---------------------------------------------------------------------------

def resolve_by_log(events: list[Event], referent: str) -> dict:
    """Compare claims with no signer privileged. If claims agree, report the shared
    assertion; if they conflict, return the configured CONTESTED output."""
    states = {e.payload["state"] for e in claims_about(events, referent)}
    if not states:
        return {"verdict": "UNKNOWN", "reason": "no claim about this referent"}
    if len(states) == 1:
        s = next(iter(states))
        return {"verdict": "ASSERTED", "state": s,
                "reason": f"every claim says {s!r} — but agreement among signers is "
                          f"consensus, not proof of the world"}
    return {"verdict": "CONTESTED",
            "reason": "claims about the referent conflict; the log exposes the "
                      "contradiction but cannot say which signer told the truth"}


def resolve_by_adjudication(events: list[Event], referent: str) -> dict:
    """Apply this fixture's policy that treats an ADJUDICATE as the terminal ruling.
    The ruling is still a recorded claim, not a measurement of the referent."""
    ruling = next((e for e in events
                   if e.type == "ADJUDICATE" and e.payload.get("referent") == referent), None)
    if ruling is None:
        return {"verdict": "NO_RULING", "reason": "no ADJUDICATE for this referent"}
    return {"verdict": "FINAL", "state": ruling.payload["state"], "by": ruling.signer,
            "reason": f"adjudicator {ruling.signer} ruled {ruling.payload['state']!r} — "
                      f"selected by this fixture's authority policy; external outcome unverified"}


def resolve_by_oracle(events: list[Event], referent: str, oracle_key: str) -> dict:
    """Select one signer's ATTEST as authoritative under this named fixture policy."""
    claim = next((e for e in claims_about(events, referent) if e.signer == oracle_key), None)
    if claim is None:
        return {"verdict": "NO_ORACLE_CLAIM", "reason": f"oracle {oracle_key} made no claim"}
    return {"verdict": "ORACLE_CLAIM_SELECTED", "state": claim.payload["state"], "by": oracle_key,
            "reason": f"oracle {oracle_key} attests {claim.payload['state']!r}, treated as "
                      f"authoritative by this fixture policy; ARC does not select that oracle"}


# ---------------------------------------------------------------------------
# Participants and ledger. The ledger carries the mock-signed claims. A generator-only
# scenario stipulation is tracked separately — readable by no observer and no fold.
# ---------------------------------------------------------------------------

class Party:
    def __init__(self, ledger: "Ledger", name: str, key: str):
        self.ledger, self.name, self.key = ledger, name, key

    def emit(self, type_: str, predicate: str, ts: str, **kw) -> Event:
        ev = make(type_, self.key, predicate, ts, **kw)
        self.ledger.append(ev)
        claim = ev.payload.get("state")
        tail = f"  claims {claim!r} about {ev.payload.get('referent')}" if claim else ""
        print(f"    -> {self.name} {type_} {predicate}  [{ev.id}]{tail}")
        return ev


class Ledger:
    def __init__(self) -> None:
        self.events: list[Event] = []
        self.fixture_outcome: dict[str, str] = {}  # generator-only scenario stipulation

    def append(self, ev: Event) -> None:
        self.events.append(ev)

    def events_by_id(self) -> dict[str, Event]:
        return {e.id: e for e in self.events}


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


# ---------------------------------------------------------------------------
# The flow — run once, top to bottom.
# ---------------------------------------------------------------------------

def run() -> None:
    led = Ledger()
    REFERENT = "delivery:order-7"

    # The fixture stipulates that the parcel was not delivered. No observer, fold, or
    # mock-signature check below receives that stipulation.
    led.fixture_outcome[REFERENT] = "not_delivered"

    principal = Party(led, "principal", "k:principal")   # the buyer; granted, then disputes
    agent     = Party(led, "agent",     "k:agent")       # delegated; claims it delivered
    carrier   = Party(led, "carrier",   "k:carrier")     # a third party; signs a receipt
    commons   = Party(led, "commons",   "k:commons")     # the adjudicator

    print("\n1. Identity — every party anchors a key")
    for p in (principal, agent, carrier, commons):
        p.emit("KEY", "id.key_register", "2026-06-12T09:00:00Z", payload={"key": p.key})

    print("\n2. Mandate — principal delegates a purchase-and-deliver mandate to the agent")
    mandate = principal.emit("AUTHORIZE", "consent.mandate", "2026-06-12T10:00:00Z",
                             refs=("k:agent",),
                             scope={"category": "market", "max_total_krw": 30000})

    # -- Readout 1: record/referent boundary -----------------------------------
    print("\n3. Readout 1 — RECORD / REFERENT BOUNDARY")
    fulfilled = agent.emit("ATTEST", "commerce.fulfillment", "2026-06-12T11:00:00Z",
                           refs=(mandate.id,),
                           payload={"referent": REFERENT, "state": "delivered"})
    print("    verify_log: ", end="")
    verify_log(led.events)
    print("passes. The record contains k:agent's fixture-labeled delivery claim.")
    print("    It does not establish a delivery; this fixture performs no delivery.")

    # -- Readout 2: the contradiction the log CAN see --------------------------
    print("\n4. Readout 2 — RECORDED CLAIMS CONFLICT")
    say("principal", "I never received it")
    disputed = principal.emit("ATTEST", "commerce.fulfillment", "2026-06-12T12:00:00Z",
                              refs=(fulfilled.id,),
                              payload={"referent": REFERENT, "state": "not_received"})
    pairs = contradiction(led.events, REFERENT)
    for a, b in pairs:
        print(f"    contradiction: [{a}] and [{b}] claim different states for the same referent")
    print("    Both Events pass this fixture check; their payload claims conflict.")
    print("    This is the event-registry's 'partially exposed' — and it is the most the")
    print("    log can do unaided: surface the conflict, not adjudicate it.")
    r = resolve_by_log(led.events, REFERENT)
    print(f"    resolve-by-log: {r['verdict']}  ({r['reason']})")

    # -- Readout 3: receipts are additional records ----------------------------
    print("\n5. Readout 3 — ADDITIONAL OUTCOME CLAIM")
    say("agent", "here is the carrier's receipt — left at the door")
    carrier.emit("ATTEST", "commerce.fulfillment", "2026-06-12T12:30:00Z",
                 refs=(fulfilled.id,),
                 payload={"referent": REFERENT, "state": "delivered", "note": "left at door"})
    say("principal", "the carrier left it at the WRONG door / colluded — I still have nothing")
    print("    The receipt does not settle it. It is another record whose weight depends on")
    print("    the declared profile and observer policy. The principal can counter it:")
    r2 = resolve_by_log(led.events, REFERENT)
    print(f"    resolve-by-log (now with the carrier receipt): {r2['verdict']}  ({r2['reason']})")
    print("    Additional records do not by themselves establish the referent.")

    # -- Readout 4: adjudication under the named policy ------------------------
    print("\n6. Readout 4 — ADJUDICATION UNDER THE NAMED POLICY")
    challenge = principal.emit("CHALLENGE", "dispute.open", "2026-06-12T13:00:00Z",
                               refs=(fulfilled.id,),
                               payload={"referent": REFERENT, "claim": "non-delivery"})
    ruling = commons.emit("ADJUDICATE", "gov.ruling", "2026-06-12T15:00:00Z",
                          refs=(challenge.id, fulfilled.id),
                          payload={"referent": REFERENT, "state": "delivered"})
    adj = resolve_by_adjudication(led.events, REFERENT)
    print(f"    resolve-by-adjudication: {adj['verdict']} = {adj['state']!r}  ({adj['reason']})")
    print("    This fixture policy selects the ADJUDICATE as its terminal ruling.")
    print("    The adjudicator recorded a claim about the world; it did not measure")
    print("    the world. The fixture stipulates 'not_delivered'; the final ruling says")
    print("    'delivered'. The ruling is final under this policy and conflicts with the stipulation.")

    # -- Readout 5: without the privileged adjudicator -------------------------
    print("\n7. Readout 5 — WITHOUT THE PRIVILEGED ADJUDICATOR")
    print("    Treat every signer alike, without the policy that gives commons the last word,")
    print("    and the unprivileged claim comparison for 'did delivery happen?' returns:")
    res = resolve_by_log([e for e in led.events if e.type != "ADJUDICATE"], REFERENT)
    print(f"      {res['verdict']}  ({res['reason']})")
    print("    The difference is caused by the selected authority policy, not by additional")
    print("    evidence about the external outcome.")

    # -- External-attestor policy ----------------------------------------------
    print("\n8. Mitigation — PRIVILEGED EXTERNAL ATTESTOR (one named policy)")
    print("    Give one signer's ATTEST decisive weight — an escrow release wired to a")
    print("    carrier-API confirmation, an IoT delivery sensor, a provider settlement webhook.")
    orc = resolve_by_oracle(led.events, REFERENT, "k:carrier")
    print(f"    resolve-by-oracle(k:carrier): {orc['verdict']} = {orc['state']!r}")
    print(f"      ({orc['reason']})")
    print("    The result is deterministic under this policy, but the selected attestation")
    print("    remains a claim and may be inaccurate.")

    print(f"\nGenerated log: {len(led.events)} mock-signed fixture Events. verify_log's "
          f"identifier/mock-signature/key-registration checks pass.")
    verify_log(led.events)

    print("\n--- generator-only stipulation (observer folds never receive this) ---")
    print(f"    referent {REFERENT}: the fixture stipulates "
          f"{led.fixture_outcome[REFERENT]!r}.")
    print(f"    the log's final ruling says 'delivered'. the oracle says 'delivered'.")
    print("    neither record establishes the world referent.")

    print_finding()


def print_finding() -> None:
    print("""
What this probe exposes
-----------------------
  * Can this fixture establish an outcome from its mock signature?
      No. The deterministic hash covers a delivery-claim payload, not its referent.
      Under a production profile, verification can check the signature over the
      covered bytes against the configured public key; it still does not establish
      the world outcome.
  * What does this fixture compute?
      - a deterministic replay check over authored record bytes and signer labels;
      - contradictions between payload claims about one referent;
      - partial ordering by `refs` and a CHALLENGE record for the conflict.
  * What does it not establish?
      - which contradictory claim matches the external outcome;
      - the referent merely by adding receipts, witnesses, or counter-claims.
  * Does adjudication resolve it?
      Under the named authority policy, ADJUDICATE supplies the terminal ruling.
      That ruling remains a recorded claim about the external outcome.
  * What happens without the privileged-adjudicator policy?
      Without the policy that gives one signer the last word, this fixture returns
      CONTESTED — finding J, on the world axis.
  * What does the external-attestor policy add?
      A privileged external attestor supplies a selected claim under a named policy.
      The attestor's record may be inaccurate; selection does not establish truth.

Conclusion: this fixture preserves its authored claim bytes with deterministic hashes,
identifies contradictory payloads, and applies one named authority policy. Together,
those operations do not establish the record's world referent.

This complements finding M (interpretation) and finding O (time) with one authored
world-referent fixture.

No sixth type was required by this fixture. It adds no stored delivery oracle or
outcome score. This is a probe, not a protocol specification.
""")


if __name__ == "__main__":
    run()

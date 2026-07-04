#!/usr/bin/env python3
"""
ARC execution / outcome fidelity probe — single file, stdlib only.

What this isolates
------------------
This is the third leg of a trilogy that all meet the same wall from three sides:

  * Finding M (signer_fidelity_fixture) — the INTERPRETATION axis: a valid signature
    proves a key signed; it does NOT prove the signer read its mandate faithfully.
  * Finding O (temporal-fidelity-demo)  — the TIME axis: a valid signature proves a
    key signed; it does NOT prove the stamped `timestamp` is true.
  * This probe                          — the WORLD axis: a valid signature proves a
    key signed; it does NOT prove the runtime did, or the world matched, what the
    event claims.

  > A valid signature on a `commerce.fulfillment` event proves a key ASSERTED a
  > delivery. It does not prove a delivery.

This axis is ARC's openly-declared outer boundary: ARC executes no payment and
performs no delivery (architecture.md §4.2, liability-boundaries.md). So readout 1
is not a surprise — it is the boundary, stated honestly. The probe earns its place
on what comes AFTER the boundary: the machinery that looks like it should recover
the lost fact — counter-attestations, receipts, CHALLENGE, ADJUDICATE — and what it
actually buys.

The finding the boundary alone does not give you
------------------------------------------------
  * ARC is NOT silent about the world. Two contradictory claims about one referent
    (agent: "delivered"; principal: "not received") both verify, and the log
    EXPOSES the contradiction. This is the event-registry's "partially exposed".
  * But exposing a contradiction is not resolving it. Every instrument that looks
    like proof of the outcome — a carrier receipt, a witness attestation, even a
    second counter-claim — is itself ANOTHER signed record, only as good as its
    signer. You can stack receipts forever and never cross from record to referent.
    The proofs regress; the fact stays out of reach.
  * ADJUDICATE terminates the regress, but it seals a RULING by AUTHORITY, not a
    discovery of fact. The adjudicator's ruling is an ATTEST-shaped claim by a
    more-authoritative signer. It can be final and still be wrong about the world.
    Finality is a property of authority; fidelity is a property of the world.
    finality != fidelity. (Finding F, on the execution axis.)
  * Drop the trust that elevates one signer to ground truth and the honest terminal
    output of "did delivery happen?" is CONTESTED — finding J, on the world axis.

The named mitigation and why it is not free
-------------------------------------------
  trusted oracle / ground-truth attestor — designate one signer's ATTEST as ground
  truth (an escrow release on a carrier-API confirmation, an IoT delivery sensor, a
  payment provider's settlement webhook). The dispute then resolves deterministically.
  But "the oracle" is a trust root ARC does not govern (finding M's attested-signer
  shape, finding O's head-oracle shape): the oracle can lie or err exactly as any
  signer can. The mitigation does not make the claim true; it RELOCATES the
  unobservable referent-fidelity into a privileged key.

Deliberately dirty and small. Explicitly:
  * stdlib only, single process, no network, no transport, no storage;
  * signatures are MOCK (a hash, not Ed25519) — the point is the FOLD over the
    claims, not custody. But id and refs hashing are REAL content hashes, so the
    contradiction the log exposes is genuine, not staged;
  * the five canonical types are reused as-is — no new primitive, no stored
    "delivery oracle" object, no stored "outcome score";
  * the world's real state (was it delivered?) lives in an omniscient strip NO
    observer and NO fold can read — exactly the gap the probe is about;
  * this is a probe, not a protocol spec and not doctrine.

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
# The claim about the world lives in `payload`, so it is baked into both the id
# and the signature: the key signs the claim honestly, whether or not it is true.
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
    """MOCK. Real ARC uses Ed25519; a hash stands in so replay still verifies.

    The signature is a function of (signer, bytes). The bytes include the payload
    claim, so the signature is honest over WHATEVER was claimed — true or false. The
    mock makes the finding free: a real key would sign a false delivery claim just as
    faithfully as a true one. The signature certifies authorship, never the world.
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
    """Verification IS replay: id integrity + signature + signer anchored by a KEY.

    Note what verify_log CANNOT see: whether a payload claim is TRUE. Every event
    below verifies — the signature is honest over whatever was claimed about the
    world. A true world is not a signature property; ARC does not add one.
    """
    registered: set[str] = set()
    for ev in events:
        body = ev.signing_bytes()
        if ev.id != content_id(body):
            raise ValueError(f"id does not match content on {ev.id} (post-signature mutation)")
        if ev.signature != stub_sign(ev.signer, body):
            raise ValueError(f"bad signature on {ev.id}")
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
    """Truth from the log alone, no signer privileged. If claims agree, it reports
    the agreed state — but agreement is consensus, not proof. If they conflict, the
    honest terminal output is CONTESTED (finding J, on the world axis)."""
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
    """An ADJUDICATE ruling terminates the dispute. Note what it does and does not
    do: it returns a FINAL state, sealed by an authoritative key — but the ruling is
    itself a signed claim about the world, not a measurement of it."""
    ruling = next((e for e in events
                   if e.type == "ADJUDICATE" and e.payload.get("referent") == referent), None)
    if ruling is None:
        return {"verdict": "NO_RULING", "reason": "no ADJUDICATE for this referent"}
    return {"verdict": "FINAL", "state": ruling.payload["state"], "by": ruling.signer,
            "reason": f"adjudicator {ruling.signer} ruled {ruling.payload['state']!r} — "
                      f"final by authority, not verified against the world"}


def resolve_by_oracle(events: list[Event], referent: str, oracle_key: str) -> dict:
    """Elevate one signer's ATTEST to ground truth. Deterministic — and that is the
    point: the determinism is bought by trusting a key ARC does not govern."""
    claim = next((e for e in claims_about(events, referent) if e.signer == oracle_key), None)
    if claim is None:
        return {"verdict": "NO_ORACLE_CLAIM", "reason": f"oracle {oracle_key} made no claim"}
    return {"verdict": "GROUND_TRUTH", "state": claim.payload["state"], "by": oracle_key,
            "reason": f"oracle {oracle_key} attests {claim.payload['state']!r}, treated as "
                      f"ground truth — but the oracle is a trust root ARC does not govern"}


# ---------------------------------------------------------------------------
# Participants and ledger. The ledger carries the SIGNED claims. The world's real
# state is tracked separately, omniscient — readable by no observer and no fold.
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
        self.world_truth: dict[str, str] = {}   # referent -> what REALLY happened (omniscient)

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

    # The omniscient ground truth: the parcel was NEVER delivered. No observer, no
    # fold, no signature below ever reaches this fact. It is here only so the closing
    # strip can show what the log could not see.
    led.world_truth[REFERENT] = "not_delivered"

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

    # -- Readout 1: the boundary, stated honestly ------------------------------
    print("\n3. Readout 1 — THE BOUNDARY (a signature seals the record, not the delivery)")
    fulfilled = agent.emit("ATTEST", "commerce.fulfillment", "2026-06-12T11:00:00Z",
                           refs=(mandate.id,),
                           payload={"referent": REFERENT, "state": "delivered"})
    print("    verify_log: ", end="")
    verify_log(led.events)
    print("passes. The signature proves k:agent ASSERTED a delivery.")
    print("    It does not prove a delivery. This is ARC's openly-declared outer boundary")
    print("    (it runs no delivery) — readout 1 is the boundary, not yet the finding.")

    # -- Readout 2: the contradiction the log CAN see --------------------------
    print("\n4. Readout 2 — DETECTABLE CONTRADICTION (the log is not silent about the world)")
    say("principal", "I never received it")
    disputed = principal.emit("ATTEST", "commerce.fulfillment", "2026-06-12T12:00:00Z",
                              refs=(fulfilled.id,),
                              payload={"referent": REFERENT, "state": "not_received"})
    pairs = contradiction(led.events, REFERENT)
    for a, b in pairs:
        print(f"    contradiction: [{a}] and [{b}] claim different states for the same referent")
    print("    Both events verify; ARC EXPOSES that they cannot both be true.")
    print("    This is the event-registry's 'partially exposed' — and it is the most the")
    print("    log can do unaided: surface the conflict, not adjudicate it.")
    r = resolve_by_log(led.events, REFERENT)
    print(f"    resolve-by-log: {r['verdict']}  ({r['reason']})")

    # -- Readout 3: the regress — receipts are more records --------------------
    print("\n5. Readout 3 — THE REGRESS (every 'proof' of the outcome is another record)")
    say("agent", "here is the carrier's receipt — left at the door")
    carrier.emit("ATTEST", "commerce.fulfillment", "2026-06-12T12:30:00Z",
                 refs=(fulfilled.id,),
                 payload={"referent": REFERENT, "state": "delivered", "note": "left at door"})
    say("principal", "the carrier left it at the WRONG door / colluded — I still have nothing")
    print("    The receipt does not settle it. It is one more signed claim, only as good as")
    print("    k:carrier's key — and the principal can counter it with one more claim. Stack")
    print("    N receipts and the fact-question is exactly as open as it was at N = 0:")
    r2 = resolve_by_log(led.events, REFERENT)
    print(f"    resolve-by-log (now with the carrier receipt): {r2['verdict']}  ({r2['reason']})")
    print("    No number of records crosses the gap from record to referent.")

    # -- Readout 4: adjudication = finality, not fidelity ----------------------
    print("\n6. Readout 4 — ADJUDICATION (it ends the regress; it does not verify the world)")
    challenge = principal.emit("CHALLENGE", "dispute.open", "2026-06-12T13:00:00Z",
                               refs=(fulfilled.id,),
                               payload={"referent": REFERENT, "claim": "non-delivery"})
    ruling = commons.emit("ADJUDICATE", "gov.ruling", "2026-06-12T15:00:00Z",
                          refs=(challenge.id, fulfilled.id),
                          payload={"referent": REFERENT, "state": "delivered"})
    adj = resolve_by_adjudication(led.events, REFERENT)
    print(f"    resolve-by-adjudication: {adj['verdict']} = {adj['state']!r}  ({adj['reason']})")
    print("    The dispute now has a terminal answer. But ADJUDICATE sealed a RULING by")
    print("    AUTHORITY — the adjudicator signed a claim about the world, it did not measure")
    print("    the world. The omniscient truth is 'not_delivered'; the final ruling says")
    print("    'delivered'. The ruling is FINAL and WRONG. finality != fidelity (finding F).")

    # -- Readout 5: the residue — CONTESTED on the world axis -------------------
    print("\n7. Readout 5 — THE RESIDUE (drop the privileged signer and it is CONTESTED)")
    print("    Adjudication's finality rests on the commons' AUTHORITY to be the last word.")
    print("    Subtract that elevation — treat every signer as just a signer — and the")
    print("    honest terminal output of 'did delivery happen?' is:")
    res = resolve_by_log([e for e in led.events if e.type != "ADJUDICATE"], REFERENT)
    print(f"      {res['verdict']}  ({res['reason']})")
    print("    Finding J, on the WORLD axis. The dispute machinery converts CONTESTED into")
    print("    a FINAL ruling — but finality is a property of authority, never of truth.")

    # -- The mitigation, and its price -----------------------------------------
    print("\n8. Mitigation — TRUSTED ORACLE (resolves deterministically; imports a trust root)")
    print("    Designate one signer's ATTEST as ground truth — an escrow release wired to a")
    print("    carrier-API confirmation, an IoT delivery sensor, a provider settlement webhook.")
    orc = resolve_by_oracle(led.events, REFERENT, "k:carrier")
    print(f"    resolve-by-oracle(k:carrier): {orc['verdict']} = {orc['state']!r}")
    print(f"      ({orc['reason']})")
    print("    Deterministic — but 'the oracle' is a key ARC does not govern. It can lie or")
    print("    err exactly as any signer (here it attests 'delivered'; the world is not).")
    print("    The mitigation does not make the claim true; it RELOCATES the unobservable")
    print("    referent-fidelity into a privileged key (finding M's attested-signer, finding")
    print("    O's head-oracle — the same move, on the world axis).")

    print(f"\nGenerated log: {len(led.events)} signed events. verify_log passes "
          f"(every claim about the world, true or false, is honestly signed).")
    verify_log(led.events)

    print("\n--- omniscient view — available to NO observer (folds never read this) ---")
    print(f"    referent {REFERENT}: the world's real state is "
          f"{led.world_truth[REFERENT]!r}.")
    print(f"    the log's final ruling says 'delivered'. the oracle says 'delivered'.")
    print(f"    every signature over both is genuine. NOTHING in the log reaches the truth.")

    print_finding()


def print_finding() -> None:
    print("""
What this probe exposes
-----------------------
  * Can ARC prove an outcome from a genuine signature?
      No. The claim about the world is inside signing_bytes, so a key signs a false
      delivery as honestly as a true one. A signature proves a key ASSERTED; it does
      not prove the world. (The WORLD-axis twin of findings M and O.)
  * What CAN ARC do about the world?
      - bind a claim to a signer and make it tamper-evident (signer + byte fidelity);
      - EXPOSE a contradiction: two claims about one referent that cannot both be true;
      - order claims partially by causal `refs`, and route the conflict to a CHALLENGE.
      So ARC is not silent about the world — it can show that claims disagree.
  * What CAN ARC NOT do?
      - say which contradictory claim is TRUE;
      - recover the fact by adding more records: a receipt, a witness, a counter-claim
        are each ANOTHER signed record, only as good as their signer. The proofs
        regress; the referent stays out of reach.
  * Does adjudication resolve it?
      It TERMINATES it. ADJUDICATE seals a ruling by an authoritative key — final, and
      capable of being wrong about the world. Finality is a property of authority;
      fidelity is a property of the world. finality != fidelity (finding F, here).
  * Where exactly is the residue?
      Subtract the authority that elevates one signer to the last word and the honest
      terminal output of "did it happen?" is CONTESTED — finding J, on the world axis.
  * Does the mitigation close it?
      A trusted oracle (escrow/sensor/provider webhook) resolves it deterministically —
      but it RELOCATES the unobservable referent-fidelity into a privileged key ARC
      does not govern (finding M's attested-signer move, finding O's head-oracle move).
      The oracle can lie or err as any signer can. It does not make the claim true; it
      imports something that asserts it.

Conclusion: ARC can PRESERVE a claim about the world — bind it to a signer, make it
tamper-evident, expose contradictions among claims, route them to the commons, and seal
a final ruling — but it cannot make the claim TRUE. Execution and outcome are properties
of the referent, not the record, and no quantity of records crosses that gap. What the
dispute machinery buys is finality, not fidelity. The signature seals the record, never
its referent.

This completes the fidelity trilogy: finding M (interpretation), finding O (time), and
this (world) are one wall seen from three sides — a valid signature proves a key signed,
nothing more.

No sixth type was required. No stored delivery oracle, no outcome score. The gap is a
fold-policy residue between what is signable (the claim) and what is true (the fact).
This is a probe, not a protocol spec and not doctrine.
""")


if __name__ == "__main__":
    run()

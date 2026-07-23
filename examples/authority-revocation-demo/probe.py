#!/usr/bin/env python3
"""
ARC authority-revocation probe — single file, stdlib only.

What this isolates
------------------
The delegation probe in `examples/canon-fold-demo` (scenario 10, finding G) did
not select how a current reader should treat an earlier recorded act after a
mandate-withdrawal record. This probe compares two authored policies.

The fixture contains a delegation chain and a downstream-party record:

    human (principal)  --AUTHORIZE consent.mandate-->  agent A      [time T1]
    agent A            --AUTHORIZE consent.execute-->   the purchase [time T1]
    agent A / merchant --ATTEST payment / fulfillment-> done         [time T1]
    human              --AUTHORIZE consent.withdraw-->  withdrawal    [time T2]

At T1 the fixture's limited reference-and-withdrawal check returns a positive
reading for the purchase authorization, and mock outcome attestations follow. At
T2 the log receives a withdrawal record. The central question is
then: does a current reader continue to honor that recorded act?

The as-of-act-time view is only a historical baseline. It replays an earlier
Event subset that does not contain the later withdrawal record, so it is not the
same-events policy comparison. Against the SAME full current log, both policies
agree on the fixture outputs `authorized_at_act=True` and
`mandate_in_force_now=False`, but differ on current honoring:

  * preserve — completed_act_honored_now=True;
  * cascade  — completed_act_honored_now=False (not honored by this projection).

The fixture represents the withdrawal with the existing `nullifies` field on an
`AUTHORIZE consent.withdraw` Event. Its current-honoring result depends on the
supplied `preserve` or `cascade` policy.

Scope:
  * stdlib only, single process, no network, no transport, no storage;
  * signatures are MOCK (a hash, not Ed25519);
  * the five canonical types are reused as-is — no new primitive;
  * this is a probe, not a revocation spec and not doctrine.

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
    """MOCK. This fixture uses a deterministic hash for reproducible replay, not production security; ARC has no selected normative signature suite, so implementations and named profiles select and declare their suite."""
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
    """Fixture replay check: deterministic mock signature and key registration."""
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
    """Return the fixture Event subset recorded at or before `t`."""
    return [e for e in events if e.timestamp <= t]


# ---------------------------------------------------------------------------
# Fixture Projection: does a current reader honor the earlier recorded act?
# ---------------------------------------------------------------------------

def project_completed_act(events: list[Event], act_id: str, *, policy: str) -> dict:
    """Apply the fixture's reference/time check and current-honoring policy.

    The check looks for a referenced `AUTHORIZE consent.mandate` and for an
    `AUTHORIZE consent.withdraw` that names it in `nullifies`.

    `authorized_at_act` is the result of this fixture's limited reference and
    withdrawal-timing check; it does not validate complete scope, expiry, lineage,
    or execution authority. The policy knob controls whether a current reader
    returns its `completed_act_honored_now` field:

      * preserve — return honored for the earlier recorded act;
      * cascade  — return not honored for that act in this Projection.

    Nothing here is stored; this is recomputed on demand."""
    if policy not in {"preserve", "cascade"}:
        raise ValueError(f"unknown completed-act policy: {policy!r}")

    by_id = {e.id: e for e in events}
    act = by_id.get(act_id)
    if act is None:
        return {"act": act_id, "found": False}

    # first referenced AUTHORIZE consent.mandate in this fixture
    mandate = next((by_id[r] for r in act.refs
                    if r in by_id and by_id[r].predicate == "consent.mandate"), None)
    if mandate is None:
        return {
            "act": act_id, "found": True, "mandate": None, "policy": policy,
            "authorized_at_act": False,
            "mandate_in_force_now": False,
            "completed_act_honored_now": False,
            "reason": "no mandate referenced",
        }

    # withdrawals that name this mandate in `nullifies`
    withdrawals = [e for e in events
                   if e.type == "AUTHORIZE" and e.predicate == "consent.withdraw"
                   and mandate.id in e.nullifies]
    withdrawn_before_or_at_act = next(
        (w for w in withdrawals if w.timestamp <= act.timestamp), None
    )
    withdrawn_by = withdrawals[0] if withdrawals else None
    authorized_at_act = withdrawn_before_or_at_act is None
    mandate_in_force_now = withdrawn_by is None
    completed_act_honored_now = (
        authorized_at_act and (mandate_in_force_now or policy == "preserve")
    )

    if not authorized_at_act:
        reason = f"fixture found withdrawal {withdrawn_before_or_at_act.id} at or before act time"
    elif mandate_in_force_now:
        reason = "fixture found no withdrawal; act honored by selected policy"
    elif completed_act_honored_now:
        reason = "later withdrawal recorded; preserve policy returns honored"
    else:
        reason = "later withdrawal recorded; completed act not honored by this projection"

    return {
        "act": act_id, "found": True, "mandate": mandate.id, "policy": policy,
        "authorized_at_act": authorized_at_act,
        "mandate_in_force_now": mandate_in_force_now,
        "completed_act_honored_now": completed_act_honored_now,
        "reason": reason,
    }


# ---------------------------------------------------------------------------
# Fixture parties — each appends records with a configured key id.
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
        # The T1 fixture records land in the morning; the withdrawal (step 4) and
        # the later dispute/adjudication (step 5) land in the afternoon.
        hour = 10 if self._clock <= 8 else 16
        return f"2026-06-08T{hour:02d}:{self._clock:02d}:00Z"

    def append(self, ev: Event) -> None:
        self.events.append(ev)


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


# ---------------------------------------------------------------------------
# The flow — run once, top to bottom.
# ---------------------------------------------------------------------------

def run() -> None:
    led = Ledger()
    human = Party(led, "human", "k:human")          # the principal / buyer
    agentA = Party(led, "agent-A", "k:agentA")       # buyer's delegated agent
    merchant = Party(led, "merchant", "k:merchant")  # fixture downstream party

    print("\n1. Identity — each party records KEY id.key_register")
    for p in (human, agentA, merchant):
        p.emit("KEY", "id.key_register", payload={"key": p.key})

    print("\n2. Delegation at T1 — the human grants agent A a scoped mandate")
    say("human", "agent A may buy groceries up to 30000 KRW, expiring tonight")
    mandate = human.emit("AUTHORIZE", "consent.mandate", refs=("k:agentA",),
                         scope={"category": "groceries", "max_total_krw": 30000,
                                "expires_at": "2026-06-08T23:59:00Z"})

    print("\n3. Commerce at T1 — agent A records an act referencing the mandate")
    offer = merchant.emit("ATTEST", "commerce.offer",
                          payload={"item": "weekly_groceries", "price_krw": 24000})
    say("agent-A", "recording the fixture purchase authorization")
    act = agentA.emit("AUTHORIZE", "consent.execute", refs=(mandate.id, offer.id, "k:merchant"),
                      scope={"total_krw": 24000})
    agentA.emit("ATTEST", "commerce.payment_result", refs=(act.id, "k:merchant"),
                payload={"result": "confirmed", "amount_krw": 24000, "provider": "mock_pay"})
    say("merchant", "recording mock payment and fulfillment attestations")
    merchant.emit("ATTEST", "commerce.fulfillment", refs=(act.id,),
                  payload={"status": "delivered"})

    print("\n--- historical baseline: AS-OF-ACT-TIME event subset ---")
    print("    This earlier subset does not contain the later withdrawal record.")
    print("    The limited fixture check is not complete authority validation.")
    historical_baseline(led, act.id, as_of_t=act.timestamp)

    print("\n4. Revocation at T2 — later, the human withdraws agent A's mandate")
    say("human", "I no longer trust agent A; withdrawing the mandate")
    human.emit("AUTHORIZE", "consent.withdraw", refs=("k:agentA",), nullifies=(mandate.id,),
               payload={"reason": "agent_no_longer_trusted"})

    preserve = project_completed_act(led.events, act.id, policy="preserve")
    cascade = project_completed_act(led.events, act.id, policy="cascade")

    print("\n--- AFTER withdrawal record: shared fixture outputs from the FULL CURRENT LOG ---")
    show_shared_outputs(preserve)

    print("\n--- SAME FULL CURRENT LOG: preserve policy ---")
    show_policy_result(preserve)

    print("\n--- SAME FULL CURRENT LOG: cascade policy ---")
    show_policy_result(cascade)

    # ---- withdrawal record vs current-honoring and later ruling record ----
    print("\n5. Recording a later challenge and ruling about one act")
    say("human", "challenging this specific recorded purchase")
    dispute = human.emit("CHALLENGE", "dispute.open", refs=(act.id, "k:merchant"),
                         payload={"reason": "claims_act_exceeded_mandate"})
    say("community", "records a ruling that references the challenged act")
    merchant_community = Party(led, "community", "k:community")
    merchant_community.emit("KEY", "id.key_register", payload={"key": "k:community"})
    merchant_community.emit("ADJUDICATE", "gov.act_voided", refs=(act.id, dispute.id),
                            payload={"resolves": dispute.id})
    print("    The CHALLENGE and ADJUDICATE reference this act by id. This fixture")
    print("    does not project legal, payment, or operational consequences from them.")

    print(f"\nGenerated log: {len(led.events)} mock-signed fixture Events; running replay checks.")
    verify_log(led.events)
    print_finding()


def historical_baseline(led: Ledger, act_id: str, as_of_t: str) -> None:
    verify_log(led.events)
    result = project_completed_act(as_of(led.events, as_of_t), act_id, policy="preserve")
    print(f"    authorized_at_act={result['authorized_at_act']}")
    print(f"    mandate_in_force_in_baseline={result['mandate_in_force_now']}")


def show_shared_outputs(r: dict) -> None:
    print(f"    authorized_at_act={r['authorized_at_act']}")
    print(f"    mandate_in_force_now={r['mandate_in_force_now']}")


def show_policy_result(r: dict) -> None:
    print(f"    completed_act_honored_now={r['completed_act_honored_now']}"
          f"  (policy={r['policy']}; {r['reason']})")


def print_finding() -> None:
    print("""
What this probe exposes
-----------------------
  * What outputs are shared after the withdrawal record?
      This fixture's limited reference-and-withdrawal check returns
      authorized_at_act=True and mandate_in_force_now=False. It does not validate
      complete scope, expiry, lineage, or execution authority. Neither output
      changes between the two current-log policies.
  * Does a current reader continue to honor the earlier recorded act?
      Under preserve, completed_act_honored_now=True. Under cascade,
      completed_act_honored_now=False: it is not honored by this projection.
      The canon does not pick a current-honoring policy.
  * What does the as-of-act-time view report?
      It applies the same limited check to an earlier Event subset that excludes the
      withdrawal record. It is not the same-events policy comparison.
  * What does the later challenge section establish?
      It establishes only that the authored CHALLENGE and ADJUDICATE records
      reference one act. The fixture projects no legal or operational effect.
  * Which layers does the fixture distinguish?
        - the withdrawal is a MOCK-SIGNED EVENT (AUTHORIZE consent.withdraw);
        - whether a reader honors the completed act now is a PROJECTION choice;
        - the later ADJUDICATE is a separate ruling record referencing that act.
  * Where does the fixture leave current honoring?
      Preserve continues honoring the recorded act; cascade does not. Base ARC
      selects no default current-honoring policy; a deployment or named profile
      may select and identify that policy. The later ruling record is separate
      from the withdrawal Event.

This fixture uses the current Event types and compares two authored
current-honoring policies. It is not a revocation specification.
""")


if __name__ == "__main__":
    run()

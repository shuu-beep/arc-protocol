#!/usr/bin/env python3
"""
ARC end-to-end flow demo — single file, stdlib only.

Purpose
-------
The other probe (`examples/canon-fold-demo`) folds a *hand-built* event log to
test whether the five canonical types are sufficient. This probe asks the
complementary question: does a real interaction actually *produce* such a log?

So here the log is **generated**, not authored. Four participants — a human, a
consumer agent acting under that human, a merchant agent, and a community —
exchange messages and each emits its own signed events. Nothing in the final
log is written by hand; every event falls out of the flow:

    human  <->  consumer-agent  <->  merchant-agent
      |                                    |
   approval                           fulfillment
      |                                    |
   payment attest  ->  dispute  ->  adjudication

Then the SAME merchant-standing projection is recomputed at three points to
show that governance moves by *adding events*, never by mutating stored state
(authority-and-conflict.md): a dispute alone does not change commons standing;
only an ADJUDICATE does.

Deliberately dirty and small. Explicitly:
  * stdlib only, single process, no network, no transport layer;
  * signatures are MOCK (a hash, not Ed25519);
  * payment is MOCK (ARC never moves money — a payment enters only as an
    ATTEST claim about an external transfer, event-registry.md §8);
  * no new event type — the five canonical types are reused as-is;
  * messages between agents are transport and are NOT stored events; only the
    canonical events are.

This shows the canonical events *compose into a real flow*. It is not an
implementation of ARC.

Run:  python3 flow.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# The Event and its mock signing — same shape as canon-fold-demo, kept lean.
# ---------------------------------------------------------------------------

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}


@dataclass(frozen=True)
class Event:
    id: str
    type: str
    signer: str                       # key id, anchored by a prior KEY register
    predicate: str                    # namespaced semantic tag
    timestamp: str
    refs: tuple[str, ...] = ()
    scope: dict[str, Any] | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    signature: str = ""

    def signing_bytes(self) -> bytes:
        body = {
            "type": self.type, "signer": self.signer, "predicate": self.predicate,
            "timestamp": self.timestamp, "refs": self.refs,
            "scope": self.scope, "payload": self.payload,
        }
        return json.dumps(body, sort_keys=True, default=list).encode()


def stub_sign(signer: str, body: bytes) -> str:
    """MOCK. Real ARC uses Ed25519; a hash stands in so replay still verifies."""
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
    """Verification IS replay: check each signature and that the signer was
    anchored by a prior KEY register (object-model.md §5)."""
    registered: set[str] = set()
    for ev in events:
        if ev.signature != stub_sign(ev.signer, ev.signing_bytes()):
            raise ValueError(f"bad signature on {ev.id}")
        is_root = ev.type == "KEY" and ev.predicate == "id.key_register"
        if not is_root and ev.signer not in registered:
            raise ValueError(f"signer {ev.signer} not anchored by a KEY register ({ev.id})")
        if is_root:
            registered.add(ev.payload["key"])


# ---------------------------------------------------------------------------
# The projection that will be recomputed — same semantics as canon-fold-demo.
# ---------------------------------------------------------------------------

def project_merchant_standing(events: list[Event], merchant: str, context: str) -> dict:
    """Fold -> a context-scoped standing view. Two separated parts:
      * advisory   — a risk signal from outcome/dispute events; may raise
                     friction, may NOT punish.
      * governance — commons standing, changed ONLY by ADJUDICATE.
    Same shape as canon-fold-demo's standing fold, plus dispute resolution: a
    dispute counts as open until an ADJUDICATE references it. Recomputed on
    demand; nothing here is stored."""
    outcomes = [
        e for e in events
        if e.type == "ATTEST" and e.predicate == "rep.outcome"
        and merchant in e.refs and e.payload.get("context") == context
    ]
    positive = sum(1 for e in outcomes if e.payload.get("result") == "positive")
    negative = sum(1 for e in outcomes if e.payload.get("result") == "negative")
    resolved = {ref for e in events if e.type == "ADJUDICATE" for ref in e.refs}
    disputes = sum(
        1 for e in events
        if e.type == "CHALLENGE" and e.predicate == "dispute.open"
        and merchant in e.refs and e.id not in resolved
    )
    distinct_raters = len({e.signer for e in outcomes})

    advisory = "trusted" if positive >= 3 and disputes == 0 else \
               "limited" if positive >= 1 and negative + disputes <= 2 else \
               "unproven"
    if distinct_raters < 2:
        advisory = "unproven"  # too few independent counterparties to rely on

    governance = "in_good_standing"
    for e in sorted((e for e in events
                     if e.type == "ADJUDICATE" and e.predicate.startswith("gov.")
                     and merchant in e.refs), key=lambda e: e.timestamp):
        governance = {
            "gov.warning": "warned", "gov.suspension": "suspended",
            "gov.expulsion": "expelled", "gov.reinstatement": "in_good_standing",
        }.get(e.predicate, governance)

    return {
        "advisory_signal": advisory,        # computed risk signal, not a verdict
        "governance_standing": governance,   # commons fact, ADJUDICATE-only
        "open_disputes": disputes,
        "positive_outcomes": positive,
        "negative_outcomes": negative,
    }


# ---------------------------------------------------------------------------
# Participants. Each holds one key and emits its OWN events into the ledger.
# A message between participants is transport (a print), not a stored event.
# ---------------------------------------------------------------------------

class Party:
    def __init__(self, ledger: "Ledger", name: str, key: str):
        self.ledger, self.name, self.key = ledger, name, key

    def emit(self, type_: str, predicate: str, **kw) -> Event:
        ev = make(type_, self.key, predicate, self.ledger.now(), **kw)
        self.ledger.append(ev)
        print(f"    -> {self.name} emits {type_} {predicate}  [{ev.id}]")
        return ev


class Ledger:
    def __init__(self) -> None:
        self.events: list[Event] = []
        self._clock = 0

    def now(self) -> str:
        self._clock += 1
        return f"2026-06-08T10:{self._clock:02d}:00Z"

    def append(self, ev: Event) -> None:
        self.events.append(ev)


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


# ---------------------------------------------------------------------------
# The flow — run once, top to bottom. No branches.
# ---------------------------------------------------------------------------

MERCHANT = "k:merchant"
CONTEXT = "lunch"


def snapshot(ledger: Ledger, label: str) -> None:
    verify_log(ledger.events)  # every recompute re-verifies the log first
    s = project_merchant_standing(ledger.events, MERCHANT, CONTEXT)
    print(f"  PROJECTION [{label}]: "
          f"governance={s['governance_standing']}, advisory={s['advisory_signal']}, "
          f"open_disputes={s['open_disputes']}, "
          f"outcomes=+{s['positive_outcomes']}/-{s['negative_outcomes']}")


def run() -> Ledger:
    led = Ledger()
    community = Party(led, "community", "k:community")
    human = Party(led, "human", "k:human")
    consumer = Party(led, "consumer-agent", "k:consumer_agent")
    merchant = Party(led, "merchant-agent", MERCHANT)

    print("\n1. Identity — every participant registers a key (KEY id.key_register;")
    print("   bare registration — the registry §4.1 cost-gate anchor is out of scope here)")
    for p in (community, human, consumer, merchant):
        p.emit("KEY", "id.key_register", payload={"key": p.key})

    print("\n2. Offer — the merchant agent publishes a signed offer")
    say("merchant-agent", "gimbap set, 8000 KRW, valid 30 min")
    offer = merchant.emit("ATTEST", "commerce.offer",
                          payload={"item": "gimbap_set", "price_krw": 8000,
                                   "context": CONTEXT, "expires": "2026-06-08T10:40:00Z"})

    print("\n3. Approval — the consumer agent CANNOT approve; it asks the human")
    say("consumer-agent", "found a matching offer; presenting it for approval")
    say("human", "reviews terms... approves")  # the hard gate; no auto-execution
    approval = human.emit("AUTHORIZE", "consent.approval", refs=(offer.id, MERCHANT),
                          scope={"max_total_krw": 8000, "context": CONTEXT})

    print("\n4. Payment — recorded as a CLAIM about an external transfer (mock)")
    say("consumer-agent", "payment sent via an external provider; attesting the result")
    consumer.emit("ATTEST", "commerce.payment_result",
                  refs=(approval.id, MERCHANT),
                  payload={"result": "confirmed", "amount_krw": 8000, "provider": "mock_pay"})

    print("\n5. Fulfillment — the merchant agent attests delivery")
    merchant.emit("ATTEST", "commerce.fulfillment", refs=(offer.id,),
                  payload={"status": "delivered", "context": CONTEXT})

    snapshot(led, "after fulfillment")

    print("\n6. Dispute — the consumer was unhappy; opens a CHALLENGE + records outcome")
    say("consumer-agent", "item was wrong; opening a dispute and logging a negative outcome")
    dispute = consumer.emit("CHALLENGE", "dispute.open", refs=(MERCHANT,),
                            payload={"reason": "wrong_item", "context": CONTEXT})
    consumer.emit("ATTEST", "rep.outcome", refs=(MERCHANT,),
                  payload={"result": "negative", "context": CONTEXT})

    snapshot(led, "after dispute (note: governance unchanged — a dispute is not a verdict)")

    print("\n7. Adjudication — the community rules on the dispute (ADJUDICATE)")
    say("community", "reviewed the dispute; issues a warning")
    community.emit("ADJUDICATE", "gov.warning", refs=(MERCHANT, dispute.id),
                   payload={"context": CONTEXT, "resolves": dispute.id})

    snapshot(led, "after adjudication (governance now moved — by an added event)")

    print(f"\nGenerated log: {len(led.events)} signed events, none hand-written.")
    print("verify_log passed at every recompute; the projection is never stored.")
    return led  # so a reader (e.g. the reference-client viewer) can reuse the log


if __name__ == "__main__":
    run()

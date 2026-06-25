#!/usr/bin/env python3
"""
ARC local-commerce reference episode — the baseline happy path, made runnable.

Purpose
-------
This directory's README has long described a tiny local-commerce flow as prose
plus mock JSON artifacts, with the explicit next step (README §8): "turn
selected artifacts into reproducible fixture checks." This file is the first
thin runnable slice of that — the baseline happy-path order, generated as a
signed event log and folded back, with nothing about the transaction stored.

The point it makes is the ARC point, not a commerce point:

    A local commerce lifecycle is represented with canonical ARC events,
    without introducing a commerce-specific event type, and the "state" a
    marketplace would store — the order's status — is a PROJECTION recomputed
    from the log on demand, never a stored field. Commerce is one application
    of the authority / approval / audit protocol, not a schema of its own.

Deliberately dirty and small, like the other examples:
  * stdlib only, single process, single file, no network, no transport layer;
  * the Event / mock-signing / verify_log machinery is MIRRORED from
    `../end-to-end-demo/flow.py` so this example stays standalone (the repo's
    convention — each example runs on its own with no shared package);
  * signatures are MOCK (a hash, not Ed25519);
  * payment is MOCK — ARC moves no money; a payment enters only as an ATTEST
    claim about an external transfer (event-registry.md §2.4);
  * delivery is MOCK — a logistics agent ATTESTs a delivery claim, which proves
    a claim, never the delivery itself (the execution/outcome boundary);
  * no new event TYPE — the five canonical types are reused as-is; the logistics
    quote rides a new PREDICATE (`commerce.logistics_offer`), which is how ARC
    grows richness (event-registry.md §2.1: extend by predicate, not by type).

This is not an implementation of ARC, and a smooth mock flow is not evidence
that ARC is safe, fair, or viable — only that the canonical events compose into
a local-commerce lifecycle whose state is a fold.

Run:  python3 episode.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

# ===========================================================================
# Minimal canonical machinery — MIRRORED from ../end-to-end-demo/flow.py.
# Kept inline (not imported) so this example is standalone stdlib, matching the
# repo convention. Same Event shape, same mock signing, same replay-verify.
# ===========================================================================

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
        return f"2026-06-08T12:{self._clock:02d}:00Z"

    def append(self, ev: Event) -> None:
        self.events.append(ev)


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


# ===========================================================================
# The new fold — transaction state is a PROJECTION, not stored state.
# ===========================================================================

CONTEXT = "lunch"


def transaction_events(events: list[Event], txn_ref: str) -> list[Event]:
    """Recover one transaction's events from the log by transitive closure over
    `refs`, rooted at `txn_ref` (the offer event that opens the transaction).

    The transaction is NOT a stored object. There is no order record, no cart,
    no row in a table — only signed events that happen to reference one another.
    This function reconstitutes the transaction's event set on demand."""
    in_txn = {txn_ref}
    changed = True
    while changed:
        changed = False
        for e in events:
            if e.id in in_txn:
                continue
            if e.id == txn_ref or any(r in in_txn for r in e.refs):
                in_txn.add(e.id)
                changed = True
    return [e for e in events if e.id in in_txn]


def project_transaction_state(events: list[Event], txn_ref: str) -> str:
    """Fold the transaction's events into a single state label. Recomputed from
    the log every call; nothing is stored between calls. The "order status" a
    marketplace would persist is here just the furthest rung reached on the
    canonical-event ladder, with the commons override on top.

      pending_approval -> approved -> paid -> fulfilled        (happy path)
      disputed / adjudicated                                   (overrides)

    (A `cancelled` state belongs here too — a `nullifies` withdrawing the offer
    or approval — but `nullifies` is left to a later failure-run slice; the
    baseline never cancels.)"""
    txn = transaction_events(events, txn_ref)
    preds = {(e.type, e.predicate) for e in txn}
    has = lambda t, p: (t, p) in preds

    # Commons authority overrides the commercial ladder.
    if any(e.type == "ADJUDICATE" for e in txn):
        return "adjudicated"
    if has("CHALLENGE", "dispute.open"):
        return "disputed"

    # The happy-path ladder — furthest rung wins.
    if has("ATTEST", "commerce.fulfillment"):
        return "fulfilled"
    if has("ATTEST", "commerce.payment_result"):
        return "paid"
    if has("AUTHORIZE", "consent.approval"):
        return "approved"
    if has("ATTEST", "commerce.offer"):
        return "pending_approval"
    return "no_offer"


# ===========================================================================
# The baseline happy-path episode — generated, not authored.
# ===========================================================================

def snapshot(led: Ledger, txn_ref: str, label: str) -> None:
    verify_log(led.events)  # every recompute re-verifies the whole log first
    state = project_transaction_state(led.events, txn_ref)
    print(f"  STATE [{label}]: {state}   "
          f"(recomputed from {len(led.events)} events; not stored)")


def run() -> Ledger:
    led = Ledger()
    community = Party(led, "community", "k:community")
    human = Party(led, "human", "k:human")
    consumer = Party(led, "consumer-agent", "k:consumer_agent")
    merchant = Party(led, "merchant-agent", "k:merchant")
    logistics = Party(led, "logistics-agent", "k:logistics")

    print("\n1. Identity — every participant anchors a key (KEY id.key_register)")
    for p in (community, human, consumer, merchant, logistics):
        p.emit("KEY", "id.key_register", payload={"key": p.key})

    print("\n2. Intent — the consumer agent records what the human asked for")
    say("human", "lunch: a gimbap set under 9000 KRW, delivered")
    say("consumer-agent", "recording the intent so a fold can later check it was honored")
    intent = consumer.emit("ATTEST", "intent.canonical",
                           payload={"item": "gimbap_set", "max_total_krw": 9000,
                                    "delivery": True, "context": CONTEXT})

    print("\n3. Merchant offer — the merchant agent publishes signed terms")
    say("merchant-agent", "gimbap set, 7000 KRW, valid 30 min")
    offer = merchant.emit("ATTEST", "commerce.offer", refs=(intent.id,),
                          payload={"item": "gimbap_set", "price_krw": 7000,
                                   "context": CONTEXT, "expires": "2026-06-08T12:40:00Z"})
    txn = offer.id  # the offer opens the transaction; the fold roots here

    print("\n4. Logistics offer — a delivery quote (new PREDICATE, not a new type)")
    say("logistics-agent", "delivery in 12 min, 1500 KRW")
    logi = logistics.emit("ATTEST", "commerce.logistics_offer", refs=(offer.id,),
                          payload={"fee_krw": 1500, "eta_min": 12, "context": CONTEXT})

    snapshot(led, txn, "after offers")  # pending_approval — the human has not acted

    print("\n5. Approval — the consumer agent CANNOT approve; it asks the human")
    say("consumer-agent", "gimbap 7000 + delivery 1500 = 8500, under budget; presenting it")
    say("human", "reviews the combined terms... approves")  # the hard gate
    approval = human.emit("AUTHORIZE", "consent.approval",
                          refs=(offer.id, logi.id, "k:merchant"),
                          scope={"max_total_krw": 8500, "payee": "k:merchant",
                                 "context": CONTEXT})

    snapshot(led, txn, "after human approval")  # approved

    print("\n6. Payment — recorded as a CLAIM about an external transfer (mock)")
    say("consumer-agent", "paid via an external provider; attesting the result")
    consumer.emit("ATTEST", "commerce.payment_result",
                  refs=(approval.id, "k:merchant"),
                  payload={"result": "confirmed", "amount_krw": 8500, "provider": "mock_pay"})

    snapshot(led, txn, "after mock payment")  # paid

    print("\n7. Fulfillment — the logistics agent attests delivery (a claim)")
    say("logistics-agent", "delivered to the door; attesting it")
    logistics.emit("ATTEST", "commerce.fulfillment", refs=(offer.id, approval.id),
                   payload={"status": "delivered", "context": CONTEXT})

    snapshot(led, txn, "after fulfillment")  # fulfilled

    print("\n8. Outcome — the consumer logs a reputation signal (not a state change)")
    say("consumer-agent", "good order; logging a positive outcome")
    consumer.emit("ATTEST", "rep.outcome", refs=("k:merchant", approval.id),
                  payload={"result": "positive", "context": CONTEXT})

    # rep.outcome feeds the REPUTATION projection, not the transaction state —
    # the order is already 'fulfilled'; a rating does not move the order status.
    snapshot(led, txn, "after outcome (state unchanged — a rating is not a state)")

    print(f"\nGenerated log: {len(led.events)} signed events, none hand-written.")
    print("verify_log passed at every recompute; the transaction state was never")
    print("stored — it was folded from the log each time it was printed.")
    return led


if __name__ == "__main__":
    print("=" * 78)
    print("ARC local-commerce reference episode — baseline happy path")
    print("=" * 78)
    run()

#!/usr/bin/env python3
"""
ARC canon fold demo — single file, stdlib only.

Purpose
-------
Test whether the ARC canon survives contact with code. Specifically:

  1. that a "Relationship" is recoverable as a *fold over a signed Event log*,
     with no stored score and no stored profile (object-model.md §4-§6);
  2. that the five canonical event types — KEY, ATTEST, AUTHORIZE, CHALLENGE,
     ADJUDICATE — plus a `nullifies` field are sufficient to express identity,
     an offer, an approval, a payment claim, a fulfillment claim, reputation
     signals, a dispute, and a governance decision (event-registry.md §4, §9);
  3. that injecting one governed dispute (CHALLENGE -> ADJUDICATE) makes the
     *same* fold produce a *different* projection — i.e. governance works by
     adding events, never by mutating stored state (authority-and-conflict.md).

This is an exploratory probe, not an implementation. Signatures are stubbed
(a hash, not real crypto). If the five types turn out to be insufficient, the
gap is meant to show up here — that is the point.

Run:  python3 demo.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Callable

# ---------------------------------------------------------------------------
# 1. The Event — the ONLY stored/transmitted/verifiable unit (object-model §2.2)
# ---------------------------------------------------------------------------
# The type set is closed and small. Application richness lives in `predicate`
# and `payload`, never in new top-level types (event-registry §2.1). Withdrawal
# is the `nullifies` field, never a per-domain revoke type (event-registry §4.6).

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}


@dataclass(frozen=True)
class Event:
    id: str                       # content hash
    type: str                     # one of CANONICAL_TYPES
    signer: str                   # key id, resolvable via a prior KEY event
    predicate: str                # namespaced semantic tag (event-registry §6)
    timestamp: str
    refs: tuple[str, ...] = ()        # prior events / parties / resources
    nullifies: tuple[str, ...] = ()   # prior event ids withdrawn going forward
    scope: dict[str, Any] | None = None        # AUTHORIZE: budget/category/...
    contrary_to: tuple[str, ...] = ()          # AUTHORIZE: overridden warnings
    payload: dict[str, Any] = field(default_factory=dict)
    signature: str = ""

    def signing_bytes(self) -> bytes:
        body = {
            "type": self.type, "signer": self.signer, "predicate": self.predicate,
            "timestamp": self.timestamp, "refs": self.refs, "nullifies": self.nullifies,
            "scope": self.scope, "contrary_to": self.contrary_to, "payload": self.payload,
        }
        return json.dumps(body, sort_keys=True, default=list).encode()


def stub_sign(signer: str, body: bytes) -> str:
    """STUB. Real ARC uses Ed25519; here a hash stands in so replay still works."""
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


# ---------------------------------------------------------------------------
# 2. Verification IS replay (object-model §5)
# ---------------------------------------------------------------------------
# Before any fold is meaningful: verify each signature, and verify the signer
# was anchored by a prior KEY register event (key provenance). A KEY root is
# anchored from outside ARC by a cost gate, so it may self-anchor.

def verify_log(events: list[Event]) -> None:
    registered: set[str] = set()
    for ev in events:
        expected = stub_sign(ev.signer, ev.signing_bytes())
        if ev.signature != expected:
            raise ValueError(f"bad signature on {ev.id}")
        is_key_root = ev.type == "KEY" and ev.predicate == "id.key_register"
        if not is_key_root and ev.signer not in registered:
            raise ValueError(f"signer {ev.signer} has no prior KEY register ({ev.id})")
        if is_key_root:
            registered.add(ev.payload["key"])


def active(events: list[Event]) -> list[Event]:
    """Drop any event withdrawn by a later `nullifies` (event-registry §4.6)."""
    withdrawn = {ref for ev in events for ref in ev.nullifies}
    return [ev for ev in events if ev.id not in withdrawn]


# ---------------------------------------------------------------------------
# 3. Projections — deterministic folds, NOTHING stored (object-model §4)
# ---------------------------------------------------------------------------
# Each projection takes the whole log and returns a view that the caller uses
# and discards. There is no profile object, no score field, no status column.

def project_identity_status(events: list[Event], key: str) -> str:
    """Fold KEY + credential ATTEST + commons ADJUDICATE -> status (identity §4).

    Status is NOT a stored field — it is recomputed here every call."""
    evs = active(events)
    if not any(e.type == "KEY" and e.payload.get("key") == key for e in evs):
        return "unverified"
    status = "verified"
    if any(e.type == "ATTEST" and e.predicate == "id.credential"
           and key in e.refs for e in evs):
        status = "credentialed"
    # Only an ADJUDICATE (commons authority) may suspend/revoke (authority §5).
    for e in evs:
        if e.type == "ADJUDICATE" and key in e.refs:
            if e.predicate == "gov.suspension":
                status = "suspended"
            elif e.predicate == "gov.expulsion":
                status = "revoked"
            elif e.predicate == "gov.reinstatement":
                status = "verified"
    return status


def project_transaction_state(events: list[Event], tx_id: str) -> str:
    """Fold one transaction's events -> state (protocol §4, a projection)."""
    evs = [e for e in active(events) if tx_id in e.refs]
    state = "intent"
    has = lambda t, p: any(e.type == t and e.predicate == p for e in evs)
    if has("ATTEST", "commerce.offer"):
        state = "offer_received"
    if has("AUTHORIZE", "consent.approval"):
        state = "approved"
    if has("ATTEST", "commerce.payment_result"):
        state = "payment_confirmed"
    if has("ATTEST", "commerce.fulfillment"):
        state = "fulfilled"
    if has("CHALLENGE", "dispute.open"):
        state = "disputed"
    for e in evs:
        if e.type == "ADJUDICATE" and e.predicate.startswith("gov."):
            state = "resolved"
    return state


def project_merchant_standing(events: list[Event], merchant: str, context: str) -> dict:
    """Fold -> a CONTEXT-SCOPED standing view for one merchant.

    Two clearly separated parts (authority-and-conflict §5):
      * advisory  — a risk signal folded from rep.outcome / dispute signals.
                    It may raise friction; it may NOT punish.
      * governance — commons standing, changed ONLY by ADJUDICATE.

    Non-aggregated and contextual: outcomes are filtered by `context`, so there
    is no single global score for the merchant (object-model §2.1, reputation §3.1).
    """
    evs = active(events)
    outcomes = [
        e for e in evs
        if e.type == "ATTEST" and e.predicate == "rep.outcome"
        and merchant in e.refs and e.payload.get("context") == context
    ]
    positive = sum(1 for e in outcomes if e.payload.get("result") == "positive")
    negative = sum(1 for e in outcomes if e.payload.get("result") == "negative")
    disputes = sum(
        1 for e in evs
        if e.type == "CHALLENGE" and e.predicate == "dispute.open" and merchant in e.refs
    )
    # Sybil down-weight lives in the fold (object-model §8): trust counts only
    # from *distinct* counterparties, so circular self-dealing does not inflate.
    distinct_raters = len({e.signer for e in outcomes})

    advisory = "trusted" if positive >= 3 and disputes == 0 else \
               "limited"  if positive >= 1 and negative + disputes <= 2 else \
               "unproven"
    if distinct_raters < 2:
        advisory = "unproven"  # too few independent counterparties to rely on

    rulings = [
        e for e in evs
        if e.type == "ADJUDICATE" and e.predicate.startswith("gov.") and merchant in e.refs
    ]
    governance = "in_good_standing"
    for e in sorted(rulings, key=lambda e: e.timestamp):
        governance = {
            "gov.warning": "warned",
            "gov.suspension": "suspended",
            "gov.expulsion": "expelled",
            "gov.reinstatement": "in_good_standing",
        }.get(e.predicate, governance)

    return {
        "merchant": merchant,
        "context": context,
        "advisory_signal": advisory,         # computed risk signal, not a verdict
        "governance_standing": governance,    # commons fact, ADJUDICATE-only
        "evidence": {
            "positive_outcomes": positive,
            "negative_outcomes": negative,
            "open_disputes": disputes,
            "distinct_counterparties": distinct_raters,
        },
        "_note": "recomputed on demand from the event log; nothing here is stored",
    }


# ---------------------------------------------------------------------------
# 4. A hand-built event log (mock data — KRW local-food scenario)
# ---------------------------------------------------------------------------

CTX = "seoul-local-food/delivery"

def base_log() -> list[Event]:
    e: list[Event] = []
    # --- KEY: anchors (each anchored outside ARC by a cost gate) -------------
    e.append(make("KEY", "k:community", "id.key_register", "2026-01-01T00:00:00Z",
                  payload={"key": "k:community", "anchor": "community-charter"}))
    e.append(make("KEY", "k:merchant_bibimbap", "id.key_register", "2026-01-02T00:00:00Z",
                  payload={"key": "k:merchant_bibimbap", "anchor": "business-registration"}))
    for i in (1, 2, 3, 4):
        e.append(make("KEY", f"k:consumer_{i}", "id.key_register", f"2026-01-03T0{i}:00:00Z",
                      payload={"key": f"k:consumer_{i}", "anchor": "payment-account"}))

    # --- Four prior transactions, each: offer -> approval -> payment ---------
    #     -> fulfillment -> positive outcome. Builds context-scoped reputation.
    for i in (1, 2, 3):
        tx = f"tx_{i}"
        e.append(make("ATTEST", "k:merchant_bibimbap", "commerce.offer", f"2026-02-0{i}T10:00:00Z",
                      refs=(tx, "k:merchant_bibimbap"),
                      payload={"item": "vegetable bibimbap", "price_krw": 9800, "context": CTX}))
        e.append(make("AUTHORIZE", f"k:consumer_{i}", "consent.approval", f"2026-02-0{i}T10:01:00Z",
                      refs=(tx, "k:merchant_bibimbap"),
                      scope={"max_total_krw": 15000}, payload={"approved_total_krw": 12300}))
        e.append(make("ATTEST", f"k:consumer_{i}", "commerce.payment_result", f"2026-02-0{i}T10:02:00Z",
                      refs=(tx,), payload={"status": "confirmed", "amount_krw": 12300}))
        e.append(make("ATTEST", "k:merchant_bibimbap", "commerce.fulfillment", f"2026-02-0{i}T10:30:00Z",
                      refs=(tx,), payload={"status": "delivered"}))
        e.append(make("ATTEST", f"k:consumer_{i}", "rep.outcome", f"2026-02-0{i}T11:00:00Z",
                      refs=(tx, "k:merchant_bibimbap"),
                      payload={"result": "positive", "context": CTX}))
    return e


def disputed_tx_4(events: list[Event]) -> list[Event]:
    """Append a FOURTH transaction that goes wrong, then a governed dispute.

    Nothing already in the log is mutated — governance only adds events
    (authority-and-conflict §5). The same folds, re-run, yield new views.
    """
    tx = "tx_4"
    events.append(make("ATTEST", "k:merchant_bibimbap", "commerce.offer", "2026-03-01T10:00:00Z",
                       refs=(tx, "k:merchant_bibimbap"),
                       payload={"item": "vegetable bibimbap", "price_krw": 9800, "context": CTX}))
    events.append(make("AUTHORIZE", "k:consumer_4", "consent.approval", "2026-03-01T10:01:00Z",
                       refs=(tx, "k:merchant_bibimbap"),
                       scope={"max_total_krw": 15000}, payload={"approved_total_krw": 12300}))
    events.append(make("ATTEST", "k:consumer_4", "commerce.payment_result", "2026-03-01T10:02:00Z",
                       refs=(tx,), payload={"status": "confirmed", "amount_krw": 12300}))
    # paid, but never fulfilled -> consumer opens a dispute (CHALLENGE) ...
    events.append(make("CHALLENGE", "k:consumer_4", "dispute.open", "2026-03-01T12:00:00Z",
                       refs=(tx, "k:merchant_bibimbap"),
                       payload={"reason": "paid but not delivered"}))
    # negative outcome signal attached to the same context
    events.append(make("ATTEST", "k:consumer_4", "rep.outcome", "2026-03-01T12:05:00Z",
                       refs=(tx, "k:merchant_bibimbap"),
                       payload={"result": "negative", "context": CTX}))
    # ... and the community renders a decision (ADJUDICATE) — the ONLY event
    # that can change commons standing.
    events.append(make("ADJUDICATE", "k:community", "gov.suspension", "2026-03-03T09:00:00Z",
                       refs=(tx, "k:merchant_bibimbap"),
                       payload={"finding": "non-fulfillment after payment", "duration_days": 30}))
    return events


# ---------------------------------------------------------------------------
# 5. Run the probe: project before, then after the governed dispute.
# ---------------------------------------------------------------------------

def show(label: str, events: list[Event]) -> None:
    verify_log(events)  # replay: signatures + key provenance, before any fold
    print(f"\n{'=' * 66}\n{label}  ({len(events)} events in log)\n{'=' * 66}")
    standing = project_merchant_standing(events, "k:merchant_bibimbap", CTX)
    print("merchant standing  :", json.dumps(standing["evidence"]))
    print("  advisory signal   :", standing["advisory_signal"], "(risk signal — may raise friction, may not punish)")
    print("  governance standing:", standing["governance_standing"], "(commons fact — ADJUDICATE-only)")
    print("identity status     :", project_identity_status(events, "k:merchant_bibimbap"))
    print("tx_4 state          :", project_transaction_state(events, "tx_4"))


def main() -> None:
    log = base_log()
    show("BEFORE — three clean transactions", log)

    log = disputed_tx_4(log)
    show("AFTER  — tx_4 disputed (CHALLENGE) and adjudicated (ADJUDICATE)", log)

    print(f"\n{'-' * 66}")
    print("What changed, and how:")
    print("  * Same fold functions, same merchant, same context — only the log grew.")
    print("  * advisory_signal moved (a negative outcome + an open dispute entered the fold).")
    print("  * governance_standing -> suspended ONLY because an ADJUDICATE was added;")
    print("    no projection and no ordinary key could have produced that effect.")
    print("  * identity status -> suspended, tx_4 state -> resolved: all recomputed,")
    print("    never stored. Verification was replay over signed events throughout.")
    print(f"{'-' * 66}")
    print("Sufficiency: KEY, ATTEST, AUTHORIZE, CHALLENGE, ADJUDICATE + `nullifies`")
    print("covered identity, offer, approval, payment, fulfillment, reputation,")
    print("dispute, and governance with no sixth type. (See README for the verdict.)")


if __name__ == "__main__":
    main()

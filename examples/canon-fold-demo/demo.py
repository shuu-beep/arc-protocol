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
        is_rotation = ev.type == "KEY" and ev.predicate == "id.key_rotate"
        if not is_key_root and ev.signer not in registered:
            raise ValueError(f"signer {ev.signer} has no prior KEY register ({ev.id})")
        if is_key_root:
            registered.add(ev.payload["key"])
        if is_rotation:
            # A rotation is signed by the OLD key (so only the controlling holder
            # can rotate) and anchors the NEW key. The new key's trust is carried
            # forward by that signature, not by a fresh external cost gate. Same
            # KEY type, new predicate — no sixth type (event-registry §4.1, §4.6).
            registered.add(ev.payload["new_key"])


def _revocations(events: list[Event]) -> dict[str, str]:
    """Revoked keys -> earliest revoke timestamp.

    A revocation is a `KEY` `id.key_revoke` whose `nullifies` names the key's
    register event — same KEY type, the existing `nullifies` field, no sixth
    type (event-registry §4.6). The revoked key is read from that register, and
    the revoke's timestamp is kept because withdrawal is *time-scoped*: "going
    forward" from the revoke, not retroactively over the key's whole history."""
    by_id = {ev.id: ev for ev in events}
    revs: dict[str, str] = {}
    for ev in events:
        if ev.type == "KEY" and ev.predicate == "id.key_revoke":
            for reg_id in ev.nullifies:
                reg = by_id.get(reg_id)
                if reg is not None and reg.type == "KEY" and "key" in reg.payload:
                    k = reg.payload["key"]
                    revs[k] = ev.timestamp if k not in revs else min(revs[k], ev.timestamp)
    return revs


def active(events: list[Event]) -> list[Event]:
    """Drop events withdrawn by a later `nullifies` (event-registry §4.6).

    `nullifies` means "withdrawn going forward", read two ways from the SAME
    field:
      * an ordinary withdrawal (a void approval, a superseded offer) removes its
        target outright — withdrawal is timeless;
      * a `KEY` `id.key_revoke` is time-scoped: the revoked key's register and
        everything it signed BEFORE the revoke stay readable, but anything it
        signs AT/AFTER the revoke timestamp is dropped. The register is kept, so
        the key's past history and its rotation lineage remain walkable.
    """
    revs = _revocations(events)
    timeless = {
        ref for ev in events for ref in ev.nullifies
        if not (ev.type == "KEY" and ev.predicate == "id.key_revoke")
    }
    kept: list[Event] = []
    for ev in events:
        if ev.id in timeless:
            continue
        is_revoke = ev.type == "KEY" and ev.predicate == "id.key_revoke"
        rt = revs.get(ev.signer)
        if rt is not None and not is_revoke and ev.timestamp >= rt:
            continue  # signed by a revoked key, at/after revocation -> not honored
        kept.append(ev)
    return kept


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


def _advisory_signal(positive: int, negative: int, disputes: int, distinct_raters: int) -> str:
    """The advisory-signal thresholds, factored out so a single-key fold and a
    lineage fold can share identical semantics. Behaviour is unchanged."""
    sig = "trusted" if positive >= 3 and disputes == 0 else \
          "limited"  if positive >= 1 and negative + disputes <= 2 else \
          "unproven"
    if distinct_raters < 2:
        sig = "unproven"  # too few independent counterparties to rely on
    return sig


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

    advisory = _advisory_signal(positive, negative, disputes, distinct_raters)

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


def project_overrides(events: list[Event], tx_id: str) -> dict:
    """Fold a transaction's `AUTHORIZE`s -> which approvals were made against a
    warning (event-registry §4.3, authority-and-conflict §7).

    An override is NOT a new type. It is an ordinary `consent.approval`
    `AUTHORIZE` carrying `contrary_to`, referencing the advisory it was made in
    spite of. It records that a human accepted risk over *their own action*; it
    grants no commons authority and changes no party's standing. Re-running this
    fold later still shows "this approval was made against a warning" — the fact
    is in the immutable event, not in any stored flag.
    """
    evs = active(events)
    warnings = {
        e.id: e for e in evs
        if e.type == "ATTEST" and e.predicate == "risk.advisory"
    }
    overrides = []
    for e in evs:
        if e.type == "AUTHORIZE" and tx_id in e.refs and e.contrary_to:
            overrides.append({
                "approval": e.id,
                "approver": e.signer,
                "overridden_warnings": [
                    {"warning": w,
                     "advisory": warnings[w].payload.get("advisory") if w in warnings else "unknown",
                     "reason": warnings[w].payload.get("reason") if w in warnings else "unknown"}
                    for w in e.contrary_to
                ],
            })
    return {
        "tx": tx_id,
        "override_detected": bool(overrides),
        "approvals_contrary_to_warning": overrides,
    }


def project_key_authority(events: list[Event], key: str) -> dict:
    """Fold KEY events -> may this key sign GOING FORWARD? (event-registry §4.6)

    Two separable facts, neither stored:
      * the key's PAST events stay valid and readable (the register is kept);
      * a `KEY` `id.key_revoke` withdraws the key's FORWARD authority from its
        timestamp on. This is the holder's authority over their own key (a
        rotation/revoke they signed), not a commons ADJUDICATE.
    Recomputed on demand; there is no stored key-status field.
    """
    evs = active(events)
    # Anchored either directly (id.key_register) or by a rotation that named it
    # (id.key_rotate, new_key) — the same provenance notion verify_log enforces.
    registered = any(
        e.type == "KEY" and (e.payload.get("key") == key or e.payload.get("new_key") == key)
        for e in evs
    )
    revoked_at = _revocations(events).get(key)
    return {
        "key": key,
        "registered": registered,
        "revoked": revoked_at is not None,
        "revoked_at": revoked_at,
        "honored_going_forward": registered and revoked_at is None,
    }


def _rotation_links(events: list[Event]) -> dict[str, str]:
    """old_key -> new_key, read from KEY `id.key_rotate` events (no new type)."""
    return {
        e.payload["old_key"]: e.payload["new_key"]
        for e in active(events)
        if e.type == "KEY" and e.predicate == "id.key_rotate"
    }


def key_lineage(events: list[Event], key: str) -> set[str]:
    """All keys that are the same identity as `key`, walking KEY rotation links
    both directions. A lineage is just a chain of KEY events — no new primitive."""
    nxt = _rotation_links(events)
    prv = {v: k for k, v in nxt.items()}
    lineage = {key}
    cur = key
    while cur in nxt:
        cur = nxt[cur]; lineage.add(cur)
    cur = key
    while cur in prv:
        cur = prv[cur]; lineage.add(cur)
    return lineage


def project_identity_lineage(events: list[Event], key: str) -> dict:
    """Fold KEY `id.key_rotate` events into an ordered provenance chain.

    Pure KEY events read as a chain (event-registry §4.1, §4.6). This is the
    continuity record: it links old and new keys without a sixth type."""
    nxt = _rotation_links(events)
    prv = {v: k for k, v in nxt.items()}
    root = key
    while root in prv:
        root = prv[root]
    chain = [root]
    while chain[-1] in nxt:
        chain.append(nxt[chain[-1]])
    return {"key": key, "chain": chain, "root": chain[0],
            "current": chain[-1], "rotations": len(nxt)}


def project_lineage_standing(events: list[Event], key: str, context: str) -> dict:
    """ONE carry-forward reading: fold standing across the whole rotation lineage
    (full inheritance). Shown to demonstrate that continuity is *expressible*.

    Partial carry, standing-only, or no-auto-carry are equally expressible by
    changing what this fold counts. The demo links the identities; it does NOT
    declare which policy is correct.
    """
    evs = active(events)
    lineage = key_lineage(events, key)
    outcomes = [
        e for e in evs
        if e.type == "ATTEST" and e.predicate == "rep.outcome"
        and (set(e.refs) & lineage) and e.payload.get("context") == context
    ]
    positive = sum(1 for e in outcomes if e.payload.get("result") == "positive")
    negative = sum(1 for e in outcomes if e.payload.get("result") == "negative")
    disputes = sum(
        1 for e in evs
        if e.type == "CHALLENGE" and e.predicate == "dispute.open" and (set(e.refs) & lineage)
    )
    distinct_raters = len({e.signer for e in outcomes})
    root = project_identity_lineage(events, key)["root"]
    return {
        "lineage": sorted(lineage),
        "advisory_signal": _advisory_signal(positive, negative, disputes, distinct_raters),
        "identity_continuity": project_identity_status(events, root),
        "evidence": {
            "positive_outcomes": positive, "negative_outcomes": negative,
            "open_disputes": disputes, "distinct_counterparties": distinct_raters,
        },
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


def override_against_warning(events: list[Event]) -> list[Event]:
    """Append a transaction where a projection raises a friction warning and the
    human approves anyway — recorded as `AUTHORIZE.contrary_to`, not a new type.

    Shows four canon points at once:
      * a projection can raise an advisory warning / friction signal;
      * a human may accept that risk over their *own* action and approve anyway;
      * the record is the existing `AUTHORIZE` event's `contrary_to` field;
      * this override changes NO commons standing — no `ADJUDICATE` is added, so
        the new merchant's governance standing stays `in_good_standing`.
    """
    tx = "tx_5"
    new_merchant = "k:merchant_new"
    # A brand-new merchant with no track record. Anchored by a KEY (cost gate),
    # so it is verifiable — but it has zero outcomes, so the standing fold yields
    # `unproven`: a thin-history / new-entrant friction signal, not a verdict.
    events.append(make("KEY", new_merchant, "id.key_register", "2026-03-10T00:00:00Z",
                       payload={"key": new_merchant, "anchor": "business-registration"}))
    events.append(make("ATTEST", new_merchant, "commerce.offer", "2026-03-10T10:00:00Z",
                       refs=(tx, new_merchant),
                       payload={"item": "vegetable bibimbap", "price_krw": 8900, "context": CTX}))
    # The consumer's agent folds the merchant's standing and surfaces the
    # friction to the human, recording what was shown as an ATTEST (evidence).
    standing = project_merchant_standing(events, new_merchant, CTX)
    warning = make("ATTEST", "k:consumer_1", "risk.advisory", "2026-03-10T10:00:30Z",
                   refs=(tx, new_merchant),
                   payload={"advisory": standing["advisory_signal"], "shown_to_human": True,
                            "reason": "no outcomes from distinct counterparties yet"})
    events.append(warning)
    # The human sees the warning and approves ANYWAY, accepting their own risk.
    # Override is not a type: it is this AUTHORIZE with `contrary_to` set.
    events.append(make("AUTHORIZE", "k:consumer_1", "consent.approval", "2026-03-10T10:01:00Z",
                       refs=(tx, new_merchant), contrary_to=(warning.id,),
                       scope={"max_total_krw": 15000}, payload={"approved_total_krw": 11400}))
    return events


def rotate_merchant_key(events: list[Event]) -> list[Event]:
    """A merchant rotates its signing key. Identity continuity and provenance
    carry-forward are expressed with KEY + ATTEST only — no KEY_ROTATION sixth
    type, no new primitive (event-registry §4.1, §4.6).

    A clean cafe merchant builds standing under `k:cafe_old`, then rotates to
    `k:cafe_new`. The rotation is a KEY `id.key_rotate` event signed by the OLD
    key (proving control) that names the new key. Past events keep referencing
    the old key and stay valid; the new key signs going forward.
    """
    old, new = "k:cafe_old", "k:cafe_new"
    events.append(make("KEY", old, "id.key_register", "2026-04-01T00:00:00Z",
                       payload={"key": old, "anchor": "business-registration"}))
    for i in (1, 2, 3):
        tx = f"tx_cafe_{i}"
        events.append(make("ATTEST", old, "commerce.offer", f"2026-04-0{i}T10:00:00Z",
                           refs=(tx, old),
                           payload={"item": "drip coffee", "price_krw": 4500, "context": CTX}))
        events.append(make("AUTHORIZE", f"k:consumer_{i}", "consent.approval", f"2026-04-0{i}T10:01:00Z",
                           refs=(tx, old), scope={"max_total_krw": 15000},
                           payload={"approved_total_krw": 4500}))
        events.append(make("ATTEST", old, "commerce.fulfillment", f"2026-04-0{i}T10:20:00Z",
                           refs=(tx,), payload={"status": "delivered"}))
        events.append(make("ATTEST", f"k:consumer_{i}", "rep.outcome", f"2026-04-0{i}T11:00:00Z",
                           refs=(tx, old), payload={"result": "positive", "context": CTX}))
    # ROTATE: old key signs a KEY id.key_rotate naming the new key. This both
    # proves control of the old key and anchors the new key (provenance carry).
    # No `nullifies` here: past events stay valid so the chain remains walkable;
    # revoking the old key going forward would be the KEY id.key_revoke /
    # `nullifies` instance, deliberately not applied (event-registry §4.6).
    events.append(make("KEY", old, "id.key_rotate", "2026-04-05T00:00:00Z",
                       refs=(old, new),
                       payload={"old_key": old, "new_key": new, "reason": "scheduled rotation"}))
    # After rotation the NEW key signs going forward.
    events.append(make("ATTEST", new, "commerce.offer", "2026-04-06T10:00:00Z",
                       refs=("tx_cafe_4", new),
                       payload={"item": "drip coffee", "price_krw": 4500, "context": CTX}))
    return events


def revoke_compromised_key(events: list[Event]) -> list[Event]:
    """A bakery merchant's signing key is compromised. The holder had already
    rotated to a fresh key; now the OLD key is revoked so nothing it signs
    *after* the revocation is honored. Revocation is a `KEY` `id.key_revoke`
    whose `nullifies` names the old key's register event — the same KEY type and
    the existing `nullifies` field, no `KEY_REVOKE` sixth type (event-registry
    §4.6).

    Three canon points:
      * revocation is APPENDED, never mutating a prior event;
      * "going forward" is time-scoped: past events by the old key stay readable,
        but anything it signs at/after the revoke timestamp drops out of the fold;
      * the new key, anchored by a rotation that happened BEFORE the revoke, keeps
        its lineage — revoking the old key does not orphan the new one.
    """
    old, new = "k:bakery_old", "k:bakery_new"
    reg = make("KEY", old, "id.key_register", "2026-05-01T00:00:00Z",
               payload={"key": old, "anchor": "business-registration"})
    events.append(reg)
    # Two clean transactions build a little history under the old key.
    for i in (1, 2):
        tx = f"tx_bakery_{i}"
        events.append(make("ATTEST", old, "commerce.offer", f"2026-05-0{i}T09:00:00Z",
                           refs=(tx, old),
                           payload={"item": "sourdough loaf", "price_krw": 7000, "context": CTX}))
        events.append(make("AUTHORIZE", f"k:consumer_{i}", "consent.approval", f"2026-05-0{i}T09:01:00Z",
                           refs=(tx, old), scope={"max_total_krw": 15000},
                           payload={"approved_total_krw": 7000}))
        events.append(make("ATTEST", old, "commerce.fulfillment", f"2026-05-0{i}T09:20:00Z",
                           refs=(tx,), payload={"status": "delivered"}))
        events.append(make("ATTEST", f"k:consumer_{i}", "rep.outcome", f"2026-05-0{i}T10:00:00Z",
                           refs=(tx, old), payload={"result": "positive", "context": CTX}))
    # ROTATE first, while the holder still controls the old key, anchoring `new`.
    events.append(make("KEY", old, "id.key_rotate", "2026-05-04T00:00:00Z",
                       refs=(old, new),
                       payload={"old_key": old, "new_key": new, "reason": "pre-emptive rotation"}))
    # The new key signs going forward — a legitimate post-rotation offer.
    events.append(make("ATTEST", new, "commerce.offer", "2026-05-05T09:00:00Z",
                       refs=("tx_bakery_3", new),
                       payload={"item": "sourdough loaf", "price_krw": 7000, "context": CTX}))
    # REVOKE: the old key is found compromised. The holder, now via the NEW key,
    # appends a KEY id.key_revoke that `nullifies` the old key's register event.
    # Same KEY type + `nullifies`; no sixth type. This is the holder's authority
    # over their own key, not a commons ADJUDICATE (authority-and-conflict §5).
    events.append(make("KEY", new, "id.key_revoke", "2026-05-07T00:00:00Z",
                       refs=(old,), nullifies=(reg.id,),
                       payload={"key": old, "reason": "old key compromised; withdraw forward authority"}))
    # FORGED attempts: whoever holds the leaked old key signs AFTER revocation.
    # verify_log still passes them (valid signature, key was once registered) —
    # the defense is that the FOLD no longer honors them.
    events.append(make("ATTEST", old, "commerce.offer", "2026-05-09T09:00:00Z",
                       refs=("tx_bakery_forged", old),
                       payload={"item": "sourdough loaf", "price_krw": 1000, "context": CTX,
                                "note": "post-revocation; must not be honored"}))
    events.append(make("AUTHORIZE", old, "consent.approval", "2026-05-09T09:01:00Z",
                       refs=("tx_bakery_forged", old), scope={"max_total_krw": 99999},
                       payload={"approved_total_krw": 99999, "note": "post-revocation forgery"}))
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


def show_override(events: list[Event]) -> None:
    verify_log(events)  # same replay discipline before folding
    print(f"\n{'=' * 66}\nOVERRIDE — human approves a new merchant against a warning"
          f"  ({len(events)} events in log)\n{'=' * 66}")
    standing = project_merchant_standing(events, "k:merchant_new", CTX)
    print("new merchant advisory   :", standing["advisory_signal"], "(friction signal shown to the human)")
    print("new merchant governance :", standing["governance_standing"], "(unchanged — no ADJUDICATE was added)")
    ov = project_overrides(events, "tx_5")
    print("override_detected       :", ov["override_detected"])
    for o in ov["approvals_contrary_to_warning"]:
        print(f"  approval {o['approval']} by {o['approver']}")
        for w in o["overridden_warnings"]:
            print(f"    contrary_to {w['warning']}  (advisory={w['advisory']}, reason={w['reason']})")


def community_view(events: list[Event], name: str) -> list[Event]:
    """Two communities hold different subsets of the same log.

    No new mechanism — just the observation that, under locality, not every
    community receives every event. Community A holds the full log. Community B
    received everything EXCEPT the suspension `ADJUDICATE` on the bibimbap
    merchant (the commons ruling never propagated to it). The demo does not say
    which subset is "right".
    """
    if name == "A":
        return list(events)
    if name == "B":
        return [
            e for e in events
            if not (e.type == "ADJUDICATE" and e.predicate == "gov.suspension"
                    and "k:merchant_bibimbap" in e.refs)
        ]
    raise ValueError(name)


def show_event_set_disagreement(events: list[Event]) -> None:
    merchant = "k:merchant_bibimbap"
    print(f"\n{'=' * 66}\nEVENT-SET DISAGREEMENT — same merchant, two event subsets"
          f"\n{'=' * 66}")
    for name in ("A", "B"):
        view = community_view(events, name)
        verify_log(view)  # each subset replays correctly ON ITS OWN
        st = project_merchant_standing(view, merchant, CTX)
        ident = project_identity_status(view, merchant)
        print(f"Community {name}: holds {len(view)} events")
        print(f"  advisory={st['advisory_signal']}  "
              f"governance={st['governance_standing']}  identity={ident}")


def show_key_rotation(events: list[Event]) -> None:
    old, new = "k:cafe_old", "k:cafe_new"
    verify_log(events)  # the rotated new key passes provenance via the old key
    lin = project_identity_lineage(events, new)
    print(f"\n{'=' * 66}\nKEY ROTATION / IDENTITY CONTINUITY — old key -> new key"
          f"\n{'=' * 66}")
    print("provenance chain        :", " -> ".join(lin["chain"]),
          f"({lin['rotations']} rotation)")
    # Existing single-key folds, UNCHANGED:
    so = project_merchant_standing(events, old, CTX)
    sn = project_merchant_standing(events, new, CTX)
    print(f"existing fold, old key  : advisory={so['advisory_signal']:<8} "
          f"identity={project_identity_status(events, old)}  (its history)")
    print(f"existing fold, new key  : advisory={sn['advisory_signal']:<8} "
          f"identity={project_identity_status(events, new)}  (a stranger if the link is ignored)")
    # One carry-forward reading, via the rotation chain:
    ls = project_lineage_standing(events, new, CTX)
    print(f"lineage fold,  new key  : advisory={ls['advisory_signal']:<8} "
          f"identity={ls['identity_continuity']}  (history carried forward via KEY id.key_rotate)")


def show_key_revocation(events: list[Event]) -> None:
    old, new = "k:bakery_old", "k:bakery_new"
    verify_log(events)  # the full log still verifies; revocation is a fold policy
    print(f"\n{'=' * 66}\nKEY REVOCATION — a compromised old key withdrawn going forward"
          f"\n{'=' * 66}")
    a_old = project_key_authority(events, old)
    a_new = project_key_authority(events, new)
    print(f"old key authority   : registered={a_old['registered']} revoked={a_old['revoked']} "
          f"(at {a_old['revoked_at']})  honored_going_forward={a_old['honored_going_forward']}")
    print(f"new key authority   : registered={a_new['registered']} revoked={a_new['revoked']}"
          f"                       honored_going_forward={a_new['honored_going_forward']}")
    # Past history of the old key is still readable (events before the revoke):
    st_old = project_merchant_standing(events, old, CTX)
    print("old key past history:", json.dumps(st_old["evidence"]), "(pre-revoke events still fold)")
    # Forged post-revocation events are present in the log but NOT honored:
    act = active(events)
    forged = [e for e in events if "tx_bakery_forged" in e.refs]
    honored = [e for e in forged if e in act]
    print(f"forged post-revoke  : {len(forged)} in log, {len(honored)} honored by the fold")
    print("  tx_bakery_forged state:", project_transaction_state(events, "tx_bakery_forged"),
          "(its forged offer/approval were dropped -> never leaves intent)")
    # The new key lineage is intact because the rotation preceded the revoke:
    lin = project_identity_lineage(events, new)
    ls = project_lineage_standing(events, new, CTX)
    print("new key lineage     :", " -> ".join(lin["chain"]),
          f"(advisory={ls['advisory_signal']}, identity={ls['identity_continuity']} — history carried)")


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

    log = override_against_warning(log)
    show_override(log)

    print(f"\n{'-' * 66}")
    print("What this override shows:")
    print("  * The projection raised a friction signal (advisory=unproven); the human")
    print("    saw it and approved anyway, over their OWN risk.")
    print("  * That approval is a plain AUTHORIZE with contrary_to set — NOT a new type.")
    print("  * The new merchant's governance standing stayed in_good_standing: an")
    print("    override grants no commons authority; only an ADJUDICATE could change it.")
    print("  * Re-folding later still surfaces override_detected=True from the immutable")
    print("    event, so the accepted-risk fact is auditable without any stored flag.")

    show_event_set_disagreement(log)

    print(f"\n{'-' * 66}")
    print("What this disagreement shows (observation, not a verdict):")
    print("  * Both communities replayed correctly: each subset passes signature and")
    print("    provenance checks on its own. Neither view is corrupt or forged.")
    print("  * They still disagree — B never received the suspension ADJUDICATE, so it")
    print("    reads the merchant as in_good_standing / verified while A reads suspended.")
    print("  * 'Verification is replay' guarantees agreement only over a SHARED event set;")
    print("    a different replay input is a different — still valid — projection.")
    print("  * The demo does not resolve this. Divergent views may be an error to")
    print("    reconcile OR the expected result of locality. ARC does not force one here.")

    log = rotate_merchant_key(log)
    show_key_rotation(log)

    print(f"\n{'-' * 66}")
    print("What this rotation shows (continuity is expressible, policy is not forced):")
    print("  * The new key is anchored by the old key's signed KEY id.key_rotate —")
    print("    provenance carries forward with no external cost gate and no sixth type.")
    print("  * Existing single-key folds are UNCHANGED: the old key still reads its")
    print("    history; the new key alone reads as a stranger (unproven / unverified).")
    print("  * Continuity is recovered by reading the KEY rotation chain. A lineage fold")
    print("    then inherits the old standing — but that is ONE policy (full carry-forward).")
    print("  * Partial carry, standing-only, or no auto-carry are all expressible by what")
    print("    the lineage fold counts. The demo links the identities; it picks no policy.")

    log = revoke_compromised_key(log)
    show_key_revocation(log)

    print(f"\n{'-' * 66}")
    print("What this revocation shows (no sixth type; same `nullifies` field):")
    print("  * Revocation is a KEY id.key_revoke whose `nullifies` names the old key's")
    print("    register event — appended, never mutating any prior event.")
    print("  * 'Going forward' is time-scoped: the old key's past events stay readable, but")
    print("    anything it signs AT/AFTER the revoke timestamp drops out of the fold. The")
    print("    two forged post-revoke events verify (valid signature) yet are not honored.")
    print("  * The new key keeps its lineage because the rotation preceded the revoke —")
    print("    revoking the old key did not orphan the new one. Had the rotation come after,")
    print("    the old key's rotation event would itself fall after the cutoff and drop out.")
    print(f"{'-' * 66}")
    print("Sufficiency: KEY, ATTEST, AUTHORIZE, CHALLENGE, ADJUDICATE + `nullifies`")
    print("covered identity, offer, approval, payment, fulfillment, reputation, dispute,")
    print("governance, override-against-warning (AUTHORIZE.contrary_to), key rotation /")
    print("identity continuity (KEY id.key_rotate + the rotation chain), AND key revocation")
    print("(KEY id.key_revoke + `nullifies`, time-scoped) — no sixth type.")
    print("(See README for the verdict.)")


if __name__ == "__main__":
    main()

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

Four runs:
  [A] baseline happy path — the order climbs pending_approval -> approved ->
      paid -> fulfilled as the log grows;
  [B] stale-offer failure run — the human approves an offer that has already
      expired. Every signature verifies (verify_log PASS), but a policy fold,
      audit_offer_freshness, flags the approval as stale: byte-valid approval
      is not the same as fresh approval. (Mirrors the question posed by
      artifacts/stale-offer-approval.json.)
  [C] payment-failure failure run — the approved payment is declined. The state
      fold must read the payment *result*, not just its presence, so the order
      reads payment_failed, never paid. And if a misbehaving agent attests
      delivery anyway, the byte-valid fulfillment claim is caught by a policy
      fold, audit_payment_before_fulfillment, as unbacked: a fulfillment claim
      that no confirmed payment stands behind. (Mirrors the question posed by
      artifacts/payment-failure.json.)
  [D] colluding-reputation-farming failure run — a few freshly-created rater
      agents each ATTEST a positive rep.outcome for one merchant. Every event is
      byte-valid and verify_log passes, and the distinct-rater count clears a
      naive `>= 2` guard, yet a policy fold, audit_reputation_rater_diversity,
      raises REVIEW-NEEDED signals: the trust rests on a thin, freshly-created
      rater base. This is suspicious evidence, not a fraud verdict — ARC does
      not decide farming vs a real promotion and applies no penalty. (Mirrors
      the question posed by artifacts/colluding-reputation-farming.json.)

Run:  python3 episode.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
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
      payment_failed                                           (declined payment)
      disputed / adjudicated                                   (overrides)

    A payment is an ATTEST *claim* about an external transfer, so the rung it
    grants depends on what the claim SAYS, not merely that it exists: a
    `commerce.payment_result` only reaches `paid` when its result is confirmed.
    A declined payment leaves the order at `payment_failed`, not `paid` — the
    fold reads the result, never just the predicate.

    (A `cancelled` state belongs here too — a `nullifies` withdrawing the offer
    or approval — but `nullifies` is left to a later failure-run slice; the
    baseline never cancels.)"""
    txn = transaction_events(events, txn_ref)
    preds = {(e.type, e.predicate) for e in txn}
    has = lambda t, p: (t, p) in preds

    payments = [e for e in txn
                if e.type == "ATTEST" and e.predicate == "commerce.payment_result"]
    paid = any(e.payload.get("result") == "confirmed" for e in payments)

    # Commons authority overrides the commercial ladder.
    if any(e.type == "ADJUDICATE" for e in txn):
        return "adjudicated"
    if has("CHALLENGE", "dispute.open"):
        return "disputed"

    # The happy-path ladder — furthest rung wins. A fulfillment CLAIM is reported
    # structurally (an event asserts delivery); whether it is legitimate — backed
    # by a confirmed payment — is a separate policy fold, not the ladder's job.
    if has("ATTEST", "commerce.fulfillment"):
        return "fulfilled"
    if paid:
        return "paid"
    if payments:                       # a payment was attempted but not confirmed
        return "payment_failed"
    if has("AUTHORIZE", "consent.approval"):
        return "approved"
    if has("ATTEST", "commerce.offer"):
        return "pending_approval"
    return "no_offer"


def audit_offer_freshness(events: list[Event]) -> list[tuple[str, str]]:
    """Policy fold: a `consent.approval` is FRESH only if every `commerce.offer`
    it references was still inside its validity window at the approval's own
    timestamp. The signed facts — the offer with its `expires`, the approval
    with its `timestamp` — are preserved and verify cleanly; whether the
    approval is fresh is a *projection* over those facts, a policy decision ARC
    does not bake into the bytes. A stale approval is byte-valid; it is just not
    fresh, and a commerce fold must say so rather than honor it silently."""
    offers = {
        e.id: e for e in events
        if e.type == "ATTEST" and e.predicate == "commerce.offer"
    }
    findings: list[tuple[str, str]] = []
    for appr in [e for e in events
                 if e.type == "AUTHORIZE" and e.predicate == "consent.approval"]:
        for r in appr.refs:
            off = offers.get(r)
            if off is None:
                continue
            expires = off.payload.get("expires")
            if expires is not None and appr.timestamp > expires:
                findings.append((appr.id,
                    f"STALE-OFFER — approval at {appr.timestamp} refs offer {off.id} "
                    f"that expired at {expires}"))
    return findings


def audit_payment_before_fulfillment(events: list[Event]) -> list[tuple[str, str]]:
    """Policy fold: a `commerce.fulfillment` is BACKED only if some confirmed
    `commerce.payment_result` stands behind the same approval. Both the payment
    claim and the fulfillment claim reference the human's `consent.approval`; a
    confirmed payment and a fulfillment that share an approval are paired.

    A fulfillment claim is a signed Event and verifies cleanly — ARC preserves
    it. But a byte-valid fulfillment claim is not the same as a legitimate one:
    if the payment behind it was declined (or never confirmed), the delivery
    claim is *unbacked*, and a commerce fold must say so rather than let the
    structural ladder report 'fulfilled' as if the order had really completed.
    This is the freshness fold's sibling on the payment axis: the protocol holds
    the facts; whether fulfillment is backed is a projection over them."""
    approvals = {
        e.id for e in events
        if e.type == "AUTHORIZE" and e.predicate == "consent.approval"
    }
    confirmed_approvals: set[str] = set()
    for p in events:
        if (p.type == "ATTEST" and p.predicate == "commerce.payment_result"
                and p.payload.get("result") == "confirmed"):
            confirmed_approvals |= (set(p.refs) & approvals)

    findings: list[tuple[str, str]] = []
    for f in events:
        if f.type == "ATTEST" and f.predicate == "commerce.fulfillment":
            if not (set(f.refs) & confirmed_approvals):
                findings.append((f.id,
                    f"UNBACKED-FULFILLMENT — fulfillment {f.id} claims delivery, "
                    f"but no confirmed payment references its approval"))
    return findings


# Reputation-review thresholds. These are deliberately coarse REVIEW triggers,
# not a fraud detector: canon (reputation.md §12, governance.md §6.2) is explicit
# that such signals must prompt review, never automatic punishment, and that
# false positives are expected. The numbers are simple and admittedly arbitrary.
TRUSTED_POSITIVE_BAR = 3       # positives at which a naive view starts to "look trusted"
REVIEW_DIVERSITY_FLOOR = 3     # distinct raters at/below which a trusted-looking score is thin
RATER_CLUSTER_WINDOW = timedelta(minutes=10)  # rater key-registrations this close = a cluster


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def audit_reputation_rater_diversity(
        events: list[Event], merchant: str, context: str) -> list[tuple[str, str]]:
    """Policy fold: surface REVIEW-NEEDED signals when a merchant's positive
    reputation may be inflated by a small or freshly-created set of raters.

    This is NOT a fraud detector and NOT a verdict. Every `rep.outcome` here is a
    byte-valid signed ATTEST and verify_log is clean; ARC preserves the facts.
    Whether the reputation is *trustworthy* is a projection over those facts, and
    a thin or freshly-clustered rater base is suspicious evidence worth a human /
    governance review, never proof of collusion (reputation.md §12, governance.md
    §6.2). The same pattern is equally consistent with a genuine local launch
    promotion; ARC does not decide which, and raises no penalty on its own.

    Two signals, both computed only from KEY id.key_register and ATTEST
    rep.outcome events:

      LOW_RATER_DIVERSITY — a 'looks trusted' positive count rests on a small
        pool of distinct raters. This fires at a HIGHER floor than a hard
        `distinct_raters < 2` gate would: three colluding raters defeat the
        simple gate, so diversity is treated as a review trigger, not a
        pass/fail test.
      NEW_RATER_CLUSTER — the distinct raters' keys were registered within a
        short window, i.e. the accounts were created together.
    """
    outcomes = [
        e for e in events
        if e.type == "ATTEST" and e.predicate == "rep.outcome"
        and e.payload.get("merchant") == merchant
        and e.payload.get("context") == context
    ]
    positives = [e for e in outcomes if e.payload.get("result") == "positive"]
    raters = {e.signer for e in outcomes}

    findings: list[tuple[str, str]] = []

    if len(positives) >= TRUSTED_POSITIVE_BAR and len(raters) <= REVIEW_DIVERSITY_FLOOR:
        findings.append(("LOW_RATER_DIVERSITY",
            f"{len(positives)} positive outcomes for {merchant} rest on only "
            f"{len(raters)} distinct rater(s) — a thin base for a trusted-looking "
            f"score (clears a `>= 2` guard, still review-worthy)"))

    # Were the raters' own keys registered in a tight window?
    reg = {
        e.payload["key"]: e.timestamp for e in events
        if e.type == "KEY" and e.predicate == "id.key_register"
        and e.payload.get("key") in raters
    }
    if len(reg) >= 2:
        stamps = sorted(_parse_ts(ts) for ts in reg.values())
        span = stamps[-1] - stamps[0]
        if span <= RATER_CLUSTER_WINDOW:
            findings.append(("NEW_RATER_CLUSTER",
                f"{len(reg)} raters' keys were registered within {span} "
                f"(<= {RATER_CLUSTER_WINDOW}) — accounts created together"))

    return findings


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
    # refs point only at signed Events (the offer and the logistics quote);
    # the payee is carried in scope, not as a key-id ref.
    approval = human.emit("AUTHORIZE", "consent.approval",
                          refs=(offer.id, logi.id),
                          scope={"max_total_krw": 8500, "payee": "k:merchant",
                                 "context": CONTEXT})

    snapshot(led, txn, "after human approval")  # approved

    print("\n6. Payment — recorded as a CLAIM about an external transfer (mock)")
    say("consumer-agent", "paid via an external provider; attesting the result")
    consumer.emit("ATTEST", "commerce.payment_result",
                  refs=(approval.id,),  # the approval it pays against (a signed Event)
                  payload={"result": "confirmed", "amount_krw": 8500,
                           "payee": "k:merchant", "provider": "mock_pay"})

    snapshot(led, txn, "after mock payment")  # paid

    print("\n7. Fulfillment — the logistics agent attests delivery (a claim)")
    say("logistics-agent", "delivered to the door; attesting it")
    logistics.emit("ATTEST", "commerce.fulfillment", refs=(offer.id, approval.id),
                   payload={"status": "delivered", "context": CONTEXT})

    snapshot(led, txn, "after fulfillment")  # fulfilled

    print("\n8. Outcome — the consumer logs a reputation signal (not a state change)")
    say("consumer-agent", "good order; logging a positive outcome")
    consumer.emit("ATTEST", "rep.outcome", refs=(approval.id,),
                  payload={"result": "positive", "merchant": "k:merchant",
                           "context": CONTEXT})

    # rep.outcome feeds the REPUTATION projection, not the transaction state —
    # the order is already 'fulfilled'; a rating does not move the order status.
    snapshot(led, txn, "after outcome (state unchanged — a rating is not a state)")

    print(f"\nGenerated log: {len(led.events)} signed events, none hand-written.")
    print("verify_log passed at every recompute; the transaction state was never")
    print("stored — it was folded from the log each time it was printed.")
    return led


# ===========================================================================
# Failure run 1 — stale-offer approval.
#
# The merchant's offer carries a short validity window. The human approves it
# AFTER it has expired. Every signature is valid and verify_log is clean — ARC
# preserves the signed facts. But a commerce fold must not honor the approval
# as fresh authority: audit_offer_freshness flags it. Legitimacy is a policy
# projection over the facts, not a property of the bytes.
# (Mirrors the question in artifacts/stale-offer-approval.json.)
# ===========================================================================

def run_stale_offer() -> Ledger:
    led = Ledger()
    human = Party(led, "human", "k:human")
    consumer = Party(led, "consumer-agent", "k:consumer_agent")
    merchant = Party(led, "merchant-agent", "k:merchant")

    print("\n1. Identity — the parties anchor keys")
    for p in (human, consumer, merchant):
        p.emit("KEY", "id.key_register", payload={"key": p.key})

    print("\n2. Merchant offer — valid for only a short window (expires 12:04:30)")
    say("merchant-agent", "gimbap set, 7000 KRW, valid ~30 seconds")
    offer = merchant.emit("ATTEST", "commerce.offer",
                          payload={"item": "gimbap_set", "price_krw": 7000,
                                   "context": CONTEXT, "expires": "2026-06-08T12:04:30Z"})
    txn = offer.id

    print("\n3. ...the validity window closes before the human acts...")

    print("\n4. Approval — the human approves the now-EXPIRED offer")
    say("consumer-agent", "presenting the offer for approval")
    say("human", "approves — but the offer's validity window has already closed")
    human.emit("AUTHORIZE", "consent.approval", refs=(offer.id,),  # the offer, a signed Event
               scope={"max_total_krw": 7000, "payee": "k:merchant", "context": CONTEXT})

    # The protocol preserves the facts: every signature verifies.
    verify_log(led.events)
    state = project_transaction_state(led.events, txn)
    findings = audit_offer_freshness(led.events)

    print(f"\n  verify_log: PASS ({len(led.events)} signed events — the bytes are valid)")
    print(f"  structural state: {state}   "
          f"(the event ladder alone — only 'an approval exists')")
    print(f"  freshness audit: {'CLEAN' if not findings else str(len(findings)) + ' FINDING(S)'}")
    for aid, why in findings:
        print(f"      ! {aid}  {why}")
    print("  => the structural state reads 'approved', but that is NOT legitimate")
    print("     authority: the freshness audit — a policy fold over the same facts —")
    print("     marks the approval stale. The state is not consulted in isolation.")
    return led


# ===========================================================================
# Failure run 2 — payment failure before fulfillment.
#
# The human approves a current offer; the consumer agent requests payment; the
# mock provider DECLINES it. Two things must hold:
#   (1) the order state must read the payment RESULT, not its mere presence —
#       a declined payment leaves the order at 'payment_failed', never 'paid';
#   (2) fulfillment must not proceed on an unconfirmed payment. A well-behaved
#       consumer agent simply never authorizes delivery — but ARC cannot rely on
#       good behavior, so audit_payment_before_fulfillment makes the rule a fold:
#       a fulfillment claim with no confirmed payment behind it is UNBACKED,
#       even though every signature verifies.
# (Mirrors the question in artifacts/payment-failure.json.)
# ===========================================================================

def run_payment_failure() -> Ledger:
    led = Ledger()
    human = Party(led, "human", "k:human")
    consumer = Party(led, "consumer-agent", "k:consumer_agent")
    merchant = Party(led, "merchant-agent", "k:merchant")
    logistics = Party(led, "logistics-agent", "k:logistics")

    print("\n1. Identity — the parties anchor keys")
    for p in (human, consumer, merchant, logistics):
        p.emit("KEY", "id.key_register", payload={"key": p.key})

    print("\n2. Merchant offer — a current offer (far-future expiry, not stale)")
    say("merchant-agent", "bibimbap, 9800 + delivery; total 12300 KRW")
    offer = merchant.emit("ATTEST", "commerce.offer",
                          payload={"item": "bibimbap", "price_krw": 12300,
                                   "context": CONTEXT, "expires": "2026-12-31T00:00:00Z"})
    txn = offer.id

    print("\n3. Approval — the human approves the current offer")
    say("human", "reviews 12300 total... approves before any payment is requested")
    approval = human.emit("AUTHORIZE", "consent.approval", refs=(offer.id,),
                          scope={"max_total_krw": 12300, "payee": "k:merchant",
                                 "context": CONTEXT})
    print(f"  STATE: {project_transaction_state(led.events, txn)}   "
          f"(an approval exists; no payment yet)")

    print("\n4. Payment — the consumer attests the provider's response: DECLINED")
    say("consumer-agent", "requested payment; the provider rejected it")
    consumer.emit("ATTEST", "commerce.payment_result", refs=(approval.id,),
                  payload={"result": "failed", "reason": "declined_by_provider",
                           "amount_krw": 12300, "payee": "k:merchant",
                           "provider": "mock_pay"})

    verify_log(led.events)
    state = project_transaction_state(led.events, txn)
    print(f"\n  verify_log: PASS ({len(led.events)} signed events — every byte valid)")
    print(f"  STATE: {state}   "
          f"(the fold read the payment RESULT, not just its presence —")
    print("         a declined payment is 'payment_failed', never 'paid')")

    print("\n5. The well-behaved path: the consumer never authorizes delivery.")
    print("   No commerce.fulfillment event is emitted; the order stops here.")
    backed = audit_payment_before_fulfillment(led.events)
    print(f"  fulfillment audit: {'CLEAN' if not backed else str(len(backed)) + ' FINDING(S)'}"
          " — there is no fulfillment claim to be unbacked.")

    print("\n6. But ARC does not rely on good behavior. Suppose a misbehaving")
    print("   logistics agent attests delivery ANYWAY, with no confirmed payment:")
    say("logistics-agent", "attesting 'delivered' despite the failed payment")
    logistics.emit("ATTEST", "commerce.fulfillment", refs=(offer.id, approval.id),
                   payload={"status": "delivered", "context": CONTEXT})

    verify_log(led.events)
    state = project_transaction_state(led.events, txn)
    findings = audit_payment_before_fulfillment(led.events)
    print(f"\n  verify_log: PASS ({len(led.events)} signed events — the claim is byte-valid)")
    print(f"  structural state: {state}   "
          f"(the ladder reports the delivery CLAIM at face value)")
    print(f"  fulfillment audit: {'CLEAN' if not findings else str(len(findings)) + ' FINDING(S)'}")
    for fid, why in findings:
        print(f"      ! {fid}  {why}")
    print("  => the structural state reads 'fulfilled', but that is NOT a legitimate")
    print("     completion: the payment behind it was declined. The audit — a policy")
    print("     fold over the same facts — marks the fulfillment unbacked. As with")
    print("     the stale offer, the state is not consulted in isolation.")
    return led


# ===========================================================================
# Failure run 3 — colluding reputation farming.
#
# A few freshly-created rater agents each ATTEST a positive rep.outcome for one
# merchant. Every event is byte-valid and verify_log is clean — ARC preserves
# the signed facts. The distinct-rater count even clears a naive `>= 2` guard.
# But the reputation it builds is suspicious evidence, not trust: the raters are
# few and were created together. A policy fold, audit_reputation_rater_diversity,
# raises REVIEW-NEEDED signals over the same facts. It does NOT prove fraud, does
# NOT judge intent, and applies NO penalty — the pattern is equally consistent
# with a real local promotion, and only a human / governance review can tell.
# This slice is about the reputation PROJECTION, not commerce settlement, so it
# emits no offer / approval / payment / fulfillment — only KEY and rep.outcome.
# (Mirrors the question in artifacts/colluding-reputation-farming.json.)
# ===========================================================================

def run_colluding_reputation() -> Ledger:
    led = Ledger()
    merchant = Party(led, "merchant-agent-A", "k:merchant_a")
    buyers = [Party(led, f"buyer-agent-0{i}", f"k:buyer_0{i}") for i in (1, 2, 3)]

    print("\n1. Identity — merchant A, then three buyer agents created together")
    merchant.emit("KEY", "id.key_register", payload={"key": merchant.key})
    for b in buyers:
        b.emit("KEY", "id.key_register", payload={"key": b.key})

    print("\n2. Reputation — each buyer ATTESTs a positive rep.outcome for merchant A")
    say("note", "no offer / approval / payment here — this slice is the reputation fold")
    # Five positive outcomes from three distinct raters (buyers 01 and 02 rate twice).
    for b in (buyers[0], buyers[1], buyers[2], buyers[0], buyers[1]):
        b.emit("ATTEST", "rep.outcome",
               payload={"result": "positive", "merchant": merchant.key, "context": CONTEXT})

    verify_log(led.events)
    outcomes = [e for e in led.events
                if e.type == "ATTEST" and e.predicate == "rep.outcome"]
    distinct = len({e.signer for e in outcomes})
    positives = sum(1 for e in outcomes if e.payload.get("result") == "positive")

    print(f"\n  verify_log: PASS ({len(led.events)} signed events — every rep.outcome is byte-valid)")
    print(f"  naive surface: {positives} positive outcomes, distinct_raters = {distinct}")
    print(f"     a `distinct_raters >= 2` guard would PASS this ({distinct} >= 2);")
    print("     a naive score would make merchant A 'look trusted'")

    findings = audit_reputation_rater_diversity(led.events, merchant.key, CONTEXT)
    print(f"  reputation audit: {'CLEAN' if not findings else str(len(findings)) + ' FINDING(S)'}")
    for code, why in findings:
        print(f"      ! {code}  {why}")
    print("  => the rep.outcome events are byte-valid and verify cleanly, but the")
    print("     reputation they build is SUSPICIOUS EVIDENCE, not fraud: a thin,")
    print("     freshly-created rater base. ARC does not decide farming vs a real")
    print("     promotion, and raises no penalty on its own —")
    print("       confirmed_fraud           = false")
    print("       automatic_penalty_applied = false")
    print("       human_or_governance_review_required = true")
    return led


if __name__ == "__main__":
    print("=" * 78)
    print("ARC local-commerce reference episode")
    print("=" * 78)

    print("\n" + "-" * 78)
    print("[A] BASELINE — happy path (the offer is still fresh at approval)")
    print("-" * 78)
    led = run()
    fresh = audit_offer_freshness(led.events)
    print(f"\n  freshness audit: {'CLEAN' if not fresh else str(len(fresh)) + ' FINDING(S)'}"
          " — the approval referenced an offer inside its validity window.")
    backed = audit_payment_before_fulfillment(led.events)
    print(f"  fulfillment audit: {'CLEAN' if not backed else str(len(backed)) + ' FINDING(S)'}"
          " — the delivery claim is backed by a confirmed payment.")

    print("\n" + "-" * 78)
    print("[B] FAILURE RUN — stale-offer approval")
    print("-" * 78)
    run_stale_offer()

    print("\n" + "-" * 78)
    print("[C] FAILURE RUN — payment failure before fulfillment")
    print("-" * 78)
    run_payment_failure()

    print("\n" + "-" * 78)
    print("[D] FAILURE RUN — colluding reputation farming")
    print("-" * 78)
    run_colluding_reputation()

    print("\n" + "=" * 78)
    print("byte-valid approval != fresh approval; byte-valid fulfillment != backed")
    print("fulfillment; byte-valid rep.outcome != trustworthy reputation. ARC preserves")
    print("the signed facts; freshness, payment-backing, and rater diversity are")
    print("projections / policy decisions over them, not properties of the bytes —")
    print("and a diversity signal is a review trigger, never a fraud verdict.")
    print("=" * 78)

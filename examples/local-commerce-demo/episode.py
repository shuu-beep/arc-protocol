#!/usr/bin/env python3
"""
ARC local-commerce reference episode — the baseline happy path plus the failure
catalog, made runnable.

Purpose
-------
This directory's README long described a tiny local-commerce flow as prose plus
mock JSON artifacts. This file makes that flow executable: the baseline happy
path and every failure-run artifact in this directory ([A] through [H] below)
are generated as mock-signed event logs and folded back, with no separate
transaction-state object stored. The mock JSON artifacts remain as review objects; producing
the richer output artifacts the README sketches (§7) is still future work.

This fixture checks one implementation pattern:

    One local-commerce lifecycle is represented with canonical ARC events,
    without introducing a commerce-specific event type, and the "state" a
    marketplace would store — the order's status — is a PROJECTION recomputed
    from the log on demand, never a stored field. Commerce is one application
    of the authority / approval / audit protocol, not a schema of its own.

Fixture limits:
  * stdlib only, single process, single file, no network, no transport layer;
  * the Event / mock-signing / verify_log machinery is MIRRORED from
    `../end-to-end-demo/flow.py` so this example stays standalone (the repo's
    convention — each example runs on its own with no shared package);
  * signatures are MOCK (a hash, not Ed25519);
  * payment is MOCK — the fixture moves no money; a payment enters only as an ATTEST
    claim about an external transfer (event-registry.md §2.4);
  * delivery is MOCK — a logistics agent emits a delivery claim; the fixture does
    not establish that delivery occurred;
  * no new event TYPE — the five canonical types are reused as-is; richness rides
    new PREDICATES instead (e.g. `commerce.logistics_offer`, `commerce.disclosure`,
    `commerce.recommendation`), which is how ARC grows (event-registry.md §2.1:
    extend by predicate, not by type).

This is not an ARC implementation. It shows only that this authored lifecycle
uses the current Event types and derives its application-state label with a fold.

Eight runs:
  [A] baseline happy path — the order climbs pending_approval -> approved ->
      paid -> fulfilled as the log grows;
  [B] stale-offer failure run — the approval oracle approves an offer that has
      already expired. The fixture check passes, but a policy fold,
      audit_offer_freshness, flags the approval as stale: mock-signed approval
      is not the same as fresh approval. (Mirrors the question posed by
      artifacts/stale-offer-approval.json.)
  [C] payment-failure failure run — the approved payment is declined. The state
      fold must read the payment *result*, not just its presence, so the order
      reads payment_failed, never paid. And if a misbehaving agent attests
      delivery anyway, a policy fold, audit_payment_before_fulfillment, reports
      the mock-signed fulfillment claim as unbacked: a fulfillment claim
      that no confirmed payment stands behind. (Mirrors the question posed by
      artifacts/payment-failure.json.)
  [D] colluding-reputation-farming failure run — a few freshly-created rater
      agents each ATTEST a positive rep.outcome for one merchant. The fixture
      check passes, and the distinct-rater count clears a
      naive `>= 2` guard, yet a policy fold, audit_reputation_rater_diversity,
      raises REVIEW-NEEDED signals: the positive application signal rests on a
      thin, freshly-created rater base. This is not a fraud verdict; the fixture
      does not decide farming vs a local promotion or apply a penalty. (Mirrors
      the question posed by artifacts/colluding-reputation-farming.json.)
  [E] no-declared-anchor failure run — a newly-created merchant with no non-self
      `id.anchor` record and no history publishes a
      mock-signed (and unusually cheap) offer.
      Before the approval oracle emits AUTHORIZE, a policy fold,
      audit_merchant_identity_assurance,
      surfaces what the merchant's key does and does not carry:
      NO_DECLARED_EXTERNAL_ANCHOR and NO_TRACK_RECORD. An established merchant in
      the same run carries a non-self `id.anchor` record and a prior outcome
      claim. The script prints the warning before approval, but records no
      warning/disclosure Event and cannot establish an actual display or decision.
      This is not a fraud finding. (Mirrors the question posed by
      artifacts/fake-merchant.json.)
  [F] compromised-consumer-agent failure run — the consumer agent records a
      commerce.disclosure whose claimed `shown` set is empty, followed by a
      mock-signed AUTHORIZE from the approval oracle. The fixture check passes. An
      observer holding the
      same evidence set and declared Projection inputs can reproduce the warning
      codes the disclosure claim omitted (NO_DECLARED_EXTERNAL_ANCHOR,
      NO_TRACK_RECORD). audit_consent_disclosure marks the record CONTESTED — not
      automatically invalid — but cannot establish the actual displayed view.
      This is the commerce counterpart to the view/bytes mismatch probe, not a
      new finding. (Mirrors the question posed by
      artifacts/compromised-consumer-agent.json.)
  [G] discovery-bias failure run — a discovery backend ranks two offers and
      records the recommendation as a mock-signed event, ranking the sponsored
      merchant first. The fixture replay check passes. A ranking is a PROJECTION over the
      offers, not a fact, so an auditor applies the fixture's named price-then-ETA
      policy: the other merchant ranks first (cheaper, faster),
      and the sponsored weight that displaced it was on the record but omitted
      from its claimed disclosed-input subset. audit_ranking_disclosure raises
      NAMED-POLICY-MISMATCH and RANKING-INFLUENCE-UNDISCLOSED. This is a new fold
      target — the ranking layer — under the same disclosure comparison as [F] /
      the view-fidelity probe; it is not a finding that sponsorship is improper,
      only that hidden influence which flips the named policy's order is
      reviewable. (Mirrors the
      question posed by artifacts/discovery-bias.json.)
  [H] approval-fatigue failure run — under one intent the merchant revises its
      offer four times in a few minutes, each changing a material term, and the
      approval oracle re-approves each in quick succession. The fixture check
      passes. A policy fold, audit_approval_cadence, reads the
      recorded SEQUENCE of approvals — a new fold target — and flags a
      structural consent-quality risk: many approvals in a short window
      (REPEATED_APPROVAL_CHURN) re-approving moving terms
      (MATERIAL_CHANGE_UNCONSOLIDATED). The configured response is to pause
      payment for a consolidated re-review. This is not a claim that the fixture
      can measure attention or prove fatigue; it is the same
      disclosure-vs-cognition boundary as [E] and [F], on the temporal/sequence
      axis: the short cadence triggers review without determining attention or
      what review occurred off-log. (Mirrors the question
      posed by artifacts/approval-fatigue.json.)

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
    """Fixture replay check: validate the deterministic mock signature and require
    a prior KEY registration. This is not a complete conformance verifier."""
    registered: set[str] = set()
    for ev in events:
        if ev.signature != stub_sign(ev.signer, ev.signing_bytes()):
            raise ValueError(f"bad mock signature on {ev.id}")
        is_root = ev.type == "KEY" and ev.predicate == "id.key_register"
        if not is_root and ev.signer not in registered:
            raise ValueError(f"signer {ev.signer} not anchored by a KEY register ({ev.id})")
        if is_root:
            registered.add(ev.payload["key"])


class Party:
    def __init__(self, ledger: "Ledger", name: str, key: str):
        self.ledger, self.name, self.key = ledger, name, key

    def emit(self, type_: str, predicate: str, ts: str | None = None, **kw) -> Event:
        # ts defaults to the ledger's auto-advancing clock (every existing run);
        # a run may pass an explicit timestamp where the cadence itself matters.
        ev = make(type_, self.key, predicate, ts or self.ledger.now(), **kw)
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

    The transaction is not a stored object. There is no order record, no cart,
    no row in a table — only mock-signed fixture Events connected by references.
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
    # structurally (an event asserts delivery); whether this fixture policy treats
    # it as backed
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
    timestamp. The mock-signed claims — the offer with its `expires`, the approval
    with its `timestamp` — remain in the fixture log; whether the
    approval is fresh is a *projection* over those claims, a policy decision ARC
    does not bake into the bytes. A stale approval passes the fixture check but is not
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
    claim and the fulfillment claim reference the same `consent.approval`; a
    confirmed payment and a fulfillment that share an approval are paired.

    A fulfillment claim is a mock-signed Event that passes this fixture's check.
    Whether it is backed is a separate application-policy reading:
    if the payment behind it was declined (or never confirmed), the delivery
    claim is *unbacked*, and a commerce fold must say so rather than let the
    structural ladder's `fulfilled` label is only a claim-state label.
    This is the freshness fold's sibling on the payment axis: the protocol holds
    the claims; whether fulfillment is backed is a projection over them."""
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


# Reputation-review thresholds. These are coarse application-policy triggers,
# not fraud detection or automatic punishment. The numbers are fixture inputs.
POSITIVE_REVIEW_BAR = 3        # positive count at which this review check starts
REVIEW_DIVERSITY_FLOOR = 3     # distinct raters at/below which that count is thin
RATER_CLUSTER_WINDOW = timedelta(minutes=10)  # rater key-registrations this close = a cluster


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def audit_reputation_rater_diversity(
        events: list[Event], merchant: str, context: str) -> list[tuple[str, str]]:
    """Policy fold: surface REVIEW-NEEDED signals when a merchant's positive
    reputation may be inflated by a small or freshly-created set of raters.

    This is not a fraud detector or a verdict. Every `rep.outcome` here is a
    mock-signed ATTEST that passes this fixture's check. Whether this policy assigns
    a review signal is a projection over those claims, and
    a thin or freshly-clustered rater base triggers review under this policy,
    never proof of collusion. The same pattern is also consistent with a local
    launch promotion; the fixture decides neither and applies no penalty.

    Two signals, both computed only from KEY id.key_register and ATTEST
    rep.outcome events:

      LOW_RATER_DIVERSITY — a high positive count rests on a small
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

    if len(positives) >= POSITIVE_REVIEW_BAR and len(raters) <= REVIEW_DIVERSITY_FLOOR:
        findings.append(("LOW_RATER_DIVERSITY",
            f"{len(positives)} positive outcomes for {merchant} rest on only "
            f"{len(raters)} distinct rater(s) — a thin base for this positive-count "
            f"signal (clears a `>= 2` guard, still review-worthy)"))

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


def audit_merchant_identity_assurance(
        events: list[Event], merchant: str, context: str) -> list[tuple[str, str]]:
    """Policy fold: before an approval, surface what
    identity evidence the merchant's key does and does not carry. Computed only
    from KEY id.key_register, non-self ATTEST id.anchor records,
    and ATTEST rep.outcome events.

    This is not a fraud test or a verdict. A mock-signed offer passing this fixture
    shows only that the deterministic record check succeeded; it says nothing
    about what an `id.anchor` issuer checked or whether the key has any track
    record. Absence of a non-self anchor record is not proof of dishonesty: a no-
    history merchant may simply be a newcomer. These are fixture warning labels;
    this policy applies no penalty.
    An anchor record remains an issuer's claim, not a guarantee of fulfillment.

    Two signals:
      NO_DECLARED_EXTERNAL_ANCHOR — no non-self id.anchor record names this
        merchant's key under this fixture policy.
      NO_TRACK_RECORD — no prior rep.outcome for this merchant in this context.
    """
    anchored = any(
        e.type == "ATTEST" and e.predicate == "id.anchor"
        and e.payload.get("subject") == merchant
        and e.signer != merchant            # self-anchoring does not count
        for e in events
    )
    has_history = any(
        e.type == "ATTEST" and e.predicate == "rep.outcome"
        and e.payload.get("merchant") == merchant
        and e.payload.get("context") == context
        for e in events
    )

    findings: list[tuple[str, str]] = []
    if not anchored:
        findings.append(("NO_DECLARED_EXTERNAL_ANCHOR",
            f"{merchant} has no non-self id.anchor record in this fixture — "
            f"its key is self-registered only"))
    if not has_history:
        findings.append(("NO_TRACK_RECORD",
            f"{merchant} has no prior rep.outcome in context '{context}' — "
            f"no completed-order history to weigh"))
    return findings


def audit_consent_disclosure(
        events: list[Event], approval: Event, context: str) -> list[tuple[str, str]]:
    """Policy fold: compare computed warning codes with a disclosure claim.
    Recompute, from the same evidence set and this declared policy, the warning
    codes for the approved offer's merchant, then compare them with what the
    consumer agent's `commerce.disclosure` claims it showed before approval.

    This applies the view-fidelity probe's record/view comparison
    (../view-fidelity-demo). It is not a new finding or a fraud test. The actual
    displayed view and human comprehension remain unknown. An observer holding
    the same evidence set, ordering, policy,
    and Projection version can reproduce these warning codes and observe that the
    recorded disclosure omits them. The verdict is CONTESTED, never automatically
    invalid; a human or application adjudicator decides what the record is worth.
    """
    offers = {
        e.id: e for e in events
        if e.type == "ATTEST" and e.predicate == "commerce.offer"
    }
    approved_offers = [offers[r] for r in approval.refs if r in offers]

    # Recompute codes under this fixture's evidence set and declared policy.
    applicable: dict[str, str] = {}
    for off in approved_offers:
        merchant = off.signer            # the offer's signer is the merchant
        for code, why in audit_merchant_identity_assurance(events, merchant, context):
            applicable[code] = why

    # What did the consumer agent claim it disclosed? A commerce.disclosure that
    # references this approval (or its offer), listing the warning codes shown.
    disclosed: set[str] = set()
    disclosure_seen = False
    refset = {approval.id} | set(approval.refs)
    for e in events:
        if (e.type == "ATTEST" and e.predicate == "commerce.disclosure"
                and refset & set(e.refs)):
            disclosure_seen = True
            disclosed |= set(e.payload.get("shown", []))

    findings: list[tuple[str, str]] = []
    for code, why in applicable.items():
        if code not in disclosed:
            note = "no disclosure was recorded" if not disclosure_seen \
                   else "the agent's disclosure did not list it"
            findings.append(("OMITTED-DISCLOSURE",
                f"approval {approval.id} has no recorded disclosure of {code} "
                f"({note}); recomputed from the fixture Event set: {why}"))
    return findings


def audit_ranking_disclosure(
        events: list[Event], recommendation: Event, context: str) -> list[tuple[str, str]]:
    """Policy fold: a recommendation's asserted ranking is a CLAIM over the
    mock-signed offers. Recompute this fixture's named price-then-ETA ordering of
    the candidate offers from the same log, compare it to the order the
    recommendation asserts, and check whether an influence that changed first place
    appears in the recommendation's claimed disclosed-input subset.

    A `commerce.recommendation` is a mock-signed ATTEST that passes this fixture's
    check. A ranking is not a fact about the world; it is a PROJECTION
    over the offers, the same way the transaction state is. The backend's asserted
    order is one such projection; the named ordering recomputed from the offers'
    own terms is another. When the two disagree and the factor that explains the
    disagreement was recorded on the mock-signed recommendation but omitted from
    its claimed disclosed-input subset, the application flags the record for
    review. It cannot establish what the backend did or what appeared on screen.

    This applies the disclosure comparison from audit_consent_disclosure / the
    view-fidelity probe (../view-fidelity-demo) — the influence sits on the
    mock-signed record but is absent from the disclosed subset — to another fold
    target: the ranking itself, recomputable as a projection over the offers. It
    is not a verdict that sponsorship is improper: it only compares the declared
    record with one named ordering and disclosure policy.

    Two signals:
      NAMED-POLICY-MISMATCH — the offer ranked first is not the offer this fixture's
        price-then-ETA ordering would put first. This covers only the listed fields.
      RANKING-INFLUENCE-UNDISCLOSED — a ranking factor recorded on the mock-signed
        recommendation favored the displacing offer over the named-policy result,
        but was absent from the record's claimed disclosed-input subset.
    """
    ranked = recommendation.payload.get("ranked", [])              # asserted order
    factors = recommendation.payload.get("ranking_factors", {})    # declared inputs, mock-signed
    disclosed = set(recommendation.payload.get("inputs_disclosed_to_human", []))

    offers = {
        e.id: e for e in events
        if e.type == "ATTEST" and e.predicate == "commerce.offer"
        and e.id in set(ranked)
    }

    findings: list[tuple[str, str]] = []
    if not ranked or any(oid not in offers for oid in ranked):
        return findings

    # Named fixture ordering: cheapest first, then fastest. Partial by design.
    def named_policy_key(oid: str) -> tuple[int, int]:
        p = offers[oid].payload
        return (p.get("price_krw", 0), p.get("eta_min", 0))

    asserted_first = ranked[0]
    named_policy_first = sorted(ranked, key=named_policy_key)[0]

    if asserted_first != named_policy_first:
        findings.append(("NAMED-POLICY-MISMATCH",
            f"recommendation ranks {offers[asserted_first].signer} first, but an "
            f"application ordering (lower price, then faster delivery) puts "
            f"{offers[named_policy_first].signer} first"))

        # Was an influence that displaced the named-policy result recorded but not
        # listed in the disclosure claim?
        # `ranking_factors` maps a factor name -> {offer_id: weight}. A factor on
        # the mock-signed record, absent from the disclosed subset, that scores the
        # asserted-first offer ABOVE the named-policy result is undisclosed influence.
        for factor, weights in factors.items():
            if factor in disclosed or not isinstance(weights, dict):
                continue
            if weights.get(asserted_first, 0) > weights.get(named_policy_first, 0):
                findings.append(("RANKING-INFLUENCE-UNDISCLOSED",
                    f"factor '{factor}' on the mock-signed recommendation scored "
                    f"{offers[asserted_first].signer} ({weights.get(asserted_first)}) "
                    f"above {offers[named_policy_first].signer} "
                    f"({weights.get(named_policy_first)}), but was not in the record's "
                    f"claimed disclosed-input subset {sorted(disclosed)}"))
    return findings


# Approval-cadence review thresholds. Coarse, admittedly arbitrary review triggers
# (like the reputation thresholds), not a measure of attention. They flag many
# approvals with changing terms in a short window for application review.
APPROVAL_CHURN_BAR = 3                            # approvals in the window that start to look like churn
APPROVAL_CADENCE_WINDOW = timedelta(minutes=3)   # approvals this close together = a cluster
MATERIAL_TERMS = ("price_krw", "eta_min", "free_cancellation")


def audit_approval_cadence(events: list[Event], context: str) -> list[tuple[str, str]]:
    """Policy fold: surface a consent-QUALITY risk when a human-labeled signer
    emits a rapid sequence of approvals for offers whose material terms keep
    changing inside a short window.

    This is not a measure of human attention or a verdict. Every approval here is
    a mock-signed AUTHORIZE that passes the fixture replay check. The fold sees how many
    approvals landed within a short window, and whether the offers they approved
    changed material terms across that window. Fast repeated approvals are equally
    consistent with an informed, decisive user — so this records a review trigger,
    never a finding that consent was uninformed. It is the same disclosure-vs-
    cognition boundary as the no-declared-anchor and compromised-agent runs, on a
    new fold target: the recorded sequence of approvals over time. The short
    cadence is a review trigger; it does not establish attention or off-log review.

    Two signals, computed only from AUTHORIZE consent.approval events and the
    commerce.offer events they reference:

      REPEATED_APPROVAL_CHURN — at least APPROVAL_CHURN_BAR approvals fall within
        APPROVAL_CADENCE_WINDOW of the EARLIEST approval (the fold anchors one
        window at the first approval; a later, separate cluster is outside this
        fold's reach by design — one window, one trigger).
      MATERIAL_CHANGE_UNCONSOLIDATED — this policy label is added when successive
        approved offers changed material terms. The Event set does not establish
        whether a consolidated side-by-side review occurred.
    """
    offers = {
        e.id: e for e in events
        if e.type == "ATTEST" and e.predicate == "commerce.offer"
    }
    approvals = [
        e for e in events
        if e.type == "AUTHORIZE" and e.predicate == "consent.approval"
        and e.scope and e.scope.get("context") == context
    ]
    approvals.sort(key=lambda e: e.timestamp)
    if len(approvals) < APPROVAL_CHURN_BAR:
        return []

    # The cluster of approvals within one window of the earliest.
    first = _parse_ts(approvals[0].timestamp)
    cluster = [a for a in approvals
               if _parse_ts(a.timestamp) - first <= APPROVAL_CADENCE_WINDOW]

    findings: list[tuple[str, str]] = []
    if len(cluster) < APPROVAL_CHURN_BAR:
        return findings

    span = _parse_ts(cluster[-1].timestamp) - first
    findings.append(("REPEATED_APPROVAL_CHURN",
        f"{len(cluster)} approvals within {span} (<= {APPROVAL_CADENCE_WINDOW}) — "
        f"repeated approval prompts in a short window"))

    # Did the approved offers' material terms change across the cluster?
    def terms_of(appr: Event) -> dict[str, Any]:
        for r in appr.refs:
            off = offers.get(r)
            if off is not None:
                return {k: off.payload.get(k) for k in MATERIAL_TERMS}
        return {}

    changes = 0
    changed_terms: list[str] = []
    prev = terms_of(cluster[0])
    for a in cluster[1:]:
        cur = terms_of(a)
        diff = [k for k in MATERIAL_TERMS if cur.get(k) != prev.get(k)]
        if diff:
            changes += 1
            changed_terms.extend(diff)
        prev = cur
    if changes:
        findings.append(("MATERIAL_CHANGE_UNCONSOLIDATED",
            f"{changes} of the clustered approvals re-approved changed material "
            f"terms ({', '.join(sorted(set(changed_terms)))}) — this policy requests "
            f"a consolidated re-review; prior off-log review is not established"))
    return findings


# ===========================================================================
# The baseline happy-path episode — emitted by an authored script.
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

    print("\n2. Intent — the script supplies a request to the consumer agent")
    say("human-labeled participant", "lunch: a gimbap set under 9000 KRW, delivered")
    say("consumer-agent", "recording the intent so a fold can later check it was honored")
    intent = consumer.emit("ATTEST", "intent.canonical",
                           payload={"item": "gimbap_set", "max_total_krw": 9000,
                                    "delivery": True, "context": CONTEXT})

    print("\n3. Merchant offer — the merchant agent publishes mock-signed terms")
    say("merchant-agent", "gimbap set, 7000 KRW, valid 30 min")
    offer = merchant.emit("ATTEST", "commerce.offer", refs=(intent.id,),
                          payload={"item": "gimbap_set", "price_krw": 7000,
                                   "context": CONTEXT, "expires": "2026-06-08T12:40:00Z"})
    txn = offer.id  # the offer opens the transaction; the fold roots here

    print("\n4. Logistics offer — a delivery quote (new PREDICATE, not a new type)")
    say("logistics-agent", "delivery in 12 min, 1500 KRW")
    logi = logistics.emit("ATTEST", "commerce.logistics_offer", refs=(offer.id,),
                          payload={"fee_krw": 1500, "eta_min": 12, "context": CONTEXT})

    snapshot(led, txn, "after offers")  # pending_approval — no approval record yet

    print("\n5. Approval — the script routes through the human-labeled participant")
    say("consumer-agent", "gimbap 7000 + delivery 1500 = 8500, under budget; presenting it")
    say("human-labeled participant", "fixture emits the approval record")
    # refs point only at mock-signed Events (the offer and the logistics quote);
    # the payee is carried in scope, not as a key-id ref.
    approval = human.emit("AUTHORIZE", "consent.approval",
                          refs=(offer.id, logi.id),
                          scope={"max_total_krw": 8500, "payee": "k:merchant",
                                 "context": CONTEXT})

    snapshot(led, txn, "after authored approval")  # approved

    print("\n6. Payment — recorded as a CLAIM about an external transfer (mock)")
    say("consumer-agent", "paid via an external provider; attesting the result")
    consumer.emit("ATTEST", "commerce.payment_result",
                  refs=(approval.id,),  # the approval it pays against (a mock-signed Event)
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

    print(f"\nGenerated log: {len(led.events)} hand-authored mock-signed fixture records.")
    print("The deterministic replay check passed at every recompute; the transaction state was never")
    print("stored — it was folded from the log each time it was printed.")
    return led


# ===========================================================================
# Failure run 1 — stale-offer approval.
#
# The merchant's offer carries a short validity window. The approval oracle emits
# AUTHORIZE AFTER it has expired. The fixture check passes and preserves the mock-signed
# claims, while audit_offer_freshness labels the approval stale under this
# application policy.
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

    print("\n3. ...the validity window closes before the approval record...")

    print("\n4. Approval — the oracle approves the now-EXPIRED offer")
    say("consumer-agent", "presenting the offer for approval")
    say("approval-oracle", "emits approval after the offer's validity window closed")
    human.emit("AUTHORIZE", "consent.approval", refs=(offer.id,),  # the offer, a mock-signed Event
               scope={"max_total_krw": 7000, "payee": "k:merchant", "context": CONTEXT})

    # The fixture preserves the claims and its mock-signature check passes.
    verify_log(led.events)
    state = project_transaction_state(led.events, txn)
    findings = audit_offer_freshness(led.events)

    print(f"\n  fixture replay check: PASS ({len(led.events)} mock-signed records)")
    print(f"  structural state: {state}   "
          f"(the event ladder alone — only 'an approval exists')")
    print(f"  freshness audit: {'CLEAN' if not findings else str(len(findings)) + ' FINDING(S)'}")
    for aid, why in findings:
        print(f"      ! {aid}  {why}")
    print("  => the structural state reads 'approved', while this application policy")
    print("     does not treat it as fresh authority; a fold over the same claims")
    print("     marks the approval stale. The state is not consulted in isolation.")
    return led


# ===========================================================================
# Failure run 2 — payment failure before fulfillment.
#
# The approval oracle approves a current offer; the consumer agent requests payment; the
# mock provider DECLINES it. Two things must hold:
#   (1) the order state must read the payment RESULT, not its mere presence —
#       a declined payment leaves the order at 'payment_failed', never 'paid';
#   (2) this application policy reports a fulfillment claim as UNBACKED when no
#       confirmed payment claim precedes it. The configured path emits no
#       fulfillment after a decline; an alternate authored path emits one so the
#       policy result is visible even though the fixture check passes.
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

    print("\n3. Approval — the oracle approves the current offer")
    say("approval-oracle", "emits approval before any payment is requested")
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
    print(f"\n  fixture replay check: PASS ({len(led.events)} mock-signed records)")
    print(f"  STATE: {state}   "
          f"(the fold read the payment RESULT, not just its presence —")
    print("         a declined payment is 'payment_failed', never 'paid')")

    print("\n5. Configured path: the consumer emits no delivery authorization.")
    print("   No commerce.fulfillment event is emitted; the order stops here.")
    backed = audit_payment_before_fulfillment(led.events)
    print(f"  fulfillment audit: {'CLEAN' if not backed else str(len(backed)) + ' FINDING(S)'}"
          " — there is no fulfillment claim to be unbacked.")

    print("\n6. Alternate fixture path: a logistics agent attests delivery")
    print("   despite the absence of a confirmed payment claim:")
    say("logistics-agent", "attesting 'delivered' despite the failed payment")
    logistics.emit("ATTEST", "commerce.fulfillment", refs=(offer.id, approval.id),
                   payload={"status": "delivered", "context": CONTEXT})

    verify_log(led.events)
    state = project_transaction_state(led.events, txn)
    findings = audit_payment_before_fulfillment(led.events)
    print(f"\n  fixture replay check: PASS ({len(led.events)} mock-signed records)")
    print(f"  structural state: {state}   "
          f"(the ladder reports the delivery CLAIM at face value)")
    print(f"  fulfillment audit: {'CLEAN' if not findings else str(len(findings)) + ' FINDING(S)'}")
    for fid, why in findings:
        print(f"      ! {fid}  {why}")
    print("  => the structural state reads 'fulfilled', while this application policy")
    print("     labels the claim unbacked. The audit — a fold over the same claims —")
    print("     applies that reading. As with")
    print("     the stale offer, the state is not consulted in isolation.")
    return led


# ===========================================================================
# Failure run 3 — colluding reputation farming.
#
# A few freshly-created rater agents each ATTEST a positive rep.outcome for one
# merchant. The fixture check passes and preserves the mock-signed claims. The
# distinct-rater count even clears a naive `>= 2` guard.
# The resulting positive-count signal rests on few raters created together. A
# policy fold, audit_reputation_rater_diversity, raises REVIEW-NEEDED signals over
# those facts. It does not prove fraud, infer intent, or apply a penalty; the same
# pattern is also consistent with a local promotion.
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

    print(f"\n  fixture replay check: PASS ({len(led.events)} mock-signed records)")
    print(f"  naive surface: {positives} positive outcomes, distinct_raters = {distinct}")
    print(f"     a `distinct_raters >= 2` guard would PASS this ({distinct} >= 2);")
    print("     a naive score would rank merchant A highly")

    findings = audit_reputation_rater_diversity(led.events, merchant.key, CONTEXT)
    print(f"  reputation audit: {'CLEAN' if not findings else str(len(findings)) + ' FINDING(S)'}")
    for code, why in findings:
        print(f"      ! {code}  {why}")
    print("  => the rep.outcome records pass the fixture checks, but the")
    print("     positive-count signal rests on a thin, freshly-created rater base.")
    print("     This fixture does not determine farming vs a promotion or apply a penalty —")
    print("       confirmed_fraud           = false")
    print("       automatic_penalty_applied = false")
    print("       fixture_review_requested = true")
    return led


# ===========================================================================
# Failure run 4 — merchant without a declared external anchor.
#
# A newly-created merchant A — self-registered key, no non-self id.anchor record,
# no history — publishes a mock-signed, unusually cheap offer. Merchant B in the
# same run has a community-authored mock-signed id.anchor record and a prior
# outcome. Before the fixture emits approval for A's offer, a policy fold,
# audit_merchant_identity_assurance, surfaces A's missing assurance
# (NO_DECLARED_EXTERNAL_ANCHOR, NO_TRACK_RECORD) while B audits CLEAN under this
# fixture policy — the signal
# distinguishes these two authored records. The script prints the warnings before
# AUTHORIZE but records no warning/disclosure Event and cannot establish what a
# person saw or weighed. No fraud is proven.
# This slice is about pre-approval identity legibility, so it stops at the
# approval — the non-fulfillment / dispute / governance tail of the artifact
# belongs to the execution-fidelity and payment-failure axes, not here.
# (Mirrors the question in artifacts/fake-merchant.json.)
# ===========================================================================

def run_fake_merchant() -> Ledger:
    led = Ledger()
    community = Party(led, "community", "k:community")
    human = Party(led, "human", "k:human")
    consumer = Party(led, "consumer-agent", "k:consumer_agent")
    merchant_b = Party(led, "merchant-B (established)", "k:merchant_b")
    merchant_a = Party(led, "merchant-A (new)", "k:merchant_a")

    print("\n1. Identity — every party anchors a key")
    regs = {p.key: p.emit("KEY", "id.key_register", payload={"key": p.key})
            for p in (community, human, consumer, merchant_b, merchant_a)}

    print("\n2. Merchant B has a non-self id.anchor record + a prior outcome")
    say("community", "B passed an external cost gate (business registration); attesting the anchor")
    community.emit("ATTEST", "id.anchor", refs=(regs[merchant_b.key].id,),
                   payload={"subject": merchant_b.key, "basis": "business_registration_mock"})
    say("consumer-agent", "B also has a completed earlier order; logging its positive outcome")
    consumer.emit("ATTEST", "rep.outcome",
                  payload={"result": "positive", "merchant": merchant_b.key, "context": CONTEXT})

    print("\n3. Merchant A is new — self-registered only, and offers an unusually cheap deal")
    say("merchant-A", "bibimbap 4900 KRW, delivery free — much cheaper than B")
    offer_a = merchant_a.emit("ATTEST", "commerce.offer",
                              payload={"item": "bibimbap", "price_krw": 4900,
                                       "context": CONTEXT, "expires": "2026-12-31T00:00:00Z"})

    print("\n4. Before approval — the consumer surfaces each merchant's identity assurance")
    verify_log(led.events)
    for label, mkey in [("A  (the cheap offer up for approval)", merchant_a.key),
                        ("B  (the established alternative)", merchant_b.key)]:
        findings = audit_merchant_identity_assurance(led.events, mkey, CONTEXT)
        verdict = "CLEAN" if not findings else f"{len(findings)} WARNING(S)"
        print(f"\n  merchant {label}")
        print(f"    assurance audit: {verdict}")
        for code, why in findings:
            print(f"      ! {code}  {why}")

    print("\n5. The script prints A's warnings, then the approval oracle approves")
    say("approval-oracle", "fixture proceeds with the cheap offer")
    human.emit("AUTHORIZE", "consent.approval", refs=(offer_a.id,),
               scope={"max_total_krw": 4900, "payee": merchant_a.key, "context": CONTEXT})

    verify_log(led.events)
    print(f"\n  fixture replay check: PASS ({len(led.events)} mock-signed events)")
    print("  => A's offer passes this record check; that does not vet the merchant.")
    print("     The script printed warnings before AUTHORIZE, but recorded no warning")
    print("     or disclosure Event and cannot establish what a human saw or weighed.")
    print("     Absence of a non-self id.anchor record is not dishonesty. The policy")
    print("     reports the record gap; the approval oracle then emits AUTHORIZE —")
    print("       confirmed_fraud      = false")
    print("       warnings_printed_by_script = true")
    print("       human_decision_established = false")
    return led


# ===========================================================================
# Failure run 5 — compromised consumer agent (disclosure-claim mismatch).
#
# The consumer agent records the fixture's disclosure claim. Here the claim lists
# no warnings, followed by a mock-signed AUTHORIZE for a new merchant's offer. The fixture check
# passes. An observer holding the same evidence set and declared Projection inputs
# can reproduce NO_DECLARED_EXTERNAL_ANCHOR and NO_TRACK_RECORD and observe that
# the disclosure claim omitted them.
#
# This is the commerce counterpart to the view/bytes mismatch probe, not a new
# finding. The check compares a disclosure claim with computed codes; the actual
# displayed view and human comprehension remain unknown.
# (Mirrors the question in artifacts/compromised-consumer-agent.json.)
# ===========================================================================

def run_compromised_agent() -> Ledger:
    led = Ledger()
    human = Party(led, "human", "k:human")
    consumer = Party(led, "consumer-agent (compromised)", "k:consumer_agent")
    merchant_a = Party(led, "merchant-A (new)", "k:merchant_a")

    print("\n1. Identity — the parties anchor keys (merchant A is self-registered only)")
    for p in (human, consumer, merchant_a):
        p.emit("KEY", "id.key_register", payload={"key": p.key})

    print("\n2. Merchant A — new, unanchored, no history; makes a current fixture offer")
    say("merchant-A", "bibimbap 4900 KRW; offer is current (far-future expiry)")
    offer = merchant_a.emit("ATTEST", "commerce.offer",
                            payload={"item": "bibimbap", "price_krw": 4900,
                                     "context": CONTEXT, "expires": "2026-12-31T00:00:00Z"})

    print("\n3. The consumer agent records a disclosure claim whose `shown` set is empty.")
    say("consumer-agent", "recording an empty claimed disclosure set")
    consumer.emit("ATTEST", "commerce.disclosure", refs=(offer.id,),
                  payload={"shown": [], "context": CONTEXT})

    print("\n4. The approval oracle emits AUTHORIZE after that disclosure claim")
    say("approval-oracle", "fixture proceeds with the cheap offer")
    approval = human.emit("AUTHORIZE", "consent.approval", refs=(offer.id,),
                          scope={"max_total_krw": 4900, "payee": merchant_a.key,
                                 "context": CONTEXT})

    verify_log(led.events)
    print(f"\n  fixture replay check: PASS ({len(led.events)} mock-signed records,")
    print("     including the offer, disclosure claim, and approval record)")

    print("\n5. An auditor re-folds the same Event set to recover what was applicable:")
    findings = audit_consent_disclosure(led.events, approval, CONTEXT)
    verdict = f"CONTESTED ({len(findings)} FINDING(S))" if findings else "CLEAN"
    print(f"  consent disclosure audit: {verdict}")
    for code, why in findings:
        print(f"      ! {code}  {why}")
    print("  => the AUTHORIZE passes the fixture checks and is not voided by this policy.")
    print("     The recorded disclosure omits warning codes produced by the named policy,")
    print("     so the fixture reports CONTESTED. The actual displayed view remains unknown.")
    print("     A view hash could bind approval to a claimed renderer output, but it")
    print("     would not establish actual display or comprehension. No fraud is judged —")
    print("       confirmed_fraud                     = false")
    print("       consent                             = CONTESTED")
    print("       fixture_review_requested             = true")
    return led


# ===========================================================================
# Failure run 6 — discovery bias (ranking disclosure-claim mismatch).
#
# A discovery backend ranks two offers for the same request and records the
# recommendation as a mock-signed event. It ranks merchant A first — a sponsored
# weight on the mock-signed record put it there — but the payload's claimed
# disclosed subset lists only neutral factors. The fixture check passes. Yet a ranking
# is not a fact; it is a PROJECTION over the offers, so the asserted order can be
# compared under the fixture's price-then-ETA policy: B ranks first, and the sponsored
# weight that displaced it was on the record but omitted from that claimed subset;
# actual display is unknown.
# audit_ranking_disclosure raises NAMED-POLICY-MISMATCH and
# RANKING-INFLUENCE-UNDISCLOSED. The configured response is to PAUSE approval.
#
# This uses the ranking layer as another fold target and applies the same disclosure
# comparison as [F] / the view-fidelity probe (the influence is on the mock-signed
# record but absent from the disclosed subset). It is not a finding that
# sponsorship is improper: the fixture compares one declared ranking record with
# one named policy and disclosure claim. It does not suppress the ranking or
# determine manipulation; downstream response is application policy.
# (Mirrors the question in artifacts/discovery-bias.json.)
# ===========================================================================

def run_discovery_bias() -> Ledger:
    led = Ledger()
    human = Party(led, "human", "k:human")
    consumer = Party(led, "consumer-agent", "k:consumer_agent")
    backend = Party(led, "discovery-backend", "k:discovery")
    merchant_a = Party(led, "merchant-A (sponsored)", "k:merchant_a")
    merchant_b = Party(led, "merchant-B (better fit)", "k:merchant_b")

    print("\n1. Identity — the parties anchor keys")
    for p in (human, consumer, backend, merchant_a, merchant_b):
        p.emit("KEY", "id.key_register", payload={"key": p.key})

    print("\n2. Two offers for the same request (bibimbap, delivered)")
    say("merchant-A", "bibimbap 13800 KRW total, ETA 32 min")
    offer_a = merchant_a.emit("ATTEST", "commerce.offer",
                              payload={"item": "bibimbap", "price_krw": 13800,
                                       "eta_min": 32, "context": CONTEXT,
                                       "expires": "2026-12-31T00:00:00Z"})
    say("merchant-B", "bibimbap 12400 KRW total, ETA 24 min — cheaper and faster")
    offer_b = merchant_b.emit("ATTEST", "commerce.offer",
                              payload={"item": "bibimbap", "price_krw": 12400,
                                       "eta_min": 24, "context": CONTEXT,
                                       "expires": "2026-12-31T00:00:00Z"})

    print("\n3. The discovery backend ranks the offers and records the recommendation.")
    print("   A is ranked first — a sponsored weight on the mock-signed record put it there —")
    print("   but the record's claimed disclosed subset lists only neutral factors.")
    say("discovery-backend", "ranking A first; recording factors and a claimed disclosed subset")
    rec = backend.emit("ATTEST", "commerce.recommendation",
                       refs=(offer_a.id, offer_b.id),
                       payload={
                           "ranked": [offer_a.id, offer_b.id],   # asserted order
                           "ranking_factors": {                  # declared inputs, mock-signed
                               "item_match":       {offer_a.id: 1.0, offer_b.id: 1.0},
                               "price_fit":        {offer_a.id: 0.6, offer_b.id: 0.8},
                               "delivery_fit":     {offer_a.id: 0.6, offer_b.id: 0.8},
                               "sponsored_weight": {offer_a.id: 0.2, offer_b.id: 0.0},
                           },
                           # fields the record claims were disclosed; actual display is unknown
                           "inputs_disclosed_to_human": ["item_match", "price_fit",
                                                         "delivery_fit"],
                           "context": CONTEXT})

    verify_log(led.events)
    print(f"\n  fixture replay check: PASS ({len(led.events)} mock-signed records,")
    print("     including the recommendation and its declared factors)")

    print("\n4. An auditor applies the fixture's named price-then-ETA ordering:")
    findings = audit_ranking_disclosure(led.events, rec, CONTEXT)
    verdict = f"{len(findings)} FINDING(S)" if findings else "CLEAN"
    print(f"  ranking disclosure audit: {verdict}")
    for code, why in findings:
        print(f"      ! {code}  {why}")

    print("\n5. Configured fixture response: PAUSE; no AUTHORIZE is emitted for")
    print("   the sponsored-first result.")
    state = project_transaction_state(led.events, offer_a.id)
    print(f"  structural state (offer A's txn): {state}   (no approval — still pending)")
    print("  => the recommendation passes the fixture checks and this policy does not suppress it. A")
    print("     ranking is a PROJECTION over the offers, so the asserted order can be")
    print("     compared: B ranks first under price-then-ETA, and the sponsored")
    print("     weight that displaced it appears in the record but is omitted from")
    print("     inputs_disclosed_to_human; the fixture cannot establish actual display.")
    print("     Under this fixture policy, the review condition is that sponsored_weight")
    print("     is omitted from the record's claimed disclosed subset and changes the named order.")
    print("     The application decides; here the configured response is to pause —")
    print("       confirmed_manipulation              = false")
    print("       named_policy_mismatch               = true")
    print("       ranking_influence_undisclosed       = true")
    print("       approval_completed                  = false")
    print("       fixture_review_requested             = true")
    return led


# ===========================================================================
# Failure run 7 — approval fatigue (consent-quality risk over a sequence).
#
# Under one intent, the merchant revises its offer four times in a few minutes —
# each revision changing a material term (price, delivery estimate, cancellation
# window) — and a human-labeled participant emits an approval for each. Every
# AUTHORIZE is mock-signed and passes verify_log. A policy fold,
# audit_approval_cadence, looks at that SEQUENCE — a new fold target — and flags
# a structural consent-quality risk: many approvals in a short window
# (REPEATED_APPROVAL_CHURN) re-approving moving terms (MATERIAL_CHANGE_UNCONSOLIDATED).
# The configured response is to PAUSE payment for a consolidated re-review.
#
# This is not a new finding letter or a claim that this fixture can measure
# attention or prove fatigue. It is the same disclosure-vs-cognition boundary as
# [E] and [F] (recorded claims do not establish what a person saw or weighed), on the
# temporal/sequence axis. Fast approvals are equally consistent with an
# informed, decisive user, so this is a review trigger, never a verdict.
# (Mirrors the question in artifacts/approval-fatigue.json.)
# ===========================================================================

def run_approval_fatigue() -> Ledger:
    led = Ledger()
    human = Party(led, "human", "k:human")
    consumer = Party(led, "consumer-agent", "k:consumer_agent")
    merchant = Party(led, "merchant-agent", "k:merchant")

    print("\n1. Identity — the parties anchor keys")
    for p in (human, consumer, merchant):
        p.emit("KEY", "id.key_register", payload={"key": p.key})

    print("\n2. One intent, then four revised offers in a few minutes — each changing")
    print("   a material term — followed by human-labeled approvals in quick succession.")
    say("human-labeled participant", "lunch: vegetable bibimbap nearby, delivered, under 15000 KRW")
    intent = consumer.emit("ATTEST", "intent.canonical",
                           payload={"item": "bibimbap", "max_total_krw": 15000,
                                    "delivery": True, "context": CONTEXT})

    # Timestamps are given explicitly so the cadence itself is visible; in a real
    # flow they would simply be the signing times. The offers and their approvals
    # cluster inside ~2.5 minutes, mirroring artifacts/approval-fatigue.json —
    # and they follow the intent and key registrations they reference (the
    # ledger clock above runs 12:01–12:04), so their claimed timestamps remain
    # consistent along the supplied references under the temporal fixture's rule.
    rounds = [
        (dict(price_krw=12300, eta_min=25, free_cancellation=True),
         "2026-06-08T12:05:20Z", "initial request"),
        (dict(price_krw=12600, eta_min=25, free_cancellation=True),
         "2026-06-08T12:06:10Z", "price +300"),
        (dict(price_krw=12600, eta_min=31, free_cancellation=True),
         "2026-06-08T12:06:55Z", "delivery estimate +6 min"),
        (dict(price_krw=12900, eta_min=31, free_cancellation=False),
         "2026-06-08T12:07:40Z", "price +300, free cancellation removed"),
    ]

    last_offer = None
    for i, (terms, ts, note) in enumerate(rounds, 1):
        offer = merchant.emit("ATTEST", "commerce.offer", ts=ts, refs=(intent.id,),
                              payload={"item": "bibimbap", "context": CONTEXT,
                                       "expires": "2026-12-31T00:00:00Z", **terms})
        say("human-labeled participant", f"authored approval {i} ({note})")
        human.emit("AUTHORIZE", "consent.approval", ts=ts, refs=(offer.id,),
                   scope={"max_total_krw": terms["price_krw"], "payee": "k:merchant",
                          "context": CONTEXT})
        last_offer = offer

    verify_log(led.events)
    state = project_transaction_state(led.events, last_offer.id)
    print(f"\n  fixture replay check: PASS ({len(led.events)} mock-signed records)")
    print(f"  structural state (latest offer's txn): {state}   "
          f"(an approval exists; no payment yet)")

    print("\n3. A policy fold reads the human-labeled signer's approval SEQUENCE:")
    findings = audit_approval_cadence(led.events, CONTEXT)
    verdict = f"{len(findings)} FINDING(S)" if findings else "CLEAN"
    print(f"  approval cadence audit: {verdict}")
    for code, why in findings:
        print(f"      ! {code}  {why}")

    print("\n4. Configured response: PAUSE payment for a consolidated re-review —")
    print("   no commerce.payment_result is emitted; the order does not advance.")
    print("  => every AUTHORIZE passes the fixture checks and this policy voids none of them. The")
    print("     cadence fold — over the human-labeled signer's approval SEQUENCE — flags")
    print("     a consent-quality risk: repeated approvals of changing terms in a short")
    print("     window. The cadence triggers review without determining attention or")
    print("     off-log review; fast approvals may come from an informed, decisive")
    print("     user. So this is a review trigger, not a verdict —")
    print("       confirmed_inattention                = false  (attention is unverifiable)")
    print("       repeated_approval_churn              = true")
    print("       material_change_unconsolidated       = true")
    print("       payment_event_emitted                = false")
    print("       fixture_review_requested             = true")
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

    print("\n" + "-" * 78)
    print("[E] FAILURE RUN — no declared external anchor")
    print("-" * 78)
    run_fake_merchant()

    print("\n" + "-" * 78)
    print("[F] FAILURE RUN — compromised consumer agent (disclosure mismatch)")
    print("-" * 78)
    run_compromised_agent()

    print("\n" + "-" * 78)
    print("[G] FAILURE RUN — discovery bias (undisclosed sponsored ranking)")
    print("-" * 78)
    run_discovery_bias()

    print("\n" + "-" * 78)
    print("[H] FAILURE RUN — approval fatigue (consent-quality over a sequence)")
    print("-" * 78)
    run_approval_fatigue()

    print("\n" + "=" * 78)
    print("A deterministic mock-signature check does not establish freshness, payment")
    print("backing, independent counterparties, merchant identity, displayed warnings,")
    print("ranking disclosure, or consolidated review. The")
    print("fixture preserves mock-signed claims; freshness,")
    print("payment-backing, rater diversity, identity assurance, consent disclosure,")
    print("ranking disclosure, and approval cadence are projections over them, not")
    print("properties of the bytes — each is a configured application review trigger,")
    print("not a fraud verdict. The fixture preserves the claimed record bytes; it does")
    print("not establish the external referent or displayed view.")
    print("=" * 78)

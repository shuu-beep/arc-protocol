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

Eight runs:
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
  [E] fake-merchant failure run — a newly-created merchant with no external
      anchor and no history publishes a byte-valid (and unusually cheap) offer.
      Before the human approves, a policy fold, audit_merchant_identity_assurance,
      surfaces what the merchant's key does and does NOT carry: IDENTITY_UNVERIFIED
      and NO_TRACK_RECORD. An established merchant in the same run, anchored and
      with a prior outcome, audits CLEAN — so the signal discriminates rather than
      penalizing every newcomer. A valid signature proves a key signed; it does
      not prove the merchant was vetted. This is a warning to show before approval,
      not a fraud finding. (Mirrors the question posed by artifacts/fake-merchant.json.)
  [F] compromised-consumer-agent failure run — the consumer agent records a
      commerce.disclosure claiming it showed the human no warnings, then relays a
      byte-valid AUTHORIZE. verify_log passes. But an auditor re-folds the SAME log
      and recovers the warnings the agent omitted (IDENTITY_UNVERIFIED,
      NO_TRACK_RECORD): they are folds over the signed events, not part of the
      off-log view, so they are recomputable by anyone. audit_consent_disclosure
      marks the consent CONTESTED — not automatically invalid. This is the commerce
      embodiment of the view-fidelity probe (../view-fidelity-demo, "What You See
      Is Not What You Sign"), NOT a new finding: the omission is detectable
      post-hoc but not preventable at consent-time, and a byte-valid approval is
      not a faithfully informed approval. (Mirrors the question posed by
      artifacts/compromised-consumer-agent.json.)
  [G] discovery-bias failure run — a discovery backend ranks two offers and
      records the recommendation as a signed event, ranking the sponsored merchant
      first. Every signature verifies. But a ranking is a PROJECTION over the
      offers, not a fact, so an auditor re-derives the objective order from the
      offers' own terms: the other merchant is the better fit (cheaper, faster),
      and the sponsored weight that displaced it was on the signed record yet
      withheld from the subset shown to the human. audit_ranking_disclosure raises
      OBJECTIVE-FIT-MISMATCH and RANKING-INFLUENCE-UNDISCLOSED. This is a new fold
      target — the ranking layer — under the same disclosure jurisprudence as [F] /
      the view-fidelity probe; it is not a finding that sponsorship is improper,
      only that hidden influence which flips the objective order is reviewable. A
      byte-valid ranking is not a faithfully disclosed ranking. (Mirrors the
      question posed by artifacts/discovery-bias.json.)
  [H] approval-fatigue failure run — under one intent the merchant revises its
      offer four times in a few minutes, each changing a material term, and the
      human re-approves each in quick succession. Every AUTHORIZE is byte-valid and
      verify_log passes. But a policy fold, audit_approval_cadence, reads the
      human's own SEQUENCE of approvals — a new fold target — and flags a
      structural consent-quality risk: many approvals in a short window
      (REPEATED_APPROVAL_CHURN) re-approving moving terms
      (MATERIAL_CHANGE_UNCONSOLIDATED). The well-behaved response is to pause
      payment for a consolidated re-review. This is NOT a new finding and NOT a
      claim that ARC can measure attention or prove fatigue — it is the same
      disclosure-vs-cognition boundary as [E] and [F], on the temporal/sequence
      axis: ARC records that review was rushed, never that it failed. A sequence of
      byte-valid approvals is not a consolidated review. (Mirrors the question
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


def audit_merchant_identity_assurance(
        events: list[Event], merchant: str, context: str) -> list[tuple[str, str]]:
    """Policy fold: before a human approves a merchant's offer, surface what
    identity assurance the merchant's key does and does NOT carry. Computed only
    from KEY id.key_register, ATTEST id.anchor (an external cost-gate credential),
    and ATTEST rep.outcome events.

    NOT a fraud test and NOT a verdict. A byte-valid offer with a valid signature
    proves only that a registered key signed it; it says nothing about whether the
    key was anchored by an outside cost gate — business registration, payment
    account, community onboarding, escrow (object-model.md §97) — or has any track
    record. Absence of assurance is NOT proof of dishonesty: an unanchored, no-
    history merchant is exactly what an honest newcomer also looks like, so these
    are warnings to make visible before approval, never grounds to penalize a
    newcomer by default (object-model.md §126: cold-start and Sybil are one dial).
    And an anchor credential is itself only as good as its issuer's reading — a
    valid credential is key-possession, not a guarantee of honest fulfillment.

    Two signals:
      IDENTITY_UNVERIFIED — no id.anchor credential, issued by someone other than
        the merchant, attests this merchant's key.
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
        findings.append(("IDENTITY_UNVERIFIED",
            f"{merchant} carries no external anchor credential (id.anchor) from a "
            f"recognized issuer — its key is self-registered only"))
    if not has_history:
        findings.append(("NO_TRACK_RECORD",
            f"{merchant} has no prior rep.outcome in context '{context}' — "
            f"no completed-order history to weigh"))
    return findings


def audit_consent_disclosure(
        events: list[Event], approval: Event, context: str) -> list[tuple[str, str]]:
    """Policy fold: did the human's approval rest on a faithful view? Recompute,
    from the SAME log, the warnings that applied to the approved offer's merchant,
    and compare them against what the consumer agent's `commerce.disclosure`
    claimed it showed the human before approval.

    This is the commerce embodiment of the view-fidelity probe
    (../view-fidelity-demo, "What You See Is Not What You Sign"). It is NOT a new
    finding and NOT a fraud test. A signature seals the bytes, never the displayed
    view, so a `consent.approval` over a doctored screen is byte-valid and, at
    sign-time, byte-identical to an honest one. The crucial commerce difference
    from the abstract probe: the omitted warnings are *folds over the signed log*
    (audit_merchant_identity_assurance), not values that live only in the off-log
    render. So although the distortion is **not preventable at consent-time**, it
    is **detectable post-hoc** — an auditor re-runs the same folds and recovers
    exactly what the agent withheld, with or without the agent's own disclosure
    record. The verdict is CONTESTED, never automatically invalid: ARC exposes the
    gap between what applied and what was shown; a human / governance review, not
    the fold, decides what the approval is worth.

    A byte-valid approval is not a faithfully informed approval.
    """
    offers = {
        e.id: e for e in events
        if e.type == "ATTEST" and e.predicate == "commerce.offer"
    }
    approved_offers = [offers[r] for r in approval.refs if r in offers]

    # Recompute the warnings that applied — agent-independent folds over the log.
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
                f"approval {approval.id} was given without {code} being shown "
                f"({note}); recomputed from the log: {why}"))
    return findings


def audit_ranking_disclosure(
        events: list[Event], recommendation: Event, context: str) -> list[tuple[str, str]]:
    """Policy fold: a recommendation's asserted ranking is a CLAIM over the signed
    offers, so it can be re-derived and checked. Recompute an objective ordering of
    the candidate offers from the same log, compare it to the order the
    recommendation asserts, and check whether an influence that changed first place
    was actually surfaced to the human.

    A `commerce.recommendation` is a byte-valid ATTEST and verifies cleanly — ARC
    preserves it. But a ranking is not a fact about the world; it is a PROJECTION
    over the offers, the same way the transaction state is. The backend's asserted
    order is one such projection; an objective-fit order recomputed from the offers'
    own terms is another. When the two disagree and the factor that explains the
    disagreement was recorded on the signed recommendation but withheld from the
    subset shown to the human, the recommendation is byte-valid yet not a faithfully
    disclosed one.

    This applies the disclosure jurisprudence of audit_consent_disclosure / the
    view-fidelity probe (../view-fidelity-demo) — the influence sits on the signed
    record but is absent from the disclosed subset — to a NEW fold target: the
    ranking itself, recomputable as a projection over the offers. It is NOT a
    verdict that sponsorship is improper: the concern is hidden influence that flips
    the objective order, not influence as such (the recommendation's own record is
    the honest, auditable copy of what the backend did).

    Two signals:
      OBJECTIVE-FIT-MISMATCH — the offer ranked first is not the offer an objective
        ordering (lower total price, then faster delivery) would put first. This
        covers the listed request factors only; it does not claim a universal rule.
      RANKING-INFLUENCE-UNDISCLOSED — a ranking factor recorded on the signed
        recommendation favored the displacing offer over the objective-fit offer,
        but was absent from the subset disclosed to the human.
    """
    ranked = recommendation.payload.get("ranked", [])              # asserted order
    factors = recommendation.payload.get("ranking_factors", {})    # full inputs, signed
    disclosed = set(recommendation.payload.get("inputs_disclosed_to_human", []))

    offers = {
        e.id: e for e in events
        if e.type == "ATTEST" and e.predicate == "commerce.offer"
        and e.id in set(ranked)
    }

    findings: list[tuple[str, str]] = []
    if not ranked or any(oid not in offers for oid in ranked):
        return findings

    # Objective ordering recomputed from the offers' own terms: cheapest first,
    # then fastest. Transparent and admittedly partial, by design.
    def objective_key(oid: str) -> tuple[int, int]:
        p = offers[oid].payload
        return (p.get("price_krw", 0), p.get("eta_min", 0))

    asserted_first = ranked[0]
    objective_first = sorted(ranked, key=objective_key)[0]

    if asserted_first != objective_first:
        findings.append(("OBJECTIVE-FIT-MISMATCH",
            f"recommendation ranks {offers[asserted_first].signer} first, but an "
            f"objective ordering (lower price, then faster delivery) puts "
            f"{offers[objective_first].signer} first"))

        # Was an influence that displaced the objective fit recorded but not shown?
        # `ranking_factors` maps a factor name -> {offer_id: weight}. A factor on
        # the signed record, absent from the disclosed subset, that scores the
        # asserted-first offer ABOVE the objective-fit offer is undisclosed influence.
        for factor, weights in factors.items():
            if factor in disclosed or not isinstance(weights, dict):
                continue
            if weights.get(asserted_first, 0) > weights.get(objective_first, 0):
                findings.append(("RANKING-INFLUENCE-UNDISCLOSED",
                    f"factor '{factor}' on the signed recommendation scored "
                    f"{offers[asserted_first].signer} ({weights.get(asserted_first)}) "
                    f"above {offers[objective_first].signer} "
                    f"({weights.get(objective_first)}), but was not in the subset "
                    f"disclosed to the human {sorted(disclosed)}"))
    return findings


# Approval-cadence review thresholds. Coarse, admittedly arbitrary review triggers
# (like the reputation thresholds), NOT a measure of attention: ARC cannot read a
# human's mental state. They flag a structural consent-quality risk — many
# approvals with changing terms in a short window — for a human to re-review.
APPROVAL_CHURN_BAR = 3                            # approvals in the window that start to look like churn
APPROVAL_CADENCE_WINDOW = timedelta(minutes=3)   # approvals this close together = a cluster
MATERIAL_TERMS = ("price_krw", "eta_min", "free_cancellation")


def audit_approval_cadence(events: list[Event], context: str) -> list[tuple[str, str]]:
    """Policy fold: surface a consent-QUALITY risk when a human re-approves a rapid
    sequence of offers whose material terms keep changing inside a short window.

    This is NOT a measure of human attention and NOT a verdict. ARC cannot prove
    fatigue or read a mental state; every approval here is a byte-valid AUTHORIZE
    and verify_log is clean. What the fold can see is purely structural: how many
    approvals landed within a short window, and whether the offers they approved
    changed material terms across that window. Fast repeated approvals are equally
    consistent with an informed, decisive user — so this records a review trigger,
    never a finding that the consent was uninformed. It is the same disclosure-vs-
    cognition boundary as the fake-merchant and compromised-agent runs, on a new
    fold target: the human's own sequence of approvals over time. ARC records that
    review was *rushed*, not that it *failed*.

    Two signals, computed only from AUTHORIZE consent.approval events and the
    commerce.offer events they reference:

      REPEATED_APPROVAL_CHURN — at least APPROVAL_CHURN_BAR approvals fall within
        APPROVAL_CADENCE_WINDOW of one another.
      MATERIAL_CHANGE_UNCONSOLIDATED — across those clustered approvals, successive
        approved offers changed material terms, so the human re-approved moving
        terms without a consolidated side-by-side review.
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
            f"terms ({', '.join(sorted(set(changed_terms)))}) without a "
            f"consolidated re-review"))
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


# ===========================================================================
# Failure run 4 — fake (unverified) merchant, identity assurance at approval.
#
# A newly-created merchant A — self-registered key, no external anchor, no
# history — publishes a byte-valid, unusually cheap offer. An established
# merchant B in the same run is anchored (a community-issued id.anchor credential)
# and has a prior outcome. Before the human approves A's offer, a policy fold,
# audit_merchant_identity_assurance, surfaces A's missing assurance
# (IDENTITY_UNVERIFIED, NO_TRACK_RECORD) while B audits CLEAN — the signal
# discriminates rather than penalizing every newcomer. A valid signature proves
# a key signed; it does not prove the merchant was vetted. The warnings are shown
# BEFORE the AUTHORIZE; ARC records that they were shown, not that the human
# weighed them. No fraud is proven, and absence of assurance is not dishonesty.
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

    print("\n2. Merchant B is established — an external anchor + a prior outcome")
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

    print("\n5. The human approves A anyway, after the warnings were shown")
    say("human", "sees A's warnings, still wants the cheap offer... approves")
    human.emit("AUTHORIZE", "consent.approval", refs=(offer_a.id,),
               scope={"max_total_krw": 4900, "payee": merchant_a.key, "context": CONTEXT})

    verify_log(led.events)
    print(f"\n  verify_log: PASS ({len(led.events)} signed events — offer, warnings,")
    print("     and approval are all byte-valid and on the log)")
    print("  => A's offer verifies, but a verified signature is not a verified MERCHANT.")
    print("     The warnings were SHOWN before the AUTHORIZE; ARC records that they")
    print("     were shown, not that the human weighed them (the disclosure-vs-")
    print("     cognition gap). Absence of an anchor is not dishonesty, so ARC names")
    print("     the assurance gap and lets the human decide —")
    print("       confirmed_fraud      = false")
    print("       warnings_shown       = true")
    print("       human_decided        = true")
    return led


# ===========================================================================
# Failure run 5 — compromised consumer agent (commerce WYSINWYS).
#
# The consumer agent is the surface between the signed log and the human's eyes.
# Here it records a commerce.disclosure claiming it showed the human NO warnings,
# then relays a byte-valid AUTHORIZE for a new, unanchored merchant's offer. Every
# signature verifies. But the warnings the agent withheld — IDENTITY_UNVERIFIED,
# NO_TRACK_RECORD — are FOLDS over the signed log, not values that live only in
# the off-log view, so an auditor re-folds the same log and recovers exactly what
# was omitted. audit_consent_disclosure marks the consent CONTESTED.
#
# This is the commerce embodiment of ../view-fidelity-demo ("What You See Is Not
# What You Sign"), NOT a new finding letter. The signature seals the bytes, never
# the displayed view: the distortion is detectable POST-HOC (the warnings are
# recomputable) but not preventable at CONSENT-TIME (the AUTHORIZE does not bind
# the view, and at sign-time it is byte-identical to an honest one). A byte-valid
# approval is not a faithfully informed approval. No fraud is judged — the
# omission could be a bug — and consent is contested, not voided.
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

    print("\n2. Merchant A — new, unanchored, no history; makes a valid (current) offer")
    say("merchant-A", "bibimbap 4900 KRW; offer is current (far-future expiry)")
    offer = merchant_a.emit("ATTEST", "commerce.offer",
                            payload={"item": "bibimbap", "price_krw": 4900,
                                     "context": CONTEXT, "expires": "2026-12-31T00:00:00Z"})

    print("\n3. The compromised consumer agent presents the offer and records what it")
    print("   claims it disclosed — and it claims it showed the human NO warnings.")
    say("consumer-agent", "hiding the new-merchant warnings; disclosing an empty set")
    consumer.emit("ATTEST", "commerce.disclosure", refs=(offer.id,),
                  payload={"shown": [], "context": CONTEXT})

    print("\n4. The human approves over that clean-looking view")
    say("human", "sees no warnings... approves the cheap offer")
    approval = human.emit("AUTHORIZE", "consent.approval", refs=(offer.id,),
                          scope={"max_total_krw": 4900, "payee": merchant_a.key,
                                 "context": CONTEXT})

    verify_log(led.events)
    print(f"\n  verify_log: PASS ({len(led.events)} signed events — offer, disclosure,")
    print("     and approval are all byte-valid; the view-doctoring is off-log)")

    print("\n5. An auditor re-folds the SAME log to recover what was applicable:")
    findings = audit_consent_disclosure(led.events, approval, CONTEXT)
    verdict = f"CONTESTED ({len(findings)} FINDING(S))" if findings else "CLEAN"
    print(f"  consent disclosure audit: {verdict}")
    for code, why in findings:
        print(f"      ! {code}  {why}")
    print("  => the AUTHORIZE is byte-valid and stays valid — ARC does NOT void it.")
    print("     But the consent rested on a view that omitted warnings the log itself")
    print("     can reproduce, so it is CONTESTED. Detectable post-hoc (the warnings")
    print("     are folds, recomputable by anyone), not preventable at consent-time")
    print("     (the signature seals the bytes, never the displayed view). Binding a")
    print("     view_hash / 'sign what you saw' would relocate trust to the renderer")
    print("     and still not prove the human comprehended. No fraud is judged —")
    print("       confirmed_fraud                     = false")
    print("       consent                             = CONTESTED")
    print("       human_or_governance_review_required = true")
    return led


# ===========================================================================
# Failure run 6 — discovery bias (undisclosed sponsored ranking).
#
# A discovery backend ranks two offers for the same request and records the
# recommendation as a signed event. It ranks merchant A first — a sponsored
# weight on the SIGNED record put it there — but the subset it surfaces to the
# human lists only the neutral factors. Every signature verifies. Yet a ranking
# is not a fact; it is a PROJECTION over the offers, so the asserted order can be
# re-derived: B is the objective fit (cheaper and faster), and the sponsored
# weight that displaced it was on the record but withheld from the human.
# audit_ranking_disclosure raises OBJECTIVE-FIT-MISMATCH and
# RANKING-INFLUENCE-UNDISCLOSED. The well-behaved response is to PAUSE approval.
#
# This is a NEW fold target — the ranking layer — under the SAME disclosure
# jurisprudence as [F] / the view-fidelity probe (the influence is on the signed
# record but absent from the disclosed subset). It is NOT a finding that
# sponsorship is improper: hidden influence that flips the objective order is the
# concern, not influence as such, and the recommendation's own record is the
# honest, auditable copy. ARC exposes the gap; it does not suppress the ranking
# or decide manipulation — a human / governance review does.
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
    print("   A is ranked first — a sponsored weight on the SIGNED record put it there —")
    print("   but the subset disclosed to the human lists only the neutral factors.")
    say("discovery-backend", "ranking A first; recording all factors, surfacing a subset")
    rec = backend.emit("ATTEST", "commerce.recommendation",
                       refs=(offer_a.id, offer_b.id),
                       payload={
                           "ranked": [offer_a.id, offer_b.id],   # asserted order
                           "ranking_factors": {                  # full inputs, signed
                               "item_match":       {offer_a.id: 1.0, offer_b.id: 1.0},
                               "price_fit":        {offer_a.id: 0.6, offer_b.id: 0.8},
                               "delivery_fit":     {offer_a.id: 0.6, offer_b.id: 0.8},
                               "sponsored_weight": {offer_a.id: 0.2, offer_b.id: 0.0},
                           },
                           # what the human actually saw — the sponsored weight omitted
                           "inputs_disclosed_to_human": ["item_match", "price_fit",
                                                         "delivery_fit"],
                           "context": CONTEXT})

    verify_log(led.events)
    print(f"\n  verify_log: PASS ({len(led.events)} signed events — the recommendation,")
    print("     with its full factors, is byte-valid and on the log)")

    print("\n4. An auditor re-folds the recommendation against an objective ordering:")
    findings = audit_ranking_disclosure(led.events, rec, CONTEXT)
    verdict = f"{len(findings)} FINDING(S)" if findings else "CLEAN"
    print(f"  ranking disclosure audit: {verdict}")
    for code, why in findings:
        print(f"      ! {code}  {why}")

    print("\n5. Seeing the exposed gap, the consumer agent / human PAUSES rather than")
    print("   approving the sponsored-first result — no AUTHORIZE is emitted.")
    state = project_transaction_state(led.events, offer_a.id)
    print(f"  structural state (offer A's txn): {state}   (no approval — still pending)")
    print("  => the recommendation is byte-valid and ARC does NOT suppress it. But a")
    print("     ranking is a PROJECTION over the offers, so the asserted order can be")
    print("     re-derived and compared: B is the objective fit, and the sponsored")
    print("     weight that displaced it was on the signed record yet absent from what")
    print("     the human saw. Sponsorship is not prohibited — hidden influence that")
    print("     flips the objective order is the concern. The human / governance, not")
    print("     ARC, decides; here the well-behaved response is to pause —")
    print("       confirmed_manipulation              = false")
    print("       objective_fit_mismatch              = true")
    print("       ranking_influence_undisclosed       = true")
    print("       approval_completed                  = false")
    print("       human_or_governance_review_required = true")
    return led


# ===========================================================================
# Failure run 7 — approval fatigue (consent-quality risk over a sequence).
#
# Under one intent, the merchant revises its offer four times in a few minutes —
# each revision changing a material term (price, delivery estimate, cancellation
# window) — and the human re-approves each in quick succession. Every AUTHORIZE
# is byte-valid and verify_log passes. But a policy fold, audit_approval_cadence,
# looks at the human's own SEQUENCE of approvals — a new fold target — and flags
# a structural consent-quality risk: many approvals in a short window
# (REPEATED_APPROVAL_CHURN) re-approving moving terms (MATERIAL_CHANGE_UNCONSOLIDATED).
# The well-behaved response is to PAUSE payment for a consolidated re-review.
#
# This is NOT a new finding letter and NOT a claim that ARC can measure attention
# or prove fatigue. It is the same disclosure-vs-cognition boundary as [E] and [F]
# (ARC records that warnings were shown / a view was rendered, never that the human
# weighed them), here on the temporal/sequence axis: ARC records that review was
# *rushed*, never that it *failed*. Fast approvals are equally consistent with an
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
    print("   a material term — that the human re-approves in quick succession.")
    say("human", "lunch: vegetable bibimbap nearby, delivered, under 15000 KRW")
    intent = consumer.emit("ATTEST", "intent.canonical",
                           payload={"item": "bibimbap", "max_total_krw": 15000,
                                    "delivery": True, "context": CONTEXT})

    # Timestamps are given explicitly so the cadence itself is visible; in a real
    # flow they would simply be the signing times. The offers and their approvals
    # cluster inside ~2.5 minutes, mirroring artifacts/approval-fatigue.json.
    rounds = [
        (dict(price_krw=12300, eta_min=25, free_cancellation=True),
         "2026-06-05T12:01:20Z", "initial request"),
        (dict(price_krw=12600, eta_min=25, free_cancellation=True),
         "2026-06-05T12:02:10Z", "price +300"),
        (dict(price_krw=12600, eta_min=31, free_cancellation=True),
         "2026-06-05T12:02:55Z", "delivery estimate +6 min"),
        (dict(price_krw=12900, eta_min=31, free_cancellation=False),
         "2026-06-05T12:03:40Z", "price +300, free cancellation removed"),
    ]

    last_offer = None
    for i, (terms, ts, note) in enumerate(rounds, 1):
        offer = merchant.emit("ATTEST", "commerce.offer", ts=ts, refs=(intent.id,),
                              payload={"item": "bibimbap", "context": CONTEXT,
                                       "expires": "2026-12-31T00:00:00Z", **terms})
        say("human", f"approval {i} ({note}) — a quick confirmation tap")
        human.emit("AUTHORIZE", "consent.approval", ts=ts, refs=(offer.id,),
                   scope={"max_total_krw": terms["price_krw"], "payee": "k:merchant",
                          "context": CONTEXT})
        last_offer = offer

    verify_log(led.events)
    state = project_transaction_state(led.events, last_offer.id)
    print(f"\n  verify_log: PASS ({len(led.events)} signed events — every approval is byte-valid)")
    print(f"  structural state (latest offer's txn): {state}   "
          f"(an approval exists; no payment yet)")

    print("\n3. A policy fold reads the human's SEQUENCE of approvals (not one consent):")
    findings = audit_approval_cadence(led.events, CONTEXT)
    verdict = f"{len(findings)} FINDING(S)" if findings else "CLEAN"
    print(f"  approval cadence audit: {verdict}")
    for code, why in findings:
        print(f"      ! {code}  {why}")

    print("\n4. The well-behaved response: PAUSE payment for a consolidated re-review —")
    print("   no commerce.payment_result is emitted; the order does not advance.")
    print("  => every AUTHORIZE is byte-valid and ARC does NOT void any of them. But the")
    print("     cadence fold — over the human's own approval SEQUENCE — flags a structural")
    print("     consent-quality risk: repeated approvals of changing terms in a short")
    print("     window. ARC records that review was RUSHED, never that it FAILED — it")
    print("     cannot read attention, and fast approvals may be an informed, decisive")
    print("     user. So this is a review trigger, not a verdict —")
    print("       confirmed_inattention                = false  (attention is unverifiable)")
    print("       repeated_approval_churn              = true")
    print("       material_change_unconsolidated       = true")
    print("       payment_blocked_pending_re_review    = true")
    print("       human_or_governance_review_required  = true")
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
    print("[E] FAILURE RUN — fake (unverified) merchant")
    print("-" * 78)
    run_fake_merchant()

    print("\n" + "-" * 78)
    print("[F] FAILURE RUN — compromised consumer agent (commerce WYSINWYS)")
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
    print("byte-valid approval != fresh approval; byte-valid fulfillment != backed")
    print("fulfillment; byte-valid rep.outcome != trustworthy reputation; byte-valid")
    print("offer != vetted merchant; byte-valid approval != faithfully informed")
    print("approval; byte-valid ranking != faithfully disclosed ranking; byte-valid")
    print("approvals != consolidated review. ARC preserves the signed facts; freshness,")
    print("payment-backing, rater diversity, identity assurance, consent disclosure,")
    print("ranking disclosure, and approval cadence are projections over them, not")
    print("properties of the bytes — each a review trigger for a human, never a fraud")
    print("verdict ARC reaches on its own. The signature seals the record; it never")
    print("seals the referent or the view.")
    print("=" * 78)

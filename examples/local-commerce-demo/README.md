# Local Commerce Demo

> **Status:** Runnable slices landed — `episode.py` runs the baseline happy path plus seven failure runs: stale-offer, payment-failure, colluding-reputation-farming, fake-merchant, compromised-consumer-agent, discovery-bias, and approval-fatigue (see §5.1). Every failure-run artifact in this directory is now executable.
>
> **Purpose:** Make a tiny local-commerce flow concrete enough to examine — for finding unclear states, unsafe assumptions, and failure modes.

## 1. Purpose

This example is intended to make one small local-commerce interaction concrete enough to examine. It is a reference flow for asking where approval, payment, recommendation, and reputation records become unclear or misleading.

It is not evidence that ARC works. Useful outcomes include exposed gaps, ambiguous transitions, and failures that cannot yet be handled responsibly.

## 2. Scope

The reference flow covers:

- one human request for a low-value local purchase
- two mock merchant offers compared by a consumer agent
- one optional mock logistics response
- explicit human review before any mock payment step
- a mock payment response
- limited mock reputation recording after an observable outcome
- selected failure artifacts that expose unresolved protocol, governance, and trust questions

The flow is intentionally small so that later implementation can make each state and record inspectable.

## 3. Non-Goals

This example does not:

- process real payment
- arrange real delivery or fulfillment
- verify real identity or credentials
- make real reputation judgments
- operate real governance or dispute resolution
- define a production protocol, product, or deployment architecture
- demonstrate that ARC is safe, fair, viable, or sustainable

## 4. Mock Actors

| Actor | Role in the Reference Flow |
| --- | --- |
| Human User | States intent, reviews visible terms, and approves or rejects the proposed action. |
| Consumer Agent | Requests offers, compares responses, shows a recommendation, and surfaces relevant warnings. Some failure runs examine what happens if this actor is biased or compromised. |
| Merchant Agent A | Returns one mock offer with terms, availability, and expiry. May represent a new, risky, or suspicious merchant in failure runs. |
| Merchant Agent B | Returns a competing mock offer and may be used as a safer alternative or comparison point. |
| Logistics Agent | Returns mock delivery or pickup terms when the selected option requires them. |
| Payment Provider Mock | Returns a mock payment confirmation or failure only after approval. |
| Reputation Layer Mock | Records a limited mock event tied to an observable outcome, without claiming complete truth. |
| Governance Reviewer Mock | Appears only as a pending review context in failure runs; no real governance process exists. |

## 5. Baseline Happy Path

1. The Human User asks for a small local purchase within a stated budget and delivery preference.
2. The Consumer Agent turns that request into a visible mock intent and asks Merchant Agent A and Merchant Agent B for offers.
3. Both merchant agents return offers with price, material terms, and expiry.
4. If delivery is needed, the Logistics Agent returns mock terms and an expiry or availability boundary.
5. The Consumer Agent presents a recommendation with the compared offers, selection basis, expiry, and any visible uncertainty.
6. The Human User reviews the presented terms and explicitly approves one current offer.
7. The Payment Provider Mock confirms the approved mock payment request.
8. The selected merchant and logistics path report a mock completed outcome.
9. The Reputation Layer Mock records only a limited completion event connected to that mock outcome.

The happy path is a comparison point for failure runs, not a claim of successful protocol validation.

### 5.1 Runnable Slice: `episode.py`

The baseline happy path above is now runnable. `episode.py` generates it as a signed ARC event log and folds the log back, with nothing about the transaction stored.

> **Reference flow vs runnable slice.** The reference flow in §5 describes the complete design, including a two-merchant (A/B) comparison. The runnable baseline **[A]** currently implements only the smallest executable subset of that flow: one merchant offer plus a logistics quote. Merchant B appears in the runnable examples only in failure run **[E]**. The runnable code is intentionally a faithful executable subset of the reference flow, not a complete implementation of it.

```
python3 episode.py
```

It runs eight parts. At a glance:

| Run | What it does | Fold | The point |
| --- | --- | --- | --- |
| **[A]** baseline | order state climbs as the log grows | `project_transaction_state` | state is a projection, not a stored field |
| **[B]** stale-offer | approve an expired offer | `audit_offer_freshness` | byte-valid approval ≠ fresh approval |
| **[C]** payment-failure | declined payment, blocked fulfillment | `audit_payment_before_fulfillment` | byte-valid fulfillment ≠ backed fulfillment |
| **[D]** colluding reputation | three Sybil raters clear a naive guard | `audit_reputation_rater_diversity` | byte-valid `rep.outcome` ≠ trustworthy reputation |
| **[E]** fake merchant | unanchored new merchant | `audit_merchant_identity_assurance` | byte-valid offer ≠ vetted merchant |
| **[F]** compromised agent | agent hides warnings before approval | `audit_consent_disclosure` | byte-valid approval ≠ faithfully informed approval |
| **[G]** discovery bias | sponsored weight flips the objective order, undisclosed | `audit_ranking_disclosure` | byte-valid ranking ≠ faithfully disclosed ranking |
| **[H]** approval fatigue | rapid re-approvals of changing terms | `audit_approval_cadence` | byte-valid approvals ≠ consolidated review |

The seven failure runs ([B]–[H]) are one catalog of a single point — *byte-valid is not legitimate* — on seven faces, against the [A] baseline. The detail for each run follows.

- **[A] Baseline happy path.** The lifecycle is emitted using only canonical ARC events — identity (`KEY`); intent, offers, payment, fulfillment, and outcome (`ATTEST`); and the human's approval (`AUTHORIZE`) — with no commerce-specific event type, and the order's **state** is recomputed from the log after each step via `project_transaction_state`. The state climbs `pending_approval -> approved -> paid -> fulfilled` purely because the log grew; it is a projection, never a stored field, and a rating (`rep.outcome`) does not move it. The logistics quote rides a new predicate (`commerce.logistics_offer`), not a new type — richness grows by predicate ([event-registry.md](../../docs/event-registry.md) §2.1).
- **[B] Failure run — stale-offer approval** (the question in `artifacts/stale-offer-approval.json`). The human approves a merchant offer *after* its validity window has closed. Every signature still verifies and `verify_log` passes — ARC preserves the signed facts — but a policy fold, `audit_offer_freshness`, flags the approval as **stale**. The structural state reads `approved`, yet that is not legitimate authority: freshness is a projection over the facts, not a property of the bytes. **Byte-valid approval is not fresh approval.**
- **[C] Failure run — payment failure before fulfillment** (the question in `artifacts/payment-failure.json`). The approved payment is declined. Two things must hold. First, the state fold reads the payment *result*, not merely its presence: a declined `commerce.payment_result` leaves the order at `payment_failed`, never `paid`. Second, fulfillment must not proceed on an unconfirmed payment — and because ARC cannot rely on a well-behaved agent simply choosing not to deliver, a policy fold, `audit_payment_before_fulfillment`, makes the rule structural: if a misbehaving agent attests delivery anyway, the structural state reads `fulfilled`, but the audit flags the claim as **unbacked** — no confirmed payment stands behind it. **Byte-valid fulfillment is not backed fulfillment.**
- **[D] Failure run — colluding reputation farming** (the question in `artifacts/colluding-reputation-farming.json`). A few freshly-created rater agents each `ATTEST` a positive `rep.outcome` for one merchant — nothing else: no offer, approval, payment, or fulfillment, because this slice is about the reputation *projection*, not commerce settlement. Every event is byte-valid and `verify_log` passes, and the distinct-rater count even clears a naive `>= 2` guard (three colluding raters defeat it). Yet a policy fold, `audit_reputation_rater_diversity`, raises two REVIEW-NEEDED signals — `LOW_RATER_DIVERSITY` (a trusted-looking score on a thin rater pool) and `NEW_RATER_CLUSTER` (the raters' keys were registered together). Crucially this is **suspicious evidence, not a fraud verdict**: the same pattern is equally consistent with a real local promotion, so ARC does not judge intent, applies no penalty, and reports `confirmed_fraud = false`, `automatic_penalty_applied = false`, `human_or_governance_review_required = true` ([reputation.md](../../docs/reputation.md) §12, [governance.md](../../docs/governance.md) §6.2; Sybil resistance lives in the fold, [object-model.md](../../docs/object-model.md) §104). **Byte-valid `rep.outcome` is not trustworthy reputation.**
- **[E] Failure run — fake (unverified) merchant** (the question in `artifacts/fake-merchant.json`). A newly-created merchant A — a self-registered key with no external anchor and no history — publishes a byte-valid, unusually cheap offer. *Before* the human approves it, a policy fold, `audit_merchant_identity_assurance`, surfaces what A's key does and does not carry: `IDENTITY_UNVERIFIED` (no `id.anchor` credential from an outside cost gate — business registration, escrow, onboarding; [object-model.md](../../docs/object-model.md) §97) and `NO_TRACK_RECORD` (no prior `rep.outcome`). An established merchant B in the same run — anchored by a community-issued credential and carrying a prior outcome — audits **CLEAN**, so the signal discriminates rather than penalizing every newcomer (cold-start and Sybil are one dial, [object-model.md](../../docs/object-model.md) §126). The warnings are shown before the `AUTHORIZE`; ARC records that they were shown, not that the human weighed them. A valid signature proves a key signed, not that the merchant was vetted, and absence of an anchor is not dishonesty — so this is a warning, not a fraud finding (`confirmed_fraud = false`). The slice stops at the approval; the non-fulfillment / dispute tail belongs to the payment-failure and execution-fidelity axes. **Byte-valid offer is not a vetted merchant.**
- **[F] Failure run — compromised consumer agent** (the question in `artifacts/compromised-consumer-agent.json`). This is the commerce embodiment of the [view-fidelity probe](../view-fidelity-demo/) ("What You See Is Not What You Sign") — **not a new finding**, the same wall in commerce clothing. The consumer agent, which sits between the signed log and the human's eyes, records a `commerce.disclosure` claiming it showed the human *no* warnings, then relays a byte-valid `AUTHORIZE` for the new merchant's offer. `verify_log` passes — the view-doctoring is off-log. But the warnings the agent withheld are *folds over the signed log*, not values that live only in the off-log render, so an auditor re-runs the same fold (`audit_consent_disclosure` → `audit_merchant_identity_assurance`) and recovers exactly what was omitted: `IDENTITY_UNVERIFIED`, `NO_TRACK_RECORD`. The verdict is **CONTESTED, never automatically invalid**: ARC does not void the approval, it exposes the gap between what applied and what was shown, and a human / governance review decides what the consent is worth. The distortion is **detectable post-hoc** (the warnings are recomputable by anyone) but **not preventable at consent-time** (the signature seals the bytes, never the displayed view; at sign-time the tainted consent is byte-identical to an honest one). Binding a `view_hash` / "sign what you saw" would only relocate trust into the renderer and still not prove comprehension. No fraud is judged — the omission could be a bug (`confirmed_fraud = false`, `human_or_governance_review_required = true`). **Byte-valid approval is not faithfully informed approval.**
- **[G] Failure run — discovery bias** (the question in `artifacts/discovery-bias.json`). A discovery backend ranks two offers for the same request and records the recommendation as a signed `commerce.recommendation` event (a new predicate, not a new type). It ranks merchant A first — a `sponsored_weight` on the *signed record* put it there — but the subset of factors it surfaces to the human (`inputs_disclosed_to_human`) lists only the neutral ones. `verify_log` passes. But a ranking is not a fact; it is a **projection over the offers**, the same way the transaction state is, so a policy fold, `audit_ranking_disclosure`, re-derives the objective order from the offers' own terms (lower price, then faster delivery) and finds merchant B is the better fit: `OBJECTIVE-FIT-MISMATCH`. It then sees that the factor which displaced B — the sponsored weight — was on the record yet absent from what the human saw: `RANKING-INFLUENCE-UNDISCLOSED`. This is a **new fold target — the ranking layer — under the same disclosure jurisprudence as [F] / the view-fidelity probe**, not a new finding: the influence sits on the signed record but is missing from the disclosed subset. It is **not** a verdict that sponsorship is improper — the recommendation's own record is the honest, auditable copy, and hidden influence that *flips the objective order* is the concern, not influence as such. ARC does not suppress the ranking or decide manipulation (`confirmed_manipulation = false`, `human_or_governance_review_required = true`); the well-behaved response here is to pause approval. **Byte-valid ranking is not faithfully disclosed ranking.**
- **[H] Failure run — approval fatigue** (the question in `artifacts/approval-fatigue.json`). Under one intent the merchant revises its offer four times in a few minutes — each revision changing a material term (price, delivery estimate, cancellation window) — and the human re-approves each in quick succession. Every `AUTHORIZE` is byte-valid and `verify_log` passes. But a policy fold, `audit_approval_cadence`, reads the human's own **sequence** of approvals — a *new fold target*: not a single consent, a merchant, or a ranking, but the review **cadence** itself — and flags a structural consent-quality risk: `REPEATED_APPROVAL_CHURN` (enough approvals inside a short window) and `MATERIAL_CHANGE_UNCONSOLIDATED` (successive approved offers changed material terms without a consolidated side-by-side review). The well-behaved response is to pause payment for a consolidated re-review. This is **not a new finding** and **not a claim that ARC can measure attention or prove fatigue** — it is the same disclosure-vs-cognition boundary as [E] and [F] (ARC records that warnings were shown / a view was rendered, never that the human weighed them), here on the temporal/sequence axis: **ARC records that review was *rushed*, never that it *failed***. Fast approvals are equally consistent with an informed, decisive user, so the thresholds are deliberately coarse review triggers, not detectors (`confirmed_inattention = false` — attention is unverifiable; `human_or_governance_review_required = true`). **A sequence of byte-valid approvals is not a consolidated review.**

`verify_log` passes at every recompute in all eight runs.

**Honest limits.** Stdlib only, single process, deterministic; mock signatures (a hash, not Ed25519); mock payment and mock delivery (each an `ATTEST` claim — no money moves, no parcel ships); the canonical machinery is mirrored from [`../end-to-end-demo/flow.py`](../end-to-end-demo/flow.py) to keep the example standalone. The baseline and seven failure runs (stale-offer, payment-failure, colluding-reputation-farming, fake-merchant, compromised-consumer-agent, discovery-bias, approval-fatigue) are executable — every failure-run artifact in this directory now runs. The reputation-review, identity-assurance, and approval-cadence thresholds are deliberately coarse and admittedly arbitrary — review triggers shown to a human, not detectors. A smooth mock flow is not evidence that ARC is safe, fair, or viable.

## 6. Current Mock Artifacts

The `artifacts/` directory contains small JSON records. They are not executable tests. They are review objects for finding missing states, unsafe assumptions, and unresolved questions.

| Artifact | Question Exposed |
| --- | --- |
| `baseline-transaction-log.json` | What does the ordinary happy path need to record before failures can be compared? |
| `stale-offer-approval.json` | Can an expired or changed offer be stopped before mock payment is requested? |
| `payment-failure.json` | Does the flow visibly stop fulfillment after an approved mock payment fails? |
| `fake-merchant.json` | Are uncertainty and identity-related warnings visible before approval without pretending fraud has been proven? |
| `discovery-bias.json` | Can the recommendation record show whether ranking or preferred placement influenced the presented choice? |
| `approval-fatigue.json` | Do repeated, slightly changed approval requests make meaningful human review harder? |
| `compromised-consumer-agent.json` | What if the consumer agent itself hides material warnings, sponsorship, or user preferences before approval? |
| `colluding-reputation-farming.json` | What if agents manufacture reputation through circular low-value transactions or coordinated buyer-merchant behavior? |

Each run should be evaluated for missing records, unclear states, misleading surfaces, and unresolved questions rather than for a success score.

## 7. Expected Output Artifacts

Later mock implementation should produce small, inspectable artifacts:

| Artifact | Intended Contents |
| --- | --- |
| `transaction-log.json` | Intent, offers, expiries, selected terms, approval, mock payment response, and resulting state. |
| `recommendation-log.json` | Candidate offers, comparison factors, warnings shown, sponsorship disclosure, and ranking influences. |
| `reputation-event.json` | Limited mock outcome event, its context, evidence source, uncertainty, confidence, and correction status. |
| `dispute-record.json` | Complaint, evidence, response window, provisional status, appeal path, and unresolved questions. |
| `failure-notes.md` | Failure run, observed ambiguity or break, expected safeguard, and open design question. |

## 8. Current Status

This directory began as a tiny mock reference flow plus JSON artifacts; the baseline happy path and the stale-offer, payment-failure, colluding-reputation-farming, fake-merchant, compromised-consumer-agent, discovery-bias, and approval-fatigue failure runs are now runnable as `episode.py` (§5.1) — every failure-run artifact in this directory is now executable.

No real transactions, real payments, real delivery, real identity verification, real reputation judgment, or real governance process exists in this example.

The standing rule still holds: a smooth mock flow is not evidence that ARC is safe, fair, viable, or sustainable.

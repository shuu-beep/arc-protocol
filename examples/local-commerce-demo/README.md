# Local Commerce Demo

> **What it shows:** seven authored Commerce review policies over mock-signed
> records. Each policy reports only the conditions named by its fixture.
>
> **Status:** `episode.py` now contains the complete runnable catalog ([A]–[H]). See §5.1.

## 1. Purpose

This example demonstrates the current Local Commerce reference application profile built on ARC. It illustrates one possible application of the protocol rather than defining ARC itself.

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
- validate production behavior or outcome quality

## 4. Mock Actors

| Actor | Role in the Reference Flow |
| --- | --- |
| Human User | States intent, reviews visible terms, and approves or rejects the proposed action. |
| Consumer Agent | Requests offers, compares responses, shows a recommendation, and surfaces relevant warnings. Some failure runs examine what happens if this actor is biased or compromised. |
| Merchant Agent A | Returns one mock offer with terms, availability, and expiry. May represent a new, risky, or suspicious merchant in failure runs. |
| Merchant Agent B | Returns a competing mock offer with different price, timing, and fixture evidence. |
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

### 5.1 Runnable Catalog: `episode.py`

The baseline happy path above is now runnable, together with the failure catalog below. `episode.py` generates each run as a mock-signed ARC Event log and folds it back. It stores no separate transaction-state object; transaction-related claims remain in Events.

> **Reference flow vs runnable subset.** The reference flow in §5 describes the complete design, including a two-merchant (A/B) comparison. The runnable baseline **[A]** currently implements only the smallest executable subset of that flow: one merchant offer plus a logistics quote. Merchant B appears in the runnable examples only in failure run **[E]**. The runnable code is intentionally a bounded executable subset of the reference flow, not a complete implementation of it.

```
python3 episode.py
```

The eight runs ([A]–[H]) at a glance:

| Run | What it does | Fold | The point |
| --- | --- | --- | --- |
| **[A]** baseline | order state climbs as the log grows | `project_transaction_state` | state is a projection, not a stored field |
| **[B]** stale-offer | approve an expired offer | `audit_offer_freshness` | mock-signature check ≠ freshness check |
| **[C]** payment-failure | declined payment, then an unbacked fulfillment claim | `audit_payment_before_fulfillment` | mock-signature check ≠ payment backing |
| **[D]** colluding reputation | three newly registered rater keys clear a naive guard | `audit_reputation_rater_diversity` | recorded outcome claims ≠ independent counterparties |
| **[E]** no declared external anchor | new merchant without a non-self `id.anchor` record | `audit_merchant_identity_assurance` | key registration ≠ external identity evidence |
| **[F]** compromised agent | disclosure claim omits computed warning codes | `audit_consent_disclosure` | recorded approval ≠ evidence of the displayed view |
| **[G]** discovery bias | sponsored weight flips the named order but is absent from the claimed disclosed subset | `audit_ranking_disclosure` | recorded recommendation ≠ complete disclosure claim |
| **[H]** approval fatigue | rapid re-approvals of changing terms | `audit_approval_cadence` | approval records ≠ evidence of consolidated review |

The seven failure runs ([B]–[H]) apply distinct authored Commerce review policies
to mock-signed claims, against the [A] baseline. The detail follows.

- **[A] Baseline happy path.** The lifecycle is emitted using only canonical ARC events — identity (`KEY`); intent, offers, payment, fulfillment, and outcome (`ATTEST`); and a human-labeled approval (`AUTHORIZE`) — with no commerce-specific event type, and the order's **state** is recomputed from the log after each step via `project_transaction_state`. The state climbs `pending_approval -> approved -> paid -> fulfilled` purely because the log grew; it is a projection, never a stored field, and a rating (`rep.outcome`) does not move it. The logistics quote rides a new predicate (`commerce.logistics_offer`), not a new type — richness grows by predicate ([event-registry.md](../../docs/event-registry.md) §2.1).
- **[B] Failure run — stale-offer approval** (the question in `artifacts/stale-offer-approval.json`). The approval oracle emits `AUTHORIZE` for a merchant offer *after* its stated validity window has closed. The fixture's mock-signature/key-registration check passes, while `audit_offer_freshness` flags the approval as **stale** under its named timestamp policy. The structural state reads `approved`; freshness is a separate Projection over the supplied records.
- **[C] Failure run — payment failure before fulfillment** (the question in `artifacts/payment-failure.json`). A declined `commerce.payment_result` produces the fixture state `payment_failed`. If a fulfillment claim is later added, `audit_payment_before_fulfillment` labels it `UNBACKED-FULFILLMENT` because no confirmed payment claim references its approval. This is an application-policy reading; the fixture executes neither payment nor delivery.
- **[D] Failure run — colluding reputation farming** (the question in `artifacts/colluding-reputation-farming.json`). Three freshly-created rater keys emit positive `rep.outcome` claims. The fixture's coarse thresholds report `LOW_RATER_DIVERSITY` and `NEW_RATER_CLUSTER`. These are authored review triggers, not proof that keys map to independent people, that transactions occurred, or that fraud occurred (`confirmed_fraud = false`).
- **[E] Failure run — no declared external anchor** (the question in `artifacts/fake-merchant.json`). A newly-created merchant A — a self-registered key with no non-self `id.anchor` record and no history — publishes a mock-signed offer. Before approval, `audit_merchant_identity_assurance` reports `NO_DECLARED_EXTERNAL_ANCHOR` and `NO_TRACK_RECORD`. Merchant B has a community-signed `id.anchor` record and a prior outcome record, so the same policy reports no warning for B. The code accepts any non-self `id.anchor`; it does not enforce a named issuer set. The script prints these warnings before emitting `AUTHORIZE`, but it emits no warning/disclosure Event and cannot establish what a human saw or weighed. Absence of such a record is not dishonesty or fraud (`confirmed_fraud = false`).
- **[F] Failure run — compromised consumer agent** (the question in `artifacts/compromised-consumer-agent.json`). The consumer agent records a `commerce.disclosure` whose claimed `shown` list is empty, followed by an `AUTHORIZE`. An observer holding the same Event set and declared Projection inputs can reproduce `NO_DECLARED_EXTERNAL_ANCHOR` and `NO_TRACK_RECORD` and compare them with that disclosure claim. The mismatch is **CONTESTED, never automatically invalid**. The code cannot establish what appeared on screen or what the human understood; it only shows that the recorded disclosure omits warning codes produced by the named policy.
- **[G] Failure run — discovery bias** (the question in `artifacts/discovery-bias.json`). A discovery backend records a `commerce.recommendation` claim whose selected offer differs from the order produced by this fixture's named price-then-ETA policy. The record includes `sponsored_weight` while `inputs_disclosed_to_human` omits it, so `audit_ranking_disclosure` reports `NAMED-POLICY-MISMATCH` and `RANKING-INFLUENCE-UNDISCLOSED`. These are policy/disclosure signals, not proof of an objective best offer, actual display, or manipulation (`confirmed_manipulation = false`).
- **[H] Failure run — approval cadence** (the question in `artifacts/approval-fatigue.json`). Four rapidly changing offers and approvals trigger the fixture's coarse `REPEATED_APPROVAL_CHURN` and `MATERIAL_CHANGE_UNCONSOLIDATED` thresholds. The short cadence is only a review trigger: timestamps do not establish attention, fatigue, whether a side-by-side view was displayed, or whether review failed (`confirmed_inattention = false`).

`verify_log` passes at every recompute in all eight runs.

**Limits.** Stdlib only, single process, deterministic; mock signatures (a hash, not Ed25519); mock payment and mock delivery (each an `ATTEST` claim — no money moves, no parcel ships). The baseline and seven authored failure runs are executable. Reputation, identity-anchor, ranking, and cadence thresholds are coarse application-policy review triggers, not detectors or evidence of what a human saw or understood.

## 6. Current Mock Artifacts

The `artifacts/` directory contains small JSON records. They are review objects for finding missing states, unsupported assumptions, and unresolved questions — not executable tests in themselves. Each one below now has a runnable counterpart in `episode.py` (§5.1), which poses the same question as a generated, folded event log.

| Artifact | Question Exposed |
| --- | --- |
| `baseline-transaction-log.json` | What does the ordinary happy path need to record before failures can be compared? |
| `stale-offer-approval.json` | Does the named freshness policy report an approval recorded after offer expiry? |
| `payment-failure.json` | Does the policy distinguish a declined payment from an unbacked fulfillment claim? |
| `fake-merchant.json` | Does the fixture report absence of a non-self `id.anchor` record without labeling the newcomer fraudulent? |
| `discovery-bias.json` | Can the recommendation record show whether ranking or preferred placement influenced the presented choice? |
| `approval-fatigue.json` | Do repeated, slightly changed approval requests make meaningful human review harder? |
| `compromised-consumer-agent.json` | What if the consumer agent itself hides material warnings, sponsorship, or user preferences before approval? |
| `colluding-reputation-farming.json` | What if agents manufacture reputation through circular low-value transactions or coordinated buyer-merchant behavior? |

Each run should be evaluated for missing records, unclear states, misleading surfaces, and unresolved questions rather than for a success score.

## 7. Expected Output Artifacts

The runnable episode (§5.1) emits its event log to stdout rather than writing files. Persisting small, inspectable output artifacts is still optional future work:

| Artifact | Intended Contents |
| --- | --- |
| `transaction-log.json` | Intent, offers, expiries, selected terms, approval, mock payment response, and resulting state. |
| `recommendation-log.json` | Candidate offers, comparison factors, warnings shown, sponsorship disclosure, and ranking influences. |
| `reputation-event.json` | Limited mock outcome event, its context, evidence source, uncertainty, confidence, and correction status. |
| `dispute-record.json` | Complaint, evidence, response window, provisional status, appeal path, and unresolved questions. |
| `failure-notes.md` | Failure run, observed ambiguity or break, expected safeguard, and open design question. |

## 8. Current Status

This directory began as a tiny mock reference flow plus JSON artifacts. The baseline happy path and each listed failure artifact now have a runnable counterpart in `episode.py` (§5.1).

No real transactions, real payments, real delivery, real identity verification, real reputation judgment, or real governance process exists in this example.

The mock flow does not validate production behavior or outcome quality.

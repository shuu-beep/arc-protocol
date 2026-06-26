# Local Commerce Demo

> **Status:** Runnable slices landed — `episode.py` runs the baseline happy path plus two failure runs, stale-offer and payment-failure (see §5.1). The remaining failure-run artifacts are still mock JSON, not yet executable.
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

```
python3 episode.py
```

It runs three parts:

- **[A] Baseline happy path.** The lifecycle is emitted using only canonical ARC events — identity (`KEY`); intent, offers, payment, fulfillment, and outcome (`ATTEST`); and the human's approval (`AUTHORIZE`) — with no commerce-specific event type, and the order's **state** is recomputed from the log after each step via `project_transaction_state`. The state climbs `pending_approval -> approved -> paid -> fulfilled` purely because the log grew; it is a projection, never a stored field, and a rating (`rep.outcome`) does not move it. The logistics quote rides a new predicate (`commerce.logistics_offer`), not a new type — richness grows by predicate ([event-registry.md](../../docs/event-registry.md) §2.1).
- **[B] Failure run — stale-offer approval** (the question in `artifacts/stale-offer-approval.json`). The human approves a merchant offer *after* its validity window has closed. Every signature still verifies and `verify_log` passes — ARC preserves the signed facts — but a policy fold, `audit_offer_freshness`, flags the approval as **stale**. The structural state reads `approved`, yet that is not legitimate authority: freshness is a projection over the facts, not a property of the bytes. **Byte-valid approval is not fresh approval.**
- **[C] Failure run — payment failure before fulfillment** (the question in `artifacts/payment-failure.json`). The approved payment is declined. Two things must hold. First, the state fold reads the payment *result*, not merely its presence: a declined `commerce.payment_result` leaves the order at `payment_failed`, never `paid`. Second, fulfillment must not proceed on an unconfirmed payment — and because ARC cannot rely on a well-behaved agent simply choosing not to deliver, a policy fold, `audit_payment_before_fulfillment`, makes the rule structural: if a misbehaving agent attests delivery anyway, the structural state reads `fulfilled`, but the audit flags the claim as **unbacked** — no confirmed payment stands behind it. **Byte-valid fulfillment is not backed fulfillment.**

`verify_log` passes at every recompute in all three runs.

**Honest limits.** Stdlib only, single process, deterministic; mock signatures (a hash, not Ed25519); mock payment and mock delivery (each an `ATTEST` claim — no money moves, no parcel ships); the canonical machinery is mirrored from [`../end-to-end-demo/flow.py`](../end-to-end-demo/flow.py) to keep the example standalone. The baseline and the first two failure runs (stale-offer, payment-failure) are executable; the remaining failure-run artifacts below are not yet. A smooth mock flow is not evidence that ARC is safe, fair, or viable.

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

This directory began as a tiny mock reference flow plus JSON artifacts; the baseline happy path and the stale-offer and payment-failure failure runs are now runnable as `episode.py` (§5.1). The remaining failure-run artifacts are still mock JSON.

No real transactions, real payments, real delivery, real identity verification, real reputation judgment, or real governance process exists in this example.

The next useful step is to turn more failure-run artifacts into reproducible fixture checks, preserving the current rule: a smooth mock flow is not evidence that ARC is safe, fair, viable, or sustainable.

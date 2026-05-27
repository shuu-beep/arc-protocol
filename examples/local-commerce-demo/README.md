# Local Commerce Demo

> **Status:** Reference flow only; not implemented
>
> **Purpose:** Describe a tiny mock flow for finding unclear states and failure modes before any demo code is written.

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

The flow is intentionally small so that later implementation can make each state and record inspectable.

## 3. Non-Goals

This example does not:

- process real payment
- arrange real delivery or fulfillment
- verify real identity or credentials
- make real reputation judgments
- operate real governance or dispute resolution
- define a production protocol, product, or deployment architecture
- demonstrate that ARC is safe, fair, or viable

## 4. Mock Actors

| Actor | Role in the Reference Flow |
| --- | --- |
| Human User | States intent, reviews visible terms, and approves or rejects the proposed action. |
| Consumer Agent | Requests offers, compares responses, shows a recommendation, and surfaces relevant warnings. |
| Merchant Agent A | Returns one mock offer with terms, availability, and expiry. |
| Merchant Agent B | Returns a competing mock offer and may later be used in bias or merchant-risk runs. |
| Logistics Agent | Returns mock delivery or pickup terms when the selected option requires them. |
| Payment Provider Mock | Returns a mock payment confirmation or failure only after approval. |
| Reputation Layer Mock | Records a limited mock event tied to an observable outcome, without claiming complete truth. |

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

The happy path is a comparison point for later failure runs, not a claim of successful protocol validation.

## 6. Failure Runs To Implement Later

| Run | Question to Expose |
| --- | --- |
| Stale offer approval | Can an expired or changed offer be stopped before mock payment is requested? |
| Payment failure | Does the flow visibly stop fulfillment after an approved mock payment fails? |
| Fake merchant | Are uncertainty and identity-related warnings visible before approval without pretending fraud has been proven? |
| Discovery bias | Can the recommendation record show whether ranking or preferred placement influenced the presented choice? |
| Approval fatigue | Do repeated, slightly changed approval requests make meaningful human review harder? |

Each run should be evaluated for missing records, unclear states, misleading surfaces, and unresolved questions rather than for a success score.

## 7. Expected Output Artifacts

Later mock implementation should produce small, inspectable artifacts:

| Artifact | Intended Contents |
| --- | --- |
| `transaction-log.json` | Intent, offers, expiries, selected terms, approval, mock payment response, and resulting state. |
| `recommendation-log.json` | Candidate offers, comparison factors, warnings shown, and disclosed ranking influences. |
| `reputation-event.json` | Limited mock outcome event, its context, evidence source, and uncertainty or correction status. |
| `failure-notes.md` | Failure run, observed ambiguity or break, expected safeguard, and open design question. |

## 8. Current Status

This file defines a tiny mock reference flow before implementation.

No code, real transactions, real payments, real delivery, real identity verification, real reputation judgment, or real governance process exists in this example. The next step, if this flow is accepted, would be to create only the smallest mock records needed to examine the baseline and selected failures.

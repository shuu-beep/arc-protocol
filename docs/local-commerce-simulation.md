# ARC Protocol: Local Commerce Simulation

> **Status:** Frozen mock-simulation specification
>
> **Purpose:** Preserve the mock local-commerce flow exercised by the current
> failure catalog. This is not an active pilot or product plan.
>
> For transaction lifecycle and message types, see [protocol.md](./protocol.md).
>
> For reputation boundaries, see [reputation.md](./reputation.md).
>
> For adversarial coordination risks, see [threat-model.md](./threat-model.md).

---

## 1. Why Simulation Is Needed

This Commerce simulation examines a human-rooted ARC application profile.
Written principles alone do not show whether its proposed interactions remain
understandable under ordinary failure and deliberate manipulation.

The retained simulation forces the research model to confront concrete
questions without establishing adoption or production safety:

- Can a human tell which offer is current and which offer has expired?
- Can a recommendation log reveal hidden ranking or coordination problems?
- Can a dispute process distinguish credible harm from strategic complaints?
- Can reputation records represent uncertainty without turning suspicion into punishment?
- Can governance review remain usable when incidents arrive faster than reviewers can examine them?

This simulation is not evidence that ARC works. It is a mock environment for finding unclear states, missing records, unsafe assumptions, and unresolved governance burdens.

## 2. Simulation Scope

The simulation models a small local-commerce order in which a human asks a consumer agent to compare nearby offers, optionally arrange delivery, present material terms for approval, request mock payment, and record the outcome.

The initial scope is intentionally narrow:

| Area | Included in the Simulation |
| --- | --- |
| Commerce context | A low-value local food or household-item order |
| Discovery | A small set of mock merchant offers and selectable ranking inputs |
| Negotiation | Structured requests, signed or attributable mock offers, and expiry times |
| Logistics | One mock delivery or pickup choice with timeout behavior |
| Approval | Explicit human review before mock payment |
| Payment | Success or failure response from a payment-provider mock |
| Fulfillment | Simplified completion, cancellation, delay, or complaint event |
| Reputation | Mock events connected to transaction and dispute outcomes |
| Governance | Limited review records for disputes and suspicious patterns |

The simulation should reuse the exploratory lifecycle described in `docs/protocol.md`, including states such as `pending_approval`, `payment_failed`, `disputed`, `reputation_pending`, and `governance_action_pending`.

## 3. Non-Goals

This simulation does not:

- process real payments
- place real orders or coordinate real delivery
- prove identity, legal compliance, security, privacy, or fraud resistance
- produce a universal reputation score
- appoint a real governance community or moderator group
- define a final wire protocol or implementation architecture
- demonstrate production readiness or an ARC MVP
- show that local commerce becomes fair merely because agent messages are structured

The simulation may reveal a promising question or an obvious failure. It cannot establish that ARC is safe or viable in operation.

## 4. Core Mock Actors

| Actor | Mock Role | What the Simulation Should Record |
| --- | --- | --- |
| Human User | States an intent, reviews material terms, approves or rejects the proposed order, and may file a complaint. | Original intent, corrected intent if any, approval or rejection, dispute submission. |
| Consumer Agent | Parses intent, requests and compares offers, presents recommendations, and requests approval. | Normalized intent, queried merchants, selection criteria, recommendation explanation, warnings shown. |
| Merchant Agents | Return item availability, price, conditions, identity status, and fulfillment updates. Some may behave dishonestly or coordinate. | Offer terms, expiry, attributable identity, revisions, fulfillment claims, suspicious relationships. |
| Logistics Agent | Returns delivery or pickup terms and may fail or time out. | Delivery fee, estimate, expiry, timeout, fallback path. |
| Payment Provider Mock | Confirms or declines a payment request after human approval. | Approved terms reference, initiation time, success or failure response. |
| Reputation Layer | Records mock outcome signals without assuming they are complete truth. | Event source, verification state, context, confidence limits, later correction. |
| Governance Reviewer | Reviews disputes or suspicious behavior and records provisional outcomes. | Evidence received, response window, decision basis, appeal or unresolved queue state. |

No mock actor should be treated as reliable merely because it emits a structured message. Attributable records help review events; they do not prove honesty or fairness.

## 5. Baseline Happy-Path Scenario

The baseline case provides a control flow against which failures can be compared. It should remain deliberately ordinary rather than impressive.

| Step | Event | Expected Record |
| --- | --- | --- |
| 1 | Human asks for a local order under a stated budget and delivery window. | Original text and displayed normalized intent. |
| 2 | Consumer agent requests offers from several merchant agents. | `offer_request` records and response deadline. |
| 3 | Merchant agents return current offers with material terms and expiry. | Attributable `offer_response` records. |
| 4 | Consumer agent requests a delivery option. | `logistics_request` and `logistics_response`. |
| 5 | Consumer agent recommends one option and discloses comparison criteria. | Recommendation log and visible expiry notice. |
| 6 | Human reviews terms and approves before expiry. | `approval_confirmed` referencing the selected offer. |
| 7 | Payment provider mock confirms payment. | `payment_confirmed` tied to approval. |
| 8 | Merchant and logistics mocks report completion. | Fulfillment updates and completion event. |
| 9 | Reputation layer records a bounded completion claim whose record passes the declared mock checks. | `reputation_event` with context and evidence source. |

Even in this baseline, the simulation should ask whether the human had enough information to approve and whether the application standing input exceeds what the fixture records support.

## 6. Failure Scenarios

Each scenario should be run separately before combining failures. A failed scenario is useful if it exposes a missing rule, ambiguous log, misleading approval surface, or governance burden.

| Scenario | Setup | Failure to Expose | Evidence to Capture | Open Question |
| --- | --- | --- | --- | --- |
| New merchant without a declared external anchor | A newly listed merchant offers unusually attractive terms and later fails fulfillment or becomes unresponsive after a mock payment claim. | The profile's identity and warning inputs may be inadequate at approval time. | Offer identity label, disclosure record, payment and fulfillment claims, dispute record. | What declared evidence should this Commerce profile use without treating every newcomer as dishonest? |
| Colluding merchants | Several merchants return coordinated offers or circular positive histories that make one option appear safer. | Apparent competition or reputation may be manufactured. | Offer timing, shared attributes, recommendation ranking, transaction graph notes. | When is a suspicious pattern enough for review, but not enough for automatic penalty? |
| Stale offer approval | Human approves an offer after `expires_at`, or a merchant changes terms during review. | An expired or materially changed offer may reach payment. | Original offer, expiry, approval timestamp, refresh prompt, payment suppression. | Does the state model prevent approval of terms the human no longer has? |
| Logistics timeout | Delivery response does not arrive before the timeout. | The recommendation may quietly change from delivery to pickup or become unusable. | Timeout record, fallback shown to the human, revised terms, approval decision. | Is pickup fallback understandable and voluntary rather than silently substituted? |
| Payment failure | Payment mock rejects a properly approved request. | Fulfillment may begin despite the mock provider's failure result, or the result may be hidden. | Approval, payment failure, any fulfillment message, user notice. | Which messages must be blocked or revoked after payment failure? |
| False dispute | A party files a complaint inconsistent with attributable transaction records. | Review time and reputation may be consumed by strategic claims. | Complaint, transaction evidence, response record, provisional reviewer outcome. | How can false claims be examined without discouraging legitimate disputes? |
| Approval fatigue | The human receives repeated or confusing approval requests with small changes in terms. | Meaningful consent may degrade into routine confirmation. | Request count, changed terms, displayed differences, rejected or accidental approvals. | What should force a clearer re-review rather than another confirmation tap? |
| Discovery bias | A discovery source ranks a sponsored or preferred merchant without adequate disclosure. | The recommendation may appear neutral while being influenced by hidden incentives. | Source results, sponsorship metadata, recommendation criteria, alternative source comparison. | What disclosure is sufficient for a human to recognize ranking influence? |
| Reputation laundering | A merchant imports strong signals from a weak, captured, or unrelated context. | Reputation may convey trust it did not earn in this transaction context. | Imported event origin, context mismatch, weighting notes, warnings shown. | Which reputation is portable, and how should uncertain imports be presented? |
| Governance overload | Many disputes or appeals arrive faster than reviewers can process them. | Delays and inconsistent decisions may make governance and reputation unreliable. | Queue length, review delay, unresolved cases, provisional actions, appeal timing. | What should happen when timely review cannot be credibly provided? |

## 7. What to Observe

The simulation should prioritize observations over scores.

| Observation Area | Questions to Record |
| --- | --- |
| Human approval quality | Were material terms, identity status, expiry, and changed conditions visible before approval? |
| State integrity | Did any transition occur out of order, especially payment or fulfillment before valid approval and payment confirmation? |
| Recommendation transparency | Can the record show why one option was recommended and whether sponsorship, bias, or reputation influenced it? |
| Failure visibility | Did timeouts, stale offers, declined payments, and uncertain evidence become visible rather than silently resolved? |
| Reputation restraint | Were signals contextual, attributable, and reversible where review remained incomplete? |
| Dispute usability | Could a reviewer identify relevant evidence without treating structured logs as automatic truth? |
| Governance load | Did the review process remain timely and consistent under repeated or coordinated reports? |
| Privacy exposure | Did the simulation collect more personal or commercial detail than was needed to examine the failure? |

The most useful result may be a state that cannot yet be resolved responsibly with the current documents.

## 8. What Should Not Be Measured as Success

The following results should not be presented as proof that ARC succeeds:

- completion of one smooth mock purchase
- high mock transaction count
- low dispute count in scenarios with weak complaint mechanisms
- fast approvals caused by reduced human review
- a simple reputation score that appears stable only because attacks were limited
- automated identification of suspicious actors without meaningful human review
- fast governance decisions produced by ignoring ambiguity or appeal rights
- a recommendation that is cheaper but hides sponsorship, expiry, risk, or uncertainty

A simulation that produces friction, unresolved cases, or design revisions may be more valuable than one that appears efficient.

## 9. Expected Outputs

Each run should create inspectable mock artifacts rather than a broad success claim.

| Output | Minimum Content | Why It Matters |
| --- | --- | --- |
| Transaction logs | Intent, offers, expiries, selected terms, approval, payment response, and fulfillment state. | Exposes invalid transitions and missing context. |
| Application standing inputs | Context, claimed signal, evidence source, record-check status, and later correction where applicable. | Tests whether derived standing remains bounded by declared inputs. |
| Dispute records | Complaint, submitted evidence, reviewer response, outcome state, appeal state, and unresolved issues. | Reveals review burden and evidentiary gaps. |
| Recommendation logs | Candidate offers, comparison factors, ranking source, sponsorship disclosure, and displayed warnings. | Makes bias and manipulation easier to inspect. |
| Failure notes | Scenario, observed break, expected safeguard, missing rule, and next document or implementation question. | Keeps the simulation oriented toward learning from failure. |

Outputs may be small JSON fixtures or markdown records in a later mock-flow phase. This document does not prescribe an implementation format.

## 10. Known Tensions

| Tension | Why It Matters in the Simulation |
| --- | --- |
| Human review vs approval fatigue | More prompts may reduce hidden action while making attention less meaningful. |
| New merchant access vs fraud-screening policy | Strong warnings and filters may reduce some exposure while preventing legitimate cold-start participation. |
| Contextual reputation vs portable reputation | Local trust can be hard to transfer, while portable trust can be laundered or misapplied. |
| Discovery openness vs ranking manipulation | Multiple discovery sources can reduce dependence while increasing audit complexity. |
| Evidence retention vs privacy | Detailed logs support disputes but may expose sensitive transaction behavior. |
| Local governance vs sustainable review | Community judgment may fit local context but fail under volume, capture, or exhaustion. |
| Rapid resolution vs procedural fairness | Fast outcomes can reduce harm while increasing the risk of mistaken penalties. |

These tensions should remain visible in the outputs. The simulation should not resolve them by assumption.

## 11. Current Status

This document specifies a mock local-commerce simulation only.

The executable corpus now includes the baseline and failure catalogue in `examples/local-commerce-demo/`.

All transactions, payments, identity checks, reputation judgments, and governance decisions remain mock. No production or real-world safety claim is established; ARC has not demonstrated that this lifecycle is safe, fair, workable, or sustainable.

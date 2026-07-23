# ARC Protocol: Liability and Payment Boundaries

> **Status:** Exploratory boundary note
>
> **Purpose:** Clarify what ARC community governance, agent coordination, and mock payment flows do not replace.
>
> This document is not legal advice. It identifies boundary questions that implementations using the current ARC drafts would need to review with qualified professionals in each jurisdiction; no compatibility certification is implied.

---

## 1. Core Boundary

ARC community governance cannot replace payment-provider dispute processes, consumer protection law, professional regulation, court procedures, insurance, or legal liability.

A community decision may help a local reputation system decide whether an agent should be warned, suspended, or reviewed. It does not by itself determine legal fault, contractual liability, consumer refund rights, regulatory compliance, or damages.

This boundary is essential. Without it, ARC governance could be mistaken for a private court, a payment arbitrator, or a substitute for public legal systems.

The same boundary has an evidentiary form. Under a declared security profile, a disclosed ARC Event can support checks that a key signed the covered bytes and that those bytes were not altered; it does not establish who controlled the key, covering authority, runtime execution, or real-world outcome (the fidelity gradient in [event-registry.md](./event-registry.md) §2.4). A signed fulfillment claim is evidence that a key asserted a delivery, not proof of delivery.

## 2. Payment Providers Remain Independent

ARC does not create a payment network at this stage.

Early Commerce-profile implementations should use existing payment providers only when the action has Current Coverage from an act-specific or valid scoped human-authored `AUTHORIZE`, and should respect the provider's own rules for authorization, settlement, refund, chargeback, fraud review, and account suspension.

Possible providers may include Stripe, PayPal, Toss, Naver Pay, Kakao Pay, Apple Pay, Google Pay, bank transfer APIs, or regional payment systems. Each provider has its own legal, technical, and operational constraints.

ARC should not assume that a community governance decision can force a payment provider to refund, release, reverse, or settle a transaction.

## 3. Community Review vs Legal Review

A community review may ask:

- What evidence supports or contradicts the claim that the signed offer matched the delivered result?
- Was the approval attached to current, visible terms?
- What attributable records support claims of repeated fulfillment failure?
- Was a dispute report supported by attributable records?
- Should a local reputation note, warning, or suspension be applied?

A legal or regulatory review may ask different questions:

- Who is legally responsible for the transaction?
- Were consumer protection obligations satisfied?
- Did a provider act as a payment intermediary or marketplace operator?
- Was there negligence, fraud, misrepresentation, or unsafe product handling?
- Did professional licensing rules apply?
- Which jurisdiction and law govern the dispute?

ARC must not collapse these two layers into one.

## 4. Responsibility Chains Remain Unresolved

Agent commerce may involve several parties:

- the human buyer
- the merchant or service provider
- the logistics provider
- the consumer-agent operator
- the merchant-agent operator
- the discovery backend
- the relay operator
- the payment provider
- the AI model provider
- the community governance body

A future implementation would need to define which party is responsible for which action, claim, interface, recommendation, payment request, data retention choice, and dispute response.

Human approval may reduce unauthorized payment risk, but it does not automatically settle responsibility for misleading recommendations, hidden sponsorship, unsafe goods, failed delivery, wrong product descriptions, or negligent agent behavior.

## 5. Regulated Domains

Regulated domains require additional caution.

Law, medicine, finance, tax, insurance, architecture, and similar fields may impose licensing, advertising, recordkeeping, confidentiality, supervision, and unauthorized-practice rules. An ARC-compatible agent associated with a licensed professional does not automatically gain authority to provide regulated services.

Future professional-agent experiments should remain outside ARC's MVP scope unless reviewed under the relevant jurisdiction and professional rules.

At minimum, a future implementation would need to clarify:

- whether the agent provides information, administrative support, recommendation, or regulated service
- which licensed human or legal entity is responsible
- what the agent is explicitly not allowed to do
- which credential checks and withdrawal rules the profile applies
- what records must be retained or deleted
- how the human user is warned about limits

## 6. Payment Failure, Refund, and Chargeback Tensions

Payment failure and refund handling are not only protocol state problems.

They may involve provider rules, settlement timing, card-network chargebacks, fraud review, bank transfer irreversibility, regional consumer law, and merchant account policies.

Future Commerce-profile work should examine:

- whether approval can be reused after payment failure
- whether a payment retry requires renewed approval
- whether inventory remains reserved after failed payment
- how a provider payment-result claim is represented
- how refund status enters the transaction log
- how community dispute records interact with provider disputes
- how to avoid giving humans false confidence that community review guarantees recovery

## 7. Local Governance Should Not Become Legal Overreach

Local governance may be useful for reputation and participation decisions, but it can also create harm if it applies penalties without evidence, appeal, proportionality, or jurisdictional awareness.

Potential risks include:

- mistaken suspension harming a legitimate business
- competitors weaponizing reports
- community reviewers exceeding their competence
- private records being exposed during disputes
- conflicting decisions between communities
- decisions that conflict with payment-provider or legal outcomes

A future governance system should treat serious penalties as reviewable, appealable, and limited to the scope of the ARC-compatible community unless legal authority exists outside the protocol.

## 8. Divergent Projections and Real Harm

Two observers using different Event subsets can produce opposite Projection results for the same merchant — one reading `suspended`, another `in_good_standing`. Each result is bounded by its declared Event set, Projection, policy, and ordering inputs. This input-dependence is documented as a spatial trade-off in [trust-model-tradeoffs.md](./trust-model-tradeoffs.md) §4 and exercised in [`examples/canon-fold-demo`](../examples/canon-fold-demo/) as the event-set-disagreement scenario.

ARC's answer here is consistent with its authority model: a Projection is advisory, not authoritative. Final authority over an action remains with the party that legitimately holds responsibility for that action and its risk; in the current Commerce profiles, that party is typically human. ARC gives no guarantee that a user's community holds a complete event set, and makes no representation about what another community's Projection will show — a user reading `in_good_standing` may simply be missing the events another community holds.

If a user is harmed while their community's Event set was incomplete or stale, base ARC supplies no global adjudicator or complete global view. A declared governance profile may record an `ADJUDICATE`, while payment-provider disputes, consumer-protection processes, and other remedies remain external. Where the relevant inputs are disclosed, ARC records can support inspection of which Event set, authority, and Projection produced a view; ARC does not guarantee that every deployment exposes that information or resolve the harm itself.

This is a current protocol boundary.

## 9. Current Position

The current boundary is:

```txt
Community governance can inform trust.
It cannot replace law.
Payment records can support review.
They cannot guarantee recovery.
Human approval can reduce unauthorized action.
It cannot eliminate liability questions.
```

These issues are not solved by this document. They are made explicit so future design does not hide legal and payment risk behind protocol language.

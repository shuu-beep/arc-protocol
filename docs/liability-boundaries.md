# ARC Protocol: Liability and Payment Boundaries

> **Status:** Exploratory boundary note
>
> **Purpose:** Clarify what ARC community governance, agent coordination, and mock payment flows do not replace.
>
> This document is not legal advice. It identifies boundary questions that future ARC-compatible implementations would need to review with qualified professionals in each jurisdiction.

---

## 1. Core Boundary

ARC community governance cannot replace payment-provider dispute processes, consumer protection law, professional regulation, court procedures, insurance, or legal liability.

A community decision may help a local reputation system decide whether an agent should be warned, suspended, or reviewed. It does not by itself determine legal fault, contractual liability, consumer refund rights, regulatory compliance, or damages.

This boundary is essential. Without it, ARC governance could be mistaken for a private court, a payment arbitrator, or a substitute for public legal systems.

The same boundary has an evidentiary form. A signed ARC event can settle who signed it and that its bytes are intact, but not that the runtime executed as claimed or that the real-world outcome matched — those enter only as further attestations, each only as good as its signer (the fidelity gradient in [event-registry.md](./event-registry.md) §2.4). A signed fulfillment claim is evidence that someone asserted a delivery, not proof of a delivery; ARC preserves the claim, it does not verify the world.

## 2. Payment Providers Remain Independent

ARC does not create a payment network at this stage.

Early ARC-compatible implementations should use existing payment providers only after human approval and should respect the provider's own rules for authorization, settlement, refund, chargeback, fraud review, and account suspension.

Possible providers may include Stripe, PayPal, Toss, Naver Pay, Kakao Pay, Apple Pay, Google Pay, bank transfer APIs, or regional payment systems. Each provider has its own legal, technical, and operational constraints.

ARC should not assume that a community governance decision can force a payment provider to refund, release, reverse, or settle a transaction.

## 3. Community Review vs Legal Review

A community review may ask:

- Did the signed offer match the delivered result?
- Was the approval attached to current, visible terms?
- Did a merchant or logistics agent repeatedly fail fulfillment?
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
- how credential status is verified and revoked
- what records must be retained or deleted
- how the human user is warned about limits

## 6. Payment Failure, Refund, and Chargeback Tensions

Payment failure and refund handling are not only protocol state problems.

They may involve provider rules, settlement timing, card-network chargebacks, fraud review, bank transfer irreversibility, regional consumer law, and merchant account policies.

Future ARC protocol work should examine:

- whether approval can be reused after payment failure
- whether a payment retry requires renewed approval
- whether inventory remains reserved after failed payment
- how provider-confirmed payment is represented
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

Because ARC stores events and computes relationships as on-demand projections, two communities holding different event subsets can produce opposite projections for the same merchant — one reading `suspended`, another `in_good_standing`. This is not a bug; it is the expected result of locality. The cost is documented as a spatial trade-off in [trust-model-tradeoffs.md](./trust-model-tradeoffs.md) §4, and the divergence is exercised directly in [`examples/canon-fold-demo`](../examples/canon-fold-demo/) as the event-set-disagreement scenario.

ARC's answer here is consistent with its authority model: a projection is advisory, not authoritative. A human is the final authority over their own action and their own risk ([authority-and-conflict.md](./authority-and-conflict.md) §3). ARC gives no guarantee that a user's community holds a complete event set, and makes no representation about what another community's projection will show — a user reading `in_good_standing` may simply be missing the events another community holds.

If a user is harmed because their community's event set was incomplete or stale, ARC cannot adjudicate that harm — it has no global view to adjudicate from, by design. The appropriate remedies are the same as in any commerce failure: a payment-provider dispute, consumer protection law, or a local governance process — not the ARC protocol. ARC's role is to make the divergence inspectable (which event set, and which authority, produced which projection), not to resolve it.

This is a known limitation, not a design oversight.

## 9. Current Position

ARC should remain honest about this boundary:

```txt
Community governance can inform trust.
It cannot replace law.
Payment records can support review.
They cannot guarantee recovery.
Human approval can reduce unauthorized action.
It cannot eliminate liability questions.
```

These issues are not solved by this document. They are made explicit so future design does not hide legal and payment risk behind protocol language.

# ARC Protocol: Commerce Reference Application Profile

> **Status:** Exploratory draft
> **Purpose:** Named Commerce lifecycle Projection, message flow, state transitions, and failure modes
> For architecture overview, see [architecture.md](./architecture.md).

---

## 1. Scope

This document is not a finalized protocol rulebook. It describes one named Commerce application profile and identifies the transaction boundaries that an implementation would need to test.

**Commerce-scope note.** The mechanics below are worked through Commerce — the offer/approval/dispute lifecycle — because that is ARC's flagship application and first implementation profile, not because the protocol is Commerce-specific. Underneath, an offer is an `ATTEST`, an approval an `AUTHORIZE`, a dispute a `CHALLENGE`, and a ruling an `ADJUDICATE`; those five canonical Event types ([event-registry.md](./event-registry.md)) are general, while this lifecycle is only a named Commerce Projection. Other domains need not adopt it. Read the transaction language as the first concrete instance of a general authority, approval, and audit flow, not as the protocol's boundary ([README §7](../README.md#7-flagship-application-commerce)).

ARC remains exploratory. The purpose of this draft is to make questions about messages, states, timeouts, and failures concrete enough for review without claiming that one schema or transport is complete.

## 2. Design Constraints

- **Current Coverage before meaningful payment.** An agent may prepare an action, but this profile proceeds only when the exact act has human-authored coverage from an act-specific authorization or a valid scoped mandate. Fresh confirmation remains its default payment policy.
- **Typed structured messages.** This profile operates on inspectable message types rather than unrecorded conversational assumptions.
- **Signed offers and approvals where manipulation resistance matters.** Under the profile-selected suite, signatures may help establish which party signed particular bytes; they do not alone establish authority or outcome truth.
- **Timeout-aware negotiation.** This profile handles expiration of requests, offers, and approval windows explicitly.
- **Failure-first design.** Missing responses, stale offers, failed payments, delivery problems, and disputes are normal Commerce application concerns, not edge cases to ignore.
- **Storage-neutral.** ARC prescribes no storage backend; it requires signed events and recomputable projections, not a specific database or ledger ([README §9](../README.md#9-protocol-boundaries), [architecture.md §1.1](./architecture.md)). Ordinary databases are sufficient for many deployments; a shared cryptographic checkpoint is an optional implementation choice, never a requirement.
- **Observer-relative dispute evidence where appropriate.** External records whose declared source and profile checks pass, plus adjudication claims, may inform a named Projection while privacy, evidence availability, and jurisdictional constraints remain under review.

## 3. Core Actors

| Actor | Early Role |
| --- | --- |
| Consumer Agent | Captures a human intent, prepares structured requests, compares offers, and requests approval. |
| Merchant Agent | Returns price, availability, conditions, and fulfillment updates for a merchant. |
| Logistics Agent | Returns delivery or pickup options where logistics are needed. |
| Human Approver | Reviews material terms and confirms or rejects the proposed transaction. |
| Payment Provider | Processes payment only after this profile establishes Current Coverage. |
| Reputation Layer | Uses Canon Events carrying evidence as inputs to a named reputation Projection. |
| Community Governance Layer | Reviews disputes, reports, and community-level trust decisions where applicable. |

## 4. Commerce Reference Lifecycle Projection

```mermaid
stateDiagram-v2
    [*] --> intent_captured
    intent_captured --> offer_requested: structured query created
    offer_requested --> offer_received: merchant responds
    offer_requested --> no_offer_available: no merchant response
    offer_received --> logistics_requested: delivery needed
    offer_received --> pending_approval: pickup or no logistics needed
    logistics_requested --> logistics_received: logistics offer received
    logistics_requested --> logistics_unavailable: timeout or no provider
    logistics_unavailable --> pending_approval: pickup fallback or user informed
    logistics_received --> pending_approval: recommendation prepared
    pending_approval --> approved: human confirms
    pending_approval --> rejected: human rejects
    pending_approval --> expired: approval window lapses
    approved --> payment_pending: payment initiated
    payment_pending --> payment_confirmed: provider result claim recorded
    payment_pending --> payment_failed: provider fails
    payment_confirmed --> fulfillment_pending: merchant/logistics begins
    fulfillment_pending --> fulfilled: fulfillment claim recorded
    fulfillment_pending --> cancelled: cancelled before completion
    fulfillment_pending --> disputed: complaint filed
    fulfilled --> reputation_pending: standing input prepared
    reputation_pending --> completed: standing input recorded
    disputed --> resolved_no_fault: dismissed
    disputed --> resolved_partial_refund: partial resolution
    disputed --> resolved_full_refund: full refund
    disputed --> resolved_fraud_ruling: fraud ruling recorded
    resolved_no_fault --> reputation_pending
    resolved_partial_refund --> reputation_pending
    resolved_full_refund --> reputation_pending
    resolved_fraud_ruling --> governance_action_pending: governance review initiated
    governance_action_pending --> reputation_pending: outcome recorded after appeal window
    completed --> [*]
    rejected --> [*]
    expired --> [*]
    no_offer_available --> [*]
    payment_failed --> [*]
    cancelled --> [*]
```

This named Commerce lifecycle is a starting model. Particular applications or services may need additional states, especially around partial fulfillment, cancellation rights, refunds, and regulated transactions. These states are Projection outputs over the declared Event set under named ordering/as-of policy, not stored objects or event types (see [object-model.md](./object-model.md) §4).

## 5. Message Lifecycle

```mermaid
sequenceDiagram
    participant H as Human
    participant C as Consumer Agent
    participant M as Merchant Agent
    participant L as Logistics Agent
    participant P as Payment Provider
    participant R as Reputation Layer
    participant G as Governance Layer

    H->>C: Natural language intent
    C->>C: Parse into structured query
    C->>M: offer_request
    M-->>C: offer_response
    C->>L: logistics_request
    L-->>C: logistics_response
    C->>H: approval_request
    H-->>C: approval_confirmed or rejected
    C->>P: payment_intent
    P-->>C: payment_confirmed or failed
    C->>M: fulfillment_authorized
    M-->>C: fulfillment_update
    C->>R: reputation_event
    C->>G: dispute_report if needed
    G-->>C: governance_decision (async, if dispute filed)
```

The diagram describes one successful-path conversation with an optional dispute report. A practical implementation should also support absent messages, cancellation, retry, and dispute escalation.

## 6. Message Types

The following Commerce-profile message types describe intended roles, not a finalized schema. They are transport roles, not stored records. The records that persist are Events ([event-registry.md](./event-registry.md)): `offer_response`, `logistics_response`, `fulfillment_update`, and `reputation_event` are `ATTEST`; `approval_confirmed` is `AUTHORIZE`; `dispute_report` is `CHALLENGE`; `governance_decision` is `ADJUDICATE` (`gov.*`); `payment_confirmed` and `payment_failed` are `ATTEST` (`commerce.payment_result`); requests and `*_intent` / `*_authorized` notices are transport and are not stored. Each `ATTEST` records a claim; it does not prove the external referent or outcome.

| Type | Purpose | Notes |
| --- | --- | --- |
| `intent_record` | Preserve the original human request and its canonical interpretation. | Should distinguish original expression from parsed fields. |
| `offer_request` | Ask a merchant for price, availability, and conditions. | Should reference the canonical intent and a response window. |
| `offer_response` | Return a merchant offer. | Should include material terms, `expires_at`, and a signature where relied upon. |
| `logistics_request` | Ask for pickup or delivery availability. | Needed only where fulfillment involves logistics. |
| `logistics_response` | Return timing, fee, and delivery conditions. | May expire independently of a merchant offer. |
| `approval_request` | Present a selected option to the human. | Should show material terms and relevant expiry. |
| `approval_confirmed` | Record human confirmation. | Should identify exactly which non-expired offer was approved. |
| `approval_rejected` | Record that the human declined. | Ends or revises the proposed flow. |
| `payment_intent` | Initiate provider payment after coverage. | Must not precede Current Coverage for the exact act. |
| `payment_confirmed` | Record a provider's payment claim. | External evidence consumed by the Commerce Projection; it does not grant authority or prove execution. |
| `payment_failed` | Record a provider's failed-or-declined payment claim. | Fulfillment should not proceed without the payment evidence required by the named profile. |
| `fulfillment_authorized` | Notify merchant/logistics that the application permits fulfillment to begin. | Should only be sent after Current Coverage and the profile-required payment evidence. |
| `fulfillment_update` | Report preparation, pickup, delivery, or service state. | May support cancellation or dispute review. |
| `cancellation_notice` | Notify parties that a transaction or offer is cancelled. | Treatment depends on approval and payment state. |
| `reputation_event` | Record a claim about a transaction outcome or rating. | Evidence, verification, and privacy rules remain open. |
| `dispute_report` | File a complaint with relevant evidence. | May attach signed transaction records. |
| `governance_decision` | Record community review outcome. | Should be subject to local policy and appeal rules. |

## 7. Structured Intent and Parsing Problem

Natural language requests are convenient for humans but unstable as Commerce application input. Two agents may parse the same request differently, and the same LLM may produce different structured outputs across runs. This profile therefore distinguishes between the original human expression and the canonical structured intent used for negotiation.

```json
{
  "intent_id": "intent_001",
  "original_text": "Find me coffee and a sandwich nearby under $10.",
  "canonical_intent": {
    "category": "food_order",
    "items": ["coffee", "sandwich"],
    "max_total_price": 10.00,
    "currency": "USD",
    "location_scope": "nearby",
    "delivery_required": true
  },
  "created_by": "consumer_agent_abc",
  "requires_human_review": true
}
```

The canonical intent should be shown to the human when ambiguity matters. Human correction should update the canonical intent before offer negotiation continues.

## 8. Offer Expiration and Stale Offers

- Every offer should include an `expires_at` value.
- This Commerce Projection refuses an expired offer as a target for new approval.
- If approval happens after expiry, the consumer agent should request a refreshed offer.
- Merchants may cancel unavailable offers before approval.
- Cancellation after approval enters a cancellation or dispute flow depending on payment state and applicable rules.

Expiration protects both people and merchants from approval based on prices, stock, or delivery terms that are no longer available. The signed Event remains evidence; application refusal does not make it byte-invalid. This profile does not define a universal expiration period.

## 9. Timeout, Retry, and Failure Modes

| Failure Mode | Example | Recommended Handling |
| --- | --- | --- |
| Merchant no response | No `offer_response` before timeout | Mark unavailable, try alternatives. |
| Logistics timeout | No `logistics_response` | Inform user, fall back to pickup or retry. Route to `pending_approval`. |
| Stale offer | Human approves after `expires_at` | Require refreshed offer. |
| Duplicate offer | Same merchant sends conflicting offers | Apply the named ordering/as-of policy or ask the merchant to clarify; a signature alone does not establish which offer is latest or current. |
| Payment failure | Provider declines payment | Stop fulfillment, notify human. |
| Fulfillment delay | Merchant or logistics misses estimate | Update status, allow cancellation or dispute. |
| Agent disconnect | Relay/WebRTC failure | Retry through fallback or async inbox. |
| Dispute after completion | User claims misrepresentation | Attach signed logs to governance review. |

Retry behavior should avoid silently converting a failed or expired proposal into an approved transaction. Implementations should make consequential failures visible to the human and relevant parties.

## 10. Async Inbox and Dead Letter Handling

Not all commerce requires real-time negotiation. For slower services, an asynchronous inbox, webhook, or polling flow may be sufficient and may reduce the operational burden of persistent communication.

A message that cannot be delivered after retries may enter a dead-letter queue. Dead-letter records should be visible to relevant parties and should not silently disappear. This matters where failure to deliver an approval, cancellation, or dispute message could change a party's expectations or rights.

## 11. Known Tensions and Trade-offs

### Cold Start vs Sybil Resistance

New participants may need a visible path to first transactions, while automatically promoting arbitrary new agents may increase Sybil risk. This Commerce profile's current policy limits cold-start discovery support to clearly labeled entrants whose declared checks are visible and remain subject to human choice.

### Automatic Approval vs Governance Burden

Automation can reduce repetitive approval friction, but it can also create unclear responsibility and more disputes when an action goes wrong. This Commerce profile defaults to fresh human confirmation for meaningful payments while allowing Current Coverage from a valid, explicit, auditable scoped mandate.

### Low Merchant Cost vs Discovery Sustainability

Small merchants may benefit from lower intermediary overhead, but directories, relays, curation, and moderation still cost time and money. This Commerce research compares funding and operation models without claiming that participation or infrastructure will be free.

### Recommendation Logs vs Real Understanding

An agent can log why it selected an offer, but a log is not proof that a human understood every trade-off or that the recommendation was fair. This Commerce profile aims to expose declared material terms and reasoning on its review surface while treating explainability quality as an unresolved application problem.

### Open Discovery vs Backend Concentration

Open protocol rules do not prevent popular discovery backends from accumulating influence. This Commerce discovery policy supports replaceable backends, disclosed sponsorship, and visible ranking signals while recognizing that actual concentration risks require continued scrutiny.

### Privacy vs Auditability

Dispute review and reputation portability may benefit from durable records, while transaction logs can contain sensitive personal and commercial information. This Commerce profile favors minimum necessary disclosure, with privacy-preserving audit methods still to be explored.

### Local Governance vs Capture Risk

Local governance can reflect context and enable practical review, but established actors may capture it or exclude newcomers. This Commerce research keeps appeal, transparency, and anti-capture safeguards as application design questions rather than assuming local control is inherently fair.

## 12. Known Unknowns

- final canonical schema
- multi-language and locale support
- jurisdiction-specific credential rules
- cross-community dispute escalation
- privacy-preserving audit logs
- reputation portability limits
- relay operator accountability
- payment provider integration differences
- offline merchant bridge
- physical logistics automation boundaries

## 13. Current Status

This document is an exploratory Commerce application profile. Executable mock artifacts exercise this lifecycle in `examples/local-commerce-demo/`, but no production implementation or complete conformance profile exists.

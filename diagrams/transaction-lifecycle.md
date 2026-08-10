# ARC Historical Commerce Application: Transaction Lifecycle

> **Status:** Frozen, non-normative application example
> **Purpose:** Visual reference for the Commerce Projection exercised by the mock
> corpus; not an active product workflow or ARC base-protocol state machine.
> These application states are not additional ARC Canon Event types.
> For message flow detail, see [protocol.md](../docs/protocol.md).

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> intent_captured

    intent_captured --> offer_requested : structured query created
    offer_requested --> offer_received : merchant responds
    offer_requested --> no_offer_available : timeout or no response

    offer_received --> logistics_requested : delivery needed
    offer_received --> pending_approval : pickup or no logistics

    logistics_requested --> logistics_received : logistics responds
    logistics_requested --> logistics_unavailable : timeout or no provider

    logistics_received --> pending_approval : recommendation prepared
    logistics_unavailable --> pending_approval : user informed, pickup fallback

    pending_approval --> approved : named-profile coverage check passes
    pending_approval --> rejected : human declines
    pending_approval --> expired : approval window lapses

    approved --> payment_pending : payment initiated
    payment_pending --> payment_confirmed : provider confirmation recorded
    payment_pending --> payment_failed : provider fails

    payment_confirmed --> fulfillment_pending : merchant or logistics begins
    fulfillment_pending --> fulfilled : fulfillment claim recorded
    fulfillment_pending --> cancelled : cancelled before completion
    fulfillment_pending --> disputed : complaint filed

    fulfilled --> reputation_pending : standing input prepared
    reputation_pending --> completed : standing input recorded

    disputed --> resolved_no_fault : dismissed
    disputed --> resolved_partial_refund : partial resolution
    disputed --> resolved_full_refund : full refund
    disputed --> resolved_fraud_finding : fraud finding recorded

    resolved_no_fault --> reputation_pending
    resolved_partial_refund --> reputation_pending
    resolved_full_refund --> reputation_pending
    resolved_fraud_finding --> governance_action_pending : governance review initiated
    governance_action_pending --> reputation_pending : outcome recorded after appeal window

    completed --> [*]
    rejected --> [*]
    expired --> [*]
    no_offer_available --> [*]
    payment_failed --> [*]
    cancelled --> [*]
```

## Notes

- `logistics_unavailable` resolves to `pending_approval` rather than terminating, because pickup fallback may still be available.
- `resolved_fraud_finding` moves into `governance_action_pending` because adjudicated application findings may require suspension, appeal, or cross-community review before final closure.
- Dispute states feed back into `reputation_pending` to record application outcome claims as evidence.
- State labels summarize recorded claims and application findings; they are not outcome proof.
- This diagram reflects the frozen historical profile in `protocol.md`. It is
  retained to explain the executable fixtures, not as an active design roadmap.

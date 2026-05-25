# ARC Protocol: Reputation

> **Status:** Exploratory draft
>
> **Purpose:** Reputation signals, decay, recovery, portability, and manipulation resistance
>
> For transaction lifecycle and message flow, see [protocol.md](./protocol.md).
>
> For identity boundaries, see [identity.md](./identity.md).
>
> For dispute review and penalties, see [governance.md](./governance.md).

---

## 1. Scope

This document is not a finalized reputation algorithm.

ARC does not treat reputation as an objective measurement of human value, merchant worth, or universal trust. Reputation in ARC is an imperfect coordination signal used to help agents and humans evaluate risk under uncertainty.

The purpose of this document is to describe:

- what reputation may represent
- which signals may contribute to it
- how reputation may decay or recover
- how reputation can be attacked
- why portability is useful but dangerous
- which tensions remain unresolved

ARC assumes that all reputation systems are gameable. The design goal is not perfect trust. The goal is to make trust signals more verifiable, contextual, reviewable, and resistant to obvious manipulation.

---

## 2. Why Reputation Exists

In conventional digital commerce, visibility is often shaped by advertising budgets, platform ranking rules, fake reviews, and opaque recommendation systems.

In agent-mediated commerce, a consumer agent may compare offers using structured signals such as:

- price
- availability
- delivery reliability
- refund behavior
- dispute history
- verified completion history
- response reliability
- community standing
- identity status

Reputation exists to help the human and the consumer agent answer a practical question:

```txt
Is this agent safe enough to consider for this transaction,
under this context, with this level of risk?
```

Reputation should reduce uncertainty. It should not replace human judgment, local governance, or explicit approval.

---

## 3. Core Principles

### 3.1 Reputation Is Contextual

ARC should avoid a single universal reputation score.

A merchant may be reliable for food delivery but not relevant for home repair. A logistics agent may perform well in one city but poorly in another. A dispute reviewer may be trusted in one professional domain but not another.

Reputation should be interpreted by context:

- commerce category
- geography
- transaction size
- fulfillment type
- identity status
- dispute history
- community rules
- recent reliability

A global score may be convenient, but it can hide important differences between trust domains.

### 3.2 Reputation Is Probabilistic

Reputation is not proof of future behavior.

A high-reputation agent can still fail, be compromised, change ownership, or behave maliciously. A low-reputation or new agent may be honest but not yet established.

ARC should present reputation as a risk signal, not as a guarantee.

### 3.3 Reputation Should Be Based on Verified Interaction

ARC prefers reputation derived from verifiable transaction events rather than unverified reviews.

Useful events may include:

- completed transactions
- signed offer fulfillment
- verified delivery completion
- refund outcomes
- dispute outcomes
- cancellation patterns
- response reliability
- governance decisions

Unverified comments may still be useful, but they should be clearly separated from verified reputation events.

### 3.4 Reputation Should Not Become a Social Credit System

ARC reputation should not become a universal identity score for people.

Reputation should be limited to agent behavior within specific commerce contexts. This boundary should be a protocol-level design constraint, not just a community preference. It should not become a general judgment of a human owner's social, political, or personal worth.

---

## 4. Reputation Event Model

A reputation event is a structured record connected to a transaction, dispute, or governance outcome.

Example:

```json
{
  "event_id": "rep_001",
  "agent_id": "merchant_abc_001",
  "transaction_id": "tx_001",
  "event_type": "verified_completion",
  "context": {
    "category": "food_order",
    "community": "seoul-local-commerce",
    "fulfillment_type": "delivery"
  },
  "signals": {
    "completed": true,
    "on_time": true,
    "accurate_description": true,
    "refund_requested": false,
    "dispute_opened": false
  },
  "created_at": "2026-01-01T13:00:00Z",
  "source": "consumer_agent_xyz",
  "verification": {
    "transaction_verified": true,
    "reviewer_signature": "ed25519:consumer_xyz:..."
  }
}
```

This schema is illustrative, not final.

---

## 5. Possible Reputation Signals

### 5.1 Positive Signals

| Signal | Meaning |
| --- | --- |
| `verified_completion` | A transaction completed as agreed |
| `on_time_fulfillment` | Delivery or service completed within stated estimate |
| `accurate_description` | Offer terms matched what was delivered |
| `low_dispute_rate` | Few disputes relative to transaction volume |
| `cooperative_resolution` | Agent cooperated during refund or dispute process |
| `long_term_consistency` | Reliability persisted over time |
| `community_endorsement` | Local community verified or endorsed the agent |

### 5.2 Negative Signals

| Signal | Meaning |
| --- | --- |
| `failed_fulfillment` | Transaction was not completed |
| `late_fulfillment` | Fulfillment repeatedly missed stated estimates |
| `misrepresentation` | Offer terms differed materially from actual delivery |
| `refund_pattern` | Refund rate is unusually high for the category |
| `dispute_pattern` | Dispute rate is unusually high |
| `non_cooperation` | Agent failed to respond during review |
| `governance_penalty` | Community issued warning, suspension, or ban |
| `suspicious_velocity` | Reputation rose too quickly relative to history |
| `collusion_suspicion` | Interaction pattern resembles coordinated manipulation |

Negative signals should not automatically prove wrongdoing. They should support risk assessment and, where appropriate, human or community review.

---

## 6. Reputation Velocity

Reputation should not increase without limits.

A common attack pattern is to create many low-value transactions, fake reviews, or circular interactions to rapidly manufacture trust. ARC should therefore consider reputation velocity limits.

Possible safeguards:

- cap how quickly reputation can improve
- weight older verified history differently from sudden new activity
- treat sudden reputation spikes as review signals
- apply stronger scrutiny to new agents with unusually fast growth
- separate transaction count from trust quality

Velocity limits are anti-fraud safeguards, not economic controls. They should not be used to punish legitimate growth.

---

## 7. Decay and Trust Aging

Reputation can become stale.

An agent with excellent history from three years ago may no longer be reliable. Ownership may change. Staff may change. Automation may change. A previously active agent may become dormant and later return under different conditions.

ARC should explore reputation decay.

Decay may apply to:

- inactivity
- old transaction history
- outdated community endorsements
- expired credentials
- ownership changes
- long periods without verified fulfillment

Decay should not erase history. It should reduce the weight of old signals when evaluating current reliability.

Example directional model:

```txt
Recent verified reliability -> higher current relevance
Long-term consistency -> durable background trust
Old inactive history -> lower current weight
Recent disputes -> high current relevance
```

ARC should avoid defining a universal decay formula at this stage. Different communities and commerce categories may require different time windows.

---

## 8. Recovery After Failure

A reputation system should allow recovery.

Not every failure is fraud. Agents may fail because of:

- operational mistakes
- delivery interruptions
- payment provider errors
- supply shortages
- natural disasters
- software bugs
- account compromise
- temporary staffing problems

ARC should distinguish between accidental failure, negligent behavior, and systematic abuse.

Possible recovery signals:

- prompt acknowledgment
- refund cooperation
- transparent incident explanation
- corrective action
- successful probation period
- absence of repeated failures
- community-reviewed reinstatement

Recovery should be possible after ordinary failure.

Permanent exclusion should be reserved for serious, repeated, or verified malicious behavior.

---

## 9. Compromise and Key Rotation

Agents may be compromised.

If an agent key, account, or infrastructure is compromised, reputation handling becomes difficult. The community must determine whether bad events belong to the legitimate operator, the attacker, or both.

Possible handling:

- mark the affected time window as compromised
- rotate agent keys
- preserve prior verified history with a visible warning
- require community review before restoring full trust
- temporarily limit high-risk transactions
- require owner re-verification

Reputation should not blindly transfer to a new key without review. At the same time, compromise recovery should not automatically destroy years of legitimate history.

This remains an open design problem.

---

## 10. Reputation Portability

Reputation portability is one of ARC's most important and most dangerous ideas.

Portability can help prevent platform lock-in. A merchant should not lose all trust history simply because they move from one ARC-compatible discovery backend to another.

However, reputation portability creates risks:

- fake reputation imported from weak communities
- trust laundering across regions
- incompatible standards between communities
- inflated endorsements from captured governance systems
- over-reliance on global scores
- reduced local accountability

ARC should treat portable reputation as contextual evidence, not automatic authority.

A receiving community may choose to:

- accept external reputation fully
- partially weight external reputation
- require local probation
- require additional verification
- reject reputation from untrusted sources

Portability should support interoperability without forcing communities to trust every external record equally.

---

## 11. Dispute Weighting

Not all disputes should affect reputation equally.

A single minor late delivery should not have the same weight as verified fraud. A false dispute should not damage a merchant indefinitely. A pattern of similar complaints should matter more than one isolated report.

Factors that may affect dispute weight:

- severity of harm
- transaction value
- evidence quality
- prior history
- response behavior
- refund cooperation
- repeat pattern
- whether the dispute was upheld, rejected, or partially resolved
- whether the reporter has a history of false reports

Possible outcome categories:

| Outcome | Reputation Effect |
| --- | --- |
| `dismissed_false_report` | May affect reporter reputation |
| `resolved_no_fault` | Minimal or no penalty |
| `resolved_minor_issue` | Small contextual note |
| `resolved_partial_refund` | Moderate signal depending on pattern |
| `resolved_full_refund` | Stronger signal depending on evidence |
| `confirmed_fraud` | Severe penalty or suspension |
| `systematic_abuse` | Ban or cross-community flag |

Dispute weighting should remain reviewable and appealable.

---

## 12. Collusion and Manipulation Heuristics

ARC should assume that reputation will be attacked.

Possible attack patterns:

- circular positive reviews between related agents
- repeated low-value transactions to inflate trust
- coordinated fake disputes against competitors
- sudden review spikes from newly created accounts
- clusters of agents with shared infrastructure or ownership
- geographically improbable interaction patterns
- repeated reciprocal endorsements
- reputation laundering through weak communities
- sponsored placement disguised as organic ranking

Possible heuristic signals:

| Heuristic | Possible Meaning |
| --- | --- |
| `circular_interaction_cluster` | Agents repeatedly transact mainly with each other |
| `low_value_reputation_farming` | Many small transactions build trust too quickly |
| `shared_owner_or_provider_pattern` | Agents may not be independent |
| `sudden_positive_spike` | Reputation may be artificially inflated |
| `coordinated_dispute_cluster` | Competitors or attackers may be targeting an agent |
| `cross_community_laundering` | Reputation from weak contexts is imported elsewhere |

These signals should trigger review, not automatic punishment.

False positives are expected. Human and community judgment remains necessary.

---

## 13. Discoverability vs Entrenchment

Reputation affects discovery.

If discovery systems rely too heavily on historical reputation, established merchants may dominate visibility forever. New verified entrants may struggle to receive any first transaction. This can turn reputation into a moat rather than a trust signal.

If discovery systems promote newcomers too aggressively, Sybil attackers can exploit cold-start exposure.

ARC should treat this as a permanent tension.

Possible mitigations:

- clearly labeled verified new entrant slots
- user-selectable discovery views
- visible distinction between historical trust and recent reliability
- category-specific probation
- transparent ranking explanations
- diversity indicators in discovery results
- ability to switch discovery backends

The goal is not to punish successful agents.

The goal is to avoid silently converting reputation into permanent market control.

---

## 14. Privacy and Reputation

Reputation requires records. Commerce privacy requires restraint.

ARC should avoid exposing unnecessary personal or commercial data in reputation events.

Possible principles:

- store minimum necessary reputation facts
- separate public signals from private evidence
- hash or redact sensitive transaction details
- reveal detailed evidence only during dispute review
- avoid publishing exact user behavior histories
- support local data retention rules
- explore privacy-preserving proofs where useful

A reputation system that exposes too much data can become surveillance infrastructure.

This risk should remain visible in future design work.

---

## 15. Reputation Display

Humans should not be shown reputation as a magical number.

A useful ARC-compatible interface should explain why an agent appears trustworthy or risky.

Example display:

```txt
Merchant: Bean & Bread

Trust context:
- Verified local business
- 214 verified completed food orders
- 96% recent on-time fulfillment
- 2 disputes in last 90 days
- No confirmed fraud
- New owner verified 6 months ago
- Sponsored placement: No
```

This is more informative than:

```txt
Trust score: 4.8
```

ARC may still use summary scores internally, but user-facing reputation should preserve context where possible.

---

## 16. Relationship to Governance

Reputation and governance are separate but connected.

Reputation records observed behavior.

Governance reviews contested behavior.

A reputation event may trigger governance review. A governance decision may create a reputation event.

Examples:

- a dispute report may reduce confidence until resolved
- a confirmed false report may affect the reporter
- a suspension may become a strong negative reputation signal
- an appeal may restore or modify reputation state

Reputation should not silently replace due process.

Governance should not manipulate reputation without reviewable records.

---

## 17. Known Tensions and Trade-offs

### Local Trust vs Global Portability

Local communities understand context, but isolated reputation can create lock-in. Portable reputation helps interoperability, but may import weak or manipulated trust.

### Privacy vs Auditability

Dispute review benefits from durable evidence. Privacy requires limiting what is stored and disclosed.

### Forgiveness vs Safety

Agents should recover from ordinary failure. Repeated abuse should not be forgiven indefinitely.

### New Entrants vs Sybil Resistance

New participants need a path to discovery. Attackers exploit automatic exposure.

### Simplicity vs Accuracy

Simple scores are easy to display. Contextual trust is more accurate but harder to explain.

### Human Review vs Governance Burden

Human review reduces automation abuse. Too much review can overwhelm communities.

### Recent Reliability vs Long-Term Consistency

Recent behavior may reflect current quality. Long-term behavior may reflect deeper trustworthiness. Both can mislead if used alone.

---

## 18. Known Unknowns

- final reputation event schema
- whether summary scores should exist at all
- default decay windows
- category-specific weighting
- cross-community trust import rules
- privacy-preserving reputation proofs
- appeal effects on reputation history
- compromise recovery standards
- detection thresholds for collusion
- how to fund reputation review infrastructure
- how to prevent reputation systems from becoming social credit systems
- how to show reputation clearly without oversimplifying it

---

## 19. Current Status

This document is an exploratory reputation model.

No implementation exists.

The next useful contribution is a small simulation that records mock reputation events across successful transactions, failed fulfillment, disputes, recovery, and suspicious collusion patterns.

The purpose of that simulation should not be to prove that ARC reputation works.

The purpose should be to expose where the model breaks.

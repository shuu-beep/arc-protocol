# ARC Protocol: Commerce Reputation Application and Named Projection Research

> **Status:** Exploratory draft
>
> **Purpose:** Illustrative Commerce reputation signals, named Projection policy, decay, recovery, portability, and manipulation resistance
>
> For transaction lifecycle and message flow, see [protocol.md](./protocol.md).
>
> For identity boundaries, see [identity.md](./identity.md).
>
> For dispute review and penalties, see [governance.md](./governance.md).

---

## 1. Scope

This document is not a finalized reputation algorithm or a mandatory global Projection.

This Commerce application research does not treat reputation as an objective measurement of human value, merchant worth, or universal trust. Its reputation output is an imperfect coordination signal used to help agents and humans evaluate risk under uncertainty.

The purpose of this document is to describe:

- what reputation may represent
- which signals may contribute to it
- how reputation may decay or recover
- how reputation can be attacked
- why portability is useful but dangerous
- which tensions remain unresolved

This research treats manipulation as a design risk. It explores evidence-linked, contextual, and reviewable application signals without claiming perfect trust or manipulation resistance.

---

## 2. Why Reputation Exists

In conventional digital commerce, visibility is often shaped by advertising budgets, platform ranking rules, fake reviews, and opaque recommendation systems.

In agent-mediated commerce, a consumer agent may compare offers using structured signals such as:

- price
- availability
- delivery reliability
- refund behavior
- dispute history
- evidence-linked completion history
- response reliability
- community standing
- identity status

In this Commerce profile, a named reputation Projection helps the human and consumer agent answer a narrower question:

```txt
Does this Projection cross the application's declared review threshold
for this transaction and context?
```

Reputation should reduce uncertainty. It should not replace human judgment, local governance, or explicit approval.

---

## 3. Commerce Reputation-Projection Research Principles

### 3.1 Reputation Is Contextual

ARC should avoid a single universal reputation score.

A merchant may have favorable evidence for food delivery but no relevant evidence for home repair. A logistics agent may have different outcome claims in different cities. A dispute reviewer may hold declared authority in one professional domain but not another.

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

### 3.2 Reputation Does Not Prove Future Behavior

Reputation is not proof of future behavior.

A high-reputation agent can still fail, be compromised, change ownership, or behave maliciously. A low-reputation or new agent may be honest but not yet established.

ARC should present reputation as a risk signal, not as a guarantee.

### 3.3 Reputation Should Be Based on Evidence-Linked Interaction Claims

This Commerce profile prefers reputation derived from evidence-linked transaction claims and external records whose declared checks pass rather than unchecked reviews. Those checks do not prove the external interaction or outcome.

Useful Event claims may include:

- transaction-completion claims
- signed fulfillment claims tied to offers
- delivery-completion records that pass the profile's declared checks
- refund-result claims
- dispute rulings
- cancellation patterns
- response reliability
- governance decisions

Unchecked comments may still be useful, but they should be clearly separated from records that pass the named profile's declared checks.

### 3.4 Avoiding a Universal Person-Level Score

This Commerce reputation profile should not become a universal identity score for people.

This application policy limits its reputation output to agent behavior within specific Commerce contexts. It is not a base-protocol rule, and it should not become a general judgment of a human owner's social, political, or personal worth.

---

## 4. Reputation-Evidence Record Model

This application model uses a Canon Event carrying a structured claim connected to a transaction, dispute, or governance ruling.

Example:

```json
{
  "event_id": "rep_001",
  "agent_id": "merchant_abc_001",
  "transaction_id": "tx_001",
  "claim_type": "completion_claim",
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
  "record_check": {
    "declared_checks_passed": true,
    "reviewer_signature": "ed25519:consumer_xyz:..."
  }
}
```

This schema is illustrative, not final. `completion_claim` and `declared_checks_passed` are application labels, not proof of completion or outcome truth. In object-model terms this record is an `ATTEST` with predicate `rep.outcome`; the reputation summary a user sees is a named Projection — a fold over claims and evidence scoped to context — never a stored score (see [object-model.md](./object-model.md), [event-registry.md](./event-registry.md)).

Any claim about a reputation output must identify the Projection name and version, Event-set scope, any completeness contract being claimed, policy parameters, and ordering/as-of assumptions. Behavior outside those declared inputs is unsupported.

---

## 5. Possible Reputation Signals

### 5.1 Positive Signals

| Signal | Meaning |
| --- | --- |
| `verified_completion` | Application label: a completion claim whose record passed declared checks; not proof that the transaction completed as agreed |
| `on_time_fulfillment` | Available evidence reports completion within the stated estimate |
| `accurate_description` | Available evidence reports that delivered results matched offer terms |
| `low_dispute_rate` | Few disclosed dispute records relative to declared transaction volume |
| `cooperative_resolution` | Available records report cooperation during refund or dispute process |
| `long_term_consistency` | Available outcome claims span the profile's declared time window |
| `community_endorsement` | A local community recorded an endorsement claim |

### 5.2 Negative Signals

| Signal | Meaning |
| --- | --- |
| `failed_fulfillment` | Available evidence contains a non-completion claim |
| `late_fulfillment` | Available evidence reports repeated misses of stated estimates |
| `misrepresentation` | Available evidence claims a material difference between offer terms and delivery |
| `refund_pattern` | Disclosed refund-result claims are unusually frequent under the profile's category baseline |
| `dispute_pattern` | Disclosed dispute records are unusually frequent under the profile's baseline |
| `non_cooperation` | Available records report no response during the declared review window |
| `governance_penalty` | A community warning, suspension, or ban ruling is recorded |
| `suspicious_velocity` | Reputation rose too quickly relative to history |
| `collusion_suspicion` | Interaction pattern resembles coordinated manipulation |

Negative signals should not automatically prove wrongdoing. They should support risk assessment and, where appropriate, human or community review.

---

## 6. Commerce Projection Policy: Reputation Velocity

Reputation should not increase without limits.

A common attack pattern is to create many low-value transactions, fake reviews, or circular interactions to rapidly manufacture trust. This Commerce Projection research therefore considers reputation velocity limits.

Possible safeguards:

- cap how quickly reputation can improve
- weight older evidence-linked history differently from sudden new activity
- treat sudden reputation spikes as review signals
- apply stronger scrutiny to new agents with unusually fast growth
- separate transaction count from trust quality

Velocity limits can also suppress legitimate growth, so a Commerce profile that uses them needs to state the threshold, review path, and affected decision.

---

## 7. Commerce Projection Policy: Decay and Trust Aging

Reputation can become stale.

An agent with excellent history from three years ago may no longer be reliable. Ownership may change. Staff may change. Automation may change. A previously active agent may become dormant and later return under different conditions.

This Commerce Projection research explores reputation decay.

Decay may apply to:

- inactivity
- old transaction history
- outdated community endorsements
- expired credentials
- ownership changes
- long periods without evidence-linked fulfillment claims

Decay should not erase history. It should reduce the weight of old signals when evaluating current reliability.

Example directional model:

```txt
Recent records passing declared checks -> higher current relevance
Long-term consistency -> durable background trust
Old inactive history -> lower current weight
Recent disputes -> high current relevance
```

No universal decay formula is defined. Named Commerce profiles and communities may select different time windows.

---

## 8. Commerce Projection Policy: Recovery After Failure

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

This Commerce Projection research distinguishes between accidental failure, negligent behavior, and systematic abuse.

Possible recovery signals:

- prompt acknowledgment
- refund cooperation
- transparent incident explanation
- corrective action
- successful probation period
- absence of repeated failures
- community-reviewed reinstatement

Recovery should be possible after ordinary failure.

Permanent exclusion should be reserved for serious, repeated, or adjudicated abuse claims under the named application policy.

---

## 9. Compromise and Key Rotation

Agents may be compromised.

If an agent key, account, or infrastructure is compromised, reputation handling becomes difficult. A named governance process may decide how its Projection treats disclosed compromise evidence; ARC does not establish whether particular acts belong to an operator, attacker, or both.

Possible handling:

- mark the affected time window as compromised
- rotate agent keys
- preserve prior evidence-linked history with a visible warning
- require community review before restoring full trust
- temporarily limit high-risk transactions
- require owner re-verification

Reputation should not blindly transfer to a new key without review. At the same time, compromise recovery should not automatically destroy years of legitimate history.

This remains an open design problem.

---

## 10. Commerce Reputation Portability Research

Reputation portability is an open Commerce application research question.

A compatible named Commerce profile may allow a merchant to export evidence for evaluation by another backend. This may reduce switching cost, but it does not require the receiving policy to preserve a prior signal or trust history.

However, reputation portability creates risks:

- fake reputation imported from weak communities
- trust laundering across regions
- incompatible standards between communities
- inflated endorsements from captured governance systems
- over-reliance on global scores
- reduced local accountability

This research treats portable reputation as contextual evidence, not automatic authority.

A receiving community may choose to:

- accept external reputation fully
- partially weight external reputation
- require local probation
- require additional declared source or profile checks
- reject reputation from sources outside the receiving profile's accepted set

Portability remains unresolved application research. It does not establish interoperability, and a receiving profile may weight external records differently by source and declared checks.

---

## 11. Dispute Weighting

Not all disputes should affect reputation equally.

A single minor late-delivery claim should not have the same weight as an adjudicated fraud claim. A false dispute should not damage a merchant indefinitely. A pattern of similar complaints should matter more than one isolated report.

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
| `adjudicated_abusive_reporting_pattern` | Repeated or knowingly abusive reporting, when established under the named governance policy, may contribute evidence to a reporter-related reputation Projection |
| `resolved_no_fault` | Minimal or no penalty |
| `resolved_minor_issue` | Small contextual note |
| `resolved_partial_refund` | Moderate signal depending on pattern |
| `resolved_full_refund` | Stronger signal depending on evidence |
| `fraud_ruling` | Adjudicated fraud ruling; profile-defined penalty or suspension |
| `systematic_abuse_ruling` | Adjudicated abuse ruling; profile-defined ban or cross-community flag |

Dispute weighting should remain reviewable and appealable.

---

## 12. Collusion and Manipulation Heuristics

Commerce reputation profiles should assess manipulation risk; the frequency and effectiveness of attacks are not established here.

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

## 13. Commerce Discovery Policy: Discoverability vs Entrenchment

Reputation affects discovery.

If discovery systems rely too heavily on historical reputation, established merchants may dominate visibility forever. New entrants that pass the profile's declared checks may struggle to receive any first transaction. This can turn reputation into a moat rather than a trust signal.

If discovery systems promote newcomers too aggressively, Sybil attackers can exploit cold-start exposure.

This Commerce application research treats this as a continuing tension.

Possible mitigations:

- clearly labeled new-entrant slots with declared checks
- user-selectable discovery views
- visible distinction between historical trust and recent reliability
- category-specific probation
- transparent ranking explanations
- diversity indicators in discovery results
- ability to switch discovery backends

These options change newcomer exposure and incumbent ranking. A Commerce profile that adopts one should expose the resulting ranking policy.

---

## 14. Commerce Reputation Privacy Research

Reputation requires records. Commerce privacy requires restraint.

This Commerce profile should avoid exposing unnecessary personal or commercial data in Canon Events carrying reputation evidence.

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

## 15. Commerce Reputation Display

An interface should not present an unexplained summary score as a protocol judgment.

A useful interface implementing this named Commerce Projection should show the evidence and policy that produced its signal.

Example display:

```txt
Merchant: Bean & Bread

Projection context:
- Business credential check recorded under profile `commerce-local/v1`
- 214 completion claims passed that profile's record checks
- 96% of recent fulfillment claims report on-time completion
- 2 disputes in last 90 days
- No fraud ruling in the disclosed Event set
- Owner-link evidence recorded 6 months ago under the named identity profile
- Sponsored placement: No
```

This is more informative than:

```txt
Trust score: 4.8
```

All verification labels in the example denote declared application checks, not proof of real-world outcomes. A named Commerce Projection may compute summary scores, but user-facing reputation should preserve context where possible. The summary is a fold over claims and evidence, not a stored score (see [object-model.md](./object-model.md) §4).

---

## 16. Commerce Reputation Relationship to Governance

Reputation and governance are separate but connected.

Canon Events carry claims and evidence about behavior; a named reputation Projection interprets them.

Governance reviews contested behavior.

A standing input may trigger governance review. A governance decision may emit an applicable Canon Event whose payload supplies further reputation evidence.

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

Local communities understand context, but isolated reputation can create lock-in. Portable reputation may improve application portability, but may import weak or manipulated trust; interoperability remains unestablished.

### Privacy vs Auditability

Dispute review benefits from durable evidence. Privacy requires limiting what is stored and disclosed.

### Forgiveness vs Safety

Agents should recover from ordinary failure. Repeated abuse should not be forgiven indefinitely.

### New Entrants vs Sybil Resistance

New participants need a path to discovery. Attackers exploit automatic exposure.

### Simplicity vs Accuracy

Simple scores are easy to display. Contextual signals can express more inputs but are harder to explain; this document does not establish that either is more accurate.

### Human Review vs Governance Burden

Human review may catch some automated manipulation, while also increasing community workload. Its effectiveness is not established here.

### Recent Reliability vs Long-Term Consistency

Recent behavior may reflect current quality. Long-term behavior may reflect deeper trustworthiness. Both can mislead if used alone.

---

## 18. Known Unknowns

- final reputation-evidence payload schema
- whether summary scores should exist at all
- default decay windows
- category-specific weighting
- cross-community trust import rules
- privacy-preserving reputation proofs
- appeal effects on reputation history
- compromise recovery standards
- detection thresholds for collusion
- how to fund reputation review infrastructure
- how to avoid universal person-level scoring
- how to show reputation clearly without oversimplifying it

---

## 19. Current Status

This document is exploratory Commerce reputation and named-Projection research.

Executable Commerce fixtures record mock Canon Events carrying reputation evidence across selected success and failure paths, but no production reputation implementation or complete conformance profile exists.

These fixtures exercise authored cases; they do not validate a production reputation Projection.

# ARC Protocol: Glossary

> **Status:** Exploratory draft
>
> **Purpose:** Shared terminology and conceptual boundaries across ARC documents

---

## 1. Scope

This glossary is not a formal specification.

The purpose of this document is to reduce ambiguity across ARC documents by explaining how certain terms are currently used inside the ARC design discussions.

Many definitions remain incomplete and may evolve as the protocol changes.

Where uncertainty exists, the glossary should preserve that uncertainty rather than pretend the terminology is fully settled.

---

## 2. Agent

An entity that participates in ARC-compatible commerce workflows using structured communication.

An agent may represent:

- a consumer
- a merchant
- a logistics provider
- a governance participant
- a software service
- a professional workflow

ARC does not assume that all agents are fully autonomous or AI-driven.

Some agents may be simple automation tools. Others may include LLM-based reasoning or human-operated workflows.

In ARC, an agent is always owned by or accountable to a human or legal entity.

An agent cannot be more trusted than the human behind it.

---

## 3. Human Approval

Explicit human confirmation before a meaningful transaction proceeds.

Human approval is one of ARC's core constraints.

ARC does not treat fully autonomous economic execution as a default assumption.

Approval may involve:

- payment confirmation
- contract acceptance
- fulfillment authorization
- dispute settlement
- permission escalation

ARC documents distinguish between:

- recommendation
- negotiation
- approval
- execution

These should not silently collapse into a single automated step.

---

## 4. Consumer Agent

An agent primarily acting on behalf of a user or buyer.

A consumer agent may:

- parse intent
- compare offers
- filter results
- explain trade-offs
- coordinate logistics
- present approval requests

A consumer agent should not silently replace human judgment.

---

## 5. Merchant Agent

An agent representing a merchant, seller, provider, or service operator.

A merchant agent may:

- publish offers
- negotiate terms
- expose structured inventory or pricing
- respond to requests
- submit fulfillment updates

ARC does not assume that every merchant agent is trustworthy.

---

## 6. Logistics Agent

An agent coordinating transport, delivery, routing, or fulfillment movement.

A logistics agent may represent:

- local delivery
- courier systems
- ride-sharing delivery
- warehouse coordination
- pickup scheduling

Logistics trust should remain contextual and operational rather than purely reputation-based.

---

## 7. Governance

Human and community processes used to review disputes, fraud reports, suspensions, appeals, and protocol-related coordination issues.

Governance exists because cryptographic verification alone cannot resolve all commerce disputes.

ARC governance is federated by design and intentionally incomplete.

---

## 8. Reputation

A contextual trust signal derived from observed or verified behavior.

ARC does not treat reputation as:

- objective truth
- universal human worth
- permanent credibility
- a social credit system

Reputation is probabilistic, contextual, and attackable.

---

## 9. Contextual Trust

Trust evaluated within a specific context rather than as a universal score.

Context may include:

- geography
- commerce category
- transaction value
- recent activity
- dispute history
- fulfillment reliability
- community standards

ARC generally prefers contextual trust over universal scoring.

---

## 10. Discovery

The process by which agents find merchants, services, logistics providers, or other agents.

Discovery may involve:

- search
- recommendation
- ranking
- directories
- maps
- community indexes

ARC treats discovery as politically and economically important infrastructure.

---

## 11. Discovery Backend

A system or service responsible for indexing, ranking, filtering, or exposing discoverable agents.

Examples may include:

- local community registries
- map-integrated search
- reputation-weighted indexes
- category-specific directories

ARC allows multiple discovery backends rather than requiring a single global registry.

---

## 12. Sponsored Discovery

Paid visibility inside a discovery system.

ARC does not prohibit sponsored placement.

ARC does require that sponsorship be visible rather than disguised as organic ranking.

---

## 13. Verification

The process of establishing confidence that an agent, identity, credential, transaction, or event is authentic.

Verification may involve:

- identity providers
- signed records
- business review
- transaction evidence
- community confirmation
- credential checks

Verification is not equivalent to moral trustworthiness.

---

## 14. Verified Transaction

A transaction connected to evidence that the interaction occurred between identified parties.

Verification may include:

- signed records
- payment confirmation
- fulfillment evidence
- delivery confirmation
- dispute records

ARC distinguishes between verified events and unverifiable claims.

---

## 15. Fulfillment

The process of delivering what was promised in an offer.

Fulfillment may include:

- physical delivery
- digital delivery
- service completion
- appointment completion
- professional workflow completion

ARC distinguishes between:

- offer creation
- approval
- payment
- fulfillment
- dispute resolution

These are separate lifecycle stages.

---

## 16. Canonical Intent

A structured representation of a user request after parsing.

Example:

```txt
Original:
"Find me coffee and a sandwich under $10 nearby."

Canonical intent:
{
  "category": "food_order",
  "max_total_price": 10,
  "items": ["coffee", "sandwich"],
  "distance_preference": "nearby"
}
```

Canonical intent is useful but imperfect.

Parsing errors, ambiguity, manipulation, and hallucinated structure remain possible.

---

## 17. Portability

The ability to move data, identity, reputation, or workflow compatibility between systems.

ARC generally prefers portability over lock-in.

However, portability introduces risks:

- reputation laundering
- weak trust imports
- incompatible standards
- governance mismatch

Portability is useful but not automatically safe.

---

## 18. Relay

A service that forwards or intermediates communication between agents when direct peer-to-peer communication is unavailable or undesirable.

Relays are pragmatic infrastructure.

ARC does not assume that relay operators are automatically trustworthy or privacy-preserving.

---

## 19. Probation Period

A temporary period during which a new or recently restored agent may face additional scrutiny or operational limits.

The purpose is anti-fraud risk reduction, not permanent exclusion.

Probation should not become an invisible barrier to legitimate new entrants.

---

## 20. Governance Capture

A condition where governance processes become dominated, manipulated, exhausted, or distorted by a narrow group of participants.

Examples may include:

- coordinated moderation
- merchant cartels
- appeal spam
- exclusionary practices
- political pressure
- hidden sponsorship influence

ARC treats governance as attackable infrastructure.

---

## 21. Approval Fatigue

A condition where users repeatedly approve requests without meaningful review because approval interactions become too frequent, repetitive, or cognitively exhausting.

Approval fatigue weakens the value of human approval.

Reducing unnecessary approval pressure is an important design concern.

---

## 22. Trust Boundary

A point where ARC must decide what assumptions are safe.

Examples include:

- identity verification
- payment confirmation
- fulfillment evidence
- recommendation reasoning
- imported reputation
- sponsored ranking disclosure

Trust boundaries should remain visible rather than hidden behind automation.

---

## 23. Trade-off

A condition where improving one property may weaken another.

ARC repeatedly encounters trade-offs such as:

- privacy vs auditability
- openness vs Sybil resistance
- portability vs local trust
- automation vs human oversight
- discoverability vs spam resistance

ARC documents intentionally preserve unresolved trade-offs where no clear solution exists.

---

## 24. Current Status

This glossary is exploratory and incomplete.

Its purpose is to improve consistency across ARC documents while preserving conceptual flexibility during the design stage.

Future implementation work may require stricter technical terminology than this document currently provides.

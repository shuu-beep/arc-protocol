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

An entity that participates in ARC-compatible authority workflows using structured communication and signed evidence.

In the Commerce application, an agent may represent:

- a consumer
- a merchant
- a logistics provider
- a governance participant
- a software service
- a professional workflow

ARC does not assume that all agents are fully autonomous or AI-driven.

Some agents may be simple automation tools. Others may include LLM-based reasoning or human-operated workflows.

Where a claimed authority requires a principal, a named profile may require evidence linking an agent key to a human or legal entity. That evidence does not establish generalized trust, universal ownership, or legal accountability.

Two observational distinctions cut across the role-based kinds below (consumer, merchant, logistics). They describe what a particular observer can see, not new agent types in the Canon:

- **Principal (root identity) vs the agents acting under it.** The human or legal entity an agent is accountable to is its principal. One principal may run many agents, so many signatures need not mean many independent actors. An observer sees the signed Events available on its declared evidence surface, not principals; it cannot certainly count the principals behind a set of agents unless the shared root is disclosed — a limitation explored in [threat-model.md](./threat-model.md) §4.1.1 and [`examples/canon-fold-demo`](../examples/canon-fold-demo/) (scenario 11).
- **Observer-visible vs pure local workflow agent.** An agent becomes visible to an observer only when relevant evidence reaches that observer's declared surface. An agent that never produces or exposes such evidence — a purely local workflow agent — is outside that observer's evidence boundary. This is an observer-relative limitation, not a new type: an ARC implementation sees available evidence, not agents as such ([threat-model.md](./threat-model.md) §4.1.1).

---

## 3. Human Approval

Human-authored authority that gives a consequential act Current Coverage when the act occurs.

Human approval is one of ARC's core constraints.

Current Coverage may come from an exact act-specific `AUTHORIZE` or a valid scoped mandate. Signature validity does not by itself establish approval; approval does not by itself establish that authority remained in force at the act; and authority does not prove execution or outcome truth. The owning definitions are in [delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md), [event-registry.md](./event-registry.md), and the claim taxonomy in [object-model.md](./object-model.md).

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

## 4. Consumer Agent *(Commerce application vocabulary)*

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

## 5. Merchant Agent *(Commerce application vocabulary)*

An agent representing a merchant, seller, provider, or service operator.

A merchant agent may:

- publish offers
- negotiate terms
- expose structured inventory or pricing
- respond to requests
- submit fulfillment updates

ARC does not assume that every merchant agent is trustworthy.

---

## 6. Logistics Agent *(Commerce application vocabulary)*

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

Commerce governance research explores federated arrangements, but the base protocol does not require federation. Governance remains intentionally incomplete.

---

## 8. Reputation

A contextual trust signal derived by a named application Projection from claims and evidence available on its declared observer surface.

ARC does not treat reputation as:

- objective truth
- universal human worth
- permanent credibility
- a universal person-level score

Reputation is contextual, Projection-defined, and susceptible to manipulation. It is not necessarily a probability.

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

Named ARC application profiles may use contextual signals rather than a universal score; base ARC does not select one trust policy.

---

## 10. Discovery *(Commerce application vocabulary)*

The process by which agents find merchants, services, logistics providers, or other agents.

Discovery may involve:

- search
- recommendation
- ranking
- directories
- maps
- community indexes

Discovery is Commerce application infrastructure.

---

## 11. Discovery Backend *(Commerce implementation vocabulary)*

A system or service responsible for indexing, ranking, filtering, or exposing discoverable agents.

Examples may include:

- local community registries
- map-integrated search
- reputation-weighted indexes
- category-specific directories

The Commerce application research allows multiple discovery backends rather than requiring a single global registry; this is not a base-protocol requirement.

---

## 12. Sponsored Discovery *(Commerce application-policy vocabulary)*

Paid visibility inside a discovery system.

The explored Commerce application policy requires sponsorship to be visible rather than disguised as organic ranking. This is not a base-protocol rule.

---

## 13. Verification

The process of checking a claim under a declared verification boundary.

Verification may involve:

- identity providers
- signed records
- business review
- transaction evidence
- community confirmation
- credential checks

External Record Verification checks a record's cryptographic, structural, or declared semantic properties; it does not by itself prove authority, execution, external occurrence, or outcome truth. Stronger recomputability claims require their own evidence and disclosure conditions. [object-model.md](./object-model.md) owns the claim taxonomy.

---

## 14. Verified Transaction *(Commerce application vocabulary)*

A Commerce transaction connected to records that can be checked under a declared verification boundary. The label must not imply that the external interaction or outcome was proved.

Verification may include:

- signed records
- payment confirmation
- fulfillment evidence
- delivery confirmation
- dispute records

Record verification establishes properties of the record, not the truth of its external referent.

---

## 15. Fulfillment *(Commerce application vocabulary)*

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

## 16. Canonical Intent *(Application vocabulary)*

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

Some ARC application research explores portability as an alternative to lock-in; base ARC does not require it.

However, portability introduces risks:

- reputation laundering
- weak trust imports
- incompatible standards
- governance mismatch

Portable data does not automatically satisfy a receiving profile's identity, evidence, or manipulation-risk criteria.

---

## 18. Relay

A service that forwards or intermediates communication between agents when direct peer-to-peer communication is unavailable or undesirable.

Relays are pragmatic infrastructure.

ARC does not assume that relay operators are automatically trustworthy or privacy-preserving.

---

## 19. Probation Period *(Application-policy vocabulary)*

A temporary period during which a new or recently restored agent may face additional scrutiny or operational limits.

The purpose is anti-fraud risk reduction, not permanent exclusion.

Probation should not become an invisible barrier to legitimate new entrants.

---

## 20. Governance Capture *(Governance research vocabulary)*

A condition where governance processes become dominated, manipulated, exhausted, or distorted by a narrow group of participants.

Examples may include:

- coordinated moderation
- merchant cartels
- appeal spam
- exclusionary practices
- political pressure
- hidden sponsorship influence

The Commerce/community governance research treats governance processes as attackable application infrastructure.

---

## 21. Approval Fatigue *(Application UX vocabulary)*

A condition where users repeatedly approve requests without meaningful review because approval interactions become too frequent, repetitive, or cognitively exhausting.

Approval fatigue weakens the value of human approval.

Reducing unnecessary approval pressure is an important design concern.

---

## 22. Trust Boundary

A boundary where a named profile or implementation changes its declared assumptions.

Examples include:

- identity verification
- payment confirmation
- fulfillment evidence
- recommendation reasoning
- imported reputation
- sponsored ranking disclosure

Assumptions relied on by a claim should be disclosed to the relevant observer. ARC cannot guarantee that an opaque deployment exposes every boundary.

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

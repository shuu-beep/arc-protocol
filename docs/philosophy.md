# ARC Protocol: Philosophy

> **Status:** Historical origin document — founding argument, commerce-framed
> **Purpose:** Preserve the historical philosophical foundation of the ARC Protocol
> For a quick overview, see the [README](../README.md).
>
> **Read this as ARC's origin argument, not its current definition.** It was
> written when commerce *was* the project, and it argues everything through
> commerce. The protocol has since been stated independently of it: the current
> spine is **human-rooted authority, scoped delegation, and recomputation over
> disclosed signed evidence**, with Commerce as ARC's first implementation profile, not its definition
> ([README §1](../README.md#1-the-multi-principal-problem)). The claims below are preserved as
> historical context, not current protocol requirements. Current documents govern
> where this origin argument and the present protocol boundary differ.

---

## 1. Why This Exists

ARC began as a Commerce-first exploration based on this question:

> If AI agents become the new interface of commerce, who should own the infrastructure behind them?

The founding proposal favored infrastructure not controlled by one corporation. This document records that argument.

---

## 2. Founding Attention-Economy Concern

The founding argument observed that much of digital commerce relies on attention.

It described platforms competing for attention and conversion, and advertising that attempts to influence human attention and emotion.

This produced familiar risks:

- Cognitive vulnerabilities could be targeted through urgency, scarcity, and social proof.
- Capital-rich actors could buy visibility, seed reviews, or pay for endorsements.
- Advertising and intermediary costs could shape which products become visible and how they are priced.

Agents may be less susceptible than humans to some forms of emotional persuasion. A countdown timer or influencer endorsement need not affect an agent as it affects a person. An agent can instead compare structured data such as price, availability, reputation, delivery time, and refund history.

That difference may weaken some attention-based tactics. It does not make the agent independent of advertising or platform influence. The threat may shift from emotional persuasion to ranking influence, recommendation bias, and agent-level optimization.

---

## 3. The Risk: Centralized Agent Bias

ARC treats centralized agent bias as a plausible threat model, not a universal outcome.

When the same operator controls an agent's discovery, ranking, and recommendation surface, its commercial incentives may shape what the agent can observe. If sponsored placement, ranking provenance, recommendation inputs, fees, or comparable alternatives are hidden, a personal agent may be unable to determine from disclosed records whether a result serves the user's stated intent or the platform's business model.

An agent may be less responsive to emotional prompts while remaining dependent on ranking inputs and implementation policy.

Consider the scenario:

> A user asks their agent: "Find me the best sandwich nearby under $10."

If that agent runs on a closed system whose operator has commercial relationships with particular merchants, those relationships could influence the ranking without being visible to the user or independently inspectable by the agent.

A closed recommendation system may therefore transfer platform dependence from the human interface to the agent interface. This is an incentive and observability risk, not a claim that every platform will exploit it or that every agent will produce biased results.

The founding Commerce proposal responded to this risk and compared itself with earlier open-protocol efforts such as ActivityPub, Matrix, Nostr, Farcaster, and AT Protocol. ARC's current protocol boundary is authority over consequential agent-mediated actions; Commerce remains the flagship application.

---

## 4. Five Founding Commerce Beliefs

The founding proposal stated five beliefs. They are historical application and governance preferences unless restated as current requirements elsewhere.

**1. Agents may negotiate, but humans grant authority.**
The founding application defaulted to fresh human confirmation. Current ARC also represents scoped mandates and agent-to-agent delegation, provided each consequential act traces to a current human-authored `AUTHORIZE` and is covered under the named Projection/profile from disclosed inputs.

**2. The shared authority layer should be open.**
The founding proposal favored a forkable, inspectable, community-governed authority layer. Openness is not a base-protocol deployment-topology requirement.

**3. Application reputation should be separable from advertising.**
The founding Commerce policy favored evidence-linked transaction history, refund records, dispute records, and contextual standing over advertising spend in merchant visibility.

**4. Local communities should be able to define governance policy.**
The founding application favored local handling of fraud reports, disputes, and suspension. This was an application governance preference, not a universal protocol requirement.

**5. Infrastructure should remain implementation-neutral.**
Centralized services, federated or community-operated systems, and shared ledgers may each fit different deployments. ARC does not require one topology; protocol semantics and human authority boundaries must remain intact whichever infrastructure is used.

---

## 5. Founding Commerce Application Policies

Its founding Commerce argument proposed three application policies intended to make recommendation, sponsorship, and discovery choices more inspectable:

### 5.1 Recommendation Records

In that founding Commerce model, every recommendation made by a consumer agent was to produce a readable record explaining the selection criteria.

Example:
```
Selected: Merchant A
Reason: Budget constraint met ($9.50 < $15.00), reputation score 4.90 (top 3% in community),
        estimated delivery 28 min (within 30 min requirement), offer signature checked.
Rejected: Merchant B — delivery time 42 min (exceeded constraint)
Rejected: Merchant C — reputation score 3.2 (below user threshold)
```

Under that proposed application policy, users were to be able to inspect, question, and override a recommendation.

A log is necessary for auditability, but not sufficient. If users cannot understand, verify, or act on it, a log may provide false assurance. Whether people have usable tools and sufficient context to evaluate agent reasoning remains an open design problem.

One exploratory direction is intent-based delegation: users might define constraints such as budget limits, reputation thresholds, and category restrictions, then review audit records rather than approve every routine prompt. ARC does not treat this as a preferred model or a substitute for human authority; it records the tension that excessive prompts may also weaken meaningful attention.

### 5.2 Explicit Sponsored Weight

The founding Commerce model did not prohibit commercial promotion.

It proposed that commercial influence be explicit, machine-readable, and visible to both humans and agents.

The proposed policy required sponsored weighting to be declared in the offer payload:

```json
{
  "offer_id": "offer_042",
  "merchant_agent_id": "merchant_xyz",
  "total_price": 9.80,
  "sponsored_weight": 0.12,
  "sponsored_disclosed": true
}
```

Under that proposed Commerce policy, hidden algorithmic nudges were treated as application violations. Sponsorship was permitted; concealment was not.

### 5.3 Multi-Tenant Open Discovery

The founding Commerce design argued that no single entity should control the discovery index.

It proposed that any community, merchant association, or individual could operate their own merchant directory, reputation index, or local commerce registry. Implementations could allow users to switch between discovery backends. This could reduce dependence on one index, but it would not prevent concentration unless usable alternatives actually existed.

---

## 6. Founding Commerce Flow

The founding application sketched this flow:

```
Agent negotiation
      ↓
Human confirmation (founding default)
      ↓
Payment execution
      ↓
Application reputation record
```

Operational latency was assigned to databases and APIs. Under a declared security profile, signatures authenticated record bytes to keys; they did not prove outcomes. Human authority remained the design constraint.

The historical claim was narrower than a universal reputation system: a named Projection could derive contextual standing from declared evidence. Implementations may cache derived values only under the cache discipline defined by current documentation.

---

## 7. What We Are Not Claiming

ARC Protocol does not claim that:

- Advertising will disappear in the agent economy
- Decentralization solves all trust problems
- Open protocols are automatically fair or safe
- This design is complete or production-ready

The founding argument claimed only that infrastructure ownership and inspectability were relevant design questions. Current ARC requirements are defined by the README, Canon, registry, object model, and conformance documents.

---

## 8. Conclusion

The founding concern was that agent-mediated commerce could shift manipulation from user-interface cues to ranking and recommendation systems. The proposed response emphasized inspectability, replaceability, and human authority. This document records that origin; current ARC is defined by the authority-protocol documentation.

> Note: ARC's ideas may have implications beyond commerce, including information discovery and social curation. Those speculative ideas are kept outside this historical Commerce-origin document; Commerce is ARC's flagship application, not its definition.

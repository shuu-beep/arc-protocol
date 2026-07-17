# ARC Protocol: Philosophy

> **Status:** Draft v1.0 — founding argument, commerce-framed
> **Purpose:** Philosophical foundation of the ARC Protocol
> For a quick overview, see the [README](../README.md).
>
> **Read this as ARC's origin argument, not its current definition.** It was
> written when commerce *was* the project, and it argues everything through
> commerce. The protocol has since been stated independently of it: the current
> spine is **human-approved delegation, portable authority, and recomputable
> audit**, with commerce as ARC's first implementation, not its definition
> ([README §1](../README.md#1-what-arc-is)). Nothing below is retracted — the
> attention-economy critique and the design axioms still hold — but where this
> document says "commerce," read "the first application of a general authority,
> approval, and audit layer for AI agents."

---

## 1. Why This Exists

The internet was built for humans.

But the next layer of commerce may be operated by agents.

ARC Protocol starts from a simple question:

> If AI agents become the new interface of commerce, who should own the infrastructure behind them?

Our answer: no single corporation should.

This document explains why — and what we propose instead.

---

## 2. Agents May Change the Attention Economy

For roughly two decades, much of digital commerce has relied on attention.

Platforms competed to stop your scroll, capture your eye, trigger your emotion, and convert your impulse into a purchase. Much of modern advertising assumes that human attention and emotion can be influenced.

This produced familiar risks:

- Cognitive vulnerabilities could be targeted through urgency, scarcity, and social proof.
- Capital-rich actors could buy visibility, seed reviews, or pay for endorsements.
- Advertising and intermediary costs could shape which products become visible and how they are priced.

Agents may be less susceptible than humans to some forms of emotional persuasion. A countdown timer or influencer endorsement need not affect an agent as it affects a person. An agent can instead compare structured data such as price, availability, reputation, delivery time, and refund history.

That difference may weaken some attention-based tactics. It does not make the agent independent of advertising or platform influence. The threat may shift from emotional persuasion to ranking influence, recommendation bias, and agent-level optimization.

---

## 3. The Risk: Centralized Agent Bias

ARC treats centralized agent bias as a plausible threat model, not a universal outcome.

When the same operator controls an agent's discovery, ranking, and recommendation surface, its commercial incentives may shape what the agent can observe. If sponsored placement, ranking provenance, recommendation inputs, fees, or comparable alternatives are hidden, a personal agent cannot independently verify whether a result serves the user's stated intent or the platform's business model.

**An agent can be emotionally indifferent yet algorithmically dependent.**

Consider the scenario:

> A user asks their agent: "Find me the best sandwich nearby under $10."

If that agent runs on a closed system whose operator has commercial relationships with particular merchants, those relationships could influence the ranking without being visible to the user or independently inspectable by the agent.

A closed recommendation system may therefore transfer platform dependence from the human interface to the agent interface. This is an incentive and observability risk, not a claim that every platform will exploit it or that every agent will produce biased results.

ARC Protocol is a response to this risk.

ARC is adjacent to earlier open protocol efforts such as ActivityPub, Matrix, Nostr, Farcaster, and AT Protocol, but its focus is narrower: human-approved economic coordination between agents. The goal is not to replace social protocols or communication networks, but to explore what open infrastructure might look like when agents negotiate commerce on behalf of humans.

---

## 4. Our Five Beliefs

ARC Protocol is built on five foundational beliefs:

**1. Agents may negotiate, but humans must approve.**
AI should reduce friction, not remove sovereignty. Every significant economic action should require explicit human confirmation. Agents are assistants, not autonomous economic actors.

Manual approval is the default and recommended behavior. A future implementation may explore explicitly pre-authorized, low-risk approval rules within user-defined thresholds, provided meaningful economic actions still require explicit confirmation and every action remains auditable. Approval fatigue, and the risk that convenience erodes oversight, remains an open design tension.

**2. The shared authority layer should be open.**
If agent-to-agent coordination becomes the next layer of the internet, the authority and approval layer behind it should be forkable, inspectable, and community-governed — not owned by a single corporation.

**3. Reputation matters more than advertising.**
In an agent economy, trust is the primary competitive asset. Verified transaction history, refund rates, dispute records, and community standing should determine merchant visibility — not advertising spend.

**4. Local communities should govern trust.**
Fraud detection, dispute resolution, and agent suspension should be handled by the communities closest to the commerce — not by a distant platform with misaligned incentives.

**5. Infrastructure should remain implementation-neutral.**
Centralized services, federated or community-operated systems, and shared ledgers may each fit different deployments. ARC does not require one topology; protocol semantics and human authority boundaries must remain intact whichever infrastructure is used.

---

## 5. ARC's Design Axioms Against Manipulation

To prevent the agent economy from reproducing the failures of the attention economy, ARC establishes three protocol-level design constraints:

### 5.1 Human-Auditable Recommendation Logs

Every recommendation made by a consumer agent must produce a readable, tamper-evident log explaining the selection criteria.

Example:
```
Selected: Merchant A
Reason: Budget constraint met ($9.50 < $15.00), reputation score 4.90 (top 3% in community),
        estimated delivery 28 min (within 30 min requirement), signed offer verified.
Rejected: Merchant B — delivery time 42 min (exceeded constraint)
Rejected: Merchant C — reputation score 3.2 (below user threshold)
```

Agents must not be black boxes. Users must be able to inspect, question, and override any recommendation.

A log is necessary for auditability, but not sufficient. If users cannot understand, verify, or act on it, a log may provide false assurance. Whether people have usable tools and sufficient context to evaluate agent reasoning remains an open design problem.

One exploratory direction is intent-based delegation: users might define constraints such as budget limits, reputation thresholds, and category restrictions, then review audit records rather than approve every routine prompt. ARC does not treat this as a preferred model or a substitute for human authority; it records the tension that excessive prompts may also weaken meaningful attention.

### 5.2 Explicit Sponsored Weight

ARC does not prohibit commercial promotion.

ARC requires commercial influence to be explicit, machine-readable, and visible to both humans and agents.

Any sponsored weighting must be declared in the offer payload:

```json
{
  "offer_id": "offer_042",
  "merchant_agent_id": "merchant_xyz",
  "total_price": 9.80,
  "sponsored_weight": 0.12,
  "sponsored_disclosed": true
}
```

Hidden algorithmic nudges are treated as protocol violations. Sponsorship is permitted; concealment is not.

### 5.3 Multi-Tenant Open Discovery

No single entity should control the discovery index.

Any community, merchant association, or individual may operate their own merchant directory, reputation index, or local commerce registry. Implementations can allow users to switch between discovery backends. This can reduce dependence on one index, but it does not prevent concentration unless usable alternatives actually exist.

---

## 6. The Core Flow

ARC's architecture follows a simple principle:

```
Agent negotiation
      ↓
Human confirmation
      ↓
Payment execution
      ↓
Community-verifiable reputation
```

Speed lives in databases and APIs.
Trust lives in cryptographic signatures and community records.
Sovereignty lives with humans.

ARC is closer to an **evidence-projection system** than a reputation-score system: there is no number to optimize or game. Standing is a contextual, reviewable, fallible fold over signed evidence — completion records, credentials, dispute outcomes, counterparty diversity — recomputed on demand and never stored.

---

## 7. What We Are Not Claiming

ARC Protocol does not claim that:

- Advertising will disappear in the agent economy
- Decentralization solves all trust problems
- Open protocols are automatically fair or safe
- This design is complete or production-ready

We claim only that **the infrastructure question matters**, and that answering it with closed, corporate-controlled systems creates a risk of reproducing familiar harms in less inspectable forms.

ARC is one attempt to propose a different answer.

---

## 8. Conclusion

The attention economy exploited human psychology.
The agent economy may exploit human trust in agents.

The defense against both is the same: **transparency, openness, and human sovereignty**.

ARC Protocol is a small experiment toward that principle.

Not a startup. Not a platform. A proposal.

> *"Agents should help people compare, negotiate, and coordinate — not replace human sovereignty."*

> Note: ARC's ideas may have implications beyond commerce, including information discovery and social curation. Those speculative ideas are kept outside the core philosophy document to keep this document focused on commerce — ARC's flagship application, not its definition.

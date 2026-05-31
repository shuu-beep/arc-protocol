# ARC Protocol: Governance

> **Status:** Exploratory draft
> **Purpose:** Community governance model, dispute resolution philosophy, and governance limits
> For system architecture, see [architecture.md](./architecture.md).
> For payment and legal boundaries, see [liability-boundaries.md](./liability-boundaries.md).

---

## 1. Why Governance Matters

Trust cannot be enforced by code alone.

Cryptographic signatures verify that an offer came from a specific key. They do not verify that the merchant behind that key is honest, that the food was edible, that the delivery driver did not steal the package, or that a dispute report is truthful.

Human judgment is irreplaceable in commerce. ARC's governance model exists to organize that judgment — to give communities a structured way to handle fraud reports, review disputes, and maintain the integrity of the reputation layer.

Without governance, reputation becomes gameable. Without community enforcement, bad actors can accumulate fake trust and exploit it. Without a clear appeal process, suspension becomes arbitrary and abusive.

ARC treats governance as a first-class design concern, not an afterthought.

But governance is not magic. It is labor, process, judgment, funding, and accountability under adversarial pressure.

---

## 2. Core Governance Principles

**Local over central.**
Communities closest to the commerce may be better positioned to understand context than a distant algorithm or corporate trust-and-safety team. This is an aspirational design position, not a guarantee that local governance will be fair, sustainable, or capture-resistant.

**Transparent process.**
Every governance decision — warning, suspension, expulsion — should produce a reviewable record. Participants should be able to understand why a decision was made.

**Right to appeal.**
No suspension should be final without an appeal path. Mistakes happen. Malicious reports happen. The system must allow correction.

**Proportional response.**
Penalties should match the severity of the violation. A first-time late delivery is not equivalent to systematic fraud. The governance model should reflect that.

**No single point of control.**
No single corporation, individual, or community should have unilateral authority over the entire network. Governance is federated by design.

**Limited authority.**
ARC governance may affect ARC-compatible reputation, discovery visibility, warnings, or local participation status. It does not replace courts, payment-provider dispute systems, consumer protection law, professional regulators, or public legal authority.

---

## 3. Governance Layers

ARC governance operates at multiple levels:

### 3.1 Local Community

Scope: A defined geographic area or commerce category (e.g., "Seoul Gangnam food delivery", "Busan logistics providers").

Responsibilities:
- First-line fraud report review
- Initial dispute handling
- Warning and temporary suspension decisions
- Community reputation adjustments

Possible composition:
- Active verified merchants
- Active verified consumers
- Elected or rotating community moderators
- Independent reviewers where available

Open questions:
- Who qualifies as a community member?
- How are conflicts of interest disclosed?
- How are reviewers rotated or removed?
- How are inactive or captured communities detected?

### 3.2 Regional or National Community

Scope: Broader geography or cross-community disputes.

Responsibilities:
- Appeals from local community decisions
- Cross-community fraud patterns
- Protocol compliance review
- Coordination between local communities

### 3.3 Protocol Maintainers

Scope: The open-source protocol itself.

Responsibilities:
- Protocol specification changes
- Security vulnerability response
- Governance model updates
- Compatibility and interoperability standards

Protocol maintainers govern the rules, not the participants. They do not have authority over individual merchant suspensions or local disputes unless they also operate a separate community with its own disclosed rules.

---

## 4. Dispute Resolution Process

### 4.1 Trigger Conditions

A dispute may be initiated when:

- A consumer reports a transaction as fraudulent, incomplete, unsafe, or significantly misrepresented
- A merchant reports a consumer for payment fraud or false dispute claims
- A logistics agent reports a merchant for unsafe or false delivery conditions
- A community member reports suspicious agent behavior
- A discovery backend or reputation layer flags suspicious patterns for human review

### 4.2 Process Flow

```txt
User submits dispute report
          ↓
Transaction log retrieved and verified where possible
          ↓
Signed offer records checked
          ↓
Both parties notified and given response period
          ↓
Conflict-of-interest check for reviewers
          ↓
Community moderators review evidence
          ↓
Community decision issued with reasoning
          ↓
Penalty applied if justified and within scope
          ↓
Appeal window opens
          ↓
Decision finalized or modified
```

### 4.3 Evidence Standards

Potentially useful evidence includes:

- Signed offer records
- Approved transaction records
- Delivery confirmation or failure logs
- Payment-provider status where available
- Communication logs between agents where retained
- Prior reputation history
- Pattern evidence across related reports

Weak or insufficient evidence may include:

- Unsigned claims
- Screenshots without verifiable source
- Anonymous accusations without corroborating records
- AI-generated summaries without underlying records
- Suspicious pattern signals without human review

A signed record is evidence of attribution. It is not automatic proof of honesty, safety, legality, or user understanding.

### 4.4 Decision Timeline

| Stage | Example Duration |
|-------|------------------|
| Report submission | Immediate |
| Evidence collection | 48 hours |
| Moderator review | 72 hours |
| Decision issued | Day 5 |
| Appeal window | 7 days |
| Final decision | Day 12 |

These are illustrative windows, not a universal rule. Communities may need different timelines depending on transaction value, urgency, evidence quality, local law, and reviewer availability.

### 4.5 Governance Overload

A governance process can fail even when its rules are reasonable.

Overload may occur when:

- many disputes arrive at once
- bad-faith actors file repeated marginal reports
- reviewers lack time or expertise
- appeals accumulate faster than decisions
- evidence is too sensitive or complex to review quickly
- local communities lack enough independent participants

If timely review cannot be provided, provisional penalties should be limited, reversible where possible, and clearly labeled as unresolved. ARC should not pretend that slow governance is equivalent to fair governance.

---

## 5. Penalty Scale

Penalties should be proportional to violation severity, evidence quality, and history.

| Level | Penalty | Trigger |
|-------|---------|---------|
| 1 | Warning + contextual reputation note | Minor first violation or uncertain concern |
| 2 | Reputation confidence reduction | Repeated minor issues or unresolved pattern |
| 3 | Temporary suspension | Confirmed serious failure or high-risk unresolved pattern |
| 4 | Extended suspension | Repeated fraud, serious harm, or non-cooperation |
| 5 | Community ban | Systematic verified abuse |
| 6 | Cross-community flag | Extreme cases with cross-community impact and appeal path |

Reputation recovery is possible after suspension periods. Agents are not permanently marked without opportunity for rehabilitation except in cases of serious, repeated, or verified malicious behavior.

Serious penalties should be reviewable and appealable. A community should avoid treating suspicion, anomaly detection, or competitive accusations as proof.

In object-model terms, each penalty here is recorded as an `ADJUDICATE` event (`gov.*`) — the only event type that may change a party's standing in the commons (see [authority-and-conflict.md](./authority-and-conflict.md) §5–§6, [event-registry.md](./event-registry.md)).

---

## 6. Anti-Gaming Measures

The reputation and governance system must resist manipulation.

### 6.1 Sybil Resistance

Fake identity farming to accumulate positive reputation or submit false dispute reports is a primary attack vector.

Possible mitigations:
- Identity provider verification for agent creation
- Business or professional verification where relevant
- New-agent probation periods
- Temporary anti-fraud risk controls
- Reputation velocity limits
- Community review of sudden reputation spikes
- Cross-community analysis of coordinated reputation patterns

AI-assisted Sybil attacks may increase the speed and scale of fake identity farming. Automated agents could build apparently legitimate histories before coordinating fraud, narrowing the window for review.

These signals should support human review rather than produce automatic penalties by themselves.

### 6.2 Collusion Detection

Groups of agents may submit coordinated false reviews, fake transactions, circular endorsements, or false dispute reports.

Possible mitigations:
- Reputation events from related agents are weighted differently
- Statistical anomaly detection on review patterns
- Review triggers for circular transaction clusters
- Attention to low-value reputation farming
- Community review of suspicious review or dispute clusters

Collusion detection is not solved. False positives are expected. Review processes should not punish participants solely because an automated detector finds a pattern.

### 6.3 False Dispute Abuse

Users, competitors, or coordinated groups may submit fraudulent dispute reports to harm a merchant, extract refunds, or exhaust moderators.

Possible mitigations:
- Evidence standards require verifiable records
- Serial false reporters may face reputation penalties
- Reviewers may flag coordinated reporting bursts
- Provisional penalties should remain reversible where evidence is incomplete
- Accused parties should have a response opportunity

### 6.4 Governance Capture

A community governance process can be captured or obstructed by coordinated participants, including competing merchants, dominant local actors, donor influence, moderator cliques, or organized bad-faith groups.

Mitigations worth exploring include:

- moderator term limits and rotation
- diversity rules that reduce control by a single affiliated group
- conflict-of-interest disclosures
- anomaly review when dispute activity spikes from a narrow set of participants
- periodic review of whether active governance participants reflect the community they serve
- appeal paths outside the local community for serious decisions

No governance model is fully resistant to coordinated capture. ARC's response is procedural transparency, review, and diversity, not a claim of technical impossibility.

---

## 7. Community Self-Governance

ARC is designed so that communities can adapt governance rules to local needs.

A community may:

- Set its own penalty thresholds within protocol minimums
- Define local reputation metrics relevant to its commerce type
- Create local identity requirements, such as business registration review
- Establish community-specific dispute resolution processes
- Invite or remove merchants from its local directory within disclosed rules
- Choose stricter or looser discovery defaults where users can see the implications

A community may not:

- Override protocol-level security requirements
- Remove the human approval requirement from transactions
- Hide sponsorship or paid ranking as neutral discovery
- Mandate exclusive use of a specific payment provider as a protocol requirement
- Discriminate based on protected characteristics
- Represent community decisions as legal judgments unless a proper legal process exists

---

## 8. Non-Profit Governance Rationale

ARC is designed as non-profit open-source infrastructure.

The reasoning is straightforward:

If agent-to-agent commerce becomes a significant layer of the economy, the governance of that layer has enormous power. It determines who can participate, whose disputes are resolved fairly, whose reputation is protected, and whose is destroyed.

That power should not be held by a single corporation with shareholders and profit motives.

It should be held by accountable, transparent, and replaceable community or public-interest structures where possible.

This is an aspirational position based on observed platform failures, not a guarantee against capture, bureaucracy, donor influence, or operational failure.

ARC proposes a different structure. Not because it is easy, and not because non-profit status solves governance, but because closed platform governance creates risks worth challenging.

### 8.1 The Sustainability Problem

Community governance depends on time spent reviewing fraud, mediating disputes, maintaining fair procedures, and preserving appeal paths. ARC does not yet have a complete answer for how that work remains sustainable as a community grows.

Possible approaches to study include:

- modest dispute-processing fees with transparent handling rules
- optional community membership contributions
- paid mediation for complex disputes while routine review remains community-led
- public-interest grants
- cooperative funding
- merchant association support
- limited volunteer moderation with strict scope boundaries

These are open design questions, not a protocol treasury or mandatory compensation system.

ARC should not assume unpaid moderation can scale under adversarial pressure.

---

## 9. Current Status

ARC governance is currently a design proposal, not an operating system.

No governance community currently exists. No moderators have been appointed. No dispute resolution process is active.

This document describes an intended model for future experimentation. It does not prove that community governance is fair, scalable, legally sufficient, or sustainable.

Contributions to the governance design are welcome. See [CONTRIBUTING.md](../CONTRIBUTING.md).

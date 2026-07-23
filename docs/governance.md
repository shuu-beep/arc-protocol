# ARC Protocol: Commerce and Community Governance Research

> **Status:** Exploratory draft
> **Purpose:** Commerce/community institution research, dispute resolution philosophy, and governance limits
> For system architecture, see [architecture.md](./architecture.md).
> For payment and legal boundaries, see [liability-boundaries.md](./liability-boundaries.md).

---

## 1. Why Governance Matters

Under a declared security profile, a signature can support a check that a key signed the covered offer bytes. It does not establish who controlled the key, covering authority, merchant honesty, product quality, delivery conduct, or dispute truth.

Human review can add context that Event records alone do not supply. This application-governance research explores how communities could organize that review — handling fraud reports, reviewing disputes, and maintaining a named reputation Projection.

Governance is one proposed way to review manipulation claims and provide appeals. It does not eliminate reputation gaming, abusive participation, capture, or arbitrary decisions.

Governance requires labor, process, judgment, funding, and accountability under adversarial pressure.

---

## 2. Possible Commerce-Profile Governance Principles

**Local review.**
Local review may add contextual information while also introducing capture, consistency, and sustainability risks. This is an application research choice, not a guarantee or base-protocol topology.

**Reviewable process.**
A named Commerce governance profile may require warning, suspension, and expulsion decisions to produce records reviewable by affected parties on its declared evidence surface. The base protocol does not require a public surface.

**Appeal policy.**
A profile may define an appeal and correction path for suspension decisions. Base ARC does not mandate one.

**Response policy.**
A profile may distinguish response levels by its declared findings and severity rules.

**Topology remains a profile choice.**
This application research explores local and federated institutions; base ARC mandates no governance topology.

**Limited authority.**
A named Commerce governance profile may affect its reputation Projection, discovery visibility, warnings, or local participation status. Its decisions are evidence and standing decisions, not proof of execution or legal truth, and do not replace courts, payment-provider dispute systems, consumer protection law, professional regulators, or public legal authority.

---

## 3. Commerce Governance Institutions and Project Governance

This application research explores multiple institutional levels; they are not a universal protocol topology:

### 3.1 Local Community

Scope: A defined geographic area or commerce category (e.g., "Seoul Gangnam food delivery", "Busan logistics providers").

Responsibilities:
- First-line fraud report review
- Initial dispute handling
- Warning and temporary suspension decisions
- Community reputation adjustments

Possible composition:
- Active merchants whose declared application checks pass
- Active consumers whose declared application checks pass
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
- Named profile and application-policy compatibility review
- Coordination between local communities

### 3.3 Protocol and Conformance Stewardship

Scope: The open-source protocol itself.

Responsibilities:
- Protocol specification changes
- Security vulnerability response
- Governance model updates
- Compatibility and interoperability standards

Project maintainers steward the specification and conformance documents, not deployment participants. A conformance claim names its profile and version. Maintainers do not have authority over individual merchant suspensions or local disputes unless they also operate a separate community with its own disclosed rules.

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
Transaction log retrieved and External Record Verification applied where evidence is available
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
- Authorization records, distinguished from execution and outcome evidence
- Delivery confirmation or failure records treated as external claims
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

If timely review cannot be provided, a named profile may limit provisional penalties, make them reversible where possible, and label them unresolved. Slow process does not by itself establish fairness.

---

## 5. Penalty Scale

Penalties should be proportional to violation severity, evidence quality, and history.

| Level | Penalty | Trigger |
|-------|---------|---------|
| 1 | Warning + contextual reputation note | Minor first violation or uncertain concern |
| 2 | Reputation confidence reduction | Repeated minor issues or unresolved pattern |
| 3 | Temporary suspension | Serious-failure ruling or high-risk unresolved pattern under the named policy |
| 4 | Extended suspension | Repeated adverse rulings, adjudicated serious harm, or non-cooperation |
| 5 | Community ban | Systematic abuse upheld under the named governance policy |
| 6 | Cross-community flag | Profile-defined severe ruling with cross-community scope and an appeal path |

Reputation recovery is possible after suspension periods. Agents are not permanently marked without opportunity for rehabilitation except for serious or repeated abuse upheld under the named governance policy.

Serious penalties should be reviewable and appealable. A community should avoid treating suspicion, anomaly detection, or competitive accusations as proof.

In object-model terms, each penalty here is recorded as an `ADJUDICATE` event (`gov.*`) — the only event type that may change a party's standing in the commons (see [authority-and-conflict.md](./authority-and-conflict.md) §5–§6, [event-registry.md](./event-registry.md)).

---

## 6. Candidate Anti-Gaming Measures

A named Commerce reputation or governance profile may apply measures intended to detect or constrain manipulation. Their effectiveness is not established here.

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
- Standing inputs from related agents are weighted differently under the named Projection
- Statistical anomaly detection on review patterns
- Review triggers for circular transaction clusters
- Attention to low-value reputation farming
- Community review of suspicious review or dispute clusters

Collusion detection is not solved. False positives are expected. Review processes should not punish participants solely because an automated detector finds a pattern.

### 6.3 False Dispute Abuse

Users, competitors, or coordinated groups may submit fraudulent dispute reports to harm a merchant, extract refunds, or exhaust moderators.

Possible mitigations:
- Evidence standards require records that pass declared External Record Verification checks
- A dismissed or unsupported report causes no automatic reporter penalty. Repeated or knowingly abusive reporting may be considered only after a reviewable governance finding.
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

This Commerce governance research allows communities to adapt application rules to local needs.

A community may:

- Set its own penalty thresholds within a named Commerce governance profile
- Define local reputation metrics relevant to its commerce type
- Create local identity requirements, such as business registration review
- Establish community-specific dispute resolution processes
- Invite or remove merchants from its local directory within disclosed rules
- Choose stricter or looser discovery defaults where users can see the implications

A community may not:

- Misstate compliance with the security requirements of its declared profile
- Claim conformance under a profile while accepting a consequential act that lacks Current Coverage; coverage may be exact act-specific authority or a valid scoped mandate
- Hide sponsorship or paid ranking where the named Commerce discovery policy requires disclosure
- Mandate exclusive use of a specific payment provider as a protocol requirement
- Discriminate based on protected characteristics
- Represent community decisions as legal judgments unless a proper legal process exists

---

## 8. Project and Research Stewardship Rationale

This section concerns stewardship of the ARC specification and research project, not protocol Event semantics or a mandatory deployment topology.

Companies, merchants, and platforms may experiment with or build against the current ARC drafts; no adoption is established. Future specification stewardship remains an open project question rather than a base-protocol topology rule.

No project-stewardship model is specified or validated. Stewardship and deployment governance remain separate questions.

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

This research does not assume unpaid moderation will scale under adversarial pressure.

---

## 9. Current Status

This Commerce/community governance model is currently a research proposal, not an operating system or base-protocol topology.

No governance community currently exists. No moderators have been appointed. No dispute resolution process is active.

This document describes an intended model for future experimentation. It does not prove that community governance is fair, scalable, legally sufficient, or sustainable.

Contributions to the governance design are welcome. See [CONTRIBUTING.md](../CONTRIBUTING.md).

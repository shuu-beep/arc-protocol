# ARC Protocol: Governance

> **Status:** Draft v1.0
> **Purpose:** Community governance model and dispute resolution philosophy
> For system architecture, see [architecture.md](./architecture.md).

---

## 1. Why Governance Matters

Trust cannot be enforced by code alone.

Cryptographic signatures verify that an offer came from a specific key. They do not verify that the merchant behind that key is honest, that the food was edible, or that the delivery driver did not steal the package.

Human judgment is irreplaceable in commerce. ARC's governance model exists to organize that judgment — to give communities a structured way to handle fraud, resolve disputes, and maintain the integrity of the reputation layer.

Without governance, reputation becomes gameable. Without community enforcement, bad actors can accumulate fake trust and exploit it. Without a clear appeal process, suspension becomes arbitrary and abusive.

ARC treats governance as a first-class design concern, not an afterthought.

---

## 2. Core Governance Principles

**Local over central.**
Communities closest to the commerce are best positioned to judge it. A neighborhood food delivery dispute should be resolved by people who understand that neighborhood — not by a distant algorithm or a corporate trust-and-safety team.

**Transparent process.**
Every governance decision — warning, suspension, expulsion — should produce a reviewable record. Participants should be able to understand why a decision was made.

**Right to appeal.**
No suspension should be final without an appeal path. Mistakes happen. Malicious reports happen. The system must allow correction.

**Proportional response.**
Penalties should match the severity of the violation. A first-time late delivery is not equivalent to systematic fraud. The governance model should reflect that.

**No single point of control.**
No single corporation, individual, or community should have unilateral authority over the entire network. Governance is federated by design.

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

Composition:
- Active verified merchants
- Active verified consumers
- Elected or rotating community moderators

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

Protocol maintainers govern the rules, not the participants. They do not have authority over individual merchant suspensions or local disputes.

---

## 4. Dispute Resolution Process

### 4.1 Trigger Conditions

A dispute may be initiated when:

- A consumer reports a transaction as fraudulent, incomplete, or significantly misrepresented
- A merchant reports a consumer for payment fraud or false dispute claims
- A logistics agent reports a merchant for unsafe or false delivery conditions
- A community member reports suspicious agent behavior

### 4.2 Process Flow

```
User submits dispute report
          ↓
Transaction log retrieved and verified
          ↓
Signed offer records checked
          ↓
Both parties notified and given response period
          ↓
Community moderators review evidence
          ↓
Community decision issued
          ↓
Penalty applied (if any)
          ↓
Appeal window opens (7 days default)
          ↓
Decision finalized
```

### 4.3 Evidence Standards

Valid evidence includes:

- Signed offer records (cryptographically verifiable)
- Approved transaction records
- Delivery confirmation or failure logs
- Communication logs between agents (where retained)
- Prior reputation history

Invalid evidence:

- Unsigned claims
- Screenshots without verifiable source
- Anonymous accusations without corroborating records

### 4.4 Decision Timeline

| Stage | Default Duration |
|-------|-----------------|
| Report submission | Immediate |
| Evidence collection | 48 hours |
| Moderator review | 72 hours |
| Decision issued | Day 5 |
| Appeal window | 7 days |
| Final decision | Day 12 |

Communities may adjust these timelines within protocol guidelines.

---

## 5. Penalty Scale

Penalties are proportional to violation severity and history:

| Level | Penalty | Trigger |
|-------|---------|---------|
| 1 | Warning + reputation note | Minor first violation |
| 2 | Reputation score reduction | Repeated minor violations |
| 3 | Temporary suspension (7 days) | Confirmed fraud, first instance |
| 4 | Extended suspension (30 days) | Repeated fraud or serious harm |
| 5 | Community ban | Systematic fraud, malicious behavior |
| 6 | Network-wide flag | Extreme cases with cross-community impact |

Reputation recovery is possible after suspension periods. Agents are not permanently marked without opportunity for rehabilitation except in cases of systematic, verified fraud.

---

## 6. Anti-Gaming Measures

The reputation and governance system must resist manipulation:

### 6.1 Sybil Resistance

Fake identity farming to accumulate positive reputation or submit false dispute reports is a primary attack vector.

Mitigations:
- Identity provider verification required for agent creation
- New agents face transaction volume limits during probation period
- Reputation score velocity limits (scores cannot increase too rapidly)
- Community moderators may flag sudden reputation spikes for review

### 6.2 Collusion Detection

Groups of agents submitting coordinated false reviews or dispute reports.

Mitigations:
- Reputation events from agents with shared identity providers are weighted differently
- Statistical anomaly detection on review patterns
- Community moderators may request review of suspicious review clusters

### 6.3 False Dispute Abuse

Users submitting fraudulent dispute reports to harm competitors or extract refunds.

Mitigations:
- Dispute reporters with high false-report rates face reputation penalties
- Evidence standards require verifiable records
- Moderators may flag serial reporters for review

---

## 7. Community Self-Governance

ARC is designed so that communities can adapt governance rules to local needs.

A community may:

- Set its own penalty thresholds within protocol minimums
- Define local reputation metrics relevant to their commerce type
- Create local identity requirements (e.g., requiring business registration verification)
- Establish community-specific dispute resolution processes
- Invite or remove merchants from their local directory

A community may not:

- Override protocol-level security requirements
- Remove the human approval requirement from transactions
- Mandate exclusive use of a specific payment provider
- Discriminate based on protected characteristics

---

## 8. Non-Profit Governance Rationale

ARC is designed as non-profit open-source infrastructure.

The reasoning is straightforward:

If agent-to-agent commerce becomes a significant layer of the economy, the governance of that layer has enormous power. It determines who can participate, whose disputes are resolved fairly, whose reputation is protected, and whose is destroyed.

That power should not be held by a single corporation with shareholders and profit motives.

It should be held by the communities that use the infrastructure — distributed, accountable, and replaceable if they fail.

This is not idealism. It is a practical conclusion from observing what happens when governance of shared infrastructure is captured by private interests: the infrastructure becomes a rent-extraction mechanism, and participants have no recourse.

ARC proposes a different structure. Not because it is easy, but because the alternative is worse.

---

## 9. Current Status

ARC governance is currently a design proposal, not an operating system.

No governance community currently exists. No moderators have been appointed. No dispute resolution process is active.

This document describes the intended model for when ARC moves beyond the philosophy and prototype stage.

Contributions to the governance design are welcome. See [CONTRIBUTING.md](../CONTRIBUTING.md).

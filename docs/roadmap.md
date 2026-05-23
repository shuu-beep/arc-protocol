# ARC Protocol: Roadmap

> **Status:** Living document
> **Last updated:** 2026
> This roadmap reflects current thinking, not commitments.
> ARC is a non-profit open-source project with no funding or deadlines.

---

## Stage 0 — Philosophy and Protocol Draft ✅

**Status: Complete**

Completed:
- [x] README — full philosophy, architecture overview, protocol concepts
- [x] `docs/philosophy.md` — attention economy critique, centralized agent bias, design axioms
- [x] `docs/architecture.md` — system diagram, agent roles, message types, discovery layer, MVP scope
- [x] `docs/governance.md` — dispute resolution model, penalty scale, community self-governance
- [x] `docs/identity.md` — exploratory identity, credential, and trust model
- [x] `docs/roadmap.md` — this document
- [x] `CONTRIBUTING.md` — contribution guide including research contributions
- [x] Apache 2.0 license

---

## Stage 1 — Local MVP

**Status: Not started**

Goal: demonstrate that multiple agents can simulate a complete commerce transaction, end to end, with a human approval step.

This is not a product. It is a working proof of concept.

**Why local food delivery as an initial test domain?**

Food delivery combines time sensitivity, location dependency, and changing order state in a familiar scenario. That makes it a useful sandbox for testing approval, logistics, cancellation, and reputation flows without claiming that it represents every commerce domain.

### Milestones

**1.1 Consumer Agent (Basic)**
- [ ] Natural language request parsing
- [ ] Structured query generation
- [ ] Offer comparison logic
- [ ] Recommendation output with auditable reasoning log

**1.2 Merchant Agent (Simulated)**
- [ ] Static product data
- [ ] Offer response generation
- [ ] Mock signature on offers

**1.3 Logistics Agent (Simulated)**
- [ ] Static availability data
- [ ] Delivery time and fee estimation
- [ ] Mock delivery status updates

**1.4 Approval UI**
- [ ] Web-based approval screen
- [ ] Clear display of offer details and reasoning
- [ ] Approve / Decline buttons
- [ ] Mock payment confirmation on approval

**1.5 Transaction Log**
- [ ] Record of each transaction
- [ ] Offer details, approval timestamp, outcome
- [ ] Basic reputation event generation

**1.6 Demo Materials**
- [ ] Public demo video or walkthrough
- [ ] Architecture walkthrough screencast
- [ ] Example approval UI screenshots
- [ ] Example agent conversation logs

### MVP Success Criteria

A user can:
1. Type a natural language request
2. Receive offers from at least two simulated merchant agents
3. See a comparison with auditable reasoning
4. Approve one option
5. See a mock transaction logged
6. See a reputation event recorded

No real money. No real delivery. That is fine for Stage 1.

---

## Stage 2 — Identity and Reputation

**Status: Not started**

Stage 2 implements the foundational identity and reputation concepts described in `docs/identity.md` and future reputation specifications.

### Milestones

**2.1 Agent Identity**
- [ ] Ed25519 key pair generation per agent
- [ ] Signed offers and approval records
- [ ] Identity provider integration (Google / Apple / basic)
- [ ] Agent profile with public key and community affiliation

**2.2 Reputation System**
- [ ] Verified transaction-based reputation events
- [ ] Multi-metric reputation scoring (completion rate, refund rate, on-time rate)
- [ ] Reputation display in approval UI
- [ ] Reputation decay for inactive agents

**2.3 Anti-Gaming Basics**
- [ ] One reputation event per transaction per party
- [ ] New agent probation period
- [ ] Rate limits on reputation score changes

---

## Stage 3 — Community Governance

**Status: Not started**

### Milestones

**3.1 Fraud Reporting**
- [ ] User-facing fraud report submission
- [ ] Transaction log attachment to reports
- [ ] Report queue for community moderators

**3.2 Dispute Review**
- [ ] Moderator interface for evidence review
- [ ] Decision recording with reasoning
- [ ] Notification to dispute parties

**3.3 Penalty Enforcement**
- [ ] Warning system
- [ ] Temporary suspension implementation
- [ ] Reputation score adjustment on penalty
- [ ] Appeal submission and review

**3.4 Community Self-Governance Tools**
- [ ] Community configuration for local penalty thresholds
- [ ] Local merchant directory management
- [ ] Community moderator election or rotation

---

## Stage 4 — Payment Integration

**Status: Not started**

### Milestones

- [ ] Stripe integration (international)
- [ ] Toss integration (Korea)
- [ ] Google Pay / Apple Pay support
- [ ] Payment execution blocked until human approval confirmed
- [ ] User-configured approval thresholds
- [ ] Approval audit log
- [ ] Refund flow support

---

## Stage 5 — Local Commerce Pilot

**Status: Not started**

Goal: run a limited, real-world test with actual merchants in a defined geography.

**Why would merchants participate?**

Stage 5 would need to test this in practice. A small pilot may be relevant to volunteer merchants interested in direct customer relationships and in exploring lower intermediary overhead, while recognizing that ARC offers no built-in demand, marketing, or transaction-volume guarantee.

### Scope Constraints

- Single city or neighborhood
- Volunteer merchants only
- No production SLA
- Full transparency to participants about experimental status

### Milestones

- [ ] Onboard 3–5 local merchants
- [ ] Run 50+ real transactions with human approval
- [ ] Collect and analyze reputation data
- [ ] Document what broke, what worked, what was missing

---

## Stage 6 — Open Agent Commerce Network

**Status: Not started**

### Milestones

- [ ] Cross-community agent identity verification
- [ ] Interoperability protocol between community governance instances
- [ ] Federated reputation portability
- [ ] Multi-community dispute escalation path
- [ ] Protocol versioning and compatibility specification

---

## What Is Not On This Roadmap

**Full decentralization.**
ARC does not aim for a fully decentralized system at any stage. A hybrid model with community-operated servers is more realistic and more maintainable.

**AI autonomy.**
Human approval remains a hard requirement at every stage. Removing it is not a future feature; it is a philosophical rejection.

**Monetization.**
ARC is non-profit open-source infrastructure. There is no plan to monetize the protocol itself.

**Global scale.**
ARC does not aim to replace existing commerce infrastructure at scale. Local, limited, verifiable demonstration of the concept is sufficient.

---

## A Note on This Roadmap

Most of this roadmap will probably never be completed by the original author alone.

That is fine.

Stage 0 — the philosophy, the architecture proposal, the governance model — is itself a contribution. If this project does nothing but articulate clearly what open agent commerce infrastructure should look like, and someone else builds it better, that is a good outcome.

The roadmap exists to show that the thinking extends beyond the manifesto. Not to promise delivery.

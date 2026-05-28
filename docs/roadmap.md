# ARC Protocol: Roadmap

> **Status:** Living document
> **Last updated:** 2026
> This roadmap reflects current thinking, not commitments.
> ARC is a non-profit open-source project with no funding or deadlines.

---

## Stage 0 — Philosophy and Protocol Draft Baseline ✅

**Status: Draft baseline complete, not design-complete**

Stage 0 means the initial documentation baseline exists. It does not mean ARC has solved identity, reputation, discovery, governance, incentives, liability, or protocol interoperability.

Completed baseline documents:
- [x] README — philosophy, architecture overview, and early protocol concepts
- [x] `docs/philosophy.md` — attention economy critique, centralized agent bias, design axioms
- [x] `docs/architecture.md` — system diagram, agent roles, message types, discovery layer, MVP scope
- [x] `docs/protocol.md` — exploratory protocol mechanics, lifecycle, messages, and failure modes
- [x] `docs/local-commerce-simulation.md` — mock simulation scope and failure runs
- [x] `docs/threat-model.md` — adversarial pressure and abuse scenarios
- [x] `docs/governance.md` — dispute resolution model, penalty scale, community self-governance
- [x] `docs/identity.md` — exploratory identity, credential, and trust model
- [x] `docs/reputation.md` — exploratory reputation model and manipulation risks
- [x] `docs/bootstrap-and-incentives.md` — cold-start, platform-value, and sustainability limitations
- [x] `docs/liability-boundaries.md` — payment, legal, and responsibility boundaries
- [x] `docs/future-protocol-spec.md` — missing pieces before ARC can become a complete specification
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
- [ ] Explicit separation between original intent, inferred preferences, and user-confirmed constraints

**1.2 Merchant Agent (Simulated)**
- [ ] Static product data
- [ ] Offer response generation
- [ ] Mock signature on offers
- [ ] Basic expiry and refreshed-offer handling

**1.3 Logistics Agent (Simulated)**
- [ ] Static availability data
- [ ] Delivery time and fee estimation
- [ ] Mock delivery status updates

**1.4 Approval UI**
- [ ] Web-based approval screen
- [ ] Clear display of offer details and reasoning
- [ ] Approve / Decline buttons
- [ ] Mock payment confirmation on approval
- [ ] Approval-fatigue warning behavior for repeated or changed prompts

**1.5 Transaction Log**
- [ ] Record of each transaction
- [ ] Offer details, approval timestamp, outcome
- [ ] Basic reputation event generation
- [ ] Invalid-transition notes for stale offers, payment failure, and unsafe retries

**1.6 Failure Artifacts**
- [ ] Compromised or biased consumer agent run
- [ ] Colluding reputation-farming run
- [ ] Payment phishing or spoofed payment request run
- [ ] Governance overload or conflict-of-interest run

**1.7 Demo Materials**
- [ ] Public demo video or walkthrough
- [ ] Architecture walkthrough screencast
- [ ] Example approval UI screenshots
- [ ] Example agent conversation logs

### MVP Success Criteria

A user can:
1. Type a natural language request
2. See the parsed intent and inferred priorities before negotiation where ambiguity matters
3. Receive offers from at least two simulated merchant agents
4. See a comparison with auditable reasoning
5. Approve one option
6. See a mock transaction logged
7. See a limited reputation event recorded
8. See failure runs that expose unresolved questions rather than hide them

No real money. No real delivery. No real identity verification. That is fine for Stage 1.

---

## Stage 2 — Identity and Reputation

**Status: Not started**

Stage 2 implements the foundational identity and reputation concepts described in `docs/identity.md`, `docs/reputation.md`, and future specification work.

### Milestones

**2.1 Agent Identity**
- [ ] Ed25519 key pair generation per agent
- [ ] Signed offers and approval records
- [ ] Identity provider integration (Google / Apple / basic)
- [ ] Agent profile with public key and community affiliation
- [ ] Clear distinction between account continuity and merchant legitimacy
- [ ] Compromised-key handling and key rotation notes

**2.2 Reputation System**
- [ ] Verified transaction-based reputation events
- [ ] Multi-metric reputation scoring (completion rate, refund rate, on-time rate)
- [ ] Reputation display in approval UI
- [ ] Reputation decay for inactive agents
- [ ] Context labels that reduce the risk of reputation becoming a universal social score

**2.3 Anti-Gaming Basics**
- [ ] One reputation event per transaction per party
- [ ] New agent probation period
- [ ] Rate limits on reputation score changes
- [ ] Collusion and circular-transaction review triggers
- [ ] False-dispute and coordinated-reporting safeguards

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
- [ ] Conflict-of-interest disclosure for reviewers
- [ ] Distinction between community action and legal/payment-provider action

**3.3 Penalty Enforcement**
- [ ] Warning system
- [ ] Temporary suspension implementation
- [ ] Reputation score adjustment on penalty
- [ ] Appeal submission and review
- [ ] Proportionality and reversible provisional actions where evidence is incomplete

**3.4 Community Self-Governance Tools**
- [ ] Community configuration for local penalty thresholds
- [ ] Local merchant directory management
- [ ] Community moderator election or rotation
- [ ] Governance overload handling
- [ ] Reviewer sustainability model exploration

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
- [ ] Payment-provider dispute and chargeback boundary notes
- [ ] Retry and renewed-approval rules after payment failure

---

## Stage 5 — Local Commerce Pilot

**Status: Not started**

Goal: run a limited, real-world test with actual merchants in a defined geography.

**Why would merchants participate?**

Stage 5 would need to test this in practice. A small pilot may be relevant to volunteer merchants interested in direct customer relationships and in exploring lower intermediary overhead, while recognizing that ARC offers no built-in demand, marketing, transaction-volume guarantee, or replacement for existing platform support.

### Scope Constraints

- Single city or neighborhood
- Volunteer merchants only
- No production SLA
- Full transparency to participants about experimental status
- No claim that the pilot proves general adoption or economic viability

### Milestones

- [ ] Onboard 3–5 local merchants
- [ ] Run limited mock or real-world trials only where legally and operationally appropriate
- [ ] Collect and analyze reputation data
- [ ] Document what broke, what worked, what was missing
- [ ] Record why any merchants, logistics providers, or users declined to participate

---

## Stage 6 — Open Agent Commerce Network

**Status: Not started**

### Milestones

- [ ] Cross-community agent identity verification
- [ ] Interoperability protocol between community governance instances
- [ ] Federated reputation portability
- [ ] Multi-community dispute escalation path
- [ ] Protocol versioning and compatibility specification
- [ ] Conformance tests for independent implementations

---

## What Is Not On This Roadmap

**Full decentralization.**
ARC does not aim for a fully decentralized system at any stage. A hybrid model with community-operated servers is more realistic and more maintainable.

**AI autonomy.**
Human approval remains a hard requirement at every stage. Removing it is not a future feature; it is a philosophical rejection.

**A required ARC token.**
ARC does not require a token economy. Sustainability questions may be studied without turning the protocol into a speculative asset system.

**Replacing payment providers.**
ARC does not currently try to replace existing payment infrastructure. Payment-provider dependency is a trade-off to document, not a problem solved by this roadmap.

**Monetization of the protocol itself.**
ARC is non-profit open-source infrastructure. There is no plan to monetize the protocol itself.

**Global scale.**
ARC does not aim to replace existing commerce infrastructure at scale. Local, limited, verifiable demonstration of the concept is sufficient.

---

## A Note on This Roadmap

Most of this roadmap will probably never be completed by the original author alone.

That is fine.

Stage 0 — the initial philosophy, architecture proposal, governance model, and limitation documents — is itself a contribution. If this project does nothing but articulate clearly what open agent commerce infrastructure should look like, and someone else builds it better, that is a good outcome.

The roadmap exists to show that the thinking extends beyond the manifesto. Not to promise delivery.

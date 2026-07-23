# ARC Protocol: Roadmap

> **Status:** Living document
> **Last updated:** 2026
> This roadmap reflects current thinking, not commitments.
> ARC is an open-source project. Collaboration, implementation partnerships, and funding are welcome.

---

## Stage 0 — Philosophy and Protocol Draft Baseline ✅

**Status: Draft baseline complete, not design-complete**

Stage 0 means the initial documentation baseline exists. It does not mean ARC has solved identity, reputation, discovery, governance, incentives, liability, or protocol interoperability.

Completed baseline documents:
- [x] README — philosophy, architecture overview, and early protocol concepts
- [x] `docs/philosophy.md` — historical Commerce attention-economy concern, agent-bias risk, and application policies
- [x] `docs/architecture.md` — system diagram, agent roles, message types, discovery layer, MVP scope
- [x] `docs/protocol.md` — exploratory protocol mechanics, lifecycle, messages, and failure modes
- [x] `docs/local-commerce-simulation.md` — mock simulation scope and failure runs
- [x] `docs/threat-model.md` — adversarial pressure and abuse scenarios
- [x] `docs/governance.md` — dispute resolution model, penalty scale, community self-governance
- [x] `docs/identity.md` — exploratory identity, credential, and trust model
- [x] `docs/reputation.md` — exploratory reputation model and manipulation risks
- [x] `docs/bootstrap-and-incentives.md` — cold-start, platform-value, and sustainability limitations
- [x] `docs/liability-boundaries.md` — payment, legal, and responsibility boundaries
- [x] `docs/authority-and-conflict.md` — authority-of-last-resort boundaries (human vs commons), conflict resolution
- [x] `docs/object-model.md` — Relationship / Event / Projection layers and non-authoritative derived-state/cache discipline
- [x] `docs/event-registry.md` — the current canonical Event vocabulary (KEY, ATTEST, AUTHORIZE, CHALLENGE, ADJUDICATE)
- [x] `docs/delegation-and-spending-mandates.md` — how principal-rooted authority and delegation coexist using only the current Canon; current reference profiles are typically human-rooted (AUTHORIZE + scope, revoked via nullifies)
- [x] `docs/landscape-and-positioning.md` — where ARC sits among agent and commerce systems, and what it is not
- [x] `docs/trust-model-tradeoffs.md` — the trust trade-offs consolidated into spatial and temporal axes
- [x] `docs/future-protocol-spec.md` — missing pieces before ARC can become a complete specification
- [x] `docs/roadmap.md` — this document
- [x] `CONTRIBUTING.md` — contribution guide including research contributions
- [x] Apache 2.0 license

---

## Stage 0.8 — Executable Reference Corpus

**Status: Ongoing, not a product**

Between the documentation baseline (Stage 0) and a running MVP (Stage 1) sits a
layer the baseline list does not capture: a body of small, dependency-light
executable probes that *exercise* the documented model rather than merely
describe it. The README therefore calls this an Executable Reference Corpus,
not a production or reference implementation. It is not the Stage 1 MVP — there is no
persistent server, no database, no real agents transacting, no product.

What exists:
- [x] Canonical event/projection probes — the five event types fold a hand-built
  log; current scenarios use only those five (which is not a sufficiency proof)
  (`examples/canon-fold-demo`). A local TypeScript discriminated union and literal
  types exercise selected compile-time shape errors and exhaustive handlers; they
  do not provide runtime or protocol-conformance enforcement (`examples/canon-ts`)
- [x] End-to-end scripted flow — four parties each emit their own mock-signed events;
  the fixture derives standing through `ADJUDICATE` Events rather than mutating stored state, with an
  optional external-reasoner consumer path
  (`examples/end-to-end-demo`)
- [x] Browser reference client — the log rendered as the surfaces a human sees,
  with a mandate-routed write path and bands probing cold-start policy, key
  compromise, federation, and the custody seam (`examples/reference-client`)
- [x] Commerce failure catalog — an eight-run [A]–[H] catalog where records passing
  the fixture's local checks do not thereby establish outcome or application legitimacy
  (`examples/local-commerce-demo`)
- [x] Custody, revocation, and fidelity experiments — including
  interpretation, temporal, world, and presentation checks
- [x] Adoption / refusal experiments — the refusal-recording fold, which
  classifies synthetic refusal records and reports gaps without establishing adoption
  (`examples/refusal-recording-demo`)

What this stage does **not** establish:
- These probes exercise the model; they do not validate the protocol, prove
  adoption, or constitute a specification.
- A probe passing means it produced the expected output under that scenario, not that ARC works in the world.
- The normative wire format and conformance suite remain future work
  (`docs/future-protocol-spec.md`).

---

## Protocol Specification and Conformance Track

**Status: Open, and separate from the Commerce implementation stages below**

External review of the current documents and executable corpus does not establish interoperability readiness. That requires, at minimum:

- [ ] Core Event Conformance, Named Projection Conformance, and Named Functional Profile Conformance requirements
- [ ] a declared wire and security profile for each interoperability claim
- [ ] quorum semantics, whose current status is `OPEN — MUST NOT BE IMPLIED BY CURRENT DOCUMENTATION`
- [ ] a deterministic mandate-evaluation profile — `REQUIRED BEFORE INTEROPERABILITY CLAIM`
- [ ] atomic cumulative mandate consumption — `REQUIRED BEFORE INTEROPERABILITY CLAIM`

---

## Commerce Flagship Implementation Track — Stage 1: Local MVP

**Status: Not started**

Goal: simulate a complete multi-agent commerce transaction, end to end, with a Current Coverage step.

This is a planned implementation experiment, not a product.

**Why local food delivery as an initial test domain?**

Food delivery combines time sensitivity, location dependency, and changing order state in a familiar scenario. That makes it a useful sandbox for testing approval, logistics, cancellation, and reputation flows without claiming that it represents every commerce domain.

### Milestones

**1.1 Consumer Agent (Basic)**
- [ ] Natural language request parsing
- [ ] Structured query generation
- [ ] Offer comparison logic
- [ ] Recommendation output with an inspectable reasoning record
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
- [ ] Offer details, approval timestamp, outcome claim
- [ ] Basic application reputation-input generation
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
7. See a limited application reputation input recorded
8. See failure runs that expose unresolved questions rather than hide them

Stage 1 excludes real money, real delivery, and real identity verification.

---

## Commerce Flagship Implementation Track — Stage 2: Identity and Reputation

**Status: Not started**

Stage 2 explores identity and reputation concepts described in `docs/identity.md`, `docs/reputation.md`, and future specification work. This track plans to record Events; identity and reputation views will be named Projections rather than authoritative stored status (see `docs/object-model.md`, `docs/event-registry.md`).

### Milestones

**2.1 Agent Identity**
- [ ] Ed25519 key pair generation per agent for this implementation profile
- [ ] Signed offers and approval records
- [ ] Identity provider integration (Google / Apple / basic)
- [ ] Agent profile with public key and community affiliation
- [ ] Clear distinction between account continuity and merchant legitimacy
- [ ] Compromised-key handling and key rotation notes

**2.2 Reputation System**
- [ ] Canon Events carrying transaction-related reputation inputs under the named Commerce profile
- [ ] Multi-metric reputation scoring (completion rate, refund rate, on-time rate)
- [ ] Reputation display in approval UI
- [ ] Reputation decay for inactive agents
- [ ] Context labels that reduce the risk of reputation becoming a universal social score

**2.3 Anti-Gaming Basics**
- [ ] At most one application reputation input per transaction per party under the named policy
- [ ] New agent probation period
- [ ] Rate limits on reputation score changes
- [ ] Collusion and circular-transaction review triggers
- [ ] False-dispute and coordinated-reporting safeguards

---

## Commerce Flagship Implementation Track — Stage 3: Community Governance

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

## Commerce Flagship Implementation Track — Stage 4: Payment Integration

**Status: Not started**

### Milestones

- [ ] Stripe integration (international)
- [ ] Toss integration (Korea)
- [ ] Google Pay / Apple Pay support
- [ ] Payment execution blocked unless the act has Current Coverage; fresh confirmation remains this Commerce track's default
- [ ] User-configured approval thresholds
- [ ] Approval audit log
- [ ] Refund flow support
- [ ] Payment-provider dispute and chargeback boundary notes
- [ ] Retry and renewed-approval rules after payment failure

---

## Commerce Flagship Implementation Track — Stage 5: Local Commerce Pilot

**Status: Not started**

Goal: run a limited, real-world test with actual merchants in a defined geography. For how such a pilot would test the inverse — learning, not validation — see [pilot-design.md](pilot-design.md). The step that comes *before* a pilot — recording why real parties decline, before any of them has begun to use ARC — is [first-refusal-protocol.md](first-refusal-protocol.md).

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
- [ ] Collect and analyze application-level reputation inputs and named Projection outputs
- [ ] Document what broke, what worked, what was missing
- [ ] Record why any merchants, logistics providers, or users declined to participate (using the refusal-recording schema in [adoption-and-defection §6](adoption-and-defection.md))

---

## Commerce Flagship Implementation Track — Stage 6: Multi-Community Commerce Interoperability

**Status: Not started**

### Milestones

- [ ] Cross-community key and credential checks
- [ ] Interoperability protocol between community governance instances
- [ ] Federated reputation portability
- [ ] Multi-community dispute escalation path
- [ ] Protocol versioning and compatibility specification, owned by the parallel protocol/conformance track
- [ ] Independent-implementation conformance tests for the named Commerce profile, dependent on that track

---

## What Is Not On This Roadmap

**A mandatory deployment topology.**
The base protocol does not require centralized, federated, fully decentralized, or hybrid operation. The Commerce track may explore community-operated and hybrid deployments as profile choices.

**AI autonomy.**
Consequential acts must have Current Coverage traceable to authority granted by the responsible principal or authority holder. Current Commerce profiles are typically human-rooted. Coverage may be act-specific or mandate-scoped; removing the authority boundary is not a future feature.

**Replacing payment providers.**
ARC does not currently try to replace existing payment infrastructure. Payment-provider dependency is a trade-off to document, not a problem solved by this roadmap.

**Protocol licensing and implementation funding.**
ARC's published source is licensed under Apache-2.0. Commercial implementations and closed deployments are compatible with the protocol; any conformance claim must identify the declared profile and version it applies.

**Global scale.**
The Commerce track currently targets bounded local demonstrations; it makes no global-adoption or infrastructure-replacement commitment.

---

## A Note on This Roadmap

Later stages may require contributors or independent implementations beyond the current maintainer.

Stage 0 documents and executable probes can remain useful even if later tracks are not completed.

These items are planning directions, not delivery promises.

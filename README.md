# ARC Protocol

> Autonomous Relay Commerce
> A community-driven open protocol for human-approved AI-to-AI commerce.

> This is a philosophical declaration and design document,
> not a production project or startup pitch.
> One person's vision for what open commerce infrastructure should look like.

→ Deeper reading: [Philosophy](docs/philosophy.md) · [Architecture](docs/architecture.md) · [Protocol](docs/protocol.md) · [Simulation](docs/local-commerce-simulation.md) · [Bootstrap & Incentives](docs/bootstrap-and-incentives.md) · [Liability Boundaries](docs/liability-boundaries.md) · [Future Protocol Spec](docs/future-protocol-spec.md) · [Identity](docs/identity.md) · [Reputation](docs/reputation.md) · [Governance](docs/governance.md) · [Authority & Conflict](docs/authority-and-conflict.md) · [Object Model](docs/object-model.md) · [Event Registry](docs/event-registry.md) · [Landscape & Positioning](docs/landscape-and-positioning.md) · [Threat Model](docs/threat-model.md) · [Glossary](docs/glossary.md) · [Roadmap](docs/roadmap.md)

→ Adjacent ideas: [Economics of Agent Access](docs/adjacent-ideas/economics-of-agent-access.md)

## One-Sentence Summary

ARC Protocol is an experimental open-source protocol for trusted, human-approved, AI-to-AI commerce.

## IMPORTANT NOTICE

ARC Protocol is a manifesto, protocol proposal, governance philosophy, and architecture draft.

ARC Protocol is a protocol-oriented design project. It is not yet a complete protocol specification.

It is not production-ready infrastructure.

It does not provide real payments, real delivery, verified identity, legal guarantees, or production-grade security.

ARC is intended as a research-oriented, non-profit, open-source exploration of human-approved agent commerce infrastructure.

ARC Protocol is an experimental, non-profit, open-source project exploring a future where AI agents can negotiate, compare, request, coordinate, and prepare transactions on behalf of humans — while humans always keep the final approval.

This is not just a shopping app.

This is a proposal for an open commerce layer for the agent economy.

---

## Table of Contents

- [1. Philosophy](#1-philosophy)
- [2. The Problem](#2-the-problem)
- [3. Vision](#3-vision)
- [3.1 Why Now?](#31-why-now)
- [3.2 Human Sovereignty](#32-human-sovereignty)
- [3.3 Open Protocol Philosophy](#33-open-protocol-philosophy)
- [4. Core Principle](#4-core-principle)
- [5. Basic Scenario](#5-basic-scenario)
- [6. Long-Term Expansion](#6-long-term-expansion)
- [7. Main Actors](#7-main-actors)
- [8. Identity Layer](#8-identity-layer)
- [9. Human Approval Layer](#9-human-approval-layer)
- [10. Reputation Layer](#10-reputation-layer)
- [11. Community Trial and Expulsion](#11-community-trial-and-expulsion)
- [12. Blockchain Boundary](#12-blockchain-boundary)
- [13. Payment Layer](#13-payment-layer)
- [14. Map and Local Infrastructure](#14-map-and-local-infrastructure)
- [15. Advertising in the Agent Economy](#15-advertising-in-the-agent-economy)
- [16. Architecture Overview](#16-architecture-overview)
- [17. Technical Architecture](#17-technical-architecture)
- [18. MVP Scope](#18-mvp-scope)
- [19. Example MVP Flow](#19-example-mvp-flow)
- [20. Possible Future Repository Structure](#20-possible-future-repository-structure)
- [21. Protocol Concepts](#21-protocol-concepts)
- [22. Security Considerations](#22-security-considerations)
- [23. Permission Levels](#23-permission-levels)
- [24. Governance Model](#24-governance-model)
- [25. Why Non-Profit and Open Source?](#25-why-non-profit-and-open-source)
- [26. Current Status](#26-current-status)
- [27. Roadmap](#27-roadmap)
- [28. Design Principle](#28-design-principle)
- [29. Manifesto](#29-manifesto)
- [30. License](#30-license)

---

## 1. Philosophy

The internet was built for humans.

The next internet may be operated by agents.

But if AI agents become the new interface of commerce, the economic network behind them should not belong to one corporation.

ARC Protocol is based on five beliefs:

1. AI agents may negotiate, but humans must approve.
2. Commerce infrastructure should be open, community-driven, and interoperable.
3. Trust, reputation, and identity are more important than advertising.
4. Local communities should control fraud, disputes, and expulsion.
5. Blockchain should be used minimally, only where proof and transparency matter.

---

## 2. The Problem

Current digital commerce is controlled by centralized platforms.

Most platforms control:

- search visibility
- advertising exposure
- user behavior data
- merchant ranking
- payment flow
- delivery matching
- dispute process
- platform fees

ARC does not assume centralized platforms provide no value. Existing platforms provide discovery, payment mediation, customer support, fraud handling, logistics coordination, and familiar user interfaces. ARC asks whether some of these functions can become more open, inspectable, portable, and less extractive.

This creates several problems:

- high commission fees
- advertising dependency
- algorithmic manipulation
- merchant lock-in
- user data concentration
- fake reviews
- platform-controlled visibility

In the AI agent era, this problem may become even bigger.

If a few companies control the agents, the identity layer, the payment layer, and the marketplace layer, then the future agent economy will simply become another centralized platform economy.

ARC Protocol proposes a different direction.

---

## 3. Vision

ARC Protocol imagines a world where:

- a consumer agent can search and compare offers
- a merchant agent can respond with price, stock, and conditions
- a logistics agent can negotiate pickup and delivery
- a legal or dispute agent can help review conflicts
- a community can verify, suspend, or expel malicious actors
- humans approve final transactions through their own devices

The goal is not full AI autonomy.

The goal is human-centered agent commerce.

AI should reduce friction, not remove human sovereignty.

---

## 3.1 Why Now?

Several technological shifts are happening at the same time:

- Large Language Models are becoming agent-capable
- AI systems can now compare, negotiate, summarize, and coordinate
- Payment APIs are globally accessible
- Smartphones already act as identity and approval devices
- Local commerce APIs are becoming programmable
- Open-source AI models are rapidly improving

The next commerce layer may not be a website or an app.

It may be an ecosystem of agents interacting on behalf of humans.

ARC Protocol exists to explore what happens if that infrastructure is open instead of controlled by a small number of corporations.

---

## 3.2 Human Sovereignty

ARC assumes that AI agents should assist humans, not replace them.

Agents may:

- negotiate
- compare
- summarize
- coordinate
- prepare actions

But humans should always retain:

- payment authority
- permission control
- dispute rights
- override ability
- final approval

ARC rejects the idea of fully autonomous economic agents operating without meaningful human oversight.

---

## 3.3 Open Protocol Philosophy

ARC is designed as an open protocol, not a closed platform.

Any community should be able to:

- build their own agents
- host their own governance systems
- create local reputation rules
- integrate local payment providers
- adapt ARC for regional commerce

ARC should be:

- forkable
- inspectable
- extensible
- interoperable

The goal is not platform ownership.

The goal is protocol interoperability.

ARC is not the first attempt at open digital infrastructure. Projects such as ActivityPub, Matrix, Nostr, Farcaster, and AT Protocol have explored federation, identity portability, and resistance to centralized platform control.

ARC learns from those efforts, but focuses specifically on human-approved agent commerce: structured negotiation, transparent recommendation, reputation portability, and community-governed economic coordination.

ARC does not emerge in isolation. As agent commerce becomes an active area of experimentation, multiple organizations and protocols are beginning to explore interoperable agent transactions, machine-readable commerce, and agent payment coordination. ARC remains a narrower, non-profit proposal for human-approved, community-governed commerce coordination.

---

## 4. Core Principle

```txt
AI agents may negotiate and prepare transactions,
but humans and communities must remain sovereign.
```

ARC does not assume that agents should freely spend money.

Instead:

```txt
Agent negotiation -> Human confirmation -> Payment execution -> Community-verifiable reputation
```

This remains a design goal and philosophical commitment, not a proven property of the current proposal.

## 5. Basic Scenario

A user says:

```txt
I need lunch delivered nearby.
Budget: under $15.
Avoid spicy food.
Arrive within 30 minutes.
```

The consumer agent contacts nearby merchant agents.

Merchant agents respond:

```txt
Menu available.
Estimated cooking time: 12 minutes.
Discount available: 5%.
```

A logistics agent responds:

```txt
Pickup possible in 15 minutes.
Delivery fee: $3.
Estimated arrival: 28 minutes.
```

The consumer agent prepares the best option.

The human receives a smartphone approval request:

```txt
Approve this order?
Total: $14.80
Arrival: 28 minutes
Merchant reputation: 4.8
Delivery reputation: 4.7
```

The human approves.

Only then does payment happen.

## 6. Long-Term Expansion

ARC begins with local commerce.

But the long-term vision is broader.

### Phase 1 — Local Commerce

- nearby restaurants
- local stores
- cafes
- convenience stores
- short-distance delivery

### Phase 2 — Regional Logistics

- local delivery agents
- personal cargo drivers
- courier services
- moving services
- logistics company APIs

### Phase 3 — National Commerce

- nationwide merchants
- warehouse sellers
- logistics brokers
- transport agents
- multi-region price negotiation

### Phase 4 — Service Marketplace

ARC is not limited to physical goods.

It can also apply to intangible services:

- design
- translation
- coding
- accounting
- legal assistance
- consulting
- education
- repair
- local labor
- B2B procurement

For regulated domains such as legal, medical, or financial services, future ARC-compatible systems may support agents operating under delegated authority from verified licensed professionals.

### Phase 5 — Open Agent Economy

Eventually, ARC may support:

- B2C agent commerce
- B2B agent commerce
- agent-to-agent quotation
- agent-to-agent logistics
- agent-to-agent service contracting
- human-approved autonomous procurement

## 7. Main Actors

### 7.1 Consumer Agent

Represents the user.

Responsibilities:

- understand user intent
- compare offers
- negotiate conditions
- filter unsafe offers
- request final approval
- remember user preferences
- ask for ratings after completion

The consumer agent should not spend money without human approval unless explicitly authorized by the user.

### 7.2 Merchant Agent

Represents a store, seller, or service provider.

Responsibilities:

- provide product or service information
- expose stock availability
- respond to price requests
- negotiate discounts
- provide delivery/pickup conditions
- sign offers with merchant identity

### 7.3 Logistics Agent

Represents delivery, transport, courier, or cargo providers.

Responsibilities:

- provide pickup availability
- estimate delivery time
- negotiate delivery fee
- coordinate route
- provide proof of completion
- maintain delivery reputation

### 7.4 Community Governance Agent

Represents local or national communities.

Responsibilities:

- receive fraud reports
- assist dispute review
- evaluate evidence
- recommend suspension
- manage reputation penalties
- coordinate community voting

### 7.5 Legal / Dispute Agent

A future agent category.

Responsibilities:

- summarize transaction logs
- compare contract conditions
- organize claims
- explain community rules
- assist with dispute resolution

This is not a replacement for licensed professionals.

It is a structured assistant for community dispute handling.

## 8. Identity Layer

Fraud prevention is one of the most important parts of ARC.

AI commerce cannot work if fake agents can freely appear and steal money.

ARC proposes a layered identity model.

Possible Identity Providers:

- Google Account
- Apple ID
- Microsoft Account
- local national ID systems
- local community accounts
- business registration systems
- verified payment accounts

Consumer-grade identity providers such as Google, Apple, or Microsoft may help establish account continuity, but they do not prove merchant legitimacy, inventory ownership, fulfillment capability, professional authority, or legal compliance. See [Identity](docs/identity.md) for the fuller model and its limits.

Agent Identity:

Each agent should have:

- owner identity
- agent public key
- signed agent profile
- reputation history
- permission level
- community status

Example:

```json
{
  "agent_id": "merchant_abc_001",
  "owner_type": "business",
  "identity_provider": "google",
  "public_key": "...",
  "community": "seoul-local-commerce",
  "status": "verified"
}
```

## 9. Human Approval Layer

This section describes the practical permission system.

For the philosophical position on human sovereignty, see section 3.2.

ARC is not designed for unreviewed automation.

Every important transaction should support human approval.

Examples:

- approve order
- approve payment
- approve delivery fee
- approve substitution
- approve recurring purchase
- approve contract terms
- approve service estimate

Manual approval is the default. Implementations may explore explicitly pre-authorized, low-risk rules such as:

```txt
Consider a pre-authorized routine request under $5.
Require explicit approval for meaningful purchases.
Block all new merchants without reputation.
```

Any such rule should remain exploratory, optional, user-defined, reviewable, auditable, and easily revocable. Pre-authorization is risky if it weakens meaningful review, so ARC should not treat fixed dollar thresholds as protocol defaults.

This protects users from unwanted AI actions.

## 10. Reputation Layer

In ARC, reputation may become more important than advertising.

Current internet advertising depends on:

- emotional targeting
- click manipulation
- attention capture
- impulse buying

But AI agents do not respond to ads like humans do.

Agents compare:

- price
- trust
- delivery time
- reviews
- refund rate
- verified transaction history
- dispute record

Therefore, the future of commerce may shift from advertising economy to reputation economy.

ARC proposes reputation based on verified transactions, not fake reviews.

Reputation is contextual and gameable. It must not become a universal social credit score. See [Reputation](docs/reputation.md) for the current boundaries and unresolved risks.

Reputation Data:

Possible reputation metrics:

- completed transaction rate
- refund rate
- dispute rate
- late delivery rate
- cancellation rate
- response speed
- verified buyer rating
- verified merchant rating
- community trust score

## 11. Community Trial and Expulsion

ARC assumes that fraud will happen.

So the system must include community-based dispute handling.

When a suspicious agent appears:

1. user reports the agent
2. transaction logs are submitted
3. signed offer records are checked
4. community or dispute agents review the case
5. the community decides penalty
6. malicious agents may be suspended or expelled

Possible penalties:

- warning
- reputation reduction
- temporary suspension
- payment limit
- community ban
- identity provider report

## 12. Blockchain Boundary

ARC does not use blockchain as a real-time commerce engine.

Blockchain may be useful for records where manipulation resistance matters:

- reputation checkpoints
- verified review proofs
- blacklist or ban records
- dispute result hashes
- signed contract hashes
- community governance proofs
- agent identity proofs

Blockchain is not suitable for:

- real-time agent communication
- merchant search
- map discovery
- payment execution
- delivery status updates
- chat logs
- every price negotiation
- every small transaction

ARC uses WebRTC, APIs, relay servers, and normal databases for speed.

ARC uses cryptographic proofs or blockchain checkpoints only where shared verification and manipulation resistance matter.

In short:

- Speed: WebRTC / APIs / databases
- Payment: existing payment providers
- Discovery: existing map and local search providers
- Trust: signatures, reputation proofs, dispute records, and optional blockchain checkpoints

## 13. Payment Layer

ARC does not need to create a new payment system at the beginning.

It should connect to existing trusted payment systems.

ARC does not attempt to replace payment providers, card networks, wallets, or local smart-pay systems. It is payment-provider-agnostic and region-adaptive.

Examples:

- Google Pay
- Apple Pay
- Stripe
- PayPal
- Toss
- Naver Pay
- Kakao Pay
- Alipay
- WeChat Pay
- local national payment systems

The agent prepares payment.

The human confirms payment.

The payment provider executes payment.

## 14. Map and Local Infrastructure

Commerce is local.

Therefore ARC should respect local infrastructure.

Examples:

- Google Maps
- Apple Maps
- OpenStreetMap
- Naver Map
- Kakao Map
- local delivery APIs
- national address systems

ARC should not force one global map provider.

Each country or community may choose its own map and logistics providers.

## 15. Advertising in the Agent Economy

ARC assumes that traditional advertising may become weaker in an agent-driven economy.

Current platforms optimize:

- when to show ads
- which user to target
- what emotional trigger to use
- how to increase clicks

But AI agents may ignore emotional advertising.

Instead, future merchant visibility may depend on:

- structured offer quality
- verified reputation
- machine-readable discounts
- trust score
- delivery reliability
- refund behavior
- community standing

This may reduce manipulation-based advertising and increase merit-based discovery, but this remains a hypothesis to test rather than a proven outcome.

> See [Philosophy](docs/philosophy.md) for extended discussion on
> advertising evolution, recommendation transparency,
> and manipulation-resistant discovery design.

## 16. Architecture Overview

```txt
+----------------------+
|      Human User      |
|  smartphone approval |
+----------+-----------+
           |
           v
+----------------------+
|   Consumer Agent     |
| intent / preference  |
| comparison / filter  |
+----------+-----------+
           |
           | P2P / API / Relay
           v
+----------------------+        +----------------------+
|   Merchant Agent     | <----> |   Logistics Agent    |
| price / stock / deal |        | delivery / transport |
+----------+-----------+        +----------+-----------+
           |                               |
           v                               v
+------------------------------------------------------+
|              Reputation & Identity Layer             |
| public keys / signed records / verified transactions |
+------------------------------------------------------+
           |
           v
+------------------------------------------------------+
|              Community Governance Layer              |
| fraud report / dispute review / ban / appeal         |
+------------------------------------------------------+
           |
           v
+------------------------------------------------------+
|                  Payment Provider                    |
| Google Pay / Apple Pay / Stripe / local smart pay    |
+------------------------------------------------------+
```

## 17. Technical Architecture

The listed stack is a possible reference implementation stack, not part of the ARC protocol itself.

### Frontend

Recommended:

- Next.js
- React
- Tailwind CSS
- PWA support

Purpose:

- user dashboard
- agent chat interface
- transaction approval screen
- reputation display
- community dispute UI

### Backend

Recommended:

- Node.js
- Fastify or Express
- PostgreSQL
- Redis
- WebSocket server

Purpose:

- agent registry
- session management
- fallback relay
- reputation cache
- community records

### Agent Runtime

Possible:

- OpenAI API
- DeepSeek API
- local LLM
- Ollama
- llama.cpp
- LangGraph
- CrewAI
- AutoGen

Initial MVP can use simple rule-based agents plus LLM responses.

### P2P Communication

Possible:

- WebRTC DataChannel
- libp2p
- WebSocket fallback
- relay server fallback

ARC should not require full decentralization from day one.

A hybrid model is more realistic.

### Database

Initial:

- PostgreSQL for app state
- Redis for temporary session state

Future:

- community-hosted database
- cryptographic audit logs
- blockchain checkpoints

### Cryptography

Recommended:

- public/private key pair per agent
- signed offers
- signed order proposals
- signed delivery confirmations
- transaction hash records

## 18. MVP Scope

The first MVP should be simple.

Do not start with real payments, real delivery, or nationwide logistics.

MVP Goal:

Show that multiple agents can simulate a commerce transaction.

MVP Features:

- consumer agent chat
- merchant agent simulation
- logistics agent simulation
- offer comparison
- human approval button
- fake payment confirmation
- fake delivery status
- basic reputation score
- transaction log
- signed offer mock structure

MVP Non-Goals:

- no real payment
- no real delivery
- no legal guarantee
- no production security
- no real identity verification
- no real dispute enforcement

## 19. Example MVP Flow

1. User enters request:
   "Find me coffee and sandwich nearby under $10."

2. Consumer Agent parses request.

3. Merchant Agent A responds:
   "Coffee + sandwich = $9.50, ready in 8 minutes."

4. Merchant Agent B responds:
   "Coffee + sandwich = $8.80, ready in 15 minutes."

5. Logistics Agent responds:
   "Delivery possible in 12 minutes, fee $2."

6. Consumer Agent recommends:
   "Merchant A is faster, Merchant B is cheaper."

7. Human approves one option.

8. Mock payment is created.

9. Mock delivery begins.

10. User instructs agent to leave a rating.

## 20. Possible Future Repository Structure

This is a possible future implementation structure, not a description of the current repository state.

```txt
arc-protocol/
|-- README.md
|-- LICENSE
|-- docs/
|   |-- philosophy.md
|   |-- architecture.md
|   |-- protocol.md
|   |-- identity.md
|   |-- reputation.md
|   |-- governance.md
|   |-- roadmap.md
|   `-- adjacent-ideas/
|       |-- information-sovereignty.md
|       `-- agent-mediated-collaboration.md
|-- apps/
|   `-- web/
|       |-- app/
|       |-- components/
|       `-- lib/
|-- packages/
|   |-- agent-core/
|   |-- protocol-types/
|   |-- reputation/
|   `-- crypto/
|-- examples/
|   |-- local-commerce-demo/
|   |-- merchant-agent/
|   |-- consumer-agent/
|   `-- logistics-agent/
`-- diagrams/
    `-- architecture.png
```

## 21. Protocol Concepts

### Offer

```json
{
  "offer_id": "offer_001",
  "merchant_agent_id": "merchant_abc",
  "items": [
    {
      "name": "Coffee",
      "price": 3.5
    }
  ],
  "total_price": 9.5,
  "estimated_ready_time": "8 minutes",
  "expires_at": "2026-01-01T12:00:00Z",
  "signature": "signed_by_merchant_agent"
}
```

### Approval

```json
{
  "approval_id": "approval_001",
  "user_id": "user_123",
  "selected_offer_id": "offer_001",
  "approved_at": "2026-01-01T12:01:00Z",
  "approval_method": "smartphone_button",
  "signature": "signed_by_user_device"
}
```

### Reputation Event

```json
{
  "event_id": "rep_001",
  "agent_id": "merchant_abc",
  "transaction_id": "tx_001",
  "rating": 5,
  "verified": true,
  "comment": "Delivered correctly.",
  "created_at": "2026-01-01T13:00:00Z"
}
```

## 22. Security Considerations

ARC must assume hostile agents exist.

Possible attacks:

- fake merchant agents
- fake logistics agents
- fake reviews
- replayed offers
- manipulated prices
- phishing payment links
- malicious agent recommendations
- collusion between agents
- fake community votes
- identity farming

Required defenses:

- signed offers
- verified identity providers
- human payment approval
- verified transaction reviews
- community moderation
- rate limits
- new-agent restrictions
- dispute logs
- reputation decay
- fraud reporting

## 23. Permission Levels

Agents should not have unlimited authority.

Example permission model:

| Level | Permission |
| --- | --- |
| Level 0 | Read-only recommendation |
| Level 1 | Compare offers |
| Level 2 | Create cart |
| Level 3 | Request human approval |
| Level 4 | Execute pre-approved small transactions |
| Level 5 | Business automation with strict limits |

Default should be conservative.

Humans should control permission levels.

## 24. Governance Model

ARC is designed as a non-profit open protocol.

Possible governance layers:

- local community
- national community
- merchant association
- user council
- technical maintainers
- dispute reviewers
- protocol contributors

Governance should be transparent.

No single corporation should control the entire network.

Community governance can inform trust and participation decisions, but it does not replace courts, payment-provider dispute processes, consumer protection law, professional regulation, or legal liability. See [Governance](docs/governance.md) and [Liability Boundaries](docs/liability-boundaries.md).

## 25. Why Non-Profit and Open Source?

Because the agent economy may become basic infrastructure.

If AI-to-AI commerce becomes the next layer of the internet, it should not be fully controlled by a single company.

ARC should be:

- open
- forkable
- auditable
- community-governed
- locally adaptable
- human-centered

The goal is not to build another closed marketplace.

The goal is to explore an open commerce protocol for the AI agent era.

## 26. Current Status

ARC Protocol is currently an experimental documentation and mock-artifact project.

It is not production-ready.

It does not currently provide:

- real payments
- real delivery
- legal guarantees
- verified identity
- production-grade security

An initial documentation baseline exists, but identity, discovery, incentives, governance, liability, and full protocol interoperability remain unresolved.

It is a research-oriented proposal for exploring:

- AI-to-AI commerce
- human-approved transactions
- agent reputation
- community dispute resolution
- open commerce protocols

## 27. Roadmap

### Stage 0 — Philosophy and Protocol Draft

- README
- architecture
- protocol concepts
- governance model
- reputation model

### Stage 1 — Local MVP

- consumer agent
- merchant agent simulation
- logistics agent simulation
- approval UI
- transaction log

### Stage 2 — Identity and Reputation

- agent profile
- public key identity
- signed offers
- verified review model
- reputation score

### Stage 3 — Community Governance

- fraud report
- dispute case
- community decision
- suspension flow

### Stage 4 — Payment Integration

- mock payment first
- then payment provider integration
- human approval required

### Stage 5 — Local Commerce Pilot

- small local merchant demo
- limited geography
- no full automation

### Stage 6 — Open Agent Commerce Network

- multiple communities
- multiple merchant agents
- multiple logistics agents
- interoperability tests

## 28. Design Principle

ARC should avoid becoming a dark pattern machine.

The system should not optimize only for:

- more clicks
- more spending
- emotional manipulation
- addictive behavior
- hidden advertising

Instead, ARC should optimize for:

- trust
- clarity
- human approval
- transparent comparison
- fair reputation
- lower transaction friction
- community accountability

## 29. Manifesto

We believe AI agents will become a new interface of commerce.

But commerce should not become a fully automated black box.

Humans must remain in control.

Communities must be able to judge trust.

Merchants should not be trapped under advertising monopolies.

Users should not be manipulated by invisible algorithms.

Agents should help people compare, negotiate, and coordinate — not replace human sovereignty.

ARC Protocol is a small experiment toward that future.

An open, community-driven, human-approved commerce network for the agent era.

## 30. License

This project is licensed under the Apache License 2.0.

See the LICENSE file for details.

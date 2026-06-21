# ARC Protocol: Architecture

> **Status:** Draft v1.0
> **Purpose:** Technical architecture and system design reference
> For philosophy and motivation, see [philosophy.md](./philosophy.md).

---

## 1. Design Philosophy

ARC is not designed to replace existing infrastructure.

It is designed to connect existing infrastructure — payment providers, map APIs, identity systems, communication protocols — into an open, interoperable layer for agent-to-agent commerce.

Three principles guide every architectural decision:

- **Speed over purity.** Real-time commerce cannot wait for blockchain consensus. Use existing fast infrastructure wherever possible.
- **Hybrid over dogmatic.** Full decentralization is not required from day one. A realistic hybrid model is more valuable than an ideologically pure system that never ships.
- **Human approval as a hard constraint.** No architectural shortcut should bypass the requirement for explicit human confirmation of significant transactions.
- **Idle by default.** Agents are not continuously reasoning processes. Presence is established on contact, not maintained around the clock, keeping the cost of participation proportional to use (see §5.5).

### 1.1 Database-First Boundary

ARC's hybrid approach starts with standard databases and existing infrastructure. Blockchain remains optional and should be considered only where shared verification is worth its additional complexity.

| Use Case | Blockchain | Standard DB |
|----------|------------|-------------|
| Real-time offer negotiation | No | Primary |
| Session and payment state | No | Primary |
| Routine reputation records | No | Primary |
| Reputation integrity checkpoints | Optional | Primary |
| Dispute transparency checkpoints | Optional | Primary |
| Agent identity proof | Optional | Primary |
| Governance transparency checkpoints | Optional | Primary |

ARC is DB-first and blockchain-minimal. No core commerce flow depends on on-chain execution or governance.

---

## 2. System Overview

```
+----------------------------------------------------------+
|                      Human User                          |
|              smartphone / browser approval               |
+-----------------------------+----------------------------+
                              |
                              ▼
+----------------------------------------------------------+
|                    Consumer Agent                        |
|         intent parsing · offer comparison · filtering    |
+-----------------------------+----------------------------+
                              |
              P2P / WebRTC / API / Relay
                              |
          +-------------------+-------------------+
          |                                       |
          ▼                                       ▼
+-------------------+                 +-------------------+
|   Merchant Agent  |  ◄────────────► |  Logistics Agent  |
| price·stock·offer |                 | pickup·delivery   |
+--------+----------+                 +----------+--------+
         |                                       |
         +-------------------+-------------------+
                             |
                             ▼
+----------------------------------------------------------+
|           Reputation & Identity Layer                    |
|   public keys · signed records · verified transactions   |
+----------------------------------------------------------+
                             |
                             ▼
+----------------------------------------------------------+
|           Community Governance Layer                     |
|   fraud report · dispute review · suspension · appeal    |
+----------------------------------------------------------+
                             |
                             ▼
+----------------------------------------------------------+
|                   Payment Provider                       |
|     Google Pay · Apple Pay · Stripe · Toss · local       |
+----------------------------------------------------------+
```

---

## 3. Agent Roles

### 3.1 Consumer Agent

Represents the user. Acts on user-defined intent and constraints.

Responsibilities:
- Parse natural language requests into structured queries
- Contact merchant and logistics agents
- Compare offers against user preferences
- Filter unsafe or low-reputation offers
- Prepare a recommendation with auditable reasoning
- Request human approval before any payment
- Submit reputation events after transaction completion

**Hard constraint:** The consumer agent must not execute payment without explicit human approval. A future implementation may explore user-defined, auditable low-risk pre-authorization rules as a limited exception, not the default.

### 3.2 Merchant Agent

Represents a store, seller, or service provider.

Responsibilities:
- Expose product or service data in structured offer format
- Respond to price and availability queries
- Sign offers with merchant identity key
- Negotiate discounts or bundle conditions
- Maintain response reliability and reputation

### 3.3 Logistics Agent

Represents delivery, transport, or courier services.

Responsibilities:
- Respond to pickup and delivery queries
- Provide estimated times and fees
- Sign delivery commitments
- Submit proof of completion
- Maintain delivery reputation metrics

### 3.4 Community Governance Agent

Represents a local or regional community.

Responsibilities:
- Receive and process fraud reports
- Coordinate dispute review
- Manage agent suspension and appeal
- Maintain community reputation standards

---

## 4. Message Types

All agent communication uses typed, signed JSON messages.

| Type | Direction | Purpose |
|------|-----------|---------|
| `offer_request` | Consumer → Merchant | Query for product/service availability and price |
| `offer_response` | Merchant → Consumer | Structured offer with price, conditions, signature |
| `logistics_request` | Consumer → Logistics | Query for pickup/delivery availability |
| `logistics_response` | Logistics → Consumer | Delivery time, fee, and commitment |
| `approval_request` | Consumer Agent → Human | Present best offer for human confirmation |
| `approval_confirmed` | Human → Consumer Agent | Signed approval to proceed with payment |
| `payment_intent` | Consumer Agent → Payment Provider | Initiate payment after human approval |
| `reputation_event` | Any party → Reputation Layer | Submit verified transaction rating |
| `dispute_report` | Any party → Governance Layer | Report fraud or transaction failure |
| `suspension_notice` | Governance → Agent | Notify agent of suspension decision |

These are transport message types, not stored records. Under the canonical object model the records that persist are Events: `offer_response` and `reputation_event` are `ATTEST`, `dispute_report` is `CHALLENGE`, and `suspension_notice` is an `ADJUDICATE` (`gov.*`); requests, `payment_intent`, and similar notices are transport and are not stored. See [event-registry.md](./event-registry.md).

For the full exploratory message type list and lifecycle flow, see [protocol.md](./protocol.md).

### 4.1 Transaction Lifecycle States

Transactions are not binary. A transaction may move through several states:

| State | Description |
|-------|-------------|
| `pending_approval` | Offer prepared, awaiting human confirmation |
| `approved` | Human confirmed, payment initiated |
| `fulfilled` | Delivery or service completed |
| `disputed` | One or more parties opened a dispute |
| `refund_partial` | Partial refund issued after resolution |
| `refund_full` | Full refund issued after resolution |
| `cancelled` | Transaction cancelled before fulfillment |
| `expired` | Offer or approval window lapsed without action |

These states are not stored fields. They are a projection over the transaction's events (see [object-model.md](./object-model.md) §4).

Refund and dispute rates are relevant reputation signals and should remain visible to users evaluating an offer.

### 4.2 Payment Boundary

ARC does not prescribe a universal payment provider. It is not a payment network, card network, wallet, banking system, or settlement rail.

Payment infrastructure varies across countries, regulations, markets, and merchant categories. ARC is designed to interoperate with existing and future payment systems rather than replace them.

ARC focuses on the trust and coordination layers around payment execution: approval, identity, reputation, governance, discovery, interoperability, and signed records. Actual payment execution remains the responsibility of payment providers.

Any agent-mediated payment should remain blocked until explicit human approval exists, or until a user-defined, auditable authorization rule applies. ARC should not treat payment automation as the default.

---

## 5. Communication Layer

### 5.1 Primary: WebRTC DataChannel

Agent-to-agent communication uses WebRTC DataChannel for direct peer-to-peer messaging where possible.

Advantages:
- Low latency
- No central server required for data transit
- Suitable for real-time offer negotiation

### 5.2 Fallback: WebSocket Relay

When direct P2P is not available (NAT traversal failure, mobile network constraints), communication falls back to a relay server using WebSocket.

ARC does not require full decentralization. Relay servers are acceptable and pragmatic.

### 5.3 Asynchronous Inbox Alternative

For scenarios where real-time negotiation is unnecessary, such as service bookings or non-urgent procurement, an asynchronous inbox may be more appropriate than persistent connections.

An implementation could accept an `offer_request` through an HTTP endpoint and respond through a webhook or polling flow. This can reduce mobile connection overhead and avoid requiring a persistent P2P channel.

ARC does not mandate one communication model. Implementations may use real-time P2P, relay-based communication, asynchronous inboxes, or combinations appropriate to their context.

Relay infrastructure is pragmatic but may expose message metadata to its operator. Communities operating relay services should document their policies.

### 5.4 Message Format

All agent messages are structured JSON with mandatory signature fields:

```json
{
  "message_id": "msg_001",
  "type": "offer_request",
  "from_agent": "consumer_abc",
  "to_agent": "merchant_xyz",
  "payload": {
    "query": "coffee and sandwich",
    "budget": 10.00,
    "currency": "USD",
    "constraints": ["no spicy", "delivery under 30min"]
  },
  "timestamp": "2026-01-01T12:00:00Z",
  "signature": "ed25519:consumer_abc:..."
}
```

### 5.5 Agent Presence and the Wake Handshake

Agents do not need to remain continuously reasoning. An agent publishes a reachable endpoint to a discovery backend (§6) and may otherwise stay idle — holding no persistent connection and running no continuous inference loop. A counterparty makes contact, the agent wakes, and a lightweight handshake establishes that it is reachable and what it can currently do, before either side commits compute to negotiation:

```txt
registry endpoint -> idle -> contact (knock) -> wake -> presence check -> capability exchange -> negotiation
```

This sequence spans three concerns that should not be conflated:

- **Transport.** The contact, presence, and capability messages are ephemeral transport, not events. They assert no truth, grant no permission, and enter no log or projection ([event-registry.md](./event-registry.md) §2.3 — requests are not events). No signed Event exists until negotiation yields one: an `ATTEST` offer or an `AUTHORIZE` approval. Any of §5.1–§5.3 (P2P, relay, async inbox) may carry the wake.
- **Architecture.** Presence is established on contact rather than maintained continuously. The handshake is the bridge between discovery (§6, which locates an endpoint) and the message layer (§5.4, which carries signed exchanges). It introduces no new message type beyond a reachability probe and a capability response.
- **Economics.** Continuous reasoning is an agent's dominant operating cost, and an always-on reasoning process per merchant is infeasible for small local participants. Idle-by-default makes the cost of presence proportional to actual contact rather than wall-clock uptime — the same DB-first, low-cost stance as §1.1, and a precondition for the local-commerce cost model ([bootstrap-and-incentives.md](./bootstrap-and-incentives.md)).

Real-time availability — whether the merchant is open, the kitchen is ready, an item is in stock — belongs in the capability response, not in a signed record: it is volatile live state, not an Event. Durable capabilities (service categories, delivery radius, accepted payment methods, hours) may instead be carried as ordinary `ATTEST` evidence where a counterparty needs them after the fact.

---

## 6. Discovery Layer

How agents find each other is as important as how they communicate.

ARC does not impose a single discovery mechanism. Communities may operate their own discovery backends.

### 6.1 Discovery Methods

| Method | Description |
|--------|-------------|
| Local community registry | Community-operated merchant directory for a geographic area |
| Map provider integration | Google Maps, Naver Map, OpenStreetMap for location-based discovery |
| Reputation-weighted index | Discovery sorted by verified reputation score |
| Category index | Domain-specific registries (food, logistics, services) |
| Direct agent address | Known agent ID for direct contact |

### 6.2 Discovery Backend Switching

Users may configure which discovery backend their consumer agent uses.

If a user believes a discovery backend is biased or compromised, they can switch to an alternative without changing anything else in the system. This is a core anti-monopoly design feature.

### 6.3 Sponsored Discovery

Merchants may pay to appear higher in discovery results. This is permitted under ARC, with one requirement: the sponsored placement must be explicitly declared.

```json
{
  "agent_id": "merchant_abc",
  "discovery_rank": 1,
  "sponsored": true,
  "sponsored_weight": 0.15
}
```

Undisclosed sponsored placement is a protocol violation.

### 6.4 Discovery Infrastructure Sustainability

Discovery infrastructure is a public goods problem. Open directories, indexes, relay endpoints, moderation queues, and reputation displays create value for many participants, but the cost of operating them does not disappear. ARC does not assume that merchants alone must pay for this infrastructure.

Possible funding and operation models to study may include:

- community-operated directories
- municipal or public-interest infrastructure
- non-profit cooperatives
- voluntary member dues
- modest listing fees where appropriate
- sponsored discovery with explicit disclosure
- merchant-hosted or association-hosted registries
- consumer-supported or donation-supported discovery tools

For small merchants, the most attractive ARC-compatible systems may be those that reduce platform dependency, lower intermediary overhead, improve settlement transparency, and preserve reputation portability. However, ARC should not claim that all merchants will participate or that infrastructure can be free. The practical question is how coordination costs can be made more transparent, portable, and less extractive than closed platform models.

These are practical questions for communities, not protocol-level economic requirements.

### 6.5 Privacy Principles

Consumer agents may handle sensitive data such as location, purchase history, dietary preferences, and budget constraints. ARC does not define a complete privacy specification at this stage, but identifies directional principles:

- **Local-first storage.** User preference and behavioral data should default to storage on the user's device.
- **Minimum necessary sharing.** Agents should share only the data needed for a specific transaction.
- **Explicit consent for retention.** Retaining data beyond the immediate transaction should require opt-in.
- **User data portability.** Users should be able to export or delete their data from an ARC-compatible implementation.

These are design intentions rather than finalized protocol requirements.

---

## 7. Identity Layer

### 7.1 Agent Identity Structure

```json
{
  "agent_id": "merchant_abc_001",
  "owner_type": "business",
  "identity_provider": "google",
  "public_key": "ed25519:...",
  "community": "seoul-local-commerce",
  "status": "verified",
  "created_at": "2026-01-01T00:00:00Z",
  "last_active": "2026-06-01T10:00:00Z"
}
```

Here `status` is shown inline for readability, but it is a projected view rather than a stored field: it is folded from the key's `KEY` lifecycle events, credential attestations, and any commons `ADJUDICATE`. The stored unit is the Event. See [object-model.md](./object-model.md) and [event-registry.md](./event-registry.md).

### 7.2 Signed Offers

Every offer must be cryptographically signed:

```json
{
  "offer_id": "offer_001",
  "merchant_agent_id": "merchant_abc_001",
  "items": [
    { "name": "Americano", "price": 3.50 },
    { "name": "Club Sandwich", "price": 6.00 }
  ],
  "total_price": 9.50,
  "estimated_ready_time": "8 minutes",
  "expires_at": "2026-01-01T12:05:00Z",
  "sponsored_weight": 0.0,
  "sponsored_disclosed": true,
  "signature": "ed25519:merchant_abc_001:..."
}
```

---

## 8. Reputation Layer

### 8.1 Reputation Event

```json
{
  "event_id": "rep_001",
  "agent_id": "merchant_abc_001",
  "transaction_id": "tx_001",
  "rating": 5,
  "verified": true,
  "metrics": {
    "on_time": true,
    "accurate_description": true,
    "refund_requested": false
  },
  "comment": "Fast and accurate.",
  "created_at": "2026-01-01T13:00:00Z",
  "reviewer_signature": "ed25519:consumer_xyz:..."
}
```

### 8.2 Reputation Metrics

| Metric | Description |
|--------|-------------|
| `completion_rate` | % of accepted offers fulfilled |
| `refund_rate` | % of transactions resulting in refund |
| `dispute_rate` | % of transactions escalated to dispute |
| `on_time_rate` | % of deliveries within estimated time |
| `response_speed` | Average time to respond to offer requests |
| `community_trust_score` | Composite signal projected from community governance events, not a stored universal score |

These metrics are projection outputs computed on demand from reputation events, not fields stored on the agent. The reputation event in §8.1 is the stored record (an `ATTEST` of an outcome); the score is a fold over such events. See [object-model.md](./object-model.md) and [event-registry.md](./event-registry.md).

---

## 9. Human Approval Layer

### 9.1 Approval Request

```
┌─────────────────────────────────────┐
│         Approve this order?         │
├─────────────────────────────────────┤
│ Merchant:    Bean & Bread (4.9 ★)   │
│ Items:       Americano + Sandwich   │
│ Total:       $9.50                  │
│ Delivery:    ~28 minutes            │
│ Logistics:   QuickRide (4.7 ★)      │
│ Delivery fee: $2.00                 │
│ Grand total: $11.50                 │
├─────────────────────────────────────┤
│ Why selected:                       │
│ Budget met · Top reputation ·       │
│ Fastest available option            │
├─────────────────────────────────────┤
│  [Approve]          [Decline]       │
└─────────────────────────────────────┘
```

### 9.2 User-Defined Approval Policies

```
Default: manual approval for payments
Consider for explicit pre-authorization: low-risk routine requests under $5.00
Always require per-transaction approval: new merchants with no reputation
Block: agents with dispute rate above 10%
```

Any pre-authorized low-risk rule remains user-defined, reviewable, and subordinate to the requirement for explicit approval of meaningful economic actions.

---

## 10. Technical Stack (Recommended)

### Frontend
- Next.js + React
- Tailwind CSS
- PWA support for mobile approval

### Backend
- Node.js (Fastify or Express)
- PostgreSQL — persistent state
- Redis — session and reputation cache
- WebSocket server — relay fallback

### Agent Runtime
- Initial MVP: rule-based logic + LLM responses
- LangGraph or CrewAI for multi-agent orchestration
- Local LLM (Ollama, llama.cpp) for privacy-sensitive operations
- OpenAI / DeepSeek API for general reasoning

### Cryptography
- Ed25519 key pairs per agent
- Signed offers and approval records
- Transaction hash records
- Optional blockchain checkpoints for reputation milestones

---

## 11. MVP Architecture

### MVP Scope

| Component | MVP Implementation |
|-----------|-------------------|
| Consumer Agent | LLM-powered chat interface |
| Merchant Agent | Simulated responses from static data |
| Logistics Agent | Simulated availability and timing |
| Payment | Mock confirmation (no real money) |
| Reputation | Contextual reputation summary (projected, not a stored score) |
| Identity | Simple API key per agent |
| Approval UI | Web button triggering mock payment |

### MVP Success Criteria

A user can type a request, receive competing offers from simulated agents, see a comparison with auditable reasoning, approve one option, and see a mock transaction logged with a reputation event.

---

## 12. Repository Structure

This repository is currently organized as a protocol research corpus, not a production monorepo.

```
arc-protocol/
├── README.md            ← project compass and entry point
├── LICENSE, CONTRIBUTING.md
├── docs/                ← normative models, tradeoffs, custody, threat model, glossary, roadmap
│   │                      (object-model, event-registry, authority-and-conflict, key-custody,
│   │                       delegation-and-spending-mandates, identity, reputation, governance,
│   │                       trust-model-tradeoffs, threat-model, future-protocol-spec, …)
│   └── adjacent-ideas/  ← exploratory essays
├── examples/            ← executable probes and reference clients
│   ├── reference-client/             browser client for observing authority/approval bands
│   ├── canon-fold-demo/, canon-ts/   canonicalization and type-level custody locks
│   ├── authority-revocation-demo/, threshold-authority-demo/, cache-discipline-demo/
│   ├── end-to-end-demo/, local-commerce-demo/
├── diagrams/            ← discovery-topology.md, dispute-flow.md, transaction-lifecycle.md
└── apps/, packages/     ← reserved placeholders, not yet populated
```

The earlier `apps/web` and `packages/*` layout was an aspirational sketch of a reference implementation, not a current commitment; treat it as non-normative. The README is the canonical map of the corpus.

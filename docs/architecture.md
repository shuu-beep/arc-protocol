# ARC Protocol: Commerce Reference Architecture

> **Status:** Draft v1.0
> **Purpose:** Non-normative technical architecture for the flagship Commerce application
> For philosophy and motivation, see [philosophy.md](./philosophy.md).

---

## 1. Design Philosophy

ARC is not designed to replace existing infrastructure.

This reference architecture connects existing infrastructure — payment providers, map APIs, identity systems, communication protocols — in an agent-to-agent Commerce application of ARC's authority layer.

> **Scope: commerce reference architecture, not the full protocol architecture.**
> This is drawn for commerce because that is ARC's first implementation, not
> because Commerce defines ARC's protocol boundary. Two things are mixed here on purpose:
> commerce-specific roles (consumer / merchant / logistics / payment) and
> reusable authority/evidence seams and application concerns (communication,
> discovery, identity, human approval, audit). Read "commerce" throughout as
> the first load placed on those general seams — the first application of a
> general authority, approval, and audit layer for AI agents — not as the
> protocol's boundary ([README §7](../README.md#7-flagship-application-commerce)).

Four current design principles guide this reference architecture:

- **Low-latency Commerce operations.** Use existing fast infrastructure wherever possible.
- **Deployment pragmatism.** A deployment selects infrastructure appropriate to its named profile; the base protocol does not mandate a topology.
- **Current Coverage as a hard constraint.** No architectural shortcut should bypass human-authored coverage for consequential acts, whether exact-target or valid mandate-scoped authority.
- **Idle by default.** In this reference profile, presence is established on contact rather than maintained continuously (see §5.5). Cost effects remain unmeasured.

### 1.1 Storage Boundary

ARC does not prescribe storage infrastructure. The protocol requires signed
events and recomputable projections, not a specific backend — ordinary
databases, append-only logs, and checkpointing mechanisms are all valid
implementation choices, selected per deployment.

The table below is a non-normative illustration of one consequence: no core
commerce flow needs on-chain execution. A shared cryptographic checkpoint (a
chain among them) is at most an optional aid where cross-party verification is
worth its added complexity — never a requirement of the protocol.

| Use Case | Shared checkpoint (optional) | Ordinary store |
|----------|------------------------------|----------------|
| Real-time offer negotiation | No | Primary |
| Session and payment state | No | Primary |
| Routine reputation records | No | Primary |
| Reputation integrity checkpoints | Optional | Primary |
| Dispute transparency checkpoints | Optional | Primary |
| Agent identity evidence | Optional | Primary |
| Governance transparency checkpoints | Optional | Primary |

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
| public keys · signed evidence · named projections       |
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
- Filter offers under declared application-policy thresholds
- Prepare a recommendation with inspectable inputs and explanation
- Require Current Coverage before any payment
- Submit Canon Events carrying reputation evidence after transaction completion

**Commerce profile constraint:** The consumer agent must not execute payment unless the exact act has Current Coverage. Fresh confirmation is this reference application's default; a valid user-authored scoped mandate may also provide coverage.

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
- Submit completion evidence or claims
- Maintain delivery reputation metrics

### 3.4 Community Governance Agent

Carries decisions from a declared local or regional community process. The interface itself has no authority; a decision has effect only through an authorized `ADJUDICATE` under the named profile.

Responsibilities:
- Receive and process fraud reports
- Coordinate dispute review
- Manage agent suspension and appeal
- Maintain community reputation standards

---

## 4. Message Types

This Commerce reference profile represents agent communication as typed, signed JSON messages. Other profiles may select different serialization and signature suites.

| Type | Direction | Purpose |
|------|-----------|---------|
| `offer_request` | Consumer → Merchant | Query for product/service availability and price |
| `offer_response` | Merchant → Consumer | Structured offer with price, conditions, signature |
| `logistics_request` | Consumer → Logistics | Query for pickup/delivery availability |
| `logistics_response` | Logistics → Consumer | Delivery time, fee, and commitment |
| `approval_request` | Consumer Agent → Human | Present best offer for human confirmation |
| `approval_confirmed` | Human → Consumer Agent | Signed act-specific approval record |
| `payment_intent` | Consumer Agent → Payment Provider | Initiate payment after Current Coverage |
| `reputation_event` | Any party → Reputation Layer | Submit an evidence-linked transaction rating claim |
| `dispute_report` | Any party → Governance Layer | Report fraud or transaction failure |
| `suspension_notice` | Governance → Agent | Notify agent of suspension decision |

These are Commerce-profile transport message types, not stored records. Under the canonical object model the records that persist are Events: `offer_response` and `reputation_event` are `ATTEST`, `dispute_report` is `CHALLENGE`, and `suspension_notice` is an `ADJUDICATE` (`gov.*`); requests, `payment_intent`, and similar notices are transport and are not stored. See [event-registry.md](./event-registry.md).

For the full exploratory message type list and lifecycle flow, see [protocol.md](./protocol.md).

### 4.1 Named Commerce Lifecycle Projection

Transactions are not binary. A transaction may move through several states:

| State | Description |
|-------|-------------|
| `pending_approval` | Offer prepared, awaiting human confirmation |
| `approved` | The exact act has Current Coverage and payment may be requested |
| `fulfilled` | Available evidence contains the profile's fulfillment claim |
| `disputed` | One or more parties opened a dispute |
| `refund_partial` | Partial refund issued after resolution |
| `refund_full` | Full refund issued after resolution |
| `cancelled` | Transaction cancelled before fulfillment |
| `expired` | Offer or approval window lapsed without action |

These states are not stored fields. They are outputs of the named Commerce lifecycle Projection over its declared Event set and ordering/as-of inputs (see [object-model.md](./object-model.md) §4).

Refund and dispute rates are relevant reputation signals and should remain visible to users evaluating an offer.

### 4.2 Payment Boundary

ARC does not prescribe a universal payment provider. It is not a payment network, card network, wallet, banking system, or settlement rail.

Payment infrastructure varies across countries, regulations, markets, and merchant categories. ARC selects no payment provider; integrations and their compatibility requirements are Commerce-profile choices.

This Commerce architecture applies ARC authority and signed-evidence semantics around payment execution. Actual payment execution remains the responsibility of payment providers, and provider records are external claims rather than proof supplied by ARC.

This reference application blocks an agent-mediated payment unless the exact act has Current Coverage from an act-specific authorization or a valid scoped mandate. Coverage does not itself prove payment execution or outcome truth.

---

## 5. Communication Layer

### 5.1 Reference-Profile Primary: WebRTC DataChannel

This reference profile uses WebRTC DataChannel for direct peer-to-peer messaging where possible.

Advantages:
- Low latency
- No central server required for data transit
- Suitable for real-time offer negotiation

### 5.2 Reference-Profile Fallback: WebSocket Relay

In this reference profile, direct-P2P failure (NAT traversal failure, mobile network constraints) falls back to a relay server using WebSocket.

ARC does not require full decentralization. Relay servers are acceptable and pragmatic.

### 5.3 Asynchronous Inbox Alternative

For scenarios where real-time negotiation is unnecessary, such as service bookings or non-urgent procurement, an asynchronous inbox may be more appropriate than persistent connections.

An implementation could accept an `offer_request` through an HTTP endpoint and respond through a webhook or polling flow. This can reduce mobile connection overhead and avoid requiring a persistent P2P channel.

ARC does not mandate one communication model. Implementations may use real-time P2P, relay-based communication, asynchronous inboxes, or combinations appropriate to their context.

Relay infrastructure is pragmatic but may expose message metadata to its operator. Communities operating relay services should document their policies.

### 5.4 Reference-Profile Message Format

This reference profile uses structured JSON with its selected signature fields:

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

- **Transport.** The contact, presence, and capability messages are ephemeral transport, not canonical Events ([event-registry.md](./event-registry.md) §2.3). They may carry claims, but they do not enter an ARC Projection unless separately recorded or attested. Any of §5.1–§5.3 (P2P, relay, async inbox) may carry the wake.
- **Architecture.** Presence is established on contact rather than maintained continuously. The handshake is the bridge between discovery (§6, which locates an endpoint) and the message layer (§5.4, which carries signed exchanges). It introduces no new message type beyond a reachability probe and a capability response.
- **Economics.** Idle-by-default may reduce inference and connection costs compared with continuous operation. The dominant cost, feasibility for small participants, and total savings are not established; they remain Commerce application research questions ([bootstrap-and-incentives.md](./bootstrap-and-incentives.md)).

Real-time availability — whether the merchant is open, the kitchen is ready, an item is in stock — belongs in the capability response, not in a signed record: it is volatile live state, not an Event. Durable capabilities (service categories, delivery radius, accepted payment methods, hours) may instead be carried as ordinary `ATTEST` evidence where a counterparty needs them after the fact.

---

## 6. Commerce Discovery Layer

How agents find each other is as important as how they communicate.

The base protocol does not define discovery. This Commerce application allows multiple discovery mechanisms, including community-operated backends.

Discovery establishes contactability, not authority: a backend may surface endpoints, while observers evaluate identity, permission, and fulfillment-capacity claims under named policies and available evidence. Appearing in a directory establishes none of those claims by itself.

### 6.1 Discovery Methods

| Method | Description |
|--------|-------------|
| Local community registry | Community-operated merchant directory for a geographic area |
| Map provider integration | Google Maps, Naver Map, OpenStreetMap for location-based discovery |
| Reputation-weighted index | Discovery sorted by a named reputation Projection output |
| Category index | Domain-specific registries (food, logistics, services) |
| Direct agent address | Known agent ID for direct contact |

### 6.2 Discovery Backend Switching

Users may configure which discovery backend their consumer agent uses.

If a user believes a discovery backend is biased or compromised, an implementation may offer an alternative. Switching depends on compatible schemas, identity references, evidence, and ranking semantics; it is not guaranteed by base ARC.

### 6.3 Sponsored Discovery

Merchants may pay to appear higher in this Commerce application's discovery results. Its named discovery policy requires sponsored placement to be explicitly declared.

```json
{
  "agent_id": "merchant_abc",
  "discovery_rank": 1,
  "sponsored": true,
  "sponsored_weight": 0.15
}
```

Undisclosed sponsored placement violates that named Commerce discovery policy, not the base protocol.

### 6.4 Discovery Infrastructure Sustainability

Discovery infrastructure has operating costs that may be shared across participants. The Commerce research does not select who must fund directories, indexes, relay endpoints, moderation queues, or reputation displays.

Possible funding and operation models to study may include:

- community-operated directories
- municipal or public-interest infrastructure
- non-profit cooperatives
- voluntary member dues
- modest listing fees where appropriate
- sponsored discovery with explicit disclosure
- merchant-hosted or association-hosted registries
- consumer-supported or donation-supported discovery tools

Potential effects on platform dependency, intermediary overhead, settlement visibility, and reputation portability require testing with merchants and operators. The corpus establishes no preference, cost reduction, participation outcome, or comparison with closed platforms.

These are Commerce application questions for communities, not protocol-level economic requirements.

### 6.5 Privacy Principles

Consumer agents may handle sensitive data such as location, purchase history, dietary preferences, and budget constraints. This Commerce reference architecture does not define a complete privacy profile, but identifies directional application principles:

- **Local-first storage.** User preference and behavioral data should default to storage on the user's device.
- **Minimum necessary sharing.** Agents should share only the data needed for a specific transaction.
- **Explicit consent for retention.** Retaining data beyond the immediate transaction should require opt-in.
- **User data portability.** Users should be able to export or delete their data from an ARC-compatible implementation.

These are application design intentions rather than finalized protocol requirements.

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
  "status": "profile_check_passed",
  "created_at": "2026-01-01T00:00:00Z",
  "last_active": "2026-06-01T10:00:00Z"
}
```

Here `status` is shown inline for readability, but it is a projected view rather than a stored field: it is folded from the key's `KEY` lifecycle events, credential attestations, and any commons `ADJUDICATE`. The stored unit is the Event. See [object-model.md](./object-model.md) and [event-registry.md](./event-registry.md).

### 7.2 Signed Offers in This Commerce Profile

This profile represents each offer as a cryptographically signed record; Ed25519 below is a reference-fixture choice, not a universal ARC signature suite:

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

## 8. Named Commerce Reputation Projection

### 8.1 Legacy Commerce Reputation-Input Example

This illustrative application-shaped payload is not a Canon Event envelope. A Canon-aligned profile would carry the claim in an `ATTEST` or use an authorized `ADJUDICATE` as governance evidence.

```json
{
  "event_id": "rep_001",
  "agent_id": "merchant_abc_001",
  "transaction_id": "tx_001",
  "rating": 5,
  "declared_record_checks_passed": true,
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

These metrics are outputs of the named Commerce reputation Projection computed on demand from its declared evidence set, not fields stored on the agent. In the §8.1 example, `declared_record_checks_passed` is an application label for a bounded record check; a corresponding `ATTEST` would claim an outcome but would not prove it. See [object-model.md](./object-model.md) and [event-registry.md](./event-registry.md).

---

## 9. Commerce Approval UI

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

These are Commerce application policies. Every consequential act still requires Current Coverage: either exact act-specific authority or a valid user-authored scoped mandate.

---

## 10. Non-Normative MVP Stack Sketch

> **Not prescribed by the protocol.** ARC defines protocol semantics, not
> infrastructure — none of the choices below are required for an implementation
> to claim Core Event Conformance, Named Projection Conformance, or Named
> Functional Profile Conformance. This is one illustrative stack for the Stage 1
> Commerce MVP, recorded so that build is concrete. No complete conformance claim
> is made for this untested stack sketch.

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

A user can type a request, receive competing offers from simulated agents, inspect the fixture inputs and comparison explanation, approve one option, and see a mock transaction logged with an application standing input.

---

## 12. Repository Structure

This repository is currently organized as a protocol research corpus, not a production monorepo.

```
arc-protocol/
├── README.md            ← project compass and entry point
├── LICENSE, CONTRIBUTING.md
├── docs/                ← normative, explanatory, application, historical, and research material
│   │                      (README identifies the authority hierarchy and each document's role)
│   └── adjacent-ideas/  ← exploratory essays
├── examples/            ← executable validation probes and reference clients
│   ├── reference-client/             browser client for observing authority/approval bands
│   ├── canon-fold-demo/, canon-ts/   canonicalization and type-level authority constraints
│   ├── authority-revocation-demo/, threshold-authority-demo/, cache-discipline-demo/
│   ├── end-to-end-demo/, local-commerce-demo/
├── diagrams/            ← explanatory application diagrams
└── apps/, packages/     ← reserved placeholders, not yet populated
```

The earlier `apps/web` and `packages/*` layout was an aspirational sketch of a reference implementation, not a current commitment; treat it as non-normative. The README is the current map of the corpus and its authority hierarchy.

# ARC Protocol: Future Protocol Specification Boundaries

> **Status:** Exploratory planning note
>
> **Purpose:** Clarify what ARC would need before it can be treated as a complete protocol specification.
>
> This document was added in response to critical review. It narrows the gap between ARC as a protocol-oriented design project and ARC as a future implementable protocol.

---

## 1. Current Boundary

ARC Protocol is currently a protocol-oriented design project, not a complete protocol specification.

The existing documents describe philosophy, actors, message intentions, state transitions, threat models, and mock failure artifacts. They do not yet define a normative wire protocol, compatibility test suite, transport profile, or conformance process.

This distinction matters. A useful protocol must eventually define not only what should happen, but how independent implementations can interoperate and fail safely.

## 2. Minimum Future Specification Areas

A future ARC protocol specification would need at least the following pieces.

| Area | Future Requirement |
| --- | --- |
| Message envelope | Canonical fields, identifiers, timestamps, sender/receiver identity, signature requirements, and replay protection. |
| Message type registry | Stable definitions for `offer_request`, `offer_response`, `approval_request`, `payment_intent`, `fulfillment_update`, `dispute_report`, and related messages. |
| State machine | Normative transaction states, allowed transitions, terminal states, and invalid-transition handling. |
| Error model | Standard error codes for expired offers, duplicate messages, stale approvals, invalid signatures, payment failure, unavailable logistics, and unsupported versions. |
| Idempotency | Rules preventing repeated requests, double approvals, duplicate payment attempts, and accidental repeated fulfillment authorization. |
| Timeout and expiry | Clock assumptions, expiry validation, retry windows, refreshed-offer handling, and stale-message rejection. |
| Versioning | Backward compatibility, feature negotiation, deprecation rules, and protocol version identifiers. |
| Discovery | How agents find compatible merchants, logistics providers, relays, communities, and discovery backends without assuming one global directory. |
| Transport profile | Transport-agnostic requirements, plus profiles for HTTP/webhook, WebSocket relay, WebRTC DataChannel, or asynchronous inbox flows. |
| Security profile | Signature algorithms, key rotation, compromised-key handling, message integrity, transport authentication, and audit-log requirements. |
| Conformance tests | Reproducible fixtures that verify independent implementations reject unsafe transitions and preserve human approval boundaries. |

## 3. Protocol vs Reference Implementation

A technology stack such as Next.js, React, Node.js, PostgreSQL, Redis, WebSocket, or WebRTC may be useful for a reference implementation.

Those tools are not ARC itself.

ARC should avoid treating any particular framework, database, relay topology, payment provider, map provider, or AI model as part of the protocol unless a future specification explicitly requires it.

A reference implementation may demonstrate one path. A protocol specification must allow multiple compatible implementations.

## 4. Discovery Is Not Yet Solved

Discovery remains one of the hardest unsolved parts of ARC.

Open discovery does not automatically prevent concentration. Multiple discovery backends can reduce single-platform dependency, but they can also create new trust problems: biased indexes, malicious directories, pay-to-play ranking, suppression of new entrants, or backend capture.

A future discovery specification would need to address:

- backend identity and accountability
- sponsored ranking disclosure
- ranking explanation metadata
- user-visible backend selection
- malicious or low-quality backend warnings
- new entrant visibility without Sybil exposure
- portability of merchant profiles across discovery systems

ARC does not currently solve the network bootstrap problem. It does not yet explain how enough consumers, merchants, logistics providers, and discovery backends would join at the same time to create a useful network.

## 5. Concurrency, Inventory, and Reservation

Real commerce is stateful.

A merchant offer may depend on limited inventory, changing price, staff availability, delivery slots, or time-limited capacity. ARC does not yet define how inventory reservations, offer locks, concurrent approvals, or payment retries should work across independent agents.

Future work must examine:

- whether an offer reserves inventory
- how long a reservation remains valid
- whether approval creates a temporary hold
- what happens when two humans approve the same limited offer
- whether refreshed offers require renewed approval
- how payment failure affects reservation state
- how cancellation changes inventory availability

Until these questions are specified, ARC should not claim to solve production commerce coordination.

## 6. Clock and Expiry Trust

ARC relies heavily on expiry times. That creates a clock-trust problem.

A signed `expires_at` value proves that an agent signed a claim about expiry. It does not prove that all participants shared the same clock, that the timestamp was honest, or that network delay did not affect the approval window.

Future work should define:

- accepted timestamp formats
- clock skew tolerance
- source of time assumptions
- expiry validation rules
- whether relays or providers may timestamp receipt
- how to handle delayed messages
- how to present expiry uncertainty to humans

## 7. Intent and Preference Ambiguity

Natural-language requests are not stable protocol input.

A request such as "find lunch nearby" may involve hidden priorities: price, distance, delivery time, taste, dietary restrictions, safety, sponsorship avoidance, merchant reputation, past user habits, or novelty.

Future ARC implementations should distinguish:

- original human text
- parsed canonical intent
- inferred preferences
- explicit constraints
- ranking priorities
- unavailable or uncertain fields
- human corrections before negotiation

No implementation should treat inferred preferences as unquestionable user intent.

## 8. Non-Goals for This Stage

This document does not define a final ARC wire format.

It does not choose a mandatory transport, payment provider, identity provider, blockchain, database, model provider, governance procedure, or ranking algorithm.

Its purpose is narrower: make clear what remains missing before ARC can move from protocol-oriented design toward implementable specification.

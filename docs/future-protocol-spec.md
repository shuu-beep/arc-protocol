# ARC Protocol: Unresolved Specification and Conformance Boundaries

> **Status:** Frozen gap register; not an active implementation plan
>
> **Purpose:** Record what the current corpus does not provide and what would
> require separate approval before any interoperability or production claim.
>
> Active implementation is frozen. Requirements below preserve unresolved
> evidence; they do not announce future delivery.

---

## 1. Current Boundary

ARC is currently an exploratory, implementation-neutral authority protocol, not a complete independently implementable specification.

The existing documents define current Event and authority semantics and describe philosophy, actors, message intentions, Commerce state transitions, threat models, and executable failure artifacts. They do not yet define a normative wire/security profile, compatibility test suite, transport profile, or complete conformance process.

This distinction matters. A future interoperability claim needs shared observable behavior, declared errors, and reproducible conformance vectors.

## 2. Unresolved Specification and Profile Work

Completing ARC's base specification and the separately named Commerce profile requires work in their respective layers below. Commerce rows are not base-protocol requirements.

| Area | Layer | Future Requirement |
| --- | --- | --- |
| Event envelope | Core Event Conformance plus a named encoding/security profile | Normative semantic fields, canonical signing bytes, identifiers, algorithm/version identifiers, errors, and replay behavior. JSON is only a current illustrative encoding. |
| Message type registry | Commerce application/profile | Stable definitions for `offer_request`, `offer_response`, `approval_request`, `payment_intent`, `fulfillment_update`, `dispute_report`, and related Commerce messages. These are not top-level Event types. |
| State machine | Named Commerce Projection/profile | Declared transaction states, allowed transitions, terminal states, ordering/as-of policy, and invalid-transition handling. |
| Error model | Core and named profiles | Shared envelope/version errors where required, plus profile-scoped errors for expired offers, duplicate messages, stale approvals, payment failure, unavailable logistics, and unsupported fields. |
| Idempotency | Named functional profile and implementation | Rules for repeated requests, act-specific approval reuse, duplicate payment attempts, and repeated fulfillment instructions without adding a new Event type. |
| Timeout and expiry | Named clock/deployment profile | Clock assumptions, expiry validation, retry windows, refreshed-offer handling, and stale-message treatment. |
| Versioning | Conformance | Backward compatibility, feature negotiation, deprecation rules, and profile/version identifiers. |
| Discovery | Commerce application/profile | How agents find compatible merchants, logistics providers, relays, communities, and discovery backends without assuming one global directory. |
| Transport profile | Named functional profile and implementation | Transport-independent behavior plus optional profiles for HTTP/webhook, WebSocket relay, WebRTC DataChannel, or asynchronous inbox flows. |
| Security profile | Named security profile | Signature suite, key rotation, compromised-key handling, message integrity, transport authentication, and evidence-surface requirements for the claim being made. No signature suite is selected by base ARC. |
| Conformance tests | Conformance | Reproducible vectors for the explicitly named Core Event, Projection, or Functional Profile claim. |

Use claim names precisely:

- **Core Event Conformance** covers the named Event envelope/security requirements; it does not prove current authority or execution.
- **Named Projection Conformance** identifies the Event set, Projection name/version, policy and ordering/as-of inputs, unsupported behavior, and expected output.
- **Named Functional Profile Conformance** applies only to an explicitly named profile and version.
- **External Record Verification** verifies disclosed records and key provenance without asserting completeness or payload truth.
- **Independently Recomputable Result** requires the declared evidence set/completeness contract and Projection inputs needed by a separate implementation.
- **Publicly Recomputable Result** additionally makes that package public; ARC does not require a public evidence surface.

Every consequential act must have **Current Coverage** from a human-authored `AUTHORIZE`: an act-specific authorization for the unchanged exact target, or an unexpired, unrevoked scoped mandate that covers the act under the named Projection/profile. Material target changes require new coverage.

Three boundaries remain explicit:

- **OPEN — MUST NOT BE IMPLIED BY CURRENT DOCUMENTATION:** quorum member participation is not yet classified universally as either `ATTEST` or `AUTHORIZE`.
- **REQUIRED BEFORE INTEROPERABILITY CLAIM:** a named deterministic mandate profile must define its closed grammar, typed terms, operators, normalization, comparison, attenuation, expiry/material-target, and error semantics with cross-implementation vectors.
- **REQUIRED BEFORE INTEROPERABILITY CLAIM:** atomic cumulative mandate consumption remains unresolved for causally concurrent acts. No lock, reservation, sequencer, or new Event is selected here.

## 3. Protocol, Profiles, and Executable Corpus

A technology stack such as Next.js, React, Node.js, PostgreSQL, Redis, WebSocket, or WebRTC may be useful for an implementation or executable reference corpus.

Those tools are not ARC itself.

ARC should avoid treating any particular framework, database, relay topology, payment provider, map provider, or AI model as part of the protocol unless a future specification explicitly requires it.

The current executable corpus demonstrates selected paths without defining a conformance standard. A protocol specification must allow multiple implementations that make the same explicitly named conformance claim.

## 4. Commerce Discovery Is Not Yet Solved

Discovery remains unresolved for the Commerce flagship application. It is application/profile work, not a base authority primitive.

Open discovery does not automatically prevent concentration. Multiple discovery backends can reduce single-platform dependency, but they can also create risks such as biased indexes, malicious directories, pay-to-play ranking, suppression of new entrants, or backend capture.

A future Commerce discovery profile would need to address:

- backend identity and accountability
- sponsored ranking disclosure
- ranking explanation metadata
- user-visible backend selection
- malicious or low-quality backend warnings
- new entrant visibility without Sybil exposure
- portability of merchant profiles across discovery systems

The Commerce application does not currently solve the network bootstrap problem. It does not yet explain how enough consumers, merchants, logistics providers, and discovery backends would join at the same time to create a useful network.

## 5. Commerce Concurrency, Inventory, and Reservation

The Commerce application is stateful.

A merchant offer may depend on limited inventory, changing price, staff availability, delivery slots, or time-limited capacity. The Commerce reference profile does not yet define how inventory reservations, offer locks, concurrent approvals, or payment retries should work across independent agents.

Future Commerce-profile work would need to examine:

- whether an offer reserves inventory
- how long a reservation remains valid
- whether approval creates a temporary hold
- what happens when two humans approve the same limited offer
- whether refreshed offers require renewed approval
- how payment failure affects reservation state
- how cancellation changes inventory availability

Until these questions are specified, ARC should not claim to solve production commerce coordination.

## 6. Named Clock and Expiry Profiles

The Commerce reference profile and other profiles that use expiry introduce clock and as-of assumptions.

Under a declared security profile, a signed `expires_at` value supports a check that a key signed an expiry claim. It does not establish that all participants shared the same clock, that the timestamp was accurate, or that network delay did not affect the approval window.

A named clock/as-of profile should define:

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

Commerce implementations should distinguish, as application policy:

- original human text
- parsed canonical intent
- inferred preferences
- explicit constraints
- ranking priorities
- unavailable or uncertain fields
- human corrections before negotiation

A named Commerce interface profile may require inferred preferences to remain distinguishable from user-authored constraints.

## 8. Non-Goals for This Stage

This document does not define a final ARC wire format. Current JSON examples are illustrative and do not select a canonical serialization or signing suite.

It does not choose a mandatory transport, payment provider, identity provider, database, model provider, governance procedure, ranking algorithm, public log, or federation topology.

Its purpose is narrower: distinguish missing base-specification work from optional functional profiles and Commerce application work.

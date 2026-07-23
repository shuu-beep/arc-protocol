# ARC Protocol: Object Model

> **Status:** Exploratory foundational draft
>
> **Purpose:** Define the two layers ARC reasons over — the conceptual **Relationship** and the protocol primitive **Event** — and the **Projection** that connects them.
>
> This document sits beneath the rest of the corpus. It fixes *what kind of thing* ARC stores and computes, so that identity, reputation, governance, disputes, approval, and commerce all rest on one substrate rather than inventing their own.
>
> For the authority boundaries these objects must respect, see [authority-and-conflict.md](./authority-and-conflict.md). For the concrete event vocabulary, see [event-registry.md](./event-registry.md). For reputation as a signal, see [reputation.md](./reputation.md). For identity boundaries, see [identity.md](./identity.md).

---

## 1. Status and Scope

This is an exploratory model, not a wire format and not an implementation. It does not define byte layouts, transports, or storage engines.

Its job is narrow and prior to those: name ARC's canonical record object and the derived object it does not treat as authoritative protocol state. Everything in the later documents — reputation scores, identity status, transaction state, trust — should be expressible in terms defined here. Where older documents differ, this document defines the intended conceptual direction. Aligning the remaining documents is deferred to future editorial work.

## 2. Two Layers

ARC reasons over exactly two kinds of object. Keeping them separate is the central discipline of this document.

### 2.1 Relationship — the conceptual primitive

A **Relationship** is a contextual Projection among named parties, actions, observers, and time. Reputation, current authority, and current trust are possible profile-specific readings of that contextual view.

A Relationship is:

- **contextual** — scoped to a category, geography, community, and time window
- **non-aggregated** — there is no single global relationship between two parties, and no global profile of one party
- **evolving and multi-party** — it changes with every relevant event and may involve more than two keys
- **not canonical or authoritative protocol state** — it is derived from declared inputs; implementations may cache it only as a non-authoritative artifact

ARC does not define a Relationship as authoritative stored protocol state.

### 2.2 Event — the protocol primitive

An **Event** is a single, immutable, single-author, timestamped signed statement. It is ARC's only canonical stored record unit. Applications may transmit other messages and implementations may export or cache derived views without making them canonical Events.

An Event is:

- **immutable** — once signed it does not change; corrections are new Events
- **single-author** — attributable to exactly one signing key
- **discrete** — it states one thing at one moment
- **signed** — its integrity and attribution rest on a key (see §7)

Identity claims, offers, approvals, mandates, outcome records, disputes, and governance decisions are all **Events**. They are not competing primitives; they are one record type distinguished by a `type` and a `predicate` (see [event-registry.md](./event-registry.md)).

## 3. Why the Event, Not the Relationship, Is the Protocol Primitive

ARC chooses immutable, attributable Events as its signed primitive because Relationship views are derived, contextual, and policy-dependent. A serialized Relationship snapshot could be signed as a claim, but it would still be an Event rather than authoritative Relationship state. Verifying an Event checks the record under its declared key/security profile; it does not establish a projected Relationship or real-world outcome as true.

ARC has in fact been Event-first since the README: `reputation_event`, `approval_confirmed`, and `dispute_report` are all discrete signed records. This document names that commitment rather than introducing it.

## 4. Projection — How Relationship Is Recovered

A **Projection** is a named deterministic fold over an identified set of Events available to an observer that produces a Relationship view:

```txt
Projection(context, parties, window) = fold(relevant_events)
    -> relationship | reputation | authority | application view
```

"Deterministic" is a claim about a **named** fold, not about the log alone. The same **event set**, folded by the same **Projection function and version**, under the same **policy parameters and ordering/as-of inputs** — an observer's honors, a revocation reading, a quorum-counting rule — yields the same view. A completeness contract is required only when the claim depends on complete input. Change any declared input and two readers can each be deterministic while producing different policy-scoped views; that disagreement is the policy layer of [authority-and-conflict.md](./authority-and-conflict.md) §9 doing its job, not a broken replay. Every executable probe that folds one log two ways (the revocation readings, the cold-start observers, the threshold counting rules) is an instance of this: same events and function, different declared policy, different results.

Reputation, current authority, identity status, and transaction state are **not canonical objects or Events**. They are different reductions of identified Event sets and may be cached only as non-authoritative implementation artifacts:

- **reputation** = fold of outcome Events under a named profile's context and weighting rules
- **identity status** (`profile_check_passed`, `credentialed`, `suspended`) = fold of key, credential, and governance Events under a named identity profile
- **transaction state** (`pending_approval`, `fulfilled`, `disputed`) = fold of one transaction's Events
- **current authority / application signal** = fold evaluated at a point in time

A Projection has no authority of its own. A named governance or application profile may use a Projection to trigger review or friction, but an authoritative change requires an authorized decision record under that profile. A Projection is a computed view, not a decision.

## 5. Scoped Replay and Recomputability

Signed Events and named deterministic Projections make a bounded result recomputable **without** a stored relationship object:

1. perform **External Record Verification** on each disclosed Event's signature and key provenance
2. identify the Event set and scope, plus a completeness contract only when the claim requires one
3. apply the same named Projection — function and version, policy parameters, ordering/as-of inputs, and unsupported behavior — to that Event set

An observer with the same evidence and declared inputs obtains the same result. This does not show that the Event set is complete, that undisclosed evidence does not exist, or that the resulting Relationship is true. Disagreement reduces to checkable questions: *which Events were available?*, *which Projection identity and version ran?*, *which policy and ordering inputs applied?*, and *what completeness, if any, was claimed?* Naming those inputs is what makes the bounded audit recomputable.

Use these claims distinctly:

- **Core Event Conformance** — the Event satisfies the named current envelope/security requirements; this alone establishes neither authority nor execution.
- **Named Projection Conformance** — the declared Projection produces the expected output over the declared inputs.
- **Named Functional Profile Conformance** — an implementation satisfies an explicitly named profile and version.
- **External Record Verification** — disclosed records and key provenance verify, without a completeness or payload-truth claim.
- **Independently Recomputable Result** — a separate implementation can recompute the result from the declared relevant Event set/completeness contract and Projection inputs.
- **Publicly Recomputable Result** — that same package is publicly available; public availability is not required by ARC.

## 6. Relationship Is Not Authoritative Protocol State

ARC does not define a global Relationship, score, profile, or status as authoritative protocol state. A named Projection is recomputable from its declared inputs; any materialized result or cache remains an implementation artifact rather than a canonical Event.

This boundary limits what ARC itself treats as authority. It does not prevent a deployment or another system from persisting derived profiles, and it does not make a claim about whether any particular data practice is safe. [Reputation.md](./reputation.md) describes contextual reputation as one application model rather than a universal score.

## 7. The Anchor — Identity and Keys

A key is not a competing primitive. It is the **precondition** of every other Event: without declared key material, an Event cannot satisfy a signature check or be attributed to that declared key.

Keys enter through key-lifecycle Events (registration, rotation, revocation). The first key cannot be vouched for by a prior ARC Event. A named identity profile may require an external anchor such as business registration, payment-account verification, community onboarding, or escrow stake. Such anchors add declared evidence; they do not establish identity or Sybil resistance with certainty. Key provenance is one of the inputs §5's record verification examines.

## 8. How This Constrains Later Work

This model is not "after" the event vocabulary and the projection design — it dictates their shape.

- **The event registry must be a small, closed set distinguished by predicate, not an open set of types.** Application richness lives in predicates and payloads, never in new top-level primitives. See [event-registry.md](./event-registry.md).
- **A named identity or reputation profile may use external anchors and graph heuristics.** ARC does not require one universal Sybil or trust policy; any weighting rules must be declared as Projection inputs (heuristics are sketched in [reputation.md](./reputation.md) §12).
- **Nothing derived is a first-class canonical object.** Scores, statuses, and states are projections. An implementation may cache them as non-authoritative artifacts. Existing documents that present an authoritative stored `reputation_score` predate this model; aligning them is deferred future work and intentionally not done in this patch.

## 9. Relationship to the Authority Model

The object model and the authority model describe complementary boundaries.

- [authority-and-conflict.md](./authority-and-conflict.md) defines *who decides* within declared authority domains, while external obligations remain outside ARC.
- This document defines *what is recorded and computed* (Events are the only canonical stored unit; Relationships are folds; derived artifacts are not authoritative protocol state).

The authority model already speaks in this vocabulary — "event history," "relationship projection," "events are evidence," "projections are advisory." This document supplies the definitions those phrases assume. The two should be read together.

## 10. Known Tensions

- **Replay cost.** Computing Relationships on demand avoids stored profiles but pushes work to query time. Caching a projection result *can* re-introduce a profile-shaped artifact — but the canon-fold executable probe (`examples/canon-fold-demo`) shows caching is a **discipline question, not a new primitive or a missing type**: the Event / Projection split is untouched, and what matters is the *shape* of the cache, not whether one exists. No cache is authoritative for a named claim; the reproducible result is the fold over that claim's declared inputs (§5), and a cache is at most a hint. Three shapes:
  - **ephemeral** — scoped to a single replay run and discarded after use. It does not outlive that computation.
  - **event-bound** — durable but keyed by an `event_set_hash` (plus projection name, subject, and context), reused only as a hint when the implementation establishes that the hash still names the current declared Event set. This is **conditional**: an incomplete or stale active-set index can still make the cache stale, so the hash alone does not prove completeness or force invalidation.
  - **durable, unbound** — persisted with no `event_set_hash` binding. It cannot support an independently recomputable claim without replay against declared inputs and is not authoritative protocol state.

  The remaining open questions are the discipline's parameters — cache lifetime, visibility, and who may hold one — not whether the object model needs a cache primitive.
- **Event set disagreement.** A named recomputation claim supports agreement only when parties use the same declared Events and Projection inputs. Communities holding different Event subsets may project different Relationships, even when some input differences happen not to change the output (see [reputation.md](./reputation.md) §10).
- **Selective disclosure.** Sharing a Relationship across contexts means sharing an Event subset, which is exactly where laundering and weak-import risks live ([threat-model.md](./threat-model.md) §13).
- **External anchoring presents an inclusion-versus-abuse-resistance trade-off.** A stronger cost gate may deter some low-cost identity creation while also excluding legitimate entrants; its actual effect depends on the named profile and deployment.

## 11. Current Status

This is an exploratory foundational model supported by executable probes, not a complete independent implementation or normative conformance specification.

Its purpose is to keep the Relationship / Event / Projection split consistent across the current Event Registry, named Projections, and later application documents; see [event-registry.md](./event-registry.md).

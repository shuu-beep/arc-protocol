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

Its job is narrow and prior to those: name the objects ARC is allowed to have, and the one object it is **not** allowed to store. Everything in the later documents — reputation scores, identity status, transaction state, trust — should be expressible in terms defined here. Where an existing document models something differently, this model is the intended direction; reconciling the older documents is deferred future work and is not performed here.

## 2. Two Layers

ARC reasons over exactly two kinds of object. Keeping them separate is the central discipline of this document.

### 2.1 Relationship — the conceptual primitive

A **Relationship** is the contextual standing between parties: how much a consumer should trust a merchant *for this kind of transaction, in this place, right now*. Reputation, current authority, and current trust are all narrower readings of the same standing.

A Relationship is:

- **contextual** — scoped to a category, geography, community, and time window
- **non-aggregated** — there is no single global relationship between two parties, and no global profile of one party
- **evolving and multi-party** — it changes with every relevant event and may involve more than two keys
- **never stored** — it is computed on demand, then discarded

The Relationship is what humans and agents actually care about. It is also the thing ARC must refuse to persist.

### 2.2 Event — the protocol primitive

An **Event** is a single, immutable, single-author, single-timestamp signed statement. It is the **only** unit ARC stores, transmits, or verifies.

An Event is:

- **immutable** — once signed it does not change; corrections are new Events
- **single-author** — attributable to exactly one signing key
- **discrete** — it states one thing at one moment
- **signed** — its integrity and attribution rest on a key (see §7)

Identity claims, offers, approvals, mandates, outcome records, disputes, and governance decisions are all **Events**. They are not competing primitives; they are one record type distinguished by a `type` and a `predicate` (see [event-registry.md](./event-registry.md)).

## 3. Why the Event, Not the Relationship, Is the Protocol Primitive

The choice is forced, not stylistic.

A cryptographic signature can only attach to an immutable, single-author, single-timestamp statement. A Relationship is multi-party, evolving, and contextual — there is nothing fixed to sign. **Relationships are unsignable; only Events are signable.** Therefore only Events can be verified, and only verifiable things can be the substrate of a trust protocol.

ARC has in fact been Event-first since the README: `reputation_event`, `approval_confirmed`, and `dispute_report` are all discrete signed records. This document names that commitment rather than introducing it.

## 4. Projection — How Relationship Is Recovered

A **Projection** is a deterministic fold over a set of Events that produces a Relationship view:

```txt
Projection(context, parties, window) = fold(relevant_events)
    -> relationship | reputation | authority | trust
```

Reputation, current authority, identity status, and transaction state are **not stored objects and not Events**. They are different reductions of the same Event log:

- **reputation** = fold of outcome Events, scoped by context, down-weighted by adversarial graph shape
- **identity status** (`verified`, `credentialed`, `suspended`) = fold of key, credential, and governance Events
- **transaction state** (`pending_approval`, `fulfilled`, `disputed`) = fold of one transaction's Events
- **authority-now / trust-now** = fold evaluated at a point in time

A Projection has no authority of its own. Per [authority-and-conflict.md](./authority-and-conflict.md) §5, a Projection is **advisory**: it may raise review or friction, but it may not punish, veto, or expel. It is a computed risk signal, not a decision.

## 5. Relationship Verification Is Replay

Because Events are signed and Projections are deterministic, relationship state is verifiable **without** a stored relationship object:

1. verify each Event's signature and key provenance
2. apply the same Projection function to the same Event set
3. anyone folding the same Events obtains the same view

This yields verifiable relationship state with nothing relationship-shaped on disk. Disagreement reduces to two checkable questions: *which Events do we each hold?* and *which Projection did we each run?*

## 6. Why ARC Never Stores the Relationship

Not storing the Relationship — computing it on demand, context-scoped, then discarding it — is the **structural** defense against the failure ARC exists to refuse.

A stored, persistent, aggregated Relationship *is* a profile. A global profile of a party is a social-credit record and a surveillance target. There is no policy that makes a persisted global profile safe; the only safe design is to not hold one.

So Event-first plus Projection-on-demand is not an efficiency choice. It is the enforcement mechanism for the anti-social-credit constraint: there is no global persistent profile to capture because none is ever stored. This is why [reputation.md](./reputation.md) insists reputation is contextual and must not become a universal score — the object model makes that boundary structural rather than merely aspirational.

## 7. The Anchor — Identity and Keys

A key is not a competing primitive. It is the **precondition** of every other Event: without a key, nothing can be signed, attributed, or verified.

Keys enter through key-lifecycle Events (registration, rotation, revocation). The first key cannot be vouched for by a prior ARC Event — it is anchored from outside ARC by a contextual cost gate (business registration, payment-account verification, community onboarding, or escrow-stake). That cost gate is also where Sybil resistance begins (see §8). Key provenance is what §5's replay walks before any fold is meaningful.

## 8. How This Constrains Later Work

This model is not "after" the event vocabulary and the projection design — it dictates their shape.

- **The event registry must be a small, closed set distinguished by predicate, not an open set of types.** Application richness lives in predicates and payloads, never in new top-level primitives. See [event-registry.md](./event-registry.md).
- **The projection function must be graph-structure-aware.** Because identity creation is permissionless by design, Sybil resistance cannot live in identity creation; it lives in the fold, which must down-weight trust that flows through circular, low-diversity, or high-velocity Event graphs (the heuristics already sketched in [reputation.md](./reputation.md) §12).
- **Nothing derived may be stored as a first-class object.** Scores, statuses, and states are projections. Existing documents that present a stored `reputation_score` predate this model; aligning them is deferred future work and intentionally not done in this patch.

## 9. Relationship to the Authority Model

The object model and the authority model are two halves of one constitution.

- [authority-and-conflict.md](./authority-and-conflict.md) defines *who decides* (human over own action, community over the commons; events are evidence; projections are advisory; external law on top).
- This document defines *what is recorded and computed* (Events are the only stored unit; Relationships are folds; nothing aggregated is persisted).

The authority model already speaks in this vocabulary — "event history," "relationship projection," "events are evidence," "projections are advisory." This document supplies the definitions those phrases assume. The two should be read together.

## 10. Known Tensions

- **Replay cost.** Computing Relationships on demand avoids stored profiles but pushes work to query time. Caching a projection result re-introduces a profile-shaped artifact; cache scope, lifetime, and visibility are unresolved.
- **Event set disagreement.** Verifiable replay only guarantees agreement when parties hold the same Events. Communities holding different Event subsets will project different Relationships — the same mechanism that makes reputation local also makes it non-portable (see [reputation.md](./reputation.md) §10).
- **Selective disclosure.** Sharing a Relationship across contexts means sharing an Event subset, which is exactly where laundering and weak-import risks live ([threat-model.md](./threat-model.md) §13).
- **The anchor is the equity dial.** A stronger cost gate resists Sybil better but excludes poor-but-honest entrants; cold-start and Sybil resistance are the same dial, not two problems.

## 11. Current Status

This is an exploratory foundational model. No implementation exists.

Its purpose is to fix the Relationship / Event / Projection split before the event vocabulary and projection functions are specified, so that later documents inherit one substrate. The next document defines the closed canonical event set consistent with this model; see [event-registry.md](./event-registry.md).

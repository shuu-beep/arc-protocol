# ARC Protocol: Event Registry

> **Status:** Exploratory canonical draft
>
> **Purpose:** Define the smallest closed set of canonical event types that can support identity, reputation, governance, disputes, approval, and commerce — without event explosion.
>
> This document depends on two others and should not be read alone. For what an Event *is* and why nothing derived is stored, see [object-model.md](./object-model.md). For who holds authority when signals conflict, see [authority-and-conflict.md](./authority-and-conflict.md).
>
> This is a protocol-layer vocabulary, not a wire format and not a message-type list. The exploratory message types in [protocol.md](./protocol.md) §6 and [architecture.md](./architecture.md) §4 are application-level and are **not** reconciled here; that is deferred future work.

---

## 1. Scope

This registry names the irreducible **event primitives**. It deliberately answers a different question than the message-type tables elsewhere in the corpus.

A message type describes a wire interaction (`offer_request`, `approval_request`). An event primitive describes a signed, stored, verifiable statement that enters the log and feeds projections. Many message types are not events at all (see §2.3), and many distinct message types collapse onto one event primitive (see §8).

Nothing here defines byte layouts, transports, signature algorithms, or storage. Those belong to a future specification ([future-protocol-spec.md](./future-protocol-spec.md) §2).

## 2. Governing Principles

### 2.1 Extend by predicate, not by type

The set of event **types** is closed and small. Application richness lives in a `predicate` namespace and in payloads. A new commerce flow, a new credential kind, a new outcome signal adds a **predicate**, never a top-level type. This is the rule that prevents event explosion.

### 2.2 State machines are projections, not events

Transaction states (`pending_approval`, `payment_pending`, `fulfilled`, `disputed`, `refund_partial`) are not events. They are a fold over a transaction's events ([object-model.md](./object-model.md) §4). The state enumerations in [protocol.md](./protocol.md) §4 and [architecture.md](./architecture.md) §4.1 are two views of one projection.

### 2.3 Requests are not events

A request asserts no truth, grants no permission, contests nothing, and decides nothing. `offer_request`, `logistics_request`, and `approval_request` are ephemeral transport. They do not enter the log or any projection.

### 2.4 External facts enter as attestations

ARC executes no payment and performs no delivery ([architecture.md](./architecture.md) §4.2, [liability-boundaries.md](./liability-boundaries.md)). A confirmed payment or a completed delivery is therefore not a native ARC state change — it is a provider's or party's **signed claim about something that happened outside ARC**.

## 3. The Set Is Forced by the Authority Canon

The taxonomy is derived from the authority domains in [authority-and-conflict.md](./authority-and-conflict.md), not invented from message semantics. The cut is by **authority source**, not by content.

| Authority canon | Forces |
| --- | --- |
| §5 "Events are evidence" — no authority | **`ATTEST`** (zero authority) |
| §3 Human authority over own action and risk | **`AUTHORIZE`** (self-domain) |
| §4 Community authority over the commons | **`ADJUDICATE`** (commons-domain) |
| §7 the boundary where an individual invokes the commons | **`CHALLENGE`** (domain-crossing) |
| verifiability precondition ([object-model.md](./object-model.md) §7) | **`KEY`** (anchor) |
| §5 "Projections are advisory" | **a Projection is not an event** |

`ADJUDICATE` cannot merge into `ATTEST` not because their shapes differ but because only `ADJUDICATE` carries commons authority: §5 forbids any other key, and any projection, from imposing a penalty. The registry is the authority constitution expressed as record types.

## 4. The Canonical Event Types

Five types and one cross-cutting field.

### 4.1 `KEY` — the anchor

Key lifecycle: register, rotate, revoke. The root of all verification.

- A registration is anchored from **outside** ARC by a contextual cost gate (business registration, payment-account verification, community onboarding, escrow-stake). This is where Sybil resistance begins.
- Rotation supersedes a prior key and carries history forward; revocation withdraws a key going forward.
- Distinct from `ATTEST` because its trust is externally anchored, not ARC-internal, and because every other event's verifiability depends on it.

### 4.2 `ATTEST` — signed evidence

A key signs a proposition. The workhorse. No authority — pure evidence.

Subsumes, by predicate: an **offer** (terms + expiry), a **reputation signal** (an outcome), a **fulfillment update** (a real-world claim), a **payment result** (a provider's claim about an external transfer), a **credential claim**, and the **canonical-intent record**.

### 4.3 `AUTHORIZE` — consent and permission

The protocol locus of human sovereignty: a key grants permission for a scoped action.

Subsumes, by predicate: an **approval** of a specific transaction; a **spending mandate / delegation** (the same primitive with a wider `scope` — budget, category, merchant, duration — so consumer-side mandates are not a new type); a **subkey binding**.

Carries `scope`, `expires_at`, and optional `contrary_to` — the record that an authorization was made against projection or community warnings. **Override is not a type; it is an `AUTHORIZE` with `contrary_to` set** ([authority-and-conflict.md](./authority-and-conflict.md) §7).

### 4.4 `CHALLENGE` — contest and invoke process

A key contests an event or outcome, invoking a process: a response window opens and the matter may route to the commons.

Subsumes: a **dispute report**, a **fraud report**, and an **appeal** (a challenge whose referent is a prior `ADJUDICATE`). This is the act by which an individual invokes community authority — the boundary crossing of [authority-and-conflict.md](./authority-and-conflict.md) §7.

### 4.5 `ADJUDICATE` — commons decision

A community renders a decision over its commons. The **only** event that may change a party's standing in the commons.

Subsumes: **warning, suspension, expulsion, reinstatement, appeal ruling, sponsorship/disclosure ruling**. Its authority source is a community process, not an individual key. Per [authority-and-conflict.md](./authority-and-conflict.md) §5–§6, neither a projection nor an ordinary key may produce this effect.

### 4.6 `nullifies` — a field, not a type

Any `ATTEST` or `AUTHORIZE` may reference a prior event and withdraw it going forward: **cancel an offer, revoke a mandate, retract a rating**. Modeling withdrawal as a field rather than as per-domain revoke types (`offer_cancel`, `mandate_revoke`, `rating_retract`) is what prevents the most common form of event explosion. `KEY` rotation and revocation are the key-typed instance of the same idea.

## 5. The Event Envelope

```txt
Event {
  id            // content hash
  type          // KEY | ATTEST | AUTHORIZE | CHALLENGE | ADJUDICATE
  signer        // key id, resolvable via a prior KEY event (except a KEY root)
  predicate     // namespaced semantic tag (see §6)
  refs[]        // prior events / parties / resources this event is about
  nullifies[]   // optional: prior event ids withdrawn going forward
  scope         // AUTHORIZE: budget/category/merchant/duration; KEY: cost-gate anchor
  contrary_to   // AUTHORIZE: signals overridden (override-friction record)
  not_before
  expires_at
  timestamp
  payload       // predicate-specific data
  signature
}
```

Fields are illustrative, not final. The type set is closed; the predicate namespace and payloads are open.

## 6. Predicate Namespace

Predicates are where richness grows without new types. Illustrative, non-exhaustive:

| Predicate | Type | Meaning |
| --- | --- | --- |
| `id.key_register` / `id.key_rotate` / `id.key_revoke` | `KEY` | key lifecycle |
| `id.credential` | `ATTEST` | a credential or career claim |
| `commerce.offer` | `ATTEST` | merchant terms + expiry |
| `commerce.payment_result` | `ATTEST` | provider claim about an external transfer |
| `commerce.fulfillment` | `ATTEST` | delivery/service real-world claim |
| `intent.canonical` | `ATTEST` | the parsed canonical intent shown to the human |
| `rep.outcome` | `ATTEST` | an outcome signal for a transaction |
| `consent.approval` | `AUTHORIZE` | approval of one transaction |
| `consent.mandate` | `AUTHORIZE` | scoped pre-authorization / delegation |
| `dispute.open` / `dispute.appeal` | `CHALLENGE` | contest an outcome or a ruling |
| `gov.warning` / `gov.suspension` / `gov.expulsion` / `gov.reinstatement` / `gov.ruling` | `ADJUDICATE` | commons decisions |

New flows extend this table. They do not extend §4.

## 7. Projections Register Against `(type, predicate)`

Projections are defined in [object-model.md](./object-model.md) §4 and are not events. Each consumes a slice of the log:

- **reputation** consumes `ATTEST{rep.outcome, commerce.payment_result, commerce.fulfillment}`, scoped by context and down-weighted by adversarial graph shape.
- **identity status** consumes `KEY{*} + ATTEST{id.credential} + ADJUDICATE{gov.suspension, gov.expulsion, gov.reinstatement}`.
- **transaction state** consumes a transaction's `ATTEST` / `AUTHORIZE` / `nullifies` references.
- **discovery ranking** consumes `ATTEST{commerce.offer}` plus the reputation projection plus disclosed sponsorship attestations.

A reputation score, an identity badge, and a transaction state are therefore outputs of projections — not stored objects and not events. Existing documents that present a stored `reputation_score` predate this model; they are intentionally left unchanged in this patch.

## 8. Illustrative Mapping (Non-Binding)

How existing exploratory message types and states would relate to this set, for orientation only. This is **not** a reconciliation of [protocol.md](./protocol.md) or [architecture.md](./architecture.md); those documents are unchanged.

| Existing name | Canonical | Note |
| --- | --- | --- |
| `offer_request`, `logistics_request`, `approval_request` | — | transport, not events |
| `offer_response` | `ATTEST` `commerce.offer` | |
| `intent_record` | `ATTEST` `intent.canonical` | attesting intent lets a projection detect dropped constraints (see `compromised-consumer-agent.json`) |
| `approval_confirmed` | `AUTHORIZE` `consent.approval` | |
| `approval_rejected` | — | absence of authorization; optionally an `ATTEST` for the record |
| `payment_intent` | — | transport instruction to a provider |
| `payment_confirmed`, `payment_failed` | `ATTEST` `commerce.payment_result` | one predicate with a status, not two types |
| `fulfillment_authorized` | — | transport, gated by transaction-state projection |
| `fulfillment_update` | `ATTEST` `commerce.fulfillment` | |
| `cancellation_notice` | `nullifies` on a prior event | not a type |
| `reputation_event` | `ATTEST` `rep.outcome` | the score is a projection |
| `dispute_report` | `CHALLENGE` `dispute.open` | |
| `governance_decision`, `suspension_notice`, penalty levels 1–6 | `ADJUDICATE` `gov.*` | four names for one primitive |
| transaction states (protocol §4, architecture §4.1) | — | projection, not events |
| identity status levels (identity §4) | — | projection of `KEY` + credential + `ADJUDICATE` |

## 9. Sufficiency Check

The five types plus `nullifies` cover every required capability:

| Capability | Built from |
| --- | --- |
| identity | `KEY` + `ATTEST{id.credential}` + `ADJUDICATE{gov.*}` → status is a projection |
| reputation | `ATTEST{rep.outcome,...}` → score is a projection, Sybil down-weight in the fold |
| governance | `ADJUDICATE`, invoked by `CHALLENGE` |
| disputes | `CHALLENGE` → `ATTEST` (evidence/response) → `ADJUDICATE` |
| approval | `AUTHORIZE` (+ `contrary_to` for override) |
| commerce | `ATTEST{commerce.offer}` + `AUTHORIZE{consent.approval}` + `ATTEST{commerce.payment_result}` + `ATTEST{commerce.fulfillment}` + `nullifies` (cancel); state is a projection |

No capability requires a sixth type. That is the irreducibility result.

## 10. Known Tensions and Open Questions

- **`CHALLENGE` is the most reducible.** It is close to `ATTEST(harm) + invoke-review`, and "invoke review" could be a projection rule on a predicate. It is kept as a primitive only because it is the constitutional act of crossing from the human domain into the commons ([authority-and-conflict.md](./authority-and-conflict.md) §7). Demoting it to four types is defensible.
- **Revocation: field vs type.** Modeling withdrawal as `nullifies` avoids explosion but spreads withdrawal semantics across types. Elevating it to a primitive is a reasonable alternative.
- **`intent.canonical` as an event.** Recording parsed intent has a cost (it captures user data), but omitted-constraint attacks (`compromised-consumer-agent.json`) are only detectable if intent is attested. The trade-off is unresolved.
- **No native commitment/offer type.** An offer is an `ATTEST`; its acceptance-and-expiry semantics are handled by an `AUTHORIZE` referencing the offer within its validity window, checked by projection. Some protocols elevate commitments to a primitive; ARC does not, for now.
- **No native transfer.** If a future ARC-compatible system ever *holds* value (escrow), a real transfer primitive could re-emerge. For v0.1 it stays an `ATTEST` about an external fact.
- **Predicate governance.** Extending by predicate only prevents explosion if the predicate namespace itself is governed. Who may register predicates, and how conflicts are resolved, is unspecified.

## 11. Current Status

This is an exploratory canonical draft. No implementation exists.

It proposes the irreducible event vocabulary implied by [object-model.md](./object-model.md) and [authority-and-conflict.md](./authority-and-conflict.md). It does not modify the existing message-type or state documents; reconciling [protocol.md](./protocol.md), [architecture.md](./architecture.md), and the stored-score fields against this registry is the next useful step and is intentionally out of scope for this additive draft.

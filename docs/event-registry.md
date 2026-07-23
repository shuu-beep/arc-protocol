# ARC Protocol: Event Registry

> **Status:** Exploratory canonical draft
>
> **Purpose:** Define the current closed set of canonical Event types used to represent identity, reputation, governance, dispute, approval, and Commerce claims without event-type proliferation.
>
> This document depends on two others and should not be read alone. For what an Event *is* and why derived views are not authoritative protocol state, see [object-model.md](./object-model.md). For who holds authority when signals conflict, see [authority-and-conflict.md](./authority-and-conflict.md).
>
> This is a protocol-layer vocabulary, not a wire format and not a message-type list. The exploratory message types in [protocol.md](./protocol.md) §6 and [architecture.md](./architecture.md) §4 are application-level; those documents have since been aligned with this registry. This registry remains the vocabulary, not the normative wire format.

---

## 1. Scope

This registry names the current canonical **event primitives**. It deliberately answers a different question than the message-type tables elsewhere in the corpus.

A message type describes a wire interaction (`offer_request`, `approval_request`). An Event primitive describes a signed canonical record that can be checked under a declared security profile and feeds Projections. Many message types are not Events at all (see §2.3), and many distinct message types collapse onto one Event primitive (see §8).

Nothing here defines byte layouts, transports, signature algorithms, or storage. Those belong to a future specification ([future-protocol-spec.md](./future-protocol-spec.md) §2).

## 2. Governing Principles

### 2.1 Extend by predicate, not by type

The current set of event **types** is closed and small. Application richness lives in a `predicate` namespace and in payloads. Under the current Canon, a new commerce flow, credential kind, or outcome signal extends the **predicate** namespace rather than adding a top-level type. No current approved flow requires another type; any future proposal would have to reopen that Canon decision explicitly.

### 2.2 State machines are projections, not events

Transaction states (`pending_approval`, `payment_pending`, `fulfilled`, `disputed`, `refund_partial`) are not events. They are a fold over a transaction's events ([object-model.md](./object-model.md) §4). The state enumerations in [protocol.md](./protocol.md) §4 and [architecture.md](./architecture.md) §4.1 are two views of one projection.

### 2.3 Requests are not events

`offer_request`, `logistics_request`, and `approval_request` are ephemeral transport rather than canonical Events. They may carry application claims, but they do not grant ARC authority or enter a Projection unless separately recorded as an Event.

### 2.4 External facts enter as attestations

ARC executes no payment and performs no delivery ([architecture.md](./architecture.md) §4.2, [liability-boundaries.md](./liability-boundaries.md)). A confirmed payment or a completed delivery is therefore not a native ARC state change — it is a provider's or party's **signed claim about something that happened outside ARC**.

This boundary has a gradient worth naming, because a signed event supports different checks at different distances from the key. Four fidelities — two record checks under a declared security profile, and two that records can only partially expose:

| Fidelity | The question | What ARC can do |
| --- | --- | --- |
| **Signer** | Did the expected key sign this event? | Under a declared security profile, the disclosed signature and key provenance can be checked. This does not establish identity, custody, authority, or truth. |
| **Byte** | Has the signed content been altered since it was signed? | Under a declared canonicalization and hash profile, mutation of the covered bytes can be detected. |
| **Execution** | Did the runtime actually do what the event claims it did? | Disclosed `refs`, receipts, counter-attestations, `CHALLENGE`, and divergent Projections may reveal inconsistency; they do not prove the runtime ran as claimed. |
| **Outcome** | Did the real-world result match the claim? | Not provable from the Event records alone. Receipts, witness statements, and provider confirmations remain further `ATTEST` claims evaluated under a named profile. |

Signer and byte fidelity are checks over the **record** under a declared security profile. Execution and outcome fidelity concern the **referent** — the world the record points at — and a signature cannot reach across that gap. A valid signature on a `commerce.fulfillment` event supports the narrower conclusion that a key asserted a delivery; it does not prove a delivery, identify the key controller, or establish covering authority. The same boundary applies to signer interpretation ([key-custody.md](./key-custody.md) §5) and **temporal fidelity**: a valid signature can preserve a false timestamp. A [probe](../examples/temporal-fidelity-demo/) suggests `refs` can supply partial causal ordering — a careless backdate that references the future is caught, while a careful one that references only the genuine past is not — and causally concurrent events require a declared ordering/as-of policy. ARC can preserve an attributable claim about the world, make covered-byte mutation detectable under a profile, disclose contradictions when the relevant records are available, and partially order records by causal `refs`; it cannot make the claim true. A [probe](../examples/execution-fidelity-demo/) shows that contradictory claims about one referent can both pass the fixture's record checks. Further receipts, witness statements, and counter-claims remain additional records, while an `ADJUDICATE` supplies a ruling under a declared authority profile without verifying the world. Runtime execution and outcome truth require external evidence or environment-specific verification that ARC does not supply; what is signable here is the claim, not the fact it points at ([object-model.md](./object-model.md) §3).

## 3. How the Current Set Maps to the Authority Model

The taxonomy maps the authority domains in [authority-and-conflict.md](./authority-and-conflict.md) to current record types. The cut is by **authority source**, not by application message content.

| Authority model | Current record type |
| --- | --- |
| §5 "Events are evidence" — no authority | **`ATTEST`** (zero authority) |
| §3 Human authority over own action and risk | **`AUTHORIZE`** (self-domain) |
| §4 Community authority over the commons | **`ADJUDICATE`** (commons-domain) |
| §7 the boundary where an individual invokes the commons | **`CHALLENGE`** (domain-crossing) |
| verifiability precondition ([object-model.md](./object-model.md) §7) | **`KEY`** (anchor) |
| §5 "Projections are advisory" | **a Projection is not an event** |

`ADJUDICATE` remains distinct from `ATTEST` because only `ADJUDICATE` records a decision carrying declared commons authority. The registry maps the current authority semantics to record types.

The five Event types are not application message categories. They are the current canonical vocabulary for distinguishing evidence, permission, contest, commons decision, and key provenance according to their authority source and authority effect.

## 4. The Canonical Event Types

Five types and one cross-cutting field.

### 4.1 `KEY` — the anchor

Key lifecycle: register, rotate, revoke. A provenance input to record verification under a declared security profile.

- A named identity profile may require an **external anchor** such as business registration, payment-account verification, community onboarding, or escrow stake. Such evidence may add identity cost or continuity without establishing identity or Sybil resistance with certainty. How the anchor is recorded is not yet fixed, and the demos deliberately diverge: canon-fold carries a self-asserted `payload.anchor` on the register, while local-commerce run [E] uses a third party's `ATTEST id.anchor`, with self-issued anchors excluded. A future specification must select a profile before making compatibility claims; until then the representations are illustrative.
- Rotation supersedes a prior key and carries history forward; revocation withdraws a key going forward.
- Distinct from `ATTEST` because it provides the dedicated key-lifecycle and provenance record used by declared verification profiles.

### 4.2 `ATTEST` — signed evidence

A key signs a proposition. The workhorse. No authority — pure evidence.

Subsumes, by predicate: an **offer** (terms + expiry), a **reputation signal** (an outcome), a **fulfillment update** (a real-world claim), a **payment result** (a provider's claim about an external transfer), a **credential claim**, and the **canonical-intent record**.

### 4.3 `AUTHORIZE` — consent and permission

The record type by which a key grants permission for a scoped action.

Subsumes, by predicate: an **approval** of a specific transaction; a **spending mandate / delegation** (the same primitive with a wider `scope` — budget, category, merchant, duration — so consumer-side mandates are not a new type); a **subkey binding**.

An act-specific `AUTHORIZE` covers only the act it identifies. It cannot be re-aimed, and any change to an application-defined material term creates a different target requiring new current coverage.

Carries `scope`, `expires_at`, and optional `contrary_to` — the record that an authorization was made against projection or community warnings. **Override is not a type; it is an `AUTHORIZE` with `contrary_to` set** ([authority-and-conflict.md](./authority-and-conflict.md) §7).

### 4.4 `CHALLENGE` — contest and invoke process

A key contests an event or outcome, invoking a process: a response window opens and the matter may route to the commons.

Subsumes: a **dispute report**, a **fraud report**, and an **appeal** (a challenge whose referent is a prior `ADJUDICATE`). This is the act by which an individual invokes community authority — the boundary crossing of [authority-and-conflict.md](./authority-and-conflict.md) §7.

### 4.5 `ADJUDICATE` — commons decision

A community renders a decision over its commons. The **only** event that may change a party's standing in the commons.

Subsumes: **warning, suspension, expulsion, reinstatement, appeal ruling, sponsorship/disclosure ruling**. Its authority source is a community process, not an individual key. Per [authority-and-conflict.md](./authority-and-conflict.md) §5–§6, neither a projection nor an ordinary key may produce this effect.

### 4.6 `nullifies` — a field, not a type

Any `ATTEST` or `AUTHORIZE` may reference a prior event and withdraw it going forward: **cancel an offer, revoke a mandate, retract a rating**. Modeling withdrawal as a field lets the current Canon avoid per-domain revoke types (`offer_cancel`, `mandate_revoke`, `rating_retract`). `KEY` rotation and revocation are the key-typed instance of the same idea.

**Who may nullify.** Withdrawal is a self-domain act ([authority-and-conflict.md](./authority-and-conflict.md) §3): a key withdraws **its own** prior statements and grants. A fold honors a `nullifies` only when the withdrawing event's signer is the **author of the target event, or a key downstream of that author in its `KEY` rotation lineage** (§4.1: rotation carries the holder's authority forward). Every canonical example is this shape — the merchant cancels the merchant's offer, the granter revokes the granter's mandate, the rater retracts the rater's rating, and a key revocation is signed by the revoked key or its rotation successor. A `nullifies` from any other signer may still pass the declared signature check and remain on the log as evidence, but it withdraws nothing: no fold drops its target. Invalidating **another party's** event is commons business — an `ADJUDICATE` referencing that event ([authority-and-conflict.md](./authority-and-conflict.md) §9) — never a `nullifies` side effect. The rule restricts keys, not holders: a stolen key can still wield this self-domain power until revoked, a residue that belongs to key custody ([key-custody.md](./key-custody.md) §5), not to the fold.

**Two readings of `nullifies`.** The same field is read two ways depending on what it withdraws, and the difference is in the fold, not in the type:

- **Ordinary withdrawal — any-age target, forward effect.** When `nullifies` names a specific `ATTEST` or `AUTHORIZE` (cancel an offer, retract a rating, revoke a mandate), a named ordering/as-of profile determines when the target ceases to cover later acts, however old the target is. Causally concurrent act and withdrawal remain contested unless that profile resolves their order. After the effective withdrawal point, the fold stops reading the target as in force: it covers no new act and backs no current standing. What withdrawal does **not** settle by itself is the past: authorization at the act remains a separate projection result, while whether a current reader continues to honor an act already *completed* under the target is a projection choice — cascade vs preserve, [authority-and-conflict.md](./authority-and-conflict.md) §9, exercised in [`examples/authority-revocation-demo`](../examples/authority-revocation-demo/) — and voiding a specific completed act is an authority decision, an `ADJUDICATE` referencing that act, never a side effect of `nullifies`. This is the same forward-looking reading as [delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md) §6.
- **Key revocation — time-scoped.** A compromised key is withdrawn with a `KEY` event carrying the `id.key_revoke` predicate, whose `nullifies` names the key's own register event. A named ordering/as-of profile determines the forward boundary: the key's register and prior events stay readable, while acts ordered at or after the effective revocation point are not honored by the fold. Concurrent cases remain contested unless the profile orders them. The register is deliberately kept so the chain remains walkable and prior events can still be checked under the declared security profile.

The canon-fold demo (`examples/canon-fold-demo`) exercises this: a compromised key is revoked with `KEY` `id.key_revoke` + `nullifies` — no `KEY_REVOKE` or other sixth type — and two attacker-authored post-revoke events pass the fixture's deterministic mock-signature check yet drop out of the fold, while the key's pre-revoke history continues to fold normally. Its fold also enforces the authority rule above: a `nullifies` — including an `id.key_revoke` — is honored only from the target's author or its rotation lineage. What differs between the two readings is how the fold reads "going forward", not the event vocabulary; this fixture uses the existing primitive. Who may revoke is fixed by the authority rule; only the completed-act residue is policy.

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

New flows extend this table through predicates. Any proposal for another top-level type must explicitly reopen the current §4 Canon.

## 7. Projections Register Against `(type, predicate)`

Projections are defined in [object-model.md](./object-model.md) §4 and are not events. Each consumes a slice of the log:

- **reputation** consumes `ATTEST{rep.outcome, commerce.payment_result, commerce.fulfillment}` under a named profile's context and weighting rules.
- **identity status** consumes `KEY{*} + ATTEST{id.credential} + ADJUDICATE{gov.suspension, gov.expulsion, gov.reinstatement}`.
- **transaction state** consumes a transaction's `ATTEST` / `AUTHORIZE` / `nullifies` references.
- **discovery ranking** consumes `ATTEST{commerce.offer}` plus the reputation projection plus disclosed sponsorship attestations.

A reputation score, identity badge, and transaction state are therefore Projection outputs rather than canonical Events or authoritative protocol state. An implementation may cache them as non-authoritative artifacts. Wherever a document shows a `reputation_score`, identity `status`, or `permission level`, read it as an illustrative Projection output. Any remaining legacy or illustrative occurrence elsewhere in the corpus is non-normative and defers to [object-model.md](./object-model.md) and this registry.

## 8. Illustrative Mapping (Non-Binding)

How the exploratory message types and states relate to this set, for orientation. The mapping below is an orientation aid, not the normative wire format; [protocol.md](./protocol.md) and [architecture.md](./architecture.md) have since been aligned with this registry.

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

## 9. Current Sufficiency Evidence

Across the current Canon, documents, and executable probes, the five types plus `nullifies` express the capabilities below:

| Capability | Built from |
| --- | --- |
| identity | `KEY` + `ATTEST{id.credential}` + `ADJUDICATE{gov.*}` → status is a projection |
| reputation | `ATTEST{rep.outcome,...}` → score is a projection, Sybil down-weight in the fold |
| governance | `ADJUDICATE`, invoked by `CHALLENGE` |
| disputes | `CHALLENGE` → `ATTEST` (evidence/response) → `ADJUDICATE` |
| approval | `AUTHORIZE` (+ `contrary_to` for override) |
| commerce | `ATTEST{commerce.offer}` + `AUTHORIZE{consent.approval}` + `ATTEST{commerce.payment_result}` + `ATTEST{commerce.fulfillment}` + `nullifies` (cancel); state is a projection |

No current scenario has forced a sixth type. This is evidence for the present closed vocabulary, not a claim that five types are universally sufficient forever.

## 10. Known Tensions and Open Questions

- **`CHALLENGE` is the most reducible.** It is close to `ATTEST(harm) + invoke-review`, and "invoke review" could be a projection rule on a predicate. The current Canon keeps it as the distinct record by which a party invokes a declared review process ([authority-and-conflict.md](./authority-and-conflict.md) §7). A four-type model is a non-current design alternative, not an implementation option under this registry.
- **Revocation: field vs type.** Modeling withdrawal as `nullifies` avoids explosion but spreads withdrawal semantics across types. A dedicated revocation primitive is a non-current design alternative. The canon-fold demo confirms current revocation uses no sixth type — a compromised key is withdrawn with `KEY` `id.key_revoke` + `nullifies` — but it surfaces that `nullifies` carries two readings (forward-effect ordinary withdrawal vs time-scoped key revocation; see §4.6). Who may nullify is fixed by §4.6's authority rule; the remaining issue is **fold-policy semantics** — whether a current reader continues to honor a *completed* act after the withdrawal (§4.6, [authority-and-conflict.md](./authority-and-conflict.md) §9) — not an event-type gap.
- **`intent.canonical` as an event.** Recording parsed intent has a cost (it captures user data), but omitted-constraint attacks (`compromised-consumer-agent.json`) are only detectable if intent is attested. The trade-off is unresolved.
- **No native commitment/offer type.** An offer is an `ATTEST`; its acceptance-and-expiry semantics are handled by an `AUTHORIZE` referencing the offer within its validity window, checked by projection. Some protocols elevate commitments to a primitive; ARC does not, for now.
- **No native transfer.** If a future ARC-compatible system ever *holds* value (escrow), a real transfer primitive could re-emerge. For v0.1 it stays an `ATTEST` about an external fact.
- **Quorum approval: evidence or consent.** The threshold probe ([`examples/threshold-authority-demo`](../examples/threshold-authority-demo/)) records M-of-N member approvals as `ATTEST quorum.approve` — evidence a fold counts against a recorded threshold — while the canon assigns consent and permission to `AUTHORIZE` (§4.3). Whether a quorum member's approval is testimony (an `ATTEST` a projection counts) or an exercise of authority (an `AUTHORIZE` that composes) is deliberately unresolved: the probe poses the question and models the evidence reading; no document answers it. It must be answered before joint authority is independently implemented — an implementer should not have to guess which side of the evidence/authority line a quorum sits on.

**OPEN — MUST NOT BE IMPLIED BY CURRENT DOCUMENTATION:** quorum member participation is not yet classified universally as either `ATTEST` or `AUTHORIZE`.
- **Predicate governance.** Extending by predicate limits type growth only if the predicate namespace itself is governed. Who may register predicates, and how conflicts are resolved, is unspecified.

## 11. Current Status

This is an exploratory canonical draft backed by executable probes, not a complete independently implementable specification.

It proposes the current closed event vocabulary implied by [object-model.md](./object-model.md) and [authority-and-conflict.md](./authority-and-conflict.md). The earlier message-type, state, and stored-score language in [protocol.md](./protocol.md) and [architecture.md](./architecture.md) has since been reconciled against this registry — those documents now read such fields as projections. Reconciling the remaining illustrative examples elsewhere in the corpus is the deferred work [object-model.md](./object-model.md) §1 and §7 above already flag, not a completed pass; what remains exploratory is the absence of a complete independent implementation and finalized wire, security, and conformance profiles.

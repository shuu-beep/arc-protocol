# ARC Protocol: Delegation and Spending Mandates

> **Status:** Exploratory draft
>
> **Purpose:** Explain how human approval and delegation coexist in ARC — *how far delegation may go*, not how to automate it.
>
> This is not a new feature proposal. Delegation is expressed entirely with the existing Canon: the `AUTHORIZE` event, its `scope`, and the `nullifies` field. It introduces no new primitive, no new event type, no new Canon, and no new governance structure.
>
> For authority boundaries, see [authority-and-conflict.md](./authority-and-conflict.md). For the `AUTHORIZE` event and `nullifies`, see [event-registry.md](./event-registry.md). For projection, see [object-model.md](./object-model.md). For approval fatigue, see [threat-model.md](./threat-model.md) §9.1. Earlier Commerce-origin material first mentioned intent-based delegation.

---

## 1. Why Delegation Matters

Humans acting through agents may face many small, repetitive consequential decisions; Commerce makes this pressure especially visible. Requiring an explicit prompt for every one can produce approval fatigue ([threat-model.md](./threat-model.md) §9.1, [glossary.md](./glossary.md) §21): frequent prompts may reduce review quality.

Delegation asks whether a human can decide *in advance*, within limits, so not every action needs a fresh prompt while each act remains traceable to human-authored authority. This document describes that boundary using the Canon.

Act-specific approval and scoped delegation are two shapes of human-authored authority. An application may prefer fresh approval as its default or fail-closed path, but that is application or implementation policy rather than a protocol ranking of the two shapes.

## 2. Human Approval as a Constraint

From [authority-and-conflict.md](./authority-and-conflict.md) §3, a human is the final authority over their own action and their own risk. An `AUTHORIZE` records the human-authored authority that covers an act.

In Canon terms, act-specific approval is an `AUTHORIZE` event referencing an exact target ([event-registry.md](./event-registry.md) §4.3). In the Commerce profile, `consent.approval` references a specific offer within its validity window. It is evidence that a human licensed that identified action; it cannot be re-aimed, and a material target change requires new coverage.

No Projection and no agent may license a consequential action on a human's behalf without an `AUTHORIZE` that traces to that human. Delegation does not remove this requirement; it changes the *shape* of the `AUTHORIZE`.

**Current Coverage** exists when an act-specific authorization still covers the unchanged target, or when an unexpired, unrevoked scoped mandate covers the act under the declared named Projection/profile. A valid signature or approval interaction alone establishes neither current coverage nor execution or outcome truth.

## 3. Delegation Is Not Full Autonomy

Delegation means issuing an `AUTHORIZE` in advance, with a scope, rather than one per transaction. The human still authored the authority — they pre-shaped it.

Full autonomy, as this document uses the term, means an agent acting with authority no human granted or beyond any human-set bound. Such an act lacks Current Coverage under ARC.

The distinction is precise:

- a **delegated** action is still covered by a human's `AUTHORIZE` — a scoped, earlier one
- an **autonomous** action is covered by no `AUTHORIZE` at all

The first has prior human-authored coverage; the second does not. A very broad or indefinite mandate remains distinguishable from absence of authorization, but approaches the risk profile of unconstrained autonomy. Bounded scope (§5) reduces that authorization risk, though it is not sufficient by itself.

## 4. Spending Mandates

A mandate is an `AUTHORIZE` that covers a *class* of future actions within explicit limits instead of one act-specific target. A spending mandate (`consent.mandate`) is the flagship Commerce-profile example. It is the same primitive as an approval, with a wider referent — not a new event type.

It is the consumer-side counterpart to the provider-side credential scope discussed in [identity.md](./identity.md) §5 (`agent_scope`). Earlier Commerce-origin documents mentioned consumer delegation but never specified it; here it is expressed in Canon terms.

A mandate is **evidence** — a signed `AUTHORIZE`. Whether a given action is *covered* by it is a **Projection** ([object-model.md](./object-model.md) §4): under a named profile, fold the mandate, relevant prior actions, and any `nullifies`, then compare the candidate action with the declared scope. The "state" of a mandate (active, expired, exhausted, revoked) is therefore a projected view, not a stored field. This description does not by itself supply deterministic cross-parser meaning or atomic cumulative consumption.

Illustrative shape, reusing the existing envelope ([event-registry.md](./event-registry.md) §5) — not a wire format:

```txt
AUTHORIZE {
  predicate: consent.mandate,
  signer:    <human key>,
  scope:     { budget, category, merchant, window },
  expires_at: <time>
}
```

## 5. Scope-Limited Authorization

Bounded scope reduces delegation risk, but scope text alone is not sufficient for interoperable enforcement. An unbounded human-authored mandate remains an authorization record, while offering little practical constraint. The dimensions below are Commerce-profile examples already named in [event-registry.md](./event-registry.md) §4.3:

- **budget limits** — a total or per-transaction ceiling (for example, routine grocery orders under a cap)
- **merchant limits** — only named merchants, merchants whose declared profile checks pass, or those whose reputation Projection clears a threshold
- **category limits** — only a commerce category (food, transit), not arbitrary purchases
- **time limits** — an `expires_at` after which the mandate is no longer in force

The Commerce reference application reads scope conservatively, mirroring [identity.md](./identity.md) §6.4: a mandate grants the minimum, and anything outside it is refused or routed to a human according to declared application policy — never widened silently.

A reputation threshold inside scope is a **projection input, not a stored score**: "only merchants whose reputation projection clears X in this context" is evaluated by folding events at decision time ([reputation.md](./reputation.md), [object-model.md](./object-model.md)).

A practical implementation limit follows: if a named profile cannot express or compare a constraint precisely, it must return an explicit unsupported result rather than widen coverage. An application may then route the action to a human.

## 6. Revocation

A mandate must be withdrawable. In the Canon, revocation is not a new event — it is the `nullifies` field ([event-registry.md](./event-registry.md) §4.6).

```txt
AUTHORIZE (mandate M)
        ↓
later event with nullifies: [M]   →   M is no longer in force going forward
```

Revocation is forward-looking: it stops future coverage. Actions validly taken under M before revocation remain attributable events; the prior Events remain attributable records under the object model ([object-model.md](./object-model.md)). Whether a *completed* act stays honored when a reader later re-folds the full log is the cascade-vs-preserve Projection choice of [authority-and-conflict.md](./authority-and-conflict.md) §9 — the fact of withdrawal is Canon, that reading is policy — and voiding a specific past act requires an `ADJUDICATE`, not a `nullifies`. Only the mandate's author — the granting key or its rotation lineage — may issue the revocation ([event-registry.md](./event-registry.md) §4.6): a `nullifies` from anyone else is recorded evidence, not a withdrawal. When an act and revocation are causally concurrent, coverage remains **contested** absent a named ordering/as-of profile; an untrusted timestamp does not settle it.

Key compromise interacts with this: revoking or rotating the signing key (a `KEY` event) also ends the mandates that depended on it ([reputation.md](./reputation.md) §9, [identity.md](./identity.md) §6.2).

## 7. Approval Fatigue

Delegation is often proposed as the answer to approval fatigue ([threat-model.md](./threat-model.md) §9.1). It does not dissolve the problem; it **relocates** it.

This is the same warning-fatigue pattern discussed in [authority-and-conflict.md](./authority-and-conflict.md) §7. With delegation, the risk moves from *prompt frequency* to *mandate-design quality* and *audit-review quality*. A broad mandate that is never reviewed may provide weak evidence of continuing, attentive oversight.

Earlier Commerce-origin research recorded this exact tension: intent-based delegation may reduce prompts, but both excessive prompts and unread audit logs weaken meaningful attention. ARC does not claim delegation solves it.

Delegation can trade frequent act-specific decisions for less frequent mandate decisions. Whether that improves review depends on mandate quality, revisit cadence, and interface behavior; those effects remain unmeasured.

## 8. Failure Cases

The Commerce reference application fails closed in the cases below and may route them to explicit human approval. The protocol requirement is narrower: unsupported or uncovered actions must not be widened silently.

- **Mandate expired.** A candidate action arrives after `expires_at`. Under the declared clock/as-of profile, the Projection finds no in-force mandate, so the Commerce application refuses the action or routes it to a human (compare [stale-offer-approval.json](../examples/local-commerce-demo/artifacts/stale-offer-approval.json)).
- **Merchant changed.** An offer's application-defined material terms (`ATTEST`) differ from the authorized target, or the merchant is outside the allowed set. The act needs new current coverage.
- **Cumulative amount appears exceeded.** Under a declared ordering, prior covered actions may leave insufficient scope for the candidate. Causally concurrent consumption is not settled by this example; §10 suspends atomic-prevention and interoperability claims.
- **Authorization conflict.** Two mandates overlap with different limits, or a mandate would cover an action that community or Projection signals warn against. A named application profile may show the conflict, require a deliberate human act, and record `contrary_to` on any `AUTHORIZE` that proceeds against a warning. Base ARC records the authorization and declared references; it does not mandate the override interface.

## 9. Community vs Personal Authority

A human may only delegate authority they actually hold. In the resource-domain model of [authority-and-conflict.md](./authority-and-conflict.md) §3–§4, human authority covers a person's own action and risk, while community authority covers its declared commons. These resource domains remain distinct.

Therefore a personal mandate can authorize the human's *own* spending and action, but it cannot:

- grant or delegate commons authority — it cannot make the network host, endorse, or protect anyone (the negative-right limit, §3), and it cannot stand in for a community's `ADJUDICATE` (`gov.*`)
- grant itself commons protection — a named application profile may require explicit override review before stepping outside the commons, even under a broad mandate

Conversely, a community cannot mandate a person's private spending. Mandates are personal-domain instruments; governance decisions (`ADJUDICATE`) remain the commons-domain instrument. The two never substitute for each other.

## 10. Open Questions

- **In-flight actions at revocation.** When the act and revocation are causally ordered, the named Projection can evaluate the declared cut. When they are causally concurrent, coverage/honoring is contested absent a named ordering profile.
- **Friction quality.** What makes a mandate decision *meaningful* rather than another reflexive accept? Unsolved, and shared with §7.
- **Scope expressiveness.** Many real constraints ("only if I actually need it") are not cleanly expressible as budget, merchant, category, or time. A named profile must declare supported typed terms and fail closed on ambiguous or unsupported input; natural-language interpretation is not base ARC.
- **Audit-review burden.** Who or what ensures the human revisits the audit trail of delegated actions? An unread trail is not oversight.
- **Compromised approval surface.** A delegated flow trusts the agent to enforce scope, yet [compromised-consumer-agent.json](../examples/local-commerce-demo/artifacts/compromised-consumer-agent.json) shows an agent can misreport. Can scope enforcement be checked independently of the consumer agent — at the approval device or the payment provider? Unresolved. [key-custody.md](./key-custody.md) §2 takes a position on part of this — scope enforcement belongs in the signer's trusted base, with the key, not in the agent — while the residue (a compromised signer) remains open.
- **Mandate portability.** A mandate has no cross-implementation meaning merely because its signature verifies. A shared claim requires a named profile with a closed grammar and term types; operator, normalization, amount/unit, intersection, attenuation, expiry, material-target, and error semantics; plus versioned positive, negative, boundary, ambiguous, and unsupported vectors.

**Deterministic interpretation gate — REQUIRED BEFORE INTEROPERABILITY CLAIM.** The illustrative scope above is not a universal mandate grammar. Independent implementations cannot claim the same Delegated Execution behavior until they declare and test the named deterministic profile surface just listed.

**Atomic cumulative-consumption gate — REQUIRED BEFORE INTEROPERABILITY CLAIM.** Given one human-authored mandate with remaining cumulative authority `R` and two causally concurrent candidate acts `A` and `B`, where each is individually within `R` but `A + B > R`, current semantics do not determine which acts are covered or provide a portable prevention mechanism. Until that question is resolved, ARC does not claim that it prevents concurrent overspend or double consumption, provides an atomic execution-time total cap, makes remaining cumulative authority portable without coordination, or interoperably enforces cumulative mandates. No lock, reservation, sequencer, or new Event is selected here.

## 11. Current ARC Position

Delegation in ARC is exploratory and additive by reuse. It is the existing `AUTHORIZE` event given a `scope` and an `expires_at`, revoked through `nullifies`, evaluated by projection, and bounded by the authority model. No new primitive, event type, Canon, or governance structure is introduced.

Act-specific approval and scoped delegation are co-equal forms of human-authored `AUTHORIZE`. An application may use fresh human approval as its default or fail-closed route; ARC does not present either approval cadence as universally preferred or sufficient for safety.

ARC's claim is narrow: it can represent delegation over one's own action and risk, within declared scope and with revocation, without granting commons authority. A named application profile may add escalation or override review. ARC does not claim that delegation is safe or interoperably enforceable; mandate interpretation, audit review, and the deterministic and atomic gates above remain open.

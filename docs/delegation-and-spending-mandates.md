# ARC Protocol: Delegation and Spending Mandates

> **Status:** Exploratory draft
>
> **Purpose:** Explain how human approval and delegation coexist in ARC — *how far delegation may go*, not how to automate it.
>
> This is not a new feature proposal. Delegation is expressed entirely with the existing Canon: the `AUTHORIZE` event, its `scope`, and the `nullifies` field. It introduces no new primitive, no new event type, no new Canon, and no new governance structure.
>
> For authority boundaries, see [authority-and-conflict.md](./authority-and-conflict.md). For the `AUTHORIZE` event and `nullifies`, see [event-registry.md](./event-registry.md). For projection, see [object-model.md](./object-model.md). For approval fatigue, see [threat-model.md](./threat-model.md) §9.1. For the original mention of intent-based delegation, see [philosophy.md](./philosophy.md) §5.1.

---

## 1. Why Delegation Matters

Humans acting through agents will face many small, repetitive economic decisions. Requiring an explicit prompt for every one is the approval-fatigue problem ([threat-model.md](./threat-model.md) §9.1, [glossary.md](./glossary.md) §21): when prompts are too frequent, review degrades into a reflex, and the sovereignty approval is meant to protect is weakened.

Delegation is the question of whether a human can decide *in advance*, within limits, so not every action needs a fresh prompt — without surrendering authority. This document bounds that question using the Canon: how far delegation can go before it stops being an exercise of human authority and becomes its abdication.

ARC does not treat delegation as the preferred mode. Manual approval remains the default ([philosophy.md](./philosophy.md) belief 1, [README](../README.md) §9). Delegation is an explicit, bounded, revocable exception.

## 2. Human Approval as a Constraint

From [authority-and-conflict.md](./authority-and-conflict.md) §3, a human is the final authority over their own action and their own risk — a negative right. Approval is the protocol moment that exercises it.

In Canon terms, approval is an `AUTHORIZE` event (predicate `consent.approval`) referencing a specific offer within its validity window ([event-registry.md](./event-registry.md) §4.3). It is evidence that a human licensed a specific action.

Approval is a hard constraint, not a step to optimize away. No projection and no agent may license a meaningful economic action on a human's behalf without an `AUTHORIZE` that traces to that human. Delegation does not remove this constraint; it changes the *shape* of the `AUTHORIZE`.

## 3. Delegation Is Not Full Autonomy

Delegation means issuing an `AUTHORIZE` in advance, with a scope, rather than one per transaction. The human still authored the authority — they pre-shaped it.

Full autonomy would mean an agent acting with authority no human granted, or beyond any human-set bound. ARC rejects that ([roadmap.md](./roadmap.md), "What Is Not On This Roadmap"; [philosophy.md](./philosophy.md)).

The distinction is precise:

- a **delegated** action is still covered by a human's `AUTHORIZE` — a scoped, earlier one
- an **autonomous** action is covered by no `AUTHORIZE` at all

The first is sovereignty exercised ahead of time; the second is sovereignty removed. Delegation lives strictly on the first side. A mandate broad enough to cover anything indefinitely is autonomy wearing a mandate's clothes — which is why scope (§5) is what keeps delegation from collapsing into autonomy.

## 4. Spending Mandates

A spending mandate is an `AUTHORIZE` (predicate `consent.mandate`) that authorizes a *class* of future actions within explicit limits, instead of a single offer. It is the same primitive as an approval, with a wider referent — not a new event type.

It is the consumer-side counterpart to the provider-side credential scope already in [identity.md](./identity.md) §2.3 (`agent_scope`). Earlier documents mentioned consumer delegation but never specified it ([philosophy.md](./philosophy.md) §5.1, [README](../README.md) §9); here it is expressed in Canon terms.

A mandate is **evidence** — a signed `AUTHORIZE`. Whether a given action is *covered* by it is a **projection** ([object-model.md](./object-model.md) §4): fold the mandate, the actions already taken under it, and any `nullifies`, then check the candidate action against the remaining scope. The "state" of a mandate (active, expired, exhausted, revoked) is therefore a projected view, not a stored field.

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

The safety of delegation lives entirely in scope. An unbounded mandate is indistinguishable from autonomy. Scope dimensions are those already named in [event-registry.md](./event-registry.md) §4.3:

- **budget limits** — a total or per-transaction ceiling (for example, routine grocery orders under a cap)
- **merchant limits** — only named or verified merchants, or only those whose reputation projection clears a threshold
- **category limits** — only a commerce category (food, transit), not arbitrary purchases
- **time limits** — an `expires_at` after which the mandate is no longer in force

Scope is conservative by default, mirroring [identity.md](./identity.md) §6.4: a mandate grants the minimum, and anything outside it falls back to per-transaction approval — never to silent action.

A reputation threshold inside scope is a **projection input, not a stored score**: "only merchants whose reputation projection clears X in this context" is evaluated by folding events at decision time ([reputation.md](./reputation.md), [object-model.md](./object-model.md)).

A practical limit follows: scope you cannot express precisely is scope you should not delegate. The harder a constraint is to state, the more it should stay manual.

## 6. Revocation

A mandate must be withdrawable. In the Canon, revocation is not a new event — it is the `nullifies` field ([event-registry.md](./event-registry.md) §4.6).

```txt
AUTHORIZE (mandate M)
        ↓
later event with nullifies: [M]   →   M is no longer in force going forward
```

Revocation is forward-looking: it stops future coverage. Actions validly taken under M before revocation remain attributable events — under the object model, events are immutable and history cannot be un-signed ([object-model.md](./object-model.md)). Whether an *in-flight* transaction is affected is an open question (§10).

Key compromise interacts with this: revoking or rotating the signing key (a `KEY` event) also ends the mandates that depended on it ([reputation.md](./reputation.md) §9, [identity.md](./identity.md) §6.2).

## 7. Approval Fatigue

Delegation is often proposed as the answer to approval fatigue ([threat-model.md](./threat-model.md) §9.1). It does not dissolve the problem; it **relocates** it.

This is the same pattern named in [authority-and-conflict.md](./authority-and-conflict.md) §8 as warning fatigue and click-through sovereignty. With delegation, the risk moves from *prompt frequency* to *mandate-design quality* and *audit-review quality*. A human who sets a broad mandate once and never reviews the audit trail is as un-sovereign as one who taps "approve" without reading.

[philosophy.md](./philosophy.md) §5.1 records this exact tension: intent-based delegation may reduce prompts, but both excessive prompts and unread audit logs weaken meaningful attention. ARC does not claim delegation solves it.

The honest framing: delegation trades a frequent, shallow decision for a rare, consequential one. That is a gain only if the rare decision — the mandate — is made well and revisited. Friction *quality*, not quantity, remains unsolved.

## 8. Failure Cases

In every case below, the safe default is to narrow back to explicit human approval, never to widen silently.

- **Mandate expired.** A candidate action arrives after `expires_at`. The projection finds no in-force mandate and falls back to explicit approval. It must not silently proceed (compare [stale-offer-approval.json](../examples/local-commerce-demo/artifacts/stale-offer-approval.json)).
- **Merchant changed.** An offer's terms (`ATTEST`) differ materially from what the mandate assumed, or the merchant is outside the allowed set. The action is outside scope, so re-approval is required.
- **Amount exceeded.** Folding prior actions under the mandate leaves insufficient remaining budget for the candidate. It is not covered; re-approval is required.
- **Authorization conflict.** Two mandates overlap with different limits, or a mandate would cover an action that community or projection signals warn against. The Canon answer is not silent resolution: the override friction of [authority-and-conflict.md](./authority-and-conflict.md) §7 applies — show the conflict, require a deliberate human act, and record `contrary_to` on any `AUTHORIZE` that proceeds against a warning. A mandate does not pre-empt the override-friction boundary.

## 9. Community vs Personal Authority

A human may only delegate authority they actually hold. From [authority-and-conflict.md](./authority-and-conflict.md) §3–§4, human authority covers a person's own action and risk, while community authority covers the commons. These domains do not overlap.

Therefore a personal mandate can authorize the human's *own* spending and action, but it cannot:

- grant or delegate commons authority — it cannot make the network host, endorse, or protect anyone (the negative-right limit, §3), and it cannot stand in for a community's `ADJUDICATE` (`gov.*`)
- silently pre-authorize away community protections — stepping outside the commons (for example, transacting with an expelled party) still requires the explicit override friction of [authority-and-conflict.md](./authority-and-conflict.md) §6–§7, even under a broad mandate

Conversely, a community cannot mandate a person's private spending. Mandates are personal-domain instruments; governance decisions (`ADJUDICATE`) remain the commons-domain instrument. The two never substitute for each other.

## 10. Open Questions

- **In-flight transactions at revocation.** What happens to an action already initiated under a mandate the instant it is revoked?
- **Friction quality.** What makes a mandate decision *meaningful* rather than another reflexive accept? Unsolved, and shared with §7.
- **Scope expressiveness.** Many real constraints ("only if I actually need it") are not cleanly expressible as budget, merchant, category, or time. What belongs to delegation, and what must stay manual?
- **Audit-review burden.** Who or what ensures the human revisits the audit trail of delegated actions? An unread trail is not oversight.
- **Compromised approval surface.** A delegated flow trusts the agent to enforce scope, yet [compromised-consumer-agent.json](../examples/local-commerce-demo/artifacts/compromised-consumer-agent.json) shows an agent can misreport. Can scope enforcement be checked independently of the consumer agent — at the approval device or the payment provider? Unresolved. [key-custody.md](./key-custody.md) §2 takes a position on part of this — scope enforcement belongs in the signer's trusted base, with the key, not in the agent — while the residue (a compromised signer) remains open.
- **Mandate portability.** Does a mandate scoped in one community carry meaning in another? This relates to reputation portability ([reputation.md](./reputation.md) §10).

## 11. Current ARC Position

Delegation in ARC is exploratory and additive by reuse. It is the existing `AUTHORIZE` event given a `scope` and an `expires_at`, revoked through `nullifies`, evaluated by projection, and bounded by the authority model. No new primitive, event type, Canon, or governance structure is introduced.

Manual human approval remains the default and the fallback. Delegation is an explicit, scoped, revocable, auditable exception, and ARC does not present it as a preferred or safe mode.

ARC's claim is narrow: it can describe *how far* delegation may go — over one's own risk only, within explicit scope, revocable, never reaching into the commons, never past override friction — not that it has made delegation safe. The quality of mandate design and audit review remains the unsolved center, shared with the approval-fatigue problem.

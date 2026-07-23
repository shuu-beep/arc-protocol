# ARC Protocol: Authority and Conflict

> **Status:** Exploratory authority-boundary draft
>
> **Purpose:** Define which signal prevails when ARC's trust signals conflict, by separating authority across resource domains.
>
> This document aligns current Event and Projection work so that the meaning of expulsion, challenge, revocation, warning, and override does not drift. It is not law, not an enforcement mechanism, and not a wire format.
>
> For governance process, see [governance.md](./governance.md). For legal and payment limits, see [liability-boundaries.md](./liability-boundaries.md). For reputation signals, see [reputation.md](./reputation.md). For adversarial pressure, see [threat-model.md](./threat-model.md).

---

## 1. Status and Scope

ARC produces at least four trust-related signals: **human approval**, **event history**, **relationship projection**, and **community governance**. These signals can disagree. A user may approve a transaction that projection flags as risky and that a community has warned against. A user may want to transact with a merchant the community has expelled.

When signals conflict, ARC needs a stable answer to one question: *who decides?*

This document answers that question by defining **boundaries of authority**, not a universal hierarchy of power. It is an exploratory boundary model, not a finalized rulebook. It does not claim that ARC can enforce any of this in production. Its job is narrow: keep authority semantics consistent across the object model, Event registry, and named Projections.

## 2. Authority Is Separated by Resource Domain

ARC's current authority semantics do not designate one internal actor as supreme across every resource domain.

Authority is **separated by resource domain**: a human's own action and risk are distinct from a community's declared commons. This is a semantic boundary, not a required deployment or federation topology. A deployment or named profile may declare an adjudication authority or precedence rule within a stated scope; base ARC does not select one universal authority-of-last-resort topology.

## 3. Human Authority

A human is the final authority over **their own actions and their own risk**.

This is a **negative right**, not a positive one:

- A human *may* act on their own behalf even against projection warnings or community signals.
- A human *may not* compel the network to trust, host, endorse, or protect any party.

Projection and governance may inform, warn, or add friction to a human's own action. They may not veto it.

This authority is bounded. It covers the human's own resources and risk. It does not extend to shared resources, and it does not extend to other parties.

## 4. Community Authority

A community is the final authority over **its commons**:

- shared discovery and directory surfacing
- shared reputation, discovery, or standing policy
- dispute and recovery support
- membership in the community's protected space

A community may withdraw any of these from a participant. A community may *not* reach past its commons to forbid a human's own action.

A named community profile may bound its process through appeal, transparency, proportionality, and anti-capture safeguards (see [governance.md](./governance.md)). External legal, contractual, provider, and professional obligations remain independent (section 8). Authority over the declared commons is not authority over a person's own action.

## 5. Events and Projections Are Not Authorities

Two of the four signals are not authorities at all.

- **Events are evidence.** Under a declared security profile, an Event can attribute covered bytes and a timestamp claim to a key. It does not establish the referent as true or decide anything.
- **Projections have no authority of their own.** A named governance or application profile may use a relationship or reputation Projection to trigger review or friction, but an authoritative change requires an authorized decision under that profile.

Projection signals may trigger human or community review under a named profile. The Projection itself does not decide; any resulting penalty or commons change must trace to the authority declared by that profile.

## 6. Expulsion Means Commons Withdrawal

Expulsion is the withdrawal of access to a declared community commons, not control over a person's own action.

Under an illustrative named community profile, expulsion may mean:

- the participant is removed from community discovery, reputation endorsement, and dispute support
- a human *may still* choose to transact with that participant
- but they do so outside the profile's commons: no discovery surfacing, reputation backing, or dispute recourse; the application may display the recorded expulsion ruling

Expulsion changes what the community offers. It does not seize the human's agency. (Compare a banned account on a hosting platform: the account may still self-host; the platform withdraws only its own commons.)

A named profile may require a new entry decision before restoring commons access.

## 7. Optional Override-Friction Policy

When a human's intent conflicts with community or Projection warnings, a named application profile may require an explicit override step. Base ARC records the relevant `AUTHORIZE` and any declared `contrary_to` references; it does not mandate a user interface or review cadence.

Such a profile may increase explicit friction in proportion to its declared risk policy:

- show the conflicting signals and exactly what protection is being given up
- make the override deliberate, slow, and clearly recorded
- avoid one-tap continuation for high-divergence actions

Repeated warnings can produce warning fatigue and low-attention approval. Review quality and burden remain unmeasured (see approval fatigue in [threat-model.md](./threat-model.md) §9.1).

Override friction is one application-policy mechanism for presenting the boundary between human authority and community or Projection signals. Its effectiveness is not established.

## 8. External Law

ARC does not replace courts, consumer protection law, criminal law, professional regulation, or payment-network rules.

External law and payment-provider processes may constrain an ARC deployment. Community decisions are not legal judgments. A human's authority over their own action does not remove legal liability, and does not settle responsibility among the parties involved (see [liability-boundaries.md](./liability-boundaries.md)).

External legal, contractual, provider, and professional obligations may constrain participants and remain outside ARC. ARC does not define a hierarchy among jurisdictions or external authorities.

## 9. Event Layer and Policy Layer

Sections 2 and 5 establish separated resource domains and that Events are evidence, not verdicts. One case makes that boundary concrete: what happens when two community authorities recognized by a reader's profile — each acting over its own declared commons (section 4) — reach **conflicting** decisions about the same subject?

Suppose community A suspends a merchant while community B, reviewing the same merchant, only warns it. The reader recognizes both authorities, both ruling records pass its declared checks, and both are recorded as `ADJUDICATE` Events. The Event vocabulary can represent the opposed rulings, but base ARC supplies no canonical precedence between them. A named profile may declare one; using only an untrusted timestamp would not establish principled precedence.

This separates two layers:

- **The Event Layer records attributable signed claims and decisions.** Parties holding the same disclosed Events can inspect the same recorded rulings, and the same named Projection under the same declared inputs returns the same reading ([object-model.md](./object-model.md) §4). The records can represent a conflict, but cannot by themselves choose a winner.
- **The Policy Layer chooses which authority to honor.** A reader, community, or implementation applies a named policy declaring whose ruling it accepts. Different policies may produce different internally reproducible answers. This choice lives *outside* the Event Canon and does not require a particular federation topology.

**Event Layer = attributable records. Policy Layer = declared interpretation.** Base ARC does not select a canonical winner for conflicting authorities. A named profile may supply precedence within its scope, and must disclose that choice as a policy input.

A new Event type would not close this gap. One could record a "final" ruling in an additional Event, but a named profile would still need to identify the authority allowed to issue it. Authority selection sits upstream of the Event vocabulary. Base ARC leaves that precedence unspecified; deployments may declare it within scope.

Resolution policies can still be layered on top — *illustratively*, not canonically. The executable probe in [`examples/canon-fold-demo`](../examples/canon-fold-demo/) demonstrates conflicting adjudication events resolving to `canonical_winner = None`, then applies example reader policies such as **subscriber choice** (honor the authority you subscribe to), **most-restrictive-wins** (a safety-biased ordering), and **explicit precedence** (a reader-supplied order). These are illustrations of *where* resolution can live, not recommendations. ARC endorses none of them, defines no federation or bridge rule here, and leaves the choice of policy — and of who agrees on a policy — to communities and readers.

**Revocation points the same way.** When authority granted at one time is later withdrawn — a delegation revoked, a key retired — the Canon represents the withdrawal as an ordinary Event carrying `nullifies`, not a new type. (One thing is *not* returned to policy: who may withdraw. [event-registry.md](./event-registry.md) §4.6 honors a `nullifies` only from the target's author or its rotation lineage; an unauthorized withdrawal is recorded evidence, nothing more.) What the Canon does *not* settle is whether a current reader continues to honor an action that already *completed* under the prior authority. The probe in [`examples/authority-revocation-demo`](../examples/authority-revocation-demo/) establishes an *as-of-act-time* baseline from an earlier Event subset, then folds the same full current log under preserve and cascade policies. Both current-log policies return that the act had coverage under the fixture's act-time inputs and that the mandate is no longer in force now; they differ only on whether the completed act is honored now. It suggests a three-layer reading: **revocation is a signed withdrawal record**; **whether a reader honors the completed act now is a Projection choice**; and **invalidating a specific past act is an authority decision** — a separate `ADJUDICATE` referencing that act, not a side effect of the withdrawal. This is offered as a probe finding, not a settled rule.

**An illustrative federation profile points the same way.** The conflict above assumed both communities sat in one reader's view. When they sit in different communities, one possible profile uses a scoped `AUTHORIZE` to recognize another authority, withdrawn by `nullifies`. A probe in [`examples/reference-client`](../examples/reference-client/) (`federation_fixture.py`) folds one such log: a strict community suspends a vendor while a lenient one, recognizing it, dismisses the same dispute. An imported ruling is not authoritative merely because it was imported; the same adjudication reads as binding, advisory, or ignored depending on the named fold. Severing the fixture's bridge bounds future imports without changing the original `ADJUDICATE` records. With two recognized authorities and no declared precedence, the fixture's no-precedence policy returns **`CONTESTED`**. A different named profile could declare scoped precedence. These are probe findings, not a required federation topology or settled rule.

A later probe ([`examples/federation-fidelity-demo`](../examples/federation-fidelity-demo/)) folds the same bridge under three named policies. Under **binding** recognition, the importer accepts the remote authority's acts without re-folding them against the recorded mandate and therefore depends on the remote signer's interpretation. Under **advisory** recognition, the importer applies its own reading: it catches a spend over a recorded ceiling but an ambiguous term remains policy-relative. Under **ignored** recognition, the imported act has no effect. In this fixture, severance bounds future imports but does not revisit an act already honored under the binding policy. These are bounded results of the fixture's declared policies, not a required federation topology or a certification of signer fidelity.

## 10. Open Tensions

- **Harmful self-directed choices.** A human may choose to transact with a party expelled after a community ruling. A named application profile may add friction and disclose forfeited commons protection, but base ARC does not prohibit the act or establish that the UX is sufficient.
- **Captured communities.** Authority over the commons can be abused to exclude participants. Appeal, transparency, and replaceable backends are candidate mitigations whose effectiveness is unestablished ([threat-model.md](./threat-model.md) §7, [governance.md](./governance.md) §6.4).
- **Warning fatigue.** The model may rely on humans understanding warnings, while repeated warnings may reduce attention. Override-friction quality remains unmeasured.
- **Misunderstanding commons withdrawal as veto.** A user may read "expelled" as "forbidden" and believe ARC blocked them, or conversely assume community protection still applies after they have stepped outside it. Communicating commons status clearly is an open UX and protocol problem.

## 11. Current Status

This is an exploratory authority-boundary model, not an enforced rule set. Executable probes illustrate parts of it; no production implementation or universal governance profile exists.

Its purpose is to keep the meaning of authority consistent across the current Event registry and named Projection work, so that expulsion, challenge, revocation, warning, and override do not silently change resource domains.

# ARC Protocol: Authority and Conflict

> **Status:** Exploratory constitutional boundary draft
>
> **Purpose:** Define which signal prevails when ARC's trust signals conflict, by separating authority across resource domains.
>
> This document is intended to constrain later work — event type definitions and projection functions — so that the meaning of expulsion, challenge, revocation, warning, and override does not drift. It is not law, not an enforcement mechanism, and not a wire format.
>
> For governance process, see [governance.md](./governance.md). For legal and payment limits, see [liability-boundaries.md](./liability-boundaries.md). For reputation signals, see [reputation.md](./reputation.md). For adversarial pressure, see [threat-model.md](./threat-model.md).

---

## 1. Status and Scope

ARC produces at least four trust-related signals: **human approval**, **event history**, **relationship projection**, and **community governance**. These signals can disagree. A user may approve a transaction that projection flags as risky and that a community has warned against. A user may want to transact with a merchant the community has expelled.

When signals conflict, ARC needs a stable answer to one question: *who decides?*

This document answers that question by defining **boundaries of authority**, not a hierarchy of power. It is an exploratory constitutional boundary, not a finalized rulebook. It does not claim that ARC can enforce any of this in production. Its job is narrow: fix the meaning of authority *before* the object model and projection design are specified, so those layers inherit a stable constitution rather than inventing one implicitly.

## 2. No Single Final Authority

ARC has no internal supreme authority.

A single internal authority of last resort — whether a sovereign user who can command the network, or a sovereign community that can forbid a user — would reproduce the centralized control ARC exists to refuse. Concentrating final authority in one place is the failure mode, regardless of which place.

Instead, authority is **separated by resource domain**. Different parties are final over different things. They meet at a boundary, not in a hierarchy. The absence of a single internal final authority is intentional, and is itself a core design commitment.

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
- the shared reputation record
- dispute and recovery support
- membership in the community's protected space

A community may withdraw any of these from a participant. A community may *not* reach past its commons to forbid a human's own action.

Community authority is itself bounded — by appeal, transparency, proportionality, and anti-capture safeguards (see [governance.md](./governance.md)), and by external law (section 8). Authority over the commons is not authority over a person.

## 5. Events and Projections Are Not Authorities

Two of the four signals are not authorities at all.

- **Events are evidence.** A signed event attributes a statement to a key at a point in time. It does not decide anything. It is the substrate other parties reason over.
- **Projections are advisory.** A relationship or reputation projection is a computed risk signal. It must not automatically punish, veto, or expel.

Projection signals may trigger human review or community review. Converting a projection *directly* into a penalty would make an algorithm the authority — the centralized agent bias ARC opposes ([philosophy.md](./philosophy.md) §3). Risk signals raise review and friction; they do not decide.

## 6. Expulsion Means Commons Withdrawal

Expulsion is the withdrawal of community commons, not the imprisonment of will.

When a community expels a participant:

- the participant is removed from community discovery, reputation endorsement, and dispute support
- a human *may still* choose to transact with that participant
- but they do so outside the commons: no discovery surfacing, no reputation backing, no dispute recourse, and with an explicit notice that the party is expelled

Expulsion changes what the community offers. It does not seize the human's agency. (Compare a banned account on a hosting platform: the account may still self-host; the platform withdraws only its own commons.)

Re-entry into the commons should require re-meeting the community's entry conditions, not silent return.

## 7. Override Friction

When a human's intent conflicts with community or projection warnings, ARC should neither silently block nor silently proceed.

It should increase **explicit, understandable friction proportional to the divergence**:

- show the conflicting signals and exactly what protection is being given up
- make the override deliberate, slow, and clearly recorded
- avoid one-tap continuation for high-divergence actions

The danger is **warning fatigue and click-through sovereignty**: a human who clicks past a warning out of exhaustion is sovereign in name only. The unresolved problem is friction *quality*, not friction *quantity* (see approval fatigue in [threat-model.md](./threat-model.md) §9.1).

Override friction is the boundary mechanism between human authority and community/projection signals. It is where the separation of authority in this document is actually exercised — and it is not yet solved.

## 8. External Law

ARC does not replace courts, consumer protection law, criminal law, professional regulation, or payment-network rules.

Where external law or a payment provider's process applies, ARC defers to it. Community decisions are not legal judgments. A human's authority over their own action does not remove legal liability, and does not settle responsibility among the parties involved (see [liability-boundaries.md](./liability-boundaries.md)).

External law is the only authority that sits above both human and community authority — and it sits outside ARC.

## 9. Event Layer and Policy Layer

Sections 2 and 5 establish that there is no single final authority and that events are evidence, not verdicts. One case makes that boundary concrete: what happens when two *legitimate* community authorities — each final over its own commons (section 4) — reach **conflicting** decisions about the same subject?

Suppose community A suspends a merchant while community B, reviewing the same merchant, only warns it. Both are valid authorities, both rulings are validly signed, and both are recorded as ordinary adjudication events. The conflict is **representable**: the event vocabulary holds two opposed rulings without strain. But it is **not canonically resolvable**. No event decides which authority governs; folding "the latest ruling" would resolve the conflict only by accident of timestamp, not by any principle.

This separates two layers:

- **The Event Layer records facts** — signed claims, approvals, and adjudications. It is shared, replayable, and deterministic: any party folding the same events sees the same rulings. It can represent a conflict faithfully, but it cannot, by itself, choose a winner.
- **The Policy Layer chooses which authority to honor.** It is plural and local: a reader, a community, or a federation decides whose ruling it accepts, and different readers may legitimately choose differently and reach different — equally valid — answers. This choice lives *outside* the event canon.

**Event Layer = facts. Policy Layer = choice.** ARC fixes the first and deliberately declines to fix the second. There is no canonical winner — the resolution is left open — because selecting one would reinstate the single final authority that section 2 refuses.

A new event type would not close this gap. One could *record* a "final" ruling in some additional event, but that only relocates the question: who has the authority to issue that final event? The authority-selection problem sits upstream of the event vocabulary, not inside it. This reinforces the no-single-final-authority principle rather than weakening it: the conflict is real, it is surfaced honestly, and its resolution is returned to local choice.

Resolution policies can still be layered on top — *illustratively*, not canonically. The executable probe in [`examples/canon-fold-demo`](../examples/canon-fold-demo/) demonstrates conflicting adjudication events resolving to `canonical_winner = None`, then applies example reader policies such as **subscriber choice** (honor the authority you subscribe to), **most-restrictive-wins** (a safety-biased ordering), and **explicit precedence** (a reader-supplied order). These are illustrations of *where* resolution can live, not recommendations. ARC endorses none of them, defines no federation or bridge rule here, and leaves the choice of policy — and of who agrees on a policy — to communities and readers.

**Revocation points the same way.** When authority granted at one time is later withdrawn — a delegation revoked, a key retired — the canon again represents it without strain: the withdrawal is an ordinary event carrying `nullifies`, not a new type. (One thing is *not* returned to policy: who may withdraw. [event-registry.md](./event-registry.md) §4.6 honors a `nullifies` only from the target's author or its rotation lineage; an unauthorized withdrawal is recorded evidence, nothing more.) What the canon does *not* settle is whether an action that already *completed* under the prior authority survives. The probe in [`examples/authority-revocation-demo`](../examples/authority-revocation-demo/) folds one revoked-authority log two ways — *as-of-act-time*, where the completed act is preserved, and *current-log*, where a retroactive reading collapses it — and shows them diverge on the same signed events. It suggests a three-layer reading: **revocation is an event fact** (one signed withdrawal); **whether it cascades onto a completed act is a projection choice** (the same policy layer above); and **invalidating a specific past act is an authority decision** — a separate `ADJUDICATE` referencing that act, not a side effect of the withdrawal. This is offered as a probe finding, not a settled rule: as with conflicting rulings, ARC fixes the fact and returns the reading to local policy.

**Federation points the same way.** The conflict above assumed both communities sat in one reader's view. When they sit in *different* communities, one must first **recognize** the other before its rulings can matter — and recognition needs no new type: it is a scoped `AUTHORIZE` ("I will read your adjudications, in this domain"), withdrawn by the same `nullifies`. A probe in [`examples/reference-client`](../examples/reference-client/) (`federation_fixture.py`) folds one such log: a strict community suspends a vendor while a lenient one, recognizing it, dismisses the same dispute. Three things recur. An imported ruling is not authoritative by virtue of being imported — the same adjudication reads as binding, advisory, or ignored depending on the reader's fold. A recognition bridge can only **route** authority the reader already grants; it cannot mint trust or rank communities numerically — the same composite ranking section 5 refuses, now between communities. And severing a bridge **bounds future imports but does not sort the past**: the contested cell outlives the bridge that created it, and the only fold that "resolves" it does so by voiding the bridge's whole history — resolution by amnesia. With two recognized authorities and no precedence between them, **`CONTESTED` is the honest terminal output**; only an authority of last resort would dissolve it, the corner section 2 declines. Offered as a probe finding, not a settled rule.

A later probe ([`examples/federation-fidelity-demo`](../examples/federation-fidelity-demo/)) folds the same bridge once more, asking what crosses it when the recognized community's *signer* reads its mandate loosely (the fidelity residue of [key-custody.md](./key-custody.md) §5). Recognition routes events, not interpretations — the importing community still folds the imported act under *some* reading. Read the bridge as **binding**, deferring to the other community's authority without re-folding the act against the mandate as written, and the other signer's reading travels along with its authority; read it as **advisory**, re-folding locally, and a drift against a *recorded* bound is caught (a spend over an on-log ceiling) while an ambiguous term only reproduces the honest disagreement above, substituting one reading for the other rather than certifying either; read it as **ignored** and nothing crosses. So the same binding/advisory/ignored choice that routes *whose authority* counts also decides *whose interpretation* travels with it: **binding recognition makes signer fidelity a transitive dependency**, extending a community's reliance on its own signer to a signer one community away, which it observes even less. Severance keeps its earlier shape — it bounds future imports but does not sort the past, so an act already honored under a binding bridge outlives the bridge. This routes-but-does-not-mint once more, now routing interpretation rather than authority, and needs no new type — the bridge is still one scoped `AUTHORIZE`. Offered as a probe finding, not a settled rule, and not a claim that federation is unsafe: only that a binding bridge is a reading inherited, not merely an authority recognized.

## 10. Open Tensions

- **Harmful self-directed choices.** A human's negative right to act may lead to self-harm, such as transacting with an expelled fraudster. ARC's response is friction and forfeited commons protection, not prohibition. Whether that is sufficient is unresolved.
- **Captured communities.** Authority over the commons can be abused to exclude legitimate participants. Appeal, transparency, and replaceable backends mitigate but do not eliminate this ([threat-model.md](./threat-model.md) §7, [governance.md](./governance.md) §6.4).
- **Warning fatigue.** The model relies on humans understanding warnings, but warnings degrade with repetition. Override friction quality remains unsolved.
- **Misunderstanding commons withdrawal as veto.** A user may read "expelled" as "forbidden" and believe ARC blocked them, or conversely assume community protection still applies after they have stepped outside it. Communicating commons status clearly is an open UX and protocol problem.

## 11. Current Status

This is an exploratory constitutional boundary, not an enforced rule set. No implementation exists.

Its purpose is to fix the meaning of authority before event types and projection functions are defined, so that expulsion, challenge, revocation, warning, and override carry stable meaning across later documents. The next useful work is to define the canonical event types and the projection function consistent with these boundaries.

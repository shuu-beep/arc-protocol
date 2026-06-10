# ARC Protocol: Trust Model Trade-offs

> **Status:** Exploratory consolidation note
>
> **Purpose:** Gather the trust-model trade-offs already scattered across the corpus into one coordinate system, so they can be reasoned about together.
>
> This document is a tidy-up, not a discovery. It introduces no new primitive, event type, Canon, or governance structure. Every tension below already appears in [glossary.md](./glossary.md) §23, [reputation.md](./reputation.md) §17, [local-commerce-simulation.md](./local-commerce-simulation.md) §10, and [threat-model.md](./threat-model.md) §16; this note only reorganizes them. Following [glossary.md](./glossary.md) §23, it preserves unresolved trade-offs rather than pretending to settle them.
>
> For the object model these trade-offs operate on, see [object-model.md](./object-model.md). For positioning language used here, see [landscape-and-positioning.md](./landscape-and-positioning.md) §9.

---

## 1. Why This Document Exists

ARC's trust trade-offs are real but scattered: a list in [glossary.md](./glossary.md) §23, a tensions section in [reputation.md](./reputation.md) §17, simulation tensions in [local-commerce-simulation.md](./local-commerce-simulation.md) §10, and design implications in [threat-model.md](./threat-model.md) §16. Read separately they look like unrelated caveats.

Read together they fall onto two axes. This note states those axes once, so later work can locate a given tension instead of rediscovering it. It adds nothing to the model; it only makes the existing shape legible.

## 2. The Core Trilemma

Three properties a reputation system might want cannot all be held at once:

- **Portability** — reputation moves across communities. Valuable (it prevents lock-in, see [reputation.md](./reputation.md) §10), but it lets reputation earned in a weak or captured context be imported where it was not earned (laundering).
- **Sybil-resistance** — real expulsion and real accountability need identity persistence and cost ([threat-model.md](./threat-model.md) §4, [governance.md](./governance.md) §6.1). But persistent, costly identity pulls against the next property.
- **Privacy / no universal score** — local-first, contextual, non-concentrated trust, with no global profile of a person ([reputation.md](./reputation.md) §3.4, [object-model.md](./object-model.md) §6). But removing the global anchor removes the thing that would otherwise stop Sybil and laundering.

Strengthening any one tends to weaken another. There is no setting that maximizes all three at once.

## 3. ARC Has Chosen a Corner

ARC does not claim to beat the trilemma. It picks a corner.

ARC favors local, contextual, non-transferable reputation ([reputation.md](./reputation.md) §3.1, §13), computed as an on-demand projection over signed events with no stored global profile ([object-model.md](./object-model.md)). In trilemma terms, ARC **sacrifices full portability** to keep **Sybil-resistance and privacy within one bounded community**.

This is a legitimate choice, but it does not dissolve the trilemma. It **relocates** it — to the boundary between communities (spatial axis, §4) — and it leaves one face of the problem entirely untouched (temporal axis, §5).

Locality is also ARC's scaling stance: by reducing the global negotiation surface, it lowers scaling pressure. This is not a claim that ARC solves internet-scale coordination — it is a claim that ARC tries to need less of it.

## 4. The Spatial Axis: Portability ↔ Sybil-resistance ↔ Privacy

Locality relaxes this axis *inside* a single community: within one bounded context, trust is local, cheap to keep contextual, and needs no global score.

At the boundary *between* communities it returns in full:

- importing reputation reopens Sybil and laundering risk ([reputation.md](./reputation.md) §10, [threat-model.md](./threat-model.md) §13.1)
- refusing all import leaves every community with its own cold start, and a malicious actor expelled in one can re-enter another fresh ([bootstrap-and-incentives.md](./bootstrap-and-incentives.md) §8, [reputation.md](./reputation.md) §13)

So locality does not remove the spatial tension; it **converts it into a bootstrap tax** — N communities, N cold starts — paid in exchange for keeping Sybil-resistance and privacy local. The existing knob is the receiving community's choice: accept fully, partially weight, require probation, require extra verification, or reject ([reputation.md](./reputation.md) §10). None of these options is free, and none is settled.

## 5. The Temporal Axis: Decay ↔ Recovery ↔ Attack

Locality does nothing for this axis. Even inside one community, the same tension persists over time:

- **Decay** — old trust should lose weight as ownership, staff, and behavior change ([reputation.md](./reputation.md) §7). Decay too fast and an honest dormant participant is punished; decay too slow and stale trust misleads.
- **Recovery** — ordinary failure should be recoverable ([reputation.md](./reputation.md) §8). Make recovery too easy and abuse is forgiven; too hard and honest rehabilitation is foreclosed.
- **Attack** — the gap between decay and recovery is exactly where wash-trading lives: build reputation, abuse it, let it decay, rebuild ([reputation.md](./reputation.md) §6 velocity, §12 collusion heuristics; [colluding-reputation-farming.json](../examples/local-commerce-demo/artifacts/colluding-reputation-farming.json)).

The existing knobs — velocity limits, weighting old vs recent history, review triggers on sudden spikes — manage but do not resolve this. Detection thresholds remain unsolved ([threat-model.md](./threat-model.md) §16, §18).

## 6. Why Locality Relocates But Does Not Dissolve

Putting the two axes together:

- the **spatial** tension is relaxed inside a community and reappears at the inter-community boundary as a bootstrap tax
- the **temporal** tension is untouched by locality and persists everywhere

ARC's locality choice is therefore best understood not as a solution but as a *relocation*: it trades a hard cross-community problem for many local cold starts, and it does not address trust over time at all.

A reference-client fixture ([`examples/reference-client`](../examples/reference-client/), `coldstart_fixture.py`) suggests a sharper formulation of what each relocated cold start *is*: **legitimacy is not a property of a node — it is a relation between an observer's fold policy and the log.** In the fixture, three observers fold the same events through three defensible policies (a path from one's own root, outcome history, transitive vouching) and legitimately disagree about the same newcomers, with each policy failing on a different one. The corollary is that **observer policy is unavoidable**: even a stored global score would not escape the choice, it would only be one policy imposed on everyone — the corner ARC already declines (§7). This is offered as a probe finding, not a settled rule: ARC fixes the evidence and returns the reading to the observer.

## 7. The Defining Proposition: Computed vs Governed Trust

Underneath both axes sits one proposition, already stated as positioning language in [landscape-and-positioning.md](./landscape-and-positioning.md) §9: is trust **computed** (a score or proof on shared infrastructure) or **governed** (a community process over evidence)?

A single stored universal score would appear to ease the spatial axis (portable by construction) and the simplicity problem (one number). ARC declines it, because that same global number is the privacy failure ([object-model.md](./object-model.md) §6) and turns the temporal-attack surface into one target worth gaming globally. ARC accepts more friction — local cold starts, contextual projection, community review — to avoid a stored global profile.

This is a bet, not a verdict, and the terms "computed" and "governed" are positioning language, not ARC protocol primitives.

## 8. Related Trade-offs That Are Not the Trilemma

For completeness, the other tensions in the scattered sources, with where they already live. These are adjacent to the trilemma, not part of it:

| Trade-off | Where it already appears |
| --- | --- |
| Privacy vs auditability | [reputation.md](./reputation.md) §17, [local-commerce-simulation.md](./local-commerce-simulation.md) §10, [threat-model.md](./threat-model.md) §12 |
| Human review vs approval fatigue / governance burden | [local-commerce-simulation.md](./local-commerce-simulation.md) §10, [threat-model.md](./threat-model.md) §9.1, [delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md) §7 |
| Discovery openness vs ranking manipulation | [local-commerce-simulation.md](./local-commerce-simulation.md) §10, [threat-model.md](./threat-model.md) §6 |
| Local governance vs sustainable / capture-resistant review | [governance.md](./governance.md) §6.4, §8.1 |
| Rapid resolution vs procedural fairness | [local-commerce-simulation.md](./local-commerce-simulation.md) §10 |
| Simplicity vs accuracy (one score vs contextual trust) | [reputation.md](./reputation.md) §17 |

## 9. What ARC Does Not Claim

This consolidation does not resolve any trade-off. It makes them legible, not solved. No knob named here is new, and none is presented as sufficient. Consistent with [glossary.md](./glossary.md) §23, the unresolved trade-offs are kept visible on purpose.

## 10. Open Questions

- Is there any safe standard for cross-community reputation import, or must the bootstrap tax always be paid in full? (spatial)
- What detection thresholds distinguish wash-trading from honest early activity without punishing newcomers? (temporal, shared with [reputation.md](./reputation.md) §6, §12)
- Is any degree of portability safe, or does portability always reopen the privacy/Sybil corner?
- Friction quality — the unsolved center shared with approval fatigue and delegation ([delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md) §7) — cuts across these axes whenever a human is asked to weigh imported or aged trust.

## 11. Current ARC Position

This is a consolidation note. It introduces no new primitive, event type, Canon, or governance structure, and it reorganizes existing material from [glossary.md](./glossary.md) §23, [reputation.md](./reputation.md) §17, [local-commerce-simulation.md](./local-commerce-simulation.md) §10, and [threat-model.md](./threat-model.md) §16 into two axes:

- **spatial** — portability ↔ Sybil-resistance ↔ privacy, relaxed locally and relocated to the inter-community boundary as a bootstrap tax
- **temporal** — decay ↔ recovery ↔ attack, untouched by locality

The defining proposition beneath both is computed vs governed trust. ARC has chosen a governed, local corner, and remains honest that this relocates the trilemma rather than dissolving it.

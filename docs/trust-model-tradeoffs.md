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

## 2. A Recurring Three-Way Trade-off

The current reputation research repeatedly encounters tension among three properties:

- **Portability** — a compatible profile may import reputation evidence across contexts. This may reduce switching cost, but may also import signals from a weak or captured context ([reputation.md](./reputation.md) §10).
- **Sybil resistance** — identity continuity, external anchors, and participation cost are candidate profile controls ([threat-model.md](./threat-model.md) §4, [governance.md](./governance.md) §6.1). They do not prove distinct principals and may increase exclusion or privacy risk.
- **Privacy / no universal score** — a contextual profile can avoid requiring one global profile of a person ([reputation.md](./reputation.md) §3.4, [object-model.md](./object-model.md) §6). That choice may limit evidence sharing while leaving Sybil and import-manipulation risks unresolved.

Strengthening one may weaken another under a given identity, disclosure, and import policy. This note does not establish a formal impossibility result or identify a setting that maximizes all three.

## 3. Policy Explored by the Commerce/Reputation Research

The current Commerce/reputation research explores one policy choice; base ARC does not mandate it.

That research uses local, contextual, non-transferable reputation ([reputation.md](./reputation.md) §3.1, §13), computed as a named Projection over declared Events rather than an authoritative global profile ([object-model.md](./object-model.md)). It accepts less portability. Locality alone does not establish Sybil resistance, privacy, or a required community topology.

This choice moves some questions to boundaries between contexts (spatial axis, §4) and leaves time-dependent reputation questions open (temporal axis, §5).

The current documents have not established the scaling effects of this policy. A local deployment may reduce some shared coordination requirements while duplicating others.

## 4. The Spatial Axis: Portability ↔ Sybil-resistance ↔ Privacy

Within one bounded context, a local profile can avoid requiring a global score. Sybil, privacy, disclosure, and governance risks still depend on the profile and deployment.

At boundaries between communities, related risks may appear:

- importing reputation may increase Sybil and evidence-laundering risk ([reputation.md](./reputation.md) §10, [threat-model.md](./threat-model.md) §13.1)
- refusing all import leaves every community with its own cold start, and a malicious actor expelled in one can re-enter another fresh ([bootstrap-and-incentives.md](./bootstrap-and-incentives.md) §8, [reputation.md](./reputation.md) §13)

Locality can therefore create recurring cold-start costs across communities. A receiving community may accept imported evidence, partially weight it, require probation or additional checks, or reject it ([reputation.md](./reputation.md) §10). None of these policies is settled, and none by itself establishes Sybil resistance or privacy.

## 5. The Temporal Axis: Decay ↔ Recovery ↔ Attack

Locality does not by itself resolve this axis. Even inside one community, related tensions may persist over time:

- **Decay** — a named policy may reduce the weight of old evidence as ownership, staff, and behavior change ([reputation.md](./reputation.md) §7). Faster decay can disadvantage dormant participants; slower decay can retain stale signals.
- **Recovery** — a named policy may allow recovery after ordinary failure ([reputation.md](./reputation.md) §8). Easier recovery can also reduce the cost of repeated abuse; stricter recovery can exclude legitimate rehabilitation.
- **Attack** — the interaction between decay and recovery creates one possible wash-trading surface: build reputation, abuse it, let it decay, rebuild ([reputation.md](./reputation.md) §6 velocity, §12 collusion heuristics; [colluding-reputation-farming.json](../examples/local-commerce-demo/artifacts/colluding-reputation-farming.json)).

The existing knobs — velocity limits, weighting old vs recent history, review triggers on sudden spikes — manage but do not resolve this. Detection thresholds remain unsolved ([threat-model.md](./threat-model.md) §16, §18).

## 6. Effects of Locality

Putting the two axes together:

- the **spatial** tension changes across community boundaries and may recur as cold-start cost
- the **temporal** tension is untouched by locality and persists everywhere

The explored locality policy is therefore not a solution: it may exchange some cross-community coordination for repeated local cold starts, and it does not resolve time-dependent reputation questions.

A reference-client fixture ([`examples/reference-client`](../examples/reference-client/), `coldstart_fixture.py`) demonstrates policy-relative newcomer readings. Three observers fold the same supplied Events through three fixture policies (a path from one's own root, outcome history, transitive vouching) and return different results, with each policy missing a different private generator classification. The fixture shows that observer policy affects its output; it does not establish legitimacy, exhaust all policies, or require a global/local topology.

## 7. Computed and Governed Models

The positioning document distinguishes **computed** models (a score or proof on shared infrastructure) from **governed** models (a community process over evidence) ([landscape-and-positioning.md](./landscape-and-positioning.md) §9).

A shared score under a compatible interface may simplify exchange and operation while creating concentration, privacy, and gaming risks ([object-model.md](./object-model.md) §6). The current Commerce/reputation research instead explores contextual Projections and community review. Base ARC defines neither policy as a required deployment topology.

The terms "computed" and "governed" are positioning language, not ARC protocol primitives.

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

- What cross-community reputation-import profiles, if any, can state bounded privacy and manipulation properties? (spatial)
- What detection thresholds distinguish wash-trading from honest early activity without punishing newcomers? (temporal, shared with [reputation.md](./reputation.md) §6, §12)
- What bounded privacy and manipulation properties, if any, can a portable reputation profile support?
- Friction quality — the unsolved center shared with approval fatigue and delegation ([delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md) §7) — cuts across these axes whenever a human is asked to weigh imported or aged trust.

## 11. Current ARC Position

This is a consolidation note. It introduces no new primitive, event type, Canon, or governance structure, and it reorganizes existing material from [glossary.md](./glossary.md) §23, [reputation.md](./reputation.md) §17, [local-commerce-simulation.md](./local-commerce-simulation.md) §10, and [threat-model.md](./threat-model.md) §16 into two axes:

- **spatial** — portability, Sybil resistance, and privacy across context boundaries and recurring cold starts
- **temporal** — decay ↔ recovery ↔ attack, untouched by locality

The note also compares computed and governed trust as positioning language. The current Commerce/reputation research explores a governed, local policy; base ARC mandates neither that topology nor its trust heuristics.

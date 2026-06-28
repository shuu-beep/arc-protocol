# ARC Protocol: Pilot Design

> **Status:** Exploratory pilot-design note
>
> **Purpose:** Define how a limited pilot would test the inverse from [adoption-and-defection.md](adoption-and-defection.md) — learning, not validation — without making product or adoption claims.

---

## 1. What This Pilot Is For

[adoption-and-defection.md](adoption-and-defection.md) argues that the honest question is not why ARC will be adopted but why each actor can rationally decline, and it holds the countering mechanisms as hypotheses. [roadmap §Stage 5](roadmap.md) names a limited real-world test but lists only milestones. This note is the bridge: how a pilot would *test the inverse* rather than demonstrate a product.

The distinction is the whole design. A pilot built to show ARC working will find a way to look like it works. A pilot built to test the inverse asks a different question:

```txt
Which defections in adoption-and-defection §3 are real for these participants?
Which §4 candidate mechanisms, if any, actually move them?
What does a participant who still declines say no candidate would have changed?
```

The answer is data, not endorsement. The pilot succeeds when it returns honest readings of those three questions — including readings that count against ARC.

A pilot also has a precondition. The mock simulation ([local-commerce-simulation.md](local-commerce-simulation.md), runnable as [`examples/local-commerce-demo`](../examples/local-commerce-demo/)) must run first, so that the folds and the approval seam are exercised against scripted failures before any real participant is asked to rely on them. A pilot is the mock's successor, not its replacement.

## 2. What the Pilot Measures

Three instruments. Each is described by what it can *falsify*, because an instrument that can only confirm is a demonstration, not a measurement.

### 2.1 Refusal-recording

- **Instrument:** every party approached who declines is logged with the schema in [adoption-and-defection §6](adoption-and-defection.md) — `actor`, `exit` (WAIT/DEFECT/FORK/REJECT), `reason` in their own words, and which §4 candidate they say would have changed the decision.
- **What it falsifies:** a `mechanism = none` refusal is a §4 candidate falsified for that actor — the most informative cell in the pilot. The instrument is corrupted if the recorder argues the participant out of their reason; its job is faithful capture, not conversion.

### 2.2 Integration-cost measurement

- **Instrument:** measure the actual work for one real merchant stack to emit structured offers and pass the approval seam — engineering time, the changes required, what could not be expressed. This is the hypothesis in [adoption-and-defection §4.1](adoption-and-defection.md) put to a number.
- **What it falsifies:** the number neither proves ARC "cheap" nor "expensive" in the abstract; it tests whether "cheap enough to remove the first-mover cost" survives contact with one real stack. A high cost falsifies §4.1 for that stack; a low cost still buys nothing without demand on the other side, which the same pilot records as WAIT refusals (§2.1).

### 2.3 Audit-overlay exercise

- **Instrument:** run ARC's existing folds — the policy audits exercised in [`local-commerce-demo`](../examples/local-commerce-demo/) and the transaction-state projection — over one real or realistic dispute, and observe whether the overlay produces review material a participant finds usable.
- **What it falsifies:** this tests the claim in [adoption-and-defection §4.2](adoption-and-defection.md) that a recomputable record is worth more to a cautious party than a platform's word. The value is felt mainly *after* a failure, so the dispute is where it is testable. The overlay stays inside its boundary (§3): it produces evidence for a review, never a legal verdict or a guarantee of recovery. An overlay output that a participant cannot act on falsifies §4.2 for that case.

## 3. Pilot Boundaries

The boundaries are not caveats appended to a pitch; they are conditions of the design, drawn from [liability-boundaries.md](liability-boundaries.md) and [roadmap §Stage 5](roadmap.md).

- **No real payment is initiated by ARC.** Existing providers are used only after human approval and under their own rules; ARC does not guarantee refund, chargeback, or recovery ([liability §2](liability-boundaries.md), §6).
- **Community review informs trust; it does not replace law.** A pilot review may inform a local reputation note; it does not settle legal fault, consumer rights, or damages ([liability §3](liability-boundaries.md), §9).
- **No regulated-domain agents.** Law, medicine, finance, and similar fields stay outside the pilot unless reviewed under the relevant professional rules ([liability §5](liability-boundaries.md)).
- **Local, voluntary, no SLA, fully disclosed.** A single locality, volunteer participants, no production guarantees, and full transparency that this is an experiment ([roadmap §Stage 5](roadmap.md)).
- **Divergence is expected, not resolved.** Two communities holding different event sets can read the same merchant differently; the pilot makes the divergence inspectable, it does not adjudicate it ([liability §8](liability-boundaries.md)).

## 4. What Counts as Learning, Not Success

A pilot can produce a comfortable result that means nothing. These outcomes must **not** be recorded as evidence that ARC works:

- a smooth completed purchase
- high transaction volume
- a low dispute count where the complaint mechanism is weak
- fast approvals produced by reduced human review
- a recorded "yes" that no instrument in §2 actually tested

The outcomes that are worth the pilot are the ones that teach:

- a refusal recorded with `mechanism = none` (§2.1) — a candidate mechanism falsified
- a measured integration cost that contradicts §4.1 (§2.2)
- an audit-overlay output a participant could not use (§2.3)
- a defection in §3 that the pilot confirms is real for these participants

A pilot that returns friction, falsified hypotheses, or a documented refusal is more useful than one that looks efficient. A failed pilot can be as informative as a successful one.

## 5. Current Position

No pilot exists. This note is design only.

Its instruments produce measurements and falsifications, not validations: the pilot is built to earn data about the inverse, not endorsement of the protocol. A recorded refusal, an integration cost, or an unusable overlay output each tells ARC something it cannot learn from the adoption it imagines.

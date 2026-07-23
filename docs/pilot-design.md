# ARC Protocol: Pilot Design

> **Status:** Exploratory pilot-design note
>
> **Purpose:** Define how a limited pilot would test the inverse from [adoption-and-defection.md](adoption-and-defection.md) — learning, not validation — without making product or adoption claims.

---

## 1. What This Pilot Is For

[adoption-and-defection.md](adoption-and-defection.md) uses an inverse analysis of why each actor may decline and holds countering mechanisms as hypotheses. [roadmap §Stage 5](roadmap.md) names a limited real-world test but lists only milestones. This note describes how a pilot would test that inverse analysis rather than demonstrate a product.

A pilot designed only to demonstrate ARC can bias observations toward positive cases. This design instead asks:

```txt
Which defections in adoption-and-defection §3 are real for these participants?
Which §4 candidate mechanisms, if any, actually move them?
What does a participant who still declines say no candidate would have changed?
```

The intended output is documented observations, not endorsement, including observations that count against ARC's candidate mechanisms.

Under this design, the mock simulation ([local-commerce-simulation.md](local-commerce-simulation.md), runnable as [`examples/local-commerce-demo`](../examples/local-commerce-demo/)) should run first, so that the folds and Current Coverage handling are exercised against scripted failures before any real participant is asked to rely on them.

A pilot also presumes a participant has *begun to use* ARC. The step before that — first contact with a real person who has not — is [first-refusal-protocol.md](first-refusal-protocol.md), which collects a refusal as data rather than seeking an adopter. The refusal-recording instrument in §2.1 inherits its operating procedure from there.

## 2. What the Pilot Measures

The design uses three instruments. Each includes a disconfirming outcome.

### 2.1 Refusal-recording

- **Instrument:** every party approached who declines is logged with the schema in [adoption-and-defection §6](adoption-and-defection.md) — `actor`, `exit` (WAIT/DEFECT/FORK/REJECT), `reason` in their own words, and which §4 candidate they say would have changed the decision.
- **Disconfirming outcome:** a `mechanism = none` refusal records that the participant identified no §4 candidate that would change the decision. The recorder should not argue the participant out of the stated reason.
- **Synthetic check:** [`examples/refusal-recording-demo`](../examples/refusal-recording-demo/) exercises the schema on synthetic records and provides a comparison surface; it does not validate the instrument against real participants.

### 2.2 Integration-cost measurement

- **Instrument:** measure the actual work for one real merchant stack to emit structured offers and pass the approval seam — engineering time, the changes required, what could not be expressed. This is the hypothesis in [adoption-and-defection §4.1](adoption-and-defection.md) put to a number.
- **Disconfirming outcome:** the measurement neither proves ARC "cheap" nor "expensive" in the abstract. A high cost counts against §4.1 for that stack; a low cost does not establish demand on the other side, which the same pilot records through `WAIT` responses (§2.1).

### 2.3 Audit-overlay exercise

- **Instrument:** run ARC's existing folds — the policy audits exercised in [`local-commerce-demo`](../examples/local-commerce-demo/) and the transaction-state projection — over one real or realistic dispute, and observe whether the overlay produces review material a participant finds usable.
- **Disconfirming outcome:** this tests whether a participant finds the recomputable record useful in that case. The overlay stays inside its boundary (§3): it produces evidence for a review, never a legal verdict or a guarantee of recovery. An output a participant cannot use counts against §4.2 for that case.

## 3. Pilot Boundaries

These are design constraints drawn from [liability-boundaries.md](liability-boundaries.md) and [roadmap §Stage 5](roadmap.md).

- **No real payment is initiated by ARC.** Existing providers are used only when an act has Current Coverage and under their own rules; ARC does not guarantee refund, chargeback, or recovery ([liability §2](liability-boundaries.md), §6).
- **Community review may inform an application reputation note; it does not replace law.** A pilot review does not settle legal fault, consumer rights, or damages ([liability §3](liability-boundaries.md), §9).
- **No regulated-domain agents.** Law, medicine, finance, and similar fields stay outside the pilot unless reviewed under the relevant professional rules ([liability §5](liability-boundaries.md)).
- **Local, voluntary, no SLA, fully disclosed.** A single locality, volunteer participants, no production guarantees, and full transparency that this is an experiment ([roadmap §Stage 5](roadmap.md)).
- **Divergence is expected, not resolved.** Two communities holding different event sets can read the same merchant differently; the pilot makes the divergence inspectable, it does not adjudicate it ([liability §8](liability-boundaries.md)).

## 4. Learning Criteria

These outcomes alone do **not** establish that ARC works:

- a smooth completed purchase
- high transaction volume
- a low dispute count where the complaint mechanism is weak
- fast approvals produced by reduced human review
- a recorded "yes" that no instrument in §2 actually tested

Candidate observations include:

- a refusal recorded with `mechanism = none` (§2.1) — evidence against that candidate for that actor
- a measured integration cost that contradicts §4.1 (§2.2)
- an audit-overlay output a participant could not use (§2.3)
- a participant report that maps to a §3 defection category

Friction, evidence against a hypothesis, and documented refusals may be at least as useful as efficient execution for this research design.

## 5. Current Position

No pilot exists. This note is design only.

Its instruments are intended to produce bounded observations about the inverse, not validation or endorsement of the protocol.

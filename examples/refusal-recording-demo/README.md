# Refusal-Recording Demo

> **Adoption does not fold. Refusals can.**

A small, runnable probe that makes the [adoption track](../../docs/adoption-and-defection.md)
load-bearing instead of only argued. It folds a set of synthetic *refusal
records* into a falsification surface, and it draws — precisely — the line
between what ARC can compute about a refusal and what it cannot.

```
python3 refusal_fold.py
```

Stdlib only. No network, no services, no real participant data.

## The boundary this probe exists to show

The adoption frontier does not fold. ARC cannot prove why a party will
honor, join, or adopt the protocol; that incentive is off-ledger
([threat-model.md §18.1](../../docs/threat-model.md)). This probe does not
attempt it. It demonstrates the *other* half of the boundary: a refusal is
not an incentive to be modeled — it is a **record of what an actor said**,
and a record folds.

| ARC **can** compute from refusal records | ARC **cannot** compute |
| --- | --- |
| counts by actor, exit, named mechanism | whether a stated reason is *true* |
| per candidate, evidence *named* by the refuser vs *cell-coincident* (reason unread) | whether the actor would really change behaviour later |
| `mechanism = none` cases (no mechanism would have moved them) | whether adoption will or will not happen |
| where a WAIT depends on a still-missing side (mutual-WAIT deadlock) | whether a mechanism is valid *in general* |
| whether any §4 lever can break a mutual-WAIT from one side (does a *solo* lever even reach it) | whether a solo lever, where one reaches, is large enough to seed adoption |
| which exits no candidate mechanism even claims to address | whether a refusal was strategic, lazy, hostile, or honest |

A candidate mechanism is **never validated** here. The strongest a refusal
can say *for* a mechanism is "named as decisive" — and that party still
declined, so the lead is unproven. The fold can only weaken, never confirm.

## What it is not

- **Not an adoption simulator.** It runs no agents and models no market.
- **It does not predict adoption.** No output is a forecast.
- **It does not prove a refusal reason is true.** Every reason is treated as
  testimony, never as established fact.
- It only shows that **refusal records fold into falsification surfaces** —
  and that this is useful, because a recorded "no" can *weaken ARC's own
  candidate mechanisms*, which an imagined "yes" never can.

## The record

Four fields, per [adoption-and-defection.md §6](../../docs/adoption-and-defection.md):

```txt
actor      developer | company | merchant | user | community
exit       WAIT | DEFECT | FORK | REJECT
reason     the participant's own words
mechanism  which §4 candidate (4.1..4.6) they say would have changed the
           decision, or "none"
```

The fixtures in [`fixtures.json`](fixtures.json) are **synthetic and
illustrative**. They are written the way a participant might speak, but they
are not claims about any real actor.

## How the evidence is read

Each §4 candidate mechanism claims to address certain `(actor, exit)` cells.
The fold keeps two qualities of evidence deliberately apart:

- **named** — the refuser themselves pointed at this candidate as the gap.
  Reason-relevant, because they chose it — but a lead only, since they still
  declined.
- **cell-coincident** — a `mechanism = none` refusal lands in a cell this
  candidate claims. It contradicts the candidate's *claim* to address that
  cell, but the fold does not read the reason and cannot say the refuser ever
  weighed this candidate.

```txt
named  &  cell-coincident   ->  MIXED
named  only                  ->  NAMED-RELEVANT (still declined)
cell-coincident  only        ->  CELL-CONTRADICTED (reason unread)
neither                      ->  UNTESTED
```

No candidate ever reaches "validated." The strongest a refusal can say *for*
a mechanism is "named as the gap" — and that party still declined.

## Does any §4 lever break the WAIT deadlock? (fold [6])

The fold detects a mutual-WAIT deadlock; this section asks whether ARC's
candidate set can *break* one. A mutual-WAIT is a standoff over **network
value** — each party waits for the other to move, so the value each wants is
exactly the value the other is withholding. Lowering cost or sweetening a
network benefit cannot break it, because at zero counterparties the benefit is
still zero. Only a **solo** lever — value that accrues to a single adopter
with no counterparty — can make moving-first rational from one side
([survey §57](../../docs/coordination-economics-survey.md)).

So each candidate carries a `value_locus`, transcribed (not invented) from its
own §4 residue or the survey:

- **network** — value needs a counterparty (4.1, 4.3, 4.4, 4.5, 4.6).
- **mixed** — a solo thread over a network principal. ARC has exactly one:
  the audit log's *self-delegation audit* — recording and recomputing your own
  agent's approvals with no one else participating
  ([survey §109](../../docs/coordination-economics-survey.md), [adoption §4.2](../../docs/adoption-and-defection.md)).

The fold then checks, per deadlock, which candidates even *reach* it (claim a
WAIT cell of a deadlocked actor) and whether any reaching candidate is solo.
This turns survey §109's prose ("an ARC audit log has *some* solo value … a
hypothesis, not a path") into a recomputed structural test.

**The finding is a property of §4, not of the fixtures.** Across the whole §4
set, exactly one candidate claims any WAIT cell at all — 4.1 (lower
integration cost), which is **network**-value. ARC's only solo lever, 4.2,
claims `REJECT` cells, **no WAIT cell**. So:

> The deadlock-breaking lever and the deadlock do not meet. §4 answers WAIT
> with a single network-value cost-reducer, and aims its lone solo lever at
> REJECT instead. No solo lever reaches the chicken-and-egg.

This neither indicts nor predicts: it does not say adoption fails, only that
the candidate set as written contains no counterparty-independent lever
pointed at the standoff the WAIT records turn on. Whether the 4.2 solo thread
could ever be *enlarged* to reach a WAIT is an open §4 question, not something
the fold can settle — and its size is unmeasured ([survey §114](../../docs/coordination-economics-survey.md)).

## What the run shows (synthetic set)

- Every candidate lands at MIXED or CELL-CONTRADICTED — **none reaches
  validated.** The strongest reading for any candidate is "named, still declined".
- The **company / DEFECT** record — the "embrace the open spec, then withdraw
  federation once the users are ours" case — falls in a cell **no candidate
  mechanism even claims to address.** ARC's §4 set is silent on it.
- A **mutual-WAIT deadlock `{merchant, user}`** is detected: each waits on the
  other, and each is individually rational to wait.
- **No §4 lever breaks that deadlock from one side.** Only 4.1 (network) reaches
  it; ARC's one solo lever (4.2) claims REJECT, not WAIT — the lever and the
  deadlock do not meet.

## A note on the exit vocabulary

Building this probe required a classification check: does the
embrace-and-defederate pattern from
[coordination-economics-survey.md §5](../../docs/coordination-economics-survey.md)
(XMPP, RSS) need a fifth exit, e.g. `CAPTURE`?

**No.** The only thing separating a hypothetical `CAPTURE` from `DEFECT` /
`FORK` is the actor's *strategic intent* to lock users in — and intent is
exactly the off-ledger thing §18.1 forbids ARC from reading. Adding a
`CAPTURE` exit would smuggle an unobservable motive into the vocabulary,
breaking the schema's "record what they say, do not infer" rule. The pattern
decomposes cleanly without it:

- genuinely adopt, then withdraw interoperation to retain the captured base →
  **DEFECT** (stop honouring once it pays; the "pay" is the retained base);
- adopt the forms but never the substance (a compliance veneer) → **FORK**
  (a captured variant; already [adoption-and-defection §3.2](../../docs/adoption-and-defection.md)).

What is real and observable is not a new *move* but a blast-radius property:
a DEFECT or FORK by an actor holding the network also forecloses others'
exit. The fold surfaces this empirically — the company DEFECT shows up as an
*unaddressed cell*, not as a new category. Resisting the fifth exit is the
anti-motive discipline doing its job.

## Red-team notes (known limitations)

This probe was deliberately attacked after it was built. The findings are
kept here rather than smoothed away, because the most useful are *principled*
limits, not bugs.

- **The fold matches by cell, but relevance lives in the reason.** A candidate
  is tied to a refusal by its `(actor, exit)` cell, so a `mechanism = none`
  refusal contradicts *every* candidate that claims its cell — even one whose
  subject its reason has nothing to do with (a "governance is unpaid" REJECT
  contributes cell-coincident pressure to "lower integration cost"). This is
  not fixable by making the fold read the reason: parsing the reason to decide
  relevance is exactly the inference [§6](../../docs/adoption-and-defection.md)
  forbids ("a reason paraphrased into our own category is a claim in
  disguise"). The fold is therefore only as precise as §4's claims, which are
  written by `(actor, exit)`, not by reason. The honest response is to label
  the two evidence qualities (NAMED vs CELL-COINCIDENT, "reason unread") and
  leave reason-relevance to a human reading the records — not to hide the
  coarseness behind a confident verdict.

- **These are weights and directions, not verdicts.** A single `none` refusal
  contributes contradiction *pressure*; the fold reports `n=` counts so the
  weight is visible and never claims a candidate is settled. The data here is
  synthetic, so nothing is contradicted "in general" — only in this set, in
  the cells a candidate claims.

- **`value_locus` is a transcription of §4, and transcriptions are
  contestable.** Each network/mixed label quotes a candidate's own residue or
  the survey (see the comments in `refusal_fold.py`), but it is still a
  *reading*. If someone argued 4.2's transaction audit had standalone value, or
  that 4.1 at literally-zero cost is its own reward, the labels would shift and
  fold [6] would read differently. The honest claim is narrow: under §4 *as
  written*, the only WAIT-claiming candidate is network and the only solo
  thread is aimed at REJECT. The fold makes that structure visible; it does not
  prove the structure is the only defensible one.

- **The §4 candidate set has blind spots, and the fold surfaces them.** Two
  refusal reasons — "governance is unpaid" and the company DEFECT that adopts
  to capture then de-federates — are not really answered by *any* candidate.
  The capture case shows up explicitly as an *unaddressed cell*; the unpaid-
  governance case shows up as cell-coincident pressure on candidates that have
  nothing to say about pay. Both point back at §4, not at the fold: the
  candidate set is incomplete, and the probe makes that visible.

## Files

- [`refusal_fold.py`](refusal_fold.py) — the fold and its report
- [`fixtures.json`](fixtures.json) — synthetic refusal records

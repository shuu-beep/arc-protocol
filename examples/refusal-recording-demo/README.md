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
| which candidate mechanisms are weakened / falsified for the cells they claim | whether the actor would really change behaviour later |
| `mechanism = none` cases (no mechanism would have moved them) | whether adoption will or will not happen |
| where a WAIT depends on a still-missing side (mutual-WAIT deadlock) | whether a mechanism is valid *in general* |
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

## How a candidate gets weakened or falsified

Each §4 candidate mechanism claims to address certain `(actor, exit)` cells.
A `mechanism = none` refusal *inside a cell a candidate claims* is direct
evidence against that candidate: ARC offered to move exactly this kind of
party, and the party says nothing — including that candidate — would have.

```txt
none-in-claimed  &  not named   ->  FALSIFIED        (for its claimed cells, in this set)
none-in-claimed  &  named       ->  WEAKENED
named            &  no none      ->  NAMED-RELEVANT  (unvalidated; the party still declined)
neither                          ->  UNTESTED
```

A candidate that claims broadly (e.g. "any actor × REJECT") is, correctly,
the most exposed: a broad promise is the easiest to falsify.

## What the run shows (synthetic set)

- Every candidate lands at WEAKENED or FALSIFIED — **none reaches validated.**
- The **company / DEFECT** record — the "embrace the open spec, then withdraw
  federation once the users are ours" case — falls in a cell **no candidate
  mechanism even claims to address.** ARC's §4 set is silent on it.
- A **mutual-WAIT deadlock `{merchant, user}`** is detected: each waits on the
  other, and each is individually rational to wait.

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

## Files

- [`refusal_fold.py`](refusal_fold.py) — the fold and its report
- [`fixtures.json`](fixtures.json) — synthetic refusal records

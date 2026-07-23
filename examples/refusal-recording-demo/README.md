# Refusal-Recording Demo

> This probe records and groups refusal records; it does not model or validate adoption.

A small runnable fixture that groups synthetic *refusal records* using the
categories in the [adoption research](../../docs/adoption-and-defection.md). It
reports record counts and category matches without inferring motives or adoption.

```
python3 refusal_fold.py
```

Stdlib only. No network, no services, no real participant data.

## The boundary this probe exists to show

ARC records do not establish why a party will honor, join, or adopt a protocol
([threat-model.md §18.1](../../docs/threat-model.md)). This fixture treats a
refusal only as a record of what an actor said and groups its declared fields.

| This fixture **computes** from refusal records | This fixture **does not compute** |
| --- | --- |
| counts by actor, exit, named mechanism | whether a stated reason is *true* |
| per candidate, evidence *named* by the refuser vs *cell-coincident* (reason unread) | whether the actor would really change behaviour later |
| records labeled `mechanism = none` | whether adoption will or will not happen |
| where a WAIT depends on a still-missing side (mutual-WAIT deadlock) | whether a mechanism is valid *in general* |
| whether any §4 candidate is labeled counterparty-independent and mapped to a mutual-WAIT cell | whether such a candidate would change adoption behavior |
| which exits no candidate mechanism even claims to address | whether the stated reason matches private motivation |

A candidate mechanism is **never validated** here. The strongest a refusal
can say *for* a mechanism is "named as decisive" — and that party still
declined, so the lead is unproven. The fold can only weaken, never confirm.

## What it is not

- **Not an adoption simulator.** It runs no agents and models no market.
- **It does not predict adoption.** No output is a forecast.
- **It does not prove a refusal reason is true.** Every reason is treated as
  testimony, never as established fact.
- It reports a grouped summary over the supplied refusal records and candidate labels.

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

## Real records

Real refusals of ARC — collected under the
[first-refusal protocol](../../docs/first-refusal-protocol.md) — live in the
sibling [`fixtures_real.json`](fixtures_real.json), which is currently empty.
The same fold consumes both files; real records are marked `*`
throughout the report and carry a provenance envelope
(`source`, `date`, `visibility`, `stimulus` — protocol §5).

Two kinds of misfit in a real record mean opposite things, and the fold's
section `[0]` keeps them apart:

- **schema-break** — a value outside the schema's vocabulary (a fifth exit, a
  dual actor, an unlisted mechanism). Excluded from the folds, because its
  cells are undefined, but the mismatch is reported separately rather than discarded.
- **recording gap** — a missing reason or provenance field. An interviewer
  error to repair, not a finding; the record still folds.

`visibility = private` records trigger a consent-gate warning: this file is a
public artifact, so a private verbatim reason must be de-identified or
consented *before* it is committed — a render-time redaction cannot
un-publish the repository.

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

The fold detects reciprocal `WAIT` labels and asks whether any authored
candidate marked as counterparty-independent reaches either labeled cell. The
result depends on the candidate coverage and `value_locus` labels supplied here
([survey §57](../../docs/coordination-economics-survey.md)).

So each candidate carries a `value_locus`, transcribed (not invented) from its
own §4 residue or the survey:

- **network** — labeled as requiring a counterparty (4.1, 4.3, 4.4, 4.5, 4.6).
- **mixed** — a candidate labeled here as having both single-party and network value.
  In this fixture, the audit log's *self-delegation audit* records and recomputes one party's
  agent's approvals with no one else participating
  ([survey §109](../../docs/coordination-economics-survey.md), [adoption §4.2](../../docs/adoption-and-defection.md)).

The fold then checks, per deadlock, which candidates even *reach* it (claim a
WAIT cell of a deadlocked actor) and whether any reaching candidate is solo.
This is a structural check over the authored labels, not evidence that the
candidate would change adoption behavior.

**The finding is a property of the candidates and `value_locus` labels encoded
here.** In that authored set, exactly one candidate claims any WAIT cell — 4.1 (lower
integration cost), which is labeled **network**-value. The only solo-thread
candidate in this encoding, 4.2,
claims `REJECT` cells, **no WAIT cell**. So:

In the authored candidate set, no counterparty-independent candidate is labeled
as addressing `WAIT`; the only candidate that reaches it is labeled `network`.

This neither indicts nor predicts: it does not say adoption fails, only that
the candidate set as written contains no counterparty-independent lever
pointed at the standoff the WAIT records turn on. Whether the 4.2 solo thread
could ever be *enlarged* to reach a WAIT is an open §4 question, not something
the fold can settle — and its size is unmeasured ([survey §114](../../docs/coordination-economics-survey.md)).

## What the run shows (synthetic set)

- Every candidate lands at MIXED or CELL-CONTRADICTED — **none reaches
  validated.** The strongest reading for any candidate is "named, still declined".
- The **company / DEFECT** record — the "embrace the open spec, then withdraw
  federation once the users are ours" case — falls in a cell **no candidate in
  the supplied map claims to address.**
- A **mutual-WAIT pair `{merchant, user}`** is detected under the fixtures' stated
  dependencies; the fold does not establish either actor's rationality.
- Under the candidates and `value_locus` labels coded here, no solo-classified
  candidate reaches that pair. Only 4.1 (network) reaches it; 4.2 claims REJECT,
  not WAIT.

## A note on the exit vocabulary

Building this probe required a classification check: does the
embrace-and-defederate pattern from
[coordination-economics-survey.md §5](../../docs/coordination-economics-survey.md)
(XMPP, RSS) need a fifth exit, e.g. `CAPTURE`?

This fixture keeps the four existing exit labels. A separate `CAPTURE` label
would encode an inferred strategic motive that these records do not establish;
the authored examples are therefore mapped as follows:

- genuinely adopt, then withdraw interoperation to retain the captured base →
  **DEFECT** (stop honouring once it pays; the "pay" is the retained base);
- adopt the forms but never the substance (a compliance veneer) → **FORK**
  (a captured variant; already [adoption-and-defection §3.2](../../docs/adoption-and-defection.md)).

The company `DEFECT` example appears as an unaddressed cell under the supplied
candidate map. The fixture does not infer the actor's motive or introduce a new exit.

## Red-team notes (known limitations)

Known limits of the authored categories and fold are listed below.

- **The fold matches by cell, but relevance lives in the reason.** A candidate
  is tied to a refusal by its `(actor, exit)` cell, so a `mechanism = none`
  refusal contradicts *every* candidate that claims its cell — even one whose
  subject its reason has nothing to do with (a "governance is unpaid" REJECT
  contributes cell-coincident pressure to "lower integration cost"). This is
  not fixable by making the fold read the reason: parsing the reason to decide
  relevance is exactly the inference [§6](../../docs/adoption-and-defection.md)
  forbids ("a reason paraphrased into our own category is a claim in
  disguise"). The fold is therefore only as precise as §4's claims, which are
  written by `(actor, exit)`, not by reason. The report therefore labels
  the two evidence qualities (NAMED vs CELL-COINCIDENT, "reason unread") and
  leaves reason-relevance to a human reading the records — not to hide the
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
  fold [6] would read differently. The result is limited to §4 *as
  written*, the only WAIT-claiming candidate is network and the only solo
  thread is aimed at REJECT. The fold makes that structure visible; it does not
  establish that this is the only possible classification.

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
- [`fixtures_real.json`](fixtures_real.json) — real refusals of ARC (empty
  until the first real record lands; see the first-refusal protocol §7)

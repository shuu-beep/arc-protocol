# First-Refusal Study Procedure

> **Status:** Exploratory experiment-design note
>
> **Purpose:** Define a procedure for recording initial refusals before a pilot. This
> note comes before [pilot-design.md](pilot-design.md): a pilot presumes
> someone has begun to use ARC; this presumes no one has.

---

## 1. What This Experiment Is For

The inverse question in [adoption-and-defection.md](adoption-and-defection.md)
is why each actor may decline. The [refusal-recording probe](../examples/refusal-recording-demo/)
processes *synthetic* refusals through that model. Neither document contains participant data.

This note specifies first-contact and recording procedure. It seeks refusal reasons, not adoption validation:

```txt
Not:  recruit an adopter
But:  record a refusal as participant-reported research data
```

The procedure tests whether a refusal can be retained in a structured record without changing the participant's words. A refusal record is research data, not ARC protocol evidence or proof about adoption.

## 2. What Is Being Tested

The primary subject is **the instrument, not ARC.** The question is:

> Does the [§6 refusal schema](adoption-and-defection.md) survive contact with
> a real refusal?

A refusal that **does not fit the schema** is a schema-mismatch result to retain, including:

- an `exit` that is none of WAIT / DEFECT / FORK / REJECT;
- a refusal that, read closely, is not a refusal of ARC at all but of the
  explanation it was given (see §5);
- a refuser who is two actors at once (a maintainer who is also a company),
  so the `actor` field forces a false choice.

Each tests the scope and limits of the instrument ([pilot-design §2](pilot-design.md)).

## 3. Study Procedure

### 3.1 One actor at a time

Mixing actors can blur analysis, because the same words may mean different
things from a developer and a merchant. Each round of contact targets a single
[§3 actor](adoption-and-defection.md):

| First-contact target | actor |
| --- | --- |
| AI-agent framework developer (CrewAI, OpenHands, LangGraph, AutoGen, OpenManus, …) | `developer` |
| Open-source maintainer | `community` |
| AI startup | `company` |
| Local-commerce operator | `merchant` |

The `user` actor is deferred because an end user has no application network to try. Its absence from early rounds is recorded as a limitation.

### 3.2 Neutral first-contact prompt

This is not a request to use ARC. The prompt asks why the participant would not use it:

> I've been building ARC Protocol. I'm **not** asking whether you'd adopt it.
> I'm interested in one thing only: if you wouldn't adopt it today, why?

The framing is intended to reduce encouragement bias. The answer to "why not" is recorded as the `reason`.

### 3.3 Question order

`mechanism = none` is an informative answer: the participant identified no
§4 candidate that would have changed the decision. A question that asks "what one
thing would change your mind?" *up front* pressures the person to invent a
mechanism, which biases the data against `none`. So the order is fixed:

```txt
1.  "Why would you not use it?"        -> record the reason, verbatim. Stop.
2.  (only then, optional)
    "Would anything change that answer?" -> offered with "nothing would" as an
                                            equally weighted, expected answer
3.  "No, nothing would."               -> mechanism = none   (a result, not a gap
                                            in the interview)
```

The mechanism question is asked *after* the reason is captured and is phrased so declining to name a mechanism is a complete answer.

### 3.4 Record verbatim; classify paraphrases separately

The `reason` field stores the participant's own words. If they say
*"Too much governance overhead,"* that string is what is stored. Rewriting it
to `"governance cost"` would be an analytical paraphrase, not a source quote. The recorder preserves the original wording and classifies it separately.

### 3.5 Classification is a separate, later, human step

Only after the reason is recorded does a human attach `actor` and `exit`. The
`mechanism` field is filled **only if the participant volunteered one** in
step 3.3; it is never inferred from the reason text. Reading the reason to
decide which §4 candidate it implicates is an analytical inference that the
[probe's red-team note](../examples/refusal-recording-demo/) already draws —
that work belongs to a human reading the record, never to the schema.

### 3.6 Do not rebut during capture

If the participant says *"This will never work,"* the response is to record it
and thank them. The capture procedure excludes correction, explanation, or persuasion because those interventions would change the recorded response.

## 4. What Is and Is Not Measured

Measured: `actor`, `exit`, `reason`, `mechanism`, and the provenance envelope
in §5. Nothing else.

**Not** measured, deliberately:

- GitHub stars, likes, follows
- email reply rate, conversion rate
- any adoption or interest metric

Adoption-rate metrics are excluded to keep this instrument focused on the content and provenance of refusals rather than response or conversion rates.

## 5. Provenance and Stimulus

Each real record carries a provenance envelope. This is **metadata about where
the record came from**, not an interpretation of the reason, so it does not
conflict with the §6 verbatim discipline:

```txt
source      github_issue | github_discussion | email | x_reply |
            reddit | conference | interview | …
date        when the refusal was recorded
visibility  public | private
stimulus    what the refuser actually saw before refusing:
            README | README-summary | 10-min-talk | email-pitch |
            GitHub-issue-thread | X-thread | …
```

`stimulus` provides context. A refusal is a refusal *of something*, and
the something may not be ARC — it may be a too-long README or an unclear
two-line summary. Recording the stimulus helps a later reader distinguish **a refusal
of ARC** from **a refusal of the explanation it was given**. The record captures what material the participant saw; this reduces ambiguity but does not eliminate it (§6).

## 6. What This Experiment Cannot Capture

The study has these limitations:

- **Nonresponse.** This procedure records only responses from people willing to engage. It cannot infer reasons or prevalence from people who do not respond.
- **Refusal of ARC vs refusal of its explanation.** `stimulus` (§5) makes the
  distinction inspectable but cannot fully resolve it; a refusal recorded
  against a poor stimulus is weaker evidence about ARC than one recorded
  against a faithful one.
- **No distribution.** With a handful of real records, nothing about frequency, representativeness, or trend can be claimed. The records demonstrate pipeline execution, not population inference.
- **Consent governs publication.** A `visibility = private` refusal recorded
  verbatim cannot enter a public artifact without consent or de-identification;
  a named person's words are theirs. Verbatim capture is the recording
  discipline; publishing it is a separate gate, drawn from the same caution as
  [liability-boundaries.md](liability-boundaries.md).

## 7. The Output

The existing fold already consumes records of this shape — both the synthetic
[`fixtures.json`](../examples/refusal-recording-demo/) and the sibling
`fixtures_real.json`, which exists and is empty. The first real refusals
populate it, and the same fold runs over both:

```txt
synthetic  12        synthetic  12
real        0   ->   real        3
```

The first real fold tests the pipeline end-to-end on **one real datum** — real refusal → §6 record →
provenance envelope → fold → comparison surface — and surfaces any reason
that does not fit the schema (§2). Three records that fold cleanly indicate schema compatibility; they do not validate the instrument. The fold
handles the cases separately: a real record whose vocabulary does not
fit is reported as a **schema-break** — excluded from the folds (its cells are
undefined) but retained in the report — while a missing
provenance field is flagged as a recording *gap*, an interviewer error rather
than a finding. The two kinds of misfit mean opposite things, and the report
keeps them apart.

## 8. Why Record Refusals First

Starting with refusals reduces selection toward positive examples. It does not make refusals representative. This procedure records early objections before pilot recruitment.

## 9. Current Position

No refusal has been collected. The recording pipeline, however, is no longer
design only: `fixtures_real.json` exists (empty), the fold consumes it
alongside the synthetic set, and the operational materials for the first
round are prepared (Appendix B). Everything before the send exists; the send
does not.

The next data point is one real refusal, recorded under
this procedure and folded against the synthetic set. That would address the request in
[adoption-and-defection §7](adoption-and-defection.md) for
"refusals recorded in the §6 schema from real merchants, users, or
communities" — using an operating procedure.

---

## Appendix A — Phase 0 (optional calibration, not an ARC-specific refusal)

> **This appendix is a preparation aid, not an ARC-specific refusal record.**

Before soliciting an ARC-specific refusal, one *may* calibrate the recording
layer on **existing public refusals of adjacent protocols** — ActivityPub,
Solid, ERC-8004, decentralized-identity and web-of-trust efforts — read from
their real public GitHub issues, mailing lists, and HN threads. These are already-public examples, but any reuse still follows applicable quotation and privacy constraints.

Its purpose is to stress-test the **recording layer**
(`actor`, `exit`, `reason`, `stimulus`, provenance) on real language before
ARC-specific outreach. Its scope
is strictly limited:

- Phase 0 exercises `actor` / `exit` / `reason` / provenance only. It
  **cannot** exercise the `mechanism` column — the §4 candidates are
  ARC-specific, and a refusal of ActivityPub is not a refusal of ARC.
- Phase 0 produces **no** record in `fixtures_real.json`. Those are reserved
  for real refusals *of ARC*.
- Phase 0 should be time-boxed so archive review does not indefinitely defer ARC-specific outreach. It may be skipped.

---

## Appendix B — Field Kit (operational materials for round 1)

> This appendix operationalizes
> §3 for the first round of contact, so that when the message goes out,
> nothing about the recording discipline is improvised. Round 1 targets the
> `developer` actor (§3.1, first row).

### B.1 Stimulus discipline

Whatever the person actually sees **is** the `stimulus` value — it is chosen
deliberately and recorded exactly (§5). For round 1 the stimulus is the
message in B.2 plus the linked README. Because the two cannot be separated
from the outside, the follow-up thanks (B.3) asks one factual question —
"did you get as far as the README, or is this from the message alone?" — and
the answer is recorded as `stimulus: README + email-pitch` or
`stimulus: email-pitch`. A refusal recorded against the two-paragraph pitch
alone is weaker evidence about ARC than one recorded against the README, and
the field keeps that difference visible instead of flattening it.

### B.2 The approach message (send-ready draft)

Subject: **one question about ARC**

> I've been building ARC Protocol — an implementation-neutral authority
> protocol for human-to-agent and agent-to-agent delegation, approval,
> revocation, adjudication, and audit of disclosed signed evidence. Repo:
> <https://github.com/shuu-beep/arc-protocol>.
>
> I'm not asking you to adopt it, try it, or star it. I'm collecting the
> opposite signal: **if you wouldn't use this today, why not?**
>
> Any reason is a complete answer — "too speculative," "wrong layer," "no
> network," "this will never work." I record refusals verbatim as data, and
> I won't argue with yours.
>
> One logistics question: may I record your answer verbatim, and may it
> appear in the public repo — attributed or de-identified, your choice?

What the draft deliberately does **not** contain: any request to try ARC,
any adoption metric, or the mechanism question (B.3).

### B.3 Question order under asynchrony

§3.3's order survives an async channel only if the mechanism question is
**absent from the first message**. Both questions in one email would pressure
the reply toward a manufactured mechanism and bias the data against
`mechanism = none`. So the first message
asks *why not* and nothing else. Only after the reason has arrived and been
recorded verbatim does the optional follow-up go out:

> Thank you — recorded verbatim, as promised. One optional follow-up, and
> "nothing would" is an expected, complete answer: would anything change
> that answer? (Also: did you get as far as the README, or is this from my
> message alone? Recording what you actually saw is part of the method.)

If the participant never replies to the follow-up, `mechanism` is left
unasked — never inferred from the reason (§3.5).

### B.4 Recording sheet

Filled top-to-bottom; the classification block is a separate, later, human
step (§3.5). The completed record enters
[`fixtures_real.json`](../examples/refusal-recording-demo/fixtures_real.json)
and the fold consumes it on the next run.

```txt
-- capture (at contact time, verbatim) ------------------------
reason        "..."              (their words, unedited)
mechanism     4.x | none | (not asked / not volunteered)
source        github_issue | email | x_reply | interview | ...
date          YYYY-MM-DD
visibility    public | private   (their explicit consent)
stimulus      what they actually saw (B.1)

-- classification (later, by a human) -------------------------
actor         developer | company | merchant | user | community
exit          WAIT | DEFECT | FORK | REJECT
waits_on / waits_on_actor        (WAIT only)
schema-break? anything that does not fit -> retain the raw record (§2)
```

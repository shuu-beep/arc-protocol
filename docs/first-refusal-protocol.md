# ARC Protocol: The First Refusal Protocol

> **Status:** Exploratory experiment-design note
>
> **Purpose:** Define how ARC makes first contact with reality — not by
> seeking a first adopter, but by collecting a first *refusal* as data. This
> note comes before [pilot-design.md](pilot-design.md): a pilot presumes
> someone has begun to use ARC; this presumes no one has.

---

## 1. What This Experiment Is For

The honest question in [adoption-and-defection.md](adoption-and-defection.md)
is not why ARC will be adopted but why each actor can rationally decline. That
document argues the inverse; the [refusal-recording probe](../examples/refusal-recording-demo/)
folds *synthetic* refusals through it. Neither has yet touched a real person.

This note designs that first touch. Its goal is deliberately inverted from how
projects usually seek validation:

```txt
Not:  prove that ARC is adopted        (collect a first success)
But:  prove that ARC can record a       (collect a first failure)
      refusal as data
```

The thing being demonstrated is not that someone said yes. It is that when
someone says **no**, ARC's machinery turns that no into structured, foldable
evidence instead of losing it. A protocol that can only learn from the
adoption it imagines learns nothing; this experiment is how it learns from a
refusal it did not.

## 2. What Is Actually Being Validated

The primary subject of this experiment is **the instrument, not ARC.** The
falsifiable hypothesis is:

> Does the [§6 refusal schema](adoption-and-defection.md) survive contact with
> a real refusal?

This reframing is the whole point. It means the most valuable outcome is a
real refusal that **does not fit the schema** — exactly as a `mechanism = none`
refusal falsifies a §4 candidate, a refusal that cannot be classified
falsifies the schema:

- an `exit` that is none of WAIT / DEFECT / FORK / REJECT;
- a refusal that, read closely, is not a refusal of ARC at all but of the
  explanation it was given (see §5);
- a refuser who is two actors at once (a maintainer who is also a company),
  so the `actor` field forces a false choice.

Each of these is a result, not a failure of the experiment. An instrument that
can only confirm is a demonstration, not a measurement
([pilot-design §2](pilot-design.md)). The first real refusal that breaks the
schema teaches more than ten that fit it.

## 3. The Protocol

### 3.1 One actor at a time

Mixing actors degrades refusal quality, because the same words mean different
things from a developer and a merchant. Each round of contact targets a single
[§3 actor](adoption-and-defection.md):

| First-contact target | actor |
| --- | --- |
| AI-agent framework developer (CrewAI, OpenHands, LangGraph, AutoGen, OpenManus, …) | `developer` |
| Open-source maintainer | `community` |
| AI startup | `company` |
| Local-commerce operator | `merchant` |

The `user` actor is the hardest to reach before a network exists (an end user
has nothing to try), and is honestly deferred — its absence from early rounds
is itself a recorded fact, not an oversight.

### 3.2 The approach is not a request

The single most important rule. This is **not** "please use ARC." The question
is "why would you *not*." A faithful approach reads roughly:

> I've been building ARC Protocol. I'm **not** asking whether you'd adopt it.
> I'm interested in one thing only: if you wouldn't adopt it today, why?

The frame removes the social pressure to be encouraging, which is the pressure
that manufactures false yeses. It maps directly onto the schema: the answer to
"why not" *is* the `reason`.

### 3.3 Question order protects the most valuable cell

`mechanism = none` is the most informative answer the schema can record — a
refusal that no §4 candidate would have moved. A question that asks "what one
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

The mechanism question is asked *after* the reason is already captured, and is
phrased so that declining to name a mechanism is a complete, respectable
answer — never a prompt the person feels obliged to fill.

### 3.4 Record verbatim — paraphrase is already inference

The `reason` field stores the participant's own words. If they say
*"Too much governance overhead,"* that string is what is stored. Rewriting it
to `"governance cost"` is not tidying — it is a claim in disguise, the same
inference [§6](adoption-and-defection.md) forbids. The recorder's job is
faithful capture, not categorization.

### 3.5 Classification is a separate, later, human step

Only after the reason is recorded does a human attach `actor` and `exit`. The
`mechanism` field is filled **only if the participant volunteered one** in
step 3.3; it is never inferred from the reason text. Reading the reason to
decide which §4 candidate it "really" implicates is the forbidden inference the
[probe's red-team note](../examples/refusal-recording-demo/) already draws —
that work belongs to a human reading the record, never to the schema.

### 3.6 Never rebut — this is measurement, not an interview

If the participant says *"This will never work,"* the response is to record it
and thank them. Correcting, explaining, or persuading is prohibited. An
interviewer who argues a participant out of their reason has corrupted the
record, not improved it. The instrument measures the refusal; it does not
contest it.

## 4. What Is and Is Not Measured

Measured: `actor`, `exit`, `reason`, `mechanism`, and the provenance envelope
in §5. Nothing else.

**Not** measured, deliberately:

- GitHub stars, likes, follows
- email reply rate, conversion rate
- any adoption or interest metric

Adoption-rate metrics would quietly turn a refusal experiment back into a
popularity contest, reintroducing exactly the "looks like it works" pressure
the design exists to remove. A high reply rate is not a result; a single
well-recorded refusal is.

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

`stimulus` does real epistemic work. A refusal is a refusal *of something*, and
the something may not be ARC — it may be a too-long README or a garbled
two-line pitch. Recording the stimulus lets a later reader separate **a refusal
of ARC** from **a refusal of the explanation it was given**. It is the
view-fidelity wall applied to first contact: the record captures what the
person understood ARC to be, not ARC itself, and `stimulus` is how that gap
stays visible. It mitigates the confusion; it does not eliminate it (§6).

## 6. What This Experiment Cannot Capture

Stated as standing boundaries, in the same spirit as ARC's off-ledger wall
([threat-model §18.1](threat-model.md)):

- **The silent refusal.** The most common refusal is *read, then close the
  tab* — no words at all. This protocol measures only **spoken refusals**, from
  people willing to engage. The modal refusal is structurally invisible to it,
  and no count of recorded refusals can speak for the silent majority. This is
  the inverse of survivorship bias and must be declared, not hidden.
- **Refusal of ARC vs refusal of its explanation.** `stimulus` (§5) makes the
  distinction inspectable but cannot fully resolve it; a refusal recorded
  against a poor stimulus is weaker evidence about ARC than one recorded
  against a faithful one.
- **No distribution.** With a handful of real records, nothing about
  frequency, representativeness, or trend can be claimed. The first records
  prove a *pipeline*, not a *population*.
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

The first real fold's job is not to measure anything. It is to prove the
pipeline end-to-end on **one real datum** — real refusal → §6 record →
provenance envelope → fold → falsification surface — and to surface any reason
that breaks the schema (§2). Three real refusals that fold cleanly prove the
instrument holds; one that does not fold is the more valuable result. The fold
already anticipates that asymmetry: a real record whose vocabulary does not
fit is reported as a **schema-break** — excluded from the folds (its cells are
undefined) but reported as the headline, never discarded — while a missing
provenance field is flagged as a recording *gap*, an interviewer error rather
than a finding. The two kinds of misfit mean opposite things, and the report
keeps them apart.

## 8. Why Refusal Studies

Most projects collect **case studies** — the successes, the logos, the "how X
adopted us." This protocol has ARC collect **refusal studies** first, and that
inversion is not a pose: it is the only form of first contact consistent with a
document whose thesis is that the honest question is why each actor declines.

A protocol learns from a real refusal what it can never learn from an imagined
adoption. Gathering the refusals first — before any pilot, before any success
story — is how ARC keeps its adoption theory inverted all the way down to its
first contact with a real person.

## 9. Current Position

No refusal has been collected. The recording pipeline, however, is no longer
design only: `fixtures_real.json` exists (empty), the fold consumes it
alongside the synthetic set, and the operational materials for the first
round are prepared (Appendix B). Everything before the send exists; the send
does not.

The next artifact is not a document but an event: one real refusal, recorded in
this protocol, folded against the synthetic set. That is the first contact
[adoption-and-defection §7](adoption-and-defection.md) asks for —
"refusals recorded in the §6 schema from real merchants, users, or
communities" — given an operating procedure. Until it happens, ARC's contact
with reality is still zero.

---

## Appendix A — Phase 0 (optional calibration, *not* outside contact)

> **This appendix is a preparation aid, not a stage of the protocol. Phase 0
> does NOT count as ARC's first contact with reality. If Phase 0 ever becomes
> the destination, it has failed.**

Before soliciting an ARC-specific refusal, one *may* calibrate the recording
layer on **existing public refusals of adjacent protocols** — ActivityPub,
Solid, ERC-8004, decentralized-identity and web-of-trust efforts — read from
their real public GitHub issues, mailing lists, and HN threads. This is the
[coordination-economics graveyard](coordination-economics-survey.md) made
personal: real, messy, already-public refusal text, with no outreach and no
consent problem.

Its only legitimate purpose is to stress-test the **recording layer**
(`actor`, `exit`, `reason`, `stimulus`, provenance) on real language before
betting a scarce, one-shot ARC outreach on a schema that might break. Its scope
is strictly limited:

- Phase 0 exercises `actor` / `exit` / `reason` / provenance only. It
  **cannot** exercise the `mechanism` column — the §4 candidates are
  ARC-specific, and a refusal of ActivityPub is not a refusal of ARC.
- Phase 0 produces **no** record in `fixtures_real.json`. Those are reserved
  for real refusals *of ARC*.
- The danger Phase 0 carries is that searching public archives is endlessly
  absorbing and feels like progress while the real, uncomfortable step — showing
  ARC to a stranger and asking why they would refuse it — is deferred
  indefinitely. The whole experiment exists to *make first contact*, and Phase 0
  is the most plausible way to never make it. Treat it as a dress rehearsal with
  a hard stop, or skip it.

---

## Appendix B — Field Kit (operational materials for round 1)

> Everything above is design; this appendix is the send. It operationalizes
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

Subject: **one question about why you wouldn't use this**

> I've been building ARC Protocol — an open protocol for delegated agent
> authority: human-approved delegation, portable authority records, and
> recomputable audit logs. Repo: <https://github.com/shuu-beep/arc-protocol>.
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
any adoption metric, and — most importantly — the mechanism question (B.3).

### B.3 Question order under asynchrony

§3.3's order survives an async channel only if the mechanism question is
**absent from the first message**. Both questions in one email would pressure
the reply toward a manufactured mechanism and bias the data against
`mechanism = none` — the single most informative cell. So the first message
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
schema-break? anything that does not fit -> record it raw (§2);
              a misfit falsifies the schema, not the refusal
```

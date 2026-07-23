# ARC Protocol: Adoption and Defection

> **Status:** Exploratory incentive note
>
> **Purpose:** Map why each participant may decline ARC, then separate candidate coordination mechanisms from any claim that they will work.
>
> **Scope:** The company, merchant, user, and community roles below are Commerce flagship-application examples. This is adoption research, not protocol or adoption evidence.

---

## 1. Why This Document Exists

ARC's executable probes do not establish why a counterparty would honor a community's authority rather than ignore, fork, or defect ([threat-model §18.1](threat-model.md)). The Canon can represent sanction and incentive claims; an observer or profile policy determines which authority it honors. Event records do not establish the incentive to honor.

[`bootstrap-and-incentives.md`](bootstrap-and-incentives.md) records this as a set of network-role gaps — what each role still lacks. This document uses an inverse analysis: not "why will ARC be adopted," but **"why might each actor decline."**

```txt
Inverse framing  — why each actor may wait, defect, fork, or reject.
Mechanism second — which coordination mechanisms could move that calculus.
No adoption claims — mechanisms are hypotheses and known-unknowns, not conclusions.
```

This order keeps each proposed mechanism tied to the adoption response it is intended to address.

## 2. Four Analytic Response Categories

This note groups non-adoption responses into four categories. The categories are not exhaustive, and a mechanism that addresses one may leave the others open.

```txt
WAIT    — defer adoption until other participant groups move.
DEFECT  — adopt, then stop honoring the selected authority or policy.
FORK    — use the open specification under a different implementation or policy.
REJECT  — decline adoption in favor of the existing arrangement.
```

These are analytic categories, not established motives or protocol states. Openness can lower fork cost while also enabling alternative governance; the adoption effect is unmeasured.

## 3. The Inverse: Why Each Actor Can Decline

### 3.1 The agent developer

- **WAIT.** A developer may defer integration until a relevant network exists.
- **REJECT.** A developer may prefer an SDK that already provides application demand rather than bear an unmeasured integration cost.
- **FORK.** A developer may reuse selected parts of the open specification without adopting an entire application profile.

### 3.2 The company or platform operator

- **REJECT.** Some platforms derive value from ranking control, demand aggregation, or switching costs. A named Commerce profile's disclosure or portability requirements may conflict with those incentives.
- **FORK.** An operator could adopt ARC vocabulary while omitting requirements of a named profile or conformance claim.
- **WAIT.** Integration costs and ecosystem benefits may fall on different actors, so an operator may defer adoption.

### 3.3 The merchant

- **WAIT.** A merchant may want consumer demand before exposing structured offers, while consumers may wait for useful merchants ([bootstrap §2](bootstrap-and-incentives.md)).
- **REJECT.** Structured offers, an agent to maintain, and an unfamiliar dispute path are real costs against an unproven channel that provides no demand, marketing, or support of its own ([roadmap §Stage 5](roadmap.md)).
- **DEFECT.** A merchant with an established application reputation may later misrepresent offers or use undisclosed influence. Harm may fall first on counterparties; actual cost depends on enforcement and exit options.

### 3.4 The user

- **REJECT.** A centralized app may already provide refunds, chargebacks, support, and a familiar interface. The user would need to evaluate whether an approval-and-audit overlay adds value.
- **WAIT.** With no participating merchants, a user may wait for the application network to develop.

### 3.5 The community or governance body

- **REJECT.** Governance can be unpaid or adversarial work — fraud reports, appeals, and conflict-of-interest checks — that does not disappear because a system is open ([bootstrap §6](bootstrap-and-incentives.md)).
- **DEFECT.** A governance body may drift from its declared policy while continuing to emit validly formed records.
- **FORK.** A community can withdraw recognition and run its own policy or implementation. Withdrawal does not alter prior Events; a named Projection and policy determine their later treatment ([threat-model §13](threat-model.md)).

## 4. Candidate Coordination Mechanisms

Each item below is a coordination mechanism that *could* change one of the calculations in §3. None is asserted to work. Each is paired with what remains unproven. Preliminary external comparisons appear in [coordination-economics-survey.md](coordination-economics-survey.md).

### 4.1 Lower integration cost → addresses WAIT, REJECT

- **Hypothesis:** if structured offers and the approval seam are cheap enough to add to an existing system, the first-mover cost that justifies WAIT shrinks.
- **Unproven:** "cheap enough" is undefined. ARC has no measured integration cost against any real merchant stack, and a low cost still buys nothing without demand on the other side.

### 4.2 Approval and audit overlay → addresses REJECT (user, company)

- **Hypothesis:** a portable record of who approved what could have value when its disclosed records pass External Record Verification and its result is independently recomputable from an identified evidence set and named Projection/profile.
- **Unproven:** the value is felt mainly *after* a failure, so it is hard to price in advance. The overlay also relocates trust onto whoever renders the approval to the human (the view-fidelity residue), which it does not eliminate.

### 4.3 Reputation portability → addresses REJECT, DEFECT (merchant)

- **Hypothesis:** if a merchant can carry earned reputation across communities, the lock-in that makes a platform's enclosure valuable weakens, raising the cost of staying enclosed.
- **Unproven:** portable reputation is only as meaningful as it is Sybil-resistant, and Sybil resistance lives in the fold, not the protocol. Portability also makes manufactured histories portable.

### 4.4 Replaceable / forkable discovery → addresses FORK, REJECT

- **Hypothesis:** if discovery is a swappable, disclosed component rather than a captured ranking, FORK loses its appeal — a participant unhappy with one backend replaces it instead of exiting the protocol.
- **Unproven:** replaceability does not create the alternative backend; someone must fund and operate one ([bootstrap §7](bootstrap-and-incentives.md)). An ecosystem with one discovery backend is captured regardless of whether the spec permits more.

### 4.5 Governance transparency → addresses DEFECT (governance), REJECT (user)

- **Hypothesis:** if rulings are recorded and recomputable by observers who have the declared evidence set, Projection/profile, ordering inputs, and policy parameters, drift toward gatekeeping may become visible on that observer surface, which could raise the cost of defecting from neutrality.
- **Unproven:** visibility is not enforcement. A recorded ruling remains a record; policy changes may become visible only to observers with the required evidence and recomputation inputs, and visibility does not reverse the ruling.

### 4.6 Open spec as latent counter-pressure → reframes FORK

- **Hypothesis:** the possibility of an alternative implementation may create counter-pressure on an operator whose deployment diverges from a community's preferences.
- **Unproven:** counter-pressure depends on whether an alternative implementation is viable. The current research does not establish that viability or the effect of forkability on operator behavior.

## 5. What Stays Off-Ledger

The mechanisms in §4 share a boundary. A private or centralized deployment can preserve internal ARC semantics, but disclosed evidence supports only the observer claims it actually exposes: External Record Verification, an Independently Recomputable Result, and a Publicly Recomputable Result are distinct. ARC does not establish adoption or non-defection incentives from Event records.

The cold-start fixture ([`examples/reference-client/coldstart_fixture.py`](../examples/reference-client/)) compares three declared strategies — earning edges over time, manufacturing volume with undisclosed agents, and borrowing an established party's weak tie. Under the fixture's event view, those strategies are not distinguishable by motive or real-world quality. The log alone does not resolve cold-start legitimacy.

Empirical evidence would require observed deployments, such as a dispute in which the audit overlay was used or an application reputation record was ported. None of that can be asserted from ARC's current repository state.

## 6. A Refusal-Recording Schema

The §3 categories can also serve as a measurement vocabulary. One low-cost experiment before a network exists is to record refusals in a structured form so a later pilot has comparable observations.

A minimal record per refusal:

```txt
actor      — developer | company | merchant | user | community
exit       — WAIT | DEFECT | FORK | REJECT
reason     — the participant's own words, not a category we assigned
mechanism  — which §4 candidate, if any, the participant says would have
             changed the decision; "none" is a valid and important answer
```

The discipline is in how the fields are filled:

- The schema records what a participant *says*, not what the recorder infers. Analytical paraphrases are stored separately from the source wording.
- `mechanism = none` is one informative cell: it records that the participant did not identify a §4 candidate that would change the decision.
- A `WAIT` is not a soft `REJECT`. It records that the calculus could flip once others move, and names *whose* move it waits on — a different datum than a flat no, and the one the bootstrap chicken-and-egg turns on.
- The instrument must not drift into a persuasion script. Its job is to capture the refusal; interviewer persuasion would change the recorded response.

This gives a concrete shape to what [roadmap §Stage 5](roadmap.md) already asks for ("Record why any merchants, logistics providers, or users declined"). It produces no adoption claim; it provides a structured surface for later comparison.

An executable probe ([`examples/refusal-recording-demo`](../examples/refusal-recording-demo/)) processes synthetic refusal records through this schema. It checks the recording and classification pipeline; it does not validate a participant's reason, establish adoption behavior, or determine future decisions. The probe also compares §4 candidates by where their stated value accrues and identifies that the current candidate set contains no counterparty-independent mechanism aimed at a mutual-`WAIT` case. That is a result of the declared fixture and categories, not empirical adoption evidence.

## 7. Current Position

No pilot or adoption evidence currently supports a trajectory from private deployment to maintainership, source opening, federation, or non-defection.

The current adoption analysis is inverse: it enumerates why each actor may decline (§3), holds countering mechanisms as hypotheses (§4), and records refusals as data (§6) without asserting that the mechanisms will succeed.

The next useful artifacts are not adoption claims but tests of the inverse:

- a measured integration cost against one real merchant stack
- a single community where the audit overlay is exercised against a real dispute
- refusals recorded in the §6 schema from real merchants, users, or communities ([roadmap §Stage 5](roadmap.md)), following the operating procedure in [first-refusal-protocol.md](first-refusal-protocol.md)

These three are the instruments of [pilot-design.md](pilot-design.md), which defines how a limited pilot would test the inverse — learning, not validation.

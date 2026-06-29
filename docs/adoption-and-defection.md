# ARC Protocol: Adoption and Defection

> **Status:** Exploratory incentive note
>
> **Purpose:** Map why each participant can rationally decline ARC, then separate the coordination mechanisms that *could* change that calculus from any claim that they *will*.

---

## 1. Why This Document Exists

ARC's executable-probe methodology bottoms out at one question it cannot fold: why a rational counterparty would honor a community's authority rather than ignore, fork, or defect ([threat-model §18.1](threat-model.md)). The canon can *represent* a sanction and *select* who honors it; it cannot model the *incentive* to honor.

[`bootstrap-and-incentives.md`](bootstrap-and-incentives.md) records this as a set of network-role gaps — what each role still lacks. This document takes the lens the threat model says is the honest one: not "why will ARC be adopted," but **"why might each actor rationally decline."** It works in one direction only:

```txt
Inverse first    — why each actor can rationally wait, defect, fork, or reject.
Mechanism second — which coordination mechanisms could move that calculus.
No adoption claims — mechanisms are hypotheses and known-unknowns, not conclusions.
```

The order matters. A mechanism listed before the defection it answers reads as a pitch. Listed after, it reads as what it is: an untested guess about a real reason to say no.

## 2. The Four Exits

A party that does not adopt ARC is not making one decision. There are four distinct exits, and a mechanism that closes one may leave the others open.

```txt
WAIT    — adoption is rational only once others move; each group waits for the rest.
DEFECT  — adopt, then stop honoring the protocol's authority once defecting pays.
FORK    — take the open spec and run a private or captured variant instead.
REJECT  — never adopt; the existing arrangement is preferred outright.
```

These are not failure states to be argued away. Each is a defensible reading of a real incentive. The point of naming them is that ARC's openness — the property that makes FORK cheap — is the same property it relies on to resist capture. The exits are entangled with the design, not external to it.

## 3. The Inverse: Why Each Actor Can Decline

### 3.1 The agent developer

- **WAIT.** Building against a protocol with no users is speculative work; the rational move is to wait for a network that may never form.
- **REJECT.** A proprietary agent SDK with a captive marketplace offers built-in demand. ARC offers none, and asks for the integration cost anyway.
- **FORK.** The spec is open. A developer can lift the parts that help (the audit log, the approval seam) and drop the parts that constrain (community governance, portable reputation) without honoring the whole.

### 3.2 The company or platform operator

- **REJECT.** A platform's value is partly its enclosure: opaque ranking, demand aggregation, switching costs that retain merchants. ARC asks an operator to make legible exactly what it currently profits from keeping illegible.
- **FORK.** An operator can adopt ARC's vocabulary as a compliance veneer — run the event types, skip the human-approval and disclosure discipline — and capture the surface while defeating the intent.
- **WAIT.** Even a sympathetic operator has no first-mover reason: the audit and portability benefits accrue to the ecosystem, the integration cost lands on whoever moves first.

### 3.3 The merchant

- **WAIT.** A merchant wants consumer demand before exposing structured offers; consumers want useful merchants first. The chicken-and-egg is structural ([bootstrap §2](bootstrap-and-incentives.md)), and waiting is the individually correct move.
- **REJECT.** Structured offers, an agent to maintain, and an unfamiliar dispute path are real costs against an unproven channel that provides no demand, marketing, or support of its own ([roadmap §Stage 5](roadmap.md)).
- **DEFECT.** A merchant who has earned reputation can later misrepresent offers or lean on undisclosed influence, and the cost of that defection is borne by counterparties, not the merchant.

### 3.4 The user

- **REJECT.** A centralized app already provides refunds, chargebacks, support, and a familiar interface. ARC asks the user to trust an approval-and-audit overlay whose protection is hard to feel until something goes wrong.
- **WAIT.** With no merchants, an ARC agent has nothing to do; the user rationally waits for the network the merchants are waiting to join.

### 3.5 The community or governance body

- **REJECT.** Governance is unpaid, adversarial labor — fraud reports, appeals, conflict-of-interest checks — that does not disappear because the system is open ([bootstrap §6](bootstrap-and-incentives.md)). A community can decline the work.
- **DEFECT.** A governance body can drift from neutral arbiter toward an entrenched gatekeeper, honoring the protocol's forms while bending its rulings.
- **FORK.** A community that dislikes a ruling can withdraw recognition and run its own fork, which severs *future* imports but cannot re-sort the rulings already folded ([threat-model §13](threat-model.md)).

## 4. Candidate Coordination Mechanisms

Each item below is a coordination mechanism that *could* change one of the calculations in §3. None is asserted to work. Each is paired with what remains unproven, because a mechanism stated without its residue is a claim in disguise. Whether mechanisms of this shape have historically moved adoption — and how often comparable open protocols were instead displaced after adopting — is surveyed in [coordination-economics-survey.md](coordination-economics-survey.md).

### 4.1 Lower integration cost → addresses WAIT, REJECT

- **Hypothesis:** if structured offers and the approval seam are cheap enough to add to an existing system, the first-mover cost that justifies WAIT shrinks.
- **Unproven:** "cheap enough" is undefined. ARC has no measured integration cost against any real merchant stack, and a low cost still buys nothing without demand on the other side.

### 4.2 Approval and audit overlay → addresses REJECT (user, company)

- **Hypothesis:** a portable, recomputable record of who approved what — verifiable after the fact — is worth more to a cautious party than an opaque platform's word.
- **Unproven:** the value is felt mainly *after* a failure, so it is hard to price in advance. The overlay also relocates trust onto whoever renders the approval to the human (the view-fidelity residue), which it does not eliminate.

### 4.3 Reputation portability → addresses REJECT, DEFECT (merchant)

- **Hypothesis:** if a merchant can carry earned reputation across communities, the lock-in that makes a platform's enclosure valuable weakens, raising the cost of staying enclosed.
- **Unproven:** portable reputation is only as meaningful as it is Sybil-resistant, and Sybil resistance lives in the fold, not the protocol. Portability also makes manufactured histories portable.

### 4.4 Replaceable / forkable discovery → addresses FORK, REJECT

- **Hypothesis:** if discovery is a swappable, disclosed component rather than a captured ranking, FORK loses its appeal — a participant unhappy with one backend replaces it instead of exiting the protocol.
- **Unproven:** replaceability does not create the alternative backend; someone must fund and operate one ([bootstrap §7](bootstrap-and-incentives.md)). An ecosystem with one discovery backend is captured regardless of whether the spec permits more.

### 4.5 Governance transparency → addresses DEFECT (governance), REJECT (user)

- **Hypothesis:** if rulings are recorded and recomputable, a governance body that drifts toward gatekeeping is visible, which raises the cost of defecting from neutrality.
- **Unproven:** visibility is not enforcement. A recorded biased ruling is still a ruling; the log exposes the drift but does not reverse it, and exposure only bites if some other community is willing to act on it.

### 4.6 Open spec as latent counter-pressure → reframes FORK

- **Hypothesis:** the openness that makes FORK cheap is not a benefit ARC hands adopters but a constraint it operates under — an operator who encloses too far invites a fork, so the bare *possibility* of forking may act as a check on whoever holds the most influence.
- **Unproven:** the check only bites if a fork is *viable*, and viability needs the very network effects that are missing. A cheap fork against an empty network pressures no one; openness is as easily a route to exit as a deterrent against capture.

## 5. What Stays Off-Ledger

The mechanisms in §4 share a boundary. ARC can make a defection *visible* and *recomputable* after the fact; it cannot make non-defection *rational* in advance. That gap is the adoption frontier, and it does not fold.

The cold-start fixture ([`examples/reference-client/coldstart_fixture.py`](../examples/reference-client/)) shows the same wall from one node's view: a newcomer has exactly three exits — *earn* edges slowly, *manufacture* volume with undisclosed agents, or *borrow* an established party's weak tie — and on the log these are indistinguishable. **Cold start cannot be resolved from the log alone.** A mechanism that claims to resolve it from the log alone is the failure mode this protocol warns against ("adoption verified by protocol").

What changes the calculus is lived experience, not a document: a community where the audit overlay caught a real fraud, a merchant whose portable reputation actually moved, a user who recovered something a platform would have swallowed. None of that can be asserted here without misrepresenting ARC's current state.

## 6. A Refusal-Recording Schema

The §3 exits are not only an analysis; they are a measurement vocabulary. The cheapest honest experiment available before any network exists is to record refusals in a structured form, so a later pilot inherits data instead of anecdotes.

A minimal record per refusal:

```txt
actor      — developer | company | merchant | user | community
exit       — WAIT | DEFECT | FORK | REJECT
reason     — the participant's own words, not a category we assigned
mechanism  — which §4 candidate, if any, the participant says would have
             changed the decision; "none" is a valid and important answer
```

The discipline is in how the fields are filled:

- The schema records what a participant *says*, not what we infer. A reason paraphrased into our own category is already a claim in disguise.
- `mechanism = none` is the most valuable cell: a refusal that no §4 candidate would have moved is a candidate falsified — which is the inverse doing exactly its job.
- A `WAIT` is not a soft `REJECT`. It records that the calculus could flip once others move, and names *whose* move it waits on — a different datum than a flat no, and the one the bootstrap chicken-and-egg turns on.
- The instrument must not drift into a persuasion script. Its job is to capture the refusal faithfully, not to convert it; an interviewer who argues the participant out of their reason has corrupted the record, not improved the result.

This gives a concrete shape to what [roadmap §Stage 5](roadmap.md) already asks for ("Record why any merchants, logistics providers, or users declined"). It produces no adoption claim. It produces a falsification surface.

An executable probe ([`examples/refusal-recording-demo`](../examples/refusal-recording-demo/)) folds synthetic records through this schema and makes the boundary literal — **adoption does not fold, but a refusal record does**: candidate mechanisms are weakened or falsified, never validated, while the reason's truth and the actor's future stay off-ledger.

## 7. Current Position

ARC's adoption theory is not just incomplete — its honest form is inverted. The defensible work is to enumerate why each actor declines (§3), to hold the countering mechanisms as hypotheses (§4), and to record refusals as data (§6) — not to assert that the mechanisms win.

The next useful artifacts are not adoption claims but tests of the inverse:

- a measured integration cost against one real merchant stack
- a single community where the audit overlay is exercised against a real dispute
- refusals recorded in the §6 schema from real merchants, users, or communities ([roadmap §Stage 5](roadmap.md))

These three are the instruments of [pilot-design.md](pilot-design.md), which defines how a limited pilot would test the inverse — learning, not validation.

A recorded "no," with its reason, is worth more to this frontier than an asserted "yes." A protocol cannot learn from the adoption it imagines.

<h1 align="center">
  <img src="assets/arc-wordmark.svg" width="380" alt="ARC Protocol">
</h1>

> **Any agent. Any model. Any company.**
> **Human approval required.**

> An open protocol for human-approved delegation, portable authority, and
> recomputable audit — with commerce as its first implementation, not its
> definition.

---

## Table of Contents

1. [What ARC Is](#1-what-arc-is) · 2. [What ARC Is Not](#2-what-arc-is-not) ·
3. [Protocol Foundations](#3-protocol-foundations) ·
4. [Authority & Delegation](#4-authority--delegation) ·
5. [Event & Projection](#5-event--projection) ·
6. [Reference Implementation](#6-reference-implementation) ·
7. [First Implementation: Commerce](#7-first-implementation-commerce) ·
8. [Adoption & First Refusal](#8-adoption--first-refusal) ·
9. [Protocol Boundaries](#9-protocol-boundaries) ·
10. [Current Status](#10-current-status) · 11. [Roadmap](#11-roadmap) ·
12. [Further Reading](#12-further-reading) · 13. [License](#13-license)

---

## 1. What ARC Is

ARC is the open layer that decides **who may act, who may approve, and how those
actions are audited** — kept open so that no single operator owns the trust. It
is not another agent; it is the common layer heterogeneous agents share to be
delegated authority, act under human approval, have that authority revoked, and
leave an auditable trail.

Three pillars, one each:

- **Human-approved delegation** — agents negotiate and prepare; the human holds
  the final signed step. Delegation is scoped, attenuating, and never
  self-widening.
- **Portable authority** — authority routes between agents and across
  communities without being minted by any single operator. *Routed, not minted,
  and never forced*: a community may honor another's authority or decline it.
- **Recomputable audit** — only signed events are stored; trust, reputation, and
  standing are recomputed from them on demand, never saved as a score.

### Stance

ARC does not decide legitimacy. Legitimacy is a relation between an observer's
policy and the log — observers legitimately disagree, and ARC renders the
disagreement rather than resolving it. What a log cannot prove — legitimacy,
and interpretive, temporal, world, and presentation fidelity — ARC leaves
visible rather than hidden.

---

## 2. What ARC Is Not

To clear the most common first-read misunderstandings:

- **Not an AI model.** ARC runs no inference and ships no model.
- **Not an agent framework or runtime.** It does not orchestrate or execute
  agents; it is the authority-and-audit layer they can share.
- **Not a marketplace.** It hosts no listings and ranks no merchants; discovery
  is a replaceable, disclosed component, not the protocol.
- **Not a payment network.** It initiates no payment and settles nothing;
  payment stays with existing providers, after human approval.

---

## 3. Protocol Foundations

Everything in ARC folds back to a small, **closed** set of ideas. This is the
map; sections 4 and 5 are the detail.

- **Event** — the only stored, signed, verifiable unit. The set is closed: five
  types — `KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`, `ADJUDICATE` — plus a
  `nullifies` field.
- **Projection** — a deterministic fold over the event log, recomputed on
  demand and then discarded. Trust, reputation, standing, identity status, and
  current authority-state are all projections, never records.

The recurring result across every probe (§6) is that what leaks out of the five
types is always **policy or discipline, never a new primitive**: no scenario has
forced a sixth event type. Not storing the relationship is the structural
defense against becoming a social-credit database — there is no stored score,
profile, or status anywhere, because there is nothing stored but signed events.

---

## 4. Authority & Delegation

- **Human approval is a hard constraint, not a feature.** Nothing meaningful
  happens without a human's final signed step.
- **Delegation is explicit and scoped.** Authority is granted as an `AUTHORIZE`
  event carrying a `scope`. It attenuates as it passes along — a delegate can
  never widen its own mandate, only narrow it — and authority moves between
  agents without moving key material.
- **A mandate is exactly what an agent may sign without re-asking.** In-scope
  proposals can be auto-signed; out-of-scope proposals **escalate to a human**
  rather than executing.
- **Revocation uses `nullifies`.** It bounds future authority; the past stays
  auditable, not rewritten. Whether an act that already *completed* under a
  now-revoked delegation still stands is a fold-policy choice, made visible.
- **No single authority of last resort.** Humans rule their own action and risk;
  communities rule the commons. Authority is **routed, not minted**: a
  federation bridge can route another community's authority, but each community
  decides whether to honor it — recognition is never forced, and an honest
  terminal answer may simply be `CONTESTED`.

The current authority-state of any agent is a projection over these events,
never a stored permission record.

---

## 5. Event & Projection

<p align="center">
  <img src="assets/arc-canon-flow.svg" width="880" alt="The ARC Canon: KEY, ATTEST, AUTHORIZE, CHALLENGE, and ADJUDICATE as a flow with human approval (AUTHORIZE) at the center. Only signed events are stored; trust, reputation, and standing are projections recomputed on demand.">
</p>

> *Example (commerce): offer → `ATTEST`, approval → `AUTHORIZE`, dispute →
> `CHALLENGE`, ruling → `ADJUDICATE`.*

ARC stores only signed **Events**. Trust, reputation, standing, and identity
status are **Projections** — deterministic folds recomputed on demand over the
event log, then discarded.

This is the recomputable-audit pillar: any party holding the same log recomputes
the same projection, so a surface is never an authority's private claim — it is a
fold anyone can re-run and check.

What it does **not** buy is referent-truth. A valid signature proves a key
signed a record; it does not prove the record's referent is true. ARC names four
faces of that one wall and leaves each visible rather than hidden:

- **Interpretation** — a valid signature does not prove the signer faithfully
  read what they signed.
- **Time** — a signed timestamp proves a key stamped it, not that the time is
  true; the `refs` DAG gives a partial causal order for free, but not wall-clock
  truth.
- **World** — a signed `fulfillment` is detectable when contested, but its truth
  is not recoverable from the log; finality is not fidelity.
- **Presentation** — a deterministic render is not a faithful one; the bytes
  signed may not be the view shown.

---

## 6. Reference Implementation

These are not only claims on paper. A body of small, dependency-light executable
probes tests them — each a single-purpose slice, not a product. One command runs
the whole catalog:

```sh
python3 run_demos.py          # all 14 probes, ~10s, stdlib only, offline
python3 run_demos.py --list   # name + thesis of each
python3 run_demos.py refusal  # stream one probe in full
```

```txt
Current Reference Implementation
✔ a dozen-plus runnable examples (canonical types, custody, federation, fidelity)
✔ 8-run commerce failure catalog  [A]–[H]   (examples/local-commerce-demo)
✔ browser reference client — 7 authority/approval surfaces (examples/reference-client)
✔ authority, revocation & custody experiments on real Ed25519
✔ adoption / refusal experiments — the refusal-recording fold
```

A representative few:

- [`examples/canon-fold-demo`](examples/canon-fold-demo/) — scenarios fold a
  hand-built log (governed disputes, key rotation and revocation, conflicting
  and delegated authority). The five event types held: no scenario forced a
  sixth.
- [`examples/canon-ts`](examples/canon-ts/) — encodes the five types as a
  TypeScript discriminated union so the **compiler itself** rejects a sixth
  type, a non-`ADJUDICATE` verdict, an over-scope hot key, and a honored
  post-revoke act.
- [`examples/end-to-end-demo`](examples/end-to-end-demo/) — four parties each
  sign their own events; standing moves only when an `ADJUDICATE` is added,
  never by mutating stored state. Its `agent_flow.py` hands the consumer side to
  a real reasoning model when configured (verified once on `claude-opus-4-8`):
  the agent's *reasoning* never widens its *authority*.
- [`examples/reference-client`](examples/reference-client/) — renders the log as
  the surfaces a human actually sees, plus a mandate-routed write path (in-scope
  auto-signs, out-of-scope escalates). Bands probe cold-start legitimacy, key
  compromise on real Ed25519, federation, and the custody seam.
- [`examples/refusal-recording-demo`](examples/refusal-recording-demo/) — folds
  refusal records into a falsification surface: candidate adoption mechanisms
  are contradicted or named as gaps, never validated (§8).

The deepest edges stay open and visible, not hidden: a valid signature proves a
key signed, not that custody was sound, that the signer read its mandate
faithfully, or that the time it stamps is true (§5).

---

## 7. First Implementation: Commerce

Commerce is the problem that birthed ARC and remains its most developed
application — but it is an **implementation of the protocol, not the protocol.**

- Commerce is ARC's first reference implementation.
- It demonstrates the protocol; it does not define it.
- The same primitives apply beyond commerce — community governance, licensing,
  and auditable research coordination among them.

A human-approved purchase folds to exactly the §3–§5 primitives: a merchant's
signed offer is an `ATTEST`, the human's approval an `AUTHORIZE`, a dispute a
`CHALLENGE`, a community ruling an `ADJUDICATE`; reputation and transaction state
are projections, never stored scores. The runnable slice and its failure catalog
live in [`examples/local-commerce-demo`](examples/local-commerce-demo/).

---

## 8. Adoption & First Refusal

ARC's adoption theory is honest only when inverted. The defensible question is
not *why ARC will be adopted* but *why each actor can rationally decline* — and
the protocol is built to learn from real refusals, not imagined adoption.

- [`docs/adoption-and-defection.md`](docs/adoption-and-defection.md) — the four
  exits (WAIT / DEFECT / FORK / REJECT), the per-actor inverse, and candidate
  coordination mechanisms held as hypotheses, never as claims.
- [`docs/first-refusal-protocol.md`](docs/first-refusal-protocol.md) — how ARC
  makes first contact with reality by collecting a first *refusal* as data; the
  experiment validates the recording instrument, not the protocol.
- [`docs/coordination-economics-survey.md`](docs/coordination-economics-survey.md)
  — a comparative survey of why open protocols are adopted or displaced, and
  which levers transfer to ARC's harder, multi-sided case.
- [`docs/pilot-design.md`](docs/pilot-design.md) — how a limited pilot would test
  the inverse: learning, not validation.

The runnable [refusal-recording fold](examples/refusal-recording-demo/) makes
the boundary literal: **adoption does not fold, but a refusal record does.**

---

## 9. Protocol Boundaries

ARC defines **protocol semantics, not infrastructure.** What "semantics" means
is fixed by §3–§5 (the canonical event set, signature verification, projection
determinism, revocation via `nullifies`); everything below is an implementation
choice left to whoever runs an implementation.

- **Storage.** ARC does not prescribe a shared database. Each implementation is
  free to choose its own storage — SQLite, PostgreSQL, S3, Kafka, a ledger —
  *provided protocol semantics are preserved.* This single rule resolves the
  central-DB, distributed-DB, and blockchain questions at once.
- **Blockchain.** Not required as part of the protocol specification. An optional
  cryptographic checkpoint is infrastructure (an implementation choice), never a
  protocol mandate.
- **Token.** ARC itself defines no native token. Implementations may add
  additional layers, but those layers are outside the ARC protocol
  specification.
- **Payment.** ARC does not execute payment; it interoperates with existing
  providers after human approval, and guarantees no refund, chargeback, or
  recovery. See [liability-boundaries.md](docs/liability-boundaries.md).
- **Legal / regulated domains.** Community review informs trust; it does not
  replace courts, consumer-protection law, or professional regulation. Regulated
  domains stay outside scope unless reviewed under the relevant professional
  rules. See [liability-boundaries.md](docs/liability-boundaries.md) and
  [identity.md §3](docs/identity.md).

*(The "ARC" name and brand are a separate governance matter, also outside this
specification.)*

---

## 10. Current Status

ARC is currently an **executable reference implementation of its protocol
model** — not yet a complete specification, and not a product.

What runs today: the canonical event/projection model, scoped delegation and
revocation, a browser reference client, a real-reasoner end-to-end flow, a
commerce failure catalog, federation and custody seams, fidelity probes, and the
adoption/refusal experiments (§6, §8). The model is not only argued; it is
exercised.

What remains unresolved: a normative wire format and conformance suite, the
identity-reputation bootstrap, discovery without backend concentration,
sustainable governance, and — the open problem ARC is most honest about —
adoption itself, which does not fold
([adoption-and-defection.md](docs/adoption-and-defection.md)).

### Current limitations

- No real payments
- No real delivery
- No verified identity
- No legal guarantees
- No production-grade security

---

## 11. Roadmap

A condensed view; the full version, including per-stage milestones and explicit
non-goals, is in [docs/roadmap.md](docs/roadmap.md).

- **Reference corpus (current).** Canonical model, executable probes, reference
  client, commerce failure catalog, and the first adoption/refusal experiments.
- **First contact.** Record real refusals via the
  [First Refusal Protocol](docs/first-refusal-protocol.md) before any party
  begins to use ARC.
- **Specification.** A normative envelope, error model, versioning, transport
  profiles, and conformance tests
  ([future-protocol-spec.md](docs/future-protocol-spec.md)).
- **Pilot.** A limited, real-world test that measures the inverse — learning, not
  validation ([pilot-design.md](docs/pilot-design.md)).
- **Federation.** Cross-community identity, interoperable governance, and
  reputation portability under explicit local control.

Not on the roadmap: full decentralization, AI autonomy without human approval, a
required token, or enclosing the protocol under a single operator. ARC is open to
research collaboration, independent implementation, commercial adoption, funding,
and community stewardship — all compatible with a protocol intended to remain
uncaptured by any single operator.

---

## 12. Further Reading

**Canonical model**
[Object Model](docs/object-model.md) ·
[Event Registry](docs/event-registry.md) ·
[Authority & Conflict](docs/authority-and-conflict.md) ·
[Delegation & Spending Mandates](docs/delegation-and-spending-mandates.md) ·
[Key Custody](docs/key-custody.md) ·
[Threat Model](docs/threat-model.md) ·
[Glossary](docs/glossary.md)

**Adoption & first contact**
[Adoption & Defection](docs/adoption-and-defection.md) ·
[First Refusal Protocol](docs/first-refusal-protocol.md) ·
[Coordination-Economics Survey](docs/coordination-economics-survey.md) ·
[Pilot Design](docs/pilot-design.md) ·
[Bootstrap & Incentives](docs/bootstrap-and-incentives.md)

**Trust, positioning & limits**
[Trust Model Trade-offs](docs/trust-model-tradeoffs.md) ·
[Landscape & Positioning](docs/landscape-and-positioning.md) ·
[Liability Boundaries](docs/liability-boundaries.md) ·
[Future Protocol Spec](docs/future-protocol-spec.md)

**Supporting models**
[Identity](docs/identity.md) ·
[Reputation](docs/reputation.md) ·
[Governance](docs/governance.md)

**Commerce reference**
[Local Commerce Simulation](docs/local-commerce-simulation.md) ·
[Protocol Mechanics (commerce)](docs/protocol.md) ·
[Architecture (commerce system)](docs/architecture.md)

**Origins / early vision**
[Philosophy](docs/philosophy.md) — the project's founding narrative, kept as
history. ·
[Adjacent Ideas](docs/adjacent-ideas/)

---

## 13. License

This project is licensed under the Apache License 2.0. See the LICENSE file for
details.

<p align="center">
  <img src="assets/arc-stamp.svg" width="420" alt="Verified, signed by community — no central issuer. Any agent. Any model. Any company. Human approval required.">
</p>

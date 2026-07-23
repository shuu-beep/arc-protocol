<h1 align="center">
  <img src="assets/arc-wordmark.svg" width="380" alt="ARC Protocol">
</h1>

> ARC is an implementation-neutral authority protocol for recording the source,
> scope, delegation, approval, revocation, contest, and adjudication of authority
> over consequential actions. It operates over disclosed signed evidence and
> supports recomputation for bounded audit; its records do not prove real-world
> outcomes. Commerce is its flagship application and first implementation profile,
> not the protocol boundary.

---

## Table of Contents

[Quick Start](#quick-start) · 1. [What ARC Is](#1-what-arc-is) · 2. [What ARC Is Not](#2-what-arc-is-not) ·
3. [Protocol Foundations](#3-protocol-foundations) ·
4. [Authority & Delegation](#4-authority--delegation) ·
5. [Event & Projection](#5-event--projection) ·
6. [Executable Reference Corpus](#6-executable-reference-corpus) ·
7. [Flagship Application: Commerce](#7-flagship-application-commerce) ·
8. [Adoption & First Refusal](#8-adoption--first-refusal) ·
9. [Protocol Boundaries](#9-protocol-boundaries) ·
10. [Current Status](#10-current-status) · 11. [Roadmap](#11-roadmap) ·
12. [Further Reading](#12-further-reading) · 13. [License](#13-license)

---

## Quick Start

New to ARC? Start by running the executable probe catalog. No services, API
keys, or database required for the default catalog — Python 3 alone:

```sh
git clone https://github.com/shuu-beep/arc-protocol.git
cd arc-protocol
python3 run_demos.py          # all 14 probes, ~10s, offline
python3 run_demos.py --list   # each probe's name and one-line thesis
```

Then inspect one probe in full:

```sh
python3 run_demos.py refusal  # e.g. the refusal-recording fold (§8)
```

Each probe is a single stdlib-only Python file next to its own README under
[`examples/`](examples/); [§6](#6-executable-reference-corpus) maps the catalog.

---

## 1. What ARC Is

ARC defines authority semantics for **who may act, who may approve, and how
disclosed signed evidence is audited**. It is not another agent; it is a protocol
model that heterogeneous agents and implementations can use to delegate authority,
act under human-authored coverage, revoke that authority, and leave signed records
for bounded audit.

Core semantics:

- **Human-rooted delegation** — every consequential act needs **Current
  Coverage** from a human-authored `AUTHORIZE`: either the unchanged exact act or
  a valid scoped mandate. Delegation attenuates and never self-widens.
- **Portable authority records** — scoped authority can be represented across
  agent-to-agent delegation chains. Interpretation across implementations requires
  compatible named profiles. A recipient remains free to honor or decline
  authority from another context.
- **Named Projection recomputation** — signed Events are folded by a named
  Projection over identified evidence and declared policy/ordering inputs. Derived standing is
  recomputed on demand, never saved as an authoritative score.

### Stance

ARC does not decide legitimacy. Named Projections can expose policy-relative
differences when the relevant evidence and declared inputs are available. ARC
does not guarantee that a deployment discloses every difference, and a log does
not by itself prove legitimacy or interpretive, temporal, world, or presentation
fidelity.

---

## 2. What ARC Is Not

To clear the most common first-read misunderstandings:

- **Not an AI model.** ARC runs no inference and ships no model.
- **Not an agent framework or runtime.** It does not orchestrate or execute
  agents; it is the authority-and-audit layer they can share.
- **Not a marketplace.** It hosts no listings and ranks no merchants; discovery
  is an application/profile component, not the protocol.
- **Not a payment network.** It initiates no payment and settles nothing;
  an ARC-compatible commerce flow hands off to external payment or settlement
  systems only when the action has Current Coverage.

---

## 3. Protocol Foundations

ARC's current model uses an Event/Projection split and a closed Event vocabulary.
Sections 4 and 5 provide the detail.

- **Event** — the only canonical stored, signed record unit. The current set is
  closed: five
  types — `KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`, `ADJUDICATE` — plus a
  `nullifies` field.
- **Projection** — a named deterministic fold over an identified Event set with
  declared version, policy, and ordering/as-of inputs. Trust, reputation,
  standing, identity status, and current authority-state are derived
  Projections, not canonical records; any cache is non-authoritative.

Across the current probe corpus (§6), no scenario has forced a sixth Event type;
that is evidence for the present closed vocabulary, not a claim of permanent
sufficiency. ARC does not define a global score, profile, Relationship, or
status as authoritative protocol state. Derived views and any caches are
implementation artifacts; this boundary does not prevent a deployment from
performing separate profiling.

---

## 4. Authority & Delegation

- **Current Coverage requirement.** A consequential act needs Current Coverage
  from an act-specific authorization for its unchanged target or from an
  unexpired, unrevoked scoped mandate.
- **Delegation is explicit and scoped.** Authority is granted as an `AUTHORIZE`
  event carrying a `scope`. It attenuates as it passes along — a delegate can
  never widen its own mandate, only narrow it — and authority moves between
  agents without moving key material.
- **A mandate bounds what an implementation may sign without re-asking.** The
  executable corpus demonstrates one fail-closed policy: in-scope proposals are
  signed and unsupported or out-of-scope proposals escalate to a human.
- **Revocation uses `nullifies`.** It bounds future authority; the past stays
  auditable, not rewritten. Whether a current reader continues to honor an act
  that already *completed* under a now-revoked delegation is a fold-policy
  choice that must be declared for a recomputability claim.
- **Authority domains remain distinct.** Authority should originate from the
  party legitimately responsible for the action and its risk. In the current ARC
  authority profiles, that root is typically human. Community authority is
  limited to its declared commons and authority profile. Where deployments exchange authority evidence,
  each recipient decides whether to honor it. Federation is optional, and an
  applicable no-precedence policy may return `CONTESTED`.

The current authority-state of any agent is a Projection over these Events, not
an authoritative permission record; any cache is an implementation artifact.

Quorum member participation remains **OPEN** between `ATTEST` and `AUTHORIZE`.
Deterministic mandate interpretation and atomic cumulative consumption are both
required before interoperability claims; no mechanism is selected here. See
[Event Registry §10](docs/event-registry.md#10-known-tensions-and-open-questions)
and [Delegation & Spending Mandates §10](docs/delegation-and-spending-mandates.md#10-open-questions).

---

## 5. Event & Projection

<p align="center">
  <img src="assets/arc-canon-flow.svg" width="880" alt="The ARC Canon: KEY, ATTEST, AUTHORIZE, CHALLENGE, and ADJUDICATE as canonical records, with trust, reputation, and standing represented as derived, recomputable Projections.">
</p>

> *Example (commerce): offer → `ATTEST`, approval → `AUTHORIZE`, dispute →
> `CHALLENGE`, ruling → `ADJUDICATE`.*

ARC defines signed **Events** as its canonical records. Trust, reputation,
standing, and identity status are **Projections** — named deterministic folds
over identified Event sets. An implementation may cache a result, but the cache
does not become authoritative protocol state.

ARC makes disclosed evidence recomputable; it does not make undisclosed evidence
observable or prove that a disclosed Event set is complete. An observer can
verify only the properties supported by the Events, Projection identity/version,
policy and ordering inputs, and completeness evidence available to that observer.
**External Record Verification**, an **Independently Recomputable Result**, and a
**Publicly Recomputable Result** are separate claims; public availability is not
required by ARC. See [Object Model §5](docs/object-model.md#5-scoped-replay-and-recomputability).

What it does **not** buy is referent-truth. Under a declared security profile, a
valid signature supports the conclusion that a key signed the covered bytes; it
does not establish the key controller, covering authority, or the record's
referent as true. ARC documents four related boundaries:

- **Interpretation** — record verification does not prove the signer faithfully
  read what they signed.
- **Time** — a signed timestamp records a key's time claim, not authoritative
  wall-clock time; `refs` express declared content dependencies but do not prove
  wall-clock issuance order.
- **World** — contradictory `fulfillment` claims may be detectable when the
  relevant records are disclosed, but their truth is not recoverable from the
  log; finality is not fidelity.
- **Presentation** — a deterministic render is not a faithful one; the bytes
  signed may not be the view shown.

---

## 6. Executable Reference Corpus

The repository includes small, dependency-light executable probes — each a
single-purpose slice, not a product. One command runs
the whole catalog — `python3 run_demos.py` ([Quick Start](#quick-start)).

```txt
Executable Reference Corpus
✔ runnable examples (canonical types, custody, federation, fidelity)
✔ 8-run commerce failure catalog  [A]–[H]   (examples/local-commerce-demo)
✔ browser reference client — 7 authority/approval surfaces (examples/reference-client)
✔ selected authority, revocation & custody fixtures use illustrative Ed25519
✔ adoption / refusal experiments — the refusal-recording fold
```

A representative few:

- [`examples/canon-fold-demo`](examples/canon-fold-demo/) — scenarios fold a
  hand-built log (governed disputes, key rotation and revocation, conflicting
  and delegated authority). The five event types held: no scenario forced a
  sixth.
- [`examples/canon-ts`](examples/canon-ts/) — encodes the five types and selected
  structural constraints as TypeScript types with negative compile cases. These
  checks do not enforce runtime authority, custody, or revocation semantics.
- [`examples/end-to-end-demo`](examples/end-to-end-demo/) — four parties each
  emit their own mock-signed Events; the fixture's standing view changes when an
  `ADJUDICATE` is added rather than by mutating stored state. Its `agent_flow.py`
  can call a configured external reasoner; the default path is scripted. The
  fixture does not establish real human approval.
- [`examples/reference-client`](examples/reference-client/) — renders fixture UI
  surfaces over supplied logs, plus a mandate-routed write path under its named
  policy. Bands probe cold-start policy, key compromise on Ed25519 fixtures,
  federation, and the custody seam.
- [`examples/refusal-recording-demo`](examples/refusal-recording-demo/) — folds
  synthetic refusal records into a comparison surface against declared candidate
  mechanisms. It does not empirically falsify or validate those mechanisms (§8).

The corpus documents unresolved custody, signer-interpretation, and timestamp
boundaries. Whether a deployment exposes the relevant evidence and policy inputs
depends on its observer surface (§5).

---

## 7. Flagship Application: Commerce

Commerce is the problem that birthed ARC and remains its most developed
application — but it is an **implementation of the protocol, not the protocol.**

- Commerce is ARC's first implementation profile and flagship application.
- It exercises the protocol model in one application; it does not define it.
- Possible future profiles could test the same Event vocabulary in domains such
  as community governance, licensing, or auditable research coordination.

A Commerce fixture maps a merchant's signed offer to `ATTEST`, human-granted
authority to `AUTHORIZE`, a dispute to `CHALLENGE`, and a community ruling to
`ADJUDICATE`; reputation and transaction state are derived Projections, not
canonical records. The runnable slice and its failure catalog
live in [`examples/local-commerce-demo`](examples/local-commerce-demo/).

---

## 8. Adoption & First Refusal

ARC's current adoption research records reasons parties may decline. It does not
establish adoption outcomes or a real-refusal dataset; the current executable
validates only the recording path with synthetic fixtures.

- [`docs/adoption-and-defection.md`](docs/adoption-and-defection.md) — the four
  exits (WAIT / DEFECT / FORK / REJECT), the per-actor inverse, and candidate
  coordination mechanisms held as hypotheses, never as claims.
- [`docs/first-refusal-protocol.md`](docs/first-refusal-protocol.md) — a study
  design for collecting an initial *refusal* as data; the experiment tests
  the recording instrument, not the protocol.
- [`docs/coordination-economics-survey.md`](docs/coordination-economics-survey.md)
  — a preliminary comparison of why selected open protocols were adopted or
  displaced, and which hypotheses may be relevant to the multi-sided Commerce
  application.
- [`docs/pilot-design.md`](docs/pilot-design.md) — how a limited pilot would test
  the inverse: learning, not validation.

The runnable [refusal-recording fold](examples/refusal-recording-demo/)
demonstrates that its refusal records can be folded; it does not model adoption.

---

## 9. Protocol Boundaries

ARC defines **protocol semantics, not infrastructure, governance topology, or
settlement.** What "semantics" means is fixed by §3–§5 (the canonical event set,
record verification, named Projection behavior, revocation via `nullifies`, and
the human and community authority boundaries). Implementations declare the
profiles needed for any stronger compatibility claim.

- **Storage and operation.** ARC prescribes neither a shared database nor a
  deployment topology. SQLite, PostgreSQL, S3, Kafka, append-only logs, shared
  ledgers, and combinations of them are all implementation choices.
- **Payment.** ARC does not initiate, execute, or settle payment. An
  ARC Commerce-profile flow hands off to an external payment rail only when the
  action has Current Coverage; those external
  rails provide no ARC guarantee of refund, chargeback, or recovery. See
  [liability-boundaries.md](docs/liability-boundaries.md).
- **Legal / regulated domains.** Community review informs trust; it does not
  replace courts, consumer-protection law, or professional regulation. Regulated
  domains stay outside scope unless reviewed under the relevant professional
  rules. See [liability-boundaries.md](docs/liability-boundaries.md) and
  [identity.md §3](docs/identity.md).

---

## 10. Current Status

ARC currently has an **Executable Reference Corpus** for its protocol model —
not a complete independently implementable specification, normative conformance
suite, production system, or product.

What runs today: the canonical Event/Projection model, scoped delegation and
revocation, a browser reference client, an optional external-reasoner flow, a
commerce failure catalog, federation and custody seams, fidelity probes, and the
adoption/refusal experiments (§6, §8).

What remains unresolved: a normative wire/security profile and complete
conformance suite; quorum member semantics; deterministic mandate interpretation;
atomic cumulative mandate consumption; the identity-reputation bootstrap;
Commerce discovery and governance operation; and
adoption incentives, which current probes do not establish
([adoption-and-defection.md](docs/adoption-and-defection.md)).

### Current limitations

- No real payments
- No real delivery
- No production identity-assurance profile
- No legal guarantees
- No selected normative signature suite
- No production-grade security

---

## 11. Roadmap

A condensed view; the full version, including per-stage milestones and explicit
non-goals, is in [docs/roadmap.md](docs/roadmap.md).

- **Reference corpus (current).** Canonical model, executable probes, reference
  client, commerce failure catalog, and the first adoption/refusal experiments.
- **First contact.** Record real refusals via the
  [First-Refusal Study Procedure](docs/first-refusal-protocol.md) before any party
  begins to use ARC.
- **Specification.** A normative envelope, error model, versioning, transport
  profiles, and conformance tests
  ([future-protocol-spec.md](docs/future-protocol-spec.md)).
- **Pilot.** A limited, real-world test that measures the inverse — learning, not
  validation ([pilot-design.md](docs/pilot-design.md)).
- **Optional profile work.** Cross-community identity, governance, and
  reputation-portability profiles under declared policies.

---

## 12. Further Reading

**Normative / current core semantics**
[Object Model](docs/object-model.md) ·
[Event Registry](docs/event-registry.md) ·
[Authority & Conflict](docs/authority-and-conflict.md) ·
[Delegation & Spending Mandates](docs/delegation-and-spending-mandates.md)

**Explanatory / conformance planning**
[Glossary](docs/glossary.md) ·
[Future Protocol Spec](docs/future-protocol-spec.md) ·
[Key Custody](docs/key-custody.md) ·
[Trust Model Trade-offs](docs/trust-model-tradeoffs.md) ·
[Landscape & Positioning](docs/landscape-and-positioning.md) ·
[Liability Boundaries](docs/liability-boundaries.md) ·
[Identity](docs/identity.md)

**Executable validation**
[Probe Catalog](examples/) ·
[Reference Client](examples/reference-client/) ·
[Local Commerce Demo](examples/local-commerce-demo/) ·
[Refusal-Recording Demo](examples/refusal-recording-demo/)

**Flagship application**
[Architecture (Commerce)](docs/architecture.md) ·
[Protocol Mechanics (Commerce)](docs/protocol.md) ·
[Local Commerce Simulation](docs/local-commerce-simulation.md) ·
[Reputation](docs/reputation.md) ·
[Governance](docs/governance.md) ·
[Threat Model](docs/threat-model.md)

**Historical / legacy**
[Philosophy](docs/philosophy.md) — the project's founding Commerce-first
narrative, preserved as history. ·
[Agent-Mediated Commerce & Infrastructure](docs/agent-mediated-commerce-infrastructure.md)

**Research notes**
[Adoption & Defection](docs/adoption-and-defection.md) ·
[First Refusal Protocol](docs/first-refusal-protocol.md) ·
[Coordination-Economics Survey](docs/coordination-economics-survey.md) ·
[Pilot Design](docs/pilot-design.md) ·
[Bootstrap & Incentives](docs/bootstrap-and-incentives.md) ·
[Adjacent Ideas](docs/adjacent-ideas/)

---

## 13. License

This project is licensed under the Apache License 2.0. See the LICENSE file for
details.

<p align="center">
  <img src="assets/arc-stamp.svg" width="420" alt="ARC recorded claim — record-level claims, not outcome proof.">
</p>

<h1 align="center">
  <img src="assets/arc-wordmark.svg" width="380" alt="ARC Protocol">
</h1>

> ARC is a research protocol and executable reference for signed, recomputable
> authority and standing evidence when independent principals act through
> Agents.

**What happens when your Agent meets another Agent and negotiates on your
behalf?**

```text
Principal A                                         Principal B
    |                                                   |
    | bounded delegation                                | bounded delegation
    v                                                   v
Buyer Agent  <--- propose / counter / refuse / accept --->  Seller Agent
    |                                                   |
    +---------- transaction and outcome evidence -------+
                            |
           withdrawal / conflict / challenge / adjudication
                            |
        Current Coverage and Current Standing recomputation
```

For example, a person may authorize a Buyer Agent to purchase one meal for no
more than KRW 20,000 when declared quality and delivery conditions are met. A
Seller Agent may offer only available items within its own application and
principal constraints. Either Agent can refuse, counter, or escalate a term
outside its authority. If authority expires or is withdrawn, an offer changes,
or claims become contested, the parties need more than a transport message or a
current policy Boolean to explain what evidence supports the current result.

ARC studies that signed semantic layer: delegation, narrowing, attributable
claims, exact approval, expiry, causal withdrawal, unresolved conflict,
challenge, authorized adjudication, and recomputation from the same declared
Event set, profile, ordering context, and `as_of` value.

ARC is **not** a payment rail, Agent transport, marketplace, checkout protocol,
universal identity system, universal reputation score, production gateway, or
real dispute tribunal.

**[Why ARC?](docs/why-arc.md)** gives the falsifiable comparison.
**[Landscape and Positioning](docs/landscape-and-positioning.md)** compares the
model with current Agent, commerce, payment, credential, and authorization
standards.

---

## Table of Contents

[Quick Start](#quick-start) ·
1. [The Multi-Principal Problem](#1-the-multi-principal-problem) ·
2. [What ARC Defines](#2-what-arc-defines) ·
3. [Events and Recomputation](#3-events-and-recomputation) ·
4. [Commerce Reference Profile](#4-commerce-reference-profile) ·
5. [Executable Evidence](#5-executable-evidence) ·
6. [Protocol, Core, and Gate](#6-protocol-core-and-gate) ·
7. [Overlap and Material Gap](#7-overlap-and-material-gap) ·
8. [Boundaries](#8-boundaries) ·
9. [Maturity and Adoption](#9-maturity-and-adoption) ·
10. [Further Reading](#10-further-reading) ·
11. [License](#11-license)

---

## Quick Start

Run the complete offline probe catalog with Python 3. No service, API key, or
database is required.

```sh
git clone https://github.com/shuu-beep/arc-protocol.git
cd arc-protocol
python3 run_demos.py          # all 14 probes, ~10s, offline
python3 run_demos.py --list   # names and one-line theses
```

Run one probe and inspect its neighboring README:

```sh
python3 run_demos.py commerce
```

<a id="1-what-arc-is"></a>

## 1. The Multi-Principal Problem

Agent runtimes already provide useful sandbox, permission, approval, and hook
controls. IAM, OAuth, policy engines, API gateways, credential brokers, and
payment systems already control many consequential actions. ARC does not try to
replace them.

Those controls are usually strongest inside one runtime, vendor, organization,
or transaction system. The original ARC question is broader: how can Agents
representing different principals exchange and inspect authority-relevant
evidence without assuming one private database is the complete shared truth?

The recurring questions are:

1. Which principal authorized which Agent or delegate?
2. What scope, amount, counterparty, resource, and time interval were covered?
3. Did a later delegation narrow rather than widen that scope?
4. Which exact offer or action did a principal approve?
5. What changes after expiry, withdrawal, key lifecycle evidence, or conflict?
6. Which challenge or adjudication is recognized under the selected profile?
7. Can another observer recompute the same current result from the same inputs?

ARC treats authority, standing, and reputation readings as named computations
over signed evidence—not as globally authoritative mutable labels.

## 2. What ARC Defines

ARC proposes shared semantics for:

- **bilateral principal/Agent applicability** across independent counterparties;
- **bounded delegation and narrowing** without sharing private key material;
- **exact approval** bound to unchanged reviewable action material;
- **causal withdrawal** that does not erase the historical record;
- **explicit `CONTESTED` results** when supplied evidence does not justify a
  unique current answer;
- **challenge and authorized adjudication records** without inventing a
  universal tribunal; and
- **Event-set/profile/as-of recomputation** of Current Coverage and Current
  Standing.

These are evidence semantics. A receiving application chooses which profile,
trust roots, Event set, and external systems it accepts.

ARC does not define discovery, network transport, product ontology, inventory,
checkout, payment credentials, settlement, delivery, legal identity, real-world
truth, or enforcement. Those layers remain external.

## 3. Events and Recomputation

ARC's Canon contains five signed Event types:

- `KEY` — key registration, rotation, revocation, and provenance claims;
- `ATTEST` — attributable evidence such as an offer or outcome claim;
- `AUTHORIZE` — exact approval or scoped delegated authority;
- `CHALLENGE` — a signed contest of a claim, action, or ruling; and
- `ADJUDICATE` — a decision by an authority recognized under a named profile.

Withdrawal and key revocation are not extra Event types. They use the existing
types, predicates, causal references, and `nullifies` field under declared
profile rules.

```text
Declared signed Events
  + profile and version
  + ordering context
  + verification/completeness boundary
  + as_of
             |
             v
       Named Projection
             |
             v
Current Coverage / Current Standing / contextual reputation view
```

Different Event sets or profiles may legitimately yield different results. ARC
therefore identifies the computation rather than claiming one invisible global
history or universal authority of last resort.

See [Object Model](docs/object-model.md),
[Event Registry](docs/event-registry.md), and
[Authority and Conflict](docs/authority-and-conflict.md).

## 4. Commerce Reference Profile

Commerce is the motivating and most developed application profile.

```text
external discovery
  -> offer request / proposal / counteroffer / refusal
  -> attributable offer evidence
  -> mandate coverage or exact principal approval
  -> optional application Gate decision
  -> external checkout/payment/fulfillment
  -> outcome evidence
  -> challenge / adjudication
  -> recomputed authority or standing
```

Proposal, counteroffer, refusal, acceptance, checkout, and fulfillment messages
are application or external-protocol messages. They are not additional ARC
Event types. An application may record an attributable offer as `ATTEST`, an
approval as `AUTHORIZE`, a dispute as `CHALLENGE`, and a recognized ruling as
`ADJUDICATE`.

The current fixtures can evaluate Buyer-side authority against an exact action
and supplied counterparty evidence. They do **not** prove a Seller Agent's
complete internal delegation chain, inventory truth, payment, delivery, or
legal outcome.

See the [Commerce application profile](docs/protocol.md),
[Architecture](docs/architecture.md), and
[discovery topology choices](diagrams/discovery-topology.md).

## 5. Executable Evidence

The repository contains 14 runnable, offline probes:

```text
✔ five-type Canon folds and deterministic authored scenarios
✔ delegated authority, narrowing, expiry, and withdrawal
✔ exact approval and escalation seams
✔ causal conflict and policy-relative resolution
✔ key rotation, revocation, compromise, and custody boundaries
✔ stale/cache, temporal, execution, signer, and view fidelity
✔ threshold and federation ambiguity
✔ eight-case Commerce failure catalog
✔ refusal-recording experiment
```

Representative paths:

- [`examples/canon-fold-demo`](examples/canon-fold-demo/) — Canon sufficiency,
  delegation, withdrawal, conflict, and illustrative resolution policies.
- [`examples/end-to-end-demo`](examples/end-to-end-demo/) — independently
  authored records folded into standing under a named policy.
- [`examples/reference-client`](examples/reference-client/) — browser reference
  artifact and authority/custody fixtures.
- [`examples/local-commerce-demo`](examples/local-commerce-demo/) — the
  Commerce application failure catalog.

Passing fixtures prove the authored behavior and boundaries they exercise. They
do not prove independent interoperability, complete evidence, production
security, external truth, or market adoption.

## 6. Protocol, Core, and Gate

```text
ARC Protocol
  signed Event and Projection semantics; application profiles; 14 probes
      |
      v
ARC Reference Core
  minimum executable authority/evidence validation and Projection reference
      |
      v
ARC Execution Gate
  optional application policy and simulated pre-dispatch enforcement examples
      |
      v
external target / payment / deployment / fulfillment
```

- **ARC Protocol** owns the proposed semantic model and the broader
  multi-principal research question.
- **[ARC Reference Core](https://github.com/shuu-beep/arc-reference-core)** is a
  non-normative executable reference for a bounded subset of authority and
  evidence semantics. It does not return application `ALLOW`/`DENY` decisions.
- **[ARC Execution Gate](https://github.com/shuu-beep/arc-execution-gate)**
  demonstrates how an application may combine a current Core result with local
  policy before a simulated dispatch. It is not ARC as a whole or a production
  gateway.

The current baselines are 14 Protocol probes, 93 Core tests, and 69 Gate tests.

## 7. Overlap and Material Gap

Current standards already cover much of the operational flow:

- A2A and FIPA provide Agent discovery/interaction and negotiation patterns;
- ACP and UCP provide checkout, order, and fulfillment state;
- AP2 provides important buyer mandate, exact transaction binding, expiry,
  verifier checking, receipts, and autonomous-use controls;
- OAuth/RFC 8693, IAM, and policy engines provide delegation and enforcement;
- verifiable credentials, OpenID4VP, UCP profiles, and payment-network Agent
  trust mechanisms provide identity and transaction evidence.

ARC must not claim those capabilities as generally unique.

The current comparison nevertheless finds a **material semantic gap**. The
reviewed stack does not natively provide one common model combining:

- signed bilateral authority and counterparty history;
- symmetric applicability to independently represented principals;
- unresolved causal `CONTESTED` state;
- causal withdrawal, challenge, and authorized adjudication; and
- reproducible Current Coverage/Standing from an identified Event set, profile,
  ordering context, and `as_of` value.

An application can build those properties itself, but doing so is custom
state/Event/recomputation work rather than use of an already equivalent standard.
See [Landscape and Positioning](docs/landscape-and-positioning.md).

## 8. Boundaries

ARC signatures and Projections do not establish:

- complete or globally available evidence;
- legal identity, beneficial ownership, or Agent independence;
- truthful offers, inventory, fulfillment, or transaction outcomes;
- legitimate governance institutions or legal jurisdiction;
- signing-key or downstream-credential custody;
- an independent approval channel or enforcement point;
- direct-path closure, durable atomic consumption, target idempotency,
  reconciliation, availability, or operations.

A production deployment must assign those responsibilities to identity,
credential, application, payment, IAM, gateway, target, and institutional
systems. See [Key Custody](docs/key-custody.md),
[Threat Model](docs/threat-model.md), and
[Liability Boundaries](docs/liability-boundaries.md).

## 9. Maturity and Adoption

ARC currently provides a coherent documentation model, 14 executable Protocol
probes, a Reference Core alpha, and simulated Execution Gate examples. The
multi-principal Commerce semantics are a real executable reference, not merely
historical speculation.

Independent wire/profile interoperability, production enforcement, and broad
Agent-to-Agent commerce adoption are not yet proved. The market is
**pre-market / not yet testable** for broad necessity claims.

That market status limits claims of inevitability, commercial necessity,
production readiness, or adoption. It is not a prerequisite for maintaining or
developing ARC as protocol research, an executable reference, or a public
technical profile. See the [Roadmap](docs/roadmap.md) for the separation between
research, interoperability, and production work.

## 10. Further Reading

**Foundations**

[Historical Philosophy](docs/philosophy.md) ·
[Object Model](docs/object-model.md) ·
[Event Registry](docs/event-registry.md) ·
[Authority and Conflict](docs/authority-and-conflict.md) ·
[Delegation and Spending Mandates](docs/delegation-and-spending-mandates.md)

**Multi-principal Commerce**

[Architecture](docs/architecture.md) ·
[Commerce Application Profile](docs/protocol.md) ·
[Agent-Mediated Commerce Infrastructure](docs/agent-mediated-commerce-infrastructure.md) ·
[Reputation](docs/reputation.md) ·
[Governance](docs/governance.md) ·
[Discovery Topology](diagrams/discovery-topology.md) ·
[Dispute Flow](diagrams/dispute-flow.md)

**Boundaries and comparison**

[Why ARC?](docs/why-arc.md) ·
[Landscape and Positioning](docs/landscape-and-positioning.md) ·
[Identity](docs/identity.md) ·
[Key Custody](docs/key-custody.md) ·
[Trust Model Trade-offs](docs/trust-model-tradeoffs.md) ·
[Liability Boundaries](docs/liability-boundaries.md) ·
[Threat Model](docs/threat-model.md) ·
[Specification Gap Register](docs/future-protocol-spec.md)

## 11. License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE).

<p align="center">
  <img src="assets/arc-stamp.svg" width="420" alt="ARC recorded claim — record-level claims, not outcome proof.">
</p>

# ARC Protocol: Research, Interoperability, and Production Tracks

> **Status:** Research/reference work may continue. Interoperability, adoption,
> production-readiness, and commercial claims require separate evidence.
> **Purpose:** Keep technically useful protocol work separate from market and
> deployment promises.

This is not a delivery schedule. It records three different tracks whose entry
conditions must not be conflated.

## 1. Current Technical Baseline

The current repositories provide:

- the Relationship/Event/Projection authority model;
- five Canon Event types;
- delegation, narrowing, expiry, withdrawal, conflict, challenge,
  adjudication, and recomputation semantics;
- 14 offline ARC Protocol probes and a browser reference artifact;
- a non-normative ARC Reference Core alpha with 93 tests;
- non-normative ARC Execution Gate examples with 69 tests; and
- a named Commerce application profile and failure catalog.

The reviewed standards can assemble the operational Agent-commerce flow, but
do not natively provide ARC's combined bilateral signed causal authority and
standing history, unresolved `CONTESTED`, and Event-set/profile/as-of
recomputation. That material semantic gap is a valid research subject.

## 2. Track A — Research and Protocol Work

### Purpose

Develop, test, explain, and falsify the semantic model as protocol research and
a public executable reference.

### Work that may proceed with explicit scope approval

- factual and Canon-consistency corrections;
- adversarial probes that test existing semantics;
- protocol/profile documentation and conformance questions;
- independent reproduction of current Projection behavior;
- security, privacy, evidence-completeness, and trust-root analysis;
- separately approved examples that exercise a genuinely new boundary;
- comparison with evolving Agent/commerce/authorization standards; and
- narrowing or removing claims when stronger alternatives emerge.

### Evidence standard

Research work does not require a current buyer, mandatory receiver, or proved
market demand. It must state what is implemented, what is hypothetical, what
the fixture proves, and what remains external.

### Current candidate, not approved here

A minimal Buyer Agent/Seller Agent Core/Gate example could make the motivating
multi-principal purpose more visible. It would require a separate approval and
must use existing Canon/API semantics; no implementation is authorized by this
document cleanup.

## 3. Track B — Interoperability and Adoption

### Purpose

Establish that independently implemented systems can exchange ARC evidence and
derive compatible results, and determine whether counterparties choose to use
that capability.

### Required evidence before claiming success

- a normative wire, hashing, signature, predicate/scope, and profile version;
- shared error and evidence-completeness semantics;
- conformance vectors and at least two independent implementations;
- compatible Event-set/profile/as-of results on adversarial cases;
- explicit trust and authority-recognition rules between participants; and
- observed integration/adoption evidence rather than forecast or conceptual
  fit.

The current corpus does not establish these results. Broad Agent-to-Agent
commerce adoption remains **pre-market / not yet testable**.

That status limits adoption claims only. It does not freeze Track A.

## 4. Track C — Production and Commercial Deployment

### Purpose

Use ARC-aware evidence to affect consequential real-world actions under a
documented security and operational architecture.

### Required evidence before claiming production readiness

- verified key/principal/Agent and external credential bindings;
- protected signing keys, approval channel, authority state, and downstream
  credentials outside an untrusted Agent runtime;
- independent PEP/dispatch ownership and closure of direct/alternate paths;
- durable concurrency, one-time consumption where required, target idempotency,
  reconciliation, and compensation;
- evidence acquisition and completeness contracts;
- privacy, retention, incident response, availability, and observability;
- domain-specific payment, fulfillment, dispute, legal, and liability controls;
  and
- measured behavior against the strongest native/IAM/domain alternative.

Reference Core and the current Execution Gate examples do not provide this
deployment architecture.

## 5. Shared Non-Goals

ARC does not aim to replace:

- A2A/FIPA Agent interaction;
- ACP/UCP checkout and order state;
- AP2 buyer mandate/payment authorization;
- OAuth/OIDC, IAM, policy engines, gateways, or credential brokers;
- verifiable credentials or identity providers;
- payment, settlement, fulfillment, refund, or chargeback systems;
- marketplaces, discovery providers, or universal ranking; or
- courts, regulators, contracts, or legitimate dispute institutions.

## 6. Claim Discipline

| Claim | Current status |
| --- | --- |
| coherent multi-principal semantic model | supported by documents and fixtures |
| material residual semantic gap | supported by current official-source comparison |
| executable Protocol reference | supported by 14 probes |
| bounded Core/Gate reference behavior | supported by their tests |
| independent interoperability | unproved |
| production security boundary | unproved |
| external transaction/outcome truth | external and unproved by ARC |
| broad adoption or commercial necessity | pre-market / not yet testable |

Market evidence is not a prerequisite for Track A. Independent implementation
evidence is required for Track B claims. Security, operational, legal, and
domain evidence is required for Track C claims.

## 7. Decision Rule

Before starting work, name the track and repository boundary.

- **Track A:** approve if the work tests, clarifies, or narrows the research
  model without silently making interoperability or production claims.
- **Track B:** require an independent counterparty/implementation and a
  falsifiable interoperability target.
- **Track C:** require an external enforcement architecture and domain owner;
  local fixtures are insufficient.

Do not use a Track B or C evidence gap to declare Track A valueless, and do not
use Track A success to imply Track B or C success.

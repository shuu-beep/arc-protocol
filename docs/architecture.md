# ARC Multi-Principal Commerce Reference Architecture

> **Status:** Non-normative application architecture
> **Purpose:** Show where ARC signed Events and recomputation fit when Agents
> representing independent principals negotiate and transact.

This document is not a production deployment blueprint. It assigns ownership
across protocol, application, identity, commerce, payment, and enforcement
layers so that an ARC record is not mistaken for a side effect or institution.

## 1. Architecture at a Glance

```text
Principal A                                      Principal B
    |                                                 |
    | mandate / exact approval                        | seller authority and policy
    v                                                 v
Buyer Agent  <--- external discovery and transport --->  Seller Agent
    |          proposal / counter / refuse / accept       |
    +---------------- attributable evidence --------------+
                              |
                              v
                    ARC signed Event set
                              |
              profile + ordering + as_of + verification
                              |
                              v
                    ARC Projection/recomputation
                              |
                 optional application Gate policy
                              |
                              v
           external checkout / payment / fulfillment
                              |
             outcome / challenge / adjudication evidence
                              |
                              v
                  recomputed Current Standing
```

## 2. Responsibility Layers

| Layer | Owns | Does not own |
| --- | --- | --- |
| Principal | intent, risk, authority grant, approval, withdrawal | Agent transport or transaction execution |
| Buyer/Seller Agent | interpretation, negotiation strategy, evidence exchange within application rules | authority beyond its mandate, external truth, legal power |
| Discovery | finding endpoints and ranking candidates | ARC authority, complete identity, offer truth |
| Agent transport | authenticated messages, tasks, sessions, retries | principal delegation or transaction settlement |
| Negotiation/application | proposal, counteroffer, refusal, acceptance, escalation, deadlines | Canon Event vocabulary or universal bargaining ontology |
| ARC Protocol | signed Event types, authority/standing concepts, named Projection inputs | discovery, checkout, credentials, dispatch, real remedies |
| ARC Reference Core | bounded structural/security validation and Current Coverage Projection reference | complete ARC application, Gate decisions, credentials, side effects |
| ARC Execution Gate | optional application policy and simulated pre-dispatch examples | ARC's whole purpose, production gateway, durable atomicity |
| Checkout/order | merchant-authoritative totals, inventory, order, cancellation, fulfillment state | ARC authority history unless integrated explicitly |
| Payment | payment credentials, authorization, settlement, refunds/chargebacks | general Agent negotiation or contextual standing |
| Identity/trust root | key-to-Agent/principal binding, credentials, issuer status, recovery | complete authority or outcome truth |
| Real institution | investigation, jurisdiction, appeal, remedy, legal enforcement | automatic legitimacy from a signed ARC record |

## 3. Concrete Buyer/Seller Flow

Assume Principal A gives Buyer Agent a mandate:

```text
category: meal
maximum: KRW 20,000
quality: at least 4.5 under the selected application view
delivery: no more than 40 minutes
valid until: declared expiry
```

Principal B configures Seller Agent with inventory, minimum price, discount,
delivery, cancellation, and escalation constraints. Those seller-side rules may
be ordinary application/IAM policy and are not automatically ARC Events.

1. Buyer Agent discovers Seller Agent through an external topology.
2. The Agents establish transport and exchange capabilities.
3. Buyer Agent requests terms; Seller Agent proposes an attributable offer.
4. Either side counters, refuses, accepts, or escalates outside its authority.
5. The Buyer application evaluates current mandate coverage against the exact
   offer/action; fresh approval is requested when required.
6. An optional Gate combines current authority with application policy.
7. External checkout/payment/fulfillment systems perform the transaction.
8. Parties or providers may issue outcome claims; a party may challenge them.
9. A profile-recognized adjudication may change the application Projection.

The current ARC fixtures can represent and evaluate parts of this flow. They do
not establish complete Seller Principal delegation, inventory, payment,
delivery, evidence completeness, or legal effect.

## 4. Transport Messages and ARC Events

Most Agent interaction is ephemeral application traffic:

- discovery query and directory result;
- capability exchange;
- offer request;
- proposal or counterproposal;
- refusal, acceptance, cancellation, timeout, or retry;
- checkout and order operations.

These are not new Canon Event types. An application records only the
authority-relevant claims it chooses to retain under a named profile:

| Application fact or message | Possible ARC representation | Boundary |
| --- | --- | --- |
| attributable offer | `ATTEST commerce.offer` | proves signed bytes, not inventory or truth |
| exact principal approval | `AUTHORIZE consent.approval` | covers unchanged bound action only |
| scoped mandate/delegation | `AUTHORIZE consent.mandate` | must narrow through the chain |
| offer/mandate withdrawal | existing Event plus `nullifies` | causal/profile rules determine effect |
| fulfillment/payment result | `ATTEST commerce.*` | external provider/party claim |
| dispute | `CHALLENGE` | contest, not proof |
| recognized ruling | `ADJUDICATE` | profile-relative decision, not legal enforcement |

## 5. ARC Computation Boundary

A reproducible Projection declares at least:

```text
Event set identity
profile and version
ordering/causal context
as_of
verification results and security profile
evidence-completeness contract, if any
```

From these inputs an application may derive Current Coverage, Current Standing,
or a contextual reputation view. Different declared inputs may produce
different valid readings. Causal conflict may remain `CONTESTED`; a timestamp is
not an automatic winner.

ARC Events are not a transaction database. Requests, sessions, inventory,
payment state, delivery state, idempotency keys, and workflow state remain in
ordinary application systems.

## 6. Protocol, Core, and Gate

### ARC Protocol

Owns the five-type Event vocabulary, object/authority model, named application
profiles, and executable probes. It contains the broader multi-principal model.

### ARC Reference Core

Provides a minimum non-normative executable reference for bounded Event
validation, key lifecycle, evidence sets, scope binding, ordering, and Current
Coverage. It does not validate the complete commerce flow or return application
`ALLOW`/`DENY` decisions.

### ARC Execution Gate

Shows how an application may map a current Core result and local policy to a
pre-dispatch decision. Current examples use simulated adapters and process-local
replay state. Gate is optional and is not ARC as a whole.

## 7. Hypothetical Production Enforcement

If ARC evidence must control a real side effect after Agent-runtime compromise,
the enforcement point and consequential credential must remain outside runtime
control:

```text
untrusted Agent/runtime
  -> authenticated exact request
  -> independent application enforcement point
       - obtain required current evidence
       - verify signatures, roots, profile, and completeness contract
       - recompute or validate Projection identity
       - apply application policy
       - atomically reserve/consume approval with dispatch
       - use a credential unavailable to the Agent
  -> target that rejects every alternate path
```

The current Gate repository does not deploy this architecture. A production
system still needs durable concurrency, target idempotency, compensation,
credential rotation, direct-path closure, availability, observability, and
incident response.

## 8. Discovery and Topology

ARC does not require a central directory, federation, peer-to-peer network, or
blockchain. Closed platforms, federated/community registries, open indexes,
decentralized discovery, and direct known counterparties are all possible
application choices. See [Discovery Topology](../diagrams/discovery-topology.md).

Transport may use A2A, HTTP, MCP where appropriate, FIPA interaction protocols,
UCP/ACP operations, message queues, or another application protocol. ARC
semantics begin only where the application records or evaluates relevant signed
evidence.

## 9. Dispute and Standing

Evidence collection, notice, response, jurisdiction, appeal, refund,
chargeback, suspension, and legal enforcement belong to real applications and
institutions. ARC can record `CHALLENGE` and profile-recognized `ADJUDICATE`
Events and recompute a named view without erasing prior claims.

See [Dispute Flow](../diagrams/dispute-flow.md),
[Governance](./governance.md), and
[Liability Boundaries](./liability-boundaries.md).

## 10. Status

This architecture explains an executable research model, not a deployed
marketplace or production standard. Current external standards cover much of
the operational path. The residual material gap is the combined bilateral
causal authority/standing history and Event-set/profile/as-of recomputation.

Broad adoption is pre-market. That limits market and production claims, not
continued protocol research or the value of the reference architecture.

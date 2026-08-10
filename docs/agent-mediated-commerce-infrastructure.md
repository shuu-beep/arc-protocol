# Agent-Mediated Commerce Infrastructure: Historical Motivation and Boundaries

> **Status:** Historical, exploratory research; not Canon, roadmap, or a
> production recommendation.
>
> This note did not begin as an argument for blockchain-based commerce. ARC is
> implementation-neutral and does not require a ledger, token, wallet, or
> decentralized marketplace.

## 1. Why This Question Mattered

ARC began from a possible future in which people and organizations increasingly
act through Agents, and independently operated seller, provider, logistics, and
buyer Agents meet across service boundaries.

```text
Principal A -> Buyer Agent <-> Seller Agent <- Principal B
```

In that environment, software can reduce some search, comparison, formatting,
and coordination costs that made earlier open or federated commerce systems
difficult to use. An Agent may discover providers, compare structured terms,
apply a bounded mandate, request a counteroffer, or escalate an exception to its
principal.

That possibility motivated a narrower protocol question: when counterparties
do not share one internal database, what signed evidence lets them inspect
delegation, offer conditions, approval, withdrawal, conflict, challenge,
adjudication, and current standing under declared rules?

## 2. Topology Is an Application Choice

Agent-mediated commerce could be built through:

- a closed marketplace or super-app;
- merchant-owned endpoints coordinated by a platform;
- a federated or community-operated directory;
- an open index or decentralized discovery mechanism; or
- direct contact with a previously known counterparty.

ARC selects none of these. Discovery, transport, availability, ranking,
payments, fulfillment, and customer support remain application infrastructure.
The topology choices are illustrated in
[Discovery Topology](../diagrams/discovery-topology.md).

## 3. What Agents May Change

Agents may lower the human effort required to:

- publish and compare structured offers;
- maintain multiple service integrations;
- enforce a principal's budget and condition constraints;
- negotiate routine variations within delegated authority;
- retain transaction evidence and surface anomalies; and
- recompute a local view instead of accepting one platform's cached label.

These are feasibility hypotheses, not adoption forecasts. Lower interface cost
does not create liquidity, trustworthy counterparties, sustainable operators,
or a reason for independent systems to interoperate.

## 4. What Agents and ARC Do Not Solve

Neither Agent automation nor ARC by itself solves:

- customer and merchant acquisition;
- liquidity and network effects;
- inventory, pricing, tax, logistics, refunds, or customer support;
- fraud, Sybil identities, collusion, retaliation, or selective disclosure;
- identity roots, credential custody, privacy, and regulatory compliance;
- governance legitimacy, appeals, chargebacks, or legal enforcement;
- durable transaction atomicity, reconciliation, or production operations; or
- sustainable marketplace, registry, federation, or infrastructure economics.

A signed Event proves only what its declared verification boundary supports. It
does not prove that an offer was truthful, goods were delivered, a payment
settled, or an adjudicator had legal authority.

## 5. Relationship to Current Standards

Current systems cover substantial parts of the operational flow. A2A and FIPA
cover Agent interaction patterns; ACP and UCP cover commerce state; AP2 covers
important buyer mandate and payment-authorization semantics; OAuth/IAM and
policy engines enforce access; credentials and payment-network mechanisms help
establish identity and transaction trust.

ARC's remaining research focus is not to replace those systems. It is the
combined bilateral signed history of authority and counterparty claims,
preservation of unresolved causal conflict, and reproducible Current Coverage
or Current Standing under a declared Event set, profile, ordering context, and
`as_of` value. See [Landscape and Positioning](./landscape-and-positioning.md).

## 6. Implementation Neutrality

An ARC-aware application may use an ordinary database, append-only log, message
stream, federated service, shared ledger, or another storage and exchange model.
No topology gains legitimacy merely by using cryptography or decentralization.
Each implementation must disclose its trust roots, observer surface,
completeness assumptions, enforcement boundary, and failure modes.

## 7. Current Status

The repository contains an executable Commerce reference corpus, not a deployed
marketplace or proof of adoption. Broad Agent-to-Agent commerce is still
pre-market. That limits claims about inevitability and commercial demand; it
does not negate the value of preserving an executable protocol reference for an
emerging multi-principal problem.

# ARC Commerce Interaction Profile

> **Status:** Named, non-normative application profile
> **Purpose:** Explain how a Buyer Agent and Seller Agent interaction can use
> ARC signed evidence without turning application messages into Canon Events.

This document does not add to or modify the ARC Canon. The five Event types
remain `KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`, and `ADJUDICATE`.

## 1. Scope

The profile considers independently represented counterparties:

```text
Principal A -> Buyer Agent <-> Seller Agent <- Principal B
```

It covers the application boundary among bounded delegation, offer evidence,
exact approval, withdrawal, conflict, transaction/outcome claims, challenge,
adjudication, and recomputation.

It does not standardize:

- discovery or Agent transport;
- the complete product/offer ontology;
- checkout, order, payment, settlement, or fulfillment APIs;
- identity roots or complete seller authority;
- a universal reputation policy;
- a governance institution or real enforcement.

## 2. Roles

### Principal A / Buyer Principal

Defines intent, budget, constraints, and the authority granted to Buyer Agent.
May issue a scoped mandate, exact approval, or withdrawal.

### Buyer Agent

Discovers or contacts counterparties, requests and compares terms, checks the
current buyer-side authority result, counters or refuses within policy, and
escalates when fresh principal approval is required.

### Principal B / Seller Principal

Owns the business or service policy under which Seller Agent operates. ARC does
not assume that every internal seller rule is exposed as portable evidence.

### Seller Agent

Provides attributable terms and may counter, refuse, accept, or escalate under
seller-side inventory, price, delivery, cancellation, and authority constraints.

### External systems

Discovery providers, identity/credential issuers, checkout/order services,
payment providers, logistics systems, and dispute institutions retain their own
state and authority.

## 3. Example Scenario

Buyer Principal authorizes one meal purchase when:

- total is no more than KRW 20,000;
- the selected application quality view is at least 4.5;
- delivery is no more than 40 minutes; and
- the action occurs before the mandate expires.

Seller Agent proposes an available meal at KRW 21,000 with 30-minute delivery.
Buyer Agent may counter at KRW 20,000. Seller Agent may accept within delegated
discount authority, refuse, or escalate to Principal B. If accepted terms are
not covered by Buyer Agent's current mandate, Buyer Agent escalates the exact
offer to Principal A.

The example shows authority/application behavior. A quality view is a
contextual application Projection, not an objective ARC score.

## 4. Interaction Sequence

```text
1. discover or contact counterparty                     external
2. exchange capabilities                               transport/application
3. request offer                                       transport/application
4. proposal / counterproposal / refusal                transport/application
5. attributable final offer                            optional ATTEST
6. buyer mandate check or exact approval               AUTHORIZE + Projection
7. acceptance and checkout                             application/external
8. payment and fulfillment                             external
9. outcome claims                                      optional ATTEST
10. withdrawal or dispute                              existing Event/nullifies or CHALLENGE
11. recognized decision                                ADJUDICATE
12. current authority/standing recomputation           named Projection
```

FIPA interaction protocols, A2A, ACP, UCP, AP2, HTTP APIs, or other systems may
carry steps 1–9. ARC neither replaces nor requires a particular one.

## 5. Application Messages Are Not Canon Events

| Application message | Purpose | Stored as an ARC Event? |
| --- | --- | --- |
| `discovery_query` / result | find a counterparty | no, unless a relevant claim is separately attested |
| `capabilities` | advertise supported operations | no by default |
| `offer_request` | request terms | no by default |
| `proposal` / `counterproposal` | negotiate terms | no by default; a material attributable offer may be `ATTEST` |
| `refuse` / `reject` | decline terms | no by default |
| `accept` | application commitment | no by itself; authority coverage and checkout state remain separate |
| `checkout` / `payment` | create or execute commerce state | external protocol/state |
| `fulfillment_update` | claim delivery/service status | may be `ATTEST`, but remains an external-world claim |
| `cancel` | cancel application state | external; a signed offer/mandate withdrawal may also use `nullifies` |

The profile follows “extend by predicate, not by type.” It does not introduce
`OFFER`, `ACCEPT`, `WITHDRAW`, `PAYMENT`, or `RECEIPT` Event types.

## 6. ARC Record Mapping

| Meaning | Canon representation | Limits |
| --- | --- | --- |
| key registration/rotation/revocation | `KEY` with declared predicate and lifecycle references | verification profile and trust root remain external |
| attributable final offer | `ATTEST commerce.offer` | does not prove inventory, seller authority, or truth |
| contextual outcome/fulfillment/payment claim | `ATTEST commerce.*` or `rep.*` | signature is not external-world proof |
| buyer mandate/delegation | `AUTHORIZE consent.mandate` | chain must narrow and be current under the profile |
| exact approval | `AUTHORIZE consent.approval` | bound to exact application-defined material |
| withdrawal | existing Event predicate plus `nullifies` | author/lineage and causal/profile rules govern effect |
| dispute | `CHALLENGE` referencing relevant records | records a contest, not a verdict |
| recognized resolution | `ADJUDICATE` referencing challenge/evidence | authority is profile-relative; enforcement is external |

## 7. Authority Evaluation

Before an ARC-aware application relies on a buyer mandate or exact approval, it
declares:

- the exact action/request material;
- principal, delegate, and counterparty bindings required by the profile;
- Event set and snapshot identity;
- profile/version and scope interpretation;
- causal ordering and `as_of`;
- signature/security results; and
- evidence-completeness requirements, if any.

Possible bounded outcomes include covered by current mandate, covered by exact
approval, not covered, expired, withdrawn, invalid/unsupported evidence, or
`CONTESTED`.

Reference Core reports authority/evidence results. It does not decide whether
the application should transact. A Gate or application policy maps the result,
offer terms, risk, and external state to a local decision.

## 8. Exact Binding and Mutation

An exact approval covers only the unchanged material the application presented
for review. Price, item, quantity, seller, delivery, cancellation terms,
beneficiary, currency, or another declared material field cannot be silently
changed and reused under the old approval.

A scoped mandate covers only actions within its declared constraints. A
delegate may narrow scope but may not widen the authority it received.

Approval consumption, checkout idempotency, and atomic side-effect dispatch are
application/enforcement concerns. They are not stored Current Coverage status.

## 9. Expiry, Withdrawal, Cancellation, and Retry

- Offer expiry is application/offer evidence and does not itself revoke a
  principal mandate.
- Authority expiry is evaluated at an explicit `as_of` boundary.
- A causal authorized withdrawal can end future coverage without deleting past
  evidence.
- Concurrent or insufficiently ordered authorization/withdrawal may remain
  `CONTESTED` under the profile.
- Checkout cancellation, transport retry, and dead-letter handling remain in
  the external application protocol.
- A fresh application attempt must not reuse a stale Projection identity or
  exact approval for different action material.

## 10. Outcome, Reputation, and Dispute

Payment providers, merchants, logistics systems, and Agents may emit
attributable claims. A named contextual reputation/standing Projection may read
those claims together with missing, challenged, or adjudicated evidence.

No universal score is defined. Sybil identities, collusion, selective omission,
retaliation, privacy, and external truth remain open application risks.

A `CHALLENGE` may reference a transaction, claim, or earlier adjudication. A
profile-recognized `ADJUDICATE` may change a current Projection. Refund,
chargeback, suspension, appeal rights, contractual remedy, and legal
enforcement remain external.

## 11. Interoperability Boundary

The current profile is executable research, not a finalized wire/security
standard. Independent interoperability would require at least:

- normative serialization, hashing, and signature profiles;
- predicate and scope schemas;
- profile/version negotiation;
- error semantics and conformance vectors;
- evidence acquisition/completeness rules; and
- two independent implementations producing compatible results.

These gaps are tracked in
[Unresolved Specification and Conformance Boundaries](./future-protocol-spec.md).

## 12. Status

The Commerce profile is the motivating application and an executable reference,
not merely obsolete history. The operational transaction can be assembled from
current standards, while the combined bilateral causal authority/standing and
Event-set/profile/as-of recomputation model remains a material semantic gap.

Broad adoption is pre-market. That limits necessity and production claims, not
continued research or the public technical value of this profile.

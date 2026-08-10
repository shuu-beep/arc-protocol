# Why ARC?

> ARC is not justified by the claim that existing authorization is weak or that
> every Agent system needs another permission layer. Its testable question is
> whether independently represented principals need a common signed model for
> causal authority, conflict, and standing that current operational standards
> do not provide together.

## 1. Two Agents, Two Principals

```text
Principal A -> Buyer Agent <-> Seller Agent <- Principal B
```

The Buyer Agent may have authority to purchase one qualifying item under a
budget and deadline. The Seller Agent may make offers only within its own price,
inventory, delivery, and cancellation constraints. During the interaction they
may propose, counter, refuse, accept, or escalate.

Transport authentication can identify the key or service that sent a message.
Application policy can decide whether one request is allowed. Checkout and
payment systems can create and settle a transaction. None of those facts alone
answers the full cross-party question:

> From which declared signed evidence does each party derive the other Agent's
> current authority or standing after delegation, expiry, withdrawal,
> conflicting claims, challenge, or adjudication?

## 2. ARC's Answer

ARC represents authority-relevant history with five signed Event types and
derives current results through named Projections.

```text
KEY / ATTEST / AUTHORIZE / CHALLENGE / ADJUDICATE
                         |
                         v
Event set + profile + ordering + verification + as_of
                         |
                         v
          Current Coverage / Current Standing
```

The model preserves:

- delegation lineage and narrowing;
- exact action/offer binding;
- validity intervals and causal withdrawal;
- unresolved `CONTESTED` results;
- challenge and profile-recognized adjudication records; and
- reproducible Event-set/profile/as-of computation identity.

ARC does not make the records complete or true. The receiver still selects its
trust roots, evidence sources, authority profile, application policy, and real
enforcement systems.

## 3. Strongest Existing Alternatives

| System | What it already provides | Honest relationship to ARC |
| --- | --- | --- |
| A2A | Agent discovery, Agent Cards, messages, tasks, artifacts, asynchronous interaction | Strong transport/interoperability layer; principal authority lineage and standing remain external |
| FIPA interaction protocols | Proposal, counter-rounds, refusal, deadlines, acceptance, binding commitment, completion/failure | Direct overlap with Commerce negotiation; does not prove principal delegation or recompute cross-party standing |
| ACP and UCP | Checkout, order, fulfillment, cancellation, merchant/business state, protocol capability negotiation | Own operational commerce state; capability negotiation is not general price/condition bargaining |
| AP2 | User-to-Agent mandate delegation, constraints, exact transaction binding, expiry, verifier checking, signed receipts, autonomous-use controls | Direct overlap with buyer authorization; Agent-to-Agent redelegation and bilateral conflict/standing history are not current AP2 semantics |
| MCP authorization, OAuth, RFC 8693, IAM, policy engines | Authentication, token exchange, actor context, scope, current policy evaluation, target enforcement | Often sufficient inside one accepted authority domain; causal portable history and explicit unresolved standing are not default outputs |
| VC/OpenID4VP, UCP profiles, Visa TAP, payment-network Agent trust | Portable claims, presentation binding, Agent/merchant recognition, payment context | Useful evidence and trust roots; not a negotiation, reputation, or adjudication system |
| Application, marketplace, payment, and dispute state | Idempotency, transaction lifecycle, fulfillment, refunds, chargebacks, real remedies | Required external systems; can implement extra ARC-like semantics with custom state and logic |

ARC must not claim that delegation, exact approval, expiry, transaction binding,
receipts, or replay controls are generally unique. AP2 in particular provides a
substantial native buyer-authorization chain for Agent commerce.

See [Landscape and Positioning](./landscape-and-positioning.md) for the
official-source comparison.

## 4. The Residual Semantic Gap

The practical transaction can be assembled from current standards. The
reviewed combination does not natively provide one shared model that combines:

1. **bilateral signed causal history** for authority and counterparty claims;
2. **symmetric multi-principal applicability** beyond one buyer/payment path;
3. **unresolved `CONTESTED` preservation** rather than an implicit winner or
   current Boolean;
4. **causal withdrawal, challenge, and authorized adjudication** in the same
   history; and
5. **Event-set/profile/as-of recomputation** of Current Coverage and Current
   Standing.

This is a **material semantic gap**, not merely cleaner packaging. An
application can fill it, but must then build a custom signed-event,
causal-ordering, conflict, and recomputation layer with essentially the same
responsibilities.

## 5. What the Current Repositories Prove

ARC Protocol's 14 offline probes demonstrate authored behavior for the five
Event types, delegation, withdrawal, conflict, adjudication, federation,
fidelity seams, and the Commerce failure catalog.

ARC Reference Core is a bounded, non-normative executable reference for
authority/evidence validation and Current Coverage Projection. ARC Execution
Gate demonstrates optional application policy and simulated pre-dispatch
handling. The current Core/Gate integration preserves `CONTESTED`, rejects stale
or substituted decisions, and exercises process-local replay controls.

These artifacts establish an executable semantic reference. They do not prove:

- a complete seller-side delegation chain;
- independent wire/profile interoperability;
- identity roots or evidence completeness;
- production credential isolation or direct-path closure;
- durable atomic consumption or target idempotency;
- payment, fulfillment, legal truth, or dispute enforcement; or
- broad adoption or commercial necessity.

The last point limits market claims, not the technical existence or research
value of the semantic model.

## 6. When ARC Is Unnecessary

ARC may add little value when:

- one trusted marketplace, IAM service, or database is the accepted complete
  source of current authority and standing;
- no authority or standing evidence crosses implementation boundaries;
- causal history, unresolved conflict, and as-of recomputation are not required;
- AP2 plus checkout/payment state fully covers the consequential buyer action;
- a receiver needs only current policy enforcement, not portable evidence; or
- the cost of maintaining profiles, evidence, and recomputation exceeds the
  value of the additional audit semantics.

In those settings, native Agent controls, OAuth/IAM, policy engines, gateways,
and ordinary application state are the simpler choice.

## 7. Maturity and Market Status

The multi-principal semantic gap is supported by the current comparison and ARC
has an executable reference model for it. Broad Agent-to-Agent commerce
necessity remains **pre-market / not yet testable**.

Market demand is not a prerequisite for maintaining or developing ARC as
protocol research, an executable reference, or a public technical profile. It
is required before claiming inevitable adoption, commercial necessity,
production readiness, or ecosystem interoperability.

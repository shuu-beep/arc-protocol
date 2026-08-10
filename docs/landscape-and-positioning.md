# ARC Protocol: Current Landscape and Positioning

> **Status:** Non-normative comparison, verified against official/primary
> sources as of 2026-08.
> **Purpose:** Distinguish operational composability from semantic equivalence
> and separate technical difference from market adoption.

## 1. Fixed Comparison Scenario

```text
Principal A
  -> bounded delegation
Buyer Agent
  <-> Seller Agent
  <- bounded seller-side authority/application constraints
Principal B
```

The Buyer Agent may buy one qualifying item for no more than KRW 20,000 under
quality and delivery constraints. The Seller Agent may propose price,
configuration, availability, delivery, and cancellation terms. The Agents may
discover, propose, counter, refuse, accept, escalate, transact, report outcomes,
withdraw authority, and dispute claims.

This comparison does not assume that ARC proves the Seller Agent's complete
internal delegation chain. It compares the semantics and boundaries actually
documented or exercised.

## 2. Layer Map

| Layer | Examples | Primary responsibility |
| --- | --- | --- |
| Discovery and Agent transport | A2A, UCP profiles, FIPA broker, marketplace directories, HTTP | find and communicate with a counterparty |
| Negotiation/application messages | FIPA Contract Net/Iterated Contract Net, A2A messages, application ontology | proposal, counter-round, refusal, acceptance, deadline |
| Commerce state | ACP, UCP, seller/order systems | checkout, inventory, order, fulfillment, cancellation |
| Buyer authorization and payment evidence | AP2, payment credentials/providers | mandate, exact transaction binding, verifier receipt, payment context |
| Identity and access | OAuth/OIDC, RFC 8693, IAM, VC/OpenID4VP, Agent/merchant trust protocols | authenticate, delegate, present credentials, enforce current access |
| Real transaction and remedy | payment rails, merchant systems, logistics, marketplaces, contracts, regulators, courts | settle, fulfill, refund, charge back, enforce |
| ARC research layer | signed Events and named Projections | causal authority/standing history, conflict preservation, recomputation |

No single layer proves the claims owned by the next one.

## 3. Standards and Direct Comparators

### A2A

[A2A](https://a2a-protocol.org/latest/) defines Agent Cards, capability and
authentication advertisement, messages, tasks, artifacts, streaming,
asynchronous operation, cancellation, rejection, and failure handling.

- **Provides:** Agent discovery and interoperable task/message transport.
- **Overlaps:** attributable Agent capability claims and multi-turn interaction.
- **External:** principal mandate, commercial commitment, payment, reputation,
  adjudication, and target enforcement.
- **Residual:** no common bilateral causal authority/standing Projection.

### FIPA interaction protocols

The [FIPA Contract Net](https://www.fipa.org/specs/fipa00029/SC00029H.html)
defines calls for proposals, proposal preconditions such as price/time, refusal,
reply deadlines, acceptance/rejection, binding commitment after acceptance,
completion, and failure. The
[Iterated Contract Net](https://www.fipa.org/specs/fipa00030/SC00030H.pdf)
supports revised rounds, and the
[Brokering Interaction Protocol](https://www.fipa.org/specs/fipa00033/SC00033H.html)
is relevant to mediated discovery.

- **Provides:** the strongest direct interaction-pattern overlap with ARC's
  Commerce proposal/counter/refusal/acceptance flow.
- **External:** principal delegation, exact authorization, identity roots,
  reputation, dispute authority, and enforcement.
- **Residual:** interaction commitment is not a recomputed authority or standing
  history.

### Agentic Commerce Protocol (ACP)

[ACP](https://www.agenticcommerce.dev/docs) keeps the seller merchant of record
and covers checkout creation/update/completion/cancellation, fulfillment
selection, seller-calculated totals, and delegated payment tokens with amount,
currency, merchant, and expiry constraints.

- **Provides:** Agent-to-seller checkout and constrained payment operations.
- **Overlaps:** exact transaction material, expiry, cancellation, escalation,
  and idempotent application behavior.
- **External:** general bargaining, bilateral principal authority, portable
  contextual standing, and adjudication.

### Universal Commerce Protocol (UCP)

[UCP](https://ucp.dev/2026-04-08/specification/overview/) defines business
profiles at `/.well-known/ucp`, version/capability negotiation, signing keys,
REST/MCP/A2A bindings, checkout, order, fulfillment, adjustments, and identity
linking. The business remains authoritative for commerce state.

- **Provides:** discovery, capability intersection, signed profiles/messages,
  and rich commerce lifecycle state.
- **Overlaps:** counterparty identification, checkout binding, order/fulfillment
  evidence, and transaction receipts.
- **External:** principal mandate semantics, open-ended price negotiation,
  contextual reputation, causal conflict, and adjudication.

UCP capability negotiation selects mutually supported protocol features; it is
not a generic offer/counteroffer bargaining protocol.

### Agent Payments Protocol (AP2)

Current [AP2 Agent Authorization](https://ap2-protocol.org/ap2/agent_authorization/)
defines user-to-Agent mandate delegation on a Trusted Surface, User Credential
and Trusted Agent Provider trust models, open and closed mandates, constraints,
proof-of-possession transaction binding, verifier checks, and signed Mandate
Receipts. It requires the provider signing key to remain inaccessible to the
Agent outside the Trusted Surface.

The [AP2 payment specification](https://ap2-protocol.org/ap2/specification/)
binds checkout/payment mandates and receipts. In autonomous flows, an Agent must
not present another open mandate without a rejection receipt from the prior
attempt. The documents treat the mandate/receipt bundle as dispute evidence.

- **Provides:** substantial native buyer delegation, exact binding, expiry,
  constraint validation, receipts, and reuse reduction.
- **Overlaps:** many earlier ARC buyer-authorization and payment-evidence claims.
- **External:** dispute resolution/enforcement, evidence retrieval/retention,
  contextual reputation, and Seller Principal delegation.
- **Residual:** Agent-to-Agent mandate delegation is outside the current AP2
  scope; AP2 does not preserve ARC's bilateral `CONTESTED`/adjudication/as-of
  standing model.

ARC must not claim generic delegation, exact approval, expiry, transaction
binding, receipts, or replay control as unique in Agent commerce.

### MCP authorization

[MCP authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
uses OAuth-style protected-resource authorization and resource indicators to
bind tokens to the intended MCP server.

- **Provides:** authorization for client-to-tool-server access.
- **Overlaps:** current access enforcement and audience/resource binding.
- **External:** Agent-to-Agent bargaining, transaction state, reputation,
  challenge/adjudication, and causal standing history.

### OAuth, RFC 8693, IAM, and policy engines

[RFC 8693](https://www.rfc-editor.org/info/rfc8693) supports token exchange,
delegation/impersonation context, actor chains, scopes, and time bounds. OAuth,
OIDC, IAM, gateways, and Cedar/OPA/OpenFGA-class policy systems can evaluate and
enforce subject/action/resource/context rules.

- **Provides:** mature identity, delegation, current policy, and target-side
  enforcement within accepted authority domains.
- **Overlaps:** scope narrowing, expiry, revocation, exact input conditions, and
  allow/deny behavior.
- **External:** one portable causal Event history, unresolved authority/standing
  conflict, and profile/as-of Projection identity unless custom-built.

If one IAM/PDP is the accepted complete source of truth, ARC may be unnecessary.

### Verifiable Credentials and OpenID4VP

[W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/)
provides portable signed claim containers. The
[Bitstring Status List](https://www.w3.org/TR/vc-bitstring-status-list/) supports
credential suspension/revocation status, and
[OpenID4VP](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)
binds presentations to verifier requests, nonces, and transaction data.

- **Provides:** credential issuance/presentation building blocks and status.
- **Overlaps:** identity, principal/Agent binding evidence, selective disclosure,
  and replay-resistant presentation context.
- **External:** negotiation, transaction lifecycle, contextual reputation,
  causal authority conflict, and adjudication.

### Merchant and payment Agent trust

[Visa Trusted Agent Protocol](https://developer.visa.com/capabilities/trusted-agent-protocol/trusted-agent-protocol-specifications/)
helps merchants recognize certified Agents, link consumer/device identity,
verify signed payment context, and reject replay using timestamps/nonces.

Mastercard's official
[Verifiable Intent](https://www.mastercard.com/europe/en/news-and-trends/stories/2026/verifiable-intent.html)
and [Agent Pay](https://www.mastercard.com/us/en/news-and-trends/press/2026/june/mastercard-launches-agent-pay-for-machines.html)
materials describe Agent credentialing, permissioning, spend rules, and payment
network participation. The public materials are product/intent descriptions,
not a general bilateral authority-history specification.

- **Provides:** merchant/payment trust and constrained payment context.
- **External:** negotiation, portable reputation, causal challenge/adjudication,
  and general Current Standing recomputation.

### ERC-8004 and ERC-8183

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) proposes Agent identity,
reputation, and validation registries. Feedback remains contextual and does not
by itself solve Sybil behavior, authority conflict, or adjudication.

[ERC-8183](https://eips.ethereum.org/EIPS/eip-8183) is a draft Agentic Commerce
escrow protocol with client/provider/evaluator roles, budget setting, funding,
submission, completion/rejection, expiry/refund, deliverable hashes, and
external reputation hooks. It explicitly has no dispute resolution or
arbitration and trusts its evaluator for completion/rejection.

- **Provides:** direct overlap in Agent identity/reputation records and
  transaction commitment/fulfillment state.
- **External:** principal delegation, bilateral causal authority history,
  independent adjudication, and off-chain real-world truth.
- **Topology note:** ARC does not require a blockchain or shared ledger.

## 4. Semantic Summary

`FULL` means the referenced system natively covers the main row within its
documented role; `PARTIAL` means a bounded subset; `EXTERNAL` means another
layer owns it; `NOT COVERED` means the semantics are absent.

| Semantic group | ARC | Strongest current alternatives |
| --- | --- | --- |
| Discovery and transport | EXTERNAL | A2A/UCP/FIPA: FULL |
| Proposal, counter, refusal, acceptance | PARTIAL application profile | FIPA: FULL; A2A: transport support |
| Principal-to-Agent delegation and narrowing | FULL reference semantics | AP2/OAuth/IAM: FULL in their domains |
| Exact approval, expiry, transaction binding | FULL reference semantics | AP2: FULL for Agent payment authorization; ACP/UCP: commerce binding |
| Replay/one-time controls | PARTIAL, process-local Gate example | AP2/ACP/application state: FULL or bounded by profile |
| Payment and target enforcement | EXTERNAL | payment providers/IAM/merchant systems: FULL |
| Fulfillment and transaction receipts | PARTIAL evidence model | ACP/UCP/AP2/application systems: FULL in their domains |
| Identity evidence | PARTIAL | VC/OpenID4VP/UCP/Visa TAP/OAuth: stronger native layers |
| Contextual reputation and Sybil/collusion limits | FULL bounded research Projection; no universal truth | marketplace/app state/ERC-8004: partial/external |
| Conflicting claims and `CONTESTED` | FULL | policy/app state: custom/partial |
| Causal withdrawal/challenge/adjudication | FULL reference semantics | distributed across auth, dispute, and application systems |
| Event-set/profile/as-of Current Standing | FULL reference semantics | custom application history/recomputation required |
| Real dispute enforcement | EXTERNAL | payment, marketplace, contractual, regulatory, and court systems |
| Independent interoperability | PARTIAL/unproved | mature standards stronger |

## 5. Composition Test

The operational transaction is composable without ARC:

```text
A2A or FIPA
  + ACP/UCP
  + AP2
  + credentials/OAuth/IAM
  + marketplace/application state
  + payment/fulfillment/dispute infrastructure
```

That composition can discover counterparties, exchange terms, authorize a
buyer action, create checkout/payment state, fulfill, and apply real remedies.

It does not natively reproduce ARC's combined bilateral signed authority and
standing history, unresolved causal conflict, challenge/adjudication, and
Event-set/profile/as-of recomputation. Adding those properties requires custom
state, Event, causal-ordering, and Projection logic.

**Result: MATERIAL SEMANTIC GAP REMAINS.**

The result is not “ARC is required.” It means the residual is a real semantic
property rather than convenience or naming. A deployment may still decide that
the property is unnecessary or cheaper to implement locally.

## 6. Market and Research Status

Broad Agent-to-Agent commerce necessity is **pre-market / not yet testable**.
No current comparison proves inevitable adoption, commercial necessity,
production readiness, or an ecosystem requirement for ARC.

That market result is independent from the technical result. Market demand is
not a prerequisite for maintaining or developing ARC as research protocol, an
executable reference, or a public technical profile.

## 7. Positioning

ARC should be described as:

> An implementation-neutral research protocol and executable reference for
> signed causal authority and standing evidence across independently
> represented principals.

It should not be described as the missing universal layer, a required commerce
standard, a superior permission system, a marketplace, a payment network, an
identity provider, or a production enforcement gateway.

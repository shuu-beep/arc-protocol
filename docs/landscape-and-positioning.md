# ARC Protocol: Landscape and Positioning

> **Status:** Exploratory positioning note
>
> **Purpose:** Locate ARC among the agent and commerce systems emerging in 2026 — beginning with what ARC is *not* — so external readers do not mistake it for a tool-use layer, an agent-interop layer, a checkout standard, a marketplace, a payment network, or a blockchain protocol.
>
> This is positioning, not comparison-for-advantage. ARC does not claim to replace or outperform any system named here. Descriptions of external systems reflect ARC's current understanding and may be imprecise or out of date; they are not authoritative and may change.
>
> For motivation, see [philosophy.md](./philosophy.md). For what ARC stores and computes, see [object-model.md](./object-model.md) and [event-registry.md](./event-registry.md). For authority boundaries, see [authority-and-conflict.md](./authority-and-conflict.md). For what remains unspecified, see [future-protocol-spec.md](./future-protocol-spec.md).

---

## 1. Why This Document Exists

Agent commerce in 2026 is not a single product but a layered stack of standards, and ARC is easy to misfile. A reader meeting ARC for the first time may reasonably assume it is "another checkout protocol," "another agent framework," or "an on-chain trust registry." It is none of those.

The clearest way to describe a narrow layer is to say which layers it is not. This document therefore locates ARC by contrast first, then states the small thing it actually tries to be.

It also makes the surrounding landscape explicit. Earlier ARC documents referred only to "multiple organizations exploring agent commerce" without naming anyone (see [future-protocol-spec.md](./future-protocol-spec.md) §1). Naming the neighboring systems is not a competitive move; it is so a reader can place ARC correctly.

## 2. What ARC Is

ARC is, as currently understood:

- **A human-approved commerce coordination layer** — a way for agents to negotiate and prepare commerce while humans keep final approval, and while identity, reputation, dispute, and governance records remain inspectable.
- **An agent-mediated commerce protocol exploration** — not a finished protocol but a design exploration of the records, approvals, and boundaries such commerce would need (see [future-protocol-spec.md](./future-protocol-spec.md)).

In Canon terms ([object-model.md](./object-model.md), [authority-and-conflict.md](./authority-and-conflict.md)), ARC reasons over signed **Events**, computes relationships and reputation as on-demand **Projections**, and locates final authority with humans (over their own action) and communities (over the commons) — never with an algorithm. Trust in ARC is governed and projected, not stored as a universal score.

ARC's intended stance is an **overlay, not a replacement**: anti-dependency, not anti-company. It is most useful if the other layers below thrive.

## 3. What ARC Is Not

ARC is not:

- a tool-use / capability layer (compare MCP, §4)
- an agent-to-agent interop or transport layer (compare A2A, §5)
- a checkout or commerce-semantics standard (compare ACP, §6)
- a marketplace or platform operator (§7)
- a payment network, wallet, or settlement rail (§8)
- a blockchain protocol or on-chain registry (§9)

Consistent with the rest of the corpus, ARC is also not a full-autonomy framework — human approval is a hard constraint, not a removable feature ([philosophy.md](./philosophy.md), [roadmap.md](./roadmap.md)) — and not a token project ([roadmap.md](./roadmap.md)).

## 4. ARC vs MCP

MCP standardizes how an agent connects to external tools and data sources — a capability and transport concern: how an agent reaches a calendar, a database, or a service.

ARC does not define tool connection. It assumes agents can already act, and asks a different question: what records, approvals, and trust boundaries a *commerce interaction between parties* needs.

These are different layers. An ARC-compatible agent could use MCP to reach its tools; nothing in ARC competes with that.

## 5. ARC vs A2A

A2A standardizes how independent vendor agents discover and delegate to one another — an interoperability and communication concern: how agents talk.

ARC is not a general agent-interop transport. It concerns the narrower *human-approved commerce* subset — signed offers, approval, reputation, dispute, governance. ARC could ride on an A2A-style transport, or on others; it does not specify the transport.

Different problem, not a rival: A2A asks "how do agents communicate?"; ARC asks "what must be recorded, and who approves, when agents transact on a human's behalf?"

## 6. ARC vs Commerce Checkout Standards

Commerce checkout standards — ACP and similar approaches — define product discovery, cart, and checkout so an agent can complete a purchase, often with merchant-owned checkout and a scoped payment token.

ARC does not define checkout semantics and does not execute purchases. It is the approval and trust overlay *around* such a transaction: was current, unexpired terms approved by a human; what does the merchant's reputation projection look like; how is a dispute recorded.

These can compose rather than collide. A plausible sequence is: ARC approval → checkout execution via a commerce standard → an ARC reputation event recorded afterward.

## 7. ARC vs Marketplace

A marketplace aggregates buyers and sellers and operates discovery, ranking, fees, support, and dispute resolution under a single operator. Marketplaces provide real value — demand aggregation, trust signals, support, fraud handling — and ARC does not deny this ([bootstrap-and-incentives.md](./bootstrap-and-incentives.md) §3).

ARC is not a platform operator and runs no marketplace. It explores open, replaceable discovery backends and community governance instead of a single operator, and it provides no built-in demand and guarantees no participation ([bootstrap-and-incentives.md](./bootstrap-and-incentives.md)).

This is a structural difference, not a claim of superiority. In many respects ARC offers *less* than a mature marketplace. The open question ARC raises is whether some coordination functions can be made inspectable, portable, and less concentrated — not whether marketplaces should go away.

## 8. ARC vs Payment Network

Payment networks, wallets, and settlement rails move money. ARC does not ([architecture.md](./architecture.md) §4.2, [liability-boundaries.md](./liability-boundaries.md)). ARC is payment-provider-agnostic and region-adaptive.

In Canon terms, a confirmed payment enters ARC only as an `ATTEST` about an external transfer ([event-registry.md](./event-registry.md)): ARC records the claim, it does not settle the funds.

So ARC depends on payment networks rather than competing with them. Payment execution stays with the provider, and only after human approval.

## 9. ARC vs Blockchain Protocol

Blockchain protocols provide shared, manipulation-resistant ledgers and consensus. Some target agent trust directly, for example on-chain identity and reputation registries.

ARC is DB-first and blockchain-minimal ([philosophy.md](./philosophy.md) belief 5, [architecture.md](./architecture.md) §1.1): a chain is optional, used only for checkpoints where shared manipulation-resistance is worth the added cost. ARC stores signed Events and computes trust as a Projection on demand, rather than placing a global score or persistent profile on a shared ledger ([object-model.md](./object-model.md)).

This is a design difference, not a verdict. Where some systems bet that trust can be *computed* on shared infrastructure, ARC explores trust as *governed* — a community process over evidence, with no stored universal score. "Computed" and "governed" are used here only as positioning language, not as ARC protocol primitives. Both bets are unproven, and ARC does not claim its choice is the better one.

## 10. Why These Systems Can Coexist

The systems above mostly occupy different layers:

| Layer | Example concern | ARC's relation |
| --- | --- | --- |
| Tool access | reaching tools and data (MCP) | ARC uses, does not define |
| Agent interop | agents discovering and delegating (A2A) | ARC may ride on, does not specify |
| Checkout semantics | discovery, cart, checkout (ACP) | ARC wraps with approval and trust records |
| Platform operation | aggregated marketplace | ARC explores an open alternative function |
| Settlement | moving money (payment networks) | ARC depends on, records as `ATTEST` |
| Shared ledger | manipulation-resistant records (blockchain) | ARC uses minimally, computes trust off-chain |

ARC occupies the human-approval and trust-coordination layer above commerce. A single transaction could plausibly use several of these at once — tools via MCP, agent contact via A2A-style transport, checkout via a commerce standard, settlement via a payment network — while ARC supplies the human-approval boundary and the inspectable identity, reputation, dispute, and governance records.

ARC's stance is overlay, not replacement. It is most useful when these other layers exist and work; it tries to add a missing layer, not substitute an existing one.

## 11. Current ARC Scope

ARC today is a Stage 0 documentation baseline plus a small mock artifact set, not a running system ([roadmap.md](./roadmap.md), [README](../README.md) §26). The Canon (Relationship → Event → Projection → Authority) and the canonical event set (`KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`, `ADJUDICATE`) are exploratory drafts, not an implemented protocol or a finalized wire format ([future-protocol-spec.md](./future-protocol-spec.md)).

In scope:

- human-approved commerce coordination
- identity, reputation, dispute, and governance expressed as signed events and projections
- failure analysis of the above

Out of scope:

- tool-connection standards, general agent transport, and checkout semantics
- marketplace operation and payment settlement
- on-chain execution and full autonomy

This positioning is a current orientation, not a fixed claim. As the external landscape changes, where ARC sits relative to it may need revisiting.

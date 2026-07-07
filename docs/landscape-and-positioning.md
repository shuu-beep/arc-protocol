# ARC Protocol: Landscape and Positioning

> **Status:** Exploratory positioning note
>
> **Purpose:** ARC is an open layer for human-approved delegation, portable authority, and recomputable audit; commerce is its first implementation, and therefore the arena where it must be told apart from its neighbors. This note locates ARC among the agent and commerce systems emerging in 2026 — beginning with what ARC is *not* — so external readers do not mistake it for a tool-use layer, an agent-interop layer, a checkout standard, a marketplace, a payment network, or a blockchain protocol.
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

ARC is, as currently understood, an open layer for three things ([README](../README.md)):

- **Human-approved delegation** — agents negotiate and prepare; the human holds the final signed step. Delegation is scoped and never self-widening.
- **Portable authority** — authority routes between agents and across communities without being minted by any single operator, and a community may honor another's or decline it.
- **Recomputable audit** — only signed events are stored; identity, reputation, dispute, and governance standing are recomputed from them on demand, never saved as a score.

Commerce is ARC's **first implementation, not its definition**, and the domain in which the comparisons below (§4–§11) are drawn — because that is where ARC first meets neighboring systems. A human-approved purchase folds to the same primitives as any other delegation: a merchant's offer is an `ATTEST`, the human's approval an `AUTHORIZE`, a dispute a `CHALLENGE`, a community ruling an `ADJUDICATE`. It remains an exploration, not a finished protocol ([future-protocol-spec.md](./future-protocol-spec.md)).

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

### 8.1 Agent-Native Monetization Gateways (x402)

A newer variant of the settlement layer deserves its own note, because it begins from the same observation ARC does. Cloudflare's **Monetization Gateway** (announced 2026-07-01, [blog.cloudflare.com/monetization-gateway](https://blog.cloudflare.com/monetization-gateway/)) is built on **x402**, an open protocol that revives the HTTP `402 Payment Required` status code: a server prices a request, the client pays in stablecoins, a facilitator verifies the payment, and the resource is delivered — per request, at sub-cent granularity, proxied at the edge. Agent identity is handled by a separate verification mechanism (Web Bot Auth), and the announcement explicitly anticipates agents that "carry wallets" and purchase autonomously.

The shared diagnosis is the closest problem-statement overlap in this document: **agents do not view ads and do not hold subscriptions**, so the human-attention business model of the web breaks under agent traffic. ARC's corpus starts from the same premise — an agent-first internet changes what the interaction record must carry ([philosophy.md](./philosophy.md)).

From that shared premise the two systems diverge into different layers:

- **x402 makes the request a transaction.** Its question is *how does an agent pay*, and its verification object is the payment: the facilitator confirms funds moved. ARC's question is *by what authority did the agent act*, and its verification object is the approval: can a third party recompute, from signed events alone, that the spend was inside a human-approved scope ([event-registry.md](./event-registry.md))?
- **A wallet-carrying agent is bearer authority.** Whoever holds the key can spend, and a valid payment proves key possession, not a faithful reading of the principal's intent — the same boundary ARC records for signatures generally ([key-custody.md](./key-custody.md)). ARC treats human approval as consent to a specific act, not a spendable token, which is exactly the distinction a per-request payment rail does not need and does not claim to make.
- **The trust root is inverted.** The gateway model concentrates verification in the facilitator and the edge operator; that is what makes it fast and cheap. ARC accepts slower, heavier verification in exchange for having no single verifier of last resort ([authority-and-conflict.md](./authority-and-conflict.md)).
- **Per-outcome pricing re-opens the record/referent boundary.** The announcement cites pricing "paid only when the work succeeds." Someone must attest that the work succeeded, and that attestation is a record about the world, not the world — the same wall ARC names for its own events ([event-registry.md](./event-registry.md) §2.4). A gateway must ultimately delegate that judgment to a trusted party; ARC records the disagreement instead of resolving it.

These layers compose rather than collide. An x402 payment enters ARC the same way any settlement does — as an `ATTEST` about an external transfer (§8 above) — and ARC's approval boundary is a natural answer to a question x402 leaves open: whether the agent presenting the payment was authorized by its principal to make it. Conversely, x402 is a plausible settlement rail *underneath* an ARC-approved purchase.

One asymmetry is worth stating plainly. A gateway operator ships this to an existing customer base with the flip of a switch; sellers already behind the edge have no reason to wait. That is the same structural head start §10 names for closed platforms, and the same adoption problem ARC cannot solve by description ([threat-model.md](./threat-model.md) §18.1). As elsewhere in this document, this description reflects ARC's current reading of a just-announced system and may be imprecise or out of date.

## 9. ARC vs Blockchain Protocol

Blockchain protocols provide shared, manipulation-resistant ledgers and consensus. Some target agent trust directly, for example on-chain identity and reputation registries.

ARC does not prescribe a storage backend and treats a chain as optional ([philosophy.md](./philosophy.md) belief 5, [architecture.md](./architecture.md) §1.1): a chain is used only for checkpoints where shared manipulation-resistance is worth the added cost. ARC stores signed Events and computes trust as a Projection on demand, rather than placing a global score or persistent profile on a shared ledger ([object-model.md](./object-model.md)).

This is a design difference, not a verdict. Where some systems bet that trust can be *computed* on shared infrastructure, ARC explores trust as *governed* — a community process over evidence, with no stored universal score. "Computed" and "governed" are used here only as positioning language, not as ARC protocol primitives. Both bets are unproven, and ARC does not claim its choice is the better one.

## 10. ARC vs Closed Agent Commerce

Sections §4–§9 contrast ARC with neighboring *layers* it composes with. This contrast is different in kind. A closed agent-commerce platform is not a layer ARC sits beside; it is an alternative way the whole stack could be organized. Both could exist, but they embody opposite bets about where coordination lives.

The likely shape is familiar: a large marketplace or super-app (an Amazon- or Coupang-style operator) extends into agent commerce by running the buyer's agent, discovery, ranking, advertising, and checkout as one closed loop. This is the agentic evolution of the marketplace contrast in §7, and it carries §7's real advantages further: demand is aggregated, fraud is handled centrally, the experience is convenient, and — crucially — adoption is immediate, because the operator already has the users, the merchants, and the payment relationship. In the FOMO-driven rush described in [bootstrap-and-incentives.md](./bootstrap-and-incentives.md), the closed path has the structural head start. ARC does not.

What such a structure concentrates is a real question, not a moral one. When the operator owns both the buyer's agent and the seller's storefront, the buyer's agent is also the seller's gatekeeper — a standing conflict of interest. The recurring tensions are:

| Closed agent commerce | ARC's contrasting bet |
| --- | --- |
| Opaque ranking under one operator | Replaceable, inspectable discovery backends (§7) |
| Operator-computed trust score | Governed trust — community process over evidence, no stored universal score (§9) |
| Captive merchants, hard to exit | Local portability of identity and reputation, with a known inter-community cost ([trust-model-tradeoffs.md](./trust-model-tradeoffs.md)) |
| Advertising blended into results | Disclosed sponsorship as a recorded event (`discovery-bias.json`; [event-registry.md](./event-registry.md)) |
| Operator-owned agent acts for the platform | Human approval as a hard constraint; the agent acts for its principal ([philosophy.md](./philosophy.md)) |

None of this is a claim that closed platforms are illegitimate or should disappear. They provide value many users will rationally prefer, and ARC has no demand to offer against theirs ([bootstrap-and-incentives.md](./bootstrap-and-incentives.md)). The honest position is that the closed path is the path of least resistance, and ARC's bet — that agent commerce can be coordinated so the buyer's agent is not owned by the seller's platform — is the harder, unproven one. Whether anyone adopts a more inspectable, less concentrated alternative when a frictionless closed one exists is the same open problem named in [threat-model.md](./threat-model.md) §18.1: ARC can describe the structure, but not manufacture the reasons to choose it.

## 11. Why These Systems Can Coexist

The layered systems in §4–§9 mostly occupy different layers:

| Layer | Example concern | ARC's relation |
| --- | --- | --- |
| Tool access | reaching tools and data (MCP) | ARC uses, does not define |
| Agent interop | agents discovering and delegating (A2A) | ARC may ride on, does not specify |
| Checkout semantics | discovery, cart, checkout (ACP) | ARC wraps with approval and trust records |
| Platform operation | aggregated marketplace | ARC explores an open alternative function |
| Settlement | moving money (payment networks, x402-style gateways §8.1) | ARC depends on, records as `ATTEST` |
| Shared ledger | manipulation-resistant records (blockchain) | ARC uses minimally, computes trust off-chain |

ARC occupies the human-approval and trust-coordination layer above commerce. A single transaction could plausibly use several of these at once — tools via MCP, agent contact via A2A-style transport, checkout via a commerce standard, settlement via a payment network — while ARC supplies the human-approval boundary and the inspectable identity, reputation, dispute, and governance records.

ARC's stance is overlay, not replacement. It is most useful when these other layers exist and work; it tries to add a missing layer, not substitute an existing one.

## 12. Current ARC Scope

ARC today is a **Stage 0.8 executable reference implementation** of its protocol model — beyond the Stage 0 documentation baseline, short of a running product ([roadmap.md](./roadmap.md) Stage 0.8, [README](../README.md)). The Canon (Relationship → Event → Projection → Authority) and the canonical event set (`KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`, `ADJUDICATE`) are exercised by a corpus of small runnable probes — canonical folds, an end-to-end flow on real Ed25519, a browser reference client, an eight-run commerce failure catalog, and the adoption/refusal experiments — but remain exploratory drafts, not a finalized wire format or conformance suite ([future-protocol-spec.md](./future-protocol-spec.md)).

In scope:

- human-approved delegation and its audit, with commerce as the first implementation
- identity, reputation, dispute, and governance expressed as signed events and projections
- failure analysis of the above

Out of scope:

- tool-connection standards, general agent transport, and checkout semantics
- marketplace operation and payment settlement
- on-chain execution and full autonomy

This positioning is a current orientation, not a fixed claim. As the external landscape changes, where ARC sits relative to it may need revisiting.

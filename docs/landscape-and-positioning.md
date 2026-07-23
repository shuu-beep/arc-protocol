# ARC Protocol: Landscape and Positioning

> **Status:** Exploratory positioning note
>
> **Purpose:** ARC is an implementation-neutral authority protocol for delegation among principals and agents over consequential actions. Commerce is its flagship application and first implementation profile, and therefore the comparison domain used here. This note locates ARC among the agent and commerce systems emerging in 2026 — beginning with what ARC is *not* — so external readers do not mistake it for a tool-use layer, an agent-interop layer, a checkout standard, a marketplace, a payment network, or a blockchain protocol.
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

ARC is, as currently understood, an authority layer for three things ([README](../README.md)):

- **Principal-rooted authority and delegation** — consequential acts require Current Coverage from authority granted by the responsible principal or authority holder. Current ARC profiles are typically human-rooted; delegation is scoped and never self-widening.
- **Portable authority** — ARC is designed to support portable authority evidence between agents and implementations under future named interoperability profiles; a recipient may honor or decline authority from another context.
- **Recomputable audit** — named Projections fold identified Event sets under declared policy and ordering inputs. External Record Verification, independent recomputability, and public recomputability are separate claims.

Commerce is ARC's **flagship application and first implementation profile, not its definition**, and the domain in which the comparisons below (§4–§11) are drawn — because that is where ARC first meets neighboring systems. In a current human-rooted Commerce profile, a purchase folds to the same primitives as other delegation: a merchant's offer is an `ATTEST`, the human's approval an `AUTHORIZE`, a dispute a `CHALLENGE`, a community ruling an `ADJUDICATE`. It remains an exploration, not a finished protocol ([future-protocol-spec.md](./future-protocol-spec.md)).

In Canon terms ([object-model.md](./object-model.md), [authority-and-conflict.md](./authority-and-conflict.md)), ARC reasons over signed **Events**, computes relationships and reputation as on-demand **Projections**, and locates final authority with the party legitimately responsible for an action and its risk, while communities act only within declared commons and authority profiles — never with an algorithm. Current ARC profiles are typically human-rooted. Named application profiles may govern how Projection outputs are used; no universal score is authoritative protocol state.

ARC's intended stance is an **overlay, not a replacement**: anti-dependency, not anti-company. It is most useful if the other layers below thrive.

## 3. What ARC Is Not

ARC is not:

- a tool-use / capability layer (compare MCP, §4)
- an agent-to-agent interop or transport layer (compare A2A, §5)
- a checkout or commerce-semantics standard (compare ACP, §6)
- a marketplace or platform operator (§7)
- a payment network, wallet, or settlement rail (§8)
- a blockchain protocol or on-chain registry (§9)

Consistent with the rest of the corpus, ARC is also not a full-autonomy framework — its authority boundary is a hard constraint, not a removable feature. Current Commerce profiles are typically human-rooted ([philosophy.md](./philosophy.md), [roadmap.md](./roadmap.md)) — and ARC is not a token project ([roadmap.md](./roadmap.md)).

## 4. ARC vs MCP

MCP standardizes how an agent connects to external tools and data sources — a capability and transport concern: how an agent reaches a calendar, a database, or a service.

ARC does not define tool connection. It assumes agents can already act, and asks a different question: by what authority may an agent perform a consequential act, and what signed evidence supports that authority and its audit? Commerce is the example used in this comparison.

These are different layers. An ARC-compatible agent could use MCP to reach its tools; nothing in ARC competes with that.

## 5. ARC vs A2A

A2A standardizes how independent vendor agents discover and delegate to one another — an interoperability and communication concern: how agents talk.

ARC is not a general agent-interop transport. It concerns authority over consequential agent-mediated acts; this comparison uses the narrower Commerce application — signed offers, approval, reputation, dispute, governance. ARC could ride on an A2A-style transport, or on others; it does not specify the transport.

Different problem, not a rival: A2A asks "how do agents communicate?"; ARC asks "what authority covers an agent's consequential act, and what evidence records that coverage?"

## 6. ARC vs Commerce Checkout Standards

Commerce checkout standards — ACP and similar approaches — define product discovery, cart, and checkout so an agent can complete a purchase, often with merchant-owned checkout and a scoped payment token.

ARC does not define checkout semantics and does not execute purchases. The Commerce profile applies its authority and audit semantics *around* such a transaction: did the unchanged act have Current Coverage; what does the named merchant-reputation Projection show from the available evidence; how is a dispute recorded.

These can compose rather than collide. A plausible Commerce-profile sequence is: ARC authority coverage → checkout execution via a commerce standard → an ARC reputation claim recorded afterward.

## 7. ARC vs Marketplace

A marketplace aggregates buyers and sellers and operates discovery, ranking, fees, support, and dispute resolution under a single operator. Marketplaces provide real value — demand aggregation, trust signals, support, fraud handling — and ARC does not deny this ([bootstrap-and-incentives.md](./bootstrap-and-incentives.md) §3).

ARC is not a platform operator and runs no marketplace. It explores open, replaceable discovery backends and community governance instead of a single operator, and it provides no built-in demand and guarantees no participation ([bootstrap-and-incentives.md](./bootstrap-and-incentives.md)).

This is a structural difference, not a claim of superiority. In many respects ARC offers *less* than a mature marketplace. The open question ARC raises is whether some coordination functions can be made inspectable, portable, and less concentrated — not whether marketplaces should go away.

## 8. ARC vs Payment Network

Payment networks, wallets, and settlement rails move money. ARC does not ([architecture.md](./architecture.md) §4.2, [liability-boundaries.md](./liability-boundaries.md)). ARC selects no payment provider; regional integration remains application/profile work.

In Canon terms, a payment-result claim enters ARC only as an `ATTEST` about an external transfer ([event-registry.md](./event-registry.md)): ARC records the claim, it does not settle the funds.

So the Commerce profile depends on payment networks rather than competing with them. Payment execution stays with the provider, and the application proceeds only when the act has Current Coverage.

### 8.1 Agent-Native Monetization Gateways (x402)

A newer variant of the settlement layer deserves its own note, because it begins from the same observation ARC does. Cloudflare's **Monetization Gateway** (announced 2026-07-01, [blog.cloudflare.com/monetization-gateway](https://blog.cloudflare.com/monetization-gateway/)) is built on **x402**, an open protocol that revives the HTTP `402 Payment Required` status code: a server prices a request, the client pays in stablecoins, a facilitator verifies the payment, and the resource is delivered — per request, at sub-cent granularity, proxied at the edge. Agent identity is handled by a separate verification mechanism (Web Bot Auth), and the announcement explicitly anticipates agents that "carry wallets" and purchase autonomously.

One possible overlap is a research question: increased agent traffic may change how conventional advertising or subscription models perform. ARC's historical Commerce material anticipated that possibility, but the corpus does not establish an "agent-first internet" or its business-model effects ([philosophy.md](./philosophy.md)).

From that shared premise the two systems diverge into different layers:

- **x402 makes the request a transaction.** Its question is *how does an agent pay*, and a facilitator applies the payment profile's checks. ARC's question is *by what authority did the agent act*: can an observer recompute Current Coverage from the declared Event set, named Projection/profile, and ordering inputs ([event-registry.md](./event-registry.md))?
- **Wallet authorization is profile-specific.** A wallet transaction demonstrates satisfaction of that wallet or payment profile's authorization checks. It does not by itself establish faithful interpretation of a principal's intent. ARC separately represents act-specific or mandate-scoped authority granted by a principal or authority holder ([key-custody.md](./key-custody.md)).
- **The verification dependencies differ.** The gateway model uses its facilitator and edge operator for payment checks. ARC's authority semantics do not require one deployment topology: a named deployment may use a central verifier, while stronger external or independent claims require the corresponding observer evidence surface ([authority-and-conflict.md](./authority-and-conflict.md)).
- **Per-outcome pricing re-opens the record/referent boundary.** The announcement cites pricing "paid only when the work succeeds." Outcome-based pricing therefore requires an external determination mechanism. ARC can record related claims, challenges, and adjudications without proving the outcome ([event-registry.md](./event-registry.md) §2.4).

These layers compose rather than collide. An x402 payment enters ARC the same way any settlement does — as an `ATTEST` about an external transfer (§8 above) — and ARC's Current Coverage boundary addresses a question x402 leaves open: whether the agent presenting the payment was authorized by its principal to make it. Conversely, x402 is a plausible settlement rail *underneath* an ARC-covered purchase.

An incumbent gateway may have lower deployment friction with existing customers, but implementation cost and seller uptake are not established. This is the same adoption question §10 raises for closed platforms ([threat-model.md](./threat-model.md) §18.1). As elsewhere in this document, the comparison reflects ARC's current reading of a recently announced system and may become outdated.

## 9. ARC vs Blockchain Protocol

Blockchain protocols provide shared, manipulation-resistant ledgers and consensus. Some target agent trust directly, for example on-chain identity and reputation registries.

ARC does not prescribe a storage or settlement backend ([philosophy.md](./philosophy.md) belief 5, [architecture.md](./architecture.md) §1.1). An implementation may use centralized services, federated or community-operated systems, a shared ledger, a blockchain, or combinations of them, provided the event, projection, and authority semantics remain intact. A chain may carry records or checkpoints or sit beneath external settlement; ARC itself supplies neither consensus nor settlement.

The design difference is not chain versus no chain. ARC defines signed Events as canonical records and permits named Projections over declared inputs, rather than making a global score or persistent profile a protocol primitive ([object-model.md](./object-model.md)).

Where some systems explore trust as *computed* on shared infrastructure, the current Commerce/reputation research explores trust as *governed* through a community process over evidence, with no authoritative stored universal score. "Computed" and "governed" are positioning language, not ARC protocol primitives. Both approaches are unproven, and base ARC mandates neither topology.

## 10. ARC vs Closed Agent Commerce

Sections §4–§9 contrast ARC with neighboring *layers* it composes with. This contrast is different in kind. A closed agent-commerce platform is not a layer ARC sits beside; it is an alternative way the whole stack could be organized. Both could exist, but they embody opposite bets about where coordination lives.

One research hypothesis has a familiar shape: a large marketplace or super-app (an Amazon- or Coupang-style operator) extends into agent commerce by running the buyer's agent, discovery, ranking, advertising, and checkout as one closed loop. This carries practical advantages: demand is aggregated, fraud may be handled centrally, the interface is familiar, and existing users, merchants, and payment relationships may lower adoption friction. This is structural inference, not observed ARC adoption evidence. In the adoption scenarios described in [bootstrap-and-incentives.md](./bootstrap-and-incentives.md), the incumbent closed path may have lower initial friction. ARC has no evidence that resolves the comparison.

What such a structure concentrates is an application-design question. When the operator owns both the buyer's agent and the seller's storefront, the buyer's agent is also the seller's gatekeeper, creating a potential conflict of interest. Candidate differences include:

| Closed agent commerce | ARC Commerce application's contrasting research bet |
| --- | --- |
| Ranking controlled by one operator | A Commerce profile may offer alternative backends and disclose ranking inputs (§7) |
| Operator-computed trust score | The research model explores community process over evidence and no authoritative universal score (§9) |
| Merchant exit governed by platform terms | The research model explores contextual portability with unresolved inter-community costs ([trust-model-tradeoffs.md](./trust-model-tradeoffs.md)) |
| Sponsorship disclosure set by operator policy | A named Commerce policy may require sponsorship disclosure (`discovery-bias.json`; [event-registry.md](./event-registry.md)) |
| Agent authority set by platform policy | ARC represents Current Coverage from authority granted by the responsible principal or authority holder for consequential acts; current ARC profiles are typically human-rooted ([delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md)) |

None of this is a claim that closed platforms are illegitimate or should disappear. They provide application functions that some users may prefer, and the current Commerce research has no adoption evidence against them ([bootstrap-and-incentives.md](./bootstrap-and-incentives.md)). A named deployment may expose ranking inputs or support alternative operators, but base ARC does not guarantee either property. Whether those choices affect adoption remains the open question in [threat-model.md](./threat-model.md) §18.1.

## 11. Why These Systems Can Coexist

The layered systems in §4–§9 mostly occupy different layers:

| Layer | Example concern | ARC's relation |
| --- | --- | --- |
| Tool access | reaching tools and data (MCP) | ARC uses, does not define |
| Agent interop | agents discovering and delegating (A2A) | ARC may ride on, does not specify |
| Checkout semantics | discovery, cart, checkout (ACP) | ARC wraps with approval and trust records |
| Platform operation | aggregated marketplace | ARC explores an open alternative function |
| Settlement | moving money (payment networks, x402-style gateways §8.1) | ARC depends on, records as `ATTEST` |
| Shared ledger | manipulation-resistant records (blockchain) | Optional implementation or external settlement layer; not an ARC semantic |

ARC occupies the authority layer for consequential agent-mediated acts. In its flagship Commerce application, a transaction could plausibly use several neighboring layers at once — tools via MCP, agent contact via A2A-style transport, checkout via a commerce standard, settlement via a payment network — while ARC semantics represent authority coverage and attributable identity, reputation, dispute, and governance claims under named profiles.

ARC's stance is overlay, not replacement: it addresses authority records around other layers rather than substituting for their transport, checkout, or settlement functions.

## 12. Current ARC Scope

ARC today has a **Stage 0.8 Executable Reference Corpus** for its protocol model — beyond the Stage 0 documentation baseline, short of a running product ([roadmap.md](./roadmap.md) Stage 0.8, [README](../README.md)). The Canon (Relationship → Event → Projection → Authority) and the canonical event set (`KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`, `ADJUDICATE`) are exercised by small runnable probes — canonical folds, an end-to-end flow on real Ed25519, a browser reference client, an eight-run Commerce failure catalog, and adoption/refusal experiments — but remain exploratory drafts, not a finalized wire/security profile or conformance suite ([future-protocol-spec.md](./future-protocol-spec.md)).

In scope:

- authority delegation and its audit, with Commerce as the flagship application and first implementation profile
- identity, reputation, dispute, and governance expressed as signed events and projections
- failure analysis of the above

Out of scope:

- tool-connection standards, general agent transport, and checkout semantics
- marketplace operation and payment settlement
- on-chain execution and full autonomy

This positioning is a current orientation, not a fixed claim. As the external landscape changes, where ARC sits relative to it may need revisiting.

# Agent-Mediated Commerce: Reassessing Infrastructure Assumptions

> **Status:** Exploratory analytical note
>
> **Purpose:** Separate observations about earlier decentralized commerce from inferences about what AI agents may change and open hypotheses about which implementations may become useful.
>
> This is not a prediction that blockchain adoption is inevitable, a proposal for an ARC token, or an expansion of ARC into payments or marketplace operation. For ARC's current boundaries, see [landscape-and-positioning.md](./landscape-and-positioning.md) and [liability-boundaries.md](./liability-boundaries.md).

---

## 1. Analytical Boundary

This note uses three labels deliberately:

- **Observation** describes recurring burdens visible across earlier decentralized or blockchain-commerce attempts. It does not assign one universal cause of failure.
- **Inference** asks how agent mediation could change who bears those burdens. It is a reasoned possibility, not a measured outcome.
- **Open hypothesis** names what future implementations or pilots would still need to test.

The distinction matters because neither the difficulty of earlier systems nor the arrival of capable agents proves what a future market will adopt.

This note did not begin as an argument for blockchain-based commerce. It emerged while examining whether personal AI agents remain meaningfully independent when closed platforms control discovery, ranking, and recommendation. That threat model suggested that an agent may be less susceptible to emotional persuasion while remaining algorithmically dependent, renewing the importance of open, inspectable discovery and explicit authority boundaries ([philosophy.md](./philosophy.md) §§2–3).

**Analytical hinge.** That inquiry raised a second question. Some earlier systems required people to handle some combination of wallets, keys, tokens, bridges, escrow selection, and reputation evaluation directly. If software can absorb operational work that people previously bore, agent mediation may change the relevant cost structure even though the underlying complexity does not disappear. Some assumptions behind earlier decentralized-commerce failures may therefore deserve re-examination. This document explores that possibility. It does not argue that earlier conclusions were wrong or that blockchain adoption is inevitable. The open question is whether software agents can absorb enough of that complexity while preserving human authority and the conditions for informed consent.

## 2. Observation: Earlier Commerce Carried a Full-Stack Burden

Earlier decentralized or blockchain-commerce efforts often asked people to operate unfamiliar infrastructure directly. The cumulative burden could include:

- **Wallet operation:** creating wallets, protecting seed phrases, acquiring tokens, estimating gas, bridging between networks, and understanding irreversible actions.
- **Market formation:** finding liquidity, discovering counterparties, and judging reputation across fragmented or thin markets.
- **Transaction completion:** selecting escrow, handling disputes, proving delivery, collecting evidence, and finding support when something failed.
- **Marketplace sustainability:** funding discovery, moderation, fraud handling, customer support, and logistics without durable multi-sided marketplace economics.

These are general historical observations, not a claim that every project faced every burden or that blockchain alone caused weak adoption. A usable marketplace must coordinate demand, trust, fulfillment, and support regardless of its ledger. ARC's own bootstrap analysis records the same missing functions without claiming to replace them ([bootstrap-and-incentives.md](./bootstrap-and-incentives.md)).

Taken together, these burdens could raise onboarding, transaction, and recovery costs before network effects made the effort worthwhile. That is one plausible explanation for why some efforts struggled, not a universal causal account.

## 3. Inference: Agents May Move the Interface Boundary

AI agents can be designed to absorb some operational work that humans previously performed themselves:

- wallet operation and transaction preparation
- market search and comparable-offer discovery
- fee, route, and settlement comparison
- contextual reputation analysis
- evidence collection and organization
- settlement routing across available providers or networks
- dispute preparation for a human, provider, or community process

The key change is not that blockchain became easy. **Humans may no longer need to operate it directly.** An agent could mediate the wallet, network, and market interfaces while presenting a smaller decision surface to the person.

That possibility could change some usability and transaction-cost assumptions behind earlier failures. It does not remove the custody boundary: a wallet-operating agent still depends on keys, scopes, and a trusted signing path ([key-custody.md](./key-custody.md)). Nor does it prove that mediation will be reliable, understandable, or cheaper in practice.

## 4. Observation: Several Constraints Do Not Disappear

Agent mediation does not automatically create liquidity, stop fraud, produce legitimate governance, move physical goods, or fund support. It may lower the cost of searching or preparing a transaction while leaving the harder coordination system intact.

The remaining questions include:

- whether enough buyers and sellers create usable liquidity
- whether identity and reputation signals resist manipulation
- who governs disputes and pays for review
- who performs delivery, returns, and customer support
- which party bears loss when an agent, wallet, provider, or counterparty fails
- whether the marketplace or infrastructure has a sustainable business model

Automation may also scale poor decisions. A faster route through an opaque market is not necessarily a more trustworthy route.

## 5. Inference: Payment Access Is Not Decision Sovereignty

**An agent can be emotionally indifferent yet algorithmically dependent.**

Agent payments are one layer. Wallet access and autonomous settlement can establish that an agent *can* pay; they do not establish that it chose in the user's interest or acted within legitimate authority.

The discovery layer remains subject to the dependency described in [philosophy.md](./philosophy.md) §§2–3. If recommendation provenance and authority boundaries remain opaque, the agent may still depend on platform-controlled discovery, ranking, fees, or available alternatives. That is an incentive and observability problem, not proof that every closed system is biased.

Decision sovereignty therefore depends on more than possession of a wallet. It also depends on whether the user or an independent reader can inspect what authority covered the action, which inputs shaped the recommendation, what alternatives were omitted, and who can contest the result.

## 6. ARC's Narrow Relevance

ARC does not provide a marketplace, blockchain, token, wallet, or payment rail. It does not execute settlement.

Its relevance is narrower:

- **authority** — which signed grant covers an agent's act
- **human approval** — where a person authorizes a specific action or bounded mandate
- **signed evidence** — what attributable records remain after the act
- **contest and adjudication** — how claims and rulings enter the same event history
- **recomputable projections** — how current authority, standing, and disagreement are derived rather than stored as opaque state

A signed claim about a payment outcome enters ARC only as an external attestation; it is not a native transfer primitive ([event-registry.md](./event-registry.md)). ARC can make the available signed authority and evidence records around a transaction inspectable. It cannot make the settlement correct, the delivery real, or the marketplace viable.

## 7. Open Hypotheses

Agent-mediated commerce may reopen demand for several implementation forms: centralized services, federated systems, cooperatives, community-operated infrastructure, shared ledgers, blockchain-based settlement, or combinations of them.

Whether any form becomes useful remains an open hypothesis. Relevant tests would include whether agents actually reduce user error and transaction cost, whether recommendation provenance is independently inspectable, whether custody and approval boundaries survive compromise, and whether liquidity, logistics, governance, support, and marketplace economics hold under real use.

The cautious conclusion is therefore not that blockchain adoption will follow. It is that agents may change who operates complex infrastructure, making some previously impractical arrangements worth testing again without resolving the reasons many marketplaces fail.

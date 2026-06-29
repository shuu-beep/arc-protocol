# ARC Protocol: Bootstrap and Incentive Limitations

> **Status:** Exploratory limitation note
>
> **Purpose:** Make explicit that ARC does not yet solve participation incentives, cold start, or network bootstrapping.

---

## 1. Why This Document Exists

ARC argues that agent commerce infrastructure should be more open, inspectable, portable, and human-approved.

That does not explain why anyone would join.

A protocol vision is not enough to create a useful commerce network. Consumers, merchants, logistics providers, discovery backends, relay operators, moderators, and implementers each need reasons to participate. Those reasons may conflict.

This document records the current bootstrap and incentive gaps rather than pretending they are solved.

## 2. The Network Bootstrap Problem

ARC does not currently solve the network bootstrap problem.

A useful local commerce network needs several groups at once:

- consumers with agents capable of requesting and comparing offers
- merchants willing to expose structured offers
- logistics providers where delivery is required
- discovery backends that can surface participants
- payment integrations that users trust
- reputation records that are meaningful enough to inspect
- governance processes that can handle disputes

Each group has a reason to wait for the others.

```txt
Consumers want useful merchants before installing or trusting an agent.
Merchants want consumer demand before operating an agent.
Logistics providers want transaction volume before integrating.
Governance requires activity before it can prove legitimacy.
Reputation requires transactions before it can become useful.
```

This chicken-and-egg problem is structural, not a marketing detail.

## 3. Platforms Provide Real Value

ARC criticizes centralized platform control, advertising dependency, and opaque ranking.

That criticism should not imply that centralized platforms provide no value.

Existing platforms often provide:

- demand aggregation
- search and discovery
- consumer trust signals
- payment mediation
- refund and chargeback workflows
- customer support
- merchant onboarding
- logistics coordination
- fraud monitoring
- quality enforcement
- familiar user interfaces

ARC does not yet replace these functions.

ARC asks whether some of these functions can eventually become more open, portable, inspectable, locally adaptable, and less extractive. That is a design question, not a proven result.

## 4. Merchant Participation Is Not Guaranteed

A merchant may ask:

- Where will demand come from?
- Who maintains the merchant agent?
- Does participation reduce platform dependence or merely add another channel?
- Who handles support, refunds, and failed orders?
- Will structured offers require technical work?
- Will reputation portability actually help?
- What prevents low-quality discovery backends from misrepresenting the merchant?

ARC has no general answer yet.

A small pilot may begin with volunteer merchants interested in experimentation, direct customer relationships, lower intermediary overhead, or portable reputation. That is not the same as proving broad merchant adoption.

## 5. Logistics Participation Is Also Unclear

Logistics providers face additional constraints:

- route optimization
- pickup timing
- delivery proof
- insurance
- worker availability
- safety
- regional rules
- integration cost
- dispute responsibility

A logistics agent is not useful merely because it can respond to a message. It must coordinate real-world capacity under time pressure.

ARC has not yet shown that independent logistics agents can coordinate reliably enough for production commerce.

## 6. Governance Labor Is Not Free

Community governance requires time, attention, judgment, and accountability.

Fraud reports, appeals, evidence review, conflict-of-interest checks, and policy updates create operational work. That work does not disappear because a system is open-source or non-profit.

Possible sustainability models to study may include:

- public-interest grants
- cooperative membership contributions
- transparent dispute-processing fees
- paid review for complex cases
- merchant association funding
- municipal or community infrastructure support
- volunteer moderation with strict scope limits

ARC does not currently choose one model.

It should not assume unpaid moderation can scale under adversarial pressure.

## 7. Discovery Infrastructure Also Needs Support

Discovery backends, relays, directories, ranking explanations, reputation displays, audit logs, and moderation queues all cost money to operate.

Possible funding and operation models may differ by community:

- community-operated directories
- non-profit cooperative infrastructure
- merchant-hosted registries
- consumer-supported tools
- transparent listing fees
- clearly disclosed sponsored discovery
- public-interest or municipal support

The important boundary is that funding should not be hidden as neutral ranking.

If sponsorship or paid placement exists, it should be explicit, machine-readable, and visible to humans and agents.

## 8. Cold Start vs Sybil Resistance

New entrants need a path to discovery.

Attackers exploit automatic exposure.

If ARC hides new merchants until they have reputation, established participants become entrenched. If ARC promotes new agents too freely, Sybil attackers can create fake merchants, fake logistics providers, or fake buyer histories.

Current ARC documents treat this as a permanent tension. They do not define a final ranking rule.

Future work should examine:

- verified-new-entrant labels
- probation periods
- low-risk transaction limits
- escrow-like participation where appropriate
- sponsorship disclosure
- user-selectable strictness
- rate limits on reputation growth
- anti-collusion review triggers

## 9. No Built-In Demand Guarantee

ARC should be explicit:

```txt
ARC does not provide built-in demand.
ARC does not guarantee lower costs.
ARC does not guarantee merchant adoption.
ARC does not guarantee logistics participation.
ARC does not guarantee that open discovery will outperform centralized platforms.
```

A future pilot can test whether specific communities find enough value to participate.

Until then, ARC remains an exploratory design proposal.

## 10. Current Position

ARC's incentive theory is incomplete.

That is acceptable at this stage if stated clearly. The next useful work is not to claim that open agent commerce will automatically attract participants, but to design small experiments that reveal what participants actually need.

Where this document catalogs the gaps by network role, [`adoption-and-defection.md`](adoption-and-defection.md) takes the per-actor decision view the threat model calls the honest entry point ([§18.1](threat-model.md)): why each actor can rationally wait, defect, fork, or reject, and which mechanisms — held as hypotheses, not claims — might change that. The historical economics behind those mechanisms — why comparable open protocols were adopted, or displaced after adopting — are surveyed in [`coordination-economics-survey.md`](coordination-economics-survey.md).

Useful future artifacts may include:

- merchant onboarding assumptions
- logistics participation assumptions
- discovery funding options
- governance labor budget estimates
- pilot recruitment notes
- failure notes from communities that decline to participate

A failed pilot may be as informative as a successful one.

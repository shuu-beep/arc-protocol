# ARC Protocol: Bootstrap and Incentive Limitations

> **Status:** Exploratory limitation note
>
> **Purpose:** Make explicit that ARC does not yet solve participation incentives, cold start, or network bootstrapping.

---

## 1. Why This Document Exists

Within its Commerce research, ARC examines open, inspectable, portable, and human-authorized application infrastructure.

That does not explain why anyone would join.

A protocol vision is not enough to create a useful commerce network. Consumers, merchants, logistics providers, discovery backends, relay operators, moderators, and implementers each need reasons to participate. Those reasons may conflict.

This document records the current bootstrap and incentive gaps rather than pretending they are solved.

## 2. The Network Bootstrap Problem

The Commerce application research does not currently solve the network bootstrap problem.

A useful local commerce network needs several groups at once:

- consumers with agents capable of requesting and comparing offers
- merchants willing to expose structured offers
- logistics providers where delivery is required
- discovery backends that can surface participants
- payment integrations acceptable under the selected profile
- reputation records that are meaningful enough to inspect
- governance processes that can handle disputes

Each group has a reason to wait for the others.

```txt
Consumers want useful merchants before installing or trusting an agent.
Merchants want consumer demand before operating an agent.
Logistics providers want transaction volume before integrating.
Governance requires activity before its procedures can be evaluated.
Reputation requires transactions before it can become useful.
```

This is a multi-party dependency in the Commerce application model.

## 3. Platforms Provide Real Value

Earlier Commerce framing criticized centralized platform control, advertising dependency, and opaque ranking.

That criticism should not imply that centralized platforms provide no value.

Existing platforms often provide:

- demand aggregation
- search and discovery
- consumer assurance signals
- payment mediation
- refund and chargeback workflows
- customer support
- merchant onboarding
- logistics coordination
- fraud monitoring
- quality enforcement
- familiar user interfaces

ARC does not yet replace these functions.

The Commerce research asks whether some of these functions can use different funding and incentive structures while becoming more open, portable, inspectable, and locally adaptable. That is a design question, not a proven result.

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
- delivery evidence
- insurance
- worker availability
- safety
- regional rules
- integration cost
- dispute responsibility

A logistics agent is not useful merely because it can respond to a message. Its usefulness depends on coordinating real-world capacity under time pressure.

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

This note does not assume unpaid moderation can scale under adversarial pressure.

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

A named Commerce application policy may require funding influence, sponsorship, or paid placement to be explicit, machine-readable, and visible to humans and agents.

## 8. Cold Start vs Sybil Resistance

New entrants need a path to discovery.

Attackers exploit automatic exposure.

If a Commerce profile hides new merchants until they have reputation, established participants may become entrenched. If it promotes new agents too freely, Sybil attackers may create fake merchants, fake logistics providers, or fake buyer histories.

Current documents identify this tension but do not define a final ranking rule.

Future work should examine:

- declared-new-entrant labels
- probation periods
- low-risk transaction limits
- escrow-like participation where appropriate
- sponsorship disclosure
- user-selectable strictness
- rate limits on reputation growth
- anti-collusion review triggers

## 9. No Built-In Demand Guarantee

This note records the following application limitations:

```txt
ARC does not provide built-in demand.
ARC does not guarantee lower costs.
ARC does not guarantee merchant adoption.
ARC does not guarantee logistics participation.
ARC does not guarantee that open discovery will outperform centralized platforms.
```

A future pilot can test whether specific communities find enough value to participate.

Until then, the Commerce application remains exploratory.

## 10. Current Position

The Commerce application's incentive research is incomplete.

The next empirical step is to design small experiments that record what participants report needing, without claiming that open agent commerce will automatically attract them.

Where this document catalogs gaps by network role, [`adoption-and-defection.md`](adoption-and-defection.md) takes an inverse per-actor view ([threat-model §18.1](threat-model.md)): why each actor may wait, defect, fork, or reject, and which mechanisms — held as hypotheses, not claims — might change that. Preliminary historical comparisons appear in [`coordination-economics-survey.md`](coordination-economics-survey.md).

Useful future artifacts may include:

- merchant onboarding assumptions
- logistics participation assumptions
- discovery funding options
- governance labor budget estimates
- pilot recruitment notes
- failure notes from communities that decline to participate

A failed pilot can provide data alongside any successful outcome.

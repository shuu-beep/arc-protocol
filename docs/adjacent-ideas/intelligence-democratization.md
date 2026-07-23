# AI Capability Access

> **Status:** Adjacent Idea
>
> **Not part of ARC Core.**
>
> **Purpose:** Explore how access to AI reasoning and agents might affect participation if such tools become widely consequential.
>
> This document does not support any specific policy. It does not advocate national AI credits, basic income, regional credits, or public AI support. It is exploration only, and deliberately holds benefits and risks side by side without recommending a direction.
>
> This sits beside [economics-of-agent-access.md](./economics-of-agent-access.md), which asks who pays for agent access; this note asks who can access AI services and on what terms. For ARC's view on centralized influence over agents, see [philosophy.md](../philosophy.md) §3. For scope, see [README](./README.md).

---

## 1. Why This Idea Exists

If AI agents and reasoning become a normal way people get things done, their access conditions may affect participation.

This note asks which access conditions could matter if AI tools become consequential. It does not predict that outcome or infer a policy need.

## 2. Scope of the Access Question

Access conditions may include hardware, network availability, provider terms, price, language support, accessibility, and institutional support. Their distributional effects are empirical questions outside ARC's protocol boundary.

## 3. The Agent Access Question

If agents become a normal interface, two access questions follow:

- **Who can access an AI agent at all?**
- **Who can access a *better* agent** — faster, more capable, better-integrated, more private?

These are different. Universal access to a weak agent and stratified access to strong ones could coexist. A society where everyone has *some* agent but capability tracks wealth may look inclusive while reproducing the gap it appears to close.

## 4. Inference Costs and Access

Access depends on who bears the cost of reasoning. Several models already exist or are emerging:

- **On-device models** — local inference, no per-use fee, bounded by device capability and energy.
- **Personal subscription** — the individual pays directly.
- **Employer-paid** — access tied to a job and lost with it.
- **Platform-paid** — access bundled into a service, often funded by advertising or data.

Each may shape who gets access and on what terms. On-device access may offer more local control while remaining limited by device capability; platform-paid access may broaden availability while increasing provider dependence. Effects vary by implementation, and this note does not rank the models.

## 5. Intelligence Gaps

A plausible scenario worth examining, not predicting:

- a group with high-quality AI access — strong models, good integration, privacy, time to use them well
- a group with limited AI access — weak or no models, poor integration, or access that is surveilled or rate-limited

If reasoning capability becomes economically significant, a gap here could compound like other capability gaps: those with better tools produce more, learn faster, and pull further ahead. Whether this materializes depends on how cheap good-enough reasoning becomes — a falling cost could narrow the gap as easily as a rising capability ceiling could widen it.

## 6. Community and Regional Support

If access mattered, communities or regions might experiment with supporting it. Possible forms — listed as questions, not proposals:

- regional access credits
- shared or community-hosted AI support
- experiments in places under demographic pressure

Whether any of these would help, or would simply add a new dependency and a new thing to capture, is unresolved. Community-level support could increase local autonomy or could create local versions of the same control problems (§11).

## 7. Depopulation Regions

One specific case sometimes raised is regions losing population. The elements below are candidate variables, not a causal chain:

```txt
regional constraint: youth out-migration
possible support experiment: regional AI access
candidate domains to evaluate: education · administration · entrepreneurship · agriculture · local commerce
```

This is a hypothesis, not evidence. Questions include whether access support would affect jobs or services, whether falling reasoning costs would reduce the value of a subsidy, who would use capacity placed in a low-population region, and whether a region-linked scheme would create new dependencies. These are reasons to treat the idea as an open research question.

## 8. Public Funding Proposals

A government or institution could propose credits, shared facilities, or other subsidies. This note neither predicts nor advocates such a program. Any proposal would need to specify eligibility, funding, operation, logging, privacy, and control, including the risks in §10 and §11.

## 9. Potential Benefits

If access were widened well, possible benefits might include:

- productivity gains for individuals and small organizations
- broader access to education and explanation
- some narrowing of information gaps
- stronger local capacity in places that currently lack specialist services

These are possibilities, not guarantees. Each assumes the access is good-quality, independent, and actually used — assumptions that often fail in practice.

## 10. Risks and Failure Modes

Held with equal weight to §9:

- **State dependency** — access provided by a government can be withdrawn, conditioned, or politicized.
- **Single-vendor dependency** — access routed through one company's models creates lock-in and a private chokepoint.
- **Platform lock-in** — bundled access ties people to a platform's terms and incentives.
- **Political capture** — whoever allocates access can favor groups, regions, or views.
- **Surveillance** — access tied to identity can become a record of what people ask and do.
- **Regional inequality** — uneven support can widen gaps between places rather than close them.
- **Budget waste** — large spending on infrastructure or credits with little durable benefit.
- **Performative policy** — programs that signal action without changing real access.

These risks warrant separate evidence; this note does not establish historical analogues for them.

## 11. Funding and Control Questions

Funding arrangements may influence recommendation, discovery, defaults, or provider access without granting direct control. This note does not establish that influence or control follows from funding. A study would need to identify the payer, decision rights, provider constraints, and observable behavior.

This overlaps with questions in [economics-of-agent-access.md](./economics-of-agent-access.md) §4 and [philosophy.md](../philosophy.md) §3: funding or hosting arrangements may influence what an agent surfaces, what is cheap to ask, and which options appear trustworthy. Widening access does not by itself answer who controls it, and concentrated control could offset intended benefits.

Inspectability, contestability, portability, and accountability are additional dimensions to evaluate alongside breadth of access. This note does not claim to provide them.

## 12. Relationship to ARC

ARC's current protocol boundary is authority over consequential agent-mediated actions; Commerce is its flagship application and first implementation profile. AI capability access is not part of that boundary and adds nothing to the ARC protocol, the Canon, or any event type.

It is recorded here because, if agent access becomes consequential, access conditions may affect application questions such as approval, reputation, discovery, and governance. AI capability access remains an adjacent, longer-horizon question, not part of ARC.

## 13. Open Questions

- Which access constraints are material in a specific deployment, and how could they be measured?
- Does falling inference cost narrow the gap on its own, removing the need for any access policy?
- Can access be widened without concentrating control of the access surface (§11)?
- Is there any access model that avoids both state dependency and single-vendor dependency?
- What would distinguish capacity-building from performative or dependency-creating programs?
- Who would be accountable when subsidized or public access produces a bad outcome?

## 14. Current Status

This document is an Adjacent Idea.

It is not a policy proposal, implementation plan, or ARC requirement. It advocates no funding model or political position. Its purpose is to keep questions about AI capability access available for adjacent research while leaving them outside ARC's protocol boundary.

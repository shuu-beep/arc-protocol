# Agent-Mediated Collaboration

> **Status:** Adjacent idea / speculative extension
> **Purpose:** Explore how ARC's intent-matching model may apply to open-source and service collaboration
> This is not part of the core ARC commerce protocol.

---

## 1. Why This Is Separate

ARC Protocol is currently focused on human-approved agent commerce.

However, many forms of work are also coordination problems:

- open-source contribution
- freelance development
- design work
- translation
- documentation
- research
- protocol review
- bug fixing
- security analysis

These are not physical goods, but they still involve matching intent:

```txt
someone needs help
someone can provide help
both sides need trust
humans approve the engagement
```

This document explores that adjacent idea.

---

## 2. The Problem

Many small projects need help but cannot easily find the right contributors.
Many developers, designers, researchers, and writers are willing to help but cannot easily find the right projects.

This problem may become more important in an AI-assisted development world.
Token costs, compute limits, and specialized knowledge may make collaboration more valuable, not less.

A solo builder may not have enough time, budget, or context to do everything alone.

---

## 3. Intent-Based Matching

Agent-mediated collaboration should be based on mutual intent.

A project may publish a machine-readable request:

```json
{
  "project": "arc-protocol",
  "needs": ["threat_model_review", "architecture_diagram", "documentation_edit"],
  "status": "open_to_contributors",
  "compensation": "voluntary_or_discussed",
  "contact_policy": "opt_in_only"
}
```

A contributor may publish an opt-in profile:

```json
{
  "contributor": "developer_agent_001",
  "skills": ["typescript", "security_review", "protocol_docs"],
  "availability": "weekends",
  "interest": ["agent_protocols", "open_governance"],
  "contact_policy": "allow_matching_requests"
}
```

Agents may help compare these signals.
But collaboration should begin only when both sides have expressed intent.

---

## 4. No Unsolicited Agent Outreach

ARC does not support agent spam.

Agents should not crawl the internet and send unsolicited collaboration offers to projects, maintainers, developers, or communities.

The correct model is not:

```txt
agent finds random project -> agent sends proposal
```

The correct model is:

```txt
project publishes need
contributor opts into discovery
agent matches compatible intent
human approves contact or engagement
```

This preserves the same principle used in ARC commerce:

```txt
intent on both sides
transparent matching
human approval
```

---

## 5. Human Approval

Agents may help with:

- finding compatible projects
- summarizing contribution opportunities
- comparing project needs with contributor skills
- drafting a proposed contribution
- preparing a pull request plan

But humans should approve:

- initial contact
- contribution submission
- payment or compensation terms
- long-term collaboration
- access to private repositories or credentials

Agents assist.
Humans decide.

---

## 6. Relationship to Commerce

Collaboration is not identical to commerce, but it shares similar structure.

In commerce:

```txt
buyer intent
seller availability
offer comparison
human approval
```

In collaboration:

```txt
project need
contributor availability
fit comparison
human approval
```

This makes collaboration a possible future extension of ARC's intent-matching philosophy.
It should not be treated as a current core protocol requirement.

---

## 7. Boundary

This document does not expand ARC into a labor marketplace, recruiting platform, or autonomous agent outreach system.

It only records a possible future direction:
agent-assisted, opt-in, human-approved collaboration matching.

Core ARC remains focused on human-approved agent commerce.

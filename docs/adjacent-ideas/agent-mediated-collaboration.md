# Agent-Mediated Collaboration

> **Status:** Adjacent idea / speculative extension
> **Purpose:** Explore opt-in intent matching for open-source and service collaboration as research adjacent to ARC
> This is adjacent research, not part of ARC's authority-protocol requirements or its Commerce flagship profile.

---

## 1. Why This Is Separate

ARC is an implementation-neutral authority protocol. Commerce is its flagship application and first implementation profile.

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
both sides need assurance
humans authorize the engagement
```

This document explores that adjacent idea.

---

## 2. The Problem

Many small projects need help but cannot easily find the right contributors.
Many developers, designers, researchers, and writers are willing to help but cannot easily find the right projects.

AI-assisted development may change demand for collaboration.
Token costs, compute limits, and specialized knowledge are factors to test, not evidence that collaboration will become more valuable.

A solo builder may not have enough time, budget, or context to do everything alone.

---

## 3. Intent-Based Matching

This note considers collaboration based on mutual intent.

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

## 4. Opt-In Outreach

This proposed collaboration model excludes unsolicited agent outreach.

Under this proposal, agents would not crawl the internet and send unsolicited collaboration offers to projects, maintainers, developers, or communities.

The model considered here is not:

```txt
agent finds random project -> agent sends proposal
```

The model considered here is:

```txt
project publishes need
contributor opts into discovery
agent matches compatible intent
human authorizes contact or engagement
```

This resembles one pattern explored in the Commerce application research:

```txt
intent on both sides
transparent matching
human-granted authority
```

---

## 5. Human Authority

Agents may help with:

- finding compatible projects
- summarizing contribution opportunities
- comparing project needs with contributor skills
- drafting a proposed contribution
- preparing a pull request plan

Under this proposal, humans would approve:

- initial contact
- contribution submission
- payment or compensation terms
- long-term collaboration
- access to private repositories or credentials

Agents may assist.
Humans grant and retain the relevant authority.

---

## 6. Relationship to Commerce

Collaboration is not identical to commerce, but it shares similar structure.

In commerce:

```txt
buyer intent
seller availability
offer comparison
human-granted authority
```

In collaboration:

```txt
project need
contributor availability
fit comparison
human-granted authority
```

This makes collaboration a possible future application-research direction adjacent to ARC.
It should not be treated as a current core protocol requirement.

---

## 7. Boundary

This document does not expand ARC into a labor marketplace, recruiting platform, or autonomous agent outreach system.

It only records a possible future direction:
agent-assisted, opt-in, human-authorized collaboration matching.

ARC's current boundary remains the authority protocol; Commerce remains its flagship application.

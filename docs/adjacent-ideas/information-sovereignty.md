# User-Controlled Information Filtering

> **Status:** Adjacent idea / speculative extension
> **Purpose:** Explore user-controlled information filtering and discovery policy beyond commerce
> This is adjacent research, not part of ARC's authority-protocol requirements.

---

## 1. Why This Is Separate

ARC is an implementation-neutral authority protocol. Commerce is its flagship application and first implementation profile.

A related platform concern appears in information systems:

- social feeds
- search results
- news aggregation
- recommendation systems
- community discovery

In many of these systems, centralized platforms influence what people see, what is buried, and what becomes visible.

This document explores a related question:

> If agents help humans navigate commerce, could they also help humans navigate information?

This is an adjacent idea, not a core protocol requirement.

---

## 2. The Platform Feed Problem

Many people do not choose their information environment directly.

They interact with feeds and recommendation systems optimized by platforms.

Those systems may optimize for:

- engagement
- advertising revenue
- time spent
- emotional reaction
- retention
- platform growth

The ordering, ranking, and repetition of information are often influenced by systems users cannot inspect.

This raises a user-control and inspectability question.

Not because all recommendation is bad, but because users often cannot inspect, modify, or replace the systems that shape their attention.

---

## 3. Personal Agent Curation

A personal agent could help users define their own information filters.

For example, a user might ask:

```txt
Show me serious discussions about open-source agent governance,
but ignore low-effort hype and repeated promotional posts.
```

Or:

```txt
Track communities discussing local commerce automation,
but surface only posts with substantive technical or governance arguments.
```

In this model, the user declares a curation policy.
The agent applies it within declared capabilities and available sources.

---

## 4. The Filter Bubble Risk

User-controlled curation can still produce epistemic isolation.

A system that only shows users what they already like can become another kind of manipulation:

- confirmation bias
- ideological isolation
- false certainty
- reduced exposure to disagreement
- self-reinforcing narratives

Replacing a platform algorithm with a personal filter does not automatically produce better understanding.

The danger changes form.

Instead of depending entirely on a platform's engagement algorithm, users may create a comfort-optimized filter.

This note does not assume that personal preference alone produces better understanding.

---

## 5. Optional Out-of-Preference Discovery

One possible design response is an optional out-of-preference discovery allocation.

For example, a user might reserve a small share of discovery for signals outside their normal preferences. The ratio and scope would be user-controlled.

The agent may use this allocation to surface:

- sources selected under a declared provenance rule
- alternative community views
- posts outside the user's usual interests that satisfy declared quality criteria
- minority perspectives accompanied by evidence identified by the policy
- random discoveries with disclosed provenance

The stated aim would be to permit surprise, correction, and discovery without forcing content.

**The tension:** Because user control is central to this adjacent idea, a user may set the allocation to zero. That choice may also create a highly personalized confirmation-bias environment.

This document does not claim to resolve the tension: the allocation is optional, and the human retains the final choice.

---

## 6. User Control and Transparency

Any such mechanism should be:

- user-configurable
- visible
- explainable
- adjustable
- optional

The user should know why something appeared.

```txt
Shown under out-of-preference discovery:
This post comes from a community you do not follow,
but it is supported by evidence under the selected policy
and challenges a topic you frequently read about.
```

This is intended to preserve user choice while testing whether the mechanism reduces total self-confirmation.

---

## 7. Boundary

This document does not propose that ARC should replace social networks, news feeds, or political discussion systems.

It only records possible future discovery-policy research adjacent to ARC.

ARC's current protocol boundary is authority: scoped delegation, approval, revocation, adjudication, and audit.
Commerce remains its flagship application and first implementation profile.

User-controlled information filtering is an adjacent research direction.

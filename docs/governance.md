# ARC Protocol: Challenge, Adjudication, and Governance Boundaries

> **Status:** Non-normative protocol and application research
>
> ARC can represent challenge and adjudication records. It does not create a
> legitimate governing institution, moderator body, court, or enforcement
> system.

## 1. Protocol Boundary

ARC Canon contains two Event types relevant to disputes:

- `CHALLENGE` records a signed claim that another record, authority state, or
  interpretation is disputed.
- `ADJUDICATE` records a signed resolution claim and its causal references.

These are evidence records. Their existence does not prove:

- the underlying facts;
- the decision-maker's legal or institutional authority;
- procedural fairness;
- acceptance by another community or counterparty; or
- execution of a remedy, penalty, refund, or suspension.

The owning Event definitions are in [event-registry.md](./event-registry.md).
Authority recognition and conflict behavior are described in
[authority-and-conflict.md](./authority-and-conflict.md).

## 2. Profile-Relative Authority

A named authority profile must state which adjudicators it recognizes and how
their records affect a Projection. Different profiles may:

- recognize the same adjudicator;
- recognize different adjudicators;
- treat an adjudication as advisory; or
- preserve the matter as unresolved.

ARC does not select a universal authority of last resort. Where relevant
records are concurrent or authorities conflict, a Projection may preserve
`CONTESTED` instead of choosing a winner by timestamp.

An `ADJUDICATE` record can resolve a conflict only for a profile that recognizes
its author and causal relation. It does not erase historical records; a current
Projection changes because the declared evidence and rules support a different
reading.

## 3. Application Responsibilities

An actual governance system must separately define and operate:

- who appoints, authenticates, removes, and audits decision-makers;
- jurisdiction and appeal paths;
- evidence submission, privacy, retention, and disclosure rules;
- notice, response, timing, accessibility, and conflict-of-interest procedures;
- remedies and the systems that enforce them;
- abuse handling, rate limits, operational security, and continuity;
- applicable law, contracts, and regulatory obligations.

ARC provides none of these institutions. It can preserve signed claims about
their decisions if an application chooses to encode them.

## 4. Commerce Dispute Example

The Commerce profile can carry a bounded record flow for claims about fraud,
fulfillment, payment, or reputation:

```text
application dispute
  -> notice and counterparty response outside ARC
  -> CHALLENGE record
  -> evidence collection outside ARC
  -> decision by a profile-recognized reviewer
  -> ADJUDICATE record
  -> application Projection recomputation
  -> optional remedy enforced by external systems
```

ARC does not prescribe the institution, reviewer selection, penalty scale,
appeal service, or production workflow. See the bounded
[Dispute Flow](../diagrams/dispute-flow.md).

## 5. Main Failure Modes

Any implementation should treat governance as attackable:

- **capture:** a narrow group controls appointments or outcomes;
- **Sybil participation:** nominally separate actors share one controller;
- **collusion:** reviewers, claimants, or counterparties coordinate;
- **false or strategic challenges:** process is used to delay or punish;
- **overload:** case volume makes meaningful review impossible;
- **evidence laundering:** weak external claims acquire apparent legitimacy;
- **privacy leakage:** dispute records expose sensitive people or transactions;
- **authority ambiguity:** receivers disagree about who may adjudicate;
- **enforcement gap:** a record exists but no external system applies a remedy.

Cryptographic signatures improve attribution to keys; they do not solve these
institutional problems.

## 6. Project Stewardship Is Separate

ARC repository maintenance, Canon change control, and release stewardship are
project-governance questions. They must not be inferred from Commerce
`CHALLENGE` or `ADJUDICATE` semantics.

## 7. Status

The maintained value of this document is the boundary between portable records
and real institutions. ARC can preserve causal challenge/adjudication evidence
and recompute a profile-relative view; it cannot manufacture legitimate
governance or enforce the result.

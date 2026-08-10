# ARC Protocol: Contextual Reputation and Current Standing

> **Status:** Non-normative Commerce application research
>
> Reputation is not an ARC authority primitive, a global score, or objective
> truth. This document describes contextual evidence and named Current Standing
> Projections learned from the Commerce research.

## 1. Scope

A reputation result is a named application Projection over supplied claims and
evidence. It is not canonical truth and does not grant authority by itself.

In a multi-principal interaction, Buyer Agent and Seller Agent may each inspect
different evidence and compute different local views. ARC does not force either
party to accept the other's cached label or authority profile.

The base ARC model does not prescribe:

- a score or ranking formula;
- a universal person-level reputation;
- a marketplace or discovery backend;
- shared acceptance of another community's result;
- a Sybil-resistant identity system; or
- a governance institution that validates outcomes.

## 2. Evidence Before Scores

An application may receive signed claims about offers, payments, fulfillment,
disputes, refunds, or adjudications. A record can establish who signed certain
bytes under a declared verification boundary. It does not prove that the
external event happened, that the claim is complete, or that the signer is an
independent actor.

A reputation Projection should therefore identify:

- its Event/evidence set and observer surface;
- the profile and version of its rules;
- the identity and verification assumptions used;
- the `as_of` time and any declared causal ordering;
- missing, rejected, contested, or unverified evidence; and
- the context for which the output is intended.

## 3. Contextual, Policy-Relative Output

The same evidence can support different readings for different contexts. A
delivery-reliability view, high-value payment-risk view, and local service view
need not share weights or thresholds.

Applications should avoid presenting one scalar as objective worth. If a score
or label is used, the interface should disclose its context, recency, evidence
surface, limitations, and policy identity.

Reputation does not prove future behavior. A strong past result cannot replace
current authority, exact approval, application policy, or target enforcement.

## 4. Possible Inputs, Not Protocol Requirements

Historical Commerce research considered inputs such as:

- completed or disputed interaction claims;
- delivery or response-time claims;
- refunds and remediation claims;
- challenge and adjudication records;
- key compromise or rotation evidence; and
- evidence age and context similarity.

These are candidate application inputs. ARC does not define their truth,
weights, decay, recovery, or legal significance.

## 5. Portability and Federation

Portable evidence can let a receiver recompute a local view rather than accept
another platform's cached score. That is a technical option, not evidence that
receivers will exchange or honor the records.

Importing reputation can also import:

- fabricated or selectively disclosed history;
- incompatible identity and verification assumptions;
- collusion or Sybil activity;
- governance decisions the receiver does not recognize; and
- privacy and retention obligations.

A receiving profile may accept, discount, quarantine, or reject imported
evidence. There is no universal ARC federation policy.

## 6. Manipulation and Failure Modes

Important threats include:

- one principal operating many apparently independent agents;
- reciprocal or wash interactions;
- selective omission of negative evidence;
- evidence laundering across communities;
- strategic disputes or adjudicator capture;
- retaliatory ratings or challenges after refusal or an unfavorable outcome;
- compromised keys continuing to emit claims;
- stale cached results after new evidence;
- ranking feedback loops that entrench incumbents; and
- UI compression that hides uncertainty.

Signatures alone do not solve these problems. Detection heuristics are
application policy and can produce false positives or exclusion.

## 7. Privacy and Display

Recomputation and auditability can conflict with privacy and deletion needs.
Applications should minimize exposed transaction details, distinguish public
from restricted observer surfaces, and avoid implying that inspectable records
are harmless to publish.

A display should not label a person or agent simply “trusted.” More bounded
language identifies the named view, context, evidence date, missing data, and
whether the result is contested.

## 8. Relationship to Governance and Authority

Governance records may be inputs to a reputation Projection, but the Projection
does not establish the legitimacy of the institution. Reputation may inform
application policy, but it does not create delegated authority. Current
Coverage asks whether current authority evidence covers an action; Current
Standing is a contextual application reading about supplied counterparty
evidence. They answer different questions.

## 9. Historical Designs Removed from Current Scope

Earlier drafts contained detailed velocity, decay, recovery, discovery-ranking,
penalty, and display proposals. No evidence established those policies as safe,
necessary, or adoptable, and no production reputation service was built. The
details remain in Git history and the local historical snapshot.

## 10. Status

The retained conclusion is narrow: signed evidence and named Projections can
make a contextual Current Standing reading more inspectable and recomputable
under declared inputs while preserving missing or contested evidence. This is
an executable research property, not a universal trust result. Broad adoption
remains unproved but is not a prerequisite for the research value of the model.

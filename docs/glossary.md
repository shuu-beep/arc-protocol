# ARC Protocol: Glossary

> **Status:** Research glossary
>
> **Purpose:** Distinguish ARC authority vocabulary from application and
> historical Commerce vocabulary.

This glossary is explanatory, not normative. Foundational meanings belong to
[object-model.md](../docs/object-model.md),
[event-registry.md](../docs/event-registry.md),
[authority-and-conflict.md](../docs/authority-and-conflict.md), and
[delegation-and-spending-mandates.md](../docs/delegation-and-spending-mandates.md).

## Core Authority Vocabulary

### Relationship

The context within which Events are interpreted. A Relationship does not prove
that every relevant Event has been supplied or that its participants accept one
authority profile.

### Event

An immutable signed record with an Event type, author, subject, timestamp,
payload, references, and optional `nullifies` links. Signature or structural
validity does not by itself establish authority, execution, or external truth.

### Event set

The exact set of Events supplied to a computation. Different Event sets may
produce different results; a result therefore identifies its inputs rather than
claiming access to a complete global history.

### Canon

The stable foundational Event vocabulary and object-model constraints. ARC's
five Event types are `KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`, and
`ADJUDICATE`. Withdrawal and key revocation are expressed through existing
Event predicates, payload/profile rules, causal references, and `nullifies`;
they are not additional Canon Event types. Application messages and lifecycle
states are not additional Canon Event types.

### Reference

A causal link from one Event to another. A timestamp alone is not treated as a
total causal order.

### Nullification

An Event's explicit claim that a prior Event no longer applies under a declared
profile. Whether the nullifier is authorized, ordered, and current must still be
evaluated.

### Principal

The human, organization, or external entity on whose behalf authority is
claimed. ARC records can name principals or keys but do not independently prove
legal identity or ownership.

### Agent or delegate

An automated or human-operated actor that may act under authority attributed to
a principal. One principal may control multiple agent keys; signatures do not
prove independent actors.

### Authority profile

A named set of rules declaring whose authority is recognized, how causal and
key-lifecycle evidence is read, and what counts as current coverage. ARC does
not define a universal authority of last resort.

### Current Coverage

A Projection result that reports whether supplied evidence covers a requested
action under a named profile and `as_of` value. It is evidence for an
application decision, not the decision itself.

### Scoped mandate

An `AUTHORIZE` record delegating a bounded class of actions. A delegate may
narrow but must not widen the principal's scope. Delegate identity, action,
resource, constraints, and validity interval remain part of coverage.

### Exact approval

An `AUTHORIZE` record bound to one exact reviewable action or request material.
Changing a bound field requires a different approval. One-time consumption and
atomic dispatch are application-enforcement concerns, not Projection status.

### Narrowing

Reducing delegated scope, amount, environment, validity, or another declared
constraint. A delegation chain must not silently widen authority.

### Validity interval

The declared `not_before` and/or expiry boundary of authority evidence. Current
Coverage is evaluated at an explicit `as_of` value.

### Withdrawal

A causal authority record that seeks to nullify earlier authority. The mere
presence of a later timestamp is insufficient; author, key lineage, references,
and the selected profile matter.

### Contested

A preserved result when supplied authority evidence conflicts without an
accepted causal/profile resolution. `CONTESTED` must not be silently converted
to a timestamp winner or ordinary `DENY` if the declared Projection promises to
preserve the disagreement.

### Adjudication

An `ADJUDICATE` record expressing a resolution by an authority recognized by a
profile. It records the decision and causal relation; it does not prove legal
validity, institutional legitimacy, or the external facts of a dispute.

### Projection

Derived state computed from a declared Event set, profile, ordering context,
verification results, and `as_of` value. Projection output is reproducible only
to the extent those inputs and rules are available.

### Projection identity

An identity binding a result to its declared computation inputs. It helps
detect stale or substituted results but does not guarantee that evidence was
complete or independently obtained.

### Verification boundary

The checks actually performed, such as structural validation, signature
verification, key provenance, or external credential lookup. A stronger claim
must not be inferred from a weaker boundary.

### Evidence completeness

A declared contract about which relevant records were expected and supplied.
ARC cannot infer global completeness from a local Event set.

## Application and Historical Research Vocabulary

The following terms are useful in examples but are not ARC primitives.

### Gate decision

An application result such as `ALLOW`, `DENY`, or `REQUIRE_APPROVAL` produced
after combining authority evidence with application policy. ARC Reference Core
does not issue Gate decisions.

### Human approval

An application workflow that authenticates an approver and produces authority
evidence. ARC does not provide the UI, channel security, identity proofing, or
consumption transaction.

### Consumer, merchant, and logistics agent

Roles used by the Commerce application profile and historical design work. They
do not define general agent types or protocol conformance.

### Governance

Institutional processes that decide who may adjudicate and how disputes are
handled. ARC can record challenge/adjudication evidence but does not create a
legitimate institution.

### Reputation

A contextual named Projection over claims and evidence. It is not objective
truth, universal worth, or a required authority primitive.

### Discovery and sponsored discovery

Application infrastructure for finding or ranking providers, including paid
visibility. ARC defines no discovery backend or ranking policy.

### Fulfillment and verified transaction

Commerce lifecycle labels. A verified record about payment or fulfillment does
not prove that the external event occurred as claimed.

### Approval fatigue

The application UX risk that repeated prompts become automatic and cease to
represent meaningful attention. ARC semantics do not solve this risk.

### Trust boundary

A boundary where assumptions, operators, credentials, or verification strength
change. Deployments must disclose and enforce these boundaries; ARC records do
not automatically secure them.

## Status

This glossary records vocabulary used by the current research corpus. Future
normative terminology or conformance work requires explicit layer and review
boundaries.

# ARC Commerce Application: Dispute Evidence Flow

> **Status:** Non-normative application diagram
> **Purpose:** Separate ARC challenge/adjudication records and recomputation
> from the institutions that investigate facts and enforce remedies.

```mermaid
sequenceDiagram
    participant A as Claimant Agent
    participant B as Counterparty Agent
    participant R as ARC-aware Application
    participant J as Profile-recognized Adjudicator
    participant E as External Enforcement

    A->>R: signed evidence or outcome claim
    R->>B: notice and request for response
    B->>R: response and supporting evidence
    A->>R: CHALLENGE referencing disputed records
    Note over R,J: Evidence collection, identity checks, procedure, and jurisdiction are external
    R->>J: declared Event set and application case material
    J->>R: authorized ADJUDICATE referencing the challenge
    R->>R: recompute named Projection with profile and as_of
    R-->>A: updated Current Standing / dispute view
    R-->>B: updated Current Standing / dispute view
    R->>E: optional refund, chargeback, suspension, or legal remedy request
    Note over E: Real enforcement is not created by the ARC record
```

## Boundary

- `CHALLENGE` records a signed contest; it does not prove the claimant is right.
- `ADJUDICATE` records a decision by an authority recognized under a named
  profile; it does not create institutional or legal legitimacy.
- Conflicting or causally unresolved records may remain `CONTESTED`.
- A later recognized adjudication may change a named Projection without erasing
  the earlier evidence.
- Appeals may be represented as a new `CHALLENGE` referencing a prior
  `ADJUDICATE`, but notice, deadlines, review bodies, and appeal rights belong to
  the external institution.
- Refunds, chargebacks, contractual remedies, account suspension, and legal
  enforcement remain application, payment-provider, marketplace, contractual,
  regulatory, or court responsibilities.

See [Governance](../docs/governance.md),
[Reputation](../docs/reputation.md), and
[Liability Boundaries](../docs/liability-boundaries.md).

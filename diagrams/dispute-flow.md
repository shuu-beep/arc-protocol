# ARC Commerce Reference Application: Dispute Flow

> **Purpose:** Visual reference for Commerce application dispute initiation, review, and resolution
> Record checks in this diagram are illustrative application checks, not outcome proof.
> For governance detail, see [docs/governance.md](../docs/governance.md).
> For reputation effects, see [docs/reputation.md](../docs/reputation.md).

## Flow Diagram

```mermaid
flowchart TD
    A["User or merchant\nfiles dispute report"] --> B["Transaction records retrieved;\nprofile checks run"]
    B --> C{"Required records\navailable?"}

    C -->|"Yes"| D["Both parties notified\nResponse period opens"]
    C -->|"No"| E["Evidence insufficient\nReport flagged for review"]

    D --> F["Community moderators\nreview evidence"]
    E --> F

    F --> G{"Moderator\ndecision"}

    G -->|"Dismissed"| H["resolved_no_fault\nReporter pattern may be reviewed"]
    G -->|"Minor issue"| I["resolved_partial_refund\nStanding input recorded"]
    G -->|"Material violation"| J["resolved_full_refund\nStanding input recorded"]
    G -->|"Fraud determination"| K["resolved_fraud_finding\nSuspension or ban initiated"]

    H --> L["Profile-defined\nappeal window opens"]
    I --> L
    J --> L
    K --> L

    L --> M{"Appeal\nfiled?"}

    M -->|"No"| N["Application decision and\nstanding input recorded"]
    M -->|"Yes"| O["Appeal reviewed\nby broader community"]

    O --> P{"Appeal\noutcome"}

    P -->|"Upheld"| Q["Revised application\ndecision recorded"]
    P -->|"Rejected"| N

    Q --> N
    N --> [*]
```

## Notes

- Under this Commerce application policy, evidence quality affects decision weight. Unsigned claims and anonymous accusations without corroborating records may be insufficient under that policy.
- A dismissed or unsupported report causes no automatic reporter penalty. Repeated or knowingly abusive reporting, when established through a reviewable governance decision under this policy, may contribute evidence to a reporter-related reputation Projection.
- An adjudicated fraud finding may trigger cross-community governance review under the selected policy.
- Appeal paths remain open regardless of initial decision direction.
- This flow is exploratory. Communities may adapt timelines and thresholds under local Commerce application policy.

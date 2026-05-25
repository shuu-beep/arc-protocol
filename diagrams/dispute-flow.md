# ARC Protocol: Dispute Flow

> **Purpose:** Visual reference for dispute initiation, review, and resolution
> For governance detail, see [docs/governance.md](../docs/governance.md).
> For reputation effects, see [docs/reputation.md](../docs/reputation.md).

## Flow Diagram

```mermaid
flowchart TD
    A["User or merchant\nfiles dispute report"] --> B["Transaction log\nretrieved and verified"]
    B --> C{"Signed records\navailable?"}

    C -->|"Yes"| D["Both parties notified\nResponse period opens"]
    C -->|"No"| E["Evidence insufficient\nReport flagged for review"]

    D --> F["Community moderators\nreview evidence"]
    E --> F

    F --> G{"Moderator\ndecision"}

    G -->|"Dismissed"| H["resolved_no_fault\nReporter pattern may be reviewed"]
    G -->|"Minor issue"| I["resolved_partial_refund\nReputation note added"]
    G -->|"Confirmed harm"| J["resolved_full_refund\nReputation signal recorded"]
    G -->|"Confirmed fraud"| K["resolved_confirmed_fraud\nSuspension or ban initiated"]

    H --> L["Appeal window opens\n7 days default"]
    I --> L
    J --> L
    K --> L

    L --> M{"Appeal\nfiled?"}

    M -->|"No"| N["Decision finalized\nReputation event recorded"]
    M -->|"Yes"| O["Appeal reviewed\nby broader community"]

    O --> P{"Appeal\noutcome"}

    P -->|"Upheld"| Q["Decision revised\nReputation adjusted"]
    P -->|"Rejected"| N

    Q --> N
    N --> [*]
```

## Notes

- Evidence quality affects decision weight. Unsigned claims and anonymous accusations without corroborating records are not treated as valid evidence.
- False reports may affect the reporter's own reputation signal.
- `resolved_confirmed_fraud` may trigger cross-community governance review in serious cases.
- Appeal paths remain open regardless of initial decision direction.
- This flow is exploratory. Communities may adapt timelines and thresholds within protocol guidelines.

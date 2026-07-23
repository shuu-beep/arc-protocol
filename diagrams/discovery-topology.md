# ARC Commerce Reference Application: Discovery Topology

> **Purpose:** Visual reference for the Commerce flagship application's multi-backend discovery policy
> This diagram describes application policy, not ARC Canon.
> For discovery layer detail, see [docs/architecture.md](../docs/architecture.md).
> For sponsored discovery and manipulation risks, see [docs/threat-model.md](../docs/threat-model.md).

## Topology Diagram

```mermaid
flowchart LR
    U["Human User"] --> CA["Consumer Agent"]

    CA --> DB1["Local Community\nRegistry"]
    CA --> DB2["External Map\nProvider"]
    CA --> DB3["Reputation-Weighted\nIndex"]
    CA --> DB4["Category Directory\nfood · logistics · services"]

    DB1 --> MA1["Merchant Agent A\nlocal registry signal"]
    DB2 --> MA2["Merchant Agent B\nmap-listed"]
    DB3 --> MA3["Merchant Agent C\nreputation inputs available"]
    DB4 --> MA4["Merchant Agent D\ncategory-specific"]

    DB1 -. "sponsored: disclosed" .-> MA1
    DB3 -. "sponsored: disclosed" .-> MA3

    CA --> SWITCH["Optional backend\nselection"]
    SWITCH --> DB1
    SWITCH --> DB3

    CA --> FILTER["User-defined filters\nreputation threshold\ncategory\ngeography"]
    FILTER --> CA
```

## Notes

- Within this Commerce profile, any discovery backend may include sponsored placement only when it is disclosed under that application policy.
- This Commerce profile models user-selectable backends. That is an application backend-choice policy, not ARC Canon.
- No single backend is mandatory or canonical within this illustrative profile.
- Reputation indexes and local registries may overlap. The consumer agent may query multiple sources.
- This topology is illustrative. Real deployments may vary based on community and region.

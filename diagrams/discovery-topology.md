# ARC Protocol: Discovery Topology

> **Purpose:** Visual reference for ARC's multi-backend discovery model
> For discovery layer detail, see [docs/architecture.md](../docs/architecture.md).
> For sponsored discovery and manipulation risks, see [docs/threat-model.md](../docs/threat-model.md).

## Topology Diagram

```mermaid
flowchart LR
    U["Human User"] --> CA["Consumer Agent"]

    CA --> DB1["Local Community\nRegistry"]
    CA --> DB2["Map Provider\nGoogle Maps · Naver · OSM"]
    CA --> DB3["Reputation-Weighted\nIndex"]
    CA --> DB4["Category Directory\nfood · logistics · services"]

    DB1 --> MA1["Merchant Agent A\nverified · local"]
    DB2 --> MA2["Merchant Agent B\nmap-listed"]
    DB3 --> MA3["Merchant Agent C\nverified reputation signals"]
    DB4 --> MA4["Merchant Agent D\ncategory-specific"]

    DB1 -. "sponsored: disclosed" .-> MA1
    DB3 -. "sponsored: disclosed" .-> MA3

    CA --> SWITCH["User can switch\ndiscovery backend"]
    SWITCH --> DB1
    SWITCH --> DB3

    CA --> FILTER["User-defined filters\nreputation threshold\ncategory\ngeography"]
    FILTER --> CA
```

## Notes

- Any discovery backend may include sponsored placement, but disclosure is required.
- Users may switch backends freely. This is a core anti-monopoly design feature.
- No single backend is mandatory or canonical.
- Reputation indexes and local registries may overlap. The consumer agent may query multiple sources.
- This topology is illustrative. Real deployments may vary based on community and region.

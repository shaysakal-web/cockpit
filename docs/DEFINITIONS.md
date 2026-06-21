# Cockpit Run Desk — definitions

Unified hub for analytics run desks. Each **world** is a registered project in [`config/projects.json`](../config/projects.json).

## Worlds (v1)

| World | Project folder | Primary metrics |
|-------|----------------|-----------------|
| Svelte retention | [Svelte subscription analysis](../../Svelte subscription analysis) | Take rates, upsell monitors, retention rollups |
| Funnel QA | [funny funnel qa](../../bmad/funny funnel qa) | Funnel integrity, CRM vs S2S, conversion monitor |
| Data quality | [Data quality](../../Data quality) | CRM product mapping, new accounts mapping, landing page vs sheet |

See sibling project docs for domain-specific terms.

## Run Desk terms

- **World tab** — top-level project selector in the UI
- **Segment sub-tab** — category within a world (Daily monitors, Funnel QA, Reports, …)
- **Registry** — JSON job list under `registry/`; Cockpit runs scripts in the project root via subprocess

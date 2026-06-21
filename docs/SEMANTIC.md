# Cockpit — semantic layer

Cockpit does not own warehouse tables. It delegates to sibling projects:

- **Svelte retention** — subscription cohorts, upsell monitors, Accounts deliverables. See [SEMANTIC.md](../../Svelte subscription analysis/docs/SEMANTIC.md).
- **Funnel QA** — S2S funnel rows, CRM reconciliation, conversion monitor. See [SEMANTIC.md](../../bmad/funny funnel qa/docs/SEMANTIC.md).
- **Data quality** — CRM product mapping, unified account mapping, landing page sheet sync. See [project-context.md](../../Data quality/docs/project-context.md).

When adding a new world, link its semantic doc here and register report roots in `config/projects.json`.

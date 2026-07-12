# AGENT_ROLES.local.md — Cockpit Run Desk hooks

```yaml
pipeline_version: "10-phase-v4"   # must match docs/PIPELINE_MANIFEST.md in cursor-analytics-pipeline
```

## Run Desk

| Action | Command |
|--------|---------|
| Open unified Run Desk | `.\start_run_desk.ps1` from Cockpit root |
| Manual server | `python webui\server.py --open` |
| Register bookmark protocol | `powershell -File scripts\register_run_desk_protocol.ps1` |

## Registered worlds

| World | Config | Registry | Sibling docs |
|-------|--------|----------|--------------|
| Svelte retention | `config/projects.json` → `svelte-retention` | `registry/svelte-retention.json` | `../Svelte subscription analysis/docs/` |
| Funnel QA | `config/projects.json` → `funny-funnel-qa` | `registry/funny-funnel-qa.json` | `../bmad/funny funnel qa/docs/` |
| Data quality | `config/projects.json` → `data-quality` | `registry/data-quality.json` | `../Data quality/docs/` |

## Key scripts (delegated — run via Run Desk UI or sibling project CLI)

**Svelte retention** — see [Svelte AGENT_ROLES.local.md](../../Svelte subscription analysis/docs/AGENT_ROLES.local.md)

**Funnel QA**

| Script | Run Desk job id |
|--------|-----------------|
| `python/run_qa.py` | `subscription_funnel_qa` |
| `python/daily_conversion_monitor.py` | `daily_conversion_monitor` |

**Data quality**

| Script | Run Desk job id |
|--------|-----------------|
| `scripts/core/data_quality_runner.py` + `crm-products.yml` | `dq_crm_products` — scope: `crm IN ('digistore24', 'paddle')` |
| `scripts/core/data_quality_runner.py` + `new-accounts.yml` | `dq_new_accounts` |
| `scripts/checks/run_landing_page_qa.py` | `dq_landing_page` |

## Domain skill

`.cursor/skills/cockpit-run-desk/SKILL.md`

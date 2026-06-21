---
name: cockpit-run-desk
description: Unified Run Desk hub — multi-world launcher, registry, and navigation. Use when working in Cockpit or adding jobs/worlds to the desk.
---

# Cockpit Run Desk

## Purpose

Single local web UI (`webui/server.py`) that runs analyses from registered sibling projects without moving their code.

## Key paths

| Path | Role |
|------|------|
| `config/projects.json` | World list + absolute paths |
| `registry/*.json` | Job definitions per world |
| `webui/index.html` | Option B UI (world + segment tabs) |
| `start_run_desk.ps1` | Canonical launcher |

## Add a job

1. Edit the world's registry JSON (`registry/svelte-retention.json` or `registry/funny-funnel-qa.json`).
2. Restart Run Desk.

## Add a world

1. Add project entry to `config/projects.json`.
2. Create `registry/<world>.json`.
3. Restart Run Desk.

## v1 worlds

- **svelte-retention** — 17 jobs from Svelte subscription analysis
- **funny-funnel-qa** — subscription funnel QA + daily conversion monitor
- **data-quality** — CRM product mapping, new accounts mapping, landing page vs Google Sheet

## Open desk

```powershell
cd "C:\Users\Shay.Sakal\Documents\Cursor\Cockpit"
.\start_run_desk.ps1
```

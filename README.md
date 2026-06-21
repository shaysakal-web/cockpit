# Cockpit — Unified Run Desk

One local web desk for all analytics worlds: **Svelte retention**, **Subscription funnel QA**, **Data quality**, and more as you add them.

## Quick start

Double-click **`Open Run Desk.vbs`** or run:

```powershell
cd "C:\Users\Shay.Sakal\Documents\Cursor\Cockpit"
.\start_run_desk.ps1
```

Opens **http://127.0.0.1:8765/** with world tabs (Option B navigation):

- **World tab** — Svelte retention | Funnel QA | Data QA | All
- **Segment sub-tab** — Daily monitors, Rollups, Funnel QA, Reports, etc.
- **Sidebar** — runnable jobs for the active world only

## Layout

```
Cockpit/
├── config/projects.json      # registered sibling projects (edit paths here)
├── registry/                 # per-world job definitions
├── webui/server.py           # multi-project HTTP server
├── webui/index.html          # unified UI
└── start_run_desk.ps1        # launcher
```

## Adding a world

1. Add an entry to [`config/projects.json`](config/projects.json) with `root`, `registry`, and `report_roots`.
2. Add [`registry/<world>.json`](registry/) with `analyses` entries (same shape as Svelte Run Desk).
3. Restart Run Desk.

Analysis code, SQL, and `.env` stay in each sibling project folder — Cockpit only launches subprocesses with `cwd` set to that project root.

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `ANALYSIS_WEB_PORT` | `8765` | Listen port |
| `ANALYSIS_WEB_TOKEN` | _(unset)_ | Bearer token for `POST /api/run` |
| `ANALYSIS_RUN_TIMEOUT_SEC` | `7200` | Subprocess timeout |

## Legacy launchers

- **Svelte** `start_run_desk.ps1` delegates to Cockpit.
- **funny funnel qa** `qa_runner_web.py` is deprecated — use Cockpit Funnel QA world tab.

## Docs

- [webui/README.md](webui/README.md) — API routes and registry format
- Sibling project docs: Svelte `docs/`, funny funnel qa `docs/`

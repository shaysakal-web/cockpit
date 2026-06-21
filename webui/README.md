# Cockpit Run Desk — Web UI

Local browser UI to run analyses from multiple registered projects.

## Start

From Cockpit root:

```powershell
python webui\server.py --open
```

Or use `start_run_desk.ps1` (recommended).

## API

| Route | Description |
|-------|-------------|
| `GET /api/analyses` | Merged registry + `projects` list |
| `GET /api/dashboard?project=<id\|all>` | Job cards and reports |
| `GET /api/reports?project=<id\|all>` | Report index |
| `POST /api/run` | Body: `{ "id", "project_id", "params" }` |
| `GET /artifact?project=&path=` | Serve PDF/HTML/CSV from project report roots |

## Registry entry shape

See [`registry/svelte-retention.json`](../registry/svelte-retention.json) for examples. Each analysis:

- `id`, `label`, `category`, `description`
- `script` — path relative to project root
- `params` — `date`, `text`, `int`, `select`, `checkbox`
- `artifact` — optional inline viewer path with `{report-date}`, `{brand}`, `{date}`, `{date_slug}` placeholders
- `post_run` — optional (e.g. `funnel_narrative_pdf` for subscription QA)

## Configuration

Edit [`config/projects.json`](../config/projects.json) — absolute Windows paths to sibling repos.

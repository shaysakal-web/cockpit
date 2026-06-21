---
name: bring-analytics-team
description: >-
  Bootstrap the ten-phase analytics pipeline into this project. Use when the user
  says bring analytics team to party, add analytics pipeline, setup analytics agents,
  or onboard analytics workflow.
---

Bring the **analytics team** (ten-phase pipeline) into **this project folder**.

## Layer 1 — Personal skills (machine-wide)

1. Check `~/.cursor/skills/` for: `ba-intake`, `data-analyst`, `data-qa`, `data-exploration`, `data-analysis`, `statistical-testing`, `ba-insights`, `analysis-context`, `insight-storytelling`, `executive-review`, `visualization-reporting`
2. If any missing, run from cloned pipeline repo:
   ```powershell
   cd "C:\Users\Shay.Sakal\Documents\Cursor\cursor-analytics-pipeline"
   .\install.ps1
   ```
   Or: `git clone https://github.com/shaysakal-web/cursor-analytics-pipeline.git` then `.\install.ps1`

## Layer 2 — This project folder

Copy from `cursor-analytics-pipeline/project-template/` if files are missing:

| Path | Purpose |
|------|---------|
| `.cursor/commands/analysis-intake.md` | Phase 1 |
| `.cursor/commands/analysis-run.md` | Orchestrator |
| `.cursor/commands/data-pull.md` | Phase 2 |
| `.cursor/commands/data-qa-check.md` | Phase 3 |
| `.cursor/commands/data-exploration-run.md` | Phase 4 |
| `.cursor/commands/data-analysis-run.md` | Phase 5 |
| `.cursor/commands/analysis-insights.md` | Phase 6 |
| `.cursor/commands/analysis-context.md` | Phase 7 |
| `.cursor/commands/insight-storytelling.md` | Phase 8 |
| `.cursor/commands/executive-review.md` | Phase 9 |
| `.cursor/commands/visualization-reporting.md` | Phase 10 |
| `.cursor/commands/bring-analytics-team.md` | This command |
| `docs/AGENT_ROLES.md` | Orchestration |
| `analysis/dedicated/_template/` | Handoff templates |
| `analysis/intake/README.md` | Ad-hoc artifacts |

Or run:
```powershell
cd "C:\Users\Shay.Sakal\Documents\Cursor\cursor-analytics-pipeline"
.\bootstrap-project.ps1 -TargetProject "<absolute path to this workspace>"
```

## Layer 3 — Project-specific (you must add or scaffold)

If missing, create stubs and ask user to fill:

- a domain skill under `.cursor/skills/<any-descriptive-name>/SKILL.md` — domain scripts/paths (e.g. `svelte-retention`, `<project>-funnel-metrics`)
- `docs/DEFINITIONS.md` — formulas
- `docs/SEMANTIC.md` — tables/columns
- `docs/DATA_INTEGRITY_CHECKLIST.md` — QA checks
- `docs/AGENT_ROLES.local.md` — project hooks: task ids, pull commands, publish scripts

## Verify

List what was added vs already present. Confirm slash commands:

`/analysis-intake` · `/analysis-run` · `/data-pull` · `/data-qa-check` · `/data-exploration-run` · `/data-analysis-run` · `/analysis-insights` · `/analysis-context` · `/insight-storytelling` · `/executive-review` · `/visualization-reporting`

## Do not

- Overwrite existing `DEFINITIONS.md` / `SEMANTIC.md` without asking
- Copy Svelte-only commands (`routine-up2-monitor`, etc.) unless user asks

See `docs/AGENT_ROLES.md` and https://github.com/shaysakal-web/cursor-analytics-pipeline

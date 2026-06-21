---
name: data-pull
description: >-
  Data Analyst phase — SQL/Python extraction from intake contract; write pull_manifest.md
  and dated raw outputs. Use for pull data, run SQL, execute task pipeline.
---

Run **phase 2** (Data Analyst). Load skill `data-analyst` + the project's domain skill (see `docs/AGENT_ROLES.local.md`).

## Stop gate (check first)

**STOP and refuse** if `intake_contract.md` is missing or `clarity_status` is not `CLEAR`
(unless the user explicitly overrides for an identical routine rerun). Report what's missing;
do not pull data on a BLOCKED or absent contract.

## Prerequisites

- `intake_contract.md` with `clarity_status: CLEAR` (or explicit user override for identical routine reruns)

## Steps

1. Load `intake_contract.md` — pipeline, task id, cuts, report date
2. Choose pull method per `~/.cursor/skills/data-analyst/workflows/extraction-playbook.md`
3. Follow `sql-playbook.md` for ad-hoc MySQL
4. Run the pipeline (examples):
   - `python scripts/analysis/run_analysis_task.py --task <id> --report-date YYYY-MM-DD`
   - `python scripts/retention/run_schedule_task.py --task <id>`
   - Or project slash command named in intake (`routine-up2-monitor`, etc.)
5. Write `pull_manifest.md` with scripts run, paths, row counts, workflow optimization
6. Confirm outputs use `YYYY-MM-DD_` prefix

## Must not

- Analytical cleaning, driver narratives, stakeholder charts
- Proceed on BLOCKED clarity

## Next phase

`/data-qa-check` when pull complete.

See `docs/AGENT_ROLES.md`.

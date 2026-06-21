---
name: data-analysis-run
description: >-
  Python / Notebook Agent phase — clean data, cohort tables, period compare, drivers,
  statistical validation; write analysis_pack.md. Use after exploration completes.
---

Run **phase 5** (Python / Notebook Agent). Load skill `data-analysis`.

## Stop gate (check first)

**STOP and refuse** if any of:
- `data_qa_report.md` missing or `Ready for analysis` is not `YES`
- `exploration_report.md` missing or `Exploration status` is not `COMPLETE`

Report what's missing; do not analyze without exploration backlog (when phase 4 ran).

## Prerequisites

- `data_qa_report.md` → `Ready for analysis: YES` (**hard stop otherwise**)
- `exploration_report.md` → `Exploration status: COMPLETE` (**hard stop when phase 4 in plan**)
- `intake_contract.md`
- Files from `pull_manifest.md`

## Steps

1. Confirm QA and exploration gates passed
2. Load intake + validated pull paths + `exploration_report.md`
3. Prioritize work from § Recommended next investigations (observation ids)
4. Per `~/.cursor/skills/data-analysis/workflows/notebook-playbook.md`:
   - Clean data (document; do not overwrite pulls)
   - Cohort tables
   - Period comparison
   - Driver isolation
   - Statistical validation (load `statistical-testing`; inferential comparisons only)
   - Optional diagnostic plots in `tables/` only
5. Write `analysis_pack.md` using template in `analysis/dedicated/_template/`
6. Summarize outputs; flag gaps for Executive Insight

## Must not

- Stakeholder publication charts, PPT, PDF (phase 10)
- Skip QA or exploration gates
- Parallel fishing outside exploration backlog

## Next phase

`/analysis-insights` when pack complete.

See `docs/AGENT_ROLES.md`.

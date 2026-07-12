---
name: chart-maker-run
description: >-
  Phase 10a — render publication charts from chart_specs.yaml using lib/chart_helpers.py
  (SWD style, collision check, PNG+SVG). Requires executive review PASS.
---

Run **phase 10a** (Chart Maker). Load skill `visualization-reporting` workflow § Chart maker.

## Stop gate (check first)

**STOP and refuse** if any of:
- `executive_review.md` missing or `Review status: REVISE`
- `chart_specs.yaml` missing
- `story_brief.md` missing
- `analysis_pack.md` missing

## Prerequisites

- `executive_review.md` → `Review status: PASS`
- `chart_specs.yaml`
- `story_brief.md`
- `analysis_pack.md`
- `data_qa_report.md` → `Ready for analysis: YES`
- Study data files referenced in chart specs exist under study folder

## Steps

1. Read `chart_specs.yaml` — one chart per entry
2. For each spec:
   - Load data (CSV/parquet under study `tables/`)
   - Validate columns (`x`, `y`, `color_by` if set); halt on missing columns
   - Drop null rows in axis columns; warn in subtitle if >20% dropped
   - Apply `lib/chart_helpers.py`: `swd_style()`, chart-type helpers, `action_title()`
   - Y-axis: follow `.cursor/rules/chart-axis-standards.mdc` (percent vs count, Y from 0)
   - Date x-axis: call `format_date_axis(ax)`
   - Run SWD declutter checklist (`docs/CHART_STYLE.md`)
   - **Collision check (hard halt):** `check_label_collisions(fig, ax, fix=True)` up to 3 attempts
   - Save `charts/{id}.png` + `.svg`; write `charts/{id}.meta.json` (title, type, nulls dropped, pack ref)
3. If `design_review.md` exists with fix report from a prior 10b run, apply fixes only for listed charts

## Must not

- Change numbers vs `analysis_pack.md`
- Save charts with unresolved label collisions
- Skip executive review gate
- Rewrite `story_brief.md` or `analysis.md`

## Output

- `charts/*.png`, `charts/*.svg`, `charts/*.meta.json`

## Next

`/chart-design-review` (phase 10b)

See `docs/CHART_STYLE.md` and `docs/AGENT_ROLES.md`.

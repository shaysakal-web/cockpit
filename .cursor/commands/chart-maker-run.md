---
name: chart-maker-run
description: >-
  Phase 10a — render publication charts from chart_specs.yaml using lib/chart_helpers.py
  (SWD style, collision check, PNG+SVG). Renders in parallel worker batches for 3+ charts.
  Requires executive review PASS.
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

## Execution mode

- **3+ specs and subagent dispatch available** → parallel batch dispatch (below)
- **2 or fewer specs, or dispatch unavailable** → render inline: run the per-chart steps
  yourself for each spec, in order
- **10b fix-loop re-runs** (specific charts listed in a `design_review.md` fix report) →
  always inline; apply fixes only for the listed charts

## Parallel batch dispatch

**Batching rule:** with N specs, assign `ceil(N/3)` specs per batch — **max 3 worker
subagents**, launched in parallel. Each worker renders its charts **sequentially within
its batch**. Never one worker per chart.

Each worker is a Task subagent (`generalPurpose`) whose prompt contains:

- The absolute study folder path and the worker's assigned spec ids from `chart_specs.yaml`
- Skill reference: `~/.cursor/skills/visualization-reporting/workflows/charts-and-deck-playbook.md` § Chart maker
- The **per-chart steps** below, verbatim
- **Write-scope rule (verbatim):** write only `charts/{id}.png`, `charts/{id}.svg`, and
  `charts/{id}.meta.json` for your assigned spec ids. Never touch other charts, study
  artifacts, or data files. Write `{id}.meta.json` **last** for each chart.
- **Return contract:** list per spec id — rendered OK, or failed (with reason, e.g.
  unresolved collision halt after 3 fix attempts)

## Per-chart steps (inline or inside each worker)

1. Load data (CSV/parquet under study `tables/`)
2. Validate columns (`x`, `y`, `color_by` if set); halt on missing columns
3. Drop null rows in axis columns; warn in subtitle if >20% dropped
4. Apply `lib/chart_helpers.py`: `swd_style()`, chart-type helpers, `action_title()`
5. Y-axis: follow `.cursor/rules/chart-axis-standards.mdc` (percent vs count, Y from 0)
6. Date x-axis: call `format_date_axis(ax)`
7. Run SWD declutter checklist (`docs/CHART_STYLE.md`)
8. **Collision check (hard halt):** `check_label_collisions(fig, ax, fix=True)` up to 3 attempts
9. Save `charts/{id}.png` + `.svg`; write `charts/{id}.meta.json` (title, type, nulls dropped, pack ref) **last**

## After all workers return — validity verification (parent)

Verify **validity, not just presence**, for every spec id:

- All three files exist: `charts/{id}.png`, `charts/{id}.svg`, `charts/{id}.meta.json`
- Each file is non-zero; PNG is **at least 1 KB** (catches zero-byte and stub renders)
- `{id}.meta.json` parses as valid JSON with the expected title and pack-ref keys
  (it is written last, so valid meta = the worker completed its full routine)

Any check failing marks that spec id **failed regardless of the worker's return message**.
Also failed: any spec a worker reported as an unresolved collision halt.

**Re-run failed specs per-spec-id, never per-batch:** re-render inline exactly the failed
spec ids; charts that passed verification are never re-rendered. Do not proceed to 10b
until every spec id passes verification (or halt and report the specs that cannot render).

## Must not

- Change numbers vs `analysis_pack.md`
- Save charts with unresolved label collisions
- Skip executive review gate
- Rewrite `story_brief.md` or `analysis.md`
- Spawn more than 3 workers, or re-render an entire batch for one failed chart

## Output

- `charts/*.png`, `charts/*.svg`, `charts/*.meta.json`

## Next

`/chart-design-review` (phase 10b)

See `docs/CHART_STYLE.md` and `docs/AGENT_ROLES.md` § Parallel execution.

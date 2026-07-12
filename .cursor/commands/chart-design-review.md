---
name: chart-design-review
description: >-
  Phase 10b — visual design review of rendered charts (SWD + axis standards).
  Writes design_review.md with PASS or fix report for chart-maker re-run.
---

Run **phase 10b** (Visual Design Review). Load skill `visualization-reporting` workflow § Design review.

## Stop gate (check first)

**STOP and refuse** if:
- No PNG files in study `charts/` folder
- `chart_specs.yaml` missing

## Prerequisites

- Phase 10a complete — charts in `charts/`
- `chart_specs.yaml`
- `story_brief.md` (for title differentiation check)

## Steps

1. Read each chart PNG in `charts/` (match to `chart_specs.yaml` ids)
2. Run per-chart checklist (`docs/CHART_STYLE.md` + axis standards):
   - Spines, grid, legend vs direct labels, action title, colors (max 2 + gray)
   - Percent vs count axis, Y from 0, no P1+P2 combined
   - Title differs from story beat headline when beat is narrative-only
   - Label collisions / readability
3. Spot-check ≥3 data points vs `analysis_pack.md`
4. Write `design_review.md` from template with Verdict:
   - **PASS** — all charts OK
   - **APPROVED_WITH_FIXES** — specific fix instructions per chart
   - **NEEDS_REVISION** — wrong chart type or misleading; escalate to insight-storytelling
5. On APPROVED_WITH_FIXES: re-run `/chart-maker-run` for listed charts only, then re-run 10b

## Must not

- Change analysis or story artifacts
- PASS with known unresolved collisions or pack mismatches

## Gate

Phase 10c requires `design_review.md` → `Verdict: PASS`

## Next

`/visualization-reporting` (phase 10c)

See `docs/AGENT_ROLES.md`.

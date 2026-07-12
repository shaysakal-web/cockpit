---
name: visualization-reporting
description: >-
  Phase 10c — assemble HTML/PDF/PPT from story_brief and rendered charts; write
  deliverables_manifest.md. Requires chart-maker-run and chart-design-review PASS.
---

Run **phase 10c** (Visualization & Reporting — assembly). Load skill `visualization-reporting`.

## Stop gate (check first)

**STOP and refuse** if any of:
- `design_review.md` missing or `Verdict` is not `PASS`
- `executive_review.md` missing or `Review status: REVISE`
- `story_brief.md` missing
- Charts missing in `charts/` when `chart_specs.yaml` lists entries

## Prerequisites

- Phase **10a** complete (`/chart-maker-run`)
- Phase **10b** complete — `design_review.md` → `Verdict: PASS`
- `story_brief.md`, `chart_specs.yaml`, `analysis_pack.md`
- `executive_review.md` → `Review status: PASS`

## Steps

1. Load story from `story_brief.md` (slide order); embed charts from `charts/`; numbers from `analysis_pack.md`
2. Per `~/.cursor/skills/visualization-reporting/workflows/charts-and-deck-playbook.md` § Assembly:
   - Key findings → exec summary / priority cards
   - Must address → appendix section
   - HTML/PDF in `reports/`
   - PPT in `presentations/` if requested
3. Prefer project chart/PPT/PDF scripts when they fit (`docs/AGENT_ROLES.local.md`)
   - **Svelte monthly pack:** `build_monthly_pack_html.py --month <MONTH> --report-date <DATE> --pdf`
4. Write `deliverables_manifest.md` — map every asset to chart_spec id, slide #, pack ref, design_review PASS

## Must not

- Regenerate charts (use 10a/10b outputs; escalate fixes to `/chart-maker-run`)
- Change metrics, rerun SQL, rewrite `analysis.md` or `story_brief.md`
- Skip design review gate

## Next

`/deliverables-qa-check` (phase 10d)

See `docs/AGENT_ROLES.md`.

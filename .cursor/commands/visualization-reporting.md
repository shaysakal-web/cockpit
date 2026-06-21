---
name: visualization-reporting
description: >-
  Visualization & Reporting Analyst phase — stakeholder charts, HTML/PDF, PowerPoint from
  story_brief.md, analysis.md, and analysis_pack; write deliverables_manifest.md.
---

Run **phase 10** (Visualization & Reporting Analyst). Load skill `visualization-reporting`.

## Stop gate (check first)

**STOP and refuse** if any of:
- `executive_review.md` missing or `Review status: REVISE`
- `story_brief.md` missing
- `analysis.md` missing
- `analysis_context.md` missing
- QA is not `YES`

Report what's missing; do not build a deck without review PASS and story brief.

## Prerequisites

- `executive_review.md` → `Review status: PASS` (**hard stop if REVISE or missing**)
- `story_brief.md` (**hard stop if missing**)
- `analysis.md` (**hard stop if missing**)
- `analysis_context.md` → `Context status: COMPLETE`
- `analysis_pack.md`
- `data_qa_report.md` → `Ready for analysis: YES`
- `intake_contract.md`

## Steps

1. Load story from `story_brief.md` (slide order, visuals); numbers from `analysis_pack.md`
2. Per `~/.cursor/skills/visualization-reporting/workflows/charts-and-deck-playbook.md`:
   - Key findings → exec summary / priority cards
   - Must address → appendix section
   - Publication charts in `charts/`
   - HTML/PDF in `reports/`
   - PPT in `presentations/` if requested
3. Prefer the project's own chart/PPT/PDF scripts when they fit
   (see **Visualization & reporting scripts** in `docs/AGENT_ROLES.local.md`)
   - **Svelte monthly pack:** after review PASS, run `build_monthly_pack_html.py --month <MONTH> --report-date <DATE> --pdf`
4. Verify numbers match `analysis_pack.md` before signing off
5. Write `deliverables_manifest.md` using template in `analysis/dedicated/_template/`

## Must not

- Change metrics, rerun SQL, rewrite `analysis.md` or `story_brief.md`
- Alter headline numbers vs analysis_pack
- Skip executive review gate
- Invent insight copy not in story_brief

## Escalation

Wrong numbers → `data-analysis` or `data-analyst`. Wrong facts → `ba-insights`. Wrong story → `insight-storytelling`. Review REVISE → user or `/executive-review`.

See `docs/AGENT_ROLES.md`.

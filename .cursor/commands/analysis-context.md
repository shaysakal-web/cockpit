---
name: analysis-context
description: >-
  Analysis Context and Limitations Agent phase — synthesize scope, exclusions,
  adjustments, assumptions, limitations, and confidence drivers into analysis_context.md.
  Use after analysis-insights, before insight-storytelling.
---

Run **phase 7** (Analysis Context & Limitations Agent). Load skill `analysis-context`.

## Stop gate (check first)

**STOP and refuse** if `analysis.md` or `analysis_pack.md` is missing, or if QA is not `YES`.
Report what's missing; do not write context without the analytical record.

## Prerequisites

- `data_qa_report.md` → `Ready for analysis: YES`
- `analysis_pack.md` (**hard stop if missing**)
- `analysis.md` (**hard stop if missing**)
- `intake_contract.md`, `pull_manifest.md`
- `exploration_report.md` (when phase 4 ran)

## Steps

1. Load upstream artifacts read-only (intake, manifest, QA, exploration, pack, analysis)
2. Per `~/.cursor/skills/analysis-context/workflows/context-playbook.md`:
   - As-run scope, included/excluded data
   - Adjustments from pack cleaning log
   - Assumptions (labeled)
   - Limitations with severity
   - Study-level confidence drivers
3. Write `analysis_context.md` using template in `analysis/dedicated/_template/`
4. Set `Context status: COMPLETE`

## Must not

- Restate findings from `analysis.md` (scope, method, constraints only)
- Re-pull, re-QA, or re-analyze
- Generate insights, recommendations, or exec narrative
- Edit upstream artifacts

## Next phase

`/insight-storytelling` — storyteller § Risks and limitations must trace to this doc.

See `docs/AGENT_ROLES.md`.

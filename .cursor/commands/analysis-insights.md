---
name: analysis-insights
description: >-
  Executive Insight Agent phase — comprehensive analytical narrative from analysis_pack;
  write analysis.md with what changed, why, impact, confidence, actions.
---

Run **phase 6** (Executive Insight Agent). Load skill `ba-insights`.

## Stop gate (check first)

**STOP and refuse** if `analysis_pack.md` is missing or QA is not `YES`. Report what's
missing and escalate to phase 5; do not write a narrative from raw CSVs.

## Prerequisites

- `data_qa_report.md` → `Ready for analysis: YES`
- `analysis_pack.md` (**hard stop if missing**)

## Steps

1. Load `analysis_pack.md` + `intake_contract.md`
2. Load `statistical-testing` — check inferential language against pack § Statistical validation
3. Write `analysis.md` with required sections:
   - What changed
   - Statistical evidence summary
   - Why it likely changed (observed / inferred / validated — validated only when pack verdict = `significant`)
   - Business impact
   - Confidence level (cite stat verdict for inferential claims)
   - Next action
   - What still needs validation
3. Use `docs/OUTPUT_TEMPLATES.md` where applicable (if present)
4. Headlines per project headline rules (see `docs/DEFINITIONS.md` / project rules)

## Must not

- Build PPT, PDF, story brief, context doc, or publication charts (phases 7–10)
- Prioritize for exec delivery or exclude findings (phase 8 owns curation)

## Next phase

`/analysis-context` for audit and limitations doc.

See `docs/AGENT_ROLES.md`.

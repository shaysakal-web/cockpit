---
name: data-qa-check
description: >-
  Data QA Agent phase — validate outputs against intake contract and database; write
  data_qa_report.md with Ready for analysis YES/NO. Use for data QA, pre-publish check.
---

Run **phase 3** (Data QA Agent). Load skill `data-qa`.

## Stop gate (check first)

**STOP and refuse** if `pull_manifest.md` or the pull output files are missing, or if
`intake_contract.md` is not `CLEAR`. Report what's missing; do not QA data that isn't there.

## Prerequisites

- `intake_contract.md` (`clarity_status: CLEAR`)
- `pull_manifest.md`
- Output files from pull phase

## Steps

1. Load intake + manifest + outputs
2. Freshness gate — `.cursor/rules/analysis-fresh-outputs.mdc` plus project extensions in `docs/DATA_INTEGRITY_CHECKLIST.md`
3. Run `~/.cursor/skills/data-qa/workflows/checklist.md`
4. Run project `docs/DATA_INTEGRITY_CHECKLIST.md` extensions
5. Spot-verify one headline metric from CSV rows
6. Write `data_qa_report.md` using template in `analysis/dedicated/_template/`
7. Set `Ready for analysis: YES` only if all critical checks PASS

## Must not

- Insights, recommendations, silent data fixes
- PASS on BLOCKED clarity or missing KPI mapping

## Gate

Phase 4+ blocked on `Ready for analysis: NO`.

See `docs/AGENT_ROLES.md`.

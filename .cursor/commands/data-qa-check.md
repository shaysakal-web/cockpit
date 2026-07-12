---
name: data-qa-check
description: >-
  Data QA Agent phase — validate outputs against intake contract and database; write
  data_qa_report.md with Ready for analysis YES/NO. Runs as an isolated reviewer
  subagent for independent review. Use for data QA, pre-publish check.
---

Run **phase 3** (Data QA Agent) as an **isolated reviewer** — dispatch a fresh-context
subagent; do not run the review inline in this session.

## Stop gate (check first, before dispatch)

**STOP and refuse** if `pull_manifest.md` or the pull output files are missing, or if
`intake_contract.md` is not `CLEAR`. Report what's missing; do not QA data that isn't there.

## Prerequisites

- `intake_contract.md` (`clarity_status: CLEAR`)
- `pull_manifest.md`
- Output files from pull phase

## Isolated reviewer dispatch

Launch a **Task subagent** (`generalPurpose`) with fresh context. The dispatch prompt must
contain **only**:

- The absolute study folder path
- Skill to load: `~/.cursor/skills/data-qa/SKILL.md` and `~/.cursor/skills/data-qa/workflows/checklist.md`
- Artifacts to review (paths only): `intake_contract.md`, `pull_manifest.md`, the pull
  output files, project `docs/DATA_INTEGRITY_CHECKLIST.md`, `.cursor/rules/analysis-fresh-outputs.mdc`
- Report template path: `analysis/dedicated/_template/data_qa_report.md`
- The subagent steps below, verbatim

**No-context-leak rule:** pass file paths only — never your own summary of the data, your
opinion of its quality, or an expected verdict. The reviewer forms its verdict from the
artifacts alone.

**Write-scope rule (include verbatim in the prompt):** the subagent may write exactly one
file — `data_qa_report.md` in the study folder. It must never edit pull outputs, the
manifest, the intake contract, or any other study file. Verification math (e.g. spot-checking
CSV rows) is read-only.

**Return contract:** the subagent returns the verdict line (`Ready for analysis: YES | NO`)
and the report path. After it returns, **re-read `data_qa_report.md` from disk** and confirm
the verdict matches the returned one before honoring the gate.

**Fallback:** if subagent dispatch is unavailable in this session, load skill `data-qa`
inline as before and add `review_isolation: inline-fallback` to the report header.

## Subagent steps (include in the dispatch prompt)

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
- Pre-summarize findings or hint at the expected verdict in the dispatch prompt

## Gate

Phase 4+ blocked on `Ready for analysis: NO`.

See `docs/AGENT_ROLES.md` § Reviewer isolation.

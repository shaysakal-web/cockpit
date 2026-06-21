---
name: data-exploration-run
description: >-
  Data Exploration Agent phase — broad scan of QA-passed data for patterns, anomalies,
  and ranked investigation paths; write exploration_report.md. Use after QA passes.
---

Run **phase 4** (Data Exploration Agent). Load skill `data-exploration`.

## Stop gate (check first)

**STOP and refuse** if `data_qa_report.md` is missing or `Ready for analysis` is not `YES`,
or if `pull_manifest.md` / pull outputs are missing. Report QA status; do not explore
unvalidated data.

## Prerequisites

- `intake_contract.md` (`clarity_status: CLEAR`)
- `pull_manifest.md` + output files
- `data_qa_report.md` → `Ready for analysis: YES` (**hard stop otherwise**)

## Steps

1. Read `data_qa_report.md` first — do not duplicate QA checks
2. Load intake + manifest + validated pull paths
3. Per `~/.cursor/skills/data-exploration/workflows/exploration-playbook.md`:
   - Dataset summary (one paragraph)
   - Broad distribution/trend/segment scans (shallow)
   - Anomalies (business-pattern only)
   - Hypotheses and segment opportunities
   - Ranked § Recommended next investigations (with observation ids)
4. Write `exploration_report.md` using template in `analysis/dedicated/_template/`
5. Set `Exploration status: COMPLETE` only when backlog is populated

## Must not

- Final insights, recommendations, causation claims, exec narrative
- Re-run QA checklist or driver decomposition tables
- Stakeholder charts (phase 10)

## Next phase

`/data-analysis-run` when exploration complete.

See `docs/AGENT_ROLES.md`.

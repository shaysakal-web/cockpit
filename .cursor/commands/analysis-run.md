---
name: analysis-run
description: >-
  Orchestrator — runs the analysis pipeline phases listed in intake_contract.md,
  in order, stopping at any failed gate. Use to execute a standard (T1) or full (T2)
  analysis after intake. Runs only the planned phases, not always all ten.
---

Run the pipeline **as planned in the intake contract** — not always all ten phases.

## Preconditions

1. `intake_contract.md` exists with `clarity_status: CLEAR`
2. Read its `tier:` and `phases_to_run:` (e.g. `2 3 4 5 6 7 8 9 10`)
3. If `clarity_status: BLOCKED` → stop, list open questions, do not run

## Execute planned phases in order

For each phase in `phases_to_run`, run its command and **check the gate before the next**:

| Phase | Command | Gate to pass before continuing |
|-------|---------|--------------------------------|
| 2 | `/data-pull` | `pull_manifest.md` written |
| 3 | `/data-qa-check` | `data_qa_report.md` → `Ready for analysis: YES` |
| 4 | `/data-exploration-run` | `exploration_report.md` → `Exploration status: COMPLETE` |
| 5 | `/data-analysis-run` | `analysis_pack.md` written |
| 6 | `/analysis-insights` | `analysis.md` written |
| 7 | `/analysis-context` | `analysis_context.md` → `Context status: COMPLETE` |
| 8 | `/insight-storytelling` | `story_brief.md` written |
| 9 | `/executive-review` | `executive_review.md` → `Review status: PASS` |
| 10 | `/visualization-reporting` | `deliverables_manifest.md` written |

## Stop conditions (hard)

- **QA FAIL** (phase 3 → `NO`) → halt, escalate to Data Analyst, do not proceed to phase 4
- **Review REVISE** (phase 9) → halt, report required revisions; user decides next step
- Any phase's artifact missing → halt, report which phase failed
- Never silently skip a gate or fabricate a downstream artifact

## After the run

State: tier, phases actually run, gate results, and the path of each artifact produced.

## Tiers (see `docs/AGENT_ROLES.md`)

- **T1 standard:** typically `phases_to_run: 2 3 4 5 6 7 8 9` (exploration + context + story + review, no deck)
- **T2 full:** `phases_to_run: 2 3 4 5 6 7 8 9 10`
- **T0** never reaches this command — it's a direct answer.

Triage with the `analysis-router` skill when the tier is unknown.

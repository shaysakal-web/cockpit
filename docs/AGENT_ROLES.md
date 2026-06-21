# AGENT_ROLES.md — Ten-phase analytics pipeline

Cross-project orchestration for analytics work. Copy this file to new projects; add a **Project hooks** section per repo.

Personal role skills live in `~/.cursor/skills/` (`analysis-router`, `ba-intake`, `data-analyst`, `data-qa`, `data-exploration`, `data-analysis`, `ba-insights`, `analysis-context`, `insight-storytelling`, `executive-review`, `visualization-reporting`).

Install from: [cursor-analytics-pipeline](https://github.com/shaysakal-web/cursor-analytics-pipeline) → `install.ps1`

**Migration:** Pre–10-phase studies used 8 phases. Remap `phases_to_run` — old phase N → new phase N+1 for N≥4 (exploration inserted at 4; context at 7). Rollback baseline tag: `pipeline-pre-exploration-v1`.

---

## Semantic grounding (every request, all tiers)

Before any number is pulled or stated — even a T0 quick answer — resolve the referenced
metrics/fields against `docs/DEFINITIONS.md` and `docs/SEMANTIC.md`. If undefined or
ambiguous, **ask the user; never guess**. Enforced by `.cursor/rules/semantic-grounding.mdc`
and `analysis-router` Step 0. This is grounding, not pipeline depth.

---

## Right-size first: triage into a tier

**Not every question runs the full pipeline.** The `analysis-router` skill (the only
model-invocable one) triages each request, then proposes a plan and waits for confirmation.

| Tier | When | Phases | Artifacts |
|------|------|--------|-----------|
| **T0 — Quick answer** | Single fact, sanity check, no decision attached | none (direct, or one `data-analyst` pull) | none |
| **T1 — Standard diagnostic** | "Why did X move?" — rigor, no deck | 1 → 2 → … → 9 | intake, exploration, pack, analysis.md, context, story, review |
| **T2 — Full pipeline** | Routine pack, monitor, stakeholder deck | 1 → 2 → … → 10 | all ten |

Bias to **T0**. The intake contract records `tier:` and `phases_to_run:`; the
`/analysis-run` orchestrator executes **only those phases**, honoring every gate.

---

## Roles

| Phase | Display name | Skill id | Command | Handoff artifact |
|-------|--------------|----------|---------|------------------|
| 1 | Main Analyst | `ba-intake` | `/analysis-intake` | `intake_contract.md` |
| 2 | Data Analyst | `data-analyst` | `/data-pull` or project pull commands | `pull_manifest.md` |
| 3 | Data QA Agent | `data-qa` | `/data-qa-check` | `data_qa_report.md` |
| 4 | Data Exploration Agent | `data-exploration` | `/data-exploration-run` | `exploration_report.md` |
| 5 | Python / Notebook Agent | `data-analysis` | `/data-analysis-run` | `analysis_pack.md` |
| 6 | Executive Insight Agent | `ba-insights` | `/analysis-insights` | `analysis.md` |
| 7 | Analysis Context & Limitations Agent | `analysis-context` | `/analysis-context` | `analysis_context.md` |
| 8 | Insight Synthesis / Storytelling Agent | `insight-storytelling` | `/insight-storytelling` | `story_brief.md` |
| 9 | Executive Review Agent | `executive-review` | `/executive-review` | `executive_review.md` |
| 10 | Visualization & Reporting Analyst | `visualization-reporting` | `/visualization-reporting` | `deliverables_manifest.md` |

---

## Clarity gate (phase 1 — non-negotiable)

Before phase 2, `intake_contract.md` must define task, KPIs, and semantic layer. Set `clarity_status: CLEAR | BLOCKED`. Phase 2+ stops on `BLOCKED`.

See `~/.cursor/skills/ba-intake/workflows/clarity-gate.md`.

---

## Phase gates

Prerequisite to **enter** phase N:

| Gate | Requirement |
|------|-------------|
| Phase 2+ | `clarity_status: CLEAR` |
| Phase 4 | `data_qa_report.md` → `Ready for analysis: YES` |
| Phase 5 | `exploration_report.md` → `Exploration status: COMPLETE` |
| Phase 6 | `analysis_pack.md` exists |
| Phase 7 | `analysis.md` exists |
| Phase 8 | `analysis_context.md` → `Context status: COMPLETE` |
| Phase 9 | `story_brief.md` exists |
| Phase 10 | `executive_review.md` → `Review status: PASS` |

---

## Escalation matrix

| Failure | Escalate to |
|---------|-------------|
| Clarity BLOCKED | Main Analyst / user |
| QA FAIL (data) | Data Analyst |
| QA FAIL (scope) | Main Analyst |
| Thin / missing exploration | Data Exploration (`data-exploration`) |
| Exploration flags integrity on QA-passed data | Data QA or Data Analyst |
| Exploration scope mismatch | Main Analyst |
| Thin analysis_pack | Python / Notebook agent |
| Thin / missing context doc | Analysis Context (`analysis-context`) |
| Wrong analytical narrative | Executive Insight (`ba-insights`) |
| Wrong exec story / missing mandatory coverage | Insight Storytelling (`insight-storytelling`) |
| Review REVISE — factual gaps | User → typically `/analysis-insights` |
| Review REVISE — story / coverage gaps | User → typically `/insight-storytelling` |
| Review REVISE — missing evidence in pack | Data Analysis or Data Analyst |
| Review REVISE — hidden limitations | User → `/analysis-context` or `/insight-storytelling` |
| User explicit override after REVISE | Document override in `executive_review.md`, then phase 10 |
| Wrong numbers in deck | Data Analysis or Data Analyst |

---

## Shortcut paths

| User intent | Tier | Phases | How |
|-------------|------|--------|-----|
| Quick fact / sanity check | T0 | none | answer directly (router) |
| Why did a metric move? | T1 | 1→2→3→4→5→6→7→8→9 | `/analysis-intake` then `/analysis-run` |
| Full diagnostic with deck | T2 | 1→2→…→10 | `/analysis-intake` then `/analysis-run` |
| QA existing pull | — | 3 only | `/data-qa-check` |
| Exploration only | — | 4 only | `/data-exploration-run` (requires QA YES) |
| Context doc only | — | 7 only | `/analysis-context` (requires `analysis.md`) |
| Story brief only | — | 8 only | `/insight-storytelling` |
| Review only | — | 9 only | `/executive-review` |
| Build PPT/PDF/charts only | — | 10 only | `/visualization-reporting` (requires review PASS) |

`/analysis-run` reads `phases_to_run` from the intake contract and runs exactly those.

---

## Artifact locations

- Study: `analysis/dedicated/<study_id>/`
- Ad-hoc: `analysis/intake/<YYYY-MM-DD>_<slug>/`
- Templates: `analysis/dedicated/_template/`

---

## Project hooks

Per-project paths, domain skill, pull commands, and publish scripts live in
**`docs/AGENT_ROLES.local.md`** (never overwritten by `update-project.ps1`).

> This file (`AGENT_ROLES.md`) is **framework only** — it is re-synced from the
> template on update. Do not add project-specific content here; put it in the
> `.local.md` file.

---

## New project bootstrap

1. Run `bootstrap-project.ps1` from this repo (or copy `project-template/`)
2. Run `install.ps1` once per machine for personal skills
3. Add domain skill + DEFINITIONS + SEMANTIC + DATA_INTEGRITY_CHECKLIST
4. Fill **`docs/AGENT_ROLES.local.md`** (project hooks)

## Keeping a project up to date

Run `update-project.ps1 -TargetProject <path>` (or `-All`) to re-sync framework
commands, `AGENT_ROLES.md`, and templates. It never touches `AGENT_ROLES.local.md`,
`DEFINITIONS.md`, `SEMANTIC.md`, the domain skill, or project-specific commands.

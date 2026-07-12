# AGENT_ROLES.md — Ten-phase analytics pipeline

Cross-project orchestration for analytics work. Copy this file to new projects; add a **Project hooks** section per repo.

Personal role skills live in `~/.cursor/skills/` (`analysis-router`, `ba-intake`, `data-analyst`, `data-qa`, `code-qa`, `data-exploration`, `data-analysis`, `ba-insights`, `analysis-context`, `insight-storytelling`, `executive-review`, `visualization-reporting`, `deliverables-qa`, `final-executive-review`).

Install from: [cursor-analytics-pipeline](https://github.com/shaysakal-web/cursor-analytics-pipeline) → `install.ps1`

**Migration:** Pre–10-phase studies used 8 phases. Remap `phases_to_run` — old phase N → new phase N+1 for N≥4 (exploration inserted at 4; context at 7). Rollback tags: `pipeline-pre-exploration-v1`, `pipeline-pre-chart-viz-v1`.

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
| **T2 — Full pipeline** | Routine pack, monitor, stakeholder deck | 1 → 2 → … → 10 | all ten (phase 10 = 10a–10e publish sign-off) |

Bias to **T0**. The intake contract records `tier:` and `phases_to_run:`; the
`/analysis-run` orchestrator executes **only those phases**, honoring every gate.

---

## Roles

| Phase | Display name | Skill id | Command | Handoff artifact |
|-------|--------------|----------|---------|------------------|
| — | Analysis Router | `analysis-router` | (model-invocable) | tier assignment |
| 1 | Main Analyst | `ba-intake` | `/analysis-intake` | `intake_contract.md` |
| 2 | Data Extraction | `data-analyst` | `/data-pull` or project pull commands | `pull_manifest.md` |
| 3a | Data QA Agent | `data-qa` | `/data-qa-check` | `data_qa_report.md` |
| 3b | Code QA Agent | `code-qa` | `/code-qa-check` | `code_review.md` |
| 4 | Data Exploration Agent | `data-exploration` | `/data-exploration-run` | `exploration_report.md` |
| 5 | Data Analysis Agent | `data-analysis` | `/data-analysis-run` | `analysis_pack.md` |
| 6 | Business Analyst Insights Agent | `ba-insights` | `/analysis-insights` | `analysis.md` |
| 7 | Analysis Context & Limitations Agent | `analysis-context` | `/analysis-context` | `analysis_context.md` |
| 8 | Insight Synthesis / Storytelling Agent | `insight-storytelling` | `/insight-storytelling` | `story_brief.md`, `chart_specs.yaml` |
| 9 | Executive Review Agent | `executive-review` | `/executive-review` | `executive_review.md` |
| 10 | Visualization & Reporting Analyst | `visualization-reporting` (+ `deliverables-qa`, `final-executive-review`) | see **Phase 10 sub-steps** | `final_executive_review.md` → PASS |

### Phase 10 sub-steps (T2 publish pack)

| Sub-step | Command | Skill | Artifact | Gate |
|----------|---------|-------|----------|------|
| 10a | `/chart-maker-run` | `visualization-reporting` | `charts/*` | collision check passed |
| 10b | `/chart-design-review` | `visualization-reporting` | `design_review.md` | `Verdict: PASS` |
| 10c | `/visualization-reporting` | `visualization-reporting` | `deliverables_manifest.md` | manifest written |
| 10d | `/deliverables-qa-check` | `deliverables-qa` | `deliverables_qa_report.md` | `Ready to publish: YES` |
| 10e | `/final-executive-review` | `final-executive-review` | `final_executive_review.md` | `Review status: PASS` |

Phase 9 reviews analysis + story **before** charts. Phase 10e reviews **rendered** deliverables.

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
| Phase 4 | `data_qa_report.md` → `Ready for analysis: YES` **and** `code_review.md` → `Code review: PASS` |
| Phase 5 | `exploration_report.md` → `Exploration status: COMPLETE` |
| Phase 6 | `analysis_pack.md` exists |
| Phase 7 | `analysis.md` exists |
| Phase 8 | `analysis_context.md` → `Context status: COMPLETE` |
| Phase 9 | `story_brief.md` exists |
| Phase 10 | `executive_review.md` → `Review status: PASS` |
| Phase 10 complete | `final_executive_review.md` → `Review status: PASS` |

---

## Reviewer isolation (phases 3a, 3b, 9, 10d)

The reviewer phases — **3a** (`data-qa`), **3b** (`code-qa`), **9** (`executive-review`),
and **10d** (`deliverables-qa`) — run as **isolated Task subagents with fresh context**,
not inline. 3b runs after 3a (even on 3a FAIL) with a two-pass order: independent code
review first, correlation with `data_qa_report.md` second — the QA report must not be
read before pass 1 findings are written.
Rationale: a reviewer sharing the context window of the agent that produced the work is
doing self-review; a fresh subagent that reads only the handoff artifacts gives a genuinely
independent check.

Rules (details in each command file):

- **No context leak** — the dispatching agent passes file paths only; never its own
  summary of the findings or an expected verdict.
- **Write scope** — the reviewer subagent writes exactly one file: its own report artifact.
  It never edits the work under review.
- **Verdict verification** — after the subagent returns, the dispatcher re-reads the report
  from disk and confirms the verdict before honoring the gate.
- **Fallback** — if subagent dispatch is unavailable, run the skill inline and add
  `review_isolation: inline-fallback` to the report header.

Phases 10b and 10e still run inline (isolation deferred to a later pipeline version).

---

## Auto-rerun and run state

`/analysis-run` maintains **`run_state.yaml`** in the study folder (template in
`analysis/dedicated/_template/`): planned phases, per-phase status, revision rounds.
On restart it resumes from the first unfinished phase, re-verifying each skipped phase's
gate line in its artifact — artifacts are the source of truth; run state is an index.

On phase 9 **REVISE** with `auto_rerun: true` in the intake contract (the default;
opt out at intake), the orchestrator reworks automatically instead of hard-stopping:
it maps each Required-revisions Target to a phase command via the escalation matrix,
re-runs those producer phases with the revision rows as the brief, re-runs downstream
dependents, and dispatches a fresh phase 9 reviewer subagent.

Bounds — escalate to the user (classic hard stop) when:

- `auto_rerun: false` or 2 auto rounds already used (`revision_rounds` in run state)
- A revision Target is ambiguous or points at phase 2 data issues
- REVISE is never auto-overridden into phase 10

---

## Parallel execution (phase 10a)

Chart rendering (`/chart-maker-run`) with 3+ specs runs as **parallel batch worker
subagents**: max 3 workers, `ceil(N/3)` specs each, sequential within a worker, each
worker writing only its own spec ids' `charts/{id}.png|.svg|.meta.json`. The dispatcher
then verifies **validity, not just presence** (non-zero files, PNG ≥ 1 KB, meta.json
parses), and re-renders failed specs **per-spec-id, never per-batch**. Details in the
command file.

This does not relax the analytical scope rules: the "no parallel fishing" constraint in
phases 4–5 is about analysis scope discipline, not execution. Chart rendering is
mechanical work on an already-approved plan (phase 9 PASS), so parallelism is safe.

---

## Escalation matrix

Phase 9 REVISE rows below are handled automatically by `/analysis-run` when
`auto_rerun: true` and fewer than 2 rounds are used; otherwise they escalate to the user
as listed.

| Failure | Escalate to |
|---------|-------------|
| Clarity BLOCKED | Main Analyst / user |
| QA FAIL (data) | Data Extraction |
| QA FAIL (scope) | Main Analyst |
| Code review FAIL (`fail_class: extraction`) | Data Extraction |
| Code review FAIL (`fail_class: contract`) | Main Analyst / user |
| Thin / missing exploration | Data Exploration (`data-exploration`) |
| Exploration flags integrity on QA-passed data | Data QA or Data Extraction |
| Exploration scope mismatch | Main Analyst |
| Thin analysis_pack | Data Analysis agent |
| Thin / missing context doc | Analysis Context (`analysis-context`) |
| Wrong analytical narrative | Business Analyst Insights (`ba-insights`) |
| Wrong exec story / missing mandatory coverage | Insight Storytelling (`insight-storytelling`) |
| Review REVISE — factual gaps | User → typically `/analysis-insights` |
| Review REVISE — story / coverage gaps | User → typically `/insight-storytelling` |
| Review REVISE — missing evidence in pack | Data Analysis or Data Extraction |
| Review REVISE — hidden limitations | User → `/analysis-context` or `/insight-storytelling` |
| User explicit override after REVISE | Document override in `executive_review.md`, then phase 10 |
| Wrong numbers in deck | Data Analysis or Data Extraction |
| Design review FIX / NEEDS_REVISION | `/chart-maker-run` or `insight-storytelling` |
| Deliverables QA NO | `/visualization-reporting` or `/chart-maker-run` |
| Final exec REVISE | `/visualization-reporting` or `/chart-maker-run` |

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
| Build PPT/PDF/charts only | — | 10 only | full 10a–10e (requires phase 9 PASS) |
| Chart only | — | 10a–10b | `/chart-maker-run` then `/chart-design-review` |
| Deliverables QA only | — | 10d | `/deliverables-qa-check` |
| Final sign-off only | — | 10e | `/final-executive-review` |

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

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

2. Read its `tier:`, `phases_to_run:` (e.g. `2 3 4 5 6 7 8 9 10`), and `auto_rerun:`

3. If `clarity_status: BLOCKED` → stop, list open questions, do not run

4. Initialize or resume `run_state.yaml` (see **Run state** below)



## Run state (`run_state.yaml`)



Maintain `run_state.yaml` in the study folder (template: `analysis/dedicated/_template/run_state.yaml`):

- **At run start:** if missing, create it from the intake contract (`study_id`, `tier`,

  `phases_to_run`, `auto_rerun`).

- **Resume rule:** if it already exists, skip phases recorded as `PASS` — but first

  **re-verify each skipped phase's gate line in its artifact on disk**. Artifacts are the

  source of truth; run state is an index, not an authority. If the artifact is missing or

  its gate line disagrees, re-run that phase.

- **After every phase and gate check:** update the phase entry (`status`, `artifact`,

  `completed_at`) and `last_updated` before moving to the next phase.



## Execute planned phases in order



For each phase in `phases_to_run`, run its command and **check the gate before the next**:



| Phase | Command | Gate to pass before continuing |

|-------|---------|--------------------------------|

| 2 | `/data-pull` | `pull_manifest.md` written |

| 3a | `/data-qa-check` *(isolated reviewer — subagent)* | `data_qa_report.md` → `Ready for analysis: YES` |

| 3b | `/code-qa-check` *(isolated reviewer — subagent; runs after 3a, even on 3a FAIL)* | `code_review.md` → `Code review: PASS` |

| 4 | `/data-exploration-run` (requires **both** 3a YES and 3b PASS) | `exploration_report.md` → `Exploration status: COMPLETE` |

| 5 | `/data-analysis-run` | `analysis_pack.md` written |

| 6 | `/analysis-insights` | `analysis.md` written |

| 7 | `/analysis-context` | `analysis_context.md` → `Context status: COMPLETE` |

| 8 | `/insight-storytelling` | `story_brief.md` + `chart_specs.yaml` written |

| 9 | `/executive-review` *(isolated reviewer — subagent)* | `executive_review.md` → `Review status: PASS` |

| 10 | see **Phase 10 sub-steps** below | `final_executive_review.md` → `Review status: PASS` |



### Phase 10 sub-steps (run in order when phase 10 is in `phases_to_run`)



| Sub-step | Command | Gate |

|----------|---------|------|

| 10a | `/chart-maker-run` | charts saved; no collision halt |

| 10b | `/chart-design-review` | `design_review.md` → `Verdict: PASS` |

| 10c | `/visualization-reporting` | `deliverables_manifest.md` written |

| 10d | `/deliverables-qa-check` *(isolated reviewer — subagent)* | `deliverables_qa_report.md` → `Ready to publish: YES` |

| 10e | `/final-executive-review` | `final_executive_review.md` → `Review status: PASS` |



On 10b FIX → re-run 10a for listed charts, then 10b again before 10c.

On 10d NO or 10e REVISE → fix and re-run from the appropriate sub-step.



## Reviewer isolation (phases 3a, 3b, 9, 10d)

Phases marked *isolated reviewer — subagent* run in a **fresh-context Task subagent** per

their command file, so the review is independent of the session that produced the work.

When dispatching them:

- Pass **file paths only** — never pre-summarize findings, quality opinions, or an

  expected verdict to the reviewer.

- After the subagent returns, **re-read the report artifact from disk** and confirm the

  verdict before honoring the gate.

- If subagent dispatch is unavailable, run the skill inline and note

  `review_isolation: inline-fallback` in the report header.



## Auto-rerun on phase 9 REVISE



When `executive_review.md` → `Review status: REVISE` and `auto_rerun: true` and

`revision_rounds < 2` in `run_state.yaml`:



1. Read the **Required revisions** table in `executive_review.md`; map each row's

   **Target** to a phase command via the escalation matrix in `docs/AGENT_ROLES.md`

   (e.g. `ba-insights` → `/analysis-insights`, `insight-storytelling` →

   `/insight-storytelling`, `analysis-context` → `/analysis-context`).

2. Re-run **only the targeted producer phases**, passing the specific revision rows as

   the rework brief. (Producers may see reviewer findings — the no-context-leak rule

   applies only when dispatching reviewers.)

3. Re-run downstream dependents of anything that changed (e.g. `analysis.md` changed →

   re-run phases 7 and 8 before 9).

4. Increment `revision_rounds` in `run_state.yaml`, then re-run `/executive-review` as a

   fresh isolated subagent.



**Escalate to the user instead of auto-rerunning** (hard stop, as before) when:



- `auto_rerun: false`, or `revision_rounds` is already 2

- Any revision Target is ambiguous, or points at phase 2 data issues

- Never auto-override REVISE into phase 10 — phase 10 requires a genuine PASS or a

  user-documented override in `executive_review.md`



## Stop conditions (hard)



- **QA FAIL** (3a → `NO`) → still run 3b for a complete rework brief, then halt and escalate to Data Extraction; do not proceed to phase 4

- **Code review FAIL** (3b) → halt; `fail_class: extraction` → escalate to phase 2 (`/data-pull`); `fail_class: contract` → escalate to phase 1 (`/analysis-intake` / user)

- **Review REVISE** (phase 9) → run **Auto-rerun on phase 9 REVISE** above; if not

  eligible, halt and report required revisions; user decides next step

- **Design review not PASS** (10b) → halt before assembly

- **Deliverables QA NO** (10d) → halt before final exec review

- Any phase's artifact missing → halt, report which phase failed

- Never silently skip a gate or fabricate a downstream artifact



## After the run



State: tier, phases actually run, gate results, revision rounds used, and the path of

each artifact produced. Leave `run_state.yaml` reflecting the final state.



## Tiers (see `docs/AGENT_ROLES.md`)



- **T1 standard:** typically `phases_to_run: 2 3 4 5 6 7 8 9` (no publish pack)

- **T2 full:** `phases_to_run: 2 3 4 5 6 7 8 9 10` (includes 10a–10e)

- **T0** never reaches this command — it's a direct answer.



Triage with the `analysis-router` skill when the tier is unknown.


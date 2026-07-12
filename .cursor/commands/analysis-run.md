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

| 3 | `/data-qa-check` *(isolated reviewer — subagent)* | `data_qa_report.md` → `Ready for analysis: YES` |

| 4 | `/data-exploration-run` | `exploration_report.md` → `Exploration status: COMPLETE` |

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



## Reviewer isolation (phases 3, 9, 10d)

Phases marked *isolated reviewer — subagent* run in a **fresh-context Task subagent** per

their command file, so the review is independent of the session that produced the work.

When dispatching them:

- Pass **file paths only** — never pre-summarize findings, quality opinions, or an

  expected verdict to the reviewer.

- After the subagent returns, **re-read the report artifact from disk** and confirm the

  verdict before honoring the gate.

- If subagent dispatch is unavailable, run the skill inline and note

  `review_isolation: inline-fallback` in the report header.



## Stop conditions (hard)



- **QA FAIL** (phase 3 → `NO`) → halt, escalate to Data Extraction, do not proceed to phase 4

- **Review REVISE** (phase 9) → halt, report required revisions; user decides next step

- **Design review not PASS** (10b) → halt before assembly

- **Deliverables QA NO** (10d) → halt before final exec review

- Any phase's artifact missing → halt, report which phase failed

- Never silently skip a gate or fabricate a downstream artifact



## After the run



State: tier, phases actually run, gate results, and the path of each artifact produced.



## Tiers (see `docs/AGENT_ROLES.md`)



- **T1 standard:** typically `phases_to_run: 2 3 4 5 6 7 8 9` (no publish pack)

- **T2 full:** `phases_to_run: 2 3 4 5 6 7 8 9 10` (includes 10a–10e)

- **T0** never reaches this command — it's a direct answer.



Triage with the `analysis-router` skill when the tier is unknown.


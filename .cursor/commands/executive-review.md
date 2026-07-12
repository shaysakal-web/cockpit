---
name: executive-review
description: >-
  Executive Review Agent phase — independent review of analysis.md and story_brief.md;
  challenge conclusions, check evidence, mandatory coverage, readability; write
  executive_review.md with PASS/REVISE gate. Runs as an isolated reviewer subagent.
---

Run **phase 9** (Executive Review Agent) as an **isolated reviewer** — dispatch a
fresh-context subagent; do not run the review inline in this session.

## Stop gate (check first, before dispatch)

**STOP and refuse** if `analysis.md`, `story_brief.md`, or `analysis_context.md` is missing, or QA is not `YES`.
Report what's missing and escalate to phase 6, 7, or 8; do not review without all three artifacts.

## Prerequisites

- `analysis.md` (**hard stop if missing**)
- `story_brief.md` (**hard stop if missing**)
- `analysis_context.md` → `Context status: COMPLETE` (**hard stop if missing**)
- `analysis_pack.md`
- `data_qa_report.md` → `Ready for analysis: YES`
- `intake_contract.md`

## Isolated reviewer dispatch

Launch a **Task subagent** (`generalPurpose`) with fresh context. The dispatch prompt must
contain **only**:

- The absolute study folder path
- Skill to load: `~/.cursor/skills/executive-review/SKILL.md` and
  `~/.cursor/skills/executive-review/workflows/review-playbook.md`
- Artifacts to review (paths only): `analysis.md`, `story_brief.md`, `analysis_context.md`,
  `analysis_pack.md`, `data_qa_report.md`, `intake_contract.md`
- Report template path: `analysis/dedicated/_template/executive_review.md`
- The subagent steps below, verbatim

**No-context-leak rule:** pass file paths only — never your own summary of the analysis,
your view of the story, or an expected verdict. Independence from the agent that produced
the work is the entire point of this phase.

**Write-scope rule (include verbatim in the prompt):** the subagent may write exactly one
file — `executive_review.md` in the study folder. It must never edit `analysis.md`,
`story_brief.md`, `analysis_context.md`, `analysis_pack.md`, or any other study file.

**Return contract:** the subagent returns the verdict line (`Review status: PASS | REVISE`)
and the report path. After it returns, **re-read `executive_review.md` from disk** and
confirm the verdict matches the returned one before honoring the gate.

**Fallback:** if subagent dispatch is unavailable in this session, load skill
`executive-review` inline as before and add `review_isolation: inline-fallback` to the
report header.

## Subagent steps (include in the dispatch prompt)

1. Load `analysis.md`, `story_brief.md`, `analysis_context.md`, `analysis_pack.md`, `intake_contract.md`
2. Follow `~/.cursor/skills/executive-review/workflows/review-playbook.md`
3. Audit story § Risks and limitations against `analysis_context.md` — hidden limits → REVISE
4. Write `executive_review.md` using template in `analysis/dedicated/_template/`
5. Run § Mandatory coverage audit — any MISSING → default REVISE
6. Set `Review status: PASS | REVISE`

## After the subagent returns

**If REVISE** → hard stop; report the numbered required revisions with target phase; user
decides next step.

## Must not

- Rewrite or edit `analysis.md`, `story_brief.md`, or `analysis_context.md`
- Build charts, PPT, PDF, or HTML (phase 10)
- Rerun SQL or change numbers in `analysis_pack.md`
- Proceed to phase 10 on REVISE without user decision
- Pre-summarize findings or hint at the expected verdict in the dispatch prompt

## Next phase (on PASS only)

`/visualization-reporting` for charts and deck.

See `docs/AGENT_ROLES.md` § Reviewer isolation.

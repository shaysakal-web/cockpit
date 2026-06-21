---
name: executive-review
description: >-
  Executive Review Agent phase — independent review of analysis.md and story_brief.md;
  challenge conclusions, check evidence, mandatory coverage, readability; write
  executive_review.md with PASS/REVISE gate.
---

Run **phase 9** (Executive Review Agent). Load skill `executive-review`.

## Stop gate (check first)

**STOP and refuse** if `analysis.md`, `story_brief.md`, or `analysis_context.md` is missing, or QA is not `YES`.
Report what's missing and escalate to phase 6, 7, or 8; do not review without all three artifacts.

## Prerequisites

- `analysis.md` (**hard stop if missing**)
- `story_brief.md` (**hard stop if missing**)
- `analysis_context.md` → `Context status: COMPLETE` (**hard stop if missing**)
- `analysis_pack.md`
- `data_qa_report.md` → `Ready for analysis: YES`
- `intake_contract.md`

## Steps

1. Load `analysis.md`, `story_brief.md`, `analysis_context.md`, `analysis_pack.md`, `intake_contract.md`
2. Follow `~/.cursor/skills/executive-review/workflows/review-playbook.md`
3. Audit story § Risks and limitations against `analysis_context.md` — hidden limits → REVISE
4. Write `executive_review.md` using template in `analysis/dedicated/_template/`
5. Run § Mandatory coverage audit — any MISSING → default REVISE
6. Set `Review status: PASS | REVISE`
7. **If REVISE** → hard stop; list required revisions with target phase; user decides next step

## Must not

- Rewrite or edit `analysis.md`, `story_brief.md`, or `analysis_context.md`
- Build charts, PPT, PDF, or HTML (phase 10)
- Rerun SQL or change numbers in `analysis_pack.md`
- Proceed to phase 10 on REVISE without user decision

## Next phase (on PASS only)

`/visualization-reporting` for charts and deck.

See `docs/AGENT_ROLES.md`.

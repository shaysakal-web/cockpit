---
name: insight-storytelling
description: >-
  Insight Synthesis / Storytelling Agent phase — curate analysis.md into story_brief.md
  with exec headline, key findings, must-address items, slide structure, visual recs.
---

Run **phase 8** (Insight Synthesis / Storytelling Agent). Load skill `insight-storytelling`.

## Stop gate (check first)

**STOP and refuse** if `analysis.md` or `analysis_context.md` is missing, or QA is not `YES`.
Report what's missing and escalate to phase 6 or 7; do not curate without analytical record and context doc.

## Prerequisites

- `analysis.md` (**hard stop if missing**)
- `analysis_context.md` → `Context status: COMPLETE` (**hard stop if missing**)
- `analysis_pack.md`
- `data_qa_report.md` → `Ready for analysis: YES`
- `intake_contract.md`

## Steps

1. Load `analysis.md`, `analysis_context.md`, `analysis_pack.md`, `intake_contract.md`
2. Follow `~/.cursor/skills/insight-storytelling/workflows/story-playbook.md`
3. Build § Mandatory coverage checklist before writing narrative sections
4. Write `story_brief.md` using template in `analysis/dedicated/_template/`
5. Write `chart_specs.yaml` using template (story-playbook Step 5b)
6. § Risks and limitations must **trace to** `analysis_context.md` (cite section)
7. Every mandatory item → Key findings **or** Must address (never Excluded)

## Must not

- Edit or rewrite `analysis.md` or `analysis_context.md`
- Invent limitations not in `analysis_context.md`
- Drop mandatory findings (demote to Must address instead)
- Exclude auto-flagged priorities or Critical/High actions without Must address placement
- Invent findings, upgrade confidence, or create PPT/PDF/HTML/charts (phase 10)

## Next phase

`/executive-review` for independent review of analysis + story (PASS/REVISE gate).

See `docs/AGENT_ROLES.md`.

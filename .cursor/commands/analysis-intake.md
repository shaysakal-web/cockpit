---
name: analysis-intake
description: >-
  Main Analyst phase — clarity gate on task, KPI, semantic fields; produce
  intake_contract.md. Use for new analysis requests, scoping, or intake.
---

Run **phase 1** (Main Analyst). Load skill `ba-intake`.

## Steps

1. Run clarity gate per `~/.cursor/skills/ba-intake/workflows/clarity-gate.md`
2. Read project `docs/DEFINITIONS.md`, `docs/SEMANTIC.md`, `docs/AGENTS.md`
3. If any KPI or field is `NEEDS_CLARIFICATION` or new → ask user; set `clarity_status: BLOCKED`
4. After answers → update `DEFINITIONS.md` / `SEMANTIC.md` as needed
5. Write `intake_contract.md` using template in `analysis/dedicated/_template/`
6. Set `clarity_status: CLEAR` only when all KPI and semantic rows are resolved
7. Set `tier:` (T0 | T1 | T2) and `phases_to_run:` — T1 default `2 3 4 5 6 7 8 9`; T2 default `2 3 4 5 6 7 8 9 10`

## Artifact location

- Study: `analysis/dedicated/<study_id>/intake_contract.md`
- Ad-hoc: `analysis/intake/<YYYY-MM-DD>_<slug>/intake_contract.md`

## Gate

Phase 2 blocked until `clarity_status: CLEAR`.

See `docs/AGENT_ROLES.md`.

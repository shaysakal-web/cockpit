---
name: deliverables-qa-check
description: >-
  Phase 10d — deliverables QA on manifest, spot-check numbers vs pack, design review gate.
  Writes deliverables_qa_report.md with Ready to publish YES/NO. Runs as an isolated
  reviewer subagent.
---

Run **phase 10d** (Deliverables QA) as an **isolated reviewer** — dispatch a fresh-context
subagent; do not run the review inline in this session.

## Stop gate (check first, before dispatch)

**STOP** if:
- `deliverables_manifest.md` missing
- `design_review.md` not `Verdict: PASS`

## Isolated reviewer dispatch

Launch a **Task subagent** (`generalPurpose`) with fresh context. The dispatch prompt must
contain **only**:

- The absolute study folder path
- Skill to load: `~/.cursor/skills/deliverables-qa/SKILL.md` and
  `~/.cursor/skills/deliverables-qa/workflows/deliverables-qa-playbook.md`
- Artifacts to review (paths only): `deliverables_manifest.md`, `design_review.md`,
  `analysis_pack.md`, and the rendered assets listed in the manifest
- Report template path: `analysis/dedicated/_template/deliverables_qa_report.md`
- The subagent steps below, verbatim

**No-context-leak rule:** pass file paths only — never your own summary of the deliverables
or an expected verdict. The reviewer forms its verdict from the rendered assets alone.

**Write-scope rule (include verbatim in the prompt):** the subagent may write exactly one
file — `deliverables_qa_report.md` in the study folder. It must never edit charts, decks,
the manifest, or any other study file. Spot-checking rendered numbers vs the pack is
read-only.

**Return contract:** the subagent returns the verdict line (`Ready to publish: YES | NO`)
and the report path. After it returns, **re-read `deliverables_qa_report.md` from disk**
and confirm the verdict matches the returned one before honoring the gate.

**Fallback:** if subagent dispatch is unavailable in this session, load skill
`deliverables-qa` inline as before and add `review_isolation: inline-fallback` to the
report header.

## Subagent steps (include in the dispatch prompt)

1. Follow `~/.cursor/skills/deliverables-qa/workflows/deliverables-qa-playbook.md`
2. Spot-check ≥3 rendered numbers vs `analysis_pack.md`
3. Write `deliverables_qa_report.md` from template

## Must not

- Fix numbers silently — FAIL and escalate
- PASS without ≥3 spot-checks vs pack
- Pre-summarize findings or hint at the expected verdict in the dispatch prompt

## Gate

`Ready to publish: YES` required before `/final-executive-review`.

## Next

`/final-executive-review` (phase 10e)

See `docs/AGENT_ROLES.md` § Reviewer isolation.

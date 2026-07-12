---
name: final-executive-review
description: >-
  Phase 10e — final executive sign-off on rendered PDF/HTML/PPT. Distinct from phase 9
  pre-viz review. Writes final_executive_review.md PASS/REVISE.
---

Run **phase 10e** (Final Executive Review). Load skill `final-executive-review`.

## Stop gate

**STOP** if:
- `deliverables_qa_report.md` missing or `Ready to publish: NO`
- Rendered deliverables missing from manifest paths

## Steps

1. Open rendered PDF/HTML/PPT listed in `deliverables_manifest.md`
2. Follow `~/.cursor/skills/final-executive-review/workflows/final-review-playbook.md`
3. Write `final_executive_review.md` from template

## Gate

Phase 10 complete when `Review status: PASS`.

## On REVISE

Fix loop: chart issues → `/chart-maker-run`; deck → `/visualization-reporting`; then re-run 10d → 10e.

See `docs/AGENT_ROLES.md`.

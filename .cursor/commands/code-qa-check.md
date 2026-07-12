---
name: code-qa-check
description: >-
  Sub-step 3b — code/reproducibility review of the phase 2 extraction code (SQL/Python):
  joins, filters, timezones, aggregation order. Writes code_review.md PASS/FAIL with
  fail_class. Runs as an isolated reviewer subagent after /data-qa-check.
---

Run **sub-step 3b** (Code QA Agent) as an **isolated reviewer** — dispatch a fresh-context
subagent; do not run the review inline in this session. Runs **after** 3a
(`/data-qa-check`), and runs **even when 3a is FAIL** (one complete rework brief for
phase 2 beats two round trips).

## Stop gate (check first, before dispatch)

**STOP and refuse** if `pull_manifest.md` is missing or `intake_contract.md` is not
`CLEAR`. Report what's missing; there is no code to locate without a manifest.

## Prerequisites

- `intake_contract.md` (`clarity_status: CLEAR`)
- `pull_manifest.md`
- `data_qa_report.md` exists (any verdict — used only in pass 2)

## Isolated reviewer dispatch

Launch a **Task subagent** (`generalPurpose`) with fresh context. The dispatch prompt must
contain **only**:

- The absolute study folder path
- Skill to load: `~/.cursor/skills/code-qa/SKILL.md` and
  `~/.cursor/skills/code-qa/workflows/code-review-playbook.md`
- Inputs (paths only): `intake_contract.md`, `pull_manifest.md`, the extraction code
  files the manifest references, project `docs/DEFINITIONS.md`; plus `data_qa_report.md`
  **marked "pass 2 only — do not read before pass 1 findings are written"**
- Report template path: `analysis/dedicated/_template/code_review.md`

**No-context-leak rule:** pass file paths only — never your own summary of the code, the
data, or an expected verdict. The reviewer forms its verdict from the artifacts alone.

**Write-scope rule (include verbatim in the prompt):** the subagent may write exactly one
file — `code_review.md` in the study folder. It must never edit the extraction code, data
files, the manifest, or any other study file. It must not re-run SQL or pulls.

**Return contract:** the subagent returns the verdict line (`Code review: PASS | FAIL`),
the `fail_class` if FAIL, and the report path. After it returns, **re-read
`code_review.md` from disk** and confirm the verdict matches before honoring the gate.

**Fallback:** if subagent dispatch is unavailable in this session, load skill `code-qa`
inline as before and add `review_isolation: inline-fallback` to the report header —
still honoring the two-pass order.

## Subagent steps (include in the dispatch prompt)

1. Locate extraction code via `pull_manifest.md`; no ad-hoc code → trivial-pull branch
   (PASS with mandatory inspection note)
2. **Pass 1:** run the playbook checks cold (joins, filters vs contract, timezones,
   aggregation order, hardcoding, reproducibility); write findings first
3. **Pass 2:** read `data_qa_report.md`; address every flagged anomaly (code cause or
   "no code cause found")
4. Write `code_review.md` from template; set `Code review: PASS | FAIL` and, on FAIL,
   `fail_class: extraction | contract`

## Must not

- Fix code, re-run pulls, or edit any study artifact
- Let the subagent read `data_qa_report.md` before pass 1 findings are written
- PASS with a known logic defect; FAIL without a `fail_class`
- Pre-summarize findings or hint at the expected verdict in the dispatch prompt

## Gate

Phase 4 requires **both** `data_qa_report.md` → `Ready for analysis: YES` **and**
`code_review.md` → `Code review: PASS`.

## On FAIL

- `fail_class: extraction` → escalate to phase 2 (`/data-pull` rework)
- `fail_class: contract` → escalate to phase 1 (`/analysis-intake` / user)

See `docs/AGENT_ROLES.md` § Reviewer isolation.

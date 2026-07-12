# Code review — {study_id}

Report date: YYYY-MM-DD
Reviewer role: Code QA Agent (sub-step 3b, isolated)
Sources: pull_manifest.md, extraction code files, intake_contract.md; data_qa_report.md (pass 2 only)

## Verdict

Code review: PASS | FAIL
fail_class:            # extraction | contract — required on FAIL, empty on PASS

## Code inspected

| File / query | Type (SQL / Python / task JSON) | Role in pull |
|--------------|--------------------------------|--------------|
| | | |

## Trivial-pull note (only if no meaningful extraction code)

_Mandatory when used: state exactly what was inspected and why it qualifies as trivial
(e.g. pre-registered task runner X, parameters only, no ad-hoc SQL/Python)._

## Pass 1 — findings (written before reading data_qa_report.md)

| # | File / section | Check (join / filter / timezone / aggregation / hardcoding / reproducibility) | Issue | Severity (Critical / High / Low) | Required fix |
|---|----------------|-------------------------------------------------------------------------------|-------|----------------------------------|--------------|
| | | | | | |

## Pass 2 — QA anomaly correlation

| Anomaly flagged in data_qa_report.md | Code cause found? | Detail |
|--------------------------------------|-------------------|--------|
| | YES / NO — no code cause found | |

### Pass 2 revisions to pass-1 findings

_Fill when data QA correlation contradicts or resolves a pass-1 conclusion; write `None` if no pass-1 finding changed._

| Pass-1 finding | Original conclusion | Revised conclusion | Why data QA changed / resolved it |
|----------------|---------------------|--------------------|-----------------------------------|
| | clean → defect / defect → clean | | |

## Reproducibility

- [ ] Every output in the manifest can be re-run from documented command + parameters
- [ ] Output naming traceable to producing code

## Escalation (on FAIL)

- fail_class extraction → phase 2 (`/data-pull` rework); list required fixes above
- fail_class contract → phase 1 (`/analysis-intake` / user); state the contract ambiguity

## Files

- pull_manifest.md
- data_qa_report.md
- intake_contract.md

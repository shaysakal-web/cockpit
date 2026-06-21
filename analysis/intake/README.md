# Ad-hoc intake artifacts

Store pipeline handoff files for requests **without** a dedicated `study_id`:

```
analysis/intake/<YYYY-MM-DD>_<slug>/
  intake_contract.md      # phase 1 — Main Analyst
  pull_manifest.md        # phase 2 — Data Analyst
  data_qa_report.md       # phase 3 — Data QA
  analysis_pack.md        # phase 4 — Python / Notebook
  analysis.md               # phase 5 — Executive Insight
  deliverables_manifest.md  # phase 6 — Visualization & Reporting
  notebooks/ tables/ charts/ reports/ presentations/  # optional
```

Templates: `analysis/dedicated/_template/`

Orchestration: `docs/AGENT_ROLES.md`

For dedicated studies, use `analysis/dedicated/<study_id>/` instead.

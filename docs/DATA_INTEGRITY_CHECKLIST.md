# Cockpit — data integrity checklist

Before trusting cross-world dashboard tiles:

- [ ] Each project `.env` / DB credentials work (`connection.py` or project verify script)
- [ ] `config/projects.json` paths point to correct folders on this machine
- [ ] Report roots exist (`analysis/reports/` for Svelte, `reports/` for funnel QA)
- [ ] After registry edits, restart Run Desk and hard-refresh browser (Ctrl+F5)

Per-world QA:

- **Svelte** — run Up2 monitor for yesterday; confirm HTML under `analysis/reports/up2_cancellation/`
- **Funnel QA** — run subscription QA for one brand/date; confirm `qa_export_*.json` and optional PDF in `reports/`
- **Conversion monitor** — run daily conversion monitor; confirm `reports/monitor_{brand}_{date}/`
- **Data QA** — run CRM or new-accounts check with dry-run; confirm JSON under `reports/data-quality/runs/`
- **Landing page** — run landing page check; confirm `reports/data-quality/landing_page_missing_pairs.csv`

See sibling [DATA_INTEGRITY_CHECKLIST.md](../../bmad/funny funnel qa/docs/DATA_INTEGRITY_CHECKLIST.md) for funnel-specific checks.

# Analysis pack

Report date: YYYY-MM-DD
Study: <id>
QA report: data_qa_report.md (Ready: YES)

## Data cleaning

- Source files: 
- Transformations: 
- Row counts: before → after

## Cohort tables

| Table | Path | Grain | Cohort anchor |
|-------|------|-------|---------------|
| | | | |

## Period comparison

| Metric | Baseline | Current | Delta | Delta % |
|--------|----------|---------|-------|---------|
| | | | | |

## Driver isolation

| Segment | Impact | Contribution % | Notes |
|---------|--------|----------------|-------|
| | | | |

## Statistical validation

Inferential comparisons only. Trend/monitoring views → § Comparisons flagged but not tested.

| comparison_id | Metric | Groups compared | Sample sizes | Observed diff | Test used | p-value or CI | Observed power | N add'l / group | Underpowered | Needs volume | Verdict | Business interpretation | Warning |
|---------------|--------|-----------------|--------------|---------------|-----------|---------------|----------------|-----------------|--------------|--------------|---------|-------------------------|---------|
| | | | | | | | | | | | | | |

Verdict values: `significant` / `directional_not_confirmed` / `inconclusive` / `insufficient_data`

- **`underpowered`:** post-hoc power &lt; 80% and not significant (analytic; does not alone trigger volume hint)
- **`needs_volume`:** insufficient or borderline sample — drives monitor volume subline (see `statistical-testing` skill § Observed power)

Detail CSV (optional): `tables/statistical_validation.csv`

## Comparisons flagged but not tested

| comparison_id | Metric | Groups / periods | Exemption code | Reason |
|---------------|--------|------------------|----------------|--------|
| | | | | |

Exemption codes: `descriptive_trend` / `reporting_only` / `comparability_limit` / `census` / `external_test` / `user_accepts_directional` / `insufficient_data`

## Open questions for Business Analyst Insights

- 

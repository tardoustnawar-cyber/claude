# Data dictionary (processed panels)

`data/processed/financial_did_panel.csv`, `patent_did_panel.csv` — one row per deal × relative year.

| Column | Meaning |
|---|---|
| Deal_ID | Workbook deal id (TRT-/CTL-) |
| Relative_Year | Calendar year − completion year (−3..+3) |
| Calendar_Year | Calendar year of the observation |
| Provisional_Classification | Innovation-driven / Alternative rationale / Borderline/mixed motive |
| Innovation_Deal | 1 innovation, 0 alternative, missing for borderline |
| Post_Excluding_t0 | 1 for t+1..t+3, else 0 |
| Treatment_x_Post | Innovation_Deal × Post |
| ROA_pct | Return on assets (%) — primary H2 |
| Operating_Margin_pct, Revenue_m, Total_Assets_m, Total_Debt_m, Net_Income_m, R_and_D_Expense_m, Leverage_pct | Bloomberg firm-year controls/secondary |
| Patent_Family_Count | Unique simple families by earliest priority year — primary H1 |
| Citation_Weighted_Output | Provisional raw forward citations (secondary, not normalised) |
| Acquirer_Normalized | Cluster id |
| n_pre / n_post / preferred / balanced | Coverage flags |

Frozen classification: `data/processed/master_transactions_classified.csv` (+ `.sha256`).

# Identification assessment

Full table: `outputs/audit/identification_diagnostics.xlsx`. Summary verdicts:

| Assumption | Verdict |
|---|---|
| Parallel trends (ROA) | Weak — not rejected only because the test is underpowered; visual divergence at t−3 |
| Parallel trends (patents) | **Rejected** (joint pre-trend p≈1e-15) — no causal reading of H1 |
| No anticipation | Partial — short announce-to-complete gaps; t0 excluded; residual t−1 anticipation possible |
| Stable pre-outcome classification | Protocol followed mechanically but classification unvalidated |
| No comparison-group contamination | Material false-negative risk (biotech targets in "alternative" group) |
| No overlapping treatment | Violated for repeat acquirers (GSK, Roche, Vectura, Zentiva) |
| Limited interference | Untestable; discussed qualitatively |
| Stable sample composition | Partially violated (Shire delisted 2019; Aduro→Chinook; Vectura/Skyepharma merger) |
| Group comparability | Severe size imbalance (SMD 1.0–1.5) |

**Bottom line.** The design does not currently support causal inference. H1 fails
its identifying test outright; H2 is at best a weakly-identified conditional association.

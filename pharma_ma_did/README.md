# Innovation-Driven M&A and Value Creation in European Pharma — Empirical Stage

Reproducible difference-in-differences (DiD) pipeline for the thesis
*"Innovation-Driven Mergers and Acquisitions and Value Creation in the European
Pharmaceutical Industry."*

The comparative estimand is the **differential** post-acquisition change in
innovation (H1) or financial (H2) performance for **innovation-driven** vs
**alternative-rationale** pharmaceutical acquisitions. Both groups completed
acquisitions; nothing here compares acquirers to non-acquirers.

## What the inputs actually were

Two pre-structured Excel workbooks (`data/raw/`) that had *already* imported and
cleaned the underlying GlobalData deal exports, per-company Bloomberg financial
workbooks, and Lens.org patent exports. No separate raw GlobalData/Bloomberg/Lens
files were supplied — they exist only as already-ingested content inside these two
workbooks. The pipeline therefore audits, deduplicates, classifies, reshapes,
and estimates from that content; it does not re-import primary sources.

## Pipeline (run in order)

| Script | Purpose |
|---|---|
| `src/00_extract_and_inventory.py` | Extract every sheet to `data/interim/`; Phase-1 inventory |
| `src/01_transaction_audit_and_classify.py` | Dedup, cross-file overlap, eligibility, **provisional** classification (frozen + SHA-256) |
| `src/02_build_panels.py` | Separate H1 (patent) and H2 (financial) deal-year panels |
| `src/03_coverage_audit.py` | Bloomberg/Lens mapping, missingness, attrition, availability matrix |
| `src/04_descriptives_balance.py` | Descriptives, group trajectories, pre-treatment SMD balance |
| `src/05_models.py` | Baseline DiD, FE-Poisson, IHS, event studies, robustness, wild-cluster bootstrap |
| `src/06_flow_and_diagnostics.py` | Sample-flow + coverage figures, identification-diagnostics table |

```bash
pip install openpyxl pandas numpy scipy statsmodels pyfixest matplotlib tabulate
for s in 00 01 02 03 04 05 06; do python3 src/${s}_*.py; done
```

Random seed `20260730` throughout. Environment is Python (R was unavailable);
`pyfixest` reproduces `fixest` TWFE estimates and the wild-cluster bootstrap is a
transparent null-imposed Rademacher implementation in `src/wcb.py`.

## The one thing to read before using any number

**No validated treatment classification exists in the source workbooks**
(`Final_Classification` is "Not reviewed" for all 351 deals; every evidence column
is a placeholder). Treatment here is a *provisional* label built from the
unvalidated GlobalData candidate screen plus announcement-text keywords, frozen
before estimation. Combined with very small usable samples (strict H2: 5 vs 6
deals; strict H1: 3 vs 6) and failed/weak parallel-trends checks, **every
coefficient in this repository is PROVISIONAL and not usable as a final thesis
result** until a human validates the classification against pre-acquisition target
evidence. See `docs/PRE_ESTIMATION_READINESS.md` and `docs/LIMITATIONS.md`.

## Outputs
- `outputs/audit/` — inventories, overlap, classification review, coverage, diagnostics
- `outputs/tables/` — descriptives, balance, main DiD, event study, robustness, hypothesis summary
- `outputs/figures/` — flow, coverage, pre-trends, event studies, trajectories
- `data/processed/` — frozen classification, firm-year tables, the two DiD panels
- `docs/` — full documentation set incl. `THESIS_RESULTS_DRAFT.md`

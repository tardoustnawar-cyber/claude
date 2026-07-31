# Pharma M&A empirical DiD — innovation-driven vs alternative-rationale transactions

Empirical execution of the thesis *Innovation-Driven Mergers and Acquisitions and Value
Creation in the European Pharmaceutical Industry*. This repository audits and repairs the
supplied DiD workbooks, reconstructs clean panels, freezes an evidence-based treatment
classification, and estimates difference-in-differences models for H1 (patents) and H2 (ROA).

> **Estimand:** the *differential* post-vs-pre change of an **innovation-driven** completed
> pharmaceutical M&A **relative to an alternative-rationale** completed M&A. Never "M&A vs
> no acquisition"; the comparison group is not untreated.

## Headline results (primary, provisional/associational)
| Hypothesis | β (Innovation × Post) | 95% CI | wild-boot p | pre-trend p | verdict |
|---|---|---|---|---|---|
| **H1 — patent families** | −0.46 | [−4.52, 3.61] | 0.82 | 0.96 | **Not supported** (imprecise null; PPML/IHS agree) |
| **H2 — ROA (pp)** | +10.78 | [−13.69, 35.24] | 0.40 | 0.57 | **Directionally consistent, not significant**; driven by ≤2 small acquirers |

Small samples (12–13 acquirer clusters), partial coverage, evidence-based (not
filing-archived) classification → results are **associational, not causal**. See
`outputs/thesis/EMPIRICAL_LIMITATIONS.md`.

## Pipeline (`src/`, run in order)
| Script | Phase | Output |
|---|---|---|
| `02_workbook_audit.py` | A | workbook structure, formula-error audit (315 `#REF!` confirmed) |
| `03_deal_master.py` | B | consolidated master, cross-file overlap tables |
| `04_classification.py` | C–D | frozen evidence-based classification (+ SHA-256) |
| `05_entity_mapping.py` | E | acquirer-group entity dictionary |
| `06_financial_panel.py` | F | ROA/margin deal-year panel + attrition |
| `07_patent_panel.py` | G | patent-family panel (validated vs family-long) |
| `08_sample_selection.py` | H | H1/H2 primary, serial, balanced samples |
| `09_descriptives_balance.py` | I | descriptives, SMD balance, common support |
| `10_estimate_did.py` | J–L | baseline DiD, event studies, robustness, leave-one-out |
| `11_placebo.py` | L | placebo (fake completion) |
| `12_figures.py` | 18 | figures 2–10 |
| `14_results_export.py` | 18–21 | consolidated tables, hypothesis matrix, flowchart |

Reproduce: `pip install -r requirements.txt` then run the scripts in the order above.
Seed = `20260730`. Raw workbooks in `data/raw/` are never modified.

## Key outputs
- **Thesis:** `outputs/thesis/CHAPTER_4_EMPIRICAL_RESULTS.md` (+ `.docx` with embedded
  figures), `CHAPTER_5_DISCUSSION_BRIDGE.md`, `EMPIRICAL_LIMITATIONS.md`,
  `HYPOTHESIS_DECISION_TABLE.xlsx`.
- **Tables:** `outputs/tables/` (T1–T12).
- **Figures:** `outputs/figures/` (fig1–fig10).
- **Audit:** `outputs/audit/` (structure, formula errors, cross-file overlap,
  classification review, conflict log).
- **Decisions:** `ANALYSIS_DECISIONS.md`, `DATA_DICTIONARY.md`.

## Environment notes
- **R unavailable** → estimation in Python (`statsmodels`/`linearmodels`) with cluster-robust
  SEs and a hand-implemented restricted wild-cluster bootstrap. Documented in the conflict log.
- **No network access** → classification uses workbook-embedded announcement text +
  GlobalData rationale; no external filings archived.
- The methodology and literature DOCX files referenced by the master prompt were **not
  supplied**; the master prompt's restated protocol governs (see conflict log).

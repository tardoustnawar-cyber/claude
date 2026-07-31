# Data dictionary

## Processed panels (`data/processed/`)
| File | Grain | Key columns |
|---|---|---|
| `deal_master_classified.csv` | canonical economic event | `deal_event_id`, `member_deal_ids`, `acquirer`, `target`, `completion_year`, `Final_Classification`, `Classification_Confidence`, `Eligibility`, `InnovationDeal`, `acquirer_group` |
| `entity_dictionary.csv` | event | `deal_event_id`, `acquirer`, `acquirer_group`, `ambiguous_flag` |
| `financial_deal_year_panel.csv` | event × calendar year | `ROA_pct`, `Operating_Margin_pct`, `Revenue_m`, `Total_Assets_m`, `log_assets`, `leverage`, `RelativeYear` |
| `patent_deal_year_panel.csv` | event × priority year | `patent_families`, `asinh_families`, `citations`, `RelativeYear`, `Coverage_Basis` |
| `h1_patent_did_panel.csv` / `h2_financial_did_panel.csv` | estimation rows | `treat`, `Post`, `TreatPost`, `acquirer_group`, outcome |
| `*_serial.csv`, `*_balanced.csv` | sensitivity samples | as above |

## Key constructed variables
| Variable | Definition |
|---|---|
| `deal_event_id` | `EVT-` + hash of canonical event key (normalised acquirer+target+completion date) |
| `RelativeYear` | `calendar/priority year − completion year` |
| `Post` | 1 if `RelativeYear ≥ 1` (primary; t0 omitted) |
| `treat` | 1 if `Final_Classification == High-confidence innovation-driven` |
| `TreatPost` | `treat × Post` — the DiD interaction; its coefficient is β |
| `acquirer_group` | parent/group key unifying variant acquirer names (Roche, GSK, …); cluster unit |
| `ROA_pct` | Bloomberg standardised Return on Assets (pp); realised actuals only |
| `patent_families` | unique simple patent families by earliest priority year |

## Classification categories
High-confidence innovation-driven · Alternative-rationale · Mixed / borderline ·
Ineligible transaction · Insufficient evidence (not data-carrying).

## Model coefficients
`Y = deal FE + calendar-year FE + δ·Post + β·(Innovation×Post) + ε` — δ = alternative-group
pre/post change; δ+β = innovation-group change; β = differential. SEs clustered by
`acquirer_group`; wild-cluster bootstrap p reported when clusters < 30.

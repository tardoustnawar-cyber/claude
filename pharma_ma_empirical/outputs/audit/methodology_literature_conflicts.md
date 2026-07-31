# Methodology / literature conflict log

## Document availability (important)
The master prompt names four inputs. **Only three were supplied** to this run:

| Referenced file | Supplied? | Role |
|---|---|---|
| `Treatment_Group_DiD_Data_Workbook…xlsx` | ✅ yes | Source data |
| `Control_Group_DiD_Data_Workbook…xlsx` | ✅ yes | Source data |
| `…Chapter_3_Research_Methodology…docx` | ❌ **not supplied** | Binding empirical protocol |
| `lmn…docx` (literature review) | ❌ **not supplied** | Theoretical framing |

Because the two DOCX files were not provided, the **master prompt itself** — which
restates the empirical protocol in detail — is treated as the governing document for
every empirical decision. Where the master prompt is explicit (estimand, H1/H2 only,
comparison of two completed-M&A groups, evidence-based classification, event window,
inference), those instructions govern. No text was invented to stand in for the missing
methodology or literature chapters.

## Governing decisions (from the master prompt, treated as the protocol)
| Empirical decision | Governing rule | Source |
|---|---|---|
| Estimand | Differential post-vs-pre change of innovation-driven **vs alternative-rationale completed M&A** — never "M&A vs no acquisition" | Master prompt §2 |
| Confirmatory hypotheses | **Only H1 and H2**. H3–H5 not estimated as confirmatory | Master prompt §2 |
| Comparison group | Two categories of **completed** transactions; comparison is **not** "non-acquiring"/"untreated" | Master prompt §2 |
| Classification | GlobalData extracts are **first-stage screens**, reassigned on **pre-completion evidence** | Master prompt §8 |
| Panels | Rebuild from source layers; **do not trust** `Panel_DiD` cached values / `#REF!` | Master prompt §3, §10–11 |
| Event window | t−3…t+3, omit t0; pre = t−3…t−1, post = t+1…t+3 | Master prompt §12 |
| Inference | Cluster by acquirer; wild bootstrap when clusters < ~30 | Master prompt §14 |

## Outdated statements to avoid (per master prompt §1)
- The literature review's references to "non-acquiring controls" and to H3–H5 as final
  hypotheses are **superseded**. This analysis reports only H1/H2 and never uses
  "treatment vs untreated" or "non-acquiring control group" language.

## Estimation-environment deviation
- The protocol prefers **R** (`fixest`, etc.). **R is unavailable** in this environment,
  so estimation uses **Python** (`statsmodels`, `linearmodels`) with two-way fixed
  effects, cluster-robust SEs by acquirer, a hand-implemented **restricted wild-cluster
  bootstrap** (Rademacher weights), Poisson **PPML**, and IHS robustness. This is the
  documented fallback permitted by the master prompt §4.

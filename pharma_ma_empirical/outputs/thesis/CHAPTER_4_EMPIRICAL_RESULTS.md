# Chapter 4 — Empirical Results

*Innovation-Driven Mergers and Acquisitions and Value Creation in the European
Pharmaceutical Industry*

> **Estimand.** Every coefficient below measures the **differential** post-versus-pre
> change associated with an **innovation-driven** pharmaceutical transaction **relative to
> an alternative-rationale transaction**. Both groups complete an M&A transaction. No
> coefficient should be read as the effect of acquiring versus not acquiring.

> **Status of this chapter.** The results are reported as **adjusted associations from a
> small, provisional analytical sample**. They satisfy the design's data-cleaning and
> identification checks (deduplicated events, frozen evidence-based classification,
> reconstructed panels, examinable pre-trends, both groups represented), but the number of
> acquirer clusters (12–13) is small and outcome coverage is partial. Estimates are
> therefore precise enough to *describe direction and rule ranges in/out only weakly*, not
> to support causal claims.

---

## 4.1 Final sample construction

The two source workbooks contained **351 candidate transactions** (45 in the innovation
extract, 306 in the alternative extract). Consolidating on a canonical economic-event key
(normalised acquirer + normalised target + exact completion date) collapsed **42 cross-file
duplicate events** — deals GlobalData had placed in *both* screens — and **3 within-file
duplicate pairs**, yielding **306 unique economic events**. The treatment workbook's
`Panel_DiD` sheet was found to contain **315 `#REF!` formula errors** in the interaction
column and was discarded; all panels were rebuilt from source layers (Table 1).

Classification was performed on **pre-completion evidence** and by evidence rather than by
source workbook. This is consequential: the innovation screen contained clear commercial
**false positives** (e.g. Nicox/Doliage — an ophthalmic *product* portfolio; Esteve/Riemser
— a specialty *product* and manufacturing deal), while the alternative screen contained
clear R&D **false negatives** (e.g. Roche/Trophos — a Phase I neurodegeneration pipeline;
Ipsen/Syntaxin — a toxin *technology platform* and IP; UCB/Handl — *gene-therapy* discovery
capability). Among data-carrying deals, adjudication produced **13 high-confidence
innovation-driven** and **12 alternative-rationale** events (Table 3); two ineligible deals
(a childcare business and an 8.31% minority stake) and two mixed/borderline deals
(Vectura/Skyepharma; a reverse merger) were excluded from the primary analysis.

Because several acquirers recur (Roche 3×, GSK 2×, Recordati 2×) and same-firm financial
series are identical, the **primary sample retains one non-overlapping event per acquirer
group**, and all standard errors are clustered by acquirer. Serial-acquirer and balanced
samples are estimated as sensitivities (Table 2, Figure 1).

## 4.2 Outcome-specific coverage

Separate samples were constructed for each hypothesis (they need not contain the same
firms). Applying the preferred rule (≥ 2 non-missing pre and ≥ 2 non-missing post
observations, t0 omitted) and the one-event-per-acquirer restriction gives:

| Sample | Events | Acquirer clusters | Innovation | Alternative | Obs |
|---|---|---|---|---|---|
| **H2 — ROA (primary)** | 12 | 12 | 8 | 4 | 72 |
| **H1 — patent families (primary)** | 13 | 13 | 7 | 6 | 72 |

Coverage by relative year is shown in Figure 2. The samples are small and the innovation
side is dominated by small biotech/speciality acquirers.

## 4.3 Descriptive statistics (Tables 4–5)

**Return on Assets (pp).** The innovation group enters with a **lower and far more volatile**
pre-period ROA (mean −6.1, s.d. 35.9; driven by loss-making biotechs, minimum ≈ −110) than
the alternative group (mean +3.9, s.d. 13.0). Raw pre→post ROA change is **+9.0 pp for
innovation** versus **+0.3 pp for alternative** — directionally consistent with H2.

**Patent families.** The innovation group is more patent-intensive pre-deal (mean 11.7
families/yr vs 2.5) and its output **declines** post-completion (raw −3.9) while the
alternative group is roughly flat (raw −0.3) — directionally consistent with H1.

## 4.4 Pre-treatment comparability and common support (Table 6, Figures 7–8)

Standardised mean differences are **large**: for H2, pre-period ROA SMD ≈ −0.36 with a
variance ratio > 7, and pre-deal log-assets (0.90) and revenue (1.19) show the innovation
acquirers are markedly smaller; for H1, the pre-outcome SMD ≈ 1.12. Common-support overlap
exists but is thin, especially in the lower ROA tail (innovation only) and the upper
patent tail (innovation only). Deal fixed effects absorb these **level** differences, but
the imbalance means **pre-trends carry the identification burden**, and a matched/weighted
specification is **not credibly supported** at this sample size (matching on 12 events would
discard most of the data for cosmetic balance). Unweighted results are therefore the
benchmark, as the protocol requires.

## 4.5 H1 — differential patent output (Tables 7, 9; Figures 4, 6)

The two-way fixed-effects model gives a differential effect of

> **β(Innovation × Post) = −0.46 patent families** (cluster-robust SE 2.07;
> 95% CI [−4.52, 3.61]; p = 0.83; **wild-bootstrap p = 0.82**), 13 events, 13 clusters.

Decomposition: the alternative group's modelled post change is δ = +5.20 families and the
innovation group's is δ + β = +4.74; the **differential is essentially zero**. The IHS
specification (β = 0.11, p = 0.85) and **Poisson PPML** (β = 0.05, p = 0.93) agree. The
event study (Figure 6) shows differential coefficients hovering around zero in every
post-year (+2.6, −1.5, −1.4 for t+1…t+3) with wide intervals, and the **joint pre-trend
test does not reject parallel pre-trends (p = 0.96)**.

**Reading.** The data do **not** support H1 at conventional levels: there is no detectable
differential in patent-family output between the two rationales over the three post years.
Given the wide confidence interval, this is an **imprecise null**, not evidence of exact
equivalence.

## 4.6 H2 — differential ROA (Tables 8, 9; Figures 3, 5)

> **β(Innovation × Post) = +10.78 pp** (cluster-robust SE 12.48; 95% CI [−13.69, 35.24];
> p = 0.39; **wild-bootstrap p = 0.40**), 12 events, 12 clusters.

Decomposition: alternative post change δ = +2.76 pp; innovation post change δ + β = +13.53
pp. The **point estimate is in the hypothesised direction** (innovation deals show a more
favourable post-ROA change), but it is **not statistically distinguishable from zero** and
the interval is very wide. The event study (Figure 5) shows positive but insignificant
post coefficients (+12.0, +9.9, +2.2) and a **non-rejected pre-trend test (p = 0.57)**,
though the pre-period differentials (−2.7, −4.6 pp) are not negligible in magnitude and
counsel caution.

## 4.7 Robustness and sensitivity analyses (Table 10)

| Perturbation | H2 β (ROA) | H1 β (families) |
|---|---|---|
| Primary (unique acquirer, ≥2/≥2) | +10.78 | −0.46 |
| Serial acquirers included | +6.43 | −0.81 |
| Balanced 3-pre/3-post | +10.78 | −1.22 |
| Winsorised 1/99 (pre-declared) | +10.10 | — |
| Include t0 as post | +11.29 | — |
| IHS / PPML (patents) | — | +0.11 / +0.05 |
| Placebo (fake completion t−2, pre-only) | −3.18 (p 0.77) | +0.20 (p 0.98) |

All signs are stable; **no specification makes either estimate significant**. Placebo tests
are correctly near zero. The winsorised and balanced results confirm the H2 point estimate
is not an artefact of a single extreme year, but…

## 4.8 Identification diagnostics and influence (Table 11, Figure 10)

Leave-one-acquirer-out analysis reveals that **H2 is fragile**: dropping **Biodexa** (a
micro-cap with extreme ROA swings) collapses β from +10.78 to **+0.43**, while dropping
Roche pushes it to +14.33. The positive H2 signal is therefore **driven by a small number
of tiny, volatile acquirers**, not a broad-based pattern. H1 is stable across leave-one-out
(β ∈ [−1.59, +1.00]), consistent with its precise-null character. Neither outcome shows a
pre-trend violation, but low power means the pre-trend tests are weak evidence.

## 4.9 Joint interpretation

Taken together, the pattern is **H1 ≈ 0 (imprecise null) and H2 > 0 in point estimate but
insignificant and outlier-driven**. This is closest to the master framework's "H1 negative
/ null, H2 positive" cell — nominally consistent with an innovation–finance story in which
innovation-driven acquirers realise no *additional* near-term patent output relative to
other acquirers, while showing a *more favourable* short-run ROA change — **but the evidence
here is far too weak to assert that mechanism**. The confidence intervals include zero for
both hypotheses, and the H2 direction hangs on one or two firms.

## 4.10 Summary of findings and readiness status

- **H1 (patents):** **Not supported** at conventional levels; differential ≈ 0; robust to
  PPML/IHS/serial/balanced; pre-trends not rejected. *Status: associational, precise-null.*
- **H2 (ROA):** **Directionally consistent** (positive) with the hypothesis but **not
  statistically significant**, wide interval, and **driven by influential small acquirers**.
  *Status: associational, not confirmed.*

Every number in this chapter is traceable to an exported file in `outputs/tables/`,
`outputs/models/`, or `outputs/figures/`. The models are **provisional/associational, not
final causal estimates**: the samples are small, coverage is partial, and classification —
though evidence-based — relies on GlobalData-embedded announcement text rather than archived
primary filings (no network access). These constraints, and the classification-error
discussion, are detailed in `EMPIRICAL_LIMITATIONS.md`.

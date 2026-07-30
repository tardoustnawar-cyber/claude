# Empirical Results (Provisional Draft)

> **Status.** Every estimate below is provisional. Treatment status rests on an
> unvalidated classification protocol, the usable samples are very small (5–6
> deals per group), and the parallel-trends assumption is weak (H2) or rejected
> (H1). The estimates are reported as **conditional associations**, not causal
> effects. See §12–13.

## 1. Final sample formation

The two workbooks contained 351 candidate deal rows (45 innovation-driven
candidates, 306 alternative-rationale candidates). The two exports are **not**
mutually exclusive: 39 `Cross_File_Key` values appear in both files (verified —
the treatment and control overlap sets are identical). Three of these carry
populated outcome data in both files with identical values (GSK/Okairos,
Shire/Premacure, Esteve/Riemser) and were each resolved to a single event; three
further exact-duplicate rows (Vectura/Skyepharma, Vectura/Activaero, SBI/photonamic)
and one duplicated acquirer firm-year (Roche 2015) were removed. This leaves 307
unique economic events.

Outcome coverage — not classification — is the binding constraint. Only 27 deals
carry any Bloomberg ROA in the event window and 21 carry any Lens patent-family
count. Requiring ≥2 usable pre- and ≥2 usable post-observations yields **20 deals
for H2** and **17 for H1**. Restricting to the strict innovation-vs-alternative
contrast (excluding text-flagged borderline/mixed-motive deals) leaves:

- **H2 (financial):** 5 innovation-driven vs 6 alternative-rationale deals (66 firm-year ROA observations, 11 acquirer clusters).
- **H1 (patent):** 3 innovation-driven vs 6 alternative-rationale deals (49 firm-year observations, 9 acquirer clusters).

## 2. Financial vs patent samples

The two panels are deliberately **not** forced onto the same deals. Private and
Bloomberg-unmatched acquirers (e.g. Servier/Symphogen) remain in the transaction
universe and, where Lens data exist, in the patent panel, even though they are
absent from the financial panel. Full attrition is in
`outputs/audit/sample_attrition.xlsx`.

## 3. Descriptive statistics (strict samples)

| Panel | Group | Deals | Pre mean | Post mean | Raw change |
|---|---|---|---|---|---|
| ROA (%) | Innovation-driven | 5 | −11.69 | 1.03 | **+12.72** |
| ROA (%) | Alternative | 6 | 5.85 | −0.97 | **−6.83** |
| Patent families | Innovation-driven | 3 | 15.43 | 12.89 | **−2.54** |
| Patent families | Alternative | 6 | 2.88 | 2.82 | **−0.05** |

The raw (unmodelled) differential change is **+19.5 pp** for ROA and **−2.5
families** for patents — both in the *direction* predicted by H2 and H1
respectively. These are descriptive contrasts, heavily confounded (see §4).

## 4. Balance and pre-treatment trends

The groups are severely imbalanced on pre-treatment characteristics
(`outputs/tables/balance_table.csv`). Standardised mean differences:

| Variable | Innovation | Alternative | SMD |
|---|---|---|---|
| Total assets (€m) | 31,890 | 576 | **1.08** |
| Revenue (€m) | 14,535 | 419 | **1.22** |
| R&D expense (€m) | 2,624 | 50 | **1.53** |
| Pre-deal patent families | 15.4 | 2.9 | **1.32** |
| Pre-deal ROA (%) | −11.7 | 5.9 | −0.51 |

The innovation-driven group is dominated by large-cap acquirers (Sanofi, GSK,
Shire); the alternative group is mostly small firms. No transparent matching can
balance the two without discarding almost the entire sample. Pre-treatment event
coefficients diverge (§7), so the parallel-trends premise is not credible on its
face.

## 5. Baseline H1 (innovation / patent families)

TWFE DiD, deal + calendar-year fixed effects, acquirer-clustered SEs:

- Linear DiD: β(Innovation×Post) = **+0.67 families** (SE 2.61; 95% CI −5.34 to 6.68; p=0.80; wild-cluster p=0.77).
- FE-Poisson (PPML): β = **+0.21** (SE 0.43; p=0.62), i.e. ≈ +24% semi-elasticity, imprecise.
- IHS(families): β = +0.37 (SE 0.61; p=0.56).

The differential is statistically indistinguishable from zero. The point estimate
is *positive*, i.e. the **opposite** sign to the H1 prediction of a relatively
weaker innovation path — but the confidence interval spans large effects in both
directions, so H1 is neither supported nor refuted.

## 6. Baseline H2 (financial / ROA)

- ROA DiD: β(Innovation×Post) = **+23.6 pp** (SE 15.7; 95% CI −11.3 to 58.5; p=0.16; wild-cluster p=0.30).
- Operating margin (secondary): β = −215.7 (SE 268; p=0.44) — dominated by near-zero-revenue firms and uninformative.

The ROA differential is large, positive, and in the direction predicted by H2
(innovation-driven acquirers improving relatively more), but not statistically
significant. The pre-treatment ROA mean in the estimation sample is −2.1 pp, so
the point estimate is economically very large relative to baseline and should be
read as an artefact of small-sample volatility rather than a settled magnitude.

## 7. Dynamic event studies

Differential (Innovation − Alternative) coefficients, reference year t−1
(`outputs/tables/event_study_results.csv`, figures `event_study_*.png`):

- **ROA:** t−3 = −33.1 (SE 18.2), t−2 = +0.64; post t+1 = +17.2, t+2 = +15.1, t+3 = +2.7. The large, imprecise t−3 differential signals **diverging pre-trends**; the joint pre-trend test does not reject (p=0.18) only because the test is underpowered.
- **Patents:** t−3 = −19.4 (SE 3.2), t−2 = −5.2; joint pre-trend test **rejected** (p≈1×10⁻¹⁵). The pre-period divergence is driven by Sanofi's pre-acquisition patent ramp-up. A conventional TWFE event study is not valid here.

## 8. Robustness (`outputs/tables/robustness_results.csv`)

The H2 ROA differential stays positive and insignificant across: including t0 as
post (β=20.1, p=0.21), 100%-acquisitions-only (β=1.3, p=0.35 — collapses to 5
deals), the broad sample adding borderline deals (β=21.2, p=0.13), and 5/95
winsorising (β=7.8, p=0.23). Leave-one-firm-out swings the ROA point estimate
from +8.6 (drop Biodexa) to +33.2 (drop Sanofi), i.e. **individual firms move the
coefficient by more than its own value** — the hallmark of an underpowered design.
The H1 patent differential stays near zero and insignificant throughout
(100%-only β=1.0 p=0.80; broad β=−0.03 p=0.99).

## 9. Classification sensitivity

Because treatment is a provisional label, classification error is a first-order
concern, not a robustness footnote. 13 of 26 data-carrying deals are text-flagged
borderline/mixed; several nominally "alternative" deals involve biotech targets
with pipelines (Roche/Tusk, GSK/GlycoVaxyn, Ipsen/Syntaxin), a false-negative
pattern that would attenuate the contrast toward zero. Moving borderline deals
into the treatment group (broad sample) barely changes the estimates, which is
consistent with the contrast being dominated by firm size rather than by
innovation orientation.

## 10. Economic magnitude

Taken at face value (which §12 says not to), the H2 estimate implies
innovation-driven acquirers improve post-deal ROA by ~20 pp *more* than
alternative-rationale acquirers — implausibly large and a direct consequence of
comparing €30bn firms with €0.5bn firms over a 6-year window. The H1 estimate
implies essentially no differential in patent-family output.

## 11. Joint innovation–finance pattern

The provisional pattern (relatively stronger finance, flat-to-slightly-stronger
innovation for the innovation-driven group) would, *if it survived validation and
power*, be broadly consistent with successful integration or with large acquirers
absorbing small targets without disrupting their own output. It is equally
consistent with pure firm-size confounding. The data cannot separate these.

## 12. Limitations

See `docs/LIMITATIONS.md`. The binding ones: unvalidated treatment classification;
5–6 deals per strict group; severe covariate imbalance; failed (H1) / weak (H2)
parallel trends; overlapping treatments for repeat acquirers; unharmonised patent
export scopes; provisional (non-age-normalised) citations.

## 13. What these models do and do not identify

Under the maintained assumptions, β is **the differential post-acquisition change
in the outcome for deals classified innovation-driven under this observable text
protocol, relative to deals classified alternative-rationale** — conditional on
deal and calendar-year fixed effects. It is **not** the effect of completing an
acquisition versus not, **not** the effect of true (unobserved) managerial
motive, and — given the failed identification checks and power — **not** a causal
effect at all in the H1 case and only a weakly-identified association in the H2
case. No hypothesis should be reported as confirmed or rejected from these
numbers.

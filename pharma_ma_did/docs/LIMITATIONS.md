# Limitations

1. **Unvalidated treatment.** Classification is provisional (screen + text). Until a human
   validates it against pre-acquisition target patent/pipeline/platform evidence, no
   coefficient is a final result.
2. **Tiny samples.** Strict H2 = 5 vs 6 deals (11 clusters); strict H1 = 3 vs 6 (9 clusters).
   Leave-one-out swings the ROA estimate from +8.6 to +33.2 — single firms dominate.
3. **Severe imbalance.** Innovation acquirers are ~50× larger by assets/revenue and hold
   ~5× the pre-deal patent stock. Firm size, not innovation orientation, plausibly drives
   any contrast. Matching is infeasible without discarding the sample.
4. **Parallel trends.** Rejected for patents (joint pre-trend p≈1e-15, driven by Sanofi);
   weak and visually violated for ROA (large imprecise t−3 differential). H1 cannot be
   causal; H2 is at best a weakly-identified association.
5. **Comparison-group contamination.** Several "alternative" deals have biotech targets with
   pipelines (Roche/Tusk, GSK/GlycoVaxyn, Ipsen/Syntaxin) — false negatives that attenuate
   the contrast.
6. **Overlapping treatments.** 61 acquirers have multiple deals; GSK, Roche, Vectura, Zentiva,
   Esteve recur inside event windows.
7. **Data scope.** Patent export scopes are unharmonised (Sanofi EP-only; GSK Haleon-heavy;
   Roche diagnostics-heavy). Citations are provisional raw forward counts, not age/field
   normalised — excluded from primary inference. Operating margin is distorted by
   near-zero-revenue firms.
8. **Missingness is informative.** Private/Bloomberg-unmatched acquirers are absent from H2,
   not zero-valued; this is documented, not imputed.

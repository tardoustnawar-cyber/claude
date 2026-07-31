# Empirical limitations

1. **Small analytical samples / few clusters.** The primary samples contain 12 (H2) and 13
   (H1) events and equally few acquirer clusters. Even with wild-cluster bootstrap
   inference, power is low and confidence intervals are wide. Insignificant estimates are
   **not** evidence of no difference or of equivalence.

2. **Partial outcome coverage.** Bloomberg financials and Lens patents are populated for
   only a subset of the eligible transaction universe. The analysis prioritised
   data-carrying deals (per protocol); the many eligible deals without imported outcomes
   cannot enter H1/H2 and their exclusion is not random with respect to firm size/listing.

3. **Classification relies on GlobalData-embedded evidence, not archived filings.** No
   network access was available, so pre-completion company announcements and target filings
   could not be retrieved and archived. Classification used the announcement text embedded
   in the workbook descriptions plus the GlobalData rationale. Residual **classification
   error is expected**: false positives inflate treatment heterogeneity; **false negatives
   in the comparison group attenuate the contrast** (several were identified and reassigned,
   but others may remain among non-data-carrying deals). Bias direction is not guaranteed.

4. **Poor pre-treatment balance.** Innovation acquirers are systematically smaller and more
   volatile. Fixed effects remove level differences but not differential dynamics; a
   credible matched/weighted counterfactual is not supported at this sample size. Fixed
   effects cannot manufacture a counterfactual where common support is thin.

5. **Influence of individual firms.** The H2 point estimate is driven by one or two small,
   volatile acquirers (notably Biodexa); dropping them collapses the effect. Results should
   not be generalised beyond the support region.

6. **Outcome-metric limits.** Patent-family counts by earliest priority year measure
   innovation **quantity**, not value or quality; the citation-weighted secondary outcome
   could not be constructed credibly at these cell sizes and is not reported. Operating
   margin is mechanically extreme for near-zero-revenue biotechs and is reported only on a
   revenue-restricted, winsorised basis.

7. **Patent search-scope heterogeneity.** Lens applicant searches differ across companies
   (explicit vs inferred ranges; occasional EP-only or limited-subsidiary scope, e.g.
   Sanofi/Ablynx). A strict scope-consistent sample would shrink the already small sample
   further.

8. **Staggered completion timing.** Completions span 2012–2020. Two-way FE DiD with
   heterogeneous timing can be biased; cohort-stratified/stacked event studies were not
   feasible at these cell sizes and remain future work.

9. **Estimation environment.** R (`fixest` etc.) was unavailable; estimation used Python
   equivalents with a hand-implemented restricted wild-cluster bootstrap. Results were
   cross-checked across linear FE, PPML, and IHS but not against an independent R
   implementation.

10. **Missing protocol documents.** The binding methodology chapter and literature review
    (DOCX) were not supplied to this run; the master prompt's restated protocol governed.
    Any methodology detail not captured in the master prompt could not be honoured.

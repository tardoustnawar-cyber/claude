# MASTER PROMPT FOR CLAUDE CODE
## Complete empirical execution of the European pharmaceutical innovation-driven M&A thesis

You are acting as a senior empirical researcher, econometrician, research-data engineer, and Master’s thesis supervisor. Your task is to execute the entire empirical stage of the thesis—not merely describe what should be done.

You must inspect the supplied files, audit and repair the analytical data, construct the final samples, estimate the Difference-in-Differences models, diagnose the identifying assumptions, run robustness analyses, generate publication-quality tables and figures, and write a thesis-ready empirical-results chapter. Do not fabricate data or conclusions. Do not stop after producing a plan.

---

## 1. FILES TO USE

Search the project directory recursively and locate these files, allowing for harmless filename variations:

1. `Treatment_Group_DiD_Data_Workbook_Financial_and_Patent_Populated(2).xlsx`
2. `Control_Group_DiD_Data_Workbook_Financial_and_Patent_Populated(4).xlsx`
3. `Nawar_TARDOUST_Chapter_3_Research_Methodology_Final_Revised(1).docx`
4. `lmn(4).docx`

Treat the revised methodology chapter as the binding empirical protocol. Use the literature review for theoretical framing, mechanisms, prior evidence, and discussion of findings. Where the literature review still refers to non-acquiring controls or presents H3–H5 as final hypotheses, do not reproduce those outdated empirical statements. The final empirical design compares two categories of completed M&A transactions, and only H1 and H2 are confirmatory.

Before coding, extract and read the complete text of both DOCX files using `python-docx` or another reproducible parser. Create a short conflict log showing any inconsistency between the literature review and the methodology, and state which document governs each empirical decision.

---

## 2. THESIS QUESTION, ESTIMAND, AND HYPOTHESES

Thesis title:

**Innovation-Driven Mergers and Acquisitions and Value Creation in the European Pharmaceutical Industry**

Broader research question:

**Do innovation-driven acquisitions create value for acquiring firms in the European pharmaceutical industry?**

Empirical question supported by the available design:

**How do post-acquisition changes in innovation and financial performance among acquirers undertaking innovation-driven pharmaceutical transactions differ from the corresponding changes among acquirers undertaking transactions motivated primarily by scale, market access, geographic expansion, diversification, customer access, or operational efficiency?**

Both groups complete an M&A transaction. The comparison group is not untreated. Therefore, the estimand is the differential post-versus-pre change associated with an innovation-driven transaction relative to an alternative-rationale transaction. Never interpret the coefficient as the effect of M&A relative to no acquisition.

Primary hypotheses:

- **H1 — Differential innovation performance:** Relative to alternative-rationale pharmaceutical transactions, innovation-driven transactions are expected to be associated with a less favourable post-acquisition change in annual patent-family output during the three full years following completion.
- **H2 — Differential financial performance:** Relative to alternative-rationale pharmaceutical transactions, innovation-driven transactions are expected to be associated with a more favourable post-acquisition change in Return on Assets during the three full fiscal years following completion.

Primary outcomes:

- H1: annual unique simple patent-family count.
- H2: Bloomberg standardised Return on Assets, in percentage points.

Secondary outcomes:

- age/cohort-normalised citation-weighted patent output, only if it can be constructed credibly;
- Bloomberg operating margin, interpreted cautiously when revenue is very low.

Do not estimate H3, H4, or H5 as confirmatory hypotheses. Technological relatedness and relative target knowledge-base size are exploratory only if systematic target patent portfolios exist. Cross-border relocation is not testable without inventor-location data.

---

## 3. IMPORTANT KNOWN FEATURES AND TECHNICAL WARNINGS

Verify these facts independently before using them, then report any discrepancy:

- The treatment workbook contains 45 candidate treatment transactions.
- The comparison workbook contains 306 candidate alternative-rationale transactions.
- Thirty-nine treatment candidates are flagged as appearing in both initial rationale extracts.
- The workbooks contain populated Bloomberg and Lens.org information only for subsets of the initial transaction universes.
- The `Final_Classification`, `Classification_Confidence`, and `Main_DiD_Decision` fields are not yet completed for the transactions.
- The treatment workbook’s `Panel_DiD` sheet contains broken `#REF!` formulas in the `Treatment_x_Post` column. Do not repair the analysis by trusting cached Excel values. Reconstruct all treatment, post, interaction, and panel variables programmatically.
- The control workbook’s `Panel_DiD` sheet contains an empty `Column1` and does not provide a final treatment indicator. Reconstruct the unified panel from source fields.

Do not treat either existing `Panel_DiD` sheet as authoritative. Use `Deal_Master_Wide`, `Financial_Long_Raw`, `Patent_Year_Summary`, `Patent_Family_Long`, the import logs, and the variable dictionaries as source layers, then rebuild clean panels from scratch.

Never overwrite either original workbook.

---

## 4. REPRODUCIBLE PROJECT STRUCTURE

Create this structure:

```text
pharma_ma_empirical/
  data/
    raw/
    interim/
    processed/
  src/
    00_environment_check.py
    01_file_inventory.py
    02_workbook_audit.py
    03_deal_master.py
    04_classification.py
    05_entity_mapping.py
    06_financial_panel.py
    07_patent_panel.py
    08_sample_selection.py
    09_descriptives_balance.py
    10_did_financial.R
    11_did_patents.R
    12_event_studies.R
    13_robustness.R
    14_results_export.py
  outputs/
    audit/
    data/
    tables/
    figures/
    models/
    logs/
    thesis/
  README.md
  DATA_DICTIONARY.md
  ANALYSIS_DECISIONS.md
  requirements.txt
  renv.lock
```

Python may be used for file ingestion, Excel repair, reshaping, classification tables, and exports. Use R for the main econometric analysis where available, preferably with `fixest`, `data.table`, `tidyverse`, `modelsummary`, `ggplot2`, `fwildclusterboot`, `clubSandwich`, `MatchIt`, `WeightIt`, and `cobalt`. If R is unavailable, use Python with `pandas`, `statsmodels`, `linearmodels`, and appropriate clustered/small-sample inference, and document the limitations.

Set and record random seeds. Record package versions. Preserve raw files unchanged.

---

## 5. PHASE A — COMPLETE FILE AND WORKBOOK AUDIT

Inspect every sheet, header row, formula, data type, named range, merged cell, and row count in both workbooks.

Produce:

- `outputs/audit/file_inventory.xlsx`
- `outputs/audit/workbook_structure.xlsx`
- `outputs/audit/formula_error_audit.xlsx`
- `outputs/audit/data_availability_matrix.xlsx`
- `outputs/audit/methodology_literature_conflicts.md`

For each workbook and sheet, report:

- dimensions;
- header row;
- key identifiers;
- formulas versus stored values;
- formula errors;
- duplicate rows;
- blank or malformed columns;
- years covered;
- companies covered;
- whether values are raw, calculated, or imported;
- whether the sheet is safe for analytical use.

Do not silently accept Excel-derived averages, deltas, completeness flags, or interaction terms. Recalculate them in code and compare them with the workbook fields as an audit.

---

## 6. PHASE B — BUILD ONE CONSOLIDATED DEAL MASTER

Read row 2 as the header of each `Deal_Master_Wide` sheet and rows 3 onward as observations. Append the two workbooks while retaining:

- original workbook;
- original `Deal_ID`;
- original group;
- initial treatment indicator;
- all GlobalData rationales;
- transaction descriptions;
- classification fields;
- financial and patent coverage fields.

Create a stable unified `deal_event_id`.

Deduplicate using, in order:

1. a reliable existing deal identifier where present;
2. normalised acquirer + normalised target + exact completion date;
3. normalised acquirer + normalised target + completion year, followed by manual verification.

Standardise legal suffixes only for matching, while preserving raw names. Use fuzzy matching only to propose candidates; never merge automatically on fuzzy similarity alone.

Create a cross-file overlap table that reports:

- exact overlapping economic events;
- conflicting or multiple rationales;
- duplicate rows within each workbook;
- acquirers with several transactions;
- transactions with overlapping ±3-year windows;
- missing or conflicting completion dates;
- acquisition, merger, majority, minority, and reverse-acquisition forms.

Save:

- `data/interim/deal_master_unclassified.csv`
- `outputs/audit/cross_file_overlap.xlsx`
- `outputs/audit/repeated_acquirer_calendar.xlsx`

One economic event must appear only once in the final master file.

---

## 7. PHASE C — ELIGIBILITY AND CONTROL TRANSFER

Apply the methodology consistently.

Strict primary sample:

- completed M&A transaction;
- completion from 1 January 2012 through 31 December 2020;
- European pharmaceutical or biotechnology scope as defined in the methodology;
- identifiable acquirer and target;
- verified completion date/year;
- 100% company acquisition;
- identifiable reporting acquirer before and after completion.

Broader sensitivity sample:

- verified majority acquisitions with transfer of control;
- mergers with a clearly identifiable surviving reporting entity and continuous financial/patent history.

Exclude from the strict sample:

- minority stakes;
- unclear mergers of equals;
- reverse acquisitions without entity continuity;
- licensing, alliances, joint ventures, or non-completed deals;
- transactions outside the stated sector/date scope;
- product or asset purchases that do not transfer control of a company, unless explicitly analysed in a separate sensitivity sample.

Create a transparent eligibility decision and exclusion reason for every data-carrying transaction.

---

## 8. PHASE D — FINAL TREATMENT CLASSIFICATION

The two GlobalData rationale lists are first-stage screens, not final mutually exclusive treatment labels.

### Candidate innovation signals

- `Expand Offering / Add Products`
- `Access to Resources`
- `Integration — Forward or Backward`

They count as innovation-driven only when the substantive content concerns pipelines, proprietary molecules, patents, research platforms, scientific teams, R&D facilities, clinical-development capabilities, diagnostics, or another R&D-specific stage.

They do not count as innovation-driven when the content concerns mature products, brands, generics, factories, manufacturing capacity, supply chains, distribution, sales teams, or raw materials.

### Candidate alternative-rationale signals

- `Increase Scale / Business Expansion`
- `Geographic Expansion`
- `Business Diversification`
- `Operational Synergy`
- `Access to New Customer Segment`

These remain in the comparison group when scale, geography, customers, mature commercial products, production, cost efficiency, or organisational integration dominate and acquisition of a material pipeline/platform/research capability is not a central motive.

### Required final categories

- High-confidence innovation-driven
- Medium-confidence innovation-driven
- Alternative-rationale
- Mixed / borderline
- Insufficient evidence
- Ineligible transaction

High-confidence innovation-driven requires both:

1. a verifiable material pre-acquisition innovation asset held by the target; and
2. contemporaneous transaction evidence that access to that asset was central to the deal.

The strict primary model compares high-confidence innovation-driven transactions with clearly alternative-rationale transactions. Medium-confidence innovation deals enter a broader sensitivity model. Mixed, borderline, and insufficient-evidence deals are excluded from the primary analysis.

### How to perform classification

First prioritise transactions that can actually enter H1 or H2 because they have usable financial or patent data. Do not waste time manually researching all 351 raw rows before dealing with the analytical candidates.

Use only pre-completion information. Do not inspect post-acquisition outcome paths while classifying.

Use this evidence hierarchy:

1. official company transaction announcement published before or at completion;
2. target annual report, investor presentation, pipeline page, or regulatory filing available before completion;
3. pre-deal patent portfolio and technology description;
4. credible contemporaneous industry source;
5. GlobalData description and rationale.

If network access is available, research and archive official sources. If network access is unavailable, classify only where the workbook’s descriptions and imported evidence are sufficient. Mark the rest `Insufficient evidence`; do not invent facts.

Record for each reviewed deal:

- target innovation asset;
- patent evidence;
- pipeline evidence;
- platform evidence;
- R&D capability evidence;
- commercial/geographic evidence;
- control-transfer status;
- final classification;
- confidence;
- source URL or source file;
- source date;
- concise justification;
- reviewer status.

Freeze the classification before estimating models. Save a versioned checksum.

Outputs:

- `outputs/audit/deal_classification_review.xlsx`
- `data/processed/deal_master_classified.csv`
- `outputs/audit/unresolved_data_carrying_deals.xlsx`
- `outputs/audit/classification_summary.md`

If final classification cannot be completed, continue with an explicitly labelled **provisional GlobalData-screen model**, but never present it as the final thesis model. Keep validated and provisional results in separate tables and folders.

---

## 9. PHASE E — ENTITY RESOLUTION

Create a versioned entity dictionary linking:

- GlobalData acquirer and target names;
- normalised names;
- Bloomberg company name and ticker;
- Lens applicants and owners;
- historical names;
- parent companies;
- relevant subsidiaries;
- transaction-specific surviving entity.

Do not use filenames as the sole company identifier.

Save:

- `data/processed/entity_dictionary.csv`
- `outputs/audit/entity_mapping_review.xlsx`

Flag ambiguous mappings instead of forcing them.

---

## 10. PHASE F — RECONSTRUCT THE FINANCIAL PANEL

Use `Financial_Long_Raw`, the financial import logs, and the deal master. Do not rely on the existing `Panel_DiD` formulas.

Use only realised historical observations. Exclude `Current`, estimates, forecasts, LTM, and NTM. Treat blanks and dashes as missing, not zero.

Primary outcome:

- `ROA_pct`, using the consistent Bloomberg standardised field.

Secondary outcome:

- `Operating_Margin_pct`.

Descriptive/balance variables where consistently available:

- revenue;
- operating income;
- net income;
- total assets;
- total debt;
- leverage;
- R&D expense;
- R&D intensity;
- log total assets.

Do not mix Bloomberg-reported ratios with researcher-reconstructed ratios in the same primary series. If a reconstructed ratio is used, label it and estimate it separately.

Create one row per `deal_event_id × fiscal-year-end calendar year`. Map the fiscal-year-end year to completion year as specified in the methodology. The fiscal period containing completion is the mixed period and is omitted from the primary static comparison.

Report every exclusion reason:

- private/unavailable acquirer;
- unmatched company;
- insufficient actual history;
- missing primary outcome;
- ambiguous entity continuity;
- overlapping event;
- ineligible transaction.

Save:

- `data/processed/financial_deal_year_panel.csv`
- `outputs/audit/financial_attrition.xlsx`
- `outputs/audit/financial_missingness.xlsx`

---

## 11. PHASE G — RECONSTRUCT THE PATENT PANEL

Use `Patent_Family_Long`, `Patent_Year_Summary`, the patent import logs, and the entity dictionary.

Primary invention unit:

- unique simple patent family.

Timing:

- earliest priority year.

Deduplicate across:

- publications belonging to the same family;
- repeated exports;
- overlapping searches;
- parent/subsidiary applicant names;
- historical company names;
- multiple sample applicants.

A zero company-year is valid only when search scope and year coverage are verified. Otherwise, retain missing.

Primary H1 variable:

- annual unique simple patent-family count for the acquirer group and mapped subsidiaries.

Secondary citation variable:

- construct from family-level cited-by information;
- account for patent age/right truncation;
- normalise at least by earliest-priority-year cohort;
- use broad CPC field normalisation only if cell sizes are adequate;
- do not treat raw lifetime citations as comparable quality measures.

Document differences in Lens search scope. Run a strict scope-consistent patent sample if searches differ materially across companies.

Save:

- `data/processed/patent_family_clean.csv`
- `data/processed/patent_deal_year_panel.csv`
- `outputs/audit/patent_deduplication.xlsx`
- `outputs/audit/patent_scope_coverage.xlsx`
- `outputs/audit/patent_attrition.xlsx`

---

## 12. PHASE H — EVENT TIME AND ANALYTICAL SAMPLES

Define:

```text
RelativeYear = ObservationYear − CompletionYear
```

Window:

- t−3, t−2, t−1, t0, t+1, t+2, t+3.

Primary static model:

- pre = t−3 to t−1;
- post = t+1 to t+3;
- omit t0.

Dynamic model:

- t−1 reference category.

Preferred unbalanced sample:

- at least two non-missing pre observations and two non-missing post observations for the relevant primary outcome.

Balanced robustness sample:

- all three pre and all three post observations.

Construct separate H1 and H2 samples. Do not force them to contain the same firms.

Repeated acquirers:

- strict sample retains non-overlapping event windows;
- censor the first event at the next major qualifying transaction where defensible;
- estimate first-deal-only and serial-acquirer sensitivity samples;
- cluster all standard errors by acquirer.

Do not duplicate the same acquirer-year outcome across overlapping deal windows in the strict model.

Outputs:

- `data/processed/h1_patent_did_panel.csv`
- `data/processed/h2_financial_did_panel.csv`
- `outputs/audit/sample_selection_flow.xlsx`
- `outputs/audit/event_time_support.xlsx`

---

## 13. PHASE I — DESCRIPTIVES, COMPARABILITY, AND COMMON SUPPORT

Before regression, report separately for H1 and H2:

- number of deals;
- number of unique acquirers;
- observations;
- completion years;
- countries;
- subsectors;
- deal forms;
- cross-border status;
- outcome coverage by relative year;
- missingness;
- pre- and post-outcome means;
- outliers;
- patent zeros.

Assess pre-treatment comparability using only variables measured before completion:

- average primary outcome at t−3 to t−1;
- pre-outcome slope over t−3 to t−1;
- log assets;
- revenue;
- leverage;
- operating margin;
- patent stock;
- R&D intensity where available;
- completion-year cohort;
- country;
- subsector;
- deal form;
- cross-border status.

Calculate standardised mean differences, variance ratios, and visual distributions. Produce a Love plot. Assess common support explicitly.

If the groups have adequate overlap, run a secondary matched/weighted specification. Prefer the simplest defensible method:

1. exact/coarsened matching on completion-year cohort and broad subsector;
2. then nearest-neighbour, Mahalanobis, or entropy balancing using a small number of pre-treatment variables.

Never match on post-treatment variables. Never discard most observations merely to obtain cosmetic balance. Report unweighted results as the benchmark.

If common support is poor, state that fixed effects cannot manufacture a credible counterfactual. Restrict to the support region if defensible and report the loss of external validity.

---

## 14. PHASE J — BASELINE DIFFERENCE-IN-DIFFERENCES MODELS

Estimate separately for every outcome:

```text
Y_d,t = α_d + λ_t + δ Post_d,t + β(InnovationDeal_d × Post_d,t) + ε_d,t
```

Where:

- `α_d` = deal-event fixed effects;
- `λ_t` = calendar-year effects;
- `Post` = full post years;
- `InnovationDeal` = validated treatment classification;
- `β` = differential post-acquisition change for innovation-driven versus alternative-rationale deals.

Interpretation:

- `δ` = pre/post change for the alternative-rationale group;
- `δ + β` = pre/post change for the innovation-driven group;
- `β` = differential change.

Report all three, not only β.

Financial models:

- linear fixed-effects ROA model as primary;
- linear fixed-effects operating-margin model as secondary.

Patent models:

1. linear fixed-effects patent-family model as transparent primary scale;
2. fixed-effects Poisson/PPML where feasible;
3. inverse-hyperbolic-sine transformation as robustness.

Inference:

- cluster by acquirer;
- report the number of clusters;
- add wild-cluster bootstrap inference when clusters are fewer than approximately 30;
- where extremely small, add CR2/Satterthwaite or another defensible small-sample correction;
- report coefficient, SE, 95% CI, p-value, wild-bootstrap p-value, observations, deal events, acquirers, pre-treatment mean, and economic magnitude.

Do not treat insignificant results as proof of no difference or equivalence.

---

## 15. PHASE K — COMPARATIVE EVENT STUDY

Estimate:

```text
Y_d,t = α_d + λ_t
      + Σ[k ≠ −1] δ_k 1(RelativeYear_d,t = k)
      + Σ[k ≠ −1] β_k [InnovationDeal_d × 1(RelativeYear_d,t = k)]
      + ε_d,t
```

Use t−1 as the reference.

Report and plot:

- the alternative-rationale trajectory `δ_k`;
- the innovation-driven trajectory `δ_k + β_k`;
- the differential trajectory `β_k`;
- 95% confidence intervals;
- deals/acquirers/observations supporting each event time.

Test the pre-treatment interaction coefficients jointly. Also inspect their signs and magnitudes visually. Failure to reject does not prove parallel trends.

Because completion years are staggered, estimate cohort-stratified or stacked event studies within completion-year blocks as robustness where sample support permits. Do not mechanically apply never-treated estimators because every unit completes an acquisition.

If pre-trends are materially different, do not attempt to rescue causal interpretation through specification mining. Present the results as adjusted associations and explain the identification failure.

---

## 16. PHASE L — ROBUSTNESS PROGRAMME

Run, as feasible:

### Classification

- high-confidence innovation deals only;
- high + medium confidence;
- original GlobalData group indicator as a clearly labelled benchmark;
- exclusion of all unresolved overlaps;
- exclusion of mixed/borderline deals;
- leave-one-treatment-deal-out;
- leave-one-acquirer-out.

### Transaction scope

- strict 100% acquisitions;
- verified broader control-transfer sample including majority acquisitions and eligible mergers;
- acquisitions only, excluding mergers;
- first-deal-only sample;
- exclusion/censoring of overlapping events.

### Timing and coverage

- omit t0 in the main model;
- include t0 as post;
- first complete fiscal/calendar year after completion;
- alternative ±2 and ±4 windows where coverage permits;
- preferred ≥2 pre/≥2 post sample;
- balanced 3-pre/3-post sample.

### Financial outcomes

- raw ROA;
- pooled winsorised ROA, with the threshold declared before viewing the robustness coefficient;
- operating income divided by average assets where available;
- raw and winsorised operating margin;
- exclude low-revenue observations that generate mechanically extreme margins, using a transparent threshold and sensitivity table.

### Patent outcomes

- linear family count;
- PPML;
- IHS family count;
- scope-consistent company searches only;
- active/pending/granted families as sensitivity if status data are reliable;
- full versus fractional allocation of jointly attributed families;
- cohort-normalised citations.

### Identification

- placebo completion dates in pre-periods;
- alternative comparison-support restriction;
- matched/weighted estimates;
- pre-trend slope adjustment only as a clearly labelled sensitivity, not as a preferred rescue model;
- influence diagnostics.

Do not run underpowered subgroup analyses merely to increase the number of tables.

---

## 17. RESULT INTERPRETATION

Use the literature review to interpret, not to predetermine, results.

Possible patterns:

- **H1 negative, H2 positive:** consistent with innovation–finance divergence, cost consolidation, removal of duplicate projects, or faster financial synergies; not proof of value destruction.
- **H1 positive, H2 positive:** consistent with successful knowledge integration and complementary assets; the regressions do not independently identify the mechanism.
- **H1 negative, H2 negative:** may reflect integration problems, overpayment, disruption, weak fit, or pre-existing deterioration; pre-trends are critical.
- **H1 positive, H2 negative:** may reflect continued R&D investment, development lags, or short-run integration costs.
- **Insignificant estimates:** may reflect small true differences, low power, wide heterogeneity, classification error, incomplete coverage, or a short window. Report confidence intervals and precision.

Classification error must be discussed substantively:

- false positives increase treatment heterogeneity;
- false negatives contaminate the comparison group and often attenuate contrasts;
- non-random disclosure means bias direction may be unpredictable.

Never claim that results prove a true managerial motive.

---

## 18. REQUIRED TABLES AND FIGURES

Tables:

1. Data and file audit.
2. Sample-selection and attrition flow.
3. Final classification counts and evidence confidence.
4. Financial-sample descriptive statistics.
5. Patent-sample descriptive statistics.
6. Pre-treatment balance and standardised mean differences.
7. Main H1 estimates.
8. Main H2 estimates.
9. Event-study coefficients and pre-trend tests.
10. Robustness results.
11. Leave-one-out/influence results.
12. Hypothesis conclusion matrix.

Figures:

1. Sample-selection flowchart.
2. Outcome coverage heatmap by deal and relative year.
3. Group-specific mean ROA trajectory.
4. Group-specific mean patent-family trajectory.
5. ROA event-study plot.
6. Patent event-study plot.
7. Balance Love plot.
8. Common-support distributions.
9. Main coefficient plot.
10. Leave-one-acquirer-out influence plot.

All figures must have publication-quality labels, units, captions, confidence intervals where relevant, and notes on sample size. Do not use misleading truncated axes.

---

## 19. THESIS-READY WRITING OUTPUTS

Create:

- `outputs/thesis/CHAPTER_4_EMPIRICAL_RESULTS.md`
- `outputs/thesis/CHAPTER_4_EMPIRICAL_RESULTS.docx` if Pandoc or another reliable conversion tool is available;
- `outputs/thesis/CHAPTER_5_DISCUSSION_BRIDGE.md`
- `outputs/thesis/EMPIRICAL_LIMITATIONS.md`
- `outputs/thesis/HYPOTHESIS_DECISION_TABLE.xlsx`

Chapter 4 structure:

1. Final sample construction.
2. Outcome-specific coverage.
3. Descriptive statistics.
4. Pre-treatment comparability and common support.
5. H1 baseline and dynamic results.
6. H2 baseline and dynamic results.
7. Robustness and sensitivity analyses.
8. Identification diagnostics.
9. Joint interpretation of innovation and financial outcomes.
10. Summary of findings and readiness status.

Use cautious academic wording:

- “The estimate indicates…”
- “The result is consistent with…”
- “Conditional on the stated assumptions…”
- “The confidence interval includes…”
- “The coefficient measures the differential post-acquisition change…”

Avoid:

- “This proves…”
- “The acquisition caused…” when identification is weak;
- “There is no effect…” solely because p > 0.05;
- “Treatment versus untreated”;
- “Non-acquiring control group.”

Every reported number in the prose must be traceable to an exported model table or descriptive file.

---

## 20. DECISION RULES AND HONEST FAILURE MODES

Do not present a model as final unless:

- economic events have been deduplicated;
- cross-file overlaps have one final classification;
- eligibility/control-transfer rules are applied;
- classification is frozen;
- primary outcomes have sufficient pre/post coverage;
- repeated-acquirer overlaps are addressed;
- financial actuals are distinguished from estimates;
- patent families are deduplicated and coverage is validated;
- both final groups remain represented;
- pre-treatment trajectories can be examined.

If any condition fails:

1. complete every feasible audit and cleaning step;
2. generate the exact review file needed to solve the blockage;
3. run only explicitly provisional models where defensible;
4. clearly separate final, provisional, and descriptive outputs;
5. explain what additional data or human decisions are required.

Do not ask broad questions before inspecting the files. Ask only narrowly targeted questions that cannot be resolved from the supplied data.

---

## 21. FINAL CONSOLE AND README SUMMARY

At completion, report:

- files inspected;
- workbook formula errors found;
- initial deal rows by source;
- unique economic events after deduplication;
- cross-file overlaps;
- eligible strict and broader transactions;
- final classification counts;
- unresolved data-carrying deals;
- financial-panel deals, acquirers, observations, and clusters;
- patent-panel deals, acquirers, observations, and clusters;
- common-support assessment;
- parallel-trend assessment for H1 and H2;
- principal H1 coefficient and inference;
- principal H2 coefficient and inference;
- most consequential robustness result;
- influence of individual firms;
- whether each result is final, provisional, associational, or not estimable;
- exact paths of all outputs.

Begin now by reading the methodology and literature review, then auditing both workbooks. Do not begin with generic advice, and do not stop at a research plan.

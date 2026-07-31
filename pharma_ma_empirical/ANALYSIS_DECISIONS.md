# Analysis decisions log

Every non-obvious decision, with rationale. Seed: `20260730`.

## Workbook audit
- Treatment `Panel_DiD` contains **315 `#REF!` formula cells** in the `Treatment_x_Post`
  block (confirmed). Control `Panel_DiD` has an empty `Column1` and no final treatment
  indicator. **Neither `Panel_DiD` sheet was used.** All panels rebuilt from
  `Deal_Master_Wide` (header row 2), `Financial_Long_Raw`, and `Patent_Year_Summary`.

## Deduplication
- Raw rows: 351 (treatment 45 + control 306).
- **Canonical economic event key** = normalised acquirer + normalised target + exact
  completion date. Legal suffixes stripped for matching only; raw names preserved.
- 42 events appear in **both** workbooks (cross-file), 3 further within-file duplicate
  pairs (Vectura/Activaero, MediGene, SBI/Photonamic) → **306 unique economic events**.
- Cross-file twins are events GlobalData placed in **both** the innovation and the
  alternative screen extract — exactly the ambiguous "appears in both extracts" case.
  They are resolved by evidence, not by source workbook.

## Classification (frozen; SHA-256 recorded in `data/processed/deal_master_classified.SHA256`)
- Classification is on **pre-completion evidence** (deal descriptions embedding
  announcement text + GlobalData rationale). **No network access** → no external filings
  archived; only data-carrying deals adjudicated (master-prompt priority rule).
- **Screen error is real and bidirectional.** Reassigned on evidence:
  - False positives (commercial deals in the innovation screen → Alternative): Nicox/Doliage,
    Eurofins/AROS, Esteve/Riemser, Cardiome/Correvio.
  - False negatives (R&D/pipeline deals in the alternative screen → Innovation): Roche/Trophos,
    Roche/Tusk, Roche/Signature, GSK/GlycoVaxyn, Ipsen/Syntaxin, UCB/Handl, Vectura/Activaero.
- High-confidence innovation-driven requires (1) a verifiable material pre-deal innovation
  asset (pipeline/platform/patents/R&D capability) **and** (2) contemporaneous evidence
  that access to that asset was central.

## Eligibility
- Strict = 100% acquisition, 2012–2020, pharma/biotech, identifiable acquirer+target,
  verified completion, identifiable reporting acquirer. Broader = majority control-transfer
  or merger with identifiable surviving entity.
- **Ineligible caught by evidence:** Busy Bees/Teddy Bear (childcare — out of sector);
  Swedbank Robur/Camurus (8.31% minority — no control transfer).

## Financial panel
- Bloomberg standardised `ROA_pct` (primary), `Operating_Margin_pct` (secondary).
- Realised actuals only: blanks/dashes → missing (never 0); calendar years capped at
  **≤ 2023** to exclude Bloomberg estimate/NTM years (still admits t+3 for 2020 deals).
- Cross-file twin carrying data in both workbooks → keep the source series with the most
  in-window non-missing ROA (avoids duplicating an acquirer-year).

## Patent panel
- Primary source: `Patent_Year_Summary` deduplicated **unique simple family** counts by
  **earliest priority year**. Validated against `Patent_Family_Long`: exact agreement for
  6 of 7 treatment deals; TRT-0010 (Sanofi/Ablynx) differs because the family-long export
  and the year-summary use different applicant-search scopes (documented EP-only provisional
  flag) — the summary count is retained as the scope-consistent series.

## Repeated acquirers (critical)
- **Roche** appears 3× (Trophos 2015, Signature 2015, Tusk 2018); **GSK** 2× (Okairos 2013,
  GlycoVaxyn 2015); **Recordati** 2×. Same-firm ROA series are identical, so including all
  would duplicate acquirer-years.
- **Primary sample = one non-overlapping event per acquirer group** (earliest completion),
  identified via a manually resolved `acquirer_group` key (e.g. "F. Hoffmann-La Roche Ltd"
  and "Roche Holding AG" → Roche). **All SEs clustered by `acquirer_group`.**
- Serial-acquirer (all events) and balanced 3/3 samples estimated as sensitivities.

## Model
- `Y = deal FE + calendar-year FE + Post + β·(Innovation × Post) + ε`. Treatment main effect
  absorbed by deal FE; report δ (Post = alternative change), δ+β (innovation change), and β.
- Inference: cluster by acquirer; restricted **wild-cluster bootstrap** (Rademacher, B=1999)
  because clusters ≈ 12–13 (< 30). PPML and IHS for the count outcome.
- Winsorisation threshold (1/99) **pre-declared** before viewing robustness coefficients.
- Operating margin restricted to revenue ≥ €50m and winsorised, because it explodes
  mechanically for near-zero-revenue biotechs.

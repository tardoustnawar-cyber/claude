# Analysis decisions

- **Unit of analysis:** deal-event (`Deal_ID`), time = relative year t−3..t+3.
  Deal fixed effects absorb time-invariant firm/deal characteristics; calendar-year
  fixed effects absorb common shocks. SEs clustered on acquirer to handle
  repeat-acquirer correlation; wild-cluster bootstrap reported given few clusters.
- **Treatment:** Innovation-driven=1, Alternative-rationale=0. Borderline/mixed
  excluded from the strict primary sample; added only in the broad sensitivity run.
- **Treatment source:** no manual classification existed in the workbooks. Provisional
  label = GlobalData candidate screen (`Initial_Group`) combined with keyword scoring
  of the deal Description/Rationale; contradictions downgraded to borderline. Frozen to
  `data/processed/master_transactions_classified.csv` with a SHA-256 checksum before any
  model was estimated.
- **Event timing:** completion year = t0. Primary Post = t+1..t+3 (t0 excluded because it
  mixes pre/post months). Robustness includes t0 as post. Reference year for event study = t−1.
- **Coverage:** preferred sample requires ≥2 non-missing pre and ≥2 non-missing post
  observations. Blank = missing (never zero). A patent count of 0 inside observed Lens
  coverage is a real zero.
- **Deduplication:** 3 cross-file overlaps with data resolved to one event each (documented
  in `src/01`); 3 exact-duplicate rows dropped; Roche-2015 duplicated firm-year collapsed
  (keep CTL-0234).
- **Outcomes:** primary H2 = ROA (%), primary H1 = annual patent-family count. Secondary:
  operating margin, IHS/log patents, FE-Poisson, provisional raw citations.
- **Software:** Python (R unavailable). `pyfixest` for TWFE/PPML; manual null-imposed
  Rademacher wild-cluster bootstrap (`src/wcb.py`) because the `wildboottest` package
  errors on string cluster labels. Seed 20260730.

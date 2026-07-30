"""
02_build_panels.py  -- Phase 6: construct the separate H1 (patent) and
H2 (financial) deal-year panels from the wide Deal_Master_Wide sheets.

Design choices (documented in ANALYSIS_DECISIONS.md):
  * Unit = DEAL-EVENT. Cross-sectional id = Deal_ID. Time = Relative_Year.
    Most acquirers are single-deal; where an acquirer repeats, SEs are
    clustered on the acquirer and multi-deal acquirers are flagged so the
    firm-level correlation is handled and can be removed in robustness.
  * Treatment: Innovation-driven = 1, Alternative rationale = 0.
    Borderline/mixed-motive deals are EXCLUDED from the strict primary sample
    (kept only for a broad sensitivity sample).
  * Event window t-3..t+3; t0 excluded from the pre/post split (Post =
    t+1..t+3). Reference year for event study = t-1.
  * Duplicated events (dup_drop) removed. Roche 2015 duplicated firm-year
    (CTL-0230/CTL-0234) collapsed to one row (keep CTL-0234, 100% deal).
  * Coverage: preferred sample requires >=2 usable pre AND >=2 usable post
    outcome observations. A blank remains missing; a patent 0 inside observed
    Lens coverage is a real zero.
"""
import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERIM = os.path.join(ROOT, "data/interim")
PROC = os.path.join(ROOT, "data/processed")
os.makedirs(PROC, exist_ok=True)

RELS = ["-3", "-2", "-1", "0", "+1", "+2", "+3"]
RELN = {"-3": -3, "-2": -2, "-1": -1, "0": 0, "+1": 1, "+2": 2, "+3": 3}

t = pd.read_csv(os.path.join(INTERIM, "treatment__Deal_Master_Wide.csv"))
c = pd.read_csv(os.path.join(INTERIM, "control__Deal_Master_Wide.csv"))
wide = pd.concat([t, c], ignore_index=True)
cls = pd.read_csv(os.path.join(INTERIM, "master_transactions_classified.csv"))

meta_cols = ["Deal_ID", "Provisional_Classification", "Provisional_Confidence",
             "Initial_Group", "screen_group", "Completion_Year", "Acquirer_Normalized",
             "Target_Normalized", "Acquirer_Raw", "Target_Raw", "Deal_Subtype_Level_3",
             "Deal_Country_s", "Deal_Value_USD_m", "Financial_Currency",
             "Multiple_Deal_Acquirer", "dup_drop", "eligible_strict", "eligible_broad"]
meta = cls[meta_cols].copy()

# same-firm-year duplicate to drop from panels (keep CTL-0234)
DROP_FIRM_YEAR_DUP = ["CTL-0230"]

FIN_VARS = ["Revenue_m", "Operating_Income_m", "Net_Income_m", "Total_Assets_m",
            "Total_Debt_m", "R_and_D_Expense_m", "ROA_pct", "Operating_Margin_pct",
            "Leverage_pct"]
PAT_VARS = ["Patent_Family_Count", "Citation_Weighted_Output"]


def reshape(wide_df, varlist):
    recs = []
    for _, r in wide_df.iterrows():
        for s in RELS:
            rec = {"Deal_ID": r["Deal_ID"], "Relative_Year": RELN[s],
                   "Calendar_Year": r.get(f"Calendar_Year_t{s}")}
            for v in varlist:
                rec[v] = r.get(f"{v}_t{s}")
            recs.append(rec)
    return pd.DataFrame(recs)


def build_panel(varlist, outcome, tag):
    long = reshape(wide, varlist).merge(meta, on="Deal_ID", how="left")
    long = long[~long.dup_drop & ~long.Deal_ID.isin(DROP_FIRM_YEAR_DUP)]
    long["Post_Excluding_t0"] = (long.Relative_Year >= 1).astype(int)
    long["is_t0"] = (long.Relative_Year == 0).astype(int)
    long["Innovation_Deal"] = np.where(
        long.Provisional_Classification.eq("Innovation-driven"), 1,
        np.where(long.Provisional_Classification.eq("Alternative rationale"), 0, np.nan))
    long["Treatment_x_Post"] = long.Innovation_Deal * long.Post_Excluding_t0

    # coverage: usable pre (t-3..t-1) and post (t+1..t+3) non-missing outcome
    pre = long[long.Relative_Year.isin([-3, -2, -1])].groupby("Deal_ID")[outcome].apply(lambda s: s.notna().sum())
    post = long[long.Relative_Year.isin([1, 2, 3])].groupby("Deal_ID")[outcome].apply(lambda s: s.notna().sum())
    cov = pd.DataFrame({"n_pre": pre, "n_post": post}).fillna(0)
    cov["preferred"] = (cov.n_pre >= 2) & (cov.n_post >= 2)     # >=2 pre & >=2 post
    cov["minimal"] = (cov.n_pre >= 2) & (cov.n_post >= 2)       # same threshold; balanced flagged below
    cov["balanced"] = (cov.n_pre == 3) & (cov.n_post == 3)
    long = long.merge(cov.reset_index(), on="Deal_ID", how="left")

    # analysis rows: exclude t0 from pre/post estimation panel, keep for event study separately
    long["in_strict_group"] = long.Innovation_Deal.notna()   # excludes borderline
    long.to_csv(os.path.join(PROC, f"{tag}_did_panel.csv"), index=False)
    return long, cov


fin, fin_cov = build_panel(FIN_VARS, "ROA_pct", "financial")
pat, pat_cov = build_panel(PAT_VARS, "Patent_Family_Count", "patent")

# also persist firm-year processed tables (non-missing outcome only)
fin[fin.ROA_pct.notna()].to_csv(os.path.join(PROC, "financial_firm_year.csv"), index=False)
pat[pat.Patent_Family_Count.notna()].to_csv(os.path.join(PROC, "patent_firm_year.csv"), index=False)


def summarise(long, outcome, cov, label):
    strict = long[long.in_strict_group & long.preferred]
    deals = strict.groupby(["Deal_ID", "Innovation_Deal"]).size().reset_index()
    n_innov = int((deals.Innovation_Deal == 1).sum())
    n_alt = int((deals.Innovation_Deal == 0).sum())
    obs = int(strict[outcome].notna().sum())
    print(f"\n=== {label} panel (strict primary: preferred coverage, "
          f"innovation vs alternative) ===")
    print(f"  deals: innovation={n_innov}, alternative={n_alt}")
    print(f"  non-missing {outcome} observations: {obs}")
    print(f"  balanced (3 pre & 3 post) deals with data: "
          f"{int(cov.balanced.sum())}")
    return {"panel": label, "n_innov": n_innov, "n_alt": n_alt, "n_obs": obs}


s1 = summarise(fin, "ROA_pct", fin_cov, "FINANCIAL / H2 (ROA)")
s2 = summarise(pat, "Patent_Family_Count", pat_cov, "PATENT / H1 (families)")

pd.DataFrame([s1, s2]).to_csv(os.path.join(ROOT, "outputs/tables", "panel_sizes.csv"), index=False) \
    if os.path.isdir(os.path.join(ROOT, "outputs/tables")) else None
print("\nPanels written to data/processed/.")

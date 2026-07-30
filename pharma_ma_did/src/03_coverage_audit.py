"""
03_coverage_audit.py -- Phase 4/5 coverage audits.

The Bloomberg and Lens data were already imported and cleaned inside the
workbooks (historical actuals only; families by earliest priority year). This
script surfaces that provenance into the required audit tables and documents
why each acquirer is present/absent from each panel.

Outputs:
  outputs/audit/bloomberg_file_mapping.xlsx
  outputs/audit/bloomberg_missingness.xlsx
  outputs/audit/lens_file_mapping.xlsx
  outputs/audit/patent_owner_dictionary.xlsx
  outputs/audit/patent_deduplication_report.xlsx
  outputs/audit/sample_attrition.xlsx
  outputs/audit/data_availability_matrix.csv
"""
import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERIM = os.path.join(ROOT, "data/interim")
PROC = os.path.join(ROOT, "data/processed")
AUDIT = os.path.join(ROOT, "outputs/audit")


def rd(group, sheet):
    return pd.read_csv(os.path.join(INTERIM, f"{group}__{sheet}.csv"))


# --- Bloomberg mapping & missingness ---------------------------------------
fin_log = pd.concat([rd("treatment", "Financial_Import_Log").assign(group="treatment"),
                     rd("control", "Financial_Import_Log").assign(group="control")],
                    ignore_index=True)
fin_raw = pd.concat([rd("treatment", "Financial_Long_Raw").assign(group="treatment"),
                     rd("control", "Financial_Long_Raw").assign(group="control")],
                    ignore_index=True)
with pd.ExcelWriter(os.path.join(AUDIT, "bloomberg_file_mapping.xlsx")) as xw:
    fin_log.to_excel(xw, sheet_name="import_log", index=False)

# missingness by variable within the reshaped panel event window
fin = pd.read_csv(os.path.join(PROC, "financial_did_panel.csv"))
miss = (fin.groupby("Deal_ID")[["Revenue_m", "Operating_Income_m", "Net_Income_m",
                                "Total_Assets_m", "Total_Debt_m", "R_and_D_Expense_m",
                                "ROA_pct", "Operating_Margin_pct", "Leverage_pct"]]
        .apply(lambda d: d.notna().sum()))
with pd.ExcelWriter(os.path.join(AUDIT, "bloomberg_missingness.xlsx")) as xw:
    miss.to_excel(xw, sheet_name="nonmissing_by_deal")

# --- Lens mapping / owner dictionary / dedup --------------------------------
pat_log = pd.concat([rd("treatment", "Patent_Import_Log").assign(group="treatment"),
                     rd("control", "Patent_Import_Log").assign(group="control")],
                    ignore_index=True)
fam = pd.concat([rd("treatment", "Patent_Family_Long").assign(group="treatment"),
                 rd("control", "Patent_Family_Long").assign(group="control")],
                ignore_index=True)
with pd.ExcelWriter(os.path.join(AUDIT, "lens_file_mapping.xlsx")) as xw:
    pat_log.to_excel(xw, sheet_name="import_log", index=False)

owner = (fam.groupby(["group", "Company_or_Group", "Source_File"])
         .agg(rows=("Source_Row", "size"),
              included=("Included_in_Aggregation", lambda s: (s == "Yes").sum()))
         .reset_index())
with pd.ExcelWriter(os.path.join(AUDIT, "patent_owner_dictionary.xlsx")) as xw:
    owner.to_excel(xw, sheet_name="owner_alias_map", index=False)

dedup = (pat_log[["group", "Source_File", "Company_or_Group", "Deal_ID", "Raw_Rows",
                  "Unique_Families", "Observed_Min_Priority_Year",
                  "Observed_Max_Priority_Year", "Import_Status", "Coverage_Status"]]
         if set(["Import_Status"]).issubset(pat_log.columns) else pat_log)
with pd.ExcelWriter(os.path.join(AUDIT, "patent_deduplication_report.xlsx")) as xw:
    pat_log.to_excel(xw, sheet_name="dedup_report", index=False)

# --- Data availability matrix by deal ---------------------------------------
cls = pd.read_csv(os.path.join(INTERIM, "master_transactions_classified.csv"))
pat = pd.read_csv(os.path.join(PROC, "patent_did_panel.csv"))


def cov_flags(panel, outcome):
    pre = panel[panel.Relative_Year.isin([-3, -2, -1])].groupby("Deal_ID")[outcome].apply(lambda s: s.notna().sum())
    post = panel[panel.Relative_Year.isin([1, 2, 3])].groupby("Deal_ID")[outcome].apply(lambda s: s.notna().sum())
    return pre, post


fpre, fpost = cov_flags(fin, "ROA_pct")
ppre, ppost = cov_flags(pat, "Patent_Family_Count")
avail = cls[["Deal_ID", "Provisional_Classification", "Acquirer_Normalized",
             "Completion_Year", "dup_drop", "eligible_strict"]].copy()
avail["fin_pre"] = avail.Deal_ID.map(fpre).fillna(0).astype(int)
avail["fin_post"] = avail.Deal_ID.map(fpost).fillna(0).astype(int)
avail["pat_pre"] = avail.Deal_ID.map(ppre).fillna(0).astype(int)
avail["pat_post"] = avail.Deal_ID.map(ppost).fillna(0).astype(int)
avail["in_H2_preferred"] = (avail.fin_pre >= 2) & (avail.fin_post >= 2) & ~avail.dup_drop
avail["in_H1_preferred"] = (avail.pat_pre >= 2) & (avail.pat_post >= 2) & ~avail.dup_drop
avail.to_csv(os.path.join(AUDIT, "data_availability_matrix.csv"), index=False)

# --- Sample attrition (separately for H1 and H2) ----------------------------
def attrition(panel, outcome, label):
    kept = cls[~cls.dup_drop]
    steps = [
        ("Deals in candidate universe (both files)", len(cls)),
        ("After removing duplicate / cross-file overlap events", len(kept)),
        ("With any %s outcome observation" % label,
         panel.groupby("Deal_ID")[outcome].apply(lambda s: s.notna().any()).sum()),
        (">=2 pre AND >=2 post observations (preferred coverage)",
         ((panel[panel.Relative_Year.isin([-3, -2, -1])].groupby("Deal_ID")[outcome].apply(lambda s: s.notna().sum()) >= 2) &
          (panel[panel.Relative_Year.isin([1, 2, 3])].groupby("Deal_ID")[outcome].apply(lambda s: s.notna().sum()) >= 2)).sum()),
    ]
    df = pd.DataFrame(steps, columns=["step", "n_deals"])
    # strict innovation vs alternative among preferred
    ok = panel.merge(
        (panel[panel.Relative_Year.isin([-3, -2, -1])].groupby("Deal_ID")[outcome].apply(lambda s: s.notna().sum()) >= 2).rename("p2") &
        (panel[panel.Relative_Year.isin([1, 2, 3])].groupby("Deal_ID")[outcome].apply(lambda s: s.notna().sum()) >= 2).rename("q2"),
        on="Deal_ID") if False else panel
    return df


att_fin = attrition(fin, "ROA_pct", "financial (ROA)")
att_pat = attrition(pat, "Patent_Family_Count", "patent (families)")
with pd.ExcelWriter(os.path.join(AUDIT, "sample_attrition.xlsx")) as xw:
    att_fin.to_excel(xw, sheet_name="H2_financial", index=False)
    att_pat.to_excel(xw, sheet_name="H1_patent", index=False)

print("Coverage audit tables written.")
print("\nH2 (financial) attrition:\n", att_fin.to_string(index=False))
print("\nH1 (patent) attrition:\n", att_pat.to_string(index=False))
print("\nDeals in H2 preferred:", int(avail.in_H2_preferred.sum()),
      "| H1 preferred:", int(avail.in_H1_preferred.sum()))

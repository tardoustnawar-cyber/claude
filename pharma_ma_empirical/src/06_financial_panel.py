"""Phase E/F: entity map + reconstructed financial deal-year panel."""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
AUDIT = ROOT / "outputs" / "audit"

canon = pd.read_csv(PROC / "deal_master_classified.csv")

# ---- load both financial long sheets into a common schema ----
tfin = pd.read_excel(RAW / "Treatment_Group_DiD_Data_Workbook.xlsx", sheet_name="Financial_Long_Raw", header=1)
tfin = tfin.rename(columns={"Mapped_Deal_ID": "deal_ids", "Company_Detected": "company"})
tfin["deal_ids"] = tfin["deal_ids"].astype(str)
tfin["src"] = "treatment"

cfin = pd.read_excel(RAW / "Control_Group_DiD_Data_Workbook.xlsx", sheet_name="Financial_Long_Raw", header=0)
cfin = cfin.rename(columns={"Mapped_Deal_IDs": "deal_ids", "Company": "company"})
cfin["deal_ids"] = cfin["deal_ids"].astype(str)
cfin["src"] = "control"

keep = ["deal_ids","company","src","Currency","Year","Revenue_m","Operating_Income_m",
        "Net_Income_m","Total_Assets_m","Total_Debt_m","R_and_D_Expense_m",
        "ROA_pct","Operating_Margin_pct","Leverage_pct"]
fin = pd.concat([tfin[keep], cfin[keep]], ignore_index=True)

# explode multi-deal mappings
fin = fin[fin["deal_ids"].str.contains("CTL|TRT", na=False)].copy()
fin["deal_ids"] = fin["deal_ids"].str.split(r"[;,]")
fin = fin.explode("deal_ids")
fin["deal_id"] = fin["deal_ids"].str.strip()
fin = fin[fin["deal_id"].str.match(r"^(CTL|TRT)-\d+$", na=False)]

for c in ["Revenue_m","Operating_Income_m","Net_Income_m","Total_Assets_m","Total_Debt_m",
          "R_and_D_Expense_m","ROA_pct","Operating_Margin_pct","Leverage_pct"]:
    fin[c] = pd.to_numeric(fin[c], errors="coerce")   # blanks/dashes -> NaN (not zero)
fin["Year"] = pd.to_numeric(fin["Year"], errors="coerce").astype("Int64")

# ---- map raw deal_ids to canonical events ----
id2evt = {}
for _, r in canon.iterrows():
    for did in str(r["member_deal_ids"]).split(";"):
        id2evt[did] = r["deal_event_id"]
fin["deal_event_id"] = fin["deal_id"].map(id2evt)
fin = fin[fin["deal_event_id"].notna()]

canon_idx = canon.set_index("deal_event_id")
fin["completion_year"] = fin["deal_event_id"].map(canon_idx["completion_year"])
fin["RelativeYear"] = fin["Year"].astype(int) - fin["completion_year"].astype(int)

# Exclude implausible-future (likely Bloomberg estimate/NTM) years: keep <= 2023,
# which still admits t+3 for 2020-completion deals. Realised actuals only.
fin = fin[fin["Year"] <= 2023]

# One row per canonical event x calendar year. When the same event carries data
# in both workbooks (cross-file twin), keep the source series with the most
# non-missing in-window ROA observations, to avoid duplicating an acquirer-year.
chosen = []
for evt, g in fin.groupby("deal_event_id"):
    if g["src"].nunique() == 1:
        chosen.append(g); continue
    inwin = g[g["RelativeYear"].between(-3, 3)]
    score = inwin.groupby("src")["ROA_pct"].apply(lambda s: s.notna().sum())
    best = score.idxmax() if len(score) else g["src"].iloc[0]
    chosen.append(g[g["src"] == best])
fin = pd.concat(chosen, ignore_index=True)
# de-dupe any residual event-year
fin = fin.sort_values(["deal_event_id","Year"]).drop_duplicates(["deal_event_id","Year"], keep="first")

# ---- attach classification for the analytical event universe ----
attrs = ["acquirer","target","Final_Classification","Classification_Confidence",
         "Eligibility","InnovationDeal","is_primary_innovation","is_alternative","member_deal_ids"]
fin = fin.merge(canon[["deal_event_id"]+attrs], on="deal_event_id", how="left")

panel = fin[["deal_event_id","member_deal_ids","acquirer","target","company","src","Currency",
             "Final_Classification","Classification_Confidence","Eligibility","InnovationDeal",
             "is_primary_innovation","is_alternative","completion_year","Year","RelativeYear",
             "Revenue_m","Operating_Income_m","Net_Income_m","Total_Assets_m","Total_Debt_m",
             "R_and_D_Expense_m","ROA_pct","Operating_Margin_pct","Leverage_pct"]].copy()
panel = panel.rename(columns={"Year":"calendar_year"})
panel["log_assets"] = np.log(panel["Total_Assets_m"].where(panel["Total_Assets_m"] > 0))
panel["leverage"] = panel["Leverage_pct"]

panel.to_csv(PROC / "financial_deal_year_panel.csv", index=False)

# ---- attrition audit ----
adj = canon[canon["Final_Classification"].isin(["High-confidence innovation-driven","Alternative-rationale"])]
have_fin = set(panel["deal_event_id"].unique())
rows = []
for _, r in adj.iterrows():
    evt = r["deal_event_id"]
    sub = panel[panel["deal_event_id"] == evt]
    inwin = sub[sub["RelativeYear"].between(-3,3)]
    pre = inwin[inwin["RelativeYear"].between(-3,-1)]["ROA_pct"].notna().sum()
    post = inwin[inwin["RelativeYear"].between(1,3)]["ROA_pct"].notna().sum()
    rows.append({"deal_event_id":evt,"acquirer":r["acquirer"],"target":r["target"],
                 "class":r["Final_Classification"],"eligibility":r["Eligibility"],
                 "in_fin_panel":evt in have_fin,"n_pre_ROA":pre,"n_post_ROA":post,
                 "meets_2pre_2post": pre>=2 and post>=2,
                 "meets_balanced_3_3": pre==3 and post==3})
attr = pd.DataFrame(rows)
attr.to_excel(AUDIT / "financial_attrition.xlsx", index=False)

# missingness by relative year for analytical events
inwin_all = panel[panel["RelativeYear"].between(-3,3) & panel["deal_event_id"].isin(adj["deal_event_id"])]
miss = inwin_all.pivot_table(index="deal_event_id", columns="RelativeYear",
                             values="ROA_pct", aggfunc=lambda s: int(s.notna().any()))
miss.to_excel(AUDIT / "financial_missingness.xlsx")

print("financial panel rows:", len(panel), "| events:", panel["deal_event_id"].nunique())
print("\nAttrition (analytical events, ROA coverage):")
print(attr.to_string())
print("\nEvents meeting >=2 pre & >=2 post ROA:", attr["meets_2pre_2post"].sum())
print("By class among those:", attr[attr.meets_2pre_2post].groupby("class").size().to_dict())

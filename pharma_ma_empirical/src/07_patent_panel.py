"""Phase G: reconstructed patent deal-year panel (unique simple families by priority year)."""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
AUDIT = ROOT / "outputs" / "audit"

canon = pd.read_csv(PROC / "deal_master_classified.csv")
id2evt, evt_cy = {}, {}
for _, r in canon.iterrows():
    for did in str(r["member_deal_ids"]).split(";"):
        id2evt[did] = r["deal_event_id"]
    evt_cy[r["deal_event_id"]] = r["completion_year"]

# ---- primary source: Patent_Year_Summary (deduped family counts by priority year) ----
frames = []
for lbl, fname in [("treatment", "Treatment_Group_DiD_Data_Workbook.xlsx"),
                   ("control", "Control_Group_DiD_Data_Workbook.xlsx")]:
    pys = pd.read_excel(RAW / fname, sheet_name="Patent_Year_Summary", header=1)
    pys["src"] = lbl
    pys["deal_id"] = pys["Deal_ID"].astype(str).str.strip()
    pys = pys[pys["deal_id"].str.match(r"^(CTL|TRT)-\d+$", na=False)]
    frames.append(pys[["src","deal_id","Company_or_Group","Calendar_Year","Patent_Family_Count",
                       "Coverage_Basis"] + ([ "Raw_Forward_Citations"] if "Raw_Forward_Citations" in pys.columns else ["Citation_Weighted_Output"])].rename(
                       columns={pys.columns[-1] if False else "Raw_Forward_Citations":"citations"} if "Raw_Forward_Citations" in pys.columns else {"Citation_Weighted_Output":"citations"}))
pat = pd.concat(frames, ignore_index=True)
pat["deal_event_id"] = pat["deal_id"].map(id2evt)
pat = pat[pat["deal_event_id"].notna()].copy()
pat["completion_year"] = pat["deal_event_id"].map(evt_cy)
pat["Calendar_Year"] = pd.to_numeric(pat["Calendar_Year"], errors="coerce").astype("Int64")
pat["Patent_Family_Count"] = pd.to_numeric(pat["Patent_Family_Count"], errors="coerce")
pat["citations"] = pd.to_numeric(pat["citations"], errors="coerce")
pat["RelativeYear"] = pat["Calendar_Year"].astype(int) - pat["completion_year"].astype(int)

# one row per canonical event x priority year: if cross-file twins both carry patents,
# keep the source with wider in-window family coverage.
chosen = []
for evt, g in pat.groupby("deal_event_id"):
    if g["src"].nunique() == 1:
        chosen.append(g); continue
    inwin = g[g["RelativeYear"].between(-3, 3)]
    score = inwin.groupby("src")["Patent_Family_Count"].apply(lambda s: s.notna().sum())
    best = score.idxmax() if len(score) else g["src"].iloc[0]
    chosen.append(g[g["src"] == best])
pat = pd.concat(chosen, ignore_index=True)
pat = pat.sort_values(["deal_event_id","Calendar_Year"]).drop_duplicates(["deal_event_id","Calendar_Year"])

attrs = ["acquirer","target","Final_Classification","Classification_Confidence",
         "Eligibility","InnovationDeal","is_primary_innovation","is_alternative","member_deal_ids"]
pat = pat.merge(canon[["deal_event_id"]+attrs], on="deal_event_id", how="left")
pat = pat.rename(columns={"Calendar_Year":"priority_year","Patent_Family_Count":"patent_families"})
pat["asinh_families"] = np.arcsinh(pat["patent_families"])
pat.to_csv(PROC / "patent_deal_year_panel.csv", index=False)

# ---- validation: rebuild family counts from Patent_Family_Long for TRT deals ----
tpfl = pd.read_excel(RAW / "Treatment_Group_DiD_Data_Workbook.xlsx", sheet_name="Patent_Family_Long", header=1)
tpfl = tpfl[tpfl["Included_in_Aggregation"].astype(str).str.lower().eq("yes")]
tpfl["deal_id"] = tpfl["Deal_ID"].astype(str).str.strip()
tpfl = tpfl[tpfl["deal_id"].str.match(r"^TRT-\d+$", na=False)]
tpfl["Priority_Year"] = pd.to_numeric(tpfl["Priority_Year"], errors="coerce").astype("Int64")
rebuilt = (tpfl.groupby(["deal_id","Priority_Year"])["Display_Key"].nunique()
           .reset_index(name="rebuilt_families"))
orig = pd.read_excel(RAW / "Treatment_Group_DiD_Data_Workbook.xlsx", sheet_name="Patent_Year_Summary", header=1)
orig["deal_id"] = orig["Deal_ID"].astype(str).str.strip()
orig = orig[orig["deal_id"].str.match(r"^TRT-\d+$", na=False)][["deal_id","Calendar_Year","Patent_Family_Count"]]
orig["Calendar_Year"] = pd.to_numeric(orig["Calendar_Year"], errors="coerce").astype("Int64")
chk = rebuilt.merge(orig, left_on=["deal_id","Priority_Year"], right_on=["deal_id","Calendar_Year"], how="outer")
chk["match"] = chk["rebuilt_families"].fillna(0) == chk["Patent_Family_Count"].fillna(0)
with pd.ExcelWriter(AUDIT / "patent_deduplication.xlsx") as xw:
    chk.to_excel(xw, sheet_name="rebuild_vs_summary_TRT", index=False)

# ---- scope/coverage + attrition ----
adj = canon[canon["Final_Classification"].isin(["High-confidence innovation-driven","Alternative-rationale"])]
have = set(pat["deal_event_id"].unique())
rows = []
for _, r in adj.iterrows():
    evt = r["deal_event_id"]; sub = pat[pat["deal_event_id"] == evt]
    inwin = sub[sub["RelativeYear"].between(-3,3)]
    pre = inwin[inwin["RelativeYear"].between(-3,-1)]["patent_families"].notna().sum()
    post = inwin[inwin["RelativeYear"].between(1,3)]["patent_families"].notna().sum()
    rows.append({"deal_event_id":evt,"acquirer":r["acquirer"],"target":r["target"],
                 "class":r["Final_Classification"],"in_patent_panel":evt in have,
                 "n_pre":pre,"n_post":post,"meets_2pre_2post":pre>=2 and post>=2,
                 "meets_balanced_3_3":pre==3 and post==3})
attr = pd.DataFrame(rows)
attr.to_excel(AUDIT / "patent_attrition.xlsx", index=False)
cov = pat.groupby("deal_event_id").agg(coverage_basis=("Coverage_Basis", lambda s: ";".join(sorted(set(s.astype(str))))),
                                       min_year=("priority_year","min"), max_year=("priority_year","max")).reset_index()
cov.to_excel(AUDIT / "patent_scope_coverage.xlsx", index=False)

print("patent panel rows:", len(pat), "| events:", pat["deal_event_id"].nunique())
print("validation rebuild vs summary (TRT): match rate =",
      round(chk["match"].mean(), 3), f"({chk['match'].sum()}/{len(chk)} cells)")
print("\nPatent attrition (analytical events):")
print(attr.to_string())
print("\nEvents meeting >=2 pre & >=2 post families:", attr["meets_2pre_2post"].sum())
print("By class:", attr[attr.meets_2pre_2post].groupby("class").size().to_dict())

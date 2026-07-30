"""Phase B: consolidated deal master with dedup and cross-file overlap audit."""
import re
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
AUDIT = ROOT / "outputs" / "audit"
INTERIM.mkdir(parents=True, exist_ok=True)

LEGAL_SUFFIXES = r"\b(plc|ltd|limited|inc|corp|corporation|sas|sa|ag|ab|as|a\/s|bv|nv|gmbh|spa|srl|sro|oyj|oy|kk|co|company|holdings?|group|pharmaceuticals?|pharma)\b"

def norm_name(s):
    if pd.isna(s):
        return ""
    s = str(s).lower().strip()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(LEGAL_SUFFIXES, " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

frames = []
for label, fname in [("treatment", "Treatment_Group_DiD_Data_Workbook.xlsx"),
                     ("control", "Control_Group_DiD_Data_Workbook.xlsx")]:
    dm = pd.read_excel(RAW / fname, sheet_name="Deal_Master_Wide", header=1)
    dm["source_workbook"] = label
    frames.append(dm)

master = pd.concat(frames, ignore_index=True)
master["deal_event_id"] = master["Deal_ID"]
master["acq_norm"] = master["Acquirer_Raw"].map(norm_name)
master["tgt_norm"] = master["Target_Raw"].map(norm_name)
master["Completion_Date"] = pd.to_datetime(master["Completion_Date"])
master["econ_key_date"] = master["acq_norm"] + "||" + master["tgt_norm"] + "||" + master["Completion_Date"].dt.strftime("%Y-%m-%d")
master["econ_key_year"] = master["acq_norm"] + "||" + master["tgt_norm"] + "||" + master["Completion_Year"].astype(int).astype(str)

# ---- within-file duplicates
within_dupes = master[master.duplicated(subset=["source_workbook", "econ_key_date"], keep=False)].sort_values(["source_workbook", "econ_key_date"])

# ---- cross-file overlaps (same economic event in both workbooks)
key_counts = master.groupby("econ_key_date")["source_workbook"].nunique()
cross_keys = key_counts[key_counts > 1].index
cross = master[master["econ_key_date"].isin(cross_keys)].sort_values(["econ_key_date", "source_workbook"])

# resolve: one economic event appears once. Rule (documented in ANALYSIS_DECISIONS.md):
# a cross-file event has both an innovation-rationale and an alternative-rationale
# GlobalData extract entry -> mixed rationale signal at the screen stage.
# Keep the TREATMENT-workbook row as the carrying row (richer innovation-signal info)
# and flag it Mixed_Screen for classification; drop the control-workbook twin.
master["cross_file_overlap"] = master["econ_key_date"].isin(cross_keys)
drop_ids = master.loc[(master["cross_file_overlap"]) & (master["source_workbook"] == "control"), "deal_event_id"]
master["dedup_drop"] = master["deal_event_id"].isin(drop_ids)

# same-year (but different-date) potential overlaps for manual review
yr_counts = master.groupby("econ_key_year")["source_workbook"].nunique()
yr_keys = set(yr_counts[yr_counts > 1].index) - set(master.loc[master["cross_file_overlap"], "econ_key_year"])
near = master[master["econ_key_year"].isin(yr_keys)].sort_values("econ_key_year")

dedup = master[~master["dedup_drop"]].copy()

# ---- repeated acquirers and overlapping ±3y windows (post-dedup)
dedup["acq_deal_count"] = dedup.groupby("acq_norm")["deal_event_id"].transform("count")
rep = dedup[dedup["acq_deal_count"] > 1][["deal_event_id", "source_workbook", "Acquirer_Raw", "acq_norm", "Target_Raw", "Completion_Date", "Completion_Year"]].sort_values(["acq_norm", "Completion_Date"])
rows = []
for acq, grp in dedup[dedup["acq_deal_count"] > 1].groupby("acq_norm"):
    g = grp.sort_values("Completion_Year")
    years = g["Completion_Year"].astype(int).tolist()
    ids = g["deal_event_id"].tolist()
    for i in range(len(years)):
        overlaps = [ids[j] for j in range(len(years)) if j != i and abs(years[j] - years[i]) <= 6]
        rows.append({"deal_event_id": ids[i], "acq_norm": acq, "completion_year": years[i],
                     "n_deals_same_acquirer": len(years),
                     "overlapping_window_deals": "; ".join(overlaps),
                     "window_overlap_flag": bool(overlaps)})
overlap_windows = pd.DataFrame(rows)
dedup = dedup.merge(overlap_windows[["deal_event_id", "overlapping_window_deals", "window_overlap_flag"]], on="deal_event_id", how="left")
dedup["window_overlap_flag"] = dedup["window_overlap_flag"].fillna(False)

# ---- exports
cols_keep = [c for c in dedup.columns]
dedup.to_csv(INTERIM / "deal_master_unclassified.csv", index=False)

with pd.ExcelWriter(AUDIT / "cross_file_overlap.xlsx") as xw:
    cross[["deal_event_id", "source_workbook", "Deal_ID", "Acquirer_Raw", "Target_Raw", "Completion_Date",
           "Completion_Year", "Overlap_Flag", "Initial_Control_Transfer_Status", "Deal_Rationale"]].to_excel(xw, sheet_name="exact_cross_file_events", index=False)
    near[["deal_event_id", "source_workbook", "Acquirer_Raw", "Target_Raw", "Completion_Date", "Completion_Year"]].to_excel(xw, sheet_name="same_year_review", index=False)
    within_dupes[["deal_event_id", "source_workbook", "Acquirer_Raw", "Target_Raw", "Completion_Date"]].to_excel(xw, sheet_name="within_file_duplicates", index=False)

overlap_windows.to_excel(AUDIT / "repeated_acquirer_calendar.xlsx", index=False)

print(f"rows in:  {len(master)}  (treatment {sum(master.source_workbook=='treatment')}, control {sum(master.source_workbook=='control')})")
print(f"exact cross-file overlapping events: {len(cross_keys)} events / {len(cross)} rows")
print(f"within-file duplicate rows: {len(within_dupes)}")
print(f"same-year near-matches for review: {near['econ_key_year'].nunique()}")
print(f"unique economic events after dedup: {len(dedup)}")
print(f"repeated acquirers (post-dedup): {rep['acq_norm'].nunique()} acquirers, {len(rep)} deals")
print(f"deals with overlapping +-3y windows: {int(overlap_windows['window_overlap_flag'].sum()) if len(overlap_windows) else 0}")
print("workbook Overlap_Flag=Yes counts:", master.groupby('source_workbook')['Overlap_Flag'].apply(lambda s:(s=='Yes').sum()).to_dict())

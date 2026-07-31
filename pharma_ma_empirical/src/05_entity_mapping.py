"""Phase E: versioned entity dictionary with acquirer-group keys for clustering/dedup."""
import re
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
AUDIT = ROOT / "outputs" / "audit"
canon = pd.read_csv(PROC / "deal_master_classified.csv")

# manual parent/group resolution for acquirers that recur under variant legal names
# or across operating companies (verified from deal descriptions).
GROUP = {
    "F. Hoffmann-La Roche Ltd": "Roche",
    "Roche Holding AG": "Roche",
    "GSK plc": "GSK",
    "GSK plc.": "GSK",
    "Recordati S.p.A.": "Recordati",
    "Recordati SpA": "Recordati",
    "Vectura Group Ltd": "Vectura",
    "Vectura Group Limited": "Vectura",
    "Zentiva Group AS": "Zentiva",
    # Aduro BioTech later renamed Chinook Therapeutics via reverse merger; BioNovion
    # acquirer of record shown as Chinook — same reporting entity lineage.
    "Chinook Therapeutics Inc": "Aduro/Chinook",
}

def group_key(name):
    if pd.isna(name): return ""
    return GROUP.get(str(name).strip(), str(name).strip())

canon["acquirer_group"] = canon["acquirer"].map(group_key)
ent = canon[["deal_event_id","member_deal_ids","acquirer","target","acquirer_group",
             "completion_year","Final_Classification","Eligibility"]].copy()
ent["ambiguous_flag"] = ent["acquirer"].isin(
    ["Chinook Therapeutics Inc"])  # entity-continuity caveat (Aduro->Chinook)
ent.to_csv(PROC / "entity_dictionary.csv", index=False)
ent.to_excel(AUDIT / "entity_mapping_review.xlsx", index=False)
canon.to_csv(PROC / "deal_master_classified.csv", index=False)  # add acquirer_group
print("entity dictionary rows:", len(ent))
print("acquirer groups with >1 event:",
      ent.groupby("acquirer_group").size().loc[lambda s: s > 1].to_dict())

"""Phase H: event-time analytical samples for H1 (patents) and H2 (ROA).

Primary comparison: High-confidence innovation-driven vs Alternative-rationale.
Treatment indicator = is_primary_innovation.
"""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
AUDIT = ROOT / "outputs" / "audit"

canon = pd.read_csv(PROC / "deal_master_classified.csv")
grp = canon.set_index("deal_event_id")["acquirer_group"].to_dict()
compl = canon.set_index("deal_event_id")["completion_year"].to_dict()

fin = pd.read_csv(PROC / "financial_deal_year_panel.csv")
pat = pd.read_csv(PROC / "patent_deal_year_panel.csv")

PRIMARY = ["High-confidence innovation-driven", "Alternative-rationale"]

def build(df, outcome, min_pre=2, min_post=2, balanced=False):
    df = df[df["Final_Classification"].isin(PRIMARY)].copy()
    df = df[df["RelativeYear"].between(-3, 3)].copy()
    df["acquirer_group"] = df["deal_event_id"].map(grp)
    df["Post"] = (df["RelativeYear"] >= 1).astype(int)
    df["treat"] = (df["Final_Classification"] == "High-confidence innovation-driven").astype(int)
    df["TreatPost"] = df["treat"] * df["Post"]
    # coverage screen on the outcome (omit t0 from pre/post counts)
    keep = []
    for evt, g in df.groupby("deal_event_id"):
        pre = g[(g["RelativeYear"].between(-3, -1)) & g[outcome].notna()]
        post = g[(g["RelativeYear"].between(1, 3)) & g[outcome].notna()]
        ok = (len(pre) >= min_pre and len(post) >= min_post)
        if balanced:
            ok = (len(pre) == 3 and len(post) == 3)
        if ok:
            keep.append(evt)
    df = df[df["deal_event_id"].isin(keep)]
    # drop t0 and outcome-missing rows for estimation
    est = df[(df["RelativeYear"] != 0) & df[outcome].notna()].copy()
    return est

def dedupe_acquirer(est, outcome):
    """Primary: one non-overlapping event per acquirer group (earliest completion)."""
    est = est.copy()
    firsts = {}
    order = (est[["deal_event_id","acquirer_group"]].drop_duplicates()
             .assign(cy=lambda d: d["deal_event_id"].map(compl))
             .sort_values(["acquirer_group","cy","deal_event_id"]))
    keep_ids = order.groupby("acquirer_group").head(1)["deal_event_id"].tolist()
    return est[est["deal_event_id"].isin(keep_ids)]

def summarize(est, name):
    ev = est["deal_event_id"].nunique()
    ac = est["acquirer_group"].nunique()
    tr = est[est.treat==1]["deal_event_id"].nunique()
    co = est[est.treat==0]["deal_event_id"].nunique()
    return {"sample":name,"events":ev,"acquirer_clusters":ac,"innovation_events":tr,
            "alternative_events":co,"obs":len(est)}

samples = {}
flow = []
# H2 ROA
h2_unb = build(fin, "ROA_pct", 2, 2, False)
h2_prim = dedupe_acquirer(h2_unb, "ROA_pct")
h2_bal = build(fin, "ROA_pct", 3, 3, True)
h2_bal_prim = dedupe_acquirer(h2_bal, "ROA_pct")
# H1 patents
h1_unb = build(pat, "patent_families", 2, 2, False)
h1_prim = dedupe_acquirer(h1_unb, "patent_families")
h1_bal = build(pat, "patent_families", 3, 3, True)
h1_bal_prim = dedupe_acquirer(h1_bal, "patent_families")

for est,name in [(h2_prim,"H2_ROA_primary_uniqueAcq"),(h2_unb,"H2_ROA_serial_all"),
                 (h2_bal_prim,"H2_ROA_balanced_uniqueAcq"),
                 (h1_prim,"H1_patents_primary_uniqueAcq"),(h1_unb,"H1_patents_serial_all"),
                 (h1_bal_prim,"H1_patents_balanced_uniqueAcq")]:
    samples[name]=est; flow.append(summarize(est,name))

# save primary analytical panels
h2_prim.to_csv(PROC / "h2_financial_did_panel.csv", index=False)
h1_prim.to_csv(PROC / "h1_patent_did_panel.csv", index=False)
h2_unb.to_csv(PROC / "h2_financial_did_serial.csv", index=False)
h1_unb.to_csv(PROC / "h1_patent_did_serial.csv", index=False)
h2_bal_prim.to_csv(PROC / "h2_financial_did_balanced.csv", index=False)
h1_bal_prim.to_csv(PROC / "h1_patent_did_balanced.csv", index=False)

flow_df = pd.DataFrame(flow)
with pd.ExcelWriter(AUDIT / "sample_selection_flow.xlsx") as xw:
    flow_df.to_excel(xw, sheet_name="samples", index=False)
    # event-time support
    for name,est in samples.items():
        sup = (est.groupby(["treat","RelativeYear"])["deal_event_id"].nunique()
               .reset_index(name="n_events"))
        sup.to_excel(xw, sheet_name=("supp_"+name)[:31], index=False)

# event-time support table
et_rows=[]
for name,est in samples.items():
    for (tr,ry),g in est.groupby(["treat","RelativeYear"]):
        et_rows.append({"sample":name,"group":"innovation" if tr else "alternative",
                        "relative_year":ry,"n_events":g["deal_event_id"].nunique()})
pd.DataFrame(et_rows).to_excel(AUDIT / "event_time_support.xlsx", index=False)

print(flow_df.to_string())
print("\nPrimary H2 events:")
print(h2_prim[["deal_event_id","acquirer","target","Final_Classification"]].drop_duplicates().to_string())
print("\nPrimary H1 events:")
print(h1_prim[["deal_event_id","acquirer","target","Final_Classification"]].drop_duplicates().to_string())

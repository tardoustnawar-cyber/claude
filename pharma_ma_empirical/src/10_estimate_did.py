"""Phases J-L (Python; R unavailable): baseline DiD, event study, robustness for H1 & H2."""
import sys, json
import numpy as np
import pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from est_utils import twfe_did, wild_cluster_bootstrap, ppml_did, event_study

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
TAB = ROOT / "outputs" / "tables"
MOD = ROOT / "outputs" / "models"
MOD.mkdir(parents=True, exist_ok=True)

def load(n): return pd.read_csv(PROC / n)
h2p = load("h2_financial_did_panel.csv"); h1p = load("h1_patent_did_panel.csv")
h2s = load("h2_financial_did_serial.csv"); h1s = load("h1_patent_did_serial.csv")
h2b = load("h2_financial_did_balanced.csv"); h1b = load("h1_patent_did_balanced.csv")

def pre_mean(df, outcome, treat):
    col = outcome if outcome in df.columns else outcome.split("(")[0]
    if col not in df.columns:
        return np.nan
    return df[(df.treat==treat)&(df.RelativeYear.between(-3,-1))][col].mean()

results = []
def record(tag, hyp, outcome, df, res, wild=None, extra_note=""):
    delta = res["delta"]; beta = res["beta"]
    results.append({
        "model_tag":tag,"hypothesis":hyp,"outcome":outcome,
        "delta_alt(Post)":round(delta,3),"beta(TreatxPost)":round(beta,3),
        "delta+beta(innov)":round(delta+beta,3),
        "se":round(res["se"],3),"ci_lo":round(res["ci"][0],3),"ci_hi":round(res["ci"][1],3),
        "p":round(res["p"],4),"wild_p":round(wild["wild_p"],4) if wild else None,
        "obs":res["n"],"events":res.get("n_events"),"clusters":res["n_clusters"],
        "pre_mean_innov":round(pre_mean(df,outcome,1),3),
        "pre_mean_alt":round(pre_mean(df,outcome,0),3),"note":extra_note})

# ================= H2: ROA (linear FE primary) =================
r = twfe_did(h2p, "ROA_pct"); w = wild_cluster_bootstrap(h2p, "ROA_pct")
record("H2_primary_linearFE_ROA","H2","ROA_pct",h2p,r,w,"Primary: unique-acquirer, >=2pre/>=2post, omit t0")
# secondary operating margin — restrict to revenue-bearing obs (>=EUR50m) and winsorise,
# because op margin = op income / revenue explodes mechanically for near-zero-revenue biotechs.
h2m = h2p.copy()
lo_m, hi_m = h2m["Operating_Margin_pct"].quantile([.01,.99])
h2m["OpMargin_w"] = h2m["Operating_Margin_pct"].clip(lo_m, hi_m)
h2m_rev = h2m[h2m["Revenue_m"] >= 50].copy()
if h2m_rev["OpMargin_w"].notna().sum() > 10 and h2m_rev["treat"].nunique()==2:
    rm = twfe_did(h2m_rev, "OpMargin_w"); wm = wild_cluster_bootstrap(h2m_rev,"OpMargin_w")
    record("H2_secondary_OpMargin","H2","OpMargin_w(rev>=50)",h2m_rev,rm,wm,
           "Secondary: winsorised op margin, revenue>=EUR50m (excludes mechanically extreme low-revenue obs)")
# robustness
r2 = twfe_did(h2s, "ROA_pct"); w2 = wild_cluster_bootstrap(h2s,"ROA_pct")
record("H2_serial_all_ROA","H2","ROA_pct",h2s,r2,w2,"Serial acquirers included (cluster by acquirer)")
r3 = twfe_did(h2b, "ROA_pct"); w3 = wild_cluster_bootstrap(h2b,"ROA_pct")
record("H2_balanced_3x3_ROA","H2","ROA_pct",h2b,r3,w3,"Balanced 3pre/3post")
# winsorised ROA (1/99 pooled, threshold pre-declared)
h2pw = h2p.copy()
lo,hi = h2pw["ROA_pct"].quantile([.01,.99])
h2pw["ROA_w"] = h2pw["ROA_pct"].clip(lo,hi)
rw = twfe_did(h2pw,"ROA_w"); ww = wild_cluster_bootstrap(h2pw,"ROA_w")
record("H2_winsorised_ROA","H2","ROA_w(1/99)",h2pw,rw,ww,"Winsorised 1/99 (threshold pre-declared)")
# include t0 as post
h2t0 = pd.read_csv(PROC/"h2_financial_did_panel.csv")  # already omits t0; rebuild with t0 from full panel
fullfin = pd.read_csv(PROC/"financial_deal_year_panel.csv")
keep_ids = set(h2p["deal_event_id"])
h2_t0 = fullfin[fullfin.deal_event_id.isin(keep_ids) & fullfin.RelativeYear.between(-3,3) & fullfin.ROA_pct.notna()].copy()
h2_t0["Post"]=(h2_t0.RelativeYear>=0).astype(int)
h2_t0["treat"]=(h2_t0.Final_Classification=="High-confidence innovation-driven").astype(int)
h2_t0["TreatPost"]=h2_t0.treat*h2_t0.Post
h2_t0["acquirer_group"]=h2_t0.deal_event_id.map(pd.read_csv(PROC/"deal_master_classified.csv").set_index("deal_event_id")["acquirer_group"])
rt0=twfe_did(h2_t0,"ROA_pct"); record("H2_include_t0_ROA","H2","ROA_pct",h2_t0,rt0,None,"t0 coded as post")

# ================= H1: patents =================
r = twfe_did(h1p, "patent_families"); w = wild_cluster_bootstrap(h1p,"patent_families")
record("H1_primary_linearFE_fam","H1","patent_families",h1p,r,w,"Primary: linear FE family count")
rihs = twfe_did(h1p, "asinh_families"); wihs = wild_cluster_bootstrap(h1p,"asinh_families")
record("H1_IHS_fam","H1","asinh(families)",h1p,rihs,wihs,"IHS transform robustness")
# PPML
try:
    rp = ppml_did(h1p, "patent_families")
    results.append({"model_tag":"H1_PPML_fam","hypothesis":"H1","outcome":"patent_families(PPML)",
        "delta_alt(Post)":round(rp["model"].params.get("Post",np.nan),3),
        "beta(TreatxPost)":round(rp["beta"],3),"delta+beta(innov)":None,
        "se":round(rp["se"],3),"ci_lo":round(rp["ci"][0],3),"ci_hi":round(rp["ci"][1],3),
        "p":round(rp["p"],4),"wild_p":None,"obs":rp["n"],"events":h1p.deal_event_id.nunique(),
        "clusters":rp["n_clusters"],"pre_mean_innov":round(pre_mean(h1p,"patent_families",1),3),
        "pre_mean_alt":round(pre_mean(h1p,"patent_families",0),3),
        "note":"Poisson PPML; beta is log-count differential"})
except Exception as e:
    print("PPML failed:", e)
r2 = twfe_did(h1s,"patent_families"); w2 = wild_cluster_bootstrap(h1s,"patent_families")
record("H1_serial_all_fam","H1","patent_families",h1s,r2,w2,"Serial acquirers included")
r3 = twfe_did(h1b,"patent_families"); w3 = wild_cluster_bootstrap(h1b,"patent_families")
record("H1_balanced_3x3_fam","H1","patent_families",h1b,r3,w3,"Balanced 3pre/3post")

res_df = pd.DataFrame(results)
res_df.to_csv(TAB / "T7_T8_T10_did_estimates.csv", index=False)
res_df.to_excel(TAB / "T7_T8_T10_did_estimates.xlsx", index=False)

# ================= Event studies =================
es_out = {}
for df,outcome,lab in [(h2p,"ROA_pct","H2_ROA"),(h1p,"patent_families","H1_patents")]:
    es = event_study(df, outcome)
    es["coefs"].to_csv(MOD / f"eventstudy_{lab}.csv", index=False)
    pt = es["pretrend_test"]
    fp = float(pt.pvalue) if pt is not None else np.nan
    es_out[lab] = {"pretrend_joint_p": round(fp,4) if fp==fp else None,
                   "pre_terms": es["pre_terms"]}
    print(f"\n=== Event study {lab} ===")
    print(es["coefs"].round(3).to_string())
    print(f"Joint pre-trend test p = {fp:.4f}" if fp==fp else "pre-trend test unavailable")
json.dump(es_out, open(MOD/"pretrend_tests.json","w"), indent=2)

# ================= leave-one-acquirer-out (influence) =================
loo_rows=[]
for df,outcome,lab in [(h2p,"ROA_pct","H2_ROA"),(h1p,"patent_families","H1_patents")]:
    base = twfe_did(df,outcome)["beta"]
    for ac in sorted(df["acquirer_group"].unique()):
        sub = df[df.acquirer_group!=ac]
        if sub["treat"].nunique()<2: continue
        try:
            b = twfe_did(sub,outcome)["beta"]
            loo_rows.append({"sample":lab,"dropped_acquirer":ac,"beta":round(b,3),
                             "delta_vs_base":round(b-base,3)})
        except Exception:
            pass
loo = pd.DataFrame(loo_rows)
loo.to_csv(TAB / "T11_leave_one_out.csv", index=False)

print("\n================ DiD ESTIMATES ================")
print(res_df[["model_tag","beta(TreatxPost)","se","p","wild_p","obs","clusters"]].to_string())
print("\nLeave-one-acquirer-out range:")
for lab in ["H2_ROA","H1_patents"]:
    s = loo[loo["sample"]==lab]["beta"]
    print(f"  {lab}: beta in [{s.min():.3f}, {s.max():.3f}]")

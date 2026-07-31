"""Phase I: descriptives, pre-treatment balance (SMD), common support."""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
TAB = ROOT / "outputs" / "tables"
TAB.mkdir(parents=True, exist_ok=True)

h2 = pd.read_csv(PROC / "h2_financial_did_panel.csv")
h1 = pd.read_csv(PROC / "h1_patent_did_panel.csv")

def desc(df, outcome, label):
    g = df.groupby("treat")
    rows = []
    for tr, sub in g:
        pre = sub[sub.RelativeYear.between(-3,-1)][outcome]
        post = sub[sub.RelativeYear.between(1,3)][outcome]
        rows.append({"group":"innovation" if tr else "alternative",
                     "events":sub.deal_event_id.nunique(),
                     "acquirers":sub.acquirer_group.nunique(),
                     "obs":len(sub),
                     "pre_mean":round(pre.mean(),3),"pre_sd":round(pre.std(),3),
                     "post_mean":round(post.mean(),3),"post_sd":round(post.std(),3),
                     "raw_prepost_change":round(post.mean()-pre.mean(),3),
                     "min":round(sub[outcome].min(),2),"max":round(sub[outcome].max(),2)})
    d = pd.DataFrame(rows); d.insert(0,"sample",label)
    return d

desc_tab = pd.concat([desc(h2,"ROA_pct","H2 ROA (pp)"), desc(h1,"patent_families","H1 patent families")])

def smd(df, var, pre_only=True):
    d = df[df.RelativeYear.between(-3,-1)] if (pre_only and "RelativeYear" in df) else df
    t = d[d.treat==1][var].dropna(); c = d[d.treat==0][var].dropna()
    if len(t)<2 or len(c)<2: return np.nan, np.nan
    sp = np.sqrt((t.var()+c.var())/2)
    smd_v = (t.mean()-c.mean())/sp if sp>0 else np.nan
    vr = t.var()/c.var() if c.var()>0 else np.nan
    return smd_v, vr

# pre-treatment balance on event-level pre-period means
def event_pre(df, outcome):
    pre = df[df.RelativeYear.between(-3,-1)]
    agg = pre.groupby(["deal_event_id","treat"]).agg(
        pre_outcome=(outcome,"mean"),
        pre_slope=(outcome, lambda s: np.polyfit(range(len(s)),s,1)[0] if len(s)>=2 else np.nan)).reset_index()
    return agg

bal_rows=[]
for df,outcome,lab,extravars in [(h2,"ROA_pct","H2",["log_assets","leverage","Operating_Margin_pct","Revenue_m"]),
                                 (h1,"patent_families","H1",[])]:
    ep = event_pre(df,outcome)
    for v,disp in [("pre_outcome","pre-period outcome mean"),("pre_slope","pre-period outcome slope")]:
        s,vr = smd(ep.rename(columns={v:v}), v)
        bal_rows.append({"sample":lab,"variable":disp,"smd":round(s,3) if s==s else None,
                         "variance_ratio":round(vr,3) if vr==vr else None})
    for v in extravars:
        if v in df:
            s,vr = smd(df, v)
            bal_rows.append({"sample":lab,"variable":f"pre {v}","smd":round(s,3) if s==s else None,
                             "variance_ratio":round(vr,3) if vr==vr else None})
bal = pd.DataFrame(bal_rows)

with pd.ExcelWriter(TAB / "T4_T5_descriptives.xlsx") as xw:
    desc_tab.to_excel(xw, sheet_name="descriptives", index=False)
    bal.to_excel(xw, sheet_name="balance_SMD", index=False)

# common support: event-level pre-outcome ranges
cs_rows=[]
for df,outcome,lab in [(h2,"ROA_pct","H2 ROA"),(h1,"patent_families","H1 patents")]:
    ep = event_pre(df,outcome)
    for tr in [1,0]:
        vals = ep[ep.treat==tr]["pre_outcome"]
        cs_rows.append({"sample":lab,"group":"innovation" if tr else "alternative",
                        "n":len(vals),"min":round(vals.min(),2),"p25":round(vals.quantile(.25),2),
                        "median":round(vals.median(),2),"p75":round(vals.quantile(.75),2),
                        "max":round(vals.max(),2)})
cs = pd.DataFrame(cs_rows)
cs.to_excel(TAB / "T6_common_support.xlsx", index=False)

print(desc_tab.to_string()); print(); print(bal.to_string()); print(); print(cs.to_string())

"""Placebo: fake completion shifted 2y earlier, using pre-period observations only."""
import sys
import pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from est_utils import twfe_did

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"; TAB = ROOT / "outputs" / "tables"

rows = []
for fn, outcome, lab in [("h2_financial_did_panel.csv","ROA_pct","H2_ROA"),
                         ("h1_patent_did_panel.csv","patent_families","H1_patents")]:
    df = pd.read_csv(PROC / fn)
    # restrict to genuine pre-period (rel in -3..-1); assign fake completion at rel=-2
    pl = df[df.RelativeYear.between(-3,-1)].copy()
    pl["Post"] = (pl["RelativeYear"] >= -2).astype(int)   # fake post = {-2,-1}
    pl["TreatPost"] = pl["treat"] * pl["Post"]
    if pl["treat"].nunique()==2 and pl.groupby("deal_event_id")["RelativeYear"].nunique().min()>=2:
        try:
            r = twfe_did(pl, outcome)
            rows.append({"sample":lab,"placebo_beta":round(r["beta"],3),"se":round(r["se"],3),
                         "p":round(r["p"],4),"obs":r["n"],"note":"fake completion at t-2; pre-period only; beta should be ~0"})
        except Exception as e:
            rows.append({"sample":lab,"placebo_beta":None,"note":f"not estimable: {e}"})
pd.DataFrame(rows).to_csv(TAB / "T10b_placebo.csv", index=False)
print(pd.DataFrame(rows).to_string())

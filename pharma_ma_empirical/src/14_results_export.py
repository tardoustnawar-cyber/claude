"""Consolidated tables, hypothesis decision matrix, flowchart, final console summary."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT/"data"/"processed"; TAB = ROOT/"outputs"/"tables"; AUD = ROOT/"outputs"/"audit"
FIG = ROOT/"outputs"/"figures"; THE = ROOT/"outputs"/"thesis"; THE.mkdir(parents=True, exist_ok=True)

canon = pd.read_csv(PROC/"deal_master_classified.csv")
res = pd.read_csv(TAB/"T7_T8_T10_did_estimates.csv")
pt = json.load(open(ROOT/"outputs"/"models"/"pretrend_tests.json"))
flow = pd.read_excel(AUD/"sample_selection_flow.xlsx", sheet_name="samples")

# ---- T1 data & file audit summary ----
struct = pd.read_excel(AUD/"workbook_structure.xlsx")
struct.to_excel(TAB/"T1_data_file_audit.xlsx", index=False)

# ---- T2 sample selection / attrition ----
n_trt = int((canon.source_workbooks.str.contains("treatment")).sum())
steps = pd.DataFrame([
 {"step":"Raw deal rows (treatment 45 + control 306)","n":351},
 {"step":"Unique economic events after dedup (cross- & within-file)","n":int(len(canon))},
 {"step":"Data-carrying events adjudicated on evidence","n":int((canon.Final_Classification.isin(['High-confidence innovation-driven','Alternative-rationale','Mixed / borderline','Ineligible transaction'])).sum())},
 {"step":"High-confidence innovation-driven (evidence)","n":int((canon.Final_Classification=='High-confidence innovation-driven').sum())},
 {"step":"Alternative-rationale (evidence)","n":int((canon.Final_Classification=='Alternative-rationale').sum())},
 {"step":"H2 ROA primary analytical events","n":int(flow.loc[flow['sample']=='H2_ROA_primary_uniqueAcq','events'].iloc[0])},
 {"step":"H1 patent primary analytical events","n":int(flow.loc[flow['sample']=='H1_patents_primary_uniqueAcq','events'].iloc[0])},
])
steps.to_excel(TAB/"T2_sample_selection_flow.xlsx", index=False)

# ---- T3 classification counts ----
t3 = canon.Final_Classification.value_counts().reset_index()
t3.columns=["Final_Classification","n_events"]
t3.to_excel(TAB/"T3_classification_counts.xlsx", index=False)

# ---- T12 / hypothesis decision matrix ----
def row(tag):
    r = res[res.model_tag==tag].iloc[0]; return r
h2 = row("H2_primary_linearFE_ROA"); h1 = row("H1_primary_linearFE_fam")
hyp = pd.DataFrame([
 {"Hypothesis":"H1 (differential patent output)","Direction expected":"Innovation < Alternative (less favourable)",
  "beta (Innovation x Post)":h1["beta(TreatxPost)"],"95% CI":f"[{h1.ci_lo}, {h1.ci_hi}]",
  "cluster-robust p":h1["p"],"wild-bootstrap p":h1["wild_p"],
  "pre-trend joint p":pt["H1_patents"]["pretrend_joint_p"],
  "events":int(h1["events"]),"acquirer clusters":int(h1["clusters"]),
  "Status":"Not supported at conventional levels (point estimate ~0; imprecise)"},
 {"Hypothesis":"H2 (differential ROA)","Direction expected":"Innovation > Alternative (more favourable)",
  "beta (Innovation x Post)":h2["beta(TreatxPost)"],"95% CI":f"[{h2.ci_lo}, {h2.ci_hi}]",
  "cluster-robust p":h2["p"],"wild-bootstrap p":h2["wild_p"],
  "pre-trend joint p":pt["H2_ROA"]["pretrend_joint_p"],
  "events":int(h2["events"]),"acquirer clusters":int(h2["clusters"]),
  "Status":"Directionally consistent (positive) but not statistically significant; wide CI"},
])
hyp.to_excel(THE/"HYPOTHESIS_DECISION_TABLE.xlsx", index=False)
hyp.to_excel(TAB/"T12_hypothesis_matrix.xlsx", index=False)

# ---- Fig 1: sample-selection flowchart ----
fig, ax = plt.subplots(figsize=(8,9)); ax.axis("off")
boxes = [
 (0.5,0.95,"Raw GlobalData deal rows\nTreatment 45 + Control 306 = 351"),
 (0.5,0.82,f"Deduplicate economic events\n(42 cross-file + 3 within-file collapsed)\n-> {len(canon)} unique events"),
 (0.5,0.68,"Evidence-based classification of data-carrying deals\n(screen false +/- reassigned)"),
 (0.5,0.54,f"High-confidence innovation: {int((canon.Final_Classification=='High-confidence innovation-driven').sum())}   |   "
           f"Alternative: {int((canon.Final_Classification=='Alternative-rationale').sum())}\n"
           f"Mixed/borderline & ineligible excluded"),
 (0.28,0.36,f"H2 ROA sample\n>=2 pre / >=2 post, unique acquirer\n"
            f"{int(flow.loc[flow['sample']=='H2_ROA_primary_uniqueAcq','events'].iloc[0])} events, "
            f"{int(flow.loc[flow['sample']=='H2_ROA_primary_uniqueAcq','acquirer_clusters'].iloc[0])} clusters"),
 (0.72,0.36,f"H1 patent sample\n>=2 pre / >=2 post, unique acquirer\n"
            f"{int(flow.loc[flow['sample']=='H1_patents_primary_uniqueAcq','events'].iloc[0])} events, "
            f"{int(flow.loc[flow['sample']=='H1_patents_primary_uniqueAcq','acquirer_clusters'].iloc[0])} clusters"),
 (0.28,0.16,"Two-way FE DiD + event study\nCluster SE + wild bootstrap"),
 (0.72,0.16,"Two-way FE DiD + PPML/IHS\nCluster SE + wild bootstrap"),
]
for x,y,t in boxes:
    ax.add_patch(plt.Rectangle((x-0.21,y-0.045),0.42,0.09,fc="#E8EEF6",ec="#2166AC"))
    ax.text(x,y,t,ha="center",va="center",fontsize=8)
for a,b in [(0,1),(1,2),(2,3)]:
    ax.annotate("",xy=(0.5,boxes[b][1]+0.045),xytext=(0.5,boxes[a][1]-0.045),arrowprops=dict(arrowstyle="->"))
ax.annotate("",xy=(0.28,0.405),xytext=(0.45,0.495),arrowprops=dict(arrowstyle="->"))
ax.annotate("",xy=(0.72,0.405),xytext=(0.55,0.495),arrowprops=dict(arrowstyle="->"))
ax.annotate("",xy=(0.28,0.205),xytext=(0.28,0.315),arrowprops=dict(arrowstyle="->"))
ax.annotate("",xy=(0.72,0.205),xytext=(0.72,0.315),arrowprops=dict(arrowstyle="->"))
ax.set_title("Fig 1. Sample-selection flowchart")
fig.savefig(FIG/"fig1_sample_flowchart.png",bbox_inches="tight",dpi=150); plt.close(fig)

print("Consolidated tables + flowchart written.")
print(hyp.to_string())

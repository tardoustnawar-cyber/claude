"""
06_flow_and_diagnostics.py -- sample-selection flow, coverage figures and the
formal identification-diagnostics table.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(ROOT, "data/processed")
TAB = os.path.join(ROOT, "outputs/tables")
FIG = os.path.join(ROOT, "outputs/figures")
AUDIT = os.path.join(ROOT, "outputs/audit")
plt.rcParams.update({"figure.dpi": 130, "font.size": 10})

cls = pd.read_csv(os.path.join(PROC, "master_transactions_classified.csv"))
fin = pd.read_csv(os.path.join(PROC, "financial_did_panel.csv"))
pat = pd.read_csv(os.path.join(PROC, "patent_did_panel.csv"))

# ---------- sample selection flow -------------------------------------------
def pref(df, outcome):
    pre = df[df.Relative_Year.isin([-3, -2, -1])].groupby("Deal_ID")[outcome].apply(lambda s: s.notna().sum())
    post = df[df.Relative_Year.isin([1, 2, 3])].groupby("Deal_ID")[outcome].apply(lambda s: s.notna().sum())
    return set(pre.index[(pre >= 2) & (post.reindex(pre.index).fillna(0) >= 2)])

fin_ok, pat_ok = pref(fin, "ROA_pct"), pref(pat, "Patent_Family_Count")
strict_ids = set(cls[cls.Provisional_Classification.isin(["Innovation-driven", "Alternative rationale"]) & ~cls.dup_drop].Deal_ID)

flow = pd.DataFrame([
    ("Raw rows: innovation-driven export (candidate treatment)", 45),
    ("Raw rows: alternative-rationale export (candidate control)", 306),
    ("Total candidate rows", 351),
    ("Cross-file overlapping events (same deal in both exports)", 39),
    ("Rows dropped as duplicates (3 cross-file with data, 3 exact dupes)", int(cls.dup_drop.sum())),
    # each cross-file overlap key = ONE economic event even where the
    # counterpart row carries no data (38 keys still have one row per file
    # among kept rows; counting unique keys collapses them)
    ("Unique economic events after consolidation",
     int(cls[~cls.dup_drop].Cross_File_Key.nunique())),
    ("Deals with any Bloomberg ROA in event window", int(fin.groupby('Deal_ID').ROA_pct.apply(lambda s: s.notna().any()).sum())),
    ("Deals with any Lens patent-family count in event window", int(pat.groupby('Deal_ID').Patent_Family_Count.apply(lambda s: s.notna().any()).sum())),
    ("H2 preferred coverage (>=2 pre & >=2 post ROA)", len(fin_ok)),
    ("H1 preferred coverage (>=2 pre & >=2 post patents)", len(pat_ok)),
    ("H2 strict estimation sample (excl. borderline/mixed)", len(fin_ok & strict_ids)),
    ("H1 strict estimation sample (excl. borderline/mixed)", len(pat_ok & strict_ids)),
], columns=["step", "n"])
flow.to_csv(os.path.join(TAB, "sample_selection_flow.csv"), index=False)
flow.to_excel(os.path.join(TAB, "sample_selection_flow.xlsx"), index=False)

fig, ax = plt.subplots(figsize=(8, 4.6))
ax.barh(range(len(flow)), flow.n, color="#1b6ca8")
ax.set_yticks(range(len(flow)))
ax.set_yticklabels(flow.step, fontsize=8)
ax.invert_yaxis()
ax.set_xscale("log")
ax.set_xlabel("Number of deals (log scale)")
ax.set_title("Sample selection flow", fontsize=11)
for i, v in enumerate(flow.n):
    ax.text(v * 1.05, i, str(v), va="center", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "sample_flow.png"))
plt.close(fig)

# ---------- coverage figures -------------------------------------------------
def coverage_fig(panel, outcome, title, fname):
    deals = sorted(panel[panel[outcome].notna()].Deal_ID.unique())
    fig, ax = plt.subplots(figsize=(7, max(3, 0.28 * len(deals) + 1)))
    for i, d_id in enumerate(deals):
        sub = panel[(panel.Deal_ID == d_id) & panel[outcome].notna()]
        grp = sub.Innovation_Deal.iloc[0] if sub.Innovation_Deal.notna().any() else np.nan
        col = "#1b6ca8" if grp == 1 else ("#c1442e" if grp == 0 else "#999999")
        ax.scatter(sub.Relative_Year, [i] * len(sub), s=18, color=col)
    ax.set_yticks(range(len(deals)))
    ax.set_yticklabels(deals, fontsize=7)
    ax.set_xlabel("Relative year")
    ax.set_title(title + "\n(blue=innovation, red=alternative, grey=borderline/mixed)", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, fname))
    plt.close(fig)

coverage_fig(fin, "ROA_pct", "Financial (ROA) observation coverage by deal", "financial_coverage.png")
coverage_fig(pat, "Patent_Family_Count", "Patent-family observation coverage by deal", "patent_coverage.png")

# ---------- identification diagnostics table --------------------------------
es = pd.read_csv(os.path.join(TAB, "event_study_results.csv"))
jp = es.groupby("panel").joint_pretrend_p.first()
diag = pd.DataFrame([
    ["Parallel trends (H2/ROA)",
     f"Joint test of differential pre-coefficients p={jp.get('H2_ROA', np.nan):.3f}; "
     "t-3 differential large (-33pp) but imprecise.",
     "Not rejected statistically, but sample too small for the test to be informative; "
     "visual pre-trends diverge. WEAK support."],
    ["Parallel trends (H1/patents)",
     f"Joint test p={jp.get('H1_Patents', np.nan):.2e}; t-3 differential -19.4 families, "
     "driven by Sanofi's pre-deal patent ramp-up.",
     "REJECTED. Causal interpretation of H1 not credible; report as conditional association only."],
    ["No anticipation",
     "Announcement-to-completion gaps typically <1 year (e.g. Servier/Symphogen ~2 months); "
     "t0 excluded from pre/post split; t0-as-post robustness similar.",
     "Partially supported; residual anticipation in t-1 cannot be excluded."],
    ["Stable, pre-outcome classification",
     "No manual classification existed in the workbooks (all 'Not reviewed'). Provisional "
     "classification built ONLY from the GlobalData screen + announcement-time text; frozen "
     "with SHA-256 before estimation.",
     "Protocol respected mechanically, but classification is UNVALIDATED -> the estimand is "
     "'deals classified innovation-driven under this observable protocol'."],
    ["No comparison-group contamination",
     "13 of 26 data-carrying deals are text-flagged borderline/mixed and excluded from strict "
     "sample; several remaining 'alternative' deals (Roche/Tusk, GSK/GlycoVaxyn, Ipsen/Syntaxin) "
     "involve biotech targets with pipelines.",
     "MATERIAL RISK of false negatives contaminating the comparison group; attenuates contrast."],
    ["No overlapping treatment",
     "61 acquirers have >1 deal in the candidate universe; GSK, Roche, Vectura, Zentiva, Esteve "
     "appear repeatedly inside event windows (e.g. GSK 2013 & 2015 windows overlap).",
     "VIOLATED for several sample firms; deal-FE absorbs levels but overlapping events blur timing."],
    ["Limited interference",
     "Large-pharma competitors in the same research races appear in both groups.",
     "Untestable with these data; discussed qualitatively."],
    ["Stable sample composition",
     "Shire acquired by Takeda 2019 (delisted); Aduro->Chinook reverse merger; Vectura/Skyepharma "
     "combined mid-window; partial windows for several deals.",
     "PARTIALLY VIOLATED; balanced-window robustness limited by n."],
    ["Group size / firm heterogeneity",
     "Strict H2: 5 innovation vs 6 alternative deals; innovation acquirers are far larger "
     "(pre-deal total assets SMD=1.08; revenue SMD=1.22; patent stock SMD=1.32).",
     "SEVERE imbalance; matching infeasible without discarding most of the sample."],
], columns=["Assumption", "Evidence", "Assessment"])
diag.to_excel(os.path.join(AUDIT, "identification_diagnostics.xlsx"), index=False)
diag.to_csv(os.path.join(AUDIT, "identification_diagnostics.csv"), index=False)

print(flow.to_string(index=False))
print("\nIdentification diagnostics written.")

"""
05_models.py -- Phase: baseline DiD, patent count models, event studies,
prioritised robustness. PROVISIONAL estimates (classification unvalidated,
very small samples). Uses pyfixest (fixest-equivalent) with acquirer-clustered SEs
and a wild-cluster bootstrap where the cluster count is small.

Outputs:
  outputs/tables/main_did_results.csv/.xlsx
  outputs/tables/event_study_results.csv/.xlsx
  outputs/tables/robustness_results.csv/.xlsx
  outputs/tables/hypothesis_results_summary.csv/.xlsx
  outputs/figures/event_study_ROA.png, event_study_patents.png,
                  coefficient_comparison.png
  outputs/models/*.txt
"""
import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pyfixest as pf
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wcb import wild_cluster_boot_p

warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(ROOT, "data/processed")
TAB = os.path.join(ROOT, "outputs/tables")
FIG = os.path.join(ROOT, "outputs/figures")
MOD = os.path.join(ROOT, "outputs/models")
for d in (TAB, FIG, MOD):
    os.makedirs(d, exist_ok=True)
plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.spines.top": False, "axes.spines.right": False})

fin = pd.read_csv(os.path.join(PROC, "financial_did_panel.csv"))
pat = pd.read_csv(os.path.join(PROC, "patent_did_panel.csv"))


def prep(df, outcome, include_borderline=False, include_t0_post=False,
         include_majority=True):
    d = df.copy()
    if not include_borderline:
        d = d[d.Innovation_Deal.notna()]
    else:
        # broad: borderline innovation-candidates -> treatment=1, else 0
        d["Innovation_Deal"] = np.where(
            d.Provisional_Classification.isin(["Innovation-driven", "Borderline/mixed motive"]) &
            d.screen_group.str.contains("Innovation"), 1,
            np.where(d.Provisional_Classification.eq("Alternative rationale"), 0, np.nan))
        d = d[d.Innovation_Deal.notna()]
    if not include_majority:
        d = d[d.Deal_Subtype_Level_3.eq("100% Acquisition")]
    # coverage: >=2 pre & >=2 post
    pre = d[d.Relative_Year.isin([-3, -2, -1])].groupby("Deal_ID")[outcome].apply(lambda s: s.notna().sum())
    post = d[d.Relative_Year.isin([1, 2, 3])].groupby("Deal_ID")[outcome].apply(lambda s: s.notna().sum())
    keep = pre.index[(pre >= 2) & (post.reindex(pre.index).fillna(0) >= 2)]
    d = d[d.Deal_ID.isin(keep)].copy()
    if include_t0_post:
        d["Post"] = (d.Relative_Year >= 0).astype(int)
    else:
        d["Post"] = (d.Relative_Year >= 1).astype(int)
        d = d[d.Relative_Year != 0]     # drop completion year from pre/post analysis
    d["TxP"] = d.Innovation_Deal * d.Post
    d = d[d[outcome].notna()]
    d["Calendar_Year"] = d["Calendar_Year"].astype("Int64").astype(str)
    return d


def run_did(d, outcome, tag, note):
    n_clust = d.Acquirer_Normalized.nunique()
    m = pf.feols(f"{outcome} ~ TxP + Post | Deal_ID + Calendar_Year",
                 data=d, vcov={"CRV1": "Acquirer_Normalized"})
    tp = m.coef()["TxP"]
    se = m.se()["TxP"]
    ci = m.confint().loc["TxP"]
    pval = m.pvalue()["TxP"]
    pre_mean = d[d.Post == 0][outcome].mean()
    with open(os.path.join(MOD, f"did_{tag}.txt"), "w") as fh:
        fh.write(note + "\n\n" + m.summary().__str__() if hasattr(m.summary(), "__str__") else note)
    # wild cluster bootstrap (null-imposed Rademacher, manual implementation:
    # the wildboottest package fails on string cluster labels)
    wcb_p = np.nan
    try:
        wb = wild_cluster_boot_p(d, outcome, "TxP", ["Post"],
                                 ["Deal_ID", "Calendar_Year"],
                                 "Acquirer_Normalized", reps=4999)
        wcb_p = wb["p_wcb"]
    except Exception as e:
        print(f"WCB failed for {tag}: {e}")
    return {"panel": tag, "outcome": outcome, "spec": note,
            "beta_TxP": round(tp, 4), "se": round(se, 4),
            "ci_low": round(ci.iloc[0], 4), "ci_high": round(ci.iloc[1], 4),
            "p_cluster": round(pval, 4), "p_wildboot": round(wcb_p, 4) if wcb_p == wcb_p else np.nan,
            "n_obs": int(d.shape[0]), "n_deals": int(d.Deal_ID.nunique()),
            "n_clusters": int(n_clust), "pre_mean_outcome": round(pre_mean, 3)}


# ---------------- BASELINE MODELS -------------------------------------------
main_rows = []
d_roa = prep(fin, "ROA_pct")
main_rows.append(run_did(d_roa, "ROA_pct", "H2_ROA_strict", "Baseline DiD, ROA, strict innovation vs alternative"))

d_om = prep(fin, "Operating_Margin_pct")
main_rows.append(run_did(d_om, "Operating_Margin_pct", "H2_OpMargin_strict", "Baseline DiD, operating margin (secondary)"))

d_pat = prep(pat, "Patent_Family_Count")
main_rows.append(run_did(d_pat, "Patent_Family_Count", "H1_Patents_strict", "Baseline linear DiD, patent families, strict"))

# Poisson patent model (fixed-effects PPML)
try:
    mp = pf.fepois("Patent_Family_Count ~ TxP + Post | Deal_ID + Calendar_Year",
                   data=d_pat, vcov={"CRV1": "Acquirer_Normalized"})
    main_rows.append({"panel": "H1_Patents_PPML", "outcome": "Patent_Family_Count",
                      "spec": "FE-Poisson (PPML), strict", "beta_TxP": round(mp.coef()["TxP"], 4),
                      "se": round(mp.se()["TxP"], 4), "ci_low": round(mp.confint().loc["TxP"].iloc[0], 4),
                      "ci_high": round(mp.confint().loc["TxP"].iloc[1], 4),
                      "p_cluster": round(mp.pvalue()["TxP"], 4), "p_wildboot": np.nan,
                      "n_obs": int(d_pat.shape[0]), "n_deals": int(d_pat.Deal_ID.nunique()),
                      "n_clusters": int(d_pat.Acquirer_Normalized.nunique()), "pre_mean_outcome": np.nan})
except Exception as e:
    print("PPML failed:", e)

# IHS patent sensitivity
d_pat["ihs_pat"] = np.arcsinh(d_pat["Patent_Family_Count"])
main_rows.append(run_did(d_pat.assign(**{"Patent_Family_Count": d_pat["ihs_pat"]}),
                         "Patent_Family_Count", "H1_Patents_IHS", "IHS(patent families) DiD, strict"))

main = pd.DataFrame(main_rows)
main.to_csv(os.path.join(TAB, "main_did_results.csv"), index=False)
main.to_excel(os.path.join(TAB, "main_did_results.xlsx"), index=False)


# ---------------- EVENT STUDIES ---------------------------------------------
def event_study(df, outcome, tag, title, fname):
    d = prep(df, outcome, include_t0_post=True)  # keep t0 present for event time
    d = d.copy()
    d["rel"] = d.Relative_Year.astype(int)
    # dummies relative to k=-1. Use safe names (no '-' which formulaic parses).
    ks = [-3, -2, 0, 1, 2, 3]
    def nm(k): return f"m{abs(k)}" if k < 0 else f"p{k}"
    rows = []
    for k in ks:
        d[f"D_{nm(k)}"] = (d.rel == k).astype(int)
        d[f"I_{nm(k)}"] = d[f"D_{nm(k)}"] * d.Innovation_Deal
    terms = " + ".join([f"D_{nm(k)} + I_{nm(k)}" for k in ks])
    m = pf.feols(f"{outcome} ~ {terms} | Deal_ID + Calendar_Year",
                 data=d, vcov={"CRV1": "Acquirer_Normalized"})
    co, se = m.coef(), m.se()
    ci = m.confint()
    for k in ks:
        p = f"I_{nm(k)}"
        if p in co.index:
            rows.append({"panel": tag, "event_time": k, "beta": round(co[p], 4),
                         "se": round(se[p], 4), "ci_low": round(ci.loc[p].iloc[0], 4),
                         "ci_high": round(ci.loc[p].iloc[1], 4)})
    rows.append({"panel": tag, "event_time": -1, "beta": 0.0, "se": 0.0,
                 "ci_low": 0.0, "ci_high": 0.0})
    es = pd.DataFrame(rows).sort_values("event_time")
    # joint pre-trend test: differential pre-period coefs (t-3, t-2) jointly zero.
    from scipy import stats as _st
    pre_terms = [f"I_{nm(k)}" for k in [-3, -2] if f"I_{nm(k)}" in co.index]
    joint_p = np.nan
    try:
        names = list(co.index)
        idx = [names.index(t) for t in pre_terms]
        V = np.asarray(m._vcov)[np.ix_(idx, idx)]
        b = co.values[idx]
        stat = float(b @ np.linalg.pinv(V) @ b)     # Wald chi2
        joint_p = float(_st.chi2.sf(stat, df=len(idx)))
    except Exception:
        pass
    # plot differential (Innovation - Alternative) trajectory
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.errorbar(es.event_time, es.beta, yerr=[es.beta - es.ci_low, es.ci_high - es.beta],
                fmt="o-", color="#1b6ca8", capsize=3)
    ax.axhline(0, color="grey", lw=1)
    ax.axvline(-1, ls="--", color="grey", lw=1, label="reference (t-1)")
    ax.set_xlabel("Event time (relative year)")
    ax.set_ylabel(f"Differential {outcome}\n(Innovation − Alternative)")
    ax.set_title(title, fontsize=11)
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, fname))
    plt.close(fig)
    return es, joint_p


es_roa, jp_roa = event_study(fin, "ROA_pct", "H2_ROA", "Event study: differential ROA", "event_study_ROA.png")
es_pat, jp_pat = event_study(pat, "Patent_Family_Count", "H1_Patents", "Event study: differential patent families", "event_study_patents.png")
es = pd.concat([es_roa.assign(joint_pretrend_p=jp_roa), es_pat.assign(joint_pretrend_p=jp_pat)], ignore_index=True)
es.to_csv(os.path.join(TAB, "event_study_results.csv"), index=False)
es.to_excel(os.path.join(TAB, "event_study_results.xlsx"), index=False)


# ---------------- ROBUSTNESS ------------------------------------------------
rob = []
rob.append({**run_did(prep(fin, "ROA_pct", include_t0_post=True), "ROA_pct", "H2_ROA_t0post",
                       "Include completion year t0 as post")})
rob.append({**run_did(prep(fin, "ROA_pct", include_majority=False), "ROA_pct", "H2_ROA_100only",
                       "100% acquisitions only")})
rob.append({**run_did(prep(fin, "ROA_pct", include_borderline=True), "ROA_pct", "H2_ROA_broad",
                       "Broad sample incl. borderline innovation-candidates")})
# winsorised ROA
dw = prep(fin, "ROA_pct").copy()
lo, hi = dw.ROA_pct.quantile([0.05, 0.95])
dw["ROA_pct"] = dw.ROA_pct.clip(lo, hi)
rob.append({**run_did(dw, "ROA_pct", "H2_ROA_winsor", "Winsorised ROA (5/95)")})
rob.append({**run_did(prep(pat, "Patent_Family_Count", include_majority=False),
                      "Patent_Family_Count", "H1_Pat_100only", "Patents, 100% acquisitions only")})
rob.append({**run_did(prep(pat, "Patent_Family_Count", include_borderline=True),
                      "Patent_Family_Count", "H1_Pat_broad", "Patents, broad sample")})

# leave-one-firm-out (ROA strict)
base = prep(fin, "ROA_pct")
for firm in sorted(base.Acquirer_Normalized.unique()):
    dsub = base[base.Acquirer_Normalized != firm]
    if dsub.Innovation_Deal.nunique() < 2:
        continue
    try:
        r = run_did(dsub, "ROA_pct", f"H2_ROA_LOO_drop_{firm[:18]}", f"Leave-one-out: drop {firm}")
        rob.append(r)
    except Exception:
        pass

robdf = pd.DataFrame(rob)
robdf.to_csv(os.path.join(TAB, "robustness_results.csv"), index=False)
robdf.to_excel(os.path.join(TAB, "robustness_results.xlsx"), index=False)


# ---------------- HYPOTHESIS SUMMARY + COEF COMPARISON FIG -------------------
h = main[main.panel.isin(["H1_Patents_strict", "H1_Patents_PPML", "H2_ROA_strict", "H2_OpMargin_strict"])].copy()
h.to_csv(os.path.join(TAB, "hypothesis_results_summary.csv"), index=False)
h.to_excel(os.path.join(TAB, "hypothesis_results_summary.xlsx"), index=False)

fig, ax = plt.subplots(figsize=(7, 3.6))
plotd = main[main.panel.isin(["H2_ROA_strict", "H2_OpMargin_strict", "H1_Patents_strict"])]
y = range(len(plotd))
ax.errorbar(plotd.beta_TxP, list(y),
            xerr=[plotd.beta_TxP - plotd.ci_low, plotd.ci_high - plotd.beta_TxP],
            fmt="o", color="#1b6ca8", capsize=3)
ax.axvline(0, color="grey", lw=1)
ax.set_yticks(list(y))
ax.set_yticklabels(plotd.panel)
ax.set_xlabel("Differential post-acquisition change (Innovation − Alternative), 95% CI")
ax.set_title("Baseline DiD coefficients (provisional)", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "coefficient_comparison.png"))
plt.close(fig)

print("=== MAIN DiD ===")
print(main.to_string(index=False))
print("\n=== EVENT STUDY (pretrend joint p: ROA=%.3f, patents=%.3f) ===" % (jp_roa if jp_roa==jp_roa else -1, jp_pat if jp_pat==jp_pat else -1))
print(es.to_string(index=False))
print("\n=== ROBUSTNESS (head) ===")
print(robdf[["panel", "beta_TxP", "se", "ci_low", "ci_high", "p_cluster", "n_deals", "n_clusters"]].to_string(index=False))

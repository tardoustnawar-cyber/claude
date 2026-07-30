"""
04_descriptives_balance.py -- Phase: descriptives, group trajectories,
pre-treatment balance (standardised mean differences).
Outputs tables (csv/xlsx) and figures (png).
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
for d in (TAB, FIG):
    os.makedirs(d, exist_ok=True)

plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.spines.top": False, "axes.spines.right": False})
INNOV_C, ALT_C = "#1b6ca8", "#c1442e"

fin = pd.read_csv(os.path.join(PROC, "financial_did_panel.csv"))
pat = pd.read_csv(os.path.join(PROC, "patent_did_panel.csv"))


def strict_preferred(df, outcome):
    d = df[df.Innovation_Deal.notna()].copy()
    pre = d[d.Relative_Year.isin([-3, -2, -1])].groupby("Deal_ID")[outcome].apply(lambda s: s.notna().sum())
    post = d[d.Relative_Year.isin([1, 2, 3])].groupby("Deal_ID")[outcome].apply(lambda s: s.notna().sum())
    keep = pre.index[(pre >= 2) & (post.reindex(pre.index).fillna(0) >= 2)]
    return d[d.Deal_ID.isin(keep)].copy()


finS = strict_preferred(fin, "ROA_pct")
patS = strict_preferred(pat, "Patent_Family_Count")


# ---- descriptive statistics -------------------------------------------------
def descr(df, outcome, label):
    rows = []
    for grp, name in [(1, "Innovation-driven"), (0, "Alternative-rationale")]:
        g = df[df.Innovation_Deal == grp]
        ndeal = g.Deal_ID.nunique()
        pre = g[g.Relative_Year.isin([-3, -2, -1])][outcome]
        post = g[g.Relative_Year.isin([1, 2, 3])][outcome]
        rows.append({"panel": label, "group": name, "n_deals": ndeal,
                     "n_obs": g[outcome].notna().sum(),
                     "pre_mean": round(pre.mean(), 3), "pre_sd": round(pre.std(), 3),
                     "post_mean": round(post.mean(), 3), "post_sd": round(post.std(), 3),
                     "raw_change": round(post.mean() - pre.mean(), 3)})
    return pd.DataFrame(rows)


desc = pd.concat([descr(finS, "ROA_pct", "ROA (%)"),
                  descr(patS, "Patent_Family_Count", "Patent families")], ignore_index=True)
desc.to_csv(os.path.join(TAB, "descriptive_statistics.csv"), index=False)
desc.to_excel(os.path.join(TAB, "descriptive_statistics.xlsx"), index=False)


# ---- balance table (pre-treatment, SMD) ------------------------------------
def smd(a, b):
    a, b = a.dropna(), b.dropna()
    if len(a) < 2 or len(b) < 2:
        return np.nan
    sp = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    return np.nan if sp == 0 else (a.mean() - b.mean()) / sp


def balance(df, varlist, label):
    pre = df[df.Relative_Year.isin([-3, -2, -1])]
    rows = []
    for v in varlist:
        if v not in pre.columns:
            continue
        a = pre[pre.Innovation_Deal == 1][v]
        b = pre[pre.Innovation_Deal == 0][v]
        rows.append({"panel": label, "variable": v,
                     "innov_mean": round(a.mean(), 3), "alt_mean": round(b.mean(), 3),
                     "SMD": round(smd(a, b), 3)})
    return pd.DataFrame(rows)


bal = pd.concat([
    balance(finS, ["ROA_pct", "Operating_Margin_pct", "Total_Assets_m", "Revenue_m",
                   "Leverage_pct", "R_and_D_Expense_m"], "financial"),
    balance(patS, ["Patent_Family_Count", "Citation_Weighted_Output"], "patent"),
], ignore_index=True)
# add deal-level completion-year balance
for df, lab, panel in [(finS, "Completion_Year", "financial"), (patS, "Completion_Year", "patent")]:
    dd = df.drop_duplicates("Deal_ID")
    a, b = dd[dd.Innovation_Deal == 1][lab], dd[dd.Innovation_Deal == 0][lab]
    bal.loc[len(bal)] = {"panel": panel, "variable": lab,
                         "innov_mean": round(a.mean(), 2), "alt_mean": round(b.mean(), 2),
                         "SMD": round(smd(a, b), 3)}
bal.to_csv(os.path.join(TAB, "balance_table.csv"), index=False)
bal.to_excel(os.path.join(TAB, "balance_table.xlsx"), index=False)


# ---- group trajectory + pretrend figures -----------------------------------
def traj(df, outcome, title, fname):
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for grp, name, col in [(1, "Innovation-driven", INNOV_C), (0, "Alternative-rationale", ALT_C)]:
        g = df[df.Innovation_Deal == grp].groupby("Relative_Year")[outcome].agg(["mean", "count"])
        ax.plot(g.index, g["mean"], marker="o", color=col, label=f"{name} (n deals={df[df.Innovation_Deal==grp].Deal_ID.nunique()})")
    ax.axvline(-0.5, ls="--", color="grey", lw=1)
    ax.axvline(0.5, ls="--", color="grey", lw=1)
    ax.set_xlabel("Relative year (t0 = completion year)")
    ax.set_ylabel(outcome)
    ax.set_title(title, fontsize=11)
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, fname))
    plt.close(fig)


traj(finS, "ROA_pct", "Mean ROA by relative year (strict primary sample)", "group_trajectories_ROA.png")
traj(patS, "Patent_Family_Count", "Mean patent-family count by relative year (strict primary sample)", "group_trajectories_patents.png")
# pretrend-focused (pre years only)
traj(finS[finS.Relative_Year <= 0], "ROA_pct", "Pre-treatment ROA trajectory", "pretrend_ROA.png")
traj(patS[patS.Relative_Year <= 0], "Patent_Family_Count", "Pre-treatment patent trajectory", "pretrend_patents.png")

print("Descriptives + balance written.")
print(desc.to_string(index=False))
print("\nBalance (pre-treatment SMD):")
print(bal.to_string(index=False))

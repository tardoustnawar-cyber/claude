"""Phase 18: publication figures."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"; MOD = ROOT / "outputs" / "models"
FIG = ROOT / "outputs" / "figures"; FIG.mkdir(parents=True, exist_ok=True)
TAB = ROOT / "outputs" / "tables"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.grid":True,
                     "grid.alpha":0.3,"figure.dpi":150})
INN, ALT = "#2166AC", "#B2182B"

h2 = pd.read_csv(PROC/"h2_financial_did_panel.csv")
h1 = pd.read_csv(PROC/"h1_patent_did_panel.csv")

# --- Fig 3/4: group-mean trajectories ---
def traj(df, outcome, ylab, title, fname):
    fig, ax = plt.subplots(figsize=(7,4.5))
    for tr,c,lbl in [(1,INN,"Innovation-driven"),(0,ALT,"Alternative-rationale")]:
        g = df[df.treat==tr].groupby("RelativeYear")[outcome].agg(["mean","sem"]).reset_index()
        g = g[g.RelativeYear!=0]
        ax.errorbar(g.RelativeYear,g["mean"],yerr=g["sem"],marker="o",color=c,label=lbl,capsize=3)
    ax.axvline(-0.5,ls="--",color="grey",alpha=0.6); ax.axhline(0,color="black",lw=0.6)
    ax.set_xlabel("Relative year (t0 = completion, omitted)"); ax.set_ylabel(ylab)
    ax.set_title(title); ax.legend(frameon=False)
    ax.text(0.01,-0.17,f"n(innovation)={df[df.treat==1].deal_event_id.nunique()} deals, "
            f"n(alternative)={df[df.treat==0].deal_event_id.nunique()} deals. Bars = SEM.",
            transform=ax.transAxes,fontsize=7.5,color="grey")
    fig.tight_layout(); fig.savefig(FIG/fname,bbox_inches="tight"); plt.close(fig)

traj(h2,"ROA_pct","Return on Assets (pp)","Fig 3. Mean ROA trajectory by deal rationale","fig3_roa_trajectory.png")
traj(h1,"patent_families","Unique simple patent families","Fig 4. Mean patent-family trajectory by deal rationale","fig4_patent_trajectory.png")

# --- Fig 5/6: event-study plots ---
def es_plot(fname_in, title, ylab, fout):
    es = pd.read_csv(MOD/fname_in)
    ref = pd.DataFrame([{"relative_year":-1,"beta_diff":0,"ci_lo":0,"ci_hi":0}])
    es = pd.concat([es,ref]).sort_values("relative_year")
    fig,ax = plt.subplots(figsize=(7,4.5))
    ax.errorbar(es.relative_year,es.beta_diff,
                yerr=[es.beta_diff-es.ci_lo,es.ci_hi-es.beta_diff],
                marker="o",color=INN,capsize=3)
    ax.axhline(0,color="black",lw=0.7); ax.axvline(-0.5,ls="--",color="grey",alpha=0.6)
    ax.set_xlabel("Relative year (reference t-1)"); ax.set_ylabel(ylab)
    ax.set_title(title)
    ax.text(0.01,-0.17,"Differential (innovation - alternative) coefficients, deal & year FE, "
            "95% CI, SE clustered by acquirer.",transform=ax.transAxes,fontsize=7.5,color="grey")
    fig.tight_layout(); fig.savefig(FIG/fout,bbox_inches="tight"); plt.close(fig)

es_plot("eventstudy_H2_ROA.csv","Fig 5. ROA event study (differential)","Differential ROA (pp)","fig5_roa_eventstudy.png")
es_plot("eventstudy_H1_patents.csv","Fig 6. Patent event study (differential)","Differential families","fig6_patent_eventstudy.png")

# --- Fig 7: Love plot (balance) ---
bal = pd.read_excel(TAB/"T4_T5_descriptives.xlsx", sheet_name="balance_SMD")
bal = bal.dropna(subset=["smd"])
fig,ax = plt.subplots(figsize=(7,4.5))
y = range(len(bal))
colors = [INN if s=="H1" else ALT for s in bal["sample"]]
ax.scatter(bal["smd"].abs(), y, c=colors)
ax.axvline(0.1,ls="--",color="grey"); ax.axvline(0.25,ls=":",color="grey")
ax.set_yticks(list(y)); ax.set_yticklabels([f"[{s}] {v}" for s,v in zip(bal["sample"],bal["variable"])],fontsize=7.5)
ax.set_xlabel("|Standardised mean difference| (pre-treatment)")
ax.set_title("Fig 7. Pre-treatment balance (Love plot)")
ax.text(0.99,-0.15,"Dashed=0.10, dotted=0.25 thresholds. Blue=H1 patent sample, red=H2 ROA sample.",
        transform=ax.transAxes,fontsize=7.5,color="grey",ha="right")
fig.tight_layout(); fig.savefig(FIG/"fig7_love_plot.png",bbox_inches="tight"); plt.close(fig)

# --- Fig 8: common support (pre-outcome distributions) ---
fig,axes = plt.subplots(1,2,figsize=(10,4))
for ax,df,outcome,title in [(axes[0],h2,"ROA_pct","H2: pre-period ROA (pp)"),
                            (axes[1],h1,"patent_families","H1: pre-period families")]:
    pre = df[df.RelativeYear.between(-3,-1)]
    ep = pre.groupby(["deal_event_id","treat"])[outcome].mean().reset_index()
    ax.hist(ep[ep.treat==1][outcome],bins=8,alpha=0.6,color=INN,label="Innovation")
    ax.hist(ep[ep.treat==0][outcome],bins=8,alpha=0.6,color=ALT,label="Alternative")
    ax.set_title(title); ax.set_ylabel("Deals"); ax.legend(frameon=False,fontsize=8)
fig.suptitle("Fig 8. Common support: pre-treatment outcome distributions")
fig.tight_layout(); fig.savefig(FIG/"fig8_common_support.png",bbox_inches="tight"); plt.close(fig)

# --- Fig 9: main coefficient plot ---
res = pd.read_csv(TAB/"T7_T8_T10_did_estimates.csv")
main = res[res.model_tag.isin(["H2_primary_linearFE_ROA","H1_primary_linearFE_fam"])]
fig,ax = plt.subplots(figsize=(7,3.2))
labels = ["H2: ROA (pp)","H1: patent families"]
for i,(_,r) in enumerate(main.iterrows()):
    ax.errorbar(r["beta(TreatxPost)"],i,xerr=[[r["beta(TreatxPost)"]-r["ci_lo"]],[r["ci_hi"]-r["beta(TreatxPost)"]]],
                marker="o",color=INN,capsize=4)
ax.axvline(0,color="black",lw=0.8)
ax.set_yticks([0,1]); ax.set_yticklabels(labels); ax.set_ylim(-0.5,1.5)
ax.set_xlabel("Differential post-acquisition change (Innovation x Post), 95% CI")
ax.set_title("Fig 9. Main DiD coefficients")
fig.tight_layout(); fig.savefig(FIG/"fig9_main_coefficients.png",bbox_inches="tight"); plt.close(fig)

# --- Fig 10: leave-one-acquirer-out influence ---
loo = pd.read_csv(TAB/"T11_leave_one_out.csv")
fig,axes = plt.subplots(1,2,figsize=(11,4.5))
for ax,lab,base in [(axes[0],"H2_ROA",res[res.model_tag=="H2_primary_linearFE_ROA"]["beta(TreatxPost)"].iloc[0]),
                    (axes[1],"H1_patents",res[res.model_tag=="H1_primary_linearFE_fam"]["beta(TreatxPost)"].iloc[0])]:
    s = loo[loo["sample"]==lab].sort_values("beta")
    ax.barh(range(len(s)),s["beta"],color=INN,alpha=0.7)
    ax.axvline(base,color=ALT,ls="--",label=f"Full-sample beta={base:.2f}")
    ax.set_yticks(range(len(s))); ax.set_yticklabels(s["dropped_acquirer"],fontsize=7)
    ax.set_xlabel("Beta when acquirer dropped"); ax.set_title(f"Fig 10. {lab}: leave-one-acquirer-out"); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(FIG/"fig10_leave_one_out.png",bbox_inches="tight"); plt.close(fig)

# --- Fig 2: coverage heatmap ---
fig,axes = plt.subplots(1,2,figsize=(11,5))
for ax,df,outcome,title in [(axes[0],h2,"ROA_pct","H2 ROA coverage"),(axes[1],h1,"patent_families","H1 patent coverage")]:
    piv = (df.assign(has=1).pivot_table(index="deal_event_id",columns="RelativeYear",values=outcome,
           aggfunc=lambda s: int(s.notna().any())).reindex(columns=[-3,-2,-1,1,2,3]))
    ax.imshow(piv.fillna(0).values,aspect="auto",cmap="Blues",vmin=0,vmax=1)
    ax.set_xticks(range(6)); ax.set_xticklabels([-3,-2,-1,1,2,3])
    ax.set_yticks(range(len(piv))); ax.set_yticklabels(piv.index,fontsize=6)
    ax.set_xlabel("Relative year"); ax.set_title(title)
fig.suptitle("Fig 2. Outcome coverage by deal and relative year")
fig.tight_layout(); fig.savefig(FIG/"fig2_coverage_heatmap.png",bbox_inches="tight"); plt.close(fig)

print("figures written:", sorted(p.name for p in FIG.glob("*.png")))

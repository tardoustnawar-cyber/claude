"""Shared estimation helpers: two-way FE DiD, cluster SE, wild-cluster bootstrap."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

RNG = np.random.default_rng(20260730)

def twfe_did(df, outcome, interaction="TreatPost", extra=None, cluster="acquirer_group"):
    """Y = deal FE + year FE + Post + Treat*Post (+extra). Cluster-robust by acquirer.
    Treat main effect is absorbed by deal FE. Returns dict of results."""
    d = df.copy()
    need = [outcome] + (extra or [])
    d = d.dropna(subset=need)
    d["deal"] = d["deal_event_id"].astype("category")
    d["yr"] = d["calendar_year"].astype("category") if "calendar_year" in d else d["priority_year"].astype("category")
    terms = ["C(deal)", "C(yr)", "Post", interaction]
    if extra:
        terms += extra
    formula = f"{outcome} ~ " + " + ".join(terms)
    groups = d[cluster].astype("category").cat.codes.values
    model = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": groups})
    n_clusters = d[cluster].nunique()
    return {"model": model, "beta": model.params.get(interaction, np.nan),
            "se": model.bse.get(interaction, np.nan), "p": model.pvalues.get(interaction, np.nan),
            "delta": model.params.get("Post", np.nan),
            "ci": model.conf_int().loc[interaction].tolist() if interaction in model.params else [np.nan, np.nan],
            "n": int(model.nobs), "n_clusters": int(n_clusters),
            "n_events": d["deal_event_id"].nunique()}

def wild_cluster_bootstrap(df, outcome, interaction="TreatPost", extra=None,
                           cluster="acquirer_group", B=1999):
    """Restricted (null-imposed) wild cluster bootstrap-t, Rademacher weights.
    Returns bootstrap p-value for H0: beta_interaction = 0."""
    d = df.copy()
    d = d.dropna(subset=[outcome] + (extra or []))
    d["deal"] = d["deal_event_id"].astype("category")
    d["yr"] = (d["calendar_year"] if "calendar_year" in d else d["priority_year"]).astype("category")
    terms = ["C(deal)", "C(yr)", "Post", interaction] + (extra or [])
    formula = f"{outcome} ~ " + " + ".join(terms)
    groups = d[cluster].astype("category").cat.codes.values
    uniq = np.unique(groups)
    # observed t
    fit = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": groups})
    t_obs = fit.params[interaction] / fit.bse[interaction]
    # restricted model (impose null: drop interaction)
    terms0 = ["C(deal)", "C(yr)", "Post"] + (extra or [])
    formula0 = f"{outcome} ~ " + " + ".join(terms0)
    fit0 = smf.ols(formula0, data=d).fit()
    resid0 = fit0.resid.values
    yhat0 = fit0.fittedvalues.values
    t_boot = np.empty(B)
    Xdesign = fit.model.exog
    for b in range(B):
        w = RNG.choice([-1.0, 1.0], size=len(uniq))
        wmap = dict(zip(uniq, w))
        wobs = np.array([wmap[g] for g in groups])
        ystar = yhat0 + resid0 * wobs
        dd = d.copy(); dd[outcome] = ystar
        try:
            fb = smf.ols(formula, data=dd).fit(cov_type="cluster", cov_kwds={"groups": groups})
            t_boot[b] = fb.params[interaction] / fb.bse[interaction]
        except Exception:
            t_boot[b] = np.nan
    t_boot = t_boot[~np.isnan(t_boot)]
    p = np.mean(np.abs(t_boot) >= np.abs(t_obs))
    return {"t_obs": t_obs, "wild_p": p, "B_used": len(t_boot)}

def ppml_did(df, outcome, interaction="TreatPost", cluster="acquirer_group"):
    """Poisson pseudo-ML with deal + year FE, cluster-robust SE."""
    d = df.copy()
    d = d.dropna(subset=[outcome])
    d["deal"] = d["deal_event_id"].astype("category")
    d["yr"] = d["priority_year"].astype("category")
    formula = f"{outcome} ~ C(deal) + C(yr) + Post + {interaction}"
    groups = d[cluster].astype("category").cat.codes.values
    m = smf.glm(formula, data=d, family=sm.families.Poisson()).fit(
        cov_type="cluster", cov_kwds={"groups": groups})
    return {"model": m, "beta": m.params.get(interaction, np.nan),
            "se": m.bse.get(interaction, np.nan), "p": m.pvalues.get(interaction, np.nan),
            "ci": m.conf_int().loc[interaction].tolist() if interaction in m.params else [np.nan, np.nan],
            "n": int(m.nobs), "n_clusters": d[cluster].nunique()}

def event_study(df, outcome, cluster="acquirer_group"):
    """Y = deal FE + year FE + sum_k delta_k 1(rel=k) + sum_k beta_k treat*1(rel=k), ref k=-1."""
    d = df.copy()
    d["deal"] = d["deal_event_id"].astype("category")
    d["yr"] = (d["calendar_year"] if "calendar_year" in d else d["priority_year"]).astype("category")
    d["rel"] = d["RelativeYear"].astype(int)
    ks = sorted([k for k in d["rel"].unique() if k != -1])
    def tok(k): return f"m{abs(k)}" if k < 0 else f"p{k}"
    for k in ks:
        d[f"D{tok(k)}"] = (d["rel"] == k).astype(int)
        d[f"T{tok(k)}"] = ((d["rel"] == k) & (d["treat"] == 1)).astype(int)
    dterms = [f"D{tok(k)}" for k in ks]
    tterms = [f"T{tok(k)}" for k in ks]
    formula = f"{outcome} ~ C(deal) + C(yr) + " + " + ".join(dterms + tterms)
    groups = d[cluster].astype("category").cat.codes.values
    m = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": groups})
    rows = []
    for k in ks:
        tt = f"T{tok(k)}"
        rows.append({"relative_year": k,
                     "beta_diff": m.params.get(tt, np.nan),
                     "se": m.bse.get(tt, np.nan),
                     "ci_lo": m.conf_int().loc[tt][0] if tt in m.params else np.nan,
                     "ci_hi": m.conf_int().loc[tt][1] if tt in m.params else np.nan,
                     "delta_alt": m.params.get(f"D{tok(k)}", np.nan)})
    es = pd.DataFrame(rows)
    # joint pre-trend test on pre-period interactions (k < -1)
    pre = [f"T{tok(k)}" for k in ks if k < -1]
    joint = None
    if pre:
        try:
            joint = m.f_test(" , ".join([f"{t} = 0" for t in pre]))
        except Exception:
            joint = None
    return {"model": m, "coefs": es, "pretrend_test": joint, "pre_terms": pre}

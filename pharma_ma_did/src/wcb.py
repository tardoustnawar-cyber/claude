"""Minimal null-imposed wild cluster bootstrap-t (Rademacher weights),
Cameron-Gelbach-Miller style, for a single coefficient in an OLS model with
dummy fixed effects. Used because the wildboottest package fails on
string cluster labels (numba typing error).
"""
import numpy as np
import pandas as pd


def _crv1_t(X, y, clusters, j):
    """OLS + CRV1 t-stat for coefficient j."""
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    u = y - X @ beta
    G = pd.unique(clusters)
    meat = np.zeros((X.shape[1], X.shape[1]))
    for g in G:
        idx = clusters == g
        Xg, ug = X[idx], u[idx]
        s = Xg.T @ ug
        meat += np.outer(s, s)
    n, k, ng = len(y), X.shape[1], len(G)
    dof = (ng / (ng - 1)) * ((n - 1) / (n - k))
    V = dof * XtX_inv @ meat @ XtX_inv
    se = np.sqrt(V[j, j])
    return beta[j], se, beta[j] / se, beta, u


def wild_cluster_boot_p(df, y_col, param, controls, fe_cols, cluster_col,
                        reps=9999, seed=20260730):
    """Bootstrap p-value for `param` with the null imposed."""
    rng = np.random.default_rng(seed)
    d = df.dropna(subset=[y_col]).copy()
    # design: param + controls + FE dummies (drop-first to avoid collinearity)
    fe_dummies = pd.get_dummies(d[fe_cols].astype(str), drop_first=True, dtype=float)
    X_full = np.column_stack([d[param].values.astype(float)] +
                             [d[c].values.astype(float) for c in controls] +
                             [np.ones(len(d))] + [fe_dummies.values])
    y = d[y_col].values.astype(float)
    clusters = d[cluster_col].values
    b_obs, se_obs, t_obs, _, _ = _crv1_t(X_full, y, clusters, 0)

    # restricted model: exclude param column
    X_r = X_full[:, 1:]
    beta_r = np.linalg.pinv(X_r.T @ X_r) @ (X_r.T @ y)
    fit_r = X_r @ beta_r
    res_r = y - fit_r

    G = pd.unique(clusters)
    gidx = {g: clusters == g for g in G}
    exceed = 0
    valid = 0
    for _ in range(reps):
        w = rng.choice([-1.0, 1.0], size=len(G))
        u_star = res_r.copy()
        for gi, g in enumerate(G):
            u_star[gidx[g]] *= w[gi]
        y_star = fit_r + u_star
        try:
            _, _, t_star, _, _ = _crv1_t(X_full, y_star, clusters, 0)
            if np.isfinite(t_star):
                valid += 1
                if abs(t_star) >= abs(t_obs):
                    exceed += 1
        except np.linalg.LinAlgError:
            continue
    p = exceed / valid if valid else np.nan
    return {"beta": b_obs, "se_crv1": se_obs, "t": t_obs, "p_wcb": p,
            "reps_valid": valid, "n_clusters": len(G)}

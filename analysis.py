"""Employee engagement driver analysis.

Usage:
    python analysis.py --data data/responses.csv
    python analysis.py --data data/DEMO_synthetic_responses.csv   # demo run

Steps: data checks -> scale scores -> reliability (Cronbach's alpha) ->
factorability + exploratory factor analysis -> correlations ->
multiple regression (standardised betas, CIs, VIF, unique R2, bootstrap) ->
pre-stated hypothesis tests -> charts + auto-generated results summary.
"""
import argparse, json, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.decomposition import FactorAnalysis

DRIVERS = {
    "Manager support": ["mgr1", "mgr2"],
    "Recognition": ["rec1", "rec2"],
    "Workload": ["wl1", "wl2"],
    "Growth": ["gro1", "gro2"],
    "Autonomy": ["aut1", "aut2"],
    "Team belonging": ["team1", "team2"],
}
OUTCOME_ITEMS = ["eng1", "eng2", "eng3"]
ITEMS = [i for v in DRIVERS.values() for i in v]
NAVY, TEAL, GREY = "#1F3A5F", "#2A9D8F", "#B0B7C3"


# ---------- helpers ----------
def cronbach_alpha(d):
    d = d.dropna()
    k = d.shape[1]
    return k / (k - 1) * (1 - d.var(ddof=1).sum() / d.sum(axis=1).var(ddof=1))


def spearman_brown(d):
    """Preferred reliability index for 2-item scales."""
    r = d.corr().iloc[0, 1]
    return 2 * r / (1 + r)


def ols(X, y):
    """OLS with intercept. Returns betas, se, t, p, ci, r2, adj_r2, F, F_p."""
    n, k = X.shape
    Xc = np.column_stack([np.ones(n), X])
    beta = np.linalg.lstsq(Xc, y, rcond=None)[0]
    resid = y - Xc @ beta
    dof = n - k - 1
    sigma2 = resid @ resid / dof
    se = np.sqrt(np.diag(sigma2 * np.linalg.inv(Xc.T @ Xc)))
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), dof)
    tcrit = stats.t.ppf(0.975, dof)
    r2 = 1 - resid @ resid / ((y - y.mean()) @ (y - y.mean()))
    adj = 1 - (1 - r2) * (n - 1) / dof
    F = (r2 / k) / ((1 - r2) / dof)
    return dict(beta=beta[1:], se=se[1:], t=t[1:], p=p[1:],
                lo=beta[1:] - tcrit * se[1:], hi=beta[1:] + tcrit * se[1:],
                r2=r2, adj_r2=adj, F=F, F_p=stats.f.sf(F, k, dof), dof=dof)


def vif(X):
    out = []
    for j in range(X.shape[1]):
        others = np.delete(X, j, axis=1)
        r2 = ols(others, X[:, j])["r2"]
        out.append(1 / (1 - r2))
    return np.array(out)


def kmo_bartlett(d):
    R = d.corr().values.copy()
    n, p = d.shape
    chi2 = -(n - 1 - (2 * p + 5) / 6) * np.log(np.linalg.det(R))
    bart_p = stats.chi2.sf(chi2, p * (p - 1) / 2)
    inv = np.linalg.inv(R)
    partial = -inv / np.sqrt(np.outer(np.diag(inv), np.diag(inv)))
    np.fill_diagonal(R, 0); np.fill_diagonal(partial, 0)
    kmo = (R ** 2).sum() / ((R ** 2).sum() + (partial ** 2).sum())
    return kmo, chi2, bart_p


def fp(p):
    return "<.001" if p < .001 else f"{p:.3f}"


def sig(p):
    return "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else "ns"


# ---------- main ----------
def main(path, outdir, seed=7):
    os.makedirs(outdir, exist_ok=True)
    demo = "DEMO" in os.path.basename(path).upper()
    tag = " [DEMO - SYNTHETIC DATA]" if demo else ""
    df = pd.read_csv(path)
    n0 = len(df)

    # 1. data quality
    missing = [c for c in ITEMS + OUTCOME_ITEMS if c not in df.columns]
    assert not missing, f"Missing columns: {missing}"
    df = df.dropna(subset=ITEMS + OUTCOME_ITEMS)
    straightliners = df[ITEMS + OUTCOME_ITEMS].std(axis=1) == 0
    df = df[~straightliners].reset_index(drop=True)
    n = len(df)
    R = {"n_raw": n0, "n_clean": n, "n_removed_incomplete": n0 - len(df) - int(straightliners.sum()),
         "n_removed_straightliners": int(straightliners.sum()), "demo": demo}

    # 2. scale scores
    scores = pd.DataFrame({k: df[v].mean(axis=1) for k, v in DRIVERS.items()})
    scores["Engagement"] = df[OUTCOME_ITEMS].mean(axis=1)

    # 3. reliability
    rel = {k: spearman_brown(df[v]) for k, v in DRIVERS.items()}
    rel["Engagement"] = cronbach_alpha(df[OUTCOME_ITEMS])
    R["reliability"] = {k: round(float(v), 3) for k, v in rel.items()}

    # 4. factorability + EFA
    kmo, chi2, bp = kmo_bartlett(df[ITEMS])
    R["kmo"], R["bartlett_p"] = round(float(kmo), 3), float(bp)
    eig = np.sort(np.linalg.eigvalsh(df[ITEMS].corr().values))[::-1]
    n_f = int((eig > 1).sum())
    R["eigenvalues"] = [round(float(e), 2) for e in eig]
    R["factors_kaiser"] = n_f
    fa = FactorAnalysis(n_components=len(DRIVERS), rotation="varimax", random_state=0)
    fa.fit((df[ITEMS] - df[ITEMS].mean()) / df[ITEMS].std())
    load = pd.DataFrame(fa.components_.T, index=ITEMS,
                        columns=[f"F{i+1}" for i in range(len(DRIVERS))])
    load.round(2).to_csv(f"{outdir}/efa_loadings.csv")

    # 5. correlations
    corr = scores.corr()
    corr.round(3).to_csv(f"{outdir}/correlations.csv")

    # 6. regression on standardised scores
    Z = (scores - scores.mean()) / scores.std(ddof=1)
    X, y = Z[list(DRIVERS)].values, Z["Engagement"].values
    m = ols(X, y)
    v = vif(X)
    unique = []
    for j in range(X.shape[1]):
        unique.append(m["r2"] - ols(np.delete(X, j, axis=1), y)["r2"])
    reg = pd.DataFrame({"driver": list(DRIVERS), "std_beta": m["beta"], "ci_low": m["lo"],
                        "ci_high": m["hi"], "p": m["p"], "vif": v,
                        "unique_R2": unique, "sig": [sig(p) for p in m["p"]]})
    reg = reg.sort_values("std_beta", ascending=False).reset_index(drop=True)

    # bootstrap: stability of driver ranking
    rng = np.random.default_rng(seed)
    B, boots = 2000, []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        boots.append(ols(X[idx], y[idx])["beta"])
    boots = np.array(boots)
    top_share = np.bincount(boots.argmax(axis=1), minlength=len(DRIVERS)) / B
    reg["boot_ci_low"] = [np.percentile(boots[:, list(DRIVERS).index(d)], 2.5) for d in reg.driver]
    reg["boot_ci_high"] = [np.percentile(boots[:, list(DRIVERS).index(d)], 97.5) for d in reg.driver]
    reg["pct_boot_ranked_#1"] = [top_share[list(DRIVERS).index(d)] for d in reg.driver]
    reg.round(3).to_csv(f"{outdir}/regression_results.csv", index=False)
    R["regression"] = {"r2": round(float(m["r2"]), 3), "adj_r2": round(float(m["adj_r2"]), 3),
                       "F": round(float(m["F"]), 2), "F_p": float(m["F_p"]), "dof": int(m["dof"]),
                       "max_vif": round(float(v.max()), 2)}

    # 7. pre-stated hypotheses
    H = {}
    top = reg.iloc[0]
    H["H1"] = dict(text="Manager support is the strongest driver of engagement",
                   result=f"Top driver = {top.driver} (beta={top.std_beta:.2f}); ranked #1 in "
                          f"{top['pct_boot_ranked_#1']:.0%} of bootstrap samples",
                   supported=bool(top.driver == "Manager support" and top["pct_boot_ranked_#1"] > .5))
    wl = reg[reg.driver == "Workload"].iloc[0]
    H["H2"] = dict(text="Manageable workload positively predicts engagement, controlling for other drivers",
                   result=f"beta={wl.std_beta:.2f}, 95% CI [{wl.ci_low:.2f}, {wl.ci_high:.2f}], p={wl.p:.3f}",
                   supported=bool(wl.std_beta > 0 and wl.p < .05))
    groups = [g["Engagement"].values for _, g in scores.assign(a=df["arrangement"]).groupby("a")]
    Fv, pv = stats.f_oneway(*groups)
    hv, pk = stats.kruskal(*groups)
    grand = scores["Engagement"].mean()
    ss_b = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
    eta2 = ss_b / ((scores["Engagement"] - grand) ** 2).sum()
    means = scores.assign(a=df["arrangement"]).groupby("a")["Engagement"].agg(["mean", "std", "count"])
    means.round(2).to_csv(f"{outdir}/engagement_by_arrangement.csv")
    H["H3"] = dict(text="Engagement differs by work arrangement (on-site / hybrid / remote)",
                   result=f"ANOVA F={Fv:.2f}, p={pv:.3f}; Kruskal-Wallis p={pk:.3f}; eta^2={eta2:.3f}",
                   supported=bool(pv < .05 and pk < .05))
    R["hypotheses"] = H

    with open(f"{outdir}/results.json", "w") as f:
        json.dump(R, f, indent=2, default=float)

    # 8. charts
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False,
                         "axes.spines.right": False})
    # driver importance
    fig, ax = plt.subplots(figsize=(7, 4))
    r = reg.iloc[::-1]
    ax.barh(r.driver, r.std_beta, color=[NAVY if p < .05 else GREY for p in r.p],
            xerr=[r.std_beta - r.ci_low, r.ci_high - r.std_beta], ecolor="#444", capsize=3)
    ax.axvline(0, color="#444", lw=.8)
    ax.set_xlabel("Standardised beta (95% CI)   |   dark = p < .05")
    ax.set_title(f"What drives engagement?{tag}", loc="left", fontweight="bold", fontsize=11)
    fig.tight_layout(); fig.savefig(f"{outdir}/fig1_driver_importance.png", dpi=200); plt.close()
    # heatmap
    fig, ax = plt.subplots(figsize=(6.4, 5))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr))); ax.set_xticklabels(corr.columns, rotation=40, ha="right")
    ax.set_yticks(range(len(corr))); ax.set_yticklabels(corr.columns)
    for i in range(len(corr)):
        for j in range(len(corr)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
    ax.set_title(f"Correlations between scales{tag}", loc="left", fontweight="bold", fontsize=11)
    fig.colorbar(im, shrink=.8); fig.tight_layout()
    fig.savefig(f"{outdir}/fig2_correlations.png", dpi=200); plt.close()
    # scree
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.plot(range(1, len(eig) + 1), eig, "o-", color=NAVY)
    ax.axhline(1, color="#c0392b", ls="--", lw=1)
    ax.set_xlabel("Factor"); ax.set_ylabel("Eigenvalue")
    ax.set_title(f"Scree plot (Kaiser criterion = 1){tag}", loc="left", fontweight="bold", fontsize=11)
    fig.tight_layout(); fig.savefig(f"{outdir}/fig3_scree.png", dpi=200); plt.close()
    # engagement by arrangement
    order = [a for a in ["On-site", "Hybrid", "Remote"] if a in means.index]
    fig, ax = plt.subplots(figsize=(5.5, 3.8))
    se = means.loc[order, "std"] / np.sqrt(means.loc[order, "count"])
    ax.bar(order, means.loc[order, "mean"], yerr=1.96 * se, color=TEAL, capsize=4)
    ax.set_ylim(1, 5); ax.set_ylabel("Engagement (1-5)")
    ax.set_title(f"Engagement by work arrangement{tag}", loc="left", fontweight="bold", fontsize=11)
    fig.tight_layout(); fig.savefig(f"{outdir}/fig4_arrangement.png", dpi=200); plt.close()

    # 9. auto-written summary (numbers come straight from the run)
    L = [f"# Results summary{tag}", ""]
    if demo:
        L += ["> **This run used SIMULATED data. The numbers below demonstrate the pipeline only "
              "and must not be reported as findings.**", ""]
    L += [f"**Sample:** {n} usable responses ({n0} received; {R['n_removed_straightliners']} straight-liners removed).", "",
          "## Reliability", "| Scale | Index | Value |", "|---|---|---|"]
    for k, val in rel.items():
        L.append(f"| {k} | {'Cronbach alpha' if k == 'Engagement' else 'Spearman-Brown (2 items)'} | {val:.2f} |")
    L += ["", f"## Factorability\nKMO = {kmo:.2f}; Bartlett's test p = {bp:.3g}; "
              f"Kaiser criterion suggests {n_f} factors (6 expected).", "",
          "## Regression: drivers of engagement",
          f"R² = {m['r2']:.2f} (adj. {m['adj_r2']:.2f}), F({len(DRIVERS)}, {m['dof']}) = {m['F']:.1f}, "
          f"p = {m['F_p']:.3g}. Max VIF = {v.max():.2f}.", "",
          "| Driver | Std. beta | 95% CI | p | Unique R² | Ranked #1 (bootstrap) |", "|---|---|---|---|---|---|"]
    for _, r_ in reg.iterrows():
        L.append(f"| {r_.driver} | {r_.std_beta:.2f} {r_.sig} | [{r_.ci_low:.2f}, {r_.ci_high:.2f}] | "
                 f"{fp(r_.p)} | {r_.unique_R2:.3f} | {r_['pct_boot_ranked_#1']:.0%} |")
    L += ["", "## Hypotheses (stated before analysis)"]
    for k, h in H.items():
        L.append(f"- **{k}** {h['text']}: **{'Supported' if h['supported'] else 'Not supported'}**. {h['result']}.")
    L += ["", "## Limitations to state in any write-up",
          "- Cross-sectional, self-report data: associations, not causes.",
          "- Convenience sample; results do not generalise to all workers.",
          "- Two items per driver keeps the survey short but limits reliability and EFA stability."]
    open(f"{outdir}/results_summary.md", "w").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/DEMO_synthetic_responses.csv")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or ("outputs/demo" if "DEMO" in a.data.upper() else "outputs/real")
    main(a.data, out)

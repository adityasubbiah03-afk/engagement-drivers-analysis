"""Generate a SYNTHETIC demo dataset so the pipeline can be run end-to-end
before real survey responses are collected.

!! The output is simulated. Never report its findings as real results. !!
Replace data/DEMO_synthetic_responses.csv with data/responses.csv from your real survey.
"""
import numpy as np, pandas as pd

rng = np.random.default_rng(42)
N = 120

# Latent driver perceptions (mildly correlated)
names = ["mgr", "rec", "wl", "gro", "aut", "team"]
corr = np.full((6, 6), 0.30) + 0.70 * np.eye(6)
Z = rng.multivariate_normal(np.zeros(6), corr, size=N)

# Assumed "true" effects used only to simulate the demo data
w = np.array([0.40, 0.20, 0.25, 0.20, 0.08, 0.10])
eng_latent = Z @ w + rng.normal(0, 0.55, N)

def likert(latent, noise=0.55, spread=0.85):
    x = 3.4 + spread * (latent + rng.normal(0, noise, len(latent)))
    return np.clip(np.round(x), 1, 5).astype(int)

df = pd.DataFrame()
for i, n in enumerate(names):
    for k in (1, 2):
        df[f"{n}{k}"] = likert(Z[:, i])
for k in (1, 2, 3):
    df[f"eng{k}"] = likert(eng_latent, noise=0.35, spread=1.0)

df["tenure"] = rng.choice(["<1 year", "1-3 years", "3+ years"], N, p=[.25, .45, .30])
df["arrangement"] = rng.choice(["On-site", "Hybrid", "Remote"], N, p=[.30, .50, .20])
df["level"] = rng.choice(["Individual contributor", "Team lead / manager"], N, p=[.75, .25])

df.to_csv("data/DEMO_synthetic_responses.csv", index=False)
print(df.shape, "-> data/DEMO_synthetic_responses.csv")

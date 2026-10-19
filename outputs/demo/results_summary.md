# Results summary [DEMO - SYNTHETIC DATA]

> **This run used SIMULATED data. The numbers below demonstrate the pipeline only and must not be reported as findings.**

**Sample:** 120 usable responses (120 received; 0 straight-liners removed).

## Reliability
| Scale | Index | Value |
|---|---|---|
| Manager support | Spearman-Brown (2 items) | 0.89 |
| Recognition | Spearman-Brown (2 items) | 0.83 |
| Workload | Spearman-Brown (2 items) | 0.81 |
| Growth | Spearman-Brown (2 items) | 0.79 |
| Autonomy | Spearman-Brown (2 items) | 0.81 |
| Team belonging | Spearman-Brown (2 items) | 0.80 |
| Engagement | Cronbach alpha | 0.93 |

## Factorability
KMO = 0.73; Bartlett's test p = 2.43e-94; Kaiser criterion suggests 5 factors (6 expected).

## Regression: drivers of engagement
R² = 0.61 (adj. 0.59), F(6, 113) = 29.4, p = 5.4e-21. Max VIF = 1.50.

| Driver | Std. beta | 95% CI | p | Unique R² | Ranked #1 (bootstrap) |
|---|---|---|---|---|---|
| Manager support | 0.41 *** | [0.27, 0.55] | <.001 | 0.121 | 89% |
| Growth | 0.26 *** | [0.13, 0.39] | <.001 | 0.051 | 9% |
| Workload | 0.20 ** | [0.07, 0.32] | 0.003 | 0.032 | 1% |
| Team belonging | 0.15 * | [0.01, 0.30] | 0.035 | 0.016 | 0% |
| Recognition | 0.06 ns | [-0.07, 0.19] | 0.386 | 0.003 | 0% |
| Autonomy | 0.05 ns | [-0.09, 0.20] | 0.444 | 0.002 | 0% |

## Hypotheses (stated before analysis)
- **H1** Manager support is the strongest driver of engagement: **Supported**. Top driver = Manager support (beta=0.41); ranked #1 in 89% of bootstrap samples.
- **H2** Manageable workload positively predicts engagement, controlling for other drivers: **Supported**. beta=0.20, 95% CI [0.07, 0.32], p=0.003.
- **H3** Engagement differs by work arrangement (on-site / hybrid / remote): **Not supported**. ANOVA F=0.30, p=0.741; Kruskal-Wallis p=0.722; eta^2=0.005.

## Limitations to state in any write-up
- Cross-sectional, self-report data: associations, not causes.
- Convenience sample; results do not generalise to all workers.
- Two items per driver keeps the survey short but limits reliability and EFA stability.
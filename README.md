# What Drives Employee Engagement? A Survey-Based Driver Analysis

A small end-to-end research project: design a survey, test pre-stated hypotheses, and turn the findings into client-style recommendations. Built to demonstrate research design, workplace analytics and hypothesis-led analysis.

> **Status:** pipeline built and tested on **synthetic demo data** (`data/DEMO_synthetic_responses.csv`). Real survey results go in `outputs/real/` once collected. The demo numbers are not findings.

## Research question
Which workplace factors (manager support, recognition, workload, growth, autonomy, team belonging) best predict employee engagement, and does engagement differ by work arrangement?

## Method
1. **Survey design**: 12 driver items (2 per driver) + 3 engagement outcome items, 5-point Likert; see `docs/survey_instrument.md`.
2. **Data quality**: remove incomplete responses and straight-liners.
3. **Reliability**: Spearman-Brown for 2-item scales, Cronbach's alpha for the 3-item outcome.
4. **Construct validity**: KMO, Bartlett's test, scree plot, exploratory factor analysis (varimax).
5. **Driver analysis**: multiple regression on standardised scale scores with 95% CIs, VIF checks, unique R², plus a 2,000-sample bootstrap to test whether the driver ranking is stable.
6. **Hypothesis tests**: H1-H3 stated before analysis; ANOVA with Kruskal-Wallis robustness check and eta².

## Run it
```bash
pip install pandas numpy scipy scikit-learn matplotlib
python generate_demo_data.py                      # optional: synthetic demo data
python analysis.py                                # demo run -> outputs/demo/
python analysis.py --data data/responses.csv      # real run -> outputs/real/
```
Outputs: `results_summary.md`, `results.json`, regression/correlation/EFA CSVs, and four charts.

## Repo structure
```
analysis.py               full pipeline
generate_demo_data.py     synthetic data (pipeline testing only)
data/                     responses go here
docs/survey_instrument.md questionnaire, codebook, hypotheses, ethics
outputs/demo/             example outputs from synthetic data
```

## Limitations
Cross-sectional self-report data shows association, not causation. A convenience sample limits generalisability. Two items per driver keeps the survey short but limits reliability and EFA stability.

## Relationship to Gallup's work
The driver framing is informed by publicly available engagement research (e.g. Gallup's published Q12 and State of the Global Workplace reports). This project is independent and is not affiliated with Gallup or its methodology.

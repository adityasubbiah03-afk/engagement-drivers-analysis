# Employee Engagement Survey (instrument + codebook)

**Build it in Google Forms or Microsoft Forms. Target: 60-120 responses, 3 minutes to complete.**

## Intro text (paste at the top of the form)
> This anonymous 3-minute survey is part of a university data analytics project on what makes people feel engaged at work. No names, employers or emails are collected. Participation is voluntary and you can stop at any time. Results will only be reported in aggregate. Please answer based on your **current or most recent job** (paid work, including part-time or casual).

Eligibility screen (first question, end form if "No"): *Are you 18+ and currently in, or have you had in the last 6 months, paid work?*

## Scale for all statements
1 = Strongly disagree, 2 = Disagree, 3 = Neutral, 4 = Agree, 5 = Strongly agree

## Items (randomise order within the form to reduce order effects)

| Code | Driver | Statement |
|---|---|---|
| mgr1 | Manager support | My manager genuinely cares about me as a person. |
| mgr2 | Manager support | I can rely on my manager for help when I need it. |
| rec1 | Recognition | I receive appropriate recognition when I do good work. |
| rec2 | Recognition | My contributions are noticed and valued by others. |
| wl1 | Workload | My workload is manageable within my normal working hours. |
| wl2 | Workload | I rarely feel overwhelmed by what is expected of me. |
| gro1 | Growth | I have opportunities to learn and develop new skills. |
| gro2 | Growth | I can see a clear path for my development here. |
| aut1 | Autonomy | I have a say in how I do my work. |
| aut2 | Autonomy | I am trusted to make decisions in my role. |
| team1 | Team belonging | I feel like I belong in my team. |
| team2 | Team belonging | People in my team support each other. |
| eng1 | **Outcome: engagement** | I am enthusiastic about my work. |
| eng2 | **Outcome: engagement** | I would recommend my workplace to a friend. |
| eng3 | **Outcome: engagement** | I see myself still working here in 12 months. |

All items are positively worded, so no reverse-coding is needed. (Workload items are worded as "manageable", so a higher score means a better experience.)

## Demographics (single-choice, optional wording below)
| Code | Question | Options |
|---|---|---|
| tenure | How long have you been in this role? | <1 year / 1-3 years / 3+ years |
| arrangement | Where do you mainly work? | On-site / Hybrid / Remote |
| level | Which best describes your role? | Individual contributor / Team lead / manager |

## Pre-stated hypotheses (write these in your repo BEFORE collecting data)
- **H1:** Manager support is the strongest driver of engagement.
- **H2:** Manageable workload positively predicts engagement, controlling for other drivers.
- **H3:** Engagement differs by work arrangement.

Committing these before you look at responses is what makes this *hypothesis-led* research rather than fishing. Make a git commit of this file with a timestamp.

## Export
Export responses as CSV with exactly the column codes above (rename headers), save as `data/responses.csv`, then run `python analysis.py --data data/responses.csv`.

## Ethics and good practice
- Keep it anonymous; do not collect identifying information.
- Do not recruit from your current employer's internal channels without permission.
- Report your sample as a convenience sample and say so.

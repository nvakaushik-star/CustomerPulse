# CustomerPulse

**B2B SaaS Customer Health & Churn Risk Analytics**

CustomerPulse is a customer-health analytics solution for B2B SaaS teams. It combines product engagement, billing, support activity, customer sentiment and revenue signals to identify at-risk accounts, quantify revenue exposure and help Customer Success teams decide where to act first.

> **Product question:** With tens of thousands of customer accounts, how can a Customer Success Manager quickly identify which accounts need attention, understand why they are risky and prioritize interventions that protect revenue?

## Why this project

I built CustomerPulse to practice the kind of product and customer analytics work used in subscription-based technology businesses. The project is designed around a real operational problem: a Customer Success Manager cannot manually inspect thousands of accounts across usage, support, sentiment and revenue metrics every day.

The goal is therefore not only to report churn. It is to turn account-level behavior into a practical **decision-support workflow**:

**Portfolio health → risk detection → risk explanation → account prioritization → retention action**

## Dataset

The project uses the **Kaggle B2B SaaS Account Health Dataset**, a synthetic dataset designed to represent realistic B2B SaaS account behavior.

Source: https://www.kaggle.com/datasets/akshankrithick/b2b-saas-account-health-dataset

The working dataset contains **50,000 accounts** and includes product usage, support, satisfaction, contract, billing and revenue variables.

> The raw CSV is not committed to this repository. See [`data/README.md`](data/README.md) for setup instructions.

## Business KPIs

Baseline portfolio metrics identified during exploratory analysis:

| KPI | Result |
|---|---:|
| Total accounts | 50,000 |
| Monthly revenue | ~$56.4M |
| 90-day churn rate | 9.53% |
| Strict rule-based risk accounts | 2,225 |
| Revenue at risk* | ~$113.7K / month |

\*Revenue-at-risk uses unique accounts across the strict risk population and high-value risk population in the MVP business rules.

## Risk logic

The current MVP is **rule-based**, not an ML churn probability model.

A **strict risk account** is defined as an account with:

- seat utilization below 30%
- feature adoption below 30%
- at least 3 support tickets in the last 30 days

A **high-value risk account** is an active account with:

- monthly revenue above $1,000
- seat utilization below 30%
- feature adoption below 30%

A wider **high-value watchlist** captures active accounts above $1,000 monthly revenue that show at least one major warning signal.

## Priority scoring

Not every risky account deserves the same level of urgency. CustomerPulse therefore creates an explainable **rule-based priority score** for strict-risk accounts.

| Component | Weight |
|---|---:|
| Revenue exposure | 30% |
| Seat-utilization weakness | 25% |
| Feature-adoption weakness | 25% |
| Support burden | 15% |
| Customer sentiment weakness | 5% |

The underlying metrics are normalized to a comparable 0–100 scale before weighting. Engagement and revenue jointly carry the largest weight because the analysis showed persistent engagement weakness among high-value risky accounts.

## Key findings

Early analysis showed clear behavioral differences between retained and churned accounts:

- churned accounts had materially lower seat utilization
- churned accounts had materially lower feature adoption
- churned accounts raised more support tickets on average
- churned accounts had lower NPS and CSAT scores
- monthly contracts dominated the broad risk population by account count
- high-revenue risky accounts showed a different mix, including several annual and multi-year contracts

This distinction matters: **segment-level risk concentration and account-level business priority are not the same thing.**

## Dashboard

The Streamlit application provides:

- executive KPI cards
- interactive filters for region, industry, contract type, billing plan, health segment and revenue
- normalized risk-rate views by contract, billing plan, region and industry
- retained-vs-churned behavioral comparison
- prioritized risk-account table
- high-value watchlist
- account explorer
- transparent definitions of the business rules used

Run the app locally with:

```bash
python -m streamlit run app.py
```

## Project structure

```text
CustomerPulse/
├── app.py                      # Streamlit dashboard
├── notebooks/
│   └── CustomerPulse.ipynb     # EDA, segmentation and scoring analysis
├── data/
│   └── README.md               # Dataset setup instructions
├── requirements.txt
├── .gitignore
└── README.md
```

## Tech stack

**Python · Pandas · NumPy · Jupyter Notebook · Matplotlib · Streamlit · Git · GitHub**

Planned/next-stage work includes SQL/BigQuery integration and supervised machine-learning experiments for churn prediction.

## Current limitations

- The dataset is synthetic, so findings demonstrate analytical workflow rather than production customer behavior.
- The current risk and priority scores use explicit business rules and manually chosen weights.
- The source data is cross-sectional; it does not provide a true historical time series for every account, so trend analysis should not be fabricated from the current snapshot.
- Risk thresholds and scoring weights should be validated against business outcomes before production use.

## Product roadmap

The next iteration focuses on turning the dashboard from reporting into a stronger decision-support product:

1. **Risk-reason segmentation** — classify accounts by the behavior driving risk.
2. **Account drill-down** — show why an account is prioritized and what signals are weak.
3. **Action recommendations** — connect risk patterns to suggested Customer Success interventions.
4. **Machine learning** — compare rule-based prioritization with a supervised churn-classification model.
5. **Model explainability** — surface feature importance / churn probability without hiding the business logic.
6. **Production data layer** — move from local CSV to a managed warehouse or application data source.

## Business value

CustomerPulse is designed around one practical outcome:

> **Help Customer Success teams act earlier on the right accounts, reduce manual investigation and protect recurring revenue.**

---

### Author

**Koushik Nimmagadda**  
Product / Customer Analytics portfolio project

# Data

CustomerPulse uses the **B2B SaaS Account Health Dataset** published on Kaggle by Akshan Krithick.

Dataset page: https://www.kaggle.com/datasets/akshankrithick/b2b-saas-account-health-dataset

The dataset is synthetic and is used here for educational and portfolio analysis.

## Local setup

1. Download the dataset from Kaggle.
2. Rename the working CSV to `saas_accounts.csv` if necessary.
3. Place it in the project root next to `app.py`.
4. Run:

```bash
python -m streamlit run app.py
```

The raw CSV is intentionally excluded from version control. This keeps the repository lightweight and makes the original dataset source explicit.

## Important fields used by CustomerPulse

The analysis uses fields covering billing and contracts, industry and region, seat utilization, feature adoption, product usage, support demand, customer sentiment, revenue, churn outcome and health segment.

See the notebook for exploratory analysis and the Streamlit application for the operational risk rules.

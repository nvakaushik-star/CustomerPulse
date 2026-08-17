import streamlit as st
import pandas as pd
from pathlib import Path


# PAGE SETUP
st.set_page_config(
    page_title="CustomerPulse",
    page_icon="📊",
    layout="wide"
)


# LOAD DATA
base_dir = Path(__file__).resolve().parent
csv_path = base_dir / "saas_accounts.csv"

df = pd.read_csv(csv_path)

# Seat utilization is stored as a decimal in the source data.
df["seat_utilization_pct"] = df["seat_utilization"] * 100

# Simple row number so the tables are easier to discuss in the presentation.
df["account_no"] = df.index + 1


# TITLE
st.title("CustomerPulse")
st.write(
    "Customer health and revenue risk dashboard for identifying accounts "
    "that may need attention before churn."
)


# SIDEBAR
st.sidebar.header("Filters")

region = st.sidebar.selectbox(
    "Region",
    ["All"] + sorted(df["region"].dropna().unique().tolist())
)

industries = st.sidebar.multiselect(
    "Industry",
    sorted(df["industry"].dropna().unique().tolist())
)

contract_types = st.sidebar.multiselect(
    "Contract Type",
    sorted(df["contract_type"].dropna().unique().tolist())
)

billing_plans = st.sidebar.multiselect(
    "Billing Plan",
    sorted(df["billing_plan"].dropna().unique().tolist())
)

health_segments = st.sidebar.multiselect(
    "Health Segment",
    sorted(df["health_segment"].dropna().unique().tolist())
)

revenue_min = float(df["monthly_revenue"].min())
revenue_max = float(df["monthly_revenue"].max())

revenue_range = st.sidebar.slider(
    "Monthly Revenue Range",
    min_value=revenue_min,
    max_value=revenue_max,
    value=(revenue_min, revenue_max),
    step=50.0
)


# FILTER DATA
filtered_df = df.copy()

if region != "All":
    filtered_df = filtered_df[filtered_df["region"] == region]

if industries:
    filtered_df = filtered_df[filtered_df["industry"].isin(industries)]

if contract_types:
    filtered_df = filtered_df[filtered_df["contract_type"].isin(contract_types)]

if billing_plans:
    filtered_df = filtered_df[filtered_df["billing_plan"].isin(billing_plans)]

if health_segments:
    filtered_df = filtered_df[filtered_df["health_segment"].isin(health_segments)]

filtered_df = filtered_df[
    filtered_df["monthly_revenue"].between(revenue_range[0], revenue_range[1])
]

if filtered_df.empty:
    st.warning("No accounts match the selected filters.")
    st.stop()


# CORE CALCULATIONS
total_accounts = len(filtered_df)
total_monthly_revenue = filtered_df["monthly_revenue"].sum()
churn_rate = filtered_df["churned_90d"].mean() * 100
avg_seat_utilization = filtered_df["seat_utilization"].mean() * 100
avg_feature_adoption = filtered_df["feature_adoption_pct"].mean()

risk_accounts = filtered_df.loc[
    (filtered_df["seat_utilization"] < 0.30)
    & (filtered_df["feature_adoption_pct"] < 30)
    & (filtered_df["support_tickets_30d"] >= 3)
].copy()

high_value_risk = filtered_df.loc[
    (filtered_df["churned_90d"] == 0)
    & (filtered_df["monthly_revenue"] > 1000)
    & (filtered_df["seat_utilization"] < 0.30)
    & (filtered_df["feature_adoption_pct"] < 30)
].copy()

high_value_watchlist = filtered_df.loc[
    (filtered_df["churned_90d"] == 0)
    & (filtered_df["monthly_revenue"] > 1000)
    & (
        (filtered_df["seat_utilization"] < 0.30)
        | (filtered_df["feature_adoption_pct"] < 30)
        | (filtered_df["support_tickets_30d"] >= 3)
    )
].copy()

revenue_risk_index = risk_accounts.index.union(high_value_risk.index)
revenue_at_risk = filtered_df.loc[revenue_risk_index, "monthly_revenue"].sum()
revenue_at_risk_pct = (
    revenue_at_risk / total_monthly_revenue * 100
    if total_monthly_revenue > 0 else 0
)


# KPI ROW
st.header("Executive Overview")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Accounts", f"{total_accounts:,}")
col2.metric("Monthly Revenue", f"${total_monthly_revenue:,.0f}")
col3.metric("Risk Accounts", f"{len(risk_accounts):,}")
col4.metric("Revenue at Risk", f"${revenue_at_risk:,.0f}")
col5.metric("Revenue at Risk %", f"{revenue_at_risk_pct:.1f}%")

col6, col7, col8, col9 = st.columns(4)
col6.metric("Churn Rate", f"{churn_rate:.1f}%")
col7.metric("Avg Seat Utilization", f"{avg_seat_utilization:.1f}%")
col8.metric("Avg Feature Adoption", f"{avg_feature_adoption:.1f}%")
col9.metric("High-Value Watchlist", f"{len(high_value_watchlist):,}")


# RISK PROFILE
st.header("Where is the risk?")
risk_view = filtered_df.copy()
risk_view["risk_account"] = risk_view.index.isin(risk_accounts.index).astype(int)

chart1, chart2 = st.columns(2)
with chart1:
    contract_risk = risk_view.groupby("contract_type").agg(
        total_accounts=("contract_type", "count"),
        risk_accounts=("risk_account", "sum")
    )
    contract_risk["risk_rate_pct"] = (
        contract_risk["risk_accounts"] / contract_risk["total_accounts"] * 100
    )
    st.subheader("Risk Rate by Contract Type")
    st.bar_chart(contract_risk["risk_rate_pct"].sort_values(ascending=False))

with chart2:
    billing_risk = risk_view.groupby("billing_plan").agg(
        total_accounts=("billing_plan", "count"),
        risk_accounts=("risk_account", "sum")
    )
    billing_risk["risk_rate_pct"] = (
        billing_risk["risk_accounts"] / billing_risk["total_accounts"] * 100
    )
    st.subheader("Risk Rate by Billing Plan")
    st.bar_chart(billing_risk["risk_rate_pct"].sort_values(ascending=False))

chart3, chart4 = st.columns(2)
with chart3:
    region_risk = risk_view.groupby("region").agg(
        total_accounts=("region", "count"),
        risk_accounts=("risk_account", "sum")
    )
    region_risk["risk_rate_pct"] = (
        region_risk["risk_accounts"] / region_risk["total_accounts"] * 100
    )
    st.subheader("Risk Rate by Region")
    st.bar_chart(region_risk["risk_rate_pct"].sort_values(ascending=False))

with chart4:
    industry_risk = risk_view.groupby("industry").agg(
        total_accounts=("industry", "count"),
        risk_accounts=("risk_account", "sum")
    )
    industry_risk["risk_rate_pct"] = (
        industry_risk["risk_accounts"] / industry_risk["total_accounts"] * 100
    )
    st.subheader("Risk Rate by Industry")
    st.bar_chart(industry_risk["risk_rate_pct"].sort_values(ascending=False))


# CHURN SIGNALS
st.header("Churn Signals")
churn_comparison = filtered_df.groupby("churned_90d").agg(
    avg_seat_utilization=("seat_utilization_pct", "mean"),
    avg_feature_adoption=("feature_adoption_pct", "mean"),
    avg_support_tickets=("support_tickets_30d", "mean"),
    avg_nps=("nps_score", "mean"),
    avg_csat=("csat_score", "mean")
).round(2)
churn_comparison.index = churn_comparison.index.map({0: "Retained", 1: "Churned"})
st.dataframe(churn_comparison, use_container_width=True)
st.caption(
    "This compares engagement, support demand and satisfaction "
    "between retained and churned accounts."
)


# PRIORITY SCORE FOR STRICT RISK ACCOUNTS
st.header("Priority Risk Accounts")
if not risk_accounts.empty:
    def score(series, reverse=False):
        minimum = series.min()
        maximum = series.max()
        if maximum == minimum:
            result = pd.Series(50.0, index=series.index)
        else:
            result = (series - minimum) / (maximum - minimum) * 100
        if reverse:
            result = 100 - result
        return result

    risk_accounts["revenue_score"] = score(risk_accounts["monthly_revenue"])
    risk_accounts["seat_weakness_score"] = score(
        risk_accounts["seat_utilization"], reverse=True
    )
    risk_accounts["feature_weakness_score"] = score(
        risk_accounts["feature_adoption_pct"], reverse=True
    )
    risk_accounts["support_score"] = score(risk_accounts["support_tickets_30d"])
    nps_weakness = score(risk_accounts["nps_score"], reverse=True)
    csat_weakness = score(risk_accounts["csat_score"], reverse=True)
    risk_accounts["sentiment_score"] = (nps_weakness + csat_weakness) / 2

    risk_accounts["priority_score"] = (
        risk_accounts["revenue_score"] * 0.30
        + risk_accounts["seat_weakness_score"] * 0.25
        + risk_accounts["feature_weakness_score"] * 0.25
        + risk_accounts["support_score"] * 0.15
        + risk_accounts["sentiment_score"] * 0.05
    ).round(2)

    priority_table = risk_accounts[[
        "account_no", "region", "industry", "billing_plan", "contract_type",
        "monthly_revenue", "seat_utilization_pct", "feature_adoption_pct",
        "support_tickets_30d", "nps_score", "csat_score", "priority_score"
    ]].sort_values("priority_score", ascending=False)

    priority_table = priority_table.rename(columns={
        "account_no": "Account #",
        "region": "Region",
        "industry": "Industry",
        "billing_plan": "Billing Plan",
        "contract_type": "Contract Type",
        "monthly_revenue": "Monthly Revenue",
        "seat_utilization_pct": "Seat Utilization %",
        "feature_adoption_pct": "Feature Adoption %",
        "support_tickets_30d": "Support Tickets",
        "nps_score": "NPS",
        "csat_score": "CSAT",
        "priority_score": "Priority Score"
    })
    st.dataframe(priority_table.head(25), use_container_width=True, hide_index=True)
else:
    st.info("No strict risk accounts match the selected filters.")


# HIGH-VALUE WATCHLIST
st.header("High-Value Watchlist")
if not high_value_watchlist.empty:
    watchlist_table = high_value_watchlist[[
        "account_no", "region", "industry", "billing_plan", "contract_type",
        "monthly_revenue", "seat_utilization_pct", "feature_adoption_pct",
        "support_tickets_30d", "nps_score", "csat_score"
    ]].sort_values("monthly_revenue", ascending=False)

    watchlist_table = watchlist_table.rename(columns={
        "account_no": "Account #",
        "region": "Region",
        "industry": "Industry",
        "billing_plan": "Billing Plan",
        "contract_type": "Contract Type",
        "monthly_revenue": "Monthly Revenue",
        "seat_utilization_pct": "Seat Utilization %",
        "feature_adoption_pct": "Feature Adoption %",
        "support_tickets_30d": "Support Tickets",
        "nps_score": "NPS",
        "csat_score": "CSAT"
    })
    st.dataframe(watchlist_table.head(25), use_container_width=True, hide_index=True)
else:
    st.info("No high-value watchlist accounts match the selected filters.")


# ACCOUNT EXPLORER
with st.expander("Account Explorer"):
    columns_to_show = [
        "account_no", "billing_plan", "contract_type", "industry", "region",
        "seats_purchased", "monthly_active_users", "seat_utilization_pct",
        "feature_adoption_pct", "support_tickets_30d", "escalated_tickets_30d",
        "nps_score", "csat_score", "monthly_revenue", "expansion_revenue_pct",
        "churned_90d", "next_month_revenue", "health_segment"
    ]
    st.write(f"Showing {len(filtered_df):,} accounts")
    st.dataframe(
        filtered_df[columns_to_show], use_container_width=True, hide_index=True
    )


# BUSINESS RULES
with st.expander("How risk is defined"):
    st.write(
        "**Strict risk account:** seat utilization below 30%, feature adoption "
        "below 30%, and at least 3 support tickets in the last 30 days."
    )
    st.write(
        "**High-value risk:** an account that has not churned, has more than "
        "$1,000 monthly revenue, seat utilization below 30%, and feature "
        "adoption below 30%."
    )
    st.write(
        "**High-value watchlist:** an account that has not churned, has more "
        "than $1,000 monthly revenue, and shows at least one warning signal."
    )

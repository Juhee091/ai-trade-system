import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import date, timedelta

st.set_page_config(page_title="Trade Risk Dashboard", layout="wide")
st.title("Trade Risk Dashboard")
st.markdown("This dashboard combines individual route risk alerts with a global heatmap overview.")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("tariff_prices_with_currency_codes.csv")

df = load_data()

# ------------------ Section 1: Individual Route Risk Alert ------------------
st.header("🚨 Individual Trade Route Risk Alert")

selected_row = st.selectbox(
    "Select a trade route to analyze:",
    df.index,
    format_func=lambda i: f"{df.loc[i, 'export_country']} → {df.loc[i, 'import_country']} ({df.loc[i, 'product']})"
)
row = df.loc[selected_row]

TARIFF_THRESHOLD = 10.0
EXCHANGE_VOLATILITY_THRESHOLD = 5.0  # %

# Exchange volatility check
def get_exchange_volatility(to_currency):
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        url = f"https://api.exchangerate.host/timeseries?start_date={start_date}&end_date={end_date}&base=USD&symbols={to_currency}"
        res = requests.get(url)
        data = res.json()
        if "rates" not in data or not data["rates"]:
            return 0, False

        rates = [v[to_currency] for v in data["rates"].values() if to_currency in v]
        if not rates:
            return 0, False

        avg = sum(rates) / len(rates)

        current_url = f"https://api.exchangerate.host/latest?base=USD&symbols={to_currency}"
        current = requests.get(current_url).json()["rates"].get(to_currency)
        if not current:
            return 0, False

        diff = abs(current - avg) / avg * 100
        return round(diff, 2), diff > EXCHANGE_VOLATILITY_THRESHOLD

    except Exception as e:
        st.warning(f"⚠️ Failed to fetch exchange rate data: {e}")
        return 0, False

tariff_risk = row["tariff_rate"] > TARIFF_THRESHOLD
exchange_diff, exchange_risk = get_exchange_volatility(row["import_currency"])

# Risk display
col1, col2 = st.columns(2)

with col1:
    if tariff_risk:
        st.error(f"🔴 High Tariff Risk: {row['tariff_rate']}% (Threshold: {TARIFF_THRESHOLD}%)")
    else:
        st.success(f"✅ Tariff is within safe range: {row['tariff_rate']}%")

with col2:
    if exchange_risk:
        st.warning(f"🟠 Exchange Volatility Detected: {exchange_diff}% deviation from 30-day average")
    else:
        st.info(f"ℹ️ Exchange Rate Stable: {exchange_diff}% difference")

# ------------------ Section 2: Global Risk Heatmap ------------------
st.header("Global Trade Route Risk Heatmap")

def calculate_risk_score(row, tariff_threshold=10.0, exchange_threshold=5.0):
    tariff_score = 1 if row["tariff_rate"] > tariff_threshold else 0
    volatility = abs(row.get("exchange_rate_usd_to_local", 1300) - 1300) / 1300 * 100
    exchange_score = 1 if volatility > exchange_threshold else 0
    return tariff_score + exchange_score

df["risk_score"] = df.apply(calculate_risk_score, axis=1)

top_exports = df["export_country"].value_counts().head(10).index
top_imports = df["import_country"].value_counts().head(10).index
filtered = df[df["export_country"].isin(top_exports) & df["import_country"].isin(top_imports)]

pivot = filtered.pivot_table(
    index="export_country",
    columns="import_country",
    values="risk_score",
    aggfunc="mean"
).fillna(0)

fig = go.Figure(data=go.Heatmap(
    z=pivot.values,
    x=pivot.columns,
    y=pivot.index,
    colorscale='Reds',
    colorbar=dict(title="Risk Score")
))
fig.update_layout(
    title="Risk Heatmap (Top 10 Export/Import Countries)",
    xaxis_title="Import Country",
    yaxis_title="Export Country"
)

st.plotly_chart(fig, use_container_width=True)

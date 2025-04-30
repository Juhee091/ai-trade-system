import streamlit as st
import pandas as pd
import requests

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("tariff_prices_with_currency_codes.csv")

df = load_data()

st.title("🚨 Trade Risk Alert System")
st.markdown("This tool highlights potential trade risks based on tariff rate and exchange rate volatility.")

# User selection
selected_row = st.selectbox("Select a trade route:", df.index, format_func=lambda i: f"{df.loc[i, 'export_country']} → {df.loc[i, 'import_country']} ({df.loc[i, 'product']})")
row = df.loc[selected_row]

# Risk thresholds
TARIFF_THRESHOLD = 10.0
EXCHANGE_VOLATILITY_THRESHOLD = 100

# Tariff risk analysis
tariff_risk = row['tariff_rate'] > TARIFF_THRESHOLD

# Exchange rate volatility check (1달 평균 대비 현재 환율 차이 비교)
def get_exchange_volatility(to_currency):
    url = f"https://api.exchangerate.host/timeseries?start_date=2023-12-01&end_date=2024-01-01&base=USD&symbols={to_currency}"
    res = requests.get(url)
    data = res.json()
    rates = [v[to_currency] for v in data['rates'].values() if to_currency in v]
    if not rates:
        return 0, False
    avg = sum(rates) / len(rates)
    current_url = f"https://api.exchangerate.host/latest?base=USD&symbols={to_currency}"
    current = requests.get(current_url).json()['rates'][to_currency]
    diff = abs(current - avg) * 100
    return round(diff, 2), diff > EXCHANGE_VOLATILITY_THRESHOLD

# Run analysis
exchange_diff, exchange_risk = get_exchange_volatility(row['import_currency'])

# Display results
st.subheader("Risk Evaluation")

if tariff_risk:
    st.error(f"🔴 High Tariff Risk: {row['tariff_rate']}% (Threshold = {TARIFF_THRESHOLD}%)")
else:
    st.success(f"✅ Tariff within acceptable range: {row['tariff_rate']}%")

if exchange_risk:
    st.warning(f"🟠 Exchange Rate Volatility Detected: {exchange_diff}% difference from 1-month average")
else:
    st.info(f"ℹ️ Exchange Rate Stable: {exchange_diff}% variation")

import streamlit as st
import pandas as pd
import requests

# Load data
st.title("Tariff Price Converter with Real-Time Exchange Rates")
df = pd.read_csv("tariff_prices_with_currency_codes.csv")

# Supported currencies
supported_currencies = sorted(list(set([
    "USD", "EUR", "KRW", "JPY", "CNY", "INR", "AUD", "CAD", "CHF",
    "BRL", "MXN", "VND", "THB", "ZAR", "PLN", "TRY", "AED", "SAR"
])))

# Currency selection
selected_currency = st.selectbox("Select the currency to convert to:", supported_currencies)

# Get exchange rate function
@st.cache_data
def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    if from_currency == to_currency:
        return 1.0
    url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["result"]
    return None

# Apply exchange rate
rate = get_exchange_rate("USD", selected_currency)
df[f"final_price_in_{selected_currency}"] = df["final_price_usd"] * rate

# Display results
st.markdown(f"### Current Exchange Rate\n1 USD = {rate:.2f} {selected_currency}")
st.dataframe(df[[
    "import_country", "product", "final_price_usd", f"final_price_in_{selected_currency}"
]])

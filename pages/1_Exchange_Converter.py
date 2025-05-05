import streamlit as st
import pandas as pd
import requests

# Load data
st.set_page_config(page_title="Exchange Converter", layout="centered")
st.title("💱 Exchange Rate Converter (Free API)")
st.markdown("Convert product prices using free real-time exchange rates from Frankfurter API.")

# Load CSV
df = pd.read_csv("tariff_prices_with_currency_codes.csv")

# Supported currencies
supported_currencies = sorted(list(set([
    "USD", "EUR", "KRW", "JPY", "CNY", "INR", "AUD", "CAD", "CHF",
    "BRL", "MXN", "VND", "THB", "ZAR", "PLN", "TRY", "AED", "SAR"
])))

# User selection
selected_currency = st.selectbox("Select the currency to convert to:", supported_currencies)

# Frankfurter API
@st.cache_data
def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    if from_currency == to_currency:
        return 1.0
    url = f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return data["rates"][to_currency]
    except Exception:
        return None

# Apply rate
rate = get_exchange_rate("USD", selected_currency)

if rate is None:
    st.error("⚠️ Failed to fetch exchange rate. Please try again later.")
else:
    df[f"final_price_in_{selected_currency}"] = (df["final_price_usd"] * rate).round(2)
    st.markdown(f"### Current Exchange Rate\n1 USD = {rate:.2f} {selected_currency}")
    st.dataframe(df[[
        "import_country", "product", "final_price_usd", f"final_price_in_{selected_currency}"
    ]])

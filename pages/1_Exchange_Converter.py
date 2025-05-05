import streamlit as st
import requests

st.set_page_config(page_title="Exchange Converter", layout="centered")
st.title("Exchange Converter")

# Currency options (supported by Frankfurter)
currencies = sorted([
    "USD", "EUR", "KRW", "JPY", "CNY", "INR", "AUD", "CAD", "CHF",
    "BRL", "MXN", "VND", "THB", "ZAR", "PLN", "TRY", "AED", "SAR"
])

from_currency = st.selectbox("From Currency", currencies, index=currencies.index("USD"))
to_currency = st.selectbox("To Currency", currencies, index=currencies.index("KRW"))
amount = st.number_input("Amount", min_value=0.0, value=100.0, step=10.0)

# API call
def get_rate(from_curr, to_curr):
    if from_curr == to_curr:
        return 1.0
    url = f"https://api.frankfurter.app/latest?from={from_curr}&to={to_curr}"
    try:
        response = requests.get(url, timeout=5)
        return response.json()["rates"][to_curr]
    except:
        return None

rate = get_rate(from_currency, to_currency)

# Output
if rate is None:
    st.error("⚠️ Failed to fetch exchange rate. Please try again later.")
else:
    converted = amount * rate
    st.success(f"{amount:,.2f} {from_currency} = {converted:,.2f} {to_currency}")
    st.caption(f"Exchange rate: 1 {from_currency} = {rate:.4f} {to_currency}")

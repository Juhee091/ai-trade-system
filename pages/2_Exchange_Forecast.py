import streamlit as st
import pandas as pd
import requests
from prophet import Prophet
import plotly.express as px

st.set_page_config(page_title="Exchange Rate Forecast", layout="centered")
st.title("Exchange Rate Forecast (USD → Selected Currency)")

# 1. Currency selection (Frankfurter-supported)
currencies = ["EUR", "JPY", "GBP", "CHF", "AUD", "CAD", "CNY", "INR", "BRL", "MXN",
              "ZAR", "SEK", "NOK", "DKK", "PLN", "CZK", "HUF", "RON", "BGN", "TRY",
              "ILS", "SGD", "HKD", "NZD", "KRW", "THB", "MYR", "PHP", "IDR", "ISK", "RUB"]

target_currency = st.selectbox("Select a target currency:", currencies)

# 2. Load time series data from Frankfurter API
@st.cache_data
def fetch_frankfurter_data(target):
    url = f"https://api.frankfurter.app/2023-01-01..2024-01-01?from=USD&to={target}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if "rates" not in data:
            return None
        records = [(date, rate[target]) for date, rate in data["rates"].items()]
        df = pd.DataFrame(records, columns=["ds", "y"])
        df["ds"] = pd.to_datetime(df["ds"])
        return df.sort_values("ds")
    except Exception:
        return None

# 3. Forecast with Prophet
@st.cache_data
def forecast_exchange(df):
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    return forecast

# 4. Run
with st.spinner("Fetching and forecasting exchange rate..."):
    df_rates = fetch_frankfurter_data(target_currency)
    if df_rates is None or df_rates.empty:
        st.error("⚠️ Failed to load exchange rate data.")
    else:
        forecast_df = forecast_exchange(df_rates)

        # 5. Show plot
        st.markdown(f"### Forecast: USD → {target_currency} (Next 30 Days)")
        fig = px.line(forecast_df, x="ds", y="yhat",
                      labels={"ds": "Date", "yhat": f"USD to {target_currency}"},
                      title=f"Exchange Rate Forecast")
        st.plotly_chart(fig)

        # 6. Show table
        st.markdown("### Forecast Table (Last 10 Days)")
        st.dataframe(forecast_df[["ds", "yhat"]].tail(10))

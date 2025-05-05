import streamlit as st
import pandas as pd
import requests
from prophet import Prophet
import plotly.express as px

st.set_page_config(page_title="Exchange Rate Forecast", layout="centered")
st.title("Exchange Rate Forecast (USD → Selected Currency)")

# 1. Currency selection
currencies = ["KRW", "EUR", "JPY", "CNY", "INR", "VND", "THB", "BRL", "MXN", "TRY"]
target_currency = st.selectbox("Select a target currency:", currencies)

# 2. Fetch time series exchange rate data
@st.cache_data
def fetch_exchange_data(target):
    url = f"https://api.exchangerate.host/timeseries?start_date=2023-01-01&end_date=2024-01-01&base=USD&symbols={target}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if "rates" not in data:
            return None
        records = []
        for date, rate in data["rates"].items():
            if target in rate:
                records.append((date, rate[target]))
        df = pd.DataFrame(records, columns=["ds", "y"])
        df["ds"] = pd.to_datetime(df["ds"])
        return df.sort_values("ds")
    except Exception as e:
        return None

# 3. Forecast using Prophet
@st.cache_data
def forecast_exchange(df):
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    return forecast

# 4. Execution
with st.spinner("Loading and forecasting exchange rate..."):
    df_rates = fetch_exchange_data(target_currency)
    if df_rates is None or df_rates.empty:
        st.error("⚠️ Failed to load exchange rate data. Please try again later.")
    else:
        forecast_df = forecast_exchange(df_rates)

        # 5. Plot forecast
        st.markdown(f"### Forecast: USD → {target_currency} (Next 30 Days)")
        fig = px.line(forecast_df, x="ds", y="yhat", labels={"ds": "Date", "yhat": f"USD to {target_currency}"},
                      title=f"Exchange Rate Prediction")
        st.plotly_chart(fig)

        # 6. Show prediction table
        st.markdown("### Forecast Table (Last 10 Days)")
        st.dataframe(forecast_df[["ds", "yhat"]].tail(10))

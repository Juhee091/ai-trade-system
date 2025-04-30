import streamlit as st
import pandas as pd
import requests
from prophet import Prophet
import plotly.express as px

st.title("Exchange Rate Forecast (USD to selected currency)")

# 1. 통화 선택 UI
currencies = ["KRW", "EUR", "JPY", "CNY", "INR", "VND", "THB", "BRL", "MXN", "TRY"]
target_currency = st.selectbox("Select a target currency:", currencies)

# 2. 환율 데이터 가져오기 (1년치)
@st.cache_data
def fetch_exchange_data(target):
    url = f"https://api.exchangerate.host/timeseries?start_date=2023-01-01&end_date=2024-01-01&base=USD&symbols={target}"
    response = requests.get(url)
    data = response.json()
    records = [(date, value[target]) for date, value in data["rates"].items() if target in value]
    df = pd.DataFrame(records, columns=["ds", "y"])
    df["ds"] = pd.to_datetime(df["ds"])
    return df.sort_values("ds")

# 3. Prophet 예측 모델 훈련 및 예측
@st.cache_data
def forecast_exchange(df):
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    return forecast

# 4. 실행
with st.spinner("Loading and forecasting exchange rate..."):
    df_rates = fetch_exchange_data(target_currency)
    forecast_df = forecast_exchange(df_rates)

# 5. 그래프 출력
st.markdown(f"### Forecast for USD → {target_currency} (Next 30 days)")
fig = px.line(forecast_df, x="ds", y="yhat", labels={"ds": "Date", "yhat": f"USD to {target_currency}"},
              title=f"Exchange Rate Prediction (USD to {target_currency})")
st.plotly_chart(fig)

# 6. 예측 요약 테이블
st.markdown("### Prediction Table (last 10 days)")
st.dataframe(forecast_df[["ds", "yhat"]].tail(10))

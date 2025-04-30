import streamlit as st
import base64

st.set_page_config(page_title="AI Trade System", layout="centered")
st.title("🌐 Welcome to the AI Trade Toolkit")
st.markdown("Choose a tool below to get started:")

# Define tool options as cards
tools = [
    {"label": "💱 Exchange Rate Converter", "desc": "Convert trade prices using real-time exchange rates.", "page": "exchange_converter.py"},
    {"label": "📈 Exchange Forecast", "desc": "Predict exchange rate trends for the next 30 days.", "page": "exchange_forecast_app.py"},
    {"label": "🔁 Scenario Analysis", "desc": "Analyze how tariff and FX rate shifts affect trade price.", "page": "scenario_analysis_app.py"},
    {"label": "🤖 Trade Chatbot", "desc": "Ask questions about tariffs, prices, and trade suggestions.", "page": "trade_chatbot_app.py"},
    {"label": "🚨 Risk Alerts", "desc": "Get warnings if tariffs or exchange rates are risky.", "page": "risk_alert_module.py"}
]

# Show tools in button cards
for tool in tools:
    with st.container():
        st.markdown(f"### {tool['label']}")
        st.markdown(tool["desc"])
        if st.button(f"➡ Go to {tool['label'].split(' ')[1]}"):
            st.switch_page(tool['page'])

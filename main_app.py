import streamlit as st

st.set_page_config(page_title="AI Trade Toolkit", layout="centered")

st.title("🌐 AI Trade Toolkit")
st.markdown("Welcome to your AI-powered international trade assistant. Choose a tool to begin:")

st.divider()

st.page_link("pages/1_💱_Exchange_Converter.py", label="💱 Exchange Converter", icon="💱")
st.page_link("pages/2_📈_Exchange_Forecast.py", label="📈 Exchange Forecast", icon="📈")
st.page_link("pages/3_🔁_Scenario_Analysis.py", label="🔁 Scenario Analysis", icon="🔁")
st.page_link("pages/4_🤖_Trade_Chatbot.py", label="🤖 Trade Chatbot", icon="🤖")
st.page_link("pages/5_🚨_Risk_Alerts.py", label="🚨 Risk Alerts", icon="🚨")

st.divider()
st.caption("Developed by Juhee Kim | AI & Data-Driven Global Trade Insights")


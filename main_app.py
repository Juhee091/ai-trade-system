import streamlit as st

st.set_page_config(page_title="AI Trade Toolkit", layout="centered")

st.title("🌐 AI Trade Toolkit")
st.markdown("Welcome to your AI-powered international trade assistant. Choose a tool to begin:")

st.divider()

st.page_link("pages/1_Exchange_Converter.py", label="Exchange Converter")
st.page_link("pages/2_Exchange_Forecast.py", label="Exchange Forecast")
st.page_link("pages/3_Scenario_Analysis.py", label="Scenario Analysis")
st.page_link("pages/4_Trade_Chatbot.py", label="Trade Chatbot")
st.page_link("pages/5_Risk_Alerts.py", label="Risk Alerts")

st.divider()
st.caption("Developed by Juhee Kim | AI & Data-Driven Global Trade Insights")


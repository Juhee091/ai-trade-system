import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Multi-Scenario Price Impact Analysis")

# User inputs
base_price = st.number_input("Base product price (USD)", min_value=1000, max_value=100000, value=30000, step=1000)
base_tariff = st.slider("Base tariff rate (%)", min_value=0, max_value=50, value=8)
base_exchange = st.number_input("Base exchange rate (USD to local currency)", min_value=500, max_value=2000, value=1300, step=50)

st.markdown("### Scenario ranges")
tariff_range = st.slider("± Tariff rate variation (%)", min_value=1, max_value=20, value=5)
exchange_range = st.slider("± Exchange rate variation", min_value=10, max_value=500, value=100, step=10)

# Define scenarios
scenarios = [
    {"name": "Base", "tariff": base_tariff, "exchange": base_exchange},
    {"name": f"Lower Tariff (-{tariff_range}%)", "tariff": base_tariff - tariff_range, "exchange": base_exchange},
    {"name": f"Higher Tariff (+{tariff_range}%)", "tariff": base_tariff + tariff_range, "exchange": base_exchange},
    {"name": f"Stronger Local (-{exchange_range})", "tariff": base_tariff, "exchange": base_exchange - exchange_range},
    {"name": f"Weaker Local (+{exchange_range})", "tariff": base_tariff, "exchange": base_exchange + exchange_range},
    {"name": f"Lower Tariff & Stronger Local", "tariff": base_tariff - tariff_range, "exchange": base_exchange - exchange_range},
    {"name": f"Higher Tariff & Weaker Local", "tariff": base_tariff + tariff_range, "exchange": base_exchange + exchange_range},
]

# Calculate final price
results = []
for s in scenarios:
    tariff_price = base_price * (1 + s["tariff"] / 100)
    final_price_local = tariff_price * s["exchange"]
    results.append({
        "Scenario": s["name"],
        "Tariff Rate (%)": s["tariff"],
        "Exchange Rate": s["exchange"],
        "Final Price (Local Currency)": round(final_price_local, 2)
    })

scenario_df = pd.DataFrame(results)

# Show table
st.markdown("### 📋 Scenario Comparison Table")
st.dataframe(scenario_df)

# Show plot
fig = px.bar(
    scenario_df,
    x="Scenario",
    y="Final Price (Local Currency)",
    text="Final Price (Local Currency)",
    title="Price Comparison Across Scenarios"
)
fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
st.plotly_chart(fig)

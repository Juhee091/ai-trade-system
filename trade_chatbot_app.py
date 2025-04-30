import streamlit as st
import pandas as pd
import plotly.express as px

# Load tariff data
@st.cache_data
def load_data():
    return pd.read_csv("tariff_prices_with_currency_codes.csv")

df = load_data()

st.title("💬 Trade Assistant Chatbot (with Scenarios & Charts)")
st.markdown("Ask about tariffs, prices, or what-if scenarios.\nExample: *Korea to Germany for Passenger cars with higher USD*")

# Chat input
user_input = st.text_input("Your question:")

# Define keyword-based parser
def parse_question(text):
    countries = list(set(df["export_country"]).union(set(df["import_country"])))
    products = list(df["product"].unique())

    export_country = next((c for c in countries if c.lower() in text.lower()), None)
    import_country = next((c for c in countries if c.lower() in text.lower() and c != export_country), None)
    product = next((p for p in products if p.lower() in text.lower()), None)

    # Detect modifiers
    is_stronger_currency = "stronger" in text.lower() or "lower usd" in text.lower()
    is_weaker_currency = "weaker" in text.lower() or "higher usd" in text.lower()
    scenario_flag = is_stronger_currency or is_weaker_currency

    return export_country, import_country, product, scenario_flag

# Scenario calculation
def calculate_scenarios(base_price, base_tariff, base_exchange):
    scenarios = [
        {"name": "Base", "tariff": base_tariff, "exchange": base_exchange},
        {"name": "Lower Tariff", "tariff": base_tariff - 2, "exchange": base_exchange},
        {"name": "Higher Tariff", "tariff": base_tariff + 3, "exchange": base_exchange},
        {"name": "Stronger Currency", "tariff": base_tariff, "exchange": base_exchange - 100},
        {"name": "Weaker Currency", "tariff": base_tariff, "exchange": base_exchange + 100},
        {"name": "Low Tariff + Stronger", "tariff": base_tariff - 2, "exchange": base_exchange - 100},
        {"name": "High Tariff + Weaker", "tariff": base_tariff + 3, "exchange": base_exchange + 100},
    ]
    results = []
    for s in scenarios:
        t_price = base_price * (1 + s["tariff"] / 100)
        final = t_price * s["exchange"]
        results.append({"Scenario": s["name"], "Final Price": round(final, 2)})
    return pd.DataFrame(results)

# Main chatbot logic
def generate_response(export_country, import_country, product, show_scenario):
    if not all([export_country, import_country, product]):
        return "❌ I couldn't recognize the countries or product. Please try again."

    match = df[(df["export_country"] == export_country) &
               (df["import_country"] == import_country) &
               (df["product"].str.lower() == product.lower())]

    if match.empty:
        return "❌ No matching trade route found.", None

    row = match.iloc[0]
    base_price = row['base_price_usd']
    base_tariff = row['tariff_rate']
    base_exchange = row['exchange_rate_usd_to_local'] if 'exchange_rate_usd_to_local' in row else 1300

    # Base response
    response = (
        f"🔍 **{export_country} → {import_country}**\n"
        f"**Product**: {product}\n"
        f"**Tariff Rate**: {base_tariff}%\n"
        f"**Base Price**: ${base_price} USD\n"
        f"**Estimated Local Price**: ≈ {row['final_price_usd'] * base_exchange:.2f} {row['import_currency']}"
    )

    scenario_df = None
    if show_scenario:
        scenario_df = calculate_scenarios(base_price, base_tariff, base_exchange)

    return response, scenario_df

# Run chatbot
if user_input:
    export_country, import_country, product, is_scenario = parse_question(user_input)
    answer, scenario_df = generate_response(export_country, import_country, product, is_scenario)
    st.markdown(answer)

    if scenario_df is not None:
        st.markdown("### Scenario Comparison")
        st.dataframe(scenario_df)
        fig = px.bar(scenario_df, x="Scenario", y="Final Price", text="Final Price")
        st.plotly_chart(fig)

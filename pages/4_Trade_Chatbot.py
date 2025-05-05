import streamlit as st
import pandas as pd
import plotly.express as px
from difflib import get_close_matches

st.set_page_config(page_title="Predictive Trade Assistant", layout="centered")

@st.cache_data
def load_data():
    return pd.read_csv("tariff_prices_with_currency_codes.csv")

df = load_data()

st.title("💬 Trade Chatbot with Debug Mode")

with st.expander("📘 How to ask questions (Click to expand)"):
    st.markdown("""
    Ask things like:
    - Korea exports wheat to Japan
    - Germany → US cars with weaker USD
    - Lower tariffs on coffee from Brazil to France

    This chatbot tries to recognize:
    - Export/import countries
    - Product names
    - Economic scenarios (tariff/currency change)
    """)

user_input = st.chat_input("Ask your trade-related question:")

def fuzzy_match(word, candidates, cutoff=0.6):
    matches = get_close_matches(word.lower(), [c.lower() for c in candidates], n=1, cutoff=cutoff)
    if matches:
        for c in candidates:
            if c.lower() == matches[0]:
                return c
    return None

def parse_with_debug(text):
    countries = list(set(df["export_country"]).union(set(df["import_country"])))
    products = list(df["product"].unique())

    export_country, import_country, product = None, None, None
    tokens = text.lower().split()

    for token in tokens:
        match = fuzzy_match(token, countries)
        if match and not export_country:
            export_country = match
        elif match and not import_country and match != export_country:
            import_country = match

    for token in tokens:
        match = fuzzy_match(token, products)
        if match:
            product = match
            break

    is_stronger = "stronger" in text or "lower usd" in text
    is_weaker = "weaker" in text or "higher usd" in text
    scenario_flag = is_stronger or is_weaker

    return export_country, import_country, product, scenario_flag

def calculate_scenarios(base_price, base_tariff, base_exchange):
    scenarios = [
        {"name": "Base", "tariff": base_tariff, "exchange": base_exchange},
        {"name": "Lower Tariff", "tariff": base_tariff - 2, "exchange": base_exchange},
        {"name": "Higher Tariff", "tariff": base_tariff + 3, "exchange": base_exchange},
        {"name": "Stronger Currency", "tariff": base_tariff, "exchange": base_exchange - 100},
        {"name": "Weaker Currency", "tariff": base_tariff, "exchange": base_exchange + 100},
    ]
    results = []
    for s in scenarios:
        t_price = base_price * (1 + s["tariff"] / 100)
        final = t_price * s["exchange"]
        results.append({"Scenario": s["name"], "Final Price": round(final, 2)})
    return pd.DataFrame(results)

def generate_response(export_country, import_country, product, show_scenario):
    if not all([export_country, import_country, product]):
        debug_msg = (
            f"🛠️ Recognized:\n"
            f"- Export Country: {export_country}\n"
            f"- Import Country: {import_country}\n"
            f"- Product: {product}"
        )
        return f"❌ Incomplete input. Please check.\n\n{debug_msg}", None

    match = df[(df["export_country"] == export_country) &
               (df["import_country"] == import_country) &
               (df["product"].str.lower() == product.lower())]

    if match.empty:
        return f"❌ No trade route found for **{export_country} → {import_country} : {product}**", None

    row = match.iloc[0]
    base_price = row["base_price_usd"]
    base_tariff = row["tariff_rate"]
    base_exchange = row.get("exchange_rate_usd_to_local", 1300)

    response = (
        f"🔍 **{export_country} → {import_country}**\n"
        f"**Product**: {product}\n"
        f"**Tariff Rate**: {base_tariff}%\n"
        f"**Base Price**: ${base_price}\n"
        f"**Estimated Local Price**: ≈ {row['final_price_usd'] * base_exchange:.2f} {row['import_currency']}"
    )

    scenario_df = calculate_scenarios(base_price, base_tariff, base_exchange) if show_scenario else None
    return response, scenario_df

if user_input:
    ec, ic, prod, sflag = parse_with_debug(user_input)
    st.markdown(f"🧠 Parsed:\n- Export Country: `{ec}`\n- Import Country: `{ic}`\n- Product: `{prod}`")

    answer, df_scenario = generate_response(ec, ic, prod, sflag)
    st.markdown(answer)

    if df_scenario is not None:
        st.markdown("### Scenario Comparison")
        st.dataframe(df_scenario)
        st.plotly_chart(px.bar(df_scenario, x="Scenario", y="Final Price", text="Final Price"))

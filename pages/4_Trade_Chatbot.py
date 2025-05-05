import streamlit as st
import pandas as pd
import plotly.express as px
import spacy

nlp = spacy.load("en_core_web_sm")

@st.cache_data
def load_data():
    return pd.read_csv("tariff_prices_with_currency_codes.csv")

df = load_data()

st.set_page_config(page_title="Improved Trade Chatbot", layout="centered")
st.title("Smarter Trade Assistant Chatbot")

with st.expander("How to ask questions (Click to expand)"):
    st.markdown("""
    Try:
    - Exporting wheat from Korea to Japan
    - Cars from Germany to US with stronger USD
    - What if Brazil exports meat to France with lower tariffs?
    """)

user_input = st.chat_input("Ask about tariffs, prices, or what-if scenarios:")

def smart_parse(text):
    doc = nlp(text)
    countries = list(set(df["export_country"]).union(set(df["import_country"])))
    products = list(df["product"].unique())

    export_country = None
    import_country = None
    product = None

    found = [ent.text for ent in doc.ents if ent.text in countries]
    if len(found) >= 2:
        export_country, import_country = found[0], found[1]
    elif len(found) == 1:
        export_country = found[0]

    for token in doc:
        for p in products:
            if p.lower() in token.text.lower():
                product = p
                break

    is_stronger = "stronger" in text.lower() or "lower usd" in text.lower()
    is_weaker = "weaker" in text.lower() or "higher usd" in text.lower()
    return export_country, import_country, product, is_stronger or is_weaker

def calculate_scenarios(price, tariff, rate):
    return pd.DataFrame([
        {"Scenario": "Base", "Final Price": round(price * (1 + tariff/100) * rate, 2)},
        {"Scenario": "Lower Tariff", "Final Price": round(price * (1 + (tariff - 2)/100) * rate, 2)},
        {"Scenario": "Higher Tariff", "Final Price": round(price * (1 + (tariff + 3)/100) * rate, 2)},
        {"Scenario": "Stronger Currency", "Final Price": round(price * (1 + tariff/100) * (rate - 100), 2)},
        {"Scenario": "Weaker Currency", "Final Price": round(price * (1 + tariff/100) * (rate + 100), 2)},
    ])

def generate_response(export_country, import_country, product, scenario):
    if not all([export_country, import_country, product]):
        return "❌ I couldn't recognize the countries or product.", None

    row = df[(df["export_country"] == export_country) &
             (df["import_country"] == import_country) &
             (df["product"].str.lower() == product.lower())]

    if row.empty:
        return "❌ No matching trade route found.", None

    row = row.iloc[0]
    base_price = row['base_price_usd']
    base_tariff = row['tariff_rate']
    rate = row.get('exchange_rate_usd_to_local', 1300)

    msg = (
        f"🔍 **{export_country} → {import_country}**\n"
        f"**Product**: {product}\n"
        f"**Tariff**: {base_tariff}%\n"
        f"**Base Price**: ${base_price}\n"
        f"**Estimated Local**: ≈ {row['final_price_usd'] * rate:.2f} {row['import_currency']}"
    )
    return msg, calculate_scenarios(base_price, base_tariff, rate) if scenario else None

if user_input:
    ec, ic, prod, sflag = smart_parse(user_input)
    ans, df_plot = generate_response(ec, ic, prod, sflag)
    st.markdown(ans)
    if df_plot is not None:
        st.markdown("### Scenario Comparison")
        st.dataframe(df_plot)
        st.plotly_chart(px.bar(df_plot, x="Scenario", y="Final Price", text="Final Price"))

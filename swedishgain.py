import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import requests
import xml.etree.ElementTree as ET
import matplotlib.ticker as mtick

# --- Haal actuele wisselkoers EUR -> SEK op via ECB XML-feed ---
default_rate = 10.90
use_fallback = False
try:
    r = requests.get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml", timeout=5)
    r.raise_for_status()
    tree = ET.fromstring(r.content)
    ns = {'gesmes': 'http://www.gesmes.org/xml/2002-08-01',
          'ecb': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
    cube = tree.find('.//ecb:Cube/ecb:Cube/ecb:Cube[@currency="SEK"]', ns)
    if cube is not None:
        sek_to_eur = float(cube.attrib['rate'])
        use_fallback = False
    else:
        sek_to_eur = default_rate
        use_fallback = True
except:
    sek_to_eur = default_rate
    use_fallback = True

st.set_page_config(page_title="European Withdrawal Tax Calculator", layout="wide")
st.title("🇸🇪 Withdrawal Strategy with Capital Gains Tax (Sweden)")

st.markdown("""
This tool simulates yearly portfolio evolution when withdrawing a **net amount** each year, adjusted for inflation.
It accounts for **capital gains tax on realized profits**, applied only to the portion of each withdrawal that comes from profit.
""")

# --- Sidebar Inputs ---
st.sidebar.header("Input Parameters")
net_start_capital = st.sidebar.number_input("Net invested capital (€)", value=1_000_000, step=50_000)
current_market_value = st.sidebar.number_input("Current market value (€)", value=1_200_000, step=50_000)
annual_return = st.sidebar.number_input("Average annual return (%)", value=5.0, step=0.5) / 100
inflation = st.sidebar.number_input("Inflation (%)", value=2.0, step=0.5) / 100
net_withdrawal = st.sidebar.number_input("Net annual withdrawal (start year, €)", value=40_000, step=1_000)
tax_rate = st.sidebar.number_input("Capital gains tax (%)", value=30.0, step=1.0) / 100
years = st.sidebar.number_input("Simulation period (years)", value=35, step=1)

# --- Output section ---
col1, col2 = st.columns([1, 2])

# --- Linkerkolom: instellingen en SEK-optie ---
with col1:
    st.markdown("### Settings Summary")
    
    # Bepaal rate label
    rate_note = "⚠️ fallback" if use_fallback else "✅ API rate"
    
    # SEK checkbox onderaan
    use_sek = st.checkbox(f"Show all amounts in SEK (converted with {sek_to_eur:.4f})")
    
    # Functie om bedragen te converteren
    def fmt_currency(value):
        if use_sek:
            return f"{int(value * sek_to_eur):,} SEK"
        else:
            return f"{int(value):,} €"
    
    # Weergave van de instellingen
    st.markdown(f"**Exchange rate:** {sek_to_eur:.4f} SEK/EUR ({rate_note})")
    st.markdown(f"**Net invested capital:** {fmt_currency(net_start_capital)}")
    st.markdown(f"**Current market value:** {fmt_currency(current_market_value)}")
    st.markdown(f"**Average annual return:** {annual_return*100:.1f}%")
    st.markdown(f"**Inflation:** {inflation*100:.1f}%")
    st.markdown(f"**Capital gains tax:** {tax_rate*100:.1f}%")
    st.markdown(f"**Net withdrawal (year 1):** {fmt_currency(net_withdrawal)}")
    st.markdown(f"**Simulation period:** {years} years")

# --- Berekeningen ---
# Zet eventueel om naar SEK voor de berekening
calc_net_start = net_start_capital * sek_to_eur if use_sek else net_start_capital
calc_current_value = current_market_value * sek_to_eur if use_sek else current_market_value
calc_net_withdrawal = net_withdrawal * sek_to_eur if use_sek else net_withdrawal

profit = max(calc_current_value - calc_net_start, 0)
invested_capital = calc_net_start
value = invested_capital + profit
net_wd = calc_net_withdrawal
current_year = datetime.date.today().year

data = []

for i in range(years):
    year = current_year + i

    if i == 0:
        data.append({
            "Year": year,
            "Start Value": None,
            "Gross Withdrawal": None,
            "Tax Paid": None,
            "Net Withdrawal": None,
            "End Value": int(round(calc_current_value)),
            "Remaining Capital": int(round(invested_capital)),
            "Remaining Profit": int(round(profit))
        })
        continue

    profit = profit * (1 + annual_return) + invested_capital * annual_return
    value = invested_capital + profit

    if value <= 0:
        break

    profit_fraction = profit / value if value > 0 else 0
    gross_wd = net_wd / (1 - tax_rate * profit_fraction)
    tax_paid = gross_wd * profit_fraction * tax_rate

    profit -= gross_wd * profit_fraction
    invested_capital -= gross_wd * (1 - profit_fraction)
    if invested_capital < 0:
        invested_capital = 0

    value = invested_capital + profit

    data.append({
        "Year": year,
        "Start Value": int(round(value / (1 + annual_return))),
        "Gross Withdrawal": int(round(gross_wd)),
        "Tax Paid": int(round(tax_paid)),
        "Net Withdrawal": int(round(net_wd)),
        "End Value": int(round(value)),
        "Remaining Capital": int(round(invested_capital)),
        "Remaining Profit": int(round(profit))
    })

    net_wd *= (1 + inflation)

df = pd.DataFrame(data)

# --- Rechterkolom: tabel, grafiek, download ---
with col2:
    st.subheader("Results Table")
    st.dataframe(df, use_container_width=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Year"], df["End Value"], label="Portfolio Value")
    ax.plot(df["Year"], df["Net Withdrawal"], label="Net Withdrawal (inflation-adjusted)")
    ax.set_xlabel("Year")
    ax.set_ylabel("SEK" if use_sek else "€")
    ax.set_title("Portfolio Value and Withdrawals Over Time")
    
    # Zorg dat y-as hele getallen toont
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
    
    ax.legend()
    st.pyplot(fig)

    st.download_button(
        label="Download as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="withdrawal_projection.csv",
        mime="text/csv"
    )

st.success("✅ Simulation complete. Adjust parameters in the sidebar to explore different scenarios.")


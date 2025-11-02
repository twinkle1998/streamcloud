# ============================================================
# Rohan — XRP (Ripple) Forecasting Dashboard
# Snapshot resized + grey footer + future-ready layout
# ============================================================

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import time, threading

# ----------------------------
# CONFIG (XRP)
# ----------------------------
COINGECKO = "https://api.coingecko.com/api/v3"
COIN_ID = "ripple"          # ← Ripple on CoinGecko
COIN_NAME = "XRP"
COIN_TICKER = "XRP"
FASTAPI = "https://at3-24669044-fastapi-1.onrender.com"  # your FastAPI

# ----------------------------
# THEME / STYLING
# ----------------------------
def _inject_theme():
    st.markdown("""
    <style>
    :root {
      --bg: #0B0E11;
      --text: #E5E7EB;
      --gold: #F0B90B;
      --card-bg: #FFFFFF;
    }

    html, body, [class*="css"] {
      background-color: var(--bg) !important;
      color: var(--text) !important;
      font-family: 'Inter', system-ui, sans-serif !important;
    }

    .heading-yellow {
      color: var(--gold);
      font-size: 1.8rem;
      font-weight: 700;
    }

    .section-title {
      color: var(--gold);
      font-weight: 900;
      font-size: 1.3rem;
      text-transform: uppercase;
      margin: 0 0 10px 0;
    }

    .white-panel {
      background: var(--card-bg);
      border-left: 5px solid var(--gold);
      border-radius: 6px;
      padding: 15px 20px;
      margin-bottom: 12px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .metric-label {
      color: #444;
      font-weight: 600;
      font-size: 0.9rem;
      margin: 2px 0;
    }
    .metric-value {
      color: #000;
      font-weight: 800;
      font-size: 1.2rem;
      margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------------------
# API HELPERS
# ----------------------------
def _fetch(url, params=None):
    try:
        r = requests.get(url, params=params, timeout=25)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("Fetch error:", e)
        return None

@st.cache_data(ttl=600)
def get_live_market():
    params = {
        "ids": COIN_ID,
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true"
    }
    return _fetch(f"{COINGECKO}/simple/price", params)

@st.cache_data(ttl=600)
def get_ohlc(days=90):
    return _fetch(f"{COINGECKO}/coins/{COIN_ID}/ohlc", {"vs_currency": "usd", "days": days})

@st.cache_data(ttl=600)
def get_market_chart(days=90):
    return _fetch(f"{COINGECKO}/coins/{COIN_ID}/market_chart", {"vs_currency": "usd", "days": days})

@st.cache_data(ttl=600)
def get_metadata():
    return _fetch(f"{COINGECKO}/coins/{COIN_ID}")

# ----------------------------
# VISUALIZATIONS
# ----------------------------
def plot_candlestick(ohlc):
    if not ohlc:
        return None
    df = pd.DataFrame(ohlc, columns=["ts", "open", "high", "low", "close"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    fig = go.Figure(data=[go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name=COIN_TICKER
    )])
    fig.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color="#E5E7EB")
    return fig

def plot_line(series, label):
    if not series:
        return None
    df = pd.DataFrame(series, columns=["ts", "value"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    fig = px.line(df, x="date", y="value", labels={"value": label})
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color="#E5E7EB")
    return fig

# ----------------------------
# MAIN DASHBOARD
# ----------------------------
def app():
    _inject_theme()

    st.markdown(f"<h1 class='heading-yellow'>{COIN_NAME} Next-Day High Price Prediction</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#bbb;'>Powered by CoinGecko & FastAPI · AT3 Group 1 · UTS 2025</p>", unsafe_allow_html=True)

    # === Prediction Section (date picker -> FastAPI) ===
    st.markdown("<div class='section-title'>Prediction by Date</div>", unsafe_allow_html=True)
    selected_date = st.date_input("Select a date", value=date.today())
    if st.button("Get Prediction"):
        try:
            resp = requests.get(f"{FASTAPI}/predict/?date={selected_date.isoformat()}", timeout=20)
            if resp.status_code == 200:
                st.json(resp.json())
            else:
                st.error(f"Error: {resp.status_code} - {resp.text}")
        except Exception as e:
            st.error(f"Prediction failed: {e}")
    st.markdown("---")

    # === Live Market Snapshot ===
    st.markdown("<div class='section-title'>Live Market Snapshot</div>", unsafe_allow_html=True)
    mk = get_live_market()
    if mk and COIN_ID in mk:
        d = mk[COIN_ID]
        html = f"""
        <div class="white-panel">
          <div class="metric-label">Price (USD):</div><div class="metric-value">${d.get('usd',0):,.4f}</div>
          <div class="metric-label">24h Change:</div><div class="metric-value">{d.get('usd_24h_change',0):,.2f}%</div>
          <div class="metric-label">Market Cap (USD):</div><div class="metric-value">${d.get('usd_market_cap',0):,.0f}</div>
          <div class="metric-label">24h Volume (USD):</div><div class="metric-value">${d.get('usd_24h_vol',0):,.0f}</div>
        </div>"""
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("Data unavailable.")
    st.markdown("---")

    # === Historical Performance ===
    st.markdown("<div class='section-title'>Historical Performance</div>", unsafe_allow_html=True)
    ohlc = get_ohlc(90)
    market_chart = get_market_chart(90)
    if ohlc:
        st.plotly_chart(plot_candlestick(ohlc), use_container_width=True)
    if market_chart:
        for key, label in [("market_caps", "Market Cap (USD)"), ("total_volumes", "Trading Volume (USD)")]:
            if market_chart.get(key):
                st.plotly_chart(plot_line(market_chart[key], label), use_container_width=True)
    st.markdown("---")

    # === Fundamentals (XRP) ===
    st.markdown("<div class='section-title'>XRP Fundamentals</div>", unsafe_allow_html=True)
    meta = get_metadata()
    if meta:
        # image & key facts
        if meta.get("image", {}).get("large"):
            st.image(meta["image"]["large"], width=80)
        sym = meta.get("symbol", COIN_TICKER).upper()
        st.markdown(f"**Name:** {meta.get('name', COIN_NAME)}  |  **Symbol:** {sym}")
        st.markdown(f"**Category:** {', '.join(meta.get('categories', [])) or 'N/A'}")
        algo = meta.get("hashing_algorithm", "N/A")  # may be N/A for XRP
        st.markdown(f"**Algorithm:** {algo}")
        # links
        homepage = (meta.get("links", {}).get("homepage") or [""])[0]
        explorer = (meta.get("links", {}).get("blockchain_site") or [""])[0]
        links_line = " | ".join(
            [f"[Website]({homepage})" if homepage else "",
             f"[Explorer]({explorer})" if explorer else ""]
        ).strip(" |")
        if links_line:
            st.markdown(links_line)
    else:
        st.info("Fundamentals unavailable.")
    st.markdown("---")

    # === Summary ===
    st.markdown("<div class='section-title'>Summary</div>", unsafe_allow_html=True)
    st.markdown(f"""
    - Live {COIN_NAME} market metrics from CoinGecko  
    - Interactive candlestick and historical charts  
    - Next-day high price prediction (FastAPI + LightGBM)  
    - Date picker to query any valid past date  
    """)
    st.markdown("<p style='color:#666;'>Developed by Rohan Yadav · AT3 Group 1 · UTS 2025</p>", unsafe_allow_html=True)

# Run app
if __name__ == "__main__":
    app()

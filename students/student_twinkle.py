# ============================================================
# Twinkle — Ethereum (ETH) Forecasting Dashboard
# Snapshot resized + grey footer + future-ready layout
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import time, threading

COINGECKO = "https://api.coingecko.com/api/v3"
COIN_ID = "ethereum"
FASTAPI = "https://fastapiethereum.onrender.com"


# ----------------------------
# THEME / CSS
# ----------------------------
def _inject_theme():
    st.markdown("""
    <style>
    :root {
      --bg: #0B0E11;
      --text: #E5E7EB;
      --gold: #F0B90B;
      --heading-mustard: #a97904;
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
      margin-bottom: 4px; /* tighter spacing */
    }

    .white-caption {
      color: #ffffff !important;
      opacity: 1 !important;
      font-weight: 500;
      margin-top: 0;
      margin-bottom: 8px; /* reduced spacing */
    }

    .section-title-mustard {
      color: var(--heading-mustard);
      font-size: 1.3rem;
      font-weight: 900;
      text-transform: uppercase;
      margin: 0 0 8px 0;
      letter-spacing: 0.3px;
    }

    .live-snapshot {
      width: 100%;
      height: 1vh;
      min-height: 100px;
    }

    .white-panel {
      background: #ffffff;
      border: 1px solid #d1d5db;
      border-radius: 0;
      padding: 10px 12px;
      box-shadow: 0 1px 6px rgba(0,0,0,0.1);
    }
    .white-panel * { color: #111 !important; }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 4px;
      align-items: center;
    }
    .metric { padding: 2px 4px; line-height: 1.1; }
    .metric-label {
      font-size: 0.72rem;
      color: #6b7280 !important;
      margin: 0 0 1px 0;
      font-weight: 600;
    }
    .metric-value {
      font-size: 1.1rem;
      font-weight: 800;
      margin: 0;
      color: #111 !important;
    }

    .chart-wrapper {
      background: #101316;
      border-radius: 10px;
      padding: 10px 14px;
      margin-top: 10px;
      border: 1px solid rgba(255,255,255,0.05);
      box-shadow: inset 0 0 6px rgba(0,0,0,0.4);
    }

    .footer-caption {
      color: #555 !important;
      font-weight: 500;
      font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)


# ----------------------------
# Helper — API Fetch
# ----------------------------
def _fetch(url, params=None, retries=3, delay=2):
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=25)
            r.raise_for_status()
            return r.json()
        except Exception:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return None


# ----------------------------
# Cached API Endpoints
# ----------------------------
@st.cache_data(ttl=600)
def get_metadata():
    return _fetch(f"{COINGECKO}/coins/{COIN_ID}")

@st.cache_data(ttl=300)
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


# ----------------------------
# Visualization Builders
# ----------------------------
def plot_candlestick(ohlc):
    if not ohlc:
        return None
    df = pd.DataFrame(ohlc, columns=["ts", "open", "high", "low", "close"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    fig = go.Figure(data=[go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="ETH"
    )])
    fig.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color="#E5E7EB")
    return fig

def plot_line(series, label, height=250):
    if not series:
        return None
    df = pd.DataFrame(series, columns=["ts", "value"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    fig = px.line(df, x="date", y="value", labels={"value": label})
    fig.update_layout(height=height, margin=dict(l=20, r=20, t=20, b=20),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color="#E5E7EB")
    return fig


# ----------------------------
# Warm-Up FastAPI
# ----------------------------
def _warm_fastapi():
    try:
        requests.get(f"{FASTAPI}/predict/ethereum?date={date.today().isoformat()}", timeout=10)
    except:
        pass


# ----------------------------
# Main App
# ----------------------------
def app():
    _inject_theme()
    threading.Thread(target=_warm_fastapi, daemon=True).start()

    # Heading section with reduced spacing
    st.markdown("<h1 class='heading-yellow'>Ethereum Next-Day High Price Prediction</h1>", unsafe_allow_html=True)
    st.markdown("<p class='white-caption'>Powered by CoinGecko & FastAPI · AT3 Group 1, UTS 2025</p>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#9ca3af; font-size:0.9rem; margin-top:-4px; margin-bottom:8px;'>"
        "Note: The prediction module runs on <strong>Render.com (free tier)</strong>. "
        "It may take <strong>50 seconds to 2 minutes</strong> to start if idle. "
        "Please allow time."
        "</p>",
        unsafe_allow_html=True
    )

    # reduced vertical spacing before iframe
    st.markdown("<div style='margin-top:-8px;'></div>", unsafe_allow_html=True)

    # Prediction iframe (top) — STATIC, NO SCROLL
    today = date.today()
    st.markdown(
        f"""
        <div style='display: flex; justify-content: center; margin-bottom: 15px;'>
            <iframe src="{FASTAPI}/predict/ethereum?date={today.isoformat()}"
                    width="85%" height="600px"
                    style="border:none; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.4);"
                    scrolling="no">
            </iframe>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")

    # 1️⃣ LIVE MARKET SNAPSHOT
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("<div class='section-title-mustard'>Live Market Snapshot</div>", unsafe_allow_html=True)
        mk = get_live_market()
        if mk and COIN_ID in mk:
            d = mk[COIN_ID]
            html = f"""
            <div class="white-panel live-snapshot">
              <div class="metrics-grid">
                <div class="metric"><div class="metric-label">Price (USD)</div><div class="metric-value">${d.get('usd',0):,.2f}</div></div>
                <div class="metric"><div class="metric-label">24h Change (%)</div><div class="metric-value">{d.get('usd_24h_change',0):,.2f}%</div></div>
                <div class="metric"><div class="metric-label">Market Cap (USD)</div><div class="metric-value">${d.get('usd_market_cap',0):,.0f}</div></div>
                <div class="metric"><div class="metric-label">24h Volume (USD)</div><div class="metric-value">${d.get('usd_24h_vol',0):,.0f}</div></div>
              </div>
            </div>"""
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.info("Data temporarily unavailable.")
    st.markdown("---")

    # 2️⃣ HISTORICAL PERFORMANCE + FUNDAMENTALS
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<div class='section-title-mustard'>Historical Market Performance</div>", unsafe_allow_html=True)
        ohlc = get_ohlc(90)
        market_chart = get_market_chart(90)
        if ohlc:
            st.markdown("<div class='chart-wrapper'>", unsafe_allow_html=True)
            st.plotly_chart(plot_candlestick(ohlc), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        if market_chart:
            for key, label in [("market_caps", "Market Cap (USD)"), ("total_volumes", "Trading Volume (USD)")]:
                if market_chart.get(key):
                    st.markdown("<div class='chart-wrapper'>", unsafe_allow_html=True)
                    st.plotly_chart(plot_line(market_chart[key], label), use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='section-title-mustard'>Ethereum Fundamentals</div>", unsafe_allow_html=True)
        meta = get_metadata()
        if meta:
            st.markdown(f"<img src='{meta['image']['large']}' width='80'>", unsafe_allow_html=True)
            st.markdown(f"**Name:** {meta['name']}  |  **Symbol:** {meta['symbol'].upper()}")
            st.markdown(f"**Algorithm:** {meta.get('hashing_algorithm','N/A')}")
            st.markdown(f"**Category:** {', '.join(meta.get('categories', []))}")
            st.markdown(f"[Website]({meta['links']['homepage'][0]}) | [Explorer]({meta['links']['blockchain_site'][0]})")
        else:
            st.info("Fundamentals unavailable.")
    st.markdown("---")

    # 3️⃣ SUMMARY
    st.markdown("<div class='section-title-mustard'>Summary</div>", unsafe_allow_html=True)
    st.markdown("""
    This dashboard delivers:
    - Real-time Ethereum market data via CoinGecko (cached for 5–10 mins)
    - Interactive candlestick and historical charts  
    - Next-day high price prediction via FastAPI ML model  
    - Automatic retry and warm-up for stable performance  
    """)
    st.markdown("<p class='footer-caption'>Developed by Twinkle · AT3 Group 1 · University of Technology Sydney (2025)</p>", unsafe_allow_html=True)


# Run app
if __name__ == "__main__":
    app()

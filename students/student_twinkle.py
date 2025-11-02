# ============================================================
# Twinkle — Ethereum (ETH) Forecasting Dashboard
# Enhanced Visuals per request (same logic)
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
      --panel: #0E1116;
      --border: #1F2937;
      --text: #E5E7EB;
      --muted: #9CA3AF;
      --gold: #F0B90B;
      --heading-mustard: #a97904;
    }
    html, body, [class*="css"] {
      background-color: var(--bg) !important;
      color: var(--text) !important;
      font-family: 'Inter', system-ui, sans-serif !important;
    }
    h1, h2, h3, h4 { color: var(--text) !important; font-weight: 600; }
    a { color: var(--gold) !important; text-decoration: none; }

    .divider { height: 1px; background: var(--border); margin: 2rem 0; }

    .heading-yellow { color: var(--gold); font-size: 1.8rem; font-weight: 700; }
    .white-caption { color: #ffffff !important; opacity: 1 !important; font-weight: 500; }

    /* ---- Section box (kept for other sections) ---- */
    .section-box {
      background: linear-gradient(180deg, #0E1116 0%, #0C0E12 100%);
      border: 1px solid rgba(240,185,11,0.15);
      border-radius: 14px;
      padding: 26px 28px;
      margin-bottom: 35px;
      box-shadow: 0 0 18px rgba(0,0,0,0.4), inset 0 0 6px rgba(255,255,255,0.03);
    }
    .section-box h3 {
      color: var(--gold);
      font-size: 1.3rem;
      font-weight: 700;
      margin: 0 0 12px 0;
      padding-bottom: 6px;
      border-bottom: 1px solid rgba(240,185,11,0.2);
      display: inline-block;
    }

    /* ---- LIVE MARKET SNAPSHOT (NEW STYLE) ---- */
    .section-title-mustard {
      color: var(--heading-mustard);
      font-size: 1.15rem;
      font-weight: 800;
      margin: 0 0 8px 0;
      letter-spacing: 0.2px;
    }
    .white-panel {
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 14px 16px; /* compact */
      margin-bottom: 28px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.12);
    }
    .white-panel * { color: #111 !important; }  /* ensure black text inside */
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;            /* VERY small spacing */
      align-items: center;
    }
    .metric {
      padding: 4px 6px;    /* compact inner padding */
      line-height: 1.15;
    }
    .metric-label {
      font-size: 0.78rem;
      color: #6b7280 !important; /* gray-500 */
      margin: 0 0 2px 0;         /* minimal spacing above value */
      font-weight: 600;
    }
    .metric-value {
      font-size: 1.15rem;
      font-weight: 800;
      margin: 0;
      color: #111 !important;    /* solid black number */
    }

    /* Chart wrappers for nicer framing (unchanged from earlier polish) */
    .chart-wrapper {
      background: #101316;
      border-radius: 10px;
      padding: 12px 16px;
      margin: 10px 0 20px 0;
      border: 1px solid rgba(255,255,255,0.05);
      box-shadow: inset 0 0 6px rgba(0,0,0,0.4);
    }
    </style>
    """, unsafe_allow_html=True)


# ----------------------------
# Helper — API Fetch (Retry)
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
    fig.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E5E7EB",
        xaxis_title="Date", yaxis_title="Price (USD)"
    )
    return fig

def plot_line(series, label, height=280):
    if not series:
        return None
    df = pd.DataFrame(series, columns=["ts", "value"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    fig = px.line(df, x="date", y="value", labels={"value": label})
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E5E7EB"
    )
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

    st.markdown("<h1 class='heading-yellow'>Ethereum Next-Day High Price Prediction</h1>", unsafe_allow_html=True)
    st.markdown("<p class='white-caption'>Powered by CoinGecko & FastAPI · AT3 Group 1, UTS 2025</p>", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ============================================================
    # SECTION 1 — Prediction via FastAPI (unchanged)
    # ============================================================
    today = date.today()
    iframe_url = f"{FASTAPI}/predict/ethereum?date={today.isoformat()}"
    components.iframe(iframe_url, height=520, scrolling=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ============================================================
    # SECTION 2 — Live Market Snapshot (NEW LAYOUT)
    # ============================================================
    st.markdown("<div class='section-title-mustard'>Live Market Snapshot</div>", unsafe_allow_html=True)

    mk = get_live_market()
    if mk and COIN_ID in mk:
        data = mk[COIN_ID]
        # Build ONE compact white panel with all four metrics (no individual boxes)
        html = f"""
        <div class="white-panel">
          <div class="metrics-grid">
            <div class="metric">
              <div class="metric-label">Price (USD)</div>
              <div class="metric-value">${data.get('usd', 0):,.2f}</div>
            </div>
            <div class="metric">
              <div class="metric-label">24h Change (%)</div>
              <div class="metric-value">{data.get('usd_24h_change', 0):,.2f}%</div>
            </div>
            <div class="metric">
              <div class="metric-label">Market Cap (USD)</div>
              <div class="metric-value">${data.get('usd_market_cap', 0):,.0f}</div>
            </div>
            <div class="metric">
              <div class="metric-label">24h Volume (USD)</div>
              <div class="metric-value">${data.get('usd_24h_vol', 0):,.0f}</div>
            </div>
          </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("Data temporarily unavailable — please retry in a moment.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ============================================================
    # SECTION 3 — Historical Charts (kept boxed)
    # ============================================================
    st.markdown("<div class='section-box'><h3>Historical Market Performance</h3>", unsafe_allow_html=True)
    days = 90
    ohlc = get_ohlc(days)
    market_chart = get_market_chart(days)

    if ohlc:
        st.markdown("<div class='chart-wrapper'>", unsafe_allow_html=True)
        st.plotly_chart(plot_candlestick(ohlc), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Price history unavailable right now.")

    if market_chart:
        for key, label in [("market_caps", "Market Cap (USD)"), ("total_volumes", "Trading Volume (USD)")]:
            if market_chart.get(key):
                st.markdown("<div class='chart-wrapper'>", unsafe_allow_html=True)
                st.plotly_chart(plot_line(market_chart[key], label), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ============================================================
    # SECTION 4 — Ethereum Fundamentals (kept boxed)
    # ============================================================
    st.markdown("<div class='section-box'><h3>Ethereum Fundamentals</h3>", unsafe_allow_html=True)
    meta = get_metadata()
    if meta:
        logo = meta["image"]["large"]
        st.markdown(f"<img src='{logo}' width='80'>", unsafe_allow_html=True)
        st.markdown(f"**Name:** {meta['name']}  |  **Symbol:** {meta['symbol'].upper()}")
        st.markdown(f"**Algorithm:** {meta.get('hashing_algorithm','N/A')}")
        st.markdown(f"**Category:** {', '.join(meta.get('categories', []))}")
        st.markdown(f"[Website]({meta['links']['homepage'][0]}) | [Explorer]({meta['links']['blockchain_site'][0]})")
    else:
        st.info("Project fundamentals unavailable — please refresh later.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ============================================================
    # SECTION 5 — Summary (unchanged)
    # ============================================================
    st.markdown("### Summary")
    st.markdown("""
    This dashboard delivers:
    - Real-time Ethereum market data via CoinGecko (cached for 5–10 mins)
    - Interactive candlestick and historical charts  
    - Next-day high price prediction via FastAPI ML model  
    - Automatic retry and warm-up for stable performance  
    """)
    st.caption("Developed by Twinkle · AT3 Group 1 · University of Technology Sydney (2025)")

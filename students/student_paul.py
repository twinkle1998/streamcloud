# Paul — Bitcoin (BTC) Forecasting Dashboard

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import time, threading


# Constants
COINGECKO = "https://api.coingecko.com/api/v3"
COIN_ID   = "bitcoin"

FASTAPI   = "https://at3-g-1-25142441-api.onrender.com"

# ----------------------------
# Theme
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
      --accent: #22C55E;
    }
    html, body, [class*="css"] {
      background-color: var(--bg) !important;
      color: var(--text) !important;
      font-family: 'Inter', system-ui, sans-serif !important;
    }
    h1, h2, h3, h4 { color: var(--text) !important; font-weight: 600; }
    a { color: var(--accent) !important; text-decoration: none; }
    .kpi {
      background: #111318;
      border: 1px solid rgba(34,197,94,0.25);
      border-radius: 14px;
      padding: 18px;
      text-align: center;
    }
    .kpi h3 {
      color: var(--muted);
      font-size: 0.9rem;
      margin-bottom: 4px;
    }
    .kpi p {
      color: var(--text);
      font-weight: 700;
      font-size: 1.4rem;
      margin: 0;
    }
    .divider {
      height: 1px;
      background: var(--border);
      margin: 2rem 0;
    }
    .heading {
      color: var(--accent);
      font-size: 1.8rem;
      font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------------------
# Helper — API fetch with retry
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
# Cached CoinGecko calls
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
        "include_24hr_change": "true",
    }
    return _fetch(f"{COINGECKO}/simple/price", params)

@st.cache_data(ttl=600)
def get_ohlc(days=90):
    return _fetch(f"{COINGECKO}/coins/{COIN_ID}/ohlc", {"vs_currency": "usd", "days": days})

@st.cache_data(ttl=600)
def get_market_chart(days=90):
    return _fetch(f"{COINGECKO}/coins/{COIN_ID}/market_chart", {"vs_currency": "usd", "days": days})

# ----------------------------
# Plot builders
# ----------------------------
def plot_candlestick(ohlc):
    if not ohlc:
        return None
    df = pd.DataFrame(ohlc, columns=["ts", "open", "high", "low", "close"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    fig = go.Figure(data=[go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"],
        low=df["low"], close=df["close"], name="BTC"
    )])
    fig.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E5E7EB",
        xaxis_title="Date", yaxis_title="Price (USD)",
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
        font_color="#E5E7EB",
    )
    return fig

# ----------------------------
# Warm-up the FastAPI service
# ----------------------------
def _warm_fastapi():
    try:
        requests.get(f"{FASTAPI}/predict/bitcoin?date=2024-11-01", timeout=10)
    except:
        pass

# ----------------------------
# Main
# ----------------------------
def app():
    _inject_theme()
    threading.Thread(target=_warm_fastapi, daemon=True).start()

    st.markdown("<h1 class='heading'>Bitcoin Next-Day High Price Prediction</h1>", unsafe_allow_html=True)
    st.caption("Powered by FastAPI + CoinGecko · AT3 Group 1, UTS 2025")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ======= Section 1: Prediction via FastAPI (iframe) =======
    left, right = st.columns([1, 1])
    with left:
        d = st.date_input("Pick a UTC date to fetch features from", value=date.today())
        source = st.selectbox("Data source (optional)", ["auto", "coingecko", "kraken"], index=0)
        st.write("Tip: if a source fails or is rate-limited, try another source or a past date.")

    # Build the API URL for the iframe (no CORS fuss)
    query = f"date={d.isoformat()}"
    if source and source != "auto":
        query += f"&source={source}"
    iframe_url = f"{FASTAPI}/predict/bitcoin?{query}"

    # Show the JSON response directlyI
    components.iframe(iframe_url, height=520, scrolling=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ======= Section 2: Live market snapshot =======
    st.markdown("### Live Market Snapshot")
    mk = get_live_market()
    if mk and COIN_ID in mk:
        data = mk[COIN_ID]
        colA, colB, colC, colD = st.columns(4)
        metrics = [
            ("Price (USD)",        f"${data.get('usd', 0):,.2f}"),
            ("24h Change (%)",     f"{data.get('usd_24h_change', 0):,.2f}%"),
            ("Market Cap (USD)",   f"${data.get('usd_market_cap', 0):,.0f}"),
            ("24h Volume (USD)",   f"${data.get('usd_24h_vol', 0):,.0f}"),
        ]
        for i, (label, value) in enumerate(metrics):
            with [colA, colB, colC, colD][i]:
                st.markdown(f"<div class='kpi'><h3>{label}</h3><p>{value}</p></div>", unsafe_allow_html=True)
    else:
        st.info("CoinGecko might be rate-limited. Please retry.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ======= Section 3: Historical Performance =======
    st.markdown("### Historical Performance (90 days)")
    ohlc = get_ohlc(90)
    market_chart = get_market_chart(90)

    fig_candle = plot_candlestick(ohlc)
    if fig_candle:
        st.plotly_chart(fig_candle, use_container_width=True)
    else:
        st.info("Price history unavailable right now.")

    if market_chart:
        for key, label in [("market_caps", "Market Cap (USD)"),
                           ("total_volumes", "Trading Volume (USD)")]:
            if market_chart.get(key):
                fig = plot_line(market_chart[key], label)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ======= Section 4: BTC Fundamentals =======
    st.markdown("### Bitcoin Fundamentals")
    meta = get_metadata()
    if meta:
        logo = meta.get("image", {}).get("large")
        if logo:
            st.image(logo, width=72)
        st.write(f"**Name:** {meta.get('name', 'Bitcoin')}  |  **Symbol:** {meta.get('symbol','BTC').upper()}")
        cats = meta.get("categories") or []
        st.write(f"**Category:** {', '.join(cats) if isinstance(cats, list) else '—'}")
        links = meta.get("links", {})
        site = (links.get("homepage") or [''])[0]
        explorer = (links.get("blockchain_site") or [''])[0]
        if site or explorer:
            st.write(f"[Website]({site}) | [Explorer]({explorer})")
    else:
        st.info("Fundamentals unavailable right now (likely rate-limit).")

    st.caption("Built by Paul Benjamin Samuel (25142441) · AT3 Group 1 · AML · UTS 2025")


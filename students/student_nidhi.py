# ============================================================
# Nidhi — Solana (SOL) Forecasting Dashboard (Optimized for Cloud)
# ============================================================

import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import date
import time, threading

# ----------------------------
# CONFIG
# ----------------------------
COINGECKO = "https://api.coingecko.com/api/v3"
FASTAPI = "https://predict-solana-api.onrender.com"
COIN_ID = "solana"

SOLANA_BLURB = (
    "Solana (SOL) is a high-performance Layer-1 blockchain designed for low-latency, "
    "low-cost transactions. It combines Proof of Stake with Proof of History to reach high throughput, "
    "supporting DeFi, payments, and consumer apps at scale. Mainnet launched in 2020 and the network "
    "is widely used for NFTs, on-chain order books, and real-time apps."
)

# ----------------------------
# THEME
# ----------------------------
def _inject_theme():
    st.markdown("""
    <style>
    :root { --bg:#0B0E11; --text:#E5E7EB; --gold:#F0B90B; }
    html, body, [class*="css"] {
      background-color: var(--bg)!important;
      color: var(--text)!important;
      font-family:'Inter',system-ui,sans-serif!important;
    }
    .heading {color:var(--gold);font-size:2rem;font-weight:800;margin-bottom:4px;}
    .sub {color:#d3d3d3;margin-bottom:12px;font-weight:500;}
    .panel {
      background:#101316;border:1px solid rgba(255,255,255,0.07);
      border-radius:10px;padding:14px 18px;margin-top:10px;
      box-shadow:inset 0 0 6px rgba(0,0,0,0.35);
    }
    .metric-label {font-size:0.9rem;color:#aaa;margin-bottom:4px;}
    .metric-value {font-size:1.8rem;font-weight:800;color:var(--gold);}
    .metric-caption {font-size:0.8rem;color:#bbb;}
    .coin-info {font-size:0.9rem;color:#ccc;line-height:1.5;margin-top:10px;}
    .note {color:#888;font-size:0.85rem;margin-top:10px;}
    </style>
    """, unsafe_allow_html=True)


# ----------------------------
# Helper — API Fetch (Twinkle-style)
# ----------------------------
def _fetch(url, params=None, retries=3, delay=2):
    """Unified fetcher with automatic retry for network/rate limit resilience."""
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=20)
            r.raise_for_status()
            return r.json()
        except Exception:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return None


# ----------------------------
# Warm-up (Render)
# ----------------------------
def _warm_fastapi():
    try:
        requests.get(f"{FASTAPI}/predict/solana", timeout=10)
    except:
        pass


# ----------------------------
# Cached API Calls
# ----------------------------
@st.cache_data(ttl=900)
def get_prediction():
    return _fetch(f"{FASTAPI}/predict/solana")

@st.cache_data(ttl=900)
def get_model_info():
    return _fetch(f"{FASTAPI}/model_info")

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
def get_ohlc(days=30):
    return _fetch(f"{COINGECKO}/coins/{COIN_ID}/ohlc", {"vs_currency": "usd", "days": days})

@st.cache_data(ttl=600)
def get_market_chart(days=90):
    return _fetch(f"{COINGECKO}/coins/{COIN_ID}/market_chart", {"vs_currency": "usd", "days": days})


# ----------------------------
# Visualization Builders
# ----------------------------
def build_candlestick(ohlc):
    if not ohlc:
        return None
    df = pd.DataFrame(ohlc, columns=["ts", "open", "high", "low", "close"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    fig = go.Figure(data=[go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing_line_color="#26A69A", decreasing_line_color="#EF5350", showlegend=False
    )])
    fig.update_layout(
        height=360, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E5E7EB", xaxis_rangeslider_visible=False
    )
    return fig


def build_line(series, label, height=250):
    if not series:
        return None
    df = pd.DataFrame(series, columns=["ts", "val"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    fig = go.Figure([go.Scatter(x=df["date"], y=df["val"], mode="lines", line=dict(color="#00BFFF", width=2.2))])
    fig.update_layout(height=height, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", font_color="#E5E7EB",
                      margin=dict(l=20, r=20, t=20, b=20))
    return fig


# ----------------------------
# Main App
# ----------------------------
def app():
    _inject_theme()
    threading.Thread(target=_warm_fastapi, daemon=True).start()

    st.markdown("<div class='heading'>Solana (SOL) — Next-Day High Prediction</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub'>Powered by CoinGecko API · FastAPI (Render) · AT3 Group 1</div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#9ca3af; font-size:0.9rem;'>Note: The prediction API runs on <strong>Render (free tier)</strong>. "
        "If idle, it may take <strong>60–120 seconds</strong> to start. Please wait while it wakes up.</p>",
        unsafe_allow_html=True
    )

    # --- Prediction ---
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Prediction Dashboard")
        with st.spinner("Fetching prediction..."):
            pred = get_prediction()
        if pred:
            st.markdown(f"<div class='metric-label'>Predicted Next-Day HIGH (USD)</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-value'>${pred.get('Predicted Next-Day HIGH (USD)', 0):,.2f}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-caption'>Generated on {pred.get('Prediction Generated On','N/A')} | Source: {pred.get('Data Source','CoinGecko')}</div>", unsafe_allow_html=True)
        else:
            st.warning("Prediction data unavailable (API may be waking up).")
        st.markdown("</div>", unsafe_allow_html=True)

        # --- Live Market Snapshot ---
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Live Market Snapshot")
        mk = get_live_market()
        if mk and COIN_ID in mk:
            d = mk[COIN_ID]
            st.markdown(f"**Price (USD):** ${d.get('usd',0):,.2f}")
            st.markdown(f"**24h Change:** {d.get('usd_24h_change',0):,.2f}%")
            st.markdown(f"**Market Cap:** ${d.get('usd_market_cap',0)/1e9:,.2f}B")
            st.markdown(f"**24h Volume:** ${d.get('usd_24h_vol',0)/1e9:,.2f}B")
            st.caption("➤ *Price* shows latest USD value. *Market Cap* ≈ circulating supply × price.")
        else:
            st.info("CoinGecko snapshot unavailable.")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Overview ---
    with col2:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Solana Overview")
        meta = get_metadata()
        if meta:
            st.image(meta['image']['large'], width=100)
            st.markdown(f"**Symbol:** {meta['symbol'].upper()}  \n**Name:** {meta['name']}")
            st.markdown(f"[Website]({meta['links']['homepage'][0]}) | [Explorer]({meta['links']['blockchain_site'][0]})")
            st.markdown(f"<div class='coin-info'>{SOLANA_BLURB}</div>", unsafe_allow_html=True)
        else:
            st.info("Metadata unavailable (CoinGecko API rate-limited).")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Model Info ---
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Model Configuration & Training Info")
    info = get_model_info()
    if info:
        st.markdown(f"**Algorithm Used:** {info.get('algorithm','N/A')}")
        st.markdown(f"**Trained Token:** {info.get('trained_token','N/A')}")
        st.markdown(f"**Training Period:** {info.get('training_period','N/A')}")
        st.markdown(f"**Feature Count:** {info.get('feature_count','N/A')}")
        with st.expander("View All Features Used"):
            features = info.get("features_used", [])
            if features:
                st.markdown("  \n".join([f"- {f}" for f in features]))
            else:
                st.write("No feature list available.")
    else:
        st.info("Model information unavailable.")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Charts ---
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Recent Price Structure — Candlestick View")
    ohlc = get_ohlc()
    if ohlc:
        st.plotly_chart(build_candlestick(ohlc), use_container_width=True)
    else:
        st.info("Candlestick data unavailable.")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Market Trends ---
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Market Overview & Historical Trends")
    mc = get_market_chart()
    if mc:
        if mc.get("prices"):
            st.caption("Price Trend (USD)")
            st.plotly_chart(build_line(mc["prices"], "Price (USD)"), use_container_width=True)
        if mc.get("market_caps"):
            st.caption("Market Cap (USD)")
            st.plotly_chart(build_line(mc["market_caps"], "Market Cap (USD)"), use_container_width=True)
        if mc.get("total_volumes"):
            st.caption("Trading Volume (USD)")
            st.plotly_chart(build_line(mc["total_volumes"], "Trading Volume (USD)"), use_container_width=True)
    else:
        st.info("Market data unavailable.")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Insights ---
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Analytical Insights")
    st.markdown("""
    - **Model:** Linear Regression forecasting next-day high using engineered OHLCV features.  
    - **Visualization:** Candlestick & line charts for recent market dynamics.  
    - **Integration:** FastAPI backend + CoinGecko API for real-time predictions.  
    - **Efficiency:** Cached data (5–15 min) minimizes API load and ensures responsiveness on Streamlit Cloud.  
    """)
    st.markdown("<p class='note'>Developed by Nidhi Upadhyay · AT3 Group 1 · UTS (2025)</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    app()

# ============================================================
# Nidhi — Solana (SOL) Forecasting Dashboard 
# ============================================================

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import time


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
# Theme
# ----------------------------
def _inject_theme():
    st.markdown("""
    <style>
    :root {
      --bg:#0B0E11; --text:#E5E7EB; --gold:#F0B90B; --blue:#00BFFF;
    }
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
# Cached Fetchers
# ----------------------------
@st.cache_data(ttl=900)
def fetch_prediction():
    try:
        r = requests.get(f"{FASTAPI}/predict/solana", timeout=20)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

@st.cache_data(ttl=1800)
def get_model_info():
    """Fetch model metadata from FastAPI backend"""
    try:
        r = requests.get(f"{FASTAPI}/model_info", timeout=15)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


@st.cache_data(ttl=1200)
def fetch_coingecko(endpoint, params=None):
    for attempt in range(3):
        try:
            r = requests.get(f"{COINGECKO}/{endpoint}", params=params, timeout=25)
            if r.status_code == 200:
                return r.json()
        except Exception:
            time.sleep(1)
    return None

@st.cache_data(ttl=1200)
def get_market_chart(days=90):
    return fetch_coingecko(f"coins/{COIN_ID}/market_chart", {"vs_currency": "usd", "days": days})

@st.cache_data(ttl=1800)
def get_ohlc(days=30):
    """Fetch OHLC data for candlestick chart"""
    return fetch_coingecko(f"coins/{COIN_ID}/ohlc", {"vs_currency": "usd", "days": days})

@st.cache_data(ttl=1200)
def get_live_price():
    return fetch_coingecko("simple/price", {
        "ids": COIN_ID,
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true"
    })

@st.cache_data(ttl=1800)
def get_metadata():
    return fetch_coingecko(f"coins/{COIN_ID}")

# ----------------------------
# Chart Builders
# ----------------------------
def build_line_chart(series, label):
    if not series:
        return None
    df = pd.DataFrame(series, columns=["ts", "val"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    df = df.tail(90)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["val"],
        mode="lines",
        line=dict(color="#00BFFF", width=2.4),
        name=label
    ))
    fig.update_layout(
        height=260,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E5E7EB", margin=dict(l=20,r=20,t=25,b=20),
        yaxis_title=label
    )
    return fig


def build_candlestick(ohlc_data):
    """Builds a 30-day candlestick chart"""
    if not ohlc_data:
        return None
    df = pd.DataFrame(ohlc_data, columns=["time", "open", "high", "low", "close"])
    df["date"] = pd.to_datetime(df["time"], unit="ms")
    fig = go.Figure(data=[go.Candlestick(
        x=df["date"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing_line_color="#26A69A",
        decreasing_line_color="#EF5350",
        showlegend=False
    )])
    fig.update_layout(
        title="30-Day Price Structure (Candlestick)",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        height=360,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E5E7EB",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_rangeslider_visible=False
    )
    return fig

# ----------------------------
# Main App
# ----------------------------
def app():
    _inject_theme()

    st.markdown("<div class='heading'>Solana (SOL) — Next-Day High Prediction</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub'>Powered by Coingecko API · FastAPI (Render) · AT3 Group 1</div>", unsafe_allow_html=True)

    # === Prediction + Snapshot ===
    col_pred, col_info = st.columns([1.2, 1])

    with col_pred:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Prediction Dashboard")
        pred = fetch_prediction()
        if pred:
            st.markdown("<div class='metric-label'>Predicted Next-Day HIGH (USD)</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-value'>${pred.get('Predicted Next-Day HIGH (USD)',0):,.2f}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='metric-caption'>Generated on {pred.get('Prediction Generated On','N/A')} | Source: {pred.get('Data Source','CoinGecko')}</div>",
                unsafe_allow_html=True
            )
        else:
            st.warning("Could not fetch prediction data from API.")
        st.markdown("</div>", unsafe_allow_html=True)

        # Live Market Snapshot (side panel style) + explanation
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Live Market Snapshot")
        live = get_live_price()
        if live and COIN_ID in live:
            d = live[COIN_ID]
            st.markdown(f"**Price (USD):** ${d.get('usd',0):,.2f}")
            st.markdown(f"**24h Change:** {d.get('usd_24h_change',0):,.2f}%")
            st.markdown(f"**Market Cap:** ${d.get('usd_market_cap',0)/1e9:,.2f}B")
            st.markdown(f"**24h Volume:** ${d.get('usd_24h_vol',0)/1e9:,.2f}B")
            st.caption(
                "➤ *Price* shows the latest USD value. *24h Change* tracks daily percentage movement. "
                "*Market Cap* ≈ circulating supply × price, and *24h Volume* measures trading liquidity in the last day."
            )
        else:
            st.info("CoinGecko snapshot unavailable.")
        st.markdown("</div>", unsafe_allow_html=True)

    # === Coin Overview ===
    with col_info:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Solana Overview")
        meta = get_metadata()
        if meta:
            img = meta['image']['large']
            st.image(img, width=100)
            st.markdown(f"**Symbol:** {meta['symbol'].upper()}  \n**Name:** {meta['name']}")
            st.markdown(f"[Official Website]({meta['links']['homepage'][0]})  |  [Explorer]({meta['links']['blockchain_site'][0]})")
            st.markdown(f"<div class='coin-info'>{SOLANA_BLURB}</div>", unsafe_allow_html=True)
        else:
            st.info("Metadata not available.")
        st.markdown("</div>", unsafe_allow_html=True)


    # === Model Info Section ===
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Model Configuration & Training Info")
    info = get_model_info()
    if info:
        st.markdown(f"**Algorithm Used:** {info.get('algorithm','N/A')}")
        st.markdown(f"**Trained Token:** {info.get('trained_token','N/A')}")
        st.markdown(f"**Training Period:** {info.get('training_period','N/A')}")
        st.markdown(f"**Feature Count:** {info.get('feature_count','N/A')}")

        with st.expander("View All Features Used", expanded=False):
            features = info.get("features_used", [])
            if features:
                cols = st.columns(2)
                half = len(features)//2
                with cols[0]:
                    for f in features[:half]:
                        st.markdown(f"- {f}")
                with cols[1]:
                    for f in features[half:]:
                        st.markdown(f"- {f}")
            else:
                st.write("No feature list available.")
    else:
        st.info("Model information unavailable (FastAPI might be offline).")
    st.markdown("</div>", unsafe_allow_html=True)


    # === Candlestick Chart ===
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Recent Price Structure — Candlestick View")
    ohlc = get_ohlc()
    if ohlc:
        st.plotly_chart(build_candlestick(ohlc), use_container_width=True)
    else:
        st.info("Candlestick data unavailable (API may be rate-limited).")
    st.markdown("</div>", unsafe_allow_html=True)

    # === Historical Trends ===
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Market Overview & Historical Trends")
    mc = get_market_chart()
    if mc:
        if mc.get("prices"):
            st.caption("Price Trend (USD)")
            st.plotly_chart(build_line_chart(mc["prices"], "Price (USD)"), use_container_width=True)
        if mc.get("market_caps"):
            st.caption("Market Cap Trend (USD)")
            st.plotly_chart(build_line_chart(mc["market_caps"], "Market Cap (USD)"), use_container_width=True)
        if mc.get("total_volumes"):
            st.caption("Trading Volume (USD)")
            st.plotly_chart(build_line_chart(mc["total_volumes"], "Trading Volume (USD)"), use_container_width=True)
    else:
        st.warning("No market data available.")
    st.markdown("</div>", unsafe_allow_html=True)

    # === Insights ===
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Analytical Insights")
    st.markdown("""
    - **Prediction Model:** Linear Regression forecasting Solana’s next-day high based on engineered OHLCV features.  
    - **Candlestick View:** Highlights intraday market volatility and trend reversals for short-term traders.  
    - **Market Summary:** Live 24-hour metrics retrieved from CoinGecko, cached to prevent rate-limit issues.  
    - **Technical Edge:** Integrated FastAPI backend ensures reliable and low-latency inference.  
    """)
    st.markdown("<p class='note'>Dashboard developed by Nidhi Upadhyay · AT3 Group 1 · University of Technology Sydney (2025)</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    app()

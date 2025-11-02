# students/student_paul.py
'''
Note: if the tab does not show information; then it likely that the fastapi in Render has not awoken for some reason.
Run the links presented in the github.txt of the AT3_G_1_25142441_API repo and then run this tab. Also there is limit on the API key
listed below, it will time out after a number of tries.
'''
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import time


# Constants / Endpoints
API_BASE   = "https://at3-g-1-25142441-api.onrender.com"
PREDICT_EP = f"{API_BASE}/predict/bitcoin"

COINGECKO  = "https://api.coingecko.com/api/v3"
COIN_ID    = "bitcoin"

def _cg_headers():
    # Hardcoding the API key like is not recommended, this was done to simplify things, usually it would be set in the environment variables
    api_key = "CG-kHQeqHSxkmf2szoFsit55iXX"
    h = {"Accept": "application/json"}
    if api_key.strip():
        h["x-cg-demo-api-key"] = api_key
    return h


# Robust fetch with retries
def _fetch(url, params=None, retries=3, delay=1.2, timeout=25, headers=None, **req_kwargs):
    merged_headers = {**_cg_headers(), **(headers or {})}
    for i in range(retries):
        try:
            r = requests.get(url, params=params, headers=merged_headers, timeout=timeout, **req_kwargs)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if i < retries - 1:
                time.sleep(delay)
            else:
                return {"__error__": f"{type(e).__name__}: {e}"}


# Cached CoinGecko helpers
@st.cache_data(ttl=300)
def cg_live():
    p = {
        "ids": COIN_ID,
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true",
    }
    return _fetch(f"{COINGECKO}/simple/price", params=p)

@st.cache_data(ttl=600)
def cg_ohlc(days=90):
    return _fetch(f"{COINGECKO}/coins/{COIN_ID}/ohlc", params={"vs_currency": "usd", "days": days})

@st.cache_data(ttl=600)
def cg_market_chart(days=90):
    return _fetch(f"{COINGECKO}/coins/{COIN_ID}/market_chart", params={"vs_currency": "usd", "days": days})

@st.cache_data(ttl=600)
def cg_metadata():
    return _fetch(f"{COINGECKO}/coins/{COIN_ID}")


# Plot helpers
def _is_dark():
    try:
        base = st.get_option("theme.base")
        return (base or "").lower() == "dark"
    except Exception:
        return True 
    
def _template():
    return "plotly_dark" if _is_dark() else "plotly_white"

def _candlestick(ohlc):
    if not isinstance(ohlc, list) or len(ohlc) == 0:
        return None
    df = pd.DataFrame(ohlc, columns=["ts", "open", "high", "low", "close"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    fig = go.Figure([go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="OHLC"
    )])
    fig.update_layout(
        template=_template(),
        height=420,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Date", yaxis_title="Price (USD)",
    )
    return fig

def _line_series(series, label, height=300):
    if not isinstance(series, list) or len(series) == 0:
        return None
    df = pd.DataFrame(series, columns=["ts", "value"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    fig = px.line(df, x="date", y="value", labels={"value": label}, template=_template())
    fig.update_layout(height=height, margin=dict(l=20, r=20, t=30, b=20))
    return fig


# UI styles
def _inject_css():
    dark = _is_dark()
    if dark:
        text = "#E5E7EB"; muted = "#9CA3AF"
        accent = "#22C55E"; panel = "#0E1116"; border = "#1F2937"
    else:
        text = "#111827"; muted = "#6B7280"
        accent = "#059669"; panel = "#FFFFFF"; border = "#E5E7EB"

    st.markdown(f"""
    <style>
      .kpi {{
        background:{panel};
        border: 1px solid {border};
        border-radius: 14px;
        padding: 14px 16px;
        text-align: center;
      }}
      .kpi h3 {{
        color:{muted}; font-size: .9rem; margin: 0 0 6px 0;
      }}
      .kpi p {{
        color:{text}; font-weight: 700; font-size: 1.35rem; margin: 0;
      }}
      .section-title {{
        font-weight: 700; font-size: 1.1rem; color:{text};
        margin-top: .75rem; margin-bottom:.3rem;
      }}
      .tip {{
        color:{muted}; font-size: .85rem;
      }}
      .accent-btn > button {{
        background:{accent} !important;
        color:white !important; font-weight:700 !important;
      }}
    </style>
    """, unsafe_allow_html=True)


# Streamlit Page
def app():
    _inject_css()

    st.subheader("Bitcoin (BTC) — Next-Day High Price Prediction")
    st.caption("Powered by FastAPI + CoinGecko · AT3 Group 1, UTS 2025")

    # --- Controls
    col1, col2, col3 = st.columns([1.2, 0.8, 0.6])
    with col1:
        d = st.date_input("Pick a UTC date to fetch features from", value=date.today())
    with col2:
        source = st.selectbox("Data source (optional)", ["auto", "coingecko", "kraken"], index=0)
    with col3:
        st.markdown("<div class='tip'>Tip: If a source fails or is rate-limited, try another source or a past date.</div>", unsafe_allow_html=True)
        run = st.button("Predict next-day HIGH", use_container_width=True)

    # --- Prediction
    if run:
        with st.spinner("Calling FastAPI…"):
            res = _fetch(PREDICT_EP, params={"date": d.isoformat(), "source": source}, timeout=60)

        if isinstance(res, dict) and "__error__" in res:
            st.error(f"API call failed: {res['__error__']}")
        elif not isinstance(res, dict):
            st.error("Unexpected response from API.")
        else:
            k1, k2, k3 = st.columns(3)
            p_high = res.get("predicted_high_t_plus_1")
            tmin   = res.get("predicted_timeHighMin_t_plus_1")
            tutc   = res.get("predicted_timeHighUTC_t_plus_1")

            k1.markdown(f"<div class='kpi'><h3>Predicted High (T+1)</h3><p>{('$' + format(p_high, ',.2f')) if isinstance(p_high,(int,float)) else '—'}</p></div>", unsafe_allow_html=True)
            k2.markdown(f"<div class='kpi'><h3>Predicted Time (min)</h3><p>{(f'{tmin:.0f}' if isinstance(tmin,(int,float)) else '—')}</p></div>", unsafe_allow_html=True)
            k3.markdown(f"<div class='kpi'><h3>Predicted Time (UTC)</h3><p>{tutc or '—'}</p></div>", unsafe_allow_html=True)

            with st.expander("Raw response"):
                st.json(res)

    st.markdown("<div class='section-title'>Live Market Snapshot</div>", unsafe_allow_html=True)
    mk = cg_live()
    if isinstance(mk, dict) and COIN_ID in mk:
        data = mk[COIN_ID]
        a, b, c, dcol = st.columns(4)
        a.markdown(f"<div class='kpi'><h3>Price (USD)</h3><p>${data.get('usd',0):,.2f}</p></div>", unsafe_allow_html=True)
        b.markdown(f"<div class='kpi'><h3>24h Change (%)</h3><p>{data.get('usd_24h_change',0):,.2f}%</p></div>", unsafe_allow_html=True)
        c.markdown(f"<div class='kpi'><h3>Market Cap (USD)</h3><p>${data.get('usd_market_cap',0):,.0f}</p></div>", unsafe_allow_html=True)
        dcol.markdown(f"<div class='kpi'><h3>24h Volume (USD)</h3><p>${data.get('usd_24h_vol',0):,.0f}</p></div>", unsafe_allow_html=True)
    else:
        st.info("CoinGecko might be rate-limited. Please retry.")

    st.markdown("<div class='section-title'>Historical Performance (90 days)</div>", unsafe_allow_html=True)
    ohlc = cg_ohlc(90)
    mc   = cg_market_chart(90)

    # Candlestick
    fig_c = _candlestick(ohlc)
    if fig_c:
        st.plotly_chart(fig_c, use_container_width=True)
    else:
        st.info("Price history unavailable right now.")

    # Extra charts: price line, market cap, volume
    if isinstance(mc, dict):
        charts = []
        if mc.get("prices"):       charts.append(("prices", "Price (USD)"))
        if mc.get("market_caps"):  charts.append(("market_caps", "Market Cap (USD)"))
        if mc.get("total_volumes"):charts.append(("total_volumes", "Trading Volume (USD)"))

        for key, label in charts:
            fig = _line_series(mc.get(key), label, height=280)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>Bitcoin Fundamentals</div>", unsafe_allow_html=True)
    meta = cg_metadata()
    if isinstance(meta, dict) and "name" in meta:
        col1, col2 = st.columns([1,3])
        with col1:
            logo = (meta.get("image") or {}).get("large")
            if logo: st.image(logo, width=72)
        with col2:
            st.write(f"**Name:** {meta['name']}  |  **Symbol:** {(meta.get('symbol') or 'BTC').upper()}")
            cats = ", ".join(meta.get("categories", [])) if isinstance(meta.get("categories", []), list) else "—"
            st.write(f"**Category:** {cats}")
            links = meta.get("links") or {}
            site = (links.get("homepage") or [''])[0]
            explorer = (links.get("blockchain_site") or [''])[0]
            if site or explorer:
                st.write(f"[Website]({site}) | [Explorer]({explorer})")
    else:
        st.info("Fundamentals unavailable right now (likely rate-limit).")

    st.caption("Built by Paul Benjamin Samuel (25142441) · AT3 Group 1 · AML · UTS")
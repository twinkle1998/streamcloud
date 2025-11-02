import streamlit as st
import importlib
import sys, os
from urllib.parse import urlencode
from pathlib import Path

# ============================================================
# --- PATH SETUP (Fixed for student imports)
# ============================================================
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
STUDENTS_PATH = ROOT_DIR / "students"

if str(STUDENTS_PATH) not in sys.path:
    sys.path.append(str(STUDENTS_PATH))

# ============================================================
# --- PAGE CONFIG ---
# ============================================================
st.set_page_config(page_title="AT3 — Crypto Forecast Portal", layout="wide")

# ============================================================
# --- BACKGROUND IMAGE (Loads from URL directly)
# ============================================================
def set_background():
    image_url = "https://i.imgur.com/54zRvLM.png"

    st.markdown(
        f"""
        <style>
        :root {{
          --gold:#E5C045;
          --gold-dark:#caa63d;
          --text:#ffffff;
          --muted:#cccccc;
          --bgveil:rgba(255,255,255,0.25);
        }}

        html, body, .stApp {{
          height: 100vh !important;
          margin: 0 !important;
          padding: 0 !important;
          overflow-x: hidden !important;
          color: var(--text);
          font-family: 'Inter', sans-serif;
          background: none !important;
        }}

        .stApp {{
            position: relative;
            background: none !important;
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url('{image_url}');
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
            background-repeat: no-repeat;
            z-index: -3;
        }}

        .stApp::after {{
            content: "";
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: var(--bgveil);
            z-index: -2;
        }}

        .hero, .token-bar, .team {{
          position: relative;
          z-index: 1;
        }}

        /* HERO SECTION */
        .hero {{
          text-align: center;
          padding: 34px 20px 0 20px;
          height: 41vh;
        }}

        .hero h1 {{
          font-size: 2.5rem;
          font-weight: 800;
          color: #1a1a1a;
          text-shadow: none;
          margin-bottom: 10px;
        }}

        .hero p {{
          color: #2a2a2a;
          font-size: 1.1rem;
          font-weight: 700;
          text-shadow: none;
          margin-bottom: 8px;
        }}

        .hero-desc {{
          color: #000000;
          max-width: 760px;
          margin: 0 auto 10px auto;
          font-size: 1rem;
          line-height: 1.6;
          background: none;
          padding: 10px 16px;
          border-radius: 6px;
        }}

        .hero a.learn-btn {{
          background: var(--gold);
          color: black !important;
          text-decoration: none;
          padding: 10px 28px;
          font-weight: 700;
          border-radius: 6px;
          transition: 0.3s ease;
          display: inline-block;
          box-shadow: 0 0 10px rgba(212,175,55,0.4);
          margin-top: 8px;
          margin-bottom: 18px;
        }}

        .hero a.learn-btn:hover {{
          background: #f0cf68;
          box-shadow: 0 0 18px rgba(212,175,55,0.5);
        }}

        .hero small {{
          display: block;
          color: var(--gold-dark);
          margin-top: 20px;
          font-weight: 700;
          letter-spacing: 1px;
          font-size: 1.2rem;
          text-transform: uppercase;
          text-shadow: 0 0 8px rgba(255,255,255,0.7);
        }}

        /* ✅ TOKEN BAR FIXED FOR PERFECT ALIGNMENT */
        .token-bar {{
          background: rgba(17,17,17,0.92);
          display: flex;
          justify-content: center;
          align-items: stretch;
          gap: 20px;
          min-height: 19vh;
          border-top: 1px solid #1c1c1c;
          border-bottom: 1px solid #1c1c1c;
          padding: 44px 3% 20px 3%;
        }}

        .token {{
          flex: 1 1 20%;
          text-align: center;
          padding: 12px 6px;
          border-radius: 10px;
          transition: all 0.3s ease;
          max-width: 280px;
          cursor: pointer;
          text-decoration: none;
          display: flex;
          flex-direction: column;
          justify-content: flex-start;
          align-items: center;
          height: 100%;
          min-height: 250px; /* consistent height */
        }}

        .token:hover {{
          background: rgba(212,175,55,0.08);
          box-shadow: 0 0 16px rgba(212,175,55,0.25);
          transform: scale(1.03);
        }}

        .token-icon {{
          width: 40px;
          height: 40px;
          margin-bottom: 10px;
        }}

        .token h3 {{
          color: var(--gold);
          font-size: 1rem;
          margin-bottom: 8px;
          height: 2.6em; /* fixed heading height */
          display: flex;
          align-items: center;
          justify-content: center;
        }}

        .token p {{
          color: var(--muted);
          font-size: 0.84rem;
          line-height: 1.4;
          margin: 0;
          flex-grow: 1;
          display: flex;
          align-items: flex-start;
          justify-content: center;
          text-align: center;
          max-width: 90%;
        }}

        /* TEAM SECTION */
        .team {{
          background: rgba(10,10,10,0.92);
          text-align: center;
          height: auto;
          display: flex;
          flex-direction: column;
          justify-content: center;
          border-top: 1px solid #1a1a1a;
          overflow: hidden;
          padding: 20px 0;
        }}

        .team h3 {{
          color: var(--gold);
          margin-bottom: 10px;
        }}

        .member-container {{
          display: flex;
          justify-content: center;
          align-items: stretch;
          gap: 20px;
          padding: 0 3%;
          flex-wrap: wrap;
        }}

        .member {{
          flex: 1 1 20%;
          text-align: center;
          padding: 3px;
          max-width: 250px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: flex-start;
          min-height: 270px;
        }}

        .member-img {{
          flex-shrink: 0;
        }}

        .member-img.twinkle {{
          width: 100px;
          height: 100px;
          border-radius: 50%;
          background: url('https://i.imgur.com/698ujqK.jpeg') center center / cover no-repeat;
          border: 2px solid rgba(212,175,55,0.6);
          margin: 0 auto 3px auto;
        }}

        .member-img.nidhi {{
          width: 100px;
          height: 100px;
          border-radius: 50%;
          background: url('https://i.imgur.com/rB0cI6O.jpeg') center center / cover no-repeat;
          border: 2px solid rgba(212,175,55,0.6);
          margin: 0 auto 3px auto;
        }}

        .member-img.rohan {{
          width: 100px;
          height: 100px;
          border-radius: 50%;
          background: url('https://i.imgur.com/xDN1Aq8.jpeg') center center / cover no-repeat;
          border: 2px solid rgba(212,175,55,0.6);
          margin: 0 auto 3px auto;
        }}

        .member-img.paul {{
          width: 100px;
          height: 100px;
          border-radius: 50%;
          background: url('https://i.imgur.com/Qy5YpQP.jpeg') center center / cover no-repeat;
          border: 2px solid rgba(212,175,55,0.6);
          margin: 0 auto 3px auto;
        }}

        .member p {{
          color: var(--muted);
          font-size: 0.82rem;
          margin: 0;
          line-height: 1.3;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# --- DYNAMIC MODULE LOADER ---
# ============================================================
def load_student_page(student_name: str):
    try:
        module = importlib.import_module(f"{student_name}")
        if hasattr(module, "show_ethereum_tab"):
            module.show_ethereum_tab()
        elif hasattr(module, "app"):
            module.app()
        else:
            st.error(f"⚠️ Module '{student_name}' found but has no callable entry function.")
    except Exception as e:
        st.error(f"❌ Unable to load {student_name}'s module.\n\n{e}")

# ============================================================
# --- URL PARAM HANDLING ---
# ============================================================
query_params = st.query_params
active_student = query_params.get("student")
if isinstance(active_student, list):
    active_student = active_student[0]

# ============================================================
# --- CONDITIONAL PAGE RENDERING ---
# ============================================================
set_background()

if active_student:
    load_student_page(active_student)
else:
    st.markdown(
        """
        <div class="hero">
          <h1>SECURE AND INTELLIGENT WAY TO FORECAST CRYPTOCURRENCY</h1>
          <p>Forecasts and insights for ETH, SOL, XRP, and BTC.</p>

          <div class="hero-desc">
            Our platform provides accessible and transparent cryptocurrency forecasting and visualization.
            It focuses on clarity, data accessibility, and analytical exploration—offering a modern interface
            for studying digital-asset trends without requiring complex models or coding knowledge.
          </div>

          <a href="https://coinmarketcap.com/alexandria/" target="_blank" class="learn-btn">LEARN MORE</a>
          <small>Explore Tokens</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    base_url = "?"
    st.markdown(
        f"""
        <div class="token-bar">
          <a href="{base_url + urlencode({'student':'student_twinkle'})}" target="_self" class="token">
            <img src="https://s2.coinmarketcap.com/static/img/coins/64x64/1027.png" class="token-icon" alt="ETH">
            <h3>Ethereum (ETH)</h3>
            <p>Ethereum forecasting interface with streamlined data visualization and analysis tools.</p>
          </a>
          <a href="{base_url + urlencode({'student':'student_nidhi'})}" target="_self" class="token">
            <img src="https://s2.coinmarketcap.com/static/img/coins/64x64/5426.png" class="token-icon" alt="SOL">
            <h3>Solana (SOL)</h3>
            <p>Feature-rich forecasting dashboard highlighting Solana price dynamics and insights.</p>
          </a>
          <a href="{base_url + urlencode({'student':'student_rohan'})}" target="_self" class="token">
            <img src="https://s2.coinmarketcap.com/static/img/coins/64x64/52.png" class="token-icon" alt="XRP">
            <h3>XRP (XRP)</h3>
            <p>Interactive visual explorer for XRP market movements and performance tracking.</p>
          </a>
          <a href="{base_url + urlencode({'student':'student_paul'})}" target="_self" class="token">
            <img src="https://s2.coinmarketcap.com/static/img/coins/64x64/1.png" class="token-icon" alt="BTC">
            <h3>Bitcoin (BTC)</h3>
            <p>Comprehensive Bitcoin data visualization with trend analysis and exploration tools.</p>
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="team">
          <h3>Our Team</h3>
          <div class="member-container">
            <div class="member">
              <div class="member-img twinkle"></div>
              <p><b>Twinkle</b></p>
              <p>Designed the website. Built a FastAPI for Ethereum and Streamlit-based cryptocurrency forecasting app for real-time tokens next-day high price prediction, with interactive visuals, smooth navigation, and a shareable API for broader use.</p>
            </div>
            <div class="member">
              <div class="member-img nidhi"></div>
              <p><b>Nidhi</b></p>
              <p>Built a FastAPI for Solana and added the information for solana token to be used in forecasting app for real-time tokens next-day high price prediction.</p>
            </div>
            <div class="member">
              <div class="member-img rohan"></div>
              <p><b>Rohan</b></p>
              <p>Built a FastAPI for XRP and added the information for XRP token to be used in forecasting app for real-time tokens next-day high price prediction.</p>
            </div>
            <div class="member">
              <div class="member-img paul"></div>
              <p><b>Paul</b></p>
              <p>Built a FastAPI for Bitcoin and added the information for Bitcoin token to be used in forecasting app for real-time tokens next-day high price prediction.</p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

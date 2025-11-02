# ============================================================
# AT3 — Streamlit Frontend for Cryptocurrency Forecast Portal
# Bright background version (final — fixed contrast)
# ============================================================

import streamlit as st
import importlib
import sys, os, base64
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
# --- BACKGROUND IMAGE (Base64 Embedded, soft but stable)
# ============================================================

def set_background():
    """
    Embeds a semi-transparent background image as Base64.
    Keeps content crisp and high contrast while preventing flicker.
    """
    image_path = ROOT_DIR / "assets" / "background.jpg"
    if image_path.exists():
        encoded = base64.b64encode(image_path.read_bytes()).decode()
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

            /* ✅ Background Layers */
            .stApp {{
                position: relative;
                background: none !important;
            }}

            .stApp::before {{
                content: "";
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background-image: url("data:image/jpg;base64,{encoded}");
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
                background: var(--bgveil); /* slightly less bright for stronger contrast */
                z-index: -2;
            }}

            /* ✅ Content above everything */
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

            /* ✅ Fixed: heading solid, contrasted dark mustard */
            .hero h1 {{
              font-size: 2.5rem;
              font-weight: 800;
              color: #a97904; /* richer dark mustard */
              text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
              margin-bottom: 10px;
            }}

            .hero p {{
              color: #222;
              font-size: 1.1rem;
              font-weight: 600;
              text-shadow: 0 0 6px rgba(255,255,255,0.4);
              margin-bottom: 8px;
            }}

            /* solid black text for paragraph */
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
              margin-top: 70px;
              font-weight: 700;
              letter-spacing: 1px;
              font-size: 1.2rem;
              text-transform: uppercase;
              text-shadow: 0 0 8px rgba(255,255,255,0.7);
            }}

            /* TOKEN BAR */
            .token-bar {{
              background: rgba(17,17,17,0.92);
              display: flex;
              justify-content: center;
              align-items: center;
              gap: 20px;
              height: 19vh;
              border-top: 1px solid #1c1c1c;
              border-bottom: 1px solid #1c1c1c;
              padding: 2px 3%;
            }}

            .token {{
              flex: 1 1 20%;
              text-align: center;
              padding: 8px 6px;
              border-radius: 10px;
              transition: all 0.3s ease;
              max-width: 280px;
              cursor: pointer;
              text-decoration: none;
            }}

            .token:hover {{
              background: rgba(212,175,55,0.08);
              box-shadow: 0 0 16px rgba(212,175,55,0.25);
            }}

            .token h3 {{
              color: var(--gold);
              font-size: 1rem;
              margin-bottom: 3px;
            }}

            .token p {{
              color: var(--muted);
              font-size: 0.84rem;
              line-height: 1.3;
              margin: 0;
            }}

            /* TEAM SECTION */
            .team {{
              background: rgba(10,10,10,0.92);
              text-align: center;
              height: 30vh;
              display: flex;
              flex-direction: column;
              justify-content: center;
              border-top: 1px solid #1a1a1a;
              overflow: hidden;
              padding: 5px 0;
            }}

            .team h3 {{
              color: var(--gold);
              margin-bottom: 5px;
            }}

            .member-container {{
              display: flex;
              justify-content: center;
              align-items: center;
              gap: 20px;
              padding: 0 3%;
            }}

            .member {{
              flex: 1 1 20%;
              text-align: center;
              padding: 3px;
              max-width: 250px;
            }}

            /* Twinkle image */
            .member-img.twinkle {{
              width: 100px;
              height: 100px;
              border-radius: 50%;
              background: url('https://i.imgur.com/srRUQAu.jpeg') center center / cover no-repeat;
              border: 2px solid rgba(212,175,55,0.6);
              margin: 0 auto 3px auto;
            }}

            .member-img {{
              width: 100px;
              height: 100px;
              border-radius: 50%;
              background: linear-gradient(145deg, #1a1a1a, #0d0d0d);
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
    else:
        st.warning("⚠️ Background image not found in assets/.")

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
    # === LANDING PAGE ===
    st.markdown(
        """
        <div class="hero">
          <h1>SECURE AND INTELLIGENT WAY TO FORECAST CRYPTOCURRENCY</h1>
          <p>Machine Learning–Driven Forecasts for ETH, SOL, XRP, and BTC.</p>

          <div class="hero-desc">
            Our project integrates advanced machine-learning models to predict cryptocurrency trends with precision.
            By leveraging real-time APIs and optimized XGBoost algorithms, we aim to make digital-asset forecasting
            accessible, transparent, and data-driven for educational and analytical use.
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
            <h3>Ethereum (ETH)</h3>
            <p>Ethereum forecasting using an Optuna-tuned XGBoost model with live FastAPI integration.</p>
          </a>
          <a href="{base_url + urlencode({'student':'student_nidhi'})}" target="_self" class="token">
            <h3>Solana (SOL)</h3>
            <p>Feature-engineered forecasting model for trend stability and pattern recognition.</p>
          </a>
          <a href="{base_url + urlencode({'student':'student_rohan'})}" target="_self" class="token">
            <h3>XRP (XRP)</h3>
            <p>FastAPI-powered endpoint with real-time API integration and validation pipeline.</p>
          </a>
          <a href="{base_url + urlencode({'student':'student_paul'})}" target="_self" class="token">
            <h3>Bitcoin (BTC)</h3>
            <p>Predict next-day highs using optimized ML regression models for consistent accuracy.</p>
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- TEAM SECTION ---
    st.markdown(
        """
        <div class="team">
          <h3>Our Team</h3>
          <div class="member-container">
            <div class="member">
              <div class="member-img twinkle"></div>
              <p><b>Twinkle</b></p>
              <p>Developed and deployed an Optuna-tuned XGBoost model for Ethereum forecasting, integrated via FastAPI and Streamlit.</p>
            </div>
            <div class="member">
              <div class="member-img"></div>
              <p><b>Nidhi</b></p>
              <p>Solana Integration and Visualization</p>
            </div>
            <div class="member">
              <div class="member-img"></div>
              <p><b>Rohan</b></p>
              <p>XRP Deployment & Validation</p>
            </div>
            <div class="member">
              <div class="member-img"></div>
              <p><b>Paul</b></p>
              <p>Bitcoin Model & API Setup</p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


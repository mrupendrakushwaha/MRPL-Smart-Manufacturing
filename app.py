# ============================================================
# MRPL SMART MANUFACTURING & QUALITY MANAGEMENT SYSTEM
# Role-based access (Admin / Manager / Employee) + Public Products page
# ============================================================

import streamlit as st
import sqlite3
import hashlib
import base64
import re
from pathlib import Path
import pandas as pd
from datetime import date, datetime
from zoneinfo import ZoneInfo

# ============================================================
# APP CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MRPL Smart Manufacturing System",
    page_icon="🏭",
    layout="wide"
)

# ============================================================
# MRPL PROFESSIONAL UI - visual layer only
# ============================================================

APP_DIR = Path(__file__).resolve().parent
MRPL_BG_PATH = APP_DIR / "Mrpl.jpg"

# Load the repository background image safely.
MRPL_BG_DATA = ""
try:
    if MRPL_BG_PATH.is_file():
        MRPL_BG_DATA = base64.b64encode(MRPL_BG_PATH.read_bytes()).decode("utf-8")
except Exception:
    MRPL_BG_DATA = ""

MRPL_BG_CSS = (
    f'url("data:image/jpeg;base64,{MRPL_BG_DATA}")'
    if MRPL_BG_DATA
    else 'none'
)
st.markdown(
    f"""
    <style>

    /* =========================================================
       MRPL — PROFESSIONAL CORPORATE UI
       Replace your existing CSS block with this only.
       No Python functionality is changed.
       ========================================================= */

    :root {{
        --mrpl-bg: #07111f;
        --mrpl-bg-2: #0b1726;
        --mrpl-panel: rgba(15, 31, 49, 0.92);
        --mrpl-panel-2: #102238;
        --mrpl-border: rgba(108, 160, 202, 0.22);
        --mrpl-border-hover: rgba(69, 170, 255, 0.55);

        --mrpl-text: #f5f9fd;
        --mrpl-muted: #9db1c5;

        --mrpl-accent: #1597e5;
        --mrpl-accent-2: #35b9ff;
        --mrpl-green: #19c89a;
        --mrpl-gold: #e7b75b;

        --mrpl-radius: 16px;
        --mrpl-shadow: 0 12px 35px rgba(0,0,0,.28);

        --mrpl-font:
            "Inter",
            "Segoe UI",
            -apple-system,
            BlinkMacSystemFont,
            sans-serif;
    }}

    /* =========================================================
       GLOBAL
       ========================================================= */

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {{
        font-family: var(--mrpl-font) !important;
    }}

    .stApp {{
        background:
            linear-gradient(
                135deg,
                rgba(6,25,48,.78) 0%,
                rgba(10,45,75,.68) 45%,
                rgba(5,13,24,.80) 100%
            ),
            {MRPL_BG_CSS};

        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;

        color: var(--mrpl-text);
    }}

    #MainMenu,
    footer {{
        visibility: hidden;
    }}

    header[data-testid="stHeader"] {{
        background: rgba(4,12,22,.72) !important;
        backdrop-filter: blur(14px);
        border-bottom: 1px solid rgba(255,255,255,.05);
    }}

    .block-container {{
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    /* =========================================================
       TYPOGRAPHY
       ========================================================= */

    h1, h2, h3, h4 {{
        color: var(--mrpl-text) !important;
        font-family: var(--mrpl-font) !important;
    }}

    p, span, label, .stMarkdown {{
        font-family: var(--mrpl-font);
    }}

    h1 {{
        font-size: 2.35rem !important;
        font-weight: 900 !important;
        letter-spacing: -1px;
        margin-bottom: 22px !important;

        background: linear-gradient(
            90deg,
            #ffffff 0%,
            #bde5ff 55%,
            #72caff 100%
        );

        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;

        padding-bottom: 16px;
        border-bottom: 1px solid rgba(75,170,230,.18);
    }}

    h2 {{
        font-size: 1.65rem !important;
        font-weight: 800 !important;
        letter-spacing: -.4px;

        border-left: 4px solid var(--mrpl-accent);
        padding-left: 13px;
        margin-top: 25px;
    }}

    h3 {{
        font-size: 1.25rem !important;
        font-weight: 750 !important;
    }}

    small,
    .stCaption,
    [data-testid="stCaptionContainer"] {{
        color: var(--mrpl-muted) !important;
    }}

    hr {{
        border: none !important;
        border-top: 1px solid rgba(120,170,210,.14) !important;
        margin: 1.8rem 0 !important;
    }}

    /* =========================================================
       SIDEBAR
       ========================================================= */

    section[data-testid="stSidebar"] {{
        background:
            linear-gradient(
                180deg,
                #081a2c 0%,
                #061322 55%,
                #040d18 100%
            ) !important;

        border-right: 1px solid rgba(69,160,220,.20);
        box-shadow: 8px 0 30px rgba(0,0,0,.22);
    }}

    section[data-testid="stSidebar"] > div {{
        background: transparent !important;
    }}

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        border: none !important;
        padding: 0 !important;
        background: none !important;
        -webkit-text-fill-color: var(--mrpl-text) !important;
    }}

    /* ---- Sidebar collapse / expand toggle (top-left control) ---- */
    header[data-testid="stHeader"] button[aria-label*="sidebar"],
    header[data-testid="stHeader"] button[title*="sidebar"],
    header[data-testid="stHeader"] button[aria-label*="Sidebar"],
    header[data-testid="stHeader"] button[title*="Sidebar"] {{
        background: linear-gradient(135deg, #10243c, #081627) !important;
        border: 1px solid rgba(86,158,204,.30) !important;
        border-radius: 10px !important;
        color: var(--mrpl-accent-2) !important;
        box-shadow: 0 4px 14px rgba(0,0,0,.25) !important;
        transition: all .18s ease !important;
    }}

    header[data-testid="stHeader"] button[aria-label*="sidebar"]:hover,
    header[data-testid="stHeader"] button[title*="sidebar"]:hover,
    header[data-testid="stHeader"] button[aria-label*="Sidebar"]:hover,
    header[data-testid="stHeader"] button[title*="Sidebar"]:hover {{
        background: linear-gradient(135deg, #147fb8, #0b4f7d) !important;
        border-color: #4bc3ff !important;
        color: #ffffff !important;
        transform: scale(1.04) !important;
    }}

    header[data-testid="stHeader"] button svg {{
        color: currentColor !important;
        fill: currentColor !important;
    }}

    /* ---- Collapsed sidebar arrow toggle (top-left ">>" control) ---- */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stExpandSidebarButton"],
    [data-testid*="Sidebar"][data-testid*="ollapse"],
    [data-testid*="Sidebar"][data-testid*="xpand"] {{
        background: linear-gradient(135deg, #1a9ddd, #0b4f7d) !important;
        border: 2px solid #4bc3ff !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(0,0,0,.45) !important;
        padding: 4px !important;
        opacity: 1 !important;
        z-index: 999999 !important;
    }}

    [data-testid="collapsedControl"] *,
    [data-testid="stSidebarCollapsedControl"] *,
    [data-testid="stSidebarCollapseButton"] *,
    [data-testid="stExpandSidebarButton"] *,
    [data-testid*="Sidebar"][data-testid*="ollapse"] *,
    [data-testid*="Sidebar"][data-testid*="xpand"] * {{
        color: #ffffff !important;
        fill: #ffffff !important;
        opacity: 1 !important;
    }}

    [data-testid="collapsedControl"]:hover,
    [data-testid="stSidebarCollapsedControl"]:hover,
    [data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="stExpandSidebarButton"]:hover {{
        background: linear-gradient(135deg, #35b9ff, #147fb8) !important;
        transform: scale(1.08) !important;
    }}

    /* ---- Unified profile card (avatar + name + role) ---- */
    .mrpl-profile-card {{
        display: flex;
        align-items: center;
        gap: 12px;

        background: linear-gradient(
            135deg,
            rgba(16, 42, 68, .95),
            rgba(9, 26, 44, .95)
        );

        border: 1px solid rgba(86, 158, 204, .22);
        border-radius: 13px;

        padding: 13px 14px;
        margin-bottom: 12px;

        box-shadow: 0 7px 20px rgba(0,0,0,.20);
    }}

    .mrpl-profile-avatar {{
        flex-shrink: 0;
        width: 40px;
        height: 40px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 50%;

        background: linear-gradient(
            135deg,
            var(--mrpl-accent),
            var(--mrpl-accent-2)
        );

        color: #ffffff;
        font-size: 14px;
        font-weight: 800;
        letter-spacing: .3px;
    }}

    .mrpl-profile-info {{
        min-width: 0;
    }}

    .mrpl-profile-name {{
        color: #f5f9fd;
        font-size: 14px;
        font-weight: 750;
        line-height: 1.25;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .mrpl-profile-role {{
        color: #7fb8e0;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .4px;
        text-transform: uppercase;
        margin-top: 1px;
    }}

    /* ---- Logout button ---- */
    section[data-testid="stSidebar"] .stButton > button {{
        background: linear-gradient(135deg, #147fbd, #075783) !important;
        border: 1px solid rgba(73, 190, 245, .42) !important;
        border-radius: 12px !important;
        min-height: 46px !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        box-shadow: 0 7px 18px rgba(0,0,0,.22) !important;
    }}

    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: linear-gradient(135deg, #1a9ddd, #086a9e) !important;
        border-color: #5bc9ff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 24px rgba(0,0,0,.30) !important;
    }}

    /* ---- Navigation section heading ---- */
    .mrpl-nav-heading {{
        color: #7d97ad !important;
        font-size: 11px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.4px !important;
        margin: 4px 0 10px 2px !important;
    }}

    section[data-testid="stSidebar"] .stRadio > label {{
        display: none !important;
    }}

    /* ---- Navigation items — clean list, no native radio dot ---- */
    section[data-testid="stSidebar"] [role="radiogroup"] {{
        gap: 3px !important;
    }}

    section[data-testid="stSidebar"] [role="radiogroup"] > label {{
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        padding: 10px 12px !important;
        margin-bottom: 2px !important;
        transform: none !important;
        gap: 10px !important;
    }}

    section[data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child {{
        display: none !important;
    }}

    section[data-testid="stSidebar"] [role="radiogroup"] > label:hover {{
        background: rgba(21,151,229,.09) !important;
        border-color: rgba(55,177,245,.22) !important;
        transform: none !important;
    }}

    section[data-testid="stSidebar"] [role="radiogroup"] > label p {{
        color: #b7c9db !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
    }}

    section[data-testid="stSidebar"] [role="radiogroup"] > label:has(
        input[type="radio"]:checked
    ) {{
        background: linear-gradient(
            90deg,
            rgba(21,151,229,.22),
            rgba(21,151,229,.05)
        ) !important;
        border-color: rgba(48,178,241,.30) !important;
        box-shadow: inset 3px 0 0 var(--mrpl-accent-2) !important;
    }}

    section[data-testid="stSidebar"] [role="radiogroup"] > label:has(
        input[type="radio"]:checked
    ) p {{
        color: #ffffff !important;
        font-weight: 750 !important;
    }}

    section[data-testid="stSidebar"] .stAlert {{
        background: rgba(255,255,255,.035);
        border: 1px solid rgba(100,160,205,.16);
        border-radius: 12px;
    }}

    /* =========================================================
       APP HEADER (main title bar)
       ========================================================= */

    .mrpl-app-header {{
        display: flex;
        align-items: center;
        gap: 16px;

        background: linear-gradient(
            135deg,
            rgba(16, 42, 68, .92),
            rgba(8, 20, 34, .92)
        );

        border: 1px solid rgba(86, 158, 204, .22);
        border-left: 4px solid var(--mrpl-accent);
        border-radius: var(--mrpl-radius);

        padding: 18px 24px;
        margin: 20px 0 28px 0;

        box-shadow: var(--mrpl-shadow);
    }}

    .mrpl-app-header-mark {{
        flex-shrink: 0;
        width: 46px;
        height: 46px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 12px;

        background: linear-gradient(
            135deg,
            var(--mrpl-accent),
            var(--mrpl-accent-2)
        );

        font-size: 22px;
    }}

    .mrpl-app-header-title {{
        color: #ffffff;
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -.4px;
        line-height: 1.2;
    }}

    .mrpl-app-header-subtitle {{
        color: var(--mrpl-muted);
        font-size: 12.5px;
        font-weight: 600;
        letter-spacing: .3px;
        margin-top: 3px;
    }}

    .mrpl-page-title {{
        display: flex;
        align-items: center;
        gap: 10px;

        color: var(--mrpl-text);
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -.3px;

        border-left: 4px solid var(--mrpl-accent);
        padding: 4px 0 4px 13px;

        margin: 4px 0 22px 0;
    }}

    .mrpl-page-title-icon {{
        font-size: 22px;
    }}

    /* =========================================================
       TABS (Add / Edit / Delete etc.) — clean segmented control
       ========================================================= */

    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background: rgba(6,16,28,.55);
        border: 1px solid rgba(100,160,205,.25);
        border-radius: 12px;
        padding: 5px;
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 40px;
        border-radius: 9px !important;
        background: rgba(9,27,45,.92) !important;
        border: 1px solid rgba(100,160,205,.28) !important;
        color: #bfe0ff !important;
        font-weight: 700 !important;
        font-size: 13.5px !important;
        padding: 0 18px !important;
        transition: all .18s ease;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        color: #ffffff !important;
        background: rgba(21,151,229,.28) !important;
        border-color: rgba(69,170,255,.55) !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(
            135deg, #ef4444, #b91c1c) !important;
        color: #ffffff !important;
        box-shadow: 0 5px 14px rgba(0,0,0,.25);
    }}
    
    .stTabs [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}

    .stTabs [data-baseweb="tab-border"] {{
        display: none !important;
    }}

    /* =========================================================
       METRIC CARDS
       ========================================================= */


    div[data-testid="stMetric"] {{
        position: relative;

        background:
            linear-gradient(
                145deg,
                rgba(18,45,70,.96),
                rgba(9,27,45,.96)
            ) !important;

        border: 1px solid rgba(86,158,204,.20);
        border-radius: var(--mrpl-radius);

        padding: 19px 20px;

        box-shadow: 0 9px 25px rgba(0,0,0,.22);

        overflow: hidden;

        transition:
            transform .18s ease,
            border-color .18s ease,
            box-shadow .18s ease;
    }}

    div[data-testid="stMetric"]::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;

        background:
            linear-gradient(
                90deg,
                var(--mrpl-accent),
                var(--mrpl-accent-2),
                var(--mrpl-green)
            );
    }}

    div[data-testid="stMetric"]:hover {{
        transform: translateY(-4px);
        border-color: rgba(50,174,244,.42);
        box-shadow: 0 15px 32px rgba(0,0,0,.32);
    }}

    div[data-testid="stMetricLabel"] {{
        color: #91a9be !important;
        font-size: 11.5px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: .7px;
    }}

    div[data-testid="stMetricValue"] {{
        color: #ffffff !important;
        font-size: 30px !important;
        font-weight: 850 !important;
        letter-spacing: -.6px;
    }}

    /* =========================================================
       TABS
       ========================================================= */

    button[data-baseweb="tab"],
    [data-testid="stTab"],
    div[data-testid="stTabs"] button,
    div[data-testid="stTabs"] [role="tab"] {{
        background: rgba(9,27,45,.92) !important;
        border: 1px solid rgba(100,160,205,.28) !important;
        border-radius: 9px !important;
        color: #bfe0ff !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        padding: 11px 18px !important;
        transition: all .18s ease;
    }}

    button[data-baseweb="tab"]:hover,
    [data-testid="stTab"]:hover,
    div[data-testid="stTabs"] button:hover,
    div[data-testid="stTabs"] [role="tab"]:hover {{
        color: #ffffff !important;
        background: rgba(21,151,229,.28) !important;
        border-color: rgba(69,170,255,.55) !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"],
    [data-testid="stTab"][aria-selected="true"],
    div[data-testid="stTabs"] button[aria-selected="true"],
    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
        color: #ffffff !important;
        background: linear-gradient(135deg, #ef4444, #b91c1c) !important;
        border-color: transparent !important;
    }}

    div[data-baseweb="tab-highlight"] {{
        background:
            linear-gradient(
                90deg,
                var(--mrpl-accent),
                var(--mrpl-accent-2)
            ) !important;

        height: 3px !important;
        border-radius: 5px;
    }}

    div[data-baseweb="tab-border"] {{
        background: rgba(100,160,205,.12) !important;
    }}

    /* =========================================================
       INPUTS
       ========================================================= */

    div[data-baseweb="input"],
    div[data-baseweb="select"],
    div[data-baseweb="base-input"],
    textarea,
    input {{
        background: rgba(8,27,45,.95) !important;
        color: #ffffff !important;

        border: 1px solid rgba(92,151,193,.22) !important;
        border-radius: 10px !important;

        transition:
            border-color .18s ease,
            box-shadow .18s ease;
    }}

    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"]:focus-within {{
        border-color: var(--mrpl-accent) !important;
        box-shadow:
            0 0 0 1px rgba(21,151,229,.35),
            0 0 18px rgba(21,151,229,.10) !important;
    }}

    div[data-baseweb="select"] * {{
        color: #ffffff !important;
    }}

    label p {{
        color: #cbd9e5 !important;
        font-weight: 650 !important;
        font-size: 13px !important;
    }}

    /* =========================================================
       BUTTONS
       ========================================================= */

    .stButton > button,
    .stLinkButton > a,
    .stDownloadButton > button,
    .stFormSubmitButton > button {{

        min-height: 44px;

        border-radius: 10px !important;

        border: 1px solid rgba(67,166,220,.35) !important;

        background:
            linear-gradient(
                135deg,
                #138bd0,
                #07578c
            ) !important;

        color: #ffffff !important;

        font-weight: 750 !important;
        letter-spacing: .15px;

        box-shadow:
            0 7px 18px rgba(0,0,0,.22);

        transition:
            transform .18s ease,
            box-shadow .18s ease,
            border-color .18s ease;
    }}

    .stButton > button:hover,
    .stLinkButton > a:hover,
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {{
        transform: translateY(-2px);

        border-color: #48bfff !important;

        box-shadow:
            0 11px 25px rgba(0,0,0,.32),
            0 0 18px rgba(21,151,229,.12);

        background:
            linear-gradient(
                135deg,
                #18a0eb,
                #086ca8
            ) !important;
    }}

    .stButton > button[kind="primary"] {{
        background:
            linear-gradient(
                135deg,
                #18c79a,
                #0b8d73
            ) !important;

        border-color: rgba(54,222,180,.55) !important;
    }}

    .stButton > button[kind="primary"]:hover {{
        background:
            linear-gradient(
                135deg,
                #25dfb0,
                #0da082
            ) !important;
    }}

    /* =========================================================
       DATAFRAME
       ========================================================= */

    div[data-testid="stDataFrame"] {{
        border: 1px solid rgba(91,155,198,.22);
        border-radius: 14px;
        overflow: hidden;

        box-shadow:
            0 10px 28px rgba(0,0,0,.22);
    }}

    /* =========================================================
       ALERTS
       ========================================================= */

    div[data-testid="stAlert"] {{
        border-radius: 12px !important;
        border: 1px solid rgba(94,160,204,.20) !important;
        background: rgba(12,31,50,.88) !important;
    }}

    /* =========================================================
       E-COMMERCE / PUBLIC MRPL PAGE
       ========================================================= */

    .store-header {{
        background:
            linear-gradient(
                135deg,
                rgba(255,255,255,.98),
                rgba(241,247,252,.98)
            );

        border: 1px solid #d8e3ec;
        border-radius: 18px;

        padding: 17px 25px;
        margin-bottom: 22px;

        box-shadow:
            0 10px 28px rgba(0,0,0,.20);

        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .store-brand {{
        color: #09243c !important;
        font-size: 28px;
        font-weight: 900;
        line-height: 1.1;
        letter-spacing: -.7px;
    }}

    .store-tagline {{
        color: #64788b !important;
        font-size: 12.5px;
        margin-top: 5px;
        font-weight: 600;
    }}

    /* =========================================================
       HERO
       ========================================================= */

    .store-hero {{
        position: relative;

        min-height: 330px;

        display: flex;
        align-items: center;

        padding: 55px;

        border-radius: 24px;
        overflow: hidden;

        margin-bottom: 32px;

        background-image:
            linear-gradient(
                100deg,
                rgba(5,22,42,.78) 0%,
                rgba(8,38,62,.62) 43%,
                rgba(10,45,68,.38) 100%
            ),
            {MRPL_BG_CSS};

        background-size: cover;
        background-position: center;

        border: 1px solid rgba(255,255,255,.10);

        box-shadow:
            0 18px 45px rgba(0,0,0,.35);
    }}

    .store-hero::after {{
        content: "";

        position: absolute;

        left: 0;
        bottom: 0;

        width: 100%;
        height: 3px;

        background:
            linear-gradient(
                90deg,
                #168fd7,
                #35b9ff,
                #19c89a,
                transparent
            );
    }}

    .store-hero-content {{
        max-width: 760px;
        position: relative;
        z-index: 2;
    }}

    .store-badge {{
        display: inline-block;

        padding: 8px 15px;

        border-radius: 999px;

        background: rgba(22,151,229,.14);

        border: 1px solid rgba(88,195,255,.35);

        color: #bfe9ff;

        font-size: 11px;
        font-weight: 800;

        letter-spacing: .8px;

        text-transform: uppercase;

        margin-bottom: 17px;
    }}

    .store-hero-title {{
        color: #ffffff !important;

        font-size: 46px;

        line-height: 1.08;

        font-weight: 900;

        letter-spacing: -1.2px;

        margin-bottom: 15px;
    }}

    .store-hero-text {{
        color: #d5e4ef !important;

        font-size: 15px;

        line-height: 1.75;

        font-weight: 450;

        max-width: 690px;
    }}

    /* =========================================================
       STORE SECTIONS
       ========================================================= */

    .store-section-title {{
        color: #ffffff !important;

        font-size: 29px;

        font-weight: 850;

        letter-spacing: -.5px;

        margin: 17px 0 5px 0;
    }}

    .store-section-subtitle {{
        color: #91aabd !important;

        font-size: 13.5px;

        line-height: 1.6;

        margin-bottom: 20px;
    }}

    /* =========================================================
       PRODUCT CARDS
       ========================================================= */

    .product-name {{
        color: #ffffff !important;

        font-size: 18px;

        font-weight: 800;

        margin-top: 9px;
        margin-bottom: 5px;
    }}

    .product-category {{
        color: #4fc2ff !important;

        font-size: 10.5px;

        font-weight: 800;

        text-transform: uppercase;

        letter-spacing: .9px;
    }}

    .product-description {{
        color: #aebfd0 !important;

        font-size: 13px;

        line-height: 1.6;
    }}

    /* =========================================================
       CATEGORY CHIPS
       ========================================================= */

    .category-chip {{
        background:
            linear-gradient(
                145deg,
                rgba(22,49,73,.82),
                rgba(10,30,49,.90)
            );

        border: 1px solid rgba(80,151,199,.22);

        border-radius: 13px;

        padding: 16px;

        color: #edf6fc !important;

        font-weight: 750;

        text-align: center;

        box-shadow:
            0 7px 18px rgba(0,0,0,.18);

        transition:
            transform .18s ease,
            border-color .18s ease,
            background .18s ease;
    }}

    .category-chip:hover {{
        transform: translateY(-3px);

        border-color: rgba(57,183,248,.50);

        background:
            linear-gradient(
                145deg,
                rgba(20,63,94,.95),
                rgba(10,39,63,.95)
            );
    }}

    /* =========================================================
       GLASS CONTAINERS
       ========================================================= */

    div[data-testid="stExpander"] {{
        background: rgba(11,30,48,.72) !important;

        border: 1px solid rgba(92,153,195,.18) !important;

        border-radius: 13px !important;

        box-shadow:
            0 8px 22px rgba(0,0,0,.16);
    }}

    /* =========================================================
       SCROLLBAR
       ========================================================= */

    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: #06111d;
    }}

    ::-webkit-scrollbar-thumb {{
        background: #1d4f70;
        border-radius: 10px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: #287ba8;
    }}

    /* =========================================================
       MOBILE
       ========================================================= */

    @media (max-width: 768px) {{

        .block-container {{
            padding: 1.1rem .8rem 2rem .8rem;
        }}

        h1 {{
            font-size: 1.75rem !important;
            line-height: 1.15;
        }}

        h2 {{
            font-size: 1.4rem !important;
        }}

        h3 {{
            font-size: 1.15rem !important;
        }}

        .store-header {{
            padding: 14px 16px;
            border-radius: 14px;
        }}

        .store-brand {{
            font-size: 21px;
        }}

        .store-tagline {{
            font-size: 10.5px;
        }}

        .store-hero {{
            min-height: 270px;
            padding: 30px 25px;
            border-radius: 19px;
        }}

        .store-hero-title {{
            font-size: 29px;
            letter-spacing: -.6px;
        }}

        .store-hero-text {{
            font-size: 13.5px;
            line-height: 1.65;
        }}

        .store-section-title {{
            font-size: 24px;
        }}

        div[data-testid="stMetric"] {{
            padding: 15px;
        }}

        div[data-testid="stMetricValue"] {{
            font-size: 25px !important;
        }}
    }}

    /* =========================================================
       SMALL PREMIUM DETAILS
       ========================================================= */

    .stProgress > div > div {{
        background:
            linear-gradient(
                90deg,
                #168fd7,
                #35b9ff,
                #19c89a
            ) !important;
    }}

    .stSpinner > div {{
        border-top-color: var(--mrpl-accent) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# JS SAFETY-NET: force-color tabs (Add/Edit/Delete etc.) even if
# Streamlit renames its internal CSS hooks in future versions.
# Targets the standard ARIA role="tab", which does not change.
# ============================================================
import streamlit.components.v1 as components

components.html(
    """
    <script>
    function mrplStyleTabs() {
        const doc = window.parent.document;
        doc.querySelectorAll('[role="tab"]').forEach(function(el) {
            if (el.getAttribute('aria-selected') === 'true') {
                el.style.setProperty('background', 'linear-gradient(135deg, #ef4444, #b91c1c)', 'important');
                el.style.setProperty('color', '#ffffff', 'important');
                el.style.setProperty('border', '1px solid transparent', 'important');
            } else {
                el.style.setProperty('background', 'rgba(9,27,45,.92)', 'important');
                el.style.setProperty('color', '#bfe0ff', 'important');
                el.style.setProperty('border', '1px solid rgba(100,160,205,.28)', 'important');
            }
            el.style.setProperty('border-radius', '9px', 'important');
            el.style.setProperty('font-weight', '700', 'important');
        });
    }
    mrplStyleTabs();
    const mrplObserver = new MutationObserver(mrplStyleTabs);
    mrplObserver.observe(window.parent.document.body, {
        childList: true, subtree: true, attributes: true
    });
    </script>
    """,
    height=0,
)

DB_PATH = "mrpl.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    # No FOREIGN KEY constraints are declared anywhere in this schema, and
    # turning this pragma on made DROP TABLE (used for schema migration
    # below) fail against leftover databases from earlier app versions.
    conn.execute("PRAGMA foreign_keys = OFF")
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# MRPL attendance/business time zone
INDIA_TZ = ZoneInfo("Asia/Kolkata")

def now_india():
    return datetime.now(INDIA_TZ)

# ============================================================
# DATABASE INITIALIZATION
# ============================================================

# Expected columns (excluding auto id) for every table this app relies on.
# If a table already exists on disk (e.g. leftover mrpl.db from an older
# deploy) but is missing any of these columns, it gets dropped and rebuilt
# fresh below instead of throwing "table X has no column named Y".
EXPECTED_SCHEMA = {
    "users": ["username", "password_hash", "role", "employee_id", "is_active"],
    "employees": ["full_name", "designation", "department", "phone", "email", "joining_date", "status"],
    "attendance": ["employee_id", "employee_name", "att_date", "status", "check_in", "check_out"],
    "leave_requests": ["employee_id", "employee_name", "leave_type", "start_date", "end_date", "reason", "status"],
    "tasks": ["employee_id", "employee_name", "title", "description", "due_date", "status"],
    "raw_materials": ["material_name", "category", "current_stock", "minimum_stock", "unit", "supplier", "unit_price", "last_updated"],
    "production": ["batch_no", "product_name", "planned_quantity", "actual_quantity", "start_date", "end_date", "status", "machine", "operator"],
    "quality_control": ["batch_no", "product_name", "test_date", "parameter", "result", "status", "inspector", "remarks"],
    "finished_goods": ["product_name", "batch_no", "quantity", "unit", "warehouse_location", "production_date", "expiry_date", "status"],
    "orders": ["order_no", "customer_name", "product_name", "quantity", "order_date", "delivery_date", "status"],
    "dispatch": ["dispatch_no", "order_no", "product_name", "quantity", "dispatch_date", "vehicle_no", "driver_name", "status"],
    "products": ["category", "product_name", "description", "image_url", "is_active"],
}


def _migrate_schema(cur):
    cur.execute("PRAGMA foreign_keys = OFF")
    for table, expected_cols in EXPECTED_SCHEMA.items():
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if cur.fetchone() is None:
            continue
        cur.execute(f"PRAGMA table_info({table})")
        existing_cols = {row[1] for row in cur.fetchall()}
        if not set(expected_cols).issubset(existing_cols):
            cur.execute(f"DROP TABLE {table}")


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    _migrate_schema(cur)
    conn.commit()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            employee_id INTEGER,
            is_active INTEGER DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            designation TEXT,
            department TEXT,
            phone TEXT,
            email TEXT,
            joining_date TEXT,
            status TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            employee_name TEXT,
            att_date TEXT,
            status TEXT,
            check_in TEXT,
            check_out TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            employee_name TEXT,
            leave_type TEXT,
            start_date TEXT,
            end_date TEXT,
            reason TEXT,
            status TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            employee_name TEXT,
            title TEXT,
            description TEXT,
            due_date TEXT,
            status TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name TEXT NOT NULL,
            category TEXT,
            current_stock REAL,
            minimum_stock REAL,
            unit TEXT,
            supplier TEXT,
            unit_price REAL,
            last_updated TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_no TEXT NOT NULL,
            product_name TEXT,
            planned_quantity REAL,
            actual_quantity REAL,
            start_date TEXT,
            end_date TEXT,
            status TEXT,
            machine TEXT,
            operator TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS quality_control (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_no TEXT NOT NULL,
            product_name TEXT,
            test_date TEXT,
            parameter TEXT,
            result TEXT,
            status TEXT,
            inspector TEXT,
            remarks TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS finished_goods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            batch_no TEXT,
            quantity REAL,
            unit TEXT,
            warehouse_location TEXT,
            production_date TEXT,
            expiry_date TEXT,
            status TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT NOT NULL,
            customer_name TEXT,
            product_name TEXT,
            quantity REAL,
            order_date TEXT,
            delivery_date TEXT,
            status TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dispatch (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dispatch_no TEXT NOT NULL,
            order_no TEXT,
            product_name TEXT,
            quantity REAL,
            dispatch_date TEXT,
            vehicle_no TEXT,
            driver_name TEXT,
            status TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            product_name TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            is_active INTEGER DEFAULT 1
        )
    """)

    conn.commit()

    # ---------------- CLEAN INITIAL DEMO DATA ----------------
    # Run only once for the upgraded version. This removes old demo/test
    # records and old login accounts, while keeping the public product catalog.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS system_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    cleanup_key = "clean_demo_data_v2"
    cleaned = cur.execute(
        "SELECT value FROM system_meta WHERE key = ?",
        (cleanup_key,)
    ).fetchone()

    if not cleaned:
        for table in [
            "attendance",
            "leave_requests",
            "tasks",
            "employees",
            "raw_materials",
            "production",
            "quality_control",
            "finished_goods",
            "orders",
            "dispatch",
            "users",
        ]:
            cur.execute(f"DELETE FROM {table}")

        cur.execute(
            "INSERT INTO system_meta (key, value) VALUES (?, ?)",
            (cleanup_key, "done")
        )

    # --------------------------------------------------------
    # --------------------------------------------------------
    # MRPL PRODUCT CATALOG
    # Images are stored inside the same GitHub repository.
    # Use LOCAL FILE PATHS instead of remote GitHub URLs.
    # This avoids raw.githubusercontent.com / URL encoding issues.
    # --------------------------------------------------------

    APP_DIR = Path(__file__).resolve().parent

    def product_image(filename):
        """Return a local image path from the repository ROOT."""
        path = APP_DIR / filename
        return str(path) if path.exists() else ""

    def product_images(folder, filenames):
        paths = []
        for filename in filenames:
            path = APP_DIR / folder / filename
            if path.exists():
                paths.append(str(path))
        return ",".join(paths)

    product_refresh_key = "mrpl_official_products_v9_root_product_folders"

    product_refreshed = cur.execute(
        "SELECT value FROM system_meta WHERE key = ?",
        (product_refresh_key,)
    ).fetchone()

    if not product_refreshed:
        cur.execute("DELETE FROM products")

        catalog = [
           (
        "Shaped Products",
        "Fireclay & High Alumina Bricks",
        "Refractory bricks with high thermal strength; high alumina grades are available up to 92% Al2O3.",
                product_image("Fireclay and High Alumina Bricks.jpg")
            ),
            (
        "Shaped Products",
        "Pre-Cast Pre-Fired (PCPF) Blocks",
        "Custom-engineered pre-fired refractory blocks for ready-to-install applications.",
               product_image("Pre-Cast Pre-Fired (PCPF) Blocks.jpg")
             ),
            
            # High & Medium Purity Dense Castables
           (
                "Unshaped Products",
                "High & Medium Purity Dense Castables",
                "Dense castables designed for high-temperature industrial applications with high strength and thermal-shock resistance.",
                product_images(
                    "High & Medium Purity Dense Castables",
                    ["Maxcast.jpg", "Maxcrete.jpg", "Maxheat.jpg"]
                )
            ),

            # Low & Ultra Low Cement Castables
            (
                "Unshaped Products",
                "Low & Ultra Low Cement Castables",
                "Low-cement monolithic refractories designed for high strength, durability and thermal performance.",
                product_images(
                    "Low & Ultra Low Cement Castables",
                    ["Maxmon65.jpg", "Maxmon70.jpg", "Maxmon80.jpg"]
                )
            ),

            # Insulating Castables
            (
                "Unshaped Products",
                "Insulating Castables",
                "Lightweight insulating castables for thermal insulation and reduced heat loss.",
                product_images(
                    "Insulating Castables",
                    ["Maxlyte11.jpg", "Maxlyte13.jpg", "Maxlyte7.jpg"]
                )
            ),

            # Plastic Masses
            (
                "Unshaped Products",
                "Plastic Masses",
                "Plastic refractory masses for installation in complex geometries and high-temperature zones.",
                product_images(
                    "Plastics Masses",
                    ["Maxphos80.jpg", "Maxphos90.jpg", "Maxplast.jpg"]
                )
            ),

            # High Alumina Cement & Binder
            (
                "Unshaped Products",
                "High Alumina Cement & Binder",
                "High alumina refractory cements and binders used in refractory castable systems.",
                product_images(
                    "High Alumina Cement & Binder",
                    ["Calcem50.jpg", "Calcem70.jpg", "Calcem75.jpg"]
                )
            ),

            # Grouting Materials
            (
                "Unshaped Products",
                "Grouting Materials",
                "Refractory grouting compounds for installation and maintenance applications.",
                product_images(
                    "Grouting Compound",
                    ["Maxgrout20.jpg", "Maxgrout30.jpg", "Maxgrout8.jpg"]
                )
            ),

            # Fireclay & High Alumina Mortars
            (
                "Unshaped Products",
                "Fireclay & High Alumina Mortars",
                "Heat-setting and air-setting refractory mortars for reliable jointing and installation.",
                product_images(
                    "Fire Clay & High Alumina Mortars (Heat & Air Setting)",
                    ["Maxset50finemonolithic.jpg", "Maxset50monolithic.jpg", "Mortar75.jpg"]
                )
            ),

        ]

        cur.executemany(
            """
            INSERT INTO products
            (category, product_name, description, image_url, is_active)
            VALUES (?, ?, ?, ?, ?)
            """,
            [(cat, name, desc, img, 1) for cat, name, desc, img in catalog]
        )

        cur.execute(
            "INSERT INTO system_meta (key, value) VALUES (?, ?)",
            (product_refresh_key, "done")
        )

    conn.commit()
    conn.close()


init_db()


def ensure_bootstrap_admins():
    """
    Create/update the two initial Admin accounts from Streamlit Secrets.

    Required Secrets:

    [admin_upendra]
    username = "Upendra"
    password = "..."

    [admin_sandeep]
    username = "Sandeephaldkar"
    password = "..."

    Passwords never appear in app.py or GitHub.
    """
    try:
        upendra = st.secrets.get("admin_upendra", {})
        sandeep = st.secrets.get("admin_sandeep", {})
    except Exception:
        upendra = {}
        sandeep = {}

    admins = [
        (str(upendra.get("username", "Upendra")).strip(), str(upendra.get("password", ""))),
        (str(sandeep.get("username", "Sandeephaldkar")).strip(), str(sandeep.get("password", ""))),
    ]

    conn = get_connection()

    # Reset Admin IDs once: keep existing Admin accounts
    conn.execute("""
    UPDATE users
    SET id = CASE
        WHEN username = 'Upendra' THEN 1
        WHEN username = 'Sandeephaldkar' THEN 2
        ELSE id
    END
    WHERE username IN ('Upendra', 'Sandeephaldkar')
""")

    conn.execute("DELETE FROM sqlite_sequence WHERE name = 'users'")
    conn.execute("""
    INSERT INTO sqlite_sequence(name, seq)
    SELECT 'users', MAX(id) FROM users
    WHERE NOT EXISTS (
        SELECT 1 FROM sqlite_sequence WHERE name = 'users'
    )
""")

    for admin_username, admin_password in admins:
        if not admin_username or not admin_password:
            continue

        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (admin_username,)
        ).fetchone()

        if existing:
            conn.execute(
                """
                UPDATE users
                SET password_hash = ?, role = 'Admin',
                    employee_id = NULL, is_active = 1
                WHERE id = ?
                """,
                (hash_password(admin_password), existing[0])
            )
        else:
            conn.execute(
                """
                INSERT INTO users
                (username, password_hash, role, employee_id, is_active)
                VALUES (?, ?, 'Admin', NULL, 1)
                """,
                (admin_username, hash_password(admin_password))
            )

    conn.commit()
    conn.close()


ensure_bootstrap_admins()


# ============================================================
# GENERIC DB HELPERS
# ============================================================

def load_data(table, where="", params=()):
    conn = get_connection()
    query = f"SELECT * FROM {table}"
    if where:
        query += f" WHERE {where}"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def run_query(query, params=()):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, params)
    inserted_rowid = cur.lastrowid

    # India time for created_at
    if query.strip().upper().startswith("INSERT"):
        try:
            table_name = query.strip().split()[2]

            cols = [
                row[1]
                for row in cur.execute(
                    f"PRAGMA table_info({table_name})"
                ).fetchall()
            ]

            if "created_at" in cols and cur.lastrowid:
                cur.execute(
                    f"""
                    UPDATE {table_name}
                    SET created_at = ?
                    WHERE rowid = ?
                    """,
                    (
                        now_india().strftime("%Y-%m-%d %H:%M:%S"),
                        inserted_rowid
                    )
                )
        except Exception:
            pass

    conn.commit()
    conn.close()


def authenticate_user(username, password):
    conn = get_connection()
    user = conn.execute(
        "SELECT id, username, password_hash, role, employee_id, is_active FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()
    if user is None:
        return None
    if user[2] == hash_password(password) and user[5] == 1:
        return user
    return None


# ============================================================
# GENERIC CRUD MODULE (used by Admin / Manager screens)
# ============================================================

def _label(col):
    return col.replace("_", " ").title()

def text_input_field(col, widget_key, default):
    return st.text_input(_label(col), value=default if default is not None else "", key=widget_key)

def number_input_field(col, widget_key, default):
    return st.number_input(_label(col), value=float(default) if default is not None else 0.0, key=widget_key)

def date_input_field(col, widget_key, default):
    try:
        default_date = datetime.strptime(default, "%Y-%m-%d").date() if default else now_india().date()
    except (ValueError, TypeError):
        default_date = now_india().date()
    return str(st.date_input(_label(col), value=default_date, key=widget_key))

def status_select_field(options):
    def _field(col, widget_key, default):
        idx = options.index(default) if default in options else 0
        return st.selectbox(_label(col), options, index=idx, key=widget_key)
    return _field


def crud_module(table, columns, title, icon, form_fields, key_prefix):
    st.header(f"{icon} {title}")

    df = load_data(table)

    st.subheader("📋 Records")
    if df.empty:
        st.info(f"No {title.lower()} records available.")
    else:
        st.dataframe(df, width="stretch", hide_index=True)

    st.divider()
    tab_add, tab_edit, tab_delete = st.tabs(["➕ Add", "✏️ Edit", "🗑️ Delete"])

    with tab_add:
        with st.form(f"{key_prefix}_add_form", clear_on_submit=True):
            values = {}
            for col in columns:
                values[col] = form_fields[col](col, f"{key_prefix}_add_{col}", None)
            if st.form_submit_button("Add Record"):
                placeholders = ",".join(["?"] * len(columns))
                col_names = ",".join(columns)
                run_query(
                    f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})",
                    tuple(values[c] for c in columns)
                )
                st.success("Record added successfully.")
                st.rerun()

    with tab_edit:
        if df.empty:
            st.info("No records to edit.")
        else:
            selected_id = st.selectbox("Select record ID to edit", df["id"].tolist(), key=f"{key_prefix}_edit_select")
            record = df[df["id"] == selected_id].iloc[0]
            with st.form(f"{key_prefix}_edit_form"):
                values = {}
                for col in columns:
                    values[col] = form_fields[col](col, f"{key_prefix}_edit_{col}", record[col])
                if st.form_submit_button("Update Record"):
                    set_clause = ",".join([f"{c}=?" for c in columns])
                    run_query(
                        f"UPDATE {table} SET {set_clause} WHERE id=?",
                        tuple(values[c] for c in columns) + (selected_id,)
                    )
                    st.success("Record updated successfully.")
                    st.rerun()

    with tab_delete:
        if df.empty:
            st.info("No records to delete.")
        else:
            selected_id = st.selectbox("Select record ID to delete", df["id"].tolist(), key=f"{key_prefix}_delete_select")
            st.warning(f"This will permanently delete record ID {selected_id}.")
            if st.button("Confirm Delete", key=f"{key_prefix}_delete_btn"):
                run_query(f"DELETE FROM {table} WHERE id=?", (selected_id,))
                st.success("Record deleted.")
                st.rerun()


# ============================================================
# PUBLIC "OUR PRODUCTS" PAGE (no login required)
# ============================================================

def render_products_page():
    # ========================================================
    # PROFESSIONAL E-COMMERCE PUBLIC PRODUCTS PAGE
    # Existing products/data are preserved.
    # ========================================================

    st.markdown("""
    <div class="store-header">
        <div class="store-brand"> 🏭 MRPL</div>
        <div class="store-tagline">
            Mahakoshal Refractories • Industrial Refractory Solutions
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="store-hero">
        <div class="store-hero-content">
            <div class="store-badge">🔥 INDUSTRIAL REFRACTORY PRODUCTS</div>
            <div class="store-hero-title">Mahakoshal Refractories</div>
            <div class="store-hero-text">
                Explore our range of shaped and unshaped refractory products
                for demanding industrial applications.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    products_df = load_data("products", where="is_active = 1")
    search_product = ""
    selected_category = "All Products"
    if products_df.empty:
        st.info("No products available right now.")
        return

    # Apply filters
    filtered_df = products_df.copy()

    if selected_category != "All Products":
        filtered_df = filtered_df[
            filtered_df["category"] == selected_category
        ]

    if search_product.strip():
        search_text = search_product.strip().lower()
        mask = (
            filtered_df["product_name"].fillna("").str.lower().str.contains(
                search_text, regex=False
            )
            |
            filtered_df["category"].fillna("").str.lower().str.contains(
                search_text, regex=False
            )
            |
            filtered_df["description"].fillna("").str.lower().str.contains(
                search_text, regex=False
            )
        )
        filtered_df = filtered_df[mask]

    st.markdown(
        '<div class="store-section-title">Our Products</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="store-section-subtitle">'
        'Browse the existing MRPL product catalog.'
        '</div>',
        unsafe_allow_html=True
    )

    if filtered_df.empty:
        st.info("No products match your search or selected category.")
    else:
        for cat in filtered_df["category"].unique():

            cat_products = filtered_df[
                filtered_df["category"] == cat
            ]

            st.markdown(
                f"### {cat}"
            )

            cols = st.columns(3)

            for i, (_, row) in enumerate(cat_products.iterrows()):

                with cols[i % 3]:

                    with st.container(border=True):

                        image_urls = [
                            u.strip()
                            for u in str(
                                row["image_url"] or ""
                            ).split(",")
                            if u.strip()
                        ]

                        valid_images = [
                            u for u in image_urls
                            if Path(u).is_file()
                        ]

                        if valid_images:
                            st.image(
                                valid_images[0],
                                width="stretch"
                            )

                            if len(valid_images) > 1:
                                thumb_cols = st.columns(
                                    min(len(valid_images) - 1, 3)
                                )

                                for tc, extra_url in zip(
                                    thumb_cols,
                                    valid_images[1:]
                                ):
                                    with tc:
                                        st.image(
                                            extra_url,
                                            width="stretch"
                                        )
                        else:
                            st.info(
                                "Product image is not available "
                                "in the deployed repository."
                            )

                        st.markdown(
                            f'<div class="product-category">'
                            f'{row["category"]}</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f'<div class="product-name">'
                            f'{row["product_name"]}</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f'<div class="product-description">'
                            f'{row["description"] or ""}</div>',
                            unsafe_allow_html=True
                        )

            st.write("")

    st.markdown("---")

    st.markdown(
        '<div class="store-section-title">'
        'Mahakoshal Refractories'
        '</div>',
        unsafe_allow_html=True
    )

    st.link_button(
        "🌐 Visit Official Products Website",
        "https://mahakoshalrefractories.com/products",
        width="stretch"
    )


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
# ============================================================
# LOGIN / PUBLIC LANDING PAGE
# ============================================================

if not st.session_state.logged_in:
    st.markdown("---")
    st.markdown(
    """
    <h1 style="
        text-align: center;
        font-size: 48px;
        font-weight: 900;
        margin-top: 20px;
        margin-bottom: 30px;
        line-height: 1.15;
        background: none;
        -webkit-background-clip: initial;
        background-clip: initial;
        -webkit-text-fill-color: #ff2b2b;
        color: #ff2b2b;
        text-shadow: 0 0 25px rgba(255, 40, 40, 0.35);
    ">
        🏭 MRPL Smart Manufacturing<br>
        System
    </h1>
    """,
    unsafe_allow_html=True
    )

    # Top buttons
    col1, col2 = st.columns(2)

    with col1:
        login_btn = st.button(
            "🔐 Staff Login",
            use_container_width=True
        )

    with col2:
        products_btn = st.button(
            "🛍️ Our Products",
            use_container_width=True
        )
    st.markdown("""
<style>
.client-link-box {
    display: flex;
    gap: 15px;
    margin: 18px 0;
}

.client-link {
    flex: 1;
    display: block;
    text-align: center;
    padding: 16px 10px;
    border-radius: 14px;
    background: linear-gradient(135deg, #e53935, #b71c1c);
    color: white !important;
    text-decoration: none !important;
    font-size: 18px;
    font-weight: 700;
    border: 1px solid rgba(255,255,255,0.3);
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}

.client-link:hover {
    transform: translateY(-2px);
    background: linear-gradient(135deg, #ff5252, #c62828);
}
</style>

<div class="client-link-box">

<a class="client-link"
   href="https://mahakoshalrefractories.com/clientele/"
   target="_blank">
   🤝 Our Clientele
</a>

<a class="client-link"
   href="https://mahakoshalrefractories.com/"
   target="_blank">
   🏭 Mahakoshal Refractories
</a>

</div>
""", unsafe_allow_html=True)

    # --------------------------------------------------------
    # CONTACT US (fills the empty space below the buttons)
    # --------------------------------------------------------
    st.markdown("""
<style>
.contact-card {
    margin: 22px 0 10px 0;
    padding: 20px 18px;
    border-radius: 16px;
    background: rgba(9,27,45,.85);
    border: 1px solid rgba(100,160,205,.30);
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}

.contact-card h3 {
    margin: 0 0 14px 0 !important;
    color: #ffffff !important;
    font-size: 20px !important;
    border: none !important;
    padding: 0 !important;
}

.contact-row {
    margin-bottom: 12px;
    color: #d7e6f2;
    font-size: 14.5px;
    line-height: 1.5;
}

.contact-row b {
    color: #ff2b2b;
}

.contact-visit-btn {
    display: block;
    text-align: center;
    margin-top: 16px;
    padding: 14px 10px;
    border-radius: 12px;
    background: linear-gradient(135deg, #147fb8, #0b4f7d);
    color: white !important;
    text-decoration: none !important;
    font-size: 16px;
    font-weight: 700;
    border: 1px solid rgba(255,255,255,0.25);
}

.contact-visit-btn:hover {
    background: linear-gradient(135deg, #1a9ddd, #086a9e);
}
</style>

<div class="contact-card">
<h3>📞 Contact Us</h3>

<div class="contact-row">
<b>Head Office + Katni Unit:</b><br>
Katay Ghat Road, Industrial Area, Katni (Madhya Pradesh - 483501), INDIA
</div>

<div class="contact-row">
<b>Domestic Enquiry:</b><br>
☎️ 07622-406394 &nbsp; | &nbsp; ✉️ marketing@mahakoshal.in
</div>

<div class="contact-row">
<b>Export Enquiry:</b><br>
☎️ 9300644329 &nbsp; | &nbsp; ✉️ export@mahakoshal.in
</div>

<a class="contact-visit-btn"
   href="https://mahakoshalrefractories.com/contact-us/"
   target="_blank">
   🌐 Visit Full Contact Us Page
</a>

</div>
""", unsafe_allow_html=True)

    # --------------------------------------------------------
    # OUR PRODUCTS
    # --------------------------------------------------------
    if products_btn:

        render_products_page()

        # Mahakoshal Refractories website link - at bottom
        st.markdown("---")
        st.markdown(
            "🌐 **Visit Mahakoshal Refractories**"
        )

        st.link_button(
            "🌐Visit Mahakoshal Refractories ",
            "https://mahakoshalrefractories.com",
            use_container_width=True
        )

        st.stop()

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------
    if login_btn or st.session_state.get("show_login", False):

        st.session_state.show_login = True

        st.subheader("🔐 Login")

        with st.form("login_form"):

            username = st.text_input("Username")

            password = st.text_input(
                "Password",
                type="password"
            )

            login_submit = st.form_submit_button(
                "🔑 Login",
                use_container_width=True
            )

            if login_submit:

                user = authenticate_user(
                    username.strip(),
                    password
                )

                if user:

                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.show_login = False

                    st.rerun()

                else:
                    st.error(
                        "Invalid username or password."
                    )

        st.caption(
            "Login credentials are managed securely by the Admin."
        )

    st.stop()


# ============================================================
# LOGGED-IN LAYOUT
# ============================================================

current_user = st.session_state.user
user_id, username, _, user_role, employee_id, _ = current_user

initials = "".join([p[0].upper() for p in username.split()[:2]]) if username else "U"

st.sidebar.markdown(f"""
<div class="mrpl-profile-card">
    <div class="mrpl-profile-avatar">{initials}</div>
    <div class="mrpl-profile-info">
        <div class="mrpl-profile-name">{username}</div>
        <div class="mrpl-profile-role">{user_role}</div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("Logout", width="stretch"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

st.sidebar.divider()

ROLE_MODULES = {
    "Admin": [
        "📊 Dashboard", "🧱 Raw Materials", "🏭 Production", "🧪 Quality Control",
        "📦 Finished Goods", "🚚 Orders & Dispatch", "👥 Employees",
        "🕐 Attendance", "📅 Leave & Tasks", "🛍️ Products", "🔐 Admin Management"
    ],
    "Manager": [
        "📊 Dashboard", "🧱 Raw Materials", "🏭 Production", "🧪 Quality Control",
        "📦 Finished Goods", "🚚 Orders & Dispatch", "👥 Employees",
        "🕐 Attendance", "📅 Leave & Tasks", "🛍️ Products"
    ],
    "Employee": [
        "🙍 My Profile", "🕐 My Attendance", "📅 My Leave", "✅ My Tasks"
    ]
}

allowed_modules = ROLE_MODULES.get(user_role, [])

st.sidebar.markdown('<div class="mrpl-nav-heading">Navigation</div>', unsafe_allow_html=True)
selected_module = st.sidebar.radio("Modules", allowed_modules, label_visibility="collapsed") if allowed_modules else None

if not allowed_modules:
    st.sidebar.warning("No modules assigned to this role.")

st.markdown("""
<div class="mrpl-app-header">
    <div class="mrpl-app-header-mark">🏭</div>
    <div>
        <div class="mrpl-app-header-title">MRPL Smart Manufacturing System</div>
        <div class="mrpl-app-header-subtitle">Manufacturing &amp; Quality Management Platform</div>
    </div>
</div>
""", unsafe_allow_html=True)
# ------------------------------------------------------------
# ADMIN / MANAGER MODULES
# ------------------------------------------------------------

if selected_module == "📊 Dashboard":
    st.markdown("""
<div class="mrpl-page-title">
    <span class="mrpl-page-title-icon">📊</span>
    Management Dashboard
</div>
""", unsafe_allow_html=True)

    raw_materials = load_data("raw_materials")
    production = load_data("production")
    finished_goods = load_data("finished_goods")
    orders = load_data("orders")
    dispatch = load_data("dispatch")

    low_stock = 0
    if not raw_materials.empty:
        low_stock = len(raw_materials[raw_materials["current_stock"] <= raw_materials["minimum_stock"]])

    col1, col2, col3 = st.columns(3)
    col1.metric("🧱 Raw Materials", len(raw_materials))
    col2.metric("🏭 Production Batches", len(production))
    col3.metric("📦 Finished Goods", len(finished_goods))

    col4, col5, col6 = st.columns(3)
    col4.metric("📝 Orders", len(orders))
    col5.metric("🚚 Dispatches", len(dispatch))
    col6.metric("⚠️ Low Stock Items", low_stock)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if not production.empty:
            st.subheader("🏭 Production by Status")
            st.bar_chart(production.groupby("status")["actual_quantity"].sum())
    with c2:
        if not orders.empty:
            st.subheader("📝 Orders by Status")
            st.bar_chart(orders["status"].value_counts())

    if low_stock > 0:
        st.divider()
        st.subheader("⚠️ Low Stock Alerts")
        st.dataframe(
            raw_materials[raw_materials["current_stock"] <= raw_materials["minimum_stock"]],
            width="stretch", hide_index=True
        )

elif selected_module == "🧱 Raw Materials":
    columns = ["material_name", "category", "current_stock", "minimum_stock", "unit", "supplier", "unit_price", "last_updated"]
    fields = {
        "material_name": text_input_field, "category": text_input_field,
        "current_stock": number_input_field, "minimum_stock": number_input_field,
        "unit": text_input_field, "supplier": text_input_field,
        "unit_price": number_input_field, "last_updated": date_input_field,
    }
    crud_module("raw_materials", columns, "Raw Material Management", "🧱", fields, "rm")

elif selected_module == "🏭 Production":
    columns = ["batch_no", "product_name", "planned_quantity", "actual_quantity", "start_date", "end_date", "status", "machine", "operator"]
    fields = {
        "batch_no": text_input_field, "product_name": text_input_field,
        "planned_quantity": number_input_field, "actual_quantity": number_input_field,
        "start_date": date_input_field, "end_date": date_input_field,
        "status": status_select_field(["Pending", "In Progress", "Completed", "On Hold"]),
        "machine": text_input_field, "operator": text_input_field,
    }
    crud_module("production", columns, "Production Management", "🏭", fields, "prod")

elif selected_module == "🧪 Quality Control":
    columns = ["batch_no", "product_name", "test_date", "parameter", "result", "status", "inspector", "remarks"]
    fields = {
        "batch_no": text_input_field, "product_name": text_input_field,
        "test_date": date_input_field, "parameter": text_input_field, "result": text_input_field,
        "status": status_select_field(["Pending", "Pass", "Fail"]),
        "inspector": text_input_field, "remarks": text_input_field,
    }
    crud_module("quality_control", columns, "Quality Control", "🧪", fields, "qc")

elif selected_module == "📦 Finished Goods":
    columns = ["product_name", "batch_no", "quantity", "unit", "warehouse_location", "production_date", "expiry_date", "status"]
    fields = {
        "product_name": text_input_field, "batch_no": text_input_field,
        "quantity": number_input_field, "unit": text_input_field,
        "warehouse_location": text_input_field, "production_date": date_input_field,
        "expiry_date": text_input_field,
        "status": status_select_field(["Available", "Reserved", "Dispatched", "Expired"]),
    }
    crud_module("finished_goods", columns, "Finished Goods / Warehouse", "📦", fields, "fg")

elif selected_module == "🚚 Orders & Dispatch":
    tab_orders, tab_dispatch = st.tabs(["📝 Orders", "🚚 Dispatch"])
    with tab_orders:
        columns = ["order_no", "customer_name", "product_name", "quantity", "order_date", "delivery_date", "status"]
        fields = {
            "order_no": text_input_field, "customer_name": text_input_field,
            "product_name": text_input_field, "quantity": number_input_field,
            "order_date": date_input_field, "delivery_date": date_input_field,
            "status": status_select_field(["Confirmed", "Processing", "Shipped", "Delivered", "Cancelled"]),
        }
        crud_module("orders", columns, "Orders", "📝", fields, "ord")
    with tab_dispatch:
        columns = ["dispatch_no", "order_no", "product_name", "quantity", "dispatch_date", "vehicle_no", "driver_name", "status"]
        fields = {
            "dispatch_no": text_input_field, "order_no": text_input_field,
            "product_name": text_input_field, "quantity": number_input_field,
            "dispatch_date": date_input_field, "vehicle_no": text_input_field,
            "driver_name": text_input_field,
            "status": status_select_field(["Scheduled", "Dispatched", "In Transit", "Delivered"]),
        }
        crud_module("dispatch", columns, "Dispatch", "🚚", fields, "disp")

elif selected_module == "👥 Employees":
    columns = [
        "id",
        "full_name",
        "designation",
        "department",
        "phone",
        "email",
        "joining_date",
        "status"
    ]

    fields = {
        "id": number_input_field,
        "full_name": text_input_field,
        "designation": text_input_field,
        "department": text_input_field,
        "phone": text_input_field,
        "email": text_input_field,
        "joining_date": date_input_field,
        "status": status_select_field(["Active", "Inactive"])
    }

    crud_module(
        "employees",
        columns,
        "Employee Management",
        "👥",
        fields,
        "id"
    )

elif selected_module == "🕐 Attendance":
    columns = ["employee_id", "employee_name", "att_date", "status", "check_in", "check_out"]
    fields = {
        "employee_id": number_input_field, "employee_name": text_input_field,
        "att_date": date_input_field,
        "status": status_select_field(["Present", "Absent", "Leave"]),
        "check_in": text_input_field, "check_out": text_input_field,
    }
    crud_module("attendance", columns, "Attendance Management", "🕐", fields, "att")

elif selected_module == "📅 Leave & Tasks":
    tab_leave, tab_tasks = st.tabs(["📅 Leave Requests", "✅ Tasks"])
    with tab_leave:
        columns = ["employee_id", "employee_name", "leave_type", "start_date", "end_date", "reason", "status"]
        fields = {
            "employee_id": number_input_field, "employee_name": text_input_field,
            "leave_type": text_input_field, "start_date": date_input_field, "end_date": date_input_field,
            "reason": text_input_field,
            "status": status_select_field(["Pending", "Approved", "Rejected"]),
        }
        crud_module("leave_requests", columns, "Leave Requests", "📅", fields, "leave")
    with tab_tasks:
        columns = ["employee_id", "employee_name", "title", "description", "due_date", "status"]
        fields = {
            "employee_id": number_input_field, "employee_name": text_input_field,
            "title": text_input_field, "description": text_input_field, "due_date": date_input_field,
            "status": status_select_field(["Pending", "In Progress", "Done"]),
        }
        crud_module("tasks", columns, "Tasks", "✅", fields, "task")

elif selected_module == "🛍️ Products":
    columns = ["category", "product_name", "description", "image_url", "is_active"]
    fields = {
        "category": text_input_field, "product_name": text_input_field,
        "description": text_input_field, "image_url": text_input_field,
        "is_active": number_input_field,
    }
    crud_module("products", columns, "Product Catalog (shown on public page)", "🛍️", fields, "prd")

elif selected_module == "🔐 Admin Management" and user_role == "Admin":
    st.header("🔐 Admin Management")
    st.caption("Manage Admin, Manager and Employee login accounts from one place.")

    users_df = load_data("users")
    visible_users = users_df.drop(columns=["password_hash"], errors="ignore")

    st.subheader("👥 Existing Accounts")
    if visible_users.empty:
        st.info("No user accounts found.")
    else:
        st.dataframe(visible_users, width="stretch", hide_index=True)

    st.divider()

    # --------------------------------------------------------
    # ADD SECOND ADMIN / OTHER USER
    # --------------------------------------------------------
    tab_admin, tab_other = st.tabs(["➕ Add Admin", "➕ Add Manager / Employee"])

    with tab_admin:
        st.subheader("➕ Add another Admin")
        with st.form("add_admin_form", clear_on_submit=True):
            admin_username = st.text_input("Admin Username")
            admin_password = st.text_input("Admin Password", type="password")
            admin_password2 = st.text_input("Confirm Admin Password", type="password")

            if st.form_submit_button("Create Admin", type="primary", width="stretch"):
                if not admin_username.strip() or not admin_password:
                    st.error("Username and password are required.")
                elif admin_password != admin_password2:
                    st.error("Passwords do not match.")
                elif len(admin_password) < 8:
                    st.error("Use a password of at least 8 characters.")
                else:
                    try:
                        run_query(
                            """
                            INSERT INTO users
                            (username, password_hash, role, employee_id,cteated_at, is_active)
                            VALUES (?, ?, 'Admin', NULL, 1)
                            """,
                            (admin_username.strip(), hash_password(admin_password))
                        )
                        st.success("Second Admin created successfully.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Username already exists.")

    with tab_other:
        st.subheader("➕ Add Manager / Employee")
        employees_df = load_data("employees")

        employee_map = {}
        employee_options = ["Not linked"]
        if not employees_df.empty:
            for _, emp_row in employees_df.iterrows():
                label = f"{emp_row['full_name']} (ID: {int(emp_row['id'])})"
                employee_options.append(label)
                employee_map[label] = int(emp_row["id"])

        with st.form("add_user_form", clear_on_submit=True):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_password2 = st.text_input("Confirm Password", type="password")
            new_role = st.selectbox("Role", ["Manager", "Employee"])
            linked_employee = st.selectbox(
                "Linked Employee",
                employee_options,
                help="Employee login must be linked to the employee profile for My Attendance, My Leave and My Profile."
            )

            if st.form_submit_button("Create User", type="primary", width="stretch"):
                if not new_username.strip() or not new_password:
                    st.error("Username and password are required.")
                elif new_password != new_password2:
                    st.error("Passwords do not match.")
                elif len(new_password) < 8:
                    st.error("Use a password of at least 8 characters.")
                else:
                    emp_id = employee_map.get(linked_employee)
                    try:
                        run_query(
                            """
                            INSERT INTO users
                            (username, password_hash, role, employee_id,created_at, is_active)
                            VALUES (?, ?, ?, ?,?, 1)
                            """,
                            (new_username.strip(), hash_password(new_password), new_role, emp_id,now_india().strftime("%Y-%m-%d %H:%M:%S")
                            ) 
                        )
                        st.success("User created successfully.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Username already exists.")

    st.divider()

    # --------------------------------------------------------
    # LINK / EDIT ACCOUNT
    # --------------------------------------------------------
    st.subheader("🔗 Link Employee Profile to Login")
    if not users_df.empty:
        user_choices = [
            f"{row['username']} — {row['role']} (ID: {int(row['id'])})"
            for _, row in users_df.iterrows()
        ]
        selected_user_label = st.selectbox(
            "Select Account",
            user_choices,
            key="admin_manage_user_select"
        )
        selected_user_id = int(
            re.search(r"ID: (\d+)", selected_user_label).group(1)
        )
        selected_user = users_df[users_df["id"] == selected_user_id].iloc[0]

        employees_df = load_data("employees")
        employee_map = {"Not linked": None}
        if not employees_df.empty:
            for _, emp_row in employees_df.iterrows():
                label = f"{emp_row['full_name']} (ID: {int(emp_row['id'])})"
                employee_map[label] = int(emp_row["id"])

        current_emp_id = selected_user["employee_id"]
        current_label = "Not linked"
        for label, emp_id in employee_map.items():
            if emp_id == current_emp_id:
                current_label = label
                break

        with st.form("link_employee_form"):
            link_options = list(employee_map.keys())
            current_index = link_options.index(current_label) if current_label in link_options else 0
            new_link = st.selectbox(
                "Employee Profile",
                link_options,
                index=current_index
            )
            active_value = st.checkbox(
                "Account Active",
                value=bool(selected_user["is_active"])
            )

            if st.form_submit_button("Save Account Settings", width="stretch"):
                run_query(
                    "UPDATE users SET employee_id = ?, is_active = ? WHERE id = ?",
                    (employee_map[new_link], 1 if active_value else 0, selected_user_id)
                )
                st.success("Account settings updated.")
                st.rerun()

    st.divider()

    # --------------------------------------------------------
    # PROTECT THE LAST ACTIVE ADMIN
    # --------------------------------------------------------
    st.subheader("🛡️ Admin Account Protection")

    active_admins = load_data(
        "users",
        where="role = 'Admin' AND is_active = 1"
    )

    if not active_admins.empty:
        for _, admin_row in active_admins.iterrows():
            is_current = int(admin_row["id"]) == int(user_id)
            label = f"{admin_row['username']} (ID: {int(admin_row['id'])})"
            if is_current:
                st.success(f"Current Admin: {label}")
            else:
                st.info(label)

    st.caption("The system will not allow the last active Admin account to be deactivated or deleted.")

    if not users_df.empty:
        manage_user_id = st.selectbox(
            "Select account for deactivation / deletion",
            users_df["id"].tolist(),
            key="admin_delete_user_select"
        )
        manage_user = users_df[users_df["id"] == manage_user_id].iloc[0]

        c1, c2 = st.columns(2)

        with c1:
            if st.button(
                "Deactivate Account",
                key="deactivate_user_btn",
                width="stretch"
            ):
                if (
                    manage_user["role"] == "Admin"
                    and int(manage_user["is_active"]) == 1
                    and len(active_admins) <= 1
                ):
                    st.error("You cannot deactivate the last active Admin.")
                elif int(manage_user_id) == int(user_id):
                    st.error("You cannot deactivate your own current Admin account.")
                else:
                    run_query(
                        "UPDATE users SET is_active = 0 WHERE id = ?",
                        (manage_user_id,)
                    )
                    st.success("Account deactivated.")
                    st.rerun()

        with c2:
            if st.button(
                "Delete Permanently",
                key="delete_user_btn",
                width="stretch"
            ):
                if (
                    manage_user["role"] == "Admin"
                    and int(manage_user["is_active"]) == 1
                    and len(active_admins) <= 1
                ):
                    st.error("You cannot delete the last active Admin.")
                elif int(manage_user_id) == int(user_id):
                    st.error("You cannot delete your own current Admin account.")
                else:
                    run_query(
                        "DELETE FROM users WHERE id = ?",
                        (manage_user_id,)
                    )
                    st.success("Account deleted.")
                    st.rerun()

# ------------------------------------------------------------
# EMPLOYEE SELF-SERVICE MODULES
# ------------------------------------------------------------

elif selected_module == "🙍 My Profile":
    st.header("🙍 My Profile")
    if employee_id:
        emp = load_data("employees", where="id = ?", params=(employee_id,))
        if not emp.empty:
            row = emp.iloc[0]
            st.write(f"**Name:** {row['full_name']}")
            st.write(f"**Designation:** {row['designation']}")
            st.write(f"**Department:** {row['department']}")
            st.write(f"**Phone:** {row['phone']}")
            st.write(f"**Email:** {row['email']}")
            st.write(f"**Joining Date:** {row['joining_date']}")
            st.write(f"**Status:** {row['status']}")
        else:
            st.info("No employee profile linked to this account.")
    else:
        st.info("No employee profile linked to this account.")

elif selected_module == "🕐 My Attendance":
    st.header("🕐 My Attendance")

    if not employee_id:
        st.error("No employee profile is linked to this account. Ask an Admin to link your Employee Profile in Admin Management.")
        st.stop()

    my_att = load_data("attendance", where="employee_id = ?", params=(employee_id,))

    if not my_att.empty:
        my_att["att_date"] = my_att["att_date"].astype(str)
        my_att = my_att.sort_values("att_date", ascending=False)
        display_columns = [
            c for c in ["employee_name", "att_date", "status", "check_in", "check_out"]
            if c in my_att.columns
        ]
        st.dataframe(my_att[display_columns], width="stretch", hide_index=True)
    else:
        st.info("No attendance records found.")

    st.divider()
    st.subheader("Mark today's attendance")
    st.caption(f"India Standard Time (IST): {now_india().strftime('%d-%m-%Y %I:%M:%S %p')}")

    now_ist = now_india()
    today_str = now_ist.date().isoformat()
    today_att = my_att[my_att["att_date"] == today_str] if not my_att.empty else pd.DataFrame()

    emp_name_row = load_data("employees", where="id = ?", params=(employee_id,))
    emp_name = emp_name_row.iloc[0]["full_name"] if not emp_name_row.empty else username

    if today_att.empty:
        if st.button("Mark Present (Check-in now)", type="primary", width="stretch"):
            check_in_time = now_india().strftime("%I:%M:%S %p")
            run_query(
                """
                INSERT INTO attendance
                (employee_id, employee_name, att_date, status, check_in, check_out)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (employee_id, emp_name, today_str, "Present", check_in_time, None)
            )
            st.success("Attendance marked successfully.")
            st.rerun()
    else:
        today_row = today_att.iloc[0]
        check_in = today_row.get("check_in")
        check_out = today_row.get("check_out")

        st.success(f"Today's attendance is marked. Check-in: {check_in or '—'}")

        if pd.isna(check_out) or not str(check_out).strip() or str(check_out).lower() == "none":
            if st.button("Check-out now", type="primary", width="stretch"):
                check_out_time = now_india().strftime("%I:%M:%S %p")
                run_query(
                    "UPDATE attendance SET check_out = ? WHERE id = ?",
                    (check_out_time, int(today_row["id"]))
                )
                st.success("Check-out marked successfully.")
                st.rerun()
        else:
            st.info(f"Check-out: {check_out}. Today's attendance is complete.")

elif selected_module == "📅 My Leave":
    st.header("📅 My Leave")
    if not employee_id:
        st.error("No employee profile is linked to this account. Ask an Admin to link your Employee Profile in Admin Management.")
        st.stop()
    my_leave = load_data("leave_requests", where="employee_id = ?", params=(employee_id,))
    st.dataframe(my_leave, width="stretch", hide_index=True)

    st.divider()
    st.subheader("Apply for leave")
    with st.form("apply_leave_form", clear_on_submit=True):
        leave_type = st.selectbox("Leave Type", ["Sick Leave", "Casual Leave", "Earned Leave"])
        start_dt = st.date_input("Start Date", value=date.today())
        end_dt = st.date_input("End Date", value=date.today())
        reason = st.text_input("Reason")
        if st.form_submit_button("Submit Request"):
            if start_dt > end_dt:
                st.error("End date cannot be before start date.")
            else:
                emp_name_row = load_data("employees", where="id = ?", params=(employee_id,))
                emp_name = emp_name_row.iloc[0]["full_name"] if not emp_name_row.empty else username
                run_query(
                    "INSERT INTO leave_requests (employee_id, employee_name, leave_type, start_date, end_date, reason, status) VALUES (?,?,?,?,?,?,?)",
                    (employee_id, emp_name, leave_type, str(start_dt), str(end_dt), reason, "Pending")
                )
                st.success("Leave request submitted.")
                st.rerun()

elif selected_module == "✅ My Tasks":
    st.header("✅ My Tasks")
    if not employee_id:
        st.error("No employee profile is linked to this account. Ask an Admin to link your Employee Profile in Admin Management.")
        st.stop()
    my_tasks = load_data("tasks", where="employee_id = ?", params=(employee_id,))
    if my_tasks.empty:
        st.info("No tasks assigned.")
    else:
        for _, row in my_tasks.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['title']}**  —  _{row['status']}_")
                st.caption(row["description"] or "")
                st.caption(f"Due: {row['due_date']}")
                new_status = st.selectbox(
                    "Update status", ["Pending", "In Progress", "Done"],
                    index=["Pending", "In Progress", "Done"].index(row["status"]) if row["status"] in ["Pending", "In Progress", "Done"] else 0,
                    key=f"task_status_{row['id']}"
                )
                if st.button("Save", key=f"task_save_{row['id']}"):
                    run_query("UPDATE tasks SET status = ? WHERE id = ?", (new_status, row["id"]))
                    st.success("Task updated.")
                    st.rerun()

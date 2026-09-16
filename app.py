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
    :root {{
        --mrpl-bg: #061525;
        --mrpl-panel: #0a1f36;
        --mrpl-panel-2: #102d4b;
        --mrpl-border: rgba(104, 181, 255, .20);
        --mrpl-text: #f5f9ff;
        --mrpl-muted: #9fb4c9;
        --mrpl-accent: #1597ff;
        --mrpl-accent-2: #19c7a5;
        --mrpl-danger: #ff5d6c;
    }}

    .stApp {{
        background-image:
            linear-gradient(rgba(3, 18, 33, .84), rgba(3, 18, 33, .91)),
            {MRPL_BG_CSS};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        background-color: var(--mrpl-bg);
        color: var(--mrpl-text);
    }}

    .block-container {{
        max-width: 1500px;
        padding-top: 1.15rem;
        padding-bottom: 2.2rem;
    }}

    h1, h2, h3, h4, p, label, .stMarkdown,
    [data-testid="stCaptionContainer"] {{
        color: var(--mrpl-text) !important;
    }}

    h1 {{ font-weight: 850; letter-spacing: -.5px; }}
    h2, h3 {{ font-weight: 800; }}

    /* =========================================================
       MODERN SIDEBAR
       ========================================================= */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #061a30 0%, #041322 100%);
        border-right: 1px solid rgba(80,170,255,.16);
    }}

    section[data-testid="stSidebar"] > div {{
        background: linear-gradient(180deg, rgba(8,31,54,.98), rgba(3,17,31,.98));
    }}

    section[data-testid="stSidebar"] .stRadio > label {{
        color: #8fb0c9 !important;
        font-size: 11px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 8px;
    }}

    section[data-testid="stSidebar"] [role="radiogroup"] {{
        gap: 7px;
    }}

    section[data-testid="stSidebar"] [role="radiogroup"] > label {{
        background: rgba(10, 42, 70, .66);
        border: 1px solid rgba(91, 169, 228, .13);
        border-radius: 13px;
        padding: 9px 11px;
        margin: 0;
        transition: .18s ease;
    }}

    section[data-testid="stSidebar"] [role="radiogroup"] > label:hover {{
        background: rgba(20, 75, 116, .82);
        border-color: rgba(39,168,255,.55);
        transform: translateX(2px);
    }}

    section[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) {{
        background: linear-gradient(135deg, #0877c9, #07569a);
        border-color: rgba(88,194,255,.8);
        box-shadow: 0 8px 22px rgba(0,118,210,.24);
    }}

    .mrpl-side-brand {{
        display:flex;
        align-items:center;
        gap:10px;
        padding: 4px 2px 16px 2px;
        margin-bottom: 10px;
        border-bottom:1px solid rgba(255,255,255,.10);
    }}

    .mrpl-side-logo {{
        width:42px; height:42px;
        display:flex; align-items:center; justify-content:center;
        border-radius:12px;
        background:linear-gradient(135deg,#0d8de8,#0a4f8a);
        font-size:22px;
        box-shadow:0 8px 20px rgba(0,130,230,.25);
    }}

    .mrpl-side-title {{ font-size:19px; font-weight:850; line-height:1.05; }}
    .mrpl-side-sub {{ font-size:10px; color:#8fa9bf; margin-top:4px; }}

    .mrpl-user-card {{
        background:linear-gradient(145deg, rgba(12,54,77,.96), rgba(6,31,51,.96));
        border:1px solid rgba(73,185,255,.18);
        border-radius:17px;
        padding:14px;
        margin:4px 0 14px 0;
        box-shadow:0 10px 28px rgba(0,0,0,.16);
    }}

    .mrpl-user-row {{ display:flex; align-items:center; gap:11px; }}
    .mrpl-avatar {{
        width:42px; height:42px; border-radius:50%;
        display:flex; align-items:center; justify-content:center;
        background:linear-gradient(145deg,#1a9df5,#0a5b9b);
        font-size:21px;
    }}
    .mrpl-user-name {{ font-weight:800; font-size:15px; }}
    .mrpl-user-role {{ color:#9fb7ca; font-size:12px; margin-top:3px; }}
    .mrpl-online {{
        margin-left:auto; color:#8ce8a5; font-size:11px; font-weight:700;
    }}
    .mrpl-online::before {{ content:""; display:inline-block; width:7px; height:7px;
        border-radius:50%; background:#63e685; margin-right:5px; }}

    /* =========================================================
       UNIVERSAL BUTTON SYSTEM
       ========================================================= */
    .stButton > button,
    .stLinkButton > a,
    .stDownloadButton > button,
    button[kind="secondary"],
    button[kind="primary"] {{
        min-height:46px;
        border-radius:13px !important;
        font-weight:800 !important;
        letter-spacing:.1px;
        border:1px solid rgba(91,182,255,.28) !important;
        transition:transform .16s ease, box-shadow .16s ease, border-color .16s ease;
        box-shadow:0 7px 20px rgba(0,0,0,.18);
    }}

    .stButton > button:hover,
    .stLinkButton > a:hover,
    .stDownloadButton > button:hover {{
        transform:translateY(-1px);
        border-color:#42b8ff !important;
        box-shadow:0 10px 24px rgba(0,128,220,.22);
    }}

    button[kind="primary"] {{
        background:linear-gradient(135deg,#1597ff,#0765b1) !important;
        color:#fff !important;
    }}

    button[kind="secondary"] {{
        background:rgba(239,247,255,.96) !important;
        color:#0b3152 !important;
        border-color:rgba(255,255,255,.75) !important;
    }}

    /* Logout gets a restrained danger treatment */
    section[data-testid="stSidebar"] .stButton > button {{
        background:linear-gradient(135deg,#123f64,#0b2a48) !important;
    }}

    /* =========================================================
       LANDING PAGE
       ========================================================= */
    .mrpl-landing {{
        position:relative;
        min-height:590px;
        display:flex;
        flex-direction:column;
        justify-content:space-between;
        overflow:hidden;
        border:1px solid rgba(111,192,255,.20);
        border-radius:26px;
        padding:30px 34px 28px;
        background-image:
            linear-gradient(135deg, rgba(3,18,33,.90), rgba(5,36,61,.58)),
            {MRPL_BG_CSS};
        background-size:cover;
        background-position:center;
        box-shadow:0 22px 55px rgba(0,0,0,.28);
    }}

    .mrpl-landing::after {{
        content:"";
        position:absolute; width:330px; height:330px;
        right:-120px; top:-120px;
        border-radius:50%;
        background:rgba(27,157,255,.16);
        filter:blur(4px);
    }}

    .mrpl-brand-row {{
        position:relative; z-index:1;
        display:flex; align-items:center; justify-content:space-between;
    }}

    .mrpl-brand-left {{ display:flex; align-items:center; gap:12px; }}
    .mrpl-brand-icon {{
        width:50px; height:50px; border-radius:15px;
        display:flex; align-items:center; justify-content:center;
        background:linear-gradient(135deg,#ff5b61,#d83243);
        font-size:25px;
        box-shadow:0 9px 22px rgba(255,72,82,.25);
    }}
    .mrpl-brand-name {{ font-size:25px; font-weight:900; }}
    .mrpl-brand-sub {{ font-size:11px; color:#a9bfd1; margin-top:3px; }}
    .mrpl-top-tag {{ font-size:11px; color:#dcecff; text-align:right; line-height:1.3; }}

    .mrpl-hero-copy {{
        position:relative; z-index:1;
        max-width:720px;
        margin-top:36px;
    }}

    .mrpl-kicker {{
        display:inline-flex; padding:7px 12px; border-radius:999px;
        background:rgba(30,160,255,.13);
        border:1px solid rgba(73,187,255,.26);
        color:#8fd5ff; font-size:11px; font-weight:850;
        letter-spacing:.9px;
    }}

    .mrpl-hero-title {{
        margin-top:18px;
        font-size:clamp(34px, 5vw, 58px);
        line-height:1.02;
        font-weight:900;
        letter-spacing:-1.5px;
    }}

    .mrpl-hero-text {{
        margin-top:15px; max-width:610px;
        color:#bfd0df; font-size:15px; line-height:1.65;
    }}

    .mrpl-feature-row {{
        display:flex; gap:28px; margin-top:24px;
        color:#dcecff; font-size:12px;
    }}
    .mrpl-feature {{ display:flex; align-items:center; gap:8px; }}
    .mrpl-feature-icon {{ font-size:20px; }}

    .mrpl-action-label {{
        position:relative; z-index:1;
        color:#9db4c9; font-size:11px; font-weight:800;
        letter-spacing:1px; text-transform:uppercase;
        margin:16px 0 8px;
    }}

    /* =========================================================
       DASHBOARD / METRICS
       ========================================================= */
    .mrpl-page-head {{
        display:flex; justify-content:space-between; align-items:center;
        gap:16px; margin-bottom:18px;
    }}
    .mrpl-page-kicker {{ color:#69c6ff; font-size:11px; font-weight:850; letter-spacing:1px; text-transform:uppercase; }}
    .mrpl-page-title {{ font-size:31px; font-weight:900; margin-top:4px; }}
    .mrpl-page-desc {{ color:#9fb4c9; font-size:13px; margin-top:4px; }}

    div[data-testid="stMetric"] {{
        position:relative;
        overflow:hidden;
        min-height:126px;
        background:linear-gradient(145deg, rgba(13,47,78,.97), rgba(7,29,50,.97));
        border:1px solid rgba(87,180,247,.18);
        border-radius:18px;
        padding:17px 18px;
        box-shadow:0 10px 28px rgba(0,0,0,.18);
    }}

    div[data-testid="stMetric"]::after {{
        content:"";
        position:absolute; width:100px; height:100px;
        right:-42px; top:-48px; border-radius:50%;
        background:rgba(29,161,255,.10);
    }}

    div[data-testid="stMetricLabel"] {{ color:#9fb8cc !important; font-size:12px !important; }}
    div[data-testid="stMetricValue"] {{ color:#f5fbff !important; font-size:30px !important; font-weight:850 !important; }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background:rgba(8,29,50,.93);
        border:1px solid rgba(92,178,235,.17);
        border-radius:18px;
        box-shadow:0 10px 28px rgba(0,0,0,.18);
    }}

    /* Inputs */
    div[data-baseweb="input"],
    div[data-baseweb="select"],
    textarea, input {{
        background:#081e34 !important;
        color:#eef6ff !important;
        border-color:#214866 !important;
    }}
    div[data-baseweb="select"] * {{ color:#eef6ff !important; }}

    hr {{ border-color:rgba(105,181,237,.16) !important; }}

    /* =========================================================
       PUBLIC PRODUCTS PAGE
       ========================================================= */
    .store-header {{
        background:rgba(255,255,255,.97);
        border:1px solid #dce5ed;
        border-radius:18px;
        padding:15px 22px;
        margin-bottom:18px;
        box-shadow:0 7px 20px rgba(0,0,0,.14);
    }}
    .store-brand {{ color:#12304a; font-size:26px; font-weight:850; line-height:1.1; }}
    .store-tagline {{ color:#64748b; font-size:13px; margin-top:4px; }}
    .store-hero {{
        position:relative; min-height:285px; display:flex; align-items:center;
        padding:42px; border-radius:20px; overflow:hidden; margin-bottom:25px;
        background-image:linear-gradient(90deg,rgba(4,20,35,.90),rgba(4,20,35,.54)), {MRPL_BG_CSS};
        background-size:cover; background-position:center;
        box-shadow:0 10px 30px rgba(0,0,0,.22);
    }}
    .store-hero-content {{ max-width:720px; }}
    .store-badge {{ display:inline-block; padding:7px 13px; border-radius:999px;
        background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.25);
        color:#fff; font-size:12px; font-weight:700; margin-bottom:12px; }}
    .store-hero-title {{ color:#fff; font-size:40px; line-height:1.12; font-weight:850; margin-bottom:10px; }}
    .store-hero-text {{ color:#e4edf5; font-size:15px; line-height:1.65; }}
    .store-section-title {{ color:#fff; font-size:27px; font-weight:800; margin:12px 0 4px; }}
    .store-section-subtitle {{ color:#b7c8d8; font-size:13px; margin-bottom:16px; }}
    .product-name {{ color:#fff; font-size:18px; font-weight:800; margin-top:8px; margin-bottom:5px; }}
    .product-category {{ color:#65c5ff; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.4px; }}
    .product-description {{ color:#b8c9d8; font-size:13px; line-height:1.5; }}
    .category-chip {{ background:rgba(255,255,255,.08); border:1px solid #315b7c;
        border-radius:12px; padding:14px 16px; color:#eef6ff; font-weight:700; text-align:center; }}

    @media (max-width: 768px) {{
        .block-container {{ padding: .75rem .65rem 1.4rem; }}
        h1 {{ font-size:1.75rem !important; line-height:1.12; }}
        h2 {{ font-size:1.4rem !important; }}
        h3 {{ font-size:1.18rem !important; }}
        .mrpl-landing {{ min-height:600px; padding:22px 18px 20px; border-radius:21px; }}
        .mrpl-brand-name {{ font-size:21px; }}
        .mrpl-brand-icon {{ width:43px; height:43px; }}
        .mrpl-top-tag {{ display:none; }}
        .mrpl-hero-copy {{ margin-top:32px; }}
        .mrpl-hero-title {{ font-size:36px; letter-spacing:-1px; }}
        .mrpl-hero-text {{ font-size:13px; }}
        .mrpl-feature-row {{ gap:12px; justify-content:space-between; }}
        .mrpl-feature {{ flex-direction:column; text-align:center; gap:4px; font-size:10px; }}
        .mrpl-feature-icon {{ font-size:19px; }}
        .mrpl-page-title {{ font-size:26px; }}
        div[data-testid="stMetric"] {{ min-height:108px; padding:14px; border-radius:15px; }}
        div[data-testid="stMetricValue"] {{ font-size:27px !important; }}
        .store-hero {{ padding:28px; min-height:255px; }}
        .store-hero-title {{ font-size:29px; }}
        .store-hero-text {{ font-size:14px; }}
        .store-brand {{ font-size:22px; }}
    }}
    </style>
    """,
    unsafe_allow_html=True
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
        """Return all existing product images from a ROOT product folder."""
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

            (
                "Unshaped Products",
                "Gunning Mixes",
                "Spray-applied refractory mixes for repair, maintenance and lining applications.",
                ""
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
        <div class="store-brand">🏭 MRPL</div>
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

    if products_df.empty:
        st.info("No products available right now.")
        return

    # Search and category filter
    search_col, category_col = st.columns([2.2, 1])

    with search_col:
        search_product = st.text_input(
            "🔎 Search Products",
            placeholder="Search by product name or category...",
            key="public_product_search"
        )

    categories = [
        "All Products"
    ] + sorted(
        products_df["category"].dropna().unique().tolist()
    )

    with category_col:
        selected_category = st.selectbox(
            "📂 Category",
            categories,
            key="public_product_category"
        )

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
    st.markdown("""
    <div class="mrpl-landing">
        <div>
            <div class="mrpl-brand-row">
                <div class="mrpl-brand-left">
                    <div class="mrpl-brand-icon">🏭</div>
                    <div>
                        <div class="mrpl-brand-name">MRPL</div>
                        <div class="mrpl-brand-sub">Mahakoshal Refractories Pvt. Ltd.</div>
                    </div>
                </div>
                <div class="mrpl-top-tag">BUILDING<br>STRONGER<br>INDUSTRIES</div>
            </div>

            <div class="mrpl-hero-copy">
                <span class="mrpl-kicker">SMART MANUFACTURING PLATFORM</span>
                <div class="mrpl-hero-title">MRPL Smart<br>Manufacturing System</div>
                <div class="mrpl-hero-text">
                    Digital operations for manufacturing, quality, inventory,
                    workforce and product management — in one connected workspace.
                </div>

                <div class="mrpl-feature-row">
                    <div class="mrpl-feature"><span class="mrpl-feature-icon">⚙️</span><span>Smart Operations</span></div>
                    <div class="mrpl-feature"><span class="mrpl-feature-icon">▥</span><span>Better Productivity</span></div>
                    <div class="mrpl-feature"><span class="mrpl-feature-icon">🌿</span><span>Sustainable Growth</span></div>
                </div>
            </div>
        </div>
        <div>
            <div class="mrpl-action-label">Quick Access</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        login_btn = st.button("👤  Staff Login  ›", use_container_width=True, type="primary")
    with col2:
        products_btn = st.button("▣  Our Products  ›", use_container_width=True, type="secondary")

    st.markdown(
        '<div style="text-align:center;color:#91a9bd;font-size:11px;margin-top:10px;">'
        'Secure • Efficient • Reliable • Sustainable'
        '</div>',
        unsafe_allow_html=True
    )

    if products_btn:
        render_products_page()
        st.markdown("---")
        st.markdown("🌐 **Visit Mahakoshal Refractories**")
        st.link_button(
            "🌐 Visit Mahakoshal Refractories",
            "https://mahakoshalrefractories.com",
            use_container_width=True
        )
        st.stop()

    if login_btn or st.session_state.get("show_login", False):
        st.session_state.show_login = True
        st.markdown("""
        <div class="mrpl-page-head">
            <div>
                <div class="mrpl-page-kicker">SECURE ACCESS</div>
                <div class="mrpl-page-title">Staff Login</div>
                <div class="mrpl-page-desc">Sign in to access your MRPL workspace.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_submit = st.form_submit_button("🔐  Login to Workspace", use_container_width=True, type="primary")

            if login_submit:
                user = authenticate_user(username.strip(), password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.show_login = False
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        st.caption("Login credentials are managed securely by the Admin.")

    st.stop()


# ============================================================
# LOGGED-IN LAYOUT
# ============================================================

current_user = st.session_state.user
user_id, username, _, user_role, employee_id, _ = current_user

st.sidebar.markdown("""
<div class="mrpl-side-brand">
    <div class="mrpl-side-logo">🏭</div>
    <div>
        <div class="mrpl-side-title">MRPL</div>
        <div class="mrpl-side-sub">SMART MANUFACTURING SYSTEM</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    f"""
    <div class="mrpl-user-card">
        <div class="mrpl-user-row">
            <div class="mrpl-avatar">👤</div>
            <div>
                <div class="mrpl-user-name">{username}</div>
                <div class="mrpl-user-role">{user_role}</div>
            </div>
            <div class="mrpl-online">Online</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if st.sidebar.button("↪  Logout", width="stretch"):
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

st.sidebar.subheader("📋 Navigation")
selected_module = st.sidebar.radio("Select Module", allowed_modules) if allowed_modules else None

if not allowed_modules:
    st.sidebar.warning("No modules assigned to this role.")

st.markdown("""
<div class="mrpl-page-head">
    <div>
        <div class="mrpl-page-kicker">MAHAKOSHAL REFRACTORIES PVT. LTD.</div>
        <div class="mrpl-page-title">MRPL Smart Manufacturing System</div>
        <div class="mrpl-page-desc">Connected operations • Real-time visibility • Better control</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# ADMIN / MANAGER MODULES
# ------------------------------------------------------------

if selected_module == "📊 Dashboard":
    st.markdown("""
    <div class="mrpl-page-head">
        <div>
            <div class="mrpl-page-kicker">OVERVIEW</div>
            <div class="mrpl-page-title">Management Dashboard</div>
            <div class="mrpl-page-desc">A quick view of inventory, production, orders and dispatch operations.</div>
        </div>
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

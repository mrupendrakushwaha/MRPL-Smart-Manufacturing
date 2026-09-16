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
        --mrpl-bg: #05131f;
        --mrpl-panel: #0c2038;
        --mrpl-panel-2: #112a45;
        --mrpl-border: #1e3f5c;
        --mrpl-border-soft: rgba(255,255,255,.08);
        --mrpl-text: #eef4fb;
        --mrpl-muted: #97acc2;
        --mrpl-accent: #2f9bf0;
        --mrpl-accent-2: #17c9a3;
        --mrpl-gold: #d8ab5c;
        --mrpl-radius: 14px;
        --mrpl-shadow: 0 10px 28px rgba(0,0,0,.28);
        --mrpl-font: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {{
        font-family: var(--mrpl-font) !important;
    }}

    /* Full-app MRPL background */
    .stApp {{
        background-image:
            linear-gradient(
                180deg,
                rgba(3, 14, 26, 0.93) 0%,
                rgba(4, 18, 32, 0.96) 55%,
                rgba(3, 14, 26, 0.98) 100%
            ),
            {MRPL_BG_CSS};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        background-color: var(--mrpl-bg);
        color: var(--mrpl-text);
        font-family: var(--mrpl-font);
    }}

    #MainMenu, footer {{ visibility: hidden; }}

    header[data-testid="stHeader"] {{
        background: rgba(5, 19, 31, 0.55);
        backdrop-filter: blur(6px);
    }}

    .block-container {{
        max-width: 1500px;
        padding-top: 1.6rem;
        padding-bottom: 2.5rem;
    }}

    h1, h2, h3, h4, p, span, label, .stMarkdown,
    [data-testid="stCaptionContainer"] {{
        color: var(--mrpl-text) !important;
        font-family: var(--mrpl-font);
    }}

    h1 {{
        font-weight: 900;
        letter-spacing: -.3px;
        padding-bottom: 14px;
        margin-bottom: 18px;
        border-bottom: 1px solid var(--mrpl-border-soft);
        background: linear-gradient(90deg, #ffffff 0%, #bcd7ee 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    h2, h3 {{ font-weight: 750; letter-spacing: -.2px; }}

    /* Section headers get a subtle accent rule */
    h2 {{
        border-left: 4px solid var(--mrpl-accent);
        padding-left: 12px;
    }}

    small, .stCaption, [data-testid="stCaptionContainer"] p {{
        color: var(--mrpl-muted) !important;
    }}

    hr {{ border-color: var(--mrpl-border-soft) !important; margin: 1.4rem 0; }}

    /* ---------------- Sidebar ---------------- */
    section[data-testid="stSidebar"] {{
        background: rgba(6, 22, 39, 0.98);
        border-right: 1px solid var(--mrpl-border-soft);
    }}

    section[data-testid="stSidebar"] > div {{
        background: linear-gradient(180deg, #08192c 0%, #050f1c 100%);
    }}

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        -webkit-text-fill-color: var(--mrpl-text) !important;
        border: none !important;
        padding: 0 !important;
    }}

    section[data-testid="stSidebar"] .stAlert {{
        border-radius: 10px;
        border: 1px solid var(--mrpl-border-soft);
    }}

    section[data-testid="stSidebar"] .stRadio > label {{
        color: #a9bed3 !important;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: .6px;
        margin-bottom: 6px;
    }}

    section[data-testid="stSidebar"] [role="radiogroup"] > label {{
        background: rgba(255,255,255,.03);
        border: 1px solid var(--mrpl-border-soft);
        border-radius: 10px;
        padding: 9px 12px;
        margin-bottom: 6px;
        transition: all .15s ease;
    }}

    section[data-testid="stSidebar"] [role="radiogroup"] > label:hover {{
        border-color: var(--mrpl-accent);
        background: rgba(47, 155, 240, .10);
        transform: translateX(2px);
    }}

    /* ---------------- Cards / containers ---------------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: linear-gradient(160deg, rgba(15, 38, 62, 0.92), rgba(9, 26, 44, 0.94));
        border: 1px solid var(--mrpl-border);
        border-radius: var(--mrpl-radius);
        box-shadow: var(--mrpl-shadow);
    }}

    div[data-testid="stMetric"] {{
        background: linear-gradient(155deg, #0f2c4a, #0a1f36);
        border: 1px solid var(--mrpl-border);
        border-left: 3px solid var(--mrpl-accent);
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 6px 18px rgba(0,0,0,.20);
        transition: transform .15s ease, box-shadow .15s ease;
    }}

    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(0,0,0,.28);
    }}

    div[data-testid="stMetricLabel"] {{
        color: var(--mrpl-muted) !important;
        font-size: 12.5px !important;
        text-transform: uppercase;
        letter-spacing: .5px;
        font-weight: 700 !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: #f5faff !important;
        font-weight: 800 !important;
    }}

    /* ---------------- Tabs ---------------- */
    button[data-baseweb="tab"] {{
        color: var(--mrpl-muted) !important;
        font-weight: 650;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--mrpl-text) !important;
    }}
    div[data-baseweb="tab-highlight"] {{
        background-color: var(--mrpl-accent) !important;
    }}
    div[data-baseweb="tab-border"] {{
        background-color: var(--mrpl-border-soft) !important;
    }}

    /* ---------------- Inputs ---------------- */
    div[data-baseweb="input"],
    div[data-baseweb="select"],
    div[data-baseweb="base-input"],
    textarea, input {{
        background: #0c2237 !important;
        color: var(--mrpl-text) !important;
        border-color: var(--mrpl-border) !important;
        border-radius: 9px !important;
    }}

    div[data-baseweb="select"] * {{ color: var(--mrpl-text) !important; }}

    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"]:focus-within {{
        border-color: var(--mrpl-accent) !important;
        box-shadow: 0 0 0 1px var(--mrpl-accent) !important;
    }}

    label p {{ font-weight: 600 !important; font-size: 13.5px !important; }}

    /* ---------------- Buttons ---------------- */
    .stButton > button,
    .stLinkButton > a,
    .stDownloadButton > button,
    .stFormSubmitButton > button {{
        border-radius: 9px;
        min-height: 42px;
        font-weight: 700;
        letter-spacing: .1px;
        border: 1px solid #2a638f;
        background: linear-gradient(135deg, #1076b8, #0a4e7d);
        color: #ffffff !important;
        box-shadow: 0 5px 14px rgba(0,0,0,.22);
        transition: all .15s ease;
    }}

    .stButton > button:hover,
    .stLinkButton > a:hover,
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {{
        border-color: #4fc0ff;
        background: linear-gradient(135deg, #1489d1, #0d5c93);
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(0,0,0,.30);
    }}

    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, var(--mrpl-accent-2), #0f9d80);
        border-color: #1bb494;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #1fe0b8, #12b494);
    }}

    /* ---------------- Dataframes / tables ---------------- */
    div[data-testid="stDataFrame"] {{
        border: 1px solid var(--mrpl-border);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 6px 16px rgba(0,0,0,.18);
    }}

    /* ---------------- Alerts ---------------- */
    div[data-testid="stAlert"] {{
        border-radius: 10px;
        border: 1px solid var(--mrpl-border-soft);
    }}

    /* ---------------- E-commerce public page ---------------- */
    .store-header {{
        background: rgba(255,255,255,.98);
        border: 1px solid #dce5ed;
        border-radius: 16px;
        padding: 16px 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 22px rgba(0,0,0,.18);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .store-brand {{
        color: #0f2942;
        font-size: 27px;
        font-weight: 900;
        line-height: 1.1;
        letter-spacing: -.3px;
    }}

    .store-tagline {{
        color: #64748b;
        font-size: 13px;
        margin-top: 4px;
        font-weight: 500;
    }}

    .store-hero {{
        position: relative;
        min-height: 300px;
        display: flex;
        align-items: center;
        padding: 46px;
        border-radius: 22px;
        overflow: hidden;
        margin-bottom: 28px;
        background-image:
            linear-gradient(
                100deg,
                rgba(3,14,26,.93),
                rgba(3,14,26,.50)
            ),
            {MRPL_BG_CSS};
        background-size: cover;
        background-position: center;
        box-shadow: 0 14px 34px rgba(0,0,0,.28);
        border: 1px solid rgba(255,255,255,.08);
    }}

    .store-hero-content {{ max-width: 720px; }}

    .store-badge {{
        display: inline-block;
        padding: 7px 14px;
        border-radius: 999px;
        background: rgba(255,255,255,.14);
        border: 1px solid rgba(255,255,255,.28);
        color: #ffffff;
        font-size: 12px;
        font-weight: 750;
        letter-spacing: .3px;
        margin-bottom: 14px;
    }}

    .store-hero-title {{
        color: #ffffff;
        font-size: 42px;
        line-height: 1.12;
        font-weight: 900;
        letter-spacing: -.5px;
        margin-bottom: 12px;
    }}

    .store-hero-text {{
        color: #e4edf5;
        font-size: 15.5px;
        line-height: 1.7;
        font-weight: 400;
    }}

    .store-section-title {{
        color: #ffffff;
        font-size: 28px;
        font-weight: 850;
        letter-spacing: -.3px;
        margin: 14px 0 4px 0;
    }}

    .store-section-subtitle {{
        color: #a9bfd4;
        font-size: 13.5px;
        margin-bottom: 18px;
    }}

    .product-name {{
        color: #ffffff;
        font-size: 18px;
        font-weight: 800;
        margin-top: 8px;
        margin-bottom: 5px;
    }}

    .product-category {{
        color: #5fc0ff;
        font-size: 11.5px;
        font-weight: 750;
        text-transform: uppercase;
        letter-spacing: .5px;
    }}

    .product-description {{
        color: #b8c9d8;
        font-size: 13px;
        line-height: 1.55;
    }}

    .category-chip {{
        background: rgba(255,255,255,.06);
        border: 1px solid #2c5578;
        border-radius: 12px;
        padding: 15px 16px;
        color: var(--mrpl-text);
        font-weight: 700;
        text-align: center;
        transition: all .15s ease;
    }}

    .category-chip:hover {{
        border-color: var(--mrpl-accent);
        background: rgba(47, 155, 240, .10);
    }}

    @media (max-width: 768px) {{
        .block-container {{ padding: 1rem .8rem 1.5rem .8rem; }}
        h1 {{ font-size: 1.8rem !important; line-height: 1.15; }}
        h2 {{ font-size: 1.45rem !important; }}
        h3 {{ font-size: 1.2rem !important; }}
        .store-hero {{ padding: 28px; min-height: 255px; }}
        .store-hero-title {{ font-size: 29px; }}
        .store-hero-text {{ font-size: 14px; }}
        .store-brand {{ font-size: 22px; }}
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
    st.markdown("---")
    st.markdown(
    "<h1 style='text-align: center;'>🏭 MRPL Smart Manufacturing System</h1>",
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

st.sidebar.success(f"👤 {username}")
st.sidebar.info(f"Role: {user_role}")

if st.sidebar.button("🚪 Logout", width="stretch"):
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

st.title("🏭 MRPL Smart Manufacturing System")

# ------------------------------------------------------------
# ADMIN / MANAGER MODULES
# ------------------------------------------------------------

if selected_module == "📊 Dashboard":
    st.header("📊 Management Dashboard")

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

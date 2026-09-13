# ============================================================
# MRPL SMART MANUFACTURING & QUALITY MANAGEMENT SYSTEM
# Professional single-admin Streamlit UI
# ============================================================

import hashlib
import sqlite3
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# ------------------------------------------------------------
# APP CONFIG
# ------------------------------------------------------------

st.set_page_config(
    page_title="MRPL Smart Manufacturing",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "mrpl.db"
CLEAN_START_VERSION = "professional_single_admin_v2"

# ------------------------------------------------------------
# PROFESSIONAL UI
# ------------------------------------------------------------

st.markdown(
    """
    <style>
    :root {
        --mrpl-navy: #12263f;
        --mrpl-blue: #1f5f8b;
        --mrpl-light: #f5f7fa;
        --mrpl-border: #e3e8ef;
        --mrpl-text: #172033;
        --mrpl-muted: #6b7280;
        --mrpl-success: #16794b;
        --mrpl-danger: #b42318;
        --mrpl-warning: #a15c00;
    }

    .stApp {
        background: #f7f9fc;
        color: var(--mrpl-text);
    }

    [data-testid="stHeader"] {
        background: rgba(247,249,252,0.92);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10243d 0%, #17395b 100%);
        border-right: 1px solid #0b1b2d;
    }

    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stSelectbox label {
        color: #f4f7fb !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        border-radius: 10px;
        padding: 8px 10px;
        margin: 2px 0;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.09);
    }

    [data-testid="stSidebar"] button {
        color: #12263f !important;
        background: #ffffff !important;
        border: 1px solid rgba(255,255,255,.35) !important;
        font-weight: 750 !important;
        border-radius: 10px !important;
        min-height: 42px !important;
    }

    [data-testid="stSidebar"] button p {
        color: #12263f !important;
    }

    [data-testid="stSidebar"] button:hover {
        background: #eef4f8 !important;
        color: #0f2944 !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        color: #f4f7fb !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label p {
        color: #f4f7fb !important;
        font-weight: 600 !important;
    }

    .top-action-row {
        margin-bottom: 14px;
    }

    .action-note {
        color: #667085;
        font-size: 12px;
        margin-top: 4px;
    }

    .mrpl-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 0 22px 0;
    }

    .mrpl-brand-icon {
        width: 46px;
        height: 46px;
        border-radius: 12px;
        background: rgba(255,255,255,0.12);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 25px;
    }

    .mrpl-brand-title {
        font-size: 17px;
        font-weight: 800;
        line-height: 1.15;
    }

    .mrpl-brand-subtitle {
        font-size: 11px;
        opacity: .72;
        margin-top: 3px;
    }

    .hero {
        background: linear-gradient(135deg, #12263f 0%, #1e5d88 100%);
        border-radius: 18px;
        padding: 28px 30px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 10px 28px rgba(18,38,63,.14);
    }

    .hero h1 {
        margin: 0;
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -.5px;
    }

    .hero p {
        margin: 8px 0 0 0;
        color: rgba(255,255,255,.82);
        font-size: 14px;
    }

    .section-title {
        font-size: 23px;
        font-weight: 800;
        margin: 8px 0 14px 0;
        color: var(--mrpl-text);
    }

    .section-subtitle {
        color: var(--mrpl-muted);
        margin-top: -8px;
        margin-bottom: 18px;
        font-size: 13px;
    }

    .metric-card {
        background: white;
        border: 1px solid var(--mrpl-border);
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 3px 12px rgba(18,38,63,.045);
        min-height: 116px;
    }

    .metric-label {
        color: var(--mrpl-muted);
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .45px;
    }

    .metric-value {
        color: var(--mrpl-navy);
        font-size: 30px;
        font-weight: 800;
        margin-top: 6px;
    }

    .metric-note {
        color: var(--mrpl-muted);
        font-size: 11px;
        margin-top: 3px;
    }

    .info-card {
        background: white;
        border: 1px solid var(--mrpl-border);
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 3px 12px rgba(18,38,63,.04);
    }

    .login-wrap {
        max-width: 520px;
        margin: 5vh auto 0 auto;
    }

    .login-card {
        background: white;
        border: 1px solid var(--mrpl-border);
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 14px 40px rgba(18,38,63,.10);
    }

    .login-logo {
        width: 64px;
        height: 64px;
        border-radius: 16px;
        background: #eaf2f8;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 34px;
        margin-bottom: 16px;
    }

    .login-title {
        font-size: 28px;
        font-weight: 800;
        color: var(--mrpl-navy);
        margin-bottom: 4px;
    }

    .login-subtitle {
        color: var(--mrpl-muted);
        font-size: 13px;
        margin-bottom: 22px;
    }

    .product-card {
        background: white;
        border: 1px solid var(--mrpl-border);
        border-radius: 16px;
        padding: 12px;
        height: 100%;
        box-shadow: 0 4px 14px rgba(18,38,63,.05);
    }

    .status-pill {
        display: inline-block;
        padding: 5px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        background: #eaf7f0;
        color: var(--mrpl-success);
    }

    .footer-note {
        text-align: center;
        color: #8993a3;
        font-size: 11px;
        margin-top: 28px;
        padding-bottom: 16px;
    }

    @media (max-width: 800px) {
        .hero { padding: 22px; border-radius: 14px; }
        .hero h1 { font-size: 26px; }
        .section-title { font-size: 20px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------

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


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = OFF")
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def migrate_schema(cur):
    for table, expected_cols in EXPECTED_SCHEMA.items():
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if cur.fetchone() is None:
            continue
        cur.execute(f"PRAGMA table_info({table})")
        existing = {row[1] for row in cur.fetchall()}
        if not set(expected_cols).issubset(existing):
            cur.execute(f"DROP TABLE {table}")


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    migrate_schema(cur)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Admin',
            employee_id INTEGER,
            is_active INTEGER DEFAULT 1
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL, designation TEXT, department TEXT,
            phone TEXT, email TEXT, joining_date TEXT, status TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER, employee_name TEXT, att_date TEXT,
            status TEXT, check_in TEXT, check_out TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER, employee_name TEXT, leave_type TEXT,
            start_date TEXT, end_date TEXT, reason TEXT, status TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER, employee_name TEXT, title TEXT,
            description TEXT, due_date TEXT, status TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name TEXT NOT NULL, category TEXT, current_stock REAL,
            minimum_stock REAL, unit TEXT, supplier TEXT, unit_price REAL,
            last_updated TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_no TEXT NOT NULL, product_name TEXT, planned_quantity REAL,
            actual_quantity REAL, start_date TEXT, end_date TEXT, status TEXT,
            machine TEXT, operator TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quality_control (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_no TEXT NOT NULL, product_name TEXT, test_date TEXT,
            parameter TEXT, result TEXT, status TEXT, inspector TEXT, remarks TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS finished_goods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL, batch_no TEXT, quantity REAL,
            unit TEXT, warehouse_location TEXT, production_date TEXT,
            expiry_date TEXT, status TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT NOT NULL, customer_name TEXT, product_name TEXT,
            quantity REAL, order_date TEXT, delivery_date TEXT, status TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dispatch (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dispatch_no TEXT NOT NULL, order_no TEXT, product_name TEXT,
            quantity REAL, dispatch_date TEXT, vehicle_no TEXT,
            driver_name TEXT, status TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT, product_name TEXT NOT NULL, description TEXT,
            image_url TEXT, is_active INTEGER DEFAULT 1
        )
    """)
    cur.execute("CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()

    # One-time clean start for the professional single-admin version.
    # This removes old/demo employees, members, orders, products, etc.
    # It does NOT run on every app refresh.
    cur.execute("SELECT value FROM app_meta WHERE key = ?", (CLEAN_START_VERSION,))
    if cur.fetchone() is None:
        cur.execute("SELECT id FROM users WHERE role = 'Admin' ORDER BY id LIMIT 1")
        admin = cur.fetchone()
        keep_admin_id = admin[0] if admin else None

        for table in [
            "attendance", "leave_requests", "tasks", "raw_materials",
            "production", "quality_control", "finished_goods", "orders",
            "dispatch", "products", "employees"
        ]:
            cur.execute(f"DELETE FROM {table}")

        # Keep exactly one administrator. Reset its credentials once for this clean professional build
        # so an old password cannot lock the owner out after deployment.
        if keep_admin_id is not None:
            cur.execute("DELETE FROM users WHERE id <> ?", (keep_admin_id,))
            cur.execute(
                "UPDATE users SET username='admin', password_hash=?, role='Admin', employee_id=NULL, is_active=1 WHERE id=?",
                (hash_password("admin123"), keep_admin_id),
            )
        else:
            cur.execute("DELETE FROM users")
            cur.execute(
                "INSERT INTO users (username,password_hash,role,employee_id,is_active) VALUES (?,?,?,?,1)",
                ("admin", hash_password("admin123"), "Admin", None),
            )

        cur.execute(
            "INSERT INTO app_meta (key,value) VALUES (?,?)",
            (CLEAN_START_VERSION, "done"),
        )
        conn.commit()

    conn.close()


init_db()

# ------------------------------------------------------------
# DB HELPERS
# ------------------------------------------------------------


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
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
    finally:
        conn.close()


def authenticate_user(username, password):
    conn = get_connection()
    user = conn.execute(
        "SELECT id,username,password_hash,role,employee_id,is_active FROM users WHERE username=?",
        (username,),
    ).fetchone()
    conn.close()
    if user and user[2] == hash_password(password) and user[5] == 1 and user[3] == "Admin":
        return user
    return None


def safe_date(value):
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date() if value else date.today()
    except (ValueError, TypeError):
        return date.today()


def label(col):
    return col.replace("_", " ").title()


def text_field(col, key, default=None):
    return st.text_input(label(col), value="" if default is None else str(default), key=key)


def number_field(col, key, default=None):
    try:
        val = float(default) if default is not None and default != "" else 0.0
    except (ValueError, TypeError):
        val = 0.0
    return st.number_input(label(col), value=val, key=key)


def date_field(col, key, default=None):
    return str(st.date_input(label(col), value=safe_date(default), key=key))


def status_field(options):
    def _field(col, key, default=None):
        idx = options.index(default) if default in options else 0
        return st.selectbox(label(col), options, index=idx, key=key)
    return _field


# ------------------------------------------------------------
# UI HELPERS
# ------------------------------------------------------------


def metric_card(label_text, value, note=""):
    return f"""
    <div class='metric-card'>
        <div class='metric-label'>{label_text}</div>
        <div class='metric-value'>{value}</div>
        <div class='metric-note'>{note}</div>
    </div>
    """


def page_header(title, subtitle, icon=""):
    st.markdown(
        f"<div class='section-title'>{icon} {title}</div>"
        f"<div class='section-subtitle'>{subtitle}</div>",
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <div class='hero'>
            <h1>MRPL Smart Manufacturing</h1>
            <p>Manufacturing, quality, inventory, warehouse and dispatch management — in one place.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_products_page(public=False):
    if public:
        st.markdown(
            """
            <div class='hero'>
                <h1>MRPL Product Catalogue</h1>
                <p>Mahakoshal Refractories — refractory products and solutions.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        page_header("Product Catalogue", "Manage products that are displayed on the public catalogue.", "🛍️")

    products = load_data("products", "is_active = 1")
    if products.empty:
        st.info("No products have been added yet.")
        return

    cats = ["All Products"] + sorted(products["category"].fillna("Other").unique().tolist())
    selected = st.selectbox("Product Category", cats, key="public_category")
    if selected != "All Products":
        products = products[products["category"].fillna("Other") == selected]

    cols = st.columns(3)
    for i, (_, row) in enumerate(products.iterrows()):
        with cols[i % 3]:
            with st.container(border=True):
                image_url = str(row.get("image_url", "") or "").strip()
                if image_url:
                    try:
                        st.image(image_url, use_container_width=True)
                    except Exception:
                        st.caption("Product image unavailable")
                st.markdown(f"### {row['product_name']}")
                if row.get("category"):
                    st.caption(str(row["category"]))
                if row.get("description"):
                    st.write(str(row["description"]))


# ------------------------------------------------------------
# GENERIC CRUD
# ------------------------------------------------------------


def crud_module(table, columns, title, icon, fields, key_prefix):
    page_header(title, "Create, review, update and remove records from the manufacturing database.", icon)
    df = load_data(table)

    if df.empty:
        st.markdown(metric_card("Records", 0, "No records added yet"), unsafe_allow_html=True)
    else:
        st.markdown(metric_card("Records", len(df), "Current database records"), unsafe_allow_html=True)
        st.write("")
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("")
    tab_add, tab_edit, tab_delete = st.tabs(["＋ Add Record", "✎ Edit Record", "Delete Record"])

    with tab_add:
        with st.form(f"{key_prefix}_add_form", clear_on_submit=True):
            values = {}
            left, right = st.columns(2)
            for i, col in enumerate(columns):
                with (left if i % 2 == 0 else right):
                    values[col] = fields[col](col, f"{key_prefix}_add_{col}", None)
            if st.form_submit_button("Add Record", type="primary", use_container_width=True):
                placeholders = ",".join(["?"] * len(columns))
                try:
                    run_query(
                        f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
                        tuple(values[c] for c in columns),
                    )
                    st.success("Record added successfully.")
                    st.rerun()
                except sqlite3.Error as exc:
                    st.error(f"Unable to add record: {exc}")

    with tab_edit:
        if df.empty:
            st.info("There are no records to edit.")
        else:
            selected_id = st.selectbox("Select record ID", df["id"].tolist(), key=f"{key_prefix}_edit_select")
            record = df[df["id"] == selected_id].iloc[0]
            with st.form(f"{key_prefix}_edit_form"):
                values = {}
                left, right = st.columns(2)
                for i, col in enumerate(columns):
                    with (left if i % 2 == 0 else right):
                        values[col] = fields[col](col, f"{key_prefix}_edit_{col}", record[col])
                if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                    try:
                        set_clause = ",".join([f"{c}=?" for c in columns])
                        run_query(
                            f"UPDATE {table} SET {set_clause} WHERE id=?",
                            tuple(values[c] for c in columns) + (selected_id,),
                        )
                        st.success("Record updated successfully.")
                        st.rerun()
                    except sqlite3.Error as exc:
                        st.error(f"Unable to update record: {exc}")

    with tab_delete:
        if df.empty:
            st.info("There are no records to delete.")
        else:
            selected_id = st.selectbox("Select record ID", df["id"].tolist(), key=f"{key_prefix}_delete_select")
            st.warning(f"Record ID {selected_id} will be permanently deleted.")
            if st.button("Delete Permanently", key=f"{key_prefix}_delete_btn", type="primary", use_container_width=True):
                run_query(f"DELETE FROM {table} WHERE id=?", (selected_id,))
                st.success("Record deleted.")
                st.rerun()


# ------------------------------------------------------------
# LOGIN / PUBLIC PAGE
# ------------------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.logged_in:
    st.markdown("""
    <div class='hero' style='max-width:1100px;margin:24px auto 26px auto;'>
        <div style='font-size:13px;opacity:.78;font-weight:700;letter-spacing:.7px;'>MAHAKOSHAL REFRACTORIES</div>
        <h1 style='margin-top:8px;'>MRPL Smart Manufacturing</h1>
        <p>Secure manufacturing operations, quality control, inventory and dispatch — managed from one professional workspace.</p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.08, 0.92], gap="large")

    with left:
        st.markdown("""
        <div class='info-card' style='padding:28px;min-height:330px;'>
            <div class='login-logo'>🏭</div>
            <h2 style='margin:0;color:#12263f;'>Administrator Console</h2>
            <p style='color:#667085;margin-top:6px;'>A centralized workspace for day-to-day manufacturing management.</p>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:24px;'>
                <div style='padding:15px;border:1px solid #e3e8ef;border-radius:12px;'><b>📦 Inventory</b><br><small style='color:#667085;'>Raw materials & finished goods</small></div>
                <div style='padding:15px;border:1px solid #e3e8ef;border-radius:12px;'><b>🏭 Production</b><br><small style='color:#667085;'>Batch & production tracking</small></div>
                <div style='padding:15px;border:1px solid #e3e8ef;border-radius:12px;'><b>🧪 Quality</b><br><small style='color:#667085;'>QC checks & results</small></div>
                <div style='padding:15px;border:1px solid #e3e8ef;border-radius:12px;'><b>🚚 Dispatch</b><br><small style='color:#667085;'>Orders & logistics</small></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class='login-card'>
            <div style='font-size:12px;color:#1f5f8b;font-weight:800;letter-spacing:.8px;'>SECURE ACCESS</div>
            <div class='login-title' style='margin-top:6px;'>Sign in</div>
            <div class='login-subtitle'>Administrator access only</div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter administrator username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            if st.form_submit_button("Sign In  →", type="primary", use_container_width=True):
                user = authenticate_user(username.strip(), password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.selected_module = "Dashboard"
                    st.session_state.show_public_products = False
                    st.rerun()
                else:
                    st.error("Invalid administrator credentials.")
                    st.caption("Initial clean-build login: admin / admin123")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style='margin-top:14px;text-align:center;color:#667085;font-size:12px;'>
            🔒 Single administrator account • No automatic member accounts
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        st.markdown("**Product Catalogue**")
        st.caption("Public product information")
    with c2:
        st.markdown("**Secure by default**")
        st.caption("Administrator-only management")
    with c3:
        st.markdown("**Ready to operate**")
        st.caption("Add only the records you need")

    if st.button("View Public Product Catalogue", use_container_width=True):
        st.session_state.show_public_products = True

    if st.session_state.get("show_public_products", False):
        st.divider()
        render_products_page(public=True)

    st.markdown("<div class='footer-note'>MRPL Smart Manufacturing • Administrator Portal</div>", unsafe_allow_html=True)
    st.stop()

# LOGGED-IN ADMIN LAYOUT
# ------------------------------------------------------------

current_user = st.session_state.user
user_id, username, _, _, _, _ = current_user

with st.sidebar:
    st.markdown(
        """
        <div class='mrpl-brand'>
            <div class='mrpl-brand-icon'>🏭</div>
            <div>
                <div class='mrpl-brand-title'>MRPL Smart</div>
                <div class='mrpl-brand-subtitle'>Manufacturing Management</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Administrator")
    st.markdown(f"**{username}**")
    st.markdown("<span class='status-pill'>● SYSTEM ACTIVE</span>", unsafe_allow_html=True)
    st.divider()

    modules = [
        "Dashboard",
        "Raw Materials",
        "Production",
        "Quality Control",
        "Finished Goods",
        "Orders & Dispatch",
        "Product Catalogue",
        "Employee Management",
        "User Management",
        "Admin Settings",
    ]
    selected_module = st.radio(
        "NAVIGATION",
        modules,
        index=modules.index(st.session_state.get("selected_module", "Dashboard")),
        label_visibility="visible",
        key="main_navigation",
    )
    st.session_state.selected_module = selected_module

    st.divider()
    if st.button("⌂  Back to Dashboard", use_container_width=True):
        st.session_state.selected_module = "Dashboard"
        st.rerun()
    if st.button("↪  Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.selected_module = "Dashboard"
        st.rerun()

# ------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------

if selected_module == "Dashboard":
    render_hero()
    st.markdown("<div class='section-title'>Operational Overview</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-subtitle'>Live summary of the records currently entered into the system.</div>",
        unsafe_allow_html=True,
    )

    raw = load_data("raw_materials")
    prod = load_data("production")
    qc = load_data("quality_control")
    fg = load_data("finished_goods")
    orders = load_data("orders")
    dispatch = load_data("dispatch")

    low_stock = 0 if raw.empty else int((raw["current_stock"] <= raw["minimum_stock"]).sum())
    passed_qc = 0 if qc.empty else int((qc["status"] == "Pass").sum())
    pending_orders = 0 if orders.empty else int(orders["status"].isin(["Confirmed", "Processing"]).sum())

    metric_cols = st.columns(4)
    metric_cols[0].markdown(metric_card("Raw Materials", len(raw), f"{low_stock} low-stock alerts"), unsafe_allow_html=True)
    metric_cols[1].markdown(metric_card("Production Batches", len(prod), "Manufacturing records"), unsafe_allow_html=True)
    metric_cols[2].markdown(metric_card("Quality Checks", len(qc), f"{passed_qc} passed"), unsafe_allow_html=True)
    metric_cols[3].markdown(metric_card("Finished Goods", len(fg), "Warehouse records"), unsafe_allow_html=True)

    st.write("")
    metric_cols2 = st.columns(3)
    metric_cols2[0].markdown(metric_card("Orders", len(orders), f"{pending_orders} active"), unsafe_allow_html=True)
    metric_cols2[1].markdown(metric_card("Dispatches", len(dispatch), "Logistics records"), unsafe_allow_html=True)
    metric_cols2[2].markdown(metric_card("Low Stock", low_stock, "Needs attention"), unsafe_allow_html=True)

    st.write("")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("### Production Status")
        if prod.empty:
            st.info("No production data yet.")
        else:
            chart = prod["status"].fillna("Unknown").value_counts()
            st.bar_chart(chart)
    with c2:
        st.markdown("### Order Status")
        if orders.empty:
            st.info("No order data yet.")
        else:
            st.bar_chart(orders["status"].fillna("Unknown").value_counts())

    if low_stock:
        st.divider()
        st.markdown("### Low Stock Alerts")
        alert_df = raw[raw["current_stock"] <= raw["minimum_stock"]].copy()
        st.dataframe(alert_df, use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# RAW MATERIALS
# ------------------------------------------------------------

elif selected_module == "Raw Materials":
    columns = ["material_name", "category", "current_stock", "minimum_stock", "unit", "supplier", "unit_price", "last_updated"]
    fields = {
        "material_name": text_field,
        "category": text_field,
        "current_stock": number_field,
        "minimum_stock": number_field,
        "unit": text_field,
        "supplier": text_field,
        "unit_price": number_field,
        "last_updated": date_field,
    }
    crud_module("raw_materials", columns, "Raw Material Management", "🧱", fields, "rm")

# ------------------------------------------------------------
# PRODUCTION
# ------------------------------------------------------------

elif selected_module == "Production":
    columns = ["batch_no", "product_name", "planned_quantity", "actual_quantity", "start_date", "end_date", "status", "machine", "operator"]
    fields = {
        "batch_no": text_field,
        "product_name": text_field,
        "planned_quantity": number_field,
        "actual_quantity": number_field,
        "start_date": date_field,
        "end_date": date_field,
        "status": status_field(["Pending", "In Progress", "Completed", "On Hold"]),
        "machine": text_field,
        "operator": text_field,
    }
    crud_module("production", columns, "Production Management", "🏭", fields, "prod")

# ------------------------------------------------------------
# QUALITY CONTROL
# ------------------------------------------------------------

elif selected_module == "Quality Control":
    columns = ["batch_no", "product_name", "test_date", "parameter", "result", "status", "inspector", "remarks"]
    fields = {
        "batch_no": text_field,
        "product_name": text_field,
        "test_date": date_field,
        "parameter": text_field,
        "result": text_field,
        "status": status_field(["Pending", "Pass", "Fail"]),
        "inspector": text_field,
        "remarks": text_field,
    }
    crud_module("quality_control", columns, "Quality Control", "🧪", fields, "qc")

# ------------------------------------------------------------
# FINISHED GOODS
# ------------------------------------------------------------

elif selected_module == "Finished Goods":
    columns = ["product_name", "batch_no", "quantity", "unit", "warehouse_location", "production_date", "expiry_date", "status"]
    fields = {
        "product_name": text_field,
        "batch_no": text_field,
        "quantity": number_field,
        "unit": text_field,
        "warehouse_location": text_field,
        "production_date": date_field,
        "expiry_date": date_field,
        "status": status_field(["Available", "Reserved", "Dispatched", "Expired"]),
    }
    crud_module("finished_goods", columns, "Finished Goods & Warehouse", "📦", fields, "fg")

# ------------------------------------------------------------
# ORDERS & DISPATCH
# ------------------------------------------------------------

elif selected_module == "Orders & Dispatch":
    page_header("Orders & Dispatch", "Track customer orders and shipment execution from one workspace.", "🚚")
    tab_orders, tab_dispatch = st.tabs(["Orders", "Dispatch"])

    with tab_orders:
        columns = ["order_no", "customer_name", "product_name", "quantity", "order_date", "delivery_date", "status"]
        fields = {
            "order_no": text_field,
            "customer_name": text_field,
            "product_name": text_field,
            "quantity": number_field,
            "order_date": date_field,
            "delivery_date": date_field,
            "status": status_field(["Confirmed", "Processing", "Shipped", "Delivered", "Cancelled"]),
        }
        crud_module("orders", columns, "Customer Orders", "📝", fields, "ord")

    with tab_dispatch:
        columns = ["dispatch_no", "order_no", "product_name", "quantity", "dispatch_date", "vehicle_no", "driver_name", "status"]
        fields = {
            "dispatch_no": text_field,
            "order_no": text_field,
            "product_name": text_field,
            "quantity": number_field,
            "dispatch_date": date_field,
            "vehicle_no": text_field,
            "driver_name": text_field,
            "status": status_field(["Scheduled", "Dispatched", "In Transit", "Delivered"]),
        }
        crud_module("dispatch", columns, "Dispatch Management", "🚚", fields, "disp")

# ------------------------------------------------------------
# EMPLOYEE MANAGEMENT
# ------------------------------------------------------------

elif selected_module == "Employee Management":
    columns = ["full_name", "designation", "department", "phone", "email", "joining_date", "status"]
    fields = {
        "full_name": text_field,
        "designation": text_field,
        "department": text_field,
        "phone": text_field,
        "email": text_field,
        "joining_date": date_field,
        "status": status_field(["Active", "Inactive", "On Leave"]),
    }
    crud_module("employees", columns, "Employee Management", "👥", fields, "emp")

# ------------------------------------------------------------
# USER MANAGEMENT — SINGLE ADMIN ONLY
# ------------------------------------------------------------

elif selected_module == "User Management":
    page_header("User Management", "View the active administrator account. Employee/member login creation is disabled.", "🔐")
    users_df = load_data("users")
    admin_df = users_df[users_df["role"] == "Admin"].copy() if not users_df.empty else pd.DataFrame()

    if admin_df.empty:
        st.warning("No administrator account is currently available.")
    else:
        st.markdown(metric_card("Administrator Accounts", len(admin_df), "System policy: exactly one admin"), unsafe_allow_html=True)
        st.write("")
        display = admin_df[["id", "username", "role", "is_active"]].copy()
        display["is_active"] = display["is_active"].map({1: "Active", 0: "Inactive"}).fillna(display["is_active"].astype(str))
        st.dataframe(display, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("### Account Policy")
        st.info("Only one Admin account is permitted. No Manager, Employee or Member user accounts are created or added from this module.")
        st.caption("To change the administrator username or password, open Admin Settings.")

# ------------------------------------------------------------
# PRODUCT CATALOGUE
# ------------------------------------------------------------

elif selected_module == "Product Catalogue":
    page_header("Product Catalogue", "Add product images, specifications and descriptions for the public catalogue.", "🛍️")
    columns = ["category", "product_name", "description", "image_url", "is_active"]
    fields = {
        "category": text_field,
        "product_name": text_field,
        "description": text_field,
        "image_url": text_field,
        "is_active": number_field,
    }
    crud_module("products", columns, "Product Catalogue Management", "🛍️", fields, "prd")

    st.divider()
    st.markdown("### Public Preview")
    render_products_page(public=False)

# ------------------------------------------------------------
# ADMIN SETTINGS — ONE ADMIN ONLY
# ------------------------------------------------------------

elif selected_module == "Admin Settings":
    page_header("Administrator Settings", "Manage the single administrator account. Member/employee accounts are intentionally disabled.", "⚙️")

    users_df = load_data("users")
    admin_df = users_df[users_df["role"] == "Admin"] if not users_df.empty else pd.DataFrame()

    if not admin_df.empty:
        st.dataframe(
            admin_df[["id", "username", "role", "is_active"]],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.markdown("### Change Administrator Credentials")
    with st.form("admin_credentials_form"):
        new_username = st.text_input("Administrator Username", value=username)
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")

        if st.form_submit_button("Update Administrator", type="primary", use_container_width=True):
            conn = get_connection()
            row = conn.execute("SELECT password_hash FROM users WHERE id=?", (user_id,)).fetchone()
            conn.close()

            if not row or row[0] != hash_password(current_password):
                st.error("Current password is incorrect.")
            elif not new_username.strip():
                st.error("Administrator username cannot be empty.")
            elif new_password and new_password != confirm_password:
                st.error("New passwords do not match.")
            elif new_password and len(new_password) < 6:
                st.error("New password should contain at least 6 characters.")
            else:
                try:
                    if new_password:
                        run_query(
                            "UPDATE users SET username=?, password_hash=?, role='Admin', employee_id=NULL, is_active=1 WHERE id=?",
                            (new_username.strip(), hash_password(new_password), user_id),
                        )
                    else:
                        run_query(
                            "UPDATE users SET username=?, role='Admin', employee_id=NULL, is_active=1 WHERE id=?",
                            (new_username.strip(), user_id),
                        )
                    st.session_state.logged_in = False
                    st.session_state.user = None
                    st.success("Administrator account updated. Please sign in again.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("That username is already in use.")

    st.divider()
    st.markdown("### Account Policy")
    st.info(
        "This version intentionally keeps one Admin account only. There is no Add User, Manager, Employee or Member creation option."
    )

st.markdown("<div class='footer-note'>MRPL Smart Manufacturing • Single Administrator System</div>", unsafe_allow_html=True)

# ============================================================
# MRPL SMART MANUFACTURING & QUALITY MANAGEMENT SYSTEM
# Role-based access (Admin / Manager / Employee) + Public Products page
# ============================================================

import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import streamlit.components.v1 as components
from datetime import date, datetime

# ============================================================
# APP CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MRPL Smart Manufacturing System",
    page_icon="🏭",
    layout="wide"
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

    # One-time clean-start marker. After the first clean start, user-added
    # employees, users, orders and other records are preserved across reruns.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT
        )
    """)
    cur.execute("SELECT setting_value FROM app_settings WHERE setting_key='clean_start_v1'")
    clean_done = cur.fetchone()

    if clean_done is None:
        # ---------------- ONE-TIME CLEAN START ----------------
        cur.execute("DELETE FROM attendance")
        cur.execute("DELETE FROM leave_requests")
        cur.execute("DELETE FROM tasks")
        cur.execute("DELETE FROM raw_materials")
        cur.execute("DELETE FROM production")
        cur.execute("DELETE FROM quality_control")
        cur.execute("DELETE FROM finished_goods")
        cur.execute("DELETE FROM orders")
        cur.execute("DELETE FROM dispatch")
        cur.execute("DELETE FROM employees")

        # Remove every old login and retain/create only Upendra as Admin.
        cur.execute("DELETE FROM users WHERE LOWER(username) <> LOWER(?)", ("Upendra",))
        cur.execute("SELECT id FROM users WHERE LOWER(username)=LOWER(?)", ("Upendra",))
        upendra = cur.fetchone()
        if upendra is None:
            cur.execute(
                "INSERT INTO users (username, password_hash, role, employee_id, is_active) VALUES (?,?,?,?,1)",
                ("Upendra", hash_password("admin123"), "Admin", None)
            )
        else:
            cur.execute(
                "UPDATE users SET role='Admin', is_active=1, employee_id=NULL WHERE id=?",
                (upendra[0],)
            )

        # Public catalogue is the only intentionally pre-populated data.
        cur.execute("DELETE FROM products")
        official_catalog = [
        ("Shaped Products", "Fireclay & High Alumina Bricks", "High-performance refractory bricks; MRPL lists grades up to 92% Al2O3.", "https://mahakoshalrefractories.com/products/shaped-refractory-products/fireclay-and-high-alumina-bricks/"),
        ("Shaped Products", "Pre-cast Pre-fired Items", "Custom-engineered pre-fired refractory items for industrial applications.", "https://mahakoshalrefractories.com/products/shaped-refractory-products/"),
        ("Shaped Products", "Silicon Carbide Bricks & Shapes", "Silicon carbide refractory shapes for demanding thermal and wear conditions.", "https://mahakoshalrefractories.com/products/shaped-refractory-products/"),
        ("Unshaped Products", "High & Medium Purity Dense Castables", "Dense monolithic refractories for high-temperature industrial applications.", "https://mahakoshalrefractories.com/products/unshaped-refractory-products/high-purity-dense-castables/"),
        ("Unshaped Products", "Low & Ultra Low Cement Castables", "High-strength low-cement castable solutions for demanding furnace zones.", "https://mahakoshalrefractories.com/products/unshaped-refractory-products/low-cement-castables/"),
        ("Unshaped Products", "Insulating Castables", "Lightweight refractory castables designed for thermal efficiency.", "https://mahakoshalrefractories.com/products/unshaped-refractory-products/insulating-castables/"),
        ("Unshaped Products", "Plastic Masses", "Application-specific refractory plastic masses.", "https://mahakoshalrefractories.com/products/"),
        ("Unshaped Products", "High Alumina Cement & Binder", "High-performance binders for refractory castables.", "https://mahakoshalrefractories.com/products/unshaped-refractory-products/high-alumina-cement/"),
        ("Unshaped Products", "Grouting Materials", "Refractory grouting solutions for industrial applications.", "https://mahakoshalrefractories.com/products/unshaped-refractory-products/grouting-material/"),
        ("Unshaped Products", "Fire Clay & High Alumina Mortars", "Heat-setting refractory mortars for demanding lining applications.", "https://mahakoshalrefractories.com/products/unshaped-refractory-products/fire-clay-high-alumina-mortars-heat-setting/"),
        ("Unshaped Products", "Gunning Mixes", "Sprayable refractory mixes for repair and maintenance applications.", "https://mahakoshalrefractories.com/products/"),
        ("Accessories", "Stainless Steel Anchors", "Refractory anchoring solutions for lining stability.", "https://mahakoshalrefractories.com/products/"),
    ]
        cur.executemany(
            "INSERT INTO products (category, product_name, description, image_url, is_active) VALUES (?,?,?,?,1)",
            official_catalog
        )
        cur.execute("INSERT INTO app_settings (setting_key, setting_value) VALUES ('clean_start_v1','done')")

    conn.commit()
    conn.close()


init_db()


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
        default_date = datetime.strptime(default, "%Y-%m-%d").date() if default else date.today()
    except (ValueError, TypeError):
        default_date = date.today()
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
        st.dataframe(df, use_container_width=True, hide_index=True)

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
    st.markdown("""
    <div class="landing-hero">
      <div>
        <div class="eyebrow">MAHAKOSHAL REFRACTORIES PVT. LTD.</div>
        <h1>Our Products</h1>
        <p>Explore MRPL's shaped and unshaped refractory product range.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.link_button("🌐 View Official MRPL Products", "https://mahakoshalrefractories.com/products/", use_container_width=True)
    st.caption("Product information is presented from Mahakoshal Refractories' official website.")
    st.divider()
    st.markdown("### Product Categories")
    products_df = load_data("products", where="is_active = 1")
    if not products_df.empty:
        categories = sorted(products_df["category"].dropna().unique().tolist())
        cols = st.columns(min(3, max(1, len(categories))))
        for i, cat in enumerate(categories):
            with cols[i % len(cols)]:
                count = int((products_df["category"] == cat).sum())
                st.markdown(f"<div class='catalog-card'><div class='catalog-icon'>▦</div><h3>{cat}</h3><p>{count} listed products</p></div>", unsafe_allow_html=True)

    st.caption("Source: Mahakoshal Refractories official Products page.")


# ============================================================
# PROFESSIONAL UI THEME
# ============================================================
st.markdown("""
<style>
:root { --mrpl-navy:#0b1f3a; --mrpl-blue:#155eef; --mrpl-bg:#f5f7fb; --mrpl-text:#172033; }
.stApp { background: var(--mrpl-bg); }
.block-container { padding-top: 2rem; max-width: 1400px; }
.landing-hero, .login-hero { background: linear-gradient(135deg,#0b1f3a,#155eef); color:white; border-radius:22px; padding:32px; margin-bottom:18px; box-shadow:0 12px 35px rgba(11,31,58,.16); }
.landing-hero h1, .login-hero h1 { margin:4px 0 8px; font-size:clamp(28px,4vw,46px); }
.landing-hero p, .login-hero p { margin:0; opacity:.88; font-size:16px; }
.eyebrow { font-size:12px; font-weight:800; letter-spacing:1.4px; opacity:.82; }
.catalog-card { background:white; border:1px solid #e5e9f2; border-radius:18px; padding:22px; min-height:145px; box-shadow:0 6px 20px rgba(16,24,40,.05); }
.catalog-icon { font-size:28px; color:#155eef; }
[data-testid="stSidebar"] { background:#0b1f3a; }
[data-testid="stSidebar"] * { color:#f5f7fb; }
[data-testid="stSidebar"] .stRadio label { padding:8px 10px; border-radius:8px; }
[data-testid="stSidebar"] button { border-radius:10px; }
[data-testid="stMetric"] { background:white; border:1px solid #e5e9f2; border-radius:14px; padding:12px; }
.stButton > button, .stFormSubmitButton > button, .stLinkButton > a { border-radius:10px; font-weight:700; min-height:42px; }
@media (max-width: 768px) { .block-container { padding-left:1rem; padding-right:1rem; } .landing-hero, .login-hero { padding:24px; border-radius:16px; } }
</style>
""", unsafe_allow_html=True)

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

    tab_login, tab_products = st.tabs(["🔐 Staff Login", "🌐 Our Products"])

    with tab_login:
        st.markdown("""
        <div class="login-hero">
          <div class="eyebrow">MRPL • SMART MANUFACTURING</div>
          <h1>Manufacturing & Quality Management</h1>
          <p>Secure operations dashboard for production, quality, inventory and dispatch.</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("🔐 Sign in to MRPL", type="primary", use_container_width=True)
            if login_button:
                user = authenticate_user(username.strip(), password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        st.caption("Initial administrator: Upendra. Change the password after your first login.")

    with tab_products:
        render_products_page()

    st.stop()


# ============================================================
# LOGGED-IN LAYOUT
# ============================================================

current_user = st.session_state.user
user_id, username, _, user_role, employee_id, _ = current_user

st.sidebar.success(f"👤 {username}")
st.sidebar.info(f"Role: {user_role}")

if st.sidebar.button("🚪 Logout", use_container_width=True,type="primary"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

st.sidebar.divider()

ROLE_MODULES = {
    "Admin": [
        "📊 Dashboard", "🧱 Raw Materials", "🏭 Production", "🧪 Quality Control",
        "📦 Finished Goods", "🚚 Orders & Dispatch", "👥 Employees",
        "🕐 Attendance", "📅 Leave & Tasks", "🛍️ Products", "🔐 Users"
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
            use_container_width=True, hide_index=True
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
    columns = ["full_name", "designation", "department", "phone", "email", "joining_date", "status"]
    fields = {
        "full_name": text_input_field, "designation": text_input_field,
        "department": text_input_field, "phone": text_input_field,
        "email": text_input_field, "joining_date": date_input_field,
        "status": status_select_field(["Active", "Inactive"]),
    }
    crud_module("employees", columns, "Employee Management", "👥", fields, "emp")

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

elif selected_module == "🔐 Users" and user_role == "Admin":
    st.header("🔐 User & Role Management")
    st.caption("Manage login accounts separately from Employee Management. Only Upendra is retained after the clean start.")

    users_df = load_data("users")
    display_df = users_df.drop(columns=["password_hash"], errors="ignore")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    tab_add, tab_transfer, tab_manage = st.tabs(["➕ Add Account", "🔄 Transfer Admin", "⚙️ Manage Accounts"])

    with tab_add:
        with st.form("add_user_form", clear_on_submit=True):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["Admin", "Manager", "Employee"])
            employees_df = load_data("employees")
            emp_options = ["None"] + employees_df["full_name"].tolist() if not employees_df.empty else ["None"]
            linked_employee = st.selectbox("Linked Employee", emp_options)
            if st.form_submit_button("Create Account", type="primary"):
                if not new_username.strip() or not new_password.strip():
                    st.error("Username and password are required.")
                else:
                    emp_id = None
                    if linked_employee != "None":
                        emp_id = int(employees_df[employees_df["full_name"] == linked_employee].iloc[0]["id"])
                    try:
                        run_query(
                            "INSERT INTO users (username, password_hash, role, employee_id, is_active) VALUES (?,?,?,?,1)",
                            (new_username.strip(), hash_password(new_password), new_role, emp_id)
                        )
                        st.success("Account created successfully.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Username already exists.")

    with tab_transfer:
        non_admin = users_df[users_df["role"] != "Admin"] if not users_df.empty else users_df
        if non_admin.empty:
            st.info("No other account is available for Admin transfer yet.")
        else:
            selected_username = st.selectbox("New Admin", non_admin["username"].tolist())
            st.warning("The selected account will become Admin. Upendra will be changed to Manager after confirmation.")
            if st.button("🔄 Confirm Admin Transfer", type="primary"):
                target_id = int(non_admin[non_admin["username"] == selected_username].iloc[0]["id"])
                up = users_df[users_df["username"].str.lower() == "upendra"]
                if not up.empty:
                    run_query("UPDATE users SET role='Manager' WHERE id=?", (int(up.iloc[0]["id"]),))
                run_query("UPDATE users SET role='Admin', is_active=1 WHERE id=?", (target_id,))
                st.success(f"Admin transferred to {selected_username}.")
                st.rerun()

    with tab_manage:
        if users_df.empty:
            st.info("No accounts available.")
        else:
            selected_id = st.selectbox("Select account", users_df["id"].tolist(), format_func=lambda x: users_df.loc[users_df["id"] == x, "username"].iloc[0])
            selected_row = users_df[users_df["id"] == selected_id].iloc[0]
            c1, c2 = st.columns(2)
            with c1:
                new_role_edit = st.selectbox("Change Role", ["Admin", "Manager", "Employee"], index=["Admin","Manager","Employee"].index(selected_row["role"]))
                if st.button("Save Role"):
                    if selected_row["username"].lower() == "upendra" and new_role_edit != "Admin":
                        st.error("Upendra is the initial protected Admin. Use Admin Transfer first.")
                    else:
                        run_query("UPDATE users SET role=? WHERE id=?", (new_role_edit, selected_id))
                        st.success("Role updated.")
                        st.rerun()
            with c2:
                if st.button("Deactivate Account"):
                    if selected_row["username"].lower() == "upendra":
                        st.error("The protected Upendra Admin cannot be deactivated.")
                    else:
                        run_query("UPDATE users SET is_active=0 WHERE id=?", (selected_id,))
                        st.success("Account deactivated.")
                        st.rerun()
                if st.button("Delete Account"):
                    if selected_row["username"].lower() == "upendra":
                        st.error("The protected Upendra Admin cannot be deleted.")
                    else:
                        run_query("DELETE FROM users WHERE id=?", (selected_id,))
                        st.success("Account deleted.")
                        st.rerun()

# ------------------------------------------------------------
# EMPLOYEE SELF-SERVICE MODULES
# ------------------------------------------------------------

elif selected_module == "🕘 My Attendance":
    st.header("🕘 My Attendance")

    # -----------------------------------------
    # SUCCESS MESSAGE
    # -----------------------------------------
    if "attendance_message" in st.session_state:
        st.success(st.session_state.attendance_message)
        del st.session_state.attendance_message

    # -----------------------------------------
    # CHECK EMPLOYEE PROFILE
    # -----------------------------------------
    if not employee_id:
        st.error("No employee profile is linked to this account.")
    else:

        emp_data = load_data(
            "employees",
            where="id = ?",
            params=(employee_id,)
        )

        if emp_data.empty:
            st.error("Employee profile not found.")
        else:

            emp_name = emp_data.iloc[0]["full_name"]

            # -----------------------------------------
            # ATTENDANCE HISTORY
            # -----------------------------------------
            st.subheader("📋 Attendance History")

            my_att = load_data(
                "attendance",
                where="employee_id = ?",
                params=(employee_id,)
            )

            if not my_att.empty:

                # Date ko string mein convert karke
                # latest attendance sabse upar rakho
                my_att["att_date"] = my_att["att_date"].astype(str)

                my_att = my_att.sort_values(
                    by="att_date",
                    ascending=False
                )

                # Sirf required columns
                columns = [
                    "employee_name",
                    "att_date",
                    "status",
                    "check_in",
                    "check_out"
                ]

                existing_columns = [
                    col for col in columns
                    if col in my_att.columns
                ]

                # Column names user-friendly
                display_att = my_att[existing_columns].copy()

                rename_columns = {
                    "employee_name": "Employee Name",
                    "att_date": "Attendance Date",
                    "status": "Status",
                    "check_in": "Check-in",
                    "check_out": "Check-out"
                }

                display_att = display_att.rename(
                    columns=rename_columns
                )

                st.dataframe(
                    display_att,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No attendance records found.")

            # -----------------------------------------
            # TODAY'S ATTENDANCE
            # -----------------------------------------
            st.divider()

            st.subheader("📅 Today's Attendance")

            today_str = str(date.today())

            today_att = load_data(
                "attendance",
                where="employee_id = ? AND att_date = ?",
                params=(employee_id, today_str)
            )

            # -----------------------------------------
            # NO ATTENDANCE MARKED TODAY
            # -----------------------------------------
            if today_att.empty:

                st.write(f"**Employee:** {emp_name}")
                st.write(f"**Date:** {today_str}")

                if st.button(
                    "✅ Mark Present",
                    key="mark_present"
                ):

                    from datetime import datetime
                    from zoneinfo import ZoneInfo

                    check_in_time = datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).strftime("%Y-%m-%d %H:%M:%S")

                    run_query(
                        """
                        INSERT INTO attendance
                        (
                            employee_id,
                            employee_name,
                            att_date,
                            status,
                            check_in,
                            check_out
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            employee_id,
                            emp_name,
                            today_str,
                            "Present",
                            check_in_time,
                            None
                        )
                    )

                    st.session_state.attendance_message = (
                        "Your attendance marked"
                    )

                    st.rerun()

            # -----------------------------------------
            # ATTENDANCE ALREADY MARKED
            # -----------------------------------------
            else:

                today_row = today_att.iloc[0]

                st.success("Your attendance marked")

                st.write(f"**Employee:** {emp_name}")
                st.write(f"**Date:** {today_str}")
                st.write(
                    f"**Status:** {today_row['status']}"
                )

                # -----------------------------------------
                # CHECK-IN TIME
                # -----------------------------------------
                if (
                    "check_in" in today_row.index
                    and today_row["check_in"]
                ):
                    st.write(
                        f"**Check-in:** {today_row['check_in']}"
                    )

                # -----------------------------------------
                # CHECK-OUT
                # -----------------------------------------
                check_out_value = (
                    today_row["check_out"]
                    if "check_out" in today_row.index
                    else None
                )

                if check_out_value:
                    st.write(
                        f"**Check-out:** {check_out_value}"
                    )

                    st.info(
                        "Today's attendance is complete."
                    )

                else:

                    st.warning(
                        "Check-out is still pending."
                    )

                    if st.button(
                        "🚪 Check Out",
                        key="check_out_today"
                    ):

                        from datetime import datetime
                        from zoneinfo import ZoneInfo

                        check_out_time = datetime.now(
                            ZoneInfo("Asia/Kolkata")
                        ).strftime("%Y-%m-%d %H:%M:%S")

                        run_query(
                            """
                            UPDATE attendance
                            SET check_out = ?
                            WHERE employee_id = ?
                            AND att_date = ?
                            """,
                            (
                                check_out_time,
                                employee_id,
                                today_str
                            )
                        )

                        st.session_state.attendance_message = (
                            "Check-out recorded successfully."
                        )

                        st.rerun()
elif selected_module == "📅 My Leave":
    st.header("📅 My Leave")
    my_leave = load_data("leave_requests", where="employee_id = ?", params=(employee_id,))
    st.dataframe(my_leave, use_container_width=True, hide_index=True)

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

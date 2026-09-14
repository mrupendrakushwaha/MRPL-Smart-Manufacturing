# ============================================================
# MRPL SMART MANUFACTURING & QUALITY MANAGEMENT SYSTEM
# Role-based access (Admin / Manager / Employee) + Public Products page
# ============================================================

import streamlit as st
import sqlite3
import hashlib
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

def india_now():
    """Return current India time for attendance records."""
    return datetime.now(ZoneInfo("Asia/Kolkata"))



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

    # ---------------- SEED DATA (only if empty) ----------------

    cur.execute("SELECT COUNT(*) FROM employees")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO employees (full_name, designation, department, phone, email, joining_date, status) VALUES (?,?,?,?,?,?,?)",
            [
                ("Rahul Sharma", "Machine Operator", "Production", "9876543210", "rahul@mrpl.com", "2024-01-15", "Active"),
                ("Sneha Patil", "Quality Inspector", "Quality", "9876500000", "sneha@mrpl.com", "2023-11-01", "Active"),
                ("Aman Verma", "Warehouse Staff", "Warehouse", "9876511111", "aman@mrpl.com", "2024-03-10", "Active"),
            ]
        )
        conn.commit()

    # Initial Admin accounts. Passwords are stored only as SHA-256 hashes.
    # If Streamlit Secrets contains [initial_admins], those passwords are used
    # only when an initial account does not already exist.
    initial_admins = {
        "Upendra": "25bf9ca42c07a89c32462ec7945ba81f82f597e5c600dcac71c73ae7ba22af47",
        "Sandeephaldkar": "83aa63490b41045748632ae5d1ffb80220ff3adcc8540de6bb60cdfe7f441f90",
    }
    try:
        secret_admins = st.secrets.get("initial_admins", {})
        for admin_username in list(initial_admins):
            secret_password = str(secret_admins.get(admin_username, ""))
            if secret_password:
                initial_admins[admin_username] = hash_password(secret_password)
    except Exception:
        pass

    # Remove only the old demo accounts from earlier versions.
    cur.execute("DELETE FROM users WHERE username IN ('admin', 'manager', 'employee')")

    for admin_username, admin_hash in initial_admins.items():
        cur.execute("SELECT id FROM users WHERE username = ?", (admin_username,))
        existing = cur.fetchone()
        if existing is None:
            cur.execute(
                "INSERT INTO users (username, password_hash, role, employee_id, is_active) VALUES (?,?,?,?,1)",
                (admin_username, admin_hash, "Admin", None)
            )

    cur.execute("SELECT COUNT(*) FROM attendance")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO attendance (employee_id, employee_name, att_date, status, check_in, check_out) VALUES (?,?,?,?,?,?)",
            [
                (1, "Rahul Sharma", str(date.today()), "Present", "09:00", "18:00"),
            ]
        )

    cur.execute("SELECT COUNT(*) FROM leave_requests")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO leave_requests (employee_id, employee_name, leave_type, start_date, end_date, reason, status) VALUES (?,?,?,?,?,?,?)",
            [
                (1, "Rahul Sharma", "Sick Leave", str(date.today()), str(date.today()), "Fever", "Pending"),
            ]
        )

    cur.execute("SELECT COUNT(*) FROM tasks")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO tasks (employee_id, employee_name, title, description, due_date, status) VALUES (?,?,?,?,?,?)",
            [
                (1, "Rahul Sharma", "Machine calibration", "Calibrate Line-A before next batch", str(date.today()), "Pending"),
            ]
        )

    cur.execute("SELECT COUNT(*) FROM raw_materials")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO raw_materials (material_name, category, current_stock, minimum_stock, unit, supplier, unit_price, last_updated) VALUES (?,?,?,?,?,?,?,?)",
            [
                ("Fireclay", "Raw Clay", 1200, 500, "Kg", "Local Supplier", 18.5, str(date.today())),
                ("Bauxite", "Raw Ore", 800, 400, "Kg", "Odisha Mines", 32.0, str(date.today())),
                ("Silicon Carbide", "Additive", 150, 200, "Kg", "BASF India", 210.0, str(date.today())),
            ]
        )

    cur.execute("SELECT COUNT(*) FROM production")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO production (batch_no, product_name, planned_quantity, actual_quantity, start_date, end_date, status, machine, operator) VALUES (?,?,?,?,?,?,?,?,?)",
            [
                ("B-1001", "Fireclay Bricks", 1000, 980, str(date.today()), str(date.today()), "Completed", "Line-A", "Rahul Sharma"),
                ("B-1002", "Dense Castable", 500, 200, str(date.today()), None, "In Progress", "Line-B", "Rahul Sharma"),
            ]
        )

    cur.execute("SELECT COUNT(*) FROM quality_control")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO quality_control (batch_no, product_name, test_date, parameter, result, status, inspector, remarks) VALUES (?,?,?,?,?,?,?,?)",
            [
                ("B-1001", "Fireclay Bricks", str(date.today()), "Refractoriness", "1580°C", "Pass", "Sneha Patil", "Within spec"),
            ]
        )

    cur.execute("SELECT COUNT(*) FROM finished_goods")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO finished_goods (product_name, batch_no, quantity, unit, warehouse_location, production_date, expiry_date, status) VALUES (?,?,?,?,?,?,?,?)",
            [
                ("Fireclay Bricks", "B-1001", 980, "Pieces", "WH-1 Rack A", str(date.today()), "", "Available"),
            ]
        )

    cur.execute("SELECT COUNT(*) FROM orders")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO orders (order_no, customer_name, product_name, quantity, order_date, delivery_date, status) VALUES (?,?,?,?,?,?,?)",
            [
                ("ORD-501", "Bharat Steel Works", "Fireclay Bricks", 200, str(date.today()), "2026-09-25", "Confirmed"),
            ]
        )

    cur.execute("SELECT COUNT(*) FROM dispatch")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO dispatch (dispatch_no, order_no, product_name, quantity, dispatch_date, vehicle_no, driver_name, status) VALUES (?,?,?,?,?,?,?,?)",
            [
                ("DSP-301", "ORD-501", "Fireclay Bricks", 200, str(date.today()), "MH-12-AB-1234", "V. Patil", "Dispatched"),
            ]
        )

    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        catalog = [
            ("Shaped Products", "Fireclay & High Alumina Bricks", "High refractoriness bricks for furnace linings.", "https://placehold.co/400x260?text=Fireclay+Bricks"),
            ("Shaped Products", "Pre-Cast Pre-Fired (PCPF) Blocks", "Ready-to-install pre-fired refractory blocks.", "https://placehold.co/400x260?text=PCPF+Blocks"),
            ("Shaped Products", "Silicon Carbide Bricks & Shapes", "High thermal conductivity SiC shapes.", "https://placehold.co/400x260?text=SiC+Bricks"),
            ("Shaped Products", "Acid-resistant Bricks", "Bricks resistant to acidic environments.", "https://placehold.co/400x260?text=Acid+Resistant+Bricks"),
            ("Unshaped Products", "Dense Castables", "High density monolithic refractory castable.", "https://placehold.co/400x260?text=Dense+Castables"),
            ("Unshaped Products", "Low & Ultra Low Cement Castables", "Low cement content for high strength.", "https://placehold.co/400x260?text=LC+Ultra+LC+Castables"),
            ("Unshaped Products", "Insulating Castables", "Lightweight insulating refractory castable.", "https://placehold.co/400x260?text=Insulating+Castables"),
            ("Unshaped Products", "Plastic Masses", "Ramming and plastic refractory masses.", "https://placehold.co/400x260?text=Plastic+Masses"),
            ("Unshaped Products", "High Alumina Cement & Binder", "Binder for refractory castables.", "https://placehold.co/400x260?text=HA+Cement"),
            ("Unshaped Products", "Grouting Materials", "Refractory grouting compounds.", "https://placehold.co/400x260?text=Grouting+Materials"),
            ("Unshaped Products", "Mortars", "Refractory jointing mortars.", "https://placehold.co/400x260?text=Mortars"),
            ("Unshaped Products", "Gunning Mixes", "Sprayable refractory repair mixes.", "https://placehold.co/400x260?text=Gunning+Mixes"),
        ]
        cur.executemany(
            "INSERT INTO products (category, product_name, description, image_url, is_active) VALUES (?,?,?,?,1)",
            catalog
        )

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
    st.title("🏭 MRPL — Mahakoshal Refractories")
    st.subheader("🌐 Our Products")
    st.caption("Browse our product catalog. No login required.")

    products_df = load_data("products", where="is_active = 1")

    if products_df.empty:
        st.info("No products available right now.")
        return

    categories = ["All Products"] + sorted(products_df["category"].dropna().unique().tolist())
    selected_category = st.selectbox("Select Product Category", categories)

    if selected_category != "All Products":
        products_df = products_df[products_df["category"] == selected_category]

    for cat in products_df["category"].unique():
        st.markdown(f"### {cat}")
        cat_products = products_df[products_df["category"] == cat]

        cols = st.columns(3)
        for i, (_, row) in enumerate(cat_products.iterrows()):
            with cols[i % 3]:
                with st.container(border=True):
                    if row["image_url"]:
                        st.image(row["image_url"], use_container_width=True)
                    st.markdown(f"**{row['product_name']}**")
                    st.caption(row["description"] or "")
        st.write("")


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "attendance_message" not in st.session_state:
    st.session_state.attendance_message = None


# ============================================================
# LOGIN / PUBLIC LANDING PAGE
# ============================================================

if not st.session_state.logged_in:

    tab_login, tab_products = st.tabs(["🔐 Staff Login", "🌐 Our Products"])

    with tab_login:
        st.title("🏭 MRPL Smart Manufacturing System")
        st.subheader("🔐 Login")

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("🔑 Login", type="primary", use_container_width=True)

            if login_button:
                user = authenticate_user(username.strip(), password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        st.caption("Login credentials are managed securely by the Admin.")

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

if st.sidebar.button("🚪 Logout", use_container_width=True):
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
                            "INSERT INTO users (username, password_hash, role, employee_id, is_active) VALUES (?, ?, 'Admin', NULL, 1)",
                            (admin_username.strip(), hash_password(admin_password))
                        )
                        st.success("Admin created successfully.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Username already exists.")

    with tab_other:
        st.subheader("➕ Add Manager / Employee")
        employees_df = load_data("employees")
        employee_map = {"Not linked": None}
        if not employees_df.empty:
            for _, emp_row in employees_df.iterrows():
                label = f"{emp_row['full_name']} (ID: {int(emp_row['id'])})"
                employee_map[label] = int(emp_row["id"])

        with st.form("add_user_form", clear_on_submit=True):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_password2 = st.text_input("Confirm Password", type="password")
            new_role = st.selectbox("Role", ["Manager", "Employee"])
            linked_employee = st.selectbox("Linked Employee", list(employee_map.keys()))

            if st.form_submit_button("Create User", type="primary", width="stretch"):
                if not new_username.strip() or not new_password:
                    st.error("Username and password are required.")
                elif new_password != new_password2:
                    st.error("Passwords do not match.")
                elif len(new_password) < 8:
                    st.error("Use a password of at least 8 characters.")
                else:
                    try:
                        run_query(
                            "INSERT INTO users (username, password_hash, role, employee_id, is_active) VALUES (?, ?, ?, ?, 1)",
                            (new_username.strip(), hash_password(new_password), new_role, employee_map[linked_employee])
                        )
                        st.success("User created successfully.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Username already exists.")

    st.divider()
    st.subheader("🔗 Link / Edit Account")
    users_df = load_data("users")
    if not users_df.empty:
        user_choices = [
            f"{row['username']} — {row['role']} (ID: {int(row['id'])})"
            for _, row in users_df.iterrows()
        ]
        selected_user_label = st.selectbox("Select Account", user_choices, key="admin_manage_user_select")
        selected_user_id = int(selected_user_label.rsplit("ID: ", 1)[1].rstrip(")"))
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
            new_link = st.selectbox("Employee Profile", link_options, index=current_index)
            active_value = st.checkbox("Account Active", value=bool(selected_user["is_active"]))
            if st.form_submit_button("Save Account Settings", width="stretch"):
                run_query(
                    "UPDATE users SET employee_id = ?, is_active = ? WHERE id = ?",
                    (employee_map[new_link], 1 if active_value else 0, selected_user_id)
                )
                st.success("Account settings updated.")
                st.rerun()

    st.divider()
    st.subheader("🛡️ Admin Account Protection")
    active_admins = load_data("users", where="role = 'Admin' AND is_active = 1")
    st.caption("The system will not allow the last active Admin account to be deactivated or deleted.")
    if not active_admins.empty:
        st.dataframe(active_admins[["id", "username", "role", "is_active"]], width="stretch", hide_index=True)

    if not users_df.empty:
        manage_user_id = st.selectbox("Select account for deactivation / deletion", users_df["id"].tolist(), key="admin_delete_user_select")
        manage_user = users_df[users_df["id"] == manage_user_id].iloc[0]
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Deactivate Account", key="deactivate_user_btn", width="stretch"):
                if manage_user["role"] == "Admin" and int(manage_user["is_active"]) == 1 and len(active_admins) <= 1:
                    st.error("You cannot deactivate the last active Admin.")
                elif int(manage_user_id) == int(user_id):
                    st.error("You cannot deactivate your own current Admin account.")
                else:
                    run_query("UPDATE users SET is_active = 0 WHERE id = ?", (manage_user_id,))
                    st.success("Account deactivated.")
                    st.rerun()
        with c2:
            if st.button("Delete Permanently", key="delete_user_btn", width="stretch"):
                if manage_user["role"] == "Admin" and int(manage_user["is_active"]) == 1 and len(active_admins) <= 1:
                    st.error("You cannot delete the last active Admin.")
                elif int(manage_user_id) == int(user_id):
                    st.error("You cannot delete your own current Admin account.")
                else:
                    run_query("DELETE FROM users WHERE id = ?", (manage_user_id,))
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

    if st.session_state.attendance_message:
        st.success(st.session_state.attendance_message)
        st.session_state.attendance_message = None

    now = india_now()
    today_str = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")

    emp_name_row = load_data("employees", where="id = ?", params=(employee_id,))
    emp_name = emp_name_row.iloc[0]["full_name"] if not emp_name_row.empty else username

    today_att = load_data(
        "attendance",
        where="employee_id = ? AND att_date = ?",
        params=(employee_id, today_str)
    )

    st.subheader("📅 Today's Attendance")

    if today_att.empty:
        st.info("Today's attendance has not been marked yet.")
        if st.button("🟢 Mark Present — Check-in Now", type="primary", width="stretch"):
            check = load_data("attendance", where="employee_id = ? AND att_date = ?", params=(employee_id, today_str))
            if check.empty:
                run_query(
                    "INSERT INTO attendance (employee_id, employee_name, att_date, status, check_in, check_out) VALUES (?,?,?,?,?,?)",
                    (employee_id, emp_name, today_str, "Present", current_time, None)
                )
                st.session_state.attendance_message = f"Attendance marked successfully. Check-in: {current_time}"
                st.rerun()
            else:
                st.warning("Today's attendance is already marked.")
    else:
        record = today_att.iloc[0]
        check_in = record["check_in"] or "—"
        check_out = record["check_out"] or "—"

        c1, c2, c3 = st.columns(3)
        c1.metric("Status", record["status"] or "Present")
        c2.metric("Check-in", check_in)
        c3.metric("Check-out", check_out)

        if pd.isna(record["check_out"]) or not str(record["check_out"]).strip():
            st.info("Check-in is complete. Please check out when your workday ends.")
            if st.button("🔴 Check-out Now", type="primary", width="stretch"):
                run_query(
                    "UPDATE attendance SET check_out = ? WHERE id = ? AND check_out IS NULL",
                    (current_time, int(record["id"]))
                )
                st.session_state.attendance_message = f"Attendance updated successfully. Check-out: {current_time}"
                st.rerun()
        else:
            st.success("Today's attendance is complete — Check-in and Check-out both recorded.")

    st.divider()
    st.subheader("📋 Attendance History")
    my_att = load_data(
        "attendance",
        where="employee_id = ?",
        params=(employee_id,)
    )
    if not my_att.empty:
        my_att["att_date"] = my_att["att_date"].astype(str)
        my_att = my_att.sort_values(by="att_date", ascending=False)
        history_columns = ["employee_name", "att_date", "status", "check_in", "check_out"]
        existing_columns = [c for c in history_columns if c in my_att.columns]
        st.dataframe(my_att[existing_columns], width="stretch", hide_index=True)
    else:
        st.info("No attendance records found.")

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

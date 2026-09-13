
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(
    page_title="MRPL Smart Management System",
    page_icon="🏭",
    layout="wide"
)

# -----------------------------
# DATABASE CONNECTION
# -----------------------------

DB_PATH = "mrpl.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# -----------------------------
# HEADER
# -----------------------------

st.title("🏭 MRPL Smart Management System")
st.caption("Smart Manufacturing & Quality Management System")

st.divider()

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("📋 Navigation")

menu = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Raw Materials",
        "Production",
        "Quality Control",
        "Finished Goods",
        "Orders & Dispatch"
    ]
)

# -----------------------------
# DASHBOARD
# -----------------------------

if menu == "Dashboard":

    st.header("📊 Management Dashboard")

    conn = get_connection()

    raw_materials = pd.read_sql_query(
        "SELECT * FROM raw_materials",
        conn
    )

    production = pd.read_sql_query(
        "SELECT * FROM production",
        conn
    )

    finished_goods = pd.read_sql_query(
        "SELECT * FROM finished_goods",
        conn
    )

    orders = pd.read_sql_query(
        "SELECT * FROM orders",
        conn
    )

    dispatch = pd.read_sql_query(
        "SELECT * FROM dispatch",
        conn
    )

    conn.close()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🧱 Raw Materials", len(raw_materials))

    with col2:
        st.metric("🏭 Production Records", len(production))

    with col3:
        st.metric("📦 Finished Goods", len(finished_goods))

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("📝 Orders", len(orders))

    with col5:
        st.metric("🚚 Dispatches", len(dispatch))

    with col6:
        st.metric("⚠️ Low Stock",
                  len(raw_materials[
                      raw_materials["current_stock"]
                      <= raw_materials["minimum_stock"]
                  ]) if not raw_materials.empty else 0)

# -----------------------------
# OTHER MODULES
# -----------------------------

elif menu == "Raw Materials":
    st.header("🧱 Raw Material Management")
    st.info("Raw Material module")

elif menu == "Production":
    st.header("🏭 Production Management")
    st.info("Production module")

elif menu == "Quality Control":
    st.header("✅ Quality Control")
    st.info("Quality Control module")

elif menu == "Finished Goods":
    st.header("📦 Finished Goods / Warehouse")
    st.info("Finished Goods module")

elif menu == "Orders & Dispatch":
    st.header("🚚 Orders & Dispatch")
    st.info("Orders & Dispatch module")

import streamlit as st
import sqlite3
import pandas as pd

# =========================================================
# MRPL SMART MANAGEMENT SYSTEM
# STEP 1 - RAW MATERIAL MANAGEMENT
# =========================================================

st.set_page_config(
    page_title="MRPL Smart Management System",
    page_icon="🏭",
    layout="wide"
)

DB_PATH = "mrpl.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# =========================================================
# RAW MATERIAL FUNCTIONS
# =========================================================

def add_raw_material(material_code, name, unit, minimum_stock, supplier):

    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO raw_materials
            (
                material_code,
                name,
                unit,
                minimum_stock,
                supplier
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                material_code,
                name,
                unit,
                minimum_stock,
                supplier
            )
        )

        conn.commit()
        return True, "Raw material added successfully."

    except sqlite3.IntegrityError:
        return False, "Material code already exists."

    finally:
        conn.close()


def get_raw_materials():

    conn = get_connection()

    data = pd.read_sql_query(
        """
        SELECT
            id,
            material_code,
            name,
            unit,
            minimum_stock,
            supplier,
            created_at
        FROM raw_materials
        ORDER BY id DESC
        """,
        conn
    )

    conn.close()

    return data


def delete_raw_material(material_id):

    conn = get_connection()

    conn.execute(
        "DELETE FROM raw_materials WHERE id = ?",
        (material_id,)
    )

    conn.commit()
    conn.close()


# =========================================================
# HEADER
# =========================================================

st.title("🏭 MRPL Smart Management System")
st.caption("Smart Manufacturing & Quality Management System")

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📋 Navigation")

menu = st.sidebar.radio(
    "Select Module",
    [
        "Raw Materials"
    ]
)


# =========================================================
# RAW MATERIAL MANAGEMENT
# =========================================================

if menu == "Raw Materials":

    st.header("🧱 Raw Material Management")

    # -----------------------------------------------------
    # ADD RAW MATERIAL
    # -----------------------------------------------------

    st.subheader("➕ Add Raw Material")

    with st.form("add_raw_material_form"):

        col1, col2 = st.columns(2)

        with col1:

            material_code = st.text_input(
                "Material Code"
            )

            name = st.text_input(
                "Material Name"
            )

            unit = st.text_input(
                "Unit",
                placeholder="Kg / Ton / Bag"
            )

        with col2:

            minimum_stock = st.number_input(
                "Minimum Stock",
                min_value=0.0,
                value=0.0,
                step=1.0
            )

            supplier = st.text_input(
                "Supplier"
            )

        submitted = st.form_submit_button(
            "➕ Add Material",
            use_container_width=True
        )

        if submitted:

            if not material_code.strip():

                st.error("Material Code is required.")

            elif not name.strip():

                st.error("Material Name is required.")

            else:

                success, message = add_raw_material(
                    material_code.strip(),
                    name.strip(),
                    unit.strip(),
                    minimum_stock,
                    supplier.strip()
                )

                if success:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)


    st.divider()


    # -----------------------------------------------------
    # RAW MATERIAL LIST
    # -----------------------------------------------------

    st.subheader("📋 Raw Material List")

    materials = get_raw_materials()

    if materials.empty:

        st.info("No raw materials available.")

    else:

        st.dataframe(
            materials,
            use_container_width=True,
            hide_index=True
        )


        # -------------------------------------------------
        # DELETE MATERIAL
        # -------------------------------------------------

        st.subheader("🗑️ Delete Raw Material")

        material_options = {
            f"{row.material_code} - {row.name}": row.id
            for _, row in materials.iterrows()
        }

        selected_material = st.selectbox(
            "Select Material",
            list(material_options.keys())
        )

        if st.button(
            "🗑️ Delete Selected Material",
            type="secondary"
        ):

            material_id = material_options[selected_material]

            delete_raw_material(material_id)

            st.success("Raw material deleted successfully.")

            st.rerun()


# =========================================================
# END
# =========================================================
# =========================================================
# EDIT RAW MATERIAL
# =========================================================

def update_raw_material(
    material_id,
    material_code,
    name,
    unit,
    minimum_stock,
    supplier
):

    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE raw_materials
            SET
                material_code = ?,
                name = ?,
                unit = ?,
                minimum_stock = ?,
                supplier = ?
            WHERE id = ?
            """,
            (
                material_code,
                name,
                unit,
                minimum_stock,
                supplier,
                material_id
            )
        )

        conn.commit()

        return True, "Raw material updated successfully."

    except sqlite3.IntegrityError:
        return False, "Material code already exists."

    finally:
        conn.close()


# =========================================================
# EDIT MATERIAL UI
# =========================================================

st.divider()

st.subheader("✏️ Edit Raw Material")

materials_edit = get_raw_materials()

if not materials_edit.empty:

    edit_options = {
        f"{row.material_code} - {row.name}": row
        for _, row in materials_edit.iterrows()
    }

    selected_edit = st.selectbox(
        "Select Material to Edit",
        list(edit_options.keys()),
        key="edit_material"
    )

    selected_row = edit_options[selected_edit]

    with st.form("edit_raw_material_form"):

        col1, col2 = st.columns(2)

        with col1:

            edit_code = st.text_input(
                "Material Code",
                value=str(selected_row.material_code)
            )

            edit_name = st.text_input(
                "Material Name",
                value=str(selected_row.name)
            )

            edit_unit = st.text_input(
                "Unit",
                value=str(selected_row.unit or "")
            )

        with col2:

            edit_minimum_stock = st.number_input(
                "Minimum Stock",
                min_value=0.0,
                value=float(selected_row.minimum_stock or 0)
            )

            edit_supplier = st.text_input(
                "Supplier",
                value=str(selected_row.supplier or "")
            )

        update_button = st.form_submit_button(
            "💾 Update Material",
            use_container_width=True
        )

        if update_button:

            if not edit_code.strip():

                st.error("Material Code is required.")

            elif not edit_name.strip():

                st.error("Material Name is required.")

            else:

                success, message = update_raw_material(
                    selected_row.id,
                    edit_code.strip(),
                    edit_name.strip(),
                    edit_unit.strip(),
                    edit_minimum_stock,
                    edit_supplier.strip()
                )

                if success:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)


# =======================================================
            
# END OF RAW MATERIAL MODULE
# ======================================================
# =========================================================
# PRODUCTION MANAGEMENT
# =========================================================

elif menu == "Production":

    st.header("🏭 Production Management")

    conn = get_connection()

    products = pd.read_sql_query(
        """
        SELECT id, product_code, name
        FROM products
        ORDER BY name
        """,
        conn
    )

    production = pd.read_sql_query(
        """
        SELECT
            p.id,
            pr.product_code,
            pr.name AS product_name,
            p.batch_number,
            p.production_date,
            p.planned_quantity,
            p.actual_quantity,
            p.rejected_quantity,
            p.status
        FROM production p
        JOIN products pr
            ON p.product_id = pr.id
        ORDER BY p.id DESC
        """,
        conn
    )

    conn.close()

    # -----------------------------------------------------
    # ADD PRODUCTION
    # -----------------------------------------------------

    st.subheader("➕ Add Production Record")

    if products.empty:

        st.warning(
            "No products available. Please add a product first."
        )

    else:

        product_options = {
            f"{row.product_code} - {row.name}": row.id
            for _, row in products.iterrows()
        }

        with st.form("add_production_form"):

            col1, col2 = st.columns(2)

            with col1:

                selected_product = st.selectbox(
                    "Select Product",
                    list(product_options.keys())
                )

                batch_number = st.text_input(
                    "Batch Number"
                )

                production_date = st.date_input(
                    "Production Date"
                )

                planned_quantity = st.number_input(
                    "Planned Quantity",
                    min_value=0.0,
                    step=1.0
                )

            with col2:

                actual_quantity = st.number_input(
                    "Actual Quantity",
                    min_value=0.0,
                    step=1.0
                )

                rejected_quantity = st.number_input(
                    "Rejected Quantity",
                    min_value=0.0,
                    step=1.0
                )

                status = st.selectbox(
                    "Status",
                    [
                        "Planned",
                        "In Progress",
                        "Completed",
                        "On Hold",
                        "Cancelled"
                    ]
                )

            submit_production = st.form_submit_button(
                "💾 Save Production",
                use_container_width=True
            )

            if submit_production:

                if not batch_number.strip():

                    st.error("Batch Number is required.")

                elif planned_quantity <= 0:

                    st.error("Planned Quantity must be greater than 0.")

                elif actual_quantity < 0:

                    st.error("Actual Quantity cannot be negative.")

                elif rejected_quantity > actual_quantity:

                    st.error(
                        "Rejected Quantity cannot be greater than Actual Quantity."
                    )

                else:

                    conn = get_connection()

                    try:

                        conn.execute(
                            """
                            INSERT INTO production
                            (
                                product_id,
                                batch_number,
                                production_date,
                                planned_quantity,
                                actual_quantity,
                                rejected_quantity,
                                status
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                product_options[selected_product],
                                batch_number.strip(),
                                production_date.isoformat(),
                                planned_quantity,
                                actual_quantity,
                                rejected_quantity,
                                status
                            )
                        )

                        conn.commit()

                        st.success(
                            "Production record added successfully."
                        )

                        st.rerun()

                    except sqlite3.IntegrityError:

                        st.error(
                            "Batch Number already exists."
                        )

                    finally:

                        conn.close()

    # -----------------------------------------------------
    # PRODUCTION RECORDS
    # -----------------------------------------------------

    st.divider()

    st.subheader("📋 Production Records")

    if production.empty:

        st.info("No production records available.")

    else:

        st.dataframe(
            production,
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# END PRODUCTION MANAGEMENT
# =========================================================
# =========================================================
# PRODUCTION - EDIT & DELETE
# =========================================================

elif menu == "Production Edit/Delete":

    st.header("✏️ Production Record Management")

    conn = get_connection()

    production = pd.read_sql_query(
        """
        SELECT
            p.id,
            pr.product_code,
            pr.name AS product_name,
            p.batch_number,
            p.production_date,
            p.planned_quantity,
            p.actual_quantity,
            p.rejected_quantity,
            p.status
        FROM production p
        JOIN products pr
            ON p.product_id = pr.id
        ORDER BY p.id DESC
        """,
        conn
    )

    products = pd.read_sql_query(
        """
        SELECT id, product_code, name
        FROM products
        ORDER BY name
        """,
        conn
    )

    conn.close()

    if production.empty:

        st.info("No production records available.")

    else:

        production_options = {
            f"{row.batch_number} | {row.product_code} - {row.product_name}": row.id
            for _, row in production.iterrows()
        }

        selected_production = st.selectbox(
            "Select Production Record",
            list(production_options.keys())
        )

        production_id = production_options[selected_production]

        selected_row = production[
            production["id"] == production_id
        ].iloc[0]

        st.subheader("✏️ Edit Production")

        product_options = {
            f"{row.product_code} - {row.name}": row.id
            for _, row in products.iterrows()
        }

        current_product = (
            f"{selected_row['product_code']} - "
            f"{selected_row['product_name']}"
        )

        selected_product = st.selectbox(
            "Product",
            list(product_options.keys()),
            index=list(product_options.keys()).index(current_product)
        )

        col1, col2 = st.columns(2)

        with col1:

            edit_batch = st.text_input(
                "Batch Number",
                value=str(selected_row["batch_number"])
            )

            edit_date = st.date_input(
                "Production Date",
                value=pd.to_datetime(
                    selected_row["production_date"]
                ).date()
            )

            edit_planned = st.number_input(
                "Planned Quantity",
                min_value=0.0,
                value=float(selected_row["planned_quantity"]),
                step=1.0
            )

        with col2:

            edit_actual = st.number_input(
                "Actual Quantity",
                min_value=0.0,
                value=float(selected_row["actual_quantity"]),
                step=1.0
            )

            edit_rejected = st.number_input(
                "Rejected Quantity",
                min_value=0.0,
                value=float(selected_row["rejected_quantity"]),
                step=1.0
            )

            status_list = [
                "Planned",
                "In Progress",
                "Completed",
                "On Hold",
                "Cancelled"
            ]

            current_status = str(selected_row["status"])

            edit_status = st.selectbox(
                "Status",
                status_list,
                index=(
                    status_list.index(current_status)
                    if current_status in status_list
                    else 0
                )
            )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "💾 Update Production",
                use_container_width=True
            ):

                if not edit_batch.strip():

                    st.error("Batch Number is required.")

                elif edit_planned <= 0:

                    st.error(
                        "Planned Quantity must be greater than 0."
                    )

                elif edit_rejected > edit_actual:

                    st.error(
                        "Rejected Quantity cannot be greater than Actual Quantity."
                    )

                else:

                    conn = get_connection()

                    try:

                        conn.execute(
                            """
                            UPDATE production
                            SET
                                product_id = ?,
                                batch_number = ?,
                                production_date = ?,
                                planned_quantity = ?,
                                actual_quantity = ?,
                                rejected_quantity = ?,
                                status = ?
                            WHERE id = ?
                            """,
                            (
                                product_options[selected_product],
                                edit_batch.strip(),
                                edit_date.isoformat(),
                                edit_planned,
                                edit_actual,
                                edit_rejected,
                                edit_status,
                                production_id
                            )
                        )

                        conn.commit()

                        st.success(
                            "Production record updated successfully."
                        )

                        st.rerun()

                    except sqlite3.IntegrityError:

                        st.error(
                            "Batch Number already exists."
                        )

                    finally:

                        conn.close()

        with col2:

            if st.button(
                "🗑️ Delete Production",
                type="secondary",
                use_container_width=True
            ):

                conn = get_connection()

                conn.execute(
                    """
                    DELETE FROM production
                    WHERE id = ?
                    """,
                    (production_id,)
                )

                conn.commit()
                conn.close()

                st.success(
                    "Production record deleted successfully."
                )

                st.rerun()

# =========================================================
# END PRODUCTION EDIT/DELETE
# =========================================================
# =========================================================
# QUALITY CONTROL MODULE
# =========================================================

elif menu == "Quality Control":

    st.header("🔬 Quality Control")

    conn = get_connection()

    # -----------------------------
    # ADD QUALITY CHECK
    # -----------------------------

    st.subheader("➕ Add Quality Check")

    col1, col2 = st.columns(2)

    with col1:
        batch_number = st.text_input("Batch Number")

        test_name = st.text_input("Test Name")

        test_value = st.text_input("Test Value")

    with col2:
        specification = st.text_input("Specification")

        result = st.selectbox(
            "Result",
            ["Pass", "Fail", "Pending"]
        )

        checked_at = st.date_input(
            "Checked Date"
        )

    if st.button(
        "💾 Save Quality Check",
        use_container_width=True
    ):

        if not batch_number.strip():
            st.error("Batch Number is required.")

        elif not test_name.strip():
            st.error("Test Name is required.")

        else:

            conn.execute(
                """
                INSERT INTO quality_checks
                (
                    batch_number,
                    test_name,
                    test_value,
                    specification,
                    result,
                    checked_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_number.strip(),
                    test_name.strip(),
                    test_value.strip(),
                    specification.strip(),
                    result,
                    checked_at.isoformat()
                )
            )

            conn.commit()
            conn.close()

            st.success(
                "Quality check saved successfully."
            )

            st.rerun()

    st.divider()

    # -----------------------------
    # QUALITY CHECK RECORDS
    # -----------------------------

    st.subheader("📋 Quality Check Records")

    conn = get_connection()

    quality_checks = pd.read_sql_query(
        """
        SELECT
            id,
            batch_number,
            test_name,
            test_value,
            specification,
            result,
            checked_at
        FROM quality_checks
        ORDER BY id DESC
        """,
        conn
    )

    conn.close()

    if quality_checks.empty:

        st.info("No quality check records available.")

    else:

        st.dataframe(
            quality_checks,
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# END QUALITY CONTROL MODULE
# =========================================================
# ============================================================
# PRODUCTION MANAGEMENT MODULE
# ============================================================

st.markdown("---")
st.header("🏭 Production Management")

# -----------------------------
# Production Records
# -----------------------------

st.subheader("📋 Production Records")

conn = sqlite3.connect("mrpl.db")

production_df = pd.read_sql_query(
    """
    SELECT *
    FROM production
    ORDER BY id DESC
    """,
    conn
)

conn.close()

if not production_df.empty:
    st.dataframe(
        production_df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No production records available.")


# -----------------------------
# Add Production
# -----------------------------

st.subheader("➕ Add Production")

with st.form("add_production_form"):

    col1, col2 = st.columns(2)

    with col1:
        product_id = st.number_input(
            "Product ID",
            min_value=1,
            step=1
        )

        quantity = st.number_input(
            "Production Quantity",
            min_value=1.0,
            step=1.0
        )

    with col2:
        production_date = st.date_input(
            "Production Date"
        )

        status = st.selectbox(
            "Status",
            [
                "Planned",
                "In Progress",
                "Completed",
                "Cancelled"
            ]
        )

    submitted = st.form_submit_button(
        "➕ Add Production",
        type="primary"
    )

    if submitted:

        conn = sqlite3.connect("mrpl.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO production
            (product_id, quantity, production_date, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                product_id,
                quantity,
                str(production_date),
                status
            )
        )

        conn.commit()
        conn.close()

        st.success("Production record added successfully.")
        st.rerun()


# -----------------------------
# Update Production Status
# -----------------------------

st.subheader("🔄 Update Production Status")

conn = sqlite3.connect("mrpl.db")

production_records = pd.read_sql_query(
    """
    SELECT id, product_id, quantity,
           production_date, status
    FROM production
    ORDER BY id DESC
    """,
    conn
)

conn.close()

if not production_records.empty:

    production_options = {
        f"Production #{row.id} | Product {row.product_id} | {row.status}":
        row.id
        for _, row in production_records.iterrows()
    }

    selected_production = st.selectbox(
        "Select Production Record",
        list(production_options.keys())
    )

    new_status = st.selectbox(
        "New Status",
        [
            "Planned",
            "In Progress",
            "Completed",
            "Cancelled"
        ]
    )

    if st.button(
        "🔄 Update Status",
        type="secondary"
    ):

        production_id = production_options[
            selected_production
        ]

        conn = sqlite3.connect("mrpl.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE production
            SET status = ?
            WHERE id = ?
            """,
            (
                new_status,
                production_id
            )
        )

        conn.commit()
        conn.close()

        st.success("Production status updated successfully.")
        st.rerun()

# ============================================================
# END OF PRODUCTION MANAGEMENT MODULE
# ============================================================
# ============================================================
# QUALITY CONTROL MODULE
# ============================================================

st.markdown("---")
st.header("🔬 Quality Control")

# -----------------------------
# Quality Records
# -----------------------------

st.subheader("📋 Quality Inspection Records")

conn = sqlite3.connect("mrpl.db")

quality_df = pd.read_sql_query(
    """
    SELECT *
    FROM quality_control
    ORDER BY id DESC
    """,
    conn
)

conn.close()

if not quality_df.empty:
    st.dataframe(
        quality_df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No quality inspection records available.")


# -----------------------------
# Add Quality Inspection
# -----------------------------

st.subheader("➕ Add Quality Inspection")

with st.form("quality_inspection_form"):

    col1, col2 = st.columns(2)

    with col1:
        production_id = st.number_input(
            "Production ID",
            min_value=1,
            step=1
        )

        inspection_date = st.date_input(
            "Inspection Date"
        )

    with col2:
        quantity_checked = st.number_input(
            "Quantity Checked",
            min_value=1.0,
            step=1.0
        )

        defects = st.number_input(
            "Defective Quantity",
            min_value=0.0,
            step=1.0
        )

    quality_status = st.selectbox(
        "Quality Status",
        [
            "Passed",
            "Failed",
            "Under Inspection"
        ]
    )

    remarks = st.text_area(
        "Remarks"
    )

    submitted = st.form_submit_button(
        "➕ Add Inspection",
        type="primary"
    )

    if submitted:

        conn = sqlite3.connect("mrpl.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO quality_control
            (
                production_id,
                inspection_date,
                quantity_checked,
                defects,
                quality_status,
                remarks
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                production_id,
                str(inspection_date),
                quantity_checked,
                defects,
                quality_status,
                remarks.strip()
            )
        )

        conn.commit()
        conn.close()

        st.success(
            "Quality inspection added successfully."
        )

        st.rerun()


# -----------------------------
# Quality Summary
# -----------------------------

st.subheader("📊 Quality Summary")

conn = sqlite3.connect("mrpl.db")

summary_df = pd.read_sql_query(
    """
    SELECT
        COUNT(*) AS total_inspections,
        COALESCE(SUM(quantity_checked), 0)
            AS total_checked,
        COALESCE(SUM(defects), 0)
            AS total_defects
    FROM quality_control
    """,
    conn
)

conn.close()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Inspections",
    int(summary_df.iloc[0]["total_inspections"])
)

col2.metric(
    "Quantity Checked",
    int(summary_df.iloc[0]["total_checked"])
)

col3.metric(
    "Total Defects",
    int(summary_df.iloc[0]["total_defects"])
)


# ============================================================
# END OF QUALITY CONTROL MODULE
# ============================================================
# ============================================================
# FINISHED GOODS / WAREHOUSE MANAGEMENT
# ============================================================

st.markdown("---")
st.header("📦 Finished Goods / Warehouse")

conn = sqlite3.connect("mrpl.db")

stock_df = pd.read_sql_query(
    """
    SELECT *
    FROM stock
    ORDER BY id DESC
    """,
    conn
)

conn.close()

# -----------------------------
# Stock Records
# -----------------------------

st.subheader("📋 Stock Records")

if not stock_df.empty:

    st.dataframe(
        stock_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No stock records available.")


# -----------------------------
# Add Stock
# -----------------------------

st.subheader("➕ Add Stock")

with st.form("add_stock_form"):

    col1, col2 = st.columns(2)

    with col1:

        item_type = st.selectbox(
            "Item Type",
            [
                "Raw Material",
                "Finished Goods"
            ]
        )

        item_id = st.number_input(
            "Item ID",
            min_value=1,
            step=1
        )

    with col2:

        quantity = st.number_input(
            "Quantity",
            min_value=0.0,
            step=1.0
        )

        unit = st.text_input(
            "Unit"
        )

    location = st.text_input(
        "Warehouse Location"
    )

    submitted = st.form_submit_button(
        "➕ Add Stock",
        type="primary"
    )

    if submitted:

        if quantity <= 0:

            st.error("Quantity must be greater than 0.")

        else:

            conn = sqlite3.connect("mrpl.db")

            conn.execute(
                """
                INSERT INTO stock
                (
                    item_type,
                    item_id,
                    quantity,
                    unit,
                    location
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    item_type,
                    item_id,
                    quantity,
                    unit.strip(),
                    location.strip()
                )
            )

            conn.commit()
            conn.close()

            st.success(
                "Stock added successfully."
            )

            st.rerun()


# -----------------------------
# Stock Summary
# -----------------------------

st.subheader("📊 Stock Summary")

conn = sqlite3.connect("mrpl.db")

stock_summary = pd.read_sql_query(
    """
    SELECT
        item_type,
        COUNT(*) AS total_items,
        COALESCE(SUM(quantity), 0) AS total_quantity
    FROM stock
    GROUP BY item_type
    """,
    conn
)

conn.close()

if not stock_summary.empty:

    st.dataframe(
        stock_summary,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# END OF WAREHOUSE MODULE
# ============================================================
# ============================================================
# ORDER MANAGEMENT
# ============================================================

st.markdown("---")
st.header("🧾 Order Management")

conn = sqlite3.connect("mrpl.db")

orders_df = pd.read_sql_query(
    """
    SELECT *
    FROM orders
    ORDER BY id DESC
    """,
    conn
)

conn.close()

st.subheader("📋 Orders")

if not orders_df.empty:
    st.dataframe(
        orders_df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No orders available.")


# ============================================================
# DISPATCH MANAGEMENT
# ============================================================

st.markdown("---")
st.header("🚚 Dispatch Management")

conn = sqlite3.connect("mrpl.db")

dispatch_df = pd.read_sql_query(
    """
    SELECT *
    FROM dispatch
    ORDER BY id DESC
    """,
    conn
)

conn.close()

st.subheader("📋 Dispatch Records")

if not dispatch_df.empty:
    st.dataframe(
        dispatch_df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No dispatch records available.")


# ============================================================
# ADD DISPATCH
# ============================================================

st.subheader("➕ Add Dispatch")

with st.form("add_dispatch_form"):

    col1, col2 = st.columns(2)

    with col1:
        order_id = st.number_input(
            "Order ID",
            min_value=1,
            step=1
        )

        dispatch_date = st.date_input(
            "Dispatch Date"
        )

        quantity = st.number_input(
            "Dispatch Quantity",
            min_value=0.0,
            step=1.0
        )

    with col2:
        vehicle_number = st.text_input(
            "Vehicle Number"
        )

        transporter = st.text_input(
            "Transporter"
        )

        dispatch_status = st.selectbox(
            "Status",
            [
                "Pending",
                "Dispatched",
                "Delivered",
                "Cancelled"
            ]
        )

    submitted = st.form_submit_button(
        "🚚 Add Dispatch",
        type="primary"
    )

    if submitted:

        if quantity <= 0:
            st.error("Dispatch quantity must be greater than 0.")

        else:

            conn = sqlite3.connect("mrpl.db")

            conn.execute(
                """
                INSERT INTO dispatch
                (
                    order_id,
                    dispatch_date,
                    quantity,
                    vehicle_number,
                    transporter,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    str(dispatch_date),
                    quantity,
                    vehicle_number.strip(),
                    transporter.strip(),
                    dispatch_status
                )
            )

            conn.commit()
            conn.close()

            st.success(
                "Dispatch record added successfully."
            )

            st.rerun()


# ============================================================
# END ORDER & DISPATCH
# ============================================================
# ============================================================
# MANAGEMENT DASHBOARD
# ============================================================

st.markdown("---")
st.header("📊 Management Dashboard")

conn = sqlite3.connect("mrpl.db")

# Total Production
production_count = pd.read_sql_query(
    "SELECT COUNT(*) AS total FROM production",
    conn
).iloc[0]["total"]

# Total Stock
stock_quantity = pd.read_sql_query(
    "SELECT COALESCE(SUM(quantity), 0) AS total FROM stock",
    conn
).iloc[0]["total"]

# Total Orders
order_count = pd.read_sql_query(
    "SELECT COUNT(*) AS total FROM orders",
    conn
).iloc[0]["total"]

# Total Dispatch
dispatch_count = pd.read_sql_query(
    "SELECT COUNT(*) AS total FROM dispatch",
    conn
).iloc[0]["total"]

conn.close()


# -----------------------------
# KPI CARDS
# -----------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🏭 Production Records",
    int(production_count)
)

col2.metric(
    "📦 Total Stock",
    f"{stock_quantity:,.2f}"
)

col3.metric(
    "🧾 Total Orders",
    int(order_count)
)

col4.metric(
    "🚚 Dispatch Records",
    int(dispatch_count)
)


# ============================================================
# PRODUCTION SUMMARY
# ============================================================

st.subheader("🏭 Production Status")

conn = sqlite3.connect("mrpl.db")

production_status = pd.read_sql_query(
    """
    SELECT
        status,
        COUNT(*) AS records
    FROM production
    GROUP BY status
    ORDER BY records DESC
    """,
    conn
)

conn.close()

if not production_status.empty:

    st.dataframe(
        production_status,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No production data available.")


# ============================================================
# STOCK SUMMARY
# ============================================================

st.subheader("📦 Stock by Item Type")

conn = sqlite3.connect("mrpl.db")

stock_status = pd.read_sql_query(
    """
    SELECT
        item_type,
        COALESCE(SUM(quantity), 0) AS quantity
    FROM stock
    GROUP BY item_type
    ORDER BY quantity DESC
    """,
    conn
)

conn.close()

if not stock_status.empty:

    st.dataframe(
        stock_status,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No stock data available.")


# ============================================================
# DISPATCH SUMMARY
# ============================================================

st.subheader("🚚 Dispatch Status")

conn = sqlite3.connect("mrpl.db")

dispatch_status = pd.read_sql_query(
    """
    SELECT
        status,
        COUNT(*) AS records
    FROM dispatch
    GROUP BY status
    ORDER BY records DESC
    """,
    conn
)

conn.close()

if not dispatch_status.empty:

    st.dataframe(
        dispatch_status,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No dispatch data available.")

# ============================================================
# END MANAGEMENT DASHBOARD
# ============================================================
# ============================================================
# EMPLOYEE & DEPARTMENT MANAGEMENT
# ============================================================

st.markdown("---")
st.header("👥 Employee Management")

conn = sqlite3.connect("mrpl.db")

departments_df = pd.read_sql_query(
    """
    SELECT id, name
    FROM departments
    ORDER BY name
    """,
    conn
)

employees_df = pd.read_sql_query(
    """
    SELECT
        e.id,
        e.employee_code,
        e.name,
        d.name AS department,
        e.designation,
        e.phone,
        e.email,
        e.joining_date,
        e.status
    FROM employees e
    LEFT JOIN departments d
        ON e.department_id = d.id
    ORDER BY e.id DESC
    """,
    conn
)

conn.close()


# ------------------------------------------------------------
# ADD EMPLOYEE
# ------------------------------------------------------------

st.subheader("➕ Add Employee")

if departments_df.empty:

    st.warning("No departments available.")

else:

    department_options = {
        row["name"]: row["id"]
        for _, row in departments_df.iterrows()
    }

    with st.form("add_employee_form"):

        col1, col2 = st.columns(2)

        with col1:

            employee_code = st.text_input(
                "Employee Code"
            )

            employee_name = st.text_input(
                "Employee Name"
            )

            designation = st.text_input(
                "Designation"
            )

            department = st.selectbox(
                "Department",
                list(department_options.keys())
            )

        with col2:

            phone = st.text_input(
                "Phone"
            )

            email = st.text_input(
                "Email"
            )

            joining_date = st.date_input(
                "Joining Date"
            )

            status = st.selectbox(
                "Status",
                [
                    "Active",
                    "Inactive"
                ]
            )

        submitted = st.form_submit_button(
            "➕ Add Employee",
            type="primary",
            use_container_width=True
        )

        if submitted:

            if not employee_code.strip():

                st.error("Employee Code is required.")

            elif not employee_name.strip():

                st.error("Employee Name is required.")

            elif not designation.strip():

                st.error("Designation is required.")

            else:

                conn = sqlite3.connect("mrpl.db")

                try:

                    conn.execute(
                        """
                        INSERT INTO employees
                        (
                            employee_code,
                            name,
                            department_id,
                            designation,
                            phone,
                            email,
                            joining_date,
                            status
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            employee_code.strip(),
                            employee_name.strip(),
                            department_options[department],
                            designation.strip(),
                            phone.strip(),
                            email.strip(),
                            joining_date.isoformat(),
                            status
                        )
                    )

                    conn.commit()

                    st.success(
                        "Employee added successfully."
                    )

                    st.rerun()

                except sqlite3.IntegrityError:

                    st.error(
                        "Employee Code already exists."
                    )

                finally:

                    conn.close()


# ------------------------------------------------------------
# EMPLOYEE LIST
# ------------------------------------------------------------

st.divider()

st.subheader("📋 Employee List")

if employees_df.empty:

    st.info("No employees available.")

else:

    st.dataframe(
        employees_df,
        use_container_width=True,
        hide_index=True
    )


# ------------------------------------------------------------
# DEPARTMENT LIST
# ------------------------------------------------------------

st.divider()

st.subheader("🏢 Departments")

if departments_df.empty:

    st.info("No departments available.")

else:

    st.dataframe(
        departments_df,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# END EMPLOYEE & DEPARTMENT MANAGEMENT
# ============================================================
# ============================================================
# USER & ROLE MANAGEMENT
# ============================================================

st.markdown("---")
st.header("🔐 User & Role Management")

conn = sqlite3.connect("mrpl.db")

users_df = pd.read_sql_query(
    """
    SELECT
        id,
        username,
        role,
        status,
        created_at
    FROM users
    ORDER BY id DESC
    """,
    conn
)

conn.close()


# ------------------------------------------------------------
# USER LIST
# ------------------------------------------------------------

st.subheader("👤 System Users")

if users_df.empty:

    st.info("No users available.")

else:

    st.dataframe(
        users_df,
        use_container_width=True,
        hide_index=True
    )


# ------------------------------------------------------------
# ADD USER
# ------------------------------------------------------------

st.subheader("➕ Add User")

with st.form("add_user_form"):

    col1, col2 = st.columns(2)

    with col1:

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

    with col2:

        role = st.selectbox(
            "Role",
            [
                "Admin",
                "Manager",
                "Production",
                "Quality",
                "Warehouse",
                "Sales",
                "Dispatch",
                "HR"
            ]
        )

        user_status = st.selectbox(
            "Status",
            [
                "Active",
                "Inactive"
            ]
        )

    submitted = st.form_submit_button(
        "➕ Create User",
        type="primary",
        use_container_width=True
    )

    if submitted:

        if not username.strip():

            st.error("Username is required.")

        elif not password:

            st.error("Password is required.")

        else:

            conn = sqlite3.connect("mrpl.db")

            try:

                conn.execute(
                    """
                    INSERT INTO users
                    (
                        username,
                        password,
                        role,
                        status
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        username.strip(),
                        password,
                        role,
                        user_status
                    )
                )

                conn.commit()

                st.success(
                    "User created successfully."
                )

                st.rerun()

            except sqlite3.IntegrityError:

                st.error(
                    "Username already exists."
                )

            finally:

                conn.close()


# ============================================================
# END USER & ROLE MANAGEMENT
# ============================================================
# ============================================================
# LOGIN + ROLE BASED ACCESS
# ============================================================

import hashlib


def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def authenticate_user(username, password):

    conn = sqlite3.connect("mrpl.db")

    user = conn.execute(
        """
        SELECT id, username, password, role, status
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    conn.close()

    if user is None:
        return None

    stored_password = user[2]

    # Supports hashed passwords
    if stored_password == hash_password(password):

        if user[4] == "Active":
            return user

    # Supports existing plain-password records
    if stored_password == password:

        if user[4] == "Active":
            return user

    return None


# ------------------------------------------------------------
# SESSION
# ------------------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# ------------------------------------------------------------
# LOGIN SCREEN
# ------------------------------------------------------------

if not st.session_state.logged_in:

    st.title("🏭 MRPL Smart Management System")

    st.subheader("🔐 Login")

    with st.form("login_form"):

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        login = st.form_submit_button(
            "🔑 Login",
            type="primary",
            use_container_width=True
        )

        if login:

            user = authenticate_user(
                username.strip(),
                password
            )

            if user:

                st.session_state.logged_in = True

                st.session_state.user = user

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    st.stop()


# ------------------------------------------------------------
# LOGGED-IN USER
# ------------------------------------------------------------

current_user = st.session_state.user

st.sidebar.success(
    f"Logged in as: {current_user[1]}"
)

st.sidebar.info(
    f"Role: {current_user[3]}"
)


# ------------------------------------------------------------
# LOGOUT
# ------------------------------------------------------------

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.logged_in = False
    st.session_state.user = None

    st.rerun()


# ============================================================
# ROLE BASED MENU
# ============================================================

role = current_user[3]

if role == "Admin":

    allowed_modules = [
        "Dashboard",
        "Raw Materials",
        "Production",
        "Quality Control",
        "Warehouse",
        "Orders",
        "Dispatch",
        "Employees",
        "Users"
    ]

elif role == "Manager":

    allowed_modules = [
        "Dashboard",
        "Raw Materials",
        "Production",
        "Quality Control",
        "Warehouse",
        "Orders",
        "Dispatch"
    ]

elif role == "Production":

    allowed_modules = [
        "Production"
    ]

elif role == "Quality":

    allowed_modules = [
        "Quality Control"
    ]

elif role == "Warehouse":

    allowed_modules = [
        "Raw Materials",
        "Warehouse",
        "Dispatch"
    ]

elif role == "Sales":

    allowed_modules = [
        "Orders"
    ]

elif role == "Dispatch":

    allowed_modules = [
        "Dispatch"
    ]

elif role == "HR":

    allowed_modules = [
        "Employees"
    ]

else:

    allowed_modules = []


# ------------------------------------------------------------
# APPLICATION NAVIGATION
# ------------------------------------------------------------

menu = st.sidebar.radio(
    "📋 Select Module",
    allowed_modules
)

# ============================================================
# END LOGIN & ROLE ACCESS
# ============================================================


# ============================================================
# MRPL SMART MANUFACTURING & QUALITY MANAGEMENT SYSTEM
# STEP 1A - LOGIN SYSTEM FOUNDATION
# ============================================================

import streamlit as st
import sqlite3
import hashlib
from pathlib import Path


# ============================================================
# APP CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MRPL Smart Manufacturing System",
    page_icon="🏭",
    layout="wide"
)


# ============================================================
# DATABASE
# ============================================================

DB_PATH = "mrpl.db"


def get_connection():
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# USER AUTHENTICATION
# ============================================================
def authenticate_user(username, password):

    conn = get_connection()

    user = conn.execute(
        """
        SELECT
            id,
            username,
            password_hash,
            role,
            employee_id,
            is_active
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    conn.close()

    if user is None:
        return None

    stored_password = user[2]

    if stored_password == hash_password(password):

        if user[5] == 1:
            return user

    return None

# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# ============================================================
# LOGIN SCREEN
# ============================================================

if not st.session_state.logged_in:

    st.title("🏭 MRPL Smart Manufacturing System")

    st.subheader("🔐 Login")

    with st.form("login_form"):

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        login_button = st.form_submit_button(
            "🔑 Login",
            type="primary",
            use_container_width=True
        )

        if login_button:

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


# ============================================================
# LOGGED-IN USER
# ============================================================

current_user = st.session_state.user

st.sidebar.success(
    f"👤 {current_user[1]}"
)

st.sidebar.info(
    f"Role: {current_user[3]}"
)


# ============================================================
# LOGOUT
# ============================================================

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.logged_in = False
    st.session_state.user = None

    st.rerun()


# ============================================================
# STEP 1A END
# ============================================================
# ============================================================
# STEP 1B - ROLE BASED ACCESS CONTROL
# ============================================================

ROLE_MODULES = {

    "Admin": [
        "Dashboard",
        "Raw Materials",
        "Production",
        "Quality Control",
        "Finished Goods",
        "Orders",
        "Dispatch",
        "Employees",
        "Attendance",
        "Leave & Tasks",
        "Users"
    ],

    "Manager": [
        "Dashboard",
        "Raw Materials",
        "Production",
        "Quality Control",
        "Finished Goods",
        "Orders",
        "Dispatch",
        "Employees",
        "Attendance",
        "Leave & Tasks"
    ],

    "Production": [
        "Dashboard",
        "Production"
    ],

    "Quality": [
        "Dashboard",
        "Quality Control"
    ],

    "Warehouse": [
        "Dashboard",
        "Raw Materials",
        "Finished Goods"
    ],

    "Sales": [
        "Dashboard",
        "Orders"
    ],

    "Dispatch": [
        "Dashboard",
        "Orders",
        "Dispatch"
    ],

    "HR": [
        "Dashboard",
        "Employees",
        "Attendance",
        "Leave & Tasks"
    ]
}


# ============================================================
# CURRENT USER ROLE
# ============================================================

user_role = current_user[3]

allowed_modules = ROLE_MODULES.get(
    user_role,
    []
)


# ============================================================
# APPLICATION NAVIGATION
# ============================================================

st.sidebar.divider()

st.sidebar.subheader("📋 Navigation")

if allowed_modules:

    selected_module = st.sidebar.radio(
        "Select Module",
        allowed_modules
    )

else:

    selected_module = None

    st.sidebar.warning(
        "No modules assigned to this role."
    )


# ============================================================
# ROLE INFORMATION
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    f"Current Role: {user_role}"
)

# ============================================================
# STEP 1B END
# ============================================================
# ============================================================
# STEP 1C - PERMISSION CONTROL
# ============================================================

def has_permission(module_name):
    """
    Check whether the currently logged-in user's
    role has access to the requested module.
    """

    return module_name in allowed_modules


def require_permission(module_name):
    """
    Stop access when the current user's role
    does not have permission for the module.
    """

    if not has_permission(module_name):

        st.error(
            "🚫 You do not have permission to access this module."
        )

        st.stop()


# ============================================================
# ACTIVE MODULE
# ============================================================

if selected_module:

    require_permission(selected_module)

    st.sidebar.success(
        f"Active Module: {selected_module}"
    )


# ============================================================
# STEP 1C END
# ============================================================
# ============================================================
# STEP 1D - DATABASE INITIALIZATION & SAFE ACCESS
# ============================================================

def database_exists():
    """
    Check whether the MRPL database file exists.
    """
    return Path(DB_PATH).exists()


def get_table_names():
    """
    Return all tables available in the MRPL database.
    """

    conn = get_connection()

    tables = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """
    ).fetchall()

    conn.close()

    return [table[0] for table in tables]


def table_exists(table_name):
    """
    Check whether a particular table exists.
    """

    conn = get_connection()

    result = conn.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
        AND name = ?
        LIMIT 1
        """,
        (table_name,)
    ).fetchone()

    conn.close()

    return result is not None


def get_table_columns(table_name):
    """
    Return column names of an existing table.
    """

    if not table_exists(table_name):
        return []

    conn = get_connection()

    columns = conn.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    conn.close()

    return [column[1] for column in columns]


# ============================================================
# DATABASE VALIDATION
# ============================================================

if not database_exists():

    st.error(
        "MRPL database file (mrpl.db) was not found."
    )

    st.stop()


# ============================================================
# STEP 1D END
# ============================================================
# ============================================================
# STEP 1E - MODULE ROUTING
# ============================================================

if selected_module == "Dashboard":

    st.header("📊 Management Dashboard")

elif selected_module == "Raw Materials":

    st.header("🧱 Raw Material Management")

    st.info(
        "Raw Material module will be developed here."
    )


elif selected_module == "Production":

    st.header("🏭 Production Management")

    st.info(
        "Production module will be developed here."
    )


elif selected_module == "Quality Control":

    st.header("🔬 Quality Control")

    st.info(
        "Quality Control module will be developed here."
    )


elif selected_module == "Finished Goods":

    st.header("📦 Finished Goods / Warehouse")

    st.info(
        "Finished Goods module will be developed here."
    )


elif selected_module == "Orders":

    st.header("🧾 Order Management")

    st.info(
        "Order Management module will be developed here."
    )


elif selected_module == "Dispatch":

    st.header("🚚 Dispatch Management")

    st.info(
        "Dispatch module will be developed here."
    )


elif selected_module == "Employees":

    st.header("👥 Employee Management")

    st.info(
        "Employee Management module will be developed here."
    )


elif selected_module == "Attendance":

    st.header("🕐 Attendance Management")

    st.info(
        "Attendance module will be developed here."
    )


elif selected_module == "Leave & Tasks":

    st.header("📅 Leave & Task Management")

    st.info(
        "Leave & Task module will be developed here."
    )


elif selected_module == "Users":

    st.header("🔐 User Management")

    st.info(
        "User Management module will be developed here."
    )


# ============================================================
# STEP 1E END
# ============================================================
# ============================================================
# STEP 2A - DATABASE CORE HELPERS
# ============================================================

def execute_query(query, parameters=()):
    """
    Execute INSERT, UPDATE or DELETE query.
    """
    conn = get_connection()

    try:
        cursor = conn.execute(
            query,
            parameters
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def fetch_one(query, parameters=()):
    """
    Fetch a single database record.
    """
    conn = get_connection()

    try:
        return conn.execute(
            query,
            parameters
        ).fetchone()

    finally:
        conn.close()


def fetch_all(query, parameters=()):
    """
    Fetch multiple database records.
    """
    conn = get_connection()

    try:
        return conn.execute(
            query,
            parameters
        ).fetchall()

    finally:
        conn.close()


def fetch_dataframe(query, parameters=()):
    """
    Fetch database results as a Pandas DataFrame.
    """

    import pandas as pd

    conn = get_connection()

    try:
        return pd.read_sql_query(
            query,
            conn,
            params=parameters
        )

    finally:
        conn.close()


# ============================================================
# STEP 2A END
# ============================================================
# ============================================================
# STEP 2B - DATABASE TABLE ACCESS
# ============================================================

def get_table_data(table_name):
    """
    Read all records from an existing MRPL database table.
    """

    if not table_exists(table_name):
        return pd.DataFrame()

    return fetch_dataframe(
        f"SELECT * FROM {table_name}"
    )


def get_table_count(table_name):
    """
    Return total number of records in a table.
    """

    if not table_exists(table_name):
        return 0

    result = fetch_one(
        f"SELECT COUNT(*) FROM {table_name}"
    )

    return result[0] if result else 0


def get_existing_tables():
    """
    Return all tables available in the MRPL database.
    """

    return get_table_names()


# ============================================================
# STEP 2B END
# ============================================================
# ============================================================
# STEP 2C - FINISHED GOODS / WAREHOUSE
# ============================================================

def add_finished_good(
    product_id,
    quantity,
    warehouse_location
):
    """
    Add finished goods to warehouse stock.
    """

    if quantity <= 0:
        return False, "Quantity must be greater than 0."

    if not table_exists("stock"):
        return False, "Stock table not found."

    try:

        execute_query(
            """
            INSERT INTO stock
            (
                item_type,
                item_id,
                quantity,
                location
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                "Finished Goods",
                product_id,
                quantity,
                warehouse_location
            )
        )

        return True, "Finished goods added successfully."

    except sqlite3.IntegrityError as e:

        return False, str(e)


def get_finished_goods():
    """
    Get finished goods inventory.
    """

    if not table_exists("stock"):
        return pd.DataFrame()

    return fetch_dataframe(
        """
        SELECT *
        FROM stock
        WHERE item_type = ?
        ORDER BY id DESC
        """,
        ("Finished Goods",)
    )


def get_finished_goods_summary():
    """
    Get total finished goods quantity by product.
    """

    if not table_exists("stock"):
        return pd.DataFrame()

    return fetch_dataframe(
        """
        SELECT
            item_id,
            SUM(quantity) AS total_quantity
        FROM stock
        WHERE item_type = ?
        GROUP BY item_id
        ORDER BY total_quantity DESC
        """,
        ("Finished Goods",)
    )


# ============================================================
# FINISHED GOODS MODULE
# ============================================================

if selected_module == "Finished Goods":

    st.header("📦 Finished Goods / Warehouse")

    # --------------------------------------------------------
    # ADD FINISHED GOODS
    # --------------------------------------------------------

    st.subheader("➕ Add Finished Goods")

    with st.form("finished_goods_form"):

        product_id = st.number_input(
            "Product ID",
            min_value=1,
            step=1
        )

        quantity = st.number_input(
            "Quantity",
            min_value=0.0,
            step=1.0
        )

        warehouse_location = st.text_input(
            "Warehouse Location"
        )

        submitted = st.form_submit_button(
            "Add Finished Goods",
            type="primary"
        )

        if submitted:

            success, message = add_finished_good(
                product_id,
                quantity,
                warehouse_location.strip()
            )

            if success:

                st.success(message)
                st.rerun()

            else:

                st.error(message)

    # --------------------------------------------------------
    # INVENTORY VIEW
    # --------------------------------------------------------

    st.divider()

    st.subheader("📋 Finished Goods Inventory")

    finished_goods = get_finished_goods()

    if finished_goods.empty:

        st.info(
            "No finished goods inventory available."
        )

    else:

        st.dataframe(
            finished_goods,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # INVENTORY SUMMARY
    # --------------------------------------------------------

    st.subheader("📊 Inventory Summary")

    summary = get_finished_goods_summary()

    if summary.empty:

        st.info(
            "No finished goods summary available."
        )

    else:

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# STEP 2C END
# ============================================================
# ============================================================
# STEP 2D - WAREHOUSE STOCK UPDATE / HANDLING
# ============================================================

def update_finished_goods_stock(stock_id, new_quantity):
    """
    Update the quantity of an existing finished-goods
    warehouse record.
    """

    if new_quantity < 0:
        return False, "Quantity cannot be negative."

    if not table_exists("stock"):
        return False, "Stock table not found."

    try:

        execute_query(
            """
            UPDATE stock
            SET quantity = ?
            WHERE id = ?
              AND item_type = ?
            """,
            (
                new_quantity,
                stock_id,
                "Finished Goods"
            )
        )

        return True, "Stock updated successfully."

    except sqlite3.Error as e:

        return False, str(e)


def delete_finished_goods_stock(stock_id):
    """
    Remove an existing finished-goods stock record.
    """

    if not table_exists("stock"):
        return False, "Stock table not found."

    try:

        execute_query(
            """
            DELETE FROM stock
            WHERE id = ?
              AND item_type = ?
            """,
            (
                stock_id,
                "Finished Goods"
            )
        )

        return True, "Stock record removed successfully."

    except sqlite3.Error as e:

        return False, str(e)


# ============================================================
# STOCK UPDATE UI
# ============================================================

if selected_module == "Finished Goods":

    st.divider()

    st.subheader("🔄 Update Warehouse Stock")

    finished_goods = get_finished_goods()

    if finished_goods.empty:

        st.info("No finished goods records available.")

    else:

        stock_options = {
            f"Stock ID {row['id']}": row["id"]
            for _, row in finished_goods.iterrows()
        }

        selected_stock = st.selectbox(
            "Select Stock Record",
            list(stock_options.keys())
        )

        selected_stock_id = stock_options[selected_stock]

        current_quantity = float(
            finished_goods.loc[
                finished_goods["id"] == selected_stock_id,
                "quantity"
            ].iloc[0]
        )

        st.write(
            f"Current Quantity: **{current_quantity}**"
        )

        new_quantity = st.number_input(
            "New Quantity",
            min_value=0.0,
            value=current_quantity,
            step=1.0
        )

        if st.button(
            "💾 Update Stock",
            type="primary"
        ):

            success, message = update_finished_goods_stock(
                selected_stock_id,
                new_quantity
            )

            if success:

                st.success(message)
                st.rerun()

            else:

                st.error(message)


# ============================================================
# STEP 2D END
# ============================================================
# ============================================================
# STEP 2E - ORDER MANAGEMENT
# ============================================================

def add_order(
    customer_name,
    product_id,
    quantity,
    order_date,
    delivery_date
):
    """
    Add a new customer order.
    """

    if not customer_name.strip():
        return False, "Customer name is required."

    if quantity <= 0:
        return False, "Quantity must be greater than 0."

    if not table_exists("orders"):
        return False, "Orders table not found."

    try:

        execute_query(
            """
            INSERT INTO orders
            (
                customer_name,
                product_id,
                quantity,
                order_date,
                delivery_date,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                customer_name.strip(),
                product_id,
                quantity,
                order_date,
                delivery_date,
                "Pending"
            )
        )

        return True, "Order added successfully."

    except sqlite3.Error as e:

        return False, str(e)


def get_orders():
    """
    Get all customer orders.
    """

    if not table_exists("orders"):
        return pd.DataFrame()

    return fetch_dataframe(
        """
        SELECT *
        FROM orders
        ORDER BY id DESC
        """
    )


def update_order_status(order_id, status):
    """
    Update the status of an order.
    """

    valid_statuses = [
        "Pending",
        "Confirmed",
        "Processing",
        "Completed",
        "Cancelled"
    ]

    if status not in valid_statuses:
        return False, "Invalid order status."

    try:

        execute_query(
            """
            UPDATE orders
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                order_id
            )
        )

        return True, "Order status updated successfully."

    except sqlite3.Error as e:

        return False, str(e)


# ============================================================
# ORDER MANAGEMENT UI
# ============================================================

if selected_module == "Orders":

    st.header("🧾 Order Management")

    # --------------------------------------------------------
    # ADD ORDER
    # --------------------------------------------------------

    st.subheader("➕ Add Order")

    with st.form("add_order_form"):

        col1, col2 = st.columns(2)

        with col1:

            customer_name = st.text_input(
                "Customer Name"
            )

            product_id = st.number_input(
                "Product ID",
                min_value=1,
                step=1
            )

            quantity = st.number_input(
                "Order Quantity",
                min_value=0.0,
                step=1.0
            )

        with col2:

            order_date = st.date_input(
                "Order Date"
            )

            delivery_date = st.date_input(
                "Expected Delivery Date"
            )

        submitted = st.form_submit_button(
            "➕ Add Order",
            type="primary"
        )

        if submitted:

            if delivery_date < order_date:

                st.error(
                    "Delivery date cannot be before order date."
                )

            else:

                success, message = add_order(
                    customer_name,
                    product_id,
                    quantity,
                    order_date.isoformat(),
                    delivery_date.isoformat()
                )

                if success:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)

    # --------------------------------------------------------
    # ORDER LIST
    # --------------------------------------------------------

    st.divider()

    st.subheader("📋 Orders")

    orders = get_orders()

    if orders.empty:

        st.info("No orders available.")

    else:

        st.dataframe(
            orders,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # UPDATE ORDER STATUS
    # --------------------------------------------------------

    if not orders.empty:

        st.divider()

        st.subheader("🔄 Update Order Status")

        order_ids = orders["id"].tolist()

        selected_order_id = st.selectbox(
            "Select Order",
            order_ids
        )

        new_status = st.selectbox(
            "New Status",
            [
                "Pending",
                "Confirmed",
                "Processing",
                "Completed",
                "Cancelled"
            ]
        )

        if st.button(
            "💾 Update Status",
            type="primary"
        ):

            success, message = update_order_status(
                selected_order_id,
                new_status
            )

            if success:

                st.success(message)
                st.rerun()

            else:

                st.error(message)


# ============================================================
# STEP 2E END
# ============================================================
# ============================================================
# STEP 2F - ORDER & DISPATCH MANAGEMENT
# ============================================================

def add_dispatch(
    order_id,
    quantity,
    dispatch_date,
    vehicle_number,
    transporter
):
    """
    Create a dispatch record for an order.
    """

    if quantity <= 0:
        return False, "Dispatch quantity must be greater than 0."

    if not table_exists("dispatch"):
        return False, "Dispatch table not found."

    try:

        execute_query(
            """
            INSERT INTO dispatch
            (
                order_id,
                quantity,
                dispatch_date,
                vehicle_number,
                transporter,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                order_id,
                quantity,
                dispatch_date,
                vehicle_number.strip(),
                transporter.strip(),
                "Pending"
            )
        )

        return True, "Dispatch created successfully."

    except sqlite3.Error as e:

        return False, str(e)


def get_dispatch_records():
    """
    Get all dispatch records.
    """

    if not table_exists("dispatch"):
        return pd.DataFrame()

    return fetch_dataframe(
        """
        SELECT *
        FROM dispatch
        ORDER BY id DESC
        """
    )


def update_dispatch_status(dispatch_id, status):
    """
    Update dispatch status.
    """

    valid_statuses = [
        "Pending",
        "Dispatched",
        "Delivered",
        "Cancelled"
    ]

    if status not in valid_statuses:
        return False, "Invalid dispatch status."

    try:

        execute_query(
            """
            UPDATE dispatch
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                dispatch_id
            )
        )

        return True, "Dispatch status updated successfully."

    except sqlite3.Error as e:

        return False, str(e)


# ============================================================
# DISPATCH MANAGEMENT UI
# ============================================================

if selected_module == "Dispatch":

    st.header("🚚 Order & Dispatch")

    # --------------------------------------------------------
    # AVAILABLE ORDERS
    # --------------------------------------------------------

    orders = get_orders()

    if orders.empty:

        st.info("No orders available for dispatch.")

    else:

        st.subheader("➕ Create Dispatch")

        with st.form("dispatch_form"):

            order_ids = orders["id"].tolist()

            order_id = st.selectbox(
                "Order",
                order_ids
            )

            quantity = st.number_input(
                "Dispatch Quantity",
                min_value=0.0,
                step=1.0
            )

            dispatch_date = st.date_input(
                "Dispatch Date"
            )

            vehicle_number = st.text_input(
                "Vehicle Number"
            )

            transporter = st.text_input(
                "Transporter"
            )

            submitted = st.form_submit_button(
                "🚚 Create Dispatch",
                type="primary"
            )

            if submitted:

                success, message = add_dispatch(
                    order_id,
                    quantity,
                    dispatch_date.isoformat(),
                    vehicle_number,
                    transporter
                )

                if success:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)

    # --------------------------------------------------------
    # DISPATCH RECORDS
    # --------------------------------------------------------

    st.divider()

    st.subheader("📋 Dispatch Records")

    dispatch_records = get_dispatch_records()

    if dispatch_records.empty:

        st.info("No dispatch records available.")

    else:

        st.dataframe(
            dispatch_records,
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # UPDATE DISPATCH STATUS
        # ----------------------------------------------------

        st.subheader("🔄 Update Dispatch Status")

        dispatch_id = st.selectbox(
            "Select Dispatch",
            dispatch_records["id"].tolist()
        )

        new_status = st.selectbox(
            "New Status",
            [
                "Pending",
                "Dispatched",
                "Delivered",
                "Cancelled"
            ]
        )

        if st.button(
            "💾 Update Dispatch",
            type="primary"
        ):

            success, message = update_dispatch_status(
                dispatch_id,
                new_status
            )

            if success:

                st.success(message)
                st.rerun()

            else:

                st.error(message)


# ============================================================
# STEP 2F END
# ============================================================
# ============================================================
# STEP 2G - EMPLOYEE MANAGEMENT
# ============================================================

def get_employees():

    if not table_exists("employees"):
        return pd.DataFrame()

    return fetch_dataframe(
        """
        SELECT *
        FROM employees
        ORDER BY id DESC
        """
    )


def add_employee(
    employee_code,
    name,
    department_id,
    designation,
    phone,
    email,
    joining_date
):

    if not employee_code.strip():
        return False, "Employee code is required."

    if not name.strip():
        return False, "Employee name is required."

    try:

        execute_query(
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
                name.strip(),
                department_id,
                designation.strip(),
                phone.strip(),
                email.strip(),
                joining_date,
                "Active"
            )
        )

        return True, "Employee added successfully."

    except sqlite3.IntegrityError:

        return False, "Employee code already exists."


# ============================================================
# EMPLOYEE UI
# ============================================================

if selected_module == "Employees":

    st.header("👥 Employee Management")

    conn = get_connection()

    departments = pd.read_sql_query(
        """
        SELECT id, name
        FROM departments
        ORDER BY name
        """,
        conn
    )

    conn.close()

    if departments.empty:

        st.warning("No departments available.")

    else:

        department_map = dict(
            zip(
                departments["name"],
                departments["id"]
            )
        )

        with st.form("employee_form"):

            col1, col2 = st.columns(2)

            with col1:

                employee_code = st.text_input(
                    "Employee Code"
                )

                name = st.text_input(
                    "Employee Name"
                )

                designation = st.text_input(
                    "Designation"
                )

                department_name = st.selectbox(
                    "Department",
                    list(department_map.keys())
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

            submitted = st.form_submit_button(
                "➕ Add Employee",
                type="primary"
            )

            if submitted:

                success, message = add_employee(
                    employee_code,
                    name,
                    department_map[department_name],
                    designation,
                    phone,
                    email,
                    joining_date.isoformat()
                )

                if success:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)

    st.divider()

    st.subheader("📋 Employees")

    employees = get_employees()

    if employees.empty:

        st.info("No employees available.")

    else:

        st.dataframe(
            employees,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# STEP 2G END
# ============================================================
# ============================================================
# STEP 2H - ATTENDANCE MANAGEMENT
# ============================================================

def get_attendance():

    if not table_exists("attendance"):
        return pd.DataFrame()

    return fetch_dataframe(
        """
        SELECT *
        FROM attendance
        ORDER BY id DESC
        """
    )


def mark_attendance(
    employee_id,
    attendance_date,
    status,
    check_in=None,
    check_out=None
):

    if not table_exists("attendance"):
        return False, "Attendance table not found."

    if status not in [
        "Present",
        "Absent",
        "Leave"
    ]:
        return False, "Invalid attendance status."

    try:

        execute_query(
            """
            INSERT INTO attendance
            (
                employee_id,
                date,
                status,
                check_in,
                check_out
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                employee_id,
                attendance_date,
                status,
                check_in,
                check_out
            )
        )

        return True, "Attendance marked successfully."

    except sqlite3.IntegrityError:

        return False, "Attendance already exists for this record."


# ============================================================
# ATTENDANCE UI
# ============================================================

if selected_module == "Attendance":

    st.header("🕐 Attendance Management")

    employees = get_employees()

    if employees.empty:

        st.warning(
            "No employees available. Add employees first."
        )

    else:

        employee_options = {
            f"{row['employee_code']} - {row['name']}":
            row["id"]
            for _, row in employees.iterrows()
        }

        st.subheader("➕ Mark Attendance")

        with st.form("attendance_form"):

            employee_name = st.selectbox(
                "Employee",
                list(employee_options.keys())
            )

            attendance_date = st.date_input(
                "Attendance Date"
            )

            status = st.selectbox(
                "Status",
                [
                    "Present",
                    "Absent",
                    "Leave"
                ]
            )

            col1, col2 = st.columns(2)

            with col1:

                check_in = st.text_input(
                    "Check In",
                    placeholder="09:00"
                )

            with col2:

                check_out = st.text_input(
                    "Check Out",
                    placeholder="18:00"
                )

            submitted = st.form_submit_button(
                "✅ Mark Attendance",
                type="primary"
            )

            if submitted:

                success, message = mark_attendance(
                    employee_options[employee_name],
                    attendance_date.isoformat(),
                    status,
                    check_in.strip() or None,
                    check_out.strip() or None
                )

                if success:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)

    # --------------------------------------------------------
    # ATTENDANCE RECORDS
    # --------------------------------------------------------

    st.divider()

    st.subheader("📋 Attendance Records")

    attendance = get_attendance()

    if attendance.empty:

        st.info(
            "No attendance records available."
        )

    else:

        st.dataframe(
            attendance,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# STEP 2H END
# ============================================================
# ============================================================
# STEP 2I - LEAVE & TASK MANAGEMENT
# ============================================================

def get_leave_requests():

    if not table_exists("leave_requests"):
        return pd.DataFrame()

    return fetch_dataframe(
        """
        SELECT *
        FROM leave_requests
        ORDER BY id DESC
        """
    )


def add_leave_request(
    employee_id,
    leave_type,
    start_date,
    end_date,
    reason
):

    if start_date > end_date:
        return False, "End date cannot be before start date."

    if not leave_type.strip():
        return False, "Leave type is required."

    try:

        execute_query(
            """
            INSERT INTO leave_requests
            (
                employee_id,
                leave_type,
                start_date,
                end_date,
                reason,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                employee_id,
                leave_type.strip(),
                start_date,
                end_date,
                reason.strip(),
                "Pending"
            )
        )

        return True, "Leave request submitted successfully."

    except sqlite3.Error as e:

        return False, str(e)


def update_leave_status(leave_id, status):

    valid_statuses = [
        "Pending",
        "Approved",
        "Rejected"
    ]

    if status not in valid_statuses:
        return False, "Invalid leave status."

    try:

        execute_query(
            """
            UPDATE leave_requests
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                leave_id
            )
        )

        return True, "Leave status updated successfully."

    except sqlite3.Error as e:

        return False, str(e)


# ============================================================
# LEAVE MANAGEMENT UI
# ============================================================

if selected_module == "Leave & Tasks":

    st.header("📅 Leave & Task Management")

    employees = get_employees()

    if employees.empty:

        st.warning(
            "No employees available. Add employees first."
        )

    else:

        employee_options = {
            f"{row['employee_code']} - {row['name']}":
            row["id"]
            for _, row in employees.iterrows()
        }

        # ----------------------------------------------------
        # LEAVE REQUEST
        # ----------------------------------------------------

        st.subheader("📝 Apply for Leave")

        with st.form("leave_request_form"):

            employee_name = st.selectbox(
                "Employee",
                list(employee_options.keys())
            )

            leave_type = st.selectbox(
                "Leave Type",
                [
                    "Casual Leave",
                    "Sick Leave",
                    "Earned Leave",
                    "Other"
                ]
            )

            col1, col2 = st.columns(2)

            with col1:

                start_date = st.date_input(
                    "Start Date"
                )

            with col2:

                end_date = st.date_input(
                    "End Date"
                )

            reason = st.text_area(
                "Reason"
            )

            submitted = st.form_submit_button(
                "📝 Submit Leave Request",
                type="primary"
            )

            if submitted:

                success, message = add_leave_request(
                    employee_options[employee_name],
                    leave_type,
                    start_date.isoformat(),
                    end_date.isoformat(),
                    reason
                )

                if success:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)

    # --------------------------------------------------------
    # LEAVE REQUESTS
    # --------------------------------------------------------

    st.divider()

    st.subheader("📋 Leave Requests")

    leave_requests = get_leave_requests()

    if leave_requests.empty:

        st.info(
            "No leave requests available."
        )

    else:

        st.dataframe(
            leave_requests,
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # UPDATE LEAVE STATUS
        # ----------------------------------------------------

        st.subheader("🔄 Update Leave Status")

        leave_id = st.selectbox(
            "Select Leave Request",
            leave_requests["id"].tolist()
        )

        leave_status = st.selectbox(
            "Status",
            [
                "Pending",
                "Approved",
                "Rejected"
            ]
        )

        if st.button(
            "💾 Update Leave",
            type="primary"
        ):

            success, message = update_leave_status(
                leave_id,
                leave_status
            )

            if success:

                st.success(message)
                st.rerun()

            else:

                st.error(message)


# ============================================================
# STEP 2I END
# ============================================================
# ============================================================
# STEP 2J - TASK MANAGEMENT
# ============================================================

def get_tasks():

    if not table_exists("tasks"):
        return pd.DataFrame()

    return fetch_dataframe(
        """
        SELECT *
        FROM tasks
        ORDER BY id DESC
        """
    )


def add_task(
    employee_id,
    title,
    description,
    due_date
):

    if not title.strip():
        return False, "Task title is required."

    try:

        execute_query(
            """
            INSERT INTO tasks
            (
                employee_id,
                title,
                description,
                due_date,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                employee_id,
                title.strip(),
                description.strip(),
                due_date,
                "Pending"
            )
        )

        return True, "Task assigned successfully."

    except sqlite3.Error as e:

        return False, str(e)


def update_task_status(task_id, status):

    valid_statuses = [
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled"
    ]

    if status not in valid_statuses:
        return False, "Invalid task status."

    try:

        execute_query(
            """
            UPDATE tasks
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                task_id
            )
        )

        return True, "Task status updated successfully."

    except sqlite3.Error as e:

        return False, str(e)


# ============================================================
# TASK MANAGEMENT UI
# ============================================================

if selected_module == "Leave & Tasks":

    st.divider()

    st.subheader("📝 Task Management")

    employees = get_employees()

    if employees.empty:

        st.warning(
            "No employees available. Add employees first."
        )

    else:

        employee_options = {
            f"{row['employee_code']} - {row['name']}":
            row["id"]
            for _, row in employees.iterrows()
        }

        with st.form("task_form"):

            employee_name = st.selectbox(
                "Assign Task To",
                list(employee_options.keys())
            )

            title = st.text_input(
                "Task Title"
            )

            description = st.text_area(
                "Task Description"
            )

            due_date = st.date_input(
                "Due Date"
            )

            submitted = st.form_submit_button(
                "➕ Assign Task",
                type="primary"
            )

            if submitted:

                success, message = add_task(
                    employee_options[employee_name],
                    title,
                    description,
                    due_date.isoformat()
                )

                if success:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(message)

    # --------------------------------------------------------
    # TASK LIST
    # --------------------------------------------------------

    st.divider()

    st.subheader("📋 Assigned Tasks")

    tasks = get_tasks()

    if tasks.empty:

        st.info(
            "No tasks available."
        )

    else:

        st.dataframe(
            tasks,
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # UPDATE TASK STATUS
        # ----------------------------------------------------

        st.subheader("🔄 Update Task Status")

        task_id = st.selectbox(
            "Select Task",
            tasks["id"].tolist()
        )

        task_status = st.selectbox(
            "New Status",
            [
                "Pending",
                "In Progress",
                "Completed",
                "Cancelled"
            ]
        )

        if st.button(
            "💾 Update Task",
            type="primary"
        ):

            success, message = update_task_status(
                task_id,
                task_status
            )

            if success:

                st.success(message)
                st.rerun()

            else:

                st.error(message)


# ============================================================
# STEP 2J END
# ============================================================
# ============================================================
# STEP 2K - MANAGEMENT DASHBOARD
# ============================================================

def get_dashboard_count(table_name):

    if not table_exists(table_name):
        return 0

    return get_table_count(table_name)


def get_dashboard_summary():

    summary = {
        "employees": get_dashboard_count("employees"),
        "production": get_dashboard_count("production"),
        "quality": get_dashboard_count("quality_checks"),
        "orders": get_dashboard_count("orders"),
        "dispatch": get_dashboard_count("dispatch"),
        "raw_materials": get_dashboard_count("raw_materials"),
    }

    return summary


# ============================================================
# DASHBOARD UI
# ============================================================

if selected_module == "Dashboard":

    st.header("📊 Management Dashboard")

    dashboard = get_dashboard_summary()

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "👥 Employees",
        dashboard["employees"]
    )

    col2.metric(
        "🏭 Production Records",
        dashboard["production"]
    )

    col3.metric(
        "🔬 Quality Checks",
        dashboard["quality"]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🧾 Orders",
        dashboard["orders"]
    )

    col2.metric(
        "🚚 Dispatch Records",
        dashboard["dispatch"]
    )

    col3.metric(
        "🧱 Raw Materials",
        dashboard["raw_materials"]
    )

    # --------------------------------------------------------
    # PRODUCTION SUMMARY
    # --------------------------------------------------------

    st.divider()

    st.subheader("🏭 Production Overview")

    if table_exists("production"):

        production_data = fetch_dataframe(
            """
            SELECT *
            FROM production
            ORDER BY id DESC
            LIMIT 10
            """
        )

        if not production_data.empty:

            st.dataframe(
                production_data,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No production records available."
            )

    # --------------------------------------------------------
    # QUALITY SUMMARY
    # --------------------------------------------------------

    st.subheader("🔬 Quality Overview")

    if table_exists("quality_checks"):

        quality_data = fetch_dataframe(
            """
            SELECT *
            FROM quality_checks
            ORDER BY id DESC
            LIMIT 10
            """
        )

        if not quality_data.empty:

            st.dataframe(
                quality_data,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No quality records available."
            )

    # --------------------------------------------------------
    # ORDER SUMMARY
    # --------------------------------------------------------

    st.subheader("🧾 Recent Orders")

    if table_exists("orders"):

        order_data = fetch_dataframe(
            """
            SELECT *
            FROM orders
            ORDER BY id DESC
            LIMIT 10
            """
        )

        if not order_data.empty:

            st.dataframe(
                order_data,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No order records available."
            )


# ============================================================
# STEP 2K END
# ============================================================
# ============================================================
# STEP 2L - STOCK & DISPATCH DASHBOARD SUMMARY
# ============================================================

if selected_module == "Dashboard":

    # --------------------------------------------------------
    # RAW MATERIAL STOCK
    # --------------------------------------------------------

    st.divider()

    st.subheader("🧱 Raw Material Stock")

    if table_exists("stock"):

        raw_stock = fetch_dataframe(
            """
            SELECT
                item_id,
                SUM(quantity) AS total_quantity
            FROM stock
            WHERE item_type = ?
            GROUP BY item_id
            ORDER BY total_quantity DESC
            """,
            ("Raw Material",)
        )

        if not raw_stock.empty:

            st.dataframe(
                raw_stock,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No raw material stock available."
            )

    # --------------------------------------------------------
    # FINISHED GOODS STOCK
    # --------------------------------------------------------

    st.subheader("📦 Finished Goods Stock")

    if table_exists("stock"):

        finished_stock = fetch_dataframe(
            """
            SELECT
                item_id,
                SUM(quantity) AS total_quantity
            FROM stock
            WHERE item_type = ?
            GROUP BY item_id
            ORDER BY total_quantity DESC
            """,
            ("Finished Goods",)
        )

        if not finished_stock.empty:

            st.dataframe(
                finished_stock,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No finished goods stock available."
            )

    # --------------------------------------------------------
    # DISPATCH SUMMARY
    # --------------------------------------------------------

    st.subheader("🚚 Dispatch Overview")

    if table_exists("dispatch"):

        dispatch_summary = fetch_dataframe(
            """
            SELECT
                status,
                COUNT(*) AS total_records
            FROM dispatch
            GROUP BY status
            ORDER BY total_records DESC
            """,
        )

        if not dispatch_summary.empty:

            st.dataframe(
                dispatch_summary,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No dispatch records available."
            )


# ============================================================
# STEP 2L END
# ============================================================
# ============================================================
# STEP 2M - QUALITY CONTROL MODULE
# ============================================================

if selected_module == "Quality Control":

    st.header("🔬 Quality Control")

    # --------------------------------------------------------
    # EXISTING QUALITY CHECK RECORDS
    # --------------------------------------------------------

    st.subheader("📋 Quality Check Records")

    if table_exists("quality_checks"):

        quality_data = fetch_dataframe(
            """
            SELECT *
            FROM quality_checks
            ORDER BY id DESC
            """
        )

        if not quality_data.empty:

            st.dataframe(
                quality_data,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No quality check records available."
            )

    else:

        st.error(
            "Quality checks table not found."
        )

    # --------------------------------------------------------
    # QUALITY SUMMARY
    # --------------------------------------------------------

    st.divider()

    st.subheader("📊 Quality Summary")

    if table_exists("quality_checks"):

        quality_summary = fetch_dataframe(
            """
            SELECT *
            FROM quality_checks
            ORDER BY id DESC
            LIMIT 10
            """
        )

        if not quality_summary.empty:

            st.dataframe(
                quality_summary,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No quality data available."
            )


# ============================================================
# STEP 2M END
# ============================================================
# ============================================================
# STEP 2N - PRODUCTION MANAGEMENT
# ============================================================

def get_production_records():

    if not table_exists("production"):
        return pd.DataFrame()

    return fetch_dataframe(
        """
        SELECT *
        FROM production
        ORDER BY id DESC
        """
    )


# ============================================================
# PRODUCTION MODULE
# ============================================================

if selected_module == "Production":

    st.header("🏭 Production Management")

    production_data = get_production_records()

    # --------------------------------------------------------
    # PRODUCTION RECORDS
    # --------------------------------------------------------

    st.subheader("📋 Production Records")

    if production_data.empty:

        st.info(
            "No production records available."
        )

    else:

        st.dataframe(
            production_data,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # PRODUCTION SUMMARY
    # --------------------------------------------------------

    st.divider()

    st.subheader("📊 Production Overview")

    if not production_data.empty:

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Production Records",
            len(production_data)
        )

        if "status" in production_data.columns:

            completed = (
                production_data["status"]
                .astype(str)
                .str.lower()
                .eq("completed")
                .sum()
            )

            col2.metric(
                "Completed",
                completed
            )

        else:

            col2.metric(
                "Status Information",
                "N/A"
            )

    else:

        st.info(
            "Production overview is not available yet."
        )


# ============================================================
# STEP 2N END
# ============================================================
# ============================================================
# STEP 2O - RAW MATERIAL MANAGEMENT
# ============================================================

def get_raw_materials():

    if not table_exists("raw_materials"):
        return pd.DataFrame()

    return fetch_dataframe(
        """
        SELECT *
        FROM raw_materials
        ORDER BY id DESC
        """
    )


# ============================================================
# RAW MATERIAL MODULE
# ============================================================

if selected_module == "Raw Materials":

    st.header("🧱 Raw Material Management")

    raw_materials = get_raw_materials()

    # --------------------------------------------------------
    # RAW MATERIAL RECORDS
    # --------------------------------------------------------

    st.subheader("📋 Raw Material Records")

    if raw_materials.empty:

        st.info(
            "No raw material records available."
        )

    else:

        st.dataframe(
            raw_materials,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # RAW MATERIAL SUMMARY
    # --------------------------------------------------------

    st.divider()

    st.subheader("📊 Raw Material Overview")

    if not raw_materials.empty:

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Raw Material Records",
            len(raw_materials)
        )

        if "status" in raw_materials.columns:

            active = (
                raw_materials["status"]
                .astype(str)
                .str.lower()
                .eq("active")
                .sum()
            )

            col2.metric(
                "Active Materials",
                active
            )

        else:

            col2.metric(
                "Status Information",
                "N/A"
            )

    else:

        st.info(
            "Raw material overview is not available yet."
        )


# ============================================================
# STEP 2O END
# ============================================================
# ============================================================
# STEP 2P - USER MANAGEMENT
# ============================================================

def get_users():

    if not table_exists("users"):
        return pd.DataFrame()

    return fetch_dataframe(
        """
        SELECT id, username, role, status
        FROM users
        ORDER BY id DESC
        """
    )


def update_user_role(user_id, role):

    valid_roles = [
        "Admin",
        "Manager",
        "Production",
        "Quality",
        "Warehouse",
        "Sales",
        "Dispatch",
        "HR"
    ]

    if role not in valid_roles:
        return False, "Invalid role."

    try:

        execute_query(
            """
            UPDATE users
            SET role = ?
            WHERE id = ?
            """,
            (
                role,
                user_id
            )
        )

        return True, "User role updated successfully."

    except sqlite3.Error as e:

        return False, str(e)


def update_user_status(user_id, status):

    valid_statuses = [
        "Active",
        "Inactive"
    ]

    if status not in valid_statuses:
        return False, "Invalid user status."

    try:

        execute_query(
            """
            UPDATE users
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                user_id
            )
        )

        return True, "User status updated successfully."

    except sqlite3.Error as e:

        return False, str(e)


# ============================================================
# USER MANAGEMENT UI
# ============================================================

if selected_module == "Users":

    # Only Admin can manage users
    if user_role != "Admin":

        st.error(
            "🚫 Only Admin can manage users."
        )

        st.stop()

    st.header("🔐 User Management")

    users = get_users()

    if users.empty:

        st.info(
            "No users available."
        )

    else:

        st.subheader("📋 System Users")

        st.dataframe(
            users,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("🔄 Update User")

        user_id = st.selectbox(
            "Select User",
            users["id"].tolist()
        )

        new_role = st.selectbox(
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

        new_status = st.selectbox(
            "Status",
            [
                "Active",
                "Inactive"
            ]
        )

        if st.button(
            "💾 Update User",
            type="primary"
        ):

            role_success, role_message = update_user_role(
                user_id,
                new_role
            )

            status_success, status_message = update_user_status(
                user_id,
                new_status
            )

            if role_success and status_success:

                st.success(
                    "User updated successfully."
                )

                st.rerun()

            else:

                if not role_success:
                    st.error(role_message)

                if not status_success:
                    st.error(status_message)


# ============================================================
# STEP 2P END
# ============================================================
# ============================================================
# STEP 2Q - MODULE INTEGRATION FOUNDATION
# RAW MATERIAL → PRODUCTION → FINISHED GOODS
# ============================================================

def get_stock_by_item(item_type, item_id):

    if not table_exists("stock"):
        return 0

    result = fetch_one(
        """
        SELECT COALESCE(SUM(quantity), 0)
        FROM stock
        WHERE item_type = ?
          AND item_id = ?
        """,
        (
            item_type,
            item_id
        )
    )

    return result[0] if result else 0


def get_raw_material_stock(item_id):

    return get_stock_by_item(
        "Raw Material",
        item_id
    )


def get_finished_goods_stock(product_id):

    return get_stock_by_item(
        "Finished Goods",
        product_id
    )


def check_raw_material_availability(
    item_id,
    required_quantity
):
    """
    Check whether sufficient raw material
    is available before production.
    """

    available_quantity = get_raw_material_stock(
        item_id
    )

    return available_quantity >= required_quantity


def check_finished_goods_availability(
    product_id,
    required_quantity
):
    """
    Check whether sufficient finished goods
    are available for an order/dispatch.
    """

    available_quantity = get_finished_goods_stock(
        product_id
    )

    return available_quantity >= required_quantity


# ============================================================
# INTEGRATION INFORMATION
# ============================================================

if selected_module == "Production":

    st.divider()

    st.subheader("🔗 Material Availability")

    st.info(
        "Production will verify raw-material availability "
        "before production processing."
    )


elif selected_module == "Orders":

    st.divider()

    st.subheader("🔗 Finished Goods Availability")

    st.info(
        "Orders can verify finished-goods availability "
        "before dispatch processing."
    )


# ============================================================
# STEP 2Q END
# ============================================================
# ============================================================
 # ============================================================
# STEP 2R - PRODUCTION FLOW INTEGRATION
# ============================================================

def validate_production_material(
    raw_material_id,
    required_quantity
):
    """
    Check whether enough raw material is available
    before starting production.
    """

    if required_quantity <= 0:
        return False, "Required quantity must be greater than 0."

    available_quantity = get_raw_material_stock(
        raw_material_id
    )

    if available_quantity < required_quantity:

        return (
            False,
            f"Insufficient raw material stock. "
            f"Available: {available_quantity}"
        )

    return True, "Raw material available."


def validate_production_output(
    product_id,
    produced_quantity
):
    """
    Validate finished-goods production quantity.
    """

    if produced_quantity <= 0:

        return (
            False,
            "Produced quantity must be greater than 0."
        )

    return True, "Production quantity valid."


# ============================================================
# PRODUCTION FLOW UI
# ============================================================

if selected_module == "Production":

    st.divider()

    st.subheader("🔗 Production Material & Output Check")

    col1, col2 = st.columns(2)

    with col1:

        raw_material_id = st.number_input(
            "Raw Material ID",
            min_value=1,
            step=1
        )

        required_quantity = st.number_input(
            "Required Raw Material Quantity",
            min_value=0.0,
            step=1.0
        )

    with col2:

        product_id = st.number_input(
            "Finished Product ID",
            min_value=1,
            step=1
        )

        produced_quantity = st.number_input(
            "Produced Quantity",
            min_value=0.0,
            step=1.0
        )

    if st.button(
        "🔎 Check Production Flow",
        type="primary"
    ):

        material_ok, material_message = (
            validate_production_material(
                raw_material_id,
                required_quantity
            )
        )

        output_ok, output_message = (
            validate_production_output(
                product_id,
                produced_quantity
            )
        )

        if material_ok:
            st.success(material_message)
        else:
            st.error(material_message)

        if output_ok:
            st.success(output_message)
        else:
            st.error(output_message)


# ============================================================
# STEP 2R END
# ============================================================
# ============================================================
# STEP 2S - PRODUCTION TRANSACTION LAYER
# ============================================================

def create_production_transaction(
    raw_material_id,
    required_quantity,
    product_id,
    produced_quantity
):
    """
    Production transaction controller.

    Flow:
    1. Validate raw material
    2. Validate production output
    3. Return transaction information

    Actual database stock movement will be connected
    after the existing database schema is mapped.
    """

    # --------------------------------------------------------
    # VALIDATE RAW MATERIAL
    # --------------------------------------------------------

    material_ok, material_message = (
        validate_production_material(
            raw_material_id,
            required_quantity
        )
    )

    if not material_ok:

        return {
            "success": False,
            "message": material_message
        }

    # --------------------------------------------------------
    # VALIDATE PRODUCTION OUTPUT
    # --------------------------------------------------------

    output_ok, output_message = (
        validate_production_output(
            product_id,
            produced_quantity
        )
    )

    if not output_ok:

        return {
            "success": False,
            "message": output_message
        }

    # --------------------------------------------------------
    # TRANSACTION INFORMATION
    # --------------------------------------------------------

    return {
        "success": True,
        "message": "Production transaction validated.",
        "raw_material_id": raw_material_id,
        "raw_material_quantity": required_quantity,
        "product_id": product_id,
        "produced_quantity": produced_quantity
    }


# ============================================================
# PRODUCTION TRANSACTION UI
# ============================================================

if selected_module == "Production":

    st.divider()

    st.subheader("🏭 Production Transaction")

    if st.button(
        "▶️ Validate Production Transaction",
        type="primary"
    ):

        transaction = create_production_transaction(
            raw_material_id,
            required_quantity,
            product_id,
            produced_quantity
        )

        if transaction["success"]:

            st.success(
                transaction["message"]
            )

            st.write(
                "Raw Material ID:",
                transaction["raw_material_id"]
            )

            st.write(
                "Raw Material Quantity:",
                transaction["raw_material_quantity"]
            )

            st.write(
                "Finished Product ID:",
                transaction["product_id"]
            )

            st.write(
                "Produced Quantity:",
                transaction["produced_quantity"]
            )

        else:

            st.error(
                transaction["message"]
            )


# ============================================================
# STEP 2S END
# ============================================================
# ============================================================
# STEP 2T - STOCK MOVEMENT LAYER
# ============================================================

def calculate_remaining_stock(
    current_stock,
    used_quantity
):
    """
    Calculate remaining raw material stock.
    """

    if used_quantity < 0:
        return None

    if used_quantity > current_stock:
        return None

    return current_stock - used_quantity


def calculate_finished_goods_stock(
    current_stock,
    produced_quantity
):
    """
    Calculate updated finished goods stock.
    """

    if produced_quantity < 0:
        return None

    return current_stock + produced_quantity


def prepare_stock_movement(
    raw_material_id,
    required_quantity,
    product_id,
    produced_quantity
):
    """
    Prepare the stock movement required by a
    production transaction.
    """

    raw_stock = get_raw_material_stock(
        raw_material_id
    )

    finished_stock = get_finished_goods_stock(
        product_id
    )

    remaining_raw_stock = calculate_remaining_stock(
        raw_stock,
        required_quantity
    )

    if remaining_raw_stock is None:

        return {
            "success": False,
            "message": "Insufficient raw material stock."
        }

    updated_finished_stock = (
        calculate_finished_goods_stock(
            finished_stock,
            produced_quantity
        )
    )

    return {
        "success": True,
        "raw_material_id": raw_material_id,
        "raw_stock_before": raw_stock,
        "raw_material_used": required_quantity,
        "raw_stock_after": remaining_raw_stock,
        "product_id": product_id,
        "finished_stock_before": finished_stock,
        "finished_goods_added": produced_quantity,
        "finished_stock_after": updated_finished_stock
    }


# ============================================================
# STOCK MOVEMENT PREVIEW
# ============================================================

if selected_module == "Production":

    st.divider()

    st.subheader("📦 Production Stock Movement")

    if st.button(
        "📊 Prepare Stock Movement"
    ):

        movement = prepare_stock_movement(
            raw_material_id,
            required_quantity,
            product_id,
            produced_quantity
        )

        if movement["success"]:

            st.success(
                "Stock movement is ready."
            )

            col1, col2 = st.columns(2)

            with col1:

                st.write("### 🧱 Raw Material")

                st.write(
                    "Stock Before:",
                    movement["raw_stock_before"]
                )

                st.write(
                    "Used:",
                    movement["raw_material_used"]
                )

                st.write(
                    "Stock After:",
                    movement["raw_stock_after"]
                )

            with col2:

                st.write("### 📦 Finished Goods")

                st.write(
                    "Stock Before:",
                    movement["finished_stock_before"]
                )

                st.write(
                    "Produced:",
                    movement["finished_goods_added"]
                )

                st.write(
                    "Stock After:",
                    movement["finished_stock_after"]
                )

        else:

            st.error(
                movement["message"]
            )


# ============================================================
# STEP 2T END
# ============================================================
# ============================================================
# STEP 2U - PRODUCTION TRANSACTION ENGINE
# ============================================================

def run_production_transaction(
    raw_material_id,
    required_quantity,
    product_id,
    produced_quantity
):
    """
    Complete production transaction controller.

    Current stage:
    - Validate raw material
    - Validate production output
    - Prepare stock movement
    - Return transaction result

    Database stock update will be connected only after
    the existing stock-table structure is confirmed.
    """

    # --------------------------------------------------------
    # 1. VALIDATE PRODUCTION
    # --------------------------------------------------------

    transaction = create_production_transaction(
        raw_material_id,
        required_quantity,
        product_id,
        produced_quantity
    )

    if not transaction["success"]:

        return transaction


    # --------------------------------------------------------
    # 2. PREPARE STOCK MOVEMENT
    # --------------------------------------------------------

    movement = prepare_stock_movement(
        raw_material_id,
        required_quantity,
        product_id,
        produced_quantity
    )

    if not movement["success"]:

        return movement


    # --------------------------------------------------------
    # 3. TRANSACTION RESULT
    # --------------------------------------------------------

    return {
        "success": True,
        "message": (
            "Production transaction prepared successfully."
        ),
        "movement": movement
    }


# ============================================================
# PRODUCTION TRANSACTION ACTION
# ============================================================

if selected_module == "Production":

    st.divider()

    st.subheader("⚙️ Production Transaction")

    if st.button(
        "🏭 Process Production",
        type="primary"
    ):

        result = run_production_transaction(
            raw_material_id,
            required_quantity,
            product_id,
            produced_quantity
        )

        if result["success"]:

            st.success(
                result["message"]
            )

            movement = result["movement"]

            st.write(
                "Raw Material Stock After:",
                movement["raw_stock_after"]
            )

            st.write(
                "Finished Goods Stock After:",
                movement["finished_stock_after"]
            )

        else:

            st.error(
                result["message"]
            )


# ============================================================
# STEP 2U END
# ============================================================
# ============================================================
# STEP 2V - PRODUCTION TRANSACTION RECORD
# ============================================================

def save_production_record(
    raw_material_id,
    required_quantity,
    product_id,
    produced_quantity
):
    """
    Save a production record using the existing
    production table.

    The function checks the available columns first,
    so it does not assume a fixed database schema.
    """

    if not table_exists("production"):
        return False, "Production table not found."

    # Get existing production-table columns
    columns = get_table_columns("production")

    # Possible column mappings
    raw_material_column = None
    required_quantity_column = None
    product_column = None
    produced_quantity_column = None

    for column in columns:

        name = column.lower()

        if name in [
            "raw_material_id",
            "material_id"
        ]:
            raw_material_column = column

        elif name in [
            "required_quantity",
            "material_quantity",
            "quantity_used"
        ]:
            required_quantity_column = column

        elif name in [
            "product_id",
            "finished_product_id"
        ]:
            product_column = column

        elif name in [
            "produced_quantity",
            "production_quantity",
            "quantity_produced"
        ]:
            produced_quantity_column = column

    # Check required fields
    if not raw_material_column:
        return False, "Production table has no raw material ID column."

    if not required_quantity_column:
        return False, "Production table has no material quantity column."

    if not product_column:
        return False, "Production table has no product ID column."

    if not produced_quantity_column:
        return False, "Production table has no produced quantity column."

    # Build query using discovered columns
    query = f"""
        INSERT INTO production
        (
            {raw_material_column},
            {required_quantity_column},
            {product_column},
            {produced_quantity_column}
        )
        VALUES (?, ?, ?, ?)
    """

    try:

        execute_query(
            query,
            (
                raw_material_id,
                required_quantity,
                product_id,
                produced_quantity
            )
        )

        return True, "Production record saved successfully."

    except sqlite3.Error as e:

        return False, f"Production record could not be saved: {e}"


# ============================================================
# STEP 2V END
# ============================================================
# ============================================================
# STEP 2W - SAVE PRODUCTION RECORD
# ============================================================

if selected_module == "Production":

    st.divider()

    st.subheader("💾 Save Production Record")

    if st.button(
        "✅ Save Production",
        type="primary"
    ):

        success, message = save_production_record(
            raw_material_id,
            required_quantity,
            product_id,
            produced_quantity
        )

        if success:

            st.success(message)
            st.rerun()

        else:

            st.error(message)


# ============================================================
# STEP 2W END
# ============================================================
# ============================================================
# STEP 2X - STOCK MOVEMENT PREPARATION
# ============================================================

def prepare_production_stock_movement(
    raw_material_id,
    required_quantity,
    product_id,
    produced_quantity
):
    """
    Prepare raw-material deduction and finished-goods addition
    for a production transaction.
    """

    # Current stock
    raw_stock = get_raw_material_stock(
        raw_material_id
    )

    finished_stock = get_finished_goods_stock(
        product_id
    )

    # Validate raw material
    if required_quantity <= 0:

        return {
            "success": False,
            "message": "Raw material quantity must be greater than 0."
        }

    if raw_stock < required_quantity:

        return {
            "success": False,
            "message": (
                f"Insufficient raw material stock. "
                f"Available: {raw_stock}"
            )
        }

    # Validate production output
    if produced_quantity <= 0:

        return {
            "success": False,
            "message": "Produced quantity must be greater than 0."
        }

    # Calculate movement
    raw_stock_after = (
        raw_stock - required_quantity
    )

    finished_stock_after = (
        finished_stock + produced_quantity
    )

    return {
        "success": True,
        "raw_material_id": raw_material_id,
        "raw_stock_before": raw_stock,
        "raw_material_used": required_quantity,
        "raw_stock_after": raw_stock_after,
        "product_id": product_id,
        "finished_stock_before": finished_stock,
        "finished_goods_added": produced_quantity,
        "finished_stock_after": finished_stock_after
    }


# ============================================================
# STEP 2X END
# ============================================================
# ============================================================
# STEP 2Y - PRODUCTION STOCK TRANSACTION CONTROLLER
# ============================================================

def process_production_stock(
    raw_material_id,
    required_quantity,
    product_id,
    produced_quantity
):
    """
    Controls the complete stock movement for production.

    Raw Material:
        Stock - Required Quantity

    Finished Goods:
        Stock + Produced Quantity
    """

    movement = prepare_production_stock_movement(
        raw_material_id,
        required_quantity,
        product_id,
        produced_quantity
    )

    if not movement["success"]:
        return movement

    return {
        "success": True,
        "message": "Production stock movement validated.",
        "raw_material": {
            "id": movement["raw_material_id"],
            "before": movement["raw_stock_before"],
            "used": movement["raw_material_used"],
            "after": movement["raw_stock_after"]
        },
        "finished_goods": {
            "id": movement["product_id"],
            "before": movement["finished_stock_before"],
            "added": movement["finished_goods_added"],
            "after": movement["finished_stock_after"]
        }
    }


# ============================================================
# STEP 2Y END
# ============================================================
# ============================================================
# STEP 2Z - ORDER & DISPATCH STOCK VALIDATION
# ============================================================

def validate_order_dispatch(
    product_id,
    required_quantity
):
    """
    Verify that enough finished goods are available
    before an order is dispatched.
    """

    if required_quantity <= 0:

        return {
            "success": False,
            "message": "Order quantity must be greater than 0."
        }

    available_stock = get_finished_goods_stock(
        product_id
    )

    if available_stock < required_quantity:

        return {
            "success": False,
            "message": (
                f"Insufficient finished goods stock. "
                f"Available: {available_stock}"
            )
        }

    remaining_stock = (
        available_stock - required_quantity
    )

    return {
        "success": True,
        "message": "Finished goods available for dispatch.",
        "product_id": product_id,
        "stock_before": available_stock,
        "dispatch_quantity": required_quantity,
        "stock_after": remaining_stock
    }


# ============================================================
# STEP 2Z END
# ============================================================
# ============================================================
# STEP 2AA - ORDER & DISPATCH UI INTEGRATION
# ============================================================

if selected_module == "Dispatch":

    st.divider()

    st.subheader("📦 Finished Goods Availability Check")

    if table_exists("orders"):

        orders = fetch_dataframe(
            """
            SELECT *
            FROM orders
            ORDER BY id DESC
            """
        )

        if not orders.empty:

            order_id = st.selectbox(
                "Select Order",
                orders["id"].tolist()
            )

            selected_order = orders[
                orders["id"] == order_id
            ].iloc[0]

            # Detect product column
            product_column = None

            for column in orders.columns:

                if column.lower() in [
                    "product_id",
                    "finished_product_id"
                ]:
                    product_column = column
                    break

            # Detect quantity column
            quantity_column = None

            for column in orders.columns:

                if column.lower() in [
                    "quantity",
                    "order_quantity"
                ]:
                    quantity_column = column
                    break

            if product_column and quantity_column:

                product_id = selected_order[
                    product_column
                ]

                order_quantity = selected_order[
                    quantity_column
                ]

                st.write(
                    "Product ID:",
                    product_id
                )

                st.write(
                    "Order Quantity:",
                    order_quantity
                )

                if st.button(
                    "🔎 Check Finished Goods",
                    type="primary"
                ):

                    result = validate_order_dispatch(
                        product_id,
                        order_quantity
                    )

                    if result["success"]:

                        st.success(
                            result["message"]
                        )

                        st.write(
                            "Available Stock:",
                            result["stock_before"]
                        )

                        st.write(
                            "Stock After Dispatch:",
                            result["stock_after"]
                        )

                    else:

                        st.error(
                            result["message"]
                        )

            else:

                st.warning(
                    "Order product/quantity columns "
                    "are not available."
                )

        else:

            st.info(
                "No orders available."
            )

    else:

        st.warning(
            "Orders table not found."
        )


# ============================================================
# STEP 2AA END
# ============================================================
# ============================================================
# STEP 2AB - REPORTS & EXCEL EXPORT
# ============================================================

def export_dataframe_to_excel(dataframe):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Report"
        )

    output.seek(0)

    return output


if selected_module == "Reports":

    st.header("📊 Reports & Export")

    report_type = st.selectbox(
        "Select Report",
        [
            "Employees",
            "Attendance",
            "Production",
            "Quality",
            "Orders",
            "Dispatch",
            "Raw Materials",
            "Stock"
        ]
    )

    report_tables = {
        "Employees": "employees",
        "Attendance": "attendance",
        "Production": "production",
        "Quality": "quality_checks",
        "Orders": "orders",
        "Dispatch": "dispatch",
        "Raw Materials": "raw_materials",
        "Stock": "stock"
    }

    selected_table = report_tables[report_type]

    if table_exists(selected_table):

        report_data = fetch_dataframe(
            f"""
            SELECT *
            FROM {selected_table}
            ORDER BY id DESC
            """
        )

        if report_data.empty:

            st.info(
                "No data available for this report."
            )

        else:

            st.dataframe(
                report_data,
                use_container_width=True,
                hide_index=True
            )

            excel_file = export_dataframe_to_excel(
                report_data
            )

            st.download_button(
                label="📥 Download Excel Report",
                data=excel_file,
                file_name=(
                    report_type.lower()
                    .replace(" ", "_")
                    + "_report.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet"
                )
            )

    else:

        st.warning(
            f"{selected_table} table not found."
        )


# ============================================================
# STEP 2AB END
# ============================================================
# ============================================================
# STEP 2AC - ADVANCED DASHBOARD ANALYTICS
# ============================================================

if selected_module == "Dashboard":

    st.divider()

    st.subheader("📈 Advanced Analytics")

    # --------------------------------------------------------
    # PRODUCTION ANALYTICS
    # --------------------------------------------------------

    if table_exists("production"):

        production_data = fetch_dataframe(
            """
            SELECT *
            FROM production
            ORDER BY id DESC
            """
        )

        if not production_data.empty:

            st.write("### 🏭 Production Analytics")

            col1, col2 = st.columns(2)

            col1.metric(
                "Production Records",
                len(production_data)
            )

            if "produced_quantity" in production_data.columns:

                total_produced = pd.to_numeric(
                    production_data["produced_quantity"],
                    errors="coerce"
                ).fillna(0).sum()

                col2.metric(
                    "Total Produced",
                    total_produced
                )

    # --------------------------------------------------------
    # ORDER ANALYTICS
    # --------------------------------------------------------

    if table_exists("orders"):

        order_data = fetch_dataframe(
            """
            SELECT *
            FROM orders
            ORDER BY id DESC
            """
        )

        if not order_data.empty:

            st.write("### 🧾 Order Analytics")

            col1, col2 = st.columns(2)

            col1.metric(
                "Total Orders",
                len(order_data)
            )

            if "status" in order_data.columns:

                pending_orders = (
                    order_data["status"]
                    .astype(str)
                    .str.lower()
                    .eq("pending")
                    .sum()
                )

                col2.metric(
                    "Pending Orders",
                    pending_orders
                )

    # --------------------------------------------------------
    # DISPATCH ANALYTICS
    # --------------------------------------------------------

    if table_exists("dispatch"):

        dispatch_data = fetch_dataframe(
            """
            SELECT *
            FROM dispatch
            ORDER BY id DESC
            """
        )

        if not dispatch_data.empty:

            st.write("### 🚚 Dispatch Analytics")

            col1, col2 = st.columns(2)

            col1.metric(
                "Total Dispatches",
                len(dispatch_data)
            )

            if "status" in dispatch_data.columns:

                delivered = (
                    dispatch_data["status"]
                    .astype(str)
                    .str.lower()
                    .eq("delivered")
                    .sum()
                )

                col2.metric(
                    "Delivered",
                    delivered
                )


# ============================================================
# STEP 2AC END
# ============================================================
# ============================================================
# STEP 2AD - AI / ML MODULE FOUNDATION
# ============================================================

if selected_module == "AI / ML":

    st.header("🤖 AI / ML Analytics")

    st.info(
        "AI/ML models will use historical MRPL data "
        "for forecasting and prediction."
    )

    # --------------------------------------------------------
    # MODEL MODULES
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📈 Demand Forecasting")

        st.write(
            "Forecast future product demand "
            "using historical order data."
        )

        if st.button(
            "Open Demand Forecasting"
        ):

            st.session_state["ai_module"] = (
                "Demand Forecasting"
            )

    with col2:

        st.subheader("🏭 Production Forecasting")

        st.write(
            "Estimate future production requirements "
            "from historical production data."
        )

        if st.button(
            "Open Production Forecasting"
        ):

            st.session_state["ai_module"] = (
                "Production Forecasting"
            )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📦 Stock-out Prediction")

        st.write(
            "Identify materials or products "
            "that may reach low stock."
        )

        if st.button(
            "Open Stock-out Prediction"
        ):

            st.session_state["ai_module"] = (
                "Stock-out Prediction"
            )

    with col2:

        st.subheader("🔬 Quality Risk Prediction")

        st.write(
            "Identify potential quality risks "
            "from historical quality data."
        )

        if st.button(
            "Open Quality Risk Prediction"
        ):

            st.session_state["ai_module"] = (
                "Quality Risk Prediction"
            )

    # --------------------------------------------------------
    # SELECTED AI MODULE
    # --------------------------------------------------------

    if "ai_module" in st.session_state:

        st.divider()

        st.subheader(
            f"Selected: {st.session_state['ai_module']}"
        )

        st.warning(
            "Model development will be added in the "
            "next AI/ML development steps."
        )


# ============================================================
# STEP 2AD END
# ============================================================
# ============================================================
# STEP 2AE - DEMAND FORECASTING
# ============================================================

def prepare_demand_data():

    if not table_exists("orders"):
        return pd.DataFrame()

    orders = fetch_dataframe(
        """
        SELECT *
        FROM orders
        ORDER BY id ASC
        """
    )

    if orders.empty:
        return pd.DataFrame()

    quantity_column = None

    for column in orders.columns:

        if column.lower() in [
            "quantity",
            "order_quantity"
        ]:
            quantity_column = column
            break

    date_column = None

    for column in orders.columns:

        if column.lower() in [
            "date",
            "order_date",
            "created_at"
        ]:
            date_column = column
            break

    if not quantity_column or not date_column:
        return pd.DataFrame()

    data = orders[
        [date_column, quantity_column]
    ].copy()

    data.columns = [
        "date",
        "quantity"
    ]

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    )

    data["quantity"] = pd.to_numeric(
        data["quantity"],
        errors="coerce"
    )

    data = data.dropna()

    if data.empty:
        return pd.DataFrame()

    data["date"] = data["date"].dt.date

    daily_demand = (
        data.groupby("date")["quantity"]
        .sum()
        .reset_index()
    )

    return daily_demand


def forecast_demand(data, periods=7):

    if data.empty:
        return pd.DataFrame()

    if len(data) < 3:
        return pd.DataFrame()

    average_demand = data["quantity"].mean()

    last_date = pd.to_datetime(
        data["date"]
    ).max()

    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=periods
    )

    forecast = pd.DataFrame({
        "date": future_dates,
        "forecast_demand": average_demand
    })

    return forecast


# ============================================================
# DEMAND FORECASTING UI
# ============================================================

if (
    selected_module == "AI / ML"
    and st.session_state.get("ai_module")
    == "Demand Forecasting"
):

    st.divider()

    st.subheader("📈 Demand Forecasting")

    demand_data = prepare_demand_data()

    if demand_data.empty:

        st.warning(
            "Not enough valid order data available "
            "for demand forecasting."
        )

    else:

        st.write("### Historical Demand")

        st.dataframe(
            demand_data,
            use_container_width=True,
            hide_index=True
        )

        forecast_days = st.slider(
            "Forecast Days",
            min_value=1,
            max_value=30,
            value=7
        )

        if st.button(
            "📈 Generate Demand Forecast",
            type="primary"
        ):

            forecast = forecast_demand(
                demand_data,
                forecast_days
            )

            if forecast.empty:

                st.warning(
                    "Not enough historical data "
                    "to generate forecast."
                )

            else:

                st.write("### 🔮 Forecast")

                st.dataframe(
                    forecast,
                    use_container_width=True,
                    hide_index=True
                )


# ============================================================
# STEP 2AE END
# ============================================================
# ============================================================
# STEP 2AF - PRODUCTION FORECASTING
# ============================================================

def prepare_production_data():

    if not table_exists("production"):
        return pd.DataFrame()

    production = fetch_dataframe(
        """
        SELECT *
        FROM production
        ORDER BY id ASC
        """
    )

    if production.empty:
        return pd.DataFrame()

    quantity_column = None

    for column in production.columns:

        if column.lower() in [
            "produced_quantity",
            "production_quantity",
            "quantity_produced"
        ]:
            quantity_column = column
            break

    date_column = None

    for column in production.columns:

        if column.lower() in [
            "date",
            "production_date",
            "created_at"
        ]:
            date_column = column
            break

    if not quantity_column or not date_column:
        return pd.DataFrame()

    data = production[
        [date_column, quantity_column]
    ].copy()

    data.columns = [
        "date",
        "quantity"
    ]

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    )

    data["quantity"] = pd.to_numeric(
        data["quantity"],
        errors="coerce"
    )

    data = data.dropna()

    if data.empty:
        return pd.DataFrame()

    data["date"] = data["date"].dt.date

    daily_production = (
        data.groupby("date")["quantity"]
        .sum()
        .reset_index()
    )

    return daily_production


def forecast_production(
    data,
    periods=7
):

    if data.empty:
        return pd.DataFrame()

    if len(data) < 3:
        return pd.DataFrame()

    average_production = (
        data["quantity"].mean()
    )

    last_date = pd.to_datetime(
        data["date"]
    ).max()

    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=periods
    )

    forecast = pd.DataFrame({
        "date": future_dates,
        "forecast_production": average_production
    })

    return forecast


# ============================================================
# PRODUCTION FORECASTING UI
# ============================================================

if (
    selected_module == "AI / ML"
    and st.session_state.get("ai_module")
    == "Production Forecasting"
):

    st.divider()

    st.subheader("🏭 Production Forecasting")

    production_data = (
        prepare_production_data()
    )

    if production_data.empty:

        st.warning(
            "Not enough valid production data "
            "available for forecasting."
        )

    else:

        st.write(
            "### Historical Production"
        )

        st.dataframe(
            production_data,
            use_container_width=True,
            hide_index=True
        )

        forecast_days = st.slider(
            "Forecast Days",
            min_value=1,
            max_value=30,
            value=7,
            key="production_forecast_days"
        )

        if st.button(
            "🏭 Generate Production Forecast",
            type="primary"
        ):

            forecast = forecast_production(
                production_data,
                forecast_days
            )

            if forecast.empty:

                st.warning(
                    "Not enough historical data "
                    "to generate forecast."
                )

            else:

                st.write(
                    "### 🔮 Production Forecast"
                )

                st.dataframe(
                    forecast,
                    use_container_width=True,
                    hide_index=True
                )


# ============================================================
# STEP 2AF END
# ============================================================
# ============================================================
# STEP 2AG - STOCK-OUT PREDICTION
# ============================================================

def prepare_stockout_data():

    if not table_exists("stock"):
        return pd.DataFrame()

    stock_data = fetch_dataframe(
        """
        SELECT *
        FROM stock
        ORDER BY id ASC
        """
    )

    if stock_data.empty:
        return pd.DataFrame()

    quantity_column = None

    for column in stock_data.columns:

        if column.lower() in [
            "quantity",
            "stock_quantity",
            "current_stock"
        ]:
            quantity_column = column
            break

    item_column = None

    for column in stock_data.columns:

        if column.lower() in [
            "item_id",
            "material_id",
            "product_id"
        ]:
            item_column = column
            break

    if not quantity_column or not item_column:
        return pd.DataFrame()

    data = stock_data[
        [item_column, quantity_column]
    ].copy()

    data.columns = [
        "item_id",
        "quantity"
    ]

    data["quantity"] = pd.to_numeric(
        data["quantity"],
        errors="coerce"
    )

    data = data.dropna()

    if data.empty:
        return pd.DataFrame()

    stock_summary = (
        data.groupby("item_id")["quantity"]
        .sum()
        .reset_index()
    )

    stock_summary["risk"] = stock_summary[
        "quantity"
    ].apply(
        lambda x:
        "High"
        if x <= 0
        else "Medium"
        if x <= 10
        else "Low"
    )

    return stock_summary


# ============================================================
# STOCK-OUT PREDICTION UI
# ============================================================

if (
    selected_module == "AI / ML"
    and st.session_state.get("ai_module")
    == "Stock-out Prediction"
):

    st.divider()

    st.subheader("📦 Stock-out Prediction")

    stockout_data = prepare_stockout_data()

    if stockout_data.empty:

        st.warning(
            "Not enough stock data available "
            "for stock-out analysis."
        )

    else:

        st.write("### Stock Risk Analysis")

        st.dataframe(
            stockout_data,
            use_container_width=True,
            hide_index=True
        )

        high_risk = (
            stockout_data["risk"]
            .eq("High")
            .sum()
        )

        medium_risk = (
            stockout_data["risk"]
            .eq("Medium")
            .sum()
        )

        low_risk = (
            stockout_data["risk"]
            .eq("Low")
            .sum()
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "🔴 High Risk",
            high_risk
        )

        col2.metric(
            "🟡 Medium Risk",
            medium_risk
        )

        col3.metric(
            "🟢 Low Risk",
            low_risk
        )


# ============================================================
# STEP 2AG END
# ============================================================
# ============================================================
# STEP 2AH - QUALITY RISK PREDICTION
# ============================================================

def prepare_quality_risk_data():

    if not table_exists("quality_checks"):
        return pd.DataFrame()

    quality_data = fetch_dataframe(
        """
        SELECT *
        FROM quality_checks
        ORDER BY id ASC
        """
    )

    if quality_data.empty:
        return pd.DataFrame()

    # Find quality result/status column
    result_column = None

    for column in quality_data.columns:

        if column.lower() in [
            "result",
            "status",
            "quality_status",
            "inspection_result"
        ]:
            result_column = column
            break

    if not result_column:
        return pd.DataFrame()

    data = quality_data.copy()

    data["risk"] = (
        data[result_column]
        .astype(str)
        .str.lower()
        .apply(
            lambda x:
            "High"
            if x in [
                "fail",
                "failed",
                "rejected",
                "defective"
            ]
            else "Low"
        )
    )

    return data


# ============================================================
# QUALITY RISK UI
# ============================================================

if (
    selected_module == "AI / ML"
    and st.session_state.get("ai_module")
    == "Quality Risk Prediction"
):

    st.divider()

    st.subheader("🔬 Quality Risk Prediction")

    quality_risk_data = (
        prepare_quality_risk_data()
    )

    if quality_risk_data.empty:

        st.warning(
            "Not enough quality data available "
            "for risk analysis."
        )

    else:

        st.write("### Quality Risk Analysis")

        st.dataframe(
            quality_risk_data,
            use_container_width=True,
            hide_index=True
        )

        high_risk = (
            quality_risk_data["risk"]
            .eq("High")
            .sum()
        )

        low_risk = (
            quality_risk_data["risk"]
            .eq("Low")
            .sum()
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "🔴 High Risk",
            high_risk
        )

        col2.metric(
            "🟢 Low Risk",
            low_risk
        )


# ============================================================
# STEP 2AH END
# ============================================================
# ============================================================
# STEP 2AI - AI / ML COMBINED DASHBOARD
# ============================================================

if selected_module == "AI / ML":

    st.divider()

    st.subheader("🤖 AI / ML Overview")

    # --------------------------------------------------------
    # DEMAND
    # --------------------------------------------------------

    demand_data = prepare_demand_data()

    if demand_data.empty:

        demand_status = "No Data"

    else:

        demand_status = "Ready"

    # --------------------------------------------------------
    # PRODUCTION
    # --------------------------------------------------------

    production_data = prepare_production_data()

    if production_data.empty:

        production_status = "No Data"

    else:

        production_status = "Ready"

    # --------------------------------------------------------
    # STOCK
    # --------------------------------------------------------

    stockout_data = prepare_stockout_data()

    if stockout_data.empty:

        stock_status = "No Data"

    else:

        stock_status = "Ready"

    # --------------------------------------------------------
    # QUALITY
    # --------------------------------------------------------

    quality_risk_data = (
        prepare_quality_risk_data()
    )

    if quality_risk_data.empty:

        quality_status = "No Data"

    else:

        quality_status = "Ready"

    # --------------------------------------------------------
    # AI MODULE CARDS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "📈 Demand Forecasting",
            demand_status
        )

    with col2:

        st.metric(
            "🏭 Production Forecasting",
            production_status
        )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "📦 Stock-out Prediction",
            stock_status
        )

    with col2:

        st.metric(
            "🔬 Quality Risk Prediction",
            quality_status
        )

    # --------------------------------------------------------
    # DATA AVAILABILITY
    # --------------------------------------------------------

    st.divider()

    st.subheader("📊 AI Data Availability")

    ai_status = pd.DataFrame({
        "AI Module": [
            "Demand Forecasting",
            "Production Forecasting",
            "Stock-out Prediction",
            "Quality Risk Prediction"
        ],
        "Data Status": [
            demand_status,
            production_status,
            stock_status,
            quality_status
        ]
    })

    st.dataframe(
        ai_status,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# STEP 2AI END
# ============================================================
# ============================================================
# STEP 2AJ - DEMAND FORECASTING ML MODEL
# ============================================================

from sklearn.linear_model import LinearRegression


def train_demand_model(data):

    if data.empty or len(data) < 3:
        return None, None

    data = data.copy()

    data["date"] = pd.to_datetime(data["date"])

    data = data.sort_values("date")

    data["day_number"] = range(len(data))

    X = data[["day_number"]]
    y = data["quantity"]

    model = LinearRegression()

    model.fit(X, y)

    return model, data


def predict_demand(model, data, periods):

    last_day = len(data)

    future_days = pd.DataFrame({
        "day_number": range(
            last_day,
            last_day + periods
        )
    })

    predictions = model.predict(
        future_days[["day_number"]]
    )

    predictions = predictions.clip(
        lower=0
    )

    last_date = data["date"].max()

    forecast_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=periods
    )

    forecast = pd.DataFrame({
        "date": forecast_dates,
        "predicted_demand": predictions
    })

    return forecast


# ============================================================
# DEMAND FORECASTING ML UI
# ============================================================

if (
    selected_module == "AI / ML"
    and st.session_state.get("ai_module")
    == "Demand Forecasting"
):

    st.divider()

    st.subheader("🤖 Demand Forecasting ML")

    demand_data = prepare_demand_data()

    if len(demand_data) < 3:

        st.warning(
            "At least 3 historical demand records "
            "are required."
        )

    else:

        model, training_data = train_demand_model(
            demand_data
        )

        forecast_days = st.slider(
            "Forecast Days",
            1,
            30,
            7,
            key="ml_demand_days"
        )

        if st.button(
            "🤖 Run ML Forecast",
            type="primary"
        ):

            forecast = predict_demand(
                model,
                training_data,
                forecast_days
            )

            st.subheader("🔮 Demand Forecast")

            st.dataframe(
                forecast,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# STEP 2AJ END
# ============================================================
# ============================================================
# STEP 2AK - PRODUCTION FORECASTING ML MODEL
# ============================================================

def train_production_model(data):

    if data.empty or len(data) < 3:
        return None, None

    data = data.copy()

    data["date"] = pd.to_datetime(data["date"])

    data = data.sort_values("date")

    data["day_number"] = range(len(data))

    X = data[["day_number"]]
    y = data["quantity"]

    model = LinearRegression()

    model.fit(X, y)

    return model, data


def predict_production(
    model,
    data,
    periods
):

    last_day = len(data)

    future_days = pd.DataFrame({
        "day_number": range(
            last_day,
            last_day + periods
        )
    })

    predictions = model.predict(
        future_days[["day_number"]]
    )

    predictions = predictions.clip(
        lower=0
    )

    last_date = data["date"].max()

    forecast_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=periods
    )

    forecast = pd.DataFrame({
        "date": forecast_dates,
        "predicted_production": predictions
    })

    return forecast


# ============================================================
# PRODUCTION FORECASTING ML UI
# ============================================================

if (
    selected_module == "AI / ML"
    and st.session_state.get("ai_module")
    == "Production Forecasting"
):

    st.divider()

    st.subheader("🤖 Production Forecasting ML")

    production_data = prepare_production_data()

    if len(production_data) < 3:

        st.warning(
            "At least 3 historical production records "
            "are required."
        )

    else:

        model, training_data = train_production_model(
            production_data
        )

        forecast_days = st.slider(
            "Forecast Days",
            1,
            30,
            7,
            key="ml_production_days"
        )

        if st.button(
            "🤖 Run Production Forecast",
            type="primary"
        ):

            forecast = predict_production(
                model,
                training_data,
                forecast_days
            )

            st.subheader(
                "🔮 Production Forecast"
            )

            st.dataframe(
                forecast,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# STEP 2AK END
# ============================================================
# ============================================================
# STEP 2AK - PRODUCTION FORECASTING ML MODEL
# ============================================================

def train_production_model(data):

    if data.empty or len(data) < 3:
        return None, None

    data = data.copy()

    data["date"] = pd.to_datetime(data["date"])

    data = data.sort_values("date")

    data["day_number"] = range(len(data))

    X = data[["day_number"]]
    y = data["quantity"]

    model = LinearRegression()

    model.fit(X, y)

    return model, data


def predict_production(
    model,
    data,
    periods
):

    last_day = len(data)

    future_days = pd.DataFrame({
        "day_number": range(
            last_day,
            last_day + periods
        )
    })

    predictions = model.predict(
        future_days[["day_number"]]
    )

    predictions = predictions.clip(
        lower=0
    )

    last_date = data["date"].max()

    forecast_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=periods
    )

    forecast = pd.DataFrame({
        "date": forecast_dates,
        "predicted_production": predictions
    })

    return forecast


# ============================================================
# PRODUCTION FORECASTING ML UI
# ============================================================

if (
    selected_module == "AI / ML"
    and st.session_state.get("ai_module")
    == "Production Forecasting"
):

    st.divider()

    st.subheader("🤖 Production Forecasting ML")

    production_data = prepare_production_data()

    if len(production_data) < 3:

        st.warning(
            "At least 3 historical production records "
            "are required."
        )

    else:

        model, training_data = train_production_model(
            production_data
        )

        forecast_days = st.slider(
            "Forecast Days",
            1,
            30,
            7,
            key="ml_production_days"
        )

        if st.button(
            "🤖 Run Production Forecast",
            type="primary"
        ):

            forecast = predict_production(
                model,
                training_data,
                forecast_days
            )

            st.subheader(
                "🔮 Production Forecast"
            )

            st.dataframe(
                forecast,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# STEP 2AK END
# ============================================================
# ============================================================
# FINAL UI POLISHING - CELL 1
# ============================================================

st.markdown(
    """
    <style>

    /* Main application background */
    .stApp {
        background: #f8fafc;
    }

    /* Main content area */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Headings */
    h1, h2, h3 {
        font-weight: 700;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        min-height: 42px;
    }

    /* Input fields */
    .stTextInput input,
    .stNumberInput input,
    .stSelectbox div,
    .stTextArea textarea {
        border-radius: 8px;
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        border-right: 1px solid #e5e7eb;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# FINAL UI POLISHING - CELL 1 END
# ============================================================
# ============================================================
# FINAL UI POLISHING - CELL 2
# ============================================================

st.markdown(
    """
    <div style="
        padding: 18px 22px;
        border-radius: 14px;
        background: white;
        border: 1px solid #e5e7eb;
        margin-bottom: 20px;
    ">
        <h1 style="margin:0;">
            🏭 MRPL Smart Manufacturing
        </h1>
        <p style="
            margin:6px 0 0 0;
            font-size:16px;
        ">
            Smart Management & Quality Management System
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# FINAL UI POLISHING - CELL 2 END
# ============================================================
# ============================================================
# FINAL UI POLISHING - CELL 3
# ============================================================

st.markdown(
    """
    <style>

    /* Sidebar title */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-weight: 700;
    }

    /* Sidebar navigation spacing */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 6px;
    }

    /* Section containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
    }

    /* Tables */
    [data-testid="stDataFrame"] {
        margin-top: 8px;
        margin-bottom: 15px;
    }

    /* Download buttons */
    .stDownloadButton > button {
        border-radius: 8px;
        font-weight: 600;
        min-height: 42px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# FINAL UI POLISHING - CELL 3 END
# ============================================================
# ============================================================
# FINAL UI POLISHING - CELL 4
# ============================================================

# Footer
st.markdown(
    """
    <div style="
        text-align:center;
        padding:18px 0 5px 0;
        margin-top:30px;
        border-top:1px solid #e5e7eb;
        font-size:14px;
        opacity:0.75;
    ">
        MRPL Smart Manufacturing & Quality Management System
        <br>
        © 2026 MRPL | Developed for Smart Manufacturing
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# FINAL UI POLISHING - CELL 4 END
# ============================================================
# ============================================================
# FINAL UI POLISHING - CELL 5
# ============================================================

st.markdown(
    """
    <style>

    /* Remove unnecessary top spacing */
    .block-container {
        padding-top: 1.5rem;
    }

    /* Consistent card appearance */
    .ui-card {
        padding: 18px;
        border-radius: 12px;
        background: white;
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
    }

    /* Responsive layout */
    @media (max-width: 768px) {

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        h1 {
            font-size: 1.8rem;
        }

        h2 {
            font-size: 1.4rem;
        }

        h3 {
            font-size: 1.2rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# FINAL UI POLISHING - CELL 5 END
# ============================================================

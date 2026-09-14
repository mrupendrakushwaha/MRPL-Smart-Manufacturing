# 🏭 MRPL Smart Manufacturing System

A web-based **Manufacturing & Quality Management System** designed for managing manufacturing operations, inventory, production, quality control, employees, attendance, orders, dispatch and product information.

The system is developed using **Python, Streamlit and SQLite** with role-based access for Admin, Manager and Employee users.

---

## 📌 Project Overview

MRPL Smart Manufacturing System is a centralized management application for organizing important manufacturing and administrative activities.

The system provides:

- 📊 Management Dashboard
- 🧱 Raw Material Management
- 🏭 Production Management
- 🧪 Quality Control
- 📦 Finished Goods Management
- 🚚 Orders & Dispatch Management
- 👥 Employee Management
- 🕐 Attendance Management
- 📅 Leave & Task Management
- 🛍️ Product Catalogue
- 🔐 User & Access Management
- 🙍 Employee Self-Service

---

# 🚀 Main Features

## 📊 1. Management Dashboard

The dashboard provides an overview of important operational data.

It includes:

- Total Raw Materials
- Production Batches
- Finished Goods
- Orders
- Dispatches
- Low Stock Items
- Production status overview
- Order status overview
- Low-stock alerts

The dashboard reads operational information directly from the database.

---

## 🧱 2. Raw Material Management

The Raw Materials module is used to manage manufacturing raw materials.

It can be used for:

- Adding raw materials
- Maintaining current stock
- Maintaining minimum stock levels
- Monitoring stock
- Identifying low-stock materials

The dashboard can display low-stock alerts when current stock reaches or falls below the minimum stock level.

---

## 🏭 3. Production Management

The Production module manages production batches.

It supports production-related records such as:

- Production batches
- Planned quantity
- Actual quantity
- Production status
- Production information

Production data is also used by the management dashboard for production-status analysis.

---

## 🧪 4. Quality Control

The Quality Control module is designed to manage quality-related records.

It supports:

- Quality inspection records
- Quality status
- Pass/Fail monitoring
- Quality information for manufactured products

The dashboard can track passed quality-control records.

---

## 📦 5. Finished Goods Management

The Finished Goods module manages finished products after production.

It can be used to maintain:

- Finished product information
- Quantity
- Stock
- Product records
- Finished goods status

---

## 🚚 6. Orders & Dispatch

This module manages customer orders and product dispatch.

### Orders

Order information can include:

- Order number
- Product
- Quantity
- Order status

### Dispatch

Dispatch information can include:

- Dispatch number
- Order number
- Product name
- Quantity
- Dispatch date
- Vehicle number
- Driver name
- Dispatch status

---

# 👥 7. Employee Management

The Employee Management module maintains employee records.

Employee information includes:

- Employee Code
- Employee Name
- Department
- Designation
- Phone
- Email
- Joining Date
- Employee Status

---

# 🕐 8. Attendance Management

The system provides attendance management for employees.

### Admin / Manager

Admin or Manager can:

- Select employee
- Select attendance date
- Set attendance status
- Enter check-in time
- Enter check-out time
- View attendance records

Available attendance statuses:

- Present
- Absent
- Leave

### Employee

Employees have a personal **My Attendance** section.

An employee can:

- View their attendance records
- Mark today's attendance
- Automatically record check-in time
- See whether today's attendance has already been marked

The employee check-in uses the current system time.

---

# 📅 9. Leave & Tasks

The system provides employee self-service functionality for leave and tasks.

### Leave

Employees can:

- View their leave records
- Apply for leave
- Select leave type
- Select start date
- Select end date
- Enter reason
- Submit a leave request

Available leave types include:

- Sick Leave
- Casual Leave
- Earned Leave

Leave requests can have a status such as:

- Pending
- Approved
- Rejected

### Tasks

Employees can access their assigned tasks through the **My Tasks** section.

---

# 🛍️ 10. Product Catalogue

The system contains a public product catalogue that can be viewed without staff login.

Products are divided into two main categories:

## 🔷 Shaped Refractory Products

Shaped products are refractory products manufactured in predefined shapes such as bricks and blocks.

### Products

1. Fireclay & High Alumina Bricks
2. Pre-Cast Pre-Fired (PCPF) Blocks
3. Silicon Carbide Bricks & Shapes
4. Acid-resistant Bricks

---

## 🔶 Unshaped Refractory Products

Unshaped products are monolithic or installation-based refractory materials.

### Products

1. Dense Castables
2. Low & Ultra Low Cement Castables
3. Insulating Castables
4. Plastic Masses
5. High Alumina Cement & Binder
6. Grouting Materials
7. Mortars
8. Gunning Mixes

---

# 📋 Product Catalogue Summary

| Category | Products |
|---|---:|
| Shaped Products | 4 |
| Unshaped Products | 8 |
| **Total Products** | **12** |

Each product can contain:

- Product Name
- Category
- Description
- Product Image
- Official Product Details Link

The application provides access to official product information through the product catalogue.

---

# 🔐 11. User Authentication & Role-Based Access

The system uses login authentication and role-based module access.

There are three major roles:

## 👑 Admin

Admin has access to:

- Dashboard
- Raw Materials
- Production
- Quality Control
- Finished Goods
- Orders & Dispatch
- Employees
- Attendance
- Leave & Tasks
- Products
- Users

---

## 👔 Manager

Manager has access to:

- Dashboard
- Raw Materials
- Production
- Quality Control
- Finished Goods
- Orders & Dispatch
- Employees
- Attendance
- Leave & Tasks
- Products

---

## 👨‍🏭 Employee

Employee has access to:

- My Profile
- My Attendance
- My Leave
- My Tasks

This provides different access levels depending on the user's role.

---

# 🙍 Employee Self-Service

Employees can independently access their own information.

### My Profile

Displays:

- Name
- Designation
- Department
- Phone
- Email
- Joining Date
- Status

### My Attendance

Displays:

- Personal attendance records
- Attendance date
- Attendance status
- Check-in time
- Check-out time

### My Leave

Employees can submit and view leave requests.

### My Tasks

Employees can view their assigned tasks.

---

# 🗄️ Database

The application uses **SQLite** as its database.

Database file:

```text
mrpl.db

---

## 👨‍💻 Developer

### Upendra Kushwaha

**MRPL Smart Manufacturing System**

> A manufacturing management application developed using Python, Streamlit and SQLite.

---

⭐ If you find this project useful, consider giving the repository a star.

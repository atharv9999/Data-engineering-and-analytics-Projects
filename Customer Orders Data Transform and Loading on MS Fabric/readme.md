# Customer Orders Data Lakehouse Pipeline on Microsoft Fabric

## 📁 Project Overview

This project implements a **daily truncate-load data pipeline** in **Microsoft Fabric** that ingests, transforms, and stores customer, order, and child item data from CSV files stored in OneLake. It uses **Spark notebooks** and **Lakehouse Delta tables**, following a structured ELT process.

---

## 📦 Data Sources (CSV Files)

All files are placed in the **Files folder** of a Fabric Lakehouse. Three types of files are handled:

### 1. `CUST_MSTR_<yyyymmdd>.csv`
- Contains customer master data.
- Multiple files exist, one per date.
- Example: `CUST_MSTR_20250701.csv`

### 2. `master_child_export-<yyyymmdd>.csv`
- Contains child records related to orders (1–3 items per order).
- Example: `master_child_export-20250701.csv`

### 3. `H_ECOM_ORDER.csv`
- A single file containing e-commerce order data.
- May be updated periodically.

---

## 🧪 Sample Fields per File

### CUST_MSTR:
| Column       | Type    |
|--------------|---------|
| CustomerID   | Integer |
| Name         | String  |
| Email        | String  |
| Country      | String  |

### master_child_export:
| Column       | Type    |
|--------------|---------|
| ParentID     | String  |
| ChildID      | String  |
| ItemName     | String  |
| Quantity     | Integer |

### H_ECOM_ORDER:
| Column       | Type    |
|--------------|---------|
| OrderID      | String  |
| CustomerID   | Integer |
| OrderDate    | Date    |
| Amount       | Float   |

---

## 🧱 Delta Tables Created

The notebook loads the data into the following **Delta tables** inside the same Lakehouse:

| Table Name       | Source Files                      | Notes                                    |
|------------------|------------------------------------|------------------------------------------|
| `cust_mstr`      | `CUST_MSTR_*.csv`                  | Adds `Date` column from file name        |
| `master_child`   | `master_child_export-*.csv`        | Adds `Date` and `DateKey` from file name |
| `h_ecom_order`   | `H_ECOM_ORDER.csv`                 | Parses `OrderDate` into proper `DateType`|

All tables are **overwritten daily** using truncate-load logic.

---

## ⚙️ Processing Logic (Notebook)

### Step 1: Extract `Date` from file name
- Uses `input_file_name()` and `regexp_extract()`.
- For `master_child`, also derives `DateKey` as `yyyyMMdd`.

### Step 2: Read only relevant files using glob patterns
- Prevents schema mismatches by separating file reads.

### Step 3: Transform data
- Adds or converts `Date`, `DateKey`, and `OrderDate` types.
- Ensures correct column types for downstream use.

### Step 4: Write to Delta Tables
- `mode("overwrite")` ensures clean load every run.
- `DROP TABLE IF EXISTS` used when schema types change.

---

## 🔁 Pipeline Trigger

- **Trigger Type**: Time-based (daily schedule)
- **Recommended Time**: Early morning (e.g., 07:00 IST)
- **Trigger Scope**: One activity calling the ELT notebook

This matches the problem requirement:  
> *"This process will work on truncate load on a daily basis."*

---

## 🔒 Notes

- No event-based trigger used (avoids accidental infinite loops).
- Delta tables stored in `/Tables/`, source files in `/Files/` within the Lakehouse.
- Avoids reading all files at once — each read is scoped to its filename pattern.

---

## 📂 Project Structure


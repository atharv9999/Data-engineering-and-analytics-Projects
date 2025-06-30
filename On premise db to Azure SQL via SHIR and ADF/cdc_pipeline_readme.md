# Incremental Data Load from PostgreSQL to Azure SQL using ADF (CDC-based)

## 📌 Project Overview

This project demonstrates an end-to-end data integration pipeline using **Azure Data Factory (ADF)** for **incremental (CDC-based) data loading** from an on-premises **PostgreSQL** database to an **Azure SQL Database**.

It uses a **timestamp-based Change Data Capture (CDC)** strategy and tracks pipeline runs using a **metadata table** to ensure only new or changed records are loaded in each run.

---

## 🧱 Architecture Components

| Component           | Details                                                              |
| ------------------- | -------------------------------------------------------------------- |
| Source Database     | PostgreSQL running on Azure VM                                       |
| Target Database     | Azure SQL Database                                                   |
| Integration Runtime | Self-Hosted Integration Runtime (SHIR) installed on same VM as PGSQL |
| Pipeline Tool       | Azure Data Factory                                                   |
| Incremental Logic   | Based on `last_updated` column and millisecond-precision filtering   |
| Metadata Tracking   | `sales_pipeline_metadata` table in Azure SQL                         |
| Data Format         | Tabular (relational data)                                            |

---

## 🛠️ PostgreSQL Setup (Source)

### sales table

```sql
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    sale_date TIMESTAMP NOT NULL DEFAULT now(),
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    store_id INT NOT NULL,
    quantity INT CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL,
    discount NUMERIC(5, 2) DEFAULT 0.0,
    total_amount NUMERIC(12, 2) NOT NULL,
    payment_type VARCHAR(20) CHECK (payment_type IN ('Cash', 'Card', 'UPI', 'Wallet')),
    status VARCHAR(20) DEFAULT 'Completed',
    remarks TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### ✅ Note:

- `last_updated` tracks insert timestamps.
- No update trigger is used (to avoid reloading old rows).

---

## 🔷 Azure SQL Setup (Target)

### sales table

```sql
CREATE TABLE sales (
    sale_id INT PRIMARY KEY,
    sale_date DATETIME2 NOT NULL,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    store_id INT NOT NULL,
    quantity INT,
    unit_price DECIMAL(10, 2),
    discount DECIMAL(5, 2),
    total_amount DECIMAL(12, 2),
    payment_type NVARCHAR(20),
    status NVARCHAR(20),
    remarks NVARCHAR(MAX),
    last_updated DATETIME2
);
```

### sales\_pipeline\_metadata table

```sql
CREATE TABLE sales_pipeline_metadata (
    id INT IDENTITY(1,1) PRIMARY KEY,
    run_timestamp DATETIME2 DEFAULT GETDATE(),
    last_loaded_time DATETIME2,
    rows_inserted INT,
    status NVARCHAR(20),
    remarks NVARCHAR(MAX)
);
```

### Stored procedures

```sql
CREATE PROCEDURE sp_get_max_last_updated
AS
BEGIN
    SELECT MAX(last_updated) AS last_loaded_time FROM sales;
END;

CREATE PROCEDURE sp_insert_sales_metadata
    @last_loaded_time DATETIME2,
    @rows_inserted INT,
    @status NVARCHAR(20),
    @remark NVARCHAR(MAX)
AS
BEGIN
    INSERT INTO sales_pipeline_metadata (
        last_loaded_time, rows_inserted, status, remarks)
    VALUES (
        @last_loaded_time, @rows_inserted, @status, @remark);
END;
```

---

## 🔄 ADF Pipeline Structure

### Activities:

1. **Lookup**: Get last successful `last_loaded_time` from metadata table.
2. **Copy Data**: Copy rows from PostgreSQL where `last_updated > last_loaded_time`.
   - Use query:
     ```sql
     SELECT * FROM sales
     WHERE date_trunc('milliseconds', last_updated) > TIMESTAMP '...';
     ```
3. **Stored Proc**: Fetch new max `last_updated` from Azure SQL sink table.
4. **Set Variable**: Store the fetched timestamp in a pipeline variable.
5. **Stored Proc**: Insert success metadata row.
6. **Stored Proc (Failure path)**: Insert failure metadata with same timestamp and error message.

### Variables:

- `newLastLoadedTime`: Stores the max timestamp for use in next run.

### Trigger:

- Daily or custom trigger (e.g., last Saturday of month).

---

## ⚠️ Common Problems and Fixes

| Problem                        | Cause                              | Solution                                                                                     |
| ------------------------------ | ---------------------------------- | -------------------------------------------------------------------------------------------- |
| Duplicate Key Error            | Microsecond mismatch in timestamps | Truncate `last_updated` in PG using `date_trunc('milliseconds', ...)`                        |
| ADF can't read `firstRow`      | Stored proc didn't return rows     | Ensure `SELECT` returns result in `sp_get_max_last_updated`                                  |
| Pipeline reprocesses same data | Triggered by rounded timestamps    | Use consistent millisecond formatting using `formatDateTime(..., 'yyyy-MM-dd HH:mm:ss.fff')` |

---

## ✅ Edge Cases Handled

- Failure metadata insert with error message.
- Timestamp formatting for consistent precision.
- Initial dummy metadata entry to load all data in first run.

---

## 🔮 Future Improvements

- Use `MERGE` instead of `INSERT` to support UPSERT (handle duplicates).
- Add second metadata column `max_sale_id` for deterministic sorting.
- Add logging table for pipeline performance & duration.
- Add email/SMS alerts on pipeline failure.
- Extend to include FTP/SFTP data ingestion before processing.

---

## 📄 Credits

Built and tested by Atharv Kulkarni using PostgreSQL, Azure SQL, and ADF with SHIR on Windows Server VM.

---

Let me know if you'd like a diagram, GitHub project layout, or YAML template for deployment.


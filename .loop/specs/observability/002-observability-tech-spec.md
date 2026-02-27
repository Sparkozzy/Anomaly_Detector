# Technical Specification: Observability and Documentation Update

## Architecture Overview
The system follows a linear pipeline architecture:
1.  **Data Ingestion**: `db.py` fetches call data from Supabase.
2.  **Processing**: `metrics.py` aggregates raw data into metrics.
3.  **Analysis**: `detector.py` compares current metrics against historical baselines using Z-score and percentiles.
4.  **Reporting**: `report.py` formats anomalies and sends alerts via WhatsApp (Z-API).
5.  **Orchestration**: `main.py` coordinates the entire flow.

## Technical Stack
-   **Language**: Python 3.x
-   **Database**: Supabase (PostgreSQL)
-   **Data Analysis**: Pandas, NumPy
-   **Notification**: Z-API (WhatsApp)

## Component Design
-   **`db.py`**: Responsible for database connections and queries. Needs logging for connection status and row counts.
-   **`metrics.py`**: Responsible for data transformation. Needs logging for processing summaries.
-   **`detector.py`**: Responsible for anomaly detection logic. Needs logging for detection results.
-   **`report.py`**: Responsible for external API communication. Needs logging for API request/response details.
-   **`main.py`**: Entry point. Needs high-level flow logging and error handling.

## Technical Decisions
-   **Logging Strategy**: Use standard `print()` statements as requested by the user for simplicity and immediate feedback in the console/logs.
-   **Z-API Integration**: Replace all legacy references to SMTP/Email with Z-API configuration.

## Changes

### Modify the `README.md` file
**Description:** Update project documentation to reflect current architecture and configuration.
**Technical patterns:** Markdown documentation standards.
**Use as reference the file:** `README.md`

### Modify the `db.py` file
**Description:** Add print statements to log Supabase connection and query results.
**Example:** `print(f"[db] Fetched {len(df)} rows from Supabase")`
**Technical patterns:** Observability logging.
**Use as reference the file:** `anomaly_detector/db.py`

### Modify the `metrics.py` file
**Description:** Add print statements to log data processing summaries.
**Example:** `print(f"[metrics] Processed {volume_total} unique calls")`
**Technical patterns:** Observability logging.
**Use as reference the file:** `anomaly_detector/metrics.py`

### Modify the `detector.py` file
**Description:** Add print statements to log detection progress and results.
**Example:** `print(f"[detector] Found {len(anomalias)} anomalies")`
**Technical patterns:** Observability logging.
**Use as reference the file:** `anomaly_detector/detector.py`

### Modify the `report.py` file
**Description:** Add print statements to log Z-API request details and responses.
**Example:** `print(f"[report] Sending message to {phone}... Status: {response.status_code}")`
**Technical patterns:** Observability logging.
**Use as reference the file:** `anomaly_detector/report.py`

### Modify the `main.py` file
**Description:** Add high-level flow tracking and error handling prints.
**Example:** `print("=== Starting Anomaly Detector ===")`
**Technical patterns:** Observability logging.
**Use as reference the file:** `anomaly_detector/main.py`
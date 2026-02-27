# Technical Specification: Anomaly Detector Production Readiness

## Architecture Overview
The system is a Python-based anomaly detector that queries a Supabase database, calculates metrics, detects anomalies based on historical data, and sends reports via WhatsApp (Z-API). It is designed to run as a scheduled batch job.

## Technical Stack
- **Language:** Python 3.x
- **Database:** Supabase (PostgreSQL)
- **Libraries:** pandas, numpy, supabase, requests, python-dotenv
- **Scheduling:** Cron (Linux) / Task Scheduler (Windows)

## Component Design
- **Ingestion (`db.py`):** Fetches data from Supabase.
- **Processing (`metrics.py`):** Aggregates raw data into metrics.
- **Analysis (`detector.py`):** Implements detection logic (Z-score, Percentiles).
- **Reporting (`report.py`):** Formats and sends alerts.
- **Orchestration (`main.py`):** Controls the execution flow.

## Technical Decisions
- **Scheduling:** The script does not contain an internal scheduler loop. It relies on an external scheduler (Cron) to run at specific times (20:00).
- **Environment:** Configuration is managed via `.env` files.
- **Logging:** Standard output (print) is used for logging, which should be redirected to a file in production.

## Changes

### Modify the README.md file
    **Description:** Update the Cron schedule example to run at 20:00 instead of 07:00.
    **Example:** `0 20 * * * /usr/bin/python3 ...`
    **Technical patterns:** Documentation update.
    **Use as reference the file:** anomaly_detector/README.md

### Create run.sh script
    **Description:** Create a shell script to simplify execution and environment setup in production.
    **Example:**
    ```bash
    #!/bin/bash
    cd /path/to/app
    source venv/bin/activate
    python main.py
    ```
    **Technical patterns:** Shell scripting for automation.
    **Use as reference the file:** N/A

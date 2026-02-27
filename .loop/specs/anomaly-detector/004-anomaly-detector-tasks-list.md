# Task List: Anomaly Detector Fixes & Improvements

## Phase 1: Setup & Inspection
- [x] **Inspect Database Schema**
    -   Run `inspect_db.py` to get the current schema.
    -   Compare with `metrics.py` and `db.py` usage.
    -   Update `AGENT.md` (or create it) with the confirmed schema.
- [x] **Validate Environment**
    -   Check `.env` file for all required keys defined in `config.py`.
    -   Verify Supabase and Z-API credentials.

## Phase 2: Code Fixes
- [x] **Fix `db.py`**
    -   Add error handling for Supabase connection.
    -   Ensure correct timestamp parsing for `created_at`.
- [x] **Fix `metrics.py`**
    -   Add column validation before access.
    -   Handle `NaN` and `None` values in numeric columns.
    -   Ensure `duration` and `combined_cost` are numeric.
    -   Handle schema mapping (`Duracao`, `Marcada`, `Numero`).
    -   Include `agent_name` in aggregation.
- [x] **Fix `detector.py`**
    -   Handle division by zero in Z-score calculation.
    -   Ensure robust handling of empty historical data.
- [x] **Fix `main.py`**
    -   Ensure proper exception handling and logging.

## Phase 3: Reporting Improvements
- [x] **Update `report.py`**
    -   Consolidate all anomalies into a single message.
    -   Use `agent_name` in the agent summary section.

## Phase 4: Testing & Documentation
- [x] **Run Pipeline**
    -   Execute `main.py` and monitor logs.
    -   Verify WhatsApp message delivery (single message).
- [x] **Update Documentation**
    -   Update `README.md` with current architecture and usage.
    -   Ensure `requirements.txt` is up to date.
# Task List: Observability and Documentation Update

## Documentation
- [ ] **Update README.md**: Rewrite `README.md` to replace Email/SMTP references with Z-API/WhatsApp, update architecture description, and refine configuration instructions.

## Observability Implementation
- [ ] **Add logging to `db.py`**: Insert print statements to log Supabase connection success and the number of rows fetched for both 24h and historical queries.
- [ ] **Add logging to `metrics.py`**: Insert print statements to log the summary of calculated metrics (e.g., total volume, unique numbers).
- [ ] **Add logging to `detector.py`**: Insert print statements to log the start of detection and the number/type of anomalies found.
- [ ] **Add logging to `report.py`**: Insert print statements to log Z-API request attempts, payload summaries, and response status codes.
- [ ] **Add logging to `main.py`**: Insert print statements for overall execution flow (start/end) and global error catching.

## Verification
- [ ] **Manual Test**: Run `main.py` and verify console output contains all added logs.
# Implementation Plan: Anomaly Detector Production Readiness

## Goal
Ensure the `anomaly_detector` is configured to run daily at 20:00 and is ready for a production environment.

## Milestones
1.  **Documentation Update:** Correct the scheduling instructions in README.md.
2.  **Execution Helper:** Create a `run.sh` script for easier cron integration.
3.  **Verification:** Verify requirements and configuration.

## Detailed Steps
1.  **Update README.md:**
    -   Change the cron example from `0 7 * * *` to `0 20 * * *`.
    -   Ensure installation instructions are clear.
2.  **Create `run.sh`:**
    -   Write a script that handles directory navigation and python execution.
    -   Make it executable.
3.  **Review Code:**
    -   Check `main.py` for any hardcoded time dependencies (none found, relies on `JANELA_HORAS`).
    -   Ensure `requirements.txt` is up to date.

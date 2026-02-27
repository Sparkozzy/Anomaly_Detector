# Technical Specification: Anomaly Detector

## Architecture Overview
The system follows a linear pipeline architecture:
1.  **Ingestion (`db.py`)**: Fetches raw call data from Supabase.
2.  **Processing (`metrics.py`)**: Aggregates data into metrics (volume, cost, disconnections). Now includes `agent_name` in agent statistics.
3.  **Analysis (`detector.py`)**: Compares current metrics against historical baselines using statistical methods (Z-score, percentiles).
4.  **Reporting (`report.py`)**: Formats anomalies and sends alerts via WhatsApp (Z-API). **Updated to send a single consolidated message.**
5.  **Orchestration (`main.py`)**: Manages the execution flow and error handling.

## Technical Stack
-   **Language**: Python 3.x
-   **Database**: Supabase (PostgreSQL)
-   **Libraries**: `pandas`, `numpy`, `supabase`, `requests`, `python-dotenv`
-   **External API**: Z-API (WhatsApp)

## Component Design
-   **`db.py`**: Handles Supabase connection and data retrieval. Converts timestamps to UTC. Includes error handling.
-   **`metrics.py`**: Calculates daily and current metrics. Handles data cleaning, type conversion, and schema mapping (`Duracao` -> `duration`, `Marcada` -> `marcada`, `Numero` -> `to_number`). Aggregates by `agent_id` and `agent_name`.
-   **`detector.py`**: Implements anomaly detection logic (Z-score, percentiles, thresholds). Handles NaN values.
-   **`report.py`**: Formats messages and handles Z-API communication. Sends a single message with all anomalies and agent summaries (using agent names).
-   **`config.py`**: Centralizes configuration and environment variables. Includes V2 thresholds.

## Data Model
-   **Input**: `Retell_calls_Mindflow` table in Supabase.
-   **Key Columns**: `created_at`, `call_id`, `to_number` (or `Numero`), `combined_cost`, `disconnection_reason`, `duration` (or `Duracao`), `marcada` (or `Marcada`), `agent_id`, `agent_name`.

## API Endpoints (if applicable)
-   **Z-API**: `POST /send-text` for sending WhatsApp messages.

## Technical Decisions
-   **Pandas for Data Processing**: Efficient handling of time-series data and aggregations.
-   **Z-score for Anomaly Detection**: Robust statistical method for identifying outliers in normal distributions.
-   **Environment Variables**: Secure storage of credentials and configuration.
-   **Single Message Report**: To reduce notification noise, all anomalies are consolidated into one WhatsApp message.

## Testing Strategy
-   **Unit Tests**: Test individual functions in `metrics.py` and `detector.py`.
-   **Integration Tests**: Verify DB connection and API communication (mocked).
-   **Manual Testing**: Run `main.py` and verify output logs and WhatsApp messages.

## Performance Considerations
-   **Data Fetching**: Fetch only necessary columns and time ranges to minimize latency.
-   **Memory Usage**: Process data in chunks if volume increases significantly.

## Security Considerations
-   **Credentials**: Store sensitive data in `.env` file, not in code.
-   **API Keys**: Rotate keys periodically.

## Changes

### Modify the `db.py` module
    **Description:** Add error handling for connection failures and empty data returns. Ensure `created_at` is correctly parsed.
    **Status:** Completed.

### Modify the `metrics.py` module
    **Description:** Validate DataFrame columns before access. Handle missing or null values gracefully. Map schema discrepancies. Include `agent_name`.
    **Status:** Completed.

### Modify the `detector.py` module
    **Description:** Ensure Z-score calculation handles division by zero (zero standard deviation).
    **Status:** Completed.

### Modify the `report.py` module
    **Description:** Consolidate messages into one. Use `agent_name` in summaries.
    **Status:** Completed.
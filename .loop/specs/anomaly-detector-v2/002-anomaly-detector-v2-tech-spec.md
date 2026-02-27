# Technical Specification: Anomaly Detector V2

## Architecture Overview
The system follows a linear pipeline architecture: Ingestion -> Processing -> Analysis -> Reporting. The V2 update introduces new metric calculations and anomaly detection logic within the existing `metrics.py` and `detector.py` modules, and expands `report.py` to include agent performance summaries.

## Technical Stack
- **Language:** Python 3.10+
- **Database:** Supabase (PostgreSQL)
- **Libraries:** Pandas, Numpy, python-dotenv, requests
- **Messaging:** Z-API (WhatsApp)

## Component Design
1.  **Config (`config.py`)**: Centralized configuration for new thresholds (short calls, concentration limits).
2.  **Metrics (`metrics.py`)**: Enhanced to calculate conversion rates, short call counts, call concentration, and agent performance stats.
3.  **Detector (`detector.py`)**: New detection functions for conversion drops (Z-score), short call spikes (Z-score), and concentration breaches (Threshold).
4.  **Report (`report.py`)**: New formatting logic for agent performance summaries.

## Data Model
- **Input:** `Retell_calls_Mindflow_rows` table from Supabase.
- **New Fields Used:** `agent_id`, `duration`, `marcada` (boolean/string), `to_number`, `created_at`.

## Technical Decisions
- **Rolling Window for Concentration:** Use Pandas `rolling` on a time-indexed DataFrame to efficiently calculate call concentration per number.
- **Agent Stats:** Aggregated daily for active agents (last 24h) to provide a snapshot of performance.
- **Z-Score for Conversion:** Use Z-score to detect significant drops in conversion rate compared to historical daily averages.

## Changes

### Modify the `config.py` file
**Description:** Add configuration variables for new thresholds.
**Example:**
```python
THRESHOLD_DURACAO_CURTA_SEC = _get("THRESHOLD_DURACAO_CURTA_SEC", "5", cast=int)
THRESHOLD_CONCENTRACAO_QTD = _get("THRESHOLD_CONCENTRACAO_QTD", "50", cast=int)
THRESHOLD_CONCENTRACAO_MINUTOS = _get("THRESHOLD_CONCENTRACAO_MINUTOS", "5", cast=int)
ZSCORE_MARCADA = 2.0
```
**Technical patterns:** Use existing `_get` helper.
**Use as reference the file:** `anomaly_detector/config.py`

### Modify the `metrics.py` file
**Description:** Implement calculations for new metrics and agent stats.
**Example:**
```python
def metricas_atual(df):
    # ... existing ...
    # Conversion Rate
    marcada_count = df[df["marcada"] == True].shape[0]
    taxa_marcada = marcada_count / volume_total if volume_total > 0 else 0
    
    # Short Calls
    short_calls = df[df["duration"] < config.THRESHOLD_DURACAO_CURTA_SEC].shape[0]
    
    # Concentration
    # ... rolling window logic ...
    
    # Agent Stats
    agent_stats = df.groupby("agent_id").agg(
        total_calls=("call_id", "nunique"),
        leads=("to_number", "nunique"),
        calls_over_1min=("duration", lambda x: (x > 60).sum()),
        meetings=("marcada", "sum")
    )
    return { ..., "agent_stats": agent_stats }
```
**Technical patterns:** Pandas `groupby` and `agg`.
**Use as reference the file:** `anomaly_detector/metrics.py`

### Modify the `detector.py` file
**Description:** Add detection logic for new anomalies.
**Example:**
```python
def detectar_queda_marcada(atual, historico):
    # Z-score logic for 'taxa_marcada'
    pass
```
**Technical patterns:** Reuse `_zscore`.
**Use as reference the file:** `anomaly_detector/detector.py`

### Modify the `report.py` file
**Description:** Format agent stats for WhatsApp.
**Example:**
```python
def _montar_resumo_agentes(stats):
    # Format string
    pass
```
**Technical patterns:** String formatting.
**Use as reference the file:** `anomaly_detector/report.py`
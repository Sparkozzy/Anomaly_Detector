# =============================================================================
# config.py — Lê todas as configurações do arquivo .env
# =============================================================================

import os
from dotenv import load_dotenv

load_dotenv()

def _get(key: str, default=None, cast=None):
    val = os.getenv(key, default)
    if val is None:
        raise EnvironmentError(f"Variável de ambiente obrigatória não definida: {key}")
    return cast(val) if cast else val

# --- Supabase ---
SUPABASE_URL  = _get("SUPABASE_URL")
SUPABASE_KEY  = _get("SUPABASE_KEY")
TABLE_NAME    = _get("TABLE_NAME", "Retell_calls_Mindflow")

# --- Z-API (WhatsApp) ---
ZAPI_INSTANCE     = _get("ZAPI_INSTANCE")
ZAPI_TOKEN        = _get("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = _get("ZAPI_CLIENT_TOKEN")
ZAPI_PHONE        = _get("ZAPI_PHONE")
ZAPI_DELAY_TYPING = _get("ZAPI_DELAY_TYPING", "3", cast=int)

# --- Janela de análise ---
HISTORICO_DIAS = _get("HISTORICO_DIAS", "30", cast=int)
JANELA_HORAS   = _get("JANELA_HORAS",   "24", cast=int)

# --- Thresholds de detecção ---
ZSCORE_VOLUME_TOTAL        = 2.0
ZSCORE_CUSTO_POR_NUMERO    = 2.5
ZSCORE_LIGACOES_POR_NUMERO = 2.0
PERCENTIL_EXCESSO_NUMERO   = 95
VARIACAO_DISCONNECTION_PCT = 50
MIN_LIGACOES_HISTORICO     = 4

# --- Novos Thresholds (V2) ---
THRESHOLD_DURACAO_CURTA_SEC    = _get("THRESHOLD_DURACAO_CURTA_SEC", "5", cast=int)
THRESHOLD_CONCENTRACAO_QTD     = _get("THRESHOLD_CONCENTRACAO_QTD", "50", cast=int)
THRESHOLD_CONCENTRACAO_MINUTOS = _get("THRESHOLD_CONCENTRACAO_MINUTOS", "5", cast=int)
ZSCORE_MARCADA                 = 2.0
ZSCORE_CURTAS                  = 2.0

# =============================================================================
# db.py — Consultas ao Supabase
# =============================================================================

from supabase import create_client, Client
from datetime import datetime, timedelta, timezone
import pandas as pd
import config


def get_client() -> Client:
    print(f"[db] Conectando ao Supabase: {config.SUPABASE_URL}")
    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)


def _to_df(data: list) -> pd.DataFrame:
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    return df


def fetch_ultimas_24h(client: Client) -> pd.DataFrame:
    """Retorna eventos das últimas 24 horas."""
    since = (datetime.now(timezone.utc) - timedelta(hours=config.JANELA_HORAS)).isoformat()
    print(f"[db] Buscando registros das últimas {config.JANELA_HORAS}h (desde {since})...")
    try:
        response = (
            client.table(config.TABLE_NAME)
            .select("*")
            .gte("created_at", since)
            .execute()
        )
        df = _to_df(response.data)
        print(f"[db] Últimas 24h: {len(df)} registros encontrados.")
        return df
    except Exception as e:
        print(f"[db] ERRO ao buscar últimas 24h: {e}")
        return pd.DataFrame()


def fetch_historico(client: Client) -> pd.DataFrame:
    """Retorna eventos dos últimos N dias (excluindo as últimas 24h)."""
    agora = datetime.now(timezone.utc)
    fim   = agora - timedelta(hours=config.JANELA_HORAS)
    inicio = agora - timedelta(days=config.HISTORICO_DIAS)

    print(f"[db] Buscando histórico de {config.HISTORICO_DIAS} dias ({inicio.isoformat()} até {fim.isoformat()})...")
    try:
        response = (
            client.table(config.TABLE_NAME)
            .select("*")
            .gte("created_at", inicio.isoformat())
            .lt("created_at", fim.isoformat())
            .execute()
        )
        df = _to_df(response.data)
        print(f"[db] Histórico ({config.HISTORICO_DIAS}d): {len(df)} registros encontrados.")
        return df
    except Exception as e:
        print(f"[db] ERRO ao buscar histórico: {e}")
        return pd.DataFrame()

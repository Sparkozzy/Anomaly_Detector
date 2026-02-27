# =============================================================================
# metrics.py — Cálculo de métricas agregadas
# =============================================================================

import pandas as pd
import numpy as np
from datetime import timezone
import config


def _safe_date(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # Normalização de colunas (Schema Mapping)
    # Prioriza 'Numero' se 'to_number' estiver vazio ou ausente, para evitar duplicidade
    if "Numero" in df.columns:
        if "to_number" in df.columns:
            # Coalesce: usa to_number, se nulo usa Numero
            df["to_number"] = df["to_number"].fillna(df["Numero"])
            df = df.drop(columns=["Numero"])
        else:
            df = df.rename(columns={"Numero": "to_number"})

    rename_map = {
        "Duracao": "duration",
        "Marcada": "marcada"
    }
    df = df.rename(columns=rename_map)

    # Conversão de tipos
    if "combined_cost" in df.columns:
        df["combined_cost"] = pd.to_numeric(df["combined_cost"], errors="coerce").fillna(0.0)
    
    if "duration" in df.columns:
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce").fillna(0.0)

    df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    df["date"] = df["created_at"].dt.tz_convert("America/Sao_Paulo").dt.date
    return df


# ---------------------------------------------------------------------------
# Métricas do período atual (últimas 24h)
# ---------------------------------------------------------------------------

def metricas_atual(df: pd.DataFrame) -> dict:
    """Agrega métricas do período atual."""
    print("[metrics] Calculando métricas do período atual...")
    if df.empty:
        print("[metrics] DataFrame vazio. Nenhuma métrica calculada.")
        return {}

    df = _safe_date(df)

    # Filtra apenas ligações reais (com call_id)
    calls = df.dropna(subset=["call_id"]).drop_duplicates(subset=["call_id"])

    # Volume total de ligações únicas
    volume_total = calls["call_id"].nunique()

    # Custo por número de telefone
    calls["combined_cost"] = pd.to_numeric(calls["combined_cost"], errors="coerce").fillna(0)
    custo_por_numero = (
        calls.groupby("to_number")["combined_cost"]
        .sum()
        .reset_index()
        .rename(columns={"combined_cost": "custo_total"})
    )

    # Ligações por número de telefone
    ligacoes_por_numero = (
        calls.groupby("to_number")["call_id"]
        .nunique()
        .reset_index()
        .rename(columns={"call_id": "n_ligacoes"})
    )

    # Distribuição de disconnection_reason
    disc = df["disconnection_reason"].dropna()
    disc_counts = disc.value_counts().to_dict()

    # --- Novas Métricas (V2) ---

    # 1. Taxa de Conversão (Marcada = True)
    if "marcada" in calls.columns:
        # Garante booleano
        calls["marcada_bool"] = calls["marcada"].astype(str).str.lower() == "true"
        marcada_count = calls["marcada_bool"].sum()
        taxa_marcada  = marcada_count / volume_total if volume_total > 0 else 0.0
    else:
        marcada_count = 0
        taxa_marcada  = 0.0

    # 2. Ligações Curtas (< X segundos)
    if "duration" in calls.columns:
        calls["duration"] = pd.to_numeric(calls["duration"], errors="coerce").fillna(0)
        short_calls_count = calls[calls["duration"] < config.THRESHOLD_DURACAO_CURTA_SEC].shape[0]
    else:
        short_calls_count = 0

    # 3. Concentração de Ligações (Janela deslizante)
    # Verifica se algum número recebeu muitas ligações em curto intervalo
    concentracao_anomala = []
    if not calls.empty:
        # Ordena por tempo para o rolling funcionar
        calls_sorted = calls.sort_values("created_at")
        
        for numero, grupo in calls_sorted.groupby("to_number"):
            if len(grupo) < config.THRESHOLD_CONCENTRACAO_QTD:
                continue
            
            # Rolling count na janela de tempo definida
            # 'on' deve ser datetime e estar ordenado
            indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=config.THRESHOLD_CONCENTRACAO_QTD)
            # Como rolling com tempo é complexo no pandas antigo/variável, 
            # vamos usar uma abordagem mais simples: contar quantos eventos em X min
            
            # Rolling count com offset de tempo requer index datetime
            grupo_idx = grupo.set_index("created_at").sort_index()
            
            # Conta quantas chamadas ocorreram nos últimos X minutos para cada registro
            # 'min_periods=1' garante que conte pelo menos a própria chamada
            counts = grupo_idx.rolling(f"{config.THRESHOLD_CONCENTRACAO_MINUTOS}min").count()["call_id"]
            
            max_count = counts.max()
            if max_count >= config.THRESHOLD_CONCENTRACAO_QTD:
                concentracao_anomala.append({
                    "numero": numero,
                    "max_count": int(max_count),
                    "limite": config.THRESHOLD_CONCENTRACAO_QTD,
                    "janela_min": config.THRESHOLD_CONCENTRACAO_MINUTOS
                })

    # 4. Resumo de Agentes (Performance)
    agent_stats = pd.DataFrame()
    if "agent_id" in calls.columns:
        # Garante colunas numéricas
        calls["duration"] = pd.to_numeric(calls["duration"], errors="coerce").fillna(0)
        if "marcada_bool" not in calls.columns:
             calls["marcada_bool"] = False

        # Agrupa por ID e Nome (se existir)
        group_cols = ["agent_id"]
        if "agent_name" in calls.columns:
            # Preenche nomes vazios para evitar perda no groupby
            calls["agent_name"] = calls["agent_name"].fillna("Desconhecido")
            group_cols.append("agent_name")

        agent_stats = calls.groupby(group_cols).agg(
            total_calls=("call_id", "nunique"),
            leads=("to_number", "nunique"),
            calls_over_1min=("duration", lambda x: (x > 60).sum()),
            meetings=("marcada_bool", "sum")
        ).reset_index()

    print(f"[metrics] Atual: {volume_total} chamadas, {marcada_count} marcadas, {short_calls_count} curtas.")
    
    return {
        "volume_total": volume_total,
        "custo_por_numero": custo_por_numero,
        "ligacoes_por_numero": ligacoes_por_numero,
        "disconnection_counts": disc_counts,
        # V2
        "taxa_marcada": taxa_marcada,
        "short_calls_count": short_calls_count,
        "concentracao_anomala": concentracao_anomala,
        "agent_stats": agent_stats
    }


# ---------------------------------------------------------------------------
# Métricas históricas (agregadas por dia para z-score)
# ---------------------------------------------------------------------------

def metricas_historico(df: pd.DataFrame) -> dict:
    """Agrega métricas históricas agrupadas por dia."""
    print("[metrics] Calculando métricas históricas...")
    if df.empty:
        print("[metrics] DataFrame histórico vazio.")
        return {}

    df = _safe_date(df)
    calls = df.dropna(subset=["call_id"]).drop_duplicates(subset=["call_id"])
    calls["combined_cost"] = pd.to_numeric(calls["combined_cost"], errors="coerce").fillna(0)

    # Volume total por dia
    volume_por_dia = (
        calls.groupby("date")["call_id"]
        .nunique()
        .reset_index()
        .rename(columns={"call_id": "n_ligacoes"})
    )

    # Custo por número por dia
    custo_por_numero_dia = (
        calls.groupby(["date", "to_number"])["combined_cost"]
        .sum()
        .reset_index()
    )

    # Ligações por número por dia
    ligacoes_por_numero_dia = (
        calls.groupby(["date", "to_number"])["call_id"]
        .nunique()
        .reset_index()
        .rename(columns={"call_id": "n_ligacoes"})
    )

    # Disconnection reason por dia
    disc_por_dia = (
        df.dropna(subset=["disconnection_reason"])
        .groupby(["date", "disconnection_reason"])
        .size()
        .reset_index(name="count")
    )

    # --- Novas Métricas Históricas (V2) ---
    
    # Taxa de Marcada por dia
    if "marcada" in calls.columns:
        calls["marcada_bool"] = calls["marcada"].astype(str).str.lower() == "true"
        marcada_por_dia = (
            calls.groupby("date")
            .agg(
                total=("call_id", "nunique"),
                marcadas=("marcada_bool", "sum")
            )
            .reset_index()
        )
        marcada_por_dia["taxa"] = marcada_por_dia["marcadas"] / marcada_por_dia["total"]
    else:
        marcada_por_dia = pd.DataFrame()

    # Ligações curtas por dia
    if "duration" in calls.columns:
        calls["duration"] = pd.to_numeric(calls["duration"], errors="coerce").fillna(0)
        curtas_por_dia = (
            calls[calls["duration"] < config.THRESHOLD_DURACAO_CURTA_SEC]
            .groupby("date")["call_id"]
            .nunique()
            .reset_index(name="count")
        )
        # Garante que dias sem curtas apareçam como 0 (merge com volume_por_dia se necessário, 
        # mas para z-score simples, dias com 0 podem ser omitidos ou tratados no detector)
    else:
        curtas_por_dia = pd.DataFrame()

    print(f"[metrics] Histórico processado: {len(volume_por_dia)} dias de dados.")
    return {
        "volume_por_dia": volume_por_dia,
        "custo_por_numero_dia": custo_por_numero_dia,
        "ligacoes_por_numero_dia": ligacoes_por_numero_dia,
        "disc_por_dia": disc_por_dia,
        # V2
        "marcada_por_dia": marcada_por_dia,
        "curtas_por_dia": curtas_por_dia
    }

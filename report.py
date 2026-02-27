# =============================================================================
# report.py — Montagem e envio do relatório via WhatsApp (Z-API)
# =============================================================================

import requests
from datetime import datetime, timezone
import pandas as pd
import config


def _url() -> str:
    return (
        f"https://api.z-api.io/instances/{config.ZAPI_INSTANCE}"
        f"/token/{config.ZAPI_TOKEN}/send-text"
    )


def _headers() -> dict:
    return {"Client-Token": config.ZAPI_CLIENT_TOKEN}


def _enviar_mensagem(texto: str) -> None:
    """Envia uma mensagem de texto via Z-API."""
    url = _url()
    print(f"[report] Enviando mensagem para {config.ZAPI_PHONE} via {url}...")
    
    payload = {
        "phone": config.ZAPI_PHONE,
        "message": texto,
        "delayTyping": config.ZAPI_DELAY_TYPING,
    }
    
    try:
        resp = requests.post(url, json=payload, headers=_headers())
        print(f"[report] Status Code: {resp.status_code}")
        resp.raise_for_status()
        print("[report] Mensagem enviada com sucesso.")
    except requests.exceptions.RequestException as e:
        print(f"[report] ERRO ao enviar mensagem: {e}")
        if 'resp' in locals() and resp is not None:
            print(f"[report] Resposta da API: {resp.text}")
        raise


# ---------------------------------------------------------------------------
# Formatação das mensagens
# ---------------------------------------------------------------------------

def _bloco_anomalia(a: dict) -> str:
    icons = {"🔴 CRÍTICO": "🔴", "🟡 ATENÇÃO": "🟡", "🟢 NORMAL": "🟢"}
    icon = icons.get(a["severidade"], "⚪")
    return (
        f"{icon} *{a['tipo']}*\n"
        f"   {a['descricao']}\n"
        f"   Atual: {a['valor_atual']} | Esperado: {a['valor_esperado']}"
    )


def _bloco_agente(row: pd.Series) -> str:
    # Usa o nome do agente se disponível, senão o ID
    nome = row.get("agent_name", row["agent_id"])
    return (
        f"👤 *{nome}*\n"
        f"- Número total de ligações: {row['total_calls']}\n"
        f"- Total de leads: {row['leads']}\n"
        f"- Ligações com mais de 1 minuto: {row['calls_over_1min']}\n"
        f"* Reuniões marcadas: {row['meetings']}"
    )


def montar_mensagem_unica(anomalias: list, periodo: str, agent_stats: pd.DataFrame = None) -> str:
    """
    Retorna uma única mensagem consolidada com todo o relatório.
    """
    agora = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")
    total    = len(anomalias)
    criticos = sum(1 for a in anomalias if "CRÍTICO" in a["severidade"])
    atencoes = sum(1 for a in anomalias if "ATENÇÃO" in a["severidade"])

    partes = []

    # --- Cabeçalho ---
    if total == 0:
        cabecalho = (
            f"🔍 *Relatório de Anomalias — Mindflow Calls*\n"
            f"📅 {agora}\n\n"
            f"✅ Nenhuma anomalia detectada. Tudo dentro do padrão!"
        )
    else:
        cabecalho = (
            f"🔍 *Relatório de Anomalias — Mindflow Calls*\n"
            f"📅 {agora}\n\n"
            f"⚠️ *{total} anomalia(s) detectada(s)*\n"
            f"🔴 {criticos} crítico(s)  |  🟡 {atencoes} atenção\n"
            f"──────────────────────"
        )
    partes.append(cabecalho)

    # --- Blocos de anomalias ---
    if total > 0:
        for a in anomalias:
            partes.append(_bloco_anomalia(a))

    # --- Resumo de Agentes ---
    if agent_stats is not None and not agent_stats.empty:
        partes.append("──────────────────────")
        partes.append("📊 *Resumo diário de Agentes*")
        
        for _, row in agent_stats.iterrows():
            partes.append(_bloco_agente(row))

    # --- Rodapé ---
    rodape = (
        f"──────────────────────\n"
        f"📊 Período: {periodo}\n"
        f"⚙️ Thresholds: Z>{config.ZSCORE_VOLUME_TOTAL} volume | "
        f"Z>{config.ZSCORE_CUSTO_POR_NUMERO} custo | "
        f"+{config.VARIACAO_DISCONNECTION_PCT}% disconnection"
    )
    partes.append(rodape)

    return "\n\n".join(partes)


def enviar_whatsapp(anomalias: list, periodo: str, agent_stats: pd.DataFrame = None) -> None:
    mensagem = montar_mensagem_unica(anomalias, periodo, agent_stats)
    _enviar_mensagem(mensagem)
    print(f"[report] WhatsApp enviado para {config.ZAPI_PHONE} | {len(anomalias)} anomalia(s)")

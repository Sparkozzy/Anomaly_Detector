# =============================================================================
# detector.py — Lógica de detecção de anomalias
# =============================================================================

import pandas as pd
import numpy as np
import config

Anomalia = dict  # {tipo, severidade, descricao, valor_atual, valor_esperado}


def _zscore(valor: float, serie: pd.Series) -> float:
    """Calcula z-score de um valor em relação a uma série histórica."""
    if len(serie) < config.MIN_LIGACOES_HISTORICO:
        return 0.0
    std = serie.std()
    if pd.isna(std) or std == 0:
        return 0.0
    return (valor - serie.mean()) / std


def _severidade(z: float) -> str:
    az = abs(z)
    if az >= 3:
        return "🔴 CRÍTICO"
    elif az >= 2:
        return "🟡 ATENÇÃO"
    return "🟢 NORMAL"


# ---------------------------------------------------------------------------
# 1. Volume total de ligações
# ---------------------------------------------------------------------------

def detectar_volume_total(atual: dict, historico: dict) -> list[Anomalia]:
    anomalias = []
    vol_atual = atual.get("volume_total", 0)
    hist_vol  = historico.get("volume_por_dia", pd.DataFrame())

    if hist_vol.empty:
        return anomalias

    z = _zscore(vol_atual, hist_vol["n_ligacoes"])
    sev = _severidade(z)

    if abs(z) >= config.ZSCORE_VOLUME_TOTAL:
        direcao = "acima" if z > 0 else "abaixo"
        anomalias.append({
            "tipo": "Volume Total de Ligações",
            "severidade": sev,
            "descricao": f"Volume {direcao} do esperado (Z={z:.2f})",
            "valor_atual": f"{vol_atual} ligações",
            "valor_esperado": f"~{hist_vol['n_ligacoes'].mean():.0f} ligações/dia (histórico)",
        })
    return anomalias


# ---------------------------------------------------------------------------
# 2. Custo por número de telefone
# ---------------------------------------------------------------------------

def detectar_custo_por_numero(atual: dict, historico: dict) -> list[Anomalia]:
    anomalias = []
    custo_atual = atual.get("custo_por_numero", pd.DataFrame())
    hist_custo  = historico.get("custo_por_numero_dia", pd.DataFrame())

    if custo_atual.empty or hist_custo.empty:
        return anomalias

    for _, row in custo_atual.iterrows():
        numero = row["to_number"]
        custo  = row["custo_total"]

        serie_hist = hist_custo[hist_custo["to_number"] == numero]["combined_cost"]
        if len(serie_hist) < config.MIN_LIGACOES_HISTORICO:
            continue

        z = _zscore(custo, serie_hist)
        if z >= config.ZSCORE_CUSTO_POR_NUMERO:
            anomalias.append({
                "tipo": "Custo por Número",
                "severidade": _severidade(z),
                "descricao": f"Custo elevado para {numero} (Z={z:.2f})",
                "valor_atual": f"R$ {custo:.4f}",
                "valor_esperado": f"~R$ {serie_hist.mean():.4f}/dia (histórico)",
            })
    return anomalias


# ---------------------------------------------------------------------------
# 3. Ligações excessivas por número (percentil 95)
# ---------------------------------------------------------------------------

def detectar_ligacoes_excessivas(atual: dict, historico: dict) -> list[Anomalia]:
    anomalias = []
    lig_atual = atual.get("ligacoes_por_numero", pd.DataFrame())
    hist_lig  = historico.get("ligacoes_por_numero_dia", pd.DataFrame())

    if lig_atual.empty or hist_lig.empty:
        return anomalias

    for _, row in lig_atual.iterrows():
        numero  = row["to_number"]
        n_atual = row["n_ligacoes"]

        serie_hist = hist_lig[hist_lig["to_number"] == numero]["n_ligacoes"]
        if len(serie_hist) < config.MIN_LIGACOES_HISTORICO:
            continue

        p95 = np.percentile(serie_hist, config.PERCENTIL_EXCESSO_NUMERO)
        if n_atual > p95:
            z = _zscore(n_atual, serie_hist)
            anomalias.append({
                "tipo": "Ligações Excessivas por Número",
                "severidade": _severidade(z),
                "descricao": f"Volume excessivo para {numero} (acima do P95 histórico)",
                "valor_atual": f"{n_atual} ligações",
                "valor_esperado": f"P95 histórico: {p95:.0f} ligações/dia",
            })
    return anomalias


# ---------------------------------------------------------------------------
# 4. Ligações por número abaixo ou acima da média (z-score bidirecional)
# ---------------------------------------------------------------------------

def detectar_volume_por_numero(atual: dict, historico: dict) -> list[Anomalia]:
    anomalias = []
    lig_atual = atual.get("ligacoes_por_numero", pd.DataFrame())
    hist_lig  = historico.get("ligacoes_por_numero_dia", pd.DataFrame())

    if lig_atual.empty or hist_lig.empty:
        return anomalias

    for _, row in lig_atual.iterrows():
        numero  = row["to_number"]
        n_atual = row["n_ligacoes"]

        serie_hist = hist_lig[hist_lig["to_number"] == numero]["n_ligacoes"]
        if len(serie_hist) < config.MIN_LIGACOES_HISTORICO:
            continue

        z = _zscore(n_atual, serie_hist)
        if abs(z) >= config.ZSCORE_LIGACOES_POR_NUMERO:
            direcao = "acima" if z > 0 else "abaixo"
            anomalias.append({
                "tipo": "Volume por Número (Bidirecional)",
                "severidade": _severidade(z),
                "descricao": f"{numero} com volume {direcao} da média (Z={z:.2f})",
                "valor_atual": f"{n_atual} ligações",
                "valor_esperado": f"~{serie_hist.mean():.1f} ligações/dia (histórico)",
            })
    return anomalias


# ---------------------------------------------------------------------------
# 5. Spike em disconnection_reason
# ---------------------------------------------------------------------------

def detectar_spike_disconnection(atual: dict, historico: dict) -> list[Anomalia]:
    anomalias = []
    disc_atual = atual.get("disconnection_counts", {})
    hist_disc  = historico.get("disc_por_dia", pd.DataFrame())

    if not disc_atual or hist_disc.empty:
        return anomalias

    for reason, count_atual in disc_atual.items():
        serie_hist = hist_disc[hist_disc["disconnection_reason"] == reason]["count"]
        if len(serie_hist) < config.MIN_LIGACOES_HISTORICO:
            continue

        media_hist = serie_hist.mean()
        if media_hist == 0:
            continue

        variacao_pct = ((count_atual - media_hist) / media_hist) * 100

        if variacao_pct >= config.VARIACAO_DISCONNECTION_PCT:
            z = _zscore(count_atual, serie_hist)
            anomalias.append({
                "tipo": "Spike em Disconnection Reason",
                "severidade": _severidade(z),
                "descricao": f"Aumento de {variacao_pct:.0f}% em '{reason}'",
                "valor_atual": f"{count_atual} ocorrências",
                "valor_esperado": f"~{media_hist:.1f}/dia (histórico)",
            })
    return anomalias


# ---------------------------------------------------------------------------
# 6. Queda na taxa de conversão (Marcada = True)
# ---------------------------------------------------------------------------

def detectar_queda_marcada(atual: dict, historico: dict) -> list[Anomalia]:
    anomalias = []
    taxa_atual = atual.get("taxa_marcada", 0.0)
    hist_marc  = historico.get("marcada_por_dia", pd.DataFrame())

    if hist_marc.empty:
        return anomalias

    # Z-score da taxa
    z = _zscore(taxa_atual, hist_marc["taxa"])
    
    # Detecta apenas queda (z negativo)
    if z <= -config.ZSCORE_MARCADA:
        anomalias.append({
            "tipo": "Queda na Conversão (Marcada=True)",
            "severidade": _severidade(z),
            "descricao": f"Taxa de agendamento abaixo do esperado (Z={z:.2f})",
            "valor_atual": f"{taxa_atual:.1%}",
            "valor_esperado": f"~{hist_marc['taxa'].mean():.1%} (histórico)",
        })
    return anomalias


# ---------------------------------------------------------------------------
# 7. Aumento de ligações curtas
# ---------------------------------------------------------------------------

def detectar_aumento_curtas(atual: dict, historico: dict) -> list[Anomalia]:
    anomalias = []
    curtas_atual = atual.get("short_calls_count", 0)
    hist_curtas  = historico.get("curtas_por_dia", pd.DataFrame())

    if hist_curtas.empty:
        return anomalias

    z = _zscore(curtas_atual, hist_curtas["count"])
    
    # Detecta apenas aumento (z positivo)
    if z >= config.ZSCORE_CURTAS:
        anomalias.append({
            "tipo": "Aumento de Ligações Curtas",
            "severidade": _severidade(z),
            "descricao": f"Volume de chamadas < {config.THRESHOLD_DURACAO_CURTA_SEC}s acima do normal (Z={z:.2f})",
            "valor_atual": f"{curtas_atual} chamadas",
            "valor_esperado": f"~{hist_curtas['count'].mean():.1f}/dia (histórico)",
        })
    return anomalias


# ---------------------------------------------------------------------------
# 8. Concentração excessiva de ligações
# ---------------------------------------------------------------------------

def detectar_concentracao(atual: dict) -> list[Anomalia]:
    anomalias = []
    concentracoes = atual.get("concentracao_anomala", [])

    for item in concentracoes:
        anomalias.append({
            "tipo": "Concentração Excessiva de Ligações",
            "severidade": "🔴 CRÍTICO",  # Sempre crítico se passar do threshold hardcoded
            "descricao": f"Número {item['numero']} recebeu {item['max_count']} chamadas em {item['janela_min']} min",
            "valor_atual": f"{item['max_count']} chamadas",
            "valor_esperado": f"Máximo {item['limite']} em {item['janela_min']} min",
        })
    return anomalias


# ---------------------------------------------------------------------------
# Runner principal
# ---------------------------------------------------------------------------

def detectar_todas(atual: dict, historico: dict) -> list[Anomalia]:
    """Executa todos os detectores e retorna lista consolidada de anomalias."""
    print("[detector] Iniciando detecção de anomalias...")
    anomalias = []
    
    a1 = detectar_volume_total(atual, historico)
    if a1: print(f"[detector] Volume Total: {len(a1)} anomalia(s)")
    anomalias += a1

    a2 = detectar_custo_por_numero(atual, historico)
    if a2: print(f"[detector] Custo por Número: {len(a2)} anomalia(s)")
    anomalias += a2

    a3 = detectar_ligacoes_excessivas(atual, historico)
    if a3: print(f"[detector] Ligações Excessivas: {len(a3)} anomalia(s)")
    anomalias += a3

    a4 = detectar_volume_por_numero(atual, historico)
    if a4: print(f"[detector] Volume por Número: {len(a4)} anomalia(s)")
    anomalias += a4

    a5 = detectar_spike_disconnection(atual, historico)
    if a5: print(f"[detector] Spike Disconnection: {len(a5)} anomalia(s)")
    anomalias += a5

    # --- Novos Detectores (V2) ---
    a6 = detectar_queda_marcada(atual, historico)
    if a6: print(f"[detector] Queda Conversão: {len(a6)} anomalia(s)")
    anomalias += a6

    a7 = detectar_aumento_curtas(atual, historico)
    if a7: print(f"[detector] Aumento Curtas: {len(a7)} anomalia(s)")
    anomalias += a7

    a8 = detectar_concentracao(atual)
    if a8: print(f"[detector] Concentração: {len(a8)} anomalia(s)")
    anomalias += a8

    # Ordena: crítico primeiro
    ordem = {"🔴 CRÍTICO": 0, "🟡 ATENÇÃO": 1, "🟢 NORMAL": 2}
    anomalias.sort(key=lambda x: ordem.get(x["severidade"], 9))

    print(f"[detector] Total de anomalias encontradas: {len(anomalias)}")
    return anomalias

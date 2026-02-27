# =============================================================================
# main.py — Orquestrador principal
# =============================================================================

import db
import metrics
import detector
import report
import config
from datetime import datetime


def main():
    print("\n=== INICIANDO DETECTOR DE ANOMALIAS ===")
    print(f"Data/Hora: {datetime.now()}")
    
    try:
        # 1. Conexão e Coleta
        print("\n--- ETAPA 1: COLETA DE DADOS ---")
        client = db.get_client()
        df_atual = db.fetch_ultimas_24h(client)
        df_hist  = db.fetch_historico(client)

        if df_atual.empty:
            print("[main] AVISO: Sem dados nas últimas 24h. Encerrando execução.")
            return

        # 2. Métricas
        print("\n--- ETAPA 2: CÁLCULO DE MÉTRICAS ---")
        metricas_atual = metrics.metricas_atual(df_atual)
        metricas_hist  = metrics.metricas_historico(df_hist)

        # 3. Detecção
        print("\n--- ETAPA 3: DETECÇÃO DE ANOMALIAS ---")
        anomalias = detector.detectar_todas(metricas_atual, metricas_hist)

        # 4. Report
        print("\n--- ETAPA 4: ENVIO DE RELATÓRIO ---")
        periodo = f"Últimas {config.JANELA_HORAS}h"
        agent_stats = metricas_atual.get("agent_stats")
        report.enviar_whatsapp(anomalias, periodo, agent_stats)
        
        print("\n=== EXECUÇÃO CONCLUÍDA COM SUCESSO ===")
        
    except Exception as e:
        print(f"\n[main] ERRO CRÍTICO DURANTE A EXECUÇÃO: {e}")
        raise


if __name__ == "__main__":
    main()

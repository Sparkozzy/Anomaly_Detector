#!/bin/bash

# =============================================================================
# run.sh — Script de execução para o Anomaly Detector
# =============================================================================
# Este script garante que o ambiente virtual seja ativado e que o diretório
# de trabalho esteja correto antes de executar o script Python.
#
# Uso no Cron (exemplo para rodar às 20:00):
# 0 20 * * * /caminho/para/anomaly_detector/run.sh >> /var/log/anomaly_detector.log 2>&1
# =============================================================================

# Define o diretório onde o script está localizado
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Ativa o ambiente virtual (ajuste o caminho se necessário)
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
else
    echo "AVISO: Ambiente virtual não encontrado. Tentando usar python do sistema."
fi

# Executa o detector
python main.py

# 🔍 Anomaly Detector — Mindflow Calls

Detector de anomalias diário para a base de ligações do Supabase, com notificações via WhatsApp (Z-API).

---

## 📁 Estrutura e Fluxo de Dados

O sistema segue um pipeline linear de processamento:

1.  **Ingestão (`db.py`)**: Coleta dados brutos de ligações do Supabase.
2.  **Processamento (`metrics.py`)**: Agrega os dados em métricas (volume, custo, desconexões).
3.  **Análise (`detector.py`)**: Compara as métricas atuais com o histórico (Z-score, percentis).
4.  **Report (`report.py`)**: Formata as anomalias encontradas e envia alerta via WhatsApp.
5.  **Orquestração (`main.py`)**: Gerencia o fluxo e tratamento de erros.

```
anomaly_detector/
├── config.py        # ⚙️  Credenciais e thresholds
├── db.py            # Consultas ao Supabase
├── metrics.py       # Cálculo de métricas agregadas
├── detector.py      # Lógica de detecção (z-score, percentil, variação %)
├── report.py        # Envio de mensagens via Z-API (WhatsApp)
├── main.py          # Orquestrador principal
├── AGENT.md         # Documentação do Schema e Regras de Negócio
└── requirements.txt
```

---

## 🚀 Setup

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar credenciais
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# --- Supabase ---
SUPABASE_URL="https://SEU_PROJECT_ID.supabase.co"
SUPABASE_KEY="SUA_SERVICE_ROLE_KEY"
TABLE_NAME="Retell_calls_Mindflow"

# --- Z-API (WhatsApp) ---
ZAPI_INSTANCE="SUA_INSTANCIA_ID"
ZAPI_TOKEN="SEU_TOKEN_DA_INSTANCIA"
ZAPI_CLIENT_TOKEN="SEU_CLIENT_TOKEN"
ZAPI_PHONE="5511999999999"

# --- Configurações Opcionais ---
HISTORICO_DIAS=30
JANELA_HORAS=24

# --- Thresholds V2 ---
THRESHOLD_DURACAO_CURTA_SEC=5
THRESHOLD_CONCENTRACAO_QTD=50
THRESHOLD_CONCENTRACAO_MINUTOS=5
```

### 3. Testar manualmente
```bash
cd anomaly_detector
python main.py
```

### 4. Agendar com cron (Linux/Mac)
Para executar todo dia às 20:00:
```bash
0 20 * * * /usr/bin/python3 /caminho/para/anomaly_detector/main.py >> /var/log/anomaly_detector.log 2>&1
```

---

## 📊 Anomalias detectadas

| Métrica | Método | Threshold padrão |
|---|---|---|
| Volume total de ligações | Z-score diário | Z > 2.0 |
| Custo por número de telefone | Z-score por número | Z > 2.5 |
| Ligações excessivas por número | Percentil 95 histórico | > P95 |
| Volume por número (bidirecional) | Z-score bidirecional | \|Z\| > 2.0 |
| Spike em disconnection_reason | Variação percentual | > 50% |
| Queda na taxa de conversão | Z-score (apenas queda) | Z < -2.0 |
| Aumento de ligações curtas | Z-score (apenas aumento) | Z > 2.0 |
| Concentração excessiva | Janela deslizante | > 50 chamadas em 5 min |

Todos os thresholds são configuráveis em `config.py`.

---

## 📱 Exemplo de Alerta (WhatsApp)

```text
🔍 Relatório de Anomalias — Mindflow Calls
📅 26/02/2026 18:30

⚠️ 2 anomalia(s) detectada(s)
🔴 1 crítico(s)  |  🟡 1 atenção
──────────────────────
🔴 CRÍTICO *Custo por Número*
   Custo elevado para +5511999999999 (Z=3.10)
   Atual: R$ 15.40 | Esperado: ~R$ 2.50/dia (histórico)

🟡 ATENÇÃO *Volume Total de Ligações*
   Volume abaixo do esperado (Z=-2.10)
   Atual: 120 ligações | Esperado: ~350 ligações/dia (histórico)

📊 *Resumo diário de Agentes*
👤 *Agente agent_123*
- Número total de ligações: 45
- Total de leads: 30
- Ligações com mais de 1 minuto: 12
* Reuniões marcadas: 3

👤 *Agente agent_456*
- Número total de ligações: 22
- Total de leads: 20
- Ligações com mais de 1 minuto: 5
* Reuniões marcadas: 0

──────────────────────
📊 Período: Últimas 24h
⚙️ Thresholds: Z>2.0 volume | Z>2.5 custo | +50% disconnection

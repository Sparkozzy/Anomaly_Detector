---
name: browser-use
description: Skill reutilizável para construção de detectores de anomalias em bases de dados Supabase.
Aplique esta skill em qualquer projeto que precise monitorar métricas diárias e alertar sobre comportamentos fora do padrão.

---
# 🧠 SKILL: supabase-anomaly-detector

## 📋 Quando usar esta skill

Use esta skill quando o projeto envolver:
- Monitoramento diário de tabelas no Supabase
- Detecção de anomalias estatísticas (z-score, percentil, variação %)
- Envio de alertas automáticos (WhatsApp, e-mail, Slack)
- Comparação de janela atual vs. histórico

---

## ⚡ Início rápido

```bash
# 1. Copie os scripts da skill para o projeto
cp skills/supabase-anomaly-detector/scripts/*.py seu_projeto/tools/

# 2. Instale dependências
pip install -r requirements.txt

# 3. Inspecione a tabela antes de qualquer coisa
python tools/inspect_db.py

# 4. Valide a conexão e o schema
python tools/validate_schema.py --required-cols created_at,id
```

---

## 🔒 REGRA #1 — Nunca alucie dados

**Antes de referenciar qualquer coluna em código novo, o agente DEVE:**

1. Rodar `python tools/inspect_db.py` para ver a estrutura real da tabela
2. Confirmar que a coluna existe e tem o tipo esperado
3. Verificar o % de nulos — colunas com > 80% de nulos precisam de tratamento especial
4. Checar valores únicos de colunas categóricas antes de filtrá-las

> ❌ Nunca escreva `df["coluna_x"]` sem ter confirmado que `coluna_x` existe na tabela real.
> ✅ Sempre rode `inspect_db.py` e consulte a seção `## Schema confirmado` do AGENT.md do projeto.

---

## 🖨️ REGRA #2 — Prints obrigatórios

Todo processo deve ser visível ao desenvolvedor. Use o padrão abaixo em **todo código novo**:

```python
print("[ETAPA] 🚀 Iniciando: <descrição>")       # início de bloco
print("[ETAPA] ⏳ Processando: <o que faz>")      # progresso
print(f"[ETAPA] 📊 <métrica>: <valor>")           # dado relevante
print("[ETAPA] ✅ Concluído: <descrição>")         # sucesso
print("[ETAPA] ⚠️  Aviso: <descrição>")            # inesperado mas não fatal
print("[ETAPA] ❌ Erro: <descrição>")              # falha
```

**Substitua `[ETAPA]` pelo nome do módulo:** `[DB]`, `[METRICS]`, `[DETECTOR]`, `[REPORT]`, `[AGENT]`

### Exemplo correto

```python
def calcular_taxa(df: pd.DataFrame, coluna: str) -> float:
    print(f"[METRICS] ⏳ Processando: calculando taxa de '{coluna}'...")

    if coluna not in df.columns:
        print(f"[METRICS] ❌ Erro: coluna '{coluna}' não encontrada no DataFrame")
        raise KeyError(f"Coluna '{coluna}' ausente")

    total = len(df)
    positivos = df[df[coluna] == True].shape[0]
    taxa = positivos / total if total > 0 else 0.0

    print(f"[METRICS] 📊 Taxa de '{coluna}': {taxa*100:.1f}% ({positivos}/{total})")
    print(f"[METRICS] ✅ Concluído: taxa calculada")
    return taxa
```

---

## 🏗️ Arquitetura recomendada

```
seu_projeto/
│
├── AGENT.md                # contexto específico do projeto (use template abaixo)
├── .env                    # credenciais reais (nunca commitar)
├── .env.example            # template de credenciais
├── .gitignore
├── requirements.txt
│
├── src/                    # código de produção
│   ├── config.py           # lê .env
│   ├── db.py               # queries ao Supabase
│   ├── metrics.py          # agregação de métricas
│   ├── detector.py         # lógica de detecção
│   ├── report.py           # envio de alertas
│   └── main.py             # orquestrador
│
└── tools/                  # utilitários de desenvolvimento
    ├── inspect_db.py       # inspeciona tabela real ← copiar da skill
    ├── validate_schema.py  # valida colunas obrigatórias ← copiar da skill
    └── test_alert.py       # testa envio de alerta ← copiar da skill
```

---

## 📐 Padrões de código

### config.py — sempre via .env com defaults

```python
import os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]       # obrigatório — sem default
SUPABASE_KEY = os.environ["SUPABASE_KEY"]       # obrigatório — sem default
TABLE_NAME   = os.getenv("TABLE_NAME", "minha_tabela")

# Thresholds com defaults sensatos
ZSCORE_THRESHOLD     = float(os.getenv("ZSCORE_THRESHOLD", "2.0"))
HISTORICO_DIAS       = int(os.getenv("HISTORICO_DIAS", "30"))
```

### db.py — sempre logar volume retornado

```python
def fetch_dados(client, since: str) -> pd.DataFrame:
    print(f"[DB] ⏳ Processando: buscando dados desde {since}...")
    response = client.table(TABLE_NAME).select("*").gte("created_at", since).execute()
    df = pd.DataFrame(response.data)
    print(f"[DB] 📊 Registros retornados: {len(df)}")
    if df.empty:
        print("[DB] ⚠️  Aviso: nenhum dado retornado para o período")
    return df
```

### detector.py — sempre logar anomalias encontradas

```python
def detectar(atual: dict, historico: dict) -> list:
    print("[DETECTOR] 🚀 Iniciando: detecção de anomalias...")
    anomalias = []

    # ... lógica de detecção ...

    print(f"[DETECTOR] 📊 Anomalias encontradas: {len(anomalias)}")
    for a in anomalias:
        print(f"[DETECTOR]    {a['severidade']} | {a['tipo']} | {a['descricao']}")
    print("[DETECTOR] ✅ Concluído: detecção finalizada")
    return anomalias
```

---

## 📊 Métodos de detecção disponíveis

### Z-score (desvio da média)
```python
def zscore(valor: float, serie: pd.Series, min_amostras: int = 5) -> float:
    if len(serie) < min_amostras:
        return 0.0
    std = serie.std()
    return 0.0 if std == 0 else (valor - serie.mean()) / std
```
**Use para:** volume de ligações, custo por número, taxas de conversão.
**Threshold:** `|Z| > 2.0` = atenção, `|Z| > 3.0` = crítico.

### Variação percentual (velocidade de mudança)
```python
def variacao_pct(atual: float, media_hist: float) -> float:
    return ((atual - media_hist) / media_hist * 100) if media_hist > 0 else 0.0
```
**Use para:** spikes em categorias (disconnection_reason), erros, eventos raros.
**Threshold:** `> 50%` de aumento = atenção.

### Percentil (valores extremos)
```python
import numpy as np
p95 = np.percentile(serie_historica, 95)
is_anomalia = valor_atual > p95
```
**Use para:** ligações excessivas por número, duração anormal.

### Janela deslizante (concentração temporal)
```python
df = df.set_index("created_at").sort_index()
rolling_count = df["call_id"].rolling("5min").count()
max_em_janela = rolling_count.max()
```
**Use para:** flood de ligações para um número, burst de erros.

---

## 🚫 Checklist — o que o agente nunca deve fazer

- [ ] Referenciar coluna sem confirmar via `inspect_db.py`
- [ ] Assumir valores de colunas categóricas sem checar
- [ ] Escrever código sem prints de progresso
- [ ] Deixar exceções silenciosas (`except: pass`)
- [ ] Modificar `.env` com credenciais reais
- [ ] Fazer `DELETE` ou `UPDATE` em massa sem confirmação explícita
- [ ] Remover prints de monitoramento existentes
- [ ] Adicionar dependência sem atualizar `requirements.txt`

---

## ✅ Checklist de entrega

Antes de considerar qualquer tarefa concluída:

```
[ ] Rodei inspect_db.py e confirmei todas as colunas usadas?
[ ] Todo código novo tem prints de início, progresso e conclusão?
[ ] Erros são tratados com try/except + print de erro?
[ ] requirements.txt atualizado com novas dependências?
[ ] .env não foi modificado nem exposto?
[ ] main.py roda sem erros com python main.py?
[ ] AGENT.md do projeto tem o schema atualizado?
```

---

## 📄 Template de AGENT.md para novos projetos

Ao iniciar um projeto com esta skill, crie um `AGENT.md` na raiz com este template:

```markdown
# AGENT.md — <Nome do Projeto>

## Skill base
supabase-anomaly-detector

## Contexto do projeto
<Descreva em 2-3 linhas o que este projeto monitora>

## Configurações específicas
- Tabela principal: <nome_da_tabela>
- Fuso horário: <America/Sao_Paulo>
- Canal de alerta: <WhatsApp / E-mail / Slack>
- Janela de análise: últimas <24>h vs. últimos <30> dias

## Schema confirmado
> Última validação: <data> — rode inspect_db.py para revalidar

| Coluna | Tipo | % Nulo | Observação |
|--------|------|--------|------------|
| id     | int  | 0%     | PK         |
| ...    | ...  | ...    | ...        |

## Regras de negócio específicas
- <ex: lead = número de telefone único>
- <ex: ligação válida = status = ended>
- <ex: horário comercial = 08h às 18h BRT>

## Thresholds ajustados
- ZSCORE_VOLUME_TOTAL: <2.0>
- CONCENTRACAO_MAX_POR_JANELA: <5>
```
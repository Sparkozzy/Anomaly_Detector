# =============================================================================
# tools/inspect_db.py
# Inspeciona a estrutura real da tabela no Supabase.
# RODE ANTES de qualquer alteração em métricas ou queries.
#
# Uso: python tools/inspect_db.py
# =============================================================================

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

TABLE = os.getenv("TABLE_NAME", "sua_tabela")

print("=" * 60)
print("[AGENT] 🚀 Iniciando: inspeção da tabela no Supabase")
print(f"[AGENT] 📋 Tabela alvo: {TABLE}")
print("=" * 60)

# ------------------------------------------------------------------
# Conexão
# ------------------------------------------------------------------
try:
    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    print("[AGENT] ✅ Conexão com Supabase estabelecida\n")
except KeyError as e:
    print(f"[AGENT] ❌ Variável de ambiente ausente: {e}")
    print("[AGENT] ❌ Certifique-se de que o .env está configurado corretamente")
    sys.exit(1)
except Exception as e:
    print(f"[AGENT] ❌ Erro ao conectar ao Supabase: {e}")
    sys.exit(1)

# ------------------------------------------------------------------
# 1. Estrutura de colunas
# ------------------------------------------------------------------
print("[AGENT] ⏳ Processando: buscando amostra de dados...")

try:
    response = client.table(TABLE).select("*").limit(5).execute()

    if not response.data:
        print("[AGENT] ❌ Nenhum dado retornado. Verifique o nome da tabela.")
        sys.exit(1)

    colunas = list(response.data[0].keys())
    print(f"[AGENT] ✅ Tabela encontrada | {len(colunas)} colunas | amostra: {len(response.data)} linhas\n")
    print(f"{'COLUNA':<30} {'TIPO':<12} {'EXEMPLO'}")
    print("-" * 75)
    for col in colunas:
        exemplo = response.data[0].get(col)
        tipo = type(exemplo).__name__ if exemplo is not None else "NoneType"
        exemplo_str = str(exemplo)
        if len(exemplo_str) > 45:
            exemplo_str = exemplo_str[:45] + "..."
        print(f"{col:<30} {tipo:<12} {exemplo_str}")

except Exception as e:
    print(f"[AGENT] ❌ Erro ao buscar estrutura: {e}")
    sys.exit(1)

# ------------------------------------------------------------------
# 2. Valores únicos de colunas categóricas
# ------------------------------------------------------------------
print("\n[AGENT] ⏳ Processando: valores únicos de colunas categóricas...")

# Tenta detectar automaticamente colunas com poucos valores únicos
try:
    res = client.table(TABLE).select("*").limit(200).execute()
    df_amostra = res.data

    for col in colunas:
        valores = [r[col] for r in df_amostra if r.get(col) is not None]
        if not valores:
            continue
        # Só mostra se for string e tiver <= 20 valores únicos
        if isinstance(valores[0], str):
            unicos = sorted(set(valores))
            if len(unicos) <= 20:
                print(f"[AGENT] 📊 '{col}' — {len(unicos)} valor(es): {unicos}")

except Exception as e:
    print(f"[AGENT] ⚠️  Erro ao checar categóricas: {e}")

# ------------------------------------------------------------------
# 3. % de nulos por coluna
# ------------------------------------------------------------------
print("\n[AGENT] ⏳ Processando: verificando nulos (amostra de 500 linhas)...")

try:
    res = client.table(TABLE).select("*").limit(500).execute()
    total = len(res.data)
    print(f"\n{'COLUNA':<30} {'NULOS':<8} {'% NULO':<10} {'ALERTA'}")
    print("-" * 60)
    for col in colunas:
        nulos = sum(1 for r in res.data if r.get(col) is None)
        pct = nulos / total * 100 if total > 0 else 0
        alerta = "⚠️  alto" if pct > 80 else ("⚠️  médio" if pct > 40 else "")
        print(f"{col:<30} {nulos:<8} {pct:<10.1f} {alerta}")

except Exception as e:
    print(f"[AGENT] ❌ Erro ao checar nulos: {e}")

# ------------------------------------------------------------------
# 4. Total de registros
# ------------------------------------------------------------------
print("\n[AGENT] ⏳ Processando: contando registros totais...")

try:
    res = client.table(TABLE).select("id", count="exact").execute()
    print(f"[AGENT] 📊 Total de registros na tabela: {res.count}")
except Exception as e:
    print(f"[AGENT] ⚠️  Não foi possível contar registros: {e}")

print("\n" + "=" * 60)
print("[AGENT] ✅ Inspeção concluída.")
print("[AGENT] 📌 Atualize a seção 'Schema confirmado' do AGENT.md com estes dados.")
print("=" * 60)
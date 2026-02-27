# =============================================================================
# tools/validate_schema.py
# Valida que colunas obrigatórias existem na tabela antes de rodar o projeto.
# Útil para rodar no início do main.py ou como check de CI.
#
# Uso:
#   python tools/validate_schema.py
#   python tools/validate_schema.py --cols created_at,id,status,call_id
# =============================================================================

import os
import sys
import argparse
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------------
# Argparse
# ------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Valida schema da tabela Supabase")
parser.add_argument(
    "--cols",
    type=str,
    default="",
    help="Colunas obrigatórias separadas por vírgula. Ex: created_at,id,status"
)
args = parser.parse_args()

REQUIRED_COLS = [c.strip() for c in args.cols.split(",") if c.strip()]
TABLE = os.getenv("TABLE_NAME", "sua_tabela")

print("=" * 60)
print("[VALIDATE] 🚀 Iniciando: validação de schema")
print(f"[VALIDATE] 📋 Tabela: {TABLE}")
if REQUIRED_COLS:
    print(f"[VALIDATE] 📋 Colunas obrigatórias: {REQUIRED_COLS}")
print("=" * 60)

# ------------------------------------------------------------------
# Conexão
# ------------------------------------------------------------------
try:
    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    print("[VALIDATE] ✅ Conexão estabelecida")
except KeyError as e:
    print(f"[VALIDATE] ❌ Variável de ambiente ausente: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[VALIDATE] ❌ Erro de conexão: {e}")
    sys.exit(1)

# ------------------------------------------------------------------
# Busca colunas reais
# ------------------------------------------------------------------
print("[VALIDATE] ⏳ Processando: buscando colunas da tabela...")

try:
    response = client.table(TABLE).select("*").limit(1).execute()
    if not response.data:
        print("[VALIDATE] ❌ Tabela vazia ou inexistente.")
        sys.exit(1)
    colunas_reais = set(response.data[0].keys())
    print(f"[VALIDATE] 📊 Colunas encontradas: {len(colunas_reais)}")
except Exception as e:
    print(f"[VALIDATE] ❌ Erro ao buscar tabela: {e}")
    sys.exit(1)

# ------------------------------------------------------------------
# Valida colunas obrigatórias
# ------------------------------------------------------------------
if REQUIRED_COLS:
    print("\n[VALIDATE] ⏳ Processando: checando colunas obrigatórias...")
    ausentes = [c for c in REQUIRED_COLS if c not in colunas_reais]

    if ausentes:
        print(f"\n[VALIDATE] ❌ Colunas obrigatórias AUSENTES na tabela:")
        for col in ausentes:
            print(f"           - {col}")
        print("\n[VALIDATE] ❌ Validação falhou. Corrija antes de continuar.")
        sys.exit(1)
    else:
        print(f"[VALIDATE] ✅ Todas as {len(REQUIRED_COLS)} colunas obrigatórias encontradas")
        for col in REQUIRED_COLS:
            print(f"           ✓ {col}")
else:
    print("\n[VALIDATE] ⚠️  Nenhuma coluna obrigatória especificada.")
    print("[VALIDATE]    Use --cols created_at,id,status para validar colunas específicas.")
    print(f"\n[VALIDATE] 📊 Colunas disponíveis: {sorted(colunas_reais)}")

print("\n" + "=" * 60)
print("[VALIDATE] ✅ Schema validado com sucesso.")
print("=" * 60)
sys.exit(0)
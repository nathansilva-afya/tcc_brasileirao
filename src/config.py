"""Caminhos e parâmetros centrais do projeto."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"              # camada bronze: dados como vieram da fonte
PROCESSED_DIR = DATA_DIR / "processed"  # camada silver: dados limpos e tipados
ANALYTICS_DIR = DATA_DIR / "analytics"  # camada gold: tabelas agregadas para análise
EXPORTS_DIR = DATA_DIR / "exports"      # cópias no formato do Excel pt-BR

# Fonte (Kaggle): só os arquivos que os notebooks 01_limpeza e 02_limpeza usam
KAGGLE_DATASET = "adaoduque/campeonato-brasileiro-de-futebol"
# nome da tabela -> arquivo do dataset (o bronze guarda com o mesmo nome do Kaggle)
KAGGLE_FILES = {
    "partidas": "campeonato-brasileiro-full.csv",
    "gols": "campeonato-brasileiro-gols.csv",
    "estatisticas": "campeonato-brasileiro-estatisticas-full.csv",
}

RAW = {nome: RAW_DIR / arquivo for nome, arquivo in KAGGLE_FILES.items()}
PROCESSED = {nome: PROCESSED_DIR / f"{nome}.csv" for nome in KAGGLE_FILES}
PARTIDAS = PROCESSED["partidas"]

TEMPORADA = 2025  # o projeto analisa apenas esta temporada

# Tabelas gold: as geradas pelos notebooks (src/analytics.py)
TABELAS_GOLD = ["bilheteria", "scout", "posse_bola"]

# Databricks (python -m src.publish): onde as tabelas gold são criadas no Unity Catalog.
# "workspace" é o catálogo padrão do Databricks Free Edition. Sem DATABRICKS_WAREHOUSE_ID,
# usa o primeiro SQL warehouse do workspace.
DATABRICKS_CATALOG = os.environ.get("DATABRICKS_CATALOG", "workspace")
DATABRICKS_SCHEMA = os.environ.get("DATABRICKS_SCHEMA", "brasileirao")
DATABRICKS_WAREHOUSE_ID = os.environ.get("DATABRICKS_WAREHOUSE_ID")

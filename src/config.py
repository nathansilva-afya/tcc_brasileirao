"""Caminhos e parâmetros centrais do projeto."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"              # camada bronze: dados como vieram da fonte
PROCESSED_DIR = DATA_DIR / "processed"  # camada silver: dados limpos e tipados
ANALYTICS_DIR = DATA_DIR / "analytics"  # camada gold: tabelas agregadas para análise
EXPORTS_DIR = DATA_DIR / "exports"      # cópias no formato do Excel pt-BR

# Fonte (Kaggle)
KAGGLE_DATASET = "adaoduque/campeonato-brasileiro-de-futebol"
# nome da tabela -> arquivo do dataset (o bronze guarda com o mesmo nome do Kaggle)
KAGGLE_FILES = {
    "partidas": "campeonato-brasileiro-full.csv",
    "gols": "campeonato-brasileiro-gols.csv",
    "cartoes": "campeonato-brasileiro-cartoes.csv",
    "estatisticas": "campeonato-brasileiro-estatisticas-full.csv",
}

RAW = {nome: RAW_DIR / arquivo for nome, arquivo in KAGGLE_FILES.items()}
PROCESSED = {nome: PROCESSED_DIR / f"{nome}.csv" for nome in KAGGLE_FILES}
PARTIDAS = PROCESSED["partidas"]

TEMPORADA = 2025  # o projeto analisa apenas esta temporada

PONTOS_VITORIA = 3
PONTOS_EMPATE = 1

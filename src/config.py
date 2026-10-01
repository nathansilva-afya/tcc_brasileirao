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
KAGGLE_FILE = "campeonato-brasileiro-full.csv"

RAW_PARTIDAS = RAW_DIR / "campeonato_brasileiro_de_futebol.csv"
PARTIDAS = PROCESSED_DIR / "partidas.csv"

TEMPORADA = 2025  # o projeto analisa apenas esta temporada

PONTOS_VITORIA = 3
PONTOS_EMPATE = 1

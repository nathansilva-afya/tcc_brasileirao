"""Baixa o dataset complementar da Série B 2023 (fora do pipeline principal).

Uso: python -m src.extras.download_serie_b
"""
import kagglehub
from kagglehub import KaggleDatasetAdapter

from src import config

df = kagglehub.dataset_load(
    KaggleDatasetAdapter.PANDAS,
    "profdavidsonsantana/campeonato-brasileiro-de-futebol-srie-b",
    "serie-b-2023.csv",
)
df.to_csv(config.RAW_DIR / "serie-b-2023.csv", index=False)
print(f"Salvo em {config.RAW_DIR / 'serie-b-2023.csv'} ({len(df)} linhas)")

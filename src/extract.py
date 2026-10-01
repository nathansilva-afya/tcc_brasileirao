"""Extração: baixa o dataset bruto do Kaggle para data/raw."""
from __future__ import annotations

import logging

from src import config

log = logging.getLogger(__name__)


def extrair(forcar: bool = False) -> None:
    """Baixa o CSV de partidas e guarda só a temporada configurada. Se o arquivo já existe, não baixa de novo (a menos que forcar=True)."""
    if config.RAW_PARTIDAS.exists() and not forcar:
        log.info("Bruto já existe em %s (use --forcar-download para baixar de novo)", config.RAW_PARTIDAS)
        return

    import kagglehub
    from kagglehub import KaggleDatasetAdapter

    log.info("Baixando %s/%s do Kaggle", config.KAGGLE_DATASET, config.KAGGLE_FILE)
    df = kagglehub.dataset_load(KaggleDatasetAdapter.PANDAS, config.KAGGLE_DATASET, config.KAGGLE_FILE)
    # Mantém no bronze só os jogos de config.TEMPORADA (sem alterar os valores)
    df = df[df["data"].str.endswith(f"/{config.TEMPORADA}")]
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.RAW_PARTIDAS, index=False, encoding="utf-8")
    log.info("Bruto salvo em %s (%d linhas)", config.RAW_PARTIDAS, len(df))

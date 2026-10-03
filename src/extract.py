"""Extração: baixa os 4 CSVs do dataset do Kaggle para data/raw."""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src import config

log = logging.getLogger(__name__)


def _ler_fonte(caminho: Path) -> pd.DataFrame:
    # Tudo como texto e sem converter vazios em nulo: o bronze guarda os valores exatamente como vieram
    return pd.read_csv(caminho, dtype=str, keep_default_na=False, encoding="utf-8")


def filtrar_temporada(tabelas: dict) -> dict:
    """Mantém só os jogos de config.TEMPORADA. Gols, cartões e estatísticas são
    filtrados pelos IDs das partidas da temporada."""
    partidas = tabelas["partidas"]
    partidas = partidas[partidas["data"].str.endswith(f"/{config.TEMPORADA}")]
    ids = set(partidas["ID"])
    filtradas = {"partidas": partidas}
    for nome, df in tabelas.items():
        if nome != "partidas":
            filtradas[nome] = df[df["partida_id"].isin(ids)]
    return filtradas


def extrair(forcar: bool = False) -> None:
    """Baixa o dataset e grava os 4 arquivos (só a temporada configurada) em data/raw.
    Se todos já existem, não baixa de novo (a menos que forcar=True)."""
    if all(p.exists() for p in config.RAW.values()) and not forcar:
        log.info("Brutos já existem em %s (use --forcar-download para baixar de novo)",
                 config.RAW_DIR.relative_to(config.ROOT))
        return

    import kagglehub

    log.info("Baixando %s do Kaggle", config.KAGGLE_DATASET)
    pasta = Path(kagglehub.dataset_download(config.KAGGLE_DATASET, force_download=forcar))
    tabelas = {nome: _ler_fonte(pasta / arquivo) for nome, arquivo in config.KAGGLE_FILES.items()}

    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    for nome, df in filtrar_temporada(tabelas).items():
        df.to_csv(config.RAW[nome], index=False, encoding="utf-8")
        log.info("Bruto salvo em %s (%d linhas)", config.RAW[nome].relative_to(config.ROOT), len(df))
        if df.empty:
            log.warning("A fonte não tem dados de %s para a temporada %d", nome, config.TEMPORADA)

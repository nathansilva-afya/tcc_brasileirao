"""Carga: grava as camadas em disco."""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src import config

log = logging.getLogger(__name__)


def salvar(df: pd.DataFrame, caminho: Path) -> None:
    """Formato padrão (UTF-8, vírgula) para ser lido por Python/Power BI/etc."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False, encoding="utf-8", date_format="%Y-%m-%d")
    log.info("Salvo %s (%d linhas)", caminho.relative_to(config.ROOT), len(df))


def exportar_excel(df: pd.DataFrame, nome: str) -> None:
    """Cópia para abrir direto no Excel pt-BR: UTF-8 com BOM, ';' e decimal ','."""
    caminho = config.EXPORTS_DIR / f"{nome}.csv"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False, sep=";", decimal=",", encoding="utf-8-sig", date_format="%d/%m/%Y")

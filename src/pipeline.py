"""Orquestra o pipeline: extract -> transform -> validate -> analytics -> load.

Uso (na raiz do projeto):
    python -m src.pipeline
    python -m src.pipeline --forcar-download
    python -m src.pipeline --databricks   # também publica as tabelas gold no Databricks
"""
from __future__ import annotations

import argparse
import logging

from src import analytics, config, extract, load, transform, validate

log = logging.getLogger("pipeline")


def executar(forcar_download: bool = False, databricks: bool = False) -> None:
    extract.extrair(forcar=forcar_download)

    tabelas = transform.transformar_tudo(config.RAW)
    validate.validar_tudo(tabelas)
    for nome, df in tabelas.items():
        load.salvar(df, config.PROCESSED[nome])
        load.exportar_excel(df, nome)

    gold = analytics.construir(**tabelas)
    for nome, df in gold.items():
        load.salvar(df, config.ANALYTICS_DIR / f"{nome}.csv")
        load.exportar_excel(df, nome)

    if databricks:
        from src import publish
        publish.publicar(gold)

    log.info("Pipeline concluído")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--forcar-download", action="store_true", help="baixa o dataset do Kaggle mesmo se já existir")
    parser.add_argument("--databricks", action="store_true", help="publica as tabelas gold no Unity Catalog do Databricks")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S")
    executar(forcar_download=args.forcar_download, databricks=args.databricks)


if __name__ == "__main__":
    main()

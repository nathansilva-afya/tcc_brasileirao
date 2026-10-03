"""Orquestra o pipeline: extract -> transform -> validate -> analytics -> load.

Uso (na raiz do projeto):
    python -m src.pipeline
    python -m src.pipeline --forcar-download
"""
from __future__ import annotations

import argparse
import logging

from src import analytics, config, extract, load, transform, validate

log = logging.getLogger("pipeline")


def executar(forcar_download: bool = False) -> None:
    extract.extrair(forcar=forcar_download)

    tabelas = transform.transformar_tudo(config.RAW)
    validate.validar_tudo(tabelas)
    for nome, df in tabelas.items():
        load.salvar(df, config.PROCESSED[nome])
        load.exportar_excel(df, nome)

    for nome, df in analytics.construir(**tabelas).items():
        load.salvar(df, config.ANALYTICS_DIR / f"{nome}.csv")
        load.exportar_excel(df, nome)

    log.info("Pipeline concluído")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--forcar-download", action="store_true", help="baixa o dataset do Kaggle mesmo se já existir")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S")
    executar(forcar_download=args.forcar_download)


if __name__ == "__main__":
    main()

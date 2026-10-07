"""Publicação: grava as tabelas gold como tabelas Delta no Unity Catalog do Databricks.

Roda da máquina local e usa o SQL warehouse serverless do workspace (o único tipo de
compute do Databricks Free Edition). Autenticação pela configuração padrão do
databricks-sdk: variáveis DATABRICKS_HOST e DATABRICKS_TOKEN ou um perfil em
~/.databrickscfg (escolhido com DATABRICKS_CONFIG_PROFILE).

Uso (na raiz do projeto, depois de `python -m src.pipeline`):
    python -m src.publish
"""
from __future__ import annotations

import logging
import math
import time

import pandas as pd

from src import config

log = logging.getLogger(__name__)

LINHAS_POR_INSERT = 500


def _tipo_sql(s: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(s):
        return "BOOLEAN"
    if pd.api.types.is_integer_dtype(s):
        return "BIGINT"
    if pd.api.types.is_float_dtype(s):
        return "DOUBLE"
    if pd.api.types.is_datetime64_any_dtype(s):
        return "DATE" if (s.dropna() == s.dropna().dt.normalize()).all() else "TIMESTAMP"
    return "STRING"


def _literal(valor, tipo: str) -> str:
    if valor is None or valor is pd.NA or valor is pd.NaT or (isinstance(valor, float) and math.isnan(valor)):
        return "NULL"
    if tipo == "BOOLEAN":
        return "TRUE" if valor else "FALSE"
    if tipo == "BIGINT":
        return str(int(valor))
    if tipo == "DOUBLE":
        return repr(float(valor))
    if tipo == "DATE":
        return f"DATE'{valor:%Y-%m-%d}'"
    if tipo == "TIMESTAMP":
        return f"TIMESTAMP'{valor:%Y-%m-%d %H:%M:%S}'"
    texto = str(valor).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{texto}'"


def comandos_sql(df: pd.DataFrame, tabela: str) -> list:
    """CREATE OR REPLACE TABLE com os tipos do DataFrame + INSERTs em lotes."""
    tipos = {col: _tipo_sql(df[col]) for col in df.columns}
    colunas = ", ".join(f"`{col}` {tipo}" for col, tipo in tipos.items())
    comandos = [f"CREATE OR REPLACE TABLE {tabela} ({colunas})"]
    for inicio in range(0, len(df), LINHAS_POR_INSERT):
        lote = df.iloc[inicio:inicio + LINHAS_POR_INSERT]
        linhas = ",\n".join(
            "(" + ", ".join(_literal(v, tipos[col]) for col, v in zip(df.columns, linha)) + ")"
            for linha in lote.itertuples(index=False, name=None))
        comandos.append(f"INSERT INTO {tabela} VALUES\n{linhas}")
    return comandos


class Databricks:
    def __init__(self, warehouse_id: str | None = None):
        from databricks.sdk import WorkspaceClient

        self.w = WorkspaceClient()
        self.warehouse_id = warehouse_id or config.DATABRICKS_WAREHOUSE_ID or self._primeiro_warehouse()

    def _primeiro_warehouse(self) -> str:
        warehouses = list(self.w.warehouses.list())
        if not warehouses:
            raise RuntimeError("Nenhum SQL warehouse no workspace. Crie um em SQL > SQL Warehouses.")
        log.info("Usando o SQL warehouse '%s'", warehouses[0].name)
        return warehouses[0].id

    def executar(self, comando: str) -> None:
        from databricks.sdk.service.sql import ExecuteStatementRequestOnWaitTimeout, StatementState

        r = self.w.statement_execution.execute_statement(
            comando, self.warehouse_id, wait_timeout="50s",
            on_wait_timeout=ExecuteStatementRequestOnWaitTimeout.CONTINUE)
        # O warehouse serverless pode estar desligado e levar alguns segundos para subir
        while r.status.state in (StatementState.PENDING, StatementState.RUNNING):
            time.sleep(2)
            r = self.w.statement_execution.get_statement(r.statement_id)
        if r.status.state != StatementState.SUCCEEDED:
            erro = r.status.error.message if r.status.error else r.status.state
            raise RuntimeError(f"Falha no Databricks: {erro}\n{comando[:300]}")


def publicar(tabelas: dict, catalogo: str = config.DATABRICKS_CATALOG,
             schema: str = config.DATABRICKS_SCHEMA) -> None:
    """Cria (ou recria) cada DataFrame de {nome: DataFrame} como catalogo.schema.nome."""
    db = Databricks()
    # Só cria o schema se faltar: quem não tem CREATE SCHEMA pode usar um já criado pelo admin
    if f"{catalogo}.{schema}" not in {s.full_name for s in db.w.schemas.list(catalogo)}:
        db.executar(f"CREATE SCHEMA `{catalogo}`.`{schema}`")
    for nome, df in tabelas.items():
        tabela = f"`{catalogo}`.`{schema}`.`{nome}`"
        for comando in comandos_sql(df, tabela):
            db.executar(comando)
        log.info("Publicado %s.%s.%s (%d linhas)", catalogo, schema, nome, len(df))


def ler_analytics() -> dict:
    """Lê as tabelas gold já geradas em data/analytics."""
    tabelas = {}
    for caminho in sorted(config.ANALYTICS_DIR.glob("*.csv")):
        df = pd.read_csv(caminho)
        if "data" in df.columns:
            df["data"] = pd.to_datetime(df["data"])
        tabelas[caminho.stem] = df
    if not tabelas:
        raise FileNotFoundError("data/analytics está vazio: rode `python -m src.pipeline` antes")
    return tabelas


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S")
    publicar(ler_analytics())


if __name__ == "__main__":
    main()

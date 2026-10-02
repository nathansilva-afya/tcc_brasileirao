"""Transformação: bruto (raw) -> partidas limpas (processed)."""
from __future__ import annotations

import pandas as pd

from src.config import TEMPORADA

COLUNAS = {
    "ID": "id_partida",
    "rodata": "rodada",
    "data": "data",
    "hora": "hora",
    "mandante": "mandante",
    "visitante": "visitante",
    "formacao_mandante": "formacao_mandante",
    "formacao_visitante": "formacao_visitante",
    "tecnico_mandante": "tecnico_mandante",
    "tecnico_visitante": "tecnico_visitante",
    "vencedor": "vencedor",
    "arena": "arena",
    "mandante_Placar": "gols_mandante",
    "visitante_Placar": "gols_visitante",
    "mandante_Estado": "estado_mandante",
    "visitante_Estado": "estado_visitante",
    "arrecadacao": "arrecadacao",
}


def ler_bruto(caminho) -> pd.DataFrame:
    return pd.read_csv(caminho, encoding="utf-8")


def limpar_texto(df: pd.DataFrame) -> pd.DataFrame:
    """Remove espaço não separável (\\xa0) e espaços nas pontas; string vazia vira nulo."""
    df = df.copy()
    for col in df.columns[[pd.api.types.is_string_dtype(t) for t in df.dtypes]]:
        s = df[col].str.replace("\xa0", " ", regex=False).str.strip()
        df[col] = s.replace("", pd.NA)
    return df


def calcular_temporada(data: pd.Series) -> pd.Series:
    """Temporada do campeonato. Como o Brasileirão não começa em jan/fev, jogos nesses
    meses pertencem à temporada anterior (ex.: fev/2026 não conta como 2025)."""
    ano = data.dt.year
    return ano.where(data.dt.month > 2, ano - 1)


def resultado(gols_mandante: pd.Series, gols_visitante: pd.Series) -> pd.Series:
    """'M' (vitória mandante), 'E' (empate) ou 'V' (vitória visitante)."""
    r = pd.Series("E", index=gols_mandante.index)
    r[gols_mandante > gols_visitante] = "M"
    r[gols_mandante < gols_visitante] = "V"
    return r


def transformar(bruto: pd.DataFrame) -> pd.DataFrame:
    df = bruto.rename(columns=COLUNAS)[list(COLUNAS.values())]
    df = limpar_texto(df)

    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["temporada"] = calcular_temporada(df["data"])
    df = df[df["temporada"] == TEMPORADA].copy()
    df["vencedor"] = df["vencedor"].replace("-", pd.NA)
    df["resultado"] = resultado(df["gols_mandante"], df["gols_visitante"])
    df["total_gols"] = df["gols_mandante"] + df["gols_visitante"]

    ordem = ["id_partida", "temporada", "rodada", "data", "hora", "mandante", "visitante",
             "gols_mandante", "gols_visitante", "total_gols", "resultado", "vencedor",
             "estado_mandante", "estado_visitante", "arena", "formacao_mandante",
             "formacao_visitante", "tecnico_mandante", "tecnico_visitante", "arrecadacao"]
    return df[ordem].sort_values(["temporada", "rodada", "data", "id_partida"]).reset_index(drop=True)


def ler_partidas(caminho) -> pd.DataFrame:
    """Lê a camada processed já com os tipos corretos."""
    return pd.read_csv(caminho, parse_dates=["data"])

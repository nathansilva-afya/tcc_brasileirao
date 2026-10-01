"""Camada analítica (gold): tabelas agregadas da temporada 2025, prontas para o TCC."""
from __future__ import annotations

import pandas as pd

from src.config import PONTOS_EMPATE, PONTOS_VITORIA


def partidas_por_time(partidas: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por time por partida (formato longo), base para as demais tabelas."""
    base = ["id_partida", "temporada", "rodada", "data", "arena"]
    casa = partidas[base + ["mandante", "visitante", "gols_mandante", "gols_visitante"]].set_axis(
        base + ["time", "adversario", "gols_pro", "gols_contra"], axis=1).assign(mando="casa")
    fora = partidas[base + ["visitante", "mandante", "gols_visitante", "gols_mandante"]].set_axis(
        base + ["time", "adversario", "gols_pro", "gols_contra"], axis=1).assign(mando="fora")
    df = pd.concat([casa, fora], ignore_index=True)

    df["vitoria"] = (df["gols_pro"] > df["gols_contra"]).astype(int)
    df["empate"] = (df["gols_pro"] == df["gols_contra"]).astype(int)
    df["derrota"] = (df["gols_pro"] < df["gols_contra"]).astype(int)
    df["pontos"] = df["vitoria"] * PONTOS_VITORIA + df["empate"] * PONTOS_EMPATE
    return df.sort_values(["temporada", "rodada", "id_partida", "mando"]).reset_index(drop=True)


def _agregar(df: pd.DataFrame, chaves: list) -> pd.DataFrame:
    t = df.groupby(chaves, as_index=False).agg(
        jogos=("id_partida", "size"),
        vitorias=("vitoria", "sum"),
        empates=("empate", "sum"),
        derrotas=("derrota", "sum"),
        gols_pro=("gols_pro", "sum"),
        gols_contra=("gols_contra", "sum"),
        pontos=("pontos", "sum"),
    )
    t["saldo_gols"] = t["gols_pro"] - t["gols_contra"]
    t["aproveitamento"] = (t["pontos"] / (t["jogos"] * PONTOS_VITORIA)).round(4)
    return t


def classificacao(ppt: pd.DataFrame) -> pd.DataFrame:
    """Tabela final de cada temporada. Critérios: pontos, vitórias, saldo, gols pró.
    Obs.: não considera punições de pontos aplicadas fora de campo (ex.: STJD)."""
    t = _agregar(ppt, ["temporada", "time"])
    t = t.sort_values(["temporada", "pontos", "vitorias", "saldo_gols", "gols_pro"],
                      ascending=[True, False, False, False, False])
    t.insert(1, "posicao", t.groupby("temporada").cumcount() + 1)
    return t.reset_index(drop=True)


def desempenho_mando(ppt: pd.DataFrame) -> pd.DataFrame:
    """Desempenho de cada time em casa e fora, por temporada."""
    return _agregar(ppt, ["temporada", "time", "mando"])


def resumo_temporadas(partidas: pd.DataFrame, tabela: pd.DataFrame) -> pd.DataFrame:
    """Indicadores gerais por temporada (vantagem do mando, média de gols, campeão)."""
    r = partidas.groupby("temporada").agg(
        jogos=("id_partida", "size"),
        times=("mandante", "nunique"),
        gols=("total_gols", "sum"),
        media_gols=("total_gols", "mean"),
        pct_vitoria_mandante=("resultado", lambda s: (s == "M").mean()),
        pct_empate=("resultado", lambda s: (s == "E").mean()),
        pct_vitoria_visitante=("resultado", lambda s: (s == "V").mean()),
    )
    campeao = tabela[tabela["posicao"] == 1].set_index("temporada")[["time", "pontos"]]
    r = r.join(campeao.rename(columns={"time": "campeao", "pontos": "pontos_campeao"}))
    return r.round(4).reset_index()


def construir(partidas: pd.DataFrame) -> dict:
    """Gera todas as tabelas gold. Retorna {nome_arquivo: DataFrame}."""
    ppt = partidas_por_time(partidas)
    tabela = classificacao(ppt)
    return {
        "partidas_por_time": ppt,
        "classificacao": tabela,
        "desempenho_mando": desempenho_mando(ppt),
        "resumo_temporadas": resumo_temporadas(partidas, tabela),
    }

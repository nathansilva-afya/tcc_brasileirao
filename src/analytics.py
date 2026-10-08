"""Camada analítica (gold): as tabelas que os notebooks 01_limpeza e 02_limpeza geram."""
from __future__ import annotations

import pandas as pd


def bilheteria(partidas: pd.DataFrame, minimo_jogos: int = 3) -> pd.DataFrame:
    """Arrecadação por dia da semana e horário (arredondado a 15 min).
    Só jogos com renda informada contam; combinações com menos de `minimo_jogos` saem."""
    df = partidas.assign(
        dia_da_semana=pd.to_datetime(partidas["data"]).dt.day_name(),
        hora_oficial=pd.to_datetime(partidas["hora"], format="%H:%M").dt.round("15min").dt.strftime("%H:%M"),
    )
    t = df.groupby(["dia_da_semana", "hora_oficial"], as_index=False)["arrecadacao"].agg(
        qtd_jogos="count", media_arrecadacao="mean", total_arrecadacao="sum")
    t = t[t["qtd_jogos"] >= minimo_jogos].copy()
    t[["media_arrecadacao", "total_arrecadacao"]] = t[["media_arrecadacao", "total_arrecadacao"]].round(2)
    return t.reset_index(drop=True)


def scout(gols: pd.DataFrame, est: pd.DataFrame) -> pd.DataFrame:
    """Gols de cada atleta junto com a eficiência do clube (gols / chutes no alvo, em %).
    Como na fonte, gol contra conta para o clube beneficiado (com o atleta adversário)."""
    gols_clube = gols.groupby("clube").size().rename("gols_do_clube")
    chutes_clube = est.groupby("clube")["chutes_no_alvo"].sum().rename("chutes_alvo_clube")
    eficiencia = pd.concat([gols_clube, chutes_clube], axis=1, join="inner")
    eficiencia["eficiencia_clube_pct"] = (
        eficiencia["gols_do_clube"] / eficiencia["chutes_alvo_clube"] * 100).astype(float).round(2)

    g = gols.dropna(subset=["atleta"]).groupby(["atleta", "clube"]).size().reset_index(name="gols_do_jogador")
    return g.merge(eficiencia["eficiencia_clube_pct"].reset_index(), on="clube")


def posse_bola(partidas: pd.DataFrame, est: pd.DataFrame, minimo_jogos: int = 4) -> pd.DataFrame:
    """Taxa de vitória (%) para cada valor de posse de bola. Valores de posse que
    aparecem em menos de `minimo_jogos` jogos saem."""
    df = est.merge(partidas[["id_partida", "vencedor"]], on="id_partida")
    df["venceu"] = (df["clube"] == df["vencedor"]).fillna(False).astype(int)
    t = df.groupby("posse_de_bola", as_index=False)["venceu"].agg(total_jogos="count", taxa_vitoria_pct="mean")
    t["taxa_vitoria_pct"] = (t["taxa_vitoria_pct"] * 100).round(2)
    t = t[t["total_jogos"] >= minimo_jogos]
    return t.sort_values("posse_de_bola").reset_index(drop=True)


def construir(partidas: pd.DataFrame, gols: pd.DataFrame, estatisticas: pd.DataFrame) -> dict:
    """Gera as tabelas gold. Retorna {nome_arquivo: DataFrame}."""
    return {
        "bilheteria": bilheteria(partidas),
        "scout": scout(gols, estatisticas),
        "posse_bola": posse_bola(partidas, estatisticas),
    }

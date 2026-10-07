"""Camada analítica (gold): tabelas agregadas da temporada 2025, prontas para o TCC."""
from __future__ import annotations

from typing import Optional

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
    """Classificação final de 2025. Critérios: pontos, vitórias, saldo, gols pró.
    Obs.: não considera punições de pontos aplicadas fora de campo (ex.: STJD)."""
    t = _agregar(ppt, ["temporada", "time"])
    t = t.sort_values(["temporada", "pontos", "vitorias", "saldo_gols", "gols_pro"],
                      ascending=[True, False, False, False, False])
    t.insert(1, "posicao", t.groupby("temporada").cumcount() + 1)
    return t.reset_index(drop=True)


def desempenho_mando(ppt: pd.DataFrame) -> pd.DataFrame:
    """Desempenho de cada time em casa e fora."""
    return _agregar(ppt, ["temporada", "time", "mando"])


def resumo_temporada(partidas: pd.DataFrame, tabela: pd.DataFrame) -> pd.DataFrame:
    """Indicadores gerais da temporada 2025 (vantagem do mando, média de gols, campeão)."""
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


FAIXAS_MINUTO = [0, 15, 30, 45, 60, 75, 90]
ROTULOS_FAIXA = ["0-15", "16-30", "31-45+", "46-60", "61-75", "76-90+"]


def artilharia(gols: pd.DataFrame) -> pd.DataFrame:
    """Gols por atleta (gols contra ficam de fora, pois contam para o adversário)."""
    g = gols[gols["tipo_gol"] != "Gol contra"]
    a = g.groupby(["atleta", "clube"], as_index=False).agg(
        gols=("id_partida", "size"),
        penaltis=("tipo_gol", lambda s: (s == "Pênalti").sum()),
        jogos_com_gol=("id_partida", "nunique"),
    )
    a = a.sort_values(["gols", "penaltis", "atleta"], ascending=[False, True, True]).reset_index(drop=True)
    a.insert(0, "posicao", a["gols"].rank(method="min", ascending=False).astype(int))
    return a


def gols_por_minuto(gols: pd.DataFrame) -> pd.DataFrame:
    """Distribuição dos gols em faixas de 15 minutos (acréscimos entram na faixa final do tempo)."""
    faixa = pd.cut(gols["minuto"].astype(float), FAIXAS_MINUTO, labels=ROTULOS_FAIXA, include_lowest=True)
    t = (gols.assign(faixa=faixa)
             .groupby("faixa", observed=False)
             .agg(gols=("id_partida", "size"),
                  penaltis=("tipo_gol", lambda s: (s == "Pênalti").sum()),
                  gols_contra=("tipo_gol", lambda s: (s == "Gol contra").sum()))
             .reset_index())
    t["pct_gols"] = (t["gols"] / t["gols"].sum()).round(4)
    t["faixa"] = t["faixa"].astype(str)
    return t


def estatisticas_partida_time(ppt: pd.DataFrame, est: pd.DataFrame) -> pd.DataFrame:
    """Resultado de cada time em cada jogo junto com suas estatísticas (base para correlações)."""
    colunas = ["id_partida", "clube", "chutes", "chutes_no_alvo", "posse_de_bola", "passes",
               "precisao_passes", "faltas", "cartao_amarelo", "cartao_vermelho", "impedimentos", "escanteios"]
    df = ppt.merge(est[colunas].rename(columns={"clube": "time"}), on=["id_partida", "time"], how="left")
    df["conversao_chutes"] = (df["gols_pro"] / df["chutes"].where(df["chutes"] > 0)).astype(float).round(4)
    return df


def estatisticas_time(ept: pd.DataFrame) -> pd.DataFrame:
    """Médias por jogo e totais de disciplina de cada time na temporada."""
    t = ept.groupby(["temporada", "time"], as_index=False).agg(
        jogos=("id_partida", "size"),
        gols_pro=("gols_pro", "sum"),
        chutes=("chutes", "sum"),
        chutes_no_alvo=("chutes_no_alvo", "sum"),
        media_chutes=("chutes", "mean"),
        media_chutes_no_alvo=("chutes_no_alvo", "mean"),
        media_posse=("posse_de_bola", "mean"),
        media_passes=("passes", "mean"),
        media_precisao_passes=("precisao_passes", "mean"),
        media_escanteios=("escanteios", "mean"),
        media_impedimentos=("impedimentos", "mean"),
        faltas=("faltas", "sum"),
        cartoes_amarelos=("cartao_amarelo", "sum"),
        cartoes_vermelhos=("cartao_vermelho", "sum"),
    )
    t["pct_chutes_no_alvo"] = t["chutes_no_alvo"] / t["chutes"]
    t["conversao_chutes"] = t["gols_pro"] / t["chutes"]
    t["chutes_por_gol"] = t["chutes"] / t["gols_pro"].where(t["gols_pro"] > 0)
    totais = ["jogos", "gols_pro", "chutes", "chutes_no_alvo", "faltas", "cartoes_amarelos", "cartoes_vermelhos"]
    taxas = [c for c in t.columns if c not in totais + ["temporada", "time"]]
    t[totais] = t[totais].astype(int)
    t[taxas] = t[taxas].astype(float).round(4)
    return t.sort_values("media_posse", ascending=False).reset_index(drop=True)


def cartoes_por_atleta(cartoes: pd.DataFrame) -> pd.DataFrame:
    """Cartões individuais por atleta (vazio quando a fonte não tem cartões da temporada)."""
    return (cartoes.groupby(["atleta", "clube", "posicao"], as_index=False, dropna=False)
                   .agg(amarelos=("cartao", lambda s: (s == "Amarelo").sum()),
                        vermelhos=("cartao", lambda s: (s == "Vermelho").sum()))
                   .sort_values(["vermelhos", "amarelos"], ascending=False)
                   .reset_index(drop=True))


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


def construir(partidas: pd.DataFrame, gols: Optional[pd.DataFrame] = None,
              cartoes: Optional[pd.DataFrame] = None, estatisticas: Optional[pd.DataFrame] = None) -> dict:
    """Gera todas as tabelas gold. Retorna {nome_arquivo: DataFrame}."""
    ppt = partidas_por_time(partidas)
    tabela = classificacao(ppt)
    tabelas = {
        "partidas_por_time": ppt,
        "classificacao": tabela,
        "desempenho_mando": desempenho_mando(ppt),
        "resumo_temporada": resumo_temporada(partidas, tabela),
        "bilheteria": bilheteria(partidas),
    }
    if gols is not None:
        tabelas["artilharia"] = artilharia(gols)
        tabelas["gols_por_minuto"] = gols_por_minuto(gols)
    if estatisticas is not None:
        ept = estatisticas_partida_time(ppt, estatisticas)
        tabelas["estatisticas_partida_time"] = ept
        tabelas["estatisticas_time"] = estatisticas_time(ept)
        tabelas["posse_bola"] = posse_bola(partidas, estatisticas)
    if gols is not None and estatisticas is not None:
        tabelas["scout"] = scout(gols, estatisticas)
    if cartoes is not None:
        tabelas["cartoes_por_atleta"] = cartoes_por_atleta(cartoes)
    return tabelas

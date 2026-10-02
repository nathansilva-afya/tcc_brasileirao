"""Camada analítica (gold): tabelas agregadas da temporada 2025, prontas para o TCC."""
from __future__ import annotations

import pandas as pd

from src.config import PONTOS_EMPATE, PONTOS_VITORIA, REGIAO

MIN_JOGOS_FORMACAO = 20  # formações com menos jogos ficam de fora (amostra pequena)


def partidas_por_time(partidas: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por time por partida (formato longo), base para as demais tabelas."""
    base = ["id_partida", "temporada", "rodada", "data", "hora", "arena", "arrecadacao"]
    lado = ["time", "adversario", "gols_pro", "gols_contra", "formacao", "estado", "estado_adversario"]
    casa = partidas[base + ["mandante", "visitante", "gols_mandante", "gols_visitante",
                            "formacao_mandante", "estado_mandante", "estado_visitante"]].set_axis(
        base + lado, axis=1).assign(mando="casa")
    fora = partidas[base + ["visitante", "mandante", "gols_visitante", "gols_mandante",
                            "formacao_visitante", "estado_visitante", "estado_mandante"]].set_axis(
        base + lado, axis=1).assign(mando="fora")
    df = pd.concat([casa, fora], ignore_index=True)

    df["vitoria"] = (df["gols_pro"] > df["gols_contra"]).astype(int)
    df["empate"] = (df["gols_pro"] == df["gols_contra"]).astype(int)
    df["derrota"] = (df["gols_pro"] < df["gols_contra"]).astype(int)
    df["pontos"] = df["vitoria"] * PONTOS_VITORIA + df["empate"] * PONTOS_EMPATE
    df["turno"] = (df["rodada"] > 19).astype(int) + 1
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


def _pct_resultados(partidas: pd.DataFrame, chaves) -> pd.DataFrame:
    """Jogos, média de gols e % de vitória do mandante / empate / vitória do visitante."""
    return partidas.groupby(chaves, observed=True).agg(
        jogos=("id_partida", "size"),
        media_gols=("total_gols", "mean"),
        pct_vitoria_mandante=("resultado", lambda s: (s == "M").mean()),
        pct_empate=("resultado", lambda s: (s == "E").mean()),
        pct_vitoria_visitante=("resultado", lambda s: (s == "V").mean()),
    ).round(4).reset_index()


def spearman(x: pd.Series, y: pd.Series) -> float:
    """Correlação de Spearman (Pearson sobre os postos), sem depender do scipy."""
    return round(x.rank().corr(y.rank()), 4)


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


def diferenca_mando(mando: pd.DataFrame) -> pd.DataFrame:
    """Aproveitamento em casa x fora por time; diferenca > 0 = rende mais em casa."""
    t = mando.pivot(index="time", columns="mando", values=["aproveitamento", "pontos"])
    t.columns = [f"{a}_{m}" for a, m in t.columns]
    t[["pontos_casa", "pontos_fora"]] = t[["pontos_casa", "pontos_fora"]].fillna(0).astype(int)
    t["diferenca"] = (t["aproveitamento_casa"] - t["aproveitamento_fora"]).round(4)
    t["pct_pontos_casa"] = (t["pontos_casa"] / (t["pontos_casa"] + t["pontos_fora"])).round(4)
    return t.sort_values("diferenca", ascending=False).reset_index()


def resumo_temporada(partidas: pd.DataFrame, tabela: pd.DataFrame, ppt: pd.DataFrame) -> pd.DataFrame:
    """Indicadores gerais da temporada 2025 (vantagem do mando, média de gols, campeão).
    pct_pontos_casa segue Pollard (1986): pontos dos mandantes ÷ total de pontos."""
    r = _pct_resultados(partidas, "temporada").set_index("temporada")
    r.insert(1, "times", partidas.groupby("temporada")["mandante"].nunique())
    r.insert(2, "gols", partidas.groupby("temporada")["total_gols"].sum())
    pontos = ppt.groupby(["temporada", "mando"])["pontos"].sum().unstack()
    r["pct_pontos_casa"] = (pontos["casa"] / pontos.sum(axis=1)).round(4)
    campeao = tabela[tabela["posicao"] == 1].set_index("temporada")[["time", "pontos"]]
    r = r.join(campeao.rename(columns={"time": "campeao", "pontos": "pontos_campeao"}))
    return r.reset_index()


def evolucao_rodadas(ppt: pd.DataFrame) -> pd.DataFrame:
    """Pontos e posição acumulados de cada time ao fim de cada rodada."""
    df = ppt.sort_values(["time", "rodada"]).copy()
    g = df.groupby("time")
    df["pontos_acumulados"] = g["pontos"].cumsum()
    df["vitorias_acumuladas"] = g["vitoria"].cumsum()
    df["saldo_acumulado"] = (df["gols_pro"] - df["gols_contra"]).groupby(df["time"]).cumsum()
    df["gols_pro_acumulados"] = g["gols_pro"].cumsum()
    df = df.sort_values(["rodada", "pontos_acumulados", "vitorias_acumuladas",
                         "saldo_acumulado", "gols_pro_acumulados"],
                        ascending=[True, False, False, False, False])
    df["posicao"] = df.groupby("rodada").cumcount() + 1
    cols = ["rodada", "time", "pontos", "pontos_acumulados", "saldo_acumulado", "posicao"]
    return df[cols].reset_index(drop=True)


def desempenho_turno(ppt: pd.DataFrame, tabela: pd.DataFrame) -> pd.DataFrame:
    """Pontos e aproveitamento de cada time no 1º e no 2º turno."""
    t = _agregar(ppt, ["time", "turno"]).pivot(index="time", columns="turno",
                                                values=["pontos", "aproveitamento"])
    t.columns = [f"{a}_turno{n}" for a, n in t.columns]
    t[["pontos_turno1", "pontos_turno2"]] = t[["pontos_turno1", "pontos_turno2"]].fillna(0).astype(int)
    t["variacao_pontos"] = t["pontos_turno2"] - t["pontos_turno1"]
    t = t.join(tabela.set_index("time")["posicao"])
    return t.sort_values("posicao").reset_index()


def placares(partidas: pd.DataFrame) -> pd.DataFrame:
    """Frequência de cada placar (mandante x visitante)."""
    p = (partidas["gols_mandante"].astype(str) + "x" + partidas["gols_visitante"].astype(str))
    t = p.value_counts().rename_axis("placar").reset_index(name="jogos")
    t["pct"] = (t["jogos"] / len(partidas)).round(4)
    return t


def mando_distancia(partidas: pd.DataFrame) -> pd.DataFrame:
    """Resultados conforme a distância entre as sedes: mesmo estado, mesma região ou outra região."""
    reg_m = partidas["estado_mandante"].map(REGIAO)
    reg_v = partidas["estado_visitante"].map(REGIAO)
    categoria = pd.Series("outra regiao", index=partidas.index)
    categoria[reg_m == reg_v] = "mesma regiao"
    categoria[partidas["estado_mandante"] == partidas["estado_visitante"]] = "mesmo estado"
    ordem = pd.CategoricalDtype(["mesmo estado", "mesma regiao", "outra regiao"], ordered=True)
    return _pct_resultados(partidas.assign(distancia=categoria.astype(ordem)), "distancia")


def eficiencia_arrecadacao(ppt: pd.DataFrame, tabela: pd.DataFrame,
                           dif_mando: pd.DataFrame) -> pd.DataFrame:
    """Arrecadação como mandante x desempenho; pontos_por_milhao = pontos ÷ arrecadação (R$ mi)."""
    casa = ppt[ppt["mando"] == "casa"].groupby("time")["arrecadacao"].agg(
        arrecadacao_total="sum", arrecadacao_media="mean")
    t = casa.join(tabela.set_index("time")[["posicao", "pontos", "aproveitamento"]])
    t = t.join(dif_mando.set_index("time")["aproveitamento_casa"])
    t["pontos_por_milhao"] = (t["pontos"] / (t["arrecadacao_total"] / 1e6)).round(2)
    t["arrecadacao_media"] = t["arrecadacao_media"].round(2)
    return t.sort_values("arrecadacao_media", ascending=False).reset_index()


def arrecadacao_resultado(partidas: pd.DataFrame) -> pd.DataFrame:
    """Resultados dos jogos agrupados por quartil de arrecadação (Q1 = menores rendas)."""
    partidas = partidas.dropna(subset=["arrecadacao"])
    n = min(4, len(partidas))
    quartil = pd.qcut(partidas["arrecadacao"].rank(method="first"), n,
                      labels=[f"Q{i}" for i in range(1, n + 1)])
    t = _pct_resultados(partidas.assign(quartil=quartil), "quartil")
    faixa = partidas.groupby(quartil, observed=True)["arrecadacao"].agg(["min", "max"]).values
    t.insert(1, "arrecadacao_min", faixa[:, 0])
    t.insert(2, "arrecadacao_max", faixa[:, 1])
    return t


def formacoes(ppt: pd.DataFrame) -> pd.DataFrame:
    """Aproveitamento por esquema tático (só formações com MIN_JOGOS_FORMACAO ou mais jogos)."""
    t = _agregar(ppt, ["formacao"])
    t["pct_jogos"] = (t["jogos"] / len(ppt)).round(4)
    t = t[t["jogos"] >= MIN_JOGOS_FORMACAO]
    return t.sort_values("jogos", ascending=False).reset_index(drop=True)


def horario(partidas: pd.DataFrame) -> pd.DataFrame:
    """Resultados por faixa de horário do jogo."""
    hora = partidas["hora"].str[:2].astype(int)
    faixa = pd.cut(hora, [0, 17, 19, 24], right=False, labels=["antes das 17h", "17h-18h", "19h ou mais"])
    return _pct_resultados(partidas.assign(faixa_horario=faixa), "faixa_horario")


def correlacoes(tabela: pd.DataFrame, efic: pd.DataFrame) -> pd.DataFrame:
    """Correlação de Spearman de cada indicador com os pontos finais (n = 20 times)."""
    t = tabela.set_index("time").join(efic.set_index("time")["arrecadacao_media"])
    linhas = [(v, spearman(t[v], t["pontos"])) for v in
              ["saldo_gols", "gols_pro", "gols_contra", "arrecadacao_media"]]
    return pd.DataFrame(linhas, columns=["indicador", "spearman_com_pontos"])


def construir(partidas: pd.DataFrame) -> dict:
    """Gera todas as tabelas gold. Retorna {nome_arquivo: DataFrame}."""
    ppt = partidas_por_time(partidas)
    tabela = classificacao(ppt)
    mando = desempenho_mando(ppt)
    dif = diferenca_mando(mando)
    efic = eficiencia_arrecadacao(ppt, tabela, dif)
    return {
        "partidas_por_time": ppt,
        "classificacao": tabela,
        "desempenho_mando": mando,
        "diferenca_mando": dif,
        "resumo_temporada": resumo_temporada(partidas, tabela, ppt),
        "evolucao_rodadas": evolucao_rodadas(ppt),
        "desempenho_turno": desempenho_turno(ppt, tabela),
        "placares": placares(partidas),
        "mando_distancia": mando_distancia(partidas),
        "eficiencia_arrecadacao": efic,
        "arrecadacao_resultado": arrecadacao_resultado(partidas),
        "formacoes": formacoes(ppt),
        "horario": horario(partidas),
        "correlacoes": correlacoes(tabela, efic),
    }

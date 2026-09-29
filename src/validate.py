"""Checagens de qualidade da camada processed. Falha o pipeline se algo estiver errado."""
from __future__ import annotations

import logging

import pandas as pd

log = logging.getLogger(__name__)

OBRIGATORIAS = ["id_partida", "temporada", "rodada", "data", "mandante", "visitante",
                "gols_mandante", "gols_visitante", "arena"]


class ErroQualidade(Exception):
    pass


def validar(df: pd.DataFrame) -> None:
    erros = []

    if df["id_partida"].duplicated().any():
        erros.append(f"{df['id_partida'].duplicated().sum()} id_partida duplicados")

    nulos = df[OBRIGATORIAS].isna().sum()
    for col, n in nulos[nulos > 0].items():
        erros.append(f"{n} nulos na coluna obrigatória '{col}'")

    if (df[["gols_mandante", "gols_visitante"]] < 0).any().any():
        erros.append("placar negativo")

    if (df["mandante"] == df["visitante"]).any():
        erros.append("partida com mandante igual ao visitante")

    esperado = df["mandante"].where(df["resultado"] == "M", df["visitante"]).where(df["resultado"] != "E")
    divergente = ~((esperado == df["vencedor"]) | (esperado.isna() & df["vencedor"].isna()))
    if divergente.any():
        erros.append(f"{divergente.sum()} partidas com 'vencedor' incoerente com o placar")

    for c in ["estado_mandante", "estado_visitante"]:
        if not df[c].str.fullmatch(r"[A-Z]{2}").all():
            erros.append(f"UF inválida em '{c}'")

    if erros:
        raise ErroQualidade("; ".join(erros))

    # Avisos (não bloqueiam): temporadas com número de jogos fora do padrão
    jogos = df.groupby("temporada").size()
    times = pd.concat([df[["temporada", "mandante"]].set_axis(["temporada", "time"], axis=1),
                       df[["temporada", "visitante"]].set_axis(["temporada", "time"], axis=1)]
                      ).drop_duplicates().groupby("temporada").size()
    for temporada, n in jogos.items():
        esperado_jogos = times[temporada] * (times[temporada] - 1)
        if n != esperado_jogos:
            log.warning("Temporada %s: %d jogos (esperado %d para %d times)",
                        temporada, n, esperado_jogos, times[temporada])

    log.info("Validação OK: %d partidas, temporadas %d-%d",
             len(df), df["temporada"].min(), df["temporada"].max())

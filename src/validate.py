"""Checagens de qualidade da camada processed. Falha o pipeline se algo estiver errado."""
from __future__ import annotations

import logging

import pandas as pd

from src.config import TEMPORADA

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

    if (df["temporada"] != TEMPORADA).any():
        erros.append(f"partidas fora da temporada {TEMPORADA}")

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

    # Aviso (não bloqueia): turno e returno completos têm times × (times − 1) jogos
    times = pd.concat([df["mandante"], df["visitante"]]).nunique()
    if len(df) != times * (times - 1):
        log.warning("Temporada %d: %d jogos (esperado %d para %d times)",
                    TEMPORADA, len(df), times * (times - 1), times)

    log.info("Validação OK: %d partidas da temporada %d", len(df), TEMPORADA)


def _clube_valido(df: pd.DataFrame, partidas: pd.DataFrame, nome: str, erros: list) -> None:
    p = partidas.set_index("id_partida")
    joga = (df["clube"] == df["id_partida"].map(p["mandante"])) | (df["clube"] == df["id_partida"].map(p["visitante"]))
    if not joga.all():
        erros.append(f"{nome}: {(~joga).sum()} linhas com clube que não jogou a partida")


def validar_gols(gols: pd.DataFrame, partidas: pd.DataFrame) -> None:
    erros = []
    _clube_valido(gols, partidas, "gols", erros)
    if gols["minuto"].isna().any():
        erros.append(f"gols: {gols['minuto'].isna().sum()} minutos inválidos")

    # Gols por clube devem bater com o placar (gol contra conta para o beneficiado)
    contagem = gols.groupby(["id_partida", "clube"]).size()
    p = partidas.set_index("id_partida")
    casa = pd.Series(list(zip(p.index, p["mandante"]))).map(contagem).fillna(0).to_numpy()
    fora = pd.Series(list(zip(p.index, p["visitante"]))).map(contagem).fillna(0).to_numpy()
    divergentes = ((casa != p["gols_mandante"].to_numpy()) | (fora != p["gols_visitante"].to_numpy())).sum()
    if divergentes:
        erros.append(f"gols: {divergentes} partidas com gols registrados diferentes do placar")

    if erros:
        raise ErroQualidade("; ".join(erros))
    log.info("Validação OK: %d gols", len(gols))


def validar_estatisticas(est: pd.DataFrame, partidas: pd.DataFrame) -> None:
    erros = []
    _clube_valido(est, partidas, "estatisticas", erros)
    if est.duplicated(["id_partida", "clube"]).any():
        erros.append("estatisticas: clube repetido na mesma partida")
    if (est["chutes_no_alvo"] > est["chutes"]).any():
        erros.append("estatisticas: chutes no alvo maior que chutes")
    if not est["posse_de_bola"].dropna().between(0, 100).all():
        erros.append("estatisticas: posse de bola fora de 0–100")
    if erros:
        raise ErroQualidade("; ".join(erros))

    sem = set(partidas["id_partida"]) - set(est["id_partida"])
    if sem:
        log.warning("Estatísticas: %d partidas sem estatísticas", len(sem))
    for col in ["posse_de_bola", "passes", "precisao_passes"]:
        n = est[col].isna().sum()
        if n:
            log.warning("Estatísticas: %d valores ausentes em '%s'", n, col)
    log.info("Validação OK: estatísticas de %d partidas", est["id_partida"].nunique())


def validar_tudo(tabelas: dict) -> None:
    partidas = tabelas["partidas"]
    validar(partidas)
    validar_gols(tabelas["gols"], partidas)
    validar_estatisticas(tabelas["estatisticas"], partidas)

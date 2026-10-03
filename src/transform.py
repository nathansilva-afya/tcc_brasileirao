"""Transformação: brutos (raw) -> partidas, gols, cartões e estatísticas limpos (processed)."""
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


def separar_minuto(minuto: pd.Series) -> pd.DataFrame:
    """'90+4' -> minuto=90, acrescimo=4, tempo=2. Minuto até 45 é do 1º tempo."""
    partes = minuto.astype("string").str.extract(r"^(\d+)(?:\+(\d+))?$")
    base = pd.to_numeric(partes[0]).astype("Int64")
    return pd.DataFrame({
        "minuto": base,
        "acrescimo": pd.to_numeric(partes[1]).fillna(0).astype("Int64"),
        "tempo": (base > 45).astype("Int64") + 1,
    }, index=minuto.index)


def _contexto_partida(df: pd.DataFrame, partidas: pd.DataFrame) -> pd.DataFrame:
    """Mantém só eventos de partidas da temporada e acrescenta mando e adversário do clube."""
    p = partidas.set_index("id_partida")
    df = df[df["id_partida"].isin(p.index)].copy()
    mandante = df["id_partida"].map(p["mandante"])
    visitante = df["id_partida"].map(p["visitante"])
    df["mando"] = (df["clube"] == mandante).map({True: "casa", False: "fora"})
    df["adversario"] = visitante.where(df["clube"] == mandante, mandante)
    return df


def transformar_gols(bruto: pd.DataFrame, partidas: pd.DataFrame) -> pd.DataFrame:
    """Um gol por linha. Em gol contra, `clube` é o time beneficiado e `atleta` é o adversário que marcou."""
    df = limpar_texto(bruto.rename(columns={"partida_id": "id_partida", "rodata": "rodada"}))
    df = _contexto_partida(df, partidas)
    df = pd.concat([df.drop(columns="minuto"), separar_minuto(df["minuto"])], axis=1)
    df["tipo_gol"] = df["tipo_de_gol"].map({"Penalty": "Pênalti", "Gol Contra": "Gol contra"}).fillna("Normal")
    ordem = ["id_partida", "rodada", "clube", "mando", "adversario", "atleta",
             "minuto", "acrescimo", "tempo", "tipo_gol"]
    return df[ordem].sort_values(["rodada", "id_partida", "tempo", "minuto", "acrescimo"]).reset_index(drop=True)


def transformar_cartoes(bruto: pd.DataFrame, partidas: pd.DataFrame) -> pd.DataFrame:
    """Um cartão por linha."""
    df = limpar_texto(bruto.rename(columns={"partida_id": "id_partida", "rodata": "rodada"}))
    df = _contexto_partida(df, partidas)
    df = pd.concat([df.drop(columns="minuto"), separar_minuto(df["minuto"])], axis=1)
    df["posicao"] = df["posicao"].replace({"Zagueira": "Zagueiro"})
    df["num_camisa"] = pd.to_numeric(df["num_camisa"]).astype("Int64")
    ordem = ["id_partida", "rodada", "clube", "mando", "adversario", "atleta", "num_camisa",
             "posicao", "cartao", "minuto", "acrescimo", "tempo"]
    return df[ordem].sort_values(["rodada", "id_partida", "tempo", "minuto", "acrescimo"]).reset_index(drop=True)


def transformar_estatisticas(bruto: pd.DataFrame, partidas: pd.DataFrame) -> pd.DataFrame:
    """Estatísticas de cada time em cada partida (2 linhas por jogo).
    Percentuais viram número (0–100). Passes = 0 é erro da fonte e vira nulo."""
    df = limpar_texto(bruto.rename(columns={"partida_id": "id_partida", "rodata": "rodada"}))
    df = _contexto_partida(df, partidas)
    for col in ["posse_de_bola", "precisao_passes"]:
        df[col] = pd.to_numeric(df[col].str.rstrip("%"))
    inteiros = ["chutes", "chutes_no_alvo", "passes", "faltas", "cartao_amarelo",
                "cartao_vermelho", "impedimentos", "escanteios"]
    for col in inteiros:
        df[col] = pd.to_numeric(df[col]).astype("Int64")
    df["passes"] = df["passes"].mask(df["passes"] == 0)
    ordem = ["id_partida", "rodada", "clube", "mando", "adversario", "chutes", "chutes_no_alvo",
             "posse_de_bola", "passes", "precisao_passes", "faltas", "cartao_amarelo",
             "cartao_vermelho", "impedimentos", "escanteios"]
    return df[ordem].sort_values(["rodada", "id_partida", "mando"]).reset_index(drop=True)


def _ler_evento(caminho) -> pd.DataFrame:
    # Os IDs são numéricos; o resto fica como texto para a limpeza tratar
    return pd.read_csv(caminho, encoding="utf-8", dtype={"minuto": str, "num_camisa": str,
                                                         "posse_de_bola": str, "precisao_passes": str})


def transformar_tudo(caminhos: dict) -> dict:
    """Lê os 4 brutos e devolve {nome: DataFrame} da camada processed."""
    partidas = transformar(ler_bruto(caminhos["partidas"]))
    return {
        "partidas": partidas,
        "gols": transformar_gols(_ler_evento(caminhos["gols"]), partidas),
        "cartoes": transformar_cartoes(_ler_evento(caminhos["cartoes"]), partidas),
        "estatisticas": transformar_estatisticas(_ler_evento(caminhos["estatisticas"]), partidas),
    }


def ler_partidas(caminho) -> pd.DataFrame:
    """Lê a camada processed já com os tipos corretos."""
    return pd.read_csv(caminho, parse_dates=["data"])

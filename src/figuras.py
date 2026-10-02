"""Gráficos (PNG) para o texto do TCC, gerados a partir das tabelas gold."""
from __future__ import annotations

import logging

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

from src import config  # noqa: E402

log = logging.getLogger(__name__)

# Paleta: azul (série 1), laranja (série 2), aqua (série 3); cinza para contexto.
AZUL, LARANJA, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
CINZA, CINZA_CLARO = "#8f8e89", "#d3d2cd"
TEXTO, TEXTO_2, GRADE = "#0b0b0b", "#52514e", "#e4e3df"

NOMES = {"Sao Paulo": "São Paulo", "Gremio": "Grêmio", "Ceara": "Ceará", "Vitoria": "Vitória",
         "Atletico-MG": "Atlético-MG", "Botafogo-RJ": "Botafogo"}

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.edgecolor": CINZA_CLARO, "axes.labelcolor": TEXTO_2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRADE,
    "grid.linewidth": 0.8, "axes.axisbelow": True, "xtick.color": TEXTO_2, "ytick.color": TEXTO_2,
    "text.color": TEXTO, "legend.frameon": False, "figure.dpi": 100, "savefig.dpi": 200,
    "savefig.bbox": "tight", "figure.facecolor": "white",
})


def _nome(time: str) -> str:
    return NOMES.get(time, time)


def _num(v: float, casas: int = 1) -> str:
    """Número no formato pt-BR (vírgula decimal)."""
    return f"{v:.{casas}f}".replace(".", ",")


def _pct():
    return FuncFormatter(lambda v, _: f"{v * 100:.0f}%")


def _salvar(fig, nome: str) -> None:
    config.FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    caminho = config.FIGURAS_DIR / f"{nome}.png"
    fig.savefig(caminho)
    plt.close(fig)
    log.info("Figura %s", caminho.relative_to(config.ROOT))


def classificacao(t: pd.DataFrame) -> None:
    t = t.sort_values("posicao", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 6.5))
    rotulos = [f"{p}º  {_nome(n)}" for p, n in zip(t["posicao"], t["time"])]
    ax.barh(rotulos, t["pontos"], color=AZUL, height=0.7, edgecolor="white", linewidth=1)
    for y, v in enumerate(t["pontos"]):
        ax.text(v + 0.8, y, str(v), va="center", fontsize=9, color=TEXTO)
    for corte, texto in [(13.5, "Libertadores (G6)"), (3.5, "Rebaixamento (Z4)")]:
        ax.axhline(corte, color=CINZA, linewidth=0.8, linestyle="--")
        ax.text(84, corte + 0.25, texto, ha="right", fontsize=8, color=TEXTO_2)
    ax.set_xlim(0, 86)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Pontos")
    ax.set_title("Classificação final do Campeonato Brasileiro Série A 2025")
    _salvar(fig, "fig01_classificacao")


def resultados_mando(r: pd.Series) -> None:
    fig, ax = plt.subplots(figsize=(6, 3.5))
    cats = ["Vitória do mandante", "Empate", "Vitória do visitante"]
    vals = [r["pct_vitoria_mandante"], r["pct_empate"], r["pct_vitoria_visitante"]]
    ax.bar(cats, vals, color=[AZUL, CINZA, LARANJA], width=0.6)
    for x, v in enumerate(vals):
        ax.text(x, v + 0.01, f"{_num(v * 100)}%", ha="center", fontsize=10)
    ax.yaxis.set_major_formatter(_pct())
    ax.set_ylim(0, 0.6)
    ax.grid(axis="x", visible=False)
    ax.set_title("Distribuição dos resultados das 380 partidas")
    _salvar(fig, "fig02_resultados_mando")


def _halteres(df: pd.DataFrame, col_a: str, col_b: str, rot_a: str, rot_b: str,
              titulo: str, xlabel: str, nome: str, formato=None) -> None:
    """Gráfico de halteres: um ponto por condição, ligados por um segmento, um time por linha."""
    fig, ax = plt.subplots(figsize=(8, 6.5))
    y = range(len(df))
    ax.hlines(y, df[col_a], df[col_b], color=CINZA_CLARO, linewidth=2)
    ax.scatter(df[col_b], y, color=LARANJA, s=45, zorder=3, label=rot_b, edgecolor="white", linewidth=1.5)
    ax.scatter(df[col_a], y, color=AZUL, s=45, zorder=3, label=rot_a, edgecolor="white", linewidth=1.5)
    ax.set_yticks(list(y), [_nome(n) for n in df["time"]])
    ax.grid(axis="y", visible=False)
    if formato:
        ax.xaxis.set_major_formatter(formato)
    ax.set_xlabel(xlabel)
    h, l = ax.get_legend_handles_labels()
    ax.legend(h[::-1], l[::-1], loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2)
    ax.set_title(titulo)
    _salvar(fig, nome)


def casa_fora(dif: pd.DataFrame) -> None:
    _halteres(dif.sort_values("diferenca"), "aproveitamento_casa", "aproveitamento_fora", "Em casa", "Fora",
              "Aproveitamento em casa e fora, por time (ordenado pela diferença)", "Aproveitamento",
              "fig03_casa_fora", _pct())


def turnos(t: pd.DataFrame) -> None:
    _halteres(t.sort_values("variacao_pontos"), "pontos_turno2", "pontos_turno1", "2º turno", "1º turno",
              "Pontos no 1º e no 2º turno (ordenado pela variação)", "Pontos", "fig04_turnos")


def evolucao(ev: pd.DataFrame, tabela: pd.DataFrame) -> None:
    destaque = {"Flamengo": AZUL, "Palmeiras": LARANJA, "Cruzeiro": AQUA}
    fig, ax = plt.subplots(figsize=(8, 5))
    for time, g in ev.groupby("time"):
        if time not in destaque:
            ax.plot(g["rodada"], g["pontos_acumulados"], color=CINZA_CLARO, linewidth=1)
    for time, cor in destaque.items():
        g = ev[ev["time"] == time]
        ax.plot(g["rodada"], g["pontos_acumulados"], color=cor, linewidth=2)
        fim = g.iloc[-1]
        deslocamento = -1.5 if time == "Palmeiras" else 1 if time == "Flamengo" else 0
        ax.text(38.6, fim["pontos_acumulados"] + deslocamento, f"{time} ({fim['pontos_acumulados']})", va="center",
                fontsize=9, color=TEXTO)
    ax.set_xlim(1, 38)
    ax.set_xticks([1, 5, 10, 15, 19, 25, 30, 35, 38])
    ax.axvline(19.5, color=CINZA, linewidth=0.8, linestyle="--")
    ax.text(19.7, 2, "fim do 1º turno", fontsize=8, color=TEXTO_2)
    ax.set_xlabel("Rodada")
    ax.set_ylabel("Pontos acumulados")
    ax.set_title("Evolução dos pontos ao longo das 38 rodadas (demais times em cinza)")
    _salvar(fig, "fig05_evolucao_pontos")


def _dispersao(df: pd.DataFrame, x: str, y: str, xlabel: str, ylabel: str, titulo: str, nome: str,
               xfmt=None, ajustes: dict | None = None) -> None:
    ajustes = ajustes or {}
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df[x], df[y], color=AZUL, s=55, edgecolor="white", linewidth=1.5, zorder=3)
    for _, r in df.iterrows():
        dx, dy, ha = ajustes.get(r["time"], (6, 0, "left"))
        ax.annotate(_nome(r["time"]), (r[x], r[y]), xytext=(dx, dy), textcoords="offset points",
                    va="center", ha=ha, fontsize=8, color=TEXTO_2)
    if xfmt:
        ax.xaxis.set_major_formatter(xfmt)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(titulo)
    _salvar(fig, nome)


def ataque_defesa(t: pd.DataFrame) -> None:
    ajustes = {"Santos": (6, -6, "left"), "Corinthians": (-6, 0, "right"), "Sao Paulo": (6, 5, "left"),
               "Gremio": (-6, 4, "right"), "Atletico-MG": (-6, -4, "right"), "Cruzeiro": (6, -5, "left"),
               "Fluminense": (-6, 0, "right"), "Botafogo-RJ": (6, 4, "left"), "Bahia": (-6, 0, "right"),
               "Vasco": (-6, 4, "right"), "Fortaleza": (6, 4, "left"), "Internacional": (0, -10, "center"),
               "Bragantino": (6, 1, "left"), "Vitoria": (-6, 0, "right")}
    _dispersao(t, "gols_pro", "gols_contra", "Gols marcados", "Gols sofridos",
               "Ataque x defesa: gols marcados e sofridos por time", "fig06_ataque_defesa", ajustes=ajustes)


def arrecadacao_pontos(e: pd.DataFrame, rho: float) -> None:
    e = e.assign(arrec_mi=e["arrecadacao_media"] / 1e6)
    ajustes = {"Santos": (-6, 0, "right"), "Atletico-MG": (0, -10, "center"), "Vitoria": (6, 4, "left"),
               "Fortaleza": (-6, -3, "right"), "Ceara": (6, -4, "left"), "Internacional": (6, -3, "left"),
               "Gremio": (6, -2, "left"), "Bahia": (6, 2, "left"), "Sao Paulo": (6, 4, "left")}
    _dispersao(e, "arrec_mi", "pontos", "Arrecadação média por jogo como mandante (R$ milhões)", "Pontos",
               f"Arrecadação média x pontos (Spearman = {_num(rho, 2)})", "fig07_arrecadacao_pontos",
               xfmt=FuncFormatter(lambda v, _: _num(v)), ajustes=ajustes)


def pontos_por_milhao(e: pd.DataFrame) -> None:
    e = e.sort_values("pontos_por_milhao")
    fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.barh([_nome(n) for n in e["time"]], e["pontos_por_milhao"], color=AZUL, height=0.7)
    for y, v in enumerate(e["pontos_por_milhao"]):
        ax.text(v + 0.15, y, _num(v, 2), va="center", fontsize=9)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Pontos por R$ 1 milhão arrecadado em bilheteria como mandante")
    ax.set_title("Eficiência: pontos conquistados por milhão de reais arrecadado")
    _salvar(fig, "fig08_pontos_por_milhao")


def _empilhado(df: pd.DataFrame, rotulos: list, titulo: str, nome: str) -> None:
    """Barras 100% empilhadas: vitória do mandante / empate / vitória do visitante."""
    fig, ax = plt.subplots(figsize=(8, 0.75 * len(df) + 1.4))
    esquerda = pd.Series(0.0, index=df.index)
    for col, cor, rot in [("pct_vitoria_mandante", AZUL, "Vitória do mandante"),
                          ("pct_empate", CINZA_CLARO, "Empate"),
                          ("pct_vitoria_visitante", LARANJA, "Vitória do visitante")]:
        ax.barh(rotulos, df[col], left=esquerda, color=cor, height=0.6, edgecolor="white",
                linewidth=2, label=rot)
        for y, (l, v) in enumerate(zip(esquerda, df[col])):
            ax.text(l + v / 2, y, f"{_num(v * 100)}%", ha="center", va="center", fontsize=9,
                    color="white" if cor != CINZA_CLARO else TEXTO)
        esquerda += df[col]
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(_pct())
    ax.grid(visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    ax.set_title(titulo)
    _salvar(fig, nome)


def arrecadacao_resultado(q: pd.DataFrame) -> None:
    rot = [f"{r.quartil}: R$ {_num(r.arrecadacao_min / 1e6, 2)}–{_num(r.arrecadacao_max / 1e6, 2)} mi"
           for r in q.itertuples()]
    _empilhado(q, rot, "Resultado das partidas por quartil de arrecadação", "fig09_arrecadacao_resultado")


def distancia(d: pd.DataFrame) -> None:
    nomes = {"mesmo estado": "Mesmo estado", "mesma regiao": "Mesma região", "outra regiao": "Outra região"}
    rot = [f"{nomes[c]} ({n} jogos)" for c, n in zip(d["distancia"], d["jogos"])]
    _empilhado(d, rot, "Resultado das partidas pela distância entre as sedes", "fig10_distancia")


def formacoes(f: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.bar(f["formacao"], f["aproveitamento"], color=AZUL, width=0.6)
    for x, (v, n) in enumerate(zip(f["aproveitamento"], f["jogos"])):
        ax.text(x, v + 0.01, f"{_num(v * 100)}%\n({n} jogos)", ha="center", fontsize=8.5)
    ax.yaxis.set_major_formatter(_pct())
    ax.set_ylim(0, 0.6)
    ax.grid(axis="x", visible=False)
    ax.set_title("Aproveitamento por esquema tático")
    _salvar(fig, "fig11_formacoes")


def placares(p: pd.DataFrame) -> None:
    p = p.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.barh(p["placar"], p["jogos"], color=AZUL, height=0.7)
    for y, (n, pc) in enumerate(zip(p["jogos"], p["pct"])):
        ax.text(n + 0.6, y, f"{n} ({_num(pc * 100)}%)", va="center", fontsize=9)
    ax.set_xlim(0, p["jogos"].max() * 1.2)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Jogos")
    ax.set_title("Os 10 placares mais frequentes (mandante x visitante)")
    _salvar(fig, "fig12_placares")


def gerar(tabelas: dict) -> None:
    """Gera todas as figuras em config.FIGURAS_DIR."""
    t = tabelas["classificacao"]
    rho = tabelas["correlacoes"].set_index("indicador").loc["arrecadacao_media", "spearman_com_pontos"]
    classificacao(t)
    resultados_mando(tabelas["resumo_temporada"].iloc[0])
    casa_fora(tabelas["diferenca_mando"])
    turnos(tabelas["desempenho_turno"])
    evolucao(tabelas["evolucao_rodadas"], t)
    ataque_defesa(t)
    arrecadacao_pontos(tabelas["eficiencia_arrecadacao"], rho)
    pontos_por_milhao(tabelas["eficiencia_arrecadacao"])
    arrecadacao_resultado(tabelas["arrecadacao_resultado"])
    distancia(tabelas["mando_distancia"])
    formacoes(tabelas["formacoes"])
    placares(tabelas["placares"])

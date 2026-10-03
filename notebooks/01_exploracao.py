# Análise exploratória. Rode "python -m src.pipeline" antes para gerar os dados.
#%%
import sys
from pathlib import Path

ROOT = Path.cwd() if (Path.cwd() / "src").exists() else Path.cwd().parent
sys.path.insert(0, str(ROOT))

import pandas as pd

from src import config
from src.transform import ler_partidas

partidas = ler_partidas(config.PARTIDAS)
classificacao = pd.read_csv(config.ANALYTICS_DIR / "classificacao.csv")
resumo = pd.read_csv(config.ANALYTICS_DIR / "resumo_temporada.csv")
mando = pd.read_csv(config.ANALYTICS_DIR / "desempenho_mando.csv")
artilharia = pd.read_csv(config.ANALYTICS_DIR / "artilharia.csv")
gols_minuto = pd.read_csv(config.ANALYTICS_DIR / "gols_por_minuto.csv")
est_time = pd.read_csv(config.ANALYTICS_DIR / "estatisticas_time.csv")
est_jogo = pd.read_csv(config.ANALYTICS_DIR / "estatisticas_partida_time.csv")

partidas.info()

# %% Resumo da temporada 2025
resumo[["campeao", "pontos_campeao", "media_gols", "pct_vitoria_mandante"]]

# %% Classificação final
classificacao[["posicao", "time", "pontos", "vitorias", "empates", "derrotas", "saldo_gols", "aproveitamento"]]

# %% Distribuição dos resultados por mando de campo
resumo[["pct_vitoria_mandante", "pct_empate", "pct_vitoria_visitante"]].T.plot.bar(
    title="Resultado por mando de campo (2025)", figsize=(8, 4), legend=False)

# %% Aproveitamento em casa x fora por time
(mando.set_index(["time", "mando"])["aproveitamento"]
      .unstack().assign(diferenca=lambda d: d["casa"] - d["fora"])
      .sort_values("diferenca", ascending=False).head(10))

# %% Artilharia
artilharia.head(10)

# %% Em que momento do jogo saem os gols
gols_minuto.plot.bar(x="faixa", y="gols", title="Gols por faixa de minuto (2025)", figsize=(8, 4), legend=False)

# %% Estilo de jogo e eficiência por time
est_time[["time", "media_posse", "media_chutes", "pct_chutes_no_alvo", "conversao_chutes", "cartoes_amarelos"]]

# %% Posse de bola e finalizações explicam o resultado?
est_jogo[["pontos", "gols_pro", "posse_de_bola", "chutes", "chutes_no_alvo", "passes", "escanteios"]].corr()["pontos"]

# %%

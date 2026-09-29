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
resumo = pd.read_csv(config.ANALYTICS_DIR / "resumo_temporadas.csv")
historico = pd.read_csv(config.ANALYTICS_DIR / "historico_times.csv")
mando = pd.read_csv(config.ANALYTICS_DIR / "desempenho_mando.csv")

partidas.info()

# %% Campeões e pontuação
resumo[["temporada", "campeao", "pontos_campeao", "media_gols", "pct_vitoria_mandante"]]

# %% Maiores campeões (era dos pontos corridos)
historico.sort_values("titulos", ascending=False)[["time", "titulos", "top4", "temporadas", "aproveitamento"]].head(10)

# %% Vantagem do mando de campo ao longo do tempo (2020-2021 sem público)
resumo.set_index("temporada")[["pct_vitoria_mandante", "pct_empate", "pct_vitoria_visitante"]].plot(
    title="Resultado por mando de campo", figsize=(10, 4))

# %% Aproveitamento em casa x fora por time
(mando.groupby(["time", "mando"])["aproveitamento"].mean()
      .unstack().assign(diferenca=lambda d: d["casa"] - d["fora"])
      .sort_values("diferenca", ascending=False).head(10))

# %%

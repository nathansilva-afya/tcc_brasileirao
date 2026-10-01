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
mando = pd.read_csv(config.ANALYTICS_DIR / "desempenho_mando.csv")

partidas.info()

# %% Resumo da temporada 2025
resumo[["temporada", "campeao", "pontos_campeao", "media_gols", "pct_vitoria_mandante"]]

# %% Classificação final
classificacao[["posicao", "time", "pontos", "vitorias", "empates", "derrotas", "saldo_gols", "aproveitamento"]]

# %% Distribuição dos resultados por mando de campo
resumo.set_index("temporada")[["pct_vitoria_mandante", "pct_empate", "pct_vitoria_visitante"]].T.plot.bar(
    title="Resultado por mando de campo (2025)", figsize=(8, 4), legend=False)

# %% Aproveitamento em casa x fora por time
(mando.set_index(["time", "mando"])["aproveitamento"]
      .unstack().assign(diferenca=lambda d: d["casa"] - d["fora"])
      .sort_values("diferenca", ascending=False).head(10))

# %%

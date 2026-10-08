# Análise exploratória. Rode "python -m src.pipeline" antes para gerar os dados.
#%%
import sys
from pathlib import Path

ROOT = Path.cwd() if (Path.cwd() / "src").exists() else Path.cwd().parent
sys.path.insert(0, str(ROOT))

import pandas as pd

from src import config

bilheteria = pd.read_csv(config.ANALYTICS_DIR / "bilheteria.csv")
scout = pd.read_csv(config.ANALYTICS_DIR / "scout.csv")
posse_bola = pd.read_csv(config.ANALYTICS_DIR / "posse_bola.csv")

# %% Arrecadação média por dia da semana e horário
bilheteria.sort_values("media_arrecadacao", ascending=False)

# %% Artilheiros e eficiência do clube
scout.sort_values("gols_do_jogador", ascending=False).head(10)

# %% Eficiência de cada clube (gols ÷ chutes no alvo)
scout.drop_duplicates("clube")[["clube", "eficiencia_clube_pct"]].sort_values("eficiencia_clube_pct", ascending=False)

# %% Posse de bola x taxa de vitória
posse_bola.plot.scatter(x="posse_de_bola", y="taxa_vitoria_pct", title="Posse de bola x vitória (2025)", figsize=(8, 4))

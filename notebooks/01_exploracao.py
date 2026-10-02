# Análise exploratória. Rode "python -m src.pipeline" antes para gerar os dados.
#%%
import sys
from pathlib import Path

ROOT = Path.cwd() if (Path.cwd() / "src").exists() else Path.cwd().parent
sys.path.insert(0, str(ROOT))

import pandas as pd

from src import config
from src.transform import ler_partidas


def gold(nome: str) -> pd.DataFrame:
    return pd.read_csv(config.ANALYTICS_DIR / f"{nome}.csv")


partidas = ler_partidas(config.PARTIDAS)
partidas.info()

# %% Resumo da temporada 2025
gold("resumo_temporada").T

# %% Classificação final
gold("classificacao")[["posicao", "time", "pontos", "vitorias", "empates", "derrotas", "saldo_gols", "aproveitamento"]]

# %% Correlação de Spearman dos indicadores com os pontos
gold("correlacoes")

# %% Vantagem de jogar em casa por time
gold("diferenca_mando")

# %% Resultados pela distância entre as sedes
gold("mando_distancia")

# %% 1º x 2º turno
gold("desempenho_turno")

# %% Arrecadação e eficiência
gold("eficiencia_arrecadacao")

# %% Resultados por quartil de arrecadação
gold("arrecadacao_resultado")

# %% Esquemas táticos
gold("formacoes")

# %% Placares mais frequentes
gold("placares").head(10)

# %% Faixa de horário
gold("horario")

# %%

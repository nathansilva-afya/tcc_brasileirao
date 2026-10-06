#Passando dados da camada raw para a camada processed

import pandas as pd

df_brasileirao = pd.read_csv("/Workspace/tcc/tcc_brasileirao/data/raw/campeonato-brasileiro-full.csv")
df_gols = pd.read_csv("/Workspace/tcc/tcc_brasileirao/data/raw/campeonato-brasileiro-gols.csv")
df_estatisticas = pd.read_csv("/Workspace/tcc/tcc_brasileirao/data/raw/campeonato-brasileiro-estatisticas-full.csv")


df_bilheteria = df_brasileirao
df_bilheteria['data'] = pd.to_datetime(df_brasileirao['data'])
df_bilheteria['dia_da_semana'] = df_bilheteria['data'].dt.day_name()
df_bilheteria.to_csv("/Workspace/tcc/tcc_brasileirao/data/processed/bilheteria_silver.csv", index=False)


df_posse = pd.merge(df_brasileirao, df_estatisticas, left_on="ID", right_on="partida_id", how='inner')
df_posse['posse_de_bola'] = df_posse['posse_de_bola'].str.replace('%', '')
df_posse['posse_de_bola'] = df_posse['posse_de_bola'].astype(float)
df_posse.to_csv("/Workspace/tcc/tcc_brasileirao/data/processed/posse_bola_silver.csv", index=False)


df_scout = pd.merge(df_estatisticas, df_gols, on=["partida_id", "clube"], how='left')
df_scout.to_csv("/Workspace/tcc/tcc_brasileirao/data/processed/scout_silver.csv", index=False)


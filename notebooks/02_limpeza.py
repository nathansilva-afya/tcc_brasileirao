#Passando dados da camada processed para a camada analytics
import pandas as pd
import numpy as np

df_posse_silver = pd.read_csv("/Workspace/Users/nathandeandrades@gmail.com/tcc_brasileirao/data/processed/posse_bola_silver.csv")
df_bilheteria_silver = pd.read_csv("/Workspace/Users/nathandeandrades@gmail.com/tcc_brasileirao/data/processed/bilheteria_silver.csv")
df_scout_silver = pd.read_csv("/Workspace/Users/nathandeandrades@gmail.com/tcc_brasileirao/data/processed/scout_silver.csv")



df_bilheteria_silver['hora_oficial'] = pd.to_datetime(df_bilheteria_silver['hora'], format='%H:%M').dt.round('15T').dt.strftime('%H:%M')

df_arrecadacao_gold = df_bilheteria_silver.groupby(['dia_da_semana', 'hora_oficial'])['arrecadacao'].agg(
    qtd_jogos='count',
    media_arrecadacao='mean',
    total_arrecadacao='sum'
).reset_index()

df_arrecadacao_gold = df_arrecadacao_gold[df_arrecadacao_gold['qtd_jogos'] >= 3]
df_arrecadacao_gold['media_arrecadacao'] = df_arrecadacao_gold['media_arrecadacao'].round(2)
df_arrecadacao_gold['total_arrecadacao'] = df_arrecadacao_gold['total_arrecadacao'].round(2)

df_arrecadacao_gold.to_csv("/Workspace/Users/nathandeandrades@gmail.com/tcc_brasileirao/data/analytics/bilheteria_gold.csv", index=False)


##############################################################


df_gols_clube = df_scout_silver.dropna(subset=['atleta']).groupby('clube')['atleta'].count().reset_index(name='gols_do_clube')

df_estat_unicas = df_scout_silver.drop_duplicates(subset=['partida_id', 'clube'])
df_chutes_clube = df_estat_unicas.groupby('clube')['chutes_no_alvo'].sum().reset_index(name='chutes_alvo_clube')

df_eficiencia_clube = pd.merge(df_gols_clube, df_chutes_clube, on='clube')
df_eficiencia_clube['eficiencia_clube_pct'] = (df_eficiencia_clube['gols_do_clube'] / df_eficiencia_clube['chutes_alvo_clube']) * 100
df_eficiencia_clube['eficiencia_clube_pct'] = df_eficiencia_clube['eficiencia_clube_pct'].round(2)

df_gols_jogador = df_scout_silver.dropna(subset=['atleta']).groupby(['atleta', 'clube'])['atleta'].count().reset_index(name='gols_do_jogador')

df_artilharia_gold = pd.merge(
    df_gols_jogador, 
    df_eficiencia_clube[['clube', 'eficiencia_clube_pct']], 
    on='clube'
)

df_artilharia_gold.to_csv("/Workspace/Users/nathandeandrades@gmail.com/tcc_brasileirao/data/analytics/scout_gold.csv", index=False)


#######################################################################


df_posse_silver['venceu'] = np.where(df_posse_silver['clube'] == df_posse_silver['vencedor'], 1, 0)

df_conversao_gold = df_posse_silver.groupby('posse_de_bola')['venceu'].agg(
    total_jogos='count',
    taxa_vitoria_pct='mean' 
).reset_index()

df_conversao_gold['taxa_vitoria_pct'] = (df_conversao_gold['taxa_vitoria_pct'] * 100).round(2)
df_conversao_gold = df_conversao_gold.sort_values(by='posse_de_bola', ascending=True)
df_conversao_gold = df_conversao_gold[df_conversao_gold['total_jogos'] >= 4]

df_conversao_gold.to_csv("/Workspace/Users/nathandeandrades@gmail.com/tcc_brasileirao/data/analytics/posse_bola_gold.csv", index=False)


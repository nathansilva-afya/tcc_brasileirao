# Dicionário de dados

## processed/partidas.csv — uma linha por partida

| Coluna | Tipo | Descrição |
|---|---|---|
| id_partida | int | Identificador da partida na fonte |
| temporada | int | Ano da temporada (a de 2020 inclui jogos de jan/fev 2021) |
| rodada | int | Rodada (1–46 em 2003/04, 1–42 em 2005, 1–38 a partir de 2006) |
| data | date | Data do jogo (AAAA-MM-DD) |
| hora | str | Horário (HH:MM) |
| mandante / visitante | str | Times |
| gols_mandante / gols_visitante | int | Placar |
| total_gols | int | Soma dos gols |
| resultado | str | `M` vitória do mandante, `E` empate, `V` vitória do visitante |
| vencedor | str | Nome do vencedor (nulo em caso de empate) |
| estado_mandante / estado_visitante | str | UF do time |
| arena | str | Estádio |
| formacao_mandante / formacao_visitante | str | Esquema tático (ex.: 4-2-3-1). Disponível a partir de 2014, em cerca de 46% dos jogos |
| tecnico_mandante / tecnico_visitante | str | Técnico. Disponível a partir de 2014, em cerca de 50% dos jogos |
| arrecadacao | float | Renda em R$. Só existe para 2025, em cerca de 4% dos jogos |

## analytics/ — camada gold

| Arquivo | Grão | Principais colunas |
|---|---|---|
| partidas_por_time.csv | time × partida | time, adversario, mando (casa/fora), gols_pro, gols_contra, vitoria, empate, derrota, pontos |
| classificacao.csv | time × temporada | posicao, jogos, V/E/D, gols_pro, gols_contra, saldo_gols, pontos, aproveitamento |
| desempenho_mando.csv | time × temporada × mando | as mesmas métricas de `classificacao`, separadas entre casa e fora |
| resumo_temporadas.csv | temporada | jogos, times, media_gols, % de vitórias do mandante, % de empates, % de vitórias do visitante, campeao |
| historico_times.csv | time | temporadas, titulos, top4, melhor_posicao, totais e aproveitamento |

`aproveitamento` = pontos ÷ (jogos × 3). Critérios de desempate da classificação: pontos,
vitórias, saldo de gols, gols pró.

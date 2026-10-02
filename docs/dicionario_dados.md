# Dicionário de dados

## processed/partidas.csv — uma linha por partida

| Coluna | Tipo | Descrição |
|---|---|---|
| id_partida | int | Identificador da partida na fonte |
| temporada | int | Ano da temporada (sempre 2025) |
| rodada | int | Rodada (1–38) |
| data | date | Data do jogo (AAAA-MM-DD) |
| hora | str | Horário (HH:MM) |
| mandante / visitante | str | Times |
| gols_mandante / gols_visitante | int | Placar |
| total_gols | int | Soma dos gols |
| resultado | str | `M` vitória do mandante, `E` empate, `V` vitória do visitante |
| vencedor | str | Nome do vencedor (nulo em caso de empate) |
| estado_mandante / estado_visitante | str | UF do time |
| arena | str | Estádio |
| formacao_mandante / formacao_visitante | str | Esquema tático (ex.: 4-2-3-1) |
| tecnico_mandante / tecnico_visitante | str | Técnico |
| arrecadacao | float | Renda em R$ |

## analytics/ — camada gold

| Arquivo | Grão | Principais colunas |
|---|---|---|
| partidas_por_time.csv | time × partida | time, adversario, mando (casa/fora), gols_pro, gols_contra, vitoria, empate, derrota, pontos |
| classificacao.csv | time | posicao, jogos, V/E/D, gols_pro, gols_contra, saldo_gols, pontos, aproveitamento |
| desempenho_mando.csv | time × mando | as mesmas métricas de `classificacao`, separadas entre casa e fora |
| resumo_temporada.csv | temporada 2025 (1 linha) | jogos, times, media_gols, % de vitórias do mandante, % de empates, % de vitórias do visitante, campeao |

`aproveitamento` = pontos ÷ (jogos × 3). Critérios de desempate da classificação: pontos,
vitórias, saldo de gols, gols pró.

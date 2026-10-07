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

## processed/gols.csv — um gol por linha

| Coluna | Tipo | Descrição |
|---|---|---|
| id_partida / rodada | int | Partida e rodada |
| clube | str | Time que recebeu o gol no placar (em gol contra, é o beneficiado) |
| mando | str | `casa` ou `fora` para o `clube` |
| adversario | str | Time adversário |
| atleta | str | Autor do gol (em gol contra, jogador do adversário) |
| minuto | int | Minuto do jogo sem os acréscimos (`90+4` → 90) |
| acrescimo | int | Minutos de acréscimo (`90+4` → 4; 0 se não houver) |
| tempo | int | 1 ou 2 |
| tipo_gol | str | `Normal`, `Pênalti` ou `Gol contra` |

## processed/estatisticas.csv — um time por partida (2 linhas por jogo)

| Coluna | Tipo | Descrição |
|---|---|---|
| id_partida / rodada / clube / mando / adversario | | como em `gols` |
| chutes / chutes_no_alvo | int | Finalizações totais e na direção do gol |
| posse_de_bola | float | % de posse (0–100). 12 valores ausentes |
| passes | int | Passes certos e errados. 0 é erro da fonte e vira nulo (7 casos) |
| precisao_passes | float | % de passes certos (0–100). 8 valores ausentes |
| faltas | int | Faltas cometidas |
| cartao_amarelo / cartao_vermelho | int | Cartões do time no jogo |
| impedimentos / escanteios | int | Totais do time no jogo |

## processed/cartoes.csv — um cartão por linha

Colunas: id_partida, rodada, clube, mando, adversario, atleta, num_camisa, posicao
(Goleiro/Zagueiro/Meio-campo/Atacante), cartao (Amarelo/Vermelho), minuto, acrescimo, tempo.
**A fonte não tem cartões de 2025, então esta tabela fica vazia**. Use os totais de `estatisticas`.

## analytics/ — camada gold

| Arquivo | Grão | Principais colunas |
|---|---|---|
| partidas_por_time.csv | time × partida | time, adversario, mando (casa/fora), gols_pro, gols_contra, vitoria, empate, derrota, pontos |
| classificacao.csv | time | posicao, jogos, V/E/D, gols_pro, gols_contra, saldo_gols, pontos, aproveitamento |
| desempenho_mando.csv | time × mando | as mesmas métricas de `classificacao`, separadas entre casa e fora |
| resumo_temporada.csv | temporada 2025 (1 linha) | jogos, times, media_gols, % de vitórias do mandante, % de empates, % de vitórias do visitante, campeao |
| artilharia.csv | atleta × clube | posicao, gols, penaltis, jogos_com_gol (gols contra não entram) |
| gols_por_minuto.csv | faixa de 15 min | gols, penaltis, gols_contra, pct_gols (acréscimos entram em 31-45+ e 76-90+) |
| estatisticas_partida_time.csv | time × partida | colunas de `partidas_por_time` + estatísticas do jogo + conversao_chutes. Base para correlações (ex.: posse × resultado) |
| estatisticas_time.csv | time | médias por jogo (chutes, posse, passes, precisão, escanteios, impedimentos), totais de faltas e cartões, pct_chutes_no_alvo, conversao_chutes, chutes_por_gol |
| cartoes_por_atleta.csv | atleta × clube | amarelos, vermelhos (vazio em 2025) |
| bilheteria.csv | dia da semana × horário | dia_da_semana (em inglês, ex.: Saturday), hora_oficial (arredondada a 15 min), qtd_jogos (com renda informada), media_arrecadacao, total_arrecadacao. Só combinações com 3+ jogos |
| scout.csv | atleta × clube | gols_do_jogador, eficiencia_clube_pct (gols do clube ÷ chutes no alvo × 100). Gol contra conta para o clube beneficiado, com o atleta adversário |
| posse_bola.csv | % de posse de bola | total_jogos, taxa_vitoria_pct (% de vitórias com aquela posse). Só valores com 4+ jogos |

`aproveitamento` = pontos ÷ (jogos × 3). Critérios de desempate da classificação: pontos,
vitórias, saldo de gols, gols pró.

No Databricks (`make databricks`), cada arquivo vira a tabela Delta
`workspace.brasileirao.<nome do arquivo sem .csv>`.

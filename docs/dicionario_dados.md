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
| partidas_por_time.csv | time × partida | time, adversario, mando (casa/fora), turno, formacao, estado, gols_pro, gols_contra, vitoria, empate, derrota, pontos, arrecadacao |
| classificacao.csv | time | posicao, jogos, V/E/D, gols_pro, gols_contra, saldo_gols, pontos, aproveitamento |
| desempenho_mando.csv | time × mando | as mesmas métricas de `classificacao`, separadas entre casa e fora |
| diferenca_mando.csv | time | aproveitamento_casa, aproveitamento_fora, diferenca (casa − fora), pct_pontos_casa |
| resumo_temporada.csv | temporada 2025 (1 linha) | jogos, times, media_gols, % de vitórias do mandante / empates / vitórias do visitante, pct_pontos_casa, campeao |
| evolucao_rodadas.csv | time × rodada | pontos da rodada, pontos_acumulados, saldo_acumulado, posicao ao fim da rodada |
| desempenho_turno.csv | time | pontos e aproveitamento no 1º turno (rodadas 1–19) e no 2º (20–38), variacao_pontos |
| placares.csv | placar | jogos, pct |
| mando_distancia.csv | distância | mesmo estado / mesma região / outra região: jogos, media_gols, % de resultados |
| eficiencia_arrecadacao.csv | time | arrecadacao_total e arrecadacao_media como mandante, pontos, aproveitamento_casa, pontos_por_milhao |
| arrecadacao_resultado.csv | quartil de arrecadação | faixa (min–max), jogos, media_gols, % de resultados |
| formacoes.csv | formação | as métricas de `classificacao` por esquema tático (só formações com 20+ jogos), pct_jogos |
| horario.csv | faixa de horário | jogos, media_gols, % de resultados |
| correlacoes.csv | indicador | correlação de Spearman de saldo, gols pró, gols contra e arrecadação média com os pontos |

`aproveitamento` = pontos ÷ (jogos × 3). Critérios de desempate da classificação: pontos,
vitórias, saldo de gols, gols pró.

`pct_pontos_casa` = pontos conquistados pelos mandantes ÷ total de pontos (medida de Pollard, 1986).
`pontos_por_milhao` = pontos totais ÷ (arrecadação como mandante em R$ milhões); considera só
a bilheteria, não a receita total do clube.

## figuras/

PNGs gerados por `src/figuras.py` a partir das tabelas acima (`fig01_classificacao.png` …
`fig12_placares.png`), prontos para inserir no TCC.

## Limitações dos dados

- `tecnico_mandante` / `tecnico_visitante` não são confiáveis: na maioria dos jogos aparece o
  técnico atual de cada clube em todas as 38 rodadas (ex.: o mesmo nome da rodada 1 à 38 em
  times que trocaram de técnico em 2025), e os nomes não seguem um padrão. Por isso não há
  análise por técnico.
- A rodada é a da tabela oficial; jogos adiados aparecem na rodada original.

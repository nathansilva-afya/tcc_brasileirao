# Documentação das análises — Brasileirão Série A 2025

Cada seção descreve uma análise do projeto: o que ela responde, em que parte do referencial
teórico se apoia, como é calculada, quais arquivos gera e o que os dados de 2025 mostram.

- **Tabelas**: `data/analytics/<nome>.csv` (cópia para Excel pt-BR em `data/exports/`).
- **Figuras**: `figuras/<nome>.png`.
- **Código**: funções de mesmo nome em `src/analytics.py` (tabelas) e `src/figuras.py` (gráficos).
- **Reprodução**: `make pipeline` recria tudo a partir de `data/raw/`.

Base: 380 partidas, 20 clubes, 38 rodadas (29/03/2025 a 07/12/2025). A classificação
calculada confere com a oficial da CBF (posições e pontos).

## Sumário

| # | Análise | Tabela | Figura |
|---|---|---|---|
| 1 | Classificação e indicadores de resultado | `classificacao` | `fig01_classificacao` |
| 2 | Correlação dos indicadores com os pontos | `correlacoes` | — |
| 3 | Ataque x defesa | `classificacao` | `fig06_ataque_defesa` |
| 4 | Placares mais frequentes | `placares` | `fig12_placares` |
| 5 | Vantagem do mando no campeonato | `resumo_temporada` | `fig02_resultados_mando` |
| 6 | Vantagem do mando por time | `desempenho_mando`, `diferenca_mando` | `fig03_casa_fora` |
| 7 | Distância entre as sedes | `mando_distancia` | `fig10_distancia` |
| 8 | Arrecadação x desempenho | `eficiencia_arrecadacao`, `correlacoes` | `fig07_arrecadacao_pontos` |
| 9 | Eficiência: pontos por milhão arrecadado | `eficiencia_arrecadacao` | `fig08_pontos_por_milhao` |
| 10 | Arrecadação x resultado do jogo | `arrecadacao_resultado` | `fig09_arrecadacao_resultado` |
| 11 | Evolução ao longo das rodadas | `evolucao_rodadas` | `fig05_evolucao_pontos` |
| 12 | 1º turno x 2º turno | `desempenho_turno` | `fig04_turnos` |
| 13 | Esquemas táticos | `formacoes` | `fig11_formacoes` |
| 14 | Faixa de horário | `horario` | — |
| — | Análise descartada: técnicos | — | — |

## Conceitos usados em várias análises

- **Pontos**: 3 por vitória, 1 por empate.
- **Aproveitamento**: pontos ÷ (jogos × 3). Permite comparar recortes com número diferente de
  jogos (casa x fora, turnos, formações), como recomendam Hughes e Bartlett (2002).
- **Formato longo (`partidas_por_time`)**: cada partida vira duas linhas, uma para o mandante e
  outra para o visitante (760 linhas). É a base de quase todas as tabelas por time.
- **Correlação de Spearman (ρ)**: correlação entre os *postos* (rankings) de duas variáveis;
  vai de −1 a 1. Foi escolhida por não exigir relação linear nem distribuição normal e por ser
  pouco sensível a valores extremos (ex.: a arrecadação do Flamengo). Com n = 20 times, o valor
  crítico bilateral para α = 0,05 é aproximadamente 0,45 (conferir em tabela de valores críticos
  de Spearman antes de citar).
- **Percentuais de resultado**: % de vitória do mandante (M), empate (E) e vitória do visitante
  (V) sempre somam 100% dentro de cada grupo.

---

## 1. Classificação e indicadores de resultado

**Pergunta**: qual foi o desempenho final de cada clube?

**Referencial**: indicadores de resultado de Hughes e Bartlett (2002); formato de pontos
corridos (seção 2.6).

**Cálculo**: soma de vitórias, empates, derrotas, gols pró, gols contra e pontos por time.
Desempate: pontos, vitórias, saldo de gols, gols pró. Não considera punições do STJD (em 2025
não houve diferença em relação à tabela oficial).

**Saídas**: `classificacao.csv` — `posicao, time, jogos, vitorias, empates, derrotas, gols_pro,
gols_contra, saldo_gols, pontos, aproveitamento`. Figura `fig01_classificacao.png` (barras com
as linhas do G6 e do Z4).

**Resultados**:
- Flamengo campeão com 79 pontos (69,3% de aproveitamento), seguido de Palmeiras (76) e
  Cruzeiro (70).
- Mirassol, em sua primeira Série A, terminou em 4º (67 pontos).
- Rebaixados: Ceará (43), Fortaleza (43), Juventude (35) e Sport (17).
- Bragantino (10º) e Atlético-MG (11º) empataram com 48 pontos; o Bragantino fica à frente por
  ter mais vitórias (14 x 12).

---

## 2. Correlação dos indicadores com os pontos

**Pergunta**: quais indicadores mais se associam à pontuação final?

**Referencial**: Hughes e Bartlett (2002); Anderson e Sally (2013), sobre o saldo de gols como
medida mais estável da qualidade de uma equipe.

**Cálculo**: Spearman entre os pontos finais e cada indicador, com n = 20 times.

**Saídas**: `correlacoes.csv` — `indicador, spearman_com_pontos`.

**Resultados**:

| Indicador | ρ com os pontos |
|---|---|
| Saldo de gols | 0,95 |
| Gols sofridos | −0,86 |
| Gols marcados | 0,85 |
| Arrecadação média como mandante | 0,50 |

**Leitura**: o saldo de gols praticamente ordena a tabela. Defesa e ataque têm peso
semelhante, com leve vantagem para a defesa. A arrecadação tem associação moderada (ver
análise 8).

**Cuidados**: correlação não indica causa. O saldo é, em parte, consequência dos mesmos jogos
que geram os pontos.

---

## 3. Ataque x defesa

**Pergunta**: como os clubes se distribuem entre eficiência ofensiva e defensiva?

**Referencial**: indicadores de resultado (Hughes; Bartlett, 2002).

**Cálculo**: gols marcados (eixo X) e sofridos (eixo Y) de cada time, a partir de
`classificacao.csv`. Média do campeonato: 47,95 gols marcados e 47,95 sofridos por time.

**Saídas**: `fig06_ataque_defesa.png` (dispersão com o nome de cada clube).

**Resultados**:
- Flamengo isolado no canto ideal: melhor ataque (78) e melhor defesa (27).
- Palmeiras (66 x 33) e Cruzeiro (55 x 31) formam o grupo seguinte.
- Sport (28 x 75) e Juventude (35 x 69) no extremo oposto.
- Vasco marcou acima da média (55), mas sofreu 60 gols e terminou em 14º.

---

## 4. Placares mais frequentes

**Pergunta**: como os gols se distribuem nos jogos?

**Referencial**: Reep e Benjamin (1968) e Anderson e Sally (2013), sobre o gol como evento raro
e o peso do acaso; Maher (1982), sobre a modelagem dos gols.

**Cálculo**: contagem de cada placar `gols_mandante x gols_visitante`.

**Saídas**: `placares.csv` — `placar, jogos, pct`. Figura `fig12_placares.png` (10 mais
frequentes).

**Resultados**: 959 gols, média de 2,52 por jogo. Placares mais comuns: 1x0 (53 jogos; 13,9%),
1x1 (46; 12,1%), 2x1 (37; 9,7%), 2x0 (33; 8,7%) e 0x0 (27; 7,1%).

**Leitura**: a maioria dos jogos é decidida por um gol ou termina empatada, o que reforça a
necessidade de analisar a temporada inteira, e não partidas isoladas.

---

## 5. Vantagem do mando no campeonato

**Pergunta**: existe vantagem de jogar em casa no Brasileirão 2025?

**Referencial**: Pollard (1986); Courneya e Carron (1992); Nevill e Holder (1999); estudos
brasileiros de Silva, Medeiros e Silva (2010) e Almeida, Oliveira e Silva (2011).

**Cálculo**:
- Distribuição dos resultados (M/E/V) nas 380 partidas.
- `pct_pontos_casa` (medida de Pollard): pontos conquistados pelos mandantes ÷ total de pontos
  conquistados. Sem vantagem de mando, o valor esperado seria 50%.

**Saídas**: `resumo_temporada.csv` (1 linha). Figura `fig02_resultados_mando.png`.

**Resultados**:
- Vitória do mandante: 50,3%; empate: 26,1%; vitória do visitante: 23,7%.
- Os mandantes conquistaram **64,6% dos pontos**.

**Leitura**: a vantagem é clara e quase igual aos cerca de 64% encontrados por Pollard (1986)
no futebol inglês. O mandante vence mais que o dobro de vezes que o visitante.

---

## 6. Vantagem do mando por time

**Pergunta**: a vantagem de jogar em casa é igual para todos os clubes?

**Referencial**: o mesmo da análise 5.

**Cálculo**: aproveitamento de cada time em casa e fora (19 jogos em cada); `diferenca` =
aproveitamento em casa − aproveitamento fora; `pct_pontos_casa` do time.

**Saídas**: `desempenho_mando.csv` (time x mando, com todas as métricas) e
`diferenca_mando.csv` — `aproveitamento_casa, aproveitamento_fora, pontos_casa, pontos_fora,
diferenca, pct_pontos_casa`. Figura `fig03_casa_fora.png` (halteres ordenados pela diferença).

**Resultados**:
- Todos os 20 clubes renderam mais em casa.
- Maiores diferenças: Bahia (79% em casa x 26% fora; 75% dos pontos em casa), Fluminense
  (81% x 32%) e Atlético-MG (61% x 23%).
- Menores diferenças: Palmeiras (72% x 61%) e Sport (18% x 12%).
- Flamengo teve o melhor aproveitamento em casa (82%) e o 2º melhor fora (56%).

**Leitura**: os primeiros colocados se diferenciam pelo desempenho **fora** de casa. Palmeiras e
Flamengo foram os únicos acima de 50% como visitantes. Clubes como Bahia e Fluminense dependem
muito do mando.

---

## 7. Distância entre as sedes

**Pergunta**: a distância da viagem do visitante influencia o resultado?

**Referencial**: fator "viagem" do modelo de Courneya e Carron (1992); Pollard e Pollard (2005).

**Cálculo**: cada jogo é classificado pela UF dos clubes em *mesmo estado*, *mesma região*
(estados diferentes da mesma região do IBGE) ou *outra região*. O mapa UF → região está em
`config.REGIAO`.

**Saídas**: `mando_distancia.csv` — `distancia, jogos, media_gols, pct_vitoria_mandante,
pct_empate, pct_vitoria_visitante`. Figura `fig10_distancia.png`.

**Resultados**:

| Distância | Jogos | Vitória mandante | Empate | Vitória visitante |
|---|---|---|---|---|
| Mesmo estado | 54 | 53,7% | 25,9% | 20,4% |
| Mesma região | 104 | 50,0% | 28,8% | 21,1% |
| Outra região | 222 | 49,5% | 24,8% | 25,7% |

**Leitura**: não há sinal de que viajar mais longe prejudique o visitante. Ele venceu um pouco
mais nos jogos entre regiões diferentes. As diferenças são pequenas e não confirmam o fator
viagem em 2025.

**Cuidados**: a UF é uma aproximação grosseira da distância; não considera km, altitude nem
clima. O grupo "mesmo estado" tem só 54 jogos e inclui clássicos estaduais.

---

## 8. Arrecadação x desempenho

**Pergunta**: os clubes que mais arrecadam são os que mais pontuam?

**Referencial**: seção 2.5 — Leoncini e Silva (2005), Kuper e Szymanski (2009), Dobson e
Goddard (2001), García e Rodríguez (2002), Madalozzo e Villar (2009).

**Cálculo**: arrecadação média e total de cada time nos 19 jogos como mandante; Spearman com os
pontos finais.

**Saídas**: `eficiencia_arrecadacao.csv` — `arrecadacao_total, arrecadacao_media, posicao,
pontos, aproveitamento, aproveitamento_casa, pontos_por_milhao`. Figura
`fig07_arrecadacao_pontos.png`.

**Resultados**:
- ρ = 0,50: associação positiva e moderada.
- Maiores médias por jogo: Flamengo (R$ 4,30 mi), Corinthians (R$ 2,85 mi), Palmeiras
  (R$ 2,51 mi), Cruzeiro (R$ 2,37 mi).
- Menores: Bragantino (R$ 0,18 mi), Mirassol (R$ 0,39 mi), Juventude (R$ 0,46 mi).
- Exceções: Corinthians, 2ª maior bilheteria e 13º lugar; Mirassol, 19ª bilheteria e 4º lugar.

**Leitura**: três das quatro maiores bilheterias são dos três primeiros colocados, o que sugere o ciclo
receita → elenco → resultado (Dobson; Goddard, 2001), mas as exceções mostram que a receita
não determina sozinha o desempenho (Kuper; Szymanski, 2009).

**Cuidados**: a arrecadação é só a bilheteria. Não inclui direitos de transmissão, patrocínio
nem venda de atletas, e depende do tamanho do estádio e do preço do ingresso. É uma
aproximação limitada do poder financeiro.

---

## 9. Eficiência: pontos por milhão arrecadado

**Pergunta**: quais clubes converteram melhor sua receita de bilheteria em pontos?

**Referencial**: eficiência e análise envoltória de dados (Barros; Leach, 2006;
Dantas; Boente, 2011); *Moneyball* (Lewis, 2003).

**Cálculo**: `pontos_por_milhao` = pontos totais ÷ (arrecadação total como mandante em
R$ milhões).

**Saídas**: coluna `pontos_por_milhao` de `eficiencia_arrecadacao.csv`. Figura
`fig08_pontos_por_milhao.png`.

**Resultados**:
- Mais eficientes: Bragantino (13,74), Mirassol (9,02), Botafogo (4,06), Vitória (4,05).
- Menos eficientes: Corinthians (0,87), Flamengo (0,97), Sport (1,27), Vasco (1,45).

**Leitura**: o Mirassol é o caso mais forte para o TCC, pois combina alta eficiência com
desempenho de topo (4º). O Flamengo aparece entre os "menos eficientes" porque arrecada muito,
mas é campeão; eficiência e resultado são dimensões diferentes.

**Cuidados**: é um indicador simplificado, não uma DEA. O valor do Bragantino reflete, em
grande parte, o estádio pequeno e a baixa bilheteria, não necessariamente um orçamento menor
(o clube tem investimento de grupo empresarial). Para uma análise de eficiência real, seria
preciso a receita total ou a folha salarial (ex.: relatórios financeiros dos clubes).

---

## 10. Arrecadação x resultado do jogo

**Pergunta**: jogos com maior renda terminam mais vezes em vitória do mandante?

**Referencial**: torcida como fator da vantagem do mando (Nevill; Holder, 1999;
McCarrick *et al.*, 2021); determinantes de público (García; Rodríguez, 2002).

**Cálculo**: as 380 partidas são divididas em quartis de arrecadação (95 jogos cada; Q1 = 25%
de menor renda, Q4 = 25% de maior renda) e se calcula a distribuição de resultados em cada um.

**Saídas**: `arrecadacao_resultado.csv` — `quartil, arrecadacao_min, arrecadacao_max, jogos,
media_gols, pct_vitoria_mandante, pct_empate, pct_vitoria_visitante`. Figura
`fig09_arrecadacao_resultado.png`.

**Resultados**:

| Quartil | Faixa (R$ mi) | Vitória mandante | Empate | Vitória visitante |
|---|---|---|---|---|
| Q1 | 0,06 – 0,47 | 46,3% | 29,5% | 24,2% |
| Q2 | 0,47 – 0,99 | 47,4% | 24,2% | 28,4% |
| Q3 | 1,00 – 1,91 | 51,6% | 24,2% | 24,2% |
| Q4 | 1,93 – 5,98 | 55,8% | 26,3% | 17,9% |

**Leitura**: a vitória do mandante cresce de forma consistente com a renda, e a do visitante
cai para 17,9% no quartil mais alto.

**Cuidados**: há confusão de variáveis. Os jogos de maior renda são, em geral, de clubes
grandes e mais fortes (Flamengo, Palmeiras, Corinthians, Cruzeiro). Não é possível separar o
efeito da torcida do efeito da qualidade do time só com esses dados.

---

## 11. Evolução ao longo das rodadas

**Pergunta**: como foi a disputa ao longo da temporada?

**Referencial**: indicadores de resultado; acompanhamento contínuo do desempenho
(Carling; Williams; Reilly, 2005).

**Cálculo**: pontos, saldo e posição acumulados por time ao fim de cada rodada, com os mesmos
critérios de desempate da classificação final.

**Saídas**: `evolucao_rodadas.csv` — `rodada, time, pontos, pontos_acumulados,
saldo_acumulado, posicao` (760 linhas). Figura `fig05_evolucao_pontos.png` (Flamengo,
Palmeiras e Cruzeiro em destaque, demais em cinza).

**Resultados**:
- O Flamengo liderou ao fim de 27 das 38 rodadas; o Palmeiras, de 9; Fortaleza (rodada 1) e
  Corinthians (rodada 2), de uma cada.
- Entre as rodadas 27 e 35 a liderança trocou de mãos seis vezes entre Flamengo e
  Palmeiras; o Flamengo assumiu de vez na rodada 35.

**Cuidados**: a rodada é a da tabela oficial. Jogos adiados aparecem na rodada original, então
a posição "ao fim da rodada X" pode não coincidir com a tabela publicada na data.

---

## 12. 1º turno x 2º turno

**Pergunta**: quais clubes melhoraram ou pioraram ao longo da temporada?

**Referencial**: indicadores normalizados (Hughes; Bartlett, 2002).

**Cálculo**: pontos e aproveitamento nas rodadas 1–19 (1º turno) e 20–38 (2º turno);
`variacao_pontos` = 2º turno − 1º turno.

**Saídas**: `desempenho_turno.csv`. Figura `fig04_turnos.png` (halteres ordenados pela
variação).

**Resultados**:
- Maiores altas: Fortaleza (+11; 16 → 27), Fluminense (+10; 27 → 37), Vitória (+9), Grêmio e
  Vasco (+7).
- Maiores quedas: Atlético-MG (−8; 28 → 20), Flamengo (−7; 43 → 36), Bahia e Bragantino (−6).
- O Fortaleza fez 27 pontos no returno (8º melhor, empatado com Vitória e Bahia), mas não
  evitou o rebaixamento por causa do 1º turno fraco (16 pontos, o 2º pior).

**Cuidados**: mudanças de técnico, elenco e calendário (Copa do Brasil, Libertadores) podem
explicar as variações, mas não estão na base de forma confiável (ver "Análise descartada").

---

## 13. Esquemas táticos

**Pergunta**: algum esquema tático rende mais?

**Referencial**: análise de jogo e variáveis situacionais (Sarmento *et al.*, 2014).

**Cálculo**: aproveitamento agregado por formação inicial de cada time em cada jogo. Só entram
formações com 20 jogos ou mais (`MIN_JOGOS_FORMACAO`), para evitar conclusões com amostra
pequena.

**Saídas**: `formacoes.csv` — métricas da classificação por formação e `pct_jogos`. Figura
`fig11_formacoes.png`.

**Resultados**:

| Formação | Jogos | % das escalações | Aproveitamento |
|---|---|---|---|
| 4-2-3-1 | 452 | 59,5% | 47,6% |
| 4-3-3 | 108 | 14,2% | 44,1% |
| 4-4-2 | 45 | 5,9% | 45,2% |
| 3-4-2-1 | 42 | 5,5% | 43,6% |
| 3-4-1-2 | 26 | 3,4% | 47,4% |

**Leitura**: o 4-2-3-1 domina o campeonato, e o aproveitamento quase não muda entre os esquemas
(diferença de 4 pontos percentuais). A formação, sozinha, não explica o desempenho.

**Cuidados**: a formação é a inicial registrada na fonte, não a usada durante o jogo. Times
melhores usam mais o 4-2-3-1, o que também influencia o resultado.

---

## 14. Faixa de horário

**Pergunta**: o horário do jogo se relaciona com gols ou com a vantagem do mando?

**Cálculo**: jogos agrupados em *antes das 17h*, *17h–18h* e *19h ou mais*.

**Saídas**: `horario.csv` (sem figura; análise complementar).

**Resultados**:

| Faixa | Jogos | Média de gols | Vitória mandante |
|---|---|---|---|
| Antes das 17h | 90 | 2,52 | 54,4% |
| 17h–18h | 106 | 2,65 | 48,1% |
| 19h ou mais | 184 | 2,45 | 49,5% |

**Leitura**: as diferenças são pequenas. O horário não parece relevante em 2025; serve no
máximo como nota de rodapé.

---

## Análise descartada: técnicos

A ideia era comparar o aproveitamento antes e depois das trocas de técnico. Ela foi descartada
porque a coluna `tecnico_mandante` / `tecnico_visitante` não é confiável:

- Na maioria dos jogos aparece o técnico **atual** de cada clube em todas as 38 rodadas
  (ex.: Tite no Cruzeiro e Vojvoda no Santos desde a rodada 1, embora os dois clubes tenham
  tido outros técnicos em 2025).
- Os nomes não seguem um padrão (ex.: "F. Luís" e "Filipe Luis Kasmirski"), e há erro de
  codificação ("ZubeldÃ­a").

Isso deve ser citado na Metodologia como limitação da fonte de dados.

## Limitações gerais

- Fonte única (dataset público do Kaggle), sem estatísticas de jogo (posse, finalizações, xG)
  nem público pagante.
- A única variável financeira é a bilheteria; não há dados de receita total, folha salarial ou
  investimento.
- Uma única temporada: as análises são descritivas e correlacionais e não permitem conclusões
  de causa e efeito nem generalização para outros anos.

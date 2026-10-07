# Brasileirão Série A — Pipeline e Análise de Dados (TCC)

Pipeline de engenharia de dados para análise do Campeonato Brasileiro Série A de **2025**
(380 jogos, 38 rodadas, 20 times), a partir do dataset público
[adaoduque/campeonato-brasileiro-de-futebol](https://www.kaggle.com/datasets/adaoduque/campeonato-brasileiro-de-futebol).

## Fontes

O dataset do Kaggle tem 4 arquivos e o pipeline baixa todos:

| Arquivo (raw) | Tabela (processed) | Conteúdo | Dados de 2025 |
|---|---|---|---|
| `campeonato-brasileiro-full.csv` | `partidas` | uma linha por jogo: placar, estádio, técnicos, formações | 380 jogos |
| `campeonato-brasileiro-gols.csv` | `gols` | um gol por linha: atleta, clube, minuto, tipo | 959 gols |
| `campeonato-brasileiro-estatisticas-full.csv` | `estatisticas` | por time e por jogo: chutes, posse, passes, faltas, cartões, escanteios | 380 jogos (760 linhas) |
| `campeonato-brasileiro-cartoes.csv` | `cartoes` | um cartão por linha: atleta, posição, minuto | **nenhum** (a fonte vai só até 2024) |

## Arquitetura

O projeto segue a arquitetura em camadas (medallion):

```
Kaggle ──extract──▶ data/raw ──transform + validate──▶ data/processed ──analytics──▶ data/analytics
 (fonte)             (bronze)                           (silver)                      (gold)
                                                                                         │
                                                                         data/exports ◀──┘ (Excel pt-BR)
```

| Camada | Pasta | Conteúdo |
|---|---|---|
| Bronze | `data/raw/` | Os 4 CSVs do Kaggle, apenas as linhas de 2025 (valores sem alterações) |
| Silver | `data/processed/` | `partidas`, `gols`, `cartoes` e `estatisticas`: limpos e tipados |
| Gold | `data/analytics/` | Tabelas agregadas para análise (classificação, mando, artilharia, estatísticas…) |
| Databricks | `workspace.brasileirao` | As tabelas gold como tabelas Delta no Unity Catalog (opcional, `make databricks`) |
| Export | `data/exports/` | Mesmas tabelas em CSV `;` / UTF-8 com BOM, para abrir no Excel |

## Estrutura

```
├── data/               # camadas de dados (processed/analytics/exports são geradas)
├── docs/               # dicionário de dados
├── notebooks/          # análises exploratórias (células # %% do VS Code)
├── src/
│   ├── config.py       # caminhos e parâmetros
│   ├── extract.py      # download do Kaggle
│   ├── transform.py    # limpeza e padronização
│   ├── validate.py     # checagens de qualidade
│   ├── analytics.py    # tabelas gold
│   ├── load.py         # gravação em disco
│   ├── publish.py      # tabelas gold no Databricks (Unity Catalog)
│   └── pipeline.py     # orquestração
├── tests/              # testes automatizados (pytest)
├── Makefile
└── requirements.txt
```

## Como executar

Requer **Python 3.11 ou mais novo** (o pandas 3 não roda em versões anteriores). O `.venv`
do projeto usa o Python 3.12 do Anaconda:

```bash
/opt/anaconda3/bin/python3.12 -m venv .venv   # ou qualquer python >= 3.11
make install     # instala dependências
make pipeline    # roda o pipeline completo
make test        # roda os testes
```

Sem `make`: `.venv/bin/python -m src.pipeline`. Para baixar o dataset de novo do Kaggle:
`make download`.

No VS Code, selecione o interpretador `.venv/bin/python` (Python: Select Interpreter).

### Publicar no Databricks (Free Edition)

`make databricks` roda o pipeline e cria (ou recria) cada tabela gold como tabela Delta em
`workspace.brasileirao`, usando o SQL warehouse serverless do workspace. Tudo roda da
máquina local; não é preciso abrir notebook nem cluster.

1. No Databricks: avatar > **Settings** > **Developer** > **Access tokens** > *Generate new token*.
2. Crie `~/.databrickscfg` (fora do repositório, o token não vai para o git):

   ```ini
   [DEFAULT]
   host  = https://<seu-workspace>.cloud.databricks.com
   token = dapi...
   ```

3. `make install` (instala o `databricks-sdk`) e `make databricks`.

Para publicar o que já está em `data/analytics` sem rodar o pipeline: `.venv/bin/python -m src.publish`.
Catálogo, schema e warehouse podem ser trocados com as variáveis `DATABRICKS_CATALOG`,
`DATABRICKS_SCHEMA` e `DATABRICKS_WAREHOUSE_ID` (padrão: `workspace`, `brasileirao` e o
primeiro warehouse do workspace).

As tabelas `bilheteria`, `scout` e `posse_bola` são as que os notebooks `01_limpeza` e
`02_limpeza` geravam no Databricks; a lógica agora está em `src/analytics.py`.

### Versionamento (git)

Só vão para o repositório o código e os dados brutos (`data/raw/`). As pastas
`data/processed/`, `data/analytics/` e `data/exports/` estão no `.gitignore` porque são
geradas pelo pipeline: quem clonar o projeto recria tudo com `make pipeline`. Os arquivos
`.gitkeep` servem só para manter essas pastas vazias no repositório.

## Tratamentos aplicados

- Somente a temporada 2025 (`TEMPORADA` em `src/config.py`) é mantida: o download grava só
  os jogos de 2025 no bronze e a transformação filtra de novo pela temporada.
- Leitura em UTF-8. Espaços não separáveis (`\xa0`) são removidos e as pontas são aparadas.
- As colunas são renomeadas (`rodata` → `rodada`, `mandante_Placar` → `gols_mandante`…).
- A coluna `temporada` é derivada da data (jogos de jan/fev contariam para a temporada anterior).
- Colunas derivadas: `resultado` (M/E/V) e `total_gols`. Quando há empate, `vencedor` fica nulo.
- Validações das partidas: `id` único, colunas obrigatórias sem nulos, placares não
  negativos, `vencedor` coerente com o placar e UF válida.
- Gols, cartões e estatísticas são filtrados pelos IDs das partidas de 2025 e ganham as
  colunas `mando` (casa/fora) e `adversario`.
- Minutos como `90+4` são separados em `minuto` (90), `acrescimo` (4) e `tempo` (1º/2º).
- Gols: `Penalty`/`Gol Contra` viram `Pênalti`/`Gol contra` (os demais, `Normal`). Em gol
  contra, `clube` é o time **beneficiado**. A validação confere se os gols de cada clube batem
  com o placar de todas as partidas.
- Estatísticas: `"64%"` vira `64`. Partidas com 0 passes (erro da fonte) ficam com `passes` nulo.

## Limitações conhecidas

- A classificação é recalculada a partir dos jogos e **não considera punições do STJD**.
  Por isso as posições podem divergir da tabela oficial.
- **Não há cartões individuais de 2025** na fonte (o arquivo de cartões termina em 2024).
  O pipeline baixa e processa o arquivo mesmo assim, mas `cartoes` e `cartoes_por_atleta`
  ficam vazios. Para disciplina, use `cartao_amarelo`/`cartao_vermelho` de `estatisticas`
  (totais por time e por jogo). Se o autor do dataset publicar 2025, basta rodar
  `make download`.
- Estatísticas com valores ausentes: 12 de posse de bola, 8 de precisão de passe e 7 de passes.

# Brasileirão Série A — Pipeline e Análise de Dados (TCC)

Pipeline de engenharia de dados para análise do Campeonato Brasileiro Série A de **2025**
(380 jogos, 38 rodadas, 20 times), a partir do dataset público
[adaoduque/campeonato-brasileiro-de-futebol](https://www.kaggle.com/datasets/adaoduque/campeonato-brasileiro-de-futebol).

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
| Bronze | `data/raw/` | CSV original, apenas as linhas de 2025 (valores sem alterações) |
| Silver | `data/processed/` | `partidas.csv`: uma linha por partida, limpa e tipada |
| Gold | `data/analytics/` | Tabelas agregadas para análise (classificação, mando, resumo) |
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
│   └── pipeline.py     # orquestração
├── tests/              # testes automatizados (pytest)
├── Makefile
└── requirements.txt
```

## Como executar

```bash
python3 -m venv .venv
make install     # instala dependências
make pipeline    # roda o pipeline completo
make test        # roda os testes
```

Sem `make`: `.venv/bin/python -m src.pipeline`. Para baixar o dataset de novo do Kaggle:
`make download`.

No VS Code, selecione o interpretador `.venv/bin/python` (Python: Select Interpreter).

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
- Validações: `id` único, colunas obrigatórias sem nulos, placares não negativos, `vencedor`
  coerente com o placar e UF válida.

## Limitações conhecidas

- A classificação é recalculada a partir dos jogos e **não considera punições do STJD**.
  Por isso as posições podem divergir da tabela oficial.

import pandas as pd
import pytest

from src import analytics, transform, validate


@pytest.fixture
def bruto():
    return pd.DataFrame({
        "ID": [1, 2, 3],
        "rodata": [1, 1, 38],
        "data": ["29/03/2025", "29/03/2025", "07/12/2025"],
        "hora": ["16:00"] * 3,
        "mandante": ["Flamengo", "Santos", "Flamengo"],
        "visitante": ["Vasco", "Palmeiras", "Santos"],
        "formacao_mandante": [None] * 3,
        "formacao_visitante": [None] * 3,
        "tecnico_mandante": [None] * 3,
        "tecnico_visitante": [None] * 3,
        "vencedor": ["Flamengo", "-", "Santos"],
        "arena": ["\xa0Maracanã", "\xa0Vila Belmiro ", "Maracanã"],
        "mandante_Placar": [2, 1, 0],
        "visitante_Placar": [0, 1, 1],
        "mandante_Estado": ["RJ", "SP", "RJ"],
        "visitante_Estado": ["RJ", "SP", "SP"],
        "arrecadacao": [None, 1000.5, None],
    })


def test_limpa_espaco_nao_separavel(bruto):
    df = transform.transformar(bruto)
    assert set(df["arena"]) == {"Maracanã", "Vila Belmiro"}


def test_mantem_apenas_2025(bruto):
    outra = bruto.iloc[[0]].assign(ID=4, data="08/12/2024")
    df = transform.transformar(pd.concat([bruto, outra], ignore_index=True))
    assert (df["temporada"] == 2025).all()
    assert set(df["id_partida"]) == {1, 2, 3}


def test_resultado_e_empate(bruto):
    df = transform.transformar(bruto).set_index("id_partida")
    assert df.loc[1, "resultado"] == "M"
    assert df.loc[2, "resultado"] == "E" and pd.isna(df.loc[2, "vencedor"])
    assert df.loc[3, "resultado"] == "V"


def test_validacao_passa(bruto):
    validate.validar(transform.transformar(bruto))


def test_validacao_detecta_vencedor_incoerente(bruto):
    bruto.loc[0, "vencedor"] = "Vasco"
    with pytest.raises(validate.ErroQualidade):
        validate.validar(transform.transformar(bruto))


def test_classificacao(bruto):
    tabelas = analytics.construir(transform.transformar(bruto))
    tab = tabelas["classificacao"].set_index("time")
    assert tab.loc["Santos", "pontos"] == 4      # empate + vitória fora
    assert tab.loc["Santos", "posicao"] == 1
    assert tab.loc["Flamengo", "pontos"] == 3
    assert len(tabelas["partidas_por_time"]) == 2 * len(bruto)


@pytest.fixture
def partidas(bruto):
    return transform.transformar(bruto)


def test_minuto_com_acrescimo():
    m = transform.separar_minuto(pd.Series(["31", "45+3", "90+12", "46"]))
    assert m["minuto"].tolist() == [31, 45, 90, 46]
    assert m["acrescimo"].tolist() == [0, 3, 12, 0]
    assert m["tempo"].tolist() == [1, 1, 2, 2]


def test_gols_validam_contra_placar(partidas):
    gols_bruto = pd.DataFrame({
        "partida_id": [1, 1, 2, 2, 3, 999],
        "rodata": [1, 1, 1, 1, 38, 1],
        "clube": ["Flamengo", "Flamengo", "Santos", "Palmeiras", "Santos", "Vasco"],
        "atleta": ["Pedro", "Zagueiro do Vasco", "A", "B", "C", "fora da temporada"],
        "minuto": ["10", "90+2", "5", "60", "45+1", "1"],
        "tipo_de_gol": [None, "Gol Contra", "Penalty", None, None, None],
    })
    gols = transform.transformar_gols(gols_bruto, partidas)
    assert len(gols) == 5                                    # partida 999 não é da temporada
    assert gols.loc[gols["atleta"] == "C", "mando"].item() == "fora"
    validate.validar_gols(gols, partidas)

    art = analytics.artilharia(gols)
    assert "Zagueiro do Vasco" not in set(art["atleta"])     # gol contra não entra na artilharia

    with pytest.raises(validate.ErroQualidade):              # gol a menos -> não bate com o placar
        validate.validar_gols(gols.iloc[1:], partidas)


def test_estatisticas(partidas):
    est_bruto = pd.DataFrame({
        "partida_id": [1, 1],
        "rodata": [1, 1],
        "clube": ["Flamengo", "Vasco"],
        "chutes": [10, 4], "chutes_no_alvo": [5, 1],
        "posse_de_bola": ["64%", "36%"], "passes": [500, 0], "precisao_passes": ["90%", None],
        "faltas": [10, 12], "cartao_amarelo": [1, 3], "cartao_vermelho": [0, 1],
        "impedimentos": [2, 0], "escanteios": [6, 2],
    })
    est = transform.transformar_estatisticas(est_bruto, partidas)
    assert est["posse_de_bola"].tolist() == [64, 36]
    assert pd.isna(est.loc[est["clube"] == "Vasco", "passes"].item())   # 0 passes = erro da fonte
    validate.validar_estatisticas(est, partidas)

    tabelas = analytics.construir(partidas, estatisticas=est)
    fla = tabelas["estatisticas_time"].set_index("time").loc["Flamengo"]
    assert fla["conversao_chutes"] == 0.2                    # 2 gols em 10 chutes


def test_cartoes_vazios_nao_quebram(partidas):
    vazio = pd.DataFrame(columns=["partida_id", "rodata", "clube", "cartao", "atleta",
                                  "num_camisa", "posicao", "minuto"])
    cartoes = transform.transformar_cartoes(vazio, partidas)
    validate.validar_cartoes(cartoes, partidas)
    assert analytics.cartoes_por_atleta(cartoes).empty


def test_tabelas_dos_notebooks(partidas):
    est = transform.transformar_estatisticas(pd.DataFrame({
        "partida_id": [1, 1, 2, 2, 3, 3], "rodata": [1, 1, 1, 1, 38, 38],
        "clube": ["Flamengo", "Vasco", "Santos", "Palmeiras", "Flamengo", "Santos"],
        "chutes": [10, 4, 5, 5, 6, 8], "chutes_no_alvo": [4, 1, 2, 2, 3, 4],
        "posse_de_bola": ["60%", "40%", "50%", "50%", "60%", "40%"], "passes": [500] * 6,
        "precisao_passes": ["90%"] * 6, "faltas": [10] * 6, "cartao_amarelo": [1] * 6,
        "cartao_vermelho": [0] * 6, "impedimentos": [0] * 6, "escanteios": [3] * 6,
    }), partidas)
    gols = transform.transformar_gols(pd.DataFrame({
        "partida_id": [1, 1, 2, 2, 3], "rodata": [1, 1, 1, 1, 38],
        "clube": ["Flamengo", "Flamengo", "Santos", "Palmeiras", "Santos"],
        "atleta": ["Pedro", "Pedro", "A", "B", "C"], "minuto": ["10", "20", "5", "60", "45"],
        "tipo_de_gol": [None] * 5,
    }), partidas)
    tabelas = analytics.construir(partidas, gols=gols, estatisticas=est)

    scout = tabelas["scout"].set_index("atleta")
    assert scout.loc["Pedro", "gols_do_jogador"] == 2
    assert scout.loc["Pedro", "eficiencia_clube_pct"] == 28.57    # 2 gols em 7 chutes no alvo

    # posse 60%: Flamengo venceu o jogo 1 e perdeu o 3 -> 50%; abaixo de 4 jogos sai
    assert analytics.posse_bola(partidas, est, minimo_jogos=1).set_index("posse_de_bola") \
        .loc[60, "taxa_vitoria_pct"] == 50
    assert tabelas["posse_bola"].empty

    bil = analytics.bilheteria(partidas, minimo_jogos=1)
    assert bil[["dia_da_semana", "hora_oficial", "qtd_jogos"]].values.tolist() == [["Saturday", "16:00", 1]]


def test_sql_do_databricks():
    from src import publish
    df = pd.DataFrame({
        "time": ["Grêmio", "Vasco D'Gama", None],
        "pontos": pd.array([1, 2, None], dtype="Int64"),
        "media": [0.5, float("nan"), 1e-05],
        "data": pd.to_datetime(["2025-03-29", "2025-12-07", None]),
    })
    criar, inserir = publish.comandos_sql(df, "t")
    assert criar == "CREATE OR REPLACE TABLE t (`time` STRING, `pontos` BIGINT, `media` DOUBLE, `data` DATE)"
    assert "('Vasco D\\'Gama', 2, NULL, DATE'2025-12-07')" in inserir
    assert "(NULL, NULL, 1e-05, NULL)" in inserir

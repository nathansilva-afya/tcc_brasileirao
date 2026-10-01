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

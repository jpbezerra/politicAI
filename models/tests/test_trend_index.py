import sys
from pathlib import Path

import numpy as np
import pandas as pd

from models_pkg.forecasting.trend_index import compute_trend_index

# Insere scripts/ no sys.path só para este teste de consistência (mesmo
# mecanismo usado pelos geradores de notebook) -- ver
# models_pkg/forecasting/trend_index.py, nota "ACOPLAMENTO DE CAMINHO
# ASSUMIDO", e docs/PRD.md Seção 15, achado 1 (RF2.4).
_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


def _make_fake_dataset_c(n_months: int = 10) -> pd.DataFrame:
    rows = []
    base = pd.Timestamp("2024-01-15")
    for i in range(n_months):
        data = base + pd.DateOffset(months=i)
        # 2 itens IA reais por mês (Dataset B) + 3 itens Tradicionais (Dataset A)
        for _ in range(2):
            rows.append(
                {"data_publicacao": data, "fonte_dataset": "B", "rotulo_ia": "IA"}
            )
        for _ in range(3):
            rows.append(
                {
                    "data_publicacao": data,
                    "fonte_dataset": "A",
                    "rotulo_ia": "Tradicional",
                }
            )
    return pd.DataFrame(rows)


def test_compute_trend_index_returns_observed_points():
    df = _make_fake_dataset_c(n_months=10)
    idx = compute_trend_index(df, forecast_periods=3, min_observacoes=6)
    observados = [p for p in idx.pontos if p.volume_ia is not None]
    assert len(observados) == 10
    assert all(p.volume_ia == 2.0 for p in observados)


def test_compute_trend_index_returns_forecast_points_with_bounds():
    df = _make_fake_dataset_c(n_months=10)
    idx = compute_trend_index(df, forecast_periods=3, min_observacoes=6)
    projetados = [p for p in idx.pontos if p.volume_ia_projetado is not None]
    assert len(projetados) == 3
    for p in projetados:
        assert p.limite_inferior is not None
        assert p.limite_superior is not None
        assert p.limite_inferior <= p.volume_ia_projetado <= p.limite_superior


def test_compute_trend_index_empty_when_insufficient_data():
    df = _make_fake_dataset_c(n_months=3)
    idx = compute_trend_index(df, forecast_periods=3, min_observacoes=6)
    assert idx.pontos == []
    assert idx.n_observacoes == 3


def test_trend_index_projection_is_never_negative():
    # série decrescente que cruzaria zero numa extrapolação linear ingênua
    rows = []
    base = pd.Timestamp("2024-01-15")
    volumes = [10, 8, 6, 4, 2, 1, 0, 0]
    for i, v in enumerate(volumes):
        data = base + pd.DateOffset(months=i)
        for _ in range(int(v)):
            rows.append(
                {"data_publicacao": data, "fonte_dataset": "B", "rotulo_ia": "IA"}
            )
        # garante que o mês existe mesmo com v=0
        rows.append(
            {"data_publicacao": data, "fonte_dataset": "A", "rotulo_ia": "Tradicional"}
        )
    df = pd.DataFrame(rows)
    idx = compute_trend_index(df, forecast_periods=5, min_observacoes=6)
    projetados = [p for p in idx.pontos if p.volume_ia_projetado is not None]
    assert all(p.volume_ia_projetado >= 0 for p in projetados)
    assert all(p.limite_inferior >= 0 for p in projetados)


# --- RF2.4 — contextualização com calendário eleitoral (docs/PRD.md, Seção
# 15, achado 1: estava marcado como implementado por engano; corrigido
# aqui) ---------------------------------------------------------------


def test_trend_index_calendario_disponivel_no_ambiente_de_teste():
    # scripts/election_calendar.py é sibling de models/ neste repositório
    # (ver nota "ACOPLAMENTO DE CAMINHO ASSUMIDO" em trend_index.py) --
    # deve importar com sucesso a partir do checkout normal do monorepo.
    df = _make_fake_dataset_c(n_months=10)
    idx = compute_trend_index(df, forecast_periods=3, min_observacoes=6)
    assert idx.calendario_disponivel is True


def test_trend_index_marca_mes_de_1_turno_quando_serie_cobre_a_eleicao():
    # Série de jan/2026 a out/2026 (10 meses observados) inclui o mês do
    # 1º turno de 2026 (2026-10-04, scripts/election_calendar.py).
    df = _make_fake_dataset_c(n_months=10)
    df["data_publicacao"] = pd.to_datetime(df["data_publicacao"]) + pd.DateOffset(years=2)
    idx = compute_trend_index(df, forecast_periods=3, min_observacoes=6)

    pontos_por_mes = {p.mes: p for p in idx.pontos}
    assert "2026-10" in pontos_por_mes
    assert pontos_por_mes["2026-10"].mes_de_1_turno is True
    # dias_para_1_turno_mais_proximo é medido a partir do 1º dia do mês
    # (granularidade mensal do índice, ver docstring de
    # _aplicar_contexto_eleitoral) até o 1º turno em 2026-10-04, não do
    # dia exato do turno -- por isso -3, não 0, mesmo sendo "o mês do turno".
    assert pontos_por_mes["2026-10"].dias_para_1_turno_mais_proximo == -3
    # Meses vizinhos não são o mês do turno.
    assert pontos_por_mes["2026-09"].mes_de_1_turno is False
    assert pontos_por_mes["2026-09"].dias_para_1_turno_mais_proximo is not None
    assert pontos_por_mes["2026-09"].dias_para_1_turno_mais_proximo < 0

    marcos = {m["mes"]: m for m in idx.marcos_eleitorais}
    assert "2026-10" in marcos
    assert marcos["2026-10"]["ano"] == 2026
    assert marcos["2026-10"]["data_1_turno"] == "2026-10-04"


def test_trend_index_sem_marco_eleitoral_fora_do_periodo():
    # Série de jan/2025 a out/2025 + projeção até jan/2026 -- nenhum mês
    # desse intervalo é o mês de um 1º turno em scripts/election_calendar.py
    # (2018, 2020, 2022, 2024, 2026, sempre em outubro/novembro), então não
    # deve marcar nenhum mês nem listar nenhum marco dentro do período.
    df = _make_fake_dataset_c(n_months=10)
    df["data_publicacao"] = pd.to_datetime(df["data_publicacao"]) + pd.DateOffset(years=1)
    idx = compute_trend_index(df, forecast_periods=3, min_observacoes=6)
    assert all(not p.mes_de_1_turno for p in idx.pontos)
    assert idx.marcos_eleitorais == []


def test_election_calendar_datas_turno_1_consistente_com_o_import_do_trend_index():
    """Guarda contra divergência silenciosa: como trend_index.py importa
    scripts/election_calendar.py via sys.path (não uma dependência de
    pacote formal), este teste confirma que o import realmente resolve
    para o mesmo módulo/arquivo que os notebooks usam -- se algum dia
    scripts/ deixar de ser sibling de models/, este teste falha aqui, de
    forma explícita, em vez de silenciosamente no cálculo do índice."""
    from election_calendar import DATAS_TURNO_1 as datas_turno_via_sys_path

    from models_pkg.forecasting import trend_index

    assert trend_index._CALENDARIO_DISPONIVEL is True
    assert trend_index.DATAS_TURNO_1 == datas_turno_via_sys_path
    assert trend_index.DATAS_TURNO_1[2026].isoformat() == "2026-10-04"

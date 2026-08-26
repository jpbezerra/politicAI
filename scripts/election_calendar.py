# -*- coding: utf-8 -*-
"""
Calendário eleitoral (datas do 1º turno) e derivação de
`ciclo_eleitoral_estimado`/`dias_para_eleicao` a partir de uma data de
publicação — usado por `gen_notebook_a.py`, `gen_notebook_b.py`,
`gen_notebook_c.py` e (em formato de string ISO) por
`export_dashboard_data.py`.

Centralizado aqui porque a mesma constante `DATAS_TURNO_1` e a mesma função
`ciclo_e_dias` estavam duplicadas de forma idêntica nos três geradores de
notebook (ver `docs/PRD.md`, backlog de melhorias de `/models`, item
"datas de turno eleitoral hardcoded"). Os notebooks gerados importam este
módulo com `sys.path.insert(0, "../scripts")` (rodam com cwd=notebooks/),
então qualquer atualização de datas (ex.: confirmação oficial do 2º turno
2026, se houver) só precisa ser feita neste único lugar.
"""
from datetime import date

import pandas as pd

DATAS_TURNO_1 = {
    2018: date(2018, 10, 7),
    2020: date(2020, 11, 15),
    2022: date(2022, 10, 2),
    2024: date(2024, 10, 6),
    2026: date(2026, 10, 4),
}

# Mesmas datas em string ISO (formato usado por export_dashboard_data.py,
# que não depende de pandas).
DATAS_TURNO_1_ISO = {ano: d.isoformat() for ano, d in DATAS_TURNO_1.items()}


def ciclo_e_dias(data_pub) -> "pd.Series":
    """Dado um Timestamp/date de publicação, retorna uma pd.Series com
    `ciclo_eleitoral_estimado` (o ano de eleição mais próximo, por distância
    absoluta) e `dias_para_eleicao` (dias entre a publicação e o 1º turno
    desse ciclo — negativo = antes da eleição, positivo = depois)."""
    ano = data_pub.year
    anos_disponiveis = sorted(DATAS_TURNO_1.keys())
    ciclo = min(anos_disponiveis, key=lambda a: abs(a - ano))
    turno = DATAS_TURNO_1[ciclo]
    data_pub_date = data_pub.date() if hasattr(data_pub, "date") else data_pub
    return pd.Series({
        "ciclo_eleitoral_estimado": ciclo,
        "dias_para_eleicao": (data_pub_date - turno).days,
    })

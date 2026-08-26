# -*- coding: utf-8 -*-
"""
Acrescenta ao Dataset A (data/processed/dataset_a_fato_ou_boato_completo.csv,
322 itens, sem recorte temporal e sem heurística) as colunas de veredito real
coletado da página individual de cada checagem — ver
`raw_scrape_dataset_a_veredito_paginas.py` para o método completo de coleta.

Aplicado aos 322 itens ORIGINAIS (não só ao recorte 2022-2026 usado a partir
do notebook 01) -- o recorte temporal continua acontecendo só no notebook,
sobre o resultado deste merge, nunca aqui.

Novas colunas, sempre com proveniência explícita (mesmo padrão de
`fonte_veredito` já usado no Dataset C):
- `url_checagem_individual`: URL da página individual localizada (vazio se
  `metodo_localizacao_pagina == "nao_localizado"`).
- `metodo_localizacao_pagina`: como a URL foi encontrada — `slug_direto`,
  `busca_com_filtro`, `busca_sem_filtro` ou `nao_localizado`.
- `veredito_texto_pagina`: palavra literal extraída do parágrafo "Por que é
  X" da página (ex.: "boato", "distorcido"); vazio quando a página foi
  localizada mas não tem essa seção, ou quando não foi localizada.
- `fonte_veredito_pagina`: rótulo de proveniência de 3 valores --
  `texto_real_pagina_individual` (achou o parágrafo, veredito é dado real),
  `pagina_sem_secao_por_que` (página existe, mas o template não tem essa
  seção -- item continua dependendo da heurística de título no notebook 01),
  `pagina_nao_localizada` (não foi possível achar a URL individual).
"""
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"
DATA_PROCESSED = REPO_ROOT / "data" / "processed"


def fonte_veredito_pagina(row):
    if row["metodo_localizacao_pagina"] == "nao_localizado":
        return "pagina_nao_localizada"
    if row["veredito_texto_pagina"] != "":
        return "texto_real_pagina_individual"
    return "pagina_sem_secao_por_que"


if __name__ == "__main__":
    completo_path = DATA_PROCESSED / "dataset_a_fato_ou_boato_completo.csv"
    df = pd.read_csv(completo_path, parse_dates=["data_publicacao_checagem"])
    n_antes, cols_antes = len(df), len(df.columns)

    veredito = pd.read_csv(DATA_RAW / "dataset_a_veredito_paginas_individuais.csv", keep_default_na=False)
    assert len(veredito) == 322, f"Esperado 322 linhas em veredito, achou {len(veredito)}"

    faltando = set(df["id_checagem"]) - set(veredito["id_checagem"])
    assert not faltando, f"id_checagem sem correspondência de veredito: {faltando}"

    df = df.merge(veredito, on="id_checagem", how="left", validate="one_to_one")
    assert len(df) == n_antes, "Merge alterou o número de linhas -- não deveria"
    assert df["metodo_localizacao_pagina"].notna().all(), "Todo item deveria ter recebido um método (mesmo que nao_localizado)"

    df["fonte_veredito_pagina"] = df.apply(fonte_veredito_pagina, axis=1)

    df.to_csv(completo_path, index=False)

    print(f"dataset_a_fato_ou_boato_completo.csv atualizado: {n_antes} linhas (inalterado), "
          f"{cols_antes} -> {len(df.columns)} colunas")
    print(df["fonte_veredito_pagina"].value_counts())
    print(f"\nVeredito real (texto da página) disponível para "
          f"{(df['fonte_veredito_pagina'] == 'texto_real_pagina_individual').sum()} "
          f"dos {n_antes} itens ({(df['fonte_veredito_pagina'] == 'texto_real_pagina_individual').mean()*100:.1f}%)")

# -*- coding: utf-8 -*-
"""
Combina dataset_a_fato_ou_boato.csv (267 itens, tag "fake news") com
dataset_a_extra_tags.csv (55 itens novos, de 7 tags adicionais tematicamente
relacionadas: fraude, resultado, crime eleitoral, boletim de urna,
totalização, código-fonte, biometria) em um unico
dataset_a_fato_ou_boato_completo.csv (322 itens), com uma coluna
'fonte_tag' que documenta a origem de cada linha -- nada e misturado sem
rastreabilidade.
"""
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"
DATA_PROCESSED = REPO_ROOT / "data" / "processed"

original = pd.read_csv(DATA_RAW / "dataset_a_fato_ou_boato.csv", parse_dates=["data_publicacao_checagem"])
original["fonte_tag"] = "fake news"
original["tags_adicionais"] = ""

extra = pd.read_csv(DATA_RAW / "dataset_a_extra_tags.csv", parse_dates=["data_publicacao_checagem"])
extra["fonte_tag"] = "tag adicional"
extra["pagina_b_start"] = pd.NA
extra["fonte_listagem"] = "https://www.justicaeleitoral.jus.br/fato-ou-boato/@@search (tags adicionais, ver tags_adicionais)"

cols = ["id_checagem", "titulo", "descricao_resumo", "data_publicacao_checagem",
        "pagina_b_start", "fonte_listagem", "fonte_tag", "tags_adicionais"]

extra = extra.rename(columns={"id_checagem_extra": "id_checagem"})
extra = extra[cols]
original = original[cols]

combined = pd.concat([original, extra], ignore_index=True)
combined = combined.sort_values("data_publicacao_checagem").reset_index(drop=True)

dup = combined.duplicated(subset=["titulo"]).sum()
assert dup == 0, f"Duplicatas de titulo apos o merge: {dup}"
assert len(combined) == 267 + 55, f"Total inesperado apos merge: {len(combined)}"

DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
combined.to_csv(DATA_PROCESSED / "dataset_a_fato_ou_boato_completo.csv", index=False)
print(f"dataset_a_fato_ou_boato_completo.csv salvo: {len(combined)} linhas "
      f"({(combined['fonte_tag']=='fake news').sum()} de 'fake news' + "
      f"{(combined['fonte_tag']=='tag adicional').sum()} de tags adicionais)")
print(f"Intervalo de datas: {combined['data_publicacao_checagem'].min().date()} a "
      f"{combined['data_publicacao_checagem'].max().date()}")

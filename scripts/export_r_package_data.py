"""Copia os dados processados para o pacote R (r-package/politicAI/inst/extdata).

O Dataset B perde `texto_completo`/`corpo_artigo` (4,7 MB) para o pacote ficar leve;
o texto continua em data/processed/dataset_b_aosfatos_enriquecido.csv.
"""
import shutil
from pathlib import Path

import pandas as pd

raiz = Path(__file__).resolve().parent.parent
src, dst = raiz / "data/processed", raiz / "r-package/politicAI/inst/extdata"
dst.mkdir(parents=True, exist_ok=True)

shutil.copy(src / "dataset_c_unificado.csv", dst / "dataset_c_unificado.csv")
shutil.copy(src / "dataset_a_fato_ou_boato_enriquecido.csv", dst / "dataset_a_fato_ou_boato.csv")
shutil.copy(src / "robustez_revisao.json", dst / "robustez_revisao.json")
b = pd.read_csv(src / "dataset_b_aosfatos_enriquecido.csv").drop(columns=["texto_completo", "corpo_artigo"])
# `data_publicacao` original e texto em portugues ("20 de agosto de 2026, 15:57"): no pacote
# vira data ISO, e a hora fica em `data_publicacao_timestamp`.
b = b.rename(columns={"data_publicacao_iso": "data_publicacao_timestamp"})
b["data_publicacao"] = b["data_publicacao_timestamp"].str[:10]
b.to_csv(dst / "dataset_b_aosfatos.csv", index=False)

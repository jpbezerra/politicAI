"""
Gera um snapshot JSON agregado do Dataset C (dados REAIS, coletados nas Fases
1-2 deste projeto) para consumo pelo dashboard em `/web`.

Por que um snapshot estático em vez do Next.js ler o CSV diretamente:
  - mantém toda a lógica de agregação/estatística em Python (pandas), onde
    já vive o resto do pipeline de dados deste projeto, em vez de duplicar
    parsing de CSV em TypeScript;
  - o site não precisa reprocessar ~875 linhas a cada request;
  - deixa explícito, no próprio nome do arquivo e no campo `gerado_em`, que
    o dashboard exibe uma FOTOGRAFIA dos dados coletados até uma data —
    nunca dado "ao vivo" das redes/institutos (essas lentes ainda não têm
    fonte real integrada; ver docs/PRD.md, Seção 5.1).

Uso:
    python scripts/export_dashboard_data.py

Lê:  data/processed/dataset_c_unificado.csv
Gera: web/src/data/dataset_c_summary.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# election_calendar.py vive no mesmo diretório (scripts/); ao rodar
# `python scripts/export_dashboard_data.py` a partir da raiz do repo, o
# próprio Python já coloca scripts/ no sys.path, então este import direto
# funciona sem manipulação extra de path.
from election_calendar import DATAS_TURNO_1_ISO as DATAS_TURNO_1

REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_C_PATH = REPO_ROOT / "data" / "processed" / "dataset_c_unificado.csv"
OUTPUT_PATH = REPO_ROOT / "web" / "src" / "data" / "dataset_c_summary.json"

# DATAS_TURNO_1 agora vem de scripts/election_calendar.py (única fonte,
# usada também pelos 3 geradores de notebook) — ver docs/PRD.md, backlog de
# melhorias. Aqui só as datas até 2026 interessam (as usadas nos gráficos).

TOP_N_TEMAS = 8


def carregar_dataset() -> pd.DataFrame:
    if not DATASET_C_PATH.exists():
        raise FileNotFoundError(
            f"Dataset C não encontrado em {DATASET_C_PATH}. "
            "Rode antes: jupyter nbconvert --execute notebooks/03_dataset_c_unificado_eda.ipynb "
            "(ou abra e rode o notebook manualmente) para gerá-lo."
        )
    df = pd.read_csv(DATASET_C_PATH, parse_dates=["data_publicacao"])
    return df


def resumo_geral(df: pd.DataFrame) -> dict:
    n_total = len(df)
    n_ia = int((df["rotulo_ia"] == "IA").sum())
    n_tradicional = int((df["rotulo_ia"] == "Tradicional").sum())
    # Só o Dataset B rotula IA de forma editorial (real); o Dataset A não tem
    # nenhum item IA na amostra coletada (ver docs/PRD.md, nota de proveniência).
    n_rotulo_editorial = int((df["fonte_rotulo_ia"] == "editorial_aos_fatos_tag").sum())
    return {
        "n_total": n_total,
        "n_ia": n_ia,
        "n_tradicional": n_tradicional,
        "pct_ia": round(100 * n_ia / n_total, 1) if n_total else None,
        "n_rotulo_editorial_confiavel": n_rotulo_editorial,
    }


def serie_mensal(df: pd.DataFrame) -> list[dict]:
    d = df.dropna(subset=["data_publicacao"]).copy()
    d["mes"] = d["data_publicacao"].dt.to_period("M").astype(str)
    tab = (
        d.groupby(["mes", "rotulo_ia"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    for col in ("IA", "Tradicional"):
        if col not in tab.columns:
            tab[col] = 0
    tab["total"] = tab["IA"] + tab["Tradicional"]
    tab = tab.sort_values("mes")
    return [
        {
            "mes": row["mes"],
            "total": int(row["total"]),
            "ia": int(row["IA"]),
            "tradicional": int(row["Tradicional"]),
        }
        for _, row in tab.iterrows()
    ]


def distribuicao_por_fonte(df: pd.DataFrame) -> list[dict]:
    tab = df["fonte_dataset"].value_counts(dropna=False)
    return [{"fonte": str(k), "n": int(v)} for k, v in tab.items()]


def distribuicao_por_tema(df: pd.DataFrame) -> list[dict]:
    d = df.copy()
    d["categoria_tema"] = d["categoria_tema"].fillna("Não classificado")
    tab = d["categoria_tema"].value_counts(dropna=False).head(TOP_N_TEMAS)
    resultado = []
    for tema, total in tab.items():
        sub = d[d["categoria_tema"] == tema]
        n_ia = int((sub["rotulo_ia"] == "IA").sum())
        resultado.append({"tema": str(tema), "n": int(total), "n_ia": n_ia})
    return resultado


def distribuicao_veredito(df: pd.DataFrame) -> list[dict]:
    tab = df["veredito_binario"].value_counts(dropna=False)
    return [
        {"veredito": ("nao_classificado" if pd.isna(k) else str(k)), "n": int(v)}
        for k, v in tab.items()
    ]


def main() -> None:
    df = carregar_dataset()

    snapshot = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "gerado_por": "scripts/export_dashboard_data.py",
        "fonte_dados": "data/processed/dataset_c_unificado.csv (Datasets A + B unificados, Fase 2 do projeto)",
        "aviso": (
            "Estes números refletem uma coleta pontual, não um feed ao vivo. "
            "A lente de IA usa rótulo editorial real apenas para os itens de "
            "origem 'B' (Aos Fatos); itens de origem 'A' não têm rótulo "
            "editorial de IA disponível (ver docs/PRD.md)."
        ),
        "datas_turno_1": DATAS_TURNO_1,
        "resumo_geral": resumo_geral(df),
        "serie_mensal": serie_mensal(df),
        "distribuicao_por_fonte": distribuicao_por_fonte(df),
        "distribuicao_por_tema": distribuicao_por_tema(df),
        "distribuicao_veredito": distribuicao_veredito(df),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    print(f"Snapshot gerado em {OUTPUT_PATH} ({len(df)} linhas processadas).")


if __name__ == "__main__":
    main()

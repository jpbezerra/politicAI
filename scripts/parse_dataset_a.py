# -*- coding: utf-8 -*-
"""
Parser do Dataset A — transforma o texto bruto raspado (raw_scrape_dataset_a_tse.py)
em um CSV estruturado: dataset_a_fato_ou_boato.csv

Fonte real: justicaeleitoral.jus.br/fato-ou-boato, tag "fake news" (267 resultados,
27 páginas), coletado via navegador em 23/08/2026.
"""
import csv
import re
from datetime import datetime
from pathlib import Path

from raw_scrape_dataset_a_tse import ALL_PAGES

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"

DATE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
BASE_SEARCH_URL = (
    "https://www.justicaeleitoral.jus.br/fato-ou-boato/@@search?"
    "SearchableText=&b_start%3Aint={b_start}&Subject%3Alist=fake+news"
    "&instituicao%3Alist=&start_date=&end_date="
)


def parse_page(raw_text, b_start):
    """Cada item ocupa 3 linhas: título / resumo (ou [SEM_RESUMO]) / data."""
    lines = [l.strip() for l in raw_text.strip().split("\n") if l.strip()]
    rows = []
    i = 0
    while i < len(lines):
        if i + 2 >= len(lines):
            break
        titulo, resumo, data_str = lines[i], lines[i + 1], lines[i + 2]
        if not DATE_RE.match(data_str):
            raise ValueError(
                f"Formato inesperado perto de: {titulo!r} (linha {i}, b_start={b_start})"
            )
        resumo_final = "" if resumo == "[SEM_RESUMO]" else resumo
        data_iso = datetime.strptime(data_str, "%d.%m.%Y").date().isoformat()
        rows.append({
            "titulo": titulo,
            "descricao_resumo": resumo_final,
            "data_publicacao_checagem": data_iso,
            "pagina_b_start": b_start,
            "fonte_listagem": BASE_SEARCH_URL.format(b_start=b_start),
        })
        i += 3
    return rows


def main():
    all_rows = []
    for idx, page_text in enumerate(ALL_PAGES):
        b_start = idx * 10
        all_rows.extend(parse_page(page_text, b_start))

    print(f"Total de checagens parseadas: {len(all_rows)} (esperado: 267)")
    assert len(all_rows) == 267, "Contagem não bate com o total real (267) do site!"

    # id_checagem sequencial e estável (a fonte não expõe um ID próprio)
    for i, row in enumerate(all_rows):
        row["id_checagem"] = f"FOB-{i+1:04d}"

    fieldnames = [
        "id_checagem", "titulo", "descricao_resumo",
        "data_publicacao_checagem", "pagina_b_start", "fonte_listagem",
    ]
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    out_path = DATA_RAW / "dataset_a_fato_ou_boato.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

    print(f"Arquivo salvo: {out_path}")


if __name__ == "__main__":
    main()

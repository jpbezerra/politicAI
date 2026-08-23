# -*- coding: utf-8 -*-
"""
Processa as 7 tags adicionais coletadas em raw_scrape_dataset_a_extra_tags.py,
com um parser generico baseado na linha de data (dd.mm.aaaa) -- que lida com
itens de 1 linha (so titulo) ou 2 linhas (titulo+resumo) automaticamente,
sem exigir recorte manual dos limites de cada item.

Depois deduplica contra os 267 itens ja existentes em dataset_a_fato_ou_boato.csv
(por titulo exato) e escreve so os itens GENUINAMENTE NOVOS em
dataset_a_extra_tags.csv, com uma coluna listando todas as tags adicionais em
que cada item apareceu (documentando a sobreposicao em vez de escondê-la).
"""
import csv
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

from raw_scrape_dataset_a_extra_tags import TAG_PAGES, EXPECTED_COUNTS

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"

DATE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
HEADER_ANCHOR_RE = re.compile(r"Foram encontrados \d+ resultados?\.")
FOOTER_ANCHOR = "< Anterior"


def clean_page(raw):
    m = HEADER_ANCHOR_RE.search(raw)
    assert m, "Ancora de cabecalho ('Foram encontrados... resultados.') nao encontrada"
    body = raw[m.end():]
    idx_footer = body.find(FOOTER_ANCHOR)
    if idx_footer != -1:
        body = body[:idx_footer]
    return body


def parse_page(raw):
    body = clean_page(raw)
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    rows = []
    buffer = []
    for line in lines:
        if DATE_RE.match(line):
            assert 1 <= len(buffer) <= 2, f"Item com {len(buffer)} linhas antes da data: {buffer}"
            titulo = buffer[0]
            resumo = buffer[1] if len(buffer) == 2 else ""
            data_iso = datetime.strptime(line, "%d.%m.%Y").date().isoformat()
            rows.append({"titulo": titulo, "descricao_resumo": resumo, "data_publicacao_checagem": data_iso})
            buffer = []
        else:
            buffer.append(line)
    assert not buffer, f"Sobraram linhas sem data ao final da pagina: {buffer}"
    return rows


def main():
    all_rows_by_tag = {}
    for tag, pages in TAG_PAGES.items():
        rows = []
        for page in pages:
            rows.extend(parse_page(page))
        expected = EXPECTED_COUNTS[tag]
        print(f"Tag '{tag}': {len(rows)} itens parseados (esperado: {expected})")
        assert len(rows) == expected, f"Contagem da tag '{tag}' nao bate com o site!"
        all_rows_by_tag[tag] = rows

    # agrega por titulo (um item pode aparecer em mais de uma tag adicional)
    by_title = {}
    for tag, rows in all_rows_by_tag.items():
        for row in rows:
            key = row["titulo"]
            if key not in by_title:
                by_title[key] = dict(row)
                by_title[key]["tags_adicionais"] = set()
            by_title[key]["tags_adicionais"].add(tag)

    total_unique_extra = len(by_title)
    print(f"\nTotal de itens unicos nas 7 tags adicionais (antes de comparar com fake news): {total_unique_extra}")

    # compara com os 267 itens ja existentes (dataset_a_fato_ou_boato.csv).
    # normaliza aspas curvas/retas antes de comparar, para nao contar como
    # "novo" um item que so difere por causa de uma transcricao manual com
    # aspas tipograficas diferentes (mesmo texto real, mesma checagem).
    def normalize_quotes(s):
        return s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")

    existing = pd.read_csv(DATA_RAW / "dataset_a_fato_ou_boato.csv")
    existing_titles_norm = {normalize_quotes(t) for t in existing["titulo"]}

    novos = {t: r for t, r in by_title.items() if normalize_quotes(t) not in existing_titles_norm}
    ja_existiam = total_unique_extra - len(novos)
    print(f"Ja existiam na tag 'fake news' (sobreposicao esperada): {ja_existiam}")
    print(f"GENUINAMENTE NOVOS (fora da tag 'fake news'): {len(novos)}")

    # monta CSV final dos itens novos
    fieldnames = ["id_checagem_extra", "titulo", "descricao_resumo",
                  "data_publicacao_checagem", "tags_adicionais"]
    novos_ordenados = sorted(novos.values(), key=lambda r: r["data_publicacao_checagem"])
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    out_path = DATA_RAW / "dataset_a_extra_tags.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, row in enumerate(novos_ordenados):
            writer.writerow({
                "id_checagem_extra": f"FOB-EXTRA-{i+1:04d}",
                "titulo": row["titulo"],
                "descricao_resumo": row["descricao_resumo"],
                "data_publicacao_checagem": row["data_publicacao_checagem"],
                "tags_adicionais": "; ".join(sorted(row["tags_adicionais"])),
            })
    print(f"\nArquivo salvo: {out_path} ({len(novos_ordenados)} linhas)")


if __name__ == "__main__":
    main()

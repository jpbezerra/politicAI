# -*- coding: utf-8 -*-
"""
Parser do Dataset B — transforma o texto bruto raspado (raw_scrape_dataset_b_aosfatos.py)
em um CSV estruturado: dataset_b_aosfatos.csv

Fonte real: aosfatos.org/noticias/?formato=checagem (arquivo de checagens do
Aos Fatos), recortado por 3 tags editoriais reais coletadas em 23/08/2026:
  - inteligencia-artificial (populacao completa, 11 paginas, 122 itens)
  - eleicoes-2026 (populacao completa, 1 pagina, 12 itens)
  - eleicoes-2022 (populacao completa, 35 paginas, 419 itens -- coletada em
    duas etapas: 7 paginas inicialmente, as 28 restantes depois a pedido do
    usuario, para substituir a amostra original por uma coleta completa)

Cada bloco tem 3, 2 ou 1 linha(s) de rótulo antes do marcador fixo "checagem",
seguido do título:
    [veredito]?  [tema]?  checagem  <titulo>
Regras de desambiguacao quando ha so 1 linha de rotulo: se ela pertence ao
vocabulario fechado de veredito, e veredito (sem tema); caso contrario, e tema
(sem veredito). Quando ha 0 linhas de rotulo, ambos ficam em branco.
"""
import csv
from pathlib import Path

from raw_scrape_dataset_b_aosfatos import (
    IA_PAGES, ELEICOES_2026_PAGES, ELEICOES_2022_PAGES,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"

VEREDITO_VOCAB = {"falso", "verdadeiro", "não é bem assim", "discurso oficial", "distorcido"}
MARCADOR = "checagem"


def parse_page(raw_text):
    lines = [l.strip() for l in raw_text.strip().split("\n") if l.strip()]
    rows = []
    pending_labels = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line == MARCADOR:
            # as ate 2 linhas anteriores (ja consumidas em pending_labels) sao os rotulos
            veredito, tema = None, None
            if len(pending_labels) == 2:
                veredito, tema = pending_labels
            elif len(pending_labels) == 1:
                if pending_labels[0] in VEREDITO_VOCAB:
                    veredito = pending_labels[0]
                else:
                    tema = pending_labels[0]
            elif len(pending_labels) > 2:
                # nao deveria ocorrer com este site; guarda tudo em tema como fallback
                tema = " | ".join(pending_labels)
            # a proxima linha nao-vazia e o titulo
            i += 1
            titulo = lines[i] if i < len(lines) else None
            rows.append({"veredito": veredito or "", "tema": tema or "", "titulo": titulo})
            pending_labels = []
        else:
            pending_labels.append(line)
        i += 1
    return rows


def build_dataset(pages, tag_pesquisa):
    all_rows = []
    for page_text in pages:
        for row in parse_page(page_text):
            row["tag_pesquisa"] = tag_pesquisa
            all_rows.append(row)
    return all_rows


def main():
    rows = []
    rows += build_dataset(IA_PAGES, "inteligencia-artificial")
    rows += build_dataset(ELEICOES_2026_PAGES, "eleicoes-2026")
    rows += build_dataset(ELEICOES_2022_PAGES, "eleicoes-2022")

    print(f"Total de checagens parseadas (Aos Fatos): {len(rows)}")
    n_ia = sum(1 for r in rows if r["tag_pesquisa"] == "inteligencia-artificial")
    n_2022 = sum(1 for r in rows if r["tag_pesquisa"] == "eleicoes-2022")
    n_2026 = sum(1 for r in rows if r["tag_pesquisa"] == "eleicoes-2026")
    print(f"  - tag inteligencia-artificial: {n_ia} (esperado: 122, 11 paginas)")
    print(f"  - tag eleicoes-2022: {n_2022} (esperado: 419, 35 paginas -- populacao completa)")
    print(f"  - tag eleicoes-2026: {n_2026} (esperado: 12, 1 pagina)")
    assert n_ia == 122, "Contagem da tag IA nao bate com a coleta real!"
    assert n_2022 == 419, "Contagem da tag eleicoes-2022 nao bate com a coleta real (35 paginas)!"
    assert n_2026 == 12, "Contagem da tag eleicoes-2026 nao bate com a coleta real!"

    for i, row in enumerate(rows):
        row["id_checagem_af"] = f"AF-{i+1:04d}"
        row["fonte"] = "https://www.aosfatos.org/noticias/?formato=checagem"

    fieldnames = ["id_checagem_af", "titulo", "veredito", "tema", "tag_pesquisa", "fonte"]
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    out_path = DATA_RAW / "dataset_b_aosfatos.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Arquivo salvo: {out_path}")


if __name__ == "__main__":
    main()

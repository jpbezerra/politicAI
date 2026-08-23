# -*- coding: utf-8 -*-
"""
Scraper HTTP real (requests + BeautifulSoup) para o Dataset B --
aosfatos.org/noticias/?formato=checagem -- fornecido para permitir
REPRODUÇÃO/VERIFICAÇÃO INDEPENDENTE da coleta original.

AVISO METODOLÓGICO IMPORTANTE (leia antes de usar):
O ambiente de execução onde este projeto foi originalmente construído não
tem acesso direto à internet. Por isso, a coleta original dos dados em
`data/raw/dataset_b_aosfatos.csv` foi feita por NAVEGAÇÃO ASSISTIDA (Claude
in Chrome): o texto renderizado de cada página foi extraído do navegador
real e copiado verbatim para `raw_scrape_dataset_b_aosfatos.py`, que é o
registro bruto e a evidência primária da coleta. Este script
`scrape_dataset_b_http.py` NÃO foi executado neste ambiente e portanto NÃO
gerou os dados existentes -- ele é fornecido como ferramenta adicional para
que qualquer pessoa com acesso à internet possa rodar a mesma lógica de
coleta e comparar o resultado com o CSV já publicado neste repositório.

O parsing de cada checagem (linha de veredito / linha de tema / marcador
"checagem" / título) reaproveita EXATAMENTE a mesma função já validada em
parse_dataset_b.py contra os 553 itens reais coletados manualmente -- só a
forma de obter o texto da página muda (aqui via requests+BeautifulSoup, lá
via texto colado manualmente).

Uso:
    pip install requests beautifulsoup4
    python3 scrape_dataset_b_http.py inteligencia-artificial
    python3 scrape_dataset_b_http.py eleicoes-2022
    python3 scrape_dataset_b_http.py eleicoes-2026
    # salva em data/raw/scrape_http_aosfatos_<tag>.csv
"""
import csv
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# reaproveita o parser de itens ja validado (mesmo diretorio)
from parse_dataset_b import parse_page, VEREDITO_VOCAB, MARCADOR  # noqa: F401

BASE_URL = "https://www.aosfatos.org/noticias/"
LAST_PAGE_RE = re.compile(r"[?&]page=(\d+)")
USER_AGENT = "Mozilla/5.0 (pesquisa-academica; contato: ver README do repositorio)"

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"


def fetch_page(tag, page, session):
    params = {"formato": "checagem", "tag": tag, "page": page}
    resp = session.get(BASE_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.text


def find_last_page(html):
    """Le o numero de pagina mais alto presente na navegacao de paginacao
    (nav com links '?page=N'), a mesma logica usada manualmente para
    descobrir que 'eleicoes-2022' tinha 35 paginas."""
    soup = BeautifulSoup(html, "html.parser")
    nav = soup.find("nav", attrs={"aria-label": re.compile("pagina", re.I)}) or soup
    pages = [int(m.group(1)) for a in nav.find_all("a", href=True)
             for m in [LAST_PAGE_RE.search(a["href"])] if m]
    return max(pages) if pages else 1


def scrape_tag(tag, delay_seconds=1.0):
    session = requests.Session()
    first_html = fetch_page(tag, 1, session)
    last_page = find_last_page(first_html)
    print(f"Tag {tag!r}: {last_page} página(s) detectada(s) pela paginação.")

    all_rows = []
    for page in range(1, last_page + 1):
        if page > 1:
            time.sleep(delay_seconds)  # educado com o servidor do Aos Fatos
            html = fetch_page(tag, page, session)
        else:
            html = first_html
        page_text = BeautifulSoup(html, "html.parser").get_text(separator="\n")
        rows = parse_page(page_text)
        for row in rows:
            row["tag_pesquisa"] = tag
        all_rows.extend(rows)
        print(f"  página {page}: {len(rows)} itens")

    print(f"Tag {tag!r}: {len(all_rows)} itens no total.")
    return all_rows


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    tag = sys.argv[1]
    rows = scrape_tag(tag)

    DATA_RAW.mkdir(parents=True, exist_ok=True)
    safe_tag = re.sub(r"[^a-z0-9]+", "-", tag.lower()).strip("-")
    out_path = DATA_RAW / f"scrape_http_aosfatos_{safe_tag}.csv"
    fieldnames = ["titulo", "veredito", "tema", "tag_pesquisa"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Arquivo salvo: {out_path}")


if __name__ == "__main__":
    main()

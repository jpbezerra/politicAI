# -*- coding: utf-8 -*-
"""
Scraper HTTP real (requests + BeautifulSoup) para o Dataset A --
justicaeleitoral.jus.br/fato-ou-boato/@@search -- fornecido para permitir
REPRODUÇÃO/VERIFICAÇÃO INDEPENDENTE da coleta original.

AVISO METODOLÓGICO IMPORTANTE (leia antes de usar):
O ambiente de execução onde este projeto foi originalmente construído não
tem acesso direto à internet (chamadas com `requests`/`curl` falham por
design do sandbox). Por isso, a coleta original dos dados em
`data/raw/dataset_a_fato_ou_boato.csv` e `data/raw/dataset_a_extra_tags.csv`
foi feita por NAVEGAÇÃO ASSISTIDA (Claude in Chrome): o texto de cada página
de resultados foi extraído do navegador real e copiado verbatim para
`raw_scrape_dataset_a_tse.py` / `raw_scrape_dataset_a_extra_tags.py`, que são
o registro bruto e a evidência primária da coleta (cada página ali documenta
a URL exata consultada). Este script `scrape_dataset_a_http.py` NÃO foi
executado neste ambiente e portanto NÃO gerou os dados existentes -- ele é
fornecido como ferramenta adicional para que qualquer pessoa com acesso à
internet possa rodar a mesma lógica de coleta (mesmas URLs, mesma paginação,
mesmo parsing por linha de data já validado em parse_dataset_a.py) e
comparar o resultado com os CSVs já publicados neste repositório, como
checagem de reprodutibilidade.

Uso:
    pip install requests beautifulsoup4
    python3 scrape_dataset_a_http.py "fake news"
    python3 scrape_dataset_a_http.py "fraude"
    # etc. -- uma tag por vez; salva em data/raw/scrape_http_<tag>.csv
    # (não sobrescreve os CSVs originais, para não misturar coleta nova com a
    # coleta original documentada nos raw_scrape_*.py)
"""
import csv
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.justicaeleitoral.jus.br/fato-ou-boato/@@search"
DATE_RE = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")
COUNT_RE = re.compile(r"Foram encontrados (\d+) resultados?")
PAGE_SIZE = 10  # confirmado empiricamente durante a coleta original (b_start incrementa de 10 em 10)
USER_AGENT = "Mozilla/5.0 (pesquisa-academica; contato: ver README do repositorio)"

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"


def fetch_page(tag, b_start, session):
    params = {
        "SearchableText": "",
        "b_start:int": b_start,
        "Subject:list": tag,
        "instituicao:list": "",
        "start_date": "",
        "end_date": "",
    }
    resp = session.get(BASE_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_items(html):
    """Extrai (titulo, resumo, data_iso) de cada item 'folha' (sem <article>
    aninhado) que contenha uma data no formato dd.mm.aaaa -- a mesma
    heurística estrutural observada na árvore de acessibilidade do site
    durante a coleta manual: cada resultado é um <article> contendo um link
    de título, um parágrafo de resumo e uma data.
    """
    soup = BeautifulSoup(html, "html.parser")
    leaf_articles = [a for a in soup.find_all("article") if not a.find("article")]
    rows = []
    for art in leaf_articles:
        text = art.get_text(separator="\n", strip=True)
        lines = [l for l in text.split("\n") if l.strip()]
        date_idx = next((i for i, l in enumerate(lines) if DATE_RE.fullmatch(l.strip())), None)
        if date_idx is None:
            continue  # nao e um item de resultado (ex.: bloco de navegacao)
        pre_date = lines[:date_idx]
        if not pre_date:
            continue
        titulo = pre_date[0]
        resumo = " ".join(pre_date[1:]) if len(pre_date) > 1 else ""
        data_iso = datetime.strptime(lines[date_idx], "%d.%m.%Y").date().isoformat()
        rows.append({"titulo": titulo, "descricao_resumo": resumo, "data_publicacao_checagem": data_iso})
    return rows


def scrape_tag(tag, delay_seconds=1.0):
    session = requests.Session()
    first_html = fetch_page(tag, 0, session)
    m = COUNT_RE.search(BeautifulSoup(first_html, "html.parser").get_text())
    if not m:
        raise RuntimeError(f"Não encontrei a contagem total de resultados para a tag {tag!r}. "
                            f"A estrutura da página pode ter mudado desde a coleta original (23/08/2026).")
    total = int(m.group(1))
    print(f"Tag {tag!r}: {total} resultados reportados pelo site.")

    all_rows = parse_items(first_html)
    b_start = PAGE_SIZE
    while b_start < total:
        time.sleep(delay_seconds)  # educado com o servidor publico do TSE
        html = fetch_page(tag, b_start, session)
        all_rows.extend(parse_items(html))
        b_start += PAGE_SIZE

    print(f"Tag {tag!r}: {len(all_rows)} itens efetivamente parseados (esperado: {total}).")
    if len(all_rows) != total:
        print("AVISO: contagem parseada difere da contagem reportada pelo site -- "
              "revise parse_items() antes de usar este resultado como substituto dos dados existentes.")
    return all_rows


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    tag = sys.argv[1]
    rows = scrape_tag(tag)

    DATA_RAW.mkdir(parents=True, exist_ok=True)
    safe_tag = re.sub(r"[^a-z0-9]+", "-", tag.lower()).strip("-")
    out_path = DATA_RAW / f"scrape_http_{safe_tag}.csv"
    fieldnames = ["titulo", "descricao_resumo", "data_publicacao_checagem"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Arquivo salvo: {out_path}")


if __name__ == "__main__":
    main()

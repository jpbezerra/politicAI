# -*- coding: utf-8 -*-
"""
Scraper HTTP real (requests + BeautifulSoup) que complementa o Dataset B com
DATA DE PUBLICAÇÃO e TEXTO COMPLETO de cada checagem — a listagem usada em
`raw_scrape_dataset_b_aosfatos.py` não expõe a data por item (só aparece na
página individual de cada checagem), o que bloqueava H3/H5 para este dataset.

IMPORTANTE — RODE ISSO NA SUA MÁQUINA, NÃO NO CLAUDE:
Tanto o sandbox do Claude quanto a VM isolada do Cowork (usada pelo
`device_bash`) ficam atrás de um proxy que bloqueia domínios como
aosfatos.org (testado e confirmado: ambos retornam
`ProxyError: Tunnel connection failed: 403 Forbidden`). Esse bloqueio não
existe no seu computador de verdade — por isso este script foi escrito para
você rodar localmente, num terminal comum (PowerShell, cmd, etc.), não para
mim rodar por você.

COMO RODAR:
    cd politicAI
    pip install requests beautifulsoup4
    python scripts\\scrape_dataset_b_completo.py inteligencia-artificial
    python scripts\\scrape_dataset_b_completo.py eleicoes-2022
    python scripts\\scrape_dataset_b_completo.py eleicoes-2026

Saída: data/raw/dataset_b_completo_<tag>.csv, com colunas:
    titulo, veredito, tema, tag_pesquisa, url, data_publicacao, texto_completo

Depois de rodar, me avise (ou já deixe os CSVs em data/raw/) que eu integro
no dataset enriquecido e re-rodo o notebook 02 com datas reais — o que
finalmente viabiliza um preview de H3/H5 neste dataset, e permite recalcular
vetor_midia/alvo_ataque a partir do texto completo em vez de só o título.

TEMPO ESPERADO (o script visita CADA checagem individualmente, não só a
listagem — por isso é mais lento que scrape_dataset_b_http.py, e usa um
delay entre requisições para não sobrecarregar o servidor do Aos Fatos):
    - inteligencia-artificial (122 itens, 11 páginas de listagem): ~3-5 min
    - eleicoes-2022 (419 itens, 35 páginas de listagem): ~15-25 min
    - eleicoes-2026 (12 itens, 1 página de listagem): ~1 min
É normal parecer "parado" por alguns segundos entre cada item — ele está
esperando de propósito (DELAY_ITEM) para ser educado com o servidor.

LIMITAÇÃO CONHECIDA: o casamento entre cada checagem (veredito/tema, extraído
do texto da listagem pelo parser já validado) e sua URL individual é feito
por POSIÇÃO na página (a ordem em que os links de artigo aparecem no HTML
deveria ser a mesma ordem em que os blocos de texto aparecem). O script
verifica essa contagem em cada página e AVISA no terminal se os números não
baterem — se isso acontecer em alguma página, me mande o aviso completo que
eu ajusto a lógica de extração de links.
"""
import csv
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# reaproveita o parser de veredito/tema/titulo ja validado contra os 553 itens
from parse_dataset_b import parse_page  # noqa: F401

BASE_URL = "https://www.aosfatos.org/noticias/"
LAST_PAGE_RE = re.compile(r"[?&]page=(\d+)")
ARTIGO_HREF_RE = re.compile(r"^/noticias/[a-z0-9\-]+/$")
DATA_LINHA_RE = re.compile(
    r"^\d{1,2} de [a-zàáâãéêíóôõúç]+ de \d{4},\s*\d{2}:\d{2}$", re.IGNORECASE
)
USER_AGENT = "Mozilla/5.0 (pesquisa-academica; contato: ver README do repositorio)"
DELAY_LISTAGEM = 1.0
DELAY_ITEM = 1.0

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"


def fetch(url, session, params=None):
    resp = session.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.text


def find_last_page(html):
    """Mesma lógica usada em scrape_dataset_b_http.py: lê o maior número de
    página presente na navegação de paginação da listagem."""
    soup = BeautifulSoup(html, "html.parser")
    nav = soup.find("nav", attrs={"aria-label": re.compile("pagina", re.I)}) or soup
    pages = [int(m.group(1)) for a in nav.find_all("a", href=True)
             for m in [LAST_PAGE_RE.search(a["href"])] if m]
    return max(pages) if pages else 1


def extrair_links_artigos(html):
    """Extrai os hrefs de checagem na mesma ordem em que aparecem no HTML —
    essa ordem deve corresponder à ordem de leitura que parse_page() usa
    sobre o texto da página, permitindo casar os dois por posição."""
    soup = BeautifulSoup(html, "html.parser")
    hrefs, vistos = [], set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ARTIGO_HREF_RE.match(href) and href not in vistos:
            hrefs.append(href)
            vistos.add(href)
    return hrefs


def extrair_data_e_texto(html):
    """Extrai a data de publicação (linha 'DD de <mês> de AAAA, HH:MM' perto
    do topo do artigo) e o texto completo do corpo da página."""
    soup = BeautifulSoup(html, "html.parser")
    texto = soup.get_text(separator="\n")
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    data_publicacao = next((l for l in linhas if DATA_LINHA_RE.match(l)), "")
    return data_publicacao, texto


def scrape_tag_completo(tag):
    session = requests.Session()
    first_html = fetch(BASE_URL, session, params={"formato": "checagem", "tag": tag, "page": 1})
    last_page = find_last_page(first_html)
    print(f"Tag {tag!r}: {last_page} pagina(s) de listagem detectadas.")

    todos_itens = []
    for page in range(1, last_page + 1):
        if page == 1:
            html = first_html
        else:
            time.sleep(DELAY_LISTAGEM)
            html = fetch(BASE_URL, session, params={"formato": "checagem", "tag": tag, "page": page})

        page_text = BeautifulSoup(html, "html.parser").get_text(separator="\n")
        itens_parseados = parse_page(page_text)
        hrefs = extrair_links_artigos(html)

        if len(hrefs) != len(itens_parseados):
            print(f"  AVISO pagina {page}: {len(hrefs)} link(s) de artigo vs {len(itens_parseados)} "
                  f"item(ns) parseado(s) pelo texto -- descasamento! Os itens desta pagina ficarao "
                  f"sem URL/data (nao vou arriscar casar errado). Me avise deste aviso.")
            for item in itens_parseados:
                item["url"] = ""
        else:
            for item, href in zip(itens_parseados, hrefs):
                item["url"] = "https://www.aosfatos.org" + href

        for item in itens_parseados:
            item["tag_pesquisa"] = tag
        todos_itens.extend(itens_parseados)
        print(f"  pagina {page}/{last_page}: {len(itens_parseados)} itens "
              f"({sum(1 for i in itens_parseados if i['url'])} com URL)")

    com_url = [i for i in todos_itens if i["url"]]
    print(f"Tag {tag!r}: {len(todos_itens)} itens no total, {len(com_url)} com URL valida. "
          f"Buscando data + texto completo de cada um...")
    for i, item in enumerate(todos_itens, start=1):
        if not item["url"]:
            item["data_publicacao"] = ""
            item["texto_completo"] = ""
            continue
        time.sleep(DELAY_ITEM)
        try:
            html_item = fetch(item["url"], session)
            data_publicacao, texto_completo = extrair_data_e_texto(html_item)
        except Exception as exc:
            print(f"  [{i}/{len(todos_itens)}] ERRO em {item['url']}: {exc}")
            data_publicacao, texto_completo = "", ""
        item["data_publicacao"] = data_publicacao
        item["texto_completo"] = texto_completo
        if i % 10 == 0 or i == len(todos_itens):
            print(f"  [{i}/{len(todos_itens)}] processados...")

    return todos_itens


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    tag = sys.argv[1]
    itens = scrape_tag_completo(tag)

    DATA_RAW.mkdir(parents=True, exist_ok=True)
    safe_tag = re.sub(r"[^a-z0-9]+", "-", tag.lower()).strip("-")
    out_path = DATA_RAW / f"dataset_b_completo_{safe_tag}.csv"
    fieldnames = ["titulo", "veredito", "tema", "tag_pesquisa", "url", "data_publicacao", "texto_completo"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in itens:
            writer.writerow({k: item.get(k, "") for k in fieldnames})

    n_com_data = sum(1 for i in itens if i.get("data_publicacao"))
    print(f"\nArquivo salvo: {out_path}")
    print(f"{n_com_data}/{len(itens)} itens com data de publicacao capturada com sucesso.")
    if n_com_data < len(itens):
        print("Itens sem data: ou tiveram descasamento de URL (ver avisos acima) ou a pagina "
              "individual mudou de formato -- me manda o CSV mesmo assim que eu dou uma olhada.")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Script de diagnóstico — não faz parte do pipeline, é só para eu entender por
que scrape_dataset_b_completo.py encontrou 0 itens parseados (mas 12 links
de artigo certinhos) em toda página testada.

Baixa o HTML BRUTO (exatamente o que requests recebe, sem nenhum
processamento) de uma página de listagem e salva em
data/raw/_debug_pagina1.html — depois disso, me avisa aqui no chat que eu
leio o arquivo direto da pasta (não precisa anexar nada).

Uso:
    python scripts\\debug_dump_html.py
"""
from pathlib import Path

import requests

USER_AGENT = "Mozilla/5.0 (pesquisa-academica; contato: ver README do repositorio)"
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"

resp = requests.get(
    "https://www.aosfatos.org/noticias/",
    params={"formato": "checagem", "tag": "inteligencia-artificial", "page": 1},
    headers={"User-Agent": USER_AGENT},
    timeout=30,
)
resp.raise_for_status()

DATA_RAW.mkdir(parents=True, exist_ok=True)
out_path = DATA_RAW / "_debug_pagina1.html"
out_path.write_text(resp.text, encoding="utf-8")

print(f"Status HTTP: {resp.status_code}")
print(f"Tamanho do HTML recebido: {len(resp.text)} caracteres")
print(f"Salvo em: {out_path}")
print("\nContém a palavra 'checagem' no HTML bruto?", "checagem" in resp.text.lower())
print("Contém a palavra 'falso' no HTML bruto?", "falso" in resp.text.lower())
print("Contém '__NEXT_DATA__' (indício de app Next.js com dados via JSON)?",
      "__next_data__" in resp.text.lower())
print("Contém '<script id=\"__NEXT_DATA__\"'?",
      "__next_data__" in resp.text.lower())

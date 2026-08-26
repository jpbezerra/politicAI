# -*- coding: utf-8 -*-
"""
Documenta a coleta real do veredito em texto (não heurístico) para os 322 itens
do Dataset A, a partir das páginas individuais de checagem do TSE
(justicaeleitoral.jus.br/fato-ou-boato/checagens/<ano>/<slug>).

## Por que esta coleta existe

A coleta original do Dataset A (`raw_scrape_dataset_a_tse.py` /
`raw_scrape_dataset_a_extra_tags.py`, ver `parse_dataset_a.py`) só visitou as
páginas de LISTAGEM de busca do site — nunca a página de cada checagem
individual. Por isso ela nunca capturou nem a URL de cada item, nem o corpo
completo do texto: só título, resumo e data, que é tudo que a listagem expõe.
O veredito (selo "FALSO"/"BOATO"/"GOLPE" mostrado na listagem) é uma imagem,
não texto, e por isso `veredito_estimado` (`gen_notebook_a.py`, Seção 3.2)
sempre foi uma heurística sobre o padrão de abertura do título, nunca uma
leitura do veredito real.

O usuário questionou se isso exigia OCR na imagem do selo, hipotetizando que
a página INDIVIDUAL de cada checagem (diferente da listagem) pudesse conter o
veredito como texto real, num parágrafo "Por que é boato?" / "Por que é
distorcido" (ou variações sem o "?"). Inspecionando exemplos reais de páginas
individuais nesta sessão, confirmamos que sim: quando presente, esse parágrafo
é HTML real, capturável via `<article>.textContent`, nunca uma imagem — OCR
não é necessário para os itens onde essa seção existe.

## O que NÃO é universal (limitação honesta)

A seção "Por que é X" é dependente do template usado na página. Checagens mais
recentes / redesenhadas (majoritariamente 2023-2026, formato "O que é boato /
O que é fato / Por que é X") costumam ter essa seção. Checagens mais antigas
(narrativas, sobretudo 2018-2022) frequentemente expressam o veredito em prosa
livre (ex.: "Essa informação é FALSA!") sem o cabeçalho padronizado — nesses
casos, a extração por regex não encontra nada e o item continua dependendo da
heurística de título (`veredito_estimado`) como já documentado.

## Método de coleta (como os 322 resultados abaixo foram obtidos)

1. **Bloqueio de rede confirmado**: o sandbox de execução deste projeto não
   tem acesso de rede direto a `justicaeleitoral.jus.br` (egress allowlist não
   inclui o domínio) — `curl`/`requests` falham com conexão recusada. Toda
   coleta precisou passar pela extensão Claude in Chrome, com uma aba real
   carregada no domínio do TSE.
2. **`fetch()` same-origin via JS injetado na aba**: em vez de navegar página
   por página (lento e sujeito a instabilidade de captura de tela), o método
   usado foi executar JavaScript diretamente no contexto da aba já carregada
   (`javascript_tool`, ação `javascript_exec`) e rodar `fetch()` para outras
   URLs do MESMO domínio — sem CORS, sem navegação, sem renderização. Isso
   permitiu buscar e comparar dezenas de páginas por chamada de ferramenta.
3. **Reconstrução de URL por slugificação do título**: o Plone (CMS do site)
   gera o slug da URL a partir do título vigente NO MOMENTO DA CRIAÇÃO da
   página — replicado em Python como:

   ```python
   def slugify(title):
       s = title.strip().lower()
       s = unicodedata.normalize('NFKD', s)
       s = ''.join(c for c in s if not unicodedata.combining(c))
       s = re.sub(r'[^a-z0-9]+', '-', s)
       return s.strip('-')
   ```

   URL candidata = `.../checagens/{ano_publicacao}/{slugify(titulo)}`.
4. **Resolução em 3 níveis** (porque títulos são às vezes editados depois da
   criação da página — evidenciado por "Atualizado em" != "Publicado em" —, o
   que quebra a slugificação ingênua em boa parte dos casos mais antigos):
   1. `slug_direto`: tenta a URL candidata; aceita só se o `<title>` da
      página bater exatamente com o título esperado (normalizado).
   2. `busca_com_filtro`: cai para a busca do site
      (`@@search?SearchableText=<titulo>&Subject:list=fake+news`), testando
      cada link `/checagens/` retornado até achar título exatamente igual.
   3. `busca_sem_filtro`: repete a busca SEM o filtro de tag "fake news" —
      necessário porque os itens `FOB-EXTRA-*` (vindos de outras 7 tags
      temáticas) não aparecem nesse filtro.
   4. Se nenhuma bater: `nao_localizado`, registrado honestamente (nunca um
      chute).
5. **Extração do veredito**: `texto = <article>.textContent` (ou `<body>` se
   não houver `<article>`), colapsando espaços; regex
   `/por que (?:é|eh)\s+([a-zà-üç]+)/i` captura a palavra seguinte, em
   minúsculas (ex.: "boato", "distorcido"). Ausência de match = página
   localizada, mas sem essa seção no template (não é um "não encontrado").
6. **Execução em lotes**: os 322 itens foram divididos em 13 lotes de ~25,
   cada lote resolvido numa única chamada de `javascript_exec` (função
   `processar` percorrendo os 3 níveis por item, sequencialmente dentro do
   lote). Coletado em 25/08/2026.

## Honestidade sobre reprodutibilidade

Este script NÃO é executável de ponta a ponta como os `raw_scrape_*.py`
anteriores, porque depende de uma aba de navegador real autenticada na mesma
origem do site (bloqueio de rede do sandbox, ver item 1 acima) — não existe
hoje uma chamada `requests.get()` que reproduza isso neste ambiente. O
resultado bruto e completo da coleta (322 linhas, uma por item de
`dataset_a_fato_ou_boato_completo.csv`) está persistido, tal como coletado,
em `data/raw/dataset_a_veredito_paginas_individuais.csv` — com colunas
`id_checagem`, `metodo_localizacao_pagina`, `url_checagem_individual`,
`veredito_texto_pagina` (vazio quando a página foi localizada mas não tinha a
seção "Por que é X", ou quando `metodo_localizacao_pagina == "nao_localizado"`).
Essa é a fonte de verdade lida por `merge_verdito_real_dataset_a.py`.
"""

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"

if __name__ == "__main__":
    df = pd.read_csv(DATA_RAW / "dataset_a_veredito_paginas_individuais.csv", keep_default_na=False)
    assert len(df) == 322, f"Esperado 322 linhas, achou {len(df)}"
    print(f"Coleta de veredito real: {len(df)} itens processados")
    print(df["metodo_localizacao_pagina"].value_counts())
    com_texto = (df["veredito_texto_pagina"] != "").sum()
    print(f"Com veredito real extraído da página individual: {com_texto} ({com_texto/len(df)*100:.1f}%)")
    print(df.loc[df["veredito_texto_pagina"] != "", "veredito_texto_pagina"].value_counts())

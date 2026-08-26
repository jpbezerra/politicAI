# -*- coding: utf-8 -*-
"""
Documenta uma PROVA DE CONCEITO (não uma coleta completa) de extração do
texto integral das páginas individuais de checagem do TSE (Dataset A), como
resposta à pergunta do autor: "você conseguiu salvar o texto inteiro?".

## Status: prova de conceito, deliberadamente NÃO escalada para os 322 itens

Só os 10 primeiros itens localizados (`FOB-0001` a `FOB-0010`, de um total de
317 páginas localizadas de 322 — ver `raw_scrape_dataset_a_veredito_paginas.py`)
tiveram o texto completo efetivamente extraído e salvo. O resultado está em
`data/raw/dataset_a_texto_completo_amostra.json` (10 registros:
`id_checagem`, `texto_completo_pagina`, `hashtags_agencia_parceira`,
`url_checagem_individual`).

Essa decisão foi tomada explicitamente com o autor, não por limitação técnica
não resolvida — o método abaixo funciona e poderia ser repetido para os 307
itens restantes. O motivo de não escalar:

1. O dado que a Fase 3 realmente usa é o VEREDITO (Seção 20 do PRD), que já
   foi extraído para os 322 itens originais via `raw_scrape_dataset_a_veredito_paginas.py`.
   O texto integral da página é material bruto adicional, não uma feature do
   pipeline atual.
2. O valor analítico do texto integral só se realizaria numa etapa futura e
   distinta (ex.: reler manualmente ou reclassificar com mais cuidado os ~240
   itens sem a seção "Por que é X", usando a prosa livre da página) — que não
   foi pedida nem executada nesta sessão. Coletar o texto sem esse plano de
   uso concreto seria esforço não amortizado.
3. O método de coleta (abaixo) é manual e frágil: depende de uma aba real do
   Chrome permanecer aberta e responsiva, e de contornar dois limites opacos
   da ferramenta de execução de JS (truncamento por string e por payload
   total, ambos documentados abaixo). Não é um script Python autônomo
   re-executável sem intervenção — rodar os ~31 lotes restantes exigiria o
   mesmo processo manual, chamada por chamada.

Se o texto completo dos itens restantes for necessário no futuro, o método
abaixo é reprodutível como está.

## Descoberta feita durante o teste: hashtag de agência parceira no `alt` da imagem

Além do parágrafo "Por que é X" (Seção 20), algumas páginas têm um `<img>`
(o link para a matéria ORIGINAL da agência parceira — Boatos.org, Fato ou
Fake/G1, Agência Lupa etc.) cujo atributo `alt` contém um veredito em formato
de hashtag escrito pela própria agência, ex.:

    "Logo do site  - Fato ou Fake - Acesse a matéria original sobre É #FAKE
    que Daniela Lima tenha dito que Bolsonaro ganhou as eleições de 2022"

Isso É texto real (não é OCR, não é heurística) — mas não é um campo único e
limpo: uma mesma página do TSE pode reunir a checagem de MAIS DE UMA agência
parceira sobre a mesma narrativa ampla, cada uma com sua própria hashtag,
fraseada de um jeito diferente (`#boato`, `#Fake`, `#Verificamos`, etc.). Por
isso este dado foi salvo como `hashtags_agencia_parceira` (lista, pode ter
0, 1 ou mais itens por página) e NÃO foi promovido a um valor único de
`fonte_veredito` — normalizar isso exigiria decidir, por agência, o que cada
hashtag/expressão significa, o que não foi feito nesta sessão.

## Método de coleta (o que de fato rodou, para os 10 itens da amostra)

1. Mesma base de acesso da Seção 20: sandbox sem rede direta ao domínio do
   TSE, então tudo passou por `fetch()` same-origin injetado via JS numa aba
   real do Claude in Chrome (`javascript_tool`, `javascript_exec`).
2. **Dois limites de truncamento da ferramenta, descobertos empiricamente**:
   - Um único valor-string retornado (ex.: um campo `texto_completo` de
     alguns milhares de caracteres) é truncado silenciosamente em ~1000
     caracteres, com um marcador `"[TRUNCATED]"` — mesmo que o payload total
     seja pequeno.
   - O payload total também tem um teto: acima de ~50KB, o resultado é
     redirecionado para um arquivo salvo — mas esse arquivo, ao ser lido de
     volta pela ferramenta `Read`, TAMBÉM é cortado em 50KB (confirmado: um
     lote de 15 itens, ~51,6KB, foi cortado no meio do item 14 de 15).
3. **Contorno usado**: cada texto é dividido em um ARRAY de pedaços de até
   900 caracteres (`splitChunks`, abaixo) em vez de uma string única — isso
   evita o truncamento por valor, já que cada pedaço fica abaixo do teto de
   ~1000 caracteres. E o lote foi limitado a 10 itens por chamada — testado
   e confirmado que produz ~35-40KB totais, com entrega inline completa, sem
   redirecionamento para arquivo.

```javascript
async function fetchDoc(url) {
  const resp = await fetch(url, {credentials: 'omit'});
  const html = await resp.text();
  return new DOMParser().parseFromString(html, 'text/html');
}

function extrairTexto(doc) {
  const article = doc.querySelector('article') || doc.body;
  return article.textContent.replace(/\s+/g, ' ').trim();
}

function extrairHashtags(doc) {
  return Array.from(doc.querySelectorAll('img'))
    .map(i => i.getAttribute('alt'))
    .filter(a => a && /#\w+/.test(a));
}

function splitChunks(s, n) {
  const out = [];
  for (let i = 0; i < s.length; i += n) out.push(s.slice(i, i + n));
  return out;
}

async function processar(items) {
  const out = [];
  for (const it of items) {
    try {
      const doc = await fetchDoc(it.url_checagem_individual);
      const texto = extrairTexto(doc);
      out.push({id: it.id_checagem, tags: extrairHashtags(doc), tc: splitChunks(texto, 900)});
    } catch (e) {
      out.push({id: it.id_checagem, erro: String(e).slice(0, 150)});
    }
  }
  return out;
}

// items = 10 objetos {id_checagem, url_checagem_individual} por vez, lidos
// de data/raw/dataset_a_veredito_paginas_individuais.csv (coluna
// url_checagem_individual, filtrando metodo_localizacao_pagina != "nao_localizado")
return await processar(items);
```

4. **Reconstrução em Python**: `texto_completo_pagina = "".join(item["tc"])`
   por item — verificado que a reconstrução bate exatamente com o texto obtido
   num teste isolado de item único antes da chunking (5016 caracteres para
   `FOB-0001`, idêntico nos dois métodos).

## Para retomar a coleta completa (se decidido no futuro)

Repetir o passo 3 para os 307 itens restantes (317 localizados − 10 já
coletados), em lotes de 10, usando os `id_checagem`/`url_checagem_individual`
de `data/raw/dataset_a_veredito_paginas_individuais.csv` (linhas com
`metodo_localizacao_pagina != "nao_localizado"`), salvando cada lote e depois
concatenando em um único arquivo no mesmo formato de
`data/raw/dataset_a_texto_completo_amostra.json`. Nenhuma etapa de merge no
pipeline (`gen_notebook_a.py`/`gen_notebook_c.py`) foi criada para esse dado —
seria decidido separadamente, dado que o texto completo hoje é material de
apoio, não uma feature do pipeline.
"""

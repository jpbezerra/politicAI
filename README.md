# Fake news por IA no eleitor brasileiro — dados e notebooks

Repositório de dados e análise exploratória para o estudo empírico sobre o impacto da desinformação eleitoral gerada por Inteligência Artificial no eleitor brasileiro, preparado para submissão à **XV SBTI** e aos **Annals of Data Analysis (ADA-UFPE)**.

Todos os dados aqui são **reais**, coletados diretamente das fontes públicas listadas abaixo por navegação (não há nenhum dado sintético, simulado ou inventado neste repositório). Onde a coleta é uma amostra em vez de uma população completa, isso está documentado explicitamente nos próprios dados e nos notebooks — nunca escondido.

## Contexto do estudo

O projeto testa cinco hipóteses sobre desinformação eleitoral assistida por IA, comparada à desinformação tradicional:

| Hipótese | Resumo | Teste estatístico previsto |
|---|---|---|
| H1 | Desinformação por IA se espalha/engaja mais rápido que a tradicional | Mann-Whitney U / GLM Binomial Negativo |
| H2 | Desinformação por IA se concentra em formatos audiovisuais (vídeo/áudio) | Qui-quadrado / V de Cramér |
| H3 | Desinformação por IA demora mais (ou menos) para ser desmentida | Kaplan-Meier, Log-Rank, Cox |
| H4 | Desinformação por IA ataca mais a pessoa do candidato do que instituições | Qui-quadrado / Regressão logística multinomial |
| H5 | Desinformação (de ambos os tipos) se acelera perto do dia da eleição | Séries temporais interrompidas (splines) |

Este repositório cobre a **Fase 2** do roteiro: coleta de dados reais e EDA (análise exploratória) dos Datasets A e B. Os testes formais de H1–H5 (Fase 3) dependem de rotulagem manual de validação sobre as heurísticas aqui descritas — ver "Limitações" em cada notebook.

## Estrutura do repositório

```
.
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/                                    # saída direta dos parsers, sem enriquecimento
│   │   ├── dataset_a_fato_ou_boato.csv         # 267 itens, tag "fake news" (TSE)
│   │   ├── dataset_a_extra_tags.csv            # 55 itens novos, 7 tags adicionais (TSE)
│   │   └── dataset_b_aosfatos.csv              # 553 itens (Aos Fatos)
│   └── processed/                              # dados prontos para análise (gerados pelos notebooks)
│       ├── dataset_a_fato_ou_boato_completo.csv    # raw/dataset_a_*.csv unidos e deduplicados (322 itens)
│       ├── dataset_a_fato_ou_boato_enriquecido.csv # + features (rótulo IA, categoria, etc.)
│       └── dataset_b_aosfatos_enriquecido.csv      # + features (vetor de mídia, alvo do ataque, etc.)
├── notebooks/
│   ├── 01_dataset_a_fato_ou_boato_eda.ipynb    # limpeza + engenharia de features + EDA do Dataset A
│   └── 02_dataset_b_aosfatos_eda.ipynb         # idem para o Dataset B
└── scripts/
    ├── raw_scrape_dataset_a_tse.py             # texto bruto coletado (tag "fake news")
    ├── raw_scrape_dataset_a_extra_tags.py      # texto bruto coletado (7 tags adicionais)
    ├── parse_dataset_a.py                      # raw_scrape_dataset_a_tse.py -> data/raw/dataset_a_fato_ou_boato.csv
    ├── build_dataset_a_extra.py                # raw_scrape_dataset_a_extra_tags.py -> data/raw/dataset_a_extra_tags.csv (já deduplicado)
    ├── merge_dataset_a.py                      # une os dois CSVs do Dataset A -> data/processed/dataset_a_fato_ou_boato_completo.csv
    ├── raw_scrape_dataset_b_aosfatos.py         # texto bruto coletado (Aos Fatos, 3 tags)
    ├── parse_dataset_b.py                      # raw_scrape_dataset_b_aosfatos.py -> data/raw/dataset_b_aosfatos.csv
    ├── scrape_dataset_a_http.py                 # scraper HTTP real (requests+BeautifulSoup) do Dataset A -- reprodução independente, ver seção abaixo
    ├── scrape_dataset_b_http.py                 # scraper HTTP real (requests+BeautifulSoup) do Dataset B -- reprodução independente, ver seção abaixo
    ├── gen_notebook_a.py                       # gera notebooks/01_....ipynb (código + markdown, sem outputs)
    ├── gen_notebook_b.py                       # gera notebooks/02_....ipynb (código + markdown, sem outputs)
    └── execute_notebooks.py                    # executa um .ipynb via nbclient, embutindo outputs/gráficos reais
```

## Dataset A — Coalizão "Fato ou Boato" (TSE)

**Fonte:** [justicaeleitoral.jus.br/fato-ou-boato](https://www.justicaeleitoral.jus.br/fato-ou-boato), agregador oficial da Justiça Eleitoral que reúne checagens de 10 agências parceiras (AFP, Agência Lupa, Aos Fatos, Boatos.org, Comprova, E-Farsas, Estadão Verifica, Fato ou Fake, Justiça Eleitoral, UOL Confere).

**Como foi coletado:** o site é renderizado no servidor (Plone CMS) e expõe um endpoint de busca (`/@@search`) com paginação via `b_start:int` e filtro por tag via `Subject:list`. O ambiente de execução deste projeto não tem acesso direto à internet (scripts com `requests`/`curl` não funcionam), então a coleta foi feita por navegação real (Claude in Chrome), extraindo o texto de cada página de resultados e guardando-o verbatim nos arquivos `raw_scrape_dataset_a_*.py` antes de qualquer parsing. Um scraper HTTP de verdade (`scripts/scrape_dataset_a_http.py`) também está incluído para reprodução independente por quem tiver acesso à internet — ver "Comprovação da coleta" abaixo.

**Composição final (322 itens, `data/processed/dataset_a_fato_ou_boato_completo.csv`):**

| Origem | Itens | Cobertura |
|---|---|---|
| Tag `fake news` | 267 | população completa da tag (267/267) |
| Tags adicionais novas | 55 | ver tabela abaixo — só itens que não apareciam na tag `fake news` |

A tag `fake news` sozinha não muda de tamanho desde a coleta original (confirmado novamente em 23/08/2026: ainda 267/267) — não há itens novos possíveis nela. Para aumentar o dataset com dados reais, sete tags adicionais tematicamente ligadas a desinformação eleitoral (fraude em urnas, apuração, biometria etc.) foram coletadas por completo e comparadas item a item com a tag `fake news`:

| Tag adicional | Itens no site | Já estavam em `fake news` | Genuinamente novos |
|---|---|---|---|
| `fraude` | 85 | 59 | 26 |
| `boletim de urna` | 28 | 15 | 13 |
| `código-fonte` | 23 | 17 | 6 |
| `totalização` | 17 | 4 | 13 |
| `biometria` | 11 | 6 | 5 |
| `resultado` | 12 | 8 | 4 |
| `crime eleitoral` | 4 | 3 | 1 |
| **Total (itens únicos entre as 7 tags)** | **151** | **96** | **55** |

(A soma das colunas "já estavam"/"novos" passa de 151/96/55 porque um item pode ter mais de uma tag adicional ao mesmo tempo — por isso o total oficial é o de itens únicos, não a soma das linhas.)

A deduplicação é por título exato (normalizando aspas tipográficas retas/curvas) — ver `scripts/build_dataset_a_extra.py`. As tags foram escolhidas por serem sobre o mesmo tema do estudo (fraude/segurança do processo eleitoral); tags genéricas de golpe financeiro/phishing do mesmo site (ex.: cobrança falsa de boleto, "Meu Título Digital") foram deixadas de fora por estarem fora do escopo de desinformação eleitoral.

**Limitações conhecidas:**
- O site não expõe veredito, agência responsável nem tags temáticas como texto por item na listagem — só título, resumo e data. O selo de veredito ("FALSO"/"BOATO"/"GOLPE") é uma imagem, não texto.
- `rotulo_ia`, `veredito_estimado`, `categoria_macro` e `alvo_ataque` (gerados no notebook 01) são **heurísticas textuais** sobre título+resumo, não classificações oficiais — precisam de validação manual amostral antes de testes inferenciais definitivos.
- Todas as tags (originais e adicionais) vêm do mesmo agregador e das mesmas 10 agências — a expansão aumenta volume, não diversifica a fonte. Diversidade de fonte vem do Dataset B.
- Cobertura total do site: 322 dos 462 itens (os ~140 restantes são majoritariamente alertas de golpe financeiro/phishing, fora do escopo temático).

## Dataset B — Arquivo de checagens do Aos Fatos

**Fonte:** [aosfatos.org/noticias/?formato=checagem](https://www.aosfatos.org/noticias/?formato=checagem), arquivo público de checagens da agência Aos Fatos (um dos parceiros da Coalizão Fato ou Boato do TSE). Assim como no Dataset A, a coleta original foi por navegação real (evidência em `raw_scrape_dataset_b_aosfatos.py`); `scripts/scrape_dataset_b_http.py` fornece um scraper HTTP real para reprodução independente — ver "Comprovação da coleta" abaixo.

**Por que esta fonte importa especialmente para o estudo:** ao contrário do Dataset A, o Aos Fatos rotula editorialmente cada checagem com **veredito** e **tema**, incluindo o tema `inteligência artificial` de forma explícita. Ou seja, aqui o rótulo IA-vs.-tradicional é uma classificação humana da própria redação jornalística, não uma heurística de regex.

**Composição final (553 itens, `data/raw/dataset_b_aosfatos.csv`):**

| Tag pesquisada | Itens | Cobertura |
|---|---|---|
| `inteligencia-artificial` | 122 | população completa (11/11 páginas) |
| `eleicoes-2022` | 419 | população completa (35/35 páginas) |
| `eleicoes-2026` | 12 | população completa (1/1 página) |

A tag `eleicoes-2022` começou como uma amostra de 7 páginas (84 itens) e foi ampliada para as 35 páginas completas (419 itens) a pedido do usuário. Três páginas (13, 27 e 31) retornaram, na primeira tentativa, conteúdo idêntico ao da página anterior — um glitch de cache do próprio site já visto durante a coleta original — e foram recarregadas (navegando para outra página e voltando) até confirmar conteúdo único antes de aceitas. Nenhuma página foi inventada.

**Limitações conhecidas:**
- A listagem usada na coleta não expõe a data de publicação por item (aparece só na página individual de cada checagem, não visitada nesta coleta). Isso impede calcular `dias_para_eleicao` e latência de desmentido (H3) diretamente neste dataset.
- `vetor_midia` e `alvo_ataque` (gerados no notebook 02) são heurísticas sobre o título — só `rotulo_grupo` (IA vs. Tradicional) e `veredito`/`tema` são classificação editorial real.

## Notebooks

Ambos os notebooks já vêm **executados**, com outputs e gráficos embutidos — não é preciso rodar nada para ver os resultados, só abrir no Jupyter, VS Code ou GitHub (que renderiza `.ipynb` nativamente).

- **`01_dataset_a_fato_ou_boato_eda.ipynb`**: carga do Dataset A completo (322 itens), limpeza, engenharia de features heurísticas (rótulo IA, veredito estimado, categoria temática, alvo do ataque, dias até a eleição), EDA descritiva, teste qui-quadrado exploratório (preview de H2/H4), visualizações, e exportação para `data/processed/dataset_a_fato_ou_boato_enriquecido.csv`.
- **`02_dataset_b_aosfatos_eda.ipynb`**: carga do Dataset B (553 itens), limpeza, engenharia de features (rótulo de grupo real, vetor de mídia heurístico, alvo do ataque heurístico), EDA descritiva, testes qui-quadrado exploratórios (preview de H2/H4) usando o rótulo editorial real, comparação com a heurística do Dataset A, e exportação para `data/processed/dataset_b_aosfatos_enriquecido.csv`.

## Comprovação da coleta: evidência bruta vs. scripts de reprodução independente

Este repositório contém **dois tipos diferentes de arquivo** relacionados à coleta, e é importante não confundi-los — especialmente para fins de pesquisa, onde a proveniência dos dados precisa ser auditável:

| Arquivo | O que é | Fez a coleta original? |
|---|---|---|
| `raw_scrape_dataset_a_tse.py`, `raw_scrape_dataset_a_extra_tags.py`, `raw_scrape_dataset_b_aosfatos.py` | **Registro bruto e evidência primária.** Cada um contém, em variáveis Python, o texto renderizado extraído verbatim de páginas reais dos sites-fonte (cada página com a URL/tag/parâmetros exatos documentados em comentário), copiado por navegação real via Claude in Chrome. | **Sim** — é exatamente o texto que os parsers (`parse_dataset_a.py`, `build_dataset_a_extra.py`, `parse_dataset_b.py`) transformam nos CSVs de `data/raw/`. |
| `scrape_dataset_a_http.py`, `scrape_dataset_b_http.py` | **Scripts de raspagem HTTP de verdade** (`requests` + `BeautifulSoup`), que fazem requisições reais aos sites do TSE e do Aos Fatos, paginam automaticamente e aplicam a mesma lógica de parsing já validada (o de Dataset B inclusive importa e reusa `parse_page()` de `parse_dataset_b.py` diretamente, em vez de duplicar a lógica). | **Não.** Ver aviso abaixo. |

**Por que existem os dois:** o ambiente onde este projeto foi construído roda em um sandbox sem acesso de saída à internet — uma chamada de teste real (`python3 scripts/scrape_dataset_a_http.py "fake news"`) falha com:

```
requests.exceptions.ProxyError: HTTPSConnectionPool(host='www.justicaeleitoral.jus.br', port=443):
Max retries exceeded ... Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden'))
```

Isso confirma, de forma verificável, que `requests`/`curl` não conseguem sair da rede do sandbox — por isso a coleta original teve que ser feita por navegação real (Claude in Chrome), e o texto obtido foi preservado verbatim nos arquivos `raw_scrape_*.py` como evidência primária, em vez de simplesmente descartado depois do parsing.

`scrape_dataset_a_http.py` e `scrape_dataset_b_http.py` foram escritos depois, especificamente para dar a qualquer pessoa (você, um revisor, um coautor) com acesso normal à internet uma forma de **re-coletar os mesmos dados de forma independente** e comparar o resultado com os CSVs já publicados aqui, como checagem de reprodutibilidade. Eles reaproveitam as mesmas URLs, os mesmos parâmetros de paginação e a mesma lógica de parsing por linha de data já validada manualmente contra os 322 + 553 itens deste repositório — mas **não foram executados com sucesso neste ambiente** (só o teste acima, que falhou por falta de rede, e não por erro de lógica) e portanto não geraram nenhum dos dados existentes. Rode-os você mesmo fora deste sandbox para validar:

```bash
pip install requests beautifulsoup4
python3 scripts/scrape_dataset_a_http.py "fake news"      # -> data/raw/scrape_http_fake-news.csv
python3 scripts/scrape_dataset_b_http.py inteligencia-artificial  # -> data/raw/scrape_http_aosfatos_inteligencia-artificial.csv
```

Eles gravam em arquivos `scrape_http_*.csv` separados (nunca sobrescrevem `dataset_a_fato_ou_boato.csv` nem `dataset_b_aosfatos.csv`), para que a comparação linha a linha com os dados originais seja explícita em vez de uma substituição silenciosa.

## Como reproduzir

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. gerar data/raw/ a partir do texto bruto já coletado
python3 scripts/parse_dataset_a.py
python3 scripts/build_dataset_a_extra.py
python3 scripts/merge_dataset_a.py
python3 scripts/parse_dataset_b.py

# 2. (re)gerar os notebooks (código + markdown, sem outputs)
python3 scripts/gen_notebook_a.py
python3 scripts/gen_notebook_b.py

# 3. executar os notebooks e embutir outputs/gráficos reais
python3 scripts/execute_notebooks.py notebooks/01_dataset_a_fato_ou_boato_eda.ipynb
python3 scripts/execute_notebooks.py notebooks/02_dataset_b_aosfatos_eda.ipynb
```

Rode os scripts a partir da raiz do repositório (ou de dentro de `scripts/` — todos os caminhos são relativos ao próprio arquivo do script, não ao diretório de onde `python3` foi chamado). Os scripts `raw_scrape_*.py` apenas armazenam texto já extraído por navegação manual — eles não fazem requisições de rede. Para re-raspar automaticamente os sites-fonte (fora deste sandbox, que não tem acesso à internet), use `scrape_dataset_a_http.py` e `scrape_dataset_b_http.py` — ver a seção "Comprovação da coleta" acima.

## O que ainda falta (Fase 3 do roteiro)

- Validação manual de uma amostra das heurísticas (`rotulo_ia`, `veredito_estimado`, `categoria_macro`, `alvo_ataque`, `vetor_midia`) contra checagem humana, com Cohen's kappa.
- Coleta complementar de data de publicação por item no Dataset B (via páginas individuais de checagem) para viabilizar H3 e H5 nele.
- **Dataset C (unificado):** cruzamento de A e B por similaridade de título/tema, incluindo preenchimento de datas ausentes do Dataset B via correspondência com o Dataset A.
- Testes estatísticos formais de H1–H5 sobre o rótulo validado.

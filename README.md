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
│   │   ├── dataset_b_aosfatos.csv              # 553 itens (Aos Fatos, só título/veredito/tema/tag)
│   │   ├── dataset_b_completo_inteligencia-artificial.csv  # 122 itens + data + texto completo (coleta local)
│   │   ├── dataset_b_completo_eleicoes-2022.csv            # 419 itens + data + texto completo (coleta local)
│   │   ├── dataset_b_completo_eleicoes-2026.csv            # 12 itens + data + texto completo (coleta local)
│   │   └── dataset_b_completo.csv              # os 3 CSVs acima unidos, com data real recuperada (553 itens)
│   └── processed/                              # dados prontos para análise (gerados pelos notebooks)
│       ├── dataset_a_fato_ou_boato_completo.csv    # raw/dataset_a_*.csv unidos e deduplicados (322 itens)
│       ├── dataset_a_fato_ou_boato_enriquecido.csv # + features (rótulo IA, categoria, etc.)
│       ├── dataset_b_aosfatos_enriquecido.csv      # + features (data real, corpo_artigo, vetor de mídia/alvo do ataque em 2 versões)
│       └── dataset_c_unificado.csv                 # A + B harmonizados (875 itens) + flag de prováveis duplicatas
├── notebooks/
│   ├── 01_dataset_a_fato_ou_boato_eda.ipynb    # limpeza + engenharia de features + EDA do Dataset A
│   ├── 02_dataset_b_aosfatos_eda.ipynb         # idem para o Dataset B
│   └── 03_dataset_c_unificado_eda.ipynb        # unificação A+B, detecção de duplicatas, EDA combinada
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
    ├── scrape_dataset_b_completo.py             # coleta local (fora do sandbox) de data + texto completo por checagem individual -- ver seção abaixo
    ├── debug_dump_html.py                       # script de diagnóstico usado para achar o bug de parsing do scraper acima (não é parte do pipeline)
    ├── build_dataset_b_completo.py              # une os 3 CSVs de scrape_dataset_b_completo.py -> data/raw/dataset_b_completo.csv, com data real recuperada
    ├── gen_notebook_a.py                       # gera notebooks/01_....ipynb (código + markdown, sem outputs)
    ├── gen_notebook_b.py                       # gera notebooks/02_....ipynb (código + markdown, sem outputs)
    ├── gen_notebook_c.py                       # gera notebooks/03_....ipynb (código + markdown, sem outputs)
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
- **O dataset não tem nenhum item real de desinformação por IA (`rotulo_ia_bin` = 0% "IA") — verificado ao vivo, não só nos dados já baixados.** Além do teste de vocabulário ampliado dentro do notebook (Seção 3.1.1), voltamos ao site do TSE em navegação real para checar (a) se existe alguma tag entre as 68 disponíveis dedicada a IA/deepfake — não existe — e (b) uma busca textual no acervo completo (462 itens, não só os 322 coletados) por termos como "inteligência artificial", "deepfake", "clonagem de voz", "ChatGPT" etc. Os poucos resultados já estavam entre os 322 itens coletados (a menção a IA fica no corpo do texto, não no título/resumo) ou apontavam para conteúdo externo ao site do TSE. Conclusão: não há dado novo e real para adicionar a partir desta fonte — só o Dataset B (Aos Fatos) tem checagens reais rotuladas como IA (122 itens, ver abaixo).

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
- ~~A listagem usada na coleta não expõe a data de publicação por item~~ — **resolvido.** Ver "`scrape_dataset_b_completo.py`" abaixo: a data e o texto completo de cada uma das 553 checagens foram coletados individualmente, permitindo calcular `dias_para_eleicao` e um preview real de H3/H5 no notebook 02.
- `vetor_midia` e `alvo_ataque` (gerados no notebook 02) existem em duas versões — sobre o título e sobre o texto completo — e continuam sendo heurísticas de palavra-chave, não classificação editorial; só `rotulo_grupo` (IA vs. Tradicional) e `veredito`/`tema` são classificação editorial real. A versão de texto completo do `alvo_ataque` mostrou sinais de contaminação lexical (0% "indeterminado" no dataset inteiro — documentado no notebook) e deve ser tratada com mais cautela que a versão de título, não menos.
- A comparação de `dias_para_eleicao` entre os grupos IA e Tradicional tem um confundimento de desenho amostral (a tag `eleicoes-2022`, quase todo o grupo Tradicional, é um recorte por ano eleitoral; a tag `inteligencia-artificial` é um recorte por tema, sem filtro de proximidade eleitoral) — documentado em detalhe no notebook 02, Seção 4.5.

## Notebooks

Ambos os notebooks já vêm **executados**, com outputs e gráficos embutidos — não é preciso rodar nada para ver os resultados, só abrir no Jupyter, VS Code ou GitHub (que renderiza `.ipynb` nativamente).

- **`01_dataset_a_fato_ou_boato_eda.ipynb`**: carga do Dataset A completo (322 itens), limpeza, engenharia de features heurísticas (rótulo IA, veredito estimado, categoria temática, alvo do ataque, **vetor de mídia**, dias até a eleição). Inclui uma investigação dedicada ao achado de que 0% dos itens foi rotulado como IA (testado contra um vocabulário ampliado, não é falso negativo de regex), a revisão da heurística de veredito que dobrou a cobertura de classificação (24,5% → ~56%, com o antes/depois documentado no próprio notebook), um teste de efeito de seleção entre a tag "fake news" e as 7 tags adicionais, um preview visual de H5 (volume mensal com as datas de eleição marcadas) e um raio-x de termos mais frequentes nos títulos. Termina exportando para `data/processed/dataset_a_fato_ou_boato_enriquecido.csv`.
- **`02_dataset_b_aosfatos_eda.ipynb`**: carga do Dataset B (553 itens, com **data de publicação real e texto completo** por item — ver `data/raw/dataset_b_completo.csv`), limpeza, engenharia de features (rótulo de grupo real, `dias_para_eleicao`/`ciclo_eleitoral_estimado` a partir da data real, e `vetor_midia`/`alvo_ataque` em duas versões — só título e `corpo_artigo`, com a concordância entre elas medida explicitamente). Inclui uma checagem de contaminação entre tags, uma análise de cobertura do campo `tema`, testes qui-quadrado com V de Cramér para os previews de H2 e H4 em ambas as versões — incluindo o teste sobre `veredito` editorial real (IA: 99,2% "falso" vs. Tradicional: 81,0%) —, e um **preview real de H3/H5**. Duas correções de metodologia foram feitas e documentadas nesta versão, não só apontadas como limitação: (1) uma contaminação lexical em `alvo_ataque_texto` (a nuvem de tags do rodapé do site, presente em toda página, inflava artificialmente as contagens) foi corrigida isolando `corpo_artigo` e podando o dicionário de palavras genéricas — o que **inverteu** o achado de H4 (o grupo IA passa a ser mais, não menos, associado a `urna_processo`); (2) um confundimento de desenho amostral em `dias_para_eleicao` (a tag `eleicoes-2022` é um recorte por ano eleitoral, `inteligencia-artificial` não é) foi corrigido com uma comparação por janela temporal equivalente, que mostra que quase todo o efeito ingênuo de H5 (p<0.0001) desaparece quando a amostragem é controlada (p≈0.44-0.78). Fecha com uma checagem de sobreposição de título com o Dataset A e exportação para `data/processed/dataset_b_aosfatos_enriquecido.csv`.
- **`03_dataset_c_unificado_eda.ipynb`**: unifica os Datasets A e B (875 itens) num esquema harmonizado que preserva a origem de cada rótulo (`fonte_rotulo_ia`, `fonte_veredito`, `fonte_categoria_tema` — heurística de regex vs. classificação editorial), detecta prováveis duplicatas entre as duas fontes por similaridade de cosseno sobre TF-IDF de título (10 pares confirmados por inspeção manual, de um agregador — TSE — que inclui o próprio Aos Fatos entre suas 10 agências parceiras), e formaliza com teste estatístico a validação cruzada que o notebook `02` tinha feito de forma só visual (as duas baselines "Tradicional" de A e B não são estatisticamente indistinguíveis em `vetor_midia` — p=0.0376 — mas o efeito é pequeno e concentrado numa categoria plausivelmente por diferença de escopo de texto, não por divergência real do fenômeno). Reforça em cada seção que juntar os dois datasets **não aumenta o poder do teste IA vs. Tradicional** (só o Dataset B contribui itens IA) e repete a correção de janela temporal do notebook `02` com a baseline Tradicional ampliada, chegando à mesma conclusão. Salva `data/processed/dataset_c_unificado.csv`.

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

### `scrape_dataset_b_completo.py` + `build_dataset_b_completo.py` — coleta real de data + texto completo (Dataset B)

O Dataset B tinha uma limitação conhecida: a listagem do Aos Fatos não expõe a data de publicação por item (só título, veredito e tema) — o que impedia qualquer análise de H3/H5 neste dataset. A data (e o texto completo da checagem) **existe**, só que só aparece na página individual de cada checagem, uma por uma — confirmado navegando manualmente até uma checagem real (`aosfatos.org/noticias/tancredo-ulysses-bolsonaro/`), que mostra "20 de agosto de 2026, 15:57" logo no topo. Essa limitação **já está resolvida** — as datas de todas as 553 checagens foram recuperadas com sucesso (ver abaixo).

Como isso significa visitar cada uma das 553 checagens individualmente (não só as ~47 páginas de listagem), e nem o sandbox do Claude nem a VM isolada do Cowork (usada por `device_bash`) conseguem sair para a internet (as duas retornam o mesmo `ProxyError: 403 Forbidden` ao tentar acessar `aosfatos.org`), `scrape_dataset_b_completo.py` foi escrito para **rodar no seu computador**, fora dessas sandboxes:

```bash
pip install requests beautifulsoup4
python scripts/scrape_dataset_b_completo.py inteligencia-artificial   # ~3-5 min, 122 itens
python scripts/scrape_dataset_b_completo.py eleicoes-2022             # ~15-25 min, 419 itens
python scripts/scrape_dataset_b_completo.py eleicoes-2026             # ~1 min, 12 itens
```

Cada execução salva `data/raw/dataset_b_completo_<tag>.csv` com `titulo, veredito, tema, tag_pesquisa, url, data_publicacao, texto_completo`. A extração de cada item da listagem lê a estrutura real do HTML (o link de overlay `<a title="...">` de cada card, e seus elementos-irmãos para veredito/tema), não texto solto por posição — validado item a item contra uma página real antes de ser usado.

**Dois bugs reais foram encontrados e corrigidos durante o uso deste script** (documentados em detalhe no próprio arquivo, seção "HISTÓRICO DE BUG CORRIGIDO"): a v1 usava um parser de texto puro que comparava com `"checagem"` (minúsculo) contra um HTML bruto que na verdade contém `"Checagem"` (maiúsculo, só exibido em minúsculo por CSS) — 100% de falha, corrigido na v2 lendo a estrutura do HTML. A v2, por sua vez, extraía o texto completo corretamente mas continuava com 0% de sucesso ao extrair a **data** de cada checagem: `"20 de agosto de 2026, 15:57"` chega quebrado em 3 nós de texto HTML separados (`"20 de agosto de 2026"`, `","`, `"15:57"`), e a regex exigia tudo numa linha só. Corrigido na v3.

Como o texto completo (`texto_completo`) das 553 checagens já tinha sido baixado corretamente mesmo com o bug de data da v2, **não foi preciso raspar o site de novo**: `scripts/build_dataset_b_completo.py` reaplica a extração de data já corrigida sobre o texto já coletado (sem nenhuma nova requisição de rede), une os 3 CSVs por tag num único `data/raw/dataset_b_completo.csv` e converte a data para ISO 8601 (`data_publicacao_iso`). Rode com:

```bash
cd scripts && python3 build_dataset_b_completo.py
```

Resultado real desta execução: **553/553 (100%) das datas recuperadas**, todas convertidas para ISO 8601. Esse arquivo unificado alimenta a versão atual do notebook `02`, com datas reais (viabilizando H3/H5) e `vetor_midia`/`alvo_ataque` recalculados a partir do texto completo, comparados explicitamente com a versão baseada só no título.

## Como reproduzir

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. gerar data/raw/ a partir do texto bruto já coletado
python3 scripts/parse_dataset_a.py
python3 scripts/build_dataset_a_extra.py
python3 scripts/merge_dataset_a.py
python3 scripts/parse_dataset_b.py
python3 scripts/build_dataset_b_completo.py  # requer os 3 CSVs dataset_b_completo_<tag>.csv já em data/raw/
                                              # (coletados localmente por scrape_dataset_b_completo.py -- ver seção acima)

# 2. (re)gerar os notebooks (código + markdown, sem outputs)
python3 scripts/gen_notebook_a.py
python3 scripts/gen_notebook_b.py
python3 scripts/gen_notebook_c.py  # depende dos dois enriquecidos, rodar por último

# 3. executar os notebooks e embutir outputs/gráficos reais (nesta ordem: 03 lê os .csv
#    enriquecidos que 01 e 02 salvam ao rodar)
python3 scripts/execute_notebooks.py notebooks/01_dataset_a_fato_ou_boato_eda.ipynb
python3 scripts/execute_notebooks.py notebooks/02_dataset_b_aosfatos_eda.ipynb
python3 scripts/execute_notebooks.py notebooks/03_dataset_c_unificado_eda.ipynb
```

Rode os scripts a partir da raiz do repositório (ou de dentro de `scripts/` — todos os caminhos são relativos ao próprio arquivo do script, não ao diretório de onde `python3` foi chamado). Os scripts `raw_scrape_*.py` apenas armazenam texto já extraído por navegação manual — eles não fazem requisições de rede. Para re-raspar automaticamente os sites-fonte (fora deste sandbox, que não tem acesso à internet), use `scrape_dataset_a_http.py` e `scrape_dataset_b_http.py` — ver a seção "Comprovação da coleta" acima.

## O que ainda falta (Fase 3 do roteiro)

- Validação manual de uma amostra das heurísticas (`rotulo_ia`, `veredito_estimado`, `categoria_macro`, `alvo_ataque`/`alvo_ataque_texto`, `vetor_midia`/`vetor_midia_texto`) contra checagem humana, com Cohen's kappa. A contaminação lexical em `alvo_ataque_texto` (0% "indeterminado") e o confundimento de desenho amostral em `dias_para_eleicao` — ambos identificados numa versão anterior deste notebook — já foram corrigidos (notebook 02, Seções 3.5 e 4.5); a validação manual continua pendente para a versão corrigida.
- **Deduplicação mais agressiva entre A e B:** o notebook `03` marcou 10 pares como prováveis duplicatas (similaridade de cosseno ≥0.5) sem removê-los; a faixa 0.3–0.5 (11 pares adicionais) fica para revisão manual antes de uma deduplicação mais completa.
- Uma coleta desenhada especificamente para isolar o efeito de H5 no grupo IA — o notebook `03` confirma, com a baseline Tradicional ampliada (753 itens de A+B), que o confundimento identificado no notebook `02` não se resolve só com mais volume de dados Tradicionais; a tag `inteligencia-artificial` em si não tem filtro de proximidade eleitoral.
- Um modelo estatístico formal para H1/H2/H4 que declare explicitamente, como os notebooks já fazem, que só o Dataset B contribui itens rotulados IA — unificar com o Dataset A não aumenta o poder desse teste específico, só amplia a baseline Tradicional.
- Testes estatísticos formais de H1–H5 sobre o rótulo validado.

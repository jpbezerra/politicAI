# PRD — Sensor de IA Eleitoral & Plataforma "Lentes Contra a Desinformação"

**Projeto:** Impacto das fake news geradas por IA no eleitor brasileiro
**Fase:** 3 (evolução para produto — Motor de ML + Plataforma), a partir da Fase 2 (coleta e EDA dos Datasets A/B/C)
**Autor:** João Pedro (com apoio de Claude, sessões de ago/2026)
**Status:** Documento de handoff — contexto completo para continuar o trabalho em outra ferramenta/IA
**Última atualização:** 24/08/2026

---

## 0. Nota para quem for continuar este projeto

Este documento foi reescrito para ser **autossuficiente**: alguém (ou uma IA) sem acesso ao histórico de conversa anterior deve conseguir entender o projeto inteiro, o que já existe, o que foi descoberto, e o que falta, só lendo este arquivo. Ele substitui a versão anterior do PRD (que cobria só as features novas) e incorpora:

1. O contexto completo do projeto (Fases 1-2, datasets reais, metodologia) — Seção 1.
2. O PRD original das features de Fase 3 (Motor de ML + Plataforma) — Seções 2-8, praticamente inalteradas.
3. O que já foi **efetivamente implementado e testado** nesta fase — Seção 9 (nova).
4. **Descobertas metodológicas** feitas durante a implementação — vieses e contaminações de dados encontrados e (na maioria) corrigidos — Seção 10 (nova, importante).
5. Um **backlog de melhorias técnicas priorizado**, para `/models` e `/web` — Seção 11 (nova).
6. Perguntas em aberto e como rodar tudo do zero — Seções 12-14.

Se você é uma IA continuando este trabalho: **leia a Seção 1 e a Seção 10 antes de mexer em qualquer código.** A Seção 1 explica o princípio inegociável do projeto (só dados reais, toda limitação documentada). A Seção 10 documenta vieses de dados já encontrados — não os reintroduza ao "otimizar" o código.

---

## 1. Contexto completo do projeto

### 1.1 O que é este projeto

Estudo empírico sobre o impacto da desinformação eleitoral gerada por Inteligência Artificial no eleitor brasileiro, preparado para submissão à **XV SBTI** e aos **Annals of Data Analysis (ADA-UFPE)**. Orientado pela profa. Maria do Carmo Soares de Lima (UFPE).

O projeto testa cinco hipóteses sobre desinformação eleitoral assistida por IA, comparada à desinformação tradicional:

| Hipótese | Resumo | Teste estatístico previsto |
|---|---|---|
| H1 | Desinformação por IA se espalha/engaja mais rápido que a tradicional | Mann-Whitney U / GLM Binomial Negativo |
| H2 | Desinformação por IA se concentra em formatos audiovisuais (vídeo/áudio) | Qui-quadrado / V de Cramér |
| H3 | Desinformação por IA demora mais (ou menos) para ser desmentida | Kaplan-Meier, Log-Rank, Cox |
| H4 | Desinformação por IA ataca mais a pessoa do candidato do que instituições | Qui-quadrado / Regressão logística multinomial |
| H5 | Desinformação (de ambos os tipos) se acelera perto do dia da eleição | Séries temporais interrompidas (splines) |

**Princípio inegociável do projeto, que rege todo o trabalho (não é negociável ao "melhorar" nada):** só dados reais são usados — nenhum dado sintético, simulado ou inventado é apresentado como real em nenhuma parte do repositório. Onde a coleta é uma amostra em vez de população completa, isso é documentado explicitamente. Toda heurística (regex, keyword-matching) é distinguida de classificação editorial real no próprio nome das colunas e na documentação. Toda limitação encontrada é documentada, nunca escondida ou "arredondada" para parecer melhor do que é. Esse padrão de honestidade metodológica levou, ao longo do projeto, a encontrar e corrigir múltiplos vieses reais (ver Seção 10) — isso é considerado um resultado do processo, não uma falha a esconder.

### 1.2 Fases do projeto

- **Fase 1-2 (concluída):** coleta de dados reais e EDA (análise exploratória) dos Datasets A, B e C.
- **Fase 3 (em andamento, é o que este PRD detalha):** evolução para produto — motor de ML (`/models`) e plataforma web (`/web`).

### 1.3 Os três datasets reais

**Dataset A — Coalizão "Fato ou Boato" (TSE).** Fonte: [justicaeleitoral.jus.br/fato-ou-boato](https://www.justicaeleitoral.jus.br/fato-ou-boato), agregador oficial que reúne checagens de 10 agências parceiras. 322 itens (`data/processed/dataset_a_fato_ou_boato_completo.csv`), com data de publicação de 2018-10-11 a 2026-07-31 — **correção:** esta seção descrevia a cobertura como "2018-2022"; a contagem real por ano é 24 (2018), 41 (2020), 29 (2021), 179 (2022), 24 (2023), 22 (2024) e 3 (2026) — fortemente concentrada em 2022, mas não limitada a 2018-2022 como o texto anterior dizia. Coletado por navegação real (Claude in Chrome), já que o ambiente de execução não tem acesso de saída à internet. **Não tem nenhum item real de IA** (`rotulo_ia` é uma heurística de regex sobre título, 0% "IA" — verificado ao vivo no site, inclusive testando se existe alguma tag de IA entre as 68 disponíveis: não existe).

**Dataset B — Arquivo de checagens do Aos Fatos.** Fonte: [aosfatos.org/noticias/?formato=checagem](https://www.aosfatos.org/noticias/?formato=checagem). 553 itens coletados no total, de 3 buscas por tag (contagem da coleta bruta, preservada em `data/raw/dataset_b_completo.csv`):

| Tag pesquisada | Itens coletados | Rótulo `rotulo_grupo` |
|---|---|---|
| `inteligencia-artificial` | 122 | 100% "IA" |
| `eleicoes-2022` | 419 | 100% "Tradicional" |
| `eleicoes-2026` | 12 | 100% "Tradicional" |

**A partir da Seção 19, `data/processed/dataset_b_aosfatos_enriquecido.csv` (o arquivo efetivamente usado em treino/análise) está restrito a checagens publicadas entre 01/01/2022 e 20/08/2026 — 541 itens (122 IA + 407 de `eleicoes-2022` + 12 de `eleicoes-2026`). Os 553 originais continuam intactos em `data/raw/`.**

Diferente do Dataset A, o Aos Fatos rotula editorialmente cada checagem com **veredito**, **tema** e a tag de busca que a originou — ou seja, `rotulo_grupo` (IA vs. Tradicional) é uma classificação humana real, não uma heurística. Colunas-chave: `titulo`, `corpo_artigo` (texto completo do artigo, já limpo de nav/menu/rodapé — ver `scripts/build_dataset_b_completo.py`), `veredito`, `tema`, `tag_pesquisa`, `data_publicacao`/`data_publicacao_iso`, `dias_para_eleicao`, `ciclo_eleitoral_estimado`, `vetor_midia`/`vetor_midia_texto`, `alvo_ataque`/`alvo_ataque_texto`.

**⚠️ Fato crítico para qualquer modelagem futura:** `rotulo_grupo` é **perfeitamente colinear** com `tag_pesquisa` (tabela acima). Todo item "IA" veio exclusivamente da busca por IA; nenhum item das buscas eleitorais foi rotulado IA. Isso é consistente com o rótulo refletir o tema real dos textos, mas significa que qualquer diferença encontrada entre os grupos IA/Tradicional pode refletir diferença de **época/lote de coleta**, não só de tema — os itens IA são majoritariamente mais recentes. Ver Seção 10.1 para como isso se manifestou concretamente no classificador.

**Dataset A — nota equivalente:** `data/processed/dataset_a_fato_ou_boato_completo.csv` (322 itens, merge bruto de `data/raw/dataset_a_fato_ou_boato.csv` + `data/raw/dataset_a_extra_tags.csv`, sem nenhum enriquecimento) permanece intacto com o histórico completo. Já `data/processed/dataset_a_fato_ou_boato_enriquecido.csv` (o arquivo usado em análise a partir da Seção 19) está restrito a 01/01/2022–20/08/2026 — 228 itens.

**Dataset C — Unificação de A + B.** Esquema harmonizado que preserva a proveniência de cada rótulo (`fonte_rotulo_ia`, `fonte_veredito`, `fonte_categoria_tema` — heurística vs. editorial). Detecção de prováveis duplicatas entre as duas fontes por similaridade de cosseno sobre TF-IDF (pares flagados, não removidos). **Importante:** unificar A+B não aumenta o poder estatístico de nenhum teste IA-vs-Tradicional — só o Dataset B contribui itens IA; a unificação só amplia a baseline "Tradicional" e a cobertura temática geral. `data/processed/dataset_c_unificado.csv` é sempre a união dos dois arquivos *enriquecidos* (não dos brutos) — por isso, a partir da Seção 19, ele tem 769 itens (228 de A + 541 de B), não mais os 875 (322 + 553) de antes do recorte.

### 1.4 Vieses já encontrados e corrigidos na Fase 2 (antes desta sessão)

Estes já estavam resolvidos antes do trabalho de Fase 3 começar, mas são essenciais para entender o padrão de rigor do projeto:

- **Contaminação lexical em `alvo_ataque_texto`:** a nuvem de tags do rodapé do site (presente em toda página do Aos Fatos) inflava artificialmente as contagens de palavras-chave. Corrigido isolando `corpo_artigo` (removendo nav/menu/rodapé) e podando o dicionário de palavras genéricas — isso **inverteu** o achado de H4 (grupo IA passou a ser mais, não menos, associado a `urna_processo`).
- **Viés de desenho amostral em `dias_para_eleicao`:** a tag `eleicoes-2022` é um recorte por ano eleitoral (viés natural para "perto da eleição"); a tag `inteligencia-artificial` não tem filtro de proximidade eleitoral. O efeito ingênuo de H5 (p<0.0001) quase desaparece numa comparação por janela temporal equivalente (p≈0.44-0.78). Documentado no notebook 02, Seção 4.5, e replicado no notebook 03 com a baseline ampliada.

### 1.5 Notebooks (Fase 2, já executados com outputs embutidos)

- `notebooks/01_dataset_a_fato_ou_boato_eda.ipynb` — EDA do Dataset A.
- `notebooks/02_dataset_b_aosfatos_eda.ipynb` — EDA do Dataset B, com as duas correções de viés acima documentadas no próprio notebook.
- `notebooks/03_dataset_c_unificado_eda.ipynb` — unificação A+B, detecção de duplicatas, EDA combinada.

Cada notebook é gerado por um script Python (`scripts/gen_notebook_{a,b,c}.py`, construção de células via nbformat) e depois executado por `scripts/execute_notebooks.py` (via nbclient), que embute outputs/gráficos reais no `.ipynb`. Esse é o padrão a seguir para qualquer notebook novo.

### 1.6 Estrutura completa do repositório (estado atual, após a Fase 3 iniciada)

```
politicAI/
├── README.md                  # visão geral do projeto (Fases 1-3)
├── requirements.txt           # deps da Fase 2 (pandas, sklearn, nbformat, etc.)
├── .gitignore
├── docs/
│   └── PRD.md                  # ESTE DOCUMENTO
├── data/
│   ├── raw/                    # saída direta dos parsers/scrapers, sem enriquecimento
│   └── processed/              # datasets prontos para análise (gerados pelos notebooks)
│       ├── dataset_a_fato_ou_boato_completo.csv
│       ├── dataset_a_fato_ou_boato_enriquecido.csv
│       ├── dataset_b_aosfatos_enriquecido.csv
│       └── dataset_c_unificado.csv
├── notebooks/                  # 01, 02, 03 (Fase 2, ver 1.5)
├── scripts/                    # coleta, parsing, geração/execução de notebooks (Fase 2)
│   ├── export_dashboard_data.py   # snapshot JSON opcional do Dataset C (não usado por padrão pelo /web — ver 9.2)
│   └── gen_notebook_models_01.py  # gera models/notebooks/01_ia_topic_classifier_baseline.ipynb
├── web/                        # Fase 3 — plataforma Next.js (ver Seção 6 e 9.2)
└── models/                     # Fase 3 — motor de ML (ver Seção 5 e 9.1)
```

---

## 2. Sumário executivo da Fase 3

A Fase 2 produziu três datasets reais e notebooks de EDA que já identificaram e corrigiram, com rigor, mais de uma armadilha metodológica. A Fase 3 evolui esse trabalho para duas frentes de produto:

1. **Motor de Machine Learning** (`/models`): um classificador que estima se um conteúdo político foi gerado ou manipulado por IA, e um motor exploratório de previsão de quanto a desinformação por IA deve pesar nas eleições de 2026.
2. **Plataforma web** (`/web`): um painel que consolida a percepção do momento eleitoral a partir de múltiplas fontes — inspirado na plataforma de referência da orientadora, **Lentes da Eleição 2026** — com um diferencial: **sinalização explícita de conteúdo suspeito de ser gerado por IA**, mais uma ferramenta interativa (**"Sensor de IA"**).

**O que este PRD não é:** uma promessa de que o motor de ML "detecta deepfakes com precisão de laboratório" ou "prevê o resultado da eleição". Cada seção declara o que os dados atuais permitem construir agora (um classificador *proxy* de temática, um índice exploratório de tendência) e o que exige coleta de dados nova (um detector geral de autoria por IA, uma previsão validada de impacto eleitoral).

---

## 3. Contexto: o que a plataforma de referência já faz, e o que falta

A **Lentes da Eleição 2026** ([lentes-da-eleicao-brasil.maria514774.chatgpt.site](https://lentes-da-eleicao-brasil.maria514774.chatgpt.site)), desenvolvida pela orientadora, organiza a percepção eleitoral em quatro "lentes" independentes:

| Lente | O que mede | Fonte |
|---|---|---|
| Google Trends | Volume de busca (atenção, não intenção de voto) | Google Trends, evolução semanal, mapa por estado |
| Jornais | Presença de candidatos/temas numa amostra jornalística | Manchetes de veículos nacionais |
| Redes Sociais | Conversação e engajamento | X, Bluesky, TikTok, Instagram |
| Pesquisas | Intenção de voto e rejeição estimadas por amostragem | Institutos de pesquisa eleitoral |

Princípio explícito da plataforma de referência: essas quatro lentes **não devem ser confundidas entre si**. Este PRD adota o mesmo princípio e o estende com uma quinta dimensão que a referência **não cobre**: quanto do volume de conversação/notícia é, ou aparenta ser, gerado ou manipulado por IA.

**Gap identificado (motivação do produto):** nenhuma das quatro lentes de referência sinaliza IA. Este projeto tem, da Fase 2, 122 checagens editoriais reais de conteúdo gerado por IA (Dataset B/C).

---

## 4. Personas e casos de uso

| Persona | Necessidade | Como o produto atende |
|---|---|---|
| Pesquisador(a)/orientador(a) | Comparar hipóteses H1–H5 num painel visual | Dashboard com os indicadores dos notebooks 01–03, navegável |
| Jornalista/checador(a) de fatos | Triagem rápida de conteúdo suspeito | Sensor de IA, com probabilidade + confiança |
| Eleitor(a) engajado(a) | Entender o clima eleitoral e desconfiar de forma informada | Dashboard público + selo "conteúdo relacionado a IA" |
| Este projeto (TCC) | Vitrine viva do trabalho + código de ML citável | `/models` reprodutível, com métricas versionadas |

**Fora de escopo:** moderação automática, remoção/bloqueio de posts, tratar saída do modelo como veredito definitivo (sempre probabilidade + confiança, nunca "true/false" categórico).

---

## 5. Feature 1 — Motor de Machine Learning (`/models`)

### 5.1 Classificador de conteúdo político gerado por IA ("Sensor de IA")

**Distinção técnica crítica:** existem dois problemas diferentes, e os dados atuais só resolvem um.

| | Problema A — o que os dados permitem AGORA | Problema B — o que se quer de fato |
|---|---|---|
| Pergunta | Este boato **é sobre** conteúdo manipulado por IA? | Este texto/vídeo/áudio **foi gerado** por IA? |
| Rótulo disponível | `rotulo_grupo` — classificação editorial sobre o **tema da checagem** | Não existe no repositório |
| Quem escreveu o texto rotulado | Sempre um jornalista humano | Ambígua por definição |

**Decisão de produto:** construir em fases, nomeando cada uma com precisão:

- **v0 (implementado, ver Seção 9.1):** *Classificador de Temática de IA* — usa Dataset B para prever se um texto é sobre desinformação envolvendo IA.
- **v1 (requer nova coleta, Seção 5.3):** *Detector de Autoria por IA* — texto-humano vs. texto-gerado-por-IA.
- **v1.1:** extensão multimodal (vídeo/áudio).

#### Requisitos funcionais v0

- RF1.1 — Dado um texto, retornar `{ rotulo, probabilidade, confianca }`. **[Implementado]**
- RF1.2 — Pipeline de treino reprodutível a partir do Dataset B. **[Implementado]**
- RF1.3 — Split estratificado, métricas por classe (não só acurácia). **[Implementado]**
- RF1.4 — Modelo versionado, carregável por API. **[Implementado — mas ver backlog 11.1, versionamento ainda ingênuo]**
- RF1.5 — Explicabilidade mínima (termos influentes). **[Implementado]**

#### Requisitos funcionais v1 (condicionados à Seção 5.3, **não implementado**)

- RF1.6 — Probabilidade de autoria por IA, com confiança.
- RF1.7 — Auditado contra ≥2 famílias de LLM.
- RF1.8 — Limitações expostas na própria UI.

### 5.2 Motor de previsão de impacto da IA nas eleições

**Avaliação honesta de viabilidade:** uma previsão validada de "impacto" não é sustentável com os dados atuais (sem medida direta de impacto no resultado, sem série longa o suficiente). A funcionalidade defensável é um **índice de tendência/atenção**, nomeado **"Índice de Intensidade de Desinformação por IA"**, não "previsão de impacto eleitoral".

#### Requisitos funcionais

- RF2.1 — Série temporal do volume de checagens IA. **[Implementado, mas com uma correção de desenho — ver Seção 10.2]**
- RF2.2 — Projeção de curto prazo, auditável. **[Implementado — GLM Binomial Negativa/Poisson com fallback para regressão linear, ver Seção 9.1]**
- RF2.3 — Intervalo de confiança/incerteza. **[Implementado]**
- RF2.4 — Contextualização com calendário eleitoral. **[Implementado — ver Seção 16, item 1. `trend_index.py` agora importa `scripts/election_calendar.py` (mesma fonte de datas de turno usada pelos notebooks) e anota cada `PontoIndice` com `mes_de_1_turno`/`dias_para_1_turno_mais_proximo`; `IndiceTendencia.marcos_eleitorais` lista os turnos dentro do período coberto. `GET /forecast/index` expõe os campos novos, e `/web` agora consome esse endpoint (`TrendIndexChart`, nova seção "Índice de tendência" em `app/page.tsx`) para desenhar marcadores verticais de 1º turno.]**
- RF2.5 — Texto de limitação explícito na tela. **[Implementado via campo `aviso` da API]**

### 5.3 Dados adicionais necessários (bloqueadores para v1)

| Necessidade | Por quê | Como obter |
|---|---|---|
| Corpus pareado texto-humano vs. texto-gerado-por-IA, domínio político-BR | Treinar o Detector de Autoria (v1) | Gerar com LLMs (prompts neutros/factuais) + coletar textos humanos comparáveis — nunca gerar desinformação real como dado de treino |
| Amostras de vídeo/áudio rotuladas (deepfake vs. real) | Extensão multimodal (v1.1) | Bancos públicos (FaceForensics++, DFDC) adaptados ao domínio político-BR |
| Série histórica mais longa de checagens IA | Validar o índice de tendência com mais de um ciclo eleitoral | Continuar a coleta do Dataset B mensalmente até out/2026 |

### 5.4 Riscos, limitações e considerações éticas

- Viés de rótulo herdado de uma única agência (Aos Fatos).
- Reforçar sempre: v0 classifica **temática**, não **autoria**.
- Ausência de detecção de IA **não** significa conteúdo verdadeiro.
- Texto gerado por IA e editado por humano reduz a taxa de detecção de qualquer classificador desse tipo.
- Dataset pequeno (122 IA) — evitar deep learning, preferir modelos clássicos regularizados.

---

## 6. Feature 2 — Plataforma web (`/web`)

### 6.1 Dashboard de percepção eleitoral

| Lente | Fonte real | Status |
|---|---|---|
| Buscadores | Google Trends API | **Em construção — não integrado** |
| Imprensa | Dataset A + B | **Real, implementado** |
| Redes sociais | APIs públicas | **Em construção — não integrado** |
| Institutos de pesquisa | Dados públicos | **Em construção — não integrado** |
| IA (diferencial) | Dataset B/C | **Real, implementado** |

#### Requisitos funcionais

- RF3.1 — Resumo executivo (nº de checagens, % IA, veredito predominante). **[Implementado — correção na Seção 16, item 2: "veredito predominante" nunca tinha sido exibido, apesar de `distribuicao_veredito` já vir pronto no JSON do resumo desde a Fase 3; agora há um card dedicado no resumo executivo.]**
- RF3.2 — Feed de checagens com selo "Relacionado a IA". **[Implementado]**
- RF3.3 — Gráfico de série temporal com calendário eleitoral. **[Implementado — correção na Seção 16, item 3: `datas_turno_1` já existia em `DatasetCSummary`, mas nunca era passado para `MonthlyVolumeChart` nem desenhado; agora o gráfico marca com uma linha vertical o mês de cada 1º turno que cai dentro do intervalo exibido.]**
- RF3.4 — Painel de metodologia (`/metodologia`). **[Implementado]**
- RF3.5 — Lentes não integradas marcadas como "em construção", nunca com dado mockado. **[Implementado]**

### 6.2 Sensor de IA (ferramenta interativa)

#### Requisitos funcionais

- RF4.1 — Texto livre → `POST /predict/ia-topic` → rótulo + probabilidade + termos influentes. **[Implementado]**
- RF4.2 — Upload de vídeo/áudio: fora do MVP. **[Não implementado — correto, é v1.1]**
- RF4.3 — Aviso permanente de limitação (temática ≠ autoria). **[Implementado]**
- RF4.4 — Rate limiting e log opt-in de submissões (para futuro corpus v1). **[Implementado — correção de status na Seção 16, item 4: este item já estava de fato implementado (`slowapi` em todos os endpoints + `consentimento_log.jsonl` opt-in via `permitir_uso_para_pesquisa`, ver Seção 9.1 e backlog 11.1, itens 10-11), mas continuava marcado como pendente aqui por não ter sido atualizado quando o backlog foi fechado.]**

### 6.3 Stack técnica

Next.js (App Router) + TypeScript + Tailwind CSS v4 + Recharts. Comunicação com `/models` via HTTP (cliente em `lib/models-client.ts`), nunca lógica de ML embutida no `/web`.

---

## 7. Arquitetura geral do repositório

`web/` e `models/` são projetos independentes (gerenciadores de dependência próprios), comunicando-se só por HTTP. Ambos leem `../data/processed/` como fonte única de verdade. Ver Seção 1.6 para a árvore completa e Seção 9 para o detalhamento de cada um.

---

## 8. Métricas de sucesso

| Métrica | Alvo (v0/MVP) | Status |
|---|---|---|
| F1-score do classificador v0, classe IA | ≥ 0.70 | **Atingido: 0.98** (ver ressalva na Seção 9.1/10.1 sobre por que isso é "alto demais para ser tranquilizador") |
| Cobertura do dashboard | 2 de 5 lentes reais no MVP | **Atingido** (Imprensa + IA) |
| Tempo de resposta do Sensor de IA | < 3s | Não medido formalmente ainda |
| Transparência | 100% das telas com fonte e data de corte | **Atingido** |
| Reprodutibilidade do pipeline de ML | Treinar do zero reproduz as métricas | **Atingido** (testes automatizados passam) |

---

## 9. Estado atual de implementação (o que já existe, concretamente)

### 9.1 `/models` — implementado e testado (atualizado na Fase 3)

Estrutura real (não apenas planejada):

```
models/
├── README.md                      # arquitetura, resultados, limitações
├── pyproject.toml
├── .gitignore
├── configs/ia_topic_classifier_v0.yaml
├── notebooks/01_ia_topic_classifier_baseline.ipynb   # EDA + baseline, executado, 0 erros
├── src/models_pkg/
│   ├── data/loader.py                    # carregamento + split estratificado + build_text_field
│   ├── data/boilerplate.py               # limpeza de 6 padrões de template do site (ver Seção 10.3)
│   ├── features/text_features.py         # TF-IDF (unigrama+bigrama), stopwords PT ampliadas
│   ├── evaluation/cross_validation.py    # validação cruzada estratificada
│   ├── evaluation/metrics.py             # precisão/recall/F1 por classe, matriz de confusão
│   ├── training/tune_hyperparameters.py  # GridSearchCV sobre o conjunto de validação (PredefinedSplit)
│   ├── training/compare_models.py        # comparação com Naive Bayes/SVM/gradient boosting
│   ├── training/train_ia_topic_classifier.py  # tuning+CV+fit+calibração+avaliação+versionamento
│   ├── inference/predictor.py            # carrega artefato, serve predição calibrada + termos influentes
│   └── forecasting/trend_index.py        # índice de tendência (Binomial Negativa/Poisson, ver Seção 10.2) + calendário eleitoral (RF2.4, ver Seção 16)
├── api/main.py       # FastAPI: /health, /predict/ia-topic(+/batch), /predict/ia-authorship (501), /forecast/index (com contexto de calendário eleitoral) — rate limiting + log opt-in
├── tests/                          # 44 testes pytest, todos passando
└── artifacts/
    ├── model_comparison.md         # resultado real da comparação entre 4 algoritmos
    └── versions/                   # snapshot imutável de cada treino + manifest.json (histórico)
```

**Classificador v0 — resultados reais (não simulados), retreinado na Seção 19 sobre o Dataset B recortado a 01/01/2022–20/08/2026:** treinado em 541 itens, split estratificado 72%/8%/20% (432 treino, 109 teste), regressão logística sobre TF-IDF, com calibração de probabilidade (`CalibratedClassifierCV`, sigmoid).

| Classe | Precisão | Recall | F1 | N (teste) |
|---|---|---|---|---|
| IA | 0.96 | 1.00 | 0.98 | 25 |
| Tradicional | 1.00 | 0.99 | 0.99 | 84 |

Acurácia geral 0.99, ROC-AUC 1.00 (hold-out único). Validação cruzada estratificada de 5 folds sobre treino+validação — mais defensável, com só 122 itens IA no total: F1 da classe IA 0.979 ± 0.021, acurácia 0.991 ± 0.009. Comparação com Naive Bayes, SVM linear calibrado e gradient boosting (mesmo TF-IDF, `artifacts/model_comparison.md`) confirma que a escolha da regressão logística não perde desempenho de forma estatisticamente relevante frente aos outros três, e mantém a vantagem de interpretabilidade nativa. **Ver Seção 10.1 e 10.3 (pré-recorte, mas o raciocínio continua valendo) e Seção 19 — por que os números de hold-out ainda são "bons demais" para tranquilizar sozinhos.**

**Índice de tendência v0:** agora ajusta um GLM apropriado para dados de contagem (Binomial Negativa, com fallback para Poisson e depois para a regressão linear original se a Binomial Negativa não convergir) sobre o volume mensal absoluto de checagens IA reais (não uma proporção — ver Seção 10.2 para por que) — o método efetivamente usado é reportado no campo `metodo` da resposta, nunca escondido. Serve via `GET /forecast/index?periods=N`, lendo `data/processed/dataset_c_unificado.csv` ao vivo a cada request (sem cache). Desde a Seção 16 (item 1), cada ponto também carrega `mes_de_1_turno`/`dias_para_1_turno_mais_proximo`, e a resposta expõe `marcos_eleitorais` — RF2.4, contextualização com calendário eleitoral.

**API FastAPI (`models/api/main.py`):** `/predict/ia-authorship` retorna `501` de propósito (não simula uma capacidade que não existe). Rate limiting básico (`slowapi`) em todos os endpoints; `/predict/ia-topic` aceita um campo opcional `permitir_uso_para_pesquisa` que, com consentimento explícito, grava o texto e a predição num log opt-in append-only (`data/consentimento_log.jsonl`, nunca usado automaticamente para retreinar); `/predict/ia-topic/batch` aceita até 50 textos por chamada.

### 9.2 `/web` — implementado, com dados reais lidos ao vivo (atualizado na Fase 3)

Estrutura real:

```
web/
├── README.md
├── package.json / package-lock.json     # Next.js 16, TypeScript, Tailwind v4, Recharts, csv-parse, zod, Vitest
├── .env.example                          # MODELS_API_URL
├── vitest.config.mts / vitest.setup.ts
└── src/
    ├── app/
    │   ├── layout.tsx                     # script inline anti-flash de tema, skip link
    │   ├── page.tsx                       # painel — force-dynamic, lê CSV ao vivo (ou snapshot, ver abaixo) + índice de tendência do /models
    │   ├── sensor/page.tsx                 # Sensor de IA, com contador de caracteres
    │   ├── metodologia/page.tsx            # force-dynamic
    │   └── api/sensor-ia/route.ts          # proxy para /models
    ├── components/                          # nav (aria-current), theme-toggle, feed paginado/filtrável,
    │                                         # gráficos com aria-label (inclui marcadores de calendário
    │                                         # eleitoral, ver Seção 16), disclaimer (role="note"), __tests__/
    └── lib/
        ├── dataset-c.ts                     # lê o CSV do disco a cada request; fallback para snapshot JSON (ver abaixo)
        ├── env.ts                           # validação de MODELS_API_URL com zod
        ├── lentes.ts                        # definição das lentes (real vs. em construção)
        ├── models-client.ts                 # cliente HTTP para /models (predição + índice de tendência)
        ├── veredito-labels.ts               # rótulos de veredito + "veredito predominante" (RF3.1, Seção 16)
        ├── types.ts
        └── __tests__/                        # testes unitários (Vitest)
```

**De onde vêm os dados do painel, e o fallback de deploy standalone (Fase 3):** o caminho principal continua sendo ler `data/processed/dataset_c_unificado.csv` direto do disco a cada request (`fs.readFileSync` + `csv-parse`, em `web/src/lib/dataset-c.ts`, com `export const dynamic = "force-dynamic"` nas páginas que dependem disso) — nenhum passo manual de exportação no caminho normal. Diferente de uma versão anterior desta fase, agora existe um fallback real: se o CSV não for encontrado em nenhum dos caminhos esperados, `getDatasetCSummary()` tenta ler um snapshot JSON estático (`web/src/data/dataset_c_summary.json`, gerado por `scripts/export_dashboard_data.py`) antes de desistir — pensado para um deploy de `/web` sozinho, sem o resto do monorepo acessível. O snapshot é claramente rotulado como fotografia estática (campos `gerado_em`/`gerado_por`/`aviso`), nunca apresentado como dado ao vivo. Só se nem o CSV nem o snapshot existirem é que a página mostra o aviso explícito de erro — nunca um número inventado. Ver `web/README.md`, "De onde vêm os dados do painel".

Build de produção (`npm run build`), lint (`npx eslint .`) e testes (`npm run test`, 27 testes — 16 originais da Fase 3 + 11 da Seção 16, RF2.4/RF3.1/RF3.3) passam limpos. Testado manualmente: dado real aparece corretamente (769 total, 122 IA, 647 Tradicional, desde o recorte de 01/01/2022–20/08/2026 da Seção 19 — antes do recorte era 875 total, 122 IA, 753 Tradicional), o cenário de CSV ausente com snapshot presente serve o snapshot, e o cenário sem CSV nem snapshot mostra o aviso de erro. Também testado manualmente com `/models` no ar e fora do ar (ver Seção 16, item 5) — o painel nunca quebra por completo quando o serviço de índice de tendência está indisponível.

---

## 10. Descobertas metodológicas da Fase 3 (importante — leia antes de re-treinar ou re-derivar qualquer coisa)

Estas descobertas seguem o mesmo padrão de honestidade da Fase 2 (Seção 1.4): identificadas ao implementar, documentadas em detalhe no código-fonte (docstrings) e nos READMEs correspondentes, corrigidas quando possível.

### 10.1 Confound de tag de busca no classificador de temática

Já descrito na Seção 1.3: `rotulo_grupo` é perfeitamente colinear com `tag_pesquisa`. Isso significa que o classificador v0, ao atingir F1=0.98 na classe IA, pode estar parcialmente aprendendo "este texto veio do lote/época coletado via busca por IA" em vez de (ou além de) "este texto fala genuinamente sobre IA". As duas coisas coincidem na amostra atual porque quem buscou "inteligência artificial" no Aos Fatos genuinamente encontrou artigos sobre IA — mas isso não foi desenhado como um experimento controlado, e o desempenho não deve ser lido como uma medida de quão bem o modelo generalizaria para um texto arbitrário fora dessas três buscas. Documentado em `models/src/models_pkg/data/loader.py` (docstring do módulo) e `models/README.md`, Limitação 1.

**Implicação prática:** uma validação mais forte exigiria uma nova coleta com rótulos IA distribuídos por múltiplas buscas/períodos, não concentrados numa única tag de coleta.

### 10.2 Confound de denominador no índice de tendência (descoberto ao implementar, PRD original previa algo diferente)

O PRD original (RF2.1) especificava normalizar o volume de itens IA pelo volume TOTAL de checagens do mesmo mês, para não confundir "mais desinformação por IA" com "mais checagens em geral". Ao implementar essa normalização, descobrimos que ela produz um artefato enganoso: como o Dataset B foi coletado por 3 buscas por tag feitas separadamente (não é uma amostra contínua e uniforme no tempo), em vários meses de 2024-2025 praticamente 100% do "total do mês" já vinha da busca "inteligencia-artificial" — não havia itens de outras buscas datados naquele mês. Isso fazia a proporção IA/total saltar para perto de 1.0 (chegando a projeções de 91-96% em poucos meses de extrapolação) sem refletir nenhuma mudança real no mundo — um artefato puro de desenho de coleta, do mesmo tipo já documentado na Seção 1.4/10.1, agora manifestado numa nova métrica.

**Correção aplicada:** o índice implementado (`models/src/models_pkg/forecasting/trend_index.py`) usa **volume absoluto mensal** de itens IA reais, não uma proporção. Isso produz uma série muito mais sensata (ex.: projeção de ~6 itens/mês para set-dez/2026, com faixa de incerteza 1.4-10.6, em vez de "quase 100% de tudo será sobre IA"). Mesmo assim, o volume absoluto ainda reflete, em parte, o que o Aos Fatos escolheu investigar e indexar sob aquela tag — não necessariamente todo o universo de desinformação por IA.

**Se você for reintroduzir a normalização por volume total no futuro:** primeiro resolva a comparabilidade temporal das buscas por tag (ex.: nova coleta com datas de corte uniformes por tag, ou usando só o período em que as 3 buscas têm cobertura mensal comparável).

### 10.3 Boilerplate editorial contaminando os termos mais influentes do classificador (encontrado e corrigido)

Ao inspecionar os "termos mais associados a IA" do primeiro treino do classificador v0, dois deles eram lixo de template do site do Aos Fatos, não vocabulário sobre o tema:

- **"receba checagens" / "checagens reportagens"** — vinham de um CTA fixo de assinatura, em pelo menos duas variantes de texto encontradas:
  - "Siga o canal do Aos Fatos no WhatsApp e receba nossas checagens e reportagens"
  - "Inscreva-se no nosso canal e receba as nossas checagens e reportagens"

  Esse CTA aparece colado, sem separador no HTML, diretamente à legenda do post/vídeo sendo checado — por isso vazava para os bigramas do TF-IDF.

- **"caminho"** (de "O caminho da apuração [Aos Fatos]...") — abertura padronizada de um quadro de metodologia ("como verificamos"), presente em boa parte dos artigos mais recentes.

**O achado mais importante não é a presença desses trechos, é a distribuição deles:** apareciam em **~87% dos itens rotulados IA** (106-107 de 122) contra **~5-7% dos itens Tradicionais** (23-32 de 431) — quase certamente porque o Aos Fatos só adicionou esse template ao site depois de um certo período, e os itens IA são majoritariamente mais recentes (é o mesmo confound da Seção 10.1, agora visível no nível lexical: o classificador estava parcialmente aprendendo "este artigo usa o template novo do site" como proxy de "este artigo é sobre IA").

**Correção aplicada:** `models/src/models_pkg/data/boilerplate.py` remove esses trechos (via regex, com 6 testes unitários) antes da vetorização, aplicado dentro de `build_text_field()`. Cobre ~145/553 itens (26%) — **best-effort, não exaustivo**: uma nova coleta pode introduzir outras variantes de template não cobertas. Retreinar e checar se termos de CTA voltam a aparecer no model card é o sinal de que este módulo precisa de mais um padrão.

Depois da correção, as métricas agregadas não mudaram (o sinal temático genuíno já dominava), mas os termos mais influentes agora são todos sobre conteúdo real: `ia`, `artificial`, `inteligência artificial`, `gerado`, `busca reversa` (esta última é, na verdade, uma técnica real de verificação de vídeo/imagem manipulada — sinal legítimo, não ruído).

### 10.4 Resolvido: o mesmo boilerplate contaminava a EDA da Fase 2 — sim, e o efeito era ainda mais direto do que uma simples inflação de contagem

**Esta era a pergunta mais urgente em aberto do projeto, e foi investigada e corrigida na Fase 3.** A resposta é **sim**: o `corpo_artigo` usado pelo classificador v0 (Seção 10.3) é a MESMA coluna que o notebook 02 (Fase 2) usa para computar `alvo_ataque_texto` via keyword-matching — a heurística por trás do teste qui-quadrado de H4 reportado nos notebooks 02 e 03. A investigação (`scripts/investigar_boilerplate_notebook02.py`) confirmou algo mais específico do que "inflação genérica de contagem": a frase-modelo "O caminho da apuração..." contém literalmente a palavra **"apuração"**, que é uma das palavras-chave do dicionário usado para classificar `urna_processo` dentro de `alvo_ataque_texto` — ou seja, a heurística estava contando a presença de um quadro de metodologia padronizado do site como se fosse um ataque real ao "processo/urna", inflando artificialmente essa categoria especificamente entre os itens IA (87% dos quais têm o template, contra 5-7% dos Tradicionais — mesma distribuição desigual da Seção 10.3).

**Correção aplicada** (`scripts/gen_notebook_b.py`, Seção 3.5b do notebook 02; replicada no notebook 03): `alvo_ataque_texto` agora é recalculado sobre `corpo_artigo` limpo pelas mesmas regexes de `models/src/models_pkg/data/boilerplate.py`, antes do keyword-matching. O resultado de H4 já tinha sido invertido uma vez antes (Seção 3.5, ao isolar `corpo_artigo` do nav/rodapé do site) e se inverteu de novo com esta segunda correção — desta vez de volta à direção original da hipótese, com efeito mais forte: entre itens com alvo determinado, o grupo IA ataca a pessoa do candidato em **97,0%** dos casos contra **44,6%** do grupo Tradicional (chi2=28,941, p<0,0001, V de Cramér=0,356) — consistente com H4. Os notebooks 01/02/03 foram regenerados e re-executados com esses números reais embutidos; ver `notebooks/02_dataset_b_aosfatos_eda.ipynb`, Seção 3.5b e 4.4b, e `README.md` (raiz) para o resumo das três correções de metodologia do notebook 02.

**Lição para quem for citar H2/H4 no artigo/TCC:** cite a versão corrigida (Seção 4.4b do notebook 02, ou o notebook 03 equivalente) — as versões anteriores da estatística de H4 (tanto a original quanto a da Seção 3.5, antes desta segunda correção) estavam ambas contaminadas por artefatos de template editorial, não pelo fenômeno real.

---

## 11. Backlog de melhorias técnicas (priorizado — **todos os itens abaixo foram implementados na Fase 3**)

Mantido como registro histórico da priorização original; cada item marca onde foi implementado e verificado (testes/build passando, dados reais).

### 11.1 `/models`

**Alta prioridade:**
1. **[Feito]** Investigar e, se necessário, corrigir a Seção 10.4 — investigado, confirmado (contaminação real, via colisão da palavra "apuração") e corrigido nos notebooks 02/03 (Seção 3.5b) — ver Seção 10.4, agora reescrita com o resultado.
2. **[Feito]** Validação cruzada estratificada — `models_pkg.evaluation.cross_validation.run_stratified_cv`, 5 folds, seed=42, rodada dentro do pipeline de treino e em `compare_models.py`. Ver Seção 9.1.
3. **[Feito]** Calibração de probabilidade — `CalibratedClassifierCV` (sigmoid, `cv=5`) sobre treino+validação, usada por `predictor.py` para a probabilidade exibida no Sensor de IA.
4. **[Feito]** Tuning de hiperparâmetros usando o conjunto de validação — `models_pkg.training.tune_hyperparameters`, `GridSearchCV` com `PredefinedSplit` sobre `C`, `ngram_range`, `min_df`; resultado documentado no model card.

**Média prioridade:**
5. **[Feito]** Comparação com outros modelos — `models_pkg.training.compare_models` (Naive Bayes, SVM linear calibrado, gradient boosting), resultado real em `artifacts/model_comparison.md` — ver tabela na Seção 9.1.
6. **[Feito]** Versionamento real de artefatos — `artifacts/versions/<versao>_<timestamp>/` + `manifest.json`, com os caminhos "sem versão" mantidos como cópia do treino mais recente por compatibilidade.
7. **[Feito]** Estender `boilerplate.py` — mais quatro padrões de template encontrados e removidos (parceria com a Meta, nota de checagem colaborativa de fim de semana, checagem cruzada com outra agência, rodapé de direitos autorais), além dos dois originais. Ver `models/README.md`, Limitação 5.
8. **[Feito]** Índice de tendência com método apropriado para dados de contagem — GLM Binomial Negativa (fallback Poisson, depois regressão linear), ver Seção 9.1 e a docstring de `trend_index.py`.
9. **[Feito]** Datas de turno eleitoral centralizadas — `scripts/election_calendar.py`, importado por `/models` e pelos três geradores de notebook.

**Baixa prioridade / antes de expor publicamente:**
10. **[Feito]** Log opt-in de submissões do Sensor de IA — campo `permitir_uso_para_pesquisa`, gravação append-only em `data/consentimento_log.jsonl` (gitignored), nunca usado automaticamente para retreinar.
11. **[Feito]** Rate limiting na API FastAPI — `slowapi`, limites por endpoint (ver Seção 9.1). Autenticação continua fora de escopo (API ainda pensada para uso interno/`localhost` pelo `/web`).
12. **[Feito]** Endpoint de predição em lote — `POST /predict/ia-topic/batch`, até 50 textos por chamada.
13. **[Feito]** Lista de stopwords em português ampliada em `features/text_features.py` (pronomes, advérbios, formas de ser/estar/ter/haver, numerais, marcadores discursivos) — permanece uma lista manual curada (não um pacote externo), decisão mantida por reprodutibilidade offline.

### 11.2 `/web`

**Alta prioridade:**
1. **[Feito]** Confirmado que `npm install` completa de forma limpa.
2. **[Feito]** CI básico — `.github/workflows/ci.yml` (raiz do repo): `npm run lint`, `npm run test`, `npm run build` para `/web` e `pytest` para `/models`, a cada push/PR em `main`.

**Média prioridade:**
3. **[Feito]** Testes automatizados — 16 testes (Vitest + Testing Library): agregação pura de `dataset-c.ts`, cliente HTTP de `models-client.ts` (com rede mockada) e o componente `ChecagensFeed`.
4. **[Feito]** Passagem de acessibilidade — skip link, `aria-current` na navegação, `role="img"`+resumo textual nos gráficos, `role="note"` no banner de aviso.
5. **[Feito]** Fallback de deploy standalone — `getDatasetCSummary()` cai para um snapshot JSON estático (`scripts/export_dashboard_data.py`) quando o CSV não está acessível no disco; documentado com passo a passo em `web/README.md`. Ver Seção 9.2.
6. **[Feito]** Paginação/filtro no feed de checagens — 12 itens por página, "carregar mais", filtro "só relacionadas a IA".

**Baixa prioridade:**
7. **[Feito]** Validação de variáveis de ambiente — `src/lib/env.ts`, schema `zod` para `MODELS_API_URL`, falha cedo com mensagem clara.
8. **[Feito]** Toggle manual de modo claro/escuro — `theme-toggle.tsx`, persistido em `localStorage`, com script inline anti-flash em `layout.tsx`.
9. **[Feito]** Contador de caracteres no textarea do Sensor de IA — `sensor-form.tsx`, mínimo/máximo comunicados na UI.

---

## 12. Roadmap faseado

| Fase | Escopo | Depende de |
|---|---|---|
| **MVP (Fase 3.0)** | `/models` v0 + `/web` com dashboard e Sensor de IA v0 | **Concluído** (Seção 9) |
| **Fase 3.0.1 (correções)** | Investigar Seção 10.4; itens de alta prioridade da Seção 11 | **Concluído** — ver Seção 10.4 e Seção 11 (todos os itens marcados **[Feito]**) |
| **V1 (Fase 3.1)** | Detector de autoria por IA (texto) + integração de buscadores | Coleta de corpus pareado humano/IA (Seção 5.3) |
| **V1.1** | Extensão multimodal (vídeo/áudio) | Dataset de deepfake rotulado (Seção 5.3) |
| **V2 (Fase 3.2)** | Redes sociais + institutos como séries próprias; índice de tendência validado com um ciclo eleitoral completo | Acesso a APIs de redes sociais; coleta contínua até a eleição de out/2026 |

---

## 13. Perguntas em aberto (para a orientadora e/ou para decisão do autor)

1. A plataforma final deve ser pública ou uma ferramenta de apoio à pesquisa/imprensa, com acesso restrito? Muda requisitos de moderação, rate limiting e disclaimers legais.
2. Há orçamento/acesso a APIs pagas de redes sociais (X/TikTok) para a V2, ou o escopo fica limitado a dados públicos raspáveis?
3. O TCC/artigo deve reportar o v0 (temática) como resultado principal, com o detector de autoria (v1) como trabalho futuro explícito?
4. Existe orçamento para gerar/licenciar um corpus de texto político gerado por IA para treinar o detector de autoria (v1)?
5. ~~(Nova, urgente) A investigação da Seção 10.4 deve ser priorizada antes de qualquer submissão que cite H2/H4 do notebook 02/03?~~ — **Resolvida:** investigação concluída, contaminação confirmada e corrigida (Seção 10.4). Cite a versão corrigida (Seção 4.4b do notebook 02 / equivalente no notebook 03), não as versões anteriores.
6. ~~(Nova) Vale a pena investir em validação cruzada e calibração antes de reportar as métricas do classificador v0 no artigo?~~ — **Resolvida:** implementado (Seção 11.1, itens 2-3). O artigo/TCC deve citar a faixa de validação cruzada (F1 IA 0.974 ± 0.018) como estimativa principal de desempenho, com o número de hold-out (0.98) como complemento — não o contrário.
7. **(Nova)** Com o backlog técnico da Seção 11 inteiro implementado, o próximo maior risco de integridade científica em aberto volta a ser o confound de desenho amostral em si (Seção 10.1: `rotulo_grupo` colinear com `tag_pesquisa`) — resolvê-lo exige uma nova coleta com rótulos IA de múltiplas buscas/períodos, não mais uma mudança de código. Vale priorizar essa coleta antes da submissão final, mesmo que atrase o cronograma?

---

## 14. Como rodar tudo do zero (para continuar em outra ferramenta/IA)

```bash
# --- Fase 2: dados e notebooks (raiz do repo) ---
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/parse_dataset_a.py
python3 scripts/build_dataset_a_extra.py
python3 scripts/merge_dataset_a.py
python3 scripts/parse_dataset_b.py
python3 scripts/build_dataset_b_completo.py
python3 scripts/gen_notebook_a.py && python3 scripts/gen_notebook_b.py && python3 scripts/gen_notebook_c.py
python3 scripts/execute_notebooks.py notebooks/01_dataset_a_fato_ou_boato_eda.ipynb
python3 scripts/execute_notebooks.py notebooks/02_dataset_b_aosfatos_eda.ipynb
python3 scripts/execute_notebooks.py notebooks/03_dataset_c_unificado_eda.ipynb

# --- Fase 3: /models ---
cd models
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
PYTHONPATH=src python -m models_pkg.training.train_ia_topic_classifier --config configs/ia_topic_classifier_v0.yaml
PYTHONPATH=src python -m pytest tests/ -v
PYTHONPATH=src uvicorn api.main:app --reload --port 8000   # serviço de inferência

# --- Fase 3: /web (em outro terminal) ---
cd web
npm install            # IMPORTANTE: confirmar que completa sem erro (ver Seção 9.2)
cp .env.example .env.local
npm run dev            # http://localhost:3000
```

Documentação detalhada de cada parte: `README.md` (raiz, Fase 2), `models/README.md`, `web/README.md`.

---

## 15. Revisão pós-implementação da Fase 3 (achados e correções)

Depois de todo o backlog da Seção 11 ser implementado, foi feita uma revisão de código independente e cética de `/models` e `/web` (leitura linha a linha, reprodução de cenários suspeitos com dados reais, não só inspeção visual) especificamente para caçar erros introduzidos pelas próprias mudanças da Fase 3. Registrado aqui pelo mesmo motivo de todas as outras seções deste documento: nenhuma limitação encontrada deve ficar só na memória de quem revisou — precisa estar em texto, para quem continuar depois.

**Achados corrigidos:**

1. **RF2.4 (Seção 5.2) estava marcado como implementado por engano.** A revisão constatou que `IndiceTendencia`/`PontoIndice` (`trend_index.py`) não carregam nenhum campo de data de turno/proximidade eleitoral, e que `/forecast/index` não é consumido por nenhuma página de `/web` hoje — ou seja, a contextualização com calendário eleitoral do índice de tendência nunca foi implementada. O que a Fase 3 implementou foi outra coisa, menor: centralizar as datas de turno já usadas nos notebooks/export (`scripts/election_calendar.py`, Seção 11.1 item 9), que eliminou duplicação mas não é RF2.4. Corrigido o status na Seção 5.2. RF2.4 fica como item de backlog genuíno em aberto (adicionar ao índice/à UI marcadores de proximidade de turno, se isso for priorizado no futuro).
2. **Boilerplate.py (achado 5, "checagem cruzada com outra agência") podia, em tese, apagar conteúdo real do boato.** O regex original usava um coringa genérico (`pel[ao][^.]{0,60}` até o próximo ponto) para capturar o nome da agência parceira citada. Verificado que isso é seguro nos 553 itens reais atuais (as 27 combinações de nome batem exatamente, sem sobra de conteúdo), mas um item futuro cuja frase de atribuição continuasse sem um ponto até 60 caracteres depois (ex.: "...também foi feita pela Reuters e mostrou que...") teria o trecho seguinte apagado silenciosamente junto com o boilerplate. Corrigido: o coringa genérico foi trocado por uma lista fechada dos nomes de agência realmente encontrados (mesma abordagem em `models/src/models_pkg/data/boilerplate.py` e na cópia sincronizada de `scripts/gen_notebook_b.py`) — não muda nenhuma estatística já publicada (confirmado recalculando H4 e retreinando o classificador: números idênticos), mas elimina o risco para coletas futuras. Como efeito colateral, também corrigiu um truncamento pré-existente ("Boatos.org" ficava cortado em "Boatos."). Duas novas regressões em `tests/test_boilerplate.py` cobrem especificamente esse cenário.
3. **`getChecagensRecentes()` derrubava a página inteira do painel no modo de deploy standalone.** `getDatasetCSummary()` tem fallback para o snapshot JSON estático quando o CSV não está acessível, mas `getChecagensRecentes()` (usada para o feed de checagens) sempre exige as linhas cruas do CSV e não tinha esse fallback — como as duas chamadas estavam no mesmo bloco `try`, a falha da segunda descartava o resultado já bem-sucedido da primeira, e a home mostrava o banner de erro completo mesmo com um snapshot válido disponível. Corrigido isolando as duas chamadas em blocos `try`/`catch` independentes em `src/app/page.tsx`: o resumo/gráficos aparecem normalmente a partir do snapshot, e só a seção do feed mostra um aviso explícito de que essa parte específica não está disponível nesse modo (nunca uma lista vazia fingindo ser "zero checagens").
4. **Snapshot estático sem validação de forma em runtime.** `lerSnapshotEstatico()` fazia só um `JSON.parse` com cast direto para `DatasetCSummary`, sem checar a forma. Um snapshot desatualizado ou malformado (gerado por uma versão diferente de `scripts/export_dashboard_data.py`) seria repassado direto para a UI. Corrigido com um schema `zod` (`DatasetCSummarySchema`, em `dataset-c.ts`) que valida a forma antes de aceitar o snapshot; se não bater, trata como "sem snapshot utilizável" e cai para o erro explícito de dataset não encontrado, nunca renderiza campos ausentes/`undefined`.
5. **`<html>` sem `suppressHydrationWarning`.** O script inline anti-flash de tema (`layout.tsx`) adiciona a classe `dark`/`light` ao elemento `<html>` antes da hidratação, com base em `localStorage`/preferência do sistema — algo que o React não pode prever no render do servidor. Sem `suppressHydrationWarning` nesse elemento específico, isso gerava um aviso de divergência de hidratação no console toda vez que o tema do cliente diferisse do padrão do servidor. Corrigido (o aviso afeta só o atributo `class` deste elemento, não seus filhos).
6. **Endpoint em lote (`/predict/ia-topic/batch`) sem limite de tamanho por item.** `TextoLoteRequest.textos` limitava a quantidade de itens da lista (`TAMANHO_MAX_LOTE=50`) mas não o tamanho de cada string — um único item de milhões de caracteres passava direto para o classificador, ao contrário do endpoint individual (que rejeita acima de 20.000 caracteres). Corrigido com um `field_validator` que aplica o mesmo limite por item; nova regressão em `tests/test_api.py`.
7. **`manifest.json` de versionamento não era escrito atomicamente, e podia referenciar um "latest" nunca promovido.** Corrigido: a promoção dos artefatos "latest" agora acontece ANTES da atualização do manifesto (uma interrupção no meio do caminho deixa o manifesto sem mencionar a versão nova, em vez de mencionar uma versão cujos arquivos "latest" nunca foram copiados), e a escrita do manifesto usa arquivo temporário + rename (evita um arquivo truncado/inválido se o processo for interrompido a meio da escrita). Corrida entre dois treinos simultâneos ainda pode perder uma entrada do histórico (cenário raro para um pipeline de pesquisa rodado localmente) — não resolvido, documentado como limitação conhecida.
8. **`compare_models.py` tinha `class_weight="balanced"` hardcoded** para o candidato de produção, em vez de ler `cfg["model"]["class_weight"]` como o resto do pipeline — inofensivo hoje (o valor no YAML já é `"balanced"`), mas divergiria silenciosamente se essa configuração fosse ajustada no futuro. Corrigido; comparação de modelos re-executada com dados reais (números praticamente idênticos aos anteriores — pequena variação em `naive_bayes_multinomial`/`gradient_boosting_hist` refletindo o texto ligeiramente diferente após a correção do achado 2 acima, não um efeito da mudança de `class_weight` em si). `models/README.md` atualizado com os números re-gerados.

**Verificado e descartado (sem problema real):** calibração de probabilidade sem vazamento de dados (o pipeline não-calibrado usado para os termos influentes é um objeto ajustado separadamente do ensemble de calibração); `PredefinedSplit`/`GridSearchCV` com `refit=False` corretos; validação cruzada estratificada sem vazamento entre folds; fallback Binomial Negativa→Poisson→linear no índice de tendência correto nos dois branches de nomes de coluna do `statsmodels`, inclusive sob separação perfeita (verificado com um caso degenerado); `useSyncExternalStore` do `ThemeToggle` implementado corretamente (só uma instância montada, sem problema de estado obsoleto); validação de `MODELS_API_URL` via zod rejeita string vazia e aceita ausência da variável; limites de caracteres do Sensor de IA no frontend batem exatamente com os do backend; paginação/filtro do feed de checagens reagem corretamente um ao outro.

Depois de todas as correções: 39/39 testes de `/models` passando (36→39, três novas regressões), lint/16 testes/build de `/web` passando limpos, H4 (notebook 02/03) recalculado com o mesmo resultado de antes (chi2=28.941, V=0.356), classificador v0 retreinado com métricas de teste idênticas (acurácia 0.991, F1 IA 0.980).

---

## 16. RF2.4 implementado, e outras lacunas de UI corrigidas (pedido explícito do autor)

A Seção 15 tinha corrigido o *status* de RF2.4 para "não implementado" e deixado como item de backlog em aberto. A pedido explícito do autor, RF2.4 foi implementado de fato nesta rodada — e, ao implementá-lo, uma varredura pelo mesmo padrão de erro (campo calculado no backend/agregação, mas nunca de fato desenhado na UI, apesar do PRD dizer "Implementado") encontrou mais dois casos reais no dashboard. Registrado aqui pelo mesmo motivo de toda seção anterior: nada fica só na memória de quem implementou.

**1. RF2.4 — contextualização com calendário eleitoral no índice de tendência (docs/PRD.md, Seção 5.2).** `models/src/models_pkg/forecasting/trend_index.py` agora importa `scripts/election_calendar.py` (mesma fonte única de `DATAS_TURNO_1` já usada pelos três geradores de notebook e por `export_dashboard_data.py` — import via `sys.path`, documentado na docstring do módulo como um acoplamento de caminho assumido, não escondido: `models/` já assumia um checkout de monorepo para ler `../data/processed/`, e esta é a mesma suposição estendida a `scripts/`). Cada `PontoIndice` (observado ou projetado) ganhou `mes_de_1_turno` (booleano) e `dias_para_1_turno_mais_proximo` (inteiro, medido a partir do 1º dia do mês, negativo = antes da eleição); `IndiceTendencia` ganhou `marcos_eleitorais` (lista dos 1º turnos cuja data cai dentro do período coberto pelos pontos retornados) e `calendario_disponivel` (booleano — `false` só se `scripts/election_calendar.py` não puder ser importado, nunca uma data inventada nesse caso). `GET /forecast/index` expõe os quatro campos novos. Do lado do `/web`, que até então nunca consumia `/forecast/index` (motivo original de RF2.4 nunca ter sido implementado — não havia onde desenhar as datas), uma nova seção "Índice de tendência de desinformação por IA" em `src/app/page.tsx` chama `obterIndiceTendencia()` (novo, em `models-client.ts`) e renderiza `TrendIndexChart` (novo componente): linha sólida para o volume observado, linha tracejada + faixa sombreada para a projeção e seu intervalo de confiança (95%), e uma linha de referência vertical vermelha em cada mês de 1º turno dentro do período. Chamada isolada em seu próprio fluxo de erro (independente do resumo/feed, que continuam lidos direto do CSV/snapshot): se `/models` estiver fora do ar, a seção do índice mostra um aviso explícito e o resto do painel continua normal — testado manualmente com o serviço no ar e depois derrubado (`pkill`), confirmando que o painel nunca quebra por completo. 6 testes novos em `models/tests/test_trend_index.py` (incluindo um teste de consistência que importa `scripts/election_calendar.py` via `sys.path` e falha explicitamente se algum dia divergir do valor usado por `trend_index.py`) + 1 em `test_api.py`, e 4 em `web/src/lib/__tests__/models-client.test.ts`, com dado real do `dataset_c_unificado.csv` verificado manualmente via `curl` (2024-10 e 2026-10 corretamente marcados como `mes_de_1_turno=true`).

**2. RF3.1 — "veredito predominante" nunca aparecia no resumo executivo (docs/PRD.md, Seção 6.1).** `distribuicao_veredito` já era calculado e enviado no JSON do resumo desde a Fase 3 (usado hoje só para o veredito de cada item individual do feed), mas nenhuma tela agregava isso num "veredito predominante" — o resumo executivo (`StatCard`s no topo do painel) tinha só total, % IA, tradicionais e itens com rótulo editorial confiável. Corrigido: nova função pura `veredictoPredominante()` (`web/src/lib/veredito-labels.ts`, testada isoladamente, retorna `null` em vez de fabricar um veredito quando a distribuição está vazia ou soma zero) alimenta um novo `StatCard` "Veredito predominante" no resumo. `VEREDITO_LABEL` (rótulos legíveis) foi extraído de `checagens-feed.tsx` para esse mesmo arquivo, para não duplicar o dicionário nos dois lugares que agora precisam dele — mesmo princípio já aplicado a `scripts/election_calendar.py` (Seção 11.1, item 9). 4 testes novos.

**3. RF3.3 — o gráfico de volume mensal nunca desenhava o calendário eleitoral que o campo já carregava (docs/PRD.md, Seção 6.1).** `DatasetCSummary.datas_turno_1` existe desde a Fase 3 (está no schema `zod`, no tipo TypeScript, no snapshot JSON), mas nunca era passado como prop para `MonthlyVolumeChart`, então nenhum marcador de 1º turno aparecia no gráfico de barras empilhadas do painel — RF3.3 dizia "[Implementado]" descrevendo só a metade "série temporal" do requisito, não a metade "calendário eleitoral". Corrigido: `MonthlyVolumeChart` aceita `datasTurno1` (passado pelo `page.tsx`) e desenha uma linha de referência vertical em cada mês de 1º turno que cai dentro do intervalo de meses exibido — a lógica de filtragem foi extraída como função pura exportada (`marcosEleitoraisVisiveis`) para ser testável sem depender de renderização de SVG do Recharts em `jsdom` (o projeto não tinha, até agora, nenhum teste automatizado de componente de gráfico — Recharts com `ResponsiveContainer` não mede largura/altura em `jsdom`; extrair a lógica de decisão como função pura contorna isso sem precisar de um mock de `ResizeObserver`). 3 testes novos.

**4. RF4.4 estava marcado como "não implementado" por engano (docs/PRD.md, Seção 6.2).** Rate limiting (`slowapi`, todos os endpoints) e log opt-in de submissões (`consentimento_log.jsonl`, via `permitir_uso_para_pesquisa`) já estavam implementados e testados desde o backlog da Seção 11.1 (itens 10-11) — o status de RF4.4 na Seção 6.2 simplesmente não tinha sido atualizado quando esses itens foram fechados. Só uma correção de documentação; nenhum código mudou por causa deste item.

**Verificação:** `models/` — 44/44 testes pytest passando (39→44, 5 novas regressões — 6 testes de calendário em `test_trend_index.py` + 1 em `test_api.py`, um dos quais substitui/estende cobertura existente). `web/` — 27/27 testes Vitest passando (16→27, 11 novos), lint (`npx eslint .`) e `npm run build` limpos. Verificação manual ponta a ponta: `/models` rodando com `uvicorn` + `/web` rodando com `npm start`, confirmando via `curl` que a home real mostra "Marcos de 1º turno eleitoral" para 2024 e 2026 no gráfico de volume mensal e para 2024/2026 no índice de tendência quando `/models` está no ar, e um aviso explícito (sem derrubar o resto da página) quando o serviço é interrompido no meio da sessão. Nenhuma estatística publicada anteriormente (H4, métricas do classificador, `model_comparison.md`) foi tocada por este trabalho — as mudanças são aditivas (novos campos/componentes), não uma alteração de dado ou de modelo.

**Itens de RF/backlog que permanecem genuinamente fora de escopo, e por quê (não confundir com uma lacuna a "descobrir" numa próxima revisão):** RF1.6-1.8 (Detector de Autoria v1) e RF4.2 (upload de vídeo/áudio, v1.1) dependem de coleta de corpus novo (Seção 5.3) — não são código faltando, são dado faltando; as três lentes "em construção" (Google Trends, redes sociais, institutos de pesquisa, Seção 6.1) dependem de acesso a APIs externas que este projeto não tem hoje — implementá-las com dado de exemplo violaria o princípio inegociável da Seção 1.1 (nunca apresentar dado simulado como real).

---

## 17. Preparação para deploy (`/models` no Render, `/web` no Vercel)

Auditoria pedida pelo autor antes do primeiro deploy real, fora do ambiente local de desenvolvimento. Diferente das Seções 15-16 (bugs/lacunas no código em si), esta seção é sobre configuração de plataforma — nenhuma delas altera comportamento local (`npm run dev`/`uvicorn --reload`).

**1. Dependências — nenhuma faltando.** `models/pyproject.toml` declara tudo que `api/main.py` e `models_pkg` usam (fastapi, uvicorn, pandas, scikit-learn, statsmodels, slowapi, pydantic); `web/package.json` declara tudo que `/web` usa (next, recharts, zod, csv-parse). `data/processed/*.csv` e `models/artifacts/*.joblib` estão versionados no git (confirmado com `git ls-files` no repositório do autor) — um clone normal pelo Render traz os dados e o modelo já treinado, sem passo manual de geração no servidor.

**2. `outputFileTracingIncludes`/`outputFileTracingRoot` em `web/next.config.ts` (implementado nesta rodada) — o painel lê o CSV real no Vercel, não só o snapshot.** Por padrão, um deploy do Vercel com "Root Directory" = `web` só empacotaria o que está dentro de `web/` para cada função serverless — `../data/processed/` ficaria de fora, e como `dataset-c.ts` monta o caminho do CSV em runtime (`path.join(process.cwd(), "..", "data", ...)`, não uma string literal), o rastreador de arquivos do Next (`@vercel/nft`) não consegue inferir essa dependência sozinho para incluí-la automaticamente. `outputFileTracingRoot` sobe a raiz de rastreamento para a raiz do monorepo (por padrão seria só `web/`); `outputFileTracingIncludes` inclui explicitamente `../data/processed/dataset_c_unificado.csv` no pacote das rotas `/` e `/metodologia` (as únicas que chamam `getDatasetCSummary()`/`getChecagensRecentes()`). Verificado localmente: depois de `npm run build`, `dataset_c_unificado.csv` aparece de fato em `.next/server/app/page.js.nft.json`, resolvendo para o caminho real do arquivo (`../../../../data/processed/dataset_c_unificado.csv` a partir de `.next/server/app/`, que é exatamente a raiz do monorepo) — essa é a mesma lista de arquivos que o Vercel usa para montar o pacote de cada função serverless, então é uma verificação direta do mecanismo, não uma inferência. **Passo manual obrigatório que só existe no painel do Vercel** (nenhuma configuração de repositório resolve isso): em Project Settings → General → Root Directory, habilitar "Include source files outside of the Root Directory in the Build Step" — sem isso, o Vercel nem baixa `../data/` no ambiente de build. Com essa configuração completa, o feed de checagens (RF3.2, `getChecagensRecentes()`) — que não tem fallback para o snapshot, ao contrário do resumo/gráficos — passa a funcionar no Vercel também, eliminando a lacuna identificada na primeira auditoria de deploy (abaixo).

**3. O fallback de snapshot estático (Seção 9.2) continua existindo como rede de segurança, não como caminho principal no Vercel.** Se o toggle do item 2 não estiver marcado, ou num deploy realmente isolado (só `web/` copiado manualmente, sem passar pelo build do Next com as opções de tracing), `getDatasetCSummary()` ainda cai para `web/src/data/dataset_c_summary.json` — mas `getChecagensRecentes()` não tem esse fallback, então esse cenário residual continua deixando o feed indisponível (com aviso explícito, nunca uma lista vazia fingindo ser dado real). Lembrete: o snapshot precisa ser regenerado (`python scripts/export_dashboard_data.py`) e commitado a cada nova coleta para não ficar desatualizado nesse cenário de fallback.

**4. Variáveis de ambiente a configurar manualmente (não têm como estar no repositório, dependem das URLs pós-deploy):** `MODELS_API_URL` no Vercel, apontando para a URL pública do serviço no Render; `WEB_ORIGIN` no Render, apontando para a URL do Vercel — na arquitetura atual isso não chega a ser estritamente necessário porque toda chamada ao `/models` passa pelo servidor do Next (proxy em `/api/sensor-ia`, e a seção do índice de tendência em `page.tsx`), nunca direto do navegador, então CORS não é de fato acionado; ainda assim, configurar corretamente evita surpresa se um consumidor futuro chamar a API direto do navegador.

**5. Configuração de build/start do Render (não inferida automaticamente, ao contrário do Vercel com Next.js):** Root Directory = `models`; Build Command = `pip install -e .` — **com `-e`, não sem** — porque `trend_index.py` (RF2.4, Seção 16) localiza `scripts/election_calendar.py` por um caminho relativo calculado a partir de `__file__`; uma instalação não-editável copia o pacote para dentro de `site-packages`, quebrando esse caminho silenciosamente (a API não cai, mas `calendario_disponivel` vira `false` e os marcadores de 1º turno somem sem nenhum aviso na tela). Depois do deploy, confirmar com `curl <url-do-render>/forecast/index?periods=3` que `"calendario_disponivel": true` aparece na resposta. Start Command = `uvicorn api.main:app --host 0.0.0.0 --port $PORT` (os exemplos do README usam `--port 8000` fixo, só para uso local — o Render injeta `$PORT` dinamicamente).

**6. Observação operacional (não é bug, é o comportamento normal do plano gratuito do Render):** o serviço "dorme" após um período ocioso e leva ~30-50s para acordar no primeiro request depois disso. O timeout das chamadas do `/web` ao `/models` (Sensor de IA, índice de tendência) é de 8s — o primeiro acesso ao painel depois de um tempo ocioso provavelmente mostra os avisos de "indisponível" dessas duas seções só por causa do cold start, não por erro de configuração real.

**7. Log de consentimento em disco efêmero.** `data/consentimento_log.jsonl` (opt-in do Sensor de IA, Seção 9.1) é escrito no sistema de arquivos do próprio serviço — no Render (sem disco persistente configurado), esse arquivo é perdido a cada redeploy/restart. Sem impacto funcional (nunca é lido automaticamente pelo pipeline de treino), mas relevante saber caso o objetivo seja acumular esse log ao longo do tempo para uma curadoria futura do corpus do detector de autoria (Seção 5.3) — nesse caso, um disco persistente do Render (ou mover o log para um destino externo) seria necessário.

---

## 18. Achados do primeiro deploy real, e documentação da API aprofundada

Depois do primeiro deploy efetivo (`/models` no Render em `https://politicai.onrender.com`, `/web` no Vercel — Seção 17), duas rodadas de ajuste, pedidas pelo autor a partir do que ele observou no ambiente real (não no `localhost`):

**1. Labels de "1º turno AAAA" cortados/sobrepostos ao eixo Y, em produção (`MonthlyVolumeChart` e `TrendIndexChart`).** Reportado pelo autor com captura de tela do painel já implantado. Causa: as duas `<ReferenceLine>` (RF2.4, Seção 16) desenham seu `label` (`position: "top"`) acima da área de plotagem do Recharts, e `margin.top: 8` — suficiente em telas mais largas ou com menos marcos visíveis simultaneamente — não deixava espaço vertical suficiente para o texto do label quando o gráfico ficava mais estreito (breakpoint mobile/tablet do layout responsivo), cortando o texto contra o topo do SVG e sobrepondo o valor máximo do eixo Y. Corrigido em `web/src/components/monthly-volume-chart.tsx` e `web/src/components/trend-index-chart.tsx`: `margin.top` de `8` para `28` (mantendo os outros lados), com um comentário no próprio JSX explicando por que esse lado é assimetricamente maior. **Verificado com renderização real** (Playwright, não só `npm run build`/inspeção de código): screenshot de página inteira do painel local, com os dois gráficos exibindo "1º turno 2018"/"1º turno 2022" (volume mensal) e "1º turno 2024"/"1º turno 2026" (índice de tendência) legíveis e sem sobreposição. Lição registrada: `npm run build` limpo e testes passando não garantem renderização visual correta — um bug de layout/CSS/SVG só aparece olhando o resultado renderizado, e só apareceu porque o autor de fato abriu o deploy real e olhou o gráfico, não porque algum teste automatizado o pegou (nenhum teste deste projeto testa layout visual; os testes de gráfico, Seção 16 item 3, testam só a lógica pura de quais marcos aparecem, não onde o SVG os desenha na tela).

**2. Documentação da API (`/docs`, Swagger UI) aprofundada, a pedido explícito do autor.** `models/api/main.py` já expunha `/docs`/`/redoc`/`/openapi.json` por padrão (comportamento padrão do FastAPI, nenhuma configuração impedia isso — só não havia sido verificado/comunicado antes do deploy). A pedido do autor, a documentação foi expandida bem além do mínimo: descrição completa do serviço no nível do app (o que ele é e, importante, o que ele explicitamente **não** é — não confundir classificação de temática com detecção de autoria, não confundir o índice de tendência com previsão eleitoral validada); `openapi_tags` agrupando os endpoints em 4 categorias, cada uma com sua própria descrição de limitação; um modelo de resposta Pydantic explícito (`response_model=`) para cada endpoint que retorna dado estruturado, com `Field(..., description=...)` documentando cada campo individualmente e um exemplo completo (`json_schema_extra`); `responses={...}` documentando os códigos de erro reais de cada endpoint (422/429/503/501), não só o caminho feliz; `summary=` curto por endpoint, além do docstring completo (Markdown, aparece expandido no Swagger UI). Os campos e tipos de cada `response_model` foram conferidos contra o código real antes de serem escritos — `Predicao` (`models_pkg/inference/predictor.py`) e `PontoIndice`/`IndiceTendencia`/o dict de `marcos_eleitorais` (`models_pkg/forecasting/trend_index.py`) — para que a documentação nunca divirja do que a API de fato retorna; como `response_model=` também valida a resposta real em runtime (não é só cosmético em `/docs`), qualquer divergência teria quebrado os 44 testes pytest existentes (incluindo os que chamam `/predict/ia-topic`, `/predict/ia-topic/batch` e `/forecast/index` via `TestClient`) — todos continuaram passando depois da mudança, e uma verificação manual adicional com `uvicorn` rodando e `curl` real contra `/health`, `/predict/ia-topic`, `/forecast/index`, `/docs` e `/redoc` confirmou as respostas e os status HTTP corretos.

**Verificação:** `models/` — 44/44 testes pytest continuam passando (nenhum teste novo necessário; a mudança é de documentação/contrato de resposta, não de comportamento). `web/` — 27/27 testes Vitest, lint e `npm run build` continuam limpos após o ajuste de `margin.top`. `app.openapi()` gerado sem erro, com os 5 paths e as 4 tags esperadas; `/docs` e `/redoc` retornando HTTP 200 num `uvicorn` local real.

---

## 19. Recorte temporal de 01/01/2022 a 20/08/2026 (pedido da orientadora)

A orientadora pediu, numa conversa direta com o autor, para restringir a análise a um período mais recente — simplificando o projeto em torno do ciclo eleitoral de 2026. A decisão passou por duas iterações antes de fechar: primeiro cogitou-se "2023 em diante" (checado e viável: 49 itens no Dataset A, 169 no B), depois a orientadora fechou em **01/01/2022 a 20/08/2026** — cobrindo o ciclo eleitoral de 2022 inteiro como referência/comparação, até a data mais recente de coleta. Essa janela final preserva uma amostra bem maior que a proposta de 2023: 228 itens no Dataset A e 541 no B, e **preserva 100% dos 122 itens rotulados "IA"** do Dataset B (a tag `inteligencia-artificial` só passou a ser usada pelo Aos Fatos a partir de março de 2023, dentro da janela de qualquer forma), então nenhum item positivo foi perdido em nenhuma das duas versões do recorte.

**Bug encontrado e corrigido durante a implementação:** a primeira versão do filtro comparava `data_publicacao_iso <= "2026-08-20"` diretamente contra uma coluna com hora:minuto — como uma string de data pura é interpretada como meia-noite, isso excluía silenciosamente qualquer item publicado depois da meia-noite do próprio dia 20/08/2026 (havia um item às 15:57 nesse dia), tirando 1 item IA da contagem sem nenhum erro ou aviso. Detectado ao conferir a contagem esperada (553 coletados − 12 antes de 2022 = 541; o primeiro resultado deu 540) e corrigido comparando contra o dia seguinte (`< 2026-08-21`) em vez de `<=`, em ambos os notebooks geradores.

**O que foi alterado, e o que foi deliberadamente preservado intacto:**

- `data/raw/*` (os 4 CSVs de coleta do Dataset A e os 4 do Dataset B) — **intocados**, com o histórico completo desde 2018.
- `data/processed/dataset_a_fato_ou_boato_completo.csv` (322 itens, merge bruto sem enriquecimento) — **intocado nesta seção**, propositalmente: é, na prática, uma extensão do raw (só junta e deduplica, não enriquece nem analisa). *(Nota adicionada depois: este arquivo passou a receber um enriquecimento real — não heurístico — na Seção 20, que colhe o veredito em texto da página individual de cada checagem; ver lá antes de assumir que este CSV continua "zero enriquecimento".)*
- `scripts/gen_notebook_a.py` e `scripts/gen_notebook_b.py` — cada um ganhou uma célula logo após carregar os dados (`## 1.1 Recorte temporal`) que filtra `data_publicacao_checagem`/`data_publicacao_iso` para `>= 2022-01-01 e < 2026-08-21` antes de qualquer limpeza/enriquecimento/EDA subsequente, com markdown explicando a decisão e reafirmando que o raw não muda.
- `data/processed/dataset_a_fato_ou_boato_enriquecido.csv`: 322 → **228 itens** (179 de 2022, 24 de 2023, 22 de 2024, 3 de 2026).
- `data/processed/dataset_b_aosfatos_enriquecido.csv`: 553 → **541 itens** (122 `inteligencia-artificial`, preservados 100%; 407 de `eleicoes-2022`, eram 419; 12 de `eleicoes-2026`, inalterado).
- `data/processed/dataset_c_unificado.csv`: 875 → **769 itens** (228 + 541) — regenerado via `notebooks/03_dataset_c_unificado_eda.ipynb`, que só une os dois enriquecidos já filtrados, sem filtro próprio adicional.
- Os 3 notebooks (`01_dataset_a_fato_ou_boato_eda.ipynb`, `02_dataset_b_aosfatos_eda.ipynb`, `03_dataset_c_unificado_eda.ipynb`) foram **reexecutados de ponta a ponta** (`scripts/execute_notebooks.py`) sobre os dados já filtrados — toda tabela, gráfico e teste estatístico embutido neles reflete o recorte, calculado de verdade (nenhum número foi editado manualmente nos notebooks).
- `models/configs/ia_topic_classifier_v0.yaml`: `artifact.version` ganhou o sufixo `-corte2022a2026`, para que o artefato treinado sobre os dados recortados seja identificável no `manifest.json` e nunca confundido com uma versão anterior.
- Classificador retreinado (`train_ia_topic_classifier.py`) sobre os 541 itens: split 432 treino / 109 teste. Teste: acurácia 0.991, ROC-AUC 1.000, IA precisão 0.962/recall 1.000/F1 0.980 (n=25), Tradicional precisão 1.000/recall 0.988/F1 0.994 (n=84). CV 5-fold (a estimativa mais defensável, ver Seção 9.1): F1 IA 0.979 ± 0.021, acurácia 0.991 ± 0.009 — números muito próximos aos de antes do recorte (F1 IA 0.974 ± 0.018), o que era esperado já que só ~12 itens (2% do total) foram removidos. `artifacts/model_comparison.md` também foi regenerado (Naive Bayes, SVM linear, gradient boosting — todos na faixa 0.74-0.98 F1, mesma conclusão de antes: regressão logística não perde para os outros).
- `web/src/data/dataset_c_summary.json` (snapshot estático de fallback) regenerado via `scripts/export_dashboard_data.py` a partir do novo `dataset_c_unificado.csv`.
- `models/src/models_pkg/data/loader.py` (docstring da tabela de colinearidade tag×rótulo) e `web/src/app/metodologia/page.tsx` (contagens citadas na página de metodologia) atualizados com os números pós-recorte.

**O que NÃO muda, verificado de verdade, não assumido:** `GET /forecast/index` — o índice de tendência já agregava só volume mensal de itens rotulados IA, e todo item IA já estava dentro da janela 2022–2026 mesmo antes deste recorte; recalculado após a mudança, `n_observacoes` continua 42, `metodo` continua `binomial_negativa`, `calendario_disponivel` continua `true` — nenhuma regressão nessa funcionalidade.

**Verificação:** `models/` — 44/44 testes pytest passando sobre os dados novos (nenhum teste hardcoda contagem exata, então nenhum precisou mudar). `web/` — 27/27 testes Vitest, lint e `npm run build` passando limpos com o `dataset_c_unificado.csv` de 769 itens. Reexecução dos 3 notebooks sem erros.

**Efeito na colinearidade tag×rótulo (o motivo metodológico original para considerar um recorte):** removeu só os ~12 itens de `eleicoes-2022` publicados antes de 01/2022 (a tag é temática, não um filtro de data, então tinha itens de fora do ano nominal) — reduz muito pouco o problema de fundo descrito na Seção 1.3/10.1 (todo item IA ainda vem de uma única tag de busca). Diferente da proposta de 2023 (que teria invertido o desbalanço de classe para 72% IA), esta janela final mantém a proporção original (~23% IA / 77% Tradicional) quase intacta — a mudança é pequena e principalmente sobre foco temporal do projeto, não uma correção estatística forte do confound. Seções 10 e 11 abaixo descrevem investigações feitas **antes** deste recorte, sobre o histórico completo (875/553/322 itens) — são registro histórico do que foi encontrado naquele momento; a diferença de amostra é pequena o suficiente (875→769, -12%) que as conclusões qualitativas (H4, direção dos coeficientes) não deveriam mudar, mas não foram recalculadas retroativamente nesta seção — se forem citadas, vale reconferir com os notebooks reexecutados.

## 20. Veredito real extraído da página individual do Dataset A (dado real, não heurística) — pedido explícito do autor

Desde a coleta original (Seção 1), o Dataset A só tinha o veredito como **imagem** (o selo "FALSO"/"BOATO"/"GOLPE" da página de listagem) — `veredito_estimado` sempre foi uma heurística de regex sobre o padrão de abertura do título (cobertura ~56%, notebook `01`, Seção 3.2), nunca uma leitura do dado real. O autor perguntou se um OCR desse selo era realmente necessário, com a hipótese de que a página INDIVIDUAL de cada checagem (nunca visitada pela coleta original — que só passou pelas páginas de listagem) pudesse trazer o veredito como texto real, num parágrafo "Por que é boato?"/"Por que é distorcido". Testado com exemplos reais antes de decidir o método: confirmado — quando presente, é HTML real (`<article>.textContent`), nunca uma imagem. OCR foi descartado por não ser necessário, não por ser inviável.

**O que foi coletado:** as 322 páginas individuais (não só o recorte 2022-2026) foram localizadas e lidas. Como a coleta original nunca guardou a URL de cada item nem o corpo do texto, cada URL precisou ser reconstruída a partir do título (o Plone gera o slug da URL a partir do título vigente na criação da página — quebra quando o título é editado depois, o que de fato acontece numa fração dos itens mais antigos) com 2 níveis de busca como *fallback* quando o slug direto não bate. Método completo, incluindo por que o sandbox deste projeto não tem acesso de rede direto ao domínio do TSE (só via uma aba real do Claude in Chrome, com `fetch()` same-origin injetado via JS) e por que este *não* é um script `requests`-based comum, está em `scripts/raw_scrape_dataset_a_veredito_paginas.py`. Resultado bruto, tal como coletado em 25/08/2026: `data/raw/dataset_a_veredito_paginas_individuais.csv` (322 linhas: `id_checagem`, `metodo_localizacao_pagina`, `url_checagem_individual`, `veredito_texto_pagina`).

**Resultado, honesto sobre cobertura:** das 322 páginas, 317 foram localizadas (204 por slug direto, 91 por busca com filtro de tag, 22 por busca sem filtro — necessário para os itens `FOB-EXTRA-*`, de outras 7 tags) e 5 não foram localizadas por nenhum dos 3 métodos (`nao_localizado`, nunca um chute). Das 317 localizadas, só **77 (23,9% dos 322 originais)** tinham a seção "Por que é X" no template — as outras 240 páginas existem e foram lidas, mas expressam o veredito em prosa livre (comum nas checagens mais antigas, 2018-2022, sem o cabeçalho padronizado), então a extração por regex genuinamente não encontra nada ali — **não é falha de extração, é ausência real da seção nesse template**. Dos 77 vereditos reais extraídos: 76 "boato", 1 "distorcido".

**Como isso entra no pipeline** (`scripts/merge_verdito_real_dataset_a.py`, aplicado aos 322 itens ORIGINAIS, sem recorte temporal — o recorte 2022-2026 continua acontecendo só depois, no notebook `01`, exatamente como pedido: *"faz isso para todos os dados originais do dataset e mantém o recorte só no processed"*):
- 4 novas colunas em `dataset_a_fato_ou_boato_completo.csv`: `metodo_localizacao_pagina`, `url_checagem_individual`, `veredito_texto_pagina`, `fonte_veredito_pagina` (`texto_real_pagina_individual` | `pagina_sem_secao_por_que` | `pagina_nao_localizada`).
- `gen_notebook_a.py`, nova Seção 3.2.1: `veredito_final` usa o texto real quando `fonte_veredito_pagina == "texto_real_pagina_individual"`, cai para `veredito_estimado` (heurística de título) nos outros casos — sempre com `fonte_veredito_final` marcando qual dos dois foi usado, item a item, nunca misturado sem rótulo (mesmo padrão de proveniência já usado em `fonte_veredito`/`fonte_rotulo_ia`/`fonte_categoria_tema` no Dataset C).
- `gen_notebook_c.py`: `veredito_original`/`veredito_binario`/`fonte_veredito` do lado do Dataset A agora vêm de `veredito_final`/`fonte_veredito_final` (antes: sempre `"heuristica_regex_titulo"`, estático). `VEREDITO_MAP_A` ganhou `"Distorcido": "parcialmente_falso"` (equivalente semântico ao `"distorcido"` do Dataset B, que já mapeava para `parcialmente_falso` — não para `"falso"`, que seria uma perda de informação).
- Dentro do recorte 2022-2026 (228 itens), a proporção final é 59 itens (25,9%) com veredito real de texto e 169 com heurística de título — note que essa proporção (25,9%) é ligeiramente maior que a dos 322 originais (23,9%) porque os itens mais recentes (2023-2026, dentro do recorte) usam o template novo com mais frequência que os mais antigos (fora do recorte em boa parte).
- `dataset_c_unificado.csv`, `web/src/data/dataset_c_summary.json` (via `scripts/export_dashboard_data.py`) e os 3 notebooks foram **regenerados e reexecutados de ponta a ponta** com essas mudanças.

**Efeito colateral encontrado e corrigido nos números do notebook `03` (não causado por esta mudança, mas descoberto ao reexecutar):** a prosa da Seção 7 do notebook `03` sobre a comparação de `vetor_midia` entre A e B estava desatualizada em relação ao código já em vigor antes desta sessão (chi2=10.174/p=0.0376, texto antigo, dizia que as duas fontes eram estatisticamente diferentes) frente ao que o código atual realmente produz (chi2=8.143/p=0.0865 — **não** significativo a 5%, ou seja, as duas fontes **convergem**, a leitura oposta da que estava escrita). Corrigido para refletir o resultado real da reexecução. Os números do teste de veredito pooled/só-B na mesma seção também foram atualizados para os valores pós-mudança (chi2=12.214/p=0.0022 pooled; chi2=17.243/p=0.0002/V=0.184/n=510 só B) — a leitura qualitativa de H1 (IA mais falso que Tradicional, testado só no Dataset B) não muda.

**O que isso NÃO resolve:** ainda não existe validação humana de que a extração por regex bate 100% com o veredito real percebido por um leitor (ex.: "distorcido" pode, em teoria, aparecer em contextos que não são exatamente o parágrafo de veredito) — uma amostra dos 77 itens deveria ser conferida manualmente antes de qualquer teste inferencial que dependa criticamente desse dado na Fase 3, mesmo sendo texto real (não heurística) da fonte. `rotulo_ia`, `categoria_macro`, `alvo_ataque` e `vetor_midia` do Dataset A continuam 100% heurísticos — esta sessão não tentou estender o mesmo método a eles.

**Verificação:** merge script com `assert` de contagem de linhas inalterada (322 → 322) e validação `one_to_one` do merge; `raw_scrape_dataset_a_veredito_paginas.py` roda como *smoke test* standalone e imprime a mesma distribuição relatada acima; os 2 notebooks afetados (`01`, `03`) reexecutados de ponta a ponta sem erros via `scripts/execute_notebooks.py`; `dataset_c_summary.json` regenerado e a estrutura de chaves conferida como inalterada (só os valores de `distribuicao_veredito` mudaram, de acordo com o esperado). Suites `pytest`/`vitest` do modelo e do web **não foram reexecutadas nesta sessão** (ambiente sem as dependências instaladas) — mas o classificador (`ia_topic_classifier`) não usa veredito como feature nem como alvo (confirmado por grep em `models/src`), então não há motivo para esperar regressão ali; quem retomar o projeto deveria rodar as duas suítes mesmo assim antes de deploy, por precaução.

---

## 21. Texto completo das páginas individuais: prova de conceito, não escalada (decisão explícita do autor)

Seguindo a Seção 20, o autor perguntou se o texto INTEGRAL de cada página individual (não só o parágrafo "Por que é X") tinha sido salvo, e pediu para refazer a extração salvando também texto completo + URL, caso ainda não estivesse feito. Resposta honesta: não estava feito — a Seção 20 só salvou o veredito extraído (um trecho curto), nunca o corpo inteiro da página.

**O que foi testado:** um método de extração de texto integral + hashtags de agências parceiras foi desenvolvido e validado contra 10 dos 317 itens localizados (`FOB-0001` a `FOB-0010`). Durante o teste surgiu uma descoberta nova: algumas páginas têm, no atributo `alt` da imagem que linka para a matéria original da agência parceira (Boatos.org, Fato ou Fake/G1, Agência Lupa etc.), uma hashtag de veredito escrita pela própria agência (ex.: `"...É #FAKE que Daniela Lima tenha dito que Bolsonaro ganhou as eleições de 2022"`). É texto real, mas não normalizável num campo único sem mais trabalho (frase e hashtag variam por agência, e uma página pode reunir mais de uma agência). Método completo (incluindo os dois limites de truncamento da ferramenta de execução de JS descobertos e contornados, e o motivo de não ter virado um script Python autônomo) documentado em `scripts/poc_texto_completo_dataset_a.py`. Resultado da amostra: `data/raw/dataset_a_texto_completo_amostra.json` (10 registros: `id_checagem`, `texto_completo_pagina`, `hashtags_agencia_parceira`, `url_checagem_individual`).

**Decisão explícita, tomada em conjunto com o autor: NÃO escalar para os 307 itens restantes.** Motivo registrado para não virar dívida técnica silenciosa: o dado que a Fase 3 usa é o veredito (já extraído para os 322 itens na Seção 20), não o texto integral; o valor do texto completo só se realizaria numa etapa futura distinta (reler/reclassificar os ~240 itens sem a seção "Por que é X" a partir da prosa livre), que não foi pedida nesta sessão; e o método de coleta é manual e frágil (depende de aba do Chrome aberta, lotes de 10 por chamada por causa dos limites de truncamento), não um script reexecutável de uma vez. Isto é: o texto integral hoje existe como prova de conceito para 10 itens, não como dataset completo — nenhum merge foi feito em `dataset_a_fato_ou_boato_completo.csv` para este dado, e nenhuma coluna nova foi adicionada ao pipeline por causa dele. Se a coleta completa for necessária no futuro, o método é reprodutível como está — os passos exatos para retomar estão no próprio script.

**Verificação:** os 10 registros da amostra foram conferidos manualmente contra as páginas de origem (tamanho de `texto_completo_pagina` e `hashtags_agencia_parceira` batem com o que as páginas mostram); a reconstrução dos pedaços de texto (`tc` → `texto_completo_pagina`) foi validada contra um teste de item único anterior à divisão em pedaços, com resultado idêntico (5016 caracteres para `FOB-0001` nos dois métodos). Nenhuma mudança foi feita em `gen_notebook_a.py`, `gen_notebook_c.py`, `dataset_c_unificado.csv` ou `dataset_c_summary.json` nesta seção — o escopo desta sessão, para este item, foi documentação e prova de conceito, não pipeline.

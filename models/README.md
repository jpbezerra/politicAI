# `/models` — Motor de ML do projeto politicAI

Duas funcionalidades, descritas em detalhe em [`../docs/PRD.md`](../docs/PRD.md), Seção 4:

1. **Classificador de temática de IA (v0)** — dado um texto político, estima
   se ele é sobre desinformação envolvendo IA (deepfake, áudio clonado,
   texto sintético). **Já treinado com dados reais** (ver Seção "Resultados"
   abaixo).
2. **Índice de tendência de desinformação por IA (v0)** — volume mensal
   real de checagens rotuladas IA, com uma projeção de curto prazo simples
   e auditável. Ver a Seção "Limitações" — **isto não é uma previsão
   validada de impacto eleitoral**.

Uma terceira funcionalidade — **detector de autoria por IA (v1)** — está
roadmapeada, mas não implementada: não existe, neste repositório, um corpus
rotulado de texto-humano vs. texto-gerado-por-IA sobre temas políticos. O
endpoint correspondente (`/predict/ia-authorship`) responde `501` de
propósito, em vez de simular uma capacidade que não existe. Ver
`docs/PRD.md`, Seção 4.3.

## Por que só o Dataset B para treino

Só o Dataset B (checagens do Aos Fatos) tem rótulo de IA atribuído
editorialmente por jornalistas (`rotulo_grupo`). O Dataset A tem uma coluna
`rotulo_ia`, mas ela vem de uma heurística de regex sobre título, não de
julgamento editorial, e não marcou nenhum item como IA na coleta atual
(0/322). Detalhe completo em
`src/models_pkg/data/loader.py` (docstring do módulo).

## Como rodar

```bash
cd models
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Treinar o classificador de temática (tuning + CV + fit + calibração +
# avaliação + versionamento -- ver "Pipeline de treino" abaixo; gera artifacts/*)
PYTHONPATH=src python -m models_pkg.training.train_ia_topic_classifier \
  --config configs/ia_topic_classifier_v0.yaml

# Comparar com outros algoritmos sobre o mesmo TF-IDF (gera artifacts/model_comparison.md)
PYTHONPATH=src python -m models_pkg.training.compare_models

# Rodar os testes (44 testes)
PYTHONPATH=src python -m pytest tests/ -v

# Subir o serviço de inferência (consumido pelo /web)
PYTHONPATH=src uvicorn api.main:app --reload --port 8000
```

Endpoints do serviço (`api/main.py`), todos com rate limiting via `slowapi`
(ver "Rate limiting e consentimento" abaixo):

- `GET /health`
- `POST /predict/ia-topic` — `{"texto": "...", "permitir_uso_para_pesquisa": false}` → rótulo + probabilidade calibrada + confiança + termos influentes (30/min)
- `POST /predict/ia-topic/batch` — `{"textos": ["...", ...]}`, até 50 textos por chamada → lista de predições na mesma ordem (10/min)
- `POST /predict/ia-authorship` — `501` (não implementado, ver acima) (30/min)
- `GET /forecast/index?periods=6` — série histórica + projeção do índice de tendência, incluindo o campo `metodo` e o contexto de calendário eleitoral (RF2.4, ver "Índice de tendência" abaixo) (30/min)

## Pipeline de treino (Fase 3 — validação cruzada, tuning e calibração)

`train_ia_topic_classifier.py` roda, em ordem: (1) tuning de hiperparâmetros
via `GridSearchCV` sobre o conjunto de validação (`PredefinedSplit`, nunca o
teste); (2) validação cruzada estratificada de 5 folds sobre treino+validação
com os hiperparâmetros escolhidos, para reportar uma faixa de desempenho em
vez de um ponto único; (3) fit final em treino+validação; (4) calibração de
probabilidade (`CalibratedClassifierCV`, método sigmoid, `cv=5`) sobre o
mesmo conjunto; (5) avaliação no conjunto de teste (hold-out nunca visto
antes); (6) geração do model card; (7) salvamento versionado do artefato.
Use `--skip-tuning` para pular a busca de hiperparâmetros (reusa os valores
já salvos na config) e `--cv-splits N` para mudar o número de folds.

`compare_models.py` roda a mesma validação cruzada estratificada sobre
quatro candidatos (regressão logística, Naive Bayes multinomial, SVM linear
calibrado, gradient boosting) para justificar com evidência, não só
conveniência, a escolha do modelo de produção — ver
`artifacts/model_comparison.md` (gerado, dados reais):

| Modelo | F1 (classe IA) | ROC-AUC | Acurácia |
|---|---|---|---|
| regressao_logistica_v0 (produção atual) | 0.974 ± 0.018 | 1.000 ± 0.000 | 0.988 ± 0.007 |
| naive_bayes_multinomial | 0.735 ± 0.077 | 1.000 ± 0.000 | 0.907 ± 0.020 |
| svm_linear_calibrado | 0.974 ± 0.018 | 1.000 ± 0.000 | 0.988 ± 0.007 |
| gradient_boosting_hist | 0.979 ± 0.020 | 0.996 ± 0.007 | 0.991 ± 0.009 |

(Números pós-recorte de 01/01/2022 a 20/08/2026, ver `docs/PRD.md`, Seção 19 —
a tabela mudou pouco em relação ao histórico completo, já que o recorte
removeu só ~12% da amostra.)

A regressão logística permanece o modelo de produção: desempenho
estatisticamente indistinguível do gradient boosting e do SVM calibrado
(dentro do desvio-padrão entre folds, com só 122 itens IA no total), mas com
a vantagem de expor coeficientes lineares por termo — usados para os "termos
mais influentes" do model card e do Sensor de IA, algo que os outros dois
não oferecem da mesma forma direta.

## Versionamento de artefatos

Cada treino grava um snapshot imutável em
`artifacts/versions/<versao>_<timestamp>/` (pipeline, calibração, métricas e
model card daquele treino específico) e registra a entrada em
`artifacts/versions/manifest.json` (histórico completo, mais antigo
primeiro). Os caminhos "sem versão" no topo de `artifacts/`
(`ia_topic_classifier_v0.joblib`, `..._model_card.md`, etc.) continuam
existindo, sempre como cópia do treino mais recente, por compatibilidade com
o que já consumia esses caminhos (`api/main.py`, `predictor.py`).

## Resultados do classificador v0 (dados reais, não simulados)

Treinado em 541 itens do Dataset B (rótulo editorial real, já restrito a
checagens entre 01/01/2022 e 20/08/2026 — ver `docs/PRD.md`, Seção 19), split
estratificado 72%/8%/20% (432 treino, 109 teste), regressão logística sobre
TF-IDF (unigrama+bigrama), com calibração de probabilidade. Métricas no
conjunto de teste (hold-out, nunca visto no treino/tuning/CV):

| Classe | Precisão | Recall | F1 | N |
|---|---|---|---|---|
| IA | 0.96 | 1.00 | 0.98 | 25 |
| Tradicional | 1.00 | 0.99 | 0.99 | 84 |

Acurácia geral: 0.99; ROC-AUC: 1.00. A validação cruzada estratificada (5
folds sobre treino+validação, seed=42) dá uma leitura mais defensável dessa
mesma classe: F1 da classe IA 0.979 ± 0.021, acurácia 0.991 ± 0.009 — a
faixa entre folds, não só o ponto único do teste, é o que deve ser citado
como estimativa de desempenho. **Mesmo assim, estes números são altos demais
para serem interpretados como "o modelo está pronto para produção geral"**
— ver a limitação abaixo antes de citar essas métricas em qualquer lugar.

Model card completo (gerado automaticamente a cada treino, agora incluindo
as seções de tuning e validação cruzada):
`artifacts/ia_topic_classifier_v0_model_card.md`.

## Índice de tendência: de regressão linear a Binomial Negativa/Poisson

A v0 original (`forecasting/trend_index.py`) extrapolava a série mensal de
volume IA com uma regressão linear simples (OLS) sobre contagens inteiras —
auditável, mas estatisticamente inadequada para dados de contagem (variância
que cresce com a média, nunca deveria projetar um valor negativo). Com os
dados reais até a última coleta, a série mensal tem média ≈3.6 e variância
≈7.7 — superdispersão clara (variância > média), o que descarta um Poisson
simples em favor de uma **Binomial Negativa**
(`statsmodels.discrete.discrete_model.NegativeBinomial`). Se ela não
convergir (ex.: série curta demais), o módulo cai para um GLM de Poisson e,
na ausência de `statsmodels` ou com poucos dados, para a regressão linear
original — o método efetivamente usado é sempre reportado no campo `metodo`
da resposta de `/forecast/index`, nunca escondido. Ver a docstring completa
do módulo para o raciocínio estatístico.

**Contextualização com calendário eleitoral (RF2.4, `docs/PRD.md` Seção
5.2/16):** cada ponto da resposta carrega `mes_de_1_turno` e
`dias_para_1_turno_mais_proximo`, e a resposta como um todo carrega
`marcos_eleitorais` (turnos dentro do período coberto) e
`calendario_disponivel`. O módulo importa `scripts/election_calendar.py`
(mesma fonte de datas usada pelos notebooks) via `sys.path`, assumindo o
mesmo checkout de monorepo já assumido por `DEFAULT_DATASET_C` — se
`scripts/` não estiver disponível como sibling de `models/`,
`calendario_disponivel` vem `false` e os campos de calendário vêm
`false`/`None`/`[]`, nunca uma data inventada. Consumido por `/web`
(`src/components/trend-index-chart.tsx`) para desenhar marcadores
verticais de 1º turno no gráfico do índice.

## Rate limiting e consentimento

A API agora tem rate limiting básico (`slowapi`, limites por endpoint
listados acima) e um campo opcional `permitir_uso_para_pesquisa` em
`/predict/ia-topic`: quando `true`, o texto submetido e a predição são
anexados (append-only) a `data/consentimento_log.jsonl` (gitignored — dado
potencialmente sensível). Esse log **nunca** é usado automaticamente para
retreinar o modelo — é a forma mais direta de começar a construir, com
consentimento explícito, o corpus pareado humano-vs-IA necessário para o
detector de autoria (v1, ver `docs/PRD.md`, Seção 5.3). Sem consentimento
(padrão), nada é gravado.

## Limitações (leia antes de estender ou citar este trabalho)

### 1. Confound de desenho amostral no classificador (temática)

O rótulo `rotulo_grupo` é **perfeitamente colinear** com a tag de busca
usada na coleta do Dataset B:

```
tag_pesquisa               IA   Tradicional
eleicoes-2022                0          407
eleicoes-2026                 0           12
inteligencia-artificial   122            0
```

(Números já refletindo o recorte de 01/01/2022 a 20/08/2026, `docs/PRD.md`
Seção 19 — `eleicoes-2022` era 419 antes do recorte; a colinearidade em si
não muda, só o N da baseline "Tradicional".)

Isso é consistente com o rótulo refletir o tema real dos textos (quem
pesquisou "inteligência artificial" no Aos Fatos encontrou artigos sobre
IA), mas significa que as métricas acima podem incluir sinais de
lote/época de coleta que não generalizam para um texto qualquer submetido
ao Sensor de IA fora dessas três buscas. Uma validação mais forte exigiria
rótulos IA coletados de múltiplas buscas/períodos, não concentrados numa
única tag.

### 2. Confound de desenho amostral no índice de tendência (descoberto ao implementar)

O PRD (`docs/PRD.md`, RF2.1) originalmente especificava normalizar o
volume de itens IA pelo volume TOTAL de checagens do mesmo mês. Ao
implementar, descobrimos que essa normalização produz um artefato: como o
Dataset B foi coletado por 3 buscas por tag feitas separadamente, em
vários meses de 2024–2025 praticamente 100% do "total do mês" já vem da
busca "inteligencia-artificial" (não há itens de outras buscas datados
naquele mês) — isso faz a proporção IA/total saltar para perto de 1.0 sem
refletir uma mudança real no mundo. Por isso, o índice implementado usa
**volume absoluto mensal**, não uma proporção — ver docstring completa em
`src/models_pkg/forecasting/trend_index.py`. Mesmo o volume absoluto ainda
reflete, em parte, o que o Aos Fatos escolheu investigar e indexar sob essa
tag, não necessariamente todo o universo de desinformação por IA.

### 3. Amostra pequena

122 itens IA no total — qualquer diferença ou tendência deve ser lida como
indicativa, não como estatisticamente robusta para decisões de alto risco.

### 4. Temática ≠ autoria

Repetindo o ponto mais importante do PRD: este classificador NÃO detecta
se um texto foi escrito por IA. Ele detecta se o texto é SOBRE o tema "IA
na política". Ver `docs/PRD.md`, Seção 4.1.

### 5. Boilerplate editorial contaminava os termos mais influentes (corrigido, estendido na Fase 3)

Ao inspecionar os "termos mais associados a IA" do primeiro treino, dois
deles eram lixo de template do site, não vocabulário sobre o tema: "receba
checagens" e "checagens reportagens" vinham do CTA fixo "Siga o canal do
Aos Fatos no WhatsApp e receba nossas checagens e reportagens", colado sem
separador à legenda do post/vídeo checado; e "caminho" vinha da abertura
padronizada "O caminho da apuração...". Numa segunda rodada (Fase 3,
revisando o corpus em busca de mais variantes não cobertas), mais quatro
padrões de template foram encontrados e removidos: a caixa de parceria com
o programa de checagem da Meta (presente em 41-44% dos itens Tradicionais e
em ZERO itens IA — mesmo viés do achado original, só que na direção
oposta), a nota de checagem colaborativa de fim de semana, a nota de
checagem cruzada com outra agência parceira (27 combinações de nomes
distintas encontradas), e um rodapé raro de "Todos os direitos reservados."
Nenhum desses seis é sinal real sobre o conteúdo do boato — são template
ou metadado editorial do site, e cada um aparecia de forma desigual entre
os grupos IA/Tradicional simplesmente porque o Aos Fatos foi adicionando e
removendo esses blocos do site ao longo do tempo, e os itens IA são
majoritariamente mais recentes (mesmo confound de tag/época do item 1,
agora visível em seis lugares diferentes no nível lexical). Todos os seis
estão em `src/models_pkg/data/boilerplate.py`, aplicados antes da
vetorização — ver a docstring completa do módulo para a distribuição exata
de cada achado, e `tests/test_boilerplate.py` (15 testes, incluindo
checagens de regressão para garantir que os regexes não comem conteúdo real
que só começa parecido com o template, nem conteúdo real que continua a
mesma frase do boilerplate sem um ponto — ver docs/PRD.md, Seção 15, item 2,
para o achado dessa segunda checagem numa revisão pós-implementação). As métricas
agregadas não mudaram (o sinal temático genuíno já dominava), mas os
termos mais influentes agora são todos sobre o conteúdo real (`ia`,
`artificial`, `inteligência artificial`, `gerado`, `busca reversa` — esta
última é, na verdade, uma técnica real de verificação de vídeo/imagem
manipulada, sinal legítimo). Esta limpeza continua sendo *best-effort*, não
exaustiva — uma nova coleta pode introduzir outras variantes não cobertas
aqui; ver a docstring do módulo para o sinal de quando revisitar.

### 6. Datas de turno eleitoral, agora centralizadas

`DATAS_TURNO_1` (datas do 1º turno de 2018/2022/2026, usadas para calcular
`dias_para_eleicao`) vivia duplicada em `trend_index.py`, no script de
export do dashboard e em cada um dos três notebooks de EDA da Fase 2. Agora
tem uma única fonte: `scripts/election_calendar.py`, importado por todos os
consumidores — elimina o risco de as datas divergirem entre `/models` e os
notebooks depois de uma edição em só um lugar.

## Estrutura

```
models/
├── README.md
├── pyproject.toml
├── .gitignore                      # .venv/, __pycache__/, data/consentimento_log.jsonl, etc.
├── configs/
│   └── ia_topic_classifier_v0.yaml
├── notebooks/
│   └── 01_ia_topic_classifier_baseline.ipynb   # EDA + baseline exploratório
├── src/models_pkg/
│   ├── data/loader.py                    # carregamento + split estratificado
│   ├── data/boilerplate.py               # limpeza de CTA/template recorrente do site (ver Limitações #5)
│   ├── features/text_features.py         # TF-IDF + stopwords PT-BR
│   ├── evaluation/cross_validation.py    # validação cruzada estratificada
│   ├── evaluation/metrics.py
│   ├── training/tune_hyperparameters.py  # GridSearchCV sobre o conjunto de validação
│   ├── training/compare_models.py        # comparação entre algoritmos (artifacts/model_comparison.md)
│   ├── training/train_ia_topic_classifier.py
│   ├── inference/predictor.py
│   └── forecasting/trend_index.py        # índice de tendência (Binomial Negativa/Poisson/linear) + calendário eleitoral (RF2.4)
├── api/main.py                     # serviço FastAPI consumido pelo /web (rate limiting, consentimento, lote)
├── tests/                           # pytest (44 testes)
└── artifacts/
    ├── model_comparison.md
    ├── ia_topic_classifier_v0.joblib          # cópia do treino mais recente (compatibilidade)
    ├── ia_topic_classifier_v0_model_card.md   # idem
    └── versions/
        ├── manifest.json                      # histórico de todos os treinos
        └── <versao>_<timestamp>/               # snapshot imutável de cada treino
```

## Roadmap (ver docs/PRD.md, Seção 8, para o roadmap completo do produto)

- **v1**: detector de autoria por IA — depende de coletar um corpus pareado
  texto-humano vs. texto-gerado-por-IA sobre os mesmos temas políticos.
- **v1.1**: extensão multimodal (vídeo/áudio).
- **v2**: índice de tendência revisitado com um ciclo eleitoral completo de
  dados (até a eleição de outubro/2026) e, se resolvido o problema de
  comparabilidade de coleta, uma normalização por volume total mais
  confiável.

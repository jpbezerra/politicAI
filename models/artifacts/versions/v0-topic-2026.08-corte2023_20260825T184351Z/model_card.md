# Model card — Classificador de Temática de IA (v0)

**Versão:** v0-topic-2026.08-corte2023
**Gerado em:** 2026-08-25T18:43:51.865969+00:00
**Tipo de modelo:** Regressão logística sobre TF-IDF (unigrama+bigrama), com
calibração de probabilidade (`CalibratedClassifierCV`, sigmoid, 5-fold).

## O que este modelo faz (e o que não faz)

Este modelo responde: **"este texto de checagem de fatos é sobre um boato
envolvendo conteúdo político manipulado/gerado por IA?"** — ou seja, um
classificador de **temática**.

Ele **não** responde "este texto foi escrito por um modelo de IA?" — essa é
uma tarefa diferente (detecção de autoria), que exigiria um corpus pareado
texto-humano vs. texto-gerado-por-IA sobre os mesmos temas políticos, que
não existe neste repositório ainda. Ver `docs/PRD.md`, Seção 4.1 e 4.3.

## Dados de treino

- Fonte única: `data/processed/dataset_b_aosfatos_enriquecido.csv`
  (169 itens, rótulo editorial real do Aos Fatos — `rotulo_grupo`).
- O Dataset A **não** foi usado: sua coluna `rotulo_ia` é uma heurística de
  regex sobre título, não um julgamento editorial, e não teve nenhum item
  marcado IA na coleta atual (0/322) — usá-la inflaria artificialmente a
  classe "Tradicional" com um rótulo de qualidade diferente do rótulo real
  de "IA". Ver `models/src/models_pkg/data/loader.py`.
- `corpo_artigo` passa por uma limpeza de boilerplate editorial recorrente
  (CTA de assinatura "Siga no WhatsApp...", frase-modelo "O caminho da
  apuração...") antes de ser vetorizado — sem isso, esses trechos fixos
  apareciam como termo espúrio mais associado à classe IA, simplesmente
  porque o Aos Fatos adicionou esse template ao site depois de um certo
  período e os itens IA são majoritariamente mais recentes. Ver
  `models/src/models_pkg/data/boilerplate.py` para o achado completo
  (best-effort, não exaustivo — a mesma contaminação também afetava os
  notebooks de EDA da Fase 2, corrigida em `notebooks/02_dataset_b_aosfatos_eda.ipynb`,
  Seção 3.5b).

## Limitação de desenho conhecida (leia antes de citar este modelo)

O rótulo `rotulo_grupo` é **perfeitamente colinear** com a tag de busca
usada na coleta (todo item "IA" veio da busca "inteligencia-artificial";
nenhum item de "eleicoes-2022"/"eleicoes-2026" foi rotulado IA). Isso é
consistente com o rótulo refletir o conteúdo real dos textos, mas significa
que o desempenho reportado abaixo pode incluir sinais de lote/época de
coleta, não só de tema. Uma validação mais forte exigiria rótulos IA
distribuídos por múltiplas buscas/períodos. Ver `models/README.md`.

## Busca de hiperparâmetros (conjunto de validação)

Melhor configuração encontrada via `GridSearchCV` sobre o conjunto de
validação reservado (nunca o teste): `{'clf__C': 0.1, 'tfidf__min_df': 1, 'tfidf__ngram_range': (1, 1)}`
(F1 da classe IA na validação: 1.000).

Top 5 configurações avaliadas:

- {'clf__C': 0.1, 'tfidf__min_df': 1, 'tfidf__ngram_range': [1, 1]} — F1=1.000 (rank 1)
- {'clf__C': 0.1, 'tfidf__min_df': 1, 'tfidf__ngram_range': [1, 2]} — F1=1.000 (rank 1)
- {'clf__C': 0.1, 'tfidf__min_df': 2, 'tfidf__ngram_range': [1, 1]} — F1=1.000 (rank 1)
- {'clf__C': 0.1, 'tfidf__min_df': 2, 'tfidf__ngram_range': [1, 2]} — F1=1.000 (rank 1)
- {'clf__C': 0.1, 'tfidf__min_df': 3, 'tfidf__ngram_range': [1, 1]} — F1=1.000 (rank 1)


## Robustez (validação cruzada estratificada, treino+validação)

Validação cruzada estratificada, 5 folds (seed=42):
  acuracia: 0.941 ± 0.030  (folds: [0.9259, 0.963, 0.963, 0.8889, 0.963])
  f1_ia: 0.960 ± 0.018  (folds: [0.95, 0.973, 0.9744, 0.9302, 0.9744])
  precisao_ia: 0.945 ± 0.052  (folds: [0.9048, 1.0, 0.95, 0.8696, 1.0])
  recall_ia: 0.979 ± 0.025  (folds: [1.0, 0.9474, 1.0, 1.0, 0.95])
  roc_auc: 0.997 ± 0.003  (folds: [0.9934, 1.0, 1.0, 1.0, 0.9929])

Reportado separadamente da métrica de teste (hold-out único) porque, com
só 122 itens IA no total, um único split tem variância alta — a faixa entre
folds aqui é mais defensável para citar do que um ponto único.


## Métricas no conjunto de TESTE (hold-out estratificado, nunca usado em treino/tuning/CV)

- Acurácia: 1.000
- ROC-AUC: 1.000
- Classe IA — precisão: 1.000, recall: 1.000, F1: 1.000 (n=25)
- Classe Tradicional — precisão: 1.000, recall: 1.000, F1: 1.000 (n=9)

Matriz de confusão (linhas=real, colunas=predito, ordem [Tradicional, IA]):
[[9, 0], [0, 25]]

Estas métricas usam a probabilidade CALIBRADA (ver acima) para decidir o
rótulo (limiar 0.5) — na prática, idêntico ao pipeline não-calibrado na
maioria dos casos, mas a probabilidade em si é mais confiável para
comunicar "confiança" ao usuário do Sensor de IA.

## Termos mais associados a cada classe (coeficientes do modelo linear, pipeline não-calibrado)

- IA: ia, artificial, inteligência, gerado, gerada, imagem, vídeo, imagens, indícios, gravação
- Tradicional: eleições, 2022, eleitoral, tse, urnas, eleição, votos, pleito, fraude, turno

## Comparação com outros modelos

Ver `artifacts/model_comparison.md` (gerado por
`models_pkg.training.compare_models`) para uma comparação com Naive Bayes,
SVM linear calibrado e gradient boosting sobre o mesmo TF-IDF.

## Uso responsável

- Nunca apresentar a saída deste modelo como prova de autoria por IA nem
  como veredito de veracidade.
- Sempre exibir probabilidade + confiança junto com o rótulo (ver
  `models/src/models_pkg/inference/predictor.py`).
- Reavaliar este modelo sempre que o Dataset B for atualizado com uma nova
  coleta (ver `scripts/scrape_dataset_b_completo.py` na raiz do repo).

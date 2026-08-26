# Comparação de modelos — classificador de temática de IA (v0)

Gerado por `models_pkg.training.compare_models`, validação cruzada
estratificada de 5 folds sobre treino+validação combinados
(432 itens) — o conjunto de teste usado para reportar as métricas
oficiais do v0 (`models/README.md`) NÃO entra nesta comparação, para não
"gastar" o hold-out em decisão de modelo.

Todos os candidatos usam o mesmo TF-IDF (config em `configs/ia_topic_classifier_v0.yaml`)
— a única variável isolada é o algoritmo de classificação.

| Modelo | F1 (classe IA) | ROC-AUC | Acurácia |
|---|---|---|---|
| regressao_logistica_v0 (produção atual) | 0.974 ± 0.018 | 1.000 ± 0.000 | 0.988 ± 0.007 |
| naive_bayes_multinomial | 0.735 ± 0.077 | 1.000 ± 0.000 | 0.907 ± 0.020 |
| svm_linear_calibrado | 0.974 ± 0.018 | 1.000 ± 0.000 | 0.988 ± 0.007 |
| gradient_boosting_hist | 0.979 ± 0.020 | 0.996 ± 0.007 | 0.991 ± 0.009 |

## Leitura

Com só 122 itens IA no total (ver models/README.md, Limitação 3), diferenças
pequenas entre modelos podem estar dentro do ruído de amostragem — compare o
desvio-padrão entre folds, não só a média, antes de trocar o modelo de
produção. A regressão logística foi escolhida para o v0 por ser interpretável
(permite reportar termos mais influentes por classe, usado no Sensor de IA e
no model card) e por não exigir mais dados do que temos para generalizar
razoavelmente — trocar de modelo só compensa se o ganho de desempenho for
grande o suficiente para justificar perder essa interpretabilidade nativa
(gradient boosting e SVM calibrado não expõem coeficientes lineares por termo
da mesma forma direta).

## Detalhe por modelo

### regressao_logistica_v0 (produção atual)

```
Validação cruzada estratificada, 5 folds (seed=42):
  acuracia: 0.988 ± 0.007  (folds: [0.9885, 0.9885, 0.9884, 1.0, 0.9767])
  f1_ia: 0.974 ± 0.018  (folds: [0.9744, 0.9744, 0.9744, 1.0, 0.9444])
  precisao_ia: 0.990 ± 0.020  (folds: [1.0, 1.0, 0.95, 1.0, 1.0])
  recall_ia: 0.959 ± 0.039  (folds: [0.95, 0.95, 1.0, 1.0, 0.8947])
  roc_auc: 1.000 ± 0.000  (folds: [1.0, 1.0, 1.0, 1.0, 1.0])
```

### naive_bayes_multinomial

```
Validação cruzada estratificada, 5 folds (seed=42):
  acuracia: 0.907 ± 0.020  (folds: [0.9195, 0.908, 0.907, 0.9302, 0.8721])
  f1_ia: 0.735 ± 0.077  (folds: [0.7879, 0.75, 0.7333, 0.8125, 0.5926])
  precisao_ia: 1.000 ± 0.000  (folds: [1.0, 1.0, 1.0, 1.0, 1.0])
  recall_ia: 0.587 ± 0.091  (folds: [0.65, 0.6, 0.5789, 0.6842, 0.4211])
  roc_auc: 1.000 ± 0.000  (folds: [1.0, 1.0, 1.0, 1.0, 0.9992])
```

### svm_linear_calibrado

```
Validação cruzada estratificada, 5 folds (seed=42):
  acuracia: 0.988 ± 0.007  (folds: [0.9885, 0.9885, 0.9884, 1.0, 0.9767])
  f1_ia: 0.974 ± 0.018  (folds: [0.9744, 0.9744, 0.9744, 1.0, 0.9444])
  precisao_ia: 0.990 ± 0.020  (folds: [1.0, 1.0, 0.95, 1.0, 1.0])
  recall_ia: 0.959 ± 0.039  (folds: [0.95, 0.95, 1.0, 1.0, 0.8947])
  roc_auc: 1.000 ± 0.000  (folds: [1.0, 1.0, 1.0, 1.0, 1.0])
```

### gradient_boosting_hist

```
Validação cruzada estratificada, 5 folds (seed=42):
  acuracia: 0.991 ± 0.009  (folds: [1.0, 1.0, 0.9767, 0.9884, 0.9884])
  f1_ia: 0.979 ± 0.020  (folds: [1.0, 1.0, 0.9474, 0.9744, 0.973])
  precisao_ia: 0.979 ± 0.025  (folds: [1.0, 1.0, 0.9474, 0.95, 1.0])
  recall_ia: 0.979 ± 0.026  (folds: [1.0, 1.0, 0.9474, 1.0, 0.9474])
  roc_auc: 0.996 ± 0.007  (folds: [1.0, 1.0, 0.9984, 1.0, 0.9827])
```


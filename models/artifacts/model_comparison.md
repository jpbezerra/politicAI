# Comparação de modelos — classificador de temática de IA (v0)

Gerado por `models_pkg.training.compare_models`, validação cruzada
estratificada de 5 folds sobre treino+validação combinados
(442 itens) — o conjunto de teste usado para reportar as métricas
oficiais do v0 (`models/README.md`) NÃO entra nesta comparação, para não
"gastar" o hold-out em decisão de modelo.

Todos os candidatos usam o mesmo TF-IDF (config em `configs/ia_topic_classifier_v0.yaml`)
— a única variável isolada é o algoritmo de classificação.

| Modelo | F1 (classe IA) | ROC-AUC | Acurácia |
|---|---|---|---|
| regressao_logistica_v0 (produção atual) | 0.974 ± 0.001 | 1.000 ± 0.000 | 0.989 ± 0.000 |
| naive_bayes_multinomial | 0.688 ± 0.097 | 1.000 ± 0.001 | 0.896 ± 0.026 |
| svm_linear_calibrado | 0.974 ± 0.001 | 1.000 ± 0.000 | 0.989 ± 0.000 |
| gradient_boosting_hist | 0.974 ± 0.016 | 0.997 ± 0.004 | 0.989 ± 0.007 |

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
  acuracia: 0.989 ± 0.000  (folds: [0.9888, 0.9888, 0.9886, 0.9886, 0.9886])
  f1_ia: 0.974 ± 0.001  (folds: [0.9744, 0.9744, 0.9756, 0.973, 0.973])
  precisao_ia: 0.990 ± 0.019  (folds: [1.0, 1.0, 0.9524, 1.0, 1.0])
  recall_ia: 0.959 ± 0.021  (folds: [0.95, 0.95, 1.0, 0.9474, 0.9474])
  roc_auc: 1.000 ± 0.000  (folds: [1.0, 1.0, 1.0, 1.0, 1.0])
```

### naive_bayes_multinomial

```
Validação cruzada estratificada, 5 folds (seed=42):
  acuracia: 0.896 ± 0.026  (folds: [0.8989, 0.8876, 0.8523, 0.9091, 0.9318])
  f1_ia: 0.688 ± 0.097  (folds: [0.7097, 0.6667, 0.5185, 0.7333, 0.8125])
  precisao_ia: 1.000 ± 0.000  (folds: [1.0, 1.0, 1.0, 1.0, 1.0])
  recall_ia: 0.533 ± 0.109  (folds: [0.55, 0.5, 0.35, 0.5789, 0.6842])
  roc_auc: 1.000 ± 0.001  (folds: [1.0, 0.9986, 1.0, 1.0, 1.0])
```

### svm_linear_calibrado

```
Validação cruzada estratificada, 5 folds (seed=42):
  acuracia: 0.989 ± 0.000  (folds: [0.9888, 0.9888, 0.9886, 0.9886, 0.9886])
  f1_ia: 0.974 ± 0.001  (folds: [0.9744, 0.9744, 0.9756, 0.973, 0.973])
  precisao_ia: 0.990 ± 0.019  (folds: [1.0, 1.0, 0.9524, 1.0, 1.0])
  recall_ia: 0.959 ± 0.021  (folds: [0.95, 0.95, 1.0, 0.9474, 0.9474])
  roc_auc: 1.000 ± 0.000  (folds: [1.0, 1.0, 1.0, 1.0, 1.0])
```

### gradient_boosting_hist

```
Validação cruzada estratificada, 5 folds (seed=42):
  acuracia: 0.989 ± 0.007  (folds: [0.9888, 0.9888, 0.9773, 0.9886, 1.0])
  f1_ia: 0.974 ± 0.016  (folds: [0.9744, 0.9744, 0.95, 0.973, 1.0])
  precisao_ia: 0.990 ± 0.020  (folds: [1.0, 1.0, 0.95, 1.0, 1.0])
  recall_ia: 0.959 ± 0.020  (folds: [0.95, 0.95, 0.95, 0.9474, 1.0])
  roc_auc: 0.997 ± 0.004  (folds: [0.9935, 1.0, 0.9912, 1.0, 1.0])
```


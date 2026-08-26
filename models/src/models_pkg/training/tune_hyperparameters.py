"""
Busca de hiperparâmetros do classificador de temática de IA (v0), usando o
conjunto de VALIDAÇÃO reservado por `data.loader.stratified_split` — não um
k-fold genérico.

Por quê um único split de validação em vez de k-fold aqui: o pipeline de
treino (`train_ia_topic_classifier.py`) já reserva 3 conjuntos (treino/
validação/teste); usar `PredefinedSplit` para que o GridSearchCV avalie
exatamente esse conjunto de validação (nunca o teste, que fica intocado até
a avaliação final) é mais simples de auditar do que introduzir um k-fold
adicional só para tuning, e respeita a divisão que já está documentada nos
model cards. A validação cruzada estratificada (`evaluation/cross_validation.py`)
continua sendo usada, separadamente, para reportar a robustez do modelo
final treinado com os hiperparâmetros escolhidos aqui.
"""

from __future__ import annotations

import pandas as pd
from sklearn.model_selection import GridSearchCV, PredefinedSplit
from sklearn.pipeline import Pipeline

from models_pkg.data.loader import SplitData
from models_pkg.features.text_features import build_tfidf_vectorizer

PARAM_GRID = {
    "clf__C": [0.1, 0.5, 1.0, 2.0, 5.0],
    "tfidf__ngram_range": [(1, 1), (1, 2)],
    "tfidf__min_df": [1, 2, 3],
}


def _build_base_pipeline(cfg: dict, clf) -> Pipeline:
    vectorizer = build_tfidf_vectorizer(**cfg["features"])
    return Pipeline([("tfidf", vectorizer), ("clf", clf)])


def tune_with_validation_set(
    split: SplitData, cfg: dict, clf, param_grid: dict | None = None
) -> dict:
    """Roda GridSearchCV usando um PredefinedSplit onde o treino é
    `split.X_train` e a (única) avaliação é `split.X_val`. Retorna
    `{"best_params": ..., "best_score_f1_ia": ..., "cv_results_resumo": [...]}`.
    """
    param_grid = param_grid or PARAM_GRID
    pipeline = _build_base_pipeline(cfg, clf)

    X_combinado = pd.concat([split.X_train, split.X_val]).reset_index(drop=True)
    y_combinado = pd.concat([split.y_train, split.y_val]).reset_index(drop=True)
    # -1 = sempre treino (nunca usado para pontuar), 0 = único fold de teste
    # (a validação) -- é assim que PredefinedSplit implementa "um split fixo".
    test_fold = [-1] * len(split.X_train) + [0] * len(split.X_val)
    ps = PredefinedSplit(test_fold=test_fold)

    busca = GridSearchCV(
        pipeline,
        param_grid=param_grid,
        scoring="f1",  # f1 da classe positiva (IA, y=1) -- ver data.loader
        cv=ps,
        n_jobs=1,
        refit=False,  # o refit final (em treino+val) é feito pelo script de treino
        error_score="raise",
    )
    busca.fit(X_combinado, y_combinado)

    resultados = pd.DataFrame(busca.cv_results_).sort_values("rank_test_score")
    top5 = resultados[["params", "mean_test_score", "rank_test_score"]].head(5)

    return {
        "best_params": busca.best_params_,
        "best_score_f1_ia_validacao": float(busca.best_score_),
        "top5_configuracoes": [
            {"params": {k: (list(v) if isinstance(v, tuple) else v) for k, v in row.params.items()},
             "f1_ia_validacao": round(float(row.mean_test_score), 4),
             "rank": int(row.rank_test_score)}
            for row in top5.itertuples()
        ],
    }

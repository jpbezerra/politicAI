"""
Validação cruzada estratificada para o classificador de temática de IA.

Complementa (não substitui) o hold-out de teste usado em
`training/train_ia_topic_classifier.py`: com só 122 itens IA no total, uma
única divisão treino/val/teste tem variância alta (ver models/README.md,
Limitação 3 — amostra pequena). K-fold estratificado dá uma estimativa de
desempenho com faixa de variação entre folds, mais defensável para citar
num artigo do que um único ponto de corte.

Usado tanto pelo script de treino principal (`train_ia_topic_classifier.py`,
para reportar robustez do modelo final) quanto pelo comparador de modelos
(`compare_models.py`, para colocar candidatos na mesma régua).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold, cross_validate

SCORING = {
    "acuracia": "accuracy",
    "f1_ia": "f1",
    "precisao_ia": "precision",
    "recall_ia": "recall",
    "roc_auc": "roc_auc",
}


def run_stratified_cv(
    pipeline,
    X: pd.Series,
    y: pd.Series,
    n_splits: int = 5,
    seed: int = 42,
) -> dict:
    """Roda StratifiedKFold sobre (X, y) com uma cópia não-treinada de
    `pipeline`, retornando média/desvio-padrão/valores por fold para cada
    métrica em SCORING.

    `y` deve ser binário com 1="IA" (mesma convenção usada em
    `data.loader.stratified_split`), para que os scorers `f1`/`precision`/
    `recall` do sklearn (que usam pos_label=1 por padrão) meçam a classe IA.
    """
    if n_splits > int(y.sum()):
        raise ValueError(
            f"n_splits={n_splits} maior que o número de exemplos da classe "
            f"minoritária ({int(y.sum())}) — reduza n_splits."
        )

    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    resultado = cross_validate(
        clone(pipeline), X, y, cv=cv, scoring=SCORING, n_jobs=1, error_score="raise"
    )

    resumo = {"n_splits": n_splits, "seed": seed, "metricas": {}}
    for nome in SCORING:
        valores = resultado[f"test_{nome}"]
        resumo["metricas"][nome] = {
            "media": float(np.mean(valores)),
            "desvio_padrao": float(np.std(valores)),
            "por_fold": [round(float(v), 4) for v in valores],
        }
    return resumo


def format_cv_summary(resumo: dict) -> str:
    """Formata o resumo de `run_stratified_cv` como texto legível (usado no
    model card e no relatório de comparação de modelos)."""
    linhas = [f"Validação cruzada estratificada, {resumo['n_splits']} folds (seed={resumo['seed']}):"]
    for nome, m in resumo["metricas"].items():
        linhas.append(f"  {nome}: {m['media']:.3f} ± {m['desvio_padrao']:.3f}  (folds: {m['por_fold']})")
    return "\n".join(linhas)

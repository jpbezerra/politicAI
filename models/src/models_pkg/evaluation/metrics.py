"""Métricas de avaliação do classificador de temática de IA (v0)."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)


def compute_classification_metrics(
    y_true: np.ndarray, y_pred: np.ndarray, y_proba: np.ndarray
) -> dict:
    """
    Retorna métricas por classe (não só acurácia — o dataset é desbalanceado:
    122 IA vs. 431 Tradicional, ver models/README.md).
    """
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1], zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    auc = roc_auc_score(y_true, y_proba) if len(set(y_true)) > 1 else None
    acc = float((y_true == y_pred).mean())

    return {
        "acuracia": acc,
        "roc_auc": auc,
        "por_classe": {
            "Tradicional": {
                "precisao": float(precision[0]),
                "recall": float(recall[0]),
                "f1": float(f1[0]),
                "n": int(support[0]),
            },
            "IA": {
                "precisao": float(precision[1]),
                "recall": float(recall[1]),
                "f1": float(f1[1]),
                "n": int(support[1]),
            },
        },
        "matriz_confusao": {
            "labels": ["Tradicional", "IA"],
            "valores": cm.tolist(),
            "nota": "linhas = rótulo real, colunas = predição",
        },
    }

import pandas as pd
import pytest

from models_pkg.data.loader import load_dataset_b_enriquecido, stratified_split
from models_pkg.evaluation.cross_validation import format_cv_summary, run_stratified_cv
from models_pkg.features.text_features import build_tfidf_vectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

DATASET_PATH = "../data/processed/dataset_b_aosfatos_enriquecido.csv"


@pytest.fixture(scope="module")
def split():
    df = load_dataset_b_enriquecido(DATASET_PATH)
    return stratified_split(
        df, text_columns=["titulo", "corpo_artigo"], label_column="rotulo_grupo",
        positive_label="IA", test_size=0.2, val_size=0.1, seed=42,
    )


def _pipeline():
    return Pipeline([
        ("tfidf", build_tfidf_vectorizer(max_features=2000, ngram_range=(1, 1), min_df=2)),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)),
    ])


def test_run_stratified_cv_returns_expected_keys(split):
    X_fit = pd.concat([split.X_train, split.X_val]).reset_index(drop=True)
    y_fit = pd.concat([split.y_train, split.y_val]).reset_index(drop=True)

    resumo = run_stratified_cv(_pipeline(), X_fit, y_fit, n_splits=3, seed=42)

    assert resumo["n_splits"] == 3
    for nome in ["acuracia", "f1_ia", "precisao_ia", "recall_ia", "roc_auc"]:
        assert nome in resumo["metricas"]
        assert 0.0 <= resumo["metricas"][nome]["media"] <= 1.0
        assert len(resumo["metricas"][nome]["por_fold"]) == 3


def test_run_stratified_cv_rejects_too_many_splits(split):
    X_fit = pd.concat([split.X_train, split.X_val]).reset_index(drop=True)
    y_fit = pd.concat([split.y_train, split.y_val]).reset_index(drop=True)

    with pytest.raises(ValueError):
        run_stratified_cv(_pipeline(), X_fit, y_fit, n_splits=10_000, seed=42)


def test_format_cv_summary_is_human_readable(split):
    X_fit = pd.concat([split.X_train, split.X_val]).reset_index(drop=True)
    y_fit = pd.concat([split.y_train, split.y_val]).reset_index(drop=True)
    resumo = run_stratified_cv(_pipeline(), X_fit, y_fit, n_splits=3, seed=42)

    texto = format_cv_summary(resumo)
    assert "3 folds" in texto
    assert "f1_ia" in texto

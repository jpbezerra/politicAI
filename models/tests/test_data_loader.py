from pathlib import Path

import pandas as pd
import pytest

from models_pkg.data.loader import build_text_field, stratified_split

DATASET_B_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "dataset_b_aosfatos_enriquecido.csv"
)


def _make_fake_df(n_ia: int = 20, n_tradicional: int = 40) -> pd.DataFrame:
    rows = []
    for i in range(n_ia):
        rows.append(
            {
                "titulo": f"Vídeo com deepfake número {i}",
                "corpo_artigo": "Este conteúdo foi manipulado por inteligência artificial. " * 5,
                "rotulo_grupo": "IA",
                "tag_pesquisa": "inteligencia-artificial",
            }
        )
    for i in range(n_tradicional):
        rows.append(
            {
                "titulo": f"Boato sobre urnas número {i}",
                "corpo_artigo": "As urnas eletrônicas passaram por testes de integridade. " * 5,
                "rotulo_grupo": "Tradicional",
                "tag_pesquisa": "eleicoes-2022",
            }
        )
    return pd.DataFrame(rows)


def test_build_text_field_concatenates_columns():
    df = pd.DataFrame({"titulo": ["A"], "corpo_artigo": ["B"]})
    texto = build_text_field(df, ["titulo", "corpo_artigo"])
    assert texto.iloc[0] == "A. B"


def test_build_text_field_handles_missing_values():
    df = pd.DataFrame({"titulo": ["A"], "corpo_artigo": [None]})
    texto = build_text_field(df, ["titulo", "corpo_artigo"])
    assert texto.iloc[0] == "A"


def test_stratified_split_preserves_class_balance():
    df = _make_fake_df(n_ia=20, n_tradicional=40)
    split = stratified_split(
        df,
        text_columns=["titulo", "corpo_artigo"],
        label_column="rotulo_grupo",
        positive_label="IA",
        test_size=0.2,
        val_size=0.1,
        seed=42,
    )
    total = len(split.y_train) + len(split.y_val) + len(split.y_test)
    assert total == len(df)
    # proporção de IA deve ficar próxima de 1/3 em cada partição (estratificado)
    for y in (split.y_train, split.y_val, split.y_test):
        assert 0.15 <= y.mean() <= 0.55


@pytest.mark.skipif(
    not DATASET_B_PATH.exists(), reason="Dataset B real não disponível neste ambiente"
)
def test_real_dataset_b_has_expected_shape():
    df = pd.read_csv(DATASET_B_PATH)
    assert len(df) > 0
    assert set(df["rotulo_grupo"].unique()) <= {"IA", "Tradicional"}

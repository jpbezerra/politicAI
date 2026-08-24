"""
Carregamento de dados para o classificador de temática de IA (v0).

Nota de proveniência (importante, ler antes de estender este módulo):
Somente o Dataset B (checagens do Aos Fatos) tem rótulo de IA atribuído
editorialmente por jornalistas (`rotulo_grupo`). O Dataset A tem uma coluna
`rotulo_ia`, mas ela é derivada de uma heurística de regex sobre o título
(`fonte_rotulo_ia == "heuristica_regex_titulo"`), não de julgamento
editorial — e, na amostra coletada, ela nunca marca nenhum item como IA
(0/322). Por isso, o treino deste classificador usa exclusivamente
`data/processed/dataset_b_aosfatos_enriquecido.csv`. Ver docs/PRD.md,
Seção 4.1, e models/README.md para a discussão completa.

Limitação de desenho conhecida (documentar sempre que este dataset for
usado para treino/avaliação): os 553 itens do Dataset B foram coletados a
partir de 3 buscas por tag diferentes, e o rótulo `rotulo_grupo` é
perfeitamente colinear com a tag de busca:

    tag_pesquisa               IA   Tradicional
    eleicoes-2022               0           419
    eleicoes-2026                0            12
    inteligencia-artificial   122             0

Ou seja, TODO item rotulado "IA" veio da busca por "inteligencia-artificial",
e nenhum item de "eleicoes-2022"/"eleicoes-2026" foi rotulado IA. Isso é
consistente com o rótulo refletir o conteúdo real dos artigos (quem
pesquisou uma checagem sobre IA tende a encontrar artigos sobre IA), mas
significa que o classificador não pode ser validado como robusto a
diferenças de lote/época de coleta — parte do desempenho pode refletir
convenções editoriais que mudaram ao longo do tempo, não só o tema do
texto. Ver `models/README.md`, seção "Limitações".
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from models_pkg.data.boilerplate import strip_known_boilerplate

REQUIRED_COLUMNS = ["titulo", "corpo_artigo", "rotulo_grupo", "tag_pesquisa"]


@dataclass
class SplitData:
    X_train: pd.Series
    X_val: pd.Series
    X_test: pd.Series
    y_train: pd.Series
    y_val: pd.Series
    y_test: pd.Series


def load_dataset_b_enriquecido(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset B enriquecido não encontrado em {path}. Rode antes o "
            "notebook notebooks/02_dataset_b_aosfatos_eda.ipynb (na raiz do "
            "repo) para gerá-lo, ou ajuste `data.path` em configs/*.yaml."
        )
    df = pd.read_csv(path)
    faltando = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if faltando:
        raise ValueError(f"Colunas esperadas ausentes no dataset: {faltando}")
    return df


def build_text_field(
    df: pd.DataFrame, text_columns: list[str] | None = None
) -> pd.Series:
    """Concatena título + corpo do artigo num único campo de texto para o TF-IDF.

    Colunas ausentes/nulas por linha são omitidas da concatenação em vez de
    deixar um separador ". " pendurado (ex.: "A. " quando só há título).

    `corpo_artigo` passa por `strip_known_boilerplate()` antes de entrar na
    concatenação — sem isso, um CTA de assinatura recorrente do site
    ("Siga no WhatsApp e receba nossas checagens e reportagens") aparecia
    como termo espúrio mais associado à classe IA. Ver
    `models_pkg.data.boilerplate` para o achado completo.
    """
    cols = text_columns or ["titulo", "corpo_artigo"]
    partes = []
    for c in cols:
        serie = df[c].fillna("")
        if c == "corpo_artigo":
            serie = serie.map(strip_known_boilerplate)
        partes.append(serie)

    def _juntar(valores: list[str]) -> str:
        return ". ".join(v for v in valores if v)

    texto = pd.concat(partes, axis=1).apply(lambda row: _juntar(list(row)), axis=1)
    return texto.str.strip()


def stratified_split(
    df: pd.DataFrame,
    text_columns: list[str],
    label_column: str,
    positive_label: str,
    test_size: float,
    val_size: float,
    seed: int,
) -> SplitData:
    """
    Split treino/validação/teste estratificado pelo rótulo binário.

    `val_size` é a fração do conjunto TREINO+VALIDAÇÃO (não do total) —
    ex.: test_size=0.2, val_size=0.1 produz aproximadamente 72%/8%/20%.
    """
    texto = build_text_field(df, text_columns)
    y = (df[label_column] == positive_label).astype(int)

    X_temp, X_test, y_temp, y_test = train_test_split(
        texto, y, test_size=test_size, stratify=y, random_state=seed
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_size, stratify=y_temp, random_state=seed
    )

    return SplitData(
        X_train=X_train,
        X_val=X_val,
        X_test=X_test,
        y_train=y_train,
        y_val=y_val,
        y_test=y_test,
    )

"""
Compara a regressão logística v0 com outros modelos clássicos sobre o
mesmo TF-IDF, usando validação cruzada estratificada (`evaluation.
cross_validation`) sobre treino+validação (o teste fica de fora, intocado,
igual ao resto do pipeline). Existe para dar uma justificativa com
evidência — não só conveniência — para a escolha de regressão logística
como modelo de produção do v0 (ver models/README.md e docs/PRD.md, backlog
de melhorias, item "comparação com outros modelos").

Uso (a partir de `models/`, com src/ no PYTHONPATH):
    python -m models_pkg.training.compare_models --config configs/ia_topic_classifier_v0.yaml
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

from models_pkg.data.loader import load_dataset_b_enriquecido, stratified_split
from models_pkg.evaluation.cross_validation import format_cv_summary, run_stratified_cv
from models_pkg.features.text_features import build_tfidf_vectorizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/ia_topic_classifier_v0.yaml")
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument(
        "--output", default="artifacts/model_comparison.md",
        help="Onde salvar o relatório em markdown.",
    )
    return parser.parse_args()


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_candidates(cfg: dict) -> dict[str, Pipeline]:
    """Cada candidato usa o MESMO TF-IDF (config do v0) para isolar o efeito
    do algoritmo de classificação, não do vetorizador."""
    def tfidf():
        return build_tfidf_vectorizer(**cfg["features"])

    candidatos = {
        "regressao_logistica_v0 (produção atual)": Pipeline([
            ("tfidf", tfidf()),
            ("clf", LogisticRegression(
                C=cfg["model"]["C"], class_weight=cfg["model"]["class_weight"],
                max_iter=cfg["model"]["max_iter"], random_state=cfg["seed"],
            )),
        ]),
        "naive_bayes_multinomial": Pipeline([
            ("tfidf", tfidf()),
            ("clf", MultinomialNB()),
        ]),
        "svm_linear_calibrado": Pipeline([
            ("tfidf", tfidf()),
            ("clf", CalibratedClassifierCV(
                LinearSVC(class_weight="balanced", random_state=cfg["seed"], max_iter=5000),
                method="sigmoid", cv=3,
            )),
        ]),
        "gradient_boosting_hist": Pipeline([
            ("tfidf", tfidf()),
            # HistGradientBoostingClassifier não aceita matriz esparsa
            # diretamente -- densificamos aqui (viável: poucas centenas de
            # linhas x max_features colunas, não escalaria para um corpus
            # muito maior sem trocar de estratégia).
            ("to_dense", FunctionTransformer(lambda x: x.toarray(), accept_sparse=True)),
            ("clf", HistGradientBoostingClassifier(random_state=cfg["seed"])),
        ]),
    }
    return candidatos


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)

    df = load_dataset_b_enriquecido(cfg["data"]["path"])
    split = stratified_split(
        df,
        text_columns=cfg["data"]["text_columns"],
        label_column=cfg["data"]["label_column"],
        positive_label=cfg["data"]["positive_label"],
        test_size=cfg["split"]["test_size"],
        val_size=cfg["split"]["val_size"],
        seed=cfg["seed"],
    )
    X_fit = pd.concat([split.X_train, split.X_val]).reset_index(drop=True)
    y_fit = pd.concat([split.y_train, split.y_val]).reset_index(drop=True)

    candidatos = build_candidates(cfg)
    linhas_tabela = []
    secoes_detalhe = []

    for nome, pipeline in candidatos.items():
        print(f"Rodando validação cruzada para: {nome}...")
        resumo = run_stratified_cv(pipeline, X_fit, y_fit, n_splits=args.n_splits, seed=cfg["seed"])
        f1 = resumo["metricas"]["f1_ia"]
        auc = resumo["metricas"]["roc_auc"]
        acc = resumo["metricas"]["acuracia"]
        linhas_tabela.append(
            f"| {nome} | {f1['media']:.3f} ± {f1['desvio_padrao']:.3f} "
            f"| {auc['media']:.3f} ± {auc['desvio_padrao']:.3f} "
            f"| {acc['media']:.3f} ± {acc['desvio_padrao']:.3f} |"
        )
        secoes_detalhe.append(f"### {nome}\n\n```\n{format_cv_summary(resumo)}\n```\n")

    relatorio = f"""# Comparação de modelos — classificador de temática de IA (v0)

Gerado por `models_pkg.training.compare_models`, validação cruzada
estratificada de {args.n_splits} folds sobre treino+validação combinados
({len(X_fit)} itens) — o conjunto de teste usado para reportar as métricas
oficiais do v0 (`models/README.md`) NÃO entra nesta comparação, para não
"gastar" o hold-out em decisão de modelo.

Todos os candidatos usam o mesmo TF-IDF (config em `configs/ia_topic_classifier_v0.yaml`)
— a única variável isolada é o algoritmo de classificação.

| Modelo | F1 (classe IA) | ROC-AUC | Acurácia |
|---|---|---|---|
{chr(10).join(linhas_tabela)}

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

{chr(10).join(secoes_detalhe)}
"""

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(relatorio, encoding="utf-8")
    print(f"\nRelatório salvo em {output_path}")
    print("\n" + "\n".join(linhas_tabela))


if __name__ == "__main__":
    main()

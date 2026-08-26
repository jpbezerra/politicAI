"""
Treina o baseline v0: classificador de TEMÁTICA de IA (regressão logística
sobre TF-IDF), a partir do Dataset B real (rótulo editorial do Aos Fatos).

Uso:
    python -m models_pkg.training.train_ia_topic_classifier \
        --config configs/ia_topic_classifier_v0.yaml

Roda a partir do diretório `models/` (para os caminhos relativos do YAML
resolverem certo), com `models/src` no PYTHONPATH — ver models/README.md.

O que este script NÃO faz: não treina um detector de autoria por IA (isso
exige dados que ainda não existem — ver docs/PRD.md, Seção 4.3). Ele só
resolve o problema de temática, e documenta isso no model card gerado.

Pipeline completo desta versão (ver docs/PRD.md, backlog de melhorias):
1. Split estratificado treino/val/teste (como antes).
2. Busca de hiperparâmetros usando o conjunto de VALIDAÇÃO (não o teste) —
   `training.tune_hyperparameters`.
3. Validação cruzada estratificada em treino+validação com os hiperparâmetros
   escolhidos, para reportar robustez (média ± desvio-padrão entre folds) —
   `evaluation.cross_validation`.
4. Fit final em treino+validação combinados, com os hiperparâmetros
   escolhidos no passo 2.
5. Calibração de probabilidade (`CalibratedClassifierCV`, sigmoid, 5-fold)
   treinada sobre o mesmo treino+validação — usada para a probabilidade
   reportada ao usuário; o pipeline não-calibrado continua sendo usado só
   para extrair termos mais influentes (interpretabilidade).
6. Avaliação no conjunto de TESTE (nunca visto antes deste ponto).
7. Versionamento do artefato: cada treino grava uma cópia completa e
   imutável em `artifacts/versions/<versao>_<timestamp>/`, além de
   atualizar os caminhos "latest" (`artifacts/ia_topic_classifier_v0.*`)
   usados por padrão pela API/predictor — ver `artifacts/versions/manifest.json`
   para o histórico.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from models_pkg.data.loader import load_dataset_b_enriquecido, stratified_split
from models_pkg.evaluation.cross_validation import format_cv_summary, run_stratified_cv
from models_pkg.evaluation.metrics import compute_classification_metrics
from models_pkg.features.text_features import build_tfidf_vectorizer
from models_pkg.training.tune_hyperparameters import tune_with_validation_set


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="configs/ia_topic_classifier_v0.yaml",
        help="Caminho do arquivo de configuração YAML.",
    )
    parser.add_argument(
        "--skip-tuning", action="store_true",
        help="Pula a busca de hiperparâmetros e usa os valores fixos do YAML "
             "(mais rápido; útil para iterar noutras partes do pipeline).",
    )
    parser.add_argument(
        "--cv-splits", type=int, default=5,
        help="Número de folds da validação cruzada de robustez (passo 3).",
    )
    return parser.parse_args()


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_pipeline(cfg: dict) -> Pipeline:
    vectorizer = build_tfidf_vectorizer(**cfg["features"])
    clf = LogisticRegression(
        C=cfg["model"]["C"],
        class_weight=cfg["model"]["class_weight"],
        max_iter=cfg["model"]["max_iter"],
        random_state=cfg["seed"],
    )
    return Pipeline([("tfidf", vectorizer), ("clf", clf)])


def apply_tuned_params(cfg: dict, best_params: dict) -> dict:
    """Devolve uma cópia de cfg com features/model atualizados a partir do
    dict `best_params` no formato `{"clf__C": ..., "tfidf__ngram_range": ..., "tfidf__min_df": ...}`."""
    cfg = json.loads(json.dumps(cfg))  # deep copy simples (cfg só tem tipos JSON-serializáveis)
    if "clf__C" in best_params:
        cfg["model"]["C"] = best_params["clf__C"]
    if "tfidf__ngram_range" in best_params:
        cfg["features"]["ngram_range"] = list(best_params["tfidf__ngram_range"])
    if "tfidf__min_df" in best_params:
        cfg["features"]["min_df"] = best_params["tfidf__min_df"]
    return cfg


def top_features_por_classe(pipeline: Pipeline, n: int = 15) -> dict:
    vectorizer = pipeline.named_steps["tfidf"]
    clf = pipeline.named_steps["clf"]
    termos = np.array(vectorizer.get_feature_names_out())
    coefs = clf.coef_[0]

    idx_ia = np.argsort(coefs)[-n:][::-1]
    idx_tradicional = np.argsort(coefs)[:n]

    return {
        "mais_associados_a_IA": termos[idx_ia].tolist(),
        "mais_associados_a_Tradicional": termos[idx_tradicional].tolist(),
    }


def write_model_card(
    cfg: dict, metrics: dict, top_features: dict, n_total: int,
    tuning: dict | None, cv_resumo: dict, path: Path,
) -> None:
    gerado_em = datetime.now(timezone.utc).isoformat()

    if tuning is not None:
        tuning_md = f"""## Busca de hiperparâmetros (conjunto de validação)

Melhor configuração encontrada via `GridSearchCV` sobre o conjunto de
validação reservado (nunca o teste): `{tuning['best_params']}`
(F1 da classe IA na validação: {tuning['best_score_f1_ia_validacao']:.3f}).

Top 5 configurações avaliadas:

{chr(10).join(f"- {c['params']} — F1={c['f1_ia_validacao']:.3f} (rank {c['rank']})" for c in tuning['top5_configuracoes'])}
"""
    else:
        tuning_md = (
            "## Busca de hiperparâmetros\n\nPulada nesta execução "
            "(`--skip-tuning`) — usados os valores fixos do YAML de config.\n"
        )

    cv_md = f"""## Robustez (validação cruzada estratificada, treino+validação)

{format_cv_summary(cv_resumo)}

Reportado separadamente da métrica de teste (hold-out único) porque, com
só 122 itens IA no total, um único split tem variância alta — a faixa entre
folds aqui é mais defensável para citar do que um ponto único.
"""

    conteudo = f"""# Model card — Classificador de Temática de IA (v0)

**Versão:** {cfg['artifact']['version']}
**Gerado em:** {gerado_em}
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
  ({n_total} itens, rótulo editorial real do Aos Fatos — `rotulo_grupo`).
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

{tuning_md}

{cv_md}

## Métricas no conjunto de TESTE (hold-out estratificado, nunca usado em treino/tuning/CV)

- Acurácia: {metrics['acuracia']:.3f}
- ROC-AUC: {metrics['roc_auc']:.3f}
- Classe IA — precisão: {metrics['por_classe']['IA']['precisao']:.3f}, recall: {metrics['por_classe']['IA']['recall']:.3f}, F1: {metrics['por_classe']['IA']['f1']:.3f} (n={metrics['por_classe']['IA']['n']})
- Classe Tradicional — precisão: {metrics['por_classe']['Tradicional']['precisao']:.3f}, recall: {metrics['por_classe']['Tradicional']['recall']:.3f}, F1: {metrics['por_classe']['Tradicional']['f1']:.3f} (n={metrics['por_classe']['Tradicional']['n']})

Matriz de confusão (linhas=real, colunas=predito, ordem [Tradicional, IA]):
{metrics['matriz_confusao']['valores']}

Estas métricas usam a probabilidade CALIBRADA (ver acima) para decidir o
rótulo (limiar 0.5) — na prática, idêntico ao pipeline não-calibrado na
maioria dos casos, mas a probabilidade em si é mais confiável para
comunicar "confiança" ao usuário do Sensor de IA.

## Termos mais associados a cada classe (coeficientes do modelo linear, pipeline não-calibrado)

- IA: {', '.join(top_features['mais_associados_a_IA'][:10])}
- Tradicional: {', '.join(top_features['mais_associados_a_Tradicional'][:10])}

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
"""
    path.write_text(conteudo, encoding="utf-8")


def _save_versioned_artifact(
    cfg: dict, pipeline: Pipeline, calibrado: CalibratedClassifierCV,
    metrics_full: dict, model_card_text: str, artifacts_dir: Path,
) -> str:
    """Salva uma cópia imutável do artefato desta execução em
    artifacts/versions/<versao>_<timestamp>/, atualiza o manifesto, e
    sobrescreve os caminhos "latest" (top-level) que a API/predictor usam
    por padrão. Retorna o id da versão salva."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    versao_id = f"{cfg['artifact']['version']}_{timestamp}"

    versions_dir = artifacts_dir / "versions" / versao_id
    versions_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump({"pipeline": pipeline, "calibrado": calibrado, "versao": cfg["artifact"]["version"]},
                versions_dir / "model.joblib")
    (versions_dir / "metrics.json").write_text(
        json.dumps(metrics_full, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (versions_dir / "model_card.md").write_text(model_card_text, encoding="utf-8")

    # Atualiza os caminhos "latest" usados por padrão pela API/predictor
    # (mantém compatibilidade retroativa em vez de exigir mudar configs/env)
    # ANTES de tocar o manifesto -- se o processo for interrompido aqui, o
    # manifesto ainda não menciona esta versão, então não fica referenciando
    # um "latest" que nunca foi promovido (a versão em si já está salva,
    # intacta, em versions_dir -- só não aparece no histórico até rodar de
    # novo ou ser adicionada manualmente).
    shutil.copyfile(versions_dir / "model.joblib", Path(cfg["artifact"]["output_path"]))
    shutil.copyfile(versions_dir / "metrics.json", Path(cfg["artifact"]["metrics_path"]))
    shutil.copyfile(versions_dir / "model_card.md", Path(cfg["artifact"]["model_card_path"]))

    manifest_path = artifacts_dir / "versions" / "manifest.json"
    manifesto = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    manifesto.append({
        "versao_id": versao_id,
        "versao_modelo": cfg["artifact"]["version"],
        "gerado_em": metrics_full["gerado_em"],
        "acuracia_teste": metrics_full["acuracia"],
        "f1_ia_teste": metrics_full["por_classe"]["IA"]["f1"],
        "path": str(versions_dir.relative_to(artifacts_dir)),
    })
    # Escrita atômica (arquivo temporário + rename) -- evita corromper ou
    # perder o manifesto se dois treinos rodarem ao mesmo tempo (last-writer-
    # wins ainda pode perder uma entrada nesse cenário raro, mas o arquivo
    # em si nunca fica truncado/inválido a meio de uma escrita).
    manifest_tmp = manifest_path.with_suffix(".json.tmp")
    manifest_tmp.write_text(json.dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8")
    manifest_tmp.replace(manifest_path)

    return versao_id


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

    tuning_resultado = None
    if not args.skip_tuning:
        print("Buscando hiperparâmetros no conjunto de validação...")
        base_clf = LogisticRegression(
            class_weight=cfg["model"]["class_weight"], max_iter=cfg["model"]["max_iter"],
            random_state=cfg["seed"],
        )
        tuning_resultado = tune_with_validation_set(split, cfg, base_clf)
        cfg = apply_tuned_params(cfg, tuning_resultado["best_params"])
        print(f"Melhores hiperparâmetros: {tuning_resultado['best_params']} "
              f"(F1 IA na validação: {tuning_resultado['best_score_f1_ia_validacao']:.3f})")

    X_fit = pd.concat([split.X_train, split.X_val]).reset_index(drop=True)
    y_fit = pd.concat([split.y_train, split.y_val]).reset_index(drop=True)

    pipeline = build_pipeline(cfg)

    print(f"Rodando validação cruzada de robustez ({args.cv_splits} folds)...")
    cv_resumo = run_stratified_cv(pipeline, X_fit, y_fit, n_splits=args.cv_splits, seed=cfg["seed"])
    print(format_cv_summary(cv_resumo))

    pipeline.fit(X_fit, y_fit)

    print("Calibrando probabilidade (CalibratedClassifierCV, sigmoid, 5-fold)...")
    calibrado = CalibratedClassifierCV(clone(pipeline), method="sigmoid", cv=5)
    calibrado.fit(X_fit, y_fit)

    y_pred = calibrado.predict(split.X_test)
    y_proba = calibrado.predict_proba(split.X_test)[:, 1]
    metrics = compute_classification_metrics(split.y_test.to_numpy(), y_pred, y_proba)
    top_features = top_features_por_classe(pipeline)

    metrics_full = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "versao_modelo": cfg["artifact"]["version"],
        "n_treino": int(len(X_fit)),
        "n_teste": int(len(split.X_test)),
        "hiperparametros_finais": {
            "C": cfg["model"]["C"], "ngram_range": cfg["features"]["ngram_range"],
            "min_df": cfg["features"]["min_df"],
        },
        "tuning": tuning_resultado,
        "validacao_cruzada": cv_resumo,
        **metrics,
        "top_features": top_features,
    }

    artifacts_dir = Path(cfg["artifact"]["output_path"]).parent
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    model_card_path = Path(cfg["artifact"]["model_card_path"])
    write_model_card(cfg, metrics, top_features, len(df), tuning_resultado, cv_resumo, model_card_path)
    model_card_text = model_card_path.read_text(encoding="utf-8")

    versao_id = _save_versioned_artifact(
        cfg, pipeline, calibrado, metrics_full, model_card_text, artifacts_dir,
    )

    print(f"\nVersão salva: {versao_id}")
    print(f"Modelo (latest) salvo em {cfg['artifact']['output_path']}")
    print(f"Métricas (latest) salvas em {cfg['artifact']['metrics_path']}")
    print(f"Model card (latest) salvo em {cfg['artifact']['model_card_path']}")
    print(f"Histórico de versões em {artifacts_dir / 'versions' / 'manifest.json'}")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

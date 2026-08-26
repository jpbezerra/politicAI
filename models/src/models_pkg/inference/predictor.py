"""Camada de inferência do classificador de temática de IA (v0)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np


@dataclass
class Predicao:
    rotulo: str  # "IA" | "Tradicional"
    probabilidade: float  # probabilidade da classe "IA"
    confianca: str  # "baixa" | "media" | "alta"
    termos_influentes: list[str]
    modelo_versao: str


def _bucket_confianca(probabilidade: float) -> str:
    """Confiança baseada na distância da predição a 0.5 — ainda uma
    heurística de bucketing (baixa/média/alta), mas agora aplicada sobre uma
    probabilidade CALIBRADA (`CalibratedClassifierCV`, ver `IATopicPredictor`),
    não mais a saída bruta e não-calibrada do classificador linear."""
    distancia = abs(probabilidade - 0.5)
    if distancia >= 0.4:
        return "alta"
    if distancia >= 0.2:
        return "media"
    return "baixa"


class IATopicPredictor:
    """Carrega o artefato treinado por
    `models_pkg.training.train_ia_topic_classifier` e serve predições.

    A partir da versão com calibração de probabilidade, o artefato também
    inclui um wrapper `CalibratedClassifierCV` ("calibrado") treinado sobre
    o mesmo treino+validação do pipeline principal. Quando presente, é ele
    quem decide rótulo/probabilidade (mais confiável para comunicar
    "confiança" ao usuário); o pipeline não-calibrado continua sendo usado
    só para os termos mais influentes (interpretabilidade, que o wrapper de
    calibração não expõe da mesma forma direta). Artefatos antigos sem essa
    chave continuam funcionando — cai de volta para o pipeline simples.
    """

    def __init__(self, pipeline, versao: str, calibrado=None):
        self._pipeline = pipeline
        self._versao = versao
        self._calibrado = calibrado

    @classmethod
    def load(cls, artifact_path: str | Path) -> "IATopicPredictor":
        artifact_path = Path(artifact_path)
        if not artifact_path.exists():
            raise FileNotFoundError(
                f"Artefato do modelo não encontrado em {artifact_path}. "
                "Rode antes: python -m models_pkg.training.train_ia_topic_classifier "
                "(a partir do diretório models/, com src/ no PYTHONPATH)."
            )
        payload = joblib.load(artifact_path)
        return cls(
            pipeline=payload["pipeline"],
            versao=payload["versao"],
            calibrado=payload.get("calibrado"),
        )

    def _termos_influentes(self, texto: str, top_n: int = 6) -> list[str]:
        vectorizer = self._pipeline.named_steps["tfidf"]
        clf = self._pipeline.named_steps["clf"]

        vetor = vectorizer.transform([texto])
        termos = np.array(vectorizer.get_feature_names_out())
        coefs = clf.coef_[0]

        # contribuição = valor tf-idf do termo no texto * peso do modelo
        contribuicoes = np.asarray(vetor.todense()).ravel() * coefs
        presentes = np.where(vetor.todense().A1 > 0)[0]
        if len(presentes) == 0:
            return []

        top_idx = presentes[np.argsort(np.abs(contribuicoes[presentes]))[-top_n:]][::-1]
        return termos[top_idx].tolist()

    def predict(self, texto: str) -> Predicao:
        estimador_proba = self._calibrado if self._calibrado is not None else self._pipeline
        probabilidade = float(estimador_proba.predict_proba([texto])[0, 1])
        rotulo = "IA" if probabilidade >= 0.5 else "Tradicional"
        return Predicao(
            rotulo=rotulo,
            probabilidade=probabilidade,
            confianca=_bucket_confianca(probabilidade),
            termos_influentes=self._termos_influentes(texto),
            modelo_versao=self._versao,
        )

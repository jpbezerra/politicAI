from pathlib import Path

import pytest

from models_pkg.inference.predictor import IATopicPredictor

ARTIFACT_PATH = (
    Path(__file__).resolve().parents[1] / "artifacts" / "ia_topic_classifier_v0.joblib"
)


@pytest.mark.skipif(
    not ARTIFACT_PATH.exists(),
    reason="Artefato do modelo não treinado neste ambiente — rode "
    "models_pkg.training.train_ia_topic_classifier primeiro",
)
class TestIATopicPredictor:
    @pytest.fixture(scope="class")
    def predictor(self):
        return IATopicPredictor.load(ARTIFACT_PATH)

    def test_predicts_ia_for_clear_ia_text(self, predictor):
        texto = (
            "Um vídeo manipulado por inteligência artificial (deepfake) mostra "
            "o candidato fazendo declarações que ele nunca fez, segundo checagem."
        )
        pred = predictor.predict(texto)
        assert pred.rotulo in ("IA", "Tradicional")
        assert 0.0 <= pred.probabilidade <= 1.0
        assert pred.confianca in ("baixa", "media", "alta")

    def test_predicts_tradicional_for_clear_non_ia_text(self, predictor):
        texto = (
            "O TSE informou que as urnas eletrônicas passaram por testes de "
            "integridade e segurança antes do primeiro turno das eleições."
        )
        pred = predictor.predict(texto)
        assert pred.rotulo == "Tradicional"

    def test_termos_influentes_nonempty_for_known_text(self, predictor):
        pred = predictor.predict(
            "Este texto fala sobre inteligência artificial e deepfakes na política."
        )
        assert len(pred.termos_influentes) > 0

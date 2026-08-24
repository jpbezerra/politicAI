"""
Testes de contrato da API FastAPI (`api/main.py`) — usam o artefato real já
treinado em `artifacts/` (não fazem mock do modelo), então precisam ser
rodados depois de `train_ia_topic_classifier` ter gerado o artefato pelo
menos uma vez (é o fluxo normal de desenvolvimento, ver models/README.md).
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_predict_ia_topic_rejects_short_text():
    resp = client.post("/predict/ia-topic", json={"texto": "curto"})
    assert resp.status_code == 422


def test_predict_ia_topic_returns_expected_shape():
    texto = (
        "Um vídeo manipulado por inteligência artificial mostra um "
        "político dizendo frases que nunca disse, segundo especialistas em "
        "checagem de fatos que analisaram o conteúdo."
    )
    resp = client.post("/predict/ia-topic", json={"texto": texto})
    assert resp.status_code == 200
    body = resp.json()
    for campo in ["rotulo", "probabilidade", "confianca", "termos_influentes", "modelo_versao"]:
        assert campo in body
    assert body["rotulo"] in {"IA", "Tradicional"}
    assert 0.0 <= body["probabilidade"] <= 1.0


def test_predict_ia_topic_does_not_log_without_consent(tmp_path, monkeypatch):
    import api.main as main_module

    log_path = tmp_path / "consentimento_log.jsonl"
    monkeypatch.setattr(main_module, "CONSENTIMENTO_LOG_PATH", log_path)

    texto = "Texto qualquer, longo o suficiente para passar da validação mínima de vinte caracteres."
    resp = client.post("/predict/ia-topic", json={"texto": texto})
    assert resp.status_code == 200
    assert not log_path.exists()


def test_predict_ia_topic_logs_with_explicit_consent(tmp_path, monkeypatch):
    import api.main as main_module

    log_path = tmp_path / "consentimento_log.jsonl"
    monkeypatch.setattr(main_module, "CONSENTIMENTO_LOG_PATH", log_path)

    texto = "Texto qualquer, longo o suficiente para passar da validação mínima de vinte caracteres."
    resp = client.post(
        "/predict/ia-topic", json={"texto": texto, "permitir_uso_para_pesquisa": True}
    )
    assert resp.status_code == 200
    assert log_path.exists()
    linhas = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(linhas) == 1
    assert texto in linhas[0]


def test_predict_ia_topic_batch():
    resp = client.post(
        "/predict/ia-topic/batch",
        json={"textos": [
            "Um vídeo com inteligência artificial mostra um político falando algo que nunca disse.",
            "curto",
        ]},
    )
    assert resp.status_code == 200
    resultados = resp.json()["resultados"]
    assert len(resultados) == 2
    assert "rotulo" in resultados[0]
    assert "erro" in resultados[1]


def test_predict_ia_topic_batch_rejects_empty_list():
    resp = client.post("/predict/ia-topic/batch", json={"textos": []})
    assert resp.status_code == 422


def test_predict_ia_topic_batch_rejects_oversized_item():
    # Regressão: TextoLoteRequest.textos limitava só a QUANTIDADE de itens
    # (max_length=TAMANHO_MAX_LOTE), não o tamanho de cada item -- um único
    # texto gigante no lote passava direto para o classificador, ao
    # contrário do endpoint individual (que rejeita com 422 acima de 20000
    # caracteres). Corrigido com um field_validator por item.
    texto_gigante = "a" * 20001
    resp = client.post(
        "/predict/ia-topic/batch",
        json={"textos": ["Texto normal, com tamanho razoável para passar a validação.", texto_gigante]},
    )
    assert resp.status_code == 422


def test_predict_ia_authorship_returns_501():
    resp = client.post("/predict/ia-authorship")
    assert resp.status_code == 501


def test_forecast_index_includes_metodo():
    resp = client.get("/forecast/index?periods=3")
    assert resp.status_code in (200, 422, 503)
    if resp.status_code == 200:
        body = resp.json()
        assert "metodo" in body
        assert body["metodo"] in {"binomial_negativa", "poisson", "regressao_linear"}


def test_forecast_index_inclui_contexto_de_calendario_eleitoral():
    # RF2.4 (docs/PRD.md, Seção 5.2/15) -- o endpoint precisa carregar o
    # contexto de calendário eleitoral, não só a série/projeção em si.
    resp = client.get("/forecast/index?periods=6")
    assert resp.status_code in (200, 422, 503)
    if resp.status_code != 200:
        return
    body = resp.json()
    assert "calendario_disponivel" in body
    assert "marcos_eleitorais" in body
    assert isinstance(body["marcos_eleitorais"], list)
    for ponto in body["pontos"]:
        assert "mes_de_1_turno" in ponto
        assert "dias_para_1_turno_mais_proximo" in ponto
    if body["calendario_disponivel"]:
        for marco in body["marcos_eleitorais"]:
            assert set(marco.keys()) == {"ano", "data_1_turno", "mes"}

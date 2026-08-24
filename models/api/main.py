"""
Serviço de inferência do /models (FastAPI). Consumido pelo `/web` (ver
`web/src/lib/models-client.ts`) e utilizável de forma independente.

Rodar (a partir de `models/`, com o venv ativado):
    uvicorn api.main:app --reload --port 8000
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from models_pkg.forecasting.trend_index import compute_trend_index
from models_pkg.inference.predictor import IATopicPredictor

MODELS_DIR = Path(__file__).resolve().parent.parent
DEFAULT_ARTIFACT = MODELS_DIR / "artifacts" / "ia_topic_classifier_v0.joblib"
DEFAULT_DATASET_C = MODELS_DIR.parent / "data" / "processed" / "dataset_c_unificado.csv"
CONSENTIMENTO_LOG_PATH = MODELS_DIR / "data" / "consentimento_log.jsonl"
TAMANHO_MAX_LOTE = 50

app = FastAPI(
    title="politicAI — Motor de ML",
    description=(
        "Classificador de temática de IA (v0) e índice de tendência de "
        "desinformação por IA. Ver ../docs/PRD.md para o escopo completo."
    ),
    version="0.1.0",
)

# Rate limiting básico (defesa contra abuso simples, não uma solução de
# produção completa — sem autenticação, chave por IP de origem via
# slowapi/get_remote_address). Ver docs/PRD.md, backlog de melhorias.
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("WEB_ORIGIN", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextoRequest(BaseModel):
    texto: str = Field(..., min_length=1, max_length=20000)
    permitir_uso_para_pesquisa: bool = Field(
        default=False,
        description=(
            "Se true, o texto e a predição são registrados (opt-in, "
            "explícito, não marcado por padrão) em um log local separado "
            "de qualquer dado de treino — ver CONSENTIMENTO_LOG_PATH. "
            "Serve como material bruto para uma futura curadoria de corpus "
            "do detector de autoria v1 (docs/PRD.md, Seção 5.3); NUNCA é "
            "usado para treinar o modelo v0 automaticamente."
        ),
    )


class TextoLoteRequest(BaseModel):
    # Cada item usa o mesmo limite de tamanho do endpoint individual
    # (TextoRequest.texto) -- sem isso, um único item gigante no lote
    # passaria pela validação de tamanho da lista (que só limita a
    # QUANTIDADE de itens) e chegaria inteiro ao vetorizador/classificador,
    # um vetor de exaustão de recursos que o endpoint individual já bloqueia.
    textos: list[str] = Field(
        ..., min_length=1, max_length=TAMANHO_MAX_LOTE
    )

    @field_validator("textos")
    @classmethod
    def _valida_tamanho_de_cada_texto(cls, textos: list[str]) -> list[str]:
        for i, texto in enumerate(textos):
            if not (1 <= len(texto) <= 20000):
                raise ValueError(
                    f"textos[{i}] deve ter entre 1 e 20000 caracteres (tem {len(texto)})."
                )
        return textos


def _registrar_consentimento(texto: str, pred) -> None:
    """Acrescenta uma linha JSONL com o texto e a predição, só quando o
    usuário marcou opt-in explicitamente. Nunca é lido pelo pipeline de
    treino automaticamente — é matéria-prima para uma curadoria manual
    futura (ver docs/PRD.md, Seção 5.3, roadmap do detector de autoria)."""
    CONSENTIMENTO_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "texto": texto,
        "rotulo": pred.rotulo,
        "probabilidade": pred.probabilidade,
        "modelo_versao": pred.modelo_versao,
    }
    with open(CONSENTIMENTO_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


@lru_cache(maxsize=1)
def get_predictor() -> IATopicPredictor:
    return IATopicPredictor.load(
        os.environ.get("IA_TOPIC_MODEL_PATH", str(DEFAULT_ARTIFACT))
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict/ia-topic")
@limiter.limit("30/minute")
def predict_ia_topic(request: Request, req: TextoRequest) -> dict:
    """Classificador de TEMÁTICA de IA (v0) — ver models/README.md."""
    if len(req.texto.strip()) < 20:
        raise HTTPException(422, "Texto muito curto para análise (mínimo 20 caracteres).")

    try:
        predictor = get_predictor()
    except FileNotFoundError as e:
        raise HTTPException(503, str(e)) from e

    pred = predictor.predict(req.texto)
    if req.permitir_uso_para_pesquisa:
        _registrar_consentimento(req.texto, pred)
    return {
        "rotulo": pred.rotulo,
        "probabilidade": pred.probabilidade,
        "confianca": pred.confianca,
        "termos_influentes": pred.termos_influentes,
        "modelo_versao": pred.modelo_versao,
    }


@app.post("/predict/ia-topic/batch")
@limiter.limit("10/minute")
def predict_ia_topic_batch(request: Request, req: TextoLoteRequest) -> dict:
    """Versão em lote de `/predict/ia-topic`, até {} textos por chamada.

    Não registra consentimento/log (opt-in não se aplica ao endpoint em
    lote nesta v0) — pensado para uso interno/análise, não para o Sensor
    de IA da interface, que usa `/predict/ia-topic`.
    """.format(TAMANHO_MAX_LOTE)
    try:
        predictor = get_predictor()
    except FileNotFoundError as e:
        raise HTTPException(503, str(e)) from e

    resultados = []
    for texto in req.textos:
        if len(texto.strip()) < 20:
            resultados.append({"erro": "Texto muito curto para análise (mínimo 20 caracteres)."})
            continue
        pred = predictor.predict(texto)
        resultados.append({
            "rotulo": pred.rotulo,
            "probabilidade": pred.probabilidade,
            "confianca": pred.confianca,
            "termos_influentes": pred.termos_influentes,
            "modelo_versao": pred.modelo_versao,
        })
    return {"resultados": resultados}


@app.post("/predict/ia-authorship")
@limiter.limit("30/minute")
def predict_ia_authorship(request: Request) -> dict:
    """
    Detector de AUTORIA por IA (v1) — ainda não implementado.

    Não existe, neste repositório, um corpus rotulado texto-humano vs.
    texto-gerado-por-IA sobre temas políticos brasileiros. Implementar este
    endpoint com um modelo "de fachada" (ex.: reaproveitar o classificador
    de temática) daria uma falsa sensação de capacidade — por isso ele
    retorna 501 de propósito. Ver docs/PRD.md, Seção 4.3.
    """
    raise HTTPException(
        501,
        "Detector de autoria por IA ainda não implementado — requer coleta de "
        "dados nova (ver docs/PRD.md, Seção 4.3, roadmap v1). Use "
        "/predict/ia-topic para o classificador de temática (v0) disponível.",
    )


@app.get("/forecast/index")
@limiter.limit("30/minute")
def forecast_index(request: Request, periods: int = 6) -> dict:
    """Índice de tendência de desinformação por IA (v0) — ver
    models_pkg.forecasting.trend_index para as limitações."""
    if not DEFAULT_DATASET_C.exists():
        raise HTTPException(
            503,
            f"Dataset C não encontrado em {DEFAULT_DATASET_C}. Rode o "
            "notebook notebooks/03_dataset_c_unificado_eda.ipynb (raiz do repo) "
            "para gerá-lo.",
        )

    df = pd.read_csv(DEFAULT_DATASET_C)
    indice = compute_trend_index(df, forecast_periods=periods)

    if not indice.pontos:
        raise HTTPException(
            422,
            f"Dados insuficientes para calcular o índice (mínimo de observações "
            f"mensais não atingido; {indice.n_observacoes} meses disponíveis).",
        )

    return {
        "aviso": indice.aviso,
        "n_observacoes": indice.n_observacoes,
        "metodo": indice.metodo,
        # RF2.4 — contextualização com calendário eleitoral (docs/PRD.md,
        # Seção 5.2 e Seção 15, achado 1). `calendario_disponivel=False`
        # só ocorre se `scripts/election_calendar.py` não puder ser
        # importado (ver trend_index.py) — nunca uma data inventada.
        "calendario_disponivel": indice.calendario_disponivel,
        "marcos_eleitorais": indice.marcos_eleitorais,
        "pontos": [
            {
                "mes": p.mes,
                "volume_ia": p.volume_ia,
                "volume_ia_projetado": p.volume_ia_projetado,
                "limite_inferior": p.limite_inferior,
                "limite_superior": p.limite_superior,
                "mes_de_1_turno": p.mes_de_1_turno,
                "dias_para_1_turno_mais_proximo": p.dias_para_1_turno_mais_proximo,
            }
            for p in indice.pontos
        ],
    }

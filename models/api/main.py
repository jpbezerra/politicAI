"""
Serviço de inferência do `/models` (FastAPI) — expõe, via HTTP, o
classificador de temática de IA (v0) e o índice de tendência de
desinformação por IA descritos em `../docs/PRD.md`, Seções 5.1 e 5.2.
Consumido pelo `/web` (ver `web/src/lib/models-client.ts`), mas utilizável
de forma independente por qualquer cliente HTTP — inclusive via a própria
UI interativa gerada automaticamente pelo FastAPI em `/docs` (Swagger UI)
e `/redoc` (ReDoc), que documentam cada endpoint, seus parâmetros, formas
de resposta e códigos de erro possíveis a partir do conteúdo deste
arquivo (docstrings, `response_model`, `responses=`, `tags=`).

Rodar localmente (a partir de `models/`, com o venv ativado):
    uvicorn api.main:app --reload --port 8000

Em produção (ex.: Render — ver `docs/PRD.md`, Seção 17): o Build Command
precisa ser `pip install -e .` (editável — sem isso, RF2.4/calendário
eleitoral do `/forecast/index` para de funcionar silenciosamente, ver
`models_pkg/forecasting/trend_index.py`) e o Start Command
`uvicorn api.main:app --host 0.0.0.0 --port $PORT`.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Literal

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
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
TAMANHO_MAX_TEXTO = 20000
TAMANHO_MIN_TEXTO = 20

# Metadados dos grupos de endpoints exibidos em /docs — cada `name` aqui
# precisa bater exatamente com o `tags=[...]` usado nos decorators das
# rotas abaixo, senão o Swagger UI cria um grupo "sem descrição" separado.
TAGS_METADATA = [
    {
        "name": "Sistema",
        "description": "Checagem de disponibilidade do serviço. Sem rate limiting.",
    },
    {
        "name": "Classificação de temática (Sensor de IA)",
        "description": (
            "Classificador de TEMÁTICA de IA (v0) — dado um texto, estima se ele "
            "é *sobre* desinformação envolvendo IA (deepfake, áudio clonado, "
            "texto sintético), não se o próprio texto *foi gerado* por IA. Essa "
            "distinção (Problema A vs. Problema B, docs/PRD.md Seção 5.1) é o "
            "limite mais importante desta API — reforçado em cada resposta via "
            "`confianca` (nunca um veredito binário) e na documentação de cada "
            "endpoint abaixo. Alimenta o \"Sensor de IA\" do `/web` "
            "(`/sensor`, via proxy `POST /api/sensor-ia`)."
        ),
    },
    {
        "name": "Detector de autoria (v1, roadmap)",
        "description": (
            "Reservado para a v1 (detector de AUTORIA por IA — texto-humano "
            "vs. texto-gerado-por-IA). Não implementado nesta versão por falta "
            "de corpus rotulado (docs/PRD.md, Seção 5.3) — o único endpoint "
            "deste grupo retorna sempre `501 Not Implemented`, de propósito, em "
            "vez de simular uma capacidade que não existe."
        ),
    },
    {
        "name": "Índice de tendência",
        "description": (
            "Índice de tendência/atenção de desinformação por IA (RF2.1-RF2.5, "
            "docs/PRD.md Seção 5.2) — volume mensal real (Dataset B) com "
            "projeção de curto prazo e contexto de calendário eleitoral "
            "(RF2.4). **Não é uma previsão validada de impacto eleitoral** — "
            "ver o campo `aviso` em toda resposta, e a docstring completa de "
            "`models_pkg.forecasting.trend_index` para a justificativa "
            "estatística (Binomial Negativa/Poisson/regressão linear) e as "
            "limitações de amostra."
        ),
    },
]

app = FastAPI(
    title="politicAI — Motor de ML",
    summary="Classificador de temática de IA e índice de tendência de desinformação por IA.",
    description="""
Serviço de inferência do projeto **politicAI** (ver `../docs/PRD.md` para o
escopo completo do projeto, incluindo `/web`, os datasets e a metodologia).

## O que este serviço É

- Um classificador de **temática** de IA (v0): estima se um texto político é
  *sobre* desinformação envolvendo IA — treinado com 553 itens reais do
  Dataset B (checagens editoriais do Aos Fatos), F1 da classe IA de
  0.974 ± 0.018 em validação cruzada (ver `models/README.md`).
- Um índice **exploratório** de tendência/atenção de desinformação por IA,
  com projeção de curto prazo (GLM Binomial Negativa/Poisson, com fallback
  para regressão linear) e contexto de calendário eleitoral.

## O que este serviço NÃO É

- **Não** é um detector de **autoria** por IA (não distingue texto
  escrito por humano de texto gerado por um modelo de linguagem) — essa é
  a v1, roadmapeada, bloqueada por falta de corpus rotulado
  (`docs/PRD.md`, Seção 5.3). `POST /predict/ia-authorship` existe só para
  deixar isso explícito via `501`, nunca simulando essa capacidade.
- **Não** é uma previsão validada de resultado eleitoral. O índice de
  tendência é uma extrapolação estatística simples e auditável de uma
  amostra pequena (122 itens IA no total) e concentrada numa única fonte
  editorial — nunca deve ser lido como "impacto eleitoral previsto".

## Como usar esta documentação

Cada endpoint abaixo lista, além da descrição, os parâmetros esperados, o
formato exato da resposta de sucesso (com exemplo) e os códigos de erro
possíveis com o que cada um significa. O botão **"Try it out"** do Swagger
UI permite testar qualquer endpoint direto do navegador, inclusive contra
este próprio deploy.

## Rate limiting e CORS

Todos os endpoints de predição/previsão têm rate limiting básico por IP de
origem (`slowapi` — ver o limite específico na descrição de cada um; sem
autenticação, não é uma solução de produção completa). CORS é controlado
pela variável de ambiente `WEB_ORIGIN` (lista separada por vírgula de
origens permitidas; padrão `http://localhost:3000` para desenvolvimento
local) — na arquitetura atual isso raramente é acionado na prática, porque
o `/web` sempre chama esta API do lado do servidor (nunca direto do
navegador do usuário final).
""",
    version="0.1.0",
    openapi_tags=TAGS_METADATA,
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


# ---------------------------------------------------------------------------
# Modelos de request/response — cada um vira, automaticamente, um schema
# documentado em /docs (aba "Schemas" no fim da página, e expandido inline
# em cada endpoint que o usa), com tipos, descrições e exemplo.
# ---------------------------------------------------------------------------


class TextoRequest(BaseModel):
    texto: str = Field(
        ...,
        min_length=1,
        max_length=TAMANHO_MAX_TEXTO,
        description=(
            f"Texto a classificar (notícia, post, transcrição). Mínimo "
            f"efetivo de {TAMANHO_MIN_TEXTO} caracteres após remover espaços "
            f"nas pontas — abaixo disso o endpoint responde 422, mesmo que "
            f"passe da validação de tamanho do Pydantic (que só garante "
            f"pelo menos 1 caractere). Máximo de {TAMANHO_MAX_TEXTO} "
            f"caracteres."
        ),
        examples=[
            "Circula nas redes um vídeo em que o candidato aparece fazendo "
            "uma declaração que ele nunca fez — especialistas apontam sinais "
            "de manipulação por inteligência artificial (deepfake).",
        ],
    )
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
        ...,
        min_length=1,
        max_length=TAMANHO_MAX_LOTE,
        description=(
            f"Lista de textos a classificar, um a um, na mesma ordem da "
            f"resposta. Entre 1 e {TAMANHO_MAX_LOTE} itens; cada item "
            f"individualmente precisa ter entre 1 e {TAMANHO_MAX_TEXTO} "
            f"caracteres (mesmo limite do endpoint individual, aplicado por "
            f"item via validador — não é só um limite de tamanho da lista)."
        ),
        examples=[
            [
                "Vídeo mostra suposta fala do candidato que especialistas "
                "apontam como manipulada por IA.",
                "Nota oficial da campanha nega qualquer irregularidade nas "
                "urnas eletrônicas utilizadas no pleito.",
            ],
        ],
    )

    @field_validator("textos")
    @classmethod
    def _valida_tamanho_de_cada_texto(cls, textos: list[str]) -> list[str]:
        for i, texto in enumerate(textos):
            if not (1 <= len(texto) <= TAMANHO_MAX_TEXTO):
                raise ValueError(
                    f"textos[{i}] deve ter entre 1 e {TAMANHO_MAX_TEXTO} "
                    f"caracteres (tem {len(texto)})."
                )
        return textos


class PredicaoResponse(BaseModel):
    """Resultado do classificador de temática de IA (v0) para um único texto."""

    rotulo: Literal["IA", "Tradicional"] = Field(
        ...,
        description=(
            '"IA" se o texto for classificado como relacionado à temática de '
            'desinformação por IA; "Tradicional" caso contrário. **Não é um '
            "veredito de autoria** — um texto \"Tradicional\" pode ter sido "
            "gerado por um modelo de linguagem sobre um tema comum, e o "
            "classificador não teria como saber (ver Seção 5.1 do PRD)."
        ),
    )
    probabilidade: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Probabilidade calibrada (`CalibratedClassifierCV`, sigmoid) da "
            'classe "IA", entre 0 e 1. `rotulo` é derivado dela com corte em '
            "0.5 — não uma saída separada e potencialmente inconsistente."
        ),
    )
    confianca: Literal["baixa", "media", "alta"] = Field(
        ...,
        description=(
            "Faixa qualitativa de confiança, derivada da distância de "
            "`probabilidade` até 0.5 (quanto mais perto de 0 ou 1, maior a "
            "confiança). Pensada para comunicar incerteza na UI sem expor "
            "um número de probabilidade cru sem contexto."
        ),
    )
    termos_influentes: list[str] = Field(
        ...,
        description=(
            "Até 6 termos (unigramas/bigramas do TF-IDF) que mais pesaram "
            "na predição deste texto específico, na direção da classe "
            "prevista — explicabilidade mínima (RF1.5), não uma explicação "
            "causal completa do modelo."
        ),
    )
    modelo_versao: str = Field(
        ...,
        description=(
            "Identificador da versão do artefato treinado que gerou esta "
            "predição (ver `models/artifacts/versions/manifest.json`) — "
            "útil para reproduzir ou auditar uma predição específica depois "
            "de um retreino."
        ),
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "rotulo": "IA",
                "probabilidade": 0.91,
                "confianca": "alta",
                "termos_influentes": ["deepfake", "manipulado", "inteligência artificial"],
                "modelo_versao": "v0-topic-2026.08",
            }
        }
    }


class PredicaoLoteItemResponse(BaseModel):
    """Um item do lote — ou os campos de predição normais, ou só `erro`
    (nunca os dois), dependendo de o texto ter passado da validação mínima
    de tamanho. Ver `PredicaoResponse` para o significado de cada campo de
    predição."""

    rotulo: Literal["IA", "Tradicional"] | None = None
    probabilidade: float | None = Field(default=None, ge=0.0, le=1.0)
    confianca: Literal["baixa", "media", "alta"] | None = None
    termos_influentes: list[str] | None = None
    modelo_versao: str | None = None
    erro: str | None = Field(
        default=None,
        description=(
            f"Presente só quando o item correspondente tinha menos de "
            f"{TAMANHO_MIN_TEXTO} caracteres úteis — os demais campos ficam "
            f"`null` nesse caso. Um item inválido não invalida o lote "
            f"inteiro; os outros itens continuam sendo classificados "
            f"normalmente."
        ),
    )


class PredicaoLoteResponse(BaseModel):
    resultados: list[PredicaoLoteItemResponse] = Field(
        ...,
        description="Um resultado por texto de entrada, na mesma ordem de `textos`.",
    )


class HealthResponse(BaseModel):
    status: Literal["ok"]


class MarcoEleitoralResponse(BaseModel):
    """Um 1º turno eleitoral cuja data cai dentro do período coberto pelos
    `pontos` da resposta de `/forecast/index` — fonte única de datas em
    `scripts/election_calendar.py` (mesma usada pelos notebooks)."""

    ano: int = Field(..., description="Ano do ciclo eleitoral (ex.: 2022, 2026).")
    data_1_turno: str = Field(..., description='Data do 1º turno, formato "YYYY-MM-DD".')
    mes: str = Field(
        ...,
        description=(
            'Mês do 1º turno no mesmo formato "YYYY-MM" usado em `pontos[].mes` — '
            "use este campo para casar o marco com o ponto correspondente da série."
        ),
    )


class PontoIndiceResponse(BaseModel):
    """Um mês da série do índice de tendência — observado (`volume_ia`
    preenchido) ou projetado (`volume_ia_projetado`/`limite_*` preenchidos),
    nunca os dois ao mesmo tempo."""

    mes: str = Field(..., description='Mês no formato "YYYY-MM".')
    volume_ia: float | None = Field(
        default=None,
        description=(
            "Volume ABSOLUTO real de checagens rotuladas IA nesse mês "
            "(Dataset B, rótulo editorial) — `null` nos meses projetados. "
            "Não é uma proporção do total de checagens do mês (ver "
            "docs/PRD.md, Seção 10.2, sobre por que essa normalização foi "
            "descartada)."
        ),
    )
    volume_ia_projetado: float | None = Field(
        default=None,
        description="Média projetada pelo modelo (ver `metodo`) — `null` nos meses observados.",
    )
    limite_inferior: float | None = Field(
        default=None,
        description=(
            "Limite inferior do intervalo de confiança de 95% da média "
            "projetada — não um intervalo preditivo para a contagem de um "
            "mês específico (que seria mais largo). `null` nos meses observados."
        ),
    )
    limite_superior: float | None = Field(
        default=None,
        description="Limite superior do mesmo intervalo de confiança de 95%. `null` nos meses observados.",
    )
    mes_de_1_turno: bool = Field(
        ...,
        description=(
            "RF2.4 — true se este mês contém a data de um 1º turno "
            "eleitoral (ver `marcos_eleitorais` na resposta)."
        ),
    )
    dias_para_1_turno_mais_proximo: int | None = Field(
        default=None,
        description=(
            "RF2.4 — dias entre o 1º dia deste mês e o 1º turno eleitoral "
            "mais próximo (negativo = antes da eleição, positivo = depois). "
            "`null` só se `calendario_disponivel` for `false`."
        ),
    )


class IndiceTendenciaResponse(BaseModel):
    aviso: str = Field(
        ...,
        description=(
            "RF2.5 — texto de limitação explícito, para exibição direta na "
            "UI (nunca omitir este aviso ao mostrar o índice)."
        ),
    )
    n_observacoes: int = Field(..., description="Quantidade de meses observados usados para ajustar o modelo.")
    metodo: Literal["binomial_negativa", "poisson", "regressao_linear"] = Field(
        ...,
        description=(
            "Método efetivamente usado nesta execução para projetar os "
            "meses futuros — Binomial Negativa é o preferido (dados de "
            "contagem superdispersos); cai para Poisson e depois regressão "
            "linear se os anteriores não convergirem. Nunca escondido."
        ),
    )
    calendario_disponivel: bool = Field(
        ...,
        description=(
            "RF2.4 — false só se `scripts/election_calendar.py` não puder "
            "ser importado no ambiente de deploy (ver docs/PRD.md, Seção "
            "17, item 5, sobre `pip install -e .`). Quando false, "
            "`marcos_eleitorais` vem vazio e os campos de calendário de "
            "cada ponto vêm `false`/`null` — nunca uma data inventada."
        ),
    )
    marcos_eleitorais: list[MarcoEleitoralResponse] = Field(
        ..., description="Turnos eleitorais dentro do período coberto por `pontos`."
    )
    pontos: list[PontoIndiceResponse] = Field(
        ..., description="Série mensal completa: observados seguidos dos projetados, em ordem cronológica."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "aviso": "Índice de tendência extrapolado do volume absoluto mensal de checagens reais rotuladas IA (Dataset B), não uma previsão validada de impacto eleitoral.",
                "n_observacoes": 42,
                "metodo": "binomial_negativa",
                "calendario_disponivel": True,
                "marcos_eleitorais": [
                    {"ano": 2026, "data_1_turno": "2026-10-04", "mes": "2026-10"}
                ],
                "pontos": [
                    {
                        "mes": "2026-08",
                        "volume_ia": 3.0,
                        "volume_ia_projetado": None,
                        "limite_inferior": None,
                        "limite_superior": None,
                        "mes_de_1_turno": False,
                        "dias_para_1_turno_mais_proximo": -64,
                    },
                    {
                        "mes": "2026-10",
                        "volume_ia": None,
                        "volume_ia_projetado": 8.9,
                        "limite_inferior": 5.1,
                        "limite_superior": 12.4,
                        "mes_de_1_turno": True,
                        "dias_para_1_turno_mais_proximo": -3,
                    },
                ],
            }
        }
    }


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


@app.get(
    "/health",
    tags=["Sistema"],
    summary="Checagem de disponibilidade",
    response_model=HealthResponse,
)
def health() -> dict:
    """Sempre retorna `{"status": "ok"}` se o processo estiver de pé —
    **não** confirma que o modelo do classificador está carregado (isso só
    é verificado sob demanda, na primeira chamada a `/predict/ia-topic`) "
    nem que o Dataset C está acessível para `/forecast/index`. Útil como
    health check de infraestrutura (ex.: Render), não como diagnóstico
    funcional completo do serviço."""
    return {"status": "ok"}


@app.post(
    "/predict/ia-topic",
    tags=["Classificação de temática (Sensor de IA)"],
    summary="Classifica um texto quanto à temática de IA",
    response_model=PredicaoResponse,
    responses={
        422: {"description": "Texto ausente ou com menos de 20 caracteres úteis."},
        429: {"description": "Limite de 30 requisições por minuto (por IP) excedido."},
        503: {"description": "Artefato do modelo não encontrado no servidor (ver `IA_TOPIC_MODEL_PATH`)."},
    },
)
def predict_ia_topic(request: Request, req: TextoRequest) -> dict:
    """Classificador de **temática** de IA (v0) — RF1.1, RF1.5
    (`docs/PRD.md`, Seção 5.1). Dado um texto político, retorna se ele é
    sobre desinformação envolvendo IA, com probabilidade calibrada,
    confiança qualitativa e os termos que mais influenciaram a predição.

    **Limite crítico de interpretação:** isto classifica o *assunto* do
    texto, não se o texto *foi escrito* por IA — ver a distinção completa
    em `models/README.md` e na descrição da tag "Classificação de
    temática" acima. Rate limit: 30 requisições/minuto por IP.

    Se `permitir_uso_para_pesquisa=true`, o texto e a predição são
    gravados num log de opt-in (`data/consentimento_log.jsonl`) para uma
    futura curadoria de corpus do detector de autoria v1 — nunca usado
    para retreinar o modelo v0 automaticamente.
    """
    if len(req.texto.strip()) < TAMANHO_MIN_TEXTO:
        raise HTTPException(
            422, f"Texto muito curto para análise (mínimo {TAMANHO_MIN_TEXTO} caracteres)."
        )

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


@app.post(
    "/predict/ia-topic/batch",
    tags=["Classificação de temática (Sensor de IA)"],
    summary="Classifica vários textos numa única chamada",
    response_model=PredicaoLoteResponse,
    responses={
        422: {"description": "Lista vazia, com mais de 50 itens, ou com algum item fora do limite de tamanho."},
        429: {"description": "Limite de 10 requisições por minuto (por IP) excedido."},
        503: {"description": "Artefato do modelo não encontrado no servidor."},
    },
)
def predict_ia_topic_batch(request: Request, req: TextoLoteRequest) -> dict:
    f"""Versão em lote de `POST /predict/ia-topic`, até {TAMANHO_MAX_LOTE}
    textos por chamada — pensado para uso interno/análise em volume (ex.:
    reclassificar um conjunto de itens de uma vez), não para o Sensor de
    IA da interface (que usa o endpoint individual, um texto por vez).

    Cada item da lista de entrada é validado e classificado
    independentemente: um item muito curto vira `{{"erro": "..."}}` na
    posição correspondente do resultado, sem invalidar os demais itens do
    lote. Diferente do endpoint individual, este **não** registra
    consentimento/log — opt-in não se aplica a uso em lote nesta v0.
    Rate limit: 10 requisições/minuto por IP (mais restritivo que o
    individual, por processar até {TAMANHO_MAX_LOTE}x mais texto por
    chamada).
    """
    try:
        predictor = get_predictor()
    except FileNotFoundError as e:
        raise HTTPException(503, str(e)) from e

    resultados = []
    for texto in req.textos:
        if len(texto.strip()) < TAMANHO_MIN_TEXTO:
            resultados.append(
                {"erro": f"Texto muito curto para análise (mínimo {TAMANHO_MIN_TEXTO} caracteres)."}
            )
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


@app.post(
    "/predict/ia-authorship",
    tags=["Detector de autoria (v1, roadmap)"],
    summary="[Não implementado] Detector de autoria por IA — sempre 501",
    responses={
        501: {
            "description": (
                "Sempre retornado, de propósito — ver descrição do endpoint "
                "e da tag \"Detector de autoria\" acima. Não é um erro de "
                "configuração; é uma decisão de honestidade de escopo."
            )
        },
        429: {"description": "Limite de 30 requisições por minuto (por IP) excedido."},
    },
)
def predict_ia_authorship(request: Request) -> dict:
    """
    Detector de **autoria** por IA (v1) — ainda **não implementado**, e
    este endpoint sempre responde `501 Not Implemented` para deixar isso
    explícito, em vez de reaproveitar o classificador de temática (v0)
    como se fosse a mesma coisa (o que passaria uma falsa sensação de
    capacidade — ver `docs/PRD.md`, Seção 5.1, "Problema A vs. Problema B").

    Não existe, neste repositório, um corpus rotulado texto-humano vs.
    texto-gerado-por-IA sobre temas políticos brasileiros — implementar
    esta v1 exige coletar esse corpus primeiro (`docs/PRD.md`, Seção 5.3).
    Use `POST /predict/ia-topic` para o classificador de temática (v0)
    disponível hoje.
    """
    raise HTTPException(
        501,
        "Detector de autoria por IA ainda não implementado — requer coleta de "
        "dados nova (ver docs/PRD.md, Seção 5.3, roadmap v1). Use "
        "/predict/ia-topic para o classificador de temática (v0) disponível.",
    )


@app.get(
    "/forecast/index",
    tags=["Índice de tendência"],
    summary="Série + projeção do índice de tendência, com contexto eleitoral",
    response_model=IndiceTendenciaResponse,
    responses={
        422: {"description": "Menos meses observados no Dataset C do que o mínimo exigido pelo modelo."},
        429: {"description": "Limite de 30 requisições por minuto (por IP) excedido."},
        503: {"description": "`data/processed/dataset_c_unificado.csv` não encontrado no servidor."},
    },
)
def forecast_index(
    request: Request,
    periods: int = Query(
        6, ge=1, le=24, description="Quantos meses futuros projetar além do último mês observado."
    ),
) -> dict:
    """Índice de tendência/atenção de desinformação por IA (v0) — RF2.1 a
    RF2.5 (`docs/PRD.md`, Seção 5.2). Lê
    `data/processed/dataset_c_unificado.csv` **ao vivo, a cada chamada**
    (sem cache), agrega o volume ABSOLUTO mensal de checagens rotuladas IA
    (Dataset B, rótulo editorial real — não uma proporção do total, ver
    Seção 10.2 do PRD) e ajusta um GLM apropriado para dados de contagem
    (Binomial Negativa, com fallback para Poisson e depois regressão
    linear) para projetar os `periods` meses seguintes, com intervalo de
    confiança de 95%.

    **RF2.4 — contexto de calendário eleitoral:** cada ponto da resposta
    também indica se aquele mês contém um 1º turno eleitoral
    (`mes_de_1_turno`) e a distância em dias até o turno mais próximo
    (`dias_para_1_turno_mais_proximo`); a resposta como um todo lista os
    turnos dentro do período coberto (`marcos_eleitorais`). Ver
    `models_pkg.forecasting.trend_index` para a docstring completa do
    raciocínio estatístico e do acoplamento de calendário.

    **Isto não é uma previsão validada de impacto eleitoral** — ver o
    campo `aviso`, sempre presente na resposta, para o texto de limitação
    completo (RF2.5).
    """
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

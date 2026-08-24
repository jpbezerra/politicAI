"""
Índice de Intensidade de Desinformação por IA (v0) — ver docs/PRD.md,
Seção 4.2.

IMPORTANTE — leia antes de usar ou expor este módulo: isto é um índice de
TENDÊNCIA/atenção extrapolado de uma série mensal pequena e concentrada
numa única fonte editorial (122 itens IA no total, até a última coleta).
NÃO é uma previsão validada de resultado eleitoral, nem uma estimativa
causal de "impacto". A extrapolação linear usada aqui é deliberadamente
simples (não uma rede neural) porque o volume de dados não sustenta um
modelo mais complexo sem overfitting — ver `models/README.md`.

DESVIO DELIBERADO DO DESENHO ORIGINAL (documentado para transparência):
o PRD (docs/PRD.md, RF2.1) especificava normalizar o volume de itens IA
pelo volume TOTAL de checagens do mesmo mês, para não confundir "mais
desinformação por IA" com "mais checagens em geral". Ao implementar essa
normalização, descobrimos que ela produz um artefato enganoso com os dados
atuais: o Dataset B foi coletado por 3 buscas por tag feitas
separadamente (`eleicoes-2022`, `eleicoes-2026`, `inteligencia-artificial`),
e essas buscas NÃO cobrem os mesmos meses de forma comparável — em vários
meses de 2024-2025, praticamente 100% dos itens do "total do mês" vêm
justamente da busca "inteligencia-artificial" (porque não há itens de
outras buscas datados naquele mês), o que faz a proporção IA/total saltar
para perto de 1.0 sem que isso reflita uma mudança real no mundo. É o mesmo
tipo de viés de desenho amostral já identificado e corrigido em
`notebooks/02_dataset_b_aosfatos_eda.ipynb` (Seção 4.5), agora encontrado
num lugar novo.

Por isso, esta v0 usa o VOLUME ABSOLUTO mensal de itens rotulados IA
(Dataset B, rótulo editorial real) como índice — não uma proporção do
total — replicando a mesma abordagem (contagem absoluta, com o cuidado de
não normalizar por um denominador incomparável) já usada nas visualizações
do notebook 02, Seção 5. Uma versão futura que reintroduza a normalização
por volume total precisaria antes resolver a comparabilidade temporal das
buscas por tag (ex.: nova coleta com datas de corte uniformes por tag).

MODELO ESTATÍSTICO (atualizado — ver docs/PRD.md, backlog de melhorias):
a v0 original extrapolava com uma regressão linear (mínimos quadrados)
simples sobre a série mensal — auditável, mas estatisticamente inadequada
para dados de CONTAGEM (valores inteiros não-negativos, variância que
cresce com a média, nunca deveria projetar um valor negativo). Com os
dados reais até a última coleta, a série mensal de volume IA tem média
≈3.6 e variância ≈7.7 — SUPERDISPERSÃO clara (variância > média), o que
descarta um Poisson simples (que assume variância = média) em favor de uma
**Binomial Negativa** (`statsmodels.discrete.discrete_model.NegativeBinomial`),
que estima o parâmetro de dispersão adicional a partir dos próprios dados.
Se a Binomial Negativa não convergir (ex.: série muito curta), o módulo cai
para um GLM de Poisson e, na ausência de `statsmodels` ou com poucochíssimos
dados, para a regressão linear original — sempre deixando explícito, no
campo `metodo` do resultado, qual dos três foi de fato usado. O intervalo
reportado é o intervalo de confiança (95%) da MÉDIA mensal projetada pelo
GLM, não um intervalo preditivo completo para a contagem de um mês
específico (que seria mais largo, por incluir também a dispersão do
processo de contagem) — mantido assim por ser mais simples de auditar e
comunicar; ver `PontoIndice`/`IndiceTendencia` para os campos exatos.

RF2.4 — CONTEXTUALIZAÇÃO COM CALENDÁRIO ELEITORAL (implementado na revisão
pós-Fase 3, ver docs/PRD.md Seção 15, achado 1): até esta correção, o
índice não carregava nenhum campo de data de turno/proximidade eleitoral —
o item do backlog que citava "datas de turno centralizadas" (Seção 11.1,
item 9) tinha implementado só a centralização de `DATAS_TURNO_1` em
`scripts/election_calendar.py` para os notebooks/export, sem nunca
conectar isso ao índice de tendência. Esta versão importa
`scripts/election_calendar.py` (mesma fonte única de datas de turno usada
pelos notebooks) e anota cada `PontoIndice` (observado ou projetado) com
`mes_de_1_turno` (booleano) e `dias_para_1_turno_mais_proximo` (inteiro,
negativo = antes da eleição), além de expor em
`IndiceTendencia.marcos_eleitorais` a lista de turnos cuja data cai dentro
do período coberto pelos pontos retornados — o que o `/web` usa para
desenhar marcadores verticais no gráfico do índice (ver
`web/src/components/trend-index-chart.tsx`).

ACOPLAMENTO DE CAMINHO ASSUMIDO (documentado, não escondido): `models/` é
declarado como pacote independente de `/web` (docs/PRD.md, Seção 7), mas
já assume um checkout de monorepo para ler `../data/processed/` (ver
`DEFAULT_DATASET_C` em `api/main.py`) — este módulo estende a mesma
suposição para importar `scripts/election_calendar.py` como sibling de
`models/` na raiz do repositório, em vez de duplicar o dicionário de datas
de turno dentro de `models_pkg` (o que reintroduziria o tipo de duplicação
que o item 9 da Seção 11.1 eliminou). Se `models/` algum dia for extraído
para um deploy separado sem `scripts/` como sibling, o import falha e
`calendario_disponivel=False` no resultado — `mes_de_1_turno`/
`dias_para_1_turno_mais_proximo` ficam `False`/`None`, e
`marcos_eleitorais` fica vazio; nunca uma data inventada.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import statsmodels.api as sm

    _STATSMODELS_DISPONIVEL = True
except ImportError:  # pragma: no cover - statsmodels é dependência declarada, mas mantemos o fallback
    _STATSMODELS_DISPONIVEL = False

# Ver nota "ACOPLAMENTO DE CAMINHO ASSUMIDO" na docstring do módulo.
_REPO_ROOT = Path(__file__).resolve().parents[4]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    from election_calendar import DATAS_TURNO_1, ciclo_e_dias

    _CALENDARIO_DISPONIVEL = True
except ImportError:  # pragma: no cover - só ocorre se models/ for extraído sem scripts/ como sibling
    DATAS_TURNO_1 = {}
    ciclo_e_dias = None
    _CALENDARIO_DISPONIVEL = False


@dataclass
class PontoIndice:
    mes: str
    volume_ia: float | None  # observado; None nos meses projetados
    volume_ia_projetado: float | None  # projetado; None nos meses observados
    limite_inferior: float | None = None
    limite_superior: float | None = None
    # RF2.4 — contextualização com calendário eleitoral (ver docstring do
    # módulo). `None`/`False` quando `scripts/election_calendar.py` não
    # está disponível (ver `IndiceTendencia.calendario_disponivel`).
    mes_de_1_turno: bool = False
    dias_para_1_turno_mais_proximo: int | None = None


@dataclass
class IndiceTendencia:
    pontos: list[PontoIndice] = field(default_factory=list)
    n_observacoes: int = 0
    metodo: str = "indisponivel"  # "binomial_negativa" | "poisson" | "regressao_linear"
    # RF2.4 — turnos eleitorais (1º turno) cuja data cai dentro do período
    # coberto por `pontos` (observado + projetado). Cada item:
    # {"ano": int, "data_1_turno": "YYYY-MM-DD", "mes": "YYYY-MM"}.
    marcos_eleitorais: list[dict] = field(default_factory=list)
    calendario_disponivel: bool = False
    aviso: str = (
        "Índice de tendência extrapolado do volume absoluto mensal de "
        "checagens reais rotuladas IA (Dataset B), não uma previsão "
        "validada de impacto eleitoral. Amostra pequena e concentrada numa "
        "única fonte editorial — ver docs/PRD.md, Seção 4.2, e "
        "models/README.md para a discussão do viés de desenho amostral "
        "que motivou usar volume absoluto em vez de proporção do total. "
        "O intervalo mostrado é o intervalo de confiança (95%) da média "
        "mensal projetada, não uma faixa de valores prováveis para a "
        "contagem de um mês específico (que seria mais larga)."
    )


def _serie_mensal_ia(df: pd.DataFrame) -> pd.DataFrame:
    """
    Série mensal de volume ABSOLUTO de checagens reais rotuladas IA.

    Só itens do Dataset B com rótulo editorial real (`fonte_dataset == "B"`
    e `rotulo_ia == "IA"`) entram na contagem — ver nota de desvio do
    desenho original no topo deste módulo para por que não normalizamos
    pelo volume total de checagens do mês.
    """
    d = df.dropna(subset=["data_publicacao"]).copy()
    d["data_publicacao"] = pd.to_datetime(d["data_publicacao"], errors="coerce")
    d = d.dropna(subset=["data_publicacao"])
    d["mes"] = d["data_publicacao"].dt.to_period("M").astype(str)

    ia_mensal = (
        d[(d["fonte_dataset"] == "B") & (d["rotulo_ia"] == "IA")]
        .groupby("mes")
        .size()
    )

    # Preenche meses sem nenhum item IA com 0, dentro do intervalo observado,
    # para a série não "pular" meses vazios como se não existissem.
    if ia_mensal.empty:
        return pd.DataFrame(columns=["mes", "volume_ia"])

    todos_os_meses = pd.period_range(
        start=pd.Period(ia_mensal.index.min(), freq="M"),
        end=pd.Period(ia_mensal.index.max(), freq="M"),
        freq="M",
    ).astype(str)
    serie = pd.DataFrame({"mes": todos_os_meses}).merge(
        ia_mensal.rename("volume_ia").reset_index(), on="mes", how="left"
    )
    serie["volume_ia"] = serie["volume_ia"].fillna(0)
    return serie.sort_values("mes")


def _ajustar_glm_contagem(x: np.ndarray, y: np.ndarray, x_futuro: np.ndarray) -> tuple[str, pd.DataFrame]:
    """Tenta Binomial Negativa (apropriada para a superdispersão real da
    série — ver docstring do módulo); cai para Poisson se a BN não
    convergir. Retorna (metodo, frame) onde frame tem colunas
    media/ci_inferior/ci_superior alinhadas com x_futuro.

    Levanta exceção se nenhum dos dois GLMs conseguir ajustar (ex.: série
    degenerada) — o chamador cai para a regressão linear original.
    """
    X = sm.add_constant(x)
    X_futuro = sm.add_constant(x_futuro, has_constant="add")

    metodo = "binomial_negativa"
    try:
        modelo = sm.NegativeBinomial(y, X).fit(disp=0, maxiter=200)
        if not modelo.mle_retvals.get("converged", True):
            raise RuntimeError("Binomial Negativa não convergiu")
    except Exception:
        metodo = "poisson"
        modelo = sm.GLM(y, X, family=sm.families.Poisson()).fit()

    frame = modelo.get_prediction(X_futuro).summary_frame(alpha=0.05)
    # Nomes de coluna diferem entre NegativeBinomial (discrete) e GLM.
    if "predicted" in frame.columns:
        frame = frame.rename(columns={"predicted": "media", "ci_lower": "ci_inferior", "ci_upper": "ci_superior"})
    else:
        frame = frame.rename(columns={"mean": "media", "mean_ci_lower": "ci_inferior", "mean_ci_upper": "ci_superior"})
    return metodo, frame[["media", "ci_inferior", "ci_superior"]]


def _aplicar_contexto_eleitoral(pontos: list[PontoIndice]) -> tuple[list[dict], bool]:
    """Anota `pontos` (in-place) com `mes_de_1_turno`/
    `dias_para_1_turno_mais_proximo` e retorna (marcos_eleitorais,
    calendario_disponivel).

    Reaproveita `ciclo_e_dias` de `scripts/election_calendar.py` (mesma
    lógica de "ciclo mais próximo por distância absoluta" já usada pelos
    notebooks), aplicada ao primeiro dia de cada mês da série — o índice
    de tendência só tem granularidade mensal, então não faz sentido pedir
    uma data exata de publicação como os notebooks fazem por checagem.
    """
    if not _CALENDARIO_DISPONIVEL or not pontos:
        return [], False

    for ponto in pontos:
        mes_ts = pd.Period(ponto.mes, freq="M").to_timestamp()
        info = ciclo_e_dias(mes_ts)
        ciclo = int(info["ciclo_eleitoral_estimado"])
        ponto.dias_para_1_turno_mais_proximo = int(info["dias_para_eleicao"])
        turno = DATAS_TURNO_1[ciclo]
        ponto.mes_de_1_turno = turno.year == mes_ts.year and turno.month == mes_ts.month

    primeiro_mes, ultimo_mes = pontos[0].mes, pontos[-1].mes
    marcos = [
        {"ano": ano, "data_1_turno": turno.isoformat(), "mes": f"{turno.year:04d}-{turno.month:02d}"}
        for ano, turno in sorted(DATAS_TURNO_1.items())
        if primeiro_mes <= f"{turno.year:04d}-{turno.month:02d}" <= ultimo_mes
    ]
    return marcos, True


def compute_trend_index(
    df: pd.DataFrame, forecast_periods: int = 6, min_observacoes: int = 6
) -> IndiceTendencia:
    serie = _serie_mensal_ia(df)

    if len(serie) < min_observacoes:
        return IndiceTendencia(pontos=[], n_observacoes=len(serie))

    x = np.arange(len(serie))
    y = serie["volume_ia"].to_numpy()
    x_futuro = np.arange(len(serie), len(serie) + forecast_periods)

    metodo = "regressao_linear"
    frame_futuro = None
    if _STATSMODELS_DISPONIVEL:
        try:
            metodo, frame_futuro = _ajustar_glm_contagem(x, y, x_futuro)
        except Exception:
            # Série pequena demais / degenerada para o GLM convergir --
            # cai para a regressão linear original, documentado no aviso.
            metodo = "regressao_linear"
            frame_futuro = None

    pontos = [
        PontoIndice(mes=row.mes, volume_ia=float(row.volume_ia), volume_ia_projetado=None)
        for row in serie.itertuples()
    ]
    ultimo_mes = pd.Period(serie["mes"].iloc[-1], freq="M")

    if frame_futuro is not None:
        for passo, row in zip(range(1, forecast_periods + 1), frame_futuro.itertuples()):
            mes_futuro = str(ultimo_mes + passo)
            pontos.append(
                PontoIndice(
                    mes=mes_futuro,
                    volume_ia=None,
                    volume_ia_projetado=max(0.0, float(row.media)),
                    limite_inferior=max(0.0, float(row.ci_inferior)),
                    limite_superior=max(0.0, float(row.ci_superior)),
                )
            )
    else:
        # Fallback: regressão linear simples (mínimos quadrados) — usada só
        # se statsmodels não estiver disponível ou o GLM não convergir
        # (ex.: série curta demais). Ver docstring do módulo.
        coef = np.polyfit(x, y, deg=1)
        y_hat = np.polyval(coef, x)
        residuos = y - y_hat
        desvio_residual = float(np.std(residuos)) if len(residuos) > 1 else 0.0
        for passo in range(1, forecast_periods + 1):
            mes_futuro = str(ultimo_mes + passo)
            x_f = len(serie) - 1 + passo
            y_proj = float(np.polyval(coef, x_f))
            margem = 1.96 * desvio_residual * np.sqrt(1 + passo / len(serie))
            pontos.append(
                PontoIndice(
                    mes=mes_futuro,
                    volume_ia=None,
                    volume_ia_projetado=max(0.0, y_proj),
                    limite_inferior=max(0.0, y_proj - margem),
                    limite_superior=max(0.0, y_proj + margem),
                )
            )

    marcos_eleitorais, calendario_disponivel = _aplicar_contexto_eleitoral(pontos)

    return IndiceTendencia(
        pontos=pontos,
        n_observacoes=len(serie),
        metodo=metodo,
        marcos_eleitorais=marcos_eleitorais,
        calendario_disponivel=calendario_disponivel,
    )

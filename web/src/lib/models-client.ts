import type { IndiceTendenciaResponse, SensorPredictionResponse } from "./types";
import { env } from "./env";

/**
 * Cliente HTTP para o serviço de inferência do `/models` (FastAPI).
 *
 * Por design, este cliente NUNCA fabrica uma predição quando o serviço está
 * indisponível — ele retorna um erro explícito, que a UI exibe como tal.
 * Ver docs/PRD.md, Seção 5.3 ("Comunicação com /models").
 */

const MODELS_API_URL = env.MODELS_API_URL ?? "http://localhost:8000";

export async function predizerTematicaIA(
  texto: string,
): Promise<SensorPredictionResponse> {
  if (!texto || texto.trim().length < 20) {
    return {
      ok: false,
      erro: "Cole um texto com pelo menos 20 caracteres para análise.",
    };
  }

  try {
    const res = await fetch(`${MODELS_API_URL}/predict/ia-topic`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto }),
      // Serviço de ML pode não estar no ar em todo ambiente de dev/demo do /web.
      signal: AbortSignal.timeout(8000),
    });

    if (!res.ok) {
      return {
        ok: false,
        erro: `Serviço de modelo respondeu com erro (HTTP ${res.status}).`,
      };
    }

    const data = await res.json();
    return {
      ok: true,
      rotulo: data.rotulo,
      probabilidade: data.probabilidade,
      confianca: data.confianca,
      termos_influentes: data.termos_influentes ?? [],
      modelo_versao: data.modelo_versao ?? "desconhecida",
    };
  } catch {
    return {
      ok: false,
      erro:
        "Não foi possível conectar ao serviço de modelo (/models). " +
        "Ele precisa estar rodando separadamente (ver models/README.md). " +
        "Nenhuma predição simulada é exibida no lugar de uma resposta real.",
    };
  }
}

/**
 * Índice de tendência de desinformação por IA, com contextualização de
 * calendário eleitoral (RF2.4, docs/PRD.md Seção 5.2/15). Chamado do
 * painel (`src/app/page.tsx`, lado servidor) — como o restante do painel
 * lê `../data/processed/` direto do disco e não depende do `/models`
 * estar no ar, esta é a primeira chamada do painel ao serviço de
 * inferência; segue a mesma regra de nunca fabricar dado (ver
 * `predizerTematicaIA` acima) — indisponibilidade vira um erro explícito
 * na seção do índice, nunca um gráfico inventado, e nunca derruba o resto
 * do painel (chamada isolada em seu próprio try/catch em `page.tsx`).
 */
export async function obterIndiceTendencia(
  periods: number = 6,
): Promise<IndiceTendenciaResponse> {
  try {
    const res = await fetch(
      `${MODELS_API_URL}/forecast/index?periods=${periods}`,
      {
        // Ver nota de timeout em predizerTematicaIA -- o painel não deve
        // ficar preso esperando um serviço de ML fora do ar.
        signal: AbortSignal.timeout(8000),
      },
    );

    if (!res.ok) {
      const detalhe = await res.json().catch(() => null);
      return {
        ok: false,
        erro:
          (typeof detalhe?.detail === "string" ? detalhe.detail : null) ??
          `Serviço de modelo respondeu com erro (HTTP ${res.status}) ao calcular o índice de tendência.`,
      };
    }

    const data = await res.json();
    return {
      ok: true,
      aviso: data.aviso,
      n_observacoes: data.n_observacoes,
      metodo: data.metodo,
      calendario_disponivel: data.calendario_disponivel ?? false,
      marcos_eleitorais: data.marcos_eleitorais ?? [],
      pontos: data.pontos ?? [],
    };
  } catch {
    return {
      ok: false,
      erro:
        "Não foi possível conectar ao serviço de modelo (/models) para " +
        "calcular o índice de tendência. Ele precisa estar rodando " +
        "separadamente (ver models/README.md). Nenhum índice simulado é " +
        "exibido no lugar de uma resposta real.",
    };
  }
}

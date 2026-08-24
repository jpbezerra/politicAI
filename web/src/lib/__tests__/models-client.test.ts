import { afterEach, describe, expect, it, vi } from "vitest";
import { obterIndiceTendencia, predizerTematicaIA } from "@/lib/models-client";

describe("predizerTematicaIA", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("recusa texto curto sem chamar a rede", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    const resultado = await predizerTematicaIA("curto");

    expect(resultado.ok).toBe(false);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("retorna erro explícito (nunca dado fabricado) quando o serviço responde com erro HTTP", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 503 }),
    );

    const resultado = await predizerTematicaIA(
      "Um texto qualquer, longo o suficiente para passar da validação mínima.",
    );

    expect(resultado.ok).toBe(false);
    if (!resultado.ok) {
      expect(resultado.erro).toMatch(/503/);
    }
  });

  it("retorna erro explícito quando a chamada de rede falha (serviço fora do ar)", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network down")));

    const resultado = await predizerTematicaIA(
      "Um texto qualquer, longo o suficiente para passar da validação mínima.",
    );

    expect(resultado.ok).toBe(false);
    if (!resultado.ok) {
      expect(resultado.erro).toContain("Não foi possível conectar");
    }
  });

  it("repassa a predição real quando o serviço responde com sucesso", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          rotulo: "IA",
          probabilidade: 0.91,
          confianca: "alta",
          termos_influentes: ["ia", "artificial"],
          modelo_versao: "v0-topic-2026.08",
        }),
      }),
    );

    const resultado = await predizerTematicaIA(
      "Um texto qualquer, longo o suficiente para passar da validação mínima.",
    );

    expect(resultado).toEqual({
      ok: true,
      rotulo: "IA",
      probabilidade: 0.91,
      confianca: "alta",
      termos_influentes: ["ia", "artificial"],
      modelo_versao: "v0-topic-2026.08",
    });
  });
});

// RF2.4 (docs/PRD.md, Seção 5.2/15) -- contextualização com calendário
// eleitoral do índice de tendência.
describe("obterIndiceTendencia", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("repassa o índice real, incluindo marcos eleitorais, quando o serviço responde com sucesso", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          aviso: "aviso real",
          n_observacoes: 30,
          metodo: "binomial_negativa",
          calendario_disponivel: true,
          marcos_eleitorais: [
            { ano: 2026, data_1_turno: "2026-10-04", mes: "2026-10" },
          ],
          pontos: [
            {
              mes: "2026-10",
              volume_ia: null,
              volume_ia_projetado: 8.8,
              limite_inferior: 5.1,
              limite_superior: 12.4,
              mes_de_1_turno: true,
              dias_para_1_turno_mais_proximo: -3,
            },
          ],
        }),
      }),
    );

    const resultado = await obterIndiceTendencia(6);

    expect(resultado.ok).toBe(true);
    if (resultado.ok) {
      expect(resultado.calendario_disponivel).toBe(true);
      expect(resultado.marcos_eleitorais).toHaveLength(1);
      expect(resultado.marcos_eleitorais[0].ano).toBe(2026);
      expect(resultado.pontos[0].mes_de_1_turno).toBe(true);
    }
  });

  it("nunca fabrica marcos eleitorais quando o serviço não os envia", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          aviso: "aviso real",
          n_observacoes: 30,
          metodo: "poisson",
          pontos: [],
        }),
      }),
    );

    const resultado = await obterIndiceTendencia(6);

    expect(resultado.ok).toBe(true);
    if (resultado.ok) {
      expect(resultado.calendario_disponivel).toBe(false);
      expect(resultado.marcos_eleitorais).toEqual([]);
    }
  });

  it("retorna erro explícito quando o serviço responde com erro HTTP", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        json: async () => ({ detail: "Dados insuficientes." }),
      }),
    );

    const resultado = await obterIndiceTendencia(6);

    expect(resultado.ok).toBe(false);
    if (!resultado.ok) {
      expect(resultado.erro).toBe("Dados insuficientes.");
    }
  });

  it("retorna erro explícito quando a chamada de rede falha (serviço fora do ar)", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network down")));

    const resultado = await obterIndiceTendencia(6);

    expect(resultado.ok).toBe(false);
    if (!resultado.ok) {
      expect(resultado.erro).toContain("Não foi possível conectar");
    }
  });
});

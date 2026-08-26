import { describe, expect, it } from "vitest";
import { marcosEleitoraisVisiveis } from "@/components/monthly-volume-chart";
import type { SerieMensalPonto } from "@/lib/types";

// RF3.3 (docs/PRD.md, Seção 6.1/15) -- corrigido nesta revisão: o campo
// `datas_turno_1` existia em DatasetCSummary desde a Fase 3, mas nunca era
// usado para desenhar nenhum marcador no gráfico de volume mensal. Este
// teste cobre a função pura que decide quais marcos aparecem.

function ponto(mes: string): SerieMensalPonto {
  return { mes, total: 1, ia: 0, tradicional: 1 };
}

describe("marcosEleitoraisVisiveis", () => {
  it("inclui só os turnos cujo mês está dentro do intervalo exibido", () => {
    const data = [ponto("2024-01"), ponto("2024-10"), ponto("2025-01")];
    const datasTurno1 = {
      "2018": "2018-10-07",
      "2022": "2022-10-02",
      "2024": "2024-10-06",
      "2026": "2026-10-04",
    };

    const marcos = marcosEleitoraisVisiveis(data, datasTurno1);

    expect(marcos).toEqual([{ ano: "2024", mes: "2024-10" }]);
  });

  it("retorna lista vazia quando nenhum turno cai no intervalo", () => {
    const data = [ponto("2025-01"), ponto("2025-06")];
    const datasTurno1 = { "2024": "2024-10-06", "2026": "2026-10-04" };

    expect(marcosEleitoraisVisiveis(data, datasTurno1)).toEqual([]);
  });

  it("não fabrica marcos quando datasTurno1 não é passado", () => {
    const data = [ponto("2024-10")];
    expect(marcosEleitoraisVisiveis(data, undefined)).toEqual([]);
  });
});

import { describe, expect, it } from "vitest";
import { veredictoPredominante } from "@/lib/veredito-labels";

// RF3.1 (docs/PRD.md, Seção 6.1/15) -- "veredito predominante" no resumo
// executivo, corrigido nesta revisão (o dado já existia, mas nunca era
// usado para calcular/exibir esse card).
describe("veredictoPredominante", () => {
  it("retorna o veredito com maior contagem e a porcentagem correta", () => {
    const resultado = veredictoPredominante([
      { veredito: "falso", n: 60 },
      { veredito: "parcialmente_falso", n: 30 },
      { veredito: "nao_falso", n: 10 },
    ]);

    expect(resultado).toEqual({ veredito: "falso", n: 60, pct: 60 });
  });

  it("retorna null quando a distribuição está vazia (nunca fabrica um veredito)", () => {
    expect(veredictoPredominante([])).toBeNull();
  });

  it("retorna null quando o total é zero", () => {
    expect(
      veredictoPredominante([
        { veredito: "falso", n: 0 },
        { veredito: "nao_falso", n: 0 },
      ]),
    ).toBeNull();
  });

  it("arredonda a porcentagem para uma casa decimal", () => {
    const resultado = veredictoPredominante([
      { veredito: "falso", n: 1 },
      { veredito: "nao_falso", n: 2 },
    ]);
    expect(resultado?.pct).toBeCloseTo(66.7, 1);
  });
});

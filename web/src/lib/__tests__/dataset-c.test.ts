import { describe, expect, it } from "vitest";
import {
  buildDistribuicaoFonte,
  buildDistribuicaoTema,
  buildDistribuicaoVeredito,
  buildSerieMensal,
  mesDe,
  type DatasetCRow,
} from "@/lib/dataset-c";

// Testa só a lógica de agregação PURA (sem tocar no disco) — a leitura real
// do CSV (readRows/getDatasetCSummary) depende de data/processed/, fora do
// escopo de um teste unitário isolado. Ver web/README.md.

// Preenche os campos de DatasetCRow não usados em cada teste com valores
// neutros, para montar fixtures completas e tipadas (sem `as any`).
function makeRow(overrides: Partial<DatasetCRow>): DatasetCRow {
  return {
    fonte_dataset: "",
    titulo: "",
    data_publicacao: "",
    rotulo_ia: "Tradicional",
    fonte_rotulo_ia: "",
    categoria_tema: "",
    veredito_binario: "",
    url: "",
    ...overrides,
  };
}

describe("mesDe", () => {
  it("extrai ano-mês de uma data com hora", () => {
    expect(mesDe("2025-03-14 10:00:00")).toBe("2025-03");
  });

  it("extrai ano-mês de uma data sem hora", () => {
    expect(mesDe("2025-03-14")).toBe("2025-03");
  });

  it("retorna null para valores vazios ou inválidos", () => {
    expect(mesDe("")).toBeNull();
    expect(mesDe(undefined as unknown as string)).toBeNull();
    expect(mesDe("data inválida")).toBeNull();
  });
});

describe("buildSerieMensal", () => {
  it("agrupa por mês e separa IA de Tradicional", () => {
    const rows = [
      makeRow({ data_publicacao: "2025-01-05", rotulo_ia: "IA" }),
      makeRow({ data_publicacao: "2025-01-20", rotulo_ia: "Tradicional" }),
      makeRow({ data_publicacao: "2025-02-01", rotulo_ia: "Tradicional" }),
    ];

    const serie = buildSerieMensal(rows);
    expect(serie).toEqual([
      { mes: "2025-01", ia: 1, tradicional: 1, total: 2 },
      { mes: "2025-02", ia: 0, tradicional: 1, total: 1 },
    ]);
  });

  it("ignora linhas sem data válida", () => {
    const rows = [makeRow({ data_publicacao: "", rotulo_ia: "IA" })];
    expect(buildSerieMensal(rows)).toEqual([]);
  });
});

describe("buildDistribuicaoFonte", () => {
  it("conta itens por fonte de dataset", () => {
    const rows = [
      makeRow({ fonte_dataset: "A" }),
      makeRow({ fonte_dataset: "A" }),
      makeRow({ fonte_dataset: "B" }),
    ];
    expect(buildDistribuicaoFonte(rows)).toEqual([
      { fonte: "A", n: 2 },
      { fonte: "B", n: 1 },
    ]);
  });
});

describe("buildDistribuicaoTema", () => {
  it("agrupa por tema, contando total e subtotal IA, limitado ao top N", () => {
    const rows = [
      makeRow({ categoria_tema: "eleicoes", rotulo_ia: "IA" }),
      makeRow({ categoria_tema: "eleicoes", rotulo_ia: "Tradicional" }),
      makeRow({ categoria_tema: "", rotulo_ia: "Tradicional" }),
    ];
    const resultado = buildDistribuicaoTema(rows);
    expect(resultado[0]).toEqual({ tema: "eleicoes", n: 2, n_ia: 1 });
    expect(resultado.find((r) => r.tema === "Não classificado")).toEqual({
      tema: "Não classificado",
      n: 1,
      n_ia: 0,
    });
  });
});

describe("buildDistribuicaoVeredito", () => {
  it("trata veredito vazio como não classificado", () => {
    const rows = [makeRow({ veredito_binario: "falso" }), makeRow({ veredito_binario: "" })];
    expect(buildDistribuicaoVeredito(rows)).toEqual([
      { veredito: "falso", n: 1 },
      { veredito: "nao_classificado", n: 1 },
    ]);
  });
});

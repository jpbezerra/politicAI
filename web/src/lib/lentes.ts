import type { LenteInfo } from "./types";

/**
 * As "lentes" do dashboard, inspiradas na plataforma de referência da
 * orientadora (Lentes da Eleição 2026), mais a lente de IA, que é o
 * diferencial deste projeto (ver docs/PRD.md, Seção 5.1).
 *
 * IMPORTANTE: `status` controla o que a UI mostra. Uma lente
 * "em_construcao" NUNCA deve renderizar números — apenas um aviso de que
 * a fonte ainda não está integrada. Isso evita repetir, no produto, o tipo
 * de erro que este projeto já corrigiu nos notebooks (dado heurístico ou
 * ausente sendo confundido com dado real).
 */
export const LENTES: LenteInfo[] = [
  {
    id: "imprensa",
    titulo: "Imprensa / Checagem de fatos",
    descricao:
      "Volume e temática de checagens de fatos eleitorais publicadas por veículos e agências (TSE 'Fato ou Boato' e Aos Fatos).",
    status: "real",
    fonte: "Dataset A (TSE) + Dataset B (Aos Fatos) — data/processed/dataset_c_unificado.csv",
  },
  {
    id: "ia",
    titulo: "Conteúdo relacionado a IA",
    descricao:
      "Checagens cujo tema é conteúdo político manipulado ou gerado por IA (deepfakes, áudio clonado, texto sintético), a partir do rótulo editorial do Aos Fatos.",
    status: "real",
    fonte: "Dataset B (rótulo editorial 'rotulo_ia') — ver docs/PRD.md, Seção 4.1 para a distinção temática vs. autoria",
  },
  {
    id: "buscadores",
    titulo: "Buscadores (Google Trends)",
    descricao: "Volume de busca por termos e candidatos ao longo do tempo.",
    status: "em_construcao",
    fonte: "Planejado: Google Trends / pytrends — ver docs/PRD.md, Seção 5.1 e Roadmap (V1)",
  },
  {
    id: "redes_sociais",
    titulo: "Redes sociais",
    descricao: "Conversação e engajamento sobre candidatos e temas eleitorais.",
    status: "em_construcao",
    fonte: "Planejado: APIs públicas de X / Bluesky / TikTok — ver docs/PRD.md, Roadmap (V2)",
  },
  {
    id: "institutos",
    titulo: "Institutos de pesquisa",
    descricao: "Intenção de voto e rejeição estimadas por amostragem.",
    status: "em_construcao",
    fonte: "Planejado: agregação de institutos públicos — ver docs/PRD.md, Roadmap (V2)",
  },
];

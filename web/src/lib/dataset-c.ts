import fs from "node:fs";
import path from "node:path";
import { z } from "zod";
import { parse } from "csv-parse/sync";
import type {
  DatasetCSummary,
  DistribuicaoFonte,
  DistribuicaoTema,
  DistribuicaoVeredito,
  SerieMensalPonto,
} from "./types";

// Validação de forma em runtime do snapshot estático (ver lerSnapshotEstatico
// abaixo) -- sem isso, um snapshot desatualizado/malformado (ex.: gerado por
// uma versão antiga de scripts/export_dashboard_data.py, com um campo
// renomeado ou faltando) seria repassado direto para a UI, que quebraria de
// forma pouco clara (undefined em algum lugar do JSX) em vez do erro
// explícito que este projeto exige para qualquer falha de dado (ver
// docs/PRD.md, Seção 1). Não precisa ficar 100% em sincronia com
// `DatasetCSummary` campo a campo -- só o suficiente para pegar um snapshot
// visivelmente incompatível antes de ele chegar à página.
const DatasetCSummarySchema = z.object({
  gerado_em: z.string(),
  gerado_por: z.string(),
  fonte_dados: z.string(),
  aviso: z.string(),
  datas_turno_1: z.record(z.string(), z.string()),
  resumo_geral: z.object({
    n_total: z.number(),
    n_ia: z.number(),
    n_tradicional: z.number(),
    pct_ia: z.number().nullable(),
    n_rotulo_editorial_confiavel: z.number(),
  }),
  serie_mensal: z.array(
    z.object({ mes: z.string(), total: z.number(), ia: z.number(), tradicional: z.number() }),
  ),
  distribuicao_por_fonte: z.array(z.object({ fonte: z.string(), n: z.number() })),
  distribuicao_por_tema: z.array(
    z.object({ tema: z.string(), n: z.number(), n_ia: z.number() }),
  ),
  distribuicao_veredito: z.array(z.object({ veredito: z.string(), n: z.number() })),
}) satisfies z.ZodType<DatasetCSummary>;

/**
 * Camada de acesso ao Dataset C — Datasets A + B unificados, Fase 2 do
 * projeto (ver docs/PRD.md).
 *
 * IMPORTANTE: isto lê `data/processed/dataset_c_unificado.csv` DIRETO DO
 * DISCO a cada chamada — não é um snapshot JSON pré-computado. Qualquer
 * atualização do CSV (nova coleta + notebook 03 regerado) aparece no
 * painel na próxima renderização, sem precisar rodar nenhum script
 * intermediário. Isso é intencional: um snapshot exigiria lembrar de
 * regenerá-lo manualmente sempre que o dataset mudasse, e um esquecimento
 * faria o painel mostrar números desatualizados sem nenhum aviso — o tipo
 * de coisa que este projeto trata como falha grave (ver docs/PRD.md e
 * README.md sobre honestidade de dados).
 *
 * Trade-off aceito: o caminho preferencial pressupõe que `/web` roda a
 * partir de dentro do monorepo (com `../data/processed/` acessível no
 * disco) -- é o caso normal de `npm run dev`/`npm run build` a partir de
 * `web/`. Se o CSV não estiver acessível (deploy "standalone", ver
 * `web/README.md`, seção "De onde vêm os dados"), cai-se para um snapshot
 * JSON estático pré-gerado por `scripts/export_dashboard_data.py` -- ver
 * `lerSnapshotEstatico()` abaixo. O snapshot é claramente rotulado como tal
 * nos próprios campos `gerado_por`/`aviso` (nunca apresentado como dado ao
 * vivo), seguindo o princípio deste projeto de nunca mascarar limitações de
 * dados (docs/PRD.md, Seção 1).
 */

const DATASET_C_CANDIDATE_PATHS = [
  path.join(process.cwd(), "..", "data", "processed", "dataset_c_unificado.csv"),
  path.join(process.cwd(), "data", "processed", "dataset_c_unificado.csv"),
];

// Onde `scripts/export_dashboard_data.py` grava o snapshot (ver esse
// script para o formato exato -- espelha `DatasetCSummary` campo a campo).
const DATASET_C_SNAPSHOT_CANDIDATE_PATHS = [
  path.join(process.cwd(), "src", "data", "dataset_c_summary.json"),
  path.join(process.cwd(), "data", "dataset_c_summary.json"),
];

const TOP_N_TEMAS = 8;

export interface DatasetCRow {
  fonte_dataset: string;
  titulo: string;
  data_publicacao: string;
  rotulo_ia: string;
  fonte_rotulo_ia: string;
  categoria_tema: string;
  veredito_binario: string;
  url: string;
}

function findExistingPath(candidates: string[]): string | null {
  // Os caminhos apontam para fora de `web/` (`../data/...`), então o
  // Turbopack não consegue provar estaticamente que são um subcaminho do
  // projeto e, por padrão, tentaria rastrear/empacotar o repositório inteiro
  // no output do servidor. Isso é intencional aqui (self-hosted, não
  // serverless com limite de tamanho) — silenciado explicitamente via
  // turbopackIgnore, em vez de deixar o aviso genérico ou mudar o
  // comportamento em produção.
  for (const candidate of candidates) {
    if (fs.existsSync(/* turbopackIgnore: true */ candidate)) return candidate;
  }
  return null;
}

function resolveDatasetPath(): string {
  const encontrado = findExistingPath(DATASET_C_CANDIDATE_PATHS);
  if (encontrado) return encontrado;
  throw new Error(
    `Dataset C não encontrado em nenhum destes caminhos: ${DATASET_C_CANDIDATE_PATHS.join(
      ", ",
    )}. Rode o notebook notebooks/03_dataset_c_unificado_eda.ipynb (raiz do repo) para gerá-lo.`,
  );
}

function readRows(): DatasetCRow[] {
  const filePath = resolveDatasetPath();
  const raw = fs.readFileSync(/* turbopackIgnore: true */ filePath, "utf-8");
  return parse(raw, { columns: true, skip_empty_lines: true }) as DatasetCRow[];
}

/**
 * Fallback de deploy "standalone" (ver docs/PRD.md, Seção 11.2, item 5, e
 * `web/README.md`, "De onde vêm os dados"): quando o CSV do Dataset C não
 * está acessível no disco (ex.: `/web` implantado sem o resto do
 * monorepo), tenta ler um snapshot JSON pré-gerado por
 * `scripts/export_dashboard_data.py`. Retorna `null` (nunca dado
 * fabricado) se também não houver snapshot -- nesse caso o chamador deve
 * seguir para o erro explícito de `resolveDatasetPath()`.
 */
function lerSnapshotEstatico(): DatasetCSummary | null {
  const filePath = findExistingPath(DATASET_C_SNAPSHOT_CANDIDATE_PATHS);
  if (!filePath) return null;
  const raw = fs.readFileSync(/* turbopackIgnore: true */ filePath, "utf-8");
  const json: unknown = JSON.parse(raw);
  const validado = DatasetCSummarySchema.safeParse(json);
  if (!validado.success) {
    // Snapshot presente mas com forma incompatível (ex.: gerado por uma
    // versão antiga/futura de export_dashboard_data.py) -- tratado como
    // "sem snapshot utilizável", nunca repassado à UI quebrado ou com
    // campos faltando. O chamador cai para o erro explícito de dataset não
    // encontrado.
    console.error(
      `Snapshot em ${filePath} não tem a forma esperada de DatasetCSummary: ${validado.error.message}`,
    );
    return null;
  }
  return validado.data as DatasetCSummary;
}

// Exportadas (além de usadas internamente) para permitir testar a lógica de
// agregação em isolamento, sem precisar de um CSV real no disco — ver
// web/src/lib/__tests__/dataset-c.test.ts.
export function mesDe(dataPublicacao: string): string | null {
  // "data_publicacao" vem como "YYYY-MM-DD HH:MM:SS" ou "YYYY-MM-DD"
  const match = /^(\d{4})-(\d{2})/.exec(dataPublicacao ?? "");
  return match ? `${match[1]}-${match[2]}` : null;
}

export function buildSerieMensal(rows: DatasetCRow[]): SerieMensalPonto[] {
  const porMes = new Map<string, { ia: number; tradicional: number }>();

  for (const row of rows) {
    const mes = mesDe(row.data_publicacao);
    if (!mes) continue;
    const bucket = porMes.get(mes) ?? { ia: 0, tradicional: 0 };
    if (row.rotulo_ia === "IA") bucket.ia += 1;
    else bucket.tradicional += 1;
    porMes.set(mes, bucket);
  }

  return Array.from(porMes.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([mes, { ia, tradicional }]) => ({
      mes,
      ia,
      tradicional,
      total: ia + tradicional,
    }));
}

export function buildDistribuicaoFonte(rows: DatasetCRow[]): DistribuicaoFonte[] {
  const contagem = new Map<string, number>();
  for (const row of rows) {
    contagem.set(row.fonte_dataset, (contagem.get(row.fonte_dataset) ?? 0) + 1);
  }
  return Array.from(contagem.entries())
    .sort(([, a], [, b]) => b - a)
    .map(([fonte, n]) => ({ fonte, n }));
}

export function buildDistribuicaoTema(rows: DatasetCRow[]): DistribuicaoTema[] {
  const contagem = new Map<string, { n: number; n_ia: number }>();
  for (const row of rows) {
    const tema = row.categoria_tema?.trim() || "Não classificado";
    const bucket = contagem.get(tema) ?? { n: 0, n_ia: 0 };
    bucket.n += 1;
    if (row.rotulo_ia === "IA") bucket.n_ia += 1;
    contagem.set(tema, bucket);
  }
  return Array.from(contagem.entries())
    .sort(([, a], [, b]) => b.n - a.n)
    .slice(0, TOP_N_TEMAS)
    .map(([tema, { n, n_ia }]) => ({ tema, n, n_ia }));
}

export function buildDistribuicaoVeredito(rows: DatasetCRow[]): DistribuicaoVeredito[] {
  const contagem = new Map<string, number>();
  for (const row of rows) {
    const veredito = row.veredito_binario?.trim() || "nao_classificado";
    contagem.set(veredito, (contagem.get(veredito) ?? 0) + 1);
  }
  return Array.from(contagem.entries())
    .sort(([, a], [, b]) => b - a)
    .map(([veredito, n]) => ({ veredito, n }));
}

/**
 * Lê o Dataset C real do disco e computa os agregados do painel — chamado a
 * cada request. Se o CSV não estiver acessível, cai para o snapshot JSON
 * estático (deploy standalone — ver `lerSnapshotEstatico()` acima); só
 * propaga o erro de "dataset não encontrado" se nenhum dos dois existir.
 */
export function getDatasetCSummary(): DatasetCSummary {
  if (!findExistingPath(DATASET_C_CANDIDATE_PATHS)) {
    const snapshot = lerSnapshotEstatico();
    if (snapshot) return snapshot;
  }

  const rows = readRows();
  const nIA = rows.filter((r) => r.rotulo_ia === "IA").length;
  const nTradicional = rows.length - nIA;
  const nEditorial = rows.filter(
    (r) => r.fonte_rotulo_ia === "editorial_aos_fatos_tag",
  ).length;

  return {
    gerado_em: new Date().toISOString(),
    gerado_por: "web/src/lib/dataset-c.ts (leitura ao vivo, a cada request)",
    fonte_dados: "data/processed/dataset_c_unificado.csv (Datasets A + B unificados, Fase 2)",
    aviso:
      "Estes números refletem o estado atual de data/processed/dataset_c_unificado.csv " +
      "no disco — não um feed em tempo real das redes/institutos, e não um snapshot " +
      "manual: qualquer atualização do CSV (nova coleta + notebook 03 regerado) aparece " +
      "aqui automaticamente. A lente de IA usa rótulo editorial real apenas para itens " +
      "de origem 'B' (Aos Fatos); itens de origem 'A' não têm rótulo editorial de IA.",
    datas_turno_1: { "2018": "2018-10-07", "2022": "2022-10-02", "2026": "2026-10-04" },
    resumo_geral: {
      n_total: rows.length,
      n_ia: nIA,
      n_tradicional: nTradicional,
      pct_ia: rows.length ? Math.round((1000 * nIA) / rows.length) / 10 : null,
      n_rotulo_editorial_confiavel: nEditorial,
    },
    serie_mensal: buildSerieMensal(rows),
    distribuicao_por_fonte: buildDistribuicaoFonte(rows),
    distribuicao_por_tema: buildDistribuicaoTema(rows),
    distribuicao_veredito: buildDistribuicaoVeredito(rows),
  };
}

export interface ChecagemFeedItem {
  titulo: string;
  fonte: string;
  rotuloIA: boolean;
  tema: string;
  veredito: string;
  url: string;
  dataPublicacao: string | null;
}

/** Itens mais recentes do Dataset C, para o feed de checagens do painel (RF3.2). */
export function getChecagensRecentes(limit = 12): ChecagemFeedItem[] {
  const rows = readRows();
  return rows
    .filter((r) => mesDe(r.data_publicacao))
    .sort((a, b) => (b.data_publicacao ?? "").localeCompare(a.data_publicacao ?? ""))
    .slice(0, limit)
    .map((r) => ({
      titulo: r.titulo,
      fonte: r.fonte_dataset === "B" ? "Aos Fatos" : "TSE — Fato ou Boato",
      rotuloIA: r.rotulo_ia === "IA",
      tema: r.categoria_tema?.trim() || "Não classificado",
      veredito: r.veredito_binario?.trim() || "não classificado",
      url: r.url,
      dataPublicacao: r.data_publicacao || null,
    }));
}

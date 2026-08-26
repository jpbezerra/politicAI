import Link from "next/link";
import { getChecagensRecentes, getDatasetCSummary } from "@/lib/dataset-c";
import { obterIndiceTendencia } from "@/lib/models-client";
import { LENTES } from "@/lib/lentes";
import { LensCard } from "@/components/lens-card";
import { DisclaimerBanner } from "@/components/disclaimer-banner";
import { MonthlyVolumeChart } from "@/components/monthly-volume-chart";
import { ThemeDistributionChart } from "@/components/theme-distribution-chart";
import { TrendIndexChart } from "@/components/trend-index-chart";
import { ChecagensFeed } from "@/components/checagens-feed";
import { VEREDITO_LABEL, veredictoPredominante } from "@/lib/veredito-labels";
import type { IndiceTendenciaResponse } from "@/lib/types";

// Lê data/processed/dataset_c_unificado.csv direto do disco a cada request
// (ver web/src/lib/dataset-c.ts) — nunca cachear esta página estaticamente,
// senão uma atualização do dataset só apareceria depois de um novo build.
export const dynamic = "force-dynamic";

export default async function Home() {
  let summary;
  let checagens: ReturnType<typeof getChecagensRecentes> = [];
  let erroDados: string | null = null;
  let erroFeed: string | null = null;

  try {
    summary = getDatasetCSummary();
  } catch (e) {
    erroDados = e instanceof Error ? e.message : "Erro desconhecido ao ler o dataset.";
  }

  // Tentativa separada: getChecagensRecentes() precisa das linhas cruas do
  // CSV (não do snapshot agregado do modo standalone -- ver dataset-c.ts),
  // então pode falhar mesmo quando getDatasetCSummary() acima teve sucesso
  // via snapshot. Isolado num try/catch próprio para que essa falha não
  // derrube a página inteira e esconda o resumo/gráficos que já carregaram.
  try {
    // Busca um pool maior do que o exibido inicialmente -- o componente
    // pagina/filtra no cliente sem nova requisição (ver checagens-feed.tsx).
    checagens = getChecagensRecentes(60);
  } catch (e) {
    erroFeed = e instanceof Error ? e.message : "Erro desconhecido ao ler as checagens recentes.";
  }

  // Terceira tentativa independente: diferente do resumo/feed (lidos direto
  // do CSV/snapshot em disco), o índice de tendência depende do serviço
  // /models estar no ar (ver models-client.ts). Isolado em seu próprio
  // try/catch pelo mesmo motivo do erroFeed acima -- indisponibilidade do
  // /models não deve derrubar o resto do painel.
  const indiceTendencia: IndiceTendenciaResponse = await obterIndiceTendencia(6);

  return (
    <div className="space-y-10">
      <section>
        <h1 className="text-2xl font-semibold tracking-tight">
          Painel de percepção eleitoral
        </h1>
        <p className="mt-2 max-w-2xl text-black/70 dark:text-white/70">
          Cada lente mede uma coisa diferente e não deve ser confundida com
          as outras — volume de checagem não é intenção de voto, e
          conteúdo &ldquo;relacionado a IA&rdquo; não é sinônimo de
          &ldquo;decisivo para o resultado&rdquo;. Veja a{" "}
          <Link href="/metodologia" className="underline">
            metodologia completa
          </Link>
          .
        </p>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {LENTES.map((lente) => (
          <LensCard key={lente.id} lente={lente} />
        ))}
      </section>

      {erroDados || !summary ? (
        <DisclaimerBanner>
          Não foi possível carregar o Dataset C real ({erroDados}). Este
          painel não exibe dado simulado no lugar de dado real — rode o
          notebook <code>03_dataset_c_unificado_eda.ipynb</code> (raiz do
          repositório) para gerar <code>data/processed/dataset_c_unificado.csv</code>{" "}
          e recarregue a página.
        </DisclaimerBanner>
      ) : (
        <>
          <section className="space-y-4">
            <DisclaimerBanner>
              {summary.aviso} Lido em{" "}
              {new Date(summary.gerado_em).toLocaleString("pt-BR")} a partir
              de {summary.fonte_dados}.
            </DisclaimerBanner>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard label="Checagens no dataset" value={summary.resumo_geral.n_total} />
              <StatCard
                label="Relacionadas a IA"
                value={summary.resumo_geral.n_ia}
                hint={
                  summary.resumo_geral.pct_ia !== null
                    ? `${summary.resumo_geral.pct_ia}% do total`
                    : undefined
                }
              />
              <StatCard label="Tradicionais" value={summary.resumo_geral.n_tradicional} />
              <StatCard
                label="Com rótulo editorial confiável"
                value={summary.resumo_geral.n_rotulo_editorial_confiavel}
                hint="Aos Fatos (Dataset B)"
              />
              {(() => {
                // RF3.1 (docs/PRD.md, Seção 6.1/15) promete "veredito
                // predominante" no resumo executivo -- `distribuicao_veredito`
                // já vinha no JSON do resumo, mas nunca tinha sido usado para
                // exibir esse card. Corrigido aqui.
                const predominante = veredictoPredominante(summary.distribuicao_veredito);
                return predominante ? (
                  <StatCard
                    label="Veredito predominante"
                    value={VEREDITO_LABEL[predominante.veredito] ?? predominante.veredito}
                    hint={`${predominante.pct}% das checagens (${predominante.n.toLocaleString("pt-BR")})`}
                  />
                ) : null;
              })()}
            </div>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-medium">Volume mensal de checagens</h2>
            <div className="rounded-xl border border-black/10 p-4 dark:border-white/10">
              <MonthlyVolumeChart
                data={summary.serie_mensal}
                datasTurno1={summary.datas_turno_1}
              />
            </div>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-medium">Principais temas checados</h2>
            <div className="rounded-xl border border-black/10 p-4 dark:border-white/10">
              <ThemeDistributionChart data={summary.distribuicao_por_tema} />
            </div>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-medium">
              Índice de tendência de desinformação por IA
            </h2>
            {indiceTendencia.ok ? (
              <>
                <DisclaimerBanner>
                  {indiceTendencia.aviso} Método usado nesta execução:{" "}
                  <strong>{indiceTendencia.metodo}</strong> ({indiceTendencia.n_observacoes}{" "}
                  meses observados).
                  {!indiceTendencia.calendario_disponivel && (
                    <>
                      {" "}
                      Contextualização com calendário eleitoral indisponível
                      nesta execução do serviço de modelo — nenhum marco de
                      1º turno é mostrado no gráfico abaixo.
                    </>
                  )}
                </DisclaimerBanner>
                <div className="rounded-xl border border-black/10 p-4 dark:border-white/10">
                  <TrendIndexChart
                    pontos={indiceTendencia.pontos}
                    marcosEleitorais={indiceTendencia.marcos_eleitorais}
                  />
                </div>
              </>
            ) : (
              <p className="rounded-xl border border-black/10 px-4 py-4 text-sm text-black/60 dark:border-white/10 dark:text-white/60">
                Índice de tendência indisponível nesta execução — depende do
                serviço <code>/models</code> estar no ar ({indiceTendencia.erro}
                ).
              </p>
            )}
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-medium">Checagens mais recentes</h2>
            <div className="rounded-xl border border-black/10 px-4 dark:border-white/10">
              {erroFeed ? (
                <p className="py-4 text-sm text-black/60 dark:text-white/60">
                  Feed de checagens individuais indisponível neste modo — depende
                  do CSV completo do Dataset C, não só do resumo agregado ({erroFeed}).
                </p>
              ) : (
                <ChecagensFeed itens={checagens} />
              )}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

function StatCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: number | string;
  hint?: string;
}) {
  return (
    <div className="rounded-xl border border-black/10 p-4 dark:border-white/10">
      <p className="text-xs uppercase tracking-wide text-black/50 dark:text-white/50">
        {label}
      </p>
      <p className="mt-1 text-2xl font-semibold">
        {typeof value === "number" ? value.toLocaleString("pt-BR") : value}
      </p>
      {hint && <p className="mt-0.5 text-xs text-black/40 dark:text-white/40">{hint}</p>}
    </div>
  );
}

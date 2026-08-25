"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { SerieMensalPonto } from "@/lib/types";

/**
 * Volume mensal de checagens (IA vs. Tradicional), dado real do Dataset C.
 * Réplica, em formato de componente web, dos gráficos do notebook 02/03.
 *
 * CORREÇÃO (docs/PRD.md, Seção 15/RF3.3): `datasTurno1` já existia em
 * `DatasetCSummary` desde a Fase 3, mas nunca era passado a este
 * componente nem desenhado no gráfico — RF3.3 ("gráfico de série temporal
 * com calendário eleitoral") estava marcado como implementado sem que
 * nenhuma data de turno aparecesse de fato na UI. Corrigido: quando o mês
 * de um 1º turno cai dentro do intervalo de meses exibido, uma linha de
 * referência vertical marca esse mês.
 */
function resumoTextual(
  data: SerieMensalPonto[],
  marcosEleitorais: { ano: string; mes: string }[],
): string {
  if (data.length === 0) return "Sem dados de volume mensal disponíveis.";
  const totalIA = data.reduce((soma, p) => soma + p.ia, 0);
  const totalTradicional = data.reduce((soma, p) => soma + p.tradicional, 0);
  const marcosTexto =
    marcosEleitorais.length > 0
      ? ` Marcos de 1º turno eleitoral dentro do período: ${marcosEleitorais
          .map((m) => m.ano)
          .join(", ")}.`
      : "";
  return (
    `Gráfico de barras empilhadas do volume mensal de checagens, de ` +
    `${data[0].mes} a ${data[data.length - 1].mes}: ${totalTradicional} ` +
    `checagens tradicionais e ${totalIA} relacionadas a IA no total do ` +
    `período.${marcosTexto}`
  );
}

/**
 * Filtra `datasTurno1` (ano -> data ISO do 1º turno) para só os anos cujo
 * mês cai dentro do intervalo de meses efetivamente exibido em `data` —
 * um marco fora do intervalo (ex.: 2018 num gráfico que só cobre
 * 2023-2026) não deve ser desenhado como se estivesse presente. Extraído
 * como função pura (não só lógica inline no componente) para ser testável
 * sem depender de renderização de SVG do Recharts em jsdom — ver
 * `__tests__/monthly-volume-chart.test.ts`.
 */
export function marcosEleitoraisVisiveis(
  data: SerieMensalPonto[],
  datasTurno1?: Record<string, string>,
): { ano: string; mes: string }[] {
  const mesesNoGrafico = new Set(data.map((p) => p.mes));
  return Object.entries(datasTurno1 ?? {})
    .map(([ano, dataIso]) => ({ ano, mes: dataIso.slice(0, 7) }))
    .filter((marco) => mesesNoGrafico.has(marco.mes));
}

export function MonthlyVolumeChart({
  data,
  datasTurno1,
}: {
  data: SerieMensalPonto[];
  /** `DatasetCSummary.datas_turno_1` — ano (string) -> data ISO do 1º turno. */
  datasTurno1?: Record<string, string>;
}) {
  const marcosEleitorais = marcosEleitoraisVisiveis(data, datasTurno1);

  return (
    <div role="img" aria-label={resumoTextual(data, marcosEleitorais)}>
      <ResponsiveContainer width="100%" height={280}>
        {/* margin.top maior que os outros lados de propósito: o label do
            ReferenceLine ("1º turno YYYY") é desenhado acima da área do
            gráfico, e com pouco espaço ele ficava cortado/sobreposto ao
            valor máximo do eixo Y (achado no deploy real, ver
            docs/PRD.md Seção 16/18). */}
        <BarChart data={data} margin={{ top: 28, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
          <XAxis
            dataKey="mes"
            tick={{ fontSize: 10 }}
            interval={Math.max(0, Math.floor(data.length / 12))}
          />
          <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
          <Tooltip
            contentStyle={{ fontSize: 12, borderRadius: 8 }}
            labelFormatter={(mes) => `Mês: ${mes}`}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="tradicional" stackId="a" name="Tradicional" fill="#94a3b8" />
          <Bar dataKey="ia" stackId="a" name="Relacionado a IA" fill="#f59e0b" />
          {marcosEleitorais.map((marco) => (
            <ReferenceLine
              key={marco.ano}
              x={marco.mes}
              stroke="#dc2626"
              strokeDasharray="3 3"
              label={{
                value: `1º turno ${marco.ano}`,
                position: "top",
                fontSize: 10,
                fill: "#dc2626",
              }}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

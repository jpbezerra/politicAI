"use client";

import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { MarcoEleitoral, PontoIndiceTendencia } from "@/lib/types";

/**
 * Índice de tendência de desinformação por IA (`/forecast/index`), com
 * marcadores de 1º turno eleitoral (RF2.4, docs/PRD.md Seção 5.2/15).
 * Linha sólida = volume observado real (Dataset B); linha tracejada +
 * faixa sombreada = projeção e intervalo de confiança (95%) da média
 * mensal projetada — nunca um valor único apresentado como certeza.
 */
function resumoTextual(
  pontos: PontoIndiceTendencia[],
  marcos: MarcoEleitoral[],
): string {
  if (pontos.length === 0) {
    return "Sem dados de índice de tendência disponíveis.";
  }
  const observados = pontos.filter((p) => p.volume_ia !== null);
  const projetados = pontos.filter((p) => p.volume_ia_projetado !== null);
  const marcosTexto =
    marcos.length > 0
      ? ` Marcos de 1º turno eleitoral dentro do período: ${marcos
          .map((m) => `${m.ano} (${m.data_1_turno})`)
          .join(", ")}.`
      : "";
  return (
    `Gráfico de linha do índice de tendência de desinformação por IA, de ` +
    `${pontos[0].mes} a ${pontos[pontos.length - 1].mes}: ${observados.length} ` +
    `meses observados e ${projetados.length} meses projetados, com faixa de ` +
    `incerteza de 95% nos meses projetados.${marcosTexto}`
  );
}

export function TrendIndexChart({
  pontos,
  marcosEleitorais,
}: {
  pontos: PontoIndiceTendencia[];
  marcosEleitorais: MarcoEleitoral[];
}) {
  const dados = pontos.map((p) => ({
    ...p,
    faixa:
      p.limite_inferior !== null && p.limite_superior !== null
        ? ([p.limite_inferior, p.limite_superior] as [number, number])
        : undefined,
  }));

  return (
    <div role="img" aria-label={resumoTextual(pontos, marcosEleitorais)}>
      <ResponsiveContainer width="100%" height={280}>
        {/* margin.top maior que os outros lados: o label do ReferenceLine
            ("1º turno YYYY") é desenhado acima da área do gráfico e
            ficava cortado/sobreposto ao eixo Y com pouco espaço — mesmo
            ajuste feito em monthly-volume-chart.tsx (ver docs/PRD.md
            Seção 16/18). */}
        <ComposedChart data={dados} margin={{ top: 28, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
          <XAxis
            dataKey="mes"
            tick={{ fontSize: 10 }}
            interval={Math.max(0, Math.floor(dados.length / 12))}
          />
          <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
          <Tooltip
            contentStyle={{ fontSize: 12, borderRadius: 8 }}
            labelFormatter={(mes) => `Mês: ${mes}`}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Area
            dataKey="faixa"
            name="Intervalo de confiança (95%)"
            stroke="none"
            fill="#f59e0b"
            fillOpacity={0.15}
            connectNulls
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="volume_ia"
            name="Observado"
            stroke="#0f172a"
            strokeWidth={2}
            dot={{ r: 2 }}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="volume_ia_projetado"
            name="Projetado"
            stroke="#f59e0b"
            strokeWidth={2}
            strokeDasharray="5 4"
            dot={{ r: 2 }}
            connectNulls={false}
          />
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
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

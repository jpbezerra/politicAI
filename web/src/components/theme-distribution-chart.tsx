"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { DistribuicaoTema } from "@/lib/types";

function resumoTextual(data: DistribuicaoTema[]): string {
  if (data.length === 0) return "Sem dados de temas disponíveis.";
  const principais = data
    .slice(0, 3)
    .map((d) => `${d.tema} (${d.n})`)
    .join(", ");
  return `Gráfico de barras horizontais dos principais temas checados. Os três maiores: ${principais}.`;
}

export function ThemeDistributionChart({ data }: { data: DistribuicaoTema[] }) {
  const chartData = [...data].sort((a, b) => b.n - a.n);

  return (
    <div role="img" aria-label={resumoTextual(chartData)}>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 8, right: 16, left: 8, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
          <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
          <YAxis
            type="category"
            dataKey="tema"
            tick={{ fontSize: 11 }}
            width={170}
          />
          <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
          <Bar dataKey="n" name="Total de checagens" fill="#64748b" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

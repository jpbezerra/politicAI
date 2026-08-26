/**
 * Rótulos legíveis para `veredito_binario` (Dataset C), compartilhados
 * pelo feed de checagens (`checagens-feed.tsx`) e pelo card de "veredito
 * predominante" do resumo executivo (`app/page.tsx`, RF3.1). Centralizado
 * aqui para não duplicar o mesmo dicionário nos dois lugares — mesmo
 * princípio já aplicado a `scripts/election_calendar.py` (ver
 * docs/PRD.md, Seção 11.1, item 9).
 */
export const VEREDITO_LABEL: Record<string, string> = {
  falso: "Falso",
  parcialmente_falso: "Parcialmente falso",
  nao_falso: "Não falso",
  nao_classificado: "Não classificado",
};

/**
 * Veredito predominante do resumo executivo (RF3.1, docs/PRD.md Seção
 * 6.1/15) -- CORREÇÃO: `distribuicao_veredito` já era calculado e enviado
 * no JSON do resumo desde a Fase 3, mas nunca era usado para exibir o
 * "veredito predominante" que RF3.1 promete; a única aparição de veredito
 * na UI era por item individual no feed. Função pura para ser testável
 * sem depender da página inteira.
 */
export function veredictoPredominante(
  distribuicao: { veredito: string; n: number }[],
): { veredito: string; n: number; pct: number } | null {
  if (distribuicao.length === 0) return null;
  const total = distribuicao.reduce((soma, d) => soma + d.n, 0);
  if (total === 0) return null;
  const predominante = distribuicao.reduce((maior, atual) =>
    atual.n > maior.n ? atual : maior,
  );
  return {
    veredito: predominante.veredito,
    n: predominante.n,
    pct: Math.round((predominante.n / total) * 1000) / 10,
  };
}

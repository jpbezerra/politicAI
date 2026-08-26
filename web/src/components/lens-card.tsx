import type { LenteInfo } from "@/lib/types";

export function LensCard({ lente }: { lente: LenteInfo }) {
  const emConstrucao = lente.status === "em_construcao";

  return (
    <div
      className={`rounded-xl border p-4 ${
        emConstrucao
          ? "border-dashed border-black/15 bg-black/[0.02] dark:border-white/15 dark:bg-white/[0.02]"
          : "border-black/10 bg-white dark:border-white/10 dark:bg-white/5"
      }`}
    >
      <div className="mb-1 flex items-center justify-between gap-2">
        <h3 className="font-medium">{lente.titulo}</h3>
        {emConstrucao ? (
          <span className="whitespace-nowrap rounded-full bg-black/10 px-2 py-0.5 text-[11px] font-medium text-black/60 dark:bg-white/10 dark:text-white/60">
            Em construção — dado ainda não integrado
          </span>
        ) : (
          <span className="whitespace-nowrap rounded-full bg-emerald-500/15 px-2 py-0.5 text-[11px] font-medium text-emerald-700 dark:text-emerald-400">
            Dado real
          </span>
        )}
      </div>
      <p className="text-sm text-black/70 dark:text-white/70">{lente.descricao}</p>
      <p className="mt-2 text-xs text-black/40 dark:text-white/40">
        Fonte: {lente.fonte}
      </p>
    </div>
  );
}

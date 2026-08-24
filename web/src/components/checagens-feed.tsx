"use client";

import { useMemo, useState } from "react";
import type { ChecagemFeedItem } from "@/lib/dataset-c";
import { VEREDITO_LABEL } from "@/lib/veredito-labels";

const PAGINA_TAMANHO = 12;

/**
 * Feed de checagens recentes (RF3.2), com paginação client-side ("carregar
 * mais") e um filtro opcional para só itens relacionados a IA — os dados já
 * chegam inteiros do servidor (`getChecagensRecentes`, até um limite fixo),
 * então paginar/filtrar aqui não faz nenhuma requisição nova. Ver
 * docs/PRD.md, backlog de melhorias, item "paginação/filtro no feed".
 */
export function ChecagensFeed({ itens }: { itens: ChecagemFeedItem[] }) {
  const [somenteIA, setSomenteIA] = useState(false);
  const [quantidadeVisivel, setQuantidadeVisivel] = useState(PAGINA_TAMANHO);

  const itensFiltrados = useMemo(
    () => (somenteIA ? itens.filter((i) => i.rotuloIA) : itens),
    [itens, somenteIA],
  );
  const itensVisiveis = itensFiltrados.slice(0, quantidadeVisivel);
  const temMais = quantidadeVisivel < itensFiltrados.length;

  if (itens.length === 0) {
    return (
      <p className="py-3 text-sm text-black/50 dark:text-white/50">
        Nenhuma checagem com data disponível para exibir.
      </p>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between gap-3 py-3">
        <label className="flex items-center gap-2 text-xs text-black/60 dark:text-white/60">
          <input
            type="checkbox"
            checked={somenteIA}
            onChange={(e) => {
              setSomenteIA(e.target.checked);
              setQuantidadeVisivel(PAGINA_TAMANHO);
            }}
            className="h-3.5 w-3.5"
          />
          Mostrar só relacionadas a IA
        </label>
        <span className="text-[11px] text-black/40 dark:text-white/40">
          {itensFiltrados.length} checagem{itensFiltrados.length === 1 ? "" : "s"}
        </span>
      </div>

      {itensFiltrados.length === 0 ? (
        <p className="py-3 text-sm text-black/50 dark:text-white/50">
          Nenhuma checagem relacionada a IA entre as mais recentes carregadas.
        </p>
      ) : (
        <ul className="divide-y divide-black/10 dark:divide-white/10">
          {itensVisiveis.map((item, i) => (
            <li key={`${item.url}-${i}`} className="py-3">
              <div className="mb-1 flex flex-wrap items-center gap-2">
                {item.rotuloIA && (
                  <span className="rounded-full bg-amber-500/15 px-2 py-0.5 text-[11px] font-medium text-amber-700 dark:text-amber-400">
                    Relacionado a IA
                  </span>
                )}
                <span className="text-[11px] text-black/40 dark:text-white/40">
                  {item.fonte}
                  {item.dataPublicacao ? ` · ${item.dataPublicacao.slice(0, 10)}` : ""}
                </span>
              </div>
              <a
                href={item.url}
                target="_blank"
                rel="noreferrer"
                className="text-sm font-medium leading-snug hover:underline"
              >
                {item.titulo}
              </a>
              <p className="mt-0.5 text-xs text-black/50 dark:text-white/50">
                {item.tema} · veredito: {VEREDITO_LABEL[item.veredito] ?? item.veredito}
              </p>
            </li>
          ))}
        </ul>
      )}

      {temMais && (
        <div className="py-3 text-center">
          <button
            type="button"
            onClick={() => setQuantidadeVisivel((n) => n + PAGINA_TAMANHO)}
            className="rounded-full border border-black/15 px-4 py-1.5 text-xs font-medium hover:bg-black/5 dark:border-white/15 dark:hover:bg-white/10"
          >
            Carregar mais ({itensFiltrados.length - quantidadeVisivel} restantes)
          </button>
        </div>
      )}
    </div>
  );
}

export { VEREDITO_LABEL };

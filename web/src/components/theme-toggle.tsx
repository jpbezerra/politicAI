"use client";

import { useSyncExternalStore } from "react";

type Tema = "light" | "dark";

const EVENTO_TEMA_ALTERADO = "tema-alterado";

function getSnapshot(): Tema {
  return document.documentElement.classList.contains("dark") ? "dark" : "light";
}

// Usado só durante SSR e na primeira renderização no cliente (antes de
// hidratar) -- o servidor não conhece a preferência do usuário. O script
// inline em `layout.tsx` já aplica a classe correta em `<html>` antes da
// hidratação; `useSyncExternalStore` então troca para o valor real
// (`getSnapshot`) assim que o React sincroniza com o DOM, sem precisar de um
// `useEffect` chamando `setState` manualmente (e sem o "flash" de conteúdo
// divergente entre servidor e cliente que isso causaria).
function getServerSnapshot(): Tema {
  return "light";
}

function subscribe(callback: () => void) {
  document.addEventListener(EVENTO_TEMA_ALTERADO, callback);
  return () => document.removeEventListener(EVENTO_TEMA_ALTERADO, callback);
}

/**
 * Alterna manualmente entre claro/escuro, sobrescrevendo a preferência do
 * sistema. A escolha é persistida em localStorage (client-side, por
 * navegador) e aplicada via classe `dark`/`light` em `<html>` — ver o script
 * inline em `layout.tsx` que aplica a escolha salva (ou a preferência do
 * sistema, na primeira visita) antes da primeira renderização, evitando um
 * "flash" do tema errado.
 */
export function ThemeToggle() {
  const tema = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  function alternar() {
    const novo: Tema = tema === "dark" ? "light" : "dark";
    document.documentElement.classList.remove("dark", "light");
    document.documentElement.classList.add(novo);
    try {
      localStorage.setItem("tema", novo);
    } catch {
      // localStorage indisponível (modo privado, etc.) -- a escolha só vale
      // para esta navegação, sem persistir. Não é um erro que precise de
      // tratamento visível ao usuário.
    }
    // Não há evento nativo de "a classe do <html> mudou" -- como só este
    // componente altera a classe, disparamos manualmente para que
    // `useSyncExternalStore` re-leia o snapshot.
    document.dispatchEvent(new Event(EVENTO_TEMA_ALTERADO));
  }

  return (
    <button
      type="button"
      onClick={alternar}
      aria-label={tema === "dark" ? "Mudar para tema claro" : "Mudar para tema escuro"}
      aria-pressed={tema === "dark"}
      className="rounded-full border border-black/10 p-2 text-sm hover:bg-black/5 dark:border-white/10 dark:hover:bg-white/10"
    >
      <span aria-hidden="true">{tema === "dark" ? "☀️" : "🌙"}</span>
    </button>
  );
}

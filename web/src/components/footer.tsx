import Link from "next/link";

export function Footer() {
  return (
    <footer className="mt-auto border-t border-black/10 px-6 py-6 text-xs text-black/50 dark:border-white/10 dark:text-white/50">
      <div className="mx-auto max-w-5xl space-y-1">
        <p>
          Dados públicos, leitura transparente. Projeto de pesquisa sobre o
          impacto de desinformação gerada por IA nas eleições brasileiras.
        </p>
        <p>
          Inspirado, em parte, na plataforma{" "}
          <a
            href="https://lentes-da-eleicao-brasil.maria514774.chatgpt.site"
            target="_blank"
            rel="noreferrer"
            className="underline"
          >
            Lentes da Eleição 2026
          </a>{" "}
          (profa. Maria do Carmo Soares de Lima, UFPE). Veja{" "}
          <Link href="/metodologia" className="underline">
            metodologia e limitações
          </Link>
          .
        </p>
      </div>
    </footer>
  );
}

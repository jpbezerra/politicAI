import type { Metadata } from "next";
import { Nav } from "@/components/nav";
import { Footer } from "@/components/footer";
import "./globals.css";

export const metadata: Metadata = {
  title: "Lentes contra a Desinformação | Painel eleitoral + Sensor de IA",
  description:
    "Painel de percepção eleitoral com sinalização explícita de conteúdo relacionado a IA, e uma ferramenta interativa para estimar se um texto foi gerado por IA.",
};

// Aplica o tema (claro/escuro) em <html> ANTES da primeira renderização,
// para evitar um "flash" do tema errado: usa a escolha salva pelo usuário
// (ThemeToggle) se existir, senão segue a preferência do sistema. Roda
// síncrono e bem cedo por ser inline -- não pode virar um módulo importado.
const THEME_INIT_SCRIPT = `
(function () {
  try {
    var salvo = localStorage.getItem("tema");
    var escuro = salvo ? salvo === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
    document.documentElement.classList.add(escuro ? "dark" : "light");
  } catch (e) {
    // localStorage/matchMedia indisponível -- deixa o CSS puro (media query) decidir.
  }
})();
`;

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    // suppressHydrationWarning é necessário aqui porque THEME_INIT_SCRIPT
    // (abaixo) adiciona a classe "dark"/"light" a este elemento ANTES da
    // hidratação, com base em localStorage/prefers-color-scheme -- o React
    // não tem como saber esse valor durante o render no servidor, então sem
    // isto ele acusaria (incorretamente) uma divergência de hidratação toda
    // vez que o tema do cliente for diferente do HTML renderizado no
    // servidor. Afeta só o atributo class deste elemento, não os filhos.
    <html lang="pt-BR" className="h-full antialiased" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body className="min-h-full flex flex-col">
        <a href="#conteudo-principal" className="skip-link">
          Pular para o conteúdo principal
        </a>
        <Nav />
        <main
          id="conteudo-principal"
          className="mx-auto w-full max-w-5xl flex-1 px-6 py-8"
        >
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}

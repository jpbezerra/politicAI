import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ChecagensFeed } from "@/components/checagens-feed";
import type { ChecagemFeedItem } from "@/lib/dataset-c";

function makeItem(overrides: Partial<ChecagemFeedItem> = {}): ChecagemFeedItem {
  return {
    titulo: "Título de teste",
    fonte: "Aos Fatos",
    rotuloIA: false,
    tema: "eleicoes",
    veredito: "falso",
    url: "https://example.com/checagem",
    dataPublicacao: "2025-01-01",
    ...overrides,
  };
}

describe("ChecagensFeed", () => {
  it("mostra mensagem quando não há itens", () => {
    render(<ChecagensFeed itens={[]} />);
    expect(screen.getByText(/nenhuma checagem/i)).toBeInTheDocument();
  });

  it("mostra o selo 'Relacionado a IA' só para itens rotulados como IA", () => {
    render(
      <ChecagensFeed
        itens={[makeItem({ titulo: "Item IA", rotuloIA: true }), makeItem({ titulo: "Item Trad" })]}
      />,
    );
    expect(screen.getAllByText("Relacionado a IA")).toHaveLength(1);
    expect(screen.getByText("Item IA")).toBeInTheDocument();
    expect(screen.getByText("Item Trad")).toBeInTheDocument();
  });

  it("filtra para só IA quando o checkbox é marcado", () => {
    render(
      <ChecagensFeed
        itens={[makeItem({ titulo: "Item IA", rotuloIA: true }), makeItem({ titulo: "Item Trad" })]}
      />,
    );
    fireEvent.click(screen.getByLabelText(/mostrar só relacionadas a ia/i));
    expect(screen.getByText("Item IA")).toBeInTheDocument();
    expect(screen.queryByText("Item Trad")).not.toBeInTheDocument();
  });

  it("pagina os itens, mostrando 'carregar mais' quando há mais de 12", () => {
    const itens = Array.from({ length: 15 }, (_, i) => makeItem({ titulo: `Item ${i}`, url: `https://example.com/${i}` }));
    render(<ChecagensFeed itens={itens} />);

    expect(screen.getByText("Item 0")).toBeInTheDocument();
    expect(screen.queryByText("Item 12")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /carregar mais/i }));
    expect(screen.getByText("Item 12")).toBeInTheDocument();
  });
});

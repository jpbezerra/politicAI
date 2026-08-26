import Link from "next/link";
import { getDatasetCSummary } from "@/lib/dataset-c";

export const metadata = {
  title: "Metodologia | Lentes contra a Desinformação",
};

// Mesma leitura ao vivo do painel (ver web/src/lib/dataset-c.ts) — a data
// de "lido em" abaixo só faz sentido se a página nunca ficar em cache.
export const dynamic = "force-dynamic";

export default function MetodologiaPage() {
  let summary: ReturnType<typeof getDatasetCSummary> | null = null;
  try {
    summary = getDatasetCSummary();
  } catch {
    // Segue sem os números ao vivo — o texto da página continua válido
    // mesmo se o CSV não estiver disponível neste ambiente.
  }

  return (
    <article className="max-w-none space-y-5 text-black/80 [&_a]:underline [&_h2]:mt-8 [&_h2]:text-lg [&_h2]:font-semibold [&_h2]:text-black [&_li]:mt-1 [&_p]:leading-relaxed [&_ul]:list-disc [&_ul]:space-y-1 [&_ul]:pl-5 dark:text-white/80 dark:[&_h2]:text-white">
      <h1 className="text-2xl font-semibold tracking-tight text-black dark:text-white">
        Metodologia e limitações
      </h1>

      <p>
        Esta página resume, em linguagem acessível, a proveniência de cada
        indicador exibido no painel e no Sensor de IA. O detalhamento
        completo — incluindo testes estatísticos, notebooks e o histórico
        de correções metodológicas já feitas neste projeto — está em{" "}
        <code>docs/PRD.md</code> e nos notebooks 01–03 do repositório.
      </p>

      <h2>De onde vêm os dados</h2>
      <p>
        O painel é construído sobre o <strong>Dataset C</strong>, uma
        unificação de dois conjuntos coletados diretamente de fontes
        públicas:
      </p>
      <ul>
        <li>
          <strong>Dataset A</strong> — 228 itens do sistema &ldquo;Fato ou
          Boato&rdquo; da Justiça Eleitoral, publicados entre 01/01/2022 e
          20/08/2026 (recorte temporal aplicado a pedido da orientadora do
          projeto — a coleta completa tem 322 itens, de 2018 em diante; ver{" "}
          <code>docs/PRD.md</code>, Seção 19). Não tem rótulo editorial de IA
          (0 itens rotulados IA nesta fonte).
        </li>
        <li>
          <strong>Dataset B</strong> — 541 itens de checagens do Aos Fatos no
          mesmo período (01/01/2022 a 20/08/2026; a coleta completa tem 553),
          incluindo a tag editorial de IA (122 itens rotulados como
          relacionados a conteúdo gerado/manipulado por IA — nenhum item foi
          perdido nesse grupo pelo recorte).
        </li>
      </ul>
      <p>
        {summary ? (
          <>
            Estes números foram lidos <strong>direto do CSV</strong> em{" "}
            <strong>{new Date(summary.gerado_em).toLocaleString("pt-BR")}</strong>{" "}
            (agora, ao carregar esta página) a partir de{" "}
            <code>{summary.fonte_dados}</code>. Não é um feed em tempo real
            das redes sociais ou institutos — é o estado atual do arquivo no
            disco: assim que uma nova coleta atualizar esse CSV (rodando o
            pipeline de coleta e o notebook{" "}
            <code>03_dataset_c_unificado_eda.ipynb</code>), o painel reflete
            os novos números automaticamente, sem nenhum passo manual
            adicional.
          </>
        ) : (
          <>
            O dataset real não pôde ser lido neste ambiente — ver o aviso na{" "}
            <Link href="/">página inicial</Link>.
          </>
        )}
      </p>

      <h2>A distinção mais importante: temática vs. autoria</h2>
      <p>
        O rótulo &ldquo;Relacionado a IA&rdquo; usado no painel e no Sensor
        de IA (v0) indica que uma checagem de fatos <em>trata de</em> um
        boato sobre conteúdo manipulado por IA (por exemplo, um vídeo
        deepfake ou um áudio clonado). Isso é diferente de dizer que{" "}
        <em>o texto da checagem em si</em> foi escrito por um modelo de
        linguagem — a própria checagem é sempre escrita por um jornalista
        humano, mesmo quando o assunto é um deepfake.
      </p>
      <p>
        Por isso, o Sensor de IA desta versão (v0) é rotulado como um{" "}
        <strong>classificador de temática</strong>, não como um{" "}
        <strong>detector de autoria</strong>. Um detector geral de autoria
        por IA — capaz de dizer se um texto qualquer foi escrito por um
        modelo de linguagem — está no roadmap (v1) e depende da coleta de
        um novo conjunto de dados pareado (textos humanos vs. textos
        gerados por IA sobre os mesmos temas políticos), que ainda não
        existe neste repositório.
      </p>

      <h2>Limitações conhecidas</h2>
      <ul>
        <li>
          <strong>Amostra pequena do grupo IA:</strong> 122 itens até a
          última coleta, concentrados em uma única fonte editorial (Aos
          Fatos). Qualquer diferença percentual entre grupos IA e
          Tradicional deve ser lida como indicativa, não como estatisticamente
          robusta para inferências causais.
        </li>
        <li>
          <strong>Viés de desenho amostral:</strong> a comparação de
          proximidade temporal com a eleição (dias até o pleito) foi
          originalmente confundida pelo próprio desenho de coleta — corrigida
          nos notebooks com uma comparação em janelas temporais equivalentes.
          Ver notebook <code>02_dataset_b_aosfatos_eda.ipynb</code>, Seção 4.5.
        </li>
        <li>
          <strong>Unificação não aumenta poder estatístico para IA:</strong>{" "}
          somente o Dataset B tem itens rotulados como IA — unir A e B
          aumenta a cobertura temática geral, mas não o N de itens IA
          disponíveis para comparação.
        </li>
        <li>
          <strong>Lentes ainda não integradas:</strong> buscadores, redes
          sociais e institutos de pesquisa aparecem no painel apenas como
          &ldquo;em construção&rdquo; — nenhum número mockado é exibido no
          lugar de dado real.
        </li>
      </ul>

      <h2>Sobre a plataforma de referência</h2>
      <p>
        A organização em &ldquo;lentes&rdquo; independentes deste painel foi
        inspirada na plataforma{" "}
        <a
          href="https://lentes-da-eleicao-brasil.maria514774.chatgpt.site"
          target="_blank"
          rel="noreferrer"
        >
          Lentes da Eleição 2026
        </a>
        , desenvolvida pela professora orientadora deste projeto (Maria do
        Carmo Soares de Lima, UFPE). O diferencial deste protótipo é a
        lente de IA e o Sensor de IA interativo — funcionalidades que a
        plataforma de referência não possui.
      </p>

      <p>
        Para o detalhamento completo de requisitos, roadmap e riscos éticos,
        veja <code>docs/PRD.md</code> no repositório do projeto.
      </p>
    </article>
  );
}

import path from "node:path";
import type { NextConfig } from "next";

/**
 * Permite que `/` e `/metodologia` leiam `../data/processed/dataset_c_unificado.csv`
 * DE VERDADE em produção no Vercel, sem depender só do snapshot estático
 * (`src/data/dataset_c_summary.json`, ver `dataset-c.ts`).
 *
 * Por que isso é necessário: o Output File Tracing do Next (`@vercel/nft`)
 * decide quais arquivos vão para o pacote de cada função serverless
 * analisando estaticamente `fs`/`import`/`require` no código — mas
 * `dataset-c.ts` monta o caminho do CSV em runtime
 * (`path.join(process.cwd(), "..", "data", ...)`), então o tracer não
 * consegue inferir sozinho essa dependência (por isso o código já tinha
 * `/* turbopackIgnore: true *\/` nos `fs.existsSync`/`readFileSync` — aquilo
 * só silencia um aviso de build do Turbopack, não resolve o que é
 * empacotado para produção). `outputFileTracingIncludes` supre isso
 * explicitamente; `outputFileTracingRoot` sobe a raiz de tracing para a
 * raiz do monorepo (`web/` é só um dos pacotes), já que por padrão o Next
 * trata o diretório do projeto (`web/`) como raiz e recusaria incluir
 * qualquer arquivo fora dele.
 *
 * Pré-requisito no painel do Vercel (não é código, é configuração do
 * projeto): com "Root Directory" = `web`, é preciso habilitar "Include
 * source files outside of the Root Directory in the Build Step" em
 * Project Settings → General — sem isso o Vercel nem baixa `../data/` no
 * ambiente de build, e nenhuma configuração aqui resolve isso.
 *
 * O fallback para o snapshot estático em `dataset-c.ts` continua existindo
 * de propósito, como rede de segurança: se essa configuração de tracing
 * algum dia sair de sincronia com o código (ex.: um novo arquivo de dados
 * lido sem ser adicionado aqui) ou o toggle acima não estiver marcado, o
 * painel ainda degrada para o snapshot em vez de mostrar erro — nunca
 * dado inventado, mas também nunca uma falha silenciosa e total.
 */
const nextConfig: NextConfig = {
  outputFileTracingRoot: path.join(__dirname, ".."),
  outputFileTracingIncludes: {
    "/": ["../data/processed/dataset_c_unificado.csv"],
    "/metodologia": ["../data/processed/dataset_c_unificado.csv"],
  },
};

export default nextConfig;

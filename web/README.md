# `/web` — Painel eleitoral + Sensor de IA

Plataforma Next.js (App Router + TypeScript + Tailwind) descrita em
[`docs/PRD.md`](../docs/PRD.md), Seção 5. Duas funcionalidades principais:

1. **Painel** (`/`) — indicadores reais, derivados do Dataset C
   (`data/processed/dataset_c_unificado.csv`), organizados em "lentes"
   inspiradas na plataforma de referência da orientadora (Lentes da
   Eleição 2026), mais uma lente de IA. Lentes ainda não integradas
   (buscadores, redes sociais, institutos) aparecem marcadas como
   "em construção" — nunca com dado mockado no lugar de dado real.
2. **Sensor de IA** (`/sensor`) — ferramenta interativa que envia um texto
   para o serviço de inferência do `/models` e exibe rótulo, probabilidade
   e confiança. Ver `/metodologia` para a distinção entre classificador de
   temática (v0, em produção) e detector de autoria (v1, roadmap).

## Como rodar

```bash
npm install
cp .env.example .env.local   # aponte MODELS_API_URL para o serviço /models
npm run dev
```

Abra [http://localhost:3000](http://localhost:3000).

O Sensor de IA (`/sensor`) depende do serviço FastAPI de `/models` estar no
ar (ver `../models/README.md`). Sem ele, a página exibe um erro explícito —
por design, nunca uma predição simulada.

`MODELS_API_URL` é validada com um schema `zod` (`src/lib/env.ts`) no
momento em que o módulo é importado: uma URL malformada falha cedo, com uma
mensagem explícita, em vez de um erro de rede confuso mais tarde no Sensor
de IA.

```bash
npx eslint .    # lint
npm run test    # testes unitários (Vitest + Testing Library)
npm run build   # build de produção — também roda o type-check do TypeScript
```

Um workflow de CI (`.github/workflows/ci.yml`, na raiz do repositório) roda
essas três checagens (mais `pytest` de `/models`) a cada push/PR — ver a
raiz do README para o job completo.

## De onde vêm os dados do painel

`src/lib/dataset-c.ts` lê **`../data/processed/dataset_c_unificado.csv` direto
do disco a cada request** (`export const dynamic = "force-dynamic"` em
`page.tsx`/`metodologia/page.tsx` impede o Next.js de cachear a página
estaticamente). Não existe um passo manual de "exportar dados para o site":
assim que o CSV for regenerado — nova coleta via
`scripts/scrape_dataset_b_completo.py` + notebook
`03_dataset_c_unificado_eda.ipynb` —, a próxima vez que alguém abrir o
painel já reflete os novos números.

Isso pressupõe que `/web` roda de dentro do monorepo, com `../data/processed/`
acessível no disco (é o caso do `npm run dev`/`npm run build` normais a
partir de `web/`).

**No Vercel, isso também é o caso — configurado, não automático.** Por
padrão, um deploy do Vercel com "Root Directory" = `web` empacotaria só o
que está dentro de `web/`, deixando `../data/` de fora e forçando o painel
a cair sempre para o snapshot (inclusive o feed de checagens, que não tem
fallback nenhum — ver abaixo). `next.config.ts` resolve isso com
`outputFileTracingRoot` (sobe a raiz de rastreamento de arquivos do Next
para a raiz do monorepo) + `outputFileTracingIncludes` (inclui
explicitamente `../data/processed/dataset_c_unificado.csv` no pacote de
`/` e `/metodologia`, já que o caminho é montado em runtime — `path.join(
process.cwd(), "..", ...)` — e o rastreador estático do Next não consegue
inferir essa dependência sozinho). Confirmado localmente: depois de
`npm run build`, o CSV aparece de fato em
`.next/server/app/page.js.nft.json` (o arquivo que descreve exatamente o
que o Vercel empacota para aquela função serverless), resolvendo para o
caminho real do arquivo. **Falta um passo que só dá para fazer no painel
do Vercel:** em Project Settings → General → Root Directory, habilitar
"Include source files outside of the Root Directory in the Build Step" —
sem isso, o Vercel nem baixa `../data/` no ambiente de build, e a
configuração do Next não tem o que incluir. Depois do primeiro deploy,
vale conferir na prática que o painel real (não só o snapshot) está sendo
servido — ex.: adicionar um item novo ao CSV localmente e ver se ele
aparece no deploy sem precisar regenerar o snapshot.

**Fallback de deploy standalone (mantido como rede de segurança):** mesmo
com a configuração acima, `getDatasetCSummary()` (`src/lib/dataset-c.ts`)
continua caindo para um snapshot JSON estático se o CSV não for encontrado
— por exemplo, se o toggle do Vercel acima não estiver marcado, ou em um
deploy realmente isolado (só a pasta `web/` copiada manualmente, sem passar
pelo build do Next com as opções de tracing). Isso cobre o resumo/gráficos;
o feed de checagens (`getChecagensRecentes()`) não tem esse fallback e
continua exigindo o CSV real — na prática, deixa de ser um problema assim
que o tracing acima estiver configurado corretamente, mas se algo nessa
configuração falhar, o feed é a primeira coisa a mostrar "indisponível".
Passo a passo para gerar o snapshot (necessário de qualquer forma como
rede de segurança, e obrigatório se você optar por não configurar o
tracing acima):

```bash
# a partir da raiz do repo, com o CSV do Dataset C já gerado
python scripts/export_dashboard_data.py
```

Isso escreve `web/src/data/dataset_c_summary.json` (mesmo formato de
`DatasetCSummary`, com `gerado_em`/`gerado_por`/`aviso` deixando explícito que
é uma fotografia estática, não dado ao vivo). Ao empacotar `/web` sozinho para
deploy, inclua esse arquivo junto (ele fica em `src/data/`, versionável
normalmente) — na primeira request sem `../data/processed/` acessível, o
painel passa a servir a partir dele automaticamente, sem nenhuma mudança de
código. Lembre-se de regenerá-lo (rodar o comando acima de novo) a cada nova
coleta que se queira refletir nesse tipo de deploy, já que ele é uma
fotografia, não um feed ao vivo.

Se nem o CSV nem o snapshot forem encontrados, o painel mostra um aviso
explícito em vez de qualquer número — nunca cai para dado mockado.

## Índice de tendência com contexto de calendário eleitoral (RF2.4)

Diferente do resumo/feed (lidos direto do CSV/snapshot em disco), a seção
"Índice de tendência de desinformação por IA" do painel chama
`obterIndiceTendencia()` (`src/lib/models-client.ts`), que consulta `GET
/forecast/index` no serviço `/models` — a primeira chamada do painel a
esse serviço (o Sensor de IA já chamava `/predict/ia-topic`, mas do lado
do cliente, não do servidor). Por isso essa é a única seção do painel que
pode ficar indisponível mesmo com o CSV/snapshot presentes: se `/models`
não estiver no ar, a chamada tem timeout de 8s e a seção mostra um aviso
explícito, sem derrubar o resto da página (chamada isolada do resumo/feed
em `page.tsx`, mesmo padrão de "falha isolada" já usado ali).

`TrendIndexChart` (`src/components/trend-index-chart.tsx`) desenha a série
observada, a projeção com faixa de confiança (95%), e uma linha vertical
em cada mês de 1º turno eleitoral que `/forecast/index` reportar dentro do
período (`marcos_eleitorais`) — ver `models/README.md`, "Índice de
tendência", para os campos exatos. O gráfico de volume mensal
(`monthly-volume-chart.tsx`) ganhou o mesmo tipo de marcador a partir de
`datas_turno_1` (que já vinha em `DatasetCSummary`, mas nunca era desenhado
— ver `docs/PRD.md`, Seção 16, item 3).

## Veredito predominante no resumo executivo (RF3.1)

`distribuicao_veredito` (`DatasetCSummary`) alimenta um card "Veredito
predominante" no resumo executivo do painel, via `veredictoPredominante()`
(`src/lib/veredito-labels.ts`) — antes desse dado só aparecia por item
individual no feed de checagens. `veredictoPredominante()` retorna `null`
(card não aparece) em vez de fabricar um veredito quando a distribuição
está vazia ou soma zero. Ver `docs/PRD.md`, Seção 16, item 2.

## Acessibilidade e UX (Fase 3)

- **Modo claro/escuro manual** (`src/components/theme-toggle.tsx`): além de
  seguir `prefers-color-scheme` do sistema por padrão, o botão no menu
  permite alternar manualmente, persistindo a escolha em `localStorage`. Um
  script inline em `layout.tsx` aplica a escolha salva antes da primeira
  renderização (evita o "flash" de tema errado), e o próprio componente lê
  o estado do DOM via `useSyncExternalStore` — sem efeito colateral de
  `setState` dentro de `useEffect`, para hidratar corretamente sem disparar
  o lint `react-hooks/set-state-in-effect`.
- **Paginação e filtro no feed de checagens** (`checagens-feed.tsx`): mostra
  12 itens por vez ("carregar mais" para o restante) e um filtro "só
  relacionadas a IA" — antes mostrava só as 12 mais recentes, sem forma de
  ver o resto.
- **Contador de caracteres no Sensor de IA** (`sensor-form.tsx`): o limite
  de 20.000 caracteres já existia no backend (validação Pydantic); agora é
  comunicado na UI, com mínimo de 20 caracteres também exposto.
- **Passagem de acessibilidade**: link "pular para o conteúdo" (skip link),
  `aria-current="page"` nos links de navegação ativos, `role="img"` +
  resumo textual (`aria-label`) nos dois gráficos (Recharts não gera texto
  alternativo sozinho), `role="note"` no banner de aviso.
- **Testes automatizados** (27 testes, `npm run test`): lógica de
  agregação pura de `dataset-c.ts` (sem tocar em disco), cliente HTTP de
  `models-client.ts` (rede mockada com `vi.stubGlobal`, cobrindo sucesso,
  erro HTTP e falha de rede — inclui `obterIndiceTendencia`, RF2.4) e o
  componente `ChecagensFeed` (filtro, paginação, selo de IA) via Testing
  Library + jsdom, mais `marcosEleitoraisVisiveis` (`monthly-volume-chart`)
  e `veredictoPredominante` (`veredito-labels`) como funções puras
  testáveis sem depender de renderização de SVG do Recharts em jsdom.

## Estrutura

```
src/
├── app/
│   ├── layout.tsx              # script inline anti-flash de tema, skip link
│   ├── page.tsx                 # painel (dashboard) — force-dynamic, inclui índice de tendência (RF2.4)
│   ├── sensor/page.tsx           # Sensor de IA
│   ├── metodologia/page.tsx      # limitações e proveniência dos dados — force-dynamic
│   └── api/sensor-ia/route.ts    # proxy para o serviço /models
├── components/
│   ├── theme-toggle.tsx          # alternância manual de tema claro/escuro
│   ├── checagens-feed.tsx        # feed com paginação + filtro "só IA"
│   ├── sensor-form.tsx           # formulário do Sensor, com contador de caracteres
│   ├── nav.tsx                   # navegação, aria-current no link ativo
│   ├── disclaimer-banner.tsx
│   ├── monthly-volume-chart.tsx  # gráfico com resumo textual (role="img") + marcadores de 1º turno
│   ├── theme-distribution-chart.tsx
│   ├── trend-index-chart.tsx     # índice de tendência + marcadores de 1º turno (RF2.4)
│   └── __tests__/                # testes de componente/função pura (Testing Library + Vitest)
└── lib/
    ├── dataset-c.ts       # lê o CSV real do disco a cada request, com fallback para snapshot JSON
    ├── env.ts              # validação de variáveis de ambiente (zod)
    ├── lentes.ts            # definição das lentes do painel (real vs. em construção)
    ├── models-client.ts     # cliente HTTP para o serviço /models (predição + índice de tendência)
    ├── veredito-labels.ts   # rótulos de veredito + "veredito predominante" (RF3.1)
    ├── types.ts              # tipos compartilhados
    └── __tests__/             # testes unitários (Vitest)
```

## Stack

Next.js 16 (App Router), TypeScript, Tailwind CSS v4, Recharts, Zod
(validação de env), Vitest + Testing Library (testes).

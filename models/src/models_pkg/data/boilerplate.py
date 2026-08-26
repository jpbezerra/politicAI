"""
Remoção de boilerplate editorial recorrente do `corpo_artigo` do Dataset B,
ANTES de vetorizar para o classificador de temática de IA.

Achado original (descoberto ao inspecionar os termos mais influentes do
baseline v0 — ver `models/README.md`, "Limitações", item 5): dois trechos
fixos e recorrentes do site do Aos Fatos vazavam para os n-gramas do TF-IDF
como sinal espúrio:

1. **Widget "Siga no WhatsApp"** — uma chamada fixa de assinatura
   (2 variantes de texto encontradas: "Siga o canal do Aos Fatos no
   WhatsApp e receba nossas checagens e reportagens" e "Inscreva-se no
   nosso canal e receba as nossas checagens e reportagens"), seguida
   diretamente, no HTML, pela legenda do post/vídeo sendo checado — sem
   separador. Isso produzia os bigramas "receba checagens" e "checagens
   reportagens" como termos "mais associados a IA" no model card, quando
   na verdade é só o CTA de assinatura, não conteúdo sobre o tema.
2. **Frase-modelo "O caminho da apuração [Aos Fatos]..."** — abertura
   padronizada de um quadro de metodologia ("como verificamos") presente
   em boa parte dos artigos mais recentes. A palavra "apuração" é,
   inclusive, uma das palavras-chave usadas para a heurística `alvo_ataque`
   dos notebooks de EDA da Fase 2 — essa mesma frase-modelo também
   contaminava aquela análise (ver `notebooks/02_dataset_b_aosfatos_eda.ipynb`,
   Seção 3.5b, corrigida na Fase 3 a partir deste mesmo achado).

Achado sobre a DISTRIBUIÇÃO desses dois primeiros trechos, não só sua
presença: eles aparecem em ~87% dos itens rotulados IA (106-107/122) contra
~5-7% dos itens Tradicionais (23-32/431) — quase certamente porque o Aos
Fatos só adicionou esse template ao site depois de um certo período, e os
itens IA são majoritariamente mais recentes (mesmo confound de tag/época já
documentado em `models/src/models_pkg/data/loader.py`).

Achados adicionais (rodada 2, ao revisar o corpus em busca de mais
variantes de template não cobertas — ver docs/PRD.md, backlog de
melhorias, "estender boilerplate.py"):

3. **Caixa de parceria com o programa de checagem da Meta** — "Aos Fatos
   integra o Programa de Verificação de Fatos Independente da Meta." /
   "Aos Fatos integra o Third-Party Fact-Checking Partners, o programa de
   verificação de fatos da Meta." seguida de "Veja aqui como funciona a
   parceria." Distribuição ainda mais desigual que os itens 1-2, só que na
   direção OPOSTA: aparece em **41-44% dos itens Tradicionais (179-191/431)
   e em ZERO itens IA (0/122)** — ou seja, sem esta limpeza, "meta",
   "parceria", "programa", "verificação", "independente", "fact-checking"
   e "partners" apareceriam como termos espúrios associados à classe
   Tradicional, pelo motivo inverso do achado original (parece que o Aos
   Fatos parou de incluir essa caixa em textos mais recentes, e os itens IA
   são majoritariamente mais recentes).
4. **Nota de checagem colaborativa de fim de semana** — "Neste fim de
   semana, o Aos Fatos se uniu às iniciativas de checagem AFP Checamos,
   Boatos.org, Comprova, E-Farsas, Fato ou Fake e Lupa para verificar em
   conjunto a desinformação sobre as eleições." — frase 100% fixa (mesmo
   texto em todas as ocorrências), presente em 25/431 itens Tradicionais e
   0/122 itens IA.
5. **Nota de checagem cruzada com outra agência** — "Esta checagem também
   foi feita por.../Esta peça de desinformação também foi checada por..."
   seguida do nome de 1-2 agências parceiras (Reuters, Estadão Verifica,
   UOL Confere, Lupa, Boatos, Comprova, Fato ou Fake, G1, NSC Total — 27
   combinações distintas encontradas). Menos desigual entre grupos (10.7%
   IA vs. 7.9% Tradicional) mas ainda assim não é conteúdo do boato, é
   metadado editorial sobre o processo de apuração.
6. **Rodapé de direitos autorais** — "Todos os direitos reservados." — raro
   (7/553 itens), provavelmente um fragmento do rodapé que escapou da
   extração por marcador de `build_dataset_b_completo.py` em alguns casos.

Esta limpeza continua sendo *best-effort*, não exaustiva: cobre as
variantes de texto encontradas na amostra atual. Uma nova coleta pode
introduzir outras variantes de template não cobertas aqui — se os termos
mais influentes de um retreino futuro voltarem a mostrar fragmentos de
template editorial (nomes de agências parceiras, "assine", "newsletter",
"compartilhe"), é sinal de que este módulo precisa de mais um padrão.

CORREÇÃO DE ROBUSTEZ (revisão pós-implementação): a primeira versão de
`_CHECADO_POR_TERCEIROS_RE` (achado 5) usava um coringa genérico
(`pel[ao][^.]{0,60}` seguido de um ponto literal — "casa qualquer coisa até o próximo ponto") para
capturar o nome da agência parceira. Isso funciona nos 553 itens reais
atuais (verificado: as 27 combinações de nome batem exatamente com o texto
completo, sem sobra), mas é frágil por construção — se uma frase real do
artigo continuasse essa mesma oração sem um ponto até 60 caracteres depois
(ex.: "...também foi feita pela Reuters e mostrou que..."), o coringa
comeria conteúdo real do boato junto com o boilerplate, silenciosamente.
Substituído por uma lista fechada dos nomes de agência realmente
encontrados (Reuters, Lupa/Agência Lupa, Boatos/Boatos.org, Estadão
Verifica, UOL/UOL Confere/UOL Verifica, Fato ou Fake, G1, NSC Total, AFP,
Comprova/Projeto Comprova) em vez de um coringa aberto — não corre mais o
risco de comer prosa real, ao custo de (como o restante deste módulo) não
reconhecer uma agência nova que apareça só numa coleta futura. Como
efeito colateral, também corrige um truncamento: o coringa antigo cortava
"Boatos.org" em "Boatos." (parava no primeiro ponto, que caía dentro do
próprio nome), deixando ".org" para trás no texto "limpo"; a lista
fechada reconhece "Boatos.org" por inteiro.
"""

from __future__ import annotations

import re

_WHATSAPP_CTA_RE = re.compile(
    r"(siga\s+o\s+canal\s+do\s*aos\s+fatos\s+no\s+whatsapp"
    r"|inscreva-se\s+no\s+nosso\s+canal)"
    r"\s*e\s*receba\s*(as\s*)?nossas\s*checagens\s*e\s*reportagens",
    re.IGNORECASE,
)

_CAMINHO_APURACAO_RE = re.compile(
    r"o\s+caminho\s+da\s+apura[cç][aã]o\s*(aos\s+fatos)?",
    re.IGNORECASE,
)

_META_PARCERIA_RE = re.compile(
    r"aos\s+fatos\s+integra\s+o\s+"
    r"(programa\s+de\s+verifica[cç][aã]o\s+de\s+fatos\s+independente\s+da\s+meta"
    r"|third-party\s+fact-checking\s+partners,?\s+o\s+programa\s+de\s+verifica[cç][aã]o\s+de\s+fatos\s+da\s+meta)"
    r"\.?\s*(veja\s+aqui\s+como\s+funciona\s+a\s+parceria\s*\.?)?",
    re.IGNORECASE,
)
# "Veja aqui como funciona a parceria." também aparece sozinha, sem o texto
# da caixa acima logo antes -- cobrimos separadamente para não depender de
# adjacência exata.
_VEJA_PARCERIA_RE = re.compile(
    r"veja\s+aqui\s+como\s+funciona\s+a\s+parceria\s*\.?",
    re.IGNORECASE,
)

_FIM_DE_SEMANA_INICIATIVAS_RE = re.compile(
    r"neste\s+fim\s+de\s+semana,\s+o\s+aos\s+fatos\s+se\s+uniu\s+[aà]s\s+iniciativas\s+de\s+checagem\s+"
    r"afp\s+checamos\s*,\s*boatos\.org\s*,\s*comprova\s*,\s*e-farsas\s*,\s*fato\s+ou\s+fake\s+e\s+lupa\s+"
    r"para\s+verificar\s+em\s+conjunto\s+a\s+desinforma[cç][aã]o\s+sobre\s+as\s+elei[cç][oõ]es\s*\.?",
    re.IGNORECASE,
)

_NOME_AGENCIA_PARCEIRA_RE_FRAGMENTO = (
    r"(?:agencia\s+lup\s*a|ag[eê]ncia\s+lup\s*a|lup\s*a|reuters|boatos(?:\.org)?|"
    r"estad[aã]o\s+verifica|uol\s+verifica|uol\s+confere|uol|"
    r"fato\s+ou\s+fake(?:\s*,\s*do\s+grupo\s+globo)?|g1|nsc\s+total|afp|"
    r"projeto\s+comprova|comprova)"
)
_CONECTOR_AGENCIA_RE_FRAGMENTO = r"(?:\s+e\s+pel[ao]\s+|\s+e\s+)"
_CHECADO_POR_TERCEIROS_RE = re.compile(
    r"esta\s+(checagem|pe[cç]a\s+de\s+desinforma[cç][aã]o)\s+tamb[eé]m\s+foi\s+(checada|feita)\s+"
    r"pel[ao]\s*\n?\s*" + _NOME_AGENCIA_PARCEIRA_RE_FRAGMENTO
    + r"(?:" + _CONECTOR_AGENCIA_RE_FRAGMENTO + _NOME_AGENCIA_PARCEIRA_RE_FRAGMENTO + r")*\s*\.",
    re.IGNORECASE,
)

_DIREITOS_RESERVADOS_RE = re.compile(
    r"todos\s+os\s+direitos\s+reservados\.?",
    re.IGNORECASE,
)


def strip_known_boilerplate(texto: str) -> str:
    """Remove os trechos de boilerplate documentados acima. Idempotente e
    segura de aplicar em texto que não contém nenhum dos padrões."""
    if not texto:
        return texto
    texto = _WHATSAPP_CTA_RE.sub(" ", texto)
    texto = _CAMINHO_APURACAO_RE.sub(" ", texto)
    texto = _META_PARCERIA_RE.sub(" ", texto)
    texto = _VEJA_PARCERIA_RE.sub(" ", texto)
    texto = _FIM_DE_SEMANA_INICIATIVAS_RE.sub(" ", texto)
    texto = _CHECADO_POR_TERCEIROS_RE.sub(" ", texto)
    texto = _DIREITOS_RESERVADOS_RE.sub(" ", texto)
    return re.sub(r"\s+", " ", texto).strip()

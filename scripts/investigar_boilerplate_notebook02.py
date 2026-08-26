# -*- coding: utf-8 -*-
"""
Investigação: o boilerplate editorial ("Siga o canal do Aos Fatos no
WhatsApp...", "O caminho da apuração...") que contaminava os termos mais
influentes do classificador de ML (ver models/src/models_pkg/data/boilerplate.py)
também contamina as heurísticas vetor_midia_texto/alvo_ataque_texto do
notebook 02 (Dataset B), usadas nos testes H2 e H4?

Reproduz EXATAMENTE a lógica de scripts/gen_notebook_b.py (normalize_text,
MEDIA_KEYWORDS, ATTACK_KEYWORDS_CORPO, alvo_ataque_corpo) sobre
corpo_artigo, primeiro sem limpeza (replicando o notebook atual) e depois
aplicando strip_known_boilerplate() antes de normalizar, comparando as
distribuições e os testes qui-quadrado antes/depois.

Rodar com: PYTHONPATH=models/src python3 scripts/investigar_boilerplate_notebook02.py
(a partir da raiz do repo)
"""
import re
import unicodedata

import numpy as np
import pandas as pd
from scipy import stats

from models_pkg.data.boilerplate import strip_known_boilerplate

pd.set_option("display.max_colwidth", 90)


def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text.lower()).strip()


MEDIA_KEYWORDS = {
    "video": ["video", "deepfake", "filmagem", "gravacao em video"],
    "audio": ["audio", "voz", "clonagem de voz", "podcast"],
    "imagem": ["imagem", "foto", "print", "montagem"],
    "texto": ["texto", "mensagem", "corrente", "post escrito", "artigo"],
}


def vetor_midia(texto_norm):
    for vetor, kws in MEDIA_KEYWORDS.items():
        if any(kw in texto_norm for kw in kws):
            return vetor
    return "indeterminado"


ATTACK_KEYWORDS_CORPO = {
    "candidato_pessoa": ["carater", "honestidade", "vida pessoal", "familia", "saude",
                          "corrupcao pessoal", "traicao", "diploma", "patrimonio pessoal",
                          "morte", "morreu"],
    "urna_processo": ["urna", "biometria", "totalizacao", "apuracao", "sistema eletronico",
                       "fraude eleitoral", "codigo-fonte", "codigo fonte", "seguranca do voto"],
}


def alvo_ataque_corpo(texto_norm):
    score_p = sum(kw in texto_norm for kw in ATTACK_KEYWORDS_CORPO["candidato_pessoa"])
    score_u = sum(kw in texto_norm for kw in ATTACK_KEYWORDS_CORPO["urna_processo"])
    if score_p == 0 and score_u == 0:
        return "indeterminado"
    return "candidato_pessoa" if score_p >= score_u else "urna_processo"


def cramers_v(tabela):
    chi2, p, dof, _ = stats.chi2_contingency(tabela)
    n = tabela.to_numpy().sum()
    r, k = tabela.shape
    v = np.sqrt((chi2 / n) / (min(r - 1, k - 1)))
    return chi2, p, v


def main():
    df = pd.read_csv("data/raw/dataset_b_completo.csv", keep_default_na=False)
    df["rotulo_grupo"] = np.where(df["tag_pesquisa"] == "inteligencia-artificial", "IA", "Tradicional")

    print(f"Total de itens: {len(df)}")

    # 0. Quantos itens têm o boilerplate especificamente, por grupo?
    tem_boilerplate = df["corpo_artigo"].map(
        lambda t: strip_known_boilerplate(t) != t if isinstance(t, str) else False
    )
    print("\n=== Itens com boilerplate conhecido detectado, por grupo ===")
    tab_bp = pd.crosstab(df["rotulo_grupo"], tem_boilerplate)
    print(tab_bp)
    print((tab_bp.div(tab_bp.sum(axis=1), axis=0) * 100).round(1))

    # 0b. Especificamente: quantos itens contêm a palavra "apuracao" (normalizada)
    # dentro do trecho de boilerplate "o caminho da apuração"? -- essa palavra
    # É LITERALMENTE uma das keywords de urna_processo em ATTACK_KEYWORDS_CORPO.
    caminho_re = re.compile(r"caminho\s+da\s+apura[cç][aã]o", re.IGNORECASE)
    tem_caminho_apuracao = df["corpo_artigo"].map(
        lambda t: bool(caminho_re.search(t)) if isinstance(t, str) else False
    )
    print('\n=== Itens que contêm a frase "caminho da apuração" (contém a keyword literal "apuracao"), por grupo ===')
    tab_ca = pd.crosstab(df["rotulo_grupo"], tem_caminho_apuracao)
    print(tab_ca)
    print((tab_ca.div(tab_ca.sum(axis=1), axis=0) * 100).round(1))

    # 1. Versão ATUAL do notebook (sem limpeza de boilerplate)
    df["corpo_norm_contaminado"] = df["corpo_artigo"].map(normalize_text)
    df["vetor_midia_texto_contaminado"] = df["corpo_norm_contaminado"].map(vetor_midia)
    df["alvo_ataque_texto_contaminado"] = df["corpo_norm_contaminado"].map(alvo_ataque_corpo)

    # 2. Versão LIMPA (aplica strip_known_boilerplate antes de normalizar)
    df["corpo_limpo"] = df["corpo_artigo"].map(strip_known_boilerplate)
    df["corpo_norm_limpo"] = df["corpo_limpo"].map(normalize_text)
    df["vetor_midia_texto_limpo"] = df["corpo_norm_limpo"].map(vetor_midia)
    df["alvo_ataque_texto_limpo"] = df["corpo_norm_limpo"].map(alvo_ataque_corpo)

    print("\n\n########## H2 — vetor_midia_texto (formato de mídia) ##########")
    for versao in ["contaminado", "limpo"]:
        col = f"vetor_midia_texto_{versao}"
        print(f"\n--- Versão: {versao} ---")
        tabela = pd.crosstab(df["rotulo_grupo"], df[col])
        print(tabela)
        chi2, p, v = cramers_v(tabela)
        print(f"qui-quadrado={chi2:.3f}  p={p:.4f}  V de Cramér={v:.3f}")
        # H2 é sobre audiovisual (video/audio) vs. resto
        audiov = df.assign(audiovisual=df[col].isin(["video", "audio"]))
        tabela_bin = pd.crosstab(audiov["rotulo_grupo"], audiov["audiovisual"])
        chi2b, pb, vb = cramers_v(tabela_bin)
        print(f"[binário audiovisual vs. resto] qui-quadrado={chi2b:.3f}  p={pb:.4f}  V de Cramér={vb:.3f}")

    print("\n\n########## H4 — alvo_ataque_texto (alvo do ataque) ##########")
    for versao in ["contaminado", "limpo"]:
        col = f"alvo_ataque_texto_{versao}"
        print(f"\n--- Versão: {versao} ---")
        tabela = pd.crosstab(df["rotulo_grupo"], df[col])
        print(tabela)
        chi2, p, v = cramers_v(tabela)
        print(f"qui-quadrado={chi2:.3f}  p={p:.4f}  V de Cramér={v:.3f}")
        # H4 restrito a itens determinados, alvo_pessoa vs. urna_processo
        det = df[df[col] != "indeterminado"].assign(
            alvo_pessoa=lambda d: d[col] == "candidato_pessoa"
        )
        tabela_bin = pd.crosstab(det["rotulo_grupo"], det["alvo_pessoa"])
        print(tabela_bin)
        chi2b, pb, vb = cramers_v(tabela_bin)
        print(f"[binário alvo_pessoa vs. urna_processo, só determinados] qui-quadrado={chi2b:.3f}  p={pb:.4f}  V de Cramér={vb:.3f}")

    print("\n\n########## Quantos itens MUDAM de classificação (contaminado -> limpo)? ##########")
    mudou_midia = (df["vetor_midia_texto_contaminado"] != df["vetor_midia_texto_limpo"]).sum()
    mudou_alvo = (df["alvo_ataque_texto_contaminado"] != df["alvo_ataque_texto_limpo"]).sum()
    print(f"vetor_midia_texto mudou em {mudou_midia}/{len(df)} itens")
    print(f"alvo_ataque_texto mudou em {mudou_alvo}/{len(df)} itens")
    if mudou_alvo:
        cols = ["rotulo_grupo", "alvo_ataque_texto_contaminado", "alvo_ataque_texto_limpo"]
        print(df.loc[df["alvo_ataque_texto_contaminado"] != df["alvo_ataque_texto_limpo"], cols]
              .value_counts().to_string())


if __name__ == "__main__":
    main()

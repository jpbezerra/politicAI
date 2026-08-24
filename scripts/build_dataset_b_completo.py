# -*- coding: utf-8 -*-
"""
Junta os 3 CSVs por tag gerados por `scrape_dataset_b_completo.py`
(dataset_b_completo_inteligencia-artificial.csv, eleicoes-2022, eleicoes-2026)
em um único arquivo `data/raw/dataset_b_completo.csv`, com data de publicação
real e texto completo por item.

Por que reparsear a data aqui em vez de só concatenar os CSVs: os 3 arquivos
enviados pelo usuário foram coletados com a v2 do scraper, que já extraía
`texto_completo` corretamente mas falhava em 100% dos itens ao extrair
`data_publicacao` (bug de quebra de linha na vírgula "data, hora" -- ver
"HISTÓRICO DE BUG CORRIGIDO (v3)" em scrape_dataset_b_completo.py). Como o
texto completo de cada checagem já foi baixado e está salvo nos 3 CSVs, dá
para corrigir a data SEM voltar a acessar a internet: basta reaplicar a lógica
de extração já corrigida (`extrair_data_e_texto`, reaproveitada por import,
não duplicada) sobre o `texto_completo` que já existe. Não é uma nova coleta.

Uso (rodar de dentro de scripts/, com os 3 CSVs já em data/raw/):
    python3 build_dataset_b_completo.py

Saída: data/raw/dataset_b_completo.csv, colunas:
    titulo, veredito, tema, tag_pesquisa, url,
    data_publicacao (string "DD de <mês> de AAAA, HH:MM"),
    data_publicacao_iso (datetime ISO 8601, ou vazio se não extraída),
    texto_completo, corpo_artigo

CORPO_ARTIGO -- por que existe além de texto_completo:
`texto_completo` é o dump de TODA a página (`soup.get_text()`), incluindo
menu de navegação, botão de compartilhar, o widget "Adicione o Aos Fatos às
suas fontes do Google" (que aparece 2x na página), sugestões de "Leia
também" e, principalmente, a nuvem de tags do rodapé -- que lista nomes como
"Luiz Inácio Lula da Silva", "Jair Bolsonaro" e "TSE" **em toda página do
site, goste ou não o artigo desses nomes**. Isso contaminava as heurísticas
de palavra-chave aplicadas sobre texto completo (ver notebook 02): rodando
`alvo_ataque` sobre `texto_completo` bruto, "indeterminado" caía para 0.0%
no dataset inteiro -- praticamente garantido, já que "lula"/"bolsonaro"/"tse"
aparecem em quase toda página, dentro ou fora da nuvem de tags,
independentemente do alvo real do boato.

`corpo_artigo` isola só o texto do artigo em si, usando dois marcadores de
texto confirmados como consistentes nos 553 itens: a string "fonte
preferencial" aparece exatamente 2x em toda página (a primeira, logo antes
do corpo do artigo; a segunda, no rodapé) -- usamos a primeira ocorrência
como início. A palavra "Referências" aparece 1x em 546/553 itens, marcando
o fim do corpo e o início da lista de fontes -- usamos como fim (nos 7 itens
sem "Referências", vai até o final do texto). Isso já remove nav/menu,
widget de compartilhar e a nuvem de tags do rodapé. Um segundo passo remove
widgets de "leia também" embutidos NO MEIO do corpo (formato: uma linha de
categoria curta, depois "Checagem" sozinho numa linha, depois o título de
outra checagem) -- presentes em 62/553 (11.2%) itens.
"""
import csv
import re
from pathlib import Path

# reaproveita a extração de data já corrigida (v3), não duplica a lógica
from scrape_dataset_b_completo import DATA_HORA_RE, DATA_MES_RE

csv.field_size_limit(10**9)

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"

TAGS = ["inteligencia-artificial", "eleicoes-2022", "eleicoes-2026"]
CONTAGEM_ESPERADA = {"inteligencia-artificial": 122, "eleicoes-2022": 419, "eleicoes-2026": 12}

MESES_PT = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4, "maio": 5,
    "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10,
    "novembro": 11, "dezembro": 12,
}
DATA_PARSE_RE = re.compile(
    r"^(\d{1,2}) de ([a-zà-ú]+) de (\d{4}), (\d{2}):(\d{2})$", re.IGNORECASE
)


def reextrair_data(texto_completo):
    """Reaplica a extração de data (v3, corrigida) sobre um texto_completo já
    baixado, sem nova requisição de rede. Ver docstring do módulo."""
    linhas = [l.strip() for l in texto_completo.split("\n") if l.strip()]
    for i in range(len(linhas) - 2):
        if (DATA_MES_RE.match(linhas[i]) and linhas[i + 1] == ","
                and DATA_HORA_RE.match(linhas[i + 2])):
            return f"{linhas[i]}, {linhas[i + 2]}"
    return ""


def data_para_iso(data_publicacao):
    m = DATA_PARSE_RE.match(data_publicacao)
    if not m:
        return ""
    dia, mes_nome, ano, hora, minuto = m.groups()
    mes = MESES_PT.get(mes_nome.lower())
    if not mes:
        return ""
    return f"{ano}-{mes:02d}-{int(dia):02d}T{hora}:{minuto}:00"


MARCADOR_INICIO = "fonte preferencial"
MARCADOR_FIM = "Referências"
WIDGET_LEIA_TAMBEM_RE = re.compile(r"\n[^\n]{0,60}\nChecagem\n+[^\n]{5,200}\n")


def extrair_corpo_artigo(texto_completo):
    """Isola o texto do próprio artigo, removendo nav/menu/widgets/rodapé
    (nuvem de tags) que contaminam heurísticas de palavra-chave -- ver
    docstring do módulo ("CORPO_ARTIGO -- por que existe além de
    texto_completo")."""
    i = texto_completo.find(MARCADOR_INICIO)
    if i == -1:
        return texto_completo
    j = texto_completo.find(MARCADOR_FIM)
    inicio = i + len(MARCADOR_INICIO)
    fim = j if j != -1 else len(texto_completo)
    corpo = texto_completo[inicio:fim]
    corpo = WIDGET_LEIA_TAMBEM_RE.sub("\n", corpo)
    return corpo


def main():
    linhas_saida = []
    resumo = {}

    for tag in TAGS:
        path = DATA_RAW / f"dataset_b_completo_{tag}.csv"
        if not path.exists():
            print(f"AVISO: {path} não encontrado -- pulando tag {tag!r}.")
            continue

        with open(path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        n_com_data_original = sum(1 for r in rows if r.get("data_publicacao"))
        n_reextraidos = 0
        for r in rows:
            if not r.get("data_publicacao"):
                nova_data = reextrair_data(r["texto_completo"])
                if nova_data:
                    r["data_publicacao"] = nova_data
                    n_reextraidos += 1
            r["data_publicacao_iso"] = data_para_iso(r["data_publicacao"])
            r["corpo_artigo"] = extrair_corpo_artigo(r["texto_completo"])
            linhas_saida.append(r)

        resumo[tag] = {
            "total": len(rows),
            "com_data_original": n_com_data_original,
            "reextraidos_do_texto_ja_baixado": n_reextraidos,
            "com_data_final": sum(1 for r in rows if r.get("data_publicacao")),
        }
        esperado = CONTAGEM_ESPERADA.get(tag)
        if esperado is not None and len(rows) != esperado:
            print(f"AVISO: tag {tag!r} tem {len(rows)} itens, esperado {esperado} "
                  f"(coleta pode estar incompleta).")

    print("=== Resumo por tag ===")
    for tag, info in resumo.items():
        print(f"  {tag}: {info['total']} itens | "
              f"{info['com_data_original']} já vinham com data | "
              f"{info['reextraidos_do_texto_ja_baixado']} recuperados do texto já baixado "
              f"(bug v2 corrigido sem nova requisição) | "
              f"{info['com_data_final']}/{info['total']} com data final")

    total = len(linhas_saida)
    total_com_data = sum(1 for r in linhas_saida if r.get("data_publicacao"))
    total_com_iso = sum(1 for r in linhas_saida if r.get("data_publicacao_iso"))
    print(f"\nTotal geral: {total} itens | {total_com_data} com data de publicação "
          f"| {total_com_iso} com data convertida para ISO 8601")
    if total_com_data < total:
        faltantes = [r["url"] for r in linhas_saida if not r.get("data_publicacao")]
        print(f"Itens sem data ({len(faltantes)}): {faltantes}")

    def _corpo_bruto_sem_limpeza(texto):
        i = texto.find(MARCADOR_INICIO)
        if i == -1:
            return texto
        j = texto.find(MARCADOR_FIM)
        return texto[i + len(MARCADOR_INICIO): (j if j != -1 else len(texto))]

    n_sem_referencias = sum(1 for r in linhas_saida if MARCADOR_FIM not in r["texto_completo"])
    n_com_widget_embutido = sum(1 for r in linhas_saida
                                 if WIDGET_LEIA_TAMBEM_RE.search(_corpo_bruto_sem_limpeza(r["texto_completo"])))
    reducao_media = 1 - (sum(len(r["corpo_artigo"]) for r in linhas_saida)
                          / sum(len(r["texto_completo"]) for r in linhas_saida))
    print(f"corpo_artigo: {n_sem_referencias} itens sem marcador 'Referências' (usado texto até o fim), "
          f"{n_com_widget_embutido} itens tinham widget 'leia também' embutido no meio do corpo "
          f"(removido), tamanho médio reduzido em {reducao_media*100:.1f}% frente a texto_completo "
          f"(nav/menu/rodapé/tags removidos).")

    fieldnames = ["titulo", "veredito", "tema", "tag_pesquisa", "url",
                  "data_publicacao", "data_publicacao_iso", "texto_completo", "corpo_artigo"]
    out_path = DATA_RAW / "dataset_b_completo.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in linhas_saida:
            writer.writerow({k: r.get(k, "") for k in fieldnames})

    print(f"\nArquivo salvo: {out_path}")


if __name__ == "__main__":
    main()

from models_pkg.data.boilerplate import strip_known_boilerplate


def test_strips_whatsapp_cta_variant_1():
    texto = (
        "Publicações compartilham um vídeo. Siga o canal do Aos Fatos no "
        "WhatsApp e receba nossas checagens e reportagens Tancredo Neves "
        "antes de falecer em 1985, deixou sua opinião."
    )
    limpo = strip_known_boilerplate(texto)
    assert "checagens e reportagens" not in limpo.lower()
    assert "siga o canal" not in limpo.lower()
    # o conteúdo real (legenda do vídeo checado) deve permanecer
    assert "tancredo neves" in limpo.lower()


def test_strips_whatsapp_cta_variant_2():
    texto = (
        "Compartilhar para aumentar o alcance. Leia mais WHATSAPP "
        "Inscreva-se no nosso canal e receba as nossas checagens e "
        "reportagens Prepare-se para a revolução."
    )
    limpo = strip_known_boilerplate(texto)
    assert "checagens e reportagens" not in limpo.lower()
    assert "prepare-se para a revolução" in limpo.lower()


def test_strips_caminho_da_apuracao():
    texto = "O caminho da apuração Aos Fatos fez uma busca reversa pelo vídeo."
    limpo = strip_known_boilerplate(texto)
    assert "caminho da apuração" not in limpo.lower()
    assert "busca reversa pelo vídeo" in limpo.lower()


def test_leaves_unrelated_text_untouched():
    texto = "As urnas eletrônicas passaram por testes de integridade."
    assert strip_known_boilerplate(texto) == texto


def test_handles_empty_string():
    assert strip_known_boilerplate("") == ""


def test_collapses_whitespace_left_by_removal():
    texto = "Início.\n\n\n\nSiga o canal do Aos Fatos no WhatsApp e receba nossas checagens e reportagens\n\n\n\nFim."
    limpo = strip_known_boilerplate(texto)
    assert "  " not in limpo
    assert limpo.startswith("Início.")
    assert limpo.endswith("Fim.")


def test_strips_meta_partnership_box_programa():
    texto = (
        "É falso que a urna foi fraudada. Aos Fatos integra o Programa de "
        "Verificação de Fatos Independente da Meta. Veja aqui como funciona "
        "a parceria. O conteúdo checado circulou no Facebook."
    )
    limpo = strip_known_boilerplate(texto)
    assert "meta" not in limpo.lower()
    assert "parceria" not in limpo.lower()
    assert "é falso que a urna foi fraudada" in limpo.lower()
    assert "circulou no facebook" in limpo.lower()


def test_strips_meta_partnership_box_third_party_variant():
    texto = (
        "Aos Fatos integra o Third-Party Fact-Checking Partners, o programa "
        "de verificação de fatos da Meta. Confira a checagem completa."
    )
    limpo = strip_known_boilerplate(texto)
    assert "fact-checking" not in limpo.lower()
    assert "confira a checagem completa" in limpo.lower()


def test_strips_veja_parceria_standalone():
    # A frase de fechamento também aparece sem a caixa de abertura logo antes.
    texto = "Texto real do boato. Veja aqui como funciona a parceria. Mais texto real."
    limpo = strip_known_boilerplate(texto)
    assert "parceria" not in limpo.lower()
    assert "texto real do boato" in limpo.lower()
    assert "mais texto real" in limpo.lower()


def test_strips_fim_de_semana_iniciativas():
    texto = (
        "Neste fim de semana, o Aos Fatos se uniu às iniciativas de checagem "
        "AFP Checamos , Boatos.org , Comprova , E-Farsas , Fato ou Fake e "
        "Lupa para verificar em conjunto a desinformação sobre as eleições. "
        "Um vídeo voltou a circular nas redes sociais."
    )
    limpo = strip_known_boilerplate(texto)
    assert "iniciativas de checagem" not in limpo.lower()
    assert "um vídeo voltou a circular" in limpo.lower()


def test_does_not_strip_real_content_that_merely_starts_similarly():
    # Regressão: um texto real sobre um protesto de fim de semana não deve
    # ser confundido com a nota fixa de checagem colaborativa.
    texto = (
        "Neste fim de semana, bolsonaristas foram às ruas em diversas "
        "cidades do país para manifestar defesa à PEC 135/2019."
    )
    assert strip_known_boilerplate(texto) == texto


def test_strips_checado_por_terceiros_variants():
    casos = [
        "Boato sobre vacina. Esta checagem também foi feita pela Reuters . Fim do texto.",
        "Vídeo manipulado. Esta peça de desinformação também foi checada pelo Estadão Verifica e pela Reuters . Outro trecho.",
    ]
    for texto in casos:
        limpo = strip_known_boilerplate(texto)
        assert "reuters" not in limpo.lower()
        assert "também foi" not in limpo.lower()


def test_checado_por_terceiros_does_not_eat_real_content_without_period():
    # Regressão: a primeira versão deste regex usava um coringa genérico
    # ("casa até o próximo ponto") para o nome da agência parceira -- se a
    # oração real continuasse sem um ponto logo após o nome, o coringa
    # comia conteúdo real do boato junto com o boilerplate. Corrigido para
    # uma lista fechada de nomes de agência conhecidos (ver achado 5 na
    # docstring do módulo) em vez de um coringa aberto.
    casos = [
        (
            "Boato sobre vacina. Esta checagem também foi feita pela Reuters "
            "e mostrou que o vídeo é falso. Outro trecho real aqui.",
            "e mostrou que o vídeo é falso",
        ),
        (
            "Esta peça de desinformação também foi checada pela AFP e "
            "mostrou provas de manipulação. Outro parágrafo.",
            "mostrou provas de manipulação",
        ),
        (
            "Esta checagem também foi feita pelo Fato ou Fake e concluiu "
            "que o vídeo era antigo.",
            "concluiu que o vídeo era antigo",
        ),
    ]
    for texto, trecho_real in casos:
        limpo = strip_known_boilerplate(texto)
        assert trecho_real in limpo.lower()


def test_checado_por_terceiros_reconhece_boatos_org_por_inteiro():
    # Regressão: o coringa antigo cortava em "Boatos." (primeiro ponto,
    # dentro do próprio nome ".org"), deixando ".org" para trás.
    texto = "Boato real aqui. Esta checagem também foi feita pelo Boatos.org. Fim do texto real."
    limpo = strip_known_boilerplate(texto)
    assert "boatos" not in limpo.lower()
    assert ".org" not in limpo
    assert "fim do texto real" in limpo.lower()


def test_strips_direitos_reservados():
    texto = "Conteúdo do boato aqui. Todos os direitos reservados. Fim."
    limpo = strip_known_boilerplate(texto)
    assert "direitos reservados" not in limpo.lower()
    assert "conteúdo do boato aqui" in limpo.lower()
    assert limpo.endswith("Fim.")

# -*- coding: utf-8 -*-
"""
Texto bruto real, coletado via navegador (Claude in Chrome) em 23/08/2026,
da Coalizão Fato ou Boato (TSE) — justicaeleitoral.jus.br/fato-ou-boato —
filtrado pela tag "fake news" (267 resultados, 27 páginas de 10 itens,
paginação via b_start:int=0,10,20,...,260).

Cada página é um bloco de texto no formato:
    <título>
    <resumo/lide>
    <dd.mm.aaaa>
    (repete)

Este arquivo apenas ARMAZENA o texto extraído (sem reformatar), para ser
parseado por parse_dataset_a.py. Nenhum dado sintético foi inserido aqui.
"""

PAGE_0 = """
TRE-SP não escolheu urnas submetidas ao teste realizado no dia da eleição
Auditoria é aplicada em equipamentos sorteados ou definidos pelas entidades fiscalizadoras
27.10.2024
Viradas de Boulos, Lula e Dilma não aconteceram todas às 18h45
Checagem do UOL Confere desmonta boato que circulou na internet. Veja a explicação:
09.10.2024
É mentira que o voto valerá como prova de vida nas Eleições 2024
Justiça Eleitoral esclarece que são falsos informes que vêm circulando de que o voto servirá como prova de vida ao INSS
17.09.2024
É falso e-mail sobre convocação como mesário que pede atualização de dados
Para saber se foram convocados, mesárias e mesários devem entrar em contato com o cartório eleitoral
30.08.2024
Golpe: site Meu Título Digital, que cobra R$ 49 para tirar título de eleitor, é falso e não pertence à Justiça Eleitoral
Serviço de emissão e regularização do documento é gratuito e pode ser realizado pelo site do TSE
29.08.2024
Código-fonte da urna eletrônica não foi quebrado e não revela voto do eleitorado
Desinformação antiga, que tratava do log do equipamento, voltou a circular em 202
26.08.2024
Em vídeo antigo, deputado federal engana ao afirmar que urnas estão programadas para definir candidatura vencedora
Discurso foi gravado em 2010 e, ao contrário do disse que faria, parlamentar não apresentou prova da alegação
21.08.2024
É mentira que, sem saber que estava sendo gravada, jornalista admitiu que eleição de 2022 foi roubada
Trecho descontextualizado de comentário tem sido compartilhado nas redes para confundir eleitorado
20.05.2024
Confira explicação da Agência Lupa sobre vídeo no qual ministra Cármen Lúcia fala de liberdade de expressão
Gravação foi feita durante sessão do TSE realizada em outubro de 2022
20.05.2024
Musk não entregou aos EUA provas de supostas interferências nas eleições brasileiras
Checagem realizada pela Agência Lupa desmentiu o boato. Veja:
20.05.2024
"""

PAGE_10 = """
TRE-RS não realizará festa para transmissão dos cargos de presidente e vice-presidente
Publicação no Twitter reproduz convite antigo, divulgado antes dos eventos climáticos que assolaram o estado, e a cerimônia foi cancelada
14.05.2024
Influenciador português mente ao afirmar que urna eletrônica brasileira foi hackeada nos Estados Unidos
Homem repete notícia falsa já desmentida pelo TSE e agências especializadas em checagem de fatos
25.04.2024
Vídeo com fala de jornalista americano não comprova fraude nas Eleições 2022
Documentos apresentados na gravação não têm relação com o pleito
25.04.2024
Fala do ministro Alexandre de Moraes foi retirada de contexto para criar fake news
Agência Boatos.org desmentiu trecho distorcido de relato do ministro em circulação nas redes sociais
12.04.2024
Vídeo engana ao questionar votos após às 17h, proibição de inspeção do código-fonte pelas Forças Armadas e existência de sala secreta do TSE
Nenhuma das alegações é verdadeira. Confira a explicação:
03.04.2024
Eleições 2022: pastor mente ao afirmar que análise de votos nulos e em branco da Bahia indicaria que houve fraude eleitoral
Em audiência pública realizada no Senado, homem propagou dados equivocados e disseminou mentiras sobre urnas eletrônicas
22.03.2024
Eleições 2022: vídeo apócrifo em italiano engana ao afirmar que votação foi fraudada
Entidades nacionais e internacionais acompanharam pleito brasileiro e atestaram segurança da urna
20.03.2024
Eleições 2022: é mentira que partido político tenha encontrado irregularidades em 60% das urnas
Vídeo antigo com informação errada sobre identificação dos equipamentos voltou a circular nas redes sociais.
20.03.2024
Redes sociais e WhatsApp não vão sair do Brasil por causa de resolução do TSE
Vídeo de deputado federal engana ao dizer que normativo prevê censura e monitoramento de usuários
07.03.2024
Eleições 2022: não é verdade que fala de ministro de Estado indique que houve fraude no pleito presidencial
Durante entrevista, ele se referiu aos eleitores aptos a votar e não aos votos efetivamente recebidos pelos candidatos
22.02.2024
"""

PAGE_20 = """
Vídeo sobre relatório de partido é antigo e não comprova problemas nas Eleições 2022
Ao contrário do que alegou a agremiação na época, todas as urnas eletrônicas podem ser identificadas
09.02.2024
Vídeo de reportagem antiga desinforma internautas sobre suposto pedido de anulação das Eleições 2022
Gravação original é de novembro de 2022 e voltou a circular recentemente nas redes sociais. Saiba por que é boato
06.12.2023
Eleitores falecidos de Camaçari (BA) não votaram nas Eleições 2022; site "Veja Seu Voto" não é fonte oficial de informação
Títulos das três pessoas citadas no no vídeo foram cancelados. Nomes delas sequer constam no caderno de votação. Saiba mais:
10.11.2023
Abertura do código-fonte para inspeção é procedimento de auditoria padrão, que ocorre um ano antes das eleições ordinárias
Ao contrário do que afirmou mensagem do Telegram, a medida não foi motivada por pleito para Conselhos Tutelares
16.10.2023
Belo Horizonte não utilizou urnas eletrônicas em eleições anuladas para Conselho Tutelar
Capital mineira usou sistema próprio de votação desenvolvido pelo município
10.10.2023
Senador não disse que partido pagou R$ 50 bilhões ao TSE para tornar adversários inelegíveis
Tarja incluída em gravação antiga mente ao afirmar que legenda subornou o TSE; assessoria do político também desmentiu a alegação
21.09.2023
Presença de público em desfiles de 7 de setembro não é parâmetro para definir candidatura vencedora da eleição
Em vídeo enganoso, homem afirmou que menor participação popular no evento indicaria a vitória do candidato derrotado à Presidência
20.09.2023
Eleições 2022: vídeo inventa dados para afirmar que apuração de urnas foi fraudulenta
Gravação falsa dizia que candidato vencedor do pleito recebeu apenas 15% dos votos válidos
11.09.2023
Postagem usa entrevista de falsa juíza sueca e fala descontextualizada de jornalista para atacar sistema eleitoral
Suposta magistrada é, na verdade, cantora da banda ABBA e o âncora de TV criticava ato de candidato à Presidência
02.08.2023
Fraude eleitoral citada por candidato à Presidência era uma crítica a outros concorrentes e não tinha relação com urnas
Fala antiga recortada de pronunciamento feito em setembro de 2022 voltou a viralizar nas redes sociais
27.07.2023
"""

PAGE_30 = """
Fala do ministro Gilmar Mendes foi editada para sugerir que houve fraude nas Eleições 2022
Trecho descontextualizado citava a figura do mesário pianista, que poderia votar por eleitor ausente
21.07.2023
Fala de ministro Nunes Marques é descontextualizada para sugerir fraude eleitoral
Em trecho que viralizou nas redes, ele apenas citava frases ditas por deputado estadual cassado por mentir sobre urnas
13.07.2023
Ex-ministro do GSI general Etchegoyen não disse que houve manipulação no resultado das Eleições 2022
Legenda que acompanha vídeo com entrevista do militar inventa números para sugerir fraude eleitoral
11.07.2023
Eleições 2022: não é verdade que mesários votaram por eleitores faltosos e que segundo turno teve 4 milhões de votos após às 17h
Em vídeo compartilhado na internet, homem ainda disseminou mentiras sobre biometria
03.07.2023
Deputado federal não mandou TSE entregar código-fonte do sistema eleitoral
Além de antiga, a fala também não menciona as linhas de programação, que ficaram abertas durante um ano para inspeção
03.07.2023
Eleições 2022: Estados Unidos não provaram vitória de candidato derrotado nas urnas
Agência Lupa recebeu nota da Embaixada dos EUA, que reafirmou confiança nas instituições brasileiras
28.06.2023
É mentira que presidente do TSE tenha admitido que Eleições 2022 foram fraudadas
Vídeo que circula de forma descontextualizada se refere a julgamento que discutiu fraude à cota de gênero no município de Roteiro (AL) em 2020
12.06.2023
Suposta perícia forense realizada pelos Estados Unidos não comprovou fraude nas eleições brasileiras
Notícia falsa propaga teorias antigas, já desmentidas pelo TSE e agências de checagem
29.05.2023
Eleição não foi anulada por falha na identificação biométrica do eleitorado
Eleitores são identificados em duas etapas: conferência do documento com foto e biometria cadastrada na JE
03.05.2023
Emissora de televisão não detém código-fonte das urnas eletrônicas
Também não é verdade que veículo de comunicação constatou vitória de candidato derrotado
26.04.2023
"""

PAGE_40 = """
Todas as urnas eletrônicas usadas para colher votos do eleitorado estavam devidamente identificadas
Comentário de apresentador de SC repercute informações equivocadas sobre as Eleições Gerais de 2022
17.02.2023
Homem repete alegações infundadas sobre mensagens nos logs das urnas, votos registrados após as 17h e tempo médio de votação
Análise dos arquivos do TSE resgata teorias falsas que já foram desmentidas pela Justiça Eleitoral
11.01.2023
Autor de vídeo viral engana ao afirmar que votos podem ser transferidos entre candidaturas
Todos os comandos do sistema eletrônico de votação estão contidos no código-fonte, que ficou aberto durante um ano para inspeção
11.01.2023
Homem mente ao afirmar que urna foi programada para favorecer candidata à Presidência nas Eleições 2014
Autor da gravação também não reproduziu o sistema utilizado no equipamento
28.12.2022
Canal argentino dissemina novas mentiras sobre urnas, votação fantasma e transferência de votos em branco para candidato à Presidência
Alegações já foram desmentidas pelo TSE e por agências especializadas em checagem de notícias falsas que circulam na internet
20.12.2022
Homem falecido há 22 anos não votou nas Eleições Gerais de 2022
Informações divulgadas pelo site "Veja Seu Voto" são falsas e não foram retiradas de base de dados do TSE
19.12.2022
Hackers não revelaram vitória de candidato derrotado ao quebrar código-fonte das urnas eletrônicas
Não houve acesso indevido às linhas de programação, que estiveram abertas durante um ano para inspeção
19.12.2022
Contratos de técnicos de urna podem ser consultados pela internet, ao contrário do que alegou candidata à deputada federal
Todas as informações referentes aos serviços contratados pela Justiça Eleitoral são públicas e estão disponíveis nos sites dos TREs
19.12.2022
Tweet fabrica dados para sugerir que votos registrados em papel divergiram de resultado de urna instalada em Israel
Na seção eleitoral 0682, que votou de forma manual e eletrônica, Bolsonaro obteve mais votos que adversário
15.12.2022
Eleitor falecido em 2010 não teve voto computado nas Eleições Gerais de 2022
TRE de São Paulo desmentiu vídeo gravado por mulher que se baseou em resultado de site falso para disseminar desinformação
14.12.2022
"""

PAGE_50 = """
Relatório apócrifo inventa cálculos para apontar existência de algoritmo capaz de desviar votos entre candidatos à Presidência
Texto divulgado na internet não se baseia em critérios claros nem comprova que houve manipulação
14.12.2022
É boato que novas eleições presidenciais foram marcadas para 11 de janeiro de 2023
"Ato Institucional" supostamente assinado pela Presidência não foi publicado no Diário Oficial da União (DOU)
13.12.2022
Mesário não ativou urnas eletrônicas simultaneamente em Campinas e no Guarujá (SP)
Equipamentos chegam aos locais de votação com softwares instalados e lacrados pela Justiça Eleitoral
12.12.2022
Alerta de golpe: votos das Eleições 2022 divulgados por site são falsos
Importante lembrar que voto é sigiloso, inviolável e não pode ser vinculado a eleitores; nem mesmo a Justiça Eleitoral identifica em quem o eleitor votou
11.12.2022
Vereador do Paraná mentiu ao acusar TSE de contratar empresa para monitorar população e censurar redes sociais
Afirmação de que serviço clipping de notícias seria usado para censurar imprensa também é falsa
09.12.2022
Comparação entre gráficos da apuração da eleição presidencial brasileira e pesquisa de intenção de voto nos Estados Unidos é enganosa
Usuário das redes tentou equiparar dados que tratam de assuntos diferentes para sugerir fraude eleitoral
09.12.2022
Código-fonte já foi inspecionado pelas Forças Armadas, ao contrário do que diz mensagem do WhatsApp
Afirmação de que houve fraude nas eleições presidenciais também não é verdadeira
01.12.2022
Texto mente ao afirmar que urnas possuem dois códigos-fonte distintos e que houve fraude nas eleições
Mensagem viral disseminou acusações infundadas pelo aplicativo WhatsApp
01.12.2022
Instituto alemão não apontou fraude nas Eleições Gerais 2022
Gefälschte Nachrichten, entidade citada em suposta reportagem, sequer existe
30.11.2022
Seção em Itabaianinha (SE) foi agregada e não desapareceu, como afirmou eleitor em vídeo enganoso
Votos podem ser consultados por meio do boletim de urna da seção principal
30.11.2022
"""

PAGE_60 = """
Primeiro-ministro holandês não confirmou que eleição presidencial brasileira foi fraudada
Print que atribuía a informação a uma matéria publicada na imprensa era montagem
30.11.2022
Emir do Qatar não mencionou eleições brasileiras na abertura da Copa do Mundo de 2022
Declaração que circula no WhatsApp foi falsamente atribuída a Tamim bin Hamad al-Thani
30.11.2022
Boato: presidente da Rússia não falou que interviria se houvesse fraude nas eleições brasileiras
Em vídeo disseminado na internet, Putin comentava relações comerciais entre os países
30.11.2022
Relatório de partido político é enganoso e não embasa convocação de novas eleições
Comentário de vereador durante entrevista reproduziu informações erradas sobre urnas e descumprimento do Código Eleitoral
30.11.2022
Urnas eletrônicas não foram descartadas de forma ilegal em Porto Alegre (RS)
Fotografia se refere a um acidente que ocorreu no RN em 2009; equipamentos envolvidos não continham dados eleitorais
29.11.2022
Áudio viral mente ao afirmar que votos registrados depois das 17h são indício de fraude e que mesários poderiam votar por eleitores
Pessoas que chegaram à seção eleitoral até este horário e aguardavam na fila puderam votar normalmente
28.11.2022
Resultado das eleições não está sob análise; relatório das Forças Armadas não apontou fraude no pleito
Publicações nas redes sociais distorciam teor do documento elaborado pela instituição
28.11.2022
Mandado de injunção não está relacionado às eleições, nem às urnas eletrônicas
Vídeo repassou informações erradas sobre suposto pedido de entrega do código-fonte
25.11.2022
É falso que ministro Alexandre de Moraes tenha sido intimado por militares sobre fraude nas eleições
Vídeo divulgado no Kwai repercute notícia falsa que circulou nas redes no início de novembro
25.11.2022
É falso que candidato derrotado ganhou eleição presidencial com 51% dos votos
Site de notícias publicou texto apócrifo baseado em relatório enganoso de partido político
25.11.2022
"""

PAGE_70 = """
Informe assinado por pesquisadores da USP, UFSCar e UFABC rebatem alegações infundadas sobre o sistema eleitoral
Estudiosos da área de TI garantem a lisura do sistema eletrônico de votação e desmentem relatos sobre a não confiabilidade das urnas
25.11.2022
Candidato perdeu eleições porque recebeu menos votos e não devido à suposta quebra de código-fonte
Após inspeção de entidades, linhas de programação foram assinadas digitalmente e lacradas; processo impede qualquer tentativa de manipulação
24.11.2022
Votos de São Pedro da Aldeia (RJ) foram contabilizados; local de votação de eleitora foi agregado à seção eleitoral 87
Mulher gravou video enganoso em que afirma ter havido fraude na cidade fluminense
22.11.2022
Não é verdade que juíza sueca afirmou ter havido fraude nas eleições brasileiras
Imagem que circula nas redes sociais é, na verdade, de cantora da banda Abba
22.11.2022
Títulos de eleitor que aparecem em vídeo são inválidos e não indicam que houve fraude nas eleições presidenciais no Ceará
Documentos mostrados pelo autor da gravação estavam sendo levados para local em que seriam devidamente descartados
22.11.2022
Retotalização de eleição proporcional em SP não é a mesma coisa que recontagem de votos
Confira a explicação para tuítes que questionavam reeleição de parlamentar após suspensão do deferimento da candidatura de adversário
22.11.2022
É falso que existam urnas com 1,5 mil eleitores, ao contrário do que alega deputado
Agências de checagem desmentiram informações falsas propagadas durante live transmitida pelo TikTok
22.11.2022
É mentira que fraudes nas urnas do Nordeste foi comprovada e noticiada no exterior
Publicação não traz nenhuma comprovação das suas afirmações e, além disso, a Lei de Benford não serve para verificar a fraude em eleições
22.11.2022
É falso que o Comando do Exército denunciou fraudes nas cidades de Barreiras e "Chiquita", na Bahia
Notícia falsa afirma que candidato à Presidência teria fugido para a Argentina e o ministro Alexandre de Moraes estaria prestes a ser preso
22.11.2022
Não é verdade que Bolsonaro não teve votos em São Gabriel da Cachoeira (AM)
Candidato à reeleição conseguiu, respectivamente nos 1º e 2º turnos, 17,52% e 19,36% dos votos na localidade
22.11.2022
"""

PAGE_80 = """
Peritos federais não comprovaram fraude nas Eleições 2022
Vídeo fora de contexto, gravado em 2018, leva a crer que os peritos criminais federais não atestam a segurança das urnas eletrônicas
22.11.2022
Vídeo não mostra atividade irregular no prédio do TRE de Mato Grosso durante final de semana
Plantão em dias não úteis está previsto no calendário eleitoral e é regulamentado por resolução da corte regional
21.11.2022
Urnas de SP estavam sendo transportadas para depósito do TSE, onde ficarão guardadas até descarte
Equipamentos modelo 2009 não foram utilizados pelo eleitorado do Estado nas Eleições Gerais 2022
21.11.2022
Mesário erra e usa carimbo de não-comparecimento por engano no Rio de Janeiro
Segundo o TRE-RJ, eleitora não foi impedida de votar nos dois turnos das Eleições 2022; hipótese de fraude foi descartada
09.11.2022
É mentira que votos de seção eleitoral em Petrópolis (RJ) não teve votos contabilizados
Seções que foram agregadas, para efeitos logísticos, têm os seus votos somados
09.11.2022
É falso que urnas estão conectadas a sistemas Starlink e eleições foram uma farsa
Áudio com informações falsas que circula nas redes sociais afirma que as Eleições de 2022 foram uma farsa
09.11.2022
É mentira que William Waack denunciou fraude nas urnas eletrônicas
Trecho do vídeo muda o contexto verdadeiro da gravação, que foi uma crítica à campanha de desinformação sobre o processo eleitoral
09.11.2022
Ao contrário do que diz indígena, candidato à Presidência recebeu mais de 15 mil votos em Manicoré (AM)
Vídeo publicado no YouTube, ela disse ter sido cobrada por conterrâneos para saber onde foi parar a votação do político
09.11.2022
TSE não alterou informações sobre resultado das eleições após divulgação de relatório com denúncias falsas
Em vídeo publicado no Instagram, mulher espalhou mentiras a respeito do processo eleitoral
07.11.2022
Eleições presidenciais não foram invalidadas por fraudes em 234 seções eleitorais
Documento cheio de erros de português foi falsamente atribuído ao STM
07.11.2022
"""

PAGE_90 = """
É mentira que candidato à Presidência não recebeu votos na seção 103 de Itacoatiara (AM)
Vídeo gravado por eleitor do município amazonense propaga dados errados da votação
07.11.2022
Tweet erra ao afirmar que seção eleitoral do Pará não teve nenhum voto para candidato à Presidência
Eleitor propagou informações equivocadas ao comentar publicação que questionava resultado do pleito
07.11.2022
Eleitores enganam ao dizer que votos de seções no exterior que não aparecem no app Resultados não foram contabilizados
Ferramenta mostra apenas seções principais. Seções agregadas e demais situações podem ser consultadas pelo Portal de Dados Abertos do TSE
07.11.2022
É falso o documento em que Ministério da Defesa cobra justificativa sobre suposta violação das urnas
STM também não enviou ofício ao TSE excluindo licitude e lisura do processo eleitoral brasileiro
04.11.2022
É falso que candidato à Presidência teve 5,1 milhões de votos roubados
Auditorias realizadas antes, durante e depois das eleições comprovam eficácia das urnas eletrônicas
04.11.2022
Print mostrado em vídeo não comprova que homem falecido votou nas Eleições Gerais de 2022
Mulher engana ao afirmar que informações retidas do site da Justiça Eleitoral indicam que avô compareceu às urnas
04.11.2022
É falso que candidato tenha vencido 2º turno por ter ganhado na maioria das regiões do país
Cálculo feito pelo autor da gravação está errado por não levar em consideração o eleitorado de cada localidade
03.11.2022
Mesária manipulou vídeo para dar a entender que seria possível votar por eleitor faltoso
Ela já havia liberado a votação por ano de nascimento no terminal antes de começar a gravar
03.11.2022
Eleitores não foram impedidos de votar no Amazonas nas Eleições Gerais de 2022
Agência AFP revelou que vídeo circula desde setembro, antes da realização do primeiro e segundo turnos do pleito
30.10.2022
Eleitor não votou duas vezes; vídeo feito por mesária de Rio Branco (AC) é desinformação
Números no terminal também não indicam em quem a pessoa votou
30.10.2022
"""

PAGE_100 = """
Vídeo de homens submetidos a revista policial em rodovia não foi gravado no segundo turno das Eleições Gerais de 2022
Gravação foi feita em abril deste ano durante abordagem a torcedores que se deslocavam para acompanhar jogo da final da Copa Nordeste
30.10.2022
É mentira que urna eletrônica de seção de Taguatinga (DF) não exibiu fotografia para cargo de presidente
Além de homem que fez um vídeo, nenhum outro eleitor relatou ter tido problema para votar no mesmo equipamento
30.10.2022
É falso que houve cobrança de passagem de ônibus no domingo (30) em Recife (PE)
Circula na internet denúncia de que houve descumprimento da gratuidade de passagem de ônibus no segundo turno das eleições
30.10.2022
Blitz da PRF na entrada de Cuité (PB) não impediu votação de eleitores
TRE-PB esclareceu vídeo sobre fiscalização da corporação no município paraibano
30.10.2022
Afirmação de eleitor de Pacajá (PA) sobre resultados que não estariam batendo com número de votos é falsa
TRE-PA esclareceu que só é possível obter o boletim de urna quando votação é encerrada na seção
30.10.2022
Não foi registrado nenhum problema em urna eletrônica de seção eleitoral de São José (SC)
Eleitora que se queixa em vídeo compartilhado pelo WhatsApp conseguiu votar para governador e presidente
30.10.2022
É falsa alegação de que urna eletrônica de Vargeão (SC) exibia fotografia de outra candidatura ao cargo de presidente
Candidata não estava concorrendo à vaga no segundo turno do pleito e, por isso, não seria possível que equipamento mostrasse uma imagem dela
30.10.2022
Não é verdade que eleitores indígenas da região do Xingu em MT não puderam votar por falta de transporte
Dezessete ônibus foram disponibilizados pela prefeitura; dois deles acabaram dispensados por cacique da Aldeia Ilha Grande
30.10.2022
Cônsul-honorária de Brisbane não fazia propaganda de partido durante eleição em Sydney
No momento da foto, ela tinha acabado de receber documento de fiscal do partido presente no local
30.10.2022
Bandeira teve que ser retirada de jardim porque era propaganda irregular
TRE-MG esclareceu que eleitora de MG estava em desacordo com a legislação eleitoral
28.10.2022
"""

PAGE_110 = """
Ex-deputado federal propaga mentiras sobre tempo de votação e inquérito da PF sobre urnas eletrônicas
Equipe de tecnologia da informação do Tribunal não identificou dados que coincidam com eventos descritos na gravação
27.10.2022
Mulher que aparece com adereço vermelho e faz símbolo de candidato não pertence ao quadro de servidores da Justiça Eleitoral
Publicação que circula nas redes dissemina informação falsa com intuito de associar TSE à defesa de candidatura
27.10.2022
É falso que houve fraude no primeiro turno porque não havia tempo suficiente para votação
Agência Lupa desmentiu vídeo de homem que apresentou cálculos que não condizem com dados do TSE
27.10.2022
Não houve fraude em votação para presidente em seção eleitoral de Belém (PA)
Setor de Tecnologia da Informação do TRE-PA não detectou nenhum problema na urna
26.10.2022
Ausência às urnas em certidão de quitação eleitoral de eleitor do Tocantins refere-se às Eleições de 2018
TRE-TO esclareceu episódio ocorrido com eleitor do município de Porto Nacional
25.10.2022
É falso que carros com adesivo de candidato à Presidência e credenciais de acesso livre sejam do TRE-RJ
Veículos de empresas prestadoras de serviços foram credenciados apenas para o primeiro turno do pleito; colabores já foram dispensados pela JE
24.10.2022
Eleitora de Bauru (SP) distorceu informações sobre biometria e confundiu número de candidato para cargo de deputado
Cadastro biométrico não é possível no momento da votação, nem transferência de eleitores entre seções eleitorais de acordo com a faixa etária
21.10.2022
Adesivo colado em vitrine de loja de Chapecó (SC) teve que ser retirado por se tratar de propaganda eleitoral irregular
Empresária foi notificada sobre sentença de juiz eleitoral de Santa Catarina, e não pelo TSE, como afirmou em vídeo
21.10.2022
André Valadão não foi intimado para se retratar perante o TSE; vídeo divulgado pelo cantor é desinformação
Religioso foi citado para responder processo ajuizado pela Coligação Brasil da Esperança, que pediu direito de resposta a conteúdo publicado por ele na internet
20.10.2022
É mentira que homem em gravação da rádio Jovem Pan trabalhe para a Justiça Eleitoral
Vídeo tem sido compartilhado com intuito de sugerir que o TSE estaria censurando emissora
19.10.2022
"""

PAGE_120 = """
Comprovante de votação do segundo turno foi entregue por engano a eleitor de Belém (PA), que não votou duas vezes
Homem foi identificado por biometria e votou somente no primeiro turno, conforme esclareceu o TRE-PA
19.10.2022
Urnas de contingência filmadas em Vale do Anari (RO) não tinham votos de eleitores e foram recolhidas no dia seguinte ao da eleição
TRE de Rondônia divulgou esclarecimento sobre o assunto; confira:
19.10.2022
Vídeo mente sobre invasão de hackers russos a sistema do TSE e paralisação no recebimento de votos de candidato à Presidência
Ao contrário do que afirma teoria da conspiração, não houve nenhum problema durante totalização dos votos no primeiro turno das Eleições 2022
19.10.2022
Áudio viral mente sobre suposto controle de votos por parte de grupo secreto pertencente a partido político
Sigilo do voto é um dos direitos assegurados pela Constituição Federal, pelo Código Eleitoral e pelo sistema eletrônico de votação
18.10.2022
Vídeo de apresentadora do Mato Grosso traz informações equivocadas sobre votos nulos, brancos e urnas eletrônicas
Na gravação, ela ainda questiona a uniformização do horário de votação no Estado
18.10.2022
TSE não proibiu campanha sobre Dia do Médico
Tribunal somente se manifesta se provocado a decidir no caso concreto
18.10.2022
Eleitora não está quite com a Justiça Eleitoral porque deixou de votar no primeiro turno das Eleições 2016
Mulher utilizou comprovante de votação de 2022 para lançar suspeitas infundadas contra urnas eletrônicas
17.10.2022
É boato que hackers russos avisaram o Exército brasileiro sobre fraude no primeiro turno
Mensagem de áudio engana ao dizer que militares agiram após serem avisados de fraude pelos russos
15.10.2022
Boletins de urna mostrados em vídeo não são de MG nem provam fraude
As imagens foram registradas no Rio de Janeiro, como confirmou o TRE-RJ
13.10.2022
É mentira que eleitor deve votar em determinado candidato à Presidência para validar prova de vida junto ao INSS
Mensagem enganosa foi compartilhada pelo aplicativo WhatsApp
11.10.2022
"""

PAGE_130 = """
Smartmatic não fabrica urnas eletrônicas, nem controla eleições no Brasil
CEO da empresa também não foi preso, como anunciava notícia falsa que circulou no Twitter
11.10.2022
É mentira que igreja católica em Quatro Marcos (MT) tenha sido fechada pela Justiça Eleitoral
TRE-MT esclareceu áudio que alegava perseguição religiosa em cidade mato-grossense
10.10.2022
Publicação distorce fala de candidato à Presidência para sugerir que ele pretende promover fraude eleitoral
Trecho reproduzido tratava-se, na verdade, da construção de alianças políticas para compor chapa que concorreria às Eleições Gerais de 2022
10.10.2022
É falso que todas as urnas de local de votação no RS tiveram 129 votos para mesmo candidato à Presidência
TRE-RS desmentiu mensagem falsa atribuída a suposta mesária que circulava no Twitter e no WhatsApp
10.10.2022
Esclarecimento: vídeo que aponta 55% dos votos para um dos candidatos não é falha do TSE, mas resultado no Paraná
Gráfico foi exibido por emissora de TV em transmissão de apuração dos resultados
07.10.2022
Áudio atribuído a Ciro Gomes com acusação de fraude eleitoral é falso
Gravação fala sobre esquema armado para eleger candidato à Presidência da República e tomada de poder pelas Forças Armadas
07.10.2022
Eleitor pressionou duas teclas ao mesmo tempo para simular problema na votação para presidente em Novo Hamburgo (RS)
TRE-RS confirmou que urna eletrônica que aparece em vídeo clandestino não apresentou nenhuma falha
07.10.2022
É falso que haja divergência de dados em boletins de urna de São Joaquim da Barra (SP)
TRE-SP desmentiu vídeo com declaração enganosa feita pelo prefeito da cidade
07.10.2022
Exército não pediu código-fonte de urnas eletrônicas por ter descoberto fraude no "voto de rebanho"
Mensagem e áudio enganosos ganharam projeção nas redes sociais logo após o 1º turno das Eleições 2022
06.10.2022
TSE autorizou campanha de conscientização sobre vacina contra a poliomielite
Tribunal somente não permitiu propaganda política irregular em período eleitoral de pronunciamento nacional do ministro da Saúde
06.10.2022
"""

PAGE_140 = """
Vídeos que levantam suspeitas sobre divergência entre eleitorado da seção e número de votos para presidente em MG são enganosos
A diferença representa a quantidade de pessoas de outros estados e da Zona Eleitoral do Exterior que se habilitaram para votar em trânsito naquela seção
06.10.2022
TRE-MG informa que é falsa informação sobre seção eleitoral que não foi computada no resultado da eleição
Seção mencionada em vídeo foi agregada e teve os votos registrados juntos com os de outra
06.10.2022
TRE-TO esclarece: número maior de votos para presidente em seções do estado se deve ao voto em trânsito
É mentirosa a alegação de que houve fraude no resultado da seção 5 da 29ª Zona Eleitoral de Palmas (TO)
06.10.2022
Urna que não permitia votação para presidente apresentou defeito e foi substituída
Vídeo produzido durante as Eleições Gerais de 2018 voltou a circular sem contexto nas redes para sugerir fraude eleitoral
06.10.2022
Urna não desbloqueia candidato secreto se eleitor pressionar as teclas "5", "Branco" e "Corrige"
Comando não existe e, por isso, sequer é identificado pelo teclado do equipamento
05.10.2022
É falsa lista de cidades nas quais número de votos em candidato à Presidência superou a população
Nenhuma das informações divulgadas pelo conteúdo bate com dados oficias do TSE e do IBGE
04.10.2022
Número de votos não superou quantidade de habitantes da cidade de Barreiras (BA)
Agências de checagem desconstruíram notícia falsa em circulação nas redes
04.10.2022
Caso de eleitora de Manaus (AM) que disse ter sido impedida de votar porque outra pessoa votou por ela já foi resolvido
TRE do Amazonas explicou que eleitor analfabeto colocou digital no local errado do caderno de votação; senhora pôde votar normalmente
04.10.2022
É falso o vídeo que mostra divergência no resultado de Zonas Eleitorais de Maceió (AL)
TRE de Alagoas esclareceu boato que utilizava dados não oficiais para disseminar mentiras sobre totalização dos votos no Estado
04.10.2022
TRE-ES informa: é falsa a informação de que eleitores capixabas já tenham votado para o 2º turno
Foto que circula nas redes sociais é de prova de impressão descartada pela gráfica
04.10.2022
"""

PAGE_150 = """
TRE-RJ esclarece relatos de eleitores que disseram ter sido impedidos de votar porque outros votaram no lugar
Vídeos foram gravados em seções eleitorais de Rio das Ostras, Barra do Piraí, Queimados e Realengo
03.10.2022
É falso que eleitora não teve voto para presidente computado em Curitiba (PR)
Central de Combate à Desinformação do TRE-PR investigou o caso. Confira o esclarecimento:
03.10.2022
É falso que boletins de urna em posse de eleitores comprovam que votos não foram computados em Curitiba (PR)
Em vídeo publicado no Kwai e que circula no WhatsApp, mulher sugere que houve fraude em seção eleitoral da cidade
03.10.2022
Vídeo de mesário de Sete Lagoas sobre diferença na quantidade de votos na urna contém informação falsa
TRE de Minas Gerais divulgou nota de esclarecimento sobre o assunto
03.10.2022
Vídeo engana ao afirmar que fotos de candidatos foram trocadas em Sapiranga (RS)
Eleitores queriam votar em candidato com mesmo nome, que perdeu o mandato e não concorria nesta eleição
02.10.2022
Totalização dos votos em cidades do Brasil e do exterior só foi iniciada às 17h do horário de Brasília
Notícias que circularam na internet afirmavam que imprensa teria divulgado vitória de candidato à Presidência em países estrangeiros
02.10.2022
Eleitores com biometria coletada não precisam assinar caderno de votação
Nota do TRE do Pará esclarece vídeo gravado perto de seção eleitoral de Tucuruí (PA)
02.10.2022
Táxi que transportava urnas em escola de Pilares (RJ) foi escoltado pela Polícia Militar e por auxiliar da Justiça Eleitoral
Ao contrário do que sugere vídeo que circula no TikTok, atividade não é irregular
02.10.2022
Filas em seções eleitorais não devem ser atribuídas à biometria
Espera ocorreu dentro da normalidade. Justiça Eleitoral garantiu o registro do voto de todos que chegaram até as 17h
02.10.2022
Urnas não foram apreendidas em Serafina Corrêa preenchidas com 81% dos votos para candidato à Presidência
Fake recicla dois boatos antigos que circularam na época das Eleições Gerais de 2018
01.10.2022
"""

PAGE_160 = """
É falso que eleitores que apoiam candidatos adversários votarão em dias separados
Todo o eleitorado deve comparecer às urnas no dia 2 de outubro, das 8h às 17h, no horário de Brasília (DF)
30.09.2022
TRE esclarece sobre vídeo de urna eletrônica no porta-malas de um veículo em Campo Grande (MS)
Equipamento era transportado por presidente de seção eleitoral. Não há nenhuma irregularidade no procedimento
30.09.2022
É falsa afirmação de que Polícia Federal (PF) conferiu urnas e que já havia votos inseridos nelas
PF não realizou ação mencionada no vídeo. Site da instituição, inclusive, não divulgou qualquer informação referente ao recolhimento de urnas enviadas para os municípios
30.09.2022
Homem precisou remover pintura de calçada por violação da lei eleitoral, não por "censura"
Checagem desmente notícia falsa que distorce acontecimento em Guarapari (ES)
30.09.2022
Hacker não desviou votos da urna eletrônica nas Eleições Presidenciais de 2018
Ao contrário do que circula na internet, sem a apresentação de provas, pleito daquele ano ocorreu sem nenhum registro de fraude
30.09.2022
Horário de votação será das 7h às 16h apenas em Mato Grosso, Mato Grosso do Sul, Rondônia, Roraima e parte do Amazonas
Em algumas cidades, seções eleitorais poderão abrir e fechar mais cedo ou mais tarde. Entenda:
29.09.2022
Retirar por determinação judicial outdoor com propaganda eleitoral não ataca a liberdade de expressão
Servidor da Justiça Eleitoral é constrangido ao realizar o seu trabalho
29.09.2022
Comprovante de vacinação e uso de máscaras não são obrigatórios para votar nas Eleições 2022
Justiça Eleitoral também não proíbe eleitor de levar celular e usar o e-Título
29.09.2022
É falsa a alegação de que o TSE aumentou o número de locais de votação em prisões e diminuiu as seções eleitorais no exterior
Conteúdo que tem circulado nas redes afirma que essa pretensa alteração na distribuição dos locais de votação visa beneficiar um candidato específico
29.09.2022
Mesário não interfere no cômputo do voto; processo é realizado pelo software da urna eletrônica
Ao contrário do que afirmado em fake news, documento em papel é recibo de quitação para o eleitor e não para a Justiça Eleitoral
28.09.2022
"""

PAGE_170 = """
Fato ou Boato: associar mortes por covid-19 e seções eleitorais é incorreto
Autora da postagem já esclareceu que dado equivocado partiu de um cálculo próprio
28.09.2022
Vídeo confunde ao afirmar que mensagem "Confira o seu voto" pode anular voto de eleitor
Nova funcionalidade visa estimular eleitorado a conferir os números digitados antes de confirmar a votação
27.09.2022
Boato: aplicativo Pardal não recebe relatos de problemas com a urna
Queixas de eleitores sobre o funcionamento da votação devem constar da ata a ser comunicada ao juiz responsável pela seção eleitoral
27.09.2022
Esclarecimento sobre vídeo gravado durante preparação de urnas em Itapeva (SP)
Servidores foram ameaçados por moradora que questionava a lisura do procedimento, realizado em espaço ao lado de cartório eleitoral
26.09.2022
É falso que TSE ordenou que todos os vídeos dos atos de 7 de Setembro sejam excluídos da internet
Proibição diz respeito exclusivamente à reprodução de imagens em propaganda eleitoral de candidato à Presidência
24.09.2022
Código Eleitoral prevê prisão em diversos casos no dia da eleição, não apenas pelo uso de celular
Checagem feita pela agência AFP desmentiu rumor compartilhado na internet
24.09.2022
Vídeo propaga inverdades sobre serviços e procedimentos terceirizados no processo eleitoral
Diversas afirmações feitas na gravação são falsas ou distorcidas. Entenda:
23.09.2022
TSE nunca comunica o cancelamento do título de eleitor por e-mail, WhatsApp, Telegram ou mensagens de texto
Justiça Eleitoral não toma a iniciativa de informar irregularidades no cadastro eleitoral. Cabe à eleitora ou ao eleitor consultar a situação no Portal do TSE na internet
21.09.2022
Foto de ministro do TSE Benedito Gonçalves com blusa de candidato à Presidência é montagem
Rosto do corregedor-geral da Justiça Eleitoral foi inserido em imagem de blogueiro de moda
16.09.2022
É mentira que Pardal não receba denúncias do PT, PCdoB, PSOL e Rede
Como as legendas estão federadas por quatro anos, queixas relativas a esses partidos devem ser feitas em nome da federação
16.09.2022
"""

PAGE_180 = """
TSE não proibiu presidente de reduzir preço dos combustíveis
Notícia falsa circulou em grupos de WhatsApp e enganou parte do eleitorado
06.09.2022
Mensagem que anunciava revelação de esquema de fraude nas urnas por ex-deputado é falsa
Agência de checagem E-farsas desmentiu boato que circulava no WhatsApp e no Telegram
02.09.2022
Post resgata notícias falsas das Eleições 2018 já desmentidas pelo TSE e por agências de checagem
Boatos reciclados usam montagem para alegar fraude na urna eletrônica e reproduzem vídeos de eleitores que anularam voto ao errar ordem de votação
25.08.2022
QR Code no título serve apenas para autenticar documentos e não computa voto do eleitor
Vídeo que circula engana ao afirmar que letras e números favorecem candidato. Código é totalmente aleatório
17.08.2022
Vídeo desinforma ao repetir alegações enganosas feitas em encontro com embaixadores
Comentarista distorce informações sobre inquérito que apura acesso a indevido à sistema interno do TSE, que não afetou segurança das Eleições Gerais de 2018
08.08.2022
Hacker foi preso por vazar dados de pelo menos 233 milhões de pessoas, não por invadir TSE
Embora seja suspeito de compartilhar dados de ex-servidores e ex-ministros, motivo da prisão foi o compartilhamento de informações como CPFs e endereços de milhões de brasileiros
08.08.2022
Mesário não pode anular voto de quem usar camiseta amarela para votar
Equipamentos utilizados por esses colaboradores não podem modificar resultado da votação. Também não há restrição quanto ao uso de cores durante o pleito
08.08.2022
Ministro Edson Fachin não foi advogado do MST
Checagem desmente alegação falsa que circulou no Twitter
26.07.2022
Uso da bandeira do Brasil não vai ser proibido durante a campanha eleitoral
Para Plenário do TRE-RS, símbolos nacionais não têm conotação governamental, ideológica ou partidária
20.07.2022
O sistema eleitoral brasileiro possui, sim, mecanismos de auditoria para as urnas eletrônicas
Checagem desmonta boatos infundados que circulam no Facebook e no Twitter
20.07.2022
"""

PAGE_190 = """
É falso que reunião no TSE não contou com a presença de técnicos
Encontro da Comissão de Transparência Eleitoral, em conjunto com o Observatório de Transparência Eleitoral (ODE) reuniu 34 representantes de instituições públicas e privadas
29.06.2022
Urnas não autocompletaram voto em candidato à Presidência nas Eleições Gerais de 2018
Eleitoras de seção eleitoral de SP mencionaram um vídeo falso já desmentido pelo TRE de Minas Gerais
27.06.2022
É falsa afirmação de que Fachin teria falado sobre "casinha secreta" durante apuração nas Eleições 2022
Vídeo atribui fala falsa ao presidente da Corte Eleitoral para atacar urnas e convite a observadores estrangeiros
03.06.2022
Ex-diretor da Datafolha não gravou áudio que narra suposto plano para fraudar urnas
Gravação que viralizou nas redes é, na verdade, uma sátira feita por um canal de humor no YouTube
03.06.2022
É falso que 'vídeo vazado' de campanha de candidato à Presidência comprove fraude nas urnas em 2002
Fake reproduz trecho de documentário que mostra preparação para um debate; urnas eletrônicas sequer são citadas na gravação original
30.05.2022
É falso que peritos da PF demonstraram que urnas eletrônicas não são confiáveis
Fala de deputado federal sobre testes públicos de segurança é desinformação: investidas ocorrem em ambiente controlado e achados já foram corrigidos
27.05.2022
Fake distorce acontecimentos do TPS 2017 para insinuar fragilidade dos sistemas eleitorais
Achados de investigadores da Polícia Federal já foram corrigidos com o fortalecimento de criptografia do sistema operacional da urna eletrônica
11.05.2022
Votar nulo ou em branco para outros cargos não anula votação para presidente
Ao contrário do que afirmam em fake news na internet, não existe "voto parcial" e é possível votar em apenas uma das funções que estão em disputa
10.05.2022
É falsa afirmação feita em vídeo de que eleitora idosa de Santa Catarina teve título indevidamente cancelado
TRE catarinense esclarece que documento da eleitora está cancelado desde 2016 porque ela não compareceu à revisão de eleitorado na cidade onde mora
20.04.2022
É falso que eleitor não esteja quite com a Justiça Eleitoral, apesar de alegar ter todos os comprovantes de votação
TRE do Maranhão esclarece que eleitor não votou no 2º turno das Eleições de 2016 e que a falta de quitação não impede, por si só, o exercício do voto
18.04.2022
"""

PAGE_200 = """
É falsa a afirmação de que o aplicativo e-Título é espião
Para que o eleitor possa acessar os vários serviços oferecidos, o e-Título solicita autorizações de acesso, em cumprimento ao que exige a LGPD
12.04.2022
Título de maiores de 70 anos não está sendo cancelado
Mais uma desinformação propagada nas redes sociais e vai contra decisões recentes do próprio TSE. Além disso, o voto para eleitores com mais de 70 anos é facultativo
25.03.2022
Empresa norte-americana não foi multada por fraudar urnas eletrônicas
Penalidades aplicadas à Diebold resultaram de acordos judiciais realizados nos Estados Unidos
25.02.2022
Certificação das urnas não é responsabilidade do Inmetro
Boato espalhado no Facebook utilizava o instituto para dar a entender que as urnas não teriam qualidade
25.02.2022
Notícia enganosa alega perseguição a juiz e faz insinuações infundadas sobre urnas eletrônicas
Postagem confunde ao afirmar que sistema eletrônico de votação não pode ser auditado
25.02.2022
Aplicativo que simula votação em político não tem relação com urnas eletrônicas oficiais
TSE não utiliza aparelho celular para colher voto do eleitorado
25.02.2022
TSE não descumpriu prazo para responder questionário das Forças Armadas sobre voto eletrônico
Não havia data-limite para entrega das respostas, que foram divulgadas na íntegra no dia 16 de fevereiro de 2022
22.02.2022
Eleições 2014: É boato que técnicos do Tribunal tenham se trancado em sala até o término da totalização dos votos
Em razão dos diferentes fusos, TSE seguiu norma que impede divulgação do resultado das eleições presidenciais antes do fim da votação no Acre
09.08.2021
É falso que ministro Alexandre de Moraes disse que cassará chapa se Bolsonaro for reeleito
Publicações compartilhadas no Facebook, YouTube e WhatsApp distorceram fala do ministro durante julgamento no TSE
20.12.2021
É falso que beneficiário do INSS tenha de comparecer a cartório eleitoral para fazer validação facial
Em outubro de 2021, atendimento presencial estava suspenso para prevenir contágio pelo novo coronavírus
21.10.2021
"""

PAGE_210 = """
É falso que 7 de setembro fará plenário da Câmara reanalisar PEC do voto impresso
Fala do presidente da Câmara dos Deputados, Arthur Lira, aconteceu um mês antes e circulou nas redes de forma totalmente descontextualizada
24.09.2021
Postagem recicla vídeo de cantor sertanejo com acusação infundada contra urna eletrônica
Gravação antiga afirma que 80% das urnas brasileiras são fraudadas. Saiba por que a informação é falsa
20.09.2021
São falsas as afirmações sobre insegurança do sistema eletrônico de votação
Desde a adoção das urnas eletrônicas, em 1996, nenhuma fraude foi comprovada
09.09.2021
Vídeo engana ao afirmar que TSE e STF querem barrar cristãos na política
Gravação ganhou força nas redes sociais, mas o conteúdo é duvidoso e não condiz com a realidade
30.08.2021
Outros países, além de Brasil, Butão e Bangladesh usam urnas sem voto impresso
Checagem desmonta notícia falsa que voltou a circular nas redes sociais. Confira
30.08.2021
É enganoso vídeo com compilado de alegações sobre fraude no sistema eleitoral
Gravação trazia edições e fake news antigas já desmentidas por agências e pela Justiça Eleitoral
24.08.2021
Emissora de TV não fez reportagem admitindo possibilidade de fraude nas urnas
Vídeo compartilhado pelo WhatsApp omitiu trechos da matéria, exibida em 2008, para lançar suspeitas sobre a credibilidade das eleições brasileiras
23.08.2021
Inquérito da PF não investiga fraude no processo de votação
[SEM_RESUMO]
17.08.2021
É falsa planilha que mostraria supostas inversões entre presidenciáveis no 2º turno das Eleições 2014
Documento oficial do TSE mostra apuração minuto a minuto. Houve uma única mudança de colocação entre os candidatos
28.07.2021
Voto impresso não está previsto em lei desde 2002
Lei nº 10.408, que instituiu a impressão do voto na época, foi revogada em 2003
23.07.2021
"""

PAGE_220 = """
Em 2020, TSE lançou campanha “Se for fake news, não transmita” e tomou a frente no combate à desinformação no contexto eleitoral
Ação, que contou com participação do biólogo Átila Iamarino, foi veiculada em emissoras de rádio e de televisão
08.09.2020
Efetivo de reserva das Forças Armadas não foi convocado para ser mesário nas Eleições 2020
Mensagem que tem circulado nas redes sociais anunciando que militares da reserva seriam convocados para atuar como mesários nas eleições é falsa
24.09.2020
É falso que TSE censurou o WhatsApp para impedir denúncias sobre a urna eletrônica
[SEM_RESUMO]
01.10.2020
Brasil, Cuba e Venezuela não são os únicos países que usam urnas eletrônicas
Fake que circula há anos na internet afirma que somente três países adotam meios eletrônicos de votação. Saiba por que a informação não é verdadeira
02.10.2020
É falso que atuar como mesário suspende recebimento do auxílio-emergencial e outros benefícios sociais
Trabalhar como mesário não cancela ou suspende benefício que o cidadão receba, como o Bolsa-Família e outros
08.10.2020
Cidades não vão parar por três meses depois das eleições municipais
Não há previsão de lockdown programado pelo governo do Ceará; informação foi confirmada pela Secretaria Estadual de Saúde e também pela coordenação de imprensa do Estado
27.10.2020
Governo Federal não criou programa Voto em Casa; cadastro é falso e pode trazer riscos
Comunicado enganoso em aplicativo de mensagens pede para cidadão clicar em link para se cadastrar para votar pelo celular
11.11.2020
Conheça os principais boatos sobre as Eleições Municipais 2020 que viralizaram na web
Parceiros do TSE no enfrentamento da desinformação apuraram dezenas de notícias falsas que foram veiculadas no contexto das Eleições 2020 e publicaram os seus desmentidos
15.11.2020
Vídeo faz alegação falsa sobre redução de votos de candidata em Palmas (TO)
A contagem dos votos pode ser feita por qualquer eleitor, a partir dos votos apurados no momento da impressão do Boletim de Urna, logo após o encerramento da votação
18.11.2020
Vídeo não prova que sistema da urna pode ser fraudado
TSE divulgou nota que reforça segurança dos equipamentos
18.11.2020
"""

PAGE_230 = """
Checagens descartam alegações de fraude nas eleições de Macaé (RJ)
Demora em mostrar a foto de candidato ocorre em algumas urnas mais antigas, como em qualquer computador com processadores mais lentos
19.11.2020
Vídeo de idosa agredida em Magé (RJ) não está relacionado à votação do 1º turno das Eleições 2020
Agressão não tem relação com as Eleições Municipais de 2020; mulheres envolvidas são concorrentes comerciais e tinham uma desavença por conta de comentários em redes sociais
19.11.2020
Eleições pelo país não foram anuladas por fraude nas urnas ou na apuração
TSE esclarece que são falsas mensagens que circulam em redes sociais sobre anulação das eleições
20.11.2020
TSE não atualizou apuração de votos com base em informações de sites de notícias
Os arquivos para divulgação de resultados, disponibilizados a empresas jornalísticas, são os mesmos do sistema do Tribunal, acessíveis por qualquer cidadão
20.11.2020
Notícias desmentem fake sobre alteração de votos em Belford Roxo (RJ)
Ex-candidato a vereador da cidade do Rio de Janeiro levantou suspeitas sobre a votação de dois candidatos de Belford Roxo (RJ)
23.11.2020
Confira a verdade sobre candidato a vereador que alega ter recebido oito votos na Paraíba
Ex-candidato em João Pessoa (PB) afirma em vídeo que não teve nenhum voto na seção eleitoral em que votou. TRE-PB teria dito que corrigiria a situação
23.11.2020
Fato: zona eleitoral no conjunto de favelas da Maré (RJ) foi transferida
É verdadeira a informação que circula nas redes sociais sobre a mudança de uma zona eleitoral na localidade, no Rio de Janeiro
26.11.2020
É falso que resultado da eleição para prefeito em Queimados (RJ) está sendo investigado e pode mudar
Boato que circula nas redes sociais afirma que o resultado do pleito para a prefeitura do município fluminense foi suspenso em razão de indícios de fraude
28.11.2020
Confira o balanço das principais fake news envolvendo as Eleições 2020
Veja vídeo em que a secretária-geral do TSE apresenta o levantamento das principais notícias falsas sobre o último pleito municipal que circularam nas redes
28.11.2020
É falso que hacker teria atacado sistema de votação no 1º turno das Eleições Municipais de 2020
Postagens sugerem que suposta violação seria responsável pelo breve atraso na divulgação dos resultados
29.11.2020
"""

PAGE_240 = """
Vídeo não mostra "urna adulterada" dentro de caminhonete particular em Fortaleza (CE)
Material que circula em redes sociais diz que urnas filmadas na caçamba de uma picape estariam sendo levadas por cabos eleitorais de candidato do PDT à prefeitura
29.11.2020
Presidente de seção eleitoral do RJ não impediu fiscais de assinarem a zerésima
Vídeo com informações falsas circula nas redes alegando que equipe do candidato a prefeito do Rio Marcelo Crivella foi proibida de assinar o documento
29.11.2020
Vídeo que denuncia suposta fraude nas urnas em João Pessoa (PB) é enganoso
Candidato a vereador disse não ter recebido votos na seção onde ele próprio votou. Documentos oficiais mostram que ele teve dois votos no local
04.12.2020
Eleições 2018: candidata ao cargo de deputado federal em São Paulo alegou possuir provas irrefutáveis de fraudes nas urnas e nas eleições
Aplicação de cálculo matemático apresentado no vídeo não é confiável no contexto eleitoral. Saiba mais:
22.10.2018
Eleições 2018: eleitor pode votar somente no cargo de presidente
Ao contrário do que dizia notícia falsa, é possível votar em branco para outros cargos sem prejuízo de anulação total da votação
22.10.2018
Eleições 2018: não é verdade que só três países usam urna eletrônica
Boato espalhado nas redes sociais não se baseou em informações confiáveis
22.10.2018
Eleições 2018: é falso que boletim de urna tenham registrado 9.909 votos para candidato à Presidência em Nagoia, no Japão
Montagem foi compartilhada para lançar dúvida sobre lisura do pleito ao insinuar que seção tinha mais votos do que eleitores
11.10.2018
Eleições 2018: votos foram anulados por eleitores, e não pela Justiça Eleitoral
Texto que circulou no WhatsApp divulgava informações erradas a respeito da votação
11.10.2018
Eleições 2018: códigos de urnas não foram entregues a venezuelanos como diz boato na internet
Notícia falsa compartilhada nas redes sociais afirma que uma empresa venezuelana teria conseguido acesso a arquivos da urna brasileira
22.10.2018
Boletim de urna com 9.909 votos em candidato à Presidência nas Eleições Gerais de 2018 é montagem
Documento foi adulterado para dar a entender que número de votos foi superior à quantidade de eleitores
11.10.2018
"""

PAGE_250 = """
Eleições 2018: modelo estatístico “Lei de Benford” não pode ser aplicado em resultados eleitorais
Inúmeros trabalhos acadêmicos apontou que metodologia não é confiável para análise de integridade do pleito
13.10.2018
Eleições 2018: código "555" só pode ser acionado em situações específicas, ao contrário do que afirma mensagem
Desinformação causou confusão às vésperas do 2º turno das Eleições de 2018 e pode ter contribuído para que eleitores perdessem voto
16.10.2018
Exército desmentiu boato de que iria convocar novas eleições com cédulas de papel
Circulou na web informação de que, se comprovada fraude nas Eleições 2018, a instituição iria anular o pleito e realizar nova votação. Confira os detalhes
17.10.2018
Eleições 2018: auditoria do TRE-PR comprovou que urnas não foram adulteradas
Delegado que se elegeu deputado estadual veiculou desinformação em vídeo transmitido ao vivo pelo Facebook
22.10.2018
Eleições 2018: problema técnico em urna foi usado para sugerir fraude eleitoral em SP
TRE-SP realizou auditoria pública e constatou que houve falha no teclado do equipamento
22.10.2018
Eleições 2018: Polícia Federal não apreendeu van com urnas eletrônicas adulteradas
Informação falsa dizia que a notícia havia sido veiculado por emissora de televisão
22.10.2018
Eleições 2018: uso de camiseta com inscrição de candidato não anula voto
Postagens que circularam na véspera e no dia do primeiro turno da votação passam informações erradas ao eleitorado
22.10.2018
Post viral recicla boato de 2018 sobre Projeto Você Fiscal, inativo desde 2016
Notícia falsa já foi esclarecida pela Justiça Eleitoral e por agências de checagem
22.10.2018
Eleições 2018: diretor da OEA não admitiu negociação para fraudar urna eletrônica
Capas de revistas com supostas críticas internacionais eram montagens
22.10.2018
Eleições 2018: Forças Armadas não exigiram que urnas eletrônicas fossem periciadas
Exército, Marinha, Aeronáutica e TSE negaram a existência do ofício com pedido inusitado
22.10.2018
"""

PAGE_260 = """
Eleições 2018: empresa venezuelana não é responsável pelas urnas eletrônicas
Não há nenhuma comprovação de fraude nos pleitos realizados após a adoção do equipamento pela Justiça Eleitoral
22.10.2018
Eleições 2018: mesário não pode falsificar assinatura e anular voto de eleitores
Boato que circulou na internet ainda pedia que apoiadores de um determinado candidato não utilizassem vestimentas que identificassem a preferência
22.10.2018
Eleições 2018: apresentador de TV e eleitores afirmaram erroneamente que tecla confirma não aparecia ao votar para presidente
Equipamento conta com teclado físico; botão verde, localizado no canto inferior, serve para confirmar o voto
22.10.2018
Eleições 2018: notícia sobre apreensão de urnas pela PM do Amazonas é falsa
Rumor distorceu fato que ocorreu na estrada de Autazes, município que fica a 113 quilômetros de Manaus
23.10.2018
Eleições 2018: confira o resultado da auditoria nas urnas de SP
Especialista espalhou mentiras ao afirmar que auditoria nas urnas eletrônicas realizada pelo TRE-SP não obteve o resultado esperado
26.10.2018
Ministros Barroso e Moraes não mandaram fabricar chips em Taiwan para fraudar urnas eletrônicas
Postagem falsa distorce conteúdo de portal de notícias sobre a crise do semicondutores, ocorrida durante a pandemia
29.06.2026
É falso que Eleições 2026 terão novas urnas; presença de observadores internacionais e abertura de código-fonte também não são novidade
Mensagem compartilhada nas redes sociais distorce procedimentos já previstos na legislação e realizados regularmente pela Justiça Eleitoral
31.07.2026
"""

ALL_PAGES = [
    PAGE_0, PAGE_10, PAGE_20, PAGE_30, PAGE_40, PAGE_50, PAGE_60, PAGE_70,
    PAGE_80, PAGE_90, PAGE_100, PAGE_110, PAGE_120, PAGE_130, PAGE_140,
    PAGE_150, PAGE_160, PAGE_170, PAGE_180, PAGE_190, PAGE_200, PAGE_210,
    PAGE_220, PAGE_230, PAGE_240, PAGE_250, PAGE_260,
]



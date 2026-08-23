# -*- coding: utf-8 -*-
"""
Dumps BRUTOS (com cabecalho "Resultado da busca / Filtros: X / Foram
encontrados N resultados." e rodape de paginacao "< Anterior ... Proximo >"),
copiados verbatim da saida do navegador, para 7 tags adicionais do site real
justicaeleitoral.jus.br/fato-ou-boato -- coletadas em 23/08/2026 para tentar
AUMENTAR o Dataset A alem da tag "fake news" (ja com populacao completa,
267 itens, sem novos itens desde a coleta original).

Tags adicionais coletadas (populacao COMPLETA de cada uma, confirmada pelo
numero "Foram encontrados N resultados." de cada uma):
  - fraude          (85 itens, 9 paginas)
  - resultado       (12 itens, 2 paginas)
  - crime eleitoral (4 itens, 1 pagina)
  - boletim de urna (28 itens, 3 paginas)
  - totalização     (17 itens, 2 paginas)
  - código-fonte    (23 itens, 3 paginas)
  - biometria       (11 itens, 2 paginas)

Estas tags foram escolhidas por serem tematicamente sobre desinformacao
eleitoral (fraude em urnas, apuracao, codigo-fonte, biometria etc.) -- o
mesmo escopo do estudo -- e nao tags genericas de golpe financeiro/phishing
(que tambem existem no site, mas fogem do escopo de "desinformacao eleitoral").
Ha sobreposicao esperada com a tag "fake news" e entre si (um item pode ter
varias tags); a deduplicacao por titulo exato e feita em build_dataset_a_v2.py,
que mantem so os itens GENUINAMENTE NOVOS (nao presentes nos 267 originais).

Cada bloco de item tem 1 ou 2 linhas antes da data (so titulo, ou
titulo+resumo) -- ao contrario da tag "fake news", que sempre tinha resumo.
O parser em build_dataset_a_v2.py usa a linha de data (dd.mm.aaaa) como
delimitador de item, entao lida com ambos os casos automaticamente.
"""

# ---------------------------------------------------------------- fraude ---
FRAUDE_PAGE_0 = """
Resultado da busca

Filtros: fraude

Foram encontrados 85 resultados.

TRE-SP não escolheu urnas submetidas ao teste realizado no dia da eleição

Auditoria é aplicada em equipamentos sorteados ou definidos pelas entidades fiscalizadoras

27.10.2024
Golpe: site Meu Título Digital, que cobra R$ 49 para tirar título de eleitor, é falso e não pertence à Justiça Eleitoral

Serviço de emissão e regularização do documento é gratuito e pode ser realizado pelo site do TSE

29.08.2024
Eleições 2018: pleito presidencial não foi definido no primeiro turno; nenhuma fraude foi comprovada

Declarações falsas de candidato voltaram a circular na web. Confira a explicação:

20.05.2024
Influenciador português mente ao afirmar que urna eletrônica brasileira foi hackeada nos Estados Unidos

Homem repete notícia falsa já desmentida pelo TSE e agências especializadas em checagem de fatos

25.04.2024
Eleições 2022: não é verdade que fala de ministro de Estado indique que houve fraude no pleito presidencial

Durante entrevista, ele se referiu aos eleitores aptos a votar e não aos votos efetivamente recebidos pelos candidatos

22.02.2024
Vídeo sobre relatório de partido é antigo e não comprova problemas nas Eleições 2022

Ao contrário do que alegou a agremiação na época, todas as urnas eletrônicas podem ser identificadas

09.02.2024
Eleições 2022: vídeo inventa dados para afirmar que apuração de urnas foi fraudulenta

Gravação falsa dizia que candidato vencedor do pleito recebeu apenas 15% dos votos válidos

11.09.2023
Postagem usa entrevista de falsa juíza sueca e fala descontextualizada de jornalista para atacar sistema eleitoral

Suposta magistrada é, na verdade, cantora da banda ABBA e o âncora de TV criticava ato de candidato à Presidência

02.08.2023
Fraude eleitoral citada por candidato à Presidência era uma crítica a outros concorrentes e não tinha relação com urnas

Fala antiga recortada de pronunciamento feito em setembro de 2022 voltou a viralizar nas redes sociais

27.07.2023
Fala de ministro Nunes Marques é descontextualizada para sugerir fraude eleitoral

Em trecho que viralizou nas redes, ele apenas citava frases ditas por deputado estadual cassado por mentir sobre urnas

13.07.2023
< Anterior
1
(atual)
2
3
4
5
6
7
...
9
Próximo >
"""

FRAUDE_PAGE_10 = """
Resultado da busca

Filtros: fraude

Foram encontrados 85 resultados.

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
Todas as urnas eletrônicas usadas para colher votos do eleitorado estavam devidamente identificadas

Comentário de apresentador de SC repercute informações equivocadas sobre as Eleições Gerais de 2022

17.02.2023
Homem repete alegações infundadas sobre mensagens nos logs das urnas, votos registrados após as 17h e tempo médio de votação

Análise dos arquivos do TSE resgata teorias falsas que já foram desmentidas pela Justiça Eleitoral

11.01.2023
Autor de vídeo viral engana ao afirmar que votos podem ser transferidos entre candidaturas

Todos os comandos do sistema eletrônico de votação estão contidos no código-fonte, que ficou aberto durante um ano para inspeção

11.01.2023
Canal argentino dissemina novas mentiras sobre urnas, votação fantasma e transferência de votos em branco para candidato à Presidência

Alegações já foram desmentidas pelo TSE e por agências especializadas em checagem de notícias falsas que circulam na internet

20.12.2022
Homem falecido há 22 anos não votou nas Eleições Gerais de 2022

Informações divulgadas pelo site “Veja Seu Voto” são falsas e não foram retiradas de base de dados do TSE

19.12.2022
Hackers não revelaram vitória de candidato derrotado ao quebrar código-fonte das urnas eletrônicas

Não houve acesso indevido às linhas de programação, que estiveram abertas durante um ano para inspeção

19.12.2022
< Anterior
1
2
(atual)
3
4
5
6
7
...
9
Próximo >
"""

FRAUDE_PAGE_20 = """
Resultado da busca

Filtros: fraude

Foram encontrados 85 resultados.

Contratos de técnicos de urna podem ser consultados pela internet, ao contrário do que alegou candidata à deputada federal

Todas as informações referentes aos serviços contratados pela Justiça Eleitoral são públicas e estão disponíveis nos sites dos TREs

19.12.2022
Eleitor falecido em 2010 não teve voto computado nas Eleições Gerais de 2022

TRE de São Paulo desmentiu vídeo gravado por mulher que se baseou em resultado de site falso para disseminar desinformação

14.12.2022
Relatório apócrifo inventa cálculos para apontar existência de algoritmo capaz de desviar votos entre candidatos à Presidência

Texto divulgado na internet não se baseia em critérios claros nem comprova que houve manipulação

14.12.2022
Alerta de golpe: votos das Eleições 2022 divulgados por site são falsos

Importante lembrar que voto é sigiloso, inviolável e não pode ser vinculado a eleitores; nem mesmo a Justiça Eleitoral identifica em quem o eleitor votou

11.12.2022
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
Primeiro-ministro holandês não confirmou que eleição presidencial brasileira foi fraudada

Print que atribuía a informação a uma matéria publicada na imprensa era montagem

30.11.2022
Emir do Qatar não mencionou eleições brasileiras na abertura da Copa do Mundo de 2022

Declaração que circula no WhatsApp foi falsamente atribuída a Tamim bin Hamad al-Thani

30.11.2022
< Anterior
1
2
3
(atual)
4
5
6
7
...
9
Próximo >
"""

FRAUDE_PAGE_30 = """
Resultado da busca

Filtros: fraude

Foram encontrados 85 resultados.

Boato: presidente da Rússia não falou que interviria se houvesse fraude nas eleições brasileiras

Em vídeo disseminado na internet, Putin comentava relações comerciais entre os países

30.11.2022
Áudio viral mente ao afirmar que votos registrados depois das 17h são indício de fraude e que mesários poderiam votar por eleitores

Pessoas que chegaram à seção eleitoral até este horário e aguardavam na fila puderam votar normalmente

28.11.2022
Mulher engana ao afirmar que relatório apócrifo comprova fraude nas eleições

Documento que circula na internet não é oficial e possui informações erradas

28.11.2022
Resultado das eleições não está sob análise; relatório das Forças Armadas não apontou fraude no pleito

Publicações nas redes sociais distorciam teor do documento elaborado pela instituição

28.11.2022
É falso que ministro Alexandre de Moraes tenha sido intimado por militares sobre fraude nas eleições

Vídeo divulgado no Kwai repercute notícia falsa que circulou nas redes no início de novembro

25.11.2022
Votos de São Pedro da Aldeia (RJ) foram contabilizados; local de votação de eleitora foi agregado à seção eleitoral 87

Mulher gravou video enganoso em que afirma ter havido fraude na cidade fluminense

22.11.2022
Não é verdade que juíza sueca afirmou ter havido fraude nas eleições brasileiras

Imagem que circula nas redes sociais é, na verdade, de cantora da banda Abba

22.11.2022
Peritos federais não comprovaram fraude nas Eleições 2022

Vídeo fora de contexto, gravado em 2018, leva a crer que os peritos criminais federais não atestam a segurança das urnas eletrônicas

22.11.2022
Eleições presidenciais não foram invalidadas por fraudes em 234 seções eleitorais

Documento cheio de erros de português foi falsamente atribuído ao STM

07.11.2022
É falso o documento em que Ministério da Defesa cobra justificativa sobre suposta violação das urnas

STM também não enviou ofício ao TSE excluindo licitude e lisura do processo eleitoral brasileiro

04.11.2022
< Anterior
1
2
3
4
(atual)
5
6
7
...
9
Próximo >
"""

FRAUDE_PAGE_40 = """
Resultado da busca

Filtros: fraude

Foram encontrados 85 resultados.

Ausência às urnas em certidão de quitação eleitoral de eleitor do Tocantins refere-se às Eleições de 2018

TRE-TO esclareceu episódio ocorrido com eleitor do município de Porto Nacional

25.10.2022
Comprovante de votação do segundo turno foi entregue por engano a eleitor de Belém (PA), que não votou duas vezes

Homem foi identificado por biometria e votou somente no primeiro turno, conforme esclareceu o TRE-PA

19.10.2022
É boato que hackers russos avisaram o Exército brasileiro sobre fraude no primeiro turno

Mensagem de áudio engana ao dizer que militares agiram após serem avisados de fraude pelos russos

15.10.2022
TRE-PB informa que é falsa a informação sobre suposta irregularidade no envio de mídias de resultados em João Pessoa

Boletim de Urna da seção 442 reflete o resultado totalizado e divulgado pelo TSE

08.10.2022
Hacker não desviou votos da urna eletrônica nas Eleições Presidenciais de 2018

Ao contrário do que circula na internet, sem a apresentação de provas, pleito daquele ano ocorreu sem nenhum registro de fraude

30.09.2022
Mensagem que anunciava revelação de esquema de fraude nas urnas por ex-deputado é falsa

Agência de checagem E-farsas desmentiu boato que circulava no WhatsApp e no Telegram

02.09.2022
É falso que hacker tenha invadido rede interna do TRE-RJ para desviar votos nas Eleições 2012

Desinformação requentada foi desmentida pela própria corte regional do Estado. Confira a explicação

24.08.2022
Votos brancos e nulos não foram transferidos para candidaturas durante “apagões” nas Eleições 2014 e 2018

Não há provas de fraudes nesses pleitos, ao contrário do que sugerem alegações falsas propagadas no TikTok

25.07.2022
É falso que reunião no TSE não contou com a presença de técnicos

Encontro da Comissão de Transparência Eleitoral, em conjunto com o Observatório de Transparência Eleitoral (ODE) reuniu 34 representantes de instituições públicas e privadas

29.06.2022
Deputada federal não denunciou fraude nas Eleições Gerais de 2018

Fala da parlamentar questionava prisão de político e não segurança das urnas eletrônicas

10.06.2022
< Anterior
1
2
3
4
5
(atual)
6
7
8
9
Próximo >
"""

FRAUDE_PAGE_50 = """
Resultado da busca

Filtros: fraude

Foram encontrados 85 resultados.

Ação no STF não discutia inconstitucionalidade do uso de urnas eletrônicas

Peritos da PF também não disseram que os equipamentos eram fraudáveis no julgamento da ADI 5889

03.06.2022
Ex-diretor da Datafolha não gravou áudio que narra suposto plano para fraudar urnas

Gravação que viralizou nas redes é, na verdade, uma sátira feita por um canal de humor no YouTube

03.06.2022
É falso que 'vídeo vazado' de campanha de candidato à Presidência comprove fraude nas urnas em 2002

Fake reproduz trecho de documentário que mostra preparação para um debate; urnas eletrônicas sequer são citadas na gravação original

30.05.2022
É falsa a afirmação de que o aplicativo e-Título é espião

Para que o eleitor possa acessar os vários serviços oferecidos, o e-Título solicita autorizações de acesso, em cumprimento ao que exige a LGPD

12.04.2022
Carregamento de cartão de memória usado em urna eletrônica não favorece ação de hackers

Boato insinuava que dispositivo estaria vulnerável a ataques e poderia ser utilizado para fraudar eleições

30.03.2022
Empresa norte-americana não foi multada por fraudar urnas eletrônicas

Penalidades aplicadas à Diebold resultaram de acordos judiciais realizados nos Estados Unidos

25.02.2022
Eleições 2014: É boato que técnicos do Tribunal tenham se trancado em sala até o término da totalização dos votos

Em razão dos diferentes fusos, TSE seguiu norma que impede divulgação do resultado das eleições presidenciais antes do fim da votação no Acre

09.08.2021
Postagem recicla vídeo de cantor sertanejo com acusação infundada contra urna eletrônica

Gravação antiga afirma que 80% das urnas brasileiras são fraudadas. Saiba por que a informação é falsa

20.09.2021
É enganoso vídeo com compilado de alegações sobre fraude no sistema eleitoral

Gravação trazia edições e fake news antigas já desmentidas por agências e pela Justiça Eleitoral

24.08.2021
Emissora de TV não fez reportagem admitindo possibilidade de fraude nas urnas

Vídeo compartilhado pelo WhatsApp omitiu trechos da matéria, exibida em 2008, para lançar suspeitas sobre a credibilidade das eleições brasileiras

23.08.2021
< Anterior
1
...
3
4
5
6
(atual)
7
8
9
Próximo >
"""

FRAUDE_PAGE_60 = """
Resultado da busca

Filtros: fraude

Foram encontrados 85 resultados.

Post usa informações falsas ao afirmar que houve fraude nas eleições de 2014 e 2018

13.08.2021
Denúncia sobre boletim de urna no lixo não prova que houve fraude nas Eleições 2018

13.08.2021
Foro de SP não controla as eleições do Brasil

13.08.2021
Código-fonte das urnas não sofreu adulteração; nenhuma fraude foi provada

13.08.2021
Supostas provas de fraude nas eleições são boatos antigos já desmentidos pelas agências

Presidente Jair Bolsonaro trouxe em sua transmissão ao vivo desta quinta-feira (29) alegações antigas que circularam nas redes sociais e que já foram desmentidas

30.07.2021
Eleição de 2018 não foi fraudada; TSE não anulou 7,2 milhões de votos

Postagem indica que o montante de votos que teriam sido anulados seria suficiente para eleger o presidente Jair Bolsonaro na primeira etapa da disputa

28.07.2021
Urnas eletrônicas não foram fraudadas nas Eleições 2008 em Caxias (MA)

Perícia feita pela Polícia Federal descartou violação física e adulteração dos programas instalados no aparelho

28.07.2021
É falsa planilha que mostraria supostas inversões entre presidenciáveis no 2º turno das Eleições 2014

Documento oficial do TSE mostra apuração minuto a minuto. Houve uma única mudança de colocação entre os candidatos

28.07.2021
Nunca houve fraude comprovada nas eleições com urna eletrônica no Brasil

Desde 1996, ano de implementação do voto eletrônico no Brasil, não foram registradas ou comprovadas fraudes eleitorais envolvendo as urnas eletrônicas

28.07.2021
Auditoria do PSDB não encontrou fraude nas eleições de 2014

Ao contrário do que afirma a notícia falsa, partido descartou hipótese de adulteração do resultado do pleito

28.07.2021
< Anterior
1
...
4
5
6
7
(atual)
8
9
Próximo >
"""

FRAUDE_PAGE_70 = """
Resultado da busca

Filtros: fraude

Foram encontrados 85 resultados.

General Etchegoyen não evitou "fraude total" nas Eleições 2018; pleito ocorreu sem irregularidades

Boato que ganhou força nas redes em julho de 2021 foi desmentido pelo próprio ex-ministro

27.07.2021
Vídeo não prova fraude nas Eleições 2014: alegações foram desmentidas pelo TSE e pelo PSDB

Em gravação que voltou a circular em julho de 2021, ex-candidata faz acusações inconsistentes sobre voto eletrônico

26.07.2021
É falso que ex-delegado se refugiou na Suíça por ter descoberto fraude nas urnas

Vídeo que circula nas redes sociais faz acusações sobre o processo eleitoral de 2014 sem qualquer prova. Denúncia foi arquivada

26.07.2021
É mentira que Lei de Benford provou fraude nas eleições brasileiras

Modelo matemático usado para verificar indícios de fraude vem sendo mal aplicado em estudos eleitorais

21.08.2020
Vídeo mostra ações da Justiça Eleitoral para deixar as urnas mais seguras

Confira o vídeo sobre as providências que a Justiça Eleitoral tem tomado para tornar as urnas eletrônicas ainda mais confiáveis

03.11.2020
Mesários não podem transferir votos abrindo sistema de urna eletrônica

Aparelho possui registro de todas as operações executadas no aparelho, inviabilizando qualquer tentativa de fraude

14.11.2020
Percentual estável dos candidatos à prefeitura de SP não comprova fraude na votação

TSE esclarece que, após análise dos dados da votação, é possível constatar estabilidade no resultado desde o fechamento das urnas até a conclusão da totalização

16.11.2020
Vídeo não prova que sistema da urna pode ser fraudado

TSE divulgou nota que reforça segurança dos equipamentos

18.11.2020
Checagens descartam alegações de fraude nas eleições de Macaé (RJ)

Demora em mostrar a foto de candidato ocorre em algumas urnas mais antigas, como em qualquer computador com processadores mais lentos

19.11.2020
Eleições pelo país não foram anuladas por fraude nas urnas ou na apuração

TSE esclarece que são falsas mensagens que circulam em redes sociais sobre anulação das eleições

20.11.2020
< Anterior
1
...
5
6
7
8
(atual)
9
Próximo >
"""

FRAUDE_PAGE_80 = """
Resultado da busca

Filtros: fraude

Foram encontrados 85 resultados.

Diferença entre resultados de pesquisa eleitoral e de eleição não implica fraude

Tuíte enganoso de político apontou divergência como indício de manipulação

23.11.2020
Fato: zona eleitoral no conjunto de favelas da Maré (RJ) foi transferida

É verdadeira a informação que circula nas redes sociais sobre a mudança de uma zona eleitoral na localidade, no Rio de Janeiro

26.11.2020
Suposto "sumiço" de seções eleitorais em Niterói (RJ) não comprova fraude

Homem mostra site do TSE e aponta que não constam as seções 13 e 365, mas TRE explica que elas foram agregadas a outras

29.11.2020
Vídeo não mostra "urna adulterada" dentro de caminhonete particular em Fortaleza (CE)

Material que circula em redes sociais diz que urnas filmadas na caçamba de uma picape estariam sendo levadas por cabos eleitorais de candidato do PDT à prefeitura

29.11.2020
Eleições 2018: empresa venezuelana não é responsável pelas urnas eletrônicas

Não há nenhuma comprovação de fraude nos pleitos realizados após a adoção do equipamento pela Justiça Eleitoral

22.10.2018
< Anterior
1
...
6
7
8
9
(atual)
"""

# -------------------------------------------------------------- resultado --
RESULTADO_PAGE_0 = """
Resultado da busca

Filtros: resultado

Foram encontrados 12 resultados.

Eleições 2022: é mentira que partido político tenha encontrado irregularidades em 60% das urnas

Vídeo antigo com informação errada sobre identificação dos equipamentos voltou a circular nas redes sociais.

20.03.2024
Ex-ministro do GSI general Etchegoyen não disse que houve manipulação no resultado das Eleições 2022

Legenda que acompanha vídeo com entrevista do militar inventa números para sugerir fraude eleitoral

11.07.2023
Emissora de televisão não detém código-fonte das urnas eletrônicas

Também não é verdade que veículo de comunicação constatou vitória de candidato derrotado

26.04.2023
Hackers não revelaram vitória de candidato derrotado ao quebrar código-fonte das urnas eletrônicas

Não houve acesso indevido às linhas de programação, que estiveram abertas durante um ano para inspeção

19.12.2022
É boato que hackers russos avisaram o Exército brasileiro sobre fraude no primeiro turno

Mensagem de áudio engana ao dizer que militares agiram após serem avisados de fraude pelos russos

15.10.2022
TRE-PB informa que é falsa a informação sobre suposta irregularidade no envio de mídias de resultados em João Pessoa

Boletim de Urna da seção 442 reflete o resultado totalizado e divulgado pelo TSE

08.10.2022
É falso que haja divergência de dados em boletins de urna de São Joaquim da Barra (SP)

TRE-SP desmentiu vídeo com declaração enganosa feita pelo prefeito da cidade

07.10.2022
TRE-TO esclarece: número maior de votos para presidente em seções do estado se deve ao voto em trânsito

É mentirosa a alegação de que houve fraude no resultado da seção 5 da 29ª Zona Eleitoral de Palmas (TO)

06.10.2022
Vídeo faz alegação falsa sobre redução de votos de candidata em Palmas (TO)

A contagem dos votos pode ser feita por qualquer eleitor, a partir dos votos apurados no momento da impressão do Boletim de Urna, logo após o encerramento da votação

18.11.2020
TSE não vendeu eleição de São Paulo para candidato da esquerda

Tribunal esclarece que, após análise dos dados da votação, é possível constatar estabilidade no resultado desde o fechamento das urnas até a conclusão da totalização

18.11.2020
< Anterior
1
(atual)
2
Próximo >
"""

RESULTADO_PAGE_10 = """
Resultado da busca

Filtros: resultado

Foram encontrados 12 resultados.

Contagem dos votos não é realizada de forma secreta por servidores do TSE

Apuração dos resultados é feita automaticamente pela urna eletrônica, logo após o encerramento da votação

18.11.2020
Vídeo que mostra divergência entre Boletim de Urna e sistema do TSE é enganoso

No caso que ocorreu no Acre, em novembro de 2020, homem compara informações de seções eleitorais diferentes

20.11.2020
< Anterior
1
2
(atual)
"""

# ---------------------------------------------------------- crime eleitoral -
CRIME_ELEITORAL_PAGE_0 = """
Resultado da busca

Filtros: crime eleitoral

Foram encontrados 4 resultados.

Homem precisou remover pintura de calçada por violação da lei eleitoral, não por "censura"

Checagem desmente notícia falsa que distorce acontecimento em Guarapari (ES)

30.09.2022
É verdade que fazer propaganda eleitoral no dia da eleição é crime

Agência Lupa confirmou veracidade das declarações dadas por juiz eleitoral em vídeo compartilhado no WhatsApp perto do 1º turno das Eleições 2020

26.11.2020
Presidente de seção eleitoral do RJ não impediu fiscais de assinarem a zerésima

Vídeo com informações falsas circula nas redes alegando que equipe do candidato a prefeito do Rio Marcelo Crivella foi proibida de assinar o documento

29.11.2020
Eleições 2018: notícia sobre apreensão de urnas pela PM do Amazonas é falsa

Rumor distorceu fato que ocorreu na estrada de Autazes, município que fica a 113 quilômetros de Manaus

23.10.2018
"""

# ------------------------------------------------------------- boletim urna -
BOLETIM_URNA_PAGE_0 = """
Resultado da busca

Filtros: boletim de urna

Foram encontrados 28 resultados.

Eleições 2022: pastor mente ao afirmar que análise de votos nulos e em branco da Bahia indicaria que houve fraude eleitoral

Em audiência pública realizada no Senado, homem propagou dados equivocados e disseminou mentiras sobre urnas eletrônicas

22.03.2024
Boato sobre “compra” de vitória de candidato à Presidência é antigo e circula desde 1998

Eleições Gerais de 2022 transcorreram normalmente, sem que nenhuma irregularidade fosse comprovada

16.10.2023
Todas as urnas eletrônicas usadas para colher votos do eleitorado estavam devidamente identificadas

Comentário de apresentador de SC repercute informações equivocadas sobre as Eleições Gerais de 2022

17.02.2023
Tweet fabrica dados para sugerir que votos registrados em papel divergiram de resultado de urna instalada em Israel

Na seção eleitoral 0682, que votou de forma manual e eletrônica, Bolsonaro obteve mais votos que adversário

15.12.2022
É falso que existam urnas com 1,5 mil eleitores, ao contrário do que alega deputado

Agências de checagem desmentiram informações falsas propagadas durante live transmitida pelo TikTok

22.11.2022
Predominância de votos para um dos candidatos não é indício de fraude eleitoral

Situação é comum e já ocorreu em eleições anteriores. Confira a explicação e o histórico ao longo das últimas eleições

09.11.2022
Similaridade de votos em seções eleitorais de Sorocaba (SP) não é indicativo de fraude

Boletins de urna do município estão corretos e refletem fielmente a vontade do eleitorado

04.11.2022
É falso que todas as urnas de local de votação no RS tiveram 129 votos para mesmo candidato à Presidência

TRE-RS desmentiu mensagem falsa atribuída a suposta mesária que circulava no Twitter e no WhatsApp

10.10.2022
TRE-PB informa que é falsa a informação sobre suposta irregularidade no envio de mídias de resultados em João Pessoa

Boletim de Urna da seção 442 reflete o resultado totalizado e divulgado pelo TSE

08.10.2022
Exército não interferiu na apuração dos votos no primeiro turno das Eleições Gerais de 2022

Notícia falsa afirmava que a instituição teria sido alertada por hackers russos sobre suposta fraude eleitoral

07.10.2022
< Anterior
1
(atual)
2
3
Próximo >
"""

BOLETIM_URNA_PAGE_10 = """
Resultado da busca

Filtros: boletim de urna

Foram encontrados 28 resultados.

É falso que haja divergência de dados em boletins de urna de São Joaquim da Barra (SP)

TRE-SP desmentiu vídeo com declaração enganosa feita pelo prefeito da cidade

07.10.2022
Vídeos que levantam suspeitas sobre divergência entre eleitorado da seção e número de votos para presidente em MG são enganosos

A diferença representa a quantidade de pessoas de outros estados e da Zona Eleitoral do Exterior que se habilitaram para votar em trânsito naquela seção

06.10.2022
TRE-MG informa que é falsa informação sobre seção eleitoral que não foi computada no resultado da eleição

Seção mencionada em vídeo foi agregada e teve os votos registrados juntos com os de outra

06.10.2022
Comprovante de votação não indica em quem o eleitor votou e não pode ser utilizado como forma de auditoria

UOL Confere desmonta boato que circulou no 1º turno das Eleições Gerais de 2022

05.10.2022
Número de votos não superou quantidade de habitantes da cidade de Barreiras (BA)

Agências de checagem desconstruíram notícia falsa em circulação nas redes

04.10.2022
É falso o vídeo que mostra divergência no resultado de Zonas Eleitorais de Maceió (AL)

TRE de Alagoas esclareceu boato que utilizava dados não oficiais para disseminar mentiras sobre totalização dos votos no Estado

04.10.2022
É falso que boletins de urna em posse de eleitores comprovam que votos não foram computados em Curitiba (PR)

Em vídeo publicado no Kwai e que circula no WhatsApp, mulher sugere que houve fraude em seção eleitoral da cidade

03.10.2022
Urna eletrônica não realiza contagem secreta dos votos nem registra "o que quer" durante votação

Agência Lupa desmontou alegações de vídeo que circula no aplicativo WhatsApp

21.09.2022
É falsa a alegação de que TSE usa sistema de autenticação do título para fazer campanha eleitoral

Código é gerado aleatoriamente, não tem qualquer uso político e também não é capaz de interferir no resultado da eleição

17.08.2022
Denúncia sobre boletim de urna no lixo não prova que houve fraude nas Eleições 2018

13.08.2021
< Anterior
1
2
(atual)
3
Próximo >
"""

BOLETIM_URNA_PAGE_20 = """
Resultado da busca

Filtros: boletim de urna

Foram encontrados 28 resultados.

Vídeo de documentos eleitorais descartados em Goiânia (GO) é de 2014 e não mostra insegurança de urna eletrônica

Circula pelas redes sociais um vídeo de um homem que mostra uma série de documentos eleitorais que teriam sido encontrados no lixo

28.07.2021
Mídia de urna eletrônica foi encontrada dentro de vaso sanitário em Juiz de Fora (MG)

Rádio mineira publicou notícia afirmando que agentes da Polícia Federal (PF) estiveram em escola de Juiz de Fora (MG) para investigar um “chip” de uma eletrônica que teria sido encontrado num vaso sanitário

17.11.2020
Vídeo que mostra divergência entre Boletim de Urna e sistema do TSE é enganoso

No caso que ocorreu no Acre, em novembro de 2020, homem compara informações de seções eleitorais diferentes

20.11.2020
Eleições 2018: é falso que boletim de urna tenham registrado 9.909 votos para candidato à Presidência em Nagoia, no Japão

Montagem foi compartilhada para lançar dúvida sobre lisura do pleito ao insinuar que seção tinha mais votos do que eleitores

11.10.2018
Boletim de urna com 9.909 votos em candidato à Presidência nas Eleições Gerais de 2018 é montagem

Documento foi adulterado para dar a entender que número de votos foi superior à quantidade de eleitores

11.10.2018
Eleições 2018: denúncia de fraude baseada em suposto extravio de Boletins de Urna em colégio eleitoral de SP é infundada

Mesmo que os documentos tivessem sido subtraídos, problema não seria capaz de influenciar resultado do pleito

17.10.2018
Post viral recicla boato de 2018 sobre Projeto Você Fiscal, inativo desde 2016

Notícia falsa já foi esclarecida pela Justiça Eleitoral e por agências de checagem

22.10.2018
Eleições 2018: confira o resultado da auditoria nas urnas de SP

Especialista espalhou mentiras ao afirmar que auditoria nas urnas eletrônicas realizada pelo TRE-SP não obteve o resultado esperado

26.10.2018
< Anterior
1
2
3
(atual)
"""

# ------------------------------------------------------------ totalizacao --
TOTALIZACAO_PAGE_0 = """
Resultado da busca

Filtros: totalização

Foram encontrados 17 resultados.

Ex-ministro do GSI general Etchegoyen não disse que houve manipulação no resultado das Eleições 2022

Legenda que acompanha vídeo com entrevista do militar inventa números para sugerir fraude eleitoral

11.07.2023
Canal argentino dissemina novas mentiras sobre urnas, votação fantasma e transferência de votos em branco para candidato à Presidência

Alegações já foram desmentidas pelo TSE e por agências especializadas em checagem de notícias falsas que circulam na internet

20.12.2022
É boato que hackers russos avisaram o Exército brasileiro sobre fraude no primeiro turno

Mensagem de áudio engana ao dizer que militares agiram após serem avisados de fraude pelos russos

15.10.2022
TRE-PB informa que é falsa a informação sobre suposta irregularidade no envio de mídias de resultados em João Pessoa

Boletim de Urna da seção 442 reflete o resultado totalizado e divulgado pelo TSE

08.10.2022
Exército não interferiu na apuração dos votos no primeiro turno das Eleições Gerais de 2022

Notícia falsa afirmava que a instituição teria sido alertada por hackers russos sobre suposta fraude eleitoral

07.10.2022
Urna eletrônica não realiza contagem secreta dos votos nem registra "o que quer" durante votação

Agência Lupa desmontou alegações de vídeo que circula no aplicativo WhatsApp

21.09.2022
Postagens tiram comentário de jornalista de contexto para atacar sistema eleitoral brasileiro

13.08.2021
Votos são contados automaticamente pelo TSE, que não é composto apenas por ministros do STF

13.08.2021
Postagem engana ao citar invasão à Nasa para questionar segurança das urnas

TSE vem reiterando que os computadores e sistemas utilizados na captação, transmissão e totalização dos votos não são conectados à internet e, por isso, não podem ser invadidos por hackers

28.07.2021
É falsa planilha que mostraria supostas inversões entre presidenciáveis no 2º turno das Eleições 2014

Documento oficial do TSE mostra apuração minuto a minuto. Houve uma única mudança de colocação entre os candidatos

28.07.2021
< Anterior
1
(atual)
2
Próximo >
"""

TOTALIZACAO_PAGE_10 = """
Resultado da busca

Filtros: totalização

Foram encontrados 17 resultados.

Nunca houve fraude comprovada nas eleições com urna eletrônica no Brasil

Desde 1996, ano de implementação do voto eletrônico no Brasil, não foram registradas ou comprovadas fraudes eleitorais envolvendo as urnas eletrônicas

28.07.2021
Mídia de urna eletrônica foi encontrada dentro de vaso sanitário em Juiz de Fora (MG)

Rádio mineira publicou notícia afirmando que agentes da Polícia Federal (PF) estiveram em escola de Juiz de Fora (MG) para investigar um “chip” de uma eletrônica que teria sido encontrado num vaso sanitário

17.11.2020
Contagem dos votos não é realizada de forma secreta por servidores do TSE

Apuração dos resultados é feita automaticamente pela urna eletrônica, logo após o encerramento da votação

18.11.2020
É falso que urna eletrônica não permite recontagem de votos

Vídeo muito compartilhado na internet dava informações erradas sobre sistema eletrônico de votação

20.11.2020
É falso que todas as zonas eleitorais de São Paulo tiveram o mesmo resultado em 2020

Peças de desinformação distorceram interpretação de resultado das eleições para sugerir fraude eleitoral

23.11.2020
Diferença entre número de habitantes e total de votos não significa que houve fraude eleitoral

Divergência pode ocorrer porque pessoas podem se inscrever para votar fora do seu lugar de residência

28.11.2020
É falso que 61% dos eleitores da cidade de São Paulo votaram em branco, nulo ou não votaram no 2º turno em 2020

Dados contidos em tabela compartilhada nas redes não equivalem ao resultado registrado pelo TSE

01.12.2020
< Anterior
1
2
(atual)
"""

# ------------------------------------------------------------ codigo fonte -
CODIGO_FONTE_PAGE_0 = """
Resultado da busca

Filtros: código-fonte

Foram encontrados 23 resultados.

Código-fonte da urna eletrônica não foi quebrado e não revela voto do eleitorado

Desinformação antiga, que tratava do log do equipamento, voltou a circular em 202

26.08.2024
Eleições 2018: pleito presidencial não foi definido no primeiro turno; nenhuma fraude foi comprovada

Declarações falsas de candidato voltaram a circular na web. Confira a explicação:

20.05.2024
Vídeo engana ao questionar votos após às 17h, proibição de inspeção do código-fonte pelas Forças Armadas e existência de sala secreta do TSE

Nenhuma das alegações é verdadeira. Confira a explicação:

03.04.2024
Abertura do código-fonte para inspeção é procedimento de auditoria padrão, que ocorre um ano antes das eleições ordinárias

Ao contrário do que afirmou mensagem do Telegram, a medida não foi motivada por pleito para Conselhos Tutelares

16.10.2023
Deputado federal não mandou TSE entregar código-fonte do sistema eleitoral

Além de antiga, a fala também não menciona as linhas de programação, que ficaram abertas durante um ano para inspeção

03.07.2023
Eleições 2022: Estados Unidos não provaram vitória de candidato derrotado nas urnas

Agência Lupa recebeu nota da Embaixada dos EUA, que reafirmou confiança nas instituições brasileiras

28.06.2023
Deputado federal mente ao afirmar que eleições são geridas por empresas estrangeiras

Em fala que viralizou nas redes, parlamentar disseminou boatos já esclarecidos pelo TSE

23.06.2023
Eleição não foi anulada por falha na identificação biométrica do eleitorado

Eleitores são identificados em duas etapas: conferência do documento com foto e biometria cadastrada na JE

03.05.2023
Emissora de televisão não detém código-fonte das urnas eletrônicas

Também não é verdade que veículo de comunicação constatou vitória de candidato derrotado

26.04.2023
Autor de vídeo viral engana ao afirmar que votos podem ser transferidos entre candidaturas

Todos os comandos do sistema eletrônico de votação estão contidos no código-fonte, que ficou aberto durante um ano para inspeção

11.01.2023
< Anterior
1
(atual)
2
3
Próximo >
"""

CODIGO_FONTE_PAGE_10 = """
Resultado da busca

Filtros: código-fonte

Foram encontrados 23 resultados.

Homem mente ao afirmar que urna foi programada para favorecer candidata à Presidência nas Eleições 2014

Autor da gravação também não reproduziu o sistema utilizado no equipamento

28.12.2022
Canal argentino dissemina novas mentiras sobre urnas, votação fantasma e transferência de votos em branco para candidato à Presidência

Alegações já foram desmentidas pelo TSE e por agências especializadas em checagem de notícias falsas que circulam na internet

20.12.2022
Hackers não revelaram vitória de candidato derrotado ao quebrar código-fonte das urnas eletrônicas

Não houve acesso indevido às linhas de programação, que estiveram abertas durante um ano para inspeção

19.12.2022
Código-fonte já foi inspecionado pelas Forças Armadas, ao contrário do que diz mensagem do WhatsApp

Afirmação de que houve fraude nas eleições presidenciais também não é verdadeira

01.12.2022
Mandado de injunção não está relacionado às eleições, nem às urnas eletrônicas

Vídeo repassou informações erradas sobre suposto pedido de entrega do código-fonte

25.11.2022
Candidato perdeu eleições porque recebeu menos votos e não devido à suposta quebra de código-fonte

Após inspeção de entidades, linhas de programação foram assinadas digitalmente e lacradas; processo impede qualquer tentativa de manipulação

24.11.2022
Exército não pediu código-fonte de urnas eletrônicas por ter descoberto fraude no “voto de rebanho”

Mensagem e áudio enganosos ganharam projeção nas redes sociais logo após o 1º turno das Eleições 2022

06.10.2022
Forças Armadas não tiveram "acesso dificultado" a código-fonte das urnas

Ao contrário do que afirma autor de vídeo, TSE ofereceu todo o suporte para realização da inspeção. Códigos estão abertos desde outubro de 2021

08.08.2022
Código-fonte das urnas não sofreu adulteração; nenhuma fraude foi provada

13.08.2021
Fake news de 2018 sobre urnas voltaram às redes, mas já foram desmentidas

Agências de checagem desmontaram boatos sobre suposta consultoria do ITA e do IME, códigos-fonte entregues a estrangeiros e supostas irregularidades em urnas do DF

19.10.2020
< Anterior
1
2
(atual)
3
Próximo >
"""

CODIGO_FONTE_PAGE_20 = """
Resultado da busca

Filtros: código-fonte

Foram encontrados 23 resultados.

Checagem desmente fake sobre software da urna entregue a ‘três venezuelanos e um português’

Empresa Smartmatic foi reprovada na licitação para a produção de novas urnas eletrônicas e não teve acesso a quaisquer código-fonte ou chaves criptográficas

21.10.2020
Eleições 2018: códigos de urnas não foram entregues a venezuelanos como diz boato na internet

Notícia falsa compartilhada nas redes sociais afirma que uma empresa venezuelana teria conseguido acesso a arquivos da urna brasileira

22.10.2018
Eleições 2018: problema técnico em urna foi usado para sugerir fraude eleitoral em SP

TRE-SP realizou auditoria pública e constatou que houve falha no teclado do equipamento

22.10.2018
< Anterior
1
2
3
(atual)
"""

# ---------------------------------------------------------------biometria --
BIOMETRIA_PAGE_0 = """
Resultado da busca

Filtros: biometria

Foram encontrados 11 resultados.

Fala do ministro Gilmar Mendes foi editada para sugerir que houve fraude nas Eleições 2022

Trecho descontextualizado citava a figura do mesário pianista, que poderia votar por eleitor ausente

21.07.2023
Deputado federal mente ao afirmar que eleições são geridas por empresas estrangeiras

Em fala que viralizou nas redes, parlamentar disseminou boatos já esclarecidos pelo TSE

23.06.2023
Eleição não foi anulada por falha na identificação biométrica do eleitorado

Eleitores são identificados em duas etapas: conferência do documento com foto e biometria cadastrada na JE

03.05.2023
Mesária manipulou vídeo para dar a entender que seria possível votar por eleitor faltoso

Ela já havia liberado a votação por ano de nascimento no terminal antes de começar a gravar

03.11.2022
Eleitora de Bauru (SP) distorceu informações sobre biometria e confundiu número de candidato para cargo de deputado

Cadastro biométrico não é possível no momento da votação, nem transferência de eleitores entre seções eleitorais de acordo com a faixa etária

21.10.2022
Filas em seções eleitorais não devem ser atribuídas à biometria

Espera ocorreu dentro da normalidade. Justiça Eleitoral garantiu o registro do voto de todos que chegaram até as 17h

02.10.2022
Eleições 2022: eleitor sem biometria não será impedido de votar

Cadastro biométrico continua suspenso em todo o país para prevenir disseminação da Covid-19

22.02.2022
É falso que beneficiário do INSS tenha de comparecer a cartório eleitoral para fazer validação facial

Em outubro de 2021, atendimento presencial estava suspenso para prevenir contágio pelo novo coronavírus

21.10.2021
Não é verdade que exclusão da biometria foi para evitar que eleitores "usem o dedo" nas Eleições 2020

O protocolo sanitário elaborado pelo TSE explica que a exclusão da biometria ocorreu para evitar aglomeração e formação de filas, além de reduzir as superfícies de contato com objetos

07.10.2020
Eleições 2018: Eleitor não pode votar sem biometria obrigatória

Texto compartilhado pelo WhatsApp causou confusão ao disseminar informações erradas para o eleitorado

22.10.2018
< Anterior
1
(atual)
2
Próximo >
"""

BIOMETRIA_PAGE_10 = """
Resultado da busca

Filtros: biometria

Foram encontrados 11 resultados.

É mentira que mesários votam na urna eletrônica no lugar de eleitores

27.04.2026
< Anterior
1
2
(atual)
"""

TAG_PAGES = {
    "fraude": [FRAUDE_PAGE_0, FRAUDE_PAGE_10, FRAUDE_PAGE_20, FRAUDE_PAGE_30,
               FRAUDE_PAGE_40, FRAUDE_PAGE_50, FRAUDE_PAGE_60, FRAUDE_PAGE_70,
               FRAUDE_PAGE_80],
    "resultado": [RESULTADO_PAGE_0, RESULTADO_PAGE_10],
    "crime eleitoral": [CRIME_ELEITORAL_PAGE_0],
    "boletim de urna": [BOLETIM_URNA_PAGE_0, BOLETIM_URNA_PAGE_10, BOLETIM_URNA_PAGE_20],
    "totalização": [TOTALIZACAO_PAGE_0, TOTALIZACAO_PAGE_10],
    "código-fonte": [CODIGO_FONTE_PAGE_0, CODIGO_FONTE_PAGE_10, CODIGO_FONTE_PAGE_20],
    "biometria": [BIOMETRIA_PAGE_0, BIOMETRIA_PAGE_10],
}

EXPECTED_COUNTS = {
    "fraude": 85, "resultado": 12, "crime eleitoral": 4, "boletim de urna": 28,
    "totalização": 17, "código-fonte": 23, "biometria": 11,
}

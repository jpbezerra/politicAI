# -*- coding: utf-8 -*-
"""
Texto bruto real, coletado via navegador (Claude in Chrome) em 23/08/2026,
do arquivo de Checagens do Aos Fatos — aosfatos.org/noticias/?formato=checagem
— um dos 10 parceiros oficiais da Coalizão Fato ou Boato do TSE.

Três recortes reais foram coletados (por tag editorial, atribuída pela própria
redação do Aos Fatos — não é uma inferência nossa):

1) tag=inteligencia-artificial  -> população COMPLETA: 11 páginas, 122 itens
   (todas as páginas existentes nesta tag foram coletadas)
2) tag=eleicoes-2026            -> população COMPLETA: 1 página, 12 itens
3) tag=eleicoes-2022            -> população COMPLETA: 35 de 35 páginas, 419 itens
   (coletada em duas etapas, ambas em 23/08/2026: 7 páginas inicialmente —
   1,2,4,5,6,7,8 — e as 28 páginas restantes depois, a pedido do usuário, para
   substituir a amostra original por uma coleta completa. Três páginas — 13,
   27 e 31 — retornaram na primeira tentativa conteúdo idêntico ao da página
   anterior, um glitch de cache do site já visto antes; cada uma foi recarregada
   navegando antes para a página 1 e então para a página-alvo, e o conteúdo
   único foi confirmado antes de aceito. Nenhuma página foi inventada ou
   preenchida por extrapolação.)

Formato de cada bloco (linhas nao vazias, em ordem):
    [veredito]?      -> um de: falso | verdadeiro | não é bem assim | discurso oficial
    [tema]?          -> tag temática livre (ex.: "inteligência artificial", "boataria política")
    checagem         -> marcador fixo presente em todo item
    <título>
(zero, uma ou duas linhas de rótulo podem preceder "checagem"; ver parse_dataset_b.py)
"""

IA_PAGE_1 = """
falso
inteligência artificial
checagem
Vídeos em que Tancredo e Ulysses criticam Bolsonaro são obra de IA
falso
boataria política
checagem
É falso que Lula disse que teve perna amputada em 2023
falso
exploração de tragédia
checagem
Vídeo de IA circula em posts como se mostrasse desabamento na Colômbia
falso
inteligência artificial
checagem
Vídeo feito com IA simula ataque dos EUA a base militar no Irã
falso
inteligência artificial
checagem
Vídeos de IA são usados para inflar repercussão do funeral de Khamenei
falso
exploração de tragédia
checagem
Vídeo feito por IA é atribuído em posts ao terremoto na Venezuela
falso
boataria política
checagem
Trump não disse que Lula é um 'escândalo ambulante'
falso
inteligência artificial
checagem
Fotos geradas por IA do encontro de Flávio e Trump circulam nas redes como reais
falso
boataria política
checagem
É falso que Trump criou ação militar contra corrupção no Brasil
falso
inteligência artificial
checagem
É falso vídeo que mostra combatente brasileiro capturado na Ucrânia
falso
boataria política
checagem
Vídeo em que Flávio Bolsonaro promete 'auxílio sacolão de osso' é de IA
falso
boataria política
checagem
Vídeo de IA inventa que Vorcaro delatou mandante de atentado a Bolsonaro
"""

IA_PAGE_2 = """
falso
inteligência artificial
checagem
Foto que mostra nave da Artemis II danificada é gerada por IA
falso
inteligência artificial
checagem
É falsa foto em que equipe da Artemis II simula missão em estúdio
falso
inteligência artificial
checagem
Vídeo que mostra funeral coletivo de soldados israelenses é gerado por IA
falso
inteligência artificial
checagem
Vídeo que mostraria ataque de Israel que matou oficial iraniano é feito por IA
falso
boataria política
checagem
Vídeo de IA engana ao dizer que Vorcaro delatou Moraes, Toffoli e Lula
falso
exploração de tragédia
checagem
Não é verdade que foto mostra míssil iraniano com mensagem sobre vítimas de Epstein
falso
boataria política
checagem
É falso que Vorcaro confessou ter feito pagamentos a Lula e a ministros do STF
falso
exploração de tragédia
checagem
Relatos gerados por IA exploram tragédia das chuvas em MG
falso
exploração de tragédia
checagem
Vídeos que mostram consequências das chuvas em MG são gerados por IA
falso
exploração de tragédia
checagem
São gerados por IA vídeos que mostram enxurrada destruindo casas em MG
falso
boataria política
checagem
É falso que música do filme de Bolsonaro tenha sido lançada e seja sucesso nos EUA
falso
inteligência artificial
checagem
Vídeo em que Lula se pronuncia sobre morte do cão Orelha é gerado por IA
"""

IA_PAGE_3 = """
falso
inteligência artificial
checagem
Foto que mostra prefeito de Nova York ainda criança ao lado de Epstein é gerada por IA
falso
inteligência artificial
checagem
É gerado por IA vídeo que mostra protesto de petista contra 'Caminhada pela Liberdade'
falso
inteligência artificial
checagem
Fotos que mostram Nikolas Ferreira caminhando junto de multidão são geradas por IA
falso
inteligência artificial
checagem
É feito com IA vídeo em que Roberto Carlos envia mensagem de apoio a Bolsonaro
falso
inteligência artificial
checagem
Vídeo em que professores protestam por reajuste no piso é gerado por IA
falso
inteligência artificial
checagem
É falso que Maduro foi condenado à morte nos EUA
falso
boataria política
checagem
Posts disseminam como reais vídeos de IA em que venezuelanos celebram prisão de Maduro
falso
boataria política
checagem
É falso que Lula visitou Bolsonaro no hospital após cirurgia do ex-presidente
falso
boataria política
checagem
Vídeo que mostra manifestação de caminhoneiros em Brasília foi gerado por IA
falso
boataria política
checagem
Foi gerado por IA vídeo que mostra policiais tomando sede do Comando Vermelho
falso
inteligência artificial
checagem
Vídeo que mostra 'fazenda de visualizações' foi gerado por IA
falso
boataria política
checagem
Vídeo que mostra apoiador de Bolsonaro implorando por ajuda de PM foi gerado por IA
"""

IA_PAGE_4 = """
falso
fraudes digitais
checagem
Golpistas manipulam vídeos da família Bolsonaro com IA para promover campanha de arrecadação falsa
falso
inteligência artificial
checagem
Não é verdade que Trump mandou projetar bandeira brasileira na Times Square em apoio a Bolsonaro
falso
boataria política
checagem
Foi gerado por IA vídeo em que pastora diz que tudo o que profetizou para Lula aconteceu com Bolsonaro
falso
boataria política
checagem
Vídeo que mostra tornozeleira de Bolsonaro violada não foi gerado por IA
falso
inteligência artificial
checagem
É falso que governo federal vai pagar benefício extra de R$ 1.150 a beneficiários do INSS
falso
boataria política
checagem
PF prendeu francês por violência doméstica, não por lavar dinheiro para o Foro de São Paulo
falso
boataria política
checagem
Posts manipulam vídeo com IA para fazer crer que Fux anunciou soltura de Bolsonaro
falso
boataria política
checagem
Vídeo que mostra protesto de indígenas pedindo um navio 'igual ao da Janja' foi gerado por IA
falso
exploração de tragédia
checagem
Cena de tornado no Paraná foi gerada por IA
falso
exploração de tragédia
checagem
Foi criada por IA gravação que mostra passagem de tornado pelo Paraná
falso
exploração de tragédia
checagem
Vídeo que mostra ônibus sendo levado por tornado no Paraná foi gerado por IA
falso
inteligência artificial
checagem
Imagem que mostra Lula e Janja brindando em iate durante COP30 foi gerada por IA
"""

IA_PAGE_5 = """
falso
exploração de tragédia
checagem
Foi gerada por IA cena que mostra passagem de tornado por cidade do Paraná
falso
boataria política
checagem
É falso que governo Lula apreendeu 30 mil cabeças de gado e enviou para Cuba
falso
boataria política
checagem
É falso que governo anunciou bloqueio do Bolsa Família a partir de novembro
falso
boataria política
checagem
Governo não anunciou salário mínimo de R$ 1.820 para 2026
falso
exploração de tragédia
checagem
É falso que café com metanol está sendo distribuído no Brasil
falso
exploração de tragédia
checagem
Não é verdade que metanol foi detectado na Heineken
falso
políticas públicas
checagem
É falso que foi aprovada lei de toque de recolher para crianças e jovens
falso
inteligência artificial
checagem
Posts compartilham vídeo de IA como se fosse registro real de ato na Paulista
falso
boataria política
checagem
Trump não mandou hastear bandeira do Brasil na Casa Branca em apoio a Bolsonaro
falso
boataria política
checagem
Vídeo de protesto nos EUA pela anulação do julgamento de Bolsonaro foi gerado por IA
falso
boataria política
checagem
Vídeo em que Janja xinga eleitores de Lula teve áudio alterado por IA
falso
boataria política
checagem
É falso que exército dos EUA declarou apoio a Bolsonaro e que Trump está a caminho do Brasil
"""

IA_PAGE_6 = """
falso
boataria política
checagem
Xi Jinping não gravou vídeo em apoio a Lula e a Moraes após tarifaço de Trump
falso
boataria política
checagem
É falso que Nicolás Maduro foi assassinado por militares venezuelanos
falso
boataria política
checagem
Foto que mostra enviado especial americano desembarcando no Brasil foi gerada por IA
falso
boataria política
checagem
GloboNews não noticiou que influenciadores apagaram fotos de encontro com ministros do STF
falso
boataria política
checagem
Foto de Eduardo Bolsonaro e Paulo Figueiredo com Trump foi gerada por IA
falso
boataria política
checagem
Vídeo em que Ivete Sangalo defende Lula sobre tarifaço foi manipulado por IA
falso
boataria política
checagem
Vídeo de protesto anti-Trump e pró-Lula nos EUA foi gerado por IA
falso
boataria política
checagem
Torcida do Corinthians não entoou cântico contra Alexandre de Moraes durante jogo
falso
boataria política
checagem
Vídeo em que André Mendonça defende Bolsonaro no STF foi manipulado por IA
falso
inteligência artificial
checagem
Preta Gil não escreveu carta com pedido de perdão a Bolsonaro
falso
inteligência artificial
checagem
Vídeo em que Trump critica Moraes e o STF foi manipulado por IA
falso
boataria política
checagem
Lula não pediu retratação ao Vaticano por críticas feitas pelo papa Leão 14
"""

IA_PAGE_7 = """
falso
fraudes digitais
checagem
Vídeo em que Nikolas Ferreira pede doações para crianças em Israel é golpe
falso
inteligência artificial
checagem
Foto que mostra mísseis no céu de Israel foi gerada por IA
falso
boataria política
checagem
Vídeo em que presidente de Burkina Fasso ameaça Lula foi dublado por IA
falso
boataria política
checagem
Posts manipulam áudio de gravação para alegar que Maduro renunciou à presidência da Venezuela
falso
inteligência artificial
checagem
Vídeo manipulado por IA faz crer que Trump chamou Lula de 'desastre total'
falso
boataria política
checagem
Foto de Jair Bolsonaro e 'Careca do INSS' em moto foi gerada por IA
falso
boataria política
checagem
Foto em que papa Leão 14 'faz o L' foi gerada por IA
falso
inteligência artificial
checagem
Vídeo em que Trump chama Lula de 'palhaço corrupto' tem áudio manipulado por IA
falso
fraudes digitais
checagem
É golpe anúncio sobre o pagamento de indenização pelo Nubank
falso
boataria política
checagem
Posts usam foto gerada por IA para inventar encontro entre Lula e Lady Gaga
falso
boataria política
checagem
Golpe usa 'deepfakes' e imagens de criança doente para roubar dinheiro de doações
falso
boataria política
checagem
É golpe lista que promete indenização de até R$ 20 mil do governo federal
"""

IA_PAGE_8 = """
falso
exploração de tragédia
checagem
Gravação que mostra cratera causada por terremoto em Mianmar foi gerada por IA
falso
autoritarismo
checagem
Vídeo em que suposta juíza dos EUA critica Moraes foi gerado por IA
falso
inteligência artificial
checagem
Vídeo em que cruzeiro despeja poluente no mar foi gerado por IA
falso
inteligência artificial
checagem
Imagem do papa Francisco hospitalizado foi gerada por IA
falso
boataria política
checagem
Vídeo de Elon Musk convocando manifestação é falso e foi gerado por IA
falso
inteligência artificial
checagem
Vídeo de protesto de celebridades contra Kanye West foi gerado por IA
falso
boataria política
checagem
Foto de encontro entre Michelle Bolsonaro e Trump em aeroporto foi gerada por IA
falso
boataria política
checagem
É falsa foto de Michelle Bolsonaro ao lado de cadeira vazia em posse de Trump
falso
boataria política
checagem
É falso que Haddad disse que plano do governo Lula é 'taxar tudo'
falso
inteligência artificial
checagem
Vídeo de dragão formado por drones na China tem indícios de uso de IA
falso
inteligência artificial
checagem
Imagem de Bolsonaro visitando Lula no hospital foi gerada por IA
falso
boataria política
checagem
Imagem de Lula com cabeça enfaixada foi gerada por inteligência artificial
"""

IA_PAGE_9 = """
tecnopolítica
checagem
Comissão do Senado aprova texto para regular IA e atenua fiscalização de redes
falso
inteligência artificial
checagem
Imagem que mostra Benjamin Netanyahu hospitalizado foi gerada por IA
falso
fraudes digitais
checagem
Golpe financeiro inventa falso 'desconto de 100%' na Havan
falso
inteligência artificial
checagem
Não há registros de filmagens de Kamala Harris em festas de Diddy
falso
inteligência artificial
checagem
Vídeo em que Vini Jr. diz que 'roubaram' Bola de Ouro foi criado por IA
falso
eleições 2024
checagem
André Fernandes não comprovou que áudio foi gerado por IA e disseminado por Leitão
falso
exploração de tragédia
checagem
Vídeo feito por IA circula como se mostrasse furacão Milton
falso
eleições 2024
checagem
Vídeos usam IA para criar 'deepfakes' em que Bonner pede voto em candidatos a vereador
falso
exploração de tragédia
checagem
Foto de base israelense destruída após ataque do Hezbollah foi gerada por IA
falso
inteligência artificial
checagem
Não há registros de que Justin Bieber falou sobre festas de Diddy em música
falso
eleições 2024
checagem
Vídeo usa 'deepfake' de Bolsonaro para dar a entender apoio a Marçal
falso
inteligência artificial
checagem
Vídeo em que Patrícia Abravanel aborda venda do SBT é 'deepfake'
"""

IA_PAGE_10 = """
falso
inteligência artificial
checagem
Posts usam vídeo satírico para acusar Kamala Harris de inflar público de comício com IA
falso
inteligência artificial
checagem
Imagem de Macron beijando homem em lancha foi criada por IA
falso
boataria política
checagem
Vídeo de Kamala Harris dizendo que 'hoje é hoje' foi alterado por IA
falso
inteligência artificial
checagem
É falso que Elon Musk construirá torre com 1.200 metros de altura em Balneário Camboriú
falso
inteligência artificial
checagem
Vídeos que mostram estátuas e flores dançando não são propaganda da Olimpíada de Paris
falso
checagem
Foto falsa gerada por IA não mostra corpos boiando em Canoas
falso
checagem
Foto de idosos fantasiados de mísseis patriotas em Copacabana foi criada por IA
falso
checagem
Imagem de crianças palestinas em frente a escombros foi criada por IA
falso
checagem
É falso que CNN britânica disse que Lula é rejeitado pela maioria dos brasileiros
falso
checagem
New York Times não publicou charge racista retratando Lula como macaco após fala sobre Israel
falso
checagem
Posts compartilham paródia de robô assassino armado como se mostrasse vídeo real
falso
checagem
Não é verdade que vídeo mostra 'mulher artificial' comercializada na China
"""

IA_PAGE_11 = """
falso
checagem
Fotos de parque temático demoníaco foram geradas por inteligência artificial
falso
checagem
Foto que mostra papa Francisco com jaqueta branca foi gerada por inteligência artificial
"""

IA_PAGES = [IA_PAGE_1, IA_PAGE_2, IA_PAGE_3, IA_PAGE_4, IA_PAGE_5, IA_PAGE_6,
            IA_PAGE_7, IA_PAGE_8, IA_PAGE_9, IA_PAGE_10, IA_PAGE_11]

ELEICOES_2026_PAGE_1 = """
falso
eleições 2026
checagem
Número maior de eleitores do que de habitantes em cidades da Bahia não indica fraude
falso
boataria política
checagem
TSE não anunciou novas urnas eletrônicas para as eleições deste ano
falso
boataria política
checagem
É falso que Smartmatic desenvolveu as urnas eletrônicas brasileiras
falso
boataria política
checagem
Não é verdade que Casa Branca 'autorizou' Bolsonaro a disputar eleições
falso
políticas públicas
checagem
É falso que André Mendonça foi nomeado coordenador-geral das eleições
falso
boataria política
checagem
Trump não disse que Lula nunca mais vai concorrer às eleições
não é bem assim
boataria política
checagem
Pesquisa que mostra Flávio com 50% dos votos no primeiro turno é restrita a SC
falso
boataria política
checagem
Nunes Marques não tornou Bolsonaro elegível novamente
falso
boataria política
checagem
É falso que Pilili fez gesto de apoio a Lula em cerimônia no TSE
falso
boataria política
checagem
É falso que Lula prometeu se mudar para Cuba caso Flávio Bolsonaro vença
falso
boataria política
checagem
É falso que 811 mil chineses entraram no Brasil desde 2023 e vão votar nas eleições
falso
boataria política
checagem
É falso que Flávio Bolsonaro disse que irá privatizar o SUS se for eleito presidente
"""

ELEICOES_2026_PAGES = [ELEICOES_2026_PAGE_1]

# tag=eleicoes-2022 -- AMOSTRA (7 de 35 paginas; pagina 3 descartada por ter
# retornado, na coleta, o mesmo conteudo da pagina 2)
ELEICOES_2022_PAGE_1 = """
falso
eleições 2026
checagem
Barroso e Moraes não mandaram fabricar chips em Taiwan para fraudar urnas
falso
boataria política
checagem
É falso que Mendonça pediu ao STF esclarecimentos sobre eleição de 2022
falso
boataria política
checagem
É falso mapa de votação do eleitorado feminino no Brasil em 2022
falso
boataria política
checagem
É falso que PF descobriu que Lula teve apenas 36% dos votos em 2022
falso
boataria política
checagem
Não é verdade que TSE contabilizou voto de eleitora ausente em 2022
discurso oficial
checagem
Em primeiro discurso após se tornar réu, Bolsonaro mente sobre 8 de Janeiro e eleições
falso
boataria política
checagem
'Financial Times' não publicou que Joe Biden fraudou eleições brasileiras de 2022
falso
boataria política
checagem
Não há provas de que funcionários do governo americano trabalharam no TSE na eleição de 2022
falso
boataria política
checagem
É falso que Elon Musk publicou no X prova de vitória de Bolsonaro em 2022
falso
boataria política
checagem
É falso que Smartmatic atuou nas eleições de 2022 no Brasil e recebeu dinheiro da Usaid
falso
eleições 2024
checagem
Posts inventam diálogo entre Moraes e engenheiro da Oracle para sugerir fraude em 2022
falso
boataria política
checagem
Lula defendeu 'asfaltozinho' e não 'assaltozinho' em discurso de 2022
"""

ELEICOES_2022_PAGE_2 = """
falso
boataria política
checagem
Posts resgatam acusações sem provas de Bolsonaro para atribuir crimes a ministros do STF
falso
boataria política
checagem
Vídeo mostra apoio de mototaxistas a Lula em 2022, não ato de facção pró-Eduardo Paes
falso
checagem
Posts reciclam vídeo em que Bolsonaro faz alegação falsa sobre fraude em 2018
falso
checagem
É falso que TSE cassou a chapa de Lula e Alckmin
falso
checagem
É falso que o 'Financial Times' afirmou que Mourão é informante da CIA
falso
checagem
É falso que vídeo mostra protesto recente de mulheres de militares no Rio de Janeiro
não é bem assim
checagem
Paulo Pimenta não admitiu fraude ao dizer que Lula venceu com 39% dos votos em 2022
não é bem assim
checagem
Vídeo mostra senador do União Brasil, não do PT, brigando com atendente em aeroporto
não é bem assim
boataria política
checagem
É de 2017 vídeo em que Mariana Godoy responde a Alckmin que problema do Brasil é má administração
falso
checagem
Posts usam banner do Avante para dar a entender que Zema apoiou Lula em 2022
falso
checagem
Marcola citado por Lula em live é seu assessor, não líder do PCC
falso
checagem
É falso que juiz anulou inelegibilidade de Jair Bolsonaro
"""

ELEICOES_2022_PAGE_3 = """
falso
checagem
Lula se referia a dados de 2018 quando disse que Brasil tinha R$ 1,45 trilhão em reservas
falso
checagem
Vídeo mostra manifestação contra governador da Paraíba, não contra Lula
falso
checagem
Posts tiram vídeo de contexto para mentir que Alckmin 'admitiu' fraude nas eleições de 2022
falso
checagem
Trecho de voto de Nunes Marques circula fora de contexto para sugerir que urnas foram fraudadas
falso
checagem
Etchegoyen não disse que resultado das eleições de 2022 foi manipulado
falso
checagem
Senado não aprovou audiência pública neste ano para questionar resultado eleitoral de 2022
falso
checagem
Estados Unidos não provaram que eleições brasileiras de 2022 foram fraudadas
falso
checagem
Alexandre de Moraes não disse que eleição teve falhas e pode ser anulada
falso
checagem
Vídeo mostra carreata em Cuiabá em 2022, não recepção a Bolsonaro em Brasília
falso
checagem
É falso que Lula comentou com Arthur Lira que não teria vencido a eleição
checagem
Eleição presidencial dominou a desinformação em 2022, com saúde e guerra na Ucrânia em seguida
falso
checagem
Fala de Bolsonaro sobre 'vitória no dia 30' foi gravada em outubro, não dezembro
"""

ELEICOES_2022_PAGE_4 = """
checagem
Bolsonaro mentiu mais de quatro vezes por dia durante governo
falso
checagem
Fala antiga de Bolsonaro sobre liberdade ser mais importante que a vida circula fora de contexto
falso
checagem
Homem que planejou atentado a bomba disse à polícia ser bolsonarista, não petista
falso
checagem
Exército não prendeu policiais federais em acampamento bolsonarista em Brasília
falso
checagem
Vídeo sobre plano da esquerda para fraudar eleições com pesquisas é sátira
falso
checagem
Homem que pede em vídeo 'atitude' de Bolsonaro não é médico que atendeu presidente
não é bem assim
checagem
Vídeo gravado em protesto bolsonarista de 15 de novembro circula nas redes como atual
falso
checagem
É falso que Tarcísio de Freitas disse que Lula nunca tomará posse
não é bem assim
checagem
Vídeo em que Bolsonaro ameaça Moraes é de agosto de 2021, não atual
falso
checagem
É falso que Globo apagou reportagem sobre quadrilha que prometia fraudar eleições
falso
checagem
É antigo vídeo em que Bolsonaro pede para apoiadores irem às ruas
checagem
Do 2º turno à diplomação, as mentiras criadas para negar o resultado das eleições
"""

ELEICOES_2022_PAGE_5 = """
falso
checagem
Vídeo em que Bolsonaro diz que 'tudo que for legal fazer, eu farei' é de 2021, não atual
falso
checagem
Não é verdade que PM do DF prendeu vândalos infiltrados pelo PT em protesto bolsonarista
não é bem assim
checagem
Vídeo de militares no RJ mostra preparação para corrida, não para golpe de Estado
não é bem assim
checagem
Vídeo sobre ônibus incendiado e grito de 'fora, Bolsonaro' é antigo
falso
checagem
É falso que um único mesário 'ativou' 5.000 urnas em cidades paulistas
falso
checagem
Passaporte de Lula foi apreendido pela PF em 2018, não recentemente
falso
checagem
Vídeo antigo volta às redes como se fosse de ato bolsonarista recente na avenida Paulista
falso
checagem
É falso que Bolsonaro editou decreto para transferir comando de polícias ao governo federal
falso
checagem
É falso que Michelle Bolsonaro tuitou que 'não haverá posse' de Lula
falso
checagem
Novo Manual de Mobilização Militar não coloca Brasil sob tutela das Forças Armadas
falso
checagem
Vídeo mostra soldados no Rio Grande do Norte em 2017, não recentemente
falso
checagem
É de 2018 vídeo que mostra ação de militares e policiais em favela do Rio de Janeiro
"""

ELEICOES_2022_PAGE_6 = """
falso
checagem
É falso que Superior Tribunal Militar decretou que Bolsonaro fique na Presidência
falso
checagem
Foto de 2021 que mostra Bolsonaro fardado circula fora de contexto
não é bem assim
checagem
É falso que deputado petista disse que Bolsa Família será de R$ 175
falso
checagem
Vídeo antigo de protesto de indígenas em Brasília volta às redes como se fosse atual
falso
checagem
Vídeo que mostra transporte do corpo de Gal Costa é usado para dizer que Lula está morto
falso
checagem
Vídeo é editado para dizer que Lula se corrigiu e só prometeu 'picanha de soja'
falso
checagem
Áudios golpistas atribuídos a Tarcísio de Freitas não foram gravados por ele
falso
checagem
Mentiras nas redes misturam Copa e política, como falsa dedicatória de Richarlison a Bolsonaro
falso
checagem
Homem que faz denúncias falsas de fraude em vídeo não é servidor exonerado do TSE
falso
checagem
É falso que Bolsonaro ganhou a eleição presidencial com 51% dos votos
checagem
Lula não disse que irá colocar 'caminhoneiros em seu devido lugar'
falso
checagem
Partido de Bolsonaro requenta informações falsas e pede que TSE anule só o 2º turno
"""

ELEICOES_2022_PAGE_7 = """
falso
checagem
É falso que TRF-1 apagou processos contra Lula
falso
checagem
É falso que petista é dono de caminhão que transportou urnas em São Paulo
falso
checagem
Tendas do Exército na praça da Sé são para população de rua, não golpe militar
falso
checagem
É falso que Bolsonaro assinou mandado de injunção para obter código-fonte das urnas
falso
checagem
Títulos de eleitor no lixo não provam fraude eleitoral no Ceará
falso
checagem
É falso que Lula não foi convidado para a COP27 e falou para 'ONG esquerdista'
falso
checagem
É falso que equipe de transição de Lula possui 283 pessoas que recebem R$ 17 mil mensais
falso
checagem
Logs das urnas não identificam nomes e votos dos eleitores
falso
checagem
Ministros do STF são alvos de reportagens falsas, vídeos antigos e mentiras já desbancadas
falso
checagem
Vídeos antigos de Bolsonaro e de militares circulam fora de contexto para estimular manifestações
falso
checagem
É falso que vídeo mostra petistas atirando em igreja
falso
checagem
Bolsonaro não chamou apoiadores dele de 'marginais' e 'terroristas'
"""

ELEICOES_2022_PAGE_8 = """
falso
checagem
Janones não disse que Lula vai acabar com o Auxílio Brasil
falso
checagem
Lula não reduziu o Auxílio Brasil para R$ 375 nem disse que manterá o benefício por mais quatro meses
falso
checagem
Montagem muda faixa bolsonarista para incluir 'ereção' no lugar de 'eleição'
falso
checagem
Militar assassinado em Campinas não integrava grupo de fiscalização das eleições
falso
checagem
Vídeo mostra militares no metrô de São Paulo no 7 de Setembro, não recentemente em Jundiaí
não é bem assim
checagem
Vídeo mostra ato do 7 de Setembro em Brasília, não manifestação recente
falso
checagem
Vídeo em que senador pede impeachment de ministros do STF é de 2019, não recente
falso
checagem
Lula não prometeu e Jovem Pan não noticiou indulto a Adélio Bispo
falso
checagem
É falso que TSE não contabilizou votos de São Pedro da Aldeia e isso indicaria fraude
falso
checagem
Eleitor brasileiro no Canadá engana ao sugerir em vídeo que seu voto não foi contabilizado
falso
checagem
É falso que Putin anunciou intervenção no Brasil em caso de fraude eleitoral
falso
checagem
Vídeo de 2017 em que PM apoia Mourão e pede golpe militar volta a circular como se fosse atual
"""

ELEICOES_2022_PAGE_9 = """
falso
checagem
Vídeo de militares em estação de trem de Suzano é de 2018, não recente
falso
checagem
É falso que voto de eleitor de Miami não foi computado pelo TSE pois seção sumiu
falso
checagem
As mentiras sobre a urna eletrônica divulgadas por site argentino a partir de texto apócrifo
falso
checagem
Mulher em vídeo mente ao dizer que Bolsonaro não teve votos contados em Manicoré
falso
checagem
Alckmin não disse que taxar o PIX é 'extremamente necessário'
falso
checagem
STM e Defesa não provaram fraude eleitoral nem intimaram Moraes
falso
checagem
É falso tuíte atribuído a Lula sobre retomada do ICMS para combustíveis
falso
checagem
Montagem usa vídeos antigos para dizer que Lula não quer cumprir promessa de auxílio de R$ 600
não é bem assim
checagem
Vídeo que mostra Malafaia em Brasília não é atual, mas do 7 de Setembro
falso
checagem
Vídeo não mostra ministro da Defesa dizendo que houve fraude na eleição
falso
checagem
É falso que peritos federais provaram fraude nas urnas em 2022
falso
checagem
É mentira que vídeo mostra visita de Lula a Marcola, líder do PCC, após eleição
"""

ELEICOES_2022_PAGE_10 = """
não é bem assim
checagem
Ratinho não chamou de 'imbecis' manifestantes golpistas que bloqueiam estradas
não é bem assim
checagem
Urna em Mato Grosso com 100% dos votos para Lula não é prova de fraude eleitoral
falso
checagem
Bolsonaro, não Lula, enviou ao Congresso Orçamento com auxílio de R$ 405
falso
checagem
Lula não publicou tuítes dizendo que irá criar 'Guarda Nacional' e desarmar polícias
falso
checagem
Vídeo de tropas do Exército em Niterói é de 2018, não deste ano
falso
checagem
Vídeo gravado no Espírito Santo em 2018 é usado para inflar atos golpistas no Rio de Janeiro
falso
checagem
CNN não noticiou que Lula tem planos taxar Pix e congelar poupanças
falso
checagem
É falso tuíte de Bolsonaro sobre reunião com generais e ministro da Justiça após derrota na eleição
não é bem assim
checagem
Vídeo em que bolsonaristas oram na Esplanada dos Ministérios foi registrado antes do segundo turno
não é bem assim
checagem
Vídeo que mostra policiais cantando hino nacional com caminhoneiros é de 2018, não atual
falso
checagem
Bolsonaro postou texto sobre '50 tons de vermelho' em setembro, não após 2º turno
falso
checagem
É falso que vídeo mostra discurso de Bolsonaro pedindo intervenção militar após 2º turno
"""

ELEICOES_2022_PAGE_11 = """
falso
checagem
É falso que artigo 142 prevê que presidente deve ficar em silêncio por 72 horas após eleições
falso
checagem
Vídeo de policiais no Congresso foi gravado em 2017, não após o segundo turno
falso
checagem
Vídeo mostra treinamento militar em Campinas, não tanques do Exército rumo a Brasília
falso
checagem
Soma de percentuais de votos de Lula e Bolsonaro nas regiões não prova fraude
falso
checagem
É falso que Lula chamou caminhoneiros de 'vagabundos fascistas'
falso
checagem
Vídeo mostra entrevista de Bolsonaro em 26 de outubro, não pronunciamento após derrota
falso
checagem
Painel de mesário mostra número de eleitores com biometria, não votos para Lula e Bolsonaro
falso
checagem
Vídeo não mostra prefeito do PT na Bahia sendo preso por roubar R$ 30 milhões
falso
checagem
Foto mostra dinheiro apreendido no RJ em 2020, não no PA antes da eleição
falso
checagem
É falso que foto de candidato não apareceu em urna de Taguatinga
falso
checagem
É falso que PF apreendeu R$ 985 milhões destinados à campanha de Lula
falso
checagem
Lula não disse que 'educação de relacionamento homoafetivo' será prioridade nas escolas
"""

ELEICOES_2022_PAGE_12 = """
falso
checagem
Lula não usou ponto eletrônico no ouvido no debate da Globo
falso
checagem
É falso que Jean Wyllys será ministro da Educação em eventual governo Lula
falso
checagem
Lula não disse que vai rever ou acabar com o PIX
falso
checagem
Vídeo mostra abordagem policial a torcedores no Ceará, não petistas que iriam 'botar o terror' em Curitiba
falso
checagem
Propostas em santinho apócrifo não constam no plano de governo de Lula
falso
checagem
Lula não disse em debate que MEI vai acabar; modalidade foi criada no governo do petista
falso
checagem
Eleitor não votou antecipadamente para o 2º turno no PA
falso
checagem
É falso que campanha de Bolsonaro gastou só R$ 2,5 milhões e não anunciou no Google
falso
checagem
Não é verdade que Pardal, aplicativo do TSE, impede denúncias contra o PT
falso
checagem
Vídeo do ex-jogador Ronaldo foi editado para insinuar que ele declarou apoio a Bolsonaro
não é bem assim
checagem
Vídeo mostra resoluções de encontro de direitos humanos do PT, não plano de governo do partido
falso
checagem
'O Globo' não teve acesso antecipado a resultado do segundo turno
"""

ELEICOES_2022_PAGE_13 = """
falso
checagem
Vídeo editado faz crer que Bolsonaro disse que cortará salários e aposentadorias em 25%
falso
checagem
Lula não tuitou que vai liberar pequenos furtos, como o de celular
falso
checagem
É falso que Bolsonaro perdeu votos na totalização após aplicativo do TSE travar
não é bem assim
checagem
Vídeo com mensagem de Maduro para Lula é de 2020, não atual
falso
checagem
Lula não é o criador do auxílio-reclusão nem do indulto para presos
falso
checagem
É falso que policial ferida por Roberto Jefferson estava grávida e perdeu o bebê
falso
checagem
Vídeo mostra limpeza de canal, não membros do MST bloqueando o rio São Francisco
falso
checagem
Imagem é manipulada para mostrar Lula ao lado de traficante carioca
falso
checagem
Vídeo mostra professoras forçando menino a tomar ômega 3, não a passar batom
checagem
Após ataque de Roberto Jefferson a policiais, Bolsonaro mente para se afastar do aliado
falso
checagem
Vídeo de balsa em chamas mostra ação contra garimpo ilegal, não incêndio criminoso de petistas
falso
checagem
É falso que PT votou contra a criação do Auxílio Brasil no Congresso
"""

ELEICOES_2022_PAGE_14 = """
falso
checagem
Tuítes atribuídos a Felipe Neto e André Janones sobre entrevista de Bolsonaro são falsos
checagem
Bolsonaro mente ao dizer que PT propôs diminuir idade do estupro de vulnerável
falso
checagem
É falso que PT pediu ao TSE para fechar a Jovem Pan
falso
checagem
Marcola citado por Lula em discurso é assessor do PT, não líder do PCC
falso
checagem
É mentira que censor do TSE esteve na Jovem Pan
falso
checagem
Vídeo mostra manifestação em faculdade em Joinville, não invasão de igreja luterana
falso
checagem
Ao dizer no Flow que 'político tem que mentir', Lula se referia a Bolsonaro
checagem
No Flow, Lula infla legado do PT e distorce fala de Bolsonaro sobre mentiras na política
falso
checagem
É falso que Lula prometeu acabar com trabalho por aplicativo
falso
checagem
Homem ao lado de Lula em vídeo não foi preso por tiroteio próximo a ato de Tarcísio de Freitas
falso
checagem
Vídeo dissemina teoria conspiratória sobre hackers russos no TSE e manipulação na apuração
falso
checagem
Augusto Heleno não disse que Tarcísio de Freitas está sob ameaça
"""

ELEICOES_2022_PAGE_15 = """
falso
checagem
Lula não escreveu tuíte sobre bloquear poupanças para manter Auxílio Brasil
falso
checagem
Vídeo é editado para fazer crer que Lula apoia roubo de celular como meio de sobrevivência
falso
checagem
É falso que traficantes invadiram seções eleitorais na Rocinha e no Turano para obrigar votos em Lula
falso
checagem
É falso tuíte atribuído a Lula sobre tráfico de drogas gerar riqueza para comunidades
falso
checagem
É falso que Bolsonaro tuitou crítica a padres e bispos sobre campanha em Aparecida
falso
checagem
Sigla CPX, que aparece em boné de Lula, não tem relação com facção criminosa
falso
checagem
PT não propôs em 2022 criar assembleia constituinte e descriminalizar drogas
falso
checagem
Lula não propôs prazo para devolver armas e nem reduzir armamentos da polícia
falso
checagem
É falso que eleitor de Lula não precisará votar no 2º turno por indicação de Alexandre de Moraes
falso
checagem
Vídeo do JN é editado para fazer crer que Bolsonaro aparece à frente de Lula em pesquisa do Ipec
falso
checagem
É falso que Bolsonaro propôs acabar com feriado de 12 de outubro
falso
checagem
Homem que aparece em vídeo não é Geddel e fazendas citadas não são de Lula e Dilma
"""

ELEICOES_2022_PAGE_16 = """
falso
checagem
Boletins de urna mostrados em vídeo não são de MG nem provam fraude
falso
checagem
Voto em trânsito explica número maior de eleitores em Macapá e Uberaba (MG), não fraude
falso
checagem
É falso que Dias Toffoli assumiu a presidência do TSE no lugar de Alexandre de Moraes
falso
checagem
Lula não postou tuíte em que diz 'chega dessa coisa de cristianismo' e 'Estado será o novo Deus'
falso
checagem
É falso que Erika Hilton foi convidada para ministério no governo Lula
falso
checagem
Vídeo em que Barroso alega atraso na totalização é de 2020, não recente
falso
checagem
Diferença de votos entre Lula e Bolsonaro em Maceió mostrada em vídeo ocorreu por erro em site de jornal
falso
checagem
É falsa imagem em que Lula segura estátua de Baphomet
falso
checagem
Tuítes atribuídos a Lula sobre fechamento de igrejas são falsos
falso
checagem
É mentira que seção em Sete Lagoas (MG) registrou mais votos do que eleitores
falso
checagem
É falso que Lula prometeu acabar com Auxílio Brasil e proibir benefício a quem mora sozinho
falso
checagem
Lula não disse que 'nem Deus tira essa eleição' dele
"""

ELEICOES_2022_PAGE_17 = """
falso
checagem
É falso que Lula propõe criação de banheiro infantil unissex caso eleito
falso
checagem
Quadro de Baphomet em foto de Bolsonaro na maçonaria é montagem
falso
checagem
Voto em trânsito justifica votação maior para presidente do que para outros cargos
falso
checagem
É falso que cidades do Nordeste registraram mais votos em Lula que total de habitantes
falso
checagem
Áudio sobre 'revelação divina' e 'guerra' no segundo turno não é de Michelle Bolsonaro
não é bem assim
checagem
Vídeo não mostra fraude, mas defeito em urna que foi substituída em Petrópolis (RJ)
falso
checagem
Não é verdade que eleitores do Espírito Santo já votaram para o segundo turno
falso
checagem
Vídeo engana ao dizer que boletim de urna jogado na rua em Curitiba indica votos descartados
falso
checagem
Não é verdade que Ciro gravou áudio dizendo que eleições estão armadas para Lula
não é bem assim
checagem
Fala de Lula sobre 'não deixar quietos' Moro e Dallagnol é de 2020, não atual
falso
checagem
É falso que o total de votos para Lula em Barreiras (BA) foi superior ao número de habitantes da cidade
falso
checagem
É falso tuíte em que Ciro Gomes teria declarado apoio a Bolsonaro
"""

ELEICOES_2022_PAGE_18 = """
falso
checagem
Vídeo engana ao afirmar que fotos de candidatos foram trocadas em Sapiranga (RS)
falso
checagem
É falso que urnas foram substituídas no Japão por mostrar número 13 em vez de 22
falso
checagem
Vídeo em que pessoas cantam hino em Lisboa é de 7 de Setembro, não da véspera do 1º turno
falso
checagem
Vídeo que mostra bolsonaristas comemorando em shopping não foi gravado na Austrália
não é bem assim
checagem
Táxi mostrado em vídeo estava a serviço do TRE-RJ e com escolta policial
falso
checagem
Não é possível afirmar que Bolsonaro venceu na Nova Zelândia em 2022
falso
checagem
Alexandre de Moraes não pediu retirada de vídeo em que Bolsonaro aparece emocionado
falso
checagem
Vídeo que mostra confusão entre petistas em Aracaju é de 2013 e não tem relação com ato de Lula
falso
checagem
Plano de governo de Lula não prevê legalização de drogas ou perseguição a religiosos
não é bem assim
checagem
Queixas sobre urnas não serão feitas pelo app Pardal, do TSE, em 2022
falso
checagem
É falso que Datafolha orienta pesquisadores a cancelar entrevista com apoiadores de Bolsonaro
falso
checagem
É falso que Polícia Federal identificou urnas com votos já registrados em Brasília
"""

ELEICOES_2022_PAGE_19 = """
falso
checagem
É falso que urnas tinham votos pré-registrados para Lula em Serafina Corrêa (RS)
falso
checagem
Vulnerabilidades em urnas citadas em vídeo de 2014 já foram corrigidas
não é bem assim
checagem
Vídeo de urna em porta-malas de Uber em Campo Grande não mostra irregularidade
falso
checagem
Faixa com 'Globo lixo' foi erguida por Bolsonaro em aeroporto, não em frente à emissora
falso
checagem
É falso que Lula usava tornozeleira eletrônica no debate da Globo
falso
checagem
É falso que Alexandre de Moraes proibiu o uso da camisa do Brasil nas eleições
falso
checagem
É falso que votação pode ser contestada se eleitor deixar de assinar livro ou pegar comprovante
falso
checagem
Notícia sobre bloqueio do WhatsApp no Brasil é de 2015, não atual
falso
checagem
É falso que urnas estão sendo modificadas no Sindicato dos Metalúrgicos do ABC
falso
checagem
Não é verdade que plano de governo de Lula prevê moradias compartilhadas
checagem
Quais desinformações Lula, Bolsonaro, Ciro e Tebet repetiram durante a campanha
falso
checagem
É falso que urnas de Cordeiro (RJ) tinham votos pré-registrados para Lula
"""

ELEICOES_2022_PAGE_20 = """
falso
checagem
Voto não é perdido ao apertar 'confirma' na urna durante alerta para conferir o voto
falso
checagem
Vídeo que mostra agressão em rádio de Roraima é de 2018 e não tem relação com Lula e Bolsonaro
falso
checagem
Posts enganam ao associar foto de praça vazia a comício de Lula em SC
não é bem assim
checagem
Globo não pediu autorização à Justiça para entrevistar Adélio Bispo
falso
checagem
Vídeo que mostra preparação de urnas em sindicato em SP não indica irregularidade ou fraude
falso
checagem
É falso que Lula pretende criar Ministério da Verdade e controlar gastos da população
falso
checagem
Vídeo mostra prisão de Lula em 2018, não manifestação contra ele no Paraná em 2022
falso
checagem
É falso que Bolsonaro foi aplaudido de pé após discurso na ONU
falso
checagem
Erro mostrado em vídeo é de pesquisa contratada por candidato em Rondônia
checagem
Presidenciáveis inflam legados e omitem fatos ao atacar adversários no Programa do Ratinho
falso
checagem
Print falso do G1 atribui a Lula frase sobre a Venezuela que ele não disse
não é bem assim
checagem
Datafolha mostra soma de percentuais de 99% e 101% devido a arredondamento
"""

ELEICOES_2022_PAGE_21 = """
falso
checagem
Reportagem do Jornal Hoje sobre aumento da pobreza foi veiculada em 2018, não em governos do PT
falso
checagem
Vídeo que mostra garis entregando urnas no RJ é de 2018 e não prova fraude
falso
checagem
É falso que TSE ordenou que todos os vídeos dos atos de 7 de Setembro sejam excluídos da internet
não é bem assim
checagem
Comício de Lula em Curitiba não estava vazio; vídeo foi gravado antes do início
falso
checagem
Música de apoio a Lula é inserida em vídeo com a torcida do Flamengo
falso
checagem
Vídeo é manipulado para afirmar que Bolsonaro liderou pesquisa Ipec divulgada em 12 de setembro
falso
checagem
É falso que vídeo mostra furto de celular em evento com Lula
falso
checagem
É falso que Alexandre de Moraes mandou Bolsonaro apagar vídeo com entrevistas de chefes de facção
falso
checagem
Lula não disse que acabará com o Pix se for eleito
checagem
Lula, Bolsonaro, Ciro e Tebet erram ao falar de mulheres, economia e alimentos
falso
checagem
É montagem foto de ministro do TSE com blusa de Lula
falso
checagem
Postagens distorcem resultados para dizer que Ibope e Datafolha erraram em 2018
"""

ELEICOES_2022_PAGE_22 = """
falso
checagem
É falso que Datafolha se recusa a entrevistar eleitores de Bolsonaro
falso
checagem
Vídeo da Globo sobre candidatura de Lula barrada em 2018 é difundido como se fosse atual
falso
checagem
Vídeo que mostra Lula se entregando à PF em 2018 é editado para inserir xingamentos
checagem
Anúncio de Thronicke engana ao dizer que uso de emendas do orçamento secreto é 'fake news'
checagem
Na CNN, Lula usa desinformação para atacar governo Bolsonaro
checagem
Bolsonaro mente a podcasters evangélicos sobre compra de imóveis em dinheiro vivo
falso
checagem
Bolsonaro não foi 'expulso' do Maracanã sob vaias em jogo do Flamengo no dia 7 de setembro
falso
checagem
Homem com boné de Lula não é empresário que negou marmita a eleitora petista
não é bem assim
checagem
Vídeo mostra ato bolsonarista na Avenida Paulista em 2021, não em 2022
falso
checagem
É falso que batalhão cantou música contra o PT em desfile do Sete de Setembro
checagem
Na TV, presidenciáveis desinformam sobre gás de cozinha, Bolsa Família e refinarias
falso
checagem
Áudio foi inserido em vídeo que mostra Bolsonaro e Michelle antes do Sete de Setembro
"""

ELEICOES_2022_PAGE_23 = """
falso
checagem
Bolsonaro não foi recebido na igreja de Valdemiro com gritos pró-Lula
falso
checagem
Vídeo de multidão em Salvador é do Sete de Setembro de 2021, não deste ano
falso
checagem
Foto da Esplanada atribuída ao Sete de Setembro de 2021 foi registrada neste ano
não é bem assim
checagem
Galeria mostra fotos publicadas no Sete de Setembro de 2021, não neste ano
falso
checagem
Vídeo de ato em Copacabana em 2021 volta a circular como se fosse deste ano
falso
checagem
Vídeos antigos são atribuídos a atos de 7 de Setembro em 2022
não é bem assim
checagem
Prefeitura de Campos Gerais (MG) cumpre lei eleitoral ao tirar logotipo do governo federal de obra
falso
checagem
Artista espanhol tatuou ânus em repúdio a Trump, não a Bolsonaro
falso
checagem
Tony Ramos não declarou apoio a Lula em vídeo
não é bem assim
checagem
Vídeo de colunista do 'UOL' é tirado de contexto para sugerir endosso a narrativas bolsonaristas
falso
checagem
É falso que Ipec e Instituto Lula funcionam no mesmo endereço
checagem
O que é falso e o que é fato em declarações de Lula sobre absolvições na ONU e na Justiça
"""

ELEICOES_2022_PAGE_24 = """
falso
checagem
Veículo apedrejado conduzia jornalistas, não apoiadores de Lula
falso
checagem
Fala de Fabíola Cidral sobre provocação a Bolsonaro se refere a Tebet, não a Vera Magalhães
falso
checagem
Não é verdade que Vera Magalhães recebe R$ 500 mil por ano do governo de SP
falso
checagem
Lei eleitoral proíbe assinatura com número de candidato no caderno de votação
falso
checagem
É falso que produção do JN entregou respostas a Lula durante entrevista
não é bem assim
checagem
Posts distorcem fala de Lula ao JN sobre setor 'fascista' do agronegócio
falso
checagem
Vídeo do JN de 2020 sobre 'fique em casa' é editado para excluir 'para quem pode'
falso
checagem
É falso que Ratinho entrevistará Bolsonaro nesta quinta
falso
checagem
Audiência da Globo subiu após entrevista de Bolsonaro, segundo Kantar Ibope
falso
checagem
Vídeo em que público canta 'Lula ladrão' não foi gravado em comício do ex-presidente
falso
checagem
Vídeo que mostra oração de Bolsonaro é de 2018, não anterior ao JN
checagem
Lula, Bolsonaro, Ciro e Tebet iniciam campanha com declarações falsas sobre economia
"""

ELEICOES_2022_PAGE_25 = """
falso
checagem
É falso que QR Code no título de eleitor conta voto para Lula automaticamente
falso
checagem
Posts enganam ao dizer que Chauí tirou garrafa de cachaça de Lula
não é bem assim
checagem
Reportagem do 'JN' é tirada de contexto para atribuir a Lula e Dilma contas na Suíça
checagem
Lula diz que Auxílio Brasil acaba em dezembro, mas lei garante benefício de R$ 400
falso
checagem
Frases sobre família e igreja atribuídas a Lula em postagem são falsas
falso
checagem
Uso da Bíblia não foi proibido no Brasil
falso
checagem
É falso vídeo que usa imagens do JN para dizer que Bolsonaro lidera pesquisa Ipec
falso
checagem
Ponte sobre rio das Mortes que aparece em vídeo não é obra do governo Bolsonaro
checagem
No Roda Viva, Ciro Gomes erra sobre endividamento de estados e acesso à internet
falso
checagem
É falso que Bolsonaro não inaugurou nenhuma unidade de educação
falso
checagem
Post atribui a Fernando Haddad falsas propostas para a segurança
falso
checagem
Cartilha citada por Damares não ensina crianças a usar crack
"""

ELEICOES_2022_PAGE_26 = """
falso
checagem
Vídeo que mostra recepção a Bolsonaro não é recente nem foi gravado em Goiânia
falso
checagem
É falso que TSE fez propaganda para Lula em título de eleitor
falso
checagem
Plano de governo de Bolsonaro contém falsidades sobre transparência e leis para mulheres
falso
checagem
Condenação no TCU não torna Deltan Dallagnol inelegível automaticamente
falso
checagem
Twitter não suspendeu Michelle Bolsonaro, que não tem conta na rede
checagem
Lula cita na Fiesp informações falsas sobre voto feminino e produção de carnes
checagem
No Roda Viva, Tebet erra informação sobre financiamento federal ao SUS
checagem
Da ditadura à eleição de 2018, Bolsonaro mente ao Flow Podcast
não é bem assim
checagem
Áudio sobre Bolsonaro atribuído a Luana Piovani é de 2018
falso
checagem
Lula não disse que '100% das mulheres no México são mulheres'
falso
checagem
É mentira que a Renner declarou apoio a Lula
falso
checagem
É falso que Lula disse que agronegócio deve ser 'eliminado da Terra'
"""

ELEICOES_2022_PAGE_27 = """
falso
checagem
Mesário não pode anular voto de quem usa camiseta amarela
não é bem assim
checagem
Pesquisa eleitoral que aparece em vídeo não foi registrada no TSE
checagem
O que Lula, Bolsonaro, Ciro, Janones e Tebet falam de enganoso sobre suas biografias
falso
checagem
É falso que Tom Cruise manifestou apoio a Bolsonaro em vídeo
falso
checagem
Vídeo infla número de leis sancionadas por Bolsonaro que beneficiam mulheres
falso
checagem
É falso que 'G1' publicou que banqueiros apoiam Lula em troca da revogação do Pix
não é bem assim
checagem
Vídeo mostra simulação de fraude em urna diferente da usada no Brasil
falso
boataria política
checagem
É falso que STF e TSE criaram lei para cassar cristãos eleitos
checagem
Ciro Nogueira infla prejuízo dos bancos e engana ao dizer que Bolsonaro criou Pix
não é bem assim
checagem
Vereadora do PSOL em Vitória corrigiu fala sobre derrota de Lula na eleição
falso
checagem
Público não gritou 'mito' após Nando Reis dizer 'Fora Bolsonaro' em Belo Horizonte
falso
checagem
Música a favor de Lula é inserida em vídeo que mostra torcedores do Liverpool
"""

ELEICOES_2022_PAGE_28 = """
falso
checagem
Áudio com xingamento a Lula é editado em vídeo que mostra bloco de Carnaval em SP
falso
checagem
Posts reciclam denúncia arquivada por falta de provas sobre vitória de Bolsonaro no 1º turno
falso
checagem
Vídeo mostra manifestantes contra Lula em MG em 2017, e não em PE recentemente
falso
checagem
É falso que vídeo mostra Lula sendo xingado em Pernambuco
falso
checagem
Dilma e Aécio não se alternaram 241 vezes na liderança do 2º turno da eleição de 2014
falso
checagem
Hacker foi preso por vazar dados de milhões de brasileiros, não por invadir TSE
falso
checagem
Vídeo é editado para parecer que Lula foi chamado de ladrão em hotel de Natal
falso
checagem
Vídeo em que homem agride padre não foi gravado na França, mas na Guiana
falso
checagem
É falso que embaixadores não aplaudiram Bolsonaro após discurso desinformativo sobre eleição
checagem
Veja a transcrição e as checagens do discurso de Bolsonaro a embaixadores
falso
checagem
Vídeo é editado para fazer crer que cantor foi agredido após 'funk do Bolsonaro'
falso
checagem
Vídeo mostra 7 de Setembro no Rio de Janeiro, não manifestação recente em Fortaleza
"""

ELEICOES_2022_PAGE_29 = """
falso
checagem
É falso que Globo ensina em vídeo como planejar atentado contra Bolsonaro
checagem
Bolsonaro usa encontro com embaixadores para repetir informações falsas sobre eleição
não é bem assim
checagem
Texto do 'El País' de 2018 sobre Bolsonaro e mercado financeiro circula como se fosse atual
falso
checagem
Vídeo de 2016 é editado para fazer crer que Lula disse que só Bolsonaro ganha dele
falso
checagem
Posts usam foto do presidente do PSOL como se fosse de anestesista preso por estupro
falso
checagem
Policial prestava auxílio e não deu soco em Bolsonaro após facada
falso
checagem
É falso que Bolsonaro gastou apenas R$ 65 milhões com publicidade por ano
checagem
Desinformação sobre estatais abastece discurso de Lula, Bolsonaro e Ciro
não é bem assim
checagem
Prefeitura de Aracaju cumpre lei eleitoral ao tirar logotipo do governo federal de obra
falso
checagem
Não há evidência de que petista assassinado e bolsonarista tinham 'rixa antiga'
falso
checagem
Homem que exaltou Bolsonaro em escola não é policial acusado de matar petista
falso
checagem
Não há registro de que médico preso por estupro no RJ declarou apoio a Bolsonaro no Facebook
"""

ELEICOES_2022_PAGE_30 = """
falso
checagem
Fotos mostram Alexandre de Moraes jantando com Lewandowski, não José Dirceu
falso
checagem
Ministros do STF não participarão de debate sobre 'novo governo' em novembro
não é bem assim
checagem
Vídeo em que Felipe Neto chama Lula de ladrão é de 2016, não atual
falso
checagem
Vídeo não mostra Lula sendo expulso de velório de padre
não é bem assim
checagem
Servidor do Recife cobriu logotipo do governo federal para cumprir lei eleitoral
falso
checagem
STF derrubou lei sancionada por Lula para urna imprimir voto
falso
checagem
Vídeo de bolsonaristas cantando o hino na Bahia é de 2021, não deste ano
checagem
Lula, Bolsonaro e Ciro falseiam e distorcem informações sobre a Amazônia
falso
checagem
Homem agredido em vídeo não é Helder Barbalho, e sim ex-prefeito de Tucuruí (PA)
falso
checagem
Vídeo é editado para fazer crer que Lula foi xingado em Natal
checagem
Audiência pública do Ministério da Saúde reforça desinformação sobre aborto no Brasil
falso
checagem
É falso que governo Bolsonaro não destina dinheiro para emissoras de TV
"""

ELEICOES_2022_PAGE_31 = """
falso
checagem
Crítica de Lula a políticos que exploram eleitores pobres é tirada de contexto
falso
checagem
Lula não tem conta com 250 milhões de euros no Banco do Vaticano
falso
checagem
É falso que filho de Lula é o maior acionista da Petrobras
falso
checagem
Vídeo mostra ato bolsonarista em SP em 2019, não em SC recentemente
não é bem assim
checagem
Fala de Lula é editada para sugerir elogio a Bolsonaro em obra do São Francisco
falso
checagem
Polícia Civil não disse que empresa ligada ao PT contratou drone que atacou petistas
checagem
Bolsonaro repete pela 209ª vez que não há corrupção — mesmo com prisão de ex-ministro
falso
checagem
Vídeo mostra Lula sendo saudado em Uberlândia, não hostilizado em Caruaru
falso
checagem
Fotos antigas são atribuídas a comício recente de Lula em Natal
checagem
Ciro, Tebet e Janones exageram números ao falar sobre empregos e Petrobras
falso
checagem
Lula não disse que vai tirar nome de Jesus da Bíblia
falso
checagem
É falso que vídeo mostra Anitta agredida pelo público após criticar Bolsonaro
"""

ELEICOES_2022_PAGE_32 = """
falso
checagem
Homem rezando com Bolsonaro é pastor, não governante da Coreia do Sul
falso
checagem
Mulher derrubada por policial fazia protesto pró-aborto, não contra Bolsonaro
falso
checagem
É falso que vídeo mostra protesto recente contra Lula em Porto Alegre
falso
checagem
É montagem foto em que Lewis Hamilton veste camiseta com o rosto de Lula
não é bem assim
checagem
Notícia sobre emails de Adélio Bispo é de 2018, não atual
falso
checagem
É falso que Bolsonaro disse 'não sou cozinheiro' ao comentar fome no país
não é bem assim
checagem
Vídeo mostra manifestação contra Lula em Bagé em 2018, não recentemente
não é bem assim
checagem
José Dirceu não disse em entrevista que Bolsonaro perderá eleição por oposição do TSE
falso
checagem
É falso que Lula disse no Twitter que bolsonaristas não conhecem um 'quadritongo'
falso
checagem
Spray nasal citado no 'Fantástico' não é o mesmo que Bolsonaro defendeu em 2021
não é bem assim
checagem
Vídeo de protesto contra Lula divulgado como atual é de 2018
falso
checagem
Posts sobre 'resumo do mês' de Bolsonaro mostram fotos antigas
"""

ELEICOES_2022_PAGE_33 = """
falso
checagem
Não é de Aldo Rebelo áudio que responsabiliza governos do PT por alta nos combustíveis
falso
checagem
Vídeo mostra casa no Ceará, não residência de Lula em São Paulo
falso
checagem
É falso que diretor do Datafolha confessou plano para fraudar urnas
falso
checagem
Johnny Depp não disse ao 'The New York Times' que espera reeleição de Bolsonaro
falso
checagem
Homem retirado de bar por PMs em vídeo não é filho de Lula
falso
checagem
Peritos da PF não provaram no STF que urnas são fraudáveis
falso
checagem
Não é verdade que Bolsonaro disse que idosos fazem hora extra no planeta
falso
checagem
É falso que One7 é a empresa que administra carreira de Gusttavo Lima
falso
checagem
Vaias ouvidas em vídeo foram direcionadas a outros políticos, não a Bolsonaro
falso
checagem
É falso que George Soros declarou que Bolsonaro não ganhará eleições de 2022
checagem
Lula, Bolsonaro, Ciro e Doria inflam dados ao defender legados de governo
falso
checagem
Certidão mostrada em vídeo não prova que eleitor do MA teve título cancelado
"""

ELEICOES_2022_PAGE_34 = """
falso
checagem
Vídeo mostra apoio de Neymar a Aécio Neves em 2014, não a Bolsonaro em 2022
distorcido
checagem
Vídeo em que Fagner declara apoio a Bolsonaro é de 2018, não atual
falso
checagem
É falso que 'G1' noticiou que Suzane von Richthofen declarou voto em Lula
falso
checagem
É falso que eleitores com mais 70 anos devem renovar título e fazer biometria para votar
distorcido
checagem
Carregamento de cartão de memória usado em urna eletrônica não favorece ação de hackers
distorcido
checagem
Vídeo em que Felipe Neto diz que votaria em Bolsonaro contra Lula é de 2017, não atual
falso
checagem
Vídeo recorre a informações falsas para atacar credibilidade de pesquisas eleitorais
distorcido
checagem
É antigo vídeo que alega que Braga Netto condicionou eleições a voto impresso
falso
checagem
Postagens enganam ao alegar que urna eletrônica deveria ser certificada pelo Inmetro
falso
checagem
É falso que eleitor sem cadastro biométrico não poderá votar neste ano
distorcido
checagem
É de 2019 pesquisa que mostra Bolsonaro mais bem avaliado que FHC, Lula e Dilma
falso
checagem
É falso que foto mostra que Alckmin sofreu ataque recente com ovos em Jundiaí
"""

ELEICOES_2022_PAGE_35 = """
falso
checagem
É falso que Alexandre de Moraes disse que cassará chapa se Bolsonaro for reeleito
falso
checagem
É falso que pesquisa mostra que Bolsonaro lidera disputa presidencial em todos os estados
falso
checagem
Vídeo em que Lula considera não se candidatar ao Planalto é de 2020, não atual
falso
checagem
É falso que Suzane Von Richthofen será candidata a vereadora pelo PT
falso
checagem
Paolla Oliveira não disse que atrizes da Globo terão que se prostituir caso Bolsonaro seja reeleito
falso
checagem
Imagem de protesto contra Dilma em 2015 é atribuída em posts a ato por voto impresso
falso
checagem
Foto mostra manifestação pelo impeachment de Dilma, não ato pelo voto impresso no RJ
falso
checagem
Não é verdade que Mourão defendeu intervenção militar se Lula for candidato
distorcido
checagem
É de 2018 declaração de Cármen Lúcia sobre Lula ser inelegível
falso
checagem
É falso que a Lenovo comprou a Positivo, fabricante de urnas das eleições de 2022
falso
checagem
Maia não anunciou pré-candidatura à Presidência em 2022; vídeo é de 2018
"""

ELEICOES_2022_PAGES = [
    ELEICOES_2022_PAGE_1, ELEICOES_2022_PAGE_2, ELEICOES_2022_PAGE_3,
    ELEICOES_2022_PAGE_4, ELEICOES_2022_PAGE_5, ELEICOES_2022_PAGE_6,
    ELEICOES_2022_PAGE_7, ELEICOES_2022_PAGE_8, ELEICOES_2022_PAGE_9,
    ELEICOES_2022_PAGE_10, ELEICOES_2022_PAGE_11, ELEICOES_2022_PAGE_12,
    ELEICOES_2022_PAGE_13, ELEICOES_2022_PAGE_14, ELEICOES_2022_PAGE_15,
    ELEICOES_2022_PAGE_16, ELEICOES_2022_PAGE_17, ELEICOES_2022_PAGE_18,
    ELEICOES_2022_PAGE_19, ELEICOES_2022_PAGE_20, ELEICOES_2022_PAGE_21,
    ELEICOES_2022_PAGE_22, ELEICOES_2022_PAGE_23, ELEICOES_2022_PAGE_24,
    ELEICOES_2022_PAGE_25, ELEICOES_2022_PAGE_26, ELEICOES_2022_PAGE_27,
    ELEICOES_2022_PAGE_28, ELEICOES_2022_PAGE_29, ELEICOES_2022_PAGE_30,
    ELEICOES_2022_PAGE_31, ELEICOES_2022_PAGE_32, ELEICOES_2022_PAGE_33,
    ELEICOES_2022_PAGE_34, ELEICOES_2022_PAGE_35,
]

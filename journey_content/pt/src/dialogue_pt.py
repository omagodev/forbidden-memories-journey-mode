# -*- coding: utf-8 -*-
# Brazilian Portuguese dialogue for JOURNEY MODE, written WITH accents (the proper text).
# build_pt.py strips the accents to make the ASCII story.pt.json the retail font can draw.
# One entry per script id of story.json; one string per page, in the same order as the English.
# Narrator pages are "Label::text". Tokens: {name}, {a|b} (a = male, b = female). Card names stay English.
S = {}

# ---------------------------------------------------------------- chapter 1
S["c1_intro"] = [
 "Ai... minha cabeça... Eu estava num torneio de Duel Monsters agora mesmo.",
 "Um portal de luz se abriu no meio da arena e me puxou para dentro.",
 "Areia, palmeiras, um rio... Isso parece o Egito antigo!",
 "Só o meu deck veio comigo. Preciso achar alguém que saiba como voltar pra casa.",
 "Objetivo::Fale com Simon Muran, o velho sábio que espera na arena dourada.",
]
S["c1_simon_pre"] = [
 "Roupas estranhas, {rapaz|moça}... Mas essas cartas são tão antigas quanto a nossa magia.",
 "Eu caí de um portal. Você sabe como eu volto pra minha época?",
 "Talvez. Mostre como você duela e eu direi de onde veio. Duelar?",
]
S["c1_simon_win"] = [
 "Impressionante! Você duela como {um mestre|uma mestra}.",
 "O portal que te trouxe é uma fenda no tempo. Só a Pedra Temporal pode fechá-la.",
 "Os pedaços da Pedra estão além do rio, ao norte. Já avisei o guarda da ponte.",
 "Recompensa::Recebeu a carta Mystical Elf e um Cantil. Veja na Mochila.",
 "Objetivo::Cruze o rio ao norte. Teana e Jono também querem duelar com você.",
]
S["c1_simon_lose"] = ["Nada mal, mas ainda falta prática. Descanse e tente de novo."]
S["c1_simon_after"] = ["A ponte fica ao norte, subindo a estrada. Boa sorte, viajante."]
S["c1_teana_pre"] = ["Oi! Você é {o|a} {estrangeiro|estrangeira} que venceu o Simon? Duela comigo?"]
S["c1_teana_win"] = [
 "Uau, você é {bom|boa} mesmo! Fica com esta carta.",
 "Recompensa::Recebeu a carta Feral Imp.",
]
S["c1_jono_pre"] = ["Ei, {novato|novata}! Aposto que o meu deck é mais forte. Duelar?"]
S["c1_jono_win"] = [
 "Tá bom, tá bom... você ganhou. Toma, é sua.",
 "Recompensa::Recebeu a carta Baby Dragon.",
]
S["c1_teana_lose"] = ["Hehe, ganhei! Volte quando quiser."]
S["c1_jono_lose"] = ["Ha! Treina mais um pouco e volta aqui."]
S["c1_teana_wait"] = ["O velho Simon está te esperando na arena."]
S["c1_jono_wait"] = ["Fala com o Simon primeiro, depois a gente duela."]
S["c1_guard_block"] = ["Alto! Ninguém atravessa o rio sem a permissão do sábio Simon Muran."]
S["c1_guard_ok"] = ["O Simon deixou? Então pode passar, viajante."]

# ---------------------------------------------------------------- chapter 2
S["c1_end__c2_intro"] = [
 "A Cidade Real fica lá no norte. Primeiro preciso passar por essas ruínas.",
 "Fim do Capítulo 1::Capítulo 2 - Ruínas de Areia",
 "Colunas quebradas, um obelisco... e lá no fundo, um portal de pedra brilhando!",
 "Tem mais gente aqui. Aqueles dois são do torneio! Será que eles também caíram no passado?",
 "Objetivo::Vença Rex Raptor e Weevil. Depois entre no portal de pedra ao norte.",
]
S["c2_teana_done"] = ["Boa viagem, {estrangeiro|estrangeira}!"]
S["c2_jono_done"] = ["Da próxima vez eu ganho!"]
S["c2_rex_pre"] = [
 "Você também caiu aqui? Ótimo. Ganhar de você me deixa mais perto de voltar pra casa.",
 "Então vamos duelar. Quem ganhar fica com o caminho livre.",
 "Meus dinossauros vão te esmagar! Duelar?",
]
S["c2_rex_win"] = [
 "Não acredito... perdi para {um|uma} {novato|novata}!",
 "Toma, achei esta pedra brilhante nas ruínas. Talvez sirva pra você.",
 "Recompensa::Recebeu o Fragmento da Pedra Temporal 1 e a carta Ryu-kishin.",
]
S["c2_rex_lose"] = ["Hahaha! Volte quando tiver dinossauros de verdade."]
S["c2_weevil_pre"] = [
 "Hehehe. Nesse mundo ninguém confere se a gente trapaceia.",
 "Então eu vou ganhar do jeito certo, pra você lembrar.",
 "Meus insetos discordam. Duelar?",
]
S["c2_weevil_win"] = [
 "Impossível! Minha estratégia era perfeita!",
 "Tá, tá... leva esta tocha velha e me deixa em paz.",
 "Recompensa::Recebeu uma Tocha e a carta Hitotsu-me Giant.",
]
S["c2_weevil_lose"] = ["Hehehe! Eu sabia que você cairia na minha armadilha."]
S["c2_rex_done"] = ["Vai logo pro portal. Eu ainda vou ter a minha revanche."]
S["c2_weevil_done"] = ["Hmpf. Some daqui antes que eu mude de ideia."]
S["c2_portal_locked"] = ["O portal não reage. Acho que preciso vencer Rex e Weevil primeiro."]

# ---------------------------------------------------------------- chapter 3
S["c2_end__c3_intro"] = [
 "O portal está brilhando mais forte agora. Vou entrar!",
 "Fim do Capítulo 2::Capítulo 3 - O Palácio e o Príncipe",
 "Uau! O portal me levou para dentro da Cidade Real. Que palácio enorme!",
 "Na frente do palácio tem um sacerdote e um jovem que parece um rei. É o Príncipe!",
 "Objetivo::Fale com o sacerdote Seto, na frente do palácio.",
]
S["c3_seto_pre"] = [
 "{Um|Uma} {estrangeiro|estrangeira} com cartas que ninguém conhece. Ameaça ou presente?",
 "Seto, deixe {ele|ela} provar. Se {ele|ela} perder, eu mesmo mando embora.",
 "Se eu ganhar, quero saber por que essas fendas no tempo estão se abrindo.",
 "Combinado. Prepare o seu deck. Duelar?",
]
S["c3_seto_win"] = [
 "Hmpf... você venceu. Se o Príncipe confia em você, eu também vou confiar.",
 "As fendas começaram quando o sacerdote Heishin abriu o cofre dos Itens do Milênio.",
 "Leve o Selo Real. Com ele você entra no palácio e descobre o que Heishin quer.",
 "Recompensa::Recebeu o Selo Real e a carta Dark Magician.",
 "Objetivo::Entre no palácio e investigue Heishin. O Mage Soldier também quer duelar.",
]
S["c3_seto_lose"] = ["Era isso? Volte quando estiver {pronto|pronta}, {estrangeiro|estrangeira}."]
S["c3_seto_done"] = ["O palácio está aberto para você. Não me decepcione."]
S["c3_prince_before"] = ["{Bem-vindo|Bem-vinda} à Cidade Real, viajante. Mostre ao Seto o que você sabe fazer."]
S["c3_prince_after"] = ["Cuidado com Heishin. Ele anda pelos corredores do palácio à noite."]
S["c3_soldier_pre"] = ["Eu treino os guardas do palácio. Quer testar o seu deck contra mim? Duelar?"]
S["c3_soldier_win"] = [
 "Bom duelo! Leve esta carta na sua jornada.",
 "Recompensa::Recebeu a carta Celtic Guardian.",
]
S["c3_soldier_lose"] = ["Treine mais um pouco e volte aqui."]
S["c3_soldier_done"] = ["Os guardas falam muito bem de você."]
S["c3_door_locked"] = ["A porta do palácio está fechada. Preciso da permissão do Seto primeiro."]

# ---------------------------------------------------------------- chapter 4
S["c3_end__c4_intro"] = [
 "Com o Selo Real a porta se abriu. Heishin esconde alguma coisa aqui dentro.",
 "Fim do Capítulo 3::Capítulo 4 - O Golpe de Heishin",
 "Naquela noite::Heishin atacou a cidade com os seus guardas. O céu ficou vermelho de fogo.",
 "Este é o salão do trono! Heishin está lá no alto e o Príncipe está cercado!",
 "Objetivo::Derrote Heishin no salão do trono.",
]
S["c4_heishin_pre"] = [
 "Os Itens do Milênio dão poder a quem tem coragem de pegá-los. E eu tive coragem.",
 "Você atacou a cidade inteira por sete pedaços de ouro?",
 "Por sete chaves. E agora você vai me entregar o seu deck. Duelar?",
]
S["c4_heishin_win"] = [
 "Impossível! {Um|Uma} {estrangeiro|estrangeira} me venceu? Isso ainda não acabou!",
 "O que aconteceu::Heishin fugiu pela janela e levou os Itens do Milênio com ele.",
 "{name}! Heishin vai voltar atrás do Príncipe. Só existe um jeito de protegê-lo.",
 "Vou guardar a alma do Príncipe dentro do Enigma do Milênio. Ele dorme até a hora certa.",
 "{name}, eu confio em você. Encontre os Itens e me acorde quando chegar a hora.",
 "Leve o Colar do Milênio. Ele mostra o futuro e pode abrir uma fenda até o seu tempo.",
 "Recompensa::Recebeu o Colar do Milênio e a carta Gaia the Fierce Knight.",
 "Objetivo::Toque o trono brilhante para viajar no tempo.",
]
S["c4_heishin_lose"] = ["Hahaha! {Fraco|Fraca} demais. Volte quando tiver coragem de verdade."]
S["c4_prince_hall"] = ["{name}! Heishin quer os Itens do Milênio. Por favor, detenha ele!"]
S["c4_seto_before"] = ["Eu protejo o Príncipe. Vá, {estrangeiro|estrangeira}, enfrente Heishin!"]
S["c4_seto_after"] = ["O Príncipe está guardado no Enigma. Encontre os Itens e traga ele de volta."]
S["c4_throne_locked"] = ["O trono não está brilhando. Primeiro preciso derrotar Heishin."]

# ---------------------------------------------------------------- chapter 5
S["c4_end__c5_intro"] = [
 "O Colar está brilhando junto com o trono. Uma fenda no tempo está se abrindo!",
 "Fim do Capítulo 4::Capítulo 5 - O Torneio Fora do Tempo",
 "Espera... esta é a ilha do torneio do Pegasus! Será que eu voltei pro meu tempo?",
 "Não... o céu ainda tem fendas. O torneio ficou preso entre duas épocas.",
 "Objetivo::Vença Mai, Bandit Keith e Shadi. Depois enfrente Pegasus na frente do castelo.",
]
S["c5_mai_pre"] = [
 "Gracinha, aqui o que vale é estratégia. E um pouco de perfume.",
 "Então vamos ver qual estratégia é melhor.",
 "Minhas Harpias estão prontas. Duelar?",
]
S["c5_mai_win"] = [
 "Nada mal, gracinha. Você ganhou na moral.",
 "Recompensa::Recebeu a carta Harpie Lady.",
]
S["c5_mai_lose"] = ["Hihi, volte quando aprender a jogar."]
S["c5_mai_done"] = ["Boa sorte com o Pegasus. Ele é muito esquisito."]
S["c5_keith_pre"] = [
 "Esse torneio é meu. Você é só mais um nome na minha lista.",
 "Então tente riscar o meu nome, se conseguir.",
 "Vamos ver, {novato|novata}. Duelar?",
]
S["c5_keith_win"] = [
 "Grr... sorte de principiante!",
 "Recompensa::Recebeu a carta Great White.",
]
S["c5_keith_lose"] = ["Hah! Volta pra casa, {novato|novata}."]
S["c5_keith_done"] = ["Não fala comigo agora, {novato|novata}."]
S["c5_shadi_pre"] = [
 "Eu sou Shadi, guardião dos Itens do Milênio. Vejo que você carrega o Colar.",
 "Mostre que o seu coração é digno dele. Duelar?",
]
S["c5_shadi_win"] = [
 "Seu coração é puro. Tome este pedaço da Pedra Temporal.",
 "Recompensa::Recebeu o Fragmento da Pedra Temporal 2 e a carta Illusionist Faceless Mage.",
]
S["c5_shadi_lose"] = ["Seu coração ainda tem dúvidas. Volte depois."]
S["c5_shadi_done"] = ["Pegasus tem o Olho do Milênio. Tenha cuidado com ele."]
S["c5_pegasus_locked"] = ["Olá, {name}-{menino|menina}! Primeiro vença os outros três duelistas. Depois eu duelo com você."]
S["c5_pegasus_pre"] = [
 "O seu destino eu já li, {name}-{menino|menina}. Que tal descobrir se estou certo?",
 "Ninguém lê o meu destino. Eu escrevo ele no duelo!",
 "Que divertido! Duelar?",
]
S["c5_pegasus_win"] = [
 "Impossível! O Olho do Milênio não conseguiu ler a sua mente!",
 "Fique com o Olho. Talvez ele ajude você a salvar o Príncipe.",
 "Eu sou Isis. Eu vi você numa visão. Vou abrir um portal de volta ao Egito.",
 "Os Magos dos Templos guardam os outros Itens. O Príncipe precisa deles.",
 "Recompensa::Recebeu o Olho do Milênio e a carta Thousand Dragon.",
 "Objetivo::Entre no portal do castelo para voltar ao Egito.",
]
S["c5_pegasus_lose"] = ["Hahaha! Eu disse que já tinha lido o seu destino."]
S["c5_pegasus_done"] = ["O portal da Isis está aberto no castelo. Adeus, {name}-{menino|menina}!"]
S["c5_gate_locked"] = ["O portão do castelo está fechado. Primeiro preciso vencer Pegasus."]

# ---------------------------------------------------------------- chapter 6
S["c5_end__c6_intro"] = [
 "O portal da Isis está aberto. Hora de voltar pro Egito!",
 "Fim do Capítulo 5::Capítulo 6 - Os Sete Itens",
]
S["c6_arrival"] = [
 "Areia quente de novo! O portal me largou num velho cruzamento.",
 "{name}! A Isis avisou que você vinha. Guardei o Enigma em segurança.",
 "Recompensa::Recebeu o Enigma do Milênio. O Príncipe dorme dentro dele.",
 "Heishin só esvaziou o cofre. Os Itens de verdade estavam escondidos em cinco templos.",
 "Cada templo tem um Mago que guarda um Item. Vença os Magos e eles deixam você levar.",
 "Mar, floresta, montanha, deserto e campina. Entendi. Bora lá.",
 "Objetivo::Visite os cinco templos e ganhe os Itens. Depois abra o portão do Labirinto.",
]
S["c6_simon_hub"] = ["Vi os homens do Heishin perto dos templos. Corra, mas não apresse os seus duelos."]
S["c6_simon_hub_done"] = ["Você tem os cinco Itens! Vá ao portão do Labirinto. Eu guardo o cruzamento."]
S["c6_ocean_pre"] = [
 "Alto, {estrangeiro|estrangeira}! O mar não abre o templo para visitantes de pé seco.",
 "Só quero pegar emprestado o que o templo guarda. Duele comigo.",
 "A maré vai decidir. Duelar?",
]
S["c6_ocean_win"] = [
 "A maré virou... Pode entrar. O High Mage Secmeton espera lá dentro.",
 "Recompensa::Recebeu a carta Aqua Dragon.",
 "Objetivo::Entre no Templo do Mar e enfrente o High Mage Secmeton.",
]
S["c6_ocean_lose"] = ["O mar te jogou de volta pra praia. Tente de novo."]
S["c6_ocean_done"] = ["Secmeton espera lá dentro. O mar deixa você passar."]
S["c6_secmeton_locked"] = ["Uma parede de água bloqueia a porta de dentro. O Ocean Mage precisa me deixar entrar."]
S["c6_secmeton_pre"] = [
 "Então é você quem caminha pelo tempo. As águas sussurraram sobre você.",
 "Então você sabe por que vim. Preciso do Tablete do Mar.",
 "Palavras são rasas. Mostre com cartas. Duelar?",
]
S["c6_secmeton_win"] = [
 "Você nada bem, viajante. O Tablete do Mar é seu.",
 "Ele serve no portão do Labirinto. Os homens do Heishin o querem muito.",
 "Recompensa::Recebeu o Tablete do Mar e a carta Suijin.",
 "Objetivo::Faltam quatro templos - Floresta, Montanha, Deserto e Campina.",
]
S["c6_secmeton_lose"] = ["Raso demais. Mergulhe mais fundo e volte."]
S["c6_secmeton_done"] = ["Guarde bem o Tablete. O mar tem memória."]
S["c6_anubisius_pre"] = [
 "Silêncio, {estrangeiro|estrangeira}. As árvores antigas não gostam de barulho.",
 "Vim buscar a Chave do Milênio. A vida do Príncipe está em jogo.",
 "A floresta não dá nada de graça. Duelar?",
]
S["c6_anubisius_win"] = [
 "As raízes se curvam a você. Leve a Chave do Milênio.",
 "Recompensa::Recebeu a Chave do Milênio e a carta Ancient One of the Deep Forest.",
]
S["c6_anubisius_lose"] = ["A floresta engoliu as suas cartas. Tente de novo."]
S["c6_anubisius_done"] = ["A Chave está em boas mãos. As árvores aprovam."]
S["c6_atenza_pre"] = [
 "O caminho é íngreme e o meu preço também. Só os fortes levam o Bastão.",
 "Eu atravessei o tempo. Uma montanha não vai me parar.",
 "Então suba! Duelar?",
]
S["c6_atenza_win"] = [
 "Você chegou ao pico. O Bastão do Milênio é seu.",
 "Recompensa::Recebeu o Bastão do Milênio e a carta Thunder Dragon.",
]
S["c6_atenza_lose"] = ["A montanha é fria e eu também. Suba de novo."]
S["c6_atenza_done"] = ["Use o Bastão com sabedoria. Poder não é sabedoria."]
S["c6_martis_pre"] = [
 "A areia enterra quem tem pressa. Devagar, viajante do tempo.",
 "Devagar? Eu acabei de cruzar cinco mil anos.",
 "Então deixe as dunas julgarem você. Duelar?",
]
S["c6_martis_win"] = [
 "As dunas se curvam a você. Leve o Anel do Milênio.",
 "Recompensa::Recebeu o Anel do Milênio e a carta Mystical Sand.",
]
S["c6_martis_lose"] = ["A areia cobre as suas pegadas. Volte."]
S["c6_martis_done"] = ["Os homens do Heishin passaram aqui. Foram embora de mãos vazias."]
S["c6_kepura_pre"] = [
 "{Bem-vindo|Bem-vinda} à campina, viajante do tempo! As flores disseram que você vinha.",
 "Flores? ...Tá. Preciso da Balança do Milênio.",
 "Com calma ou com garra, um duelo decide. Duelar?",
]
S["c6_kepura_win"] = [
 "Que lindo! Você duela com bom coração. A Balança é sua.",
 "Recompensa::Recebeu a Balança do Milênio e a carta Queen of Autumn Leaves.",
]
S["c6_kepura_lose"] = ["Ai, ai. Descanse entre as flores e tente de novo."]
S["c6_kepura_done"] = ["Mantenha o coração em equilíbrio e a Balança faz o resto."]
S["c6_gate_locked"] = ["O portão tem cinco encaixes vazios. Preciso dos Itens dos cinco templos."]
S["side_cockatiel_pre"] = [
 "Piu-piu! {Bem-vindo|Bem-vinda}, viajante do tempo. Eu sou Calopsita, duelista andarilho.",
 "Belo topete. O seu passarinho morde?",
 "Só quem perde feio. O meu bando está ansioso por um duelo. {Pronto|Pronta}?",
]
S["side_cockatiel_win"] = [
 "Ha! Nada mal. O meu bando ficou impressionado.",
 "Fique com esta pena. Ela traz sorte a quem voa alto.",
 "Recompensa::Recebeu a Pena de Calopsita e a carta Crimson Sunbird.",
]
S["side_cockatiel_lose"] = ["Piu! Volte depois de comer uns grãos e treinar."]
S["side_cockatiel_done"] = ["Voe alto, viajante. O vento se lembra de você."]

# ---------------------------------------------------------------- chapter 7
S["c6_end__c7_intro"] = [
 "Tablete, Chave, Bastão, Anel e Balança... os encaixes estão brilhando!",
 "Fim do Capítulo 6::Capítulo 7 - O Labirinto e os Guardiões",
 "O portão abre para uma escada que desce no escuro. Vai com tudo.",
 "Cuidado! Senti Heishin passar por aqui. Seto foi na frente guardar o caminho.",
 "Objetivo::Cruze o Labirinto. Vença os guardiões para chegar ao altar.",
]
S["c7_lmage_pre"] = [
 "Um rosto novo no labirinto. Poucos voltam a sair daqui.",
 "Então eu serei um dos poucos.",
 "Aqui as paredes mudam. As chances também. Duelar?",
]
S["c7_lmage_win"] = [
 "Você leu bem o labirinto. Leve isto e siga em frente.",
 "Recompensa::Recebeu a carta Guardian of the Labyrinth.",
 "Objetivo::Siga até a primeira porta e enfrente o Guardian Sebek.",
]
S["c7_lmage_lose"] = ["Já se perdeu? O labirinto adora rostos novos."]
S["c7_lmage_done"] = ["Em frente, depois à esquerda. Ou à direita. Quem sabe?"]
S["c7_door1_locked"] = ["As paredes não param de se mexer. O Mago que as controla deve estar perto."]
S["c7_sebek_pre"] = [
 "Nenhuma alma viva passa por esta porta sem o julgamento dos deuses.",
 "Então me julgue.",
 "A balança está pronta. Duelar?",
]
S["c7_sebek_win"] = [
 "Os deuses acham você... aceitável. A porta está aberta.",
 "Recompensa::Recebeu a carta Guardian of the Throne Room.",
 "Objetivo::Próxima porta - Guardian Neku.",
]
S["c7_sebek_lose"] = ["Julgado e reprovado. Volte quando for {digno|digna}."]
S["c7_sebek_done"] = ["Vá. Neku espera na próxima porta."]
S["c7_door2_locked"] = ["Outra porta, mas o julgamento do Sebek vem primeiro."]
S["c7_neku_pre"] = [
 "Sou Neku, guardião da segunda porta. Sebek julga o corpo. Eu julgo o coração.",
 "O meu coração está bem. É o resto de mim que está cansado.",
 "Vamos ver. Duelar?",
]
S["c7_neku_win"] = [
 "Seu coração é firme. Pode passar, viajante.",
 "Recompensa::Recebeu a carta Rude Kaiser.",
 "Objetivo::Seto está além da segunda porta.",
]
S["c7_neku_lose"] = ["Seu coração vacila. Descanse e volte."]
S["c7_neku_done"] = ["Seto espera adiante. Não o faça esperar."]
S["c7_door3_locked"] = ["Esta porta não se move. Preciso vencer Neku primeiro."]
S["c7_seto2_pre"] = [
 "Você veio. Eu tinha as minhas dúvidas.",
 "Eu disse que ia encontrar os Itens.",
 "Eu sirvo o Príncipe, não você. Mas hoje lutamos do mesmo lado.",
 "Então por que duelar?",
 "O altar vai testar você. Não deixarei o Príncipe descansar em mãos não testadas. Duelar?",
]
S["c7_seto2_win"] = [
 "Chega. Eu errei em duvidar de você.",
 "Leve o White Dragon. Ele escolheu lutar ao seu lado.",
 "Recompensa::Recebeu a carta Blue-eyes White Dragon.",
 "Objetivo::Chegue ao altar e acorde o Príncipe.",
]
S["c7_seto2_lose"] = ["Ainda não. Volte mais forte."]
S["c7_seto2_done"] = ["O altar está logo ali. Eu guardo as suas costas."]
S["c7_altar_locked"] = ["Seto está na frente do altar. Ele ainda não vai me deixar passar."]
S["c7_altar_wake"] = [
 "Anel, Bastão, Chave, Balança, Colar, Olho... e o Enigma.",
 "O Altar::Os sete Itens brilham. A alma do Príncipe sai do Enigma.",
 "{name}... Seto... Ouvi tudo enquanto dormia. Obrigado.",
 "Meu Príncipe! Você está livre.",
 "Hahaha! Você fez o trabalho pesado por mim. Os sete Itens num só lugar!",
 "Heishin! Você nunca desiste.",
 "Eu não desisti de nada. Duele, se tiver coragem!",
]
S["c7_heishin2_retry"] = ["Voltou pra apanhar? Entregue os Itens!"]
S["c7_heishin2_win"] = [
 "Não... os Itens! A sombra me prometeu...",
 "A Sombra::Heishin some em fumaça negra. Algo mais profundo desperta lá embaixo.",
 "Esse poder não era do Heishin. Algo mais antigo acordou.",
 "Recompensa::Recebeu o Fragmento da Pedra Temporal 3 e a carta Summoned Skull.",
 "Objetivo::Desça a escada escura atrás do altar com o Príncipe.",
]
S["c7_heishin2_lose"] = ["Hahaha! Os Itens são meus!"]
S["c7_prince_free"] = ["Vamos. O que quer que espere lá embaixo, enfrentamos juntos."]
S["c7_seto2_after_altar"] = ["Heishin era só um peão. O verdadeiro inimigo está lá embaixo. Vá, eu sigo você."]

# ---------------------------------------------------------------- chapter 8
S["c7_end__c8_intro"] = [
 "Os Fragmentos e os Itens estão todos puxando para a escada escura.",
 "Fim do Capítulo 7::Capítulo 8 - Nitemare",
 "O Templo Final. Ele flutua no Reino das Sombras.",
 "Último duelo. Depois disso, eu vou pra casa.",
 "Objetivo::Chegue ao Templo Final e derrote Nitemare.",
]
S["c8_seto3_pre"] = [
 "Volte... A noite não perdoa.",
 "Seto! Quem está falando não é você.",
 "A sombra o prende. Quebre-a com um duelo, {name}!",
 "...Duelo.",
]
S["c8_seto3_win"] = [
 "Argh... o que eu fiz? Príncipe?",
 "Eu vi. DarkNite carrega o rancor de Heishin. Nitemare dorme lá em cima.",
 "Recompensa::Recebeu a carta Red-eyes B. Dragon.",
 "Objetivo::Vença DarkNite no salão das sombras.",
]
S["c8_seto3_lose"] = ["...Vá embora. Volte mais forte."]
S["c8_seto3_done"] = ["Siga em frente. Eu seguro a porta atrás de você."]
S["c8_hall_locked"] = ["Uma parede de névoa negra. Seto está no meu caminho."]
S["c8_darknite_pre"] = [
 "Os sete Itens me chamaram. Obrigado por trazê-los.",
 "{name}, eu duelo ao seu lado. Este mundo não é só meu.",
 "Vamos acabar com isso.",
 "Dois corações contra uma noite? Duelo!",
]
S["c8_darknite_win"] = [
 "Impossível... a escuridão não pode perder pra luz!",
 "Você me divertiu, DarkNite. Agora saia da frente.",
 "Recompensa::Recebeu a carta Zoa.",
 "Objetivo::Suba até o topo e enfrente Nitemare.",
]
S["c8_darknite_lose"] = ["Nada se perde no escuro. Nem você."]
S["c8_stairs_locked"] = ["A escada está selada por sombras. DarkNite a guarda."]
S["c8_nitemare_pre"] = [
 "Eu sou Nitemare. Eu já estava aqui antes do primeiro Item.",
 "Heishin era um fantoche. As fendas, os Itens... tudo isso era meu.",
 "Foi você que abriu as fendas? Você me tirou do meu tempo?",
 "Eu abri todas as portas. Feche a última você mesmo, se puder.",
 "Juntos, {name}! Ilumine o caminho pela noite!",
 "Último duelo. Depois eu vou pra casa.",
 "Venha, então. Duelo!",
]
S["c8_nitemare_win"] = [
 "Não... a luz dos sete Itens...",
 "A Pedra Temporal::Os três Fragmentos voam juntos e formam a Pedra Temporal completa.",
 "Recompensa::Recebeu a Pedra Temporal e a carta lendária Workers' Rights.",
 "Objetivo::Escolha como a sua jornada termina.",
]
S["c8_nitemare_lose"] = ["A escuridão leva tudo. Até a esperança."]
S["c8_choice"] = [
 "A Pedra pode te mandar pra casa, {name}. Ou você pode ficar ao nosso lado.",
 "Usar a Pedra Temporal para voltar pra casa?",
]
S["ending_home"] = [
 "Adeus, Seto. Adeus, Príncipe. Obrigad{o|a} por tudo.",
 "Leve esta carta de lembrança. Nós nunca vamos esquecer você.",
 "Recompensa::Recebeu a carta Mystical Elf de lembrança.",
 "Epílogo::A luz da Pedra leva {name} de volta à arena, um segundo depois de sair.",
 "...A mesma arena. A mesma plateia. E eu ainda tenho a carta do Príncipe.",
 "Fim::Valeu por jogar o MODO JORNADA.",
]
S["ending_stay"] = [
 "Acho que a minha história agora é aqui. Eu vou ficar.",
 "Então sirva ao meu lado, {sacerdote|sacerdotisa}. O Príncipe vai precisar de você.",
 "Bem-vind{o|a} ao lar, {name}. O Egito também é o seu tempo.",
 "Epílogo::{name} virou {sacerdote|sacerdotisa} da Cidade Real e guardou a Pedra Temporal para sempre.",
 "Fim::Valeu por jogar o MODO JORNADA.",
]

# ---------------------------------------------------------------- post-game
S["side_cockatiel_epilogue"] = ["Ouvi o que você fez lá fora. O bando inteiro está cantando sobre isso."]
S["side_mirror_pre"] = [
 "Peraí... esse é o meu rosto! E isso parece o meu deck!",
 "Eu sou o Atos que ficou em casa. A fenda puxou o errado, ou talvez o certo.",
 "Então vamos ver qual de nós é o melhor duelista.",
 "Por mim tudo bem. O meu deck faz hora extra. Duelar?",
]
S["side_mirror_win"] = [
 "Nada mal... você trabalha mais que eu.",
 "Recompensa::Recebeu a carta Hero of the East.",
]
S["side_mirror_lose"] = ["Hora extra compensa. Tente de novo."]
S["side_mirror_done"] = ["Vá em frente. Eu mantenho a arena aquecida."]

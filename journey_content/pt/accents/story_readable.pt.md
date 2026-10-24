# JOURNEY MODE - story script (pt, generated from story.pt.json)


## Capitulo 1


### c1_intro

- **{name}**: Ai... minha cabeça... Eu estava num torneio de Duel Monsters agora mesmo.
- **{name}**: Um portal de luz se abriu no meio da arena e me puxou para dentro.
- **{name}**: Areia, palmeiras, um rio... Isso parece o Egito antigo!
- **{name}**: Só o meu deck veio comigo. Preciso achar alguém que saiba como voltar pra casa.
- **Objetivo**: Fale com Simon Muran, o velho sábio que espera na arena dourada.

### c1_simon_pre

- **Simon Muran**: Roupas estranhas, {rapaz|moça}... Mas essas cartas são tão antigas quanto a nossa magia.
- **{name}**: Eu caí de um portal. Você sabe como eu volto pra minha época?
- **Simon Muran**: Talvez. Mostre como você duela e eu direi de onde veio. Duelar?  _[ask]_

### c1_simon_win

- **Simon Muran**: Impressionante! Você duela como {um mestre|uma mestra}.
- **Simon Muran**: O portal que te trouxe é uma fenda no tempo. Só a Pedra Temporal pode fechá-la.
- **Simon Muran**: Os pedaços da Pedra estão além do rio, ao norte. Já avisei o guarda da ponte.
- **Recompensa**: Recebeu a carta Mystical Elf e um Cantil. Veja na Mochila.
- **Objetivo**: Cruze o rio ao norte. Teana e Jono também querem duelar com você.

### c1_simon_lose

- **Simon Muran**: Nada mal, mas ainda falta prática. Descanse e tente de novo.

### c1_simon_after

- **Simon Muran**: A ponte fica ao norte, subindo a estrada. Boa sorte, viajante.

### c1_teana_pre

- **Teana**: Oi! Você é {o|a} {estrangeiro|estrangeira} que venceu o Simon? Duela comigo?  _[ask]_

### c1_teana_win

- **Teana**: Uau, você é {bom|boa} mesmo! Fica com esta carta.
- **Recompensa**: Recebeu a carta Feral Imp.

### c1_jono_pre

- **Jono**: Ei, {novato|novata}! Aposto que o meu deck é mais forte. Duelar?  _[ask]_

### c1_jono_win

- **Jono**: Tá bom, tá bom... você ganhou. Toma, é sua.
- **Recompensa**: Recebeu a carta Baby Dragon.

### c1_teana_lose

- **Teana**: Hehe, ganhei! Volte quando quiser.

### c1_jono_lose

- **Jono**: Ha! Treina mais um pouco e volta aqui.

### c1_teana_wait

- **Teana**: O velho Simon está te esperando na arena.

### c1_jono_wait

- **Jono**: Fala com o Simon primeiro, depois a gente duela.

### c1_guard_block

- **Guarda**: Alto! Ninguém atravessa o rio sem a permissão do sábio Simon Muran.

### c1_guard_ok

- **Guarda**: O Simon deixou? Então pode passar, viajante.

## Capitulo 2


### c1_end__c2_intro

- **{name}**: A Cidade Real fica lá no norte. Primeiro preciso passar por essas ruínas.
- **Fim do Capítulo 1**: Capítulo 2 - Ruínas de Areia
- **{name}**: Colunas quebradas, um obelisco... e lá no fundo, um portal de pedra brilhando!
- **{name}**: Tem mais gente aqui. Aqueles dois são do torneio! Será que eles também caíram no passado?
- **Objetivo**: Vença Rex Raptor e Weevil. Depois entre no portal de pedra ao norte.

### c2_teana_done

- **Teana**: Boa viagem, {estrangeiro|estrangeira}!

### c2_jono_done

- **Jono**: Da próxima vez eu ganho!

### c2_rex_pre

- **Rex Raptor**: Você também caiu aqui? Ótimo. Ganhar de você me deixa mais perto de voltar pra casa.
- **{name}**: Então vamos duelar. Quem ganhar fica com o caminho livre.
- **Rex Raptor**: Meus dinossauros vão te esmagar! Duelar?  _[ask]_

### c2_rex_win

- **Rex Raptor**: Não acredito... perdi para {um|uma} {novato|novata}!
- **Rex Raptor**: Toma, achei esta pedra brilhante nas ruínas. Talvez sirva pra você.
- **Recompensa**: Recebeu o Fragmento da Pedra Temporal 1 e a carta Ryu-kishin.

### c2_rex_lose

- **Rex Raptor**: Hahaha! Volte quando tiver dinossauros de verdade.

### c2_weevil_pre

- **Weevil**: Hehehe. Nesse mundo ninguém confere se a gente trapaceia.
- **{name}**: Então eu vou ganhar do jeito certo, pra você lembrar.
- **Weevil**: Meus insetos discordam. Duelar?  _[ask]_

### c2_weevil_win

- **Weevil**: Impossível! Minha estratégia era perfeita!
- **Weevil**: Tá, tá... leva esta tocha velha e me deixa em paz.
- **Recompensa**: Recebeu uma Tocha e a carta Hitotsu-me Giant.

### c2_weevil_lose

- **Weevil**: Hehehe! Eu sabia que você cairia na minha armadilha.

### c2_rex_done

- **Rex Raptor**: Vai logo pro portal. Eu ainda vou ter a minha revanche.

### c2_weevil_done

- **Weevil**: Hmpf. Some daqui antes que eu mude de ideia.

### c2_portal_locked

- **{name}**: O portal não reage. Acho que preciso vencer Rex e Weevil primeiro.

## Capitulo 3


### c2_end__c3_intro

- **{name}**: O portal está brilhando mais forte agora. Vou entrar!
- **Fim do Capítulo 2**: Capítulo 3 - O Palácio e o Príncipe
- **{name}**: Uau! O portal me levou para dentro da Cidade Real. Que palácio enorme!
- **{name}**: Na frente do palácio tem um sacerdote e um jovem que parece um rei. É o Príncipe!
- **Objetivo**: Fale com o sacerdote Seto, na frente do palácio.

### c3_seto_pre

- **Seto**: {Um|Uma} {estrangeiro|estrangeira} com cartas que ninguém conhece. Ameaça ou presente?
- **Príncipe**: Seto, deixe {ele|ela} provar. Se {ele|ela} perder, eu mesmo mando embora.
- **{name}**: Se eu ganhar, quero saber por que essas fendas no tempo estão se abrindo.
- **Seto**: Combinado. Prepare o seu deck. Duelar?  _[ask]_

### c3_seto_win

- **Seto**: Hmpf... você venceu. Se o Príncipe confia em você, eu também vou confiar.
- **Príncipe**: As fendas começaram quando o sacerdote Heishin abriu o cofre dos Itens do Milênio.
- **Príncipe**: Leve o Selo Real. Com ele você entra no palácio e descobre o que Heishin quer.
- **Recompensa**: Recebeu o Selo Real e a carta Dark Magician.
- **Objetivo**: Entre no palácio e investigue Heishin. O Mage Soldier também quer duelar.

### c3_seto_lose

- **Seto**: Era isso? Volte quando estiver {pronto|pronta}, {estrangeiro|estrangeira}.

### c3_seto_done

- **Seto**: O palácio está aberto para você. Não me decepcione.

### c3_prince_before

- **Príncipe**: {Bem-vindo|Bem-vinda} à Cidade Real, viajante. Mostre ao Seto o que você sabe fazer.

### c3_prince_after

- **Príncipe**: Cuidado com Heishin. Ele anda pelos corredores do palácio à noite.

### c3_soldier_pre

- **Mage Soldier**: Eu treino os guardas do palácio. Quer testar o seu deck contra mim? Duelar?  _[ask]_

### c3_soldier_win

- **Mage Soldier**: Bom duelo! Leve esta carta na sua jornada.
- **Recompensa**: Recebeu a carta Celtic Guardian.

### c3_soldier_lose

- **Mage Soldier**: Treine mais um pouco e volte aqui.

### c3_soldier_done

- **Mage Soldier**: Os guardas falam muito bem de você.

### c3_door_locked

- **{name}**: A porta do palácio está fechada. Preciso da permissão do Seto primeiro.

## Capitulo 4


### c3_end__c4_intro

- **{name}**: Com o Selo Real a porta se abriu. Heishin esconde alguma coisa aqui dentro.
- **Fim do Capítulo 3**: Capítulo 4 - O Golpe de Heishin
- **Naquela noite**: Heishin atacou a cidade com os seus guardas. O céu ficou vermelho de fogo.
- **{name}**: Este é o salão do trono! Heishin está lá no alto e o Príncipe está cercado!
- **Objetivo**: Derrote Heishin no salão do trono.

### c4_heishin_pre

- **Heishin**: Os Itens do Milênio dão poder a quem tem coragem de pegá-los. E eu tive coragem.
- **{name}**: Você atacou a cidade inteira por sete pedaços de ouro?
- **Heishin**: Por sete chaves. E agora você vai me entregar o seu deck. Duelar?  _[ask]_

### c4_heishin_win

- **Heishin**: Impossível! {Um|Uma} {estrangeiro|estrangeira} me venceu? Isso ainda não acabou!
- **O que aconteceu**: Heishin fugiu pela janela e levou os Itens do Milênio com ele.
- **Simon Muran**: {name}! Heishin vai voltar atrás do Príncipe. Só existe um jeito de protegê-lo.
- **Simon Muran**: Vou guardar a alma do Príncipe dentro do Enigma do Milênio. Ele dorme até a hora certa.
- **Príncipe**: {name}, eu confio em você. Encontre os Itens e me acorde quando chegar a hora.
- **Simon Muran**: Leve o Colar do Milênio. Ele mostra o futuro e pode abrir uma fenda até o seu tempo.
- **Recompensa**: Recebeu o Colar do Milênio e a carta Gaia the Fierce Knight.
- **Objetivo**: Toque o trono brilhante para viajar no tempo.

### c4_heishin_lose

- **Heishin**: Hahaha! {Fraco|Fraca} demais. Volte quando tiver coragem de verdade.

### c4_prince_hall

- **Príncipe**: {name}! Heishin quer os Itens do Milênio. Por favor, detenha ele!

### c4_seto_before

- **Seto**: Eu protejo o Príncipe. Vá, {estrangeiro|estrangeira}, enfrente Heishin!

### c4_seto_after

- **Seto**: O Príncipe está guardado no Enigma. Encontre os Itens e traga ele de volta.

### c4_throne_locked

- **{name}**: O trono não está brilhando. Primeiro preciso derrotar Heishin.

## Capitulo 5


### c4_end__c5_intro

- **{name}**: O Colar está brilhando junto com o trono. Uma fenda no tempo está se abrindo!
- **Fim do Capítulo 4**: Capítulo 5 - O Torneio Fora do Tempo
- **{name}**: Espera... esta é a ilha do torneio do Pegasus! Será que eu voltei pro meu tempo?
- **{name}**: Não... o céu ainda tem fendas. O torneio ficou preso entre duas épocas.
- **Objetivo**: Vença Mai, Bandit Keith e Shadi. Depois enfrente Pegasus na frente do castelo.

### c5_mai_pre

- **Mai**: Gracinha, aqui o que vale é estratégia. E um pouco de perfume.
- **{name}**: Então vamos ver qual estratégia é melhor.
- **Mai**: Minhas Harpias estão prontas. Duelar?  _[ask]_

### c5_mai_win

- **Mai**: Nada mal, gracinha. Você ganhou na moral.
- **Recompensa**: Recebeu a carta Harpie Lady.

### c5_mai_lose

- **Mai**: Hihi, volte quando aprender a jogar.

### c5_mai_done

- **Mai**: Boa sorte com o Pegasus. Ele é muito esquisito.

### c5_keith_pre

- **Bandit Keith**: Esse torneio é meu. Você é só mais um nome na minha lista.
- **{name}**: Então tente riscar o meu nome, se conseguir.
- **Bandit Keith**: Vamos ver, {novato|novata}. Duelar?  _[ask]_

### c5_keith_win

- **Bandit Keith**: Grr... sorte de principiante!
- **Recompensa**: Recebeu a carta Great White.

### c5_keith_lose

- **Bandit Keith**: Hah! Volta pra casa, {novato|novata}.

### c5_keith_done

- **Bandit Keith**: Não fala comigo agora, {novato|novata}.

### c5_shadi_pre

- **Shadi**: Eu sou Shadi, guardião dos Itens do Milênio. Vejo que você carrega o Colar.
- **Shadi**: Mostre que o seu coração é digno dele. Duelar?  _[ask]_

### c5_shadi_win

- **Shadi**: Seu coração é puro. Tome este pedaço da Pedra Temporal.
- **Recompensa**: Recebeu o Fragmento da Pedra Temporal 2 e a carta Illusionist Faceless Mage.

### c5_shadi_lose

- **Shadi**: Seu coração ainda tem dúvidas. Volte depois.

### c5_shadi_done

- **Shadi**: Pegasus tem o Olho do Milênio. Tenha cuidado com ele.

### c5_pegasus_locked

- **Pegasus**: Olá, {name}-{menino|menina}! Primeiro vença os outros três duelistas. Depois eu duelo com você.

### c5_pegasus_pre

- **Pegasus**: O seu destino eu já li, {name}-{menino|menina}. Que tal descobrir se estou certo?
- **{name}**: Ninguém lê o meu destino. Eu escrevo ele no duelo!
- **Pegasus**: Que divertido! Duelar?  _[ask]_

### c5_pegasus_win

- **Pegasus**: Impossível! O Olho do Milênio não conseguiu ler a sua mente!
- **Pegasus**: Fique com o Olho. Talvez ele ajude você a salvar o Príncipe.
- **Isis**: Eu sou Isis. Eu vi você numa visão. Vou abrir um portal de volta ao Egito.
- **Isis**: Os Magos dos Templos guardam os outros Itens. O Príncipe precisa deles.
- **Recompensa**: Recebeu o Olho do Milênio e a carta Thousand Dragon.
- **Objetivo**: Entre no portal do castelo para voltar ao Egito.

### c5_pegasus_lose

- **Pegasus**: Hahaha! Eu disse que já tinha lido o seu destino.

### c5_pegasus_done

- **Pegasus**: O portal da Isis está aberto no castelo. Adeus, {name}-{menino|menina}!

### c5_gate_locked

- **{name}**: O portão do castelo está fechado. Primeiro preciso vencer Pegasus.

## Capitulo 6


### c5_end__c6_intro

- **{name}**: O portal da Isis está aberto. Hora de voltar pro Egito!
- **Fim do Capítulo 5**: Capítulo 6 - Os Sete Itens

### c6_arrival

- **{name}**: Areia quente de novo! O portal me largou num velho cruzamento.
- **Simon Muran**: {name}! A Isis avisou que você vinha. Guardei o Enigma em segurança.
- **Recompensa**: Recebeu o Enigma do Milênio. O Príncipe dorme dentro dele.
- **Simon Muran**: Heishin só esvaziou o cofre. Os Itens de verdade estavam escondidos em cinco templos.
- **Simon Muran**: Cada templo tem um Mago que guarda um Item. Vença os Magos e eles deixam você levar.
- **{name}**: Mar, floresta, montanha, deserto e campina. Entendi. Bora lá.
- **Objetivo**: Visite os cinco templos e ganhe os Itens. Depois abra o portão do Labirinto.

### c6_simon_hub

- **Simon Muran**: Vi os homens do Heishin perto dos templos. Corra, mas não apresse os seus duelos.

### c6_simon_hub_done

- **Simon Muran**: Você tem os cinco Itens! Vá ao portão do Labirinto. Eu guardo o cruzamento.

### c6_ocean_pre

- **Ocean Mage**: Alto, {estrangeiro|estrangeira}! O mar não abre o templo para visitantes de pé seco.
- **{name}**: Só quero pegar emprestado o que o templo guarda. Duele comigo.
- **Ocean Mage**: A maré vai decidir. Duelar?  _[ask]_

### c6_ocean_win

- **Ocean Mage**: A maré virou... Pode entrar. O High Mage Secmeton espera lá dentro.
- **Recompensa**: Recebeu a carta Aqua Dragon.
- **Objetivo**: Entre no Templo do Mar e enfrente o High Mage Secmeton.

### c6_ocean_lose

- **Ocean Mage**: O mar te jogou de volta pra praia. Tente de novo.

### c6_ocean_done

- **Ocean Mage**: Secmeton espera lá dentro. O mar deixa você passar.

### c6_secmeton_locked

- **{name}**: Uma parede de água bloqueia a porta de dentro. O Ocean Mage precisa me deixar entrar.

### c6_secmeton_pre

- **High Mage Secmeton**: Então é você quem caminha pelo tempo. As águas sussurraram sobre você.
- **{name}**: Então você sabe por que vim. Preciso do Tablete do Mar.
- **High Mage Secmeton**: Palavras são rasas. Mostre com cartas. Duelar?  _[ask]_

### c6_secmeton_win

- **High Mage Secmeton**: Você nada bem, viajante. O Tablete do Mar é seu.
- **High Mage Secmeton**: Ele serve no portão do Labirinto. Os homens do Heishin o querem muito.
- **Recompensa**: Recebeu o Tablete do Mar e a carta Suijin.
- **Objetivo**: Faltam quatro templos - Floresta, Montanha, Deserto e Campina.

### c6_secmeton_lose

- **High Mage Secmeton**: Raso demais. Mergulhe mais fundo e volte.

### c6_secmeton_done

- **High Mage Secmeton**: Guarde bem o Tablete. O mar tem memória.

### c6_anubisius_pre

- **High Mage Anubisius**: Silêncio, {estrangeiro|estrangeira}. As árvores antigas não gostam de barulho.
- **{name}**: Vim buscar a Chave do Milênio. A vida do Príncipe está em jogo.
- **High Mage Anubisius**: A floresta não dá nada de graça. Duelar?  _[ask]_

### c6_anubisius_win

- **High Mage Anubisius**: As raízes se curvam a você. Leve a Chave do Milênio.
- **Recompensa**: Recebeu a Chave do Milênio e a carta Ancient One of the Deep Forest.

### c6_anubisius_lose

- **High Mage Anubisius**: A floresta engoliu as suas cartas. Tente de novo.

### c6_anubisius_done

- **High Mage Anubisius**: A Chave está em boas mãos. As árvores aprovam.

### c6_atenza_pre

- **High Mage Atenza**: O caminho é íngreme e o meu preço também. Só os fortes levam o Bastão.
- **{name}**: Eu atravessei o tempo. Uma montanha não vai me parar.
- **High Mage Atenza**: Então suba! Duelar?  _[ask]_

### c6_atenza_win

- **High Mage Atenza**: Você chegou ao pico. O Bastão do Milênio é seu.
- **Recompensa**: Recebeu o Bastão do Milênio e a carta Thunder Dragon.

### c6_atenza_lose

- **High Mage Atenza**: A montanha é fria e eu também. Suba de novo.

### c6_atenza_done

- **High Mage Atenza**: Use o Bastão com sabedoria. Poder não é sabedoria.

### c6_martis_pre

- **High Mage Martis**: A areia enterra quem tem pressa. Devagar, viajante do tempo.
- **{name}**: Devagar? Eu acabei de cruzar cinco mil anos.
- **High Mage Martis**: Então deixe as dunas julgarem você. Duelar?  _[ask]_

### c6_martis_win

- **High Mage Martis**: As dunas se curvam a você. Leve o Anel do Milênio.
- **Recompensa**: Recebeu o Anel do Milênio e a carta Mystical Sand.

### c6_martis_lose

- **High Mage Martis**: A areia cobre as suas pegadas. Volte.

### c6_martis_done

- **High Mage Martis**: Os homens do Heishin passaram aqui. Foram embora de mãos vazias.

### c6_kepura_pre

- **High Mage Kepura**: {Bem-vindo|Bem-vinda} à campina, viajante do tempo! As flores disseram que você vinha.
- **{name}**: Flores? ...Tá. Preciso da Balança do Milênio.
- **High Mage Kepura**: Com calma ou com garra, um duelo decide. Duelar?  _[ask]_

### c6_kepura_win

- **High Mage Kepura**: Que lindo! Você duela com bom coração. A Balança é sua.
- **Recompensa**: Recebeu a Balança do Milênio e a carta Queen of Autumn Leaves.

### c6_kepura_lose

- **High Mage Kepura**: Ai, ai. Descanse entre as flores e tente de novo.

### c6_kepura_done

- **High Mage Kepura**: Mantenha o coração em equilíbrio e a Balança faz o resto.

### c6_gate_locked

- **{name}**: O portão tem cinco encaixes vazios. Preciso dos Itens dos cinco templos.

### side_cockatiel_pre

- **Cockatiel**: Piu-piu! {Bem-vindo|Bem-vinda}, viajante do tempo. Eu sou Calopsita, duelista andarilho.
- **{name}**: Belo topete. O seu passarinho morde?
- **Cockatiel**: Só quem perde feio. O meu bando está ansioso por um duelo. {Pronto|Pronta}?  _[ask]_

### side_cockatiel_win

- **Cockatiel**: Ha! Nada mal. O meu bando ficou impressionado.
- **Cockatiel**: Fique com esta pena. Ela traz sorte a quem voa alto.
- **Recompensa**: Recebeu a Pena de Calopsita e a carta Crimson Sunbird.

### side_cockatiel_lose

- **Cockatiel**: Piu! Volte depois de comer uns grãos e treinar.

### side_cockatiel_done

- **Cockatiel**: Voe alto, viajante. O vento se lembra de você.

## Capitulo 7


### c6_end__c7_intro

- **{name}**: Tablete, Chave, Bastão, Anel e Balança... os encaixes estão brilhando!
- **Fim do Capítulo 6**: Capítulo 7 - O Labirinto e os Guardiões
- **{name}**: O portão abre para uma escada que desce no escuro. Vai com tudo.
- **Simon Muran**: Cuidado! Senti Heishin passar por aqui. Seto foi na frente guardar o caminho.
- **Objetivo**: Cruze o Labirinto. Vença os guardiões para chegar ao altar.

### c7_lmage_pre

- **Labyrinth Mage**: Um rosto novo no labirinto. Poucos voltam a sair daqui.
- **{name}**: Então eu serei um dos poucos.
- **Labyrinth Mage**: Aqui as paredes mudam. As chances também. Duelar?  _[ask]_

### c7_lmage_win

- **Labyrinth Mage**: Você leu bem o labirinto. Leve isto e siga em frente.
- **Recompensa**: Recebeu a carta Guardian of the Labyrinth.
- **Objetivo**: Siga até a primeira porta e enfrente o Guardian Sebek.

### c7_lmage_lose

- **Labyrinth Mage**: Já se perdeu? O labirinto adora rostos novos.

### c7_lmage_done

- **Labyrinth Mage**: Em frente, depois à esquerda. Ou à direita. Quem sabe?

### c7_door1_locked

- **{name}**: As paredes não param de se mexer. O Mago que as controla deve estar perto.

### c7_sebek_pre

- **Guardian Sebek**: Nenhuma alma viva passa por esta porta sem o julgamento dos deuses.
- **{name}**: Então me julgue.
- **Guardian Sebek**: A balança está pronta. Duelar?  _[ask]_

### c7_sebek_win

- **Guardian Sebek**: Os deuses acham você... aceitável. A porta está aberta.
- **Recompensa**: Recebeu a carta Guardian of the Throne Room.
- **Objetivo**: Próxima porta - Guardian Neku.

### c7_sebek_lose

- **Guardian Sebek**: Julgado e reprovado. Volte quando for {digno|digna}.

### c7_sebek_done

- **Guardian Sebek**: Vá. Neku espera na próxima porta.

### c7_door2_locked

- **{name}**: Outra porta, mas o julgamento do Sebek vem primeiro.

### c7_neku_pre

- **Guardian Neku**: Sou Neku, guardião da segunda porta. Sebek julga o corpo. Eu julgo o coração.
- **{name}**: O meu coração está bem. É o resto de mim que está cansado.
- **Guardian Neku**: Vamos ver. Duelar?  _[ask]_

### c7_neku_win

- **Guardian Neku**: Seu coração é firme. Pode passar, viajante.
- **Recompensa**: Recebeu a carta Rude Kaiser.
- **Objetivo**: Seto está além da segunda porta.

### c7_neku_lose

- **Guardian Neku**: Seu coração vacila. Descanse e volte.

### c7_neku_done

- **Guardian Neku**: Seto espera adiante. Não o faça esperar.

### c7_door3_locked

- **{name}**: Esta porta não se move. Preciso vencer Neku primeiro.

### c7_seto2_pre

- **Seto**: Você veio. Eu tinha as minhas dúvidas.
- **{name}**: Eu disse que ia encontrar os Itens.
- **Seto**: Eu sirvo o Príncipe, não você. Mas hoje lutamos do mesmo lado.
- **{name}**: Então por que duelar?
- **Seto**: O altar vai testar você. Não deixarei o Príncipe descansar em mãos não testadas. Duelar?  _[ask]_

### c7_seto2_win

- **Seto**: Chega. Eu errei em duvidar de você.
- **Seto**: Leve o White Dragon. Ele escolheu lutar ao seu lado.
- **Recompensa**: Recebeu a carta Blue-eyes White Dragon.
- **Objetivo**: Chegue ao altar e acorde o Príncipe.

### c7_seto2_lose

- **Seto**: Ainda não. Volte mais forte.

### c7_seto2_done

- **Seto**: O altar está logo ali. Eu guardo as suas costas.

### c7_altar_locked

- **{name}**: Seto está na frente do altar. Ele ainda não vai me deixar passar.

### c7_altar_wake

- **{name}**: Anel, Bastão, Chave, Balança, Colar, Olho... e o Enigma.
- **O Altar**: Os sete Itens brilham. A alma do Príncipe sai do Enigma.
- **Príncipe**: {name}... Seto... Ouvi tudo enquanto dormia. Obrigado.
- **Seto**: Meu Príncipe! Você está livre.
- **Heishin**: Hahaha! Você fez o trabalho pesado por mim. Os sete Itens num só lugar!
- **{name}**: Heishin! Você nunca desiste.
- **Heishin**: Eu não desisti de nada. Duele, se tiver coragem!  _[ask]_

### c7_heishin2_retry

- **Heishin**: Voltou pra apanhar? Entregue os Itens!  _[ask]_

### c7_heishin2_win

- **Heishin**: Não... os Itens! A sombra me prometeu...
- **A Sombra**: Heishin some em fumaça negra. Algo mais profundo desperta lá embaixo.
- **Príncipe**: Esse poder não era do Heishin. Algo mais antigo acordou.
- **Recompensa**: Recebeu o Fragmento da Pedra Temporal 3 e a carta Summoned Skull.
- **Objetivo**: Desça a escada escura atrás do altar com o Príncipe.

### c7_heishin2_lose

- **Heishin**: Hahaha! Os Itens são meus!

### c7_prince_free

- **Príncipe**: Vamos. O que quer que espere lá embaixo, enfrentamos juntos.

### c7_seto2_after_altar

- **Seto**: Heishin era só um peão. O verdadeiro inimigo está lá embaixo. Vá, eu sigo você.

## Capitulo 8


### c7_end__c8_intro

- **{name}**: Os Fragmentos e os Itens estão todos puxando para a escada escura.
- **Fim do Capítulo 7**: Capítulo 8 - Nitemare
- **Príncipe**: O Templo Final. Ele flutua no Reino das Sombras.
- **{name}**: Último duelo. Depois disso, eu vou pra casa.
- **Objetivo**: Chegue ao Templo Final e derrote Nitemare.

### c8_seto3_pre

- **Seto**: Volte... A noite não perdoa.
- **{name}**: Seto! Quem está falando não é você.
- **Príncipe**: A sombra o prende. Quebre-a com um duelo, {name}!
- **Seto**: ...Duelo.  _[ask]_

### c8_seto3_win

- **Seto**: Argh... o que eu fiz? Príncipe?
- **Seto**: Eu vi. DarkNite carrega o rancor de Heishin. Nitemare dorme lá em cima.
- **Recompensa**: Recebeu a carta Red-eyes B. Dragon.
- **Objetivo**: Vença DarkNite no salão das sombras.

### c8_seto3_lose

- **Seto**: ...Vá embora. Volte mais forte.

### c8_seto3_done

- **Seto**: Siga em frente. Eu seguro a porta atrás de você.

### c8_hall_locked

- **{name}**: Uma parede de névoa negra. Seto está no meu caminho.

### c8_darknite_pre

- **DarkNite**: Os sete Itens me chamaram. Obrigado por trazê-los.
- **Príncipe**: {name}, eu duelo ao seu lado. Este mundo não é só meu.
- **{name}**: Vamos acabar com isso.
- **DarkNite**: Dois corações contra uma noite? Duelo!  _[ask]_

### c8_darknite_win

- **DarkNite**: Impossível... a escuridão não pode perder pra luz!
- **Nitemare**: Você me divertiu, DarkNite. Agora saia da frente.
- **Recompensa**: Recebeu a carta Zoa.
- **Objetivo**: Suba até o topo e enfrente Nitemare.

### c8_darknite_lose

- **DarkNite**: Nada se perde no escuro. Nem você.

### c8_stairs_locked

- **{name}**: A escada está selada por sombras. DarkNite a guarda.

### c8_nitemare_pre

- **Nitemare**: Eu sou Nitemare. Eu já estava aqui antes do primeiro Item.
- **Nitemare**: Heishin era um fantoche. As fendas, os Itens... tudo isso era meu.
- **{name}**: Foi você que abriu as fendas? Você me tirou do meu tempo?
- **Nitemare**: Eu abri todas as portas. Feche a última você mesmo, se puder.
- **Príncipe**: Juntos, {name}! Ilumine o caminho pela noite!
- **{name}**: Último duelo. Depois eu vou pra casa.
- **Nitemare**: Venha, então. Duelo!  _[ask]_

### c8_nitemare_win

- **Nitemare**: Não... a luz dos sete Itens...
- **A Pedra Temporal**: Os três Fragmentos voam juntos e formam a Pedra Temporal completa.
- **Recompensa**: Recebeu a Pedra Temporal e a carta lendária Workers' Rights.
- **Objetivo**: Escolha como a sua jornada termina.

### c8_nitemare_lose

- **Nitemare**: A escuridão leva tudo. Até a esperança.

### c8_choice

- **Príncipe**: A Pedra pode te mandar pra casa, {name}. Ou você pode ficar ao nosso lado.
- **{name}**: Usar a Pedra Temporal para voltar pra casa?  _[ask]_

### ending_home

- **{name}**: Adeus, Seto. Adeus, Príncipe. Obrigad{o|a} por tudo.
- **Príncipe**: Leve esta carta de lembrança. Nós nunca vamos esquecer você.
- **Recompensa**: Recebeu a carta Mystical Elf de lembrança.
- **Epílogo**: A luz da Pedra leva {name} de volta à arena, um segundo depois de sair.
- **{name}**: ...A mesma arena. A mesma plateia. E eu ainda tenho a carta do Príncipe.
- **Fim**: Valeu por jogar o MODO JORNADA.

### ending_stay

- **{name}**: Acho que a minha história agora é aqui. Eu vou ficar.
- **Seto**: Então sirva ao meu lado, {sacerdote|sacerdotisa}. O Príncipe vai precisar de você.
- **Príncipe**: Bem-vind{o|a} ao lar, {name}. O Egito também é o seu tempo.
- **Epílogo**: {name} virou {sacerdote|sacerdotisa} da Cidade Real e guardou a Pedra Temporal para sempre.
- **Fim**: Valeu por jogar o MODO JORNADA.

## Pos-jogo


### side_cockatiel_epilogue

- **Cockatiel**: Ouvi o que você fez lá fora. O bando inteiro está cantando sobre isso.

### side_mirror_pre

- **{name}**: Peraí... esse é o meu rosto! E isso parece o meu deck!
- **Atos Vinicius**: Eu sou o Atos que ficou em casa. A fenda puxou o errado, ou talvez o certo.
- **{name}**: Então vamos ver qual de nós é o melhor duelista.
- **Atos Vinicius**: Por mim tudo bem. O meu deck faz hora extra. Duelar?  _[ask]_

### side_mirror_win

- **Atos Vinicius**: Nada mal... você trabalha mais que eu.
- **Recompensa**: Recebeu a carta Hero of the East.

### side_mirror_lose

- **Atos Vinicius**: Hora extra compensa. Tente de novo.

### side_mirror_done

- **Atos Vinicius**: Vá em frente. Eu mantenho a arena aquecida.

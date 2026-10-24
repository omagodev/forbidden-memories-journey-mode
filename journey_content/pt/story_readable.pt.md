# JOURNEY MODE - story script (pt, generated from story.pt.json)


## Capitulo 1


### c1_intro

- **{name}**: Ai... minha cabeca... Eu estava num torneio de Duel Monsters agora mesmo.
- **{name}**: Um portal de luz se abriu no meio da arena e me puxou para dentro.
- **{name}**: Areia, palmeiras, um rio... Isso parece o Egito antigo!
- **{name}**: So o meu deck veio comigo. Preciso achar alguem que saiba como voltar pra casa.
- **Objetivo**: Fale com Simon Muran, o velho sabio que espera na arena dourada.

### c1_simon_pre

- **Simon Muran**: Roupas estranhas, {rapaz|moca}... Mas essas cartas sao tao antigas quanto a nossa magia.
- **{name}**: Eu cai de um portal. Voce sabe como eu volto pra minha epoca?
- **Simon Muran**: Talvez. Mostre como voce duela e eu direi de onde veio. Duelar?  _[ask]_

### c1_simon_win

- **Simon Muran**: Impressionante! Voce duela como {um mestre|uma mestra}.
- **Simon Muran**: O portal que te trouxe e uma fenda no tempo. So a Pedra Temporal pode fecha-la.
- **Simon Muran**: Os pedacos da Pedra estao alem do rio, ao norte. Ja avisei o guarda da ponte.
- **Recompensa**: Recebeu a carta Mystical Elf e um Cantil. Veja na Mochila.
- **Objetivo**: Cruze o rio ao norte. Teana e Jono tambem querem duelar com voce.

### c1_simon_lose

- **Simon Muran**: Nada mal, mas ainda falta pratica. Descanse e tente de novo.

### c1_simon_after

- **Simon Muran**: A ponte fica ao norte, subindo a estrada. Boa sorte, viajante.

### c1_teana_pre

- **Teana**: Oi! Voce e {o|a} {estrangeiro|estrangeira} que venceu o Simon? Duela comigo?  _[ask]_

### c1_teana_win

- **Teana**: Uau, voce e {bom|boa} mesmo! Fica com esta carta.
- **Recompensa**: Recebeu a carta Feral Imp.

### c1_jono_pre

- **Jono**: Ei, {novato|novata}! Aposto que o meu deck e mais forte. Duelar?  _[ask]_

### c1_jono_win

- **Jono**: Ta bom, ta bom... voce ganhou. Toma, e sua.
- **Recompensa**: Recebeu a carta Baby Dragon.

### c1_teana_lose

- **Teana**: Hehe, ganhei! Volte quando quiser.

### c1_jono_lose

- **Jono**: Ha! Treina mais um pouco e volta aqui.

### c1_teana_wait

- **Teana**: O velho Simon esta te esperando na arena.

### c1_jono_wait

- **Jono**: Fala com o Simon primeiro, depois a gente duela.

### c1_guard_block

- **Guarda**: Alto! Ninguem atravessa o rio sem a permissao do sabio Simon Muran.

### c1_guard_ok

- **Guarda**: O Simon deixou? Entao pode passar, viajante.

## Capitulo 2


### c1_end__c2_intro

- **{name}**: A Cidade Real fica la no norte. Primeiro preciso passar por essas ruinas.
- **Fim do Capitulo 1**: Capitulo 2 - Ruinas de Areia
- **{name}**: Colunas quebradas, um obelisco... e la no fundo, um portal de pedra brilhando!
- **{name}**: Tem mais gente aqui. Aqueles dois sao do torneio! Sera que eles tambem cairam no passado?
- **Objetivo**: Venca Rex Raptor e Weevil. Depois entre no portal de pedra ao norte.

### c2_teana_done

- **Teana**: Boa viagem, {estrangeiro|estrangeira}!

### c2_jono_done

- **Jono**: Da proxima vez eu ganho!

### c2_rex_pre

- **Rex Raptor**: Voce tambem caiu aqui? Otimo. Ganhar de voce me deixa mais perto de voltar pra casa.
- **{name}**: Entao vamos duelar. Quem ganhar fica com o caminho livre.
- **Rex Raptor**: Meus dinossauros vao te esmagar! Duelar?  _[ask]_

### c2_rex_win

- **Rex Raptor**: Nao acredito... perdi para {um|uma} {novato|novata}!
- **Rex Raptor**: Toma, achei esta pedra brilhante nas ruinas. Talvez sirva pra voce.
- **Recompensa**: Recebeu o Fragmento da Pedra Temporal 1 e a carta Ryu-kishin.

### c2_rex_lose

- **Rex Raptor**: Hahaha! Volte quando tiver dinossauros de verdade.

### c2_weevil_pre

- **Weevil**: Hehehe. Nesse mundo ninguem confere se a gente trapaceia.
- **{name}**: Entao eu vou ganhar do jeito certo, pra voce lembrar.
- **Weevil**: Meus insetos discordam. Duelar?  _[ask]_

### c2_weevil_win

- **Weevil**: Impossivel! Minha estrategia era perfeita!
- **Weevil**: Ta, ta... leva esta tocha velha e me deixa em paz.
- **Recompensa**: Recebeu uma Tocha e a carta Hitotsu-me Giant.

### c2_weevil_lose

- **Weevil**: Hehehe! Eu sabia que voce cairia na minha armadilha.

### c2_rex_done

- **Rex Raptor**: Vai logo pro portal. Eu ainda vou ter a minha revanche.

### c2_weevil_done

- **Weevil**: Hmpf. Some daqui antes que eu mude de ideia.

### c2_portal_locked

- **{name}**: O portal nao reage. Acho que preciso vencer Rex e Weevil primeiro.

## Capitulo 3


### c2_end__c3_intro

- **{name}**: O portal esta brilhando mais forte agora. Vou entrar!
- **Fim do Capitulo 2**: Capitulo 3 - O Palacio e o Principe
- **{name}**: Uau! O portal me levou para dentro da Cidade Real. Que palacio enorme!
- **{name}**: Na frente do palacio tem um sacerdote e um jovem que parece um rei. E o Principe!
- **Objetivo**: Fale com o sacerdote Seto, na frente do palacio.

### c3_seto_pre

- **Seto**: {Um|Uma} {estrangeiro|estrangeira} com cartas que ninguem conhece. Ameaca ou presente?
- **Principe**: Seto, deixe {ele|ela} provar. Se {ele|ela} perder, eu mesmo mando embora.
- **{name}**: Se eu ganhar, quero saber por que essas fendas no tempo estao se abrindo.
- **Seto**: Combinado. Prepare o seu deck. Duelar?  _[ask]_

### c3_seto_win

- **Seto**: Hmpf... voce venceu. Se o Principe confia em voce, eu tambem vou confiar.
- **Principe**: As fendas comecaram quando o sacerdote Heishin abriu o cofre dos Itens do Milenio.
- **Principe**: Leve o Selo Real. Com ele voce entra no palacio e descobre o que Heishin quer.
- **Recompensa**: Recebeu o Selo Real e a carta Dark Magician.
- **Objetivo**: Entre no palacio e investigue Heishin. O Mage Soldier tambem quer duelar.

### c3_seto_lose

- **Seto**: Era isso? Volte quando estiver {pronto|pronta}, {estrangeiro|estrangeira}.

### c3_seto_done

- **Seto**: O palacio esta aberto para voce. Nao me decepcione.

### c3_prince_before

- **Principe**: {Bem-vindo|Bem-vinda} a Cidade Real, viajante. Mostre ao Seto o que voce sabe fazer.

### c3_prince_after

- **Principe**: Cuidado com Heishin. Ele anda pelos corredores do palacio a noite.

### c3_soldier_pre

- **Mage Soldier**: Eu treino os guardas do palacio. Quer testar o seu deck contra mim? Duelar?  _[ask]_

### c3_soldier_win

- **Mage Soldier**: Bom duelo! Leve esta carta na sua jornada.
- **Recompensa**: Recebeu a carta Celtic Guardian.

### c3_soldier_lose

- **Mage Soldier**: Treine mais um pouco e volte aqui.

### c3_soldier_done

- **Mage Soldier**: Os guardas falam muito bem de voce.

### c3_door_locked

- **{name}**: A porta do palacio esta fechada. Preciso da permissao do Seto primeiro.

## Capitulo 4


### c3_end__c4_intro

- **{name}**: Com o Selo Real a porta se abriu. Heishin esconde alguma coisa aqui dentro.
- **Fim do Capitulo 3**: Capitulo 4 - O Golpe de Heishin
- **Naquela noite**: Heishin atacou a cidade com os seus guardas. O ceu ficou vermelho de fogo.
- **{name}**: Este e o salao do trono! Heishin esta la no alto e o Principe esta cercado!
- **Objetivo**: Derrote Heishin no salao do trono.

### c4_heishin_pre

- **Heishin**: Os Itens do Milenio dao poder a quem tem coragem de pega-los. E eu tive coragem.
- **{name}**: Voce atacou a cidade inteira por sete pedacos de ouro?
- **Heishin**: Por sete chaves. E agora voce vai me entregar o seu deck. Duelar?  _[ask]_

### c4_heishin_win

- **Heishin**: Impossivel! {Um|Uma} {estrangeiro|estrangeira} me venceu? Isso ainda nao acabou!
- **O que aconteceu**: Heishin fugiu pela janela e levou os Itens do Milenio com ele.
- **Simon Muran**: {name}! Heishin vai voltar atras do Principe. So existe um jeito de protege-lo.
- **Simon Muran**: Vou guardar a alma do Principe dentro do Enigma do Milenio. Ele dorme ate a hora certa.
- **Principe**: {name}, eu confio em voce. Encontre os Itens e me acorde quando chegar a hora.
- **Simon Muran**: Leve o Colar do Milenio. Ele mostra o futuro e pode abrir uma fenda ate o seu tempo.
- **Recompensa**: Recebeu o Colar do Milenio e a carta Gaia the Fierce Knight.
- **Objetivo**: Toque o trono brilhante para viajar no tempo.

### c4_heishin_lose

- **Heishin**: Hahaha! {Fraco|Fraca} demais. Volte quando tiver coragem de verdade.

### c4_prince_hall

- **Principe**: {name}! Heishin quer os Itens do Milenio. Por favor, detenha ele!

### c4_seto_before

- **Seto**: Eu protejo o Principe. Va, {estrangeiro|estrangeira}, enfrente Heishin!

### c4_seto_after

- **Seto**: O Principe esta guardado no Enigma. Encontre os Itens e traga ele de volta.

### c4_throne_locked

- **{name}**: O trono nao esta brilhando. Primeiro preciso derrotar Heishin.

## Capitulo 5


### c4_end__c5_intro

- **{name}**: O Colar esta brilhando junto com o trono. Uma fenda no tempo esta se abrindo!
- **Fim do Capitulo 4**: Capitulo 5 - O Torneio Fora do Tempo
- **{name}**: Espera... esta e a ilha do torneio do Pegasus! Sera que eu voltei pro meu tempo?
- **{name}**: Nao... o ceu ainda tem fendas. O torneio ficou preso entre duas epocas.
- **Objetivo**: Venca Mai, Bandit Keith e Shadi. Depois enfrente Pegasus na frente do castelo.

### c5_mai_pre

- **Mai**: Gracinha, aqui o que vale e estrategia. E um pouco de perfume.
- **{name}**: Entao vamos ver qual estrategia e melhor.
- **Mai**: Minhas Harpias estao prontas. Duelar?  _[ask]_

### c5_mai_win

- **Mai**: Nada mal, gracinha. Voce ganhou na moral.
- **Recompensa**: Recebeu a carta Harpie Lady.

### c5_mai_lose

- **Mai**: Hihi, volte quando aprender a jogar.

### c5_mai_done

- **Mai**: Boa sorte com o Pegasus. Ele e muito esquisito.

### c5_keith_pre

- **Bandit Keith**: Esse torneio e meu. Voce e so mais um nome na minha lista.
- **{name}**: Entao tente riscar o meu nome, se conseguir.
- **Bandit Keith**: Vamos ver, {novato|novata}. Duelar?  _[ask]_

### c5_keith_win

- **Bandit Keith**: Grr... sorte de principiante!
- **Recompensa**: Recebeu a carta Great White.

### c5_keith_lose

- **Bandit Keith**: Hah! Volta pra casa, {novato|novata}.

### c5_keith_done

- **Bandit Keith**: Nao fala comigo agora, {novato|novata}.

### c5_shadi_pre

- **Shadi**: Eu sou Shadi, guardiao dos Itens do Milenio. Vejo que voce carrega o Colar.
- **Shadi**: Mostre que o seu coracao e digno dele. Duelar?  _[ask]_

### c5_shadi_win

- **Shadi**: Seu coracao e puro. Tome este pedaco da Pedra Temporal.
- **Recompensa**: Recebeu o Fragmento da Pedra Temporal 2 e a carta Illusionist Faceless Mage.

### c5_shadi_lose

- **Shadi**: Seu coracao ainda tem duvidas. Volte depois.

### c5_shadi_done

- **Shadi**: Pegasus tem o Olho do Milenio. Tenha cuidado com ele.

### c5_pegasus_locked

- **Pegasus**: Ola, {name}-{menino|menina}! Primeiro venca os outros tres duelistas. Depois eu duelo com voce.

### c5_pegasus_pre

- **Pegasus**: O seu destino eu ja li, {name}-{menino|menina}. Que tal descobrir se estou certo?
- **{name}**: Ninguem le o meu destino. Eu escrevo ele no duelo!
- **Pegasus**: Que divertido! Duelar?  _[ask]_

### c5_pegasus_win

- **Pegasus**: Impossivel! O Olho do Milenio nao conseguiu ler a sua mente!
- **Pegasus**: Fique com o Olho. Talvez ele ajude voce a salvar o Principe.
- **Isis**: Eu sou Isis. Eu vi voce numa visao. Vou abrir um portal de volta ao Egito.
- **Isis**: Os Magos dos Templos guardam os outros Itens. O Principe precisa deles.
- **Recompensa**: Recebeu o Olho do Milenio e a carta Thousand Dragon.
- **Objetivo**: Entre no portal do castelo para voltar ao Egito.

### c5_pegasus_lose

- **Pegasus**: Hahaha! Eu disse que ja tinha lido o seu destino.

### c5_pegasus_done

- **Pegasus**: O portal da Isis esta aberto no castelo. Adeus, {name}-{menino|menina}!

### c5_gate_locked

- **{name}**: O portao do castelo esta fechado. Primeiro preciso vencer Pegasus.

## Capitulo 6


### c5_end__c6_intro

- **{name}**: O portal da Isis esta aberto. Hora de voltar pro Egito!
- **Fim do Capitulo 5**: Capitulo 6 - Os Sete Itens

### c6_arrival

- **{name}**: Areia quente de novo! O portal me largou num velho cruzamento.
- **Simon Muran**: {name}! A Isis avisou que voce vinha. Guardei o Enigma em seguranca.
- **Recompensa**: Recebeu o Enigma do Milenio. O Principe dorme dentro dele.
- **Simon Muran**: Heishin so esvaziou o cofre. Os Itens de verdade estavam escondidos em cinco templos.
- **Simon Muran**: Cada templo tem um Mago que guarda um Item. Venca os Magos e eles deixam voce levar.
- **{name}**: Mar, floresta, montanha, deserto e campina. Entendi. Bora la.
- **Objetivo**: Visite os cinco templos e ganhe os Itens. Depois abra o portao do Labirinto.

### c6_simon_hub

- **Simon Muran**: Vi os homens do Heishin perto dos templos. Corra, mas nao apresse os seus duelos.

### c6_simon_hub_done

- **Simon Muran**: Voce tem os cinco Itens! Va ao portao do Labirinto. Eu guardo o cruzamento.

### c6_ocean_pre

- **Ocean Mage**: Alto, {estrangeiro|estrangeira}! O mar nao abre o templo para visitantes de pe seco.
- **{name}**: So quero pegar emprestado o que o templo guarda. Duele comigo.
- **Ocean Mage**: A mare vai decidir. Duelar?  _[ask]_

### c6_ocean_win

- **Ocean Mage**: A mare virou... Pode entrar. O High Mage Secmeton espera la dentro.
- **Recompensa**: Recebeu a carta Aqua Dragon.
- **Objetivo**: Entre no Templo do Mar e enfrente o High Mage Secmeton.

### c6_ocean_lose

- **Ocean Mage**: O mar te jogou de volta pra praia. Tente de novo.

### c6_ocean_done

- **Ocean Mage**: Secmeton espera la dentro. O mar deixa voce passar.

### c6_secmeton_locked

- **{name}**: Uma parede de agua bloqueia a porta de dentro. O Ocean Mage precisa me deixar entrar.

### c6_secmeton_pre

- **High Mage Secmeton**: Entao e voce quem caminha pelo tempo. As aguas sussurraram sobre voce.
- **{name}**: Entao voce sabe por que vim. Preciso do Tablete do Mar.
- **High Mage Secmeton**: Palavras sao rasas. Mostre com cartas. Duelar?  _[ask]_

### c6_secmeton_win

- **High Mage Secmeton**: Voce nada bem, viajante. O Tablete do Mar e seu.
- **High Mage Secmeton**: Ele serve no portao do Labirinto. Os homens do Heishin o querem muito.
- **Recompensa**: Recebeu o Tablete do Mar e a carta Suijin.
- **Objetivo**: Faltam quatro templos - Floresta, Montanha, Deserto e Campina.

### c6_secmeton_lose

- **High Mage Secmeton**: Raso demais. Mergulhe mais fundo e volte.

### c6_secmeton_done

- **High Mage Secmeton**: Guarde bem o Tablete. O mar tem memoria.

### c6_anubisius_pre

- **High Mage Anubisius**: Silencio, {estrangeiro|estrangeira}. As arvores antigas nao gostam de barulho.
- **{name}**: Vim buscar a Chave do Milenio. A vida do Principe esta em jogo.
- **High Mage Anubisius**: A floresta nao da nada de graca. Duelar?  _[ask]_

### c6_anubisius_win

- **High Mage Anubisius**: As raizes se curvam a voce. Leve a Chave do Milenio.
- **Recompensa**: Recebeu a Chave do Milenio e a carta Ancient One of the Deep Forest.

### c6_anubisius_lose

- **High Mage Anubisius**: A floresta engoliu as suas cartas. Tente de novo.

### c6_anubisius_done

- **High Mage Anubisius**: A Chave esta em boas maos. As arvores aprovam.

### c6_atenza_pre

- **High Mage Atenza**: O caminho e ingreme e o meu preco tambem. So os fortes levam o Bastao.
- **{name}**: Eu atravessei o tempo. Uma montanha nao vai me parar.
- **High Mage Atenza**: Entao suba! Duelar?  _[ask]_

### c6_atenza_win

- **High Mage Atenza**: Voce chegou ao pico. O Bastao do Milenio e seu.
- **Recompensa**: Recebeu o Bastao do Milenio e a carta Thunder Dragon.

### c6_atenza_lose

- **High Mage Atenza**: A montanha e fria e eu tambem. Suba de novo.

### c6_atenza_done

- **High Mage Atenza**: Use o Bastao com sabedoria. Poder nao e sabedoria.

### c6_martis_pre

- **High Mage Martis**: A areia enterra quem tem pressa. Devagar, viajante do tempo.
- **{name}**: Devagar? Eu acabei de cruzar cinco mil anos.
- **High Mage Martis**: Entao deixe as dunas julgarem voce. Duelar?  _[ask]_

### c6_martis_win

- **High Mage Martis**: As dunas se curvam a voce. Leve o Anel do Milenio.
- **Recompensa**: Recebeu o Anel do Milenio e a carta Mystical Sand.

### c6_martis_lose

- **High Mage Martis**: A areia cobre as suas pegadas. Volte.

### c6_martis_done

- **High Mage Martis**: Os homens do Heishin passaram aqui. Foram embora de maos vazias.

### c6_kepura_pre

- **High Mage Kepura**: {Bem-vindo|Bem-vinda} a campina, viajante do tempo! As flores disseram que voce vinha.
- **{name}**: Flores? ...Ta. Preciso da Balanca do Milenio.
- **High Mage Kepura**: Com calma ou com garra, um duelo decide. Duelar?  _[ask]_

### c6_kepura_win

- **High Mage Kepura**: Que lindo! Voce duela com bom coracao. A Balanca e sua.
- **Recompensa**: Recebeu a Balanca do Milenio e a carta Queen of Autumn Leaves.

### c6_kepura_lose

- **High Mage Kepura**: Ai, ai. Descanse entre as flores e tente de novo.

### c6_kepura_done

- **High Mage Kepura**: Mantenha o coracao em equilibrio e a Balanca faz o resto.

### c6_gate_locked

- **{name}**: O portao tem cinco encaixes vazios. Preciso dos Itens dos cinco templos.

### side_cockatiel_pre

- **Cockatiel**: Piu-piu! {Bem-vindo|Bem-vinda}, viajante do tempo. Eu sou Calopsita, duelista andarilho.
- **{name}**: Belo topete. O seu passarinho morde?
- **Cockatiel**: So quem perde feio. O meu bando esta ansioso por um duelo. {Pronto|Pronta}?  _[ask]_

### side_cockatiel_win

- **Cockatiel**: Ha! Nada mal. O meu bando ficou impressionado.
- **Cockatiel**: Fique com esta pena. Ela traz sorte a quem voa alto.
- **Recompensa**: Recebeu a Pena de Calopsita e a carta Crimson Sunbird.

### side_cockatiel_lose

- **Cockatiel**: Piu! Volte depois de comer uns graos e treinar.

### side_cockatiel_done

- **Cockatiel**: Voe alto, viajante. O vento se lembra de voce.

## Capitulo 7


### c6_end__c7_intro

- **{name}**: Tablete, Chave, Bastao, Anel e Balanca... os encaixes estao brilhando!
- **Fim do Capitulo 6**: Capitulo 7 - O Labirinto e os Guardioes
- **{name}**: O portao abre para uma escada que desce no escuro. Vai com tudo.
- **Simon Muran**: Cuidado! Senti Heishin passar por aqui. Seto foi na frente guardar o caminho.
- **Objetivo**: Cruze o Labirinto. Venca os guardioes para chegar ao altar.

### c7_lmage_pre

- **Labyrinth Mage**: Um rosto novo no labirinto. Poucos voltam a sair daqui.
- **{name}**: Entao eu serei um dos poucos.
- **Labyrinth Mage**: Aqui as paredes mudam. As chances tambem. Duelar?  _[ask]_

### c7_lmage_win

- **Labyrinth Mage**: Voce leu bem o labirinto. Leve isto e siga em frente.
- **Recompensa**: Recebeu a carta Guardian of the Labyrinth.
- **Objetivo**: Siga ate a primeira porta e enfrente o Guardian Sebek.

### c7_lmage_lose

- **Labyrinth Mage**: Ja se perdeu? O labirinto adora rostos novos.

### c7_lmage_done

- **Labyrinth Mage**: Em frente, depois a esquerda. Ou a direita. Quem sabe?

### c7_door1_locked

- **{name}**: As paredes nao param de se mexer. O Mago que as controla deve estar perto.

### c7_sebek_pre

- **Guardian Sebek**: Nenhuma alma viva passa por esta porta sem o julgamento dos deuses.
- **{name}**: Entao me julgue.
- **Guardian Sebek**: A balanca esta pronta. Duelar?  _[ask]_

### c7_sebek_win

- **Guardian Sebek**: Os deuses acham voce... aceitavel. A porta esta aberta.
- **Recompensa**: Recebeu a carta Guardian of the Throne Room.
- **Objetivo**: Proxima porta - Guardian Neku.

### c7_sebek_lose

- **Guardian Sebek**: Julgado e reprovado. Volte quando for {digno|digna}.

### c7_sebek_done

- **Guardian Sebek**: Va. Neku espera na proxima porta.

### c7_door2_locked

- **{name}**: Outra porta, mas o julgamento do Sebek vem primeiro.

### c7_neku_pre

- **Guardian Neku**: Sou Neku, guardiao da segunda porta. Sebek julga o corpo. Eu julgo o coracao.
- **{name}**: O meu coracao esta bem. E o resto de mim que esta cansado.
- **Guardian Neku**: Vamos ver. Duelar?  _[ask]_

### c7_neku_win

- **Guardian Neku**: Seu coracao e firme. Pode passar, viajante.
- **Recompensa**: Recebeu a carta Rude Kaiser.
- **Objetivo**: Seto esta alem da segunda porta.

### c7_neku_lose

- **Guardian Neku**: Seu coracao vacila. Descanse e volte.

### c7_neku_done

- **Guardian Neku**: Seto espera adiante. Nao o faca esperar.

### c7_door3_locked

- **{name}**: Esta porta nao se move. Preciso vencer Neku primeiro.

### c7_seto2_pre

- **Seto**: Voce veio. Eu tinha as minhas duvidas.
- **{name}**: Eu disse que ia encontrar os Itens.
- **Seto**: Eu sirvo o Principe, nao voce. Mas hoje lutamos do mesmo lado.
- **{name}**: Entao por que duelar?
- **Seto**: O altar vai testar voce. Nao deixarei o Principe descansar em maos nao testadas. Duelar?  _[ask]_

### c7_seto2_win

- **Seto**: Chega. Eu errei em duvidar de voce.
- **Seto**: Leve o White Dragon. Ele escolheu lutar ao seu lado.
- **Recompensa**: Recebeu a carta Blue-eyes White Dragon.
- **Objetivo**: Chegue ao altar e acorde o Principe.

### c7_seto2_lose

- **Seto**: Ainda nao. Volte mais forte.

### c7_seto2_done

- **Seto**: O altar esta logo ali. Eu guardo as suas costas.

### c7_altar_locked

- **{name}**: Seto esta na frente do altar. Ele ainda nao vai me deixar passar.

### c7_altar_wake

- **{name}**: Anel, Bastao, Chave, Balanca, Colar, Olho... e o Enigma.
- **O Altar**: Os sete Itens brilham. A alma do Principe sai do Enigma.
- **Principe**: {name}... Seto... Ouvi tudo enquanto dormia. Obrigado.
- **Seto**: Meu Principe! Voce esta livre.
- **Heishin**: Hahaha! Voce fez o trabalho pesado por mim. Os sete Itens num so lugar!
- **{name}**: Heishin! Voce nunca desiste.
- **Heishin**: Eu nao desisti de nada. Duele, se tiver coragem!  _[ask]_

### c7_heishin2_retry

- **Heishin**: Voltou pra apanhar? Entregue os Itens!  _[ask]_

### c7_heishin2_win

- **Heishin**: Nao... os Itens! A sombra me prometeu...
- **A Sombra**: Heishin some em fumaca negra. Algo mais profundo desperta la embaixo.
- **Principe**: Esse poder nao era do Heishin. Algo mais antigo acordou.
- **Recompensa**: Recebeu o Fragmento da Pedra Temporal 3 e a carta Summoned Skull.
- **Objetivo**: Desca a escada escura atras do altar com o Principe.

### c7_heishin2_lose

- **Heishin**: Hahaha! Os Itens sao meus!

### c7_prince_free

- **Principe**: Vamos. O que quer que espere la embaixo, enfrentamos juntos.

### c7_seto2_after_altar

- **Seto**: Heishin era so um peao. O verdadeiro inimigo esta la embaixo. Va, eu sigo voce.

## Capitulo 8


### c7_end__c8_intro

- **{name}**: Os Fragmentos e os Itens estao todos puxando para a escada escura.
- **Fim do Capitulo 7**: Capitulo 8 - Nitemare
- **Principe**: O Templo Final. Ele flutua no Reino das Sombras.
- **{name}**: Ultimo duelo. Depois disso, eu vou pra casa.
- **Objetivo**: Chegue ao Templo Final e derrote Nitemare.

### c8_seto3_pre

- **Seto**: Volte... A noite nao perdoa.
- **{name}**: Seto! Quem esta falando nao e voce.
- **Principe**: A sombra o prende. Quebre-a com um duelo, {name}!
- **Seto**: ...Duelo.  _[ask]_

### c8_seto3_win

- **Seto**: Argh... o que eu fiz? Principe?
- **Seto**: Eu vi. DarkNite carrega o rancor de Heishin. Nitemare dorme la em cima.
- **Recompensa**: Recebeu a carta Red-eyes B. Dragon.
- **Objetivo**: Venca DarkNite no salao das sombras.

### c8_seto3_lose

- **Seto**: ...Va embora. Volte mais forte.

### c8_seto3_done

- **Seto**: Siga em frente. Eu seguro a porta atras de voce.

### c8_hall_locked

- **{name}**: Uma parede de nevoa negra. Seto esta no meu caminho.

### c8_darknite_pre

- **DarkNite**: Os sete Itens me chamaram. Obrigado por traze-los.
- **Principe**: {name}, eu duelo ao seu lado. Este mundo nao e so meu.
- **{name}**: Vamos acabar com isso.
- **DarkNite**: Dois coracoes contra uma noite? Duelo!  _[ask]_

### c8_darknite_win

- **DarkNite**: Impossivel... a escuridao nao pode perder pra luz!
- **Nitemare**: Voce me divertiu, DarkNite. Agora saia da frente.
- **Recompensa**: Recebeu a carta Zoa.
- **Objetivo**: Suba ate o topo e enfrente Nitemare.

### c8_darknite_lose

- **DarkNite**: Nada se perde no escuro. Nem voce.

### c8_stairs_locked

- **{name}**: A escada esta selada por sombras. DarkNite a guarda.

### c8_nitemare_pre

- **Nitemare**: Eu sou Nitemare. Eu ja estava aqui antes do primeiro Item.
- **Nitemare**: Heishin era um fantoche. As fendas, os Itens... tudo isso era meu.
- **{name}**: Foi voce que abriu as fendas? Voce me tirou do meu tempo?
- **Nitemare**: Eu abri todas as portas. Feche a ultima voce mesmo, se puder.
- **Principe**: Juntos, {name}! Ilumine o caminho pela noite!
- **{name}**: Ultimo duelo. Depois eu vou pra casa.
- **Nitemare**: Venha, entao. Duelo!  _[ask]_

### c8_nitemare_win

- **Nitemare**: Nao... a luz dos sete Itens...
- **A Pedra Temporal**: Os tres Fragmentos voam juntos e formam a Pedra Temporal completa.
- **Recompensa**: Recebeu a Pedra Temporal e a carta lendaria Workers' Rights.
- **Objetivo**: Escolha como a sua jornada termina.

### c8_nitemare_lose

- **Nitemare**: A escuridao leva tudo. Ate a esperanca.

### c8_choice

- **Principe**: A Pedra pode te mandar pra casa, {name}. Ou voce pode ficar ao nosso lado.
- **{name}**: Usar a Pedra Temporal para voltar pra casa?  _[ask]_

### ending_home

- **{name}**: Adeus, Seto. Adeus, Principe. Obrigad{o|a} por tudo.
- **Principe**: Leve esta carta de lembranca. Nos nunca vamos esquecer voce.
- **Recompensa**: Recebeu a carta Mystical Elf de lembranca.
- **Epilogo**: A luz da Pedra leva {name} de volta a arena, um segundo depois de sair.
- **{name}**: ...A mesma arena. A mesma plateia. E eu ainda tenho a carta do Principe.
- **Fim**: Valeu por jogar o MODO JORNADA.

### ending_stay

- **{name}**: Acho que a minha historia agora e aqui. Eu vou ficar.
- **Seto**: Entao sirva ao meu lado, {sacerdote|sacerdotisa}. O Principe vai precisar de voce.
- **Principe**: Bem-vind{o|a} ao lar, {name}. O Egito tambem e o seu tempo.
- **Epilogo**: {name} virou {sacerdote|sacerdotisa} da Cidade Real e guardou a Pedra Temporal para sempre.
- **Fim**: Valeu por jogar o MODO JORNADA.

## Pos-jogo


### side_cockatiel_epilogue

- **Cockatiel**: Ouvi o que voce fez la fora. O bando inteiro esta cantando sobre isso.

### side_mirror_pre

- **{name}**: Perai... esse e o meu rosto! E isso parece o meu deck!
- **Atos Vinicius**: Eu sou o Atos que ficou em casa. A fenda puxou o errado, ou talvez o certo.
- **{name}**: Entao vamos ver qual de nos e o melhor duelista.
- **Atos Vinicius**: Por mim tudo bem. O meu deck faz hora extra. Duelar?  _[ask]_

### side_mirror_win

- **Atos Vinicius**: Nada mal... voce trabalha mais que eu.
- **Recompensa**: Recebeu a carta Hero of the East.

### side_mirror_lose

- **Atos Vinicius**: Hora extra compensa. Tente de novo.

### side_mirror_done

- **Atos Vinicius**: Va em frente. Eu mantenho a arena aquecida.

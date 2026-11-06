# -*- coding: utf-8 -*-
"""Dialogue of the Duelist Kingdom story, chapter 1 (home town). Each page is written twice: EN and PT (ASCII, no accents).
Page tuple helpers: H = hero, X = any speaker, N = narrator (needs a label)."""
SCRIPTS = []
def H(en, pt, ask=False): return ("atos", en, pt, ask, None, None)
def X(spk, en, pt, ask=False): return (spk, en, pt, ask, None, None)
def N(len_, lpt, en, pt): return ("narrator", en, pt, False, len_, lpt)
def sc(id, desc, pages, chapter=1):
    SCRIPTS.append({"id": id, "chapter": chapter, "desc": desc, "pages": pages})

# ---------------------------------------------------------------- prologue
sc("dk1_intro", "Opening, right after character creation. Hero stands at the home door.", [
 H("Good morning, home town! Sun, sand and the sound of cards being shuffled.",
   "Bom dia, minha vila! Sol, areia e o barulho de cartas sendo embaralhadas."),
 H("Today is the Festival of the Palms. Everyone is outside, but nobody is dueling.",
   "Hoje e o Festival das Palmeiras. Todos estao na rua, mas ninguem esta duelando."),
 H("They are all whispering. Something is going on. I'll write it in my notebook.",
   "Estao todos cochichando. Algo esta acontecendo. Vou anotar tudo no meu caderno."),
 N("Objective", "Objetivo", "Ask Teana, Jono and the Guard what the whispers are about.",
   "Pergunte a Teana, Jono e ao Guarda sobre os cochichos."),
])

# ---------------------------------------------------------------- quest 1 - whispers
sc("dk1_teana_rumor", "Teana, first talk (rumor 1).", [
 X("teana", "{name}! Come here, quick! You won't believe what happened at dawn.",
   "{name}! Venha ca, rapido! Voce nao vai acreditar no que houve de madrugada."),
 X("teana", "A man in a black hood bought my whole tray of date cakes!",
   "Um homem de capuz preto comprou minha bandeja inteira de bolinhos de tamara!"),
 H("That's great news! Why the long face?", "Mas isso e otimo! Por que essa cara?"),
 X("teana", "He paid with THIS. A golden star! He said 'See you in the Kingdom' and left.",
   "Ele pagou com ISTO. Uma estrela dourada! Disse 'Nos vemos no Reino' e foi embora."),
 X("teana", "And there were no footprints in the sand. Not one!",
   "E nao havia pegadas na areia. Nenhuma!"),
 N("Rumor 1", "Boato 1", "A hooded man pays with golden stars and talks about a Kingdom.",
   "Um homem de capuz paga com estrelas douradas e fala de um Reino."),
])
sc("dk1_teana_rumor_after", "Teana, rumor already heard, other rumors missing.", [
 X("teana", "Ask Jono and the Guard too. Everybody knows a different piece!",
   "Pergunte ao Jono e ao Guarda tambem. Cada um sabe um pedacinho!"),
])
sc("dk1_teana_tell_simon", "Teana, all three rumors heard.", [
 X("teana", "Three rumors, one mystery! Old Simon knows old stories. Go and ask him.",
   "Tres boatos, um misterio! O velho Simon conhece historias antigas. Va falar com ele."),
])
sc("dk1_jono_rumor", "Jono, first talk (rumor 2).", [
 X("jono", "Hey, {name}! Perfect timing. I'm about to become rich and famous!",
   "Ei, {name}! Na hora certa. Eu vou ficar rico e famoso!"),
 H("Again? Last week it was the sand-surfing business.",
   "De novo? Semana passada era o negocio de surfe na areia."),
 X("jono", "This is different! A sailor told me about a white ship by the river mouth.",
   "Isto e diferente! Um marinheiro me falou de um navio branco na foz do rio."),
 X("jono", "It sails to an island where duelists fight for stars. The winner gets ANYTHING!",
   "Ele leva a uma ilha onde duelistas lutam por estrelas. O vencedor ganha QUALQUER COISA!"),
 X("jono", "Anything! Even a lifetime supply of fried fish!",
   "Qualquer coisa! Ate peixe frito pelo resto da vida!"),
 N("Rumor 2", "Boato 2", "A white ship takes duelists to an island. Winners get anything.",
   "Um navio branco leva duelistas a uma ilha. O campeao ganha qualquer coisa."),
])
sc("dk1_jono_rumor_after", "Jono, rumor heard, others missing.", [
 X("jono", "Don't tell anyone, but I'm already packing. Heh. Go ask the others.",
   "Nao conte pra ninguem, mas eu ja estou fazendo as malas. Heh. Pergunte aos outros."),
])
sc("dk1_jono_tell_simon", "Jono, all three rumors heard.", [
 X("jono", "Simon will know what this is about. Old men always do. Go on, I'll wait.",
   "O Simon sabe do que se trata. Velhos sempre sabem. Va la, eu espero."),
])
sc("dk1_guard_rumor", "Guard, first talk (rumor 3).", [
 X("guard", "Halt! Oh, it's you, {name}. Keep your voice down.",
   "Alto! Ah, e voce, {name}. Fale baixo."),
 X("guard", "Last night someone nailed a poster to the gate. Strange paper. It glowed.",
   "Ontem a noite alguem pregou um cartaz no portao. Papel estranho. Brilhava."),
 X("guard", "I tore it down, as is my job. But the wind took half of it. Look.",
   "Eu arranquei, e o meu trabalho. Mas o vento levou metade. Olhe."),
 H("'STAR PASSAGE. Three treasures. One duelist.' And then it's torn off.",
   "'PASSAGEM ESTELAR. Tres tesouros. Um duelista.' E depois esta rasgado."),
 X("guard", "That's all I know. Ask old Simon. He gets nervous when people say 'Kingdom'.",
   "So sei isso. Pergunte ao velho Simon. Ele fica nervoso quando falam 'Reino'."),
 N("Rumor 3", "Boato 3", "A torn poster says - Star Passage. Three treasures. One duelist.",
   "Um cartaz rasgado diz - Passagem Estelar. Tres tesouros. Um duelista."),
])
sc("dk1_guard_rumor_after", "Guard, rumor heard, others missing.", [
 X("guard", "I told you what I know. Talk to the others, but quietly.",
   "Ja contei o que sei. Fale com os outros, mas baixinho."),
])
sc("dk1_guard_tell_simon", "Guard, all three rumors heard.", [
 X("guard", "Simon. Go and see Simon. And never say I showed you that poster.",
   "O Simon. Va falar com o Simon. E nunca diga que eu mostrei aquele cartaz."),
])
sc("dk1_notice", "Notice board (optional, flavor).", [
 H("The village notice board. 'Date harvest on Friday. Lost goat - answers to Sphinx.'",
   "O mural da vila. 'Colheita de tamaras na sexta. Cabra perdida - atende por Esfinge.'"),
 H("Under it, a shiny gold nail. Someone pinned something here last night.",
   "Embaixo, um prego dourado e brilhante. Alguem pregou algo aqui ontem a noite."),
])
sc("dk1_notice_after", "Notice board, seen.", [
 H("Still just a goat notice and a gold nail. The goat is probably fine.",
   "Ainda so o aviso da cabra e um prego dourado. A cabra deve estar bem."),
])

# ---------------------------------------------------------------- quest 2 - the sage
sc("dk1_simon_wait", "Simon, before all three rumors are heard.", [
 X("simon", "The whole village buzzes like bees. I prefer quiet.",
   "A vila inteira zumbe como abelhas. Prefiro o silencio."),
 X("simon", "Ask Teana, Jono and the Guard what they heard. Then come and tell me.",
   "Pergunte a Teana, Jono e ao Guarda o que ouviram. Depois volte e me conte."),
])
sc("dk1_simon_pre", "Simon, all rumors heard. Ask page - duel (the sage's test).", [
 X("simon", "{name}! You look like someone carrying three rumors.",
   "{name}! Voce parece alguem carregando tres boatos."),
 H("A hooded man, a white ship and a torn poster. Simon, what is the Kingdom?",
   "Um homem de capuz, um navio branco e um cartaz rasgado. Simon, o que e o Reino?"),
 X("simon", "Hm. Nobody has said that word in this village for thirty years.",
   "Hum. Ninguem diz essa palavra nesta vila ha trinta anos."),
 X("simon", "I will tell you. But first show me you can hold a deck without shaking. Duel?",
   "Eu conto. Mas antes mostre que segura um baralho sem tremer. Duelar?", True),
])
sc("dk1_simon_win", "Simon beaten - the legend of Duelist Kingdom.", [
 X("simon", "Steady hands and a good heart. Good. Now listen carefully.",
   "Maos firmes e bom coracao. Bom. Agora ouca com atencao."),
 X("simon", "Far across the sea lies Duelist Kingdom, an island castle built by a showman named Pegasus.",
   "Alem do mar fica o Reino dos Duelistas, castelo numa ilha feito pelo showman Pegasus."),
 X("simon", "Duelists gather there with star chips. Win a duel and take a star. Lose and you give one.",
   "Duelistas se reunem la com fichas de estrela. Vencer rende uma estrela. Perder custa uma."),
 X("simon", "Ten stars open the castle gates. Whoever reaches the top faces Pegasus himself.",
   "Dez estrelas abrem os portoes do castelo. Quem chega ao topo enfrenta o proprio Pegasus."),
 H("And the winner gets anything?", "E o campeao ganha qualquer coisa?"),
 X("simon", "Anything he asks. That is the bait. Pegasus does love a good show.",
   "Qualquer coisa que pedir. Essa e a isca. Pegasus adora um bom espetaculo."),
 X("simon", "Invitations are rare. The other way is the Star Passage, earned, never bought.",
   "Convites sao raros. O outro caminho e a Passagem Estelar, ganha, nunca comprada."),
 X("simon", "Careful - a Passage duelist starts with a single star. Do not expect a warm welcome.",
   "Cuidado - quem vai pela Passagem comeca com uma unica estrela. Nada de boas-vindas."),
 X("simon", "A hooded courier hands out the Passage, only at night. Wait on the plaza bench.",
   "Um mensageiro encapuzado entrega a Passagem, so a noite. Espere no banco da praca."),
 N("Reward", "Recompensa", "You got the card Magician of Faith from Simon.",
   "Voce ganhou a carta Magician of Faith de Simon."),
 N("Objective", "Objetivo", "Sit on the plaza bench and wait for night.",
   "Sente no banco da praca e espere anoitecer."),
])
sc("dk1_simon_lose", "Simon wins.", [
 X("simon", "Your hands shook, but your eyes did not. Rest and try again.",
   "Suas maos tremeram, mas seus olhos nao. Descanse e tente de novo."),
])
sc("dk1_simon_stage2", "Simon, waiting for the bench.", [
 X("simon", "The bench in the plaza. Be patient, {name}. The courier comes when the sun is gone.",
   "O banco da praca. Paciencia, {name}. O mensageiro vem quando o sol se vai."),
])
sc("dk1_simon_treasures", "Simon, during the treasure hunt.", [
 X("simon", "Lost, Won, Given. I know that riddle. Do not think of them as chores.",
   "Perdido, Ganho, Dado. Conheco esse enigma. Nao pense neles como tarefas."),
 X("simon", "Think of them as a mirror. The Kingdom will ask you the same three things.",
   "Pense neles como um espelho. O Reino vai te perguntar as mesmas tres coisas."),
])
sc("dk1_teana_stage2", "Teana, stage 2.", [
 X("teana", "Simon sent you to sit on a bench? Hehe. Take a cushion, the stone is cold.",
   "O Simon mandou voce sentar num banco? Hehe. Leve uma almofada, a pedra e fria."),
])
sc("dk1_jono_stage2", "Jono, stage 2.", [
 X("jono", "A bench? That's the plan? I thought it'd be more... dramatic. Good luck!",
   "Um banco? Esse e o plano? Achei que seria mais... dramatico. Boa sorte!"),
])
sc("dk1_guard_stage2", "Guard, stage 2.", [
 X("guard", "Sitting outside after dark? I did not see anything. I was napping.",
   "Sentado la fora depois de escurecer? Eu nao vi nada. Estava cochilando."),
])

# ---------------------------------------------------------------- quest 3 - midnight bench
sc("dk1_bench_early", "Bench, before Simon's test.", [
 H("A nice stone bench. It is not the time to sit yet.",
   "Um bom banco de pedra. Ainda nao e hora de sentar."),
])
sc("dk1_bench", "Bench at stage 2 - night falls, the hooded man appears.", [
 H("I'll sit here and wait. Surely the courier will show up any minute.",
   "Vou sentar aqui e esperar. Com certeza o mensageiro vai aparecer a qualquer momento."),
 N("Later", "Mais tarde", "The sun sinks. The stalls close. The plaza grows quiet and cold.",
   "O sol se poe. As barracas fecham. A praca fica quieta e fria."),
 H("Nobody yet...", "Ninguem ainda..."),
 N("Far Away", "Ao Longe", "On a far rooftop, a robed figure stands in a faint green shimmer.",
   "Num telhado distante, uma figura de manto fica num leve brilho verde."),
 H("Somebody is watching me from up there... Gone. Only a flicker of green.",
   "Alguem me observa la de cima... Sumiu. So um piscar de verde."),
 H("Wait. Is someone standing by the old palm?",
   "Espere. Tem alguem parado perto da palmeira velha?"),
 N("Objective", "Objetivo", "Talk to the hooded man in the plaza.", "Fale com o homem encapuzado na praca."),
])
sc("dk1_bench_after", "Bench, later.", [
 H("A good bench. When I come back a champion, I'll sit here and tell everyone.",
   "Um bom banco. Quando eu voltar campeao, vou sentar aqui e contar a todos."),
])
sc("dk1_hooded_riddle", "The hooded man (Shadi in disguise) - the three treasures. Ends the night.", [
 X("hooded_man", "You wait well. Few people do.", "Voce espera bem. Poucos esperam."),
 X("hooded_man", "And ignore the one on the roof. He only watches. He never touches.",
   "E ignore aquele no telhado. Ele so observa. Nunca toca em nada."),
 H("Who is he?", "Quem e ele?"),
 X("hooded_man", "A reader, not a writer. Not tonight. Now, to business.",
   "Um leitor, nao um escritor. Nao hoje a noite. Agora, aos negocios."),
 H("Are you the courier? Do you have the Star Passage?",
   "Voce e o mensageiro? Tem a Passagem Estelar?"),
 X("hooded_man", "I am a voice in the dark, nothing more. The Passage is not given. It is earned.",
   "Sou uma voz no escuro, nada mais. A Passagem nao e dada. E conquistada."),
 X("hooded_man", "Take this card. It has three empty stamps.",
   "Pegue esta carta. Ela tem tres selos vazios."),
 X("hooded_man", "Fill them with three treasures of your village. One lost. One won. One given.",
   "Preencha com tres tesouros da sua vila. Um perdido. Um ganho. Um dado."),
 H("That is a riddle, not a quest!", "Isso e um enigma, nao uma missao!"),
 X("hooded_man", "Life is mostly riddles. Come to the harbor when the card is full. The ship won't wait long.",
   "A vida e quase so enigmas. Venha ao porto quando a carta estiver cheia. O navio nao espera muito."),
 N("You got", "Voce ganhou", "You got the Stamp Card. It shows three empty stamps.",
   "Voce ganhou o Cartao de Selos. Ele tem tres selos vazios."),
 N("Next Morning", "Manha seguinte", "The sun rises and the village wakes. Three treasures await.",
   "O sol nasce e a vila acorda. Tres tesouros esperam."),
 N("Objective", "Objetivo", "Find a Lost, a Won and a Given treasure. Ask the villagers.",
   "Ache um tesouro Perdido, um Ganho e um Dado. Pergunte aos moradores."),
])

# ---------------------------------------------------------------- stage 3 shared
sc("dk1_baker_hello", "Hakim the baker, before the treasure hunt.", [
 X("baker", "Fresh bread! Warm bread! ... Nobody? Everyone is too busy whispering to eat.",
   "Pao fresquinho! Pao quentinho! ... Ninguem? Todos estao ocupados cochichando."),
 X("baker", "Mark my words - this Festival is cursed. Or very strange.",
   "Anote o que digo - este Festival esta amaldicoado. Ou muito estranho."),
])
sc("dk1_baker_hint", "Hakim, hint about the Founder's Scarab and the hatch.", [
 H("Hakim, do you know of any lost treasure around here?",
   "Hakim, voce conhece algum tesouro perdido por aqui?"),
 X("baker", "Funny you ask. My grandfather told me about one - the Founder's Scarab.",
   "Engracado voce perguntar. Meu avo falava de um - o Escaravelho do Fundador."),
 X("baker", "It fell into the old cistern under the little pyramid, long ago.",
   "Ele caiu na antiga cisterna embaixo da piramidezinha, ha muito tempo."),
 X("baker", "Last week I saw a pale light in the hatch. Brrr! Ask Kemet for his lantern.",
   "Semana passada vi uma luz palida na escotilha. Brrr! Peca a lanterna do Kemet."),
 N("Objective", "Objetivo", "Win Kemet's lantern, then open the hatch of the little pyramid.",
   "Consiga a lanterna do Kemet e abra a escotilha da piramidezinha."),
])
sc("dk1_baker_honey", "Hakim gives honey for Teana's cakes.", [
 H("Hakim, Teana needs honey for her festival cakes.",
   "Hakim, a Teana precisa de mel para os bolinhos do festival."),
 X("baker", "For Teana's cakes? Of course! Here, careful, it is very sticky.",
   "Para os bolinhos da Teana? Claro! Tome, cuidado, e muito grudento."),
 N("You got", "Voce ganhou", "You got a Honey Jar.", "Voce ganhou um Pote de Mel."),
])
sc("dk1_baker_pre", "Hakim, optional duel.", [
 X("baker", "Between batches I like a duel. Want to try your deck against my oven? Duel?",
   "Entre uma fornada e outra eu gosto de duelar. Quer testar seu baralho no meu forno? Duelar?", True),
])
sc("dk1_baker_win", "Hakim beaten.", [
 X("baker", "Ha! You duel better than I bake. Here, a little thank-you.",
   "Ha! Voce duela melhor do que eu asso. Tome, um agradecimento."),
 N("Reward", "Recompensa", "You got the card Mooyan Curry.", "Voce ganhou a carta Mooyan Curry."),
])
sc("dk1_baker_lose", "Hakim wins.", [
 X("baker", "My bread rises faster than your deck. Try again!",
   "Meu pao cresce mais rapido que seu baralho. Tente de novo!"),
])
sc("dk1_baker_after", "Hakim, after everything.", [
 X("baker", "Safe travels, {name}. I'll keep a loaf warm for when you return.",
   "Boa viagem, {name}. Vou deixar um pao quente para quando voce voltar."),
])
sc("dk1_farmer_hello", "Kemet the farmer, stages 1-2.", [
 X("farmer", "Whispers? I'm a farmer. I mostly hear crickets and my goat.",
   "Cochichos? Sou fazendeiro. So escuto grilos e a minha cabra."),
 X("farmer", "My dates are ripe, though. Best dates for miles.",
   "Mas minhas tamaras estao maduras. As melhores por quilometros."),
])
sc("dk1_farmer_nohint", "Kemet, treasure hunt, hero has no reason for the lantern yet.", [
 X("farmer", "Dates ripe, sun hot, goat missing. That's my news.",
   "Tamaras maduras, sol quente, cabra sumida. Essas sao minhas novidades."),
 X("farmer", "I own the best lantern in the village, but I only lend it to the brave.",
   "Tenho a melhor lanterna da vila, mas so empresto aos corajosos."),
])
sc("dk1_farmer_pre", "Kemet, lantern duel.", [
 H("Hakim says you have a lantern. I need to go into the little pyramid.",
   "O Hakim disse que voce tem uma lanterna. Preciso entrar na piramidezinha."),
 X("farmer", "Into the haunted hatch? Ha! Brave or crazy?",
   "Na escotilha assombrada? Ha! Corajoso ou maluco?"),
 X("farmer", "I only lend to the brave. Prove it with a duel! Duel?",
   "So empresto aos corajosos. Prove num duelo! Duelar?", True),
])
sc("dk1_farmer_win", "Kemet beaten.", [
 X("farmer", "Ha! Brave AND crazy. The best kind. Take the lantern.",
   "Ha! Corajoso E maluco. O melhor tipo. Leve a lanterna."),
 X("farmer", "And this card. If you hear music down there, run.",
   "E esta carta. Se ouvir musica la embaixo, corra."),
 N("Reward", "Recompensa", "You got a Lantern and the card Killer Needle.",
   "Voce ganhou uma Lanterna e a carta Killer Needle."),
 N("Objective", "Objetivo", "Open the hatch of the little pyramid next to the house.",
   "Abra a escotilha da piramidezinha ao lado da casa."),
])
sc("dk1_farmer_lose", "Kemet wins.", [
 X("farmer", "The lantern stays with me, friend. Practice and come back.",
   "A lanterna fica comigo, amigo. Treine e volte."),
])
sc("dk1_farmer_after", "Kemet, after the lantern.", [
 X("farmer", "Mind the ghost. If you hear music, run. I said that already? Run anyway.",
   "Cuidado com o fantasma. Se ouvir musica, corra. Ja falei? Corra mesmo assim."),
])

sc("dk1_hatch_locked", "Pyramid hatch, no lantern.", [
 H("A little pyramid with a stone hatch. It is far too dark to go inside.",
   "Uma piramidezinha com uma escotilha de pedra. Escuro demais para entrar."),
])
sc("dk1_cistern_enter", "Hatch opened with the lantern.", [
 H("Lantern lit. Down the old steps I go. Brrr, it's cold down here.",
   "Lanterna acesa. Desco as escadas antigas. Brrr, que frio aqui embaixo."),
])
sc("dk1_cistern_exit", "Cistern stairs up.", [
 H("Up the steps and back into the warm sun.", "Subo a escada e volto para o sol quente."),
])
sc("dk1_bakura_pre", "Bakura the lonely ghost - duel for the Scarab.", [
 X("bakura", "A visitor! A real, breathing visitor! Oh, joyful day!",
   "Um visitante! Um visitante de verdade, que respira! Que dia feliz!"),
 H("Um... you are floating.", "Hum... voce esta flutuando."),
 X("bakura", "Three hundred years of floating. I walk through walls, but nobody ever drops by.",
   "Trezentos anos flutuando. Atravesso paredes, mas ninguem nunca aparece."),
 H("I'm looking for the Founder's Scarab.", "Estou procurando o Escaravelho do Fundador."),
 X("bakura", "That shiny thing? I use it as a lamp! Win it from me. A duel! Please! Duel?",
   "Aquela coisa brilhante? Eu uso de lampada! Ganhe de mim. Um duelo! Por favor! Duelar?", True),
])
sc("dk1_bakura_win", "Bakura beaten.", [
 X("bakura", "Splendid! The best duel in three centuries. Also the only one.",
   "Esplendido! O melhor duelo em tres seculos. Tambem o unico."),
 X("bakura", "Take the Scarab. I'll find another lamp. Please visit again, it gets quiet.",
   "Leve o Escaravelho. Acho outra lampada. Visite de novo, aqui fica quieto."),
 N("Reward", "Recompensa", "You got the Founder's Scarab and the card The 13th Grave.",
   "Voce ganhou o Escaravelho do Fundador e a carta The 13th Grave."),
 N("Stamp", "Selo", "A stamp glows on your Stamp Card - Lost.",
   "Um selo brilha no seu Cartao de Selos - Perdido."),
])
sc("dk1_bakura_lose", "Bakura wins.", [
 X("bakura", "Leaving already? Stay! One more duel? Pretty please?",
   "Ja vai embora? Fique! Mais um duelo? Por favorzinho?"),
])
sc("dk1_bakura_after", "Bakura, after.", [
 X("bakura", "Hello, friend! The step is slippery. Oh, and thank you for the visit.",
   "Ola, amigo! O degrau esta escorregadio. Ah, e obrigado pela visita."),
])
sc("dk1_rex_first", "Rex Raptor, first talk (boast). Points to Jono.", [
 X("rex", "ROAR! Behold the mighty Rex Raptor, wandering dinosaur duelist!",
   "ROAR! Contemple o poderoso Rex Raptor, duelista errante de dinossauros!"),
 H("Aren't you just passing through?", "Voce nao esta so de passagem?"),
 X("rex", "I collect trophies. See this bandana? Won it from a loud kid called Jono.",
   "Eu coleciono trofeus. Ve esta bandana? Ganhei de um garoto barulhento, o Jono."),
 H("Jono's bandana... I should talk to him first.",
   "A bandana do Jono... Melhor falar com ele primeiro."),
])
sc("dk1_rex_pre", "Rex, duel for the bandana.", [
 H("Rex, I want Jono's bandana back.", "Rex, quero a bandana do Jono de volta."),
 X("rex", "Ha! Then take it from my dinosaurs. Win and it is yours. Fair is fair.",
   "Ha! Entao tome dos meus dinossauros. Vencer e levar. Justo e justo."),
 X("rex", "But lose, and I get your lucky socks too! Duel?",
   "Mas se perder, fico com suas meias da sorte tambem! Duelar?", True),
])
sc("dk1_rex_win", "Rex beaten.", [
 X("rex", "Impossible! My dinosaurs! My trophy!", "Impossivel! Meus dinossauros! Meu trofeu!"),
 X("rex", "Hmph. Take it. And this card, rookie. I don't carry grudges. Only dinosaurs.",
   "Hmph. Leve. E esta carta, novato. Eu nao guardo magoa. So dinossauros."),
 N("Reward", "Recompensa", "You got Jono's Bandana and the card Uraby.",
   "Voce ganhou a Bandana do Jono e a carta Uraby."),
 N("Stamp", "Selo", "A stamp glows on your Stamp Card - Won.",
   "Um selo brilha no seu Cartao de Selos - Ganho."),
])
sc("dk1_rex_lose", "Rex wins.", [
 X("rex", "ROAR! More dinosaurs than you can count! Come back stronger.",
   "ROAR! Mais dinossauros do que voce consegue contar! Volte mais forte."),
])
sc("dk1_rex_after", "Rex, after.", [
 X("rex", "I'll find a new trophy. You should enter that Kingdom, kid. I hear stars are shiny.",
   "Vou achar outro trofeu. Entre nesse Reino, garoto. Dizem que estrelas brilham."),
])
sc("dk1_jono_ask", "Jono tells about the bandana.", [
 X("jono", "Ugh. {name}. Don't look at me. Worst day ever.",
   "Ugh. {name}. Nao olhe pra mim. O pior dia da vida."),
 H("What happened?", "O que houve?"),
 X("jono", "Rex Raptor, the big dino guy on the east road, bet my lucky bandana. I lost in three turns!",
   "O Rex Raptor, o dino da estrada leste, apostou minha bandana da sorte. Perdi em tres turnos!"),
 X("jono", "I'm too embarrassed to go back. If you won it back for me, I'd owe you big.",
   "Estou com vergonha de voltar la. Se voce ganhasse de volta, eu ficaria devendo muito."),
 N("Objective", "Objetivo", "Beat Rex Raptor on the east road and win the bandana back.",
   "Venca Rex Raptor na estrada leste e ganhe a bandana de volta."),
])
sc("dk1_jono_waiting", "Jono, waiting for the bandana.", [
 X("jono", "Rex is on the east road. Please be gentle... no, be MEAN.",
   "O Rex esta na estrada leste. Seja gentil... nao, seja MALVADO."),
])
sc("dk1_jono_thanks", "Jono, bandana won back.", [
 X("jono", "My bandana! You did it! You actually did it!",
   "Minha bandana! Voce conseguiu! Voce conseguiu mesmo!"),
 H("It's yours. Take it.", "E sua. Pegue."),
 X("jono", "No way. You won it fair and square. Keep it, it brings luck.",
   "De jeito nenhum. Voce ganhou limpo. Fique com ela, da sorte."),
 X("jono", "Take this card too. I have a plan, by the way. A secret plan. Heh.",
   "Leve esta carta tambem. Eu tenho um plano, alias. Um plano secreto. Heh."),
 N("Reward", "Recompensa", "You got the card Dragon Treasure from Jono.",
   "Voce ganhou a carta Dragon Treasure do Jono."),
])
sc("dk1_jono_after", "Jono, bandana done / waiting for harbor.", [
 X("jono", "That bandana looks better on you. Well, no. But keep it anyway.",
   "Essa bandana fica melhor em voce. Bom, nao. Mas fique com ela."),
])
sc("dk1_teana_ask", "Teana asks for help with the cakes (Given quest).", [
 X("teana", "{name}! You were out all night. Did the ghost bite you? Hehe.",
   "{name}! Voce ficou fora a noite toda. O fantasma te mordeu? Hehe."),
 H("I'm looking for a Given treasure. Whatever that means.",
   "Estou procurando um tesouro Dado. Seja la o que isso significa."),
 X("teana", "Given? Oh... I can't talk now. The festival starts and I have no cakes!",
   "Dado? Ah... agora nao posso. O festival comeca e eu nao tenho bolinhos!"),
 X("teana", "I need honey from Hakim, fresh river water and ripe dates. But I can't leave the stall.",
   "Preciso de mel do Hakim, agua fresca do rio e tamaras maduras. Mas nao posso sair da barraca."),
 X("teana", "Help me and I'll give you something precious. Here, take my water jug.",
   "Me ajude e eu te dou algo precioso. Tome, leve minha jarra de agua."),
 N("You got", "Voce ganhou", "You got a Water Jug.", "Voce ganhou uma Jarra de Agua."),
 N("Objective", "Objetivo", "Get honey from Hakim, fill the jug at the river, pick dates from a palm.",
   "Pegue mel com o Hakim, encha a jarra no rio e colha tamaras de uma palmeira."),
])
sc("dk1_teana_waiting", "Teana, waiting for the ingredients.", [
 X("teana", "Honey from Hakim, water from the river and dates from a palm. Please hurry!",
   "Mel do Hakim, agua do rio e tamaras de uma palmeira. Por favor, ande rapido!"),
])
sc("dk1_teana_pre", "Teana, all ingredients - duel for the charm.", [
 X("teana", "Honey, water AND dates! You're a hero, {name}!",
   "Mel, agua E tamaras! Voce e um heroi, {name}!"),
 X("teana", "The cakes need time to bake. So duel me! I want my charm in good hands.",
   "Os bolinhos precisam assar. Entao duele comigo! Quero meu amuleto em boas maos."),
 X("teana", "If you win, the charm is yours. If you lose, you wash dishes! Duel?",
   "Se ganhar, o amuleto e seu. Se perder, lava a louca! Duelar?", True),
])
sc("dk1_teana_win", "Teana beaten - the Given treasure.", [
 X("teana", "Wow! Okay, okay, you win. A deal is a deal.",
   "Uau! Tudo bem, tudo bem, voce venceu. Combinado e combinado."),
 X("teana", "This is my Lucky Charm. My granny gave it to me. I can't go anywhere, but you can.",
   "Este e meu Amuleto da Sorte, presente da minha avo. Eu nao posso ir, mas voce pode."),
 X("teana", "It is not a trade. It is a gift. That is what makes it special.",
   "Nao e uma troca. E um presente. E isso que o torna especial."),
 N("Reward", "Recompensa", "You got the Lucky Charm and the card Kuriboh.",
   "Voce ganhou o Amuleto da Sorte e a carta Kuriboh."),
 N("Stamp", "Selo", "A stamp glows on your Stamp Card - Given.",
   "Um selo brilha no seu Cartao de Selos - Dado."),
])
sc("dk1_teana_lose", "Teana wins.", [
 X("teana", "Hehe, I won! Dishes after the festival. Try again, {name}!",
   "Hehe, eu ganhei! Louca depois do festival. Tente de novo, {name}!"),
])
sc("dk1_teana_after", "Teana, charm given.", [
 X("teana", "Come and see me before you go, ok? And take care of that charm.",
   "Venha me ver antes de partir, ta? E cuide bem desse amuleto."),
])
sc("dk1_date_palm", "Date palm - dates for Teana.", [
 H("The palm is full of ripe dates. Shake, shake, shake!",
   "A palmeira esta cheia de tamaras maduras. Sacode, sacode, sacode!"),
 H("Plop, plop, plop! A whole basket of sweet dates.",
   "Plop, plop, plop! Uma cesta inteira de tamaras doces."),
 N("You got", "Voce ganhou", "You got Dates.", "Voce ganhou Tamaras."),
])
sc("dk1_date_palm_idle", "Date palm, no errand or already picked.", [
 H("Ripe dates. Teana would love some. Maybe I should ask her first.",
   "Tamaras maduras. A Teana ia adorar. Talvez eu deva perguntar a ela primeiro."),
])
sc("dk1_river_fill", "River - fill the jug.", [
 H("The river is cool and clear. Glug, glug, glug.",
   "O rio e fresco e limpo. Glub, glub, glub."),
 N("You got", "Voce ganhou", "You got River Water.", "Voce ganhou Agua do Rio."),
])
sc("dk1_river_idle", "River, nothing to fill.", [
 H("A clear river. The fish stare at me as if I owe them money.",
   "Um rio limpo. Os peixes me olham como se eu devesse dinheiro."),
])
sc("dk1_guard_block", "Guard, stage 3 - bridge closed.", [
 X("guard", "Orders - nobody crosses the bridge today. Not after that poster business.",
   "Ordens - ninguem cruza a ponte hoje. Nao depois daquele caso do cartaz."),
 X("guard", "Unless you have a very good reason. And a very full card.",
   "A nao ser que tenha um motivo muito bom. E um cartao bem cheio."),
])
sc("dk1_bridge_locked", "Bridge object, stage 3.", [
 H("The Guard blocks the bridge. I can't cross yet.",
   "O Guarda bloqueia a ponte. Ainda nao posso cruzar."),
])
sc("dk1_treasures_done", "All three stamps. Chained after the third treasure.", [
 H("The Stamp Card is full! Lost, Won and Given, all three stamps are glowing.",
   "O Cartao de Selos esta cheio! Perdido, Ganho e Dado, os tres selos brilham."),
 H("The hooded man said to come to the harbor. The road is across the bridge.",
   "O homem encapuzado disse para ir ao porto. A estrada fica depois da ponte."),
 N("Objective", "Objetivo", "Cross the bridge to the harbor. The Guard will let you pass.",
   "Cruze a ponte ate o porto. O Guarda vai deixar voce passar."),
])
sc("dk1_guard_open", "Guard, stage 4-5 - lets the hero pass.", [
 X("guard", "That glowing card... is that a full Star Passage card? In twenty years I never saw one!",
   "Aquele cartao brilhante... e uma Passagem Estelar cheia? Em vinte anos nunca vi!"),
 X("guard", "Go on. The bridge is yours. Be careful, {name}.",
   "Va em frente. A ponte e sua. Cuidado, {name}."),
])
sc("dk1_bridge_cross", "Crossing the bridge to the harbor.", [
 H("Across the bridge and down the golden road. I smell salt in the air.",
   "Cruzo a ponte e desco a estrada dourada. Sinto cheiro de sal no ar."),
 N("The Harbor", "O Porto", "Creaking ropes and gulls. A gate, and an empty pier beyond it.",
   "Cordas rangendo e gaivotas. Um portao e um cais vazio depois dele."),
])
sc("dk1_bridge_back", "Walking back to the village.", [
 H("Back across the bridge, to the village.", "Volto pela ponte, para a vila."),
])

# ---------------------------------------------------------------- harbor
sc("dk1_inspector_pre", "Harbor inspector (Mage Soldier) - gate exam.", [
 X("soldier", "Halt, traveler. This pier is closed for the Kingdom ship.",
   "Alto, viajante. Este cais esta fechado para o navio do Reino."),
 H("I have a Stamp Card with three stamps.", "Tenho um Cartao de Selos com tres selos."),
 X("soldier", "Impressive. But anyone can collect stamps. Duelists must pass the Harbor Exam.",
   "Impressionante. Mas qualquer um junta selos. Duelistas precisam passar no Exame do Porto."),
 X("soldier", "Beat me and the gate opens. Lose and go practice. Duel?",
   "Venca e o portao abre. Perca e va treinar. Duelar?", True),
])
sc("dk1_inspector_win", "Inspector beaten.", [
 X("soldier", "Excellent! The gate is open. The Courier is waiting at the end of the pier.",
   "Excelente! O portao esta aberto. O Mensageiro espera no fim do cais."),
 N("Reward", "Recompensa", "You got the card Warrior of Tradition.",
   "Voce ganhou a carta Warrior of Tradition."),
 N("Objective", "Objetivo", "Walk to the end of the pier and meet the Courier.",
   "Va ate o fim do cais e encontre o Mensageiro."),
])
sc("dk1_inspector_lose", "Inspector wins.", [
 X("soldier", "Not today. Go practice and come back, recruit.",
   "Hoje nao. Va treinar e volte, recruta."),
])
sc("dk1_inspector_after", "Inspector, after.", [
 X("soldier", "Go ahead, the pier is waiting. Good luck over the sea.",
   "Pode ir, o cais espera. Boa sorte no mar."),
])
sc("dk1_gate_locked", "Harbor gate object, before the exam.", [
 H("The gate is shut. The Inspector stands right in front of it.",
   "O portao esta fechado. O Inspetor esta bem na frente dele."),
])
sc("dk1_shadi_pre", "Shadi reveals himself - the Courier's trial.", [
 X("shadi", "You came. I am Shadi, Pegasus's messenger. And yes, I was the hooded man.",
   "Voce veio. Sou Shadi, mensageiro de Pegasus. E sim, eu era o homem encapuzado."),
 H("I knew that voice was familiar!", "Eu sabia que aquela voz era familiar!"),
 X("shadi", "You did not. Do not lie to a spirit. The three stamps - Memory, Courage, Kindness.",
   "Nao sabia. Nao minta a um espirito. Os tres selos - Memoria, Coragem, Bondade."),
 X("shadi", "A duelist needs all three. And a deck. One last test - duel me. Duel?",
   "Um duelista precisa dos tres. E de um baralho. Um ultimo teste - duele comigo. Duelar?", True),
])
sc("dk1_shadi_win", "Shadi beaten - the Passage and the first star.", [
 X("shadi", "Your cards are loyal and your heart is true. The Star Passage is yours.",
   "Suas cartas sao leais e seu coracao e verdadeiro. A Passagem Estelar e sua."),
 N("Far Away", "Ao Longe", "On the far breakwater, a robed figure glows green and looks at your Star Passage.",
   "No quebra-mar distante, uma figura de manto brilha em verde e olha a sua Passagem Estelar."),
 X("shadi", "Hm. Someone has read your Passage. Ignore him. He only reads.",
   "Hum. Alguem leu a sua Passagem. Ignore. Ele so le."),
 H("Who is 'he'?", "Quem e 'ele'?"),
 X("shadi", "A reader. He never turns a page for you. Back to your Passage.",
   "Um leitor. Ele nunca vira a pagina por voce. Volte a sua Passagem."),
 X("shadi", "Invited duelists enter with three stars. Passage duelists enter with only one.",
   "Duelistas convidados entram com tres estrelas. Os da Passagem entram com apenas uma."),
 H("One star? That is hardly anything!", "Uma estrela? Isso e quase nada!"),
 X("shadi", "It is all you need to begin. Win a duel, take a star. Lose and one goes. At zero, you go home.",
   "E tudo que precisa. Vencer rende uma estrela. Perder custa uma. Com zero, volta pra casa."),
 X("shadi", "Before each star duel you pick the wager. Lose, and your rival keeps it.",
   "Antes de cada duelo de estrelas voce escolhe a aposta. Perdeu, o rival fica com ela."),
 X("shadi", "If your last star is lost, there is no camp and no second chance. Your journey ends there.",
   "Se a ultima estrela se for, nao ha acampamento nem segunda chance. A jornada acaba ali."),
 H("Game over, then. I will never bet my last star lightly.", "Game over, entao. Nunca vou apostar a ultima a toa."),
 X("shadi", "Ten stars open the castle. Pegasus waits at the top. Your friends came to see you off.",
   "Dez estrelas abrem o castelo. Pegasus espera no topo. Seus amigos vieram se despedir."),
 N("Reward", "Recompensa", "You got the Star Passage, a Star Chip and the card Illusionist Faceless Mage.",
   "Voce ganhou a Passagem Estelar, uma Ficha de Estrela e a carta Illusionist Faceless Mage."),
 N("Stars", "Estrelas", "You have 1 star. The white ship arrives at the pier.",
   "Voce tem 1 estrela. O navio branco chega ao cais."),
 N("Objective", "Objetivo", "Say goodbye to Simon, Teana and Jono, then board the ship.",
   "Despeca-se de Simon, Teana e Jono e embarque no navio."),
])
sc("dk1_shadi_lose", "Shadi wins.", [
 X("shadi", "Your heart is willing but your deck needs work. Try again, young one.",
   "Seu coracao quer, mas seu baralho precisa de trabalho. Tente de novo, jovem."),
])
sc("dk1_simon_farewell", "Simon at the pier - the confession.", [
 X("simon", "So the ship is real. I'm too old for sea voyages, but my heart sails with you.",
   "Entao o navio e real. Estou velho para viagens, mas meu coracao vai com voce."),
 X("simon", "I must confess something. Who do you think wrote to Pegasus?",
   "Preciso confessar algo. Quem voce acha que escreveu para Pegasus?"),
 H("YOU did?!", "VOCE escreveu?!"),
 X("simon", "Pegasus and I were friends once. We argued about cards. He built an island, I built a village.",
   "Pegasus e eu fomos amigos. Brigamos por cartas. Ele fez uma ilha, eu uma vila."),
 X("simon", "He asked for my best student. I said I'd think about it. Then you showed up with that deck.",
   "Ele pediu meu melhor aluno. Disse que ia pensar. Ai voce apareceu com aquele baralho."),
 X("simon", "Tell him Simon says hello. And that he still owes me a card. Take this one, my first.",
   "Diga que Simon mandou ola. E que ele ainda me deve uma carta. Leve esta, minha primeira."),
 N("Reward", "Recompensa", "You got the card Mystical Elf from Simon.",
   "Voce ganhou a carta Mystical Elf de Simon."),
])
sc("dk1_simon_after", "Simon at the pier, after the farewell.", [
 X("simon", "Go. And remember - stars are only numbers. Cards are only paper. People matter.",
   "Va. E lembre - estrelas sao so numeros. Cartas sao so papel. Pessoas importam."),
])
sc("dk1_teana_farewell", "Teana at the pier.", [
 X("teana", "Take care! I'm not crying, it's the sea breeze! Bring back a BIG story.",
   "Se cuida! Nao estou chorando, e a brisa do mar! Traga uma historia GRANDE."),
 X("teana", "I'll keep my golden star safe until you're back. Don't lose that charm!",
   "Vou guardar minha estrela dourada ate voce voltar. Nao perca o amuleto!"),
])
sc("dk1_teana_after_farewell", "Teana, after.", [
 X("teana", "Go on, before I start crying for real. Hehe.",
   "Va logo, antes que eu chore de verdade. Hehe."),
])
sc("dk1_jono_farewell", "Jono at the pier.", [
 X("jono", "So you got the Passage! Of course you did. Heh.",
   "Entao voce pegou a Passagem! Claro que pegou. Heh."),
 X("jono", "Don't think I'm giving up. I have a raft, three barrels and a dream.",
   "Nao pense que desisti. Tenho uma jangada, tres barris e um sonho."),
 H("Jono, you can't swim.", "Jono, voce nao sabe nadar."),
 X("jono", "Details! See you on the island, {name}!",
   "Detalhes! Nos vemos na ilha, {name}!"),
])
sc("dk1_jono_after_farewell", "Jono, after.", [
 X("jono", "Raft, barrels, dream. Easy. Go, I'll catch up!",
   "Jangada, barris, sonho. Facil. Va, eu alcanco voce!"),
])
sc("dk1_gangway_locked", "Gangway before all three goodbyes.", [
 H("My friends are still here. I should say goodbye before I leave.",
   "Meus amigos ainda estao aqui. Devo me despedir antes de partir."),
])
sc("dk1_board", "Boarding the ship.", [
 N("All Aboard", "Todos a bordo", "A horn blows. A white ship with a golden eye on its sail waits at the pier.",
   "Uma buzina soa. Um navio branco com um olho dourado na vela espera no cais."),
 H("Goodbye, home town. I'll be back with stories.",
   "Adeus, minha vila. Volto com historias."),
 N("Objective", "Objetivo", "Look around the ship and talk to the lady on deck.",
   "Olhe o navio e fale com a moca no convez."),
])

# ---------------------------------------------------------------- ship deck
sc("dk1_mai_rules", "Mai on deck - the star rules (and the rival tease).", [
 X("mai", "Well, well. A rookie from the sand. Cute. Where are your friends?",
   "Ora, ora. Um novato da areia. Fofo. Cade seus amigos?"),
 H("I came alone. I think. Who are you?", "Vim {sozinho|sozinha}. Acho. Quem e voce?"),
 X("mai", "Mai Valentine. Harpie Ladies and bad manners. Let me guess - Passage, one star?",
   "Mai Valentine. Harpie Ladies e ma educacao. Deixa eu adivinhar - Passagem, uma estrela?"),
 X("mai", "Oh sweetie. Here are the rules so you don't cry later. Win a duel, take one star.",
   "Ah, queridinho. Aqui vao as regras para voce nao chorar depois. Venca, leve uma estrela."),
 X("mai", "Lose a duel, give one up. Zone masters are worth two stars. Ten stars open the castle.",
   "Perca, entregue uma. Mestres de zona valem duas estrelas. Dez estrelas abrem o castelo."),
 X("mai", "No stars left? Pegasus's men send you home. Do not let that happen.",
   "Sem estrelas? Os homens de Pegasus mandam voce pra casa. Nao deixe acontecer."),
 H("Thanks for the tips.", "{Obrigado|Obrigada} pelas dicas."),
 X("mai", "Don't thank me. We'll duel soon. And I won't go easy on you.",
   "Nao agradeca. Vamos duelar logo. E nao vou pegar leve."),
])
sc("dk1_mai_after", "Mai, after the rules.", [
 X("mai", "Look at the sea. Last time you can enjoy it before the fun starts.",
   "Olhe o mar. Ultima vez que voce pode aproveitar antes da diversao comecar."),
])
sc("dk1_inseto_early", "InsetoKaiba, before Mai's rules.", [
 X("inseto", "STOP RIGHT THERE, bug! Talk to the lady first. I want an audience.",
   "PARE AI, inseto! Fale com a dama primeiro. Quero plateia."),
])
sc("dk1_inseto_pre", "InsetoKaiba - the arrogant bug-lord. Optional duel on the ship.", [
 X("inseto", "HAHAHA! Look at all these little bugs crawling onto MY ship!",
   "HAHAHA! Olhem quantos insetinhos subindo no MEU navio!"),
 H("Who are you calling a bug? And it's not your ship.",
   "Quem voce esta chamando de inseto? E o navio nao e seu."),
 X("inseto", "I am InsetoKaiba! Champion! Bug collector! Owner of the most unbeatable deck ever made!",
   "Eu sou InsetoKaiba! Campeao! Colecionador de insetos! Dono do baralho mais imbativel ja feito!"),
 X("inseto", "Nobody has ever touched it. Not once. I checked. Twice.",
   "Ninguem nunca encostou nele. Nenhuma vez. Eu conferi. Duas vezes."),
 X("inseto", "Face me, little larva, and learn your place in the food chain. Duel?",
   "Enfrente-me, larvinha, e aprenda seu lugar na cadeia alimentar. Duelar?", True),
])
sc("dk1_inseto_win", "InsetoKaiba beaten.", [
 X("inseto", "WHAT?! Impossible! I am InsetoKaiba! My deck is UNBEATABLE!",
   "O QUE?! Impossivel! Eu sou InsetoKaiba! Meu baralho e IMBATIVEL!"),
 H("It was beatable. Just now.", "Foi batido. Agorinha."),
 X("inseto", "A glitch! A bug in the system! ... And I am the only bug allowed here!",
   "Um defeito! Um bug no sistema! ... E eu sou o unico bug permitido aqui!"),
 X("inseto", "Fine. Take this, you mildly impressive beetle. I will remember your name.",
   "Tudo bem. Leve isto, besouro minimamente impressionante. Vou lembrar do seu nome."),
 N("Reward", "Recompensa", "You got the Golden Bug Pin and the card Javelin Beetle.",
   "Voce ganhou o Pin do Inseto Dourado e a carta Javelin Beetle."),
])
sc("dk1_inseto_lose", "InsetoKaiba wins.", [
 X("inseto", "HAHAHA! Squashed! Another bug for my collection! Come back when you grow wings, larva.",
   "HAHAHA! Esmagado! Mais um inseto pra minha colecao! Volte quando tiver asas, larva."),
])
sc("dk1_inseto_after", "InsetoKaiba, after.", [
 X("inseto", "You again? Shoo, shoo! I'm rehearsing my victory speech. It is very long.",
   "Voce de novo? Xo, xo! Estou ensaiando meu discurso de vitoria. E muito longo."),
])
sc("dk1_barrel", "Suspicious barrel on deck.", [
 H("A barrel on the deck. It smells like... date cakes?",
   "Um barril no convez. Cheira a... bolinhos de tamara?"),
 N("Barrel", "Barril", "The barrel whispers - 'Shhh...' and giggles.",
   "O barril sussurra - 'Shhh...' e da risadinha."),
])
sc("dk1_bow_wait", "Ship bow before talking to Mai.", [
 H("The sea is wide. Maybe I should talk to the lady on deck first.",
   "O mar e imenso. Talvez eu deva falar com a dama no convez primeiro."),
])
sc("dk1_arrival", "End of chapter 1 - the island appears.", [
 N("Up High", "La no Alto", "At the top of the mast, a robed figure sits in a green shimmer, watching the island.",
   "No topo do mastro, uma figura de manto senta num brilho verde, olhando a ilha."),
 H("Mai, who is that up on the mast?", "Mai, quem e aquele no mastro?"),
 X("mai", "Where? Nobody is up there, sweetie. Too much sun.",
   "Onde? Nao tem ninguem la, queridinho. Sol demais."),
 N("Up High", "La no Alto", "The green flicker goes out. The mast is empty.",
   "O brilho verde se apaga. O mastro esta vazio."),
 N("Mist", "Neblina", "The mist parts. Towers, flags and a castle with a giant eye on its tallest spire.",
   "A neblina se abre. Torres, bandeiras e um castelo com um olho gigante na torre mais alta."),
 H("Duelist Kingdom. One star. Ten to go. Let's play.",
   "Reino dos Duelistas. Uma estrela. Dez para chegar. Vamos jogar."),
 N("End of Chapter 1", "Fim do Capitulo 1", "Chapter 2 - The Shore of Illusions",
   "Capitulo 2 - A Costa das Ilusoes"),
])

sc("dk1_mago_glyph", "Cistern wall glyph (observer appearance 2). Never helps.", [
 N("Wall", "Parede", "Green characters flicker on the wall, like a window into something else.",
   "Letras verdes piscam na parede, como uma janela para outra coisa."),
 H("I can't read it. Something like 'observe... do not edit'.",
   "Nao consigo ler. Algo como 'observar... nao editar'."),
 N("Wall", "Parede", "The glyphs fade. Nothing in the room has changed.",
   "As letras somem. Nada na sala mudou."),
])
sc("dk1_mago_glyph_after", "Cistern wall, glyph already seen.", [
 H("Plain old stone. Whatever was written here has gone quiet.",
   "Pedra velha e comum. O que estava escrito aqui ficou quieto."),
])
sc("dk1_bakura_glyph", "Bakura mentions the green writing.", [
 X("bakura", "The green writing on the wall? It was here before me.",
   "A escrita verde na parede? Ja estava aqui antes de mim."),
 X("bakura", "It never helps and never harms. It only watches. I like it. Good company.",
   "Nunca ajuda e nunca atrapalha. So observa. Eu gosto. Boa companhia."),
])

# ---------------------------------------------------------------- optional Duel Academy
sc("dk1_academy_intro", "Nabil opens his informal Duel Academy in the village plaza.", [
 X("academy_teacher", "Hello! I am Nabil. No title, really. I just enjoy teaching new duelists.",
   "Ola! Sou Nabil. Sem titulo, na verdade. Eu so gosto de ensinar novos duelistas."),
 X("academy_teacher", "This patch of sand is my Duel Academy. Tuition is free and shoes are optional.",
   "Este pedaco de areia e minha Academia de Duelo. E gratis e sapatos sao opcionais."),
 X("academy_teacher", "Five short classes, then a practice duel. Come back for each new class.",
   "Cinco aulas curtas e um duelo pratico. Volte para cada nova aula."),
 N("Duel Academy", "Academia de Duelo", "Class unlocked - turns, cards and battle.",
   "Aula liberada - turnos, cartas e batalha."),
])

sc("dk1_academy_basics", "Academy class 1: the Forbidden Memories turn.", [
 X("academy_teacher", "Class one - the rhythm of a duel. Both duelists begin with 8000 Life Points.",
   "Aula um - o ritmo do duelo. Cada duelista comeca com 8000 Pontos de Vida."),
 X("academy_teacher", "Your hand refills to five each turn. You must play one card or one ordered combination.",
   "Sua mao volta a ter cinco cartas por turno. Jogue uma carta ou uma combinacao ordenada."),
 X("academy_teacher", "There are no tributes here. A monster you just played can attack on that same turn.",
   "Aqui nao ha tributos. Um monstro que acabou de baixar pode atacar no mesmo turno."),
 X("academy_teacher", "Each upright monster may attack once per turn. You choose the order of those attacks.",
   "Cada monstro de pe ataca uma vez por turno. Voce escolhe a ordem dos ataques."),
 X("academy_teacher", "Attack upright. Turn sideways to defend. Press Start to end your turn.",
   "Ataque de pe. Vire de lado para defender. Aperte Start para encerrar."),
 X("academy_teacher", "With no enemy monster, you attack Life Points directly. Empty them and you win.",
   "Sem monstro inimigo, o ataque acerta os Pontos de Vida. Zere todos para vencer."),
 N("Class 1", "Aula 1", "Complete. Next class - Guardian Stars.",
   "Concluida. Proxima aula - Guardioes."),
])

sc("dk1_academy_guardians", "Academy class 2: Guardian Star cycles and their 500 point swing.", [
 X("academy_teacher", "Each monster offers two Guardian Stars. Choose one when you summon it.",
   "Cada monstro tem dois Guardioes. Escolha um quando invocar."),
 X("academy_teacher", "Mars beats Jupiter, then Saturn, Uranus, Pluto, Neptune, then Mars.",
   "Marte vence Jupiter, depois Saturno, Urano, Plutao, Netuno e Marte."),
 X("academy_teacher", "Second cycle - Mercury beats Sun, Sun beats Moon, Moon beats Venus, and Venus beats Mercury.",
   "Segundo ciclo - Mercurio vence Sol, Sol vence Lua, Lua vence Venus, e Venus vence Mercurio."),
 X("academy_teacher", "Only neighbors in the same cycle matter. Advantage swings the battle by 500 points.",
   "So vizinhos do mesmo ciclo importam. A vantagem muda a batalha em 500 pontos."),
 X("academy_teacher", "Check the enemy star before attacking. A weaker monster can win with the right Guardian.",
   "Veja o Guardiao inimigo antes de atacar. Um monstro menor pode vencer com a escolha certa."),
 N("Class 2", "Aula 2", "Complete. Next class - fields and terrain.",
   "Concluida. Proxima aula - campos e terreno."),
])

sc("dk1_academy_fields", "Academy class 3: all six terrain cards and type bonuses.", [
 X("academy_teacher", "A field card changes the terrain for both duelists until another field replaces it.",
   "Uma carta de campo muda o terreno dos dois duelistas ate outro campo substituir."),
 X("academy_teacher", "A favored type gains 500 ATK and DEF. A harmed type loses 500 ATK and DEF.",
   "Um tipo favorecido ganha 500 ATK e DEF. Um tipo ferido perde 500 ATK e DEF."),
 X("academy_teacher", "Forest helps Beasts, Beast-Warriors, Insects and Plants.",
   "Forest ajuda Feras, Guerreiros-Fera, Insetos e Plantas."),
 X("academy_teacher", "Mountain helps Dragons, Winged Beasts and Thunder monsters.",
   "Mountain ajuda Dragoes, Feras Aladas e monstros Trovao."),
 X("academy_teacher", "Wasteland helps Zombies, Dinosaurs and Rocks. Sogen helps Warriors and Beast-Warriors.",
   "Ermos ajuda Zumbi, Dino e Rocha. Sogen ajuda Guerreiro e Guerreiro-Fera."),
 X("academy_teacher", "Umi helps sea types, Aqua and Thunder, but hurts Machines and Pyro monsters.",
   "Umi ajuda tipos marinhos, Aqua e Trovao, mas fere Maquinas e monstros Pyro."),
 X("academy_teacher", "Yami helps Spellcasters and Fiends, but hurts Fairies. A field can help your rival too.",
   "Yami ajuda Magos e Demonios, mas fere Fadas. Um campo tambem pode ajudar seu rival."),
 N("Class 3", "Aula 3", "Complete. Next class - raising ATK and DEF.",
   "Concluida. Proxima aula - aumentar ATK e DEF."),
])

sc("dk1_academy_power", "Academy class 4: equips and stacking stat bonuses.", [
 X("academy_teacher", "Equip cards fit only certain monsters. Combine a valid equip with its monster to use it.",
   "Equipamentos servem so em certos monstros. Combine um equipamento valido com o monstro."),
 X("academy_teacher", "Most equips add 500 ATK and DEF. Megamorph adds 1000. Several equips can stack.",
   "A maioria soma 500 ATK e DEF. Megamorph soma 1000. Varios equipamentos acumulam."),
 X("academy_teacher", "You may combine them in your hand or play one onto your monster already on the field.",
   "Combine na mao ou jogue o equipamento sobre seu monstro que ja esta no campo."),
 X("academy_teacher", "An invalid equip is discarded. Test safely, and remember which monsters accept each one.",
   "Um equipamento invalido e descartado. Teste com cuidado e lembre quem aceita cada um."),
 X("academy_teacher", "Equip and terrain bonuses stack. Guardian advantage adds its own 500 during battle.",
   "Equipamento e terreno acumulam. A vantagem de Guardiao soma seus 500 na batalha."),
 N("Class 4", "Aula 4", "Complete. Next class - wild fusions.",
   "Concluida. Proxima aula - fusoes malucas."),
])

sc("dk1_academy_fusions", "Academy class 5: selecting and resolving ordered fusion chains.", [
 X("academy_teacher", "Now the fun part. In your hand, press Up to number two or more cards in order.",
   "Agora a parte divertida. Na mao, aperte Cima para numerar duas ou mais cartas em ordem."),
 X("academy_teacher", "Confirm. The first two combine. Their survivor meets the third, then the next.",
   "Confirme. As duas primeiras combinam. O resultado encontra a terceira e segue."),
 X("academy_teacher", "Some recipes are exact. Many use types and strength. Dragon plus Thunder is a famous path.",
   "Ha receitas exatas e outras por tipo e forca. Dragao mais Trovao e famosa."),
 X("academy_teacher", "If two monsters fail to fuse, the first is lost and the second stays. Order matters a lot.",
   "Se dois monstros falham, o primeiro se perde e o segundo fica. A ordem importa muito."),
 X("academy_teacher", "You can also play a card onto your field monster to fuse or equip it in the same zone.",
   "Voce tambem pode jogar sobre seu monstro no campo para fundir ou equipar na mesma zona."),
 X("academy_teacher", "Experiment. The strangest chains often turn a weak hand into one enormous monster.",
   "Experimente. As cadeias mais estranhas podem transformar uma mao fraca num monstro enorme."),
 N("Class 5", "Aula 5", "Complete. Return for Nabil's practice duel.",
   "Concluida. Volte para o duelo pratico do Nabil."),
])

sc("dk1_academy_exam", "Nabil offers the optional practice duel after every class.", [
 X("academy_teacher", "You know turns, Guardians, fields, equips and fusion chains. Time for the sand exam.",
   "Voce conhece turnos, Guardioes, campos, equipamentos e fusoes. Hora da prova na areia."),
 X("academy_teacher", "My deck is simple. Try a fusion, watch the stars, and use the field if it favors you.",
   "Meu baralho e simples. Tente fundir, veja os Guardioes e use o campo se ele ajudar."),
 X("academy_teacher", "No entry fee and no shame in losing. Ready for your practice duel?",
   "Sem taxa e sem vergonha de perder. Pronto para o duelo pratico?", True),
])

sc("dk1_academy_win", "The hero graduates from Nabil's optional Duel Academy.", [
 X("academy_teacher", "Excellent! You read the board instead of staring only at the biggest ATK number.",
   "Excelente! Voce leu a mesa em vez de olhar so para o maior numero de ATK."),
 X("academy_teacher", "Academy complete. I will stay here if you want a summary and another practice duel.",
   "Academia concluida. Ficarei aqui se quiser um resumo e outro duelo pratico."),
 N("Duel Academy", "Academia de Duelo", "Training complete. Professor Nabil remains available in the village.",
   "Treino concluido. Professor Nabil continua disponivel na vila."),
])

sc("dk1_academy_lose", "Nabil wins a practice duel and encourages another attempt.", [
 X("academy_teacher", "Good practice. A loss costs nothing here, and now you know where your plan broke.",
   "Boa pratica. Perder nao custa nada aqui, e agora voce sabe onde seu plano quebrou."),
 X("academy_teacher", "Change one thing, not the whole deck. Then come back and try again.",
   "Mude uma coisa, nao o baralho inteiro. Depois volte e tente de novo."),
])

sc("dk1_academy_review", "Post-graduation summary and repeatable practice duel.", [
 X("academy_teacher", "Quick review - play one card or ordered chain, then battle and press Start to end.",
   "Resumo - jogue uma carta ou cadeia ordenada, batalhe e aperte Start para encerrar."),
 X("academy_teacher", "Guardian advantage swings 500. Terrain changes ATK and DEF. Valid equips stack.",
   "Guardiao muda 500. Terreno muda ATK e DEF. Equipamentos validos acumulam."),
 X("academy_teacher", "Fusion chains resolve in numbered order. A failed pair can discard the first card.",
   "Fusoes seguem a ordem numerada. Uma dupla que falha pode descartar a primeira carta."),
 X("academy_teacher", "That is the whole academy. Want another practice duel?",
   "Essa e toda a academia. Quer outro duelo pratico?", True),
])

sc("dk1_academy_rematch_win", "Nabil loses a post-graduation practice rematch.", [
 X("academy_teacher", "Sharp play. Class dismissed until you feel like shuffling again.",
   "Jogada afiada. Aula encerrada ate voce querer embaralhar de novo."),
])

# ---------------------------------------------------------------- chapter 2 (the Shore of Illusions): dk_chapter2.py
import dk_chapter2 as _C2
_C2.scripts(sc, H, X, N)

# ---------------------------------------------------------------- chapter 3 (the Forest of Whispers): dk_chapter3.py
import dk_chapter3 as _C3
_C3.scripts(sc, H, X, N)

# ---------------------------------------------------------------- chapter 4 (the Mountain Pass): dk_chapter4.py
import dk_chapter4 as _C4
_C4.scripts(sc, H, X, N)

# ---------------------------------------------------------------- chapter 5 (the Meadow Maze): dk_chapter5.py
import dk_chapter5 as _C5
_C5.scripts(sc, H, X, N)

# ---------------------------------------------------------------- chapter 6 (the Desert of Lost Stars): dk_chapter6.py
import dk_chapter6 as _C6
_C6.scripts(sc, H, X, N)

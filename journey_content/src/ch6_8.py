"""Chapters 6-8 (new), the Cockatiel side duelist and the Atos mirror duelist (new)."""
from common import pg, nar, obj, rew

def S(id, chapter, desc, pages):
    return {"id": id, "legacy_id": None, "chapter": chapter, "desc": desc, "pages": pages}

SCRIPTS = [
 # ------------------------------------------------------------------ chapter 6
 S("c6_arrival", 6, "Arrival at the Temple Crossroads (plays right after c5_end__c6_intro). Simon hands over the Puzzle.", [
   pg("atos", "Hot sand again! The portal dropped me at an old crossroads."),
   pg("simon", "{name}! Isis sent word that you were coming. I kept the Puzzle safe."),
   rew("You got the Millennium Puzzle. The Prince sleeps inside it."),
   pg("simon", "Heishin only emptied the vault. The real Items were hidden in five temples."),
   pg("simon", "Each temple has a Mage who guards one. Beat the Mages and they will let you take it."),
   pg("atos", "Sea, forest, mountain, desert and meadow. Got it. Let's go."),
   obj("Visit the five temples and win their Items. Then open the Labyrinth gate.")]),
 S("c6_simon_hub", 6, "Simon at the crossroads while temples remain.", [
   pg("simon", "Heishin's men were seen near the temples. Hurry, but do not rush your duels.")]),
 S("c6_simon_hub_done", 6, "Simon at the crossroads once all five temples are won.", [
   pg("simon", "You have all five Items! Go to the Labyrinth gate. I will guard the crossroads.")]),

 S("c6_ocean_pre", 6, "Ocean Mage, Sea Temple shore (first Sea duel).", [
   pg("ocean_mage", "Halt, stranger! The sea does not open its temple to dry-footed visitors."),
   pg("atos", "I only want to borrow what the temple guards. Duel me."),
   pg("ocean_mage", "The tide will decide. Duel?", ask=True)]),
 S("c6_ocean_win", 6, "Ocean Mage beaten.", [
   pg("ocean_mage", "The tide has turned... Go in. High Mage Secmeton waits inside."),
   rew("You got the card Aqua Dragon."),
   obj("Enter the Sea Temple and face High Mage Secmeton.")]),
 S("c6_ocean_lose", 6, "Ocean Mage wins.", [pg("ocean_mage", "The sea washes you back to shore. Try again.")]),
 S("c6_ocean_done", 6, "Ocean Mage, after his duel.", [pg("ocean_mage", "Secmeton waits inside. The sea lets you pass.")]),
 S("c6_secmeton_locked", 6, "Sea Temple inner door, before the Ocean Mage was beaten.", [
   pg("atos", "A wall of water blocks the inner door. The Ocean Mage must let me in first.")]),
 S("c6_secmeton_pre", 6, "Secmeton asks for a duel.", [
   pg("secmeton", "So you are the one who walks through time. The waters whispered about you."),
   pg("atos", "Then you know why I am here. I need the Sea Tablet."),
   pg("secmeton", "Words are shallow. Show me with cards. Duel?", ask=True)]),
 S("c6_secmeton_win", 6, "Secmeton beaten.", [
   pg("secmeton", "You swim well, traveler. The Sea Tablet is yours."),
   pg("secmeton", "It fits the Labyrinth gate. Heishin's men want it badly."),
   rew("You got the Sea Tablet and the card Suijin."),
   obj("Four temples remain - Forest, Mountain, Desert and Meadow.")]),
 S("c6_secmeton_lose", 6, "Secmeton wins.", [pg("secmeton", "Too shallow. Dive deeper and come back.")]),
 S("c6_secmeton_done", 6, "Secmeton, after his duel.", [pg("secmeton", "Guard the Tablet well. The sea remembers.")]),

 S("c6_anubisius_pre", 6, "Anubisius asks for a duel (Forest Temple).", [
   pg("anubisius", "Quiet, stranger. The old trees do not like noise."),
   pg("atos", "I came for the Millennium Key. The Prince's life is at stake."),
   pg("anubisius", "The forest gives nothing for free. Duel?", ask=True)]),
 S("c6_anubisius_win", 6, "Anubisius beaten.", [
   pg("anubisius", "The roots yield to you. Take the Millennium Key."),
   rew("You got the Millennium Key and the card Ancient One of the Deep Forest.")]),
 S("c6_anubisius_lose", 6, "Anubisius wins.", [pg("anubisius", "The forest swallowed your cards. Try again.")]),
 S("c6_anubisius_done", 6, "Anubisius, after his duel.", [pg("anubisius", "The Key is in good hands. The trees approve.")]),

 S("c6_atenza_pre", 6, "Atenza asks for a duel (Mountain Temple).", [
   pg("atenza", "The path is steep and so is my price. Only the strong may take the Rod."),
   pg("atos", "I came through time. A mountain will not stop me."),
   pg("atenza", "Then climb! Duel?", ask=True)]),
 S("c6_atenza_win", 6, "Atenza beaten.", [
   pg("atenza", "You reached the peak. The Millennium Rod is yours."),
   rew("You got the Millennium Rod and the card Thunder Dragon.")]),
 S("c6_atenza_lose", 6, "Atenza wins.", [pg("atenza", "The mountain is cold and so am I. Climb again.")]),
 S("c6_atenza_done", 6, "Atenza, after his duel.", [pg("atenza", "Use the Rod wisely. Power is not wisdom.")]),

 S("c6_martis_pre", 6, "Martis asks for a duel (Desert Temple).", [
   pg("martis", "The sand buries those who rush. Slow down, time traveler."),
   pg("atos", "Slow down? I just crossed five thousand years."),
   pg("martis", "Then let the dunes judge you. Duel?", ask=True)]),
 S("c6_martis_win", 6, "Martis beaten.", [
   pg("martis", "The dunes bow to you. Take the Millennium Ring."),
   rew("You got the Millennium Ring and the card Mystical Sand.")]),
 S("c6_martis_lose", 6, "Martis wins.", [pg("martis", "The sand covers your footprints. Come back.")]),
 S("c6_martis_done", 6, "Martis, after his duel.", [pg("martis", "Heishin's men came by. They left empty-handed.")]),

 S("c6_kepura_pre", 6, "Kepura asks for a duel (Meadow Temple).", [
   pg("kepura", "Welcome to the meadow, little traveler! The flowers said you were coming."),
   pg("atos", "Flowers? ...Okay. I need the Millennium Scales."),
   pg("kepura", "Gently or fiercely, a duel decides. Duel?", ask=True)]),
 S("c6_kepura_win", 6, "Kepura beaten.", [
   pg("kepura", "How lovely! You duel with a kind heart. The Scales are yours."),
   rew("You got the Millennium Scales and the card Queen of Autumn Leaves.")]),
 S("c6_kepura_lose", 6, "Kepura wins.", [pg("kepura", "Oh dear. Rest among the flowers, then try again.")]),
 S("c6_kepura_done", 6, "Kepura, after her duel.", [pg("kepura", "Keep your heart balanced and the Scales will do the rest.")]),

 S("c6_gate_locked", 6, "Labyrinth gate at the crossroads, before all five Items are won.", [
   pg("atos", "The gate has five empty sockets. I need the Items from all five temples.")]),
 S("c6_end__c7_intro", 7, "Opening the Labyrinth gate: end of chapter 6, chapter 7 intro (teleport into the Labyrinth).", [
   pg("atos", "Tablet, Key, Rod, Ring and Scales... the sockets are glowing!"),
   nar("End of Chapter 6", "Chapter 7 - The Labyrinth and the Guardians"),
   pg("atos", "The gate opens onto stairs going down into the dark. Here goes nothing."),
   pg("simon", "Careful! I felt Heishin pass here. Seto went ahead to guard the way."),
   obj("Cross the Labyrinth. Beat its guardians to reach the altar.")]),

 # ------------------------------------------------------------------ chapter 7
 S("c7_lmage_pre", 7, "Labyrinth Mage asks for a duel.", [
   pg("labyrinth_mage", "A new face in the maze. Few ever walk back out."),
   pg("atos", "Then I will be one of the few."),
   pg("labyrinth_mage", "The walls shift here. So do the odds. Duel?", ask=True)]),
 S("c7_lmage_win", 7, "Labyrinth Mage beaten.", [
   pg("labyrinth_mage", "You read the maze well. Take this and move on."),
   rew("You got the card Guardian of the Labyrinth."),
   obj("Go on to the first door and face Guardian Sebek.")]),
 S("c7_lmage_lose", 7, "Labyrinth Mage wins.", [pg("labyrinth_mage", "Lost already? The maze loves new faces.")]),
 S("c7_lmage_done", 7, "Labyrinth Mage, after his duel.", [pg("labyrinth_mage", "Straight on, then left. Or right. Who knows?")]),
 S("c7_door1_locked", 7, "First door, before the Labyrinth Mage was beaten.", [
   pg("atos", "The walls keep moving. The Mage who controls them must be near.")]),
 S("c7_sebek_pre", 7, "Sebek asks for a duel.", [
   pg("sebek", "No living soul passes this door without the judgment of the gods."),
   pg("atos", "Then judge me."),
   pg("sebek", "The scales are ready. Duel?", ask=True)]),
 S("c7_sebek_win", 7, "Sebek beaten.", [
   pg("sebek", "The gods find you... acceptable. The door is open."),
   rew("You got the card Guardian of the Throne Room."),
   obj("Next door - Guardian Neku.")]),
 S("c7_sebek_lose", 7, "Sebek wins.", [pg("sebek", "Judged and found lacking. Return when you are worthy.")]),
 S("c7_sebek_done", 7, "Sebek, after his duel.", [pg("sebek", "Go. Neku waits at the next door.")]),
 S("c7_door2_locked", 7, "Second door, before Sebek was beaten.", [
   pg("atos", "Another door, but Sebek's judgment comes first.")]),
 S("c7_neku_pre", 7, "Neku asks for a duel.", [
   pg("neku", "I am Neku, keeper of the second door. Sebek judges the body. I judge the heart."),
   pg("atos", "My heart is fine. It is the rest of me that is tired."),
   pg("neku", "We will see. Duel?", ask=True)]),
 S("c7_neku_win", 7, "Neku beaten.", [
   pg("neku", "Your heart is steady. Pass, traveler."),
   rew("You got the card Rude Kaiser."),
   obj("Seto stands beyond the second door.")]),
 S("c7_neku_lose", 7, "Neku wins.", [pg("neku", "Your heart wavers. Rest, then return.")]),
 S("c7_neku_done", 7, "Neku, after his duel.", [pg("neku", "Seto waits beyond. Do not keep him waiting.")]),
 S("c7_door3_locked", 7, "Third door (Seto), before Neku was beaten.", [
   pg("atos", "This door will not budge. I must beat Neku first.")]),
 S("c7_seto2_pre", 7, "Seto asks for a duel (altar guard).", [
   pg("seto2", "You came. I had my doubts."),
   pg("atos", "I said I would find the Items."),
   pg("seto2", "I serve the Prince, not you. But today we fight on the same side."),
   pg("atos", "Then why duel?"),
   pg("seto2", "The altar will test you. I will not let the Prince rest in untested hands. Duel?", ask=True)]),
 S("c7_seto2_win", 7, "Seto beaten.", [
   pg("seto2", "Enough. I was wrong to doubt you."),
   pg("seto2", "Take the White Dragon. It chose to fight beside you."),
   rew("You got the card Blue-eyes White Dragon."),
   obj("Reach the altar and wake the Prince.")]),
 S("c7_seto2_lose", 7, "Seto wins.", [pg("seto2", "Not yet. Come back stronger.")]),
 S("c7_seto2_done", 7, "Seto, after his duel.", [pg("seto2", "The altar is ahead. I will guard your back.")]),
 S("c7_altar_locked", 7, "Altar, before Seto was beaten.", [
   pg("atos", "Seto stands in front of the altar. He will not let me through yet.")]),
 S("c7_altar_wake", 7, "Placing the Items on the altar; Heishin ambushes.", [
   pg("atos", "Ring, Rod, Key, Scales, Necklace, Eye... and the Puzzle."),
   nar("The Altar", "The seven Items glow. The Prince's soul rises from the Puzzle."),
   pg("prince", "{name}... Seto... I heard everything in my sleep. Thank you."),
   pg("seto2", "My Prince! You are free."),
   pg("heishin2", "Hahaha! You did the hard work for me. All seven Items in one room!"),
   pg("atos", "Heishin! You never give up."),
   pg("heishin2", "I gave up nothing. Duel, if you dare!", ask=True)]),
 S("c7_heishin2_retry", 7, "Heishin asks again after Atos lost (the altar scene does not replay).", [
   pg("heishin2", "Back for more? Hand over the Items!", ask=True)]),
 S("c7_heishin2_win", 7, "Heishin beaten; the Prince is free.", [
   pg("heishin2", "No... the Items! The shadow promised me..."),
   nar("The Shadow", "Heishin fades into black smoke. Something deeper stirs below."),
   pg("prince", "That was not Heishin's own power. Something older has woken."),
   rew("You got Time Stone Fragment 3 and the card Summoned Skull."),
   obj("Take the dark stairs behind the altar with the Prince.")]),
 S("c7_heishin2_lose", 7, "Heishin wins.", [pg("heishin2", "Hahaha! The Items are mine!")]),
 S("c7_prince_free", 7, "Prince, after the altar.", [
   pg("prince", "Let us go. Whatever waits below, we face it together.")]),
 S("c7_seto2_after_altar", 7, "Seto, after the altar.", [
   pg("seto2", "Heishin was a pawn. The real enemy is below. Go, I will follow.")]),
 S("c7_end__c8_intro", 8, "Taking the dark stairs: end of chapter 7, chapter 8 intro (teleport to the Final Temple).", [
   pg("atos", "The Fragments and the Items are all pulling toward the dark stairs."),
   nar("End of Chapter 7", "Chapter 8 - Nitemare"),
   pg("prince", "The Final Temple. It floats in the Shadow Realm."),
   pg("atos", "Last duel. After this, I go home."),
   obj("Reach the Final Temple and defeat Nitemare.")]),

 # ------------------------------------------------------------------ chapter 8
 S("c8_seto3_pre", 8, "Shadow-touched Seto guards the Final Temple gate.", [
   pg("seto3", "Turn back... The night does not forgive."),
   pg("atos", "Seto! That is not you talking."),
   pg("prince", "The shadow holds him. Break it with a duel, {name}!"),
   pg("seto3", "...Duel.", ask=True)]),
 S("c8_seto3_win", 8, "Seto freed.", [
   pg("seto3", "Argh... what have I done? Prince?"),
   pg("seto3", "I saw it. DarkNite wears Heishin's grudge. Nitemare sleeps above."),
   rew("You got the card Red-eyes B. Dragon."),
   obj("Beat DarkNite in the hall of shadows.")]),
 S("c8_seto3_lose", 8, "Seto wins.", [pg("seto3", "...Leave. Come back stronger.")]),
 S("c8_seto3_done", 8, "Seto, after his duel.", [pg("seto3", "Go on. I will hold the door behind you.")]),
 S("c8_hall_locked", 8, "Hall of shadows, before Seto was beaten.", [
   pg("atos", "A wall of black mist. Seto stands in my way.")]),
 S("c8_darknite_pre", 8, "DarkNite asks for a duel.", [
   pg("darknite", "The seven Items called me. Thank you for bringing them."),
   pg("prince", "{name}, I duel beside you. This world is not only mine."),
   pg("atos", "Let's finish this."),
   pg("darknite", "Two hearts against one night? Duel!", ask=True)]),
 S("c8_darknite_win", 8, "DarkNite beaten.", [
   pg("darknite", "Impossible... the dark cannot lose to the light!"),
   pg("nitemare", "You amused me, DarkNite. Now step aside."),
   rew("You got the card Zoa."),
   obj("Climb to the top and face Nitemare.")]),
 S("c8_darknite_lose", 8, "DarkNite wins.", [pg("darknite", "Nothing is lost in the dark. Not even you.")]),
 S("c8_stairs_locked", 8, "Stairs to Nitemare, before DarkNite was beaten.", [
   pg("atos", "The stairs are sealed by shadow. DarkNite is guarding them.")]),
 S("c8_nitemare_pre", 8, "Nitemare asks for a duel (final boss).", [
   pg("nitemare", "I am Nitemare. I was here before the first Item."),
   pg("nitemare", "Heishin was a puppet. The rifts, the Items... all of it was mine."),
   pg("atos", "You opened the rifts? You pulled me from my own time?"),
   pg("nitemare", "I opened every door. Close the last one yourself, if you can."),
   pg("prince", "Together, {name}! Light the way through the night!"),
   pg("atos", "Last duel. Then I am going home."),
   pg("nitemare", "Come, then. Duel!", ask=True)]),
 S("c8_nitemare_win", 8, "Nitemare beaten; the Time Stone is complete.", [
   pg("nitemare", "No... the light of seven Items..."),
   nar("The Time Stone", "The three Fragments fly together and form the complete Time Stone."),
   rew("You got the Time Stone and the legendary card Workers' Rights."),
   obj("Choose how your journey ends.")]),
 S("c8_nitemare_lose", 8, "Nitemare wins.", [pg("nitemare", "The dark takes everything. Even hope.")]),
 S("c8_choice", 8, "Ending choice. Yes -> ending_home, No -> ending_stay.", [
   pg("prince", "The Stone can send you home, {name}. Or you can stay beside us."),
   pg("atos", "Use the Time Stone to go home?", ask=True)]),
 S("ending_home", 8, "Ending A: go home.", [
   pg("atos", "Goodbye, Seto. Goodbye, Prince. Thank you for everything."),
   pg("prince", "Take this card as a memory. We will not forget you."),
   rew("You got the card Mystical Elf as a keepsake."),
   nar("Epilogue", "The Stone's light carries {name} back to the arena, one second after leaving."),
   pg("atos", "...Same arena. Same crowd. And I still have the Prince's card."),
   nar("The End", "Thank you for playing JOURNEY MODE.")]),
 S("ending_stay", 8, "Ending B: stay in Egypt.", [
   pg("atos", "I think my story is here now. I will stay."),
   pg("seto3", "Then serve beside me, priest. The Prince will need you."),
   pg("prince", "Welcome home, {name}. Egypt is your time too."),
   nar("Epilogue", "{name} became a priest of the Royal City and kept the Time Stone safe forever."),
   nar("The End", "Thank you for playing JOURNEY MODE.")]),

 # ------------------------------------------------------------------ side duelists
 S("side_cockatiel_pre", 6, "Cockatiel asks for a duel (optional, Temple Crossroads, from chapter 6).", [
   pg("cockatiel", "Tweet-tweet! Welcome, time traveler. I am Cockatiel, wandering duelist."),
   pg("atos", "Nice crest. Does your bird bite?"),
   pg("cockatiel", "Only sore losers. My flock is eager for a duel. Ready?", ask=True)]),
 S("side_cockatiel_win", 6, "Cockatiel beaten.", [
   pg("cockatiel", "Ha! Not bad. My flock is impressed."),
   pg("cockatiel", "Keep this feather. It brings luck to those who fly high."),
   rew("You got the Cockatiel Feather and the card Crimson Sunbird.")]),
 S("side_cockatiel_lose", 6, "Cockatiel wins.", [
   pg("cockatiel", "Chirp! Come back after some seeds and practice.")]),
 S("side_cockatiel_done", 6, "Cockatiel, after the duel.", [
   pg("cockatiel", "Fly high, traveler. The wind remembers you.")]),
 S("side_cockatiel_epilogue", 9, "Cockatiel, after the main story ends.", [
   pg("cockatiel", "I heard what you did out there. The whole flock is singing about it.")]),

 S("side_mirror_pre", 9, "Atos Vinicius (mirror duelist) asks for a duel (post-game, Temple Crossroads).", [
   pg("atos", "Wait... that is my face! And that looks like my deck!"),
   pg("mirror", "I am the Atos who stayed home. The rift pulled the wrong one, or maybe the right one."),
   pg("atos", "Then let's see which of us is the better duelist."),
   pg("mirror", "Fine by me. My deck works overtime. Duel?", ask=True)]),
 S("side_mirror_win", 9, "Mirror Atos beaten.", [
   pg("mirror", "Not bad... you work harder than I do."),
   rew("You got the card Hero of the East.")]),
 S("side_mirror_lose", 9, "Mirror Atos wins.", [pg("mirror", "Overtime pays off. Try again.")]),
 S("side_mirror_done", 9, "Mirror Atos, after the duel.", [pg("mirror", "Go on. I will keep the arena warm.")]),
]

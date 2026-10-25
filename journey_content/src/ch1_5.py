"""Chapters 1-5: faithful English translation of ow4/story.py (67 scripted pages groups, legacy ids 0..66)."""
from common import pg, nar, obj, rew

def S(id, legacy, chapter, desc, pages):
    return {"id": id, "legacy_id": legacy, "chapter": chapter, "desc": desc, "pages": pages}

SCRIPTS = [
 S("c1_intro", 0, 1, "Opening, right after character creation.", [
   pg("atos", "Ugh... my head. I was in a Duel Monsters tournament a second ago."),
   pg("atos", "A portal of light opened in the middle of the arena and pulled me in."),
   pg("atos", "Sand, palm trees, a river... This looks like ancient Egypt!"),
   pg("atos", "Only my deck came with me. I need someone who knows the way home."),
   obj("Talk to Simon Muran, the old sage waiting at the golden arena.")]),
 S("c1_simon_pre", 1, 1, "Simon, first talk. Last page asks Duel? Yes/No.", [
   pg("simon", "Strange clothes, {lad|lass}... But those cards are as old as our magic."),
   pg("atos", "I fell out of a portal. Do you know how I get back to my own time?"),
   pg("simon", "Maybe. Show me how you duel and I will tell you where you came from. Duel?", ask=True)]),
 S("c1_simon_win", 2, 1, "Simon beaten.", [
   pg("simon", "Impressive! You duel like a master."),
   pg("simon", "The portal that brought you is a rift in time. Only the Time Stone can close it."),
   pg("simon", "The Stone's pieces lie beyond the river, to the north. I told the bridge guard."),
   rew("You got the card Mystical Elf and a Canteen. Check your Backpack."),
   obj("Cross the river to the north. Teana and Jono want a duel too.")]),
 S("c1_simon_lose", 3, 1, "Simon wins.", [
   pg("simon", "Not bad, but you need more practice. Rest and try again.")]),
 S("c1_simon_after", 4, 1, "Simon, after he was beaten.", [
   pg("simon", "The bridge is up the road to the north. Good luck, traveler.")]),
 S("c1_teana_pre", 5, 1, "Teana asks for a duel.", [
   pg("teana", "Hi! Are you the stranger who beat Simon? Duel me?", ask=True)]),
 S("c1_teana_win", 6, 1, "Teana beaten.", [
   pg("teana", "Wow, you're really good! Take this card."),
   rew("You got the card Feral Imp.")]),
 S("c1_jono_pre", 7, 1, "Jono asks for a duel.", [
   pg("jono", "Hey, rookie! I bet my deck is stronger. Duel?", ask=True)]),
 S("c1_jono_win", 8, 1, "Jono beaten.", [
   pg("jono", "Fine, fine... you won. Here, it's yours."),
   rew("You got the card Baby Dragon.")]),
 S("c1_teana_lose", 9, 1, "Teana wins.", [pg("teana", "Hehe, I won! Come back anytime.")]),
 S("c1_jono_lose", 10, 1, "Jono wins.", [pg("jono", "Ha! Train some more and come back.")]),
 S("c1_teana_wait", 11, 1, "Teana, before Simon was beaten.", [pg("teana", "Old Simon is waiting for you at the arena.")]),
 S("c1_jono_wait", 12, 1, "Jono, before Simon was beaten.", [pg("jono", "Talk to Simon first, then we duel.")]),
 S("c1_guard_block", 13, 1, "Bridge guard, before Simon's permission.", [
   pg("guard", "Halt! Nobody crosses the river without the sage Simon Muran's permission.")]),
 S("c1_guard_ok", 14, 1, "Bridge guard, after Simon was beaten.", [
   pg("guard", "Simon allowed it? Then you may pass, traveler.")]),
 S("c1_end__c2_intro", 15, 2, "Crossing the river: end of chapter 1, chapter 2 intro.", [
   pg("atos", "The Royal City is far to the north. First I have to get past these ruins."),
   nar("End of Chapter 1", "Chapter 2 - Sand Ruins"),
   pg("atos", "Broken columns, an obelisk... and a glowing stone portal in the back!"),
   pg("atos", "There are people here. Those two are from the tournament! Did they fall into the past too?"),
   obj("Beat Rex Raptor and Weevil. Then enter the stone portal to the north.")]),
 S("c2_teana_done", 16, 2, "Teana, after her duel.", [pg("teana", "Safe travels, stranger!")]),
 S("c2_jono_done", 17, 2, "Jono, after his duel.", [pg("jono", "Next time I win!")]),
 S("c2_rex_pre", 18, 2, "Rex asks for a duel.", [
   pg("rex", "You fell here too? Great. Beating you puts me closer to going home."),
   pg("atos", "Then let's duel. The winner gets a clear path."),
   pg("rex", "My dinosaurs will crush you! Duel?", ask=True)]),
 S("c2_rex_win", 19, 2, "Rex beaten.", [
   pg("rex", "I can't believe it... I lost to a rookie!"),
   pg("rex", "Here, I found this shiny stone in the ruins. Maybe it helps you."),
   rew("You got Time Stone Fragment 1 and the card Ryu-kishin.")]),
 S("c2_rex_lose", 20, 2, "Rex wins.", [pg("rex", "Hahaha! Come back when you have real dinosaurs.")]),
 S("c2_weevil_pre", 21, 2, "Weevil asks for a duel.", [
   pg("weevil", "Hehehe. In this world nobody checks if we cheat."),
   pg("atos", "Then I'll win the right way, so you remember it."),
   pg("weevil", "My bugs disagree. Duel?", ask=True)]),
 S("c2_weevil_win", 22, 2, "Weevil beaten.", [
   pg("weevil", "Impossible! My strategy was perfect!"),
   pg("weevil", "Fine, fine... take this old torch and leave me alone."),
   rew("You got a Torch and the card Hitotsu-me Giant.")]),
 S("c2_weevil_lose", 23, 2, "Weevil wins.", [pg("weevil", "Hehehe! I knew you'd fall into my trap.")]),
 S("c2_rex_done", 24, 2, "Rex, after his duel.", [pg("rex", "Go on to the portal. I will still get my rematch.")]),
 S("c2_weevil_done", 25, 2, "Weevil, after his duel.", [pg("weevil", "Hmpf. Get lost before I change my mind.")]),
 S("c2_portal_locked", 26, 2, "Stone portal, before both duels are won.", [
   pg("atos", "The portal does not react. I think I must beat Rex and Weevil first.")]),
 S("c2_end__c3_intro", 27, 3, "Entering the portal: end of chapter 2, chapter 3 intro (teleport to the Royal City).", [
   pg("atos", "The portal glows brighter now. I'm going in!"),
   nar("End of Chapter 2", "Chapter 3 - The Palace and the Prince"),
   pg("atos", "Wow! The portal took me inside the Royal City. What a huge palace!"),
   pg("atos", "In front of the palace stand a priest and a young man who looks like a king. The Prince!"),
   obj("Talk to the priest Seto in front of the palace.")]),
 S("c3_seto_pre", 28, 3, "Seto asks for a duel.", [
   pg("seto", "A stranger with cards nobody knows. Are you a threat or a gift?"),
   pg("prince", "Seto, let him prove himself. If he loses, I will send him away myself."),
   pg("atos", "If I win, I want to know why these time rifts keep opening."),
   pg("seto", "Agreed. Prepare your deck. Duel?", ask=True)]),
 S("c3_seto_win", 29, 3, "Seto beaten.", [
   pg("seto", "Hmpf... you won. If the Prince trusts you, so will I."),
   pg("prince", "The rifts began when the priest Heishin opened the vault of the Millennium Items."),
   pg("prince", "Take the Royal Seal. It opens the palace, so you can find out what Heishin wants."),
   rew("You got the Royal Seal and the card Dark Magician."),
   obj("Enter the palace and investigate Heishin. The Mage Soldier offers a duel.")]),
 S("c3_seto_lose", 30, 3, "Seto wins.", [pg("seto", "That was it? Come back when you are ready, stranger.")]),
 S("c3_seto_done", 31, 3, "Seto, after his duel.", [pg("seto", "The palace is open to you. Do not disappoint me.")]),
 S("c3_prince_before", 32, 3, "Prince, before Seto was beaten.", [
   pg("prince", "Welcome to the Royal City, traveler. Show Seto what you can do.")]),
 S("c3_prince_after", 33, 3, "Prince, after Seto was beaten.", [
   pg("prince", "Beware of Heishin. He roams the palace halls at night.")]),
 S("c3_soldier_pre", 34, 3, "Mage Soldier asks for a duel (optional).", [
   pg("mage_soldier", "I train the palace guards. Want to test your deck against me? Duel?", ask=True)]),
 S("c3_soldier_win", 35, 3, "Mage Soldier beaten.", [
   pg("mage_soldier", "Good duel! Take this card on your journey."),
   rew("You got the card Celtic Guardian.")]),
 S("c3_soldier_lose", 36, 3, "Mage Soldier wins.", [pg("mage_soldier", "Train a bit more and come back.")]),
 S("c3_soldier_done", 37, 3, "Mage Soldier, after his duel.", [pg("mage_soldier", "The guards speak highly of you.")]),
 S("c3_door_locked", 38, 3, "Palace door, before Seto was beaten.", [
   pg("atos", "The palace door is shut. I need Seto's permission first.")]),
 S("c3_end__c4_intro", 39, 4, "Entering the palace: end of chapter 3, chapter 4 intro (teleport to the throne hall).", [
   pg("atos", "With the Royal Seal the door opened. Heishin is hiding something in here."),
   nar("End of Chapter 3", "Chapter 4 - Heishin's Coup"),
   nar("That Night", "Heishin attacked the city with his guards. The sky turned red with fire."),
   pg("atos", "This is the throne hall! Heishin is up on the throne and the Prince is surrounded!"),
   obj("Defeat Heishin in the throne hall.")]),
 S("c4_heishin_pre", 40, 4, "Heishin asks for a duel.", [
   pg("heishin", "The Millennium Items give power to those with the courage to take them. And I had it."),
   pg("atos", "You attacked the whole city for seven pieces of gold?"),
   pg("heishin", "For seven keys. And now you hand me your deck. Duel?", ask=True)]),
 S("c4_heishin_win", 41, 4, "Heishin beaten; Simon seals the Prince in the Puzzle.", [
   pg("heishin", "Impossible! A stranger beat me? This is not over!"),
   nar("What Happened", "Heishin fled through the window and took the Millennium Items with him."),
   pg("simon", "{name}! Heishin will come back for the Prince. There is only one way to protect him."),
   pg("simon", "I will keep the Prince's soul in the Millennium Puzzle. He sleeps until the time is right."),
   pg("prince", "{name}, I trust you. Find the Items and wake me when the time comes."),
   pg("simon", "Take the Millennium Necklace. It shows the future and can open a rift to your time."),
   rew("You got the Millennium Necklace and the card Gaia the Fierce Knight."),
   obj("Touch the glowing throne to travel through time.")]),
 S("c4_heishin_lose", 42, 4, "Heishin wins.", [pg("heishin", "Hahaha! Too weak. Come back when you have real courage.")]),
 S("c4_prince_hall", 43, 4, "Prince in the throne hall.", [
   pg("prince", "{name}! Heishin wants the Millennium Items. Please, stop him!")]),
 S("c4_seto_before", 44, 4, "Seto in the hall, before Heishin was beaten.", [
   pg("seto", "I protect the Prince. Go, stranger, face Heishin!")]),
 S("c4_seto_after", 45, 4, "Seto in the hall, after Heishin was beaten.", [
   pg("seto", "The Prince is kept in the Puzzle. Find the Items and bring him back.")]),
 S("c4_throne_locked", 46, 4, "Throne, before Heishin was beaten.", [
   pg("atos", "The throne is not glowing. I must defeat Heishin first.")]),
 S("c4_end__c5_intro", 47, 5, "Touching the throne: end of chapter 4, chapter 5 intro (teleport to the tournament island).", [
   pg("atos", "The Necklace is glowing with the throne. A time rift is opening!"),
   nar("End of Chapter 4", "Chapter 5 - The Tournament Out of Time"),
   pg("atos", "Wait... this is Pegasus's tournament island! Did I come back to my own time?"),
   pg("atos", "No... the sky still has rifts. The tournament got stuck between two eras."),
   obj("Beat Mai, Bandit Keith and Shadi. Then face Pegasus in front of the castle.")]),
 S("c5_mai_pre", 48, 5, "Mai asks for a duel.", [
   pg("mai", "Honey, strategy is what counts here. And a little perfume."),
   pg("atos", "Then let's see which strategy is better."),
   pg("mai", "My Harpies are ready. Duel?", ask=True)]),
 S("c5_mai_win", 49, 5, "Mai beaten.", [
   pg("mai", "Not bad, honey. You won fair and square."),
   rew("You got the card Harpie Lady.")]),
 S("c5_mai_lose", 50, 5, "Mai wins.", [pg("mai", "Hihi, come back when you learn to play.")]),
 S("c5_mai_done", 51, 5, "Mai, after her duel.", [pg("mai", "Good luck with Pegasus. He is very weird.")]),
 S("c5_keith_pre", 52, 5, "Keith asks for a duel.", [
   pg("keith", "This tournament is mine. You're just another name on my list."),
   pg("atos", "Then try to cross my name out, if you can."),
   pg("keith", "We'll see, rookie. Duel?", ask=True)]),
 S("c5_keith_win", 53, 5, "Keith beaten.", [
   pg("keith", "Grr... beginner's luck!"),
   rew("You got the card Great White.")]),
 S("c5_keith_lose", 54, 5, "Keith wins.", [pg("keith", "Hah! Go home, rookie.")]),
 S("c5_keith_done", 55, 5, "Keith, after his duel.", [pg("keith", "Don't talk to me now, rookie.")]),
 S("c5_shadi_pre", 56, 5, "Shadi asks for a duel.", [
   pg("shadi", "I am Shadi, guardian of the Millennium Items. I see you carry the Necklace."),
   pg("shadi", "Show me that your heart is worthy of it. Duel?", ask=True)]),
 S("c5_shadi_win", 57, 5, "Shadi beaten.", [
   pg("shadi", "Your heart is pure. Take this piece of the Time Stone."),
   rew("You got Time Stone Fragment 2 and the card Illusionist Faceless Mage.")]),
 S("c5_shadi_lose", 58, 5, "Shadi wins.", [pg("shadi", "Your heart still holds doubts. Come back later.")]),
 S("c5_shadi_done", 59, 5, "Shadi, after his duel.", [pg("shadi", "Pegasus has the Millennium Eye. Be careful with him.")]),
 S("c5_pegasus_locked", 60, 5, "Pegasus, before the other three are beaten.", [
   pg("pegasus", "Hello, {name}-{boy|girl}! First beat the other three duelists. Then I duel you.")]),
 S("c5_pegasus_pre", 61, 5, "Pegasus asks for a duel (boss).", [
   pg("pegasus", "I already read your fate, {name}-{boy|girl}. Why not find out if I am right?"),
   pg("atos", "Nobody reads my fate. I write it in the duel!"),
   pg("pegasus", "How fun! Duel?", ask=True)]),
 S("c5_pegasus_win", 62, 5, "Pegasus beaten; Isis opens the way back to Egypt.", [
   pg("pegasus", "Impossible! The Millennium Eye could not read your mind!"),
   pg("pegasus", "Keep the Eye. Maybe it will help you save the Prince."),
   pg("isis", "I am Isis. I saw you in a vision. I will open a portal back to Egypt."),
   pg("isis", "The Temple Mages guard the other Items. The Prince needs them."),
   rew("You got the Millennium Eye and the card Thousand Dragon."),
   obj("Enter the castle portal to return to Egypt.")]),
 S("c5_pegasus_lose", 63, 5, "Pegasus wins.", [pg("pegasus", "Hahaha! I told you I had read your fate.")]),
 S("c5_pegasus_done", 64, 5, "Pegasus, after his duel.", [
   pg("pegasus", "Isis's portal is open at the castle. Goodbye, {name}-{boy|girl}!")]),
 S("c5_gate_locked", 65, 5, "Castle gate, before Pegasus was beaten.", [
   pg("atos", "The castle gate is shut. I have to beat Pegasus first.")]),
 S("c5_end__c6_intro", 66, 6, "Entering the castle portal: end of chapter 5, then chapter 6 starts (arrival is script c6_arrival).", [
   pg("atos", "Isis's portal is open. Time to go back to Egypt!"),
   nar("End of Chapter 5", "Chapter 6 - The Seven Items")]),
]

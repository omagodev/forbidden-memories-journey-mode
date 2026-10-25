# -*- coding: utf-8 -*-
# Brazilian Portuguese for everything that is not a dialogue page (written with accents; build_pt.py strips them).
# Keys of the *_MAP dicts are the exact English strings of story.json / journey.json.

SPEAKER_NAMES = {   # only generic words are translated; character names stay as the game writes them
    "Guard": ("Guarda", "Guarda"),
    "Prince": ("Príncipe", "Príncipe"),
}

HUD_OBJECTIVES = {   # story.json hud_objectives
    "Talk to Simon Muran": "Fale com Simon Muran",
    "Cross the river to the north": "Cruze o rio ao norte",
    "Enter the portal": "Entre no portal",
    "Beat the other duelist": "Vença o outro duelista",
    "Beat Rex and Weevil": "Vença Rex e Weevil",
    "Enter the palace": "Entre no palácio",
    "Duel Seto": "Duele com Seto",
    "Touch the glowing throne": "Toque o trono brilhante",
    "Defeat Heishin": "Derrote Heishin",
    "Enter the castle portal": "Entre no portal do castelo",
    "Face Pegasus": "Enfrente Pegasus",
    "Beat Mai, Keith and Shadi": "Vença Mai, Keith e Shadi",
    "Open the Labyrinth gate": "Abra o portão do Labirinto",
    "Face High Mage Secmeton": "Enfrente o H.M. Secmeton",
    "Win the five temple Items": "Ganhe os cinco Itens",
    "Take the dark stairs": "Desça a escada escura",
    "Wake the Prince at the altar": "Acorde o Príncipe no altar",
    "Beat Seto at the third door": "Vença Seto na 3a porta",
    "Face Guardian Neku": "Enfrente o Guardian Neku",
    "Face Guardian Sebek": "Enfrente o Guardian Sebek",
    "Cross the Labyrinth": "Cruze o Labirinto",
    "Choose your ending": "Escolha o seu final",
    "Face Nitemare": "Enfrente Nitemare",
    "Beat DarkNite": "Vença DarkNite",
    "Free Seto from the shadow": "Liberte Seto da sombra",
    "Story complete!": "História completa!",
}

# journey.json "objectives" (the HUD the engine really uses); same idea, more entries
ENGINE_OBJECTIVES = {
    "Talk to Simon Muran": "Fale com Simon Muran",
    "Cross the river to the north": "Cruze o rio ao norte",
    "Enter the stone portal": "Entre no portal de pedra",
    "Beat Weevil Underwood": "Vença Weevil Underwood",
    "Beat Rex Raptor": "Vença Rex Raptor",
    "Beat Rex Raptor and Weevil": "Vença Rex Raptor e Weevil",
    "Enter the palace": "Entre no palácio",
    "Duel Seto in front of the palace": "Duele com Seto na frente do palácio",
    "Touch the glowing throne": "Toque o trono brilhante",
    "Defeat Heishin": "Derrote Heishin",
    "Enter the castle portal": "Entre no portal do castelo",
    "Face Pegasus": "Enfrente Pegasus",
    "Beat Mai, Bandit Keith and Shadi": "Vença Mai, Bandit Keith e Shadi",
    "Open the Labyrinth gate": "Abra o portão do Labirinto",
    "Face High Mage Secmeton": "Enfrente o High Mage Secmeton",
    "Win the five temple Items": "Ganhe os cinco Itens dos templos",
    "Take the dark stairs": "Desça a escada escura",
    "Wake the Prince at the altar": "Acorde o Príncipe no altar",
    "Beat Seto at the third door": "Vença Seto na terceira porta",
    "Face Guardian Neku": "Enfrente o Guardian Neku",
    "Face Guardian Sebek": "Enfrente o Guardian Sebek",
    "Cross the Labyrinth": "Cruze o Labirinto",
    "Choose your ending": "Escolha o seu final",
    "Face Nitemare": "Enfrente Nitemare",
    "Beat DarkNite": "Vença DarkNite",
    "Free Seto from the shadow": "Liberte Seto da sombra",
    "Story complete!": "História completa!",
    "Chapter 5 complete!": "Capítulo 5 completo!",
}

ENGINE_CHAPTERS = {  # journey.json "chapters" (HUD banner)
    "Chapter 1: The Village": "Capítulo 1: A Vila",
    "Chapter 2: Sand Ruins": "Capítulo 2: Ruínas de Areia",
    "Chapter 3: The Palace and the Prince": "Capítulo 3: O Palácio e o Príncipe",
    "Chapter 4: Heishin's Coup": "Capítulo 4: O Golpe de Heishin",
    "Chapter 5: The Tournament Out of Time": "Capítulo 5: O Torneio Fora do Tempo",
    "Chapter 6: The Seven Items": "Capítulo 6: Os Sete Itens",
    "Chapter 7: The Labyrinth and the Guardians": "Capítulo 7: O Labirinto e os Guardiões",
    "Chapter 8: Nitemare": "Capítulo 8: Nitemare",
    "Epilogue": "Epílogo",
}

AREAS = {  # both files
    "Village": "Vila", "Fields": "Campos", "Nile River": "Rio Nilo", "Sand Ruins": "Ruínas de Areia",
    "Royal City": "Cidade Real", "Throne Hall": "Salão do Trono", "Tournament Island": "Ilha do Torneio",
    "Temple": "Templo", "Desert Temple": "Templo do Deserto", "Temple Crossroads": "Cruzamento dos Templos",
    "Sea Temple": "Templo do Mar", "Forest Temple": "Templo da Floresta", "Mountain Temple": "Templo da Montanha",
    "Meadow Temple": "Templo da Campina", "Labyrinth": "Labirinto", "Final Temple": "Templo Final",
}

ITEMS = {  # item names; "Fragment" etc. appear in the win pages exactly like this
    "Canteen": "Cantil", "Time Stone Fragment 1": "Fragmento da Pedra Temporal 1", "Torch": "Tocha",
    "Royal Seal": "Selo Real", "Millennium Necklace": "Colar do Milênio",
    "Time Stone Fragment 2": "Fragmento da Pedra Temporal 2", "Millennium Eye": "Olho do Milênio",
    "Millennium Puzzle": "Enigma do Milênio", "Sea Tablet": "Tablete do Mar", "Millennium Key": "Chave do Milênio",
    "Millennium Rod": "Bastão do Milênio", "Millennium Ring": "Anel do Milênio",
    "Millennium Scales": "Balança do Milênio", "Time Stone Fragment 3": "Fragmento da Pedra Temporal 3",
    "Time Stone": "Pedra Temporal", "Cockatiel Feather": "Pena de Calopsita",
}

BACKPACK_LABELS = {  # story.json ui_strings.backpack_item_labels (short forms)
    "Fragment 1": "Fragmento 1", "Fragment 2": "Fragmento 2",
}

OBJECTS = {
    "Stone portal": "Portal de pedra", "Palace door": "Porta do palácio", "Throne": "Trono",
    "Castle gate / Isis portal": "Portão do castelo", "Labyrinth gate": "Portão do Labirinto",
    "Tide wall": "Parede de água", "First door": "Primeira porta", "Second door": "Segunda porta",
    "Third door": "Terceira porta", "Altar": "Altar", "Dark stairs": "Escada escura", "Mist wall": "Parede de névoa",
    "Stairs to Nitemare": "Escada para Nitemare",
}
NPC_NAMES = {"Guard": "Guarda", "Prince": "Príncipe"}   # every other NPC keeps the game's name

STORY_CHAPTERS = {  # story.json chapters[].title (banner) and design_title
    "The Sand That Swallowed the Tournament": "A Areia que Engoliu o Torneio",
    "Sand Ruins": "Ruínas de Areia", "Visitors From the Future": "Visitantes do Futuro",
    "The Palace and the Prince": "O Palácio e o Príncipe", "Heishin's Coup": "O Golpe de Heishin",
    "The Tournament Out of Time": "O Torneio Fora do Tempo", "The Seven Items": "Os Sete Itens",
    "The Labyrinth and the Guardians": "O Labirinto e os Guardiões", "Nitemare": "Nitemare",
}
STORY_CHAPTER_HUD = "Capítulo %d"

STORY_UI = {
    "backpack_title": "Mochila", "backpack_empty": "Vazia", "objective_label": "Objetivo:",
    "chapter_label": "Capítulo %d", "ask_yes_no": ["Sim", "Não"],
}
STORY_TITLE = "MODO JORNADA: O Duelista de Outra Época"

COCKATIEL_EXTRA = {
    "free_duel_taunt_win": "Piu! Voe mais alto da próxima vez!",
    "free_duel_taunt_lose": "O Pip diz que você trapaceou. O Pip está errado.",
    "idle_1": "Pip, para de comer as cartas.",
    "idle_2": "O vento trouxe você até aqui. Não desperdice.",
}

# ---------------------------------------------------------------- engine UI strings (ui.*.json)
UI_PT = {
    "language": {"name": "Português (Brasil)", "label": "Idioma"},
    "mod": {
        "name": "Modo Jornada",
        "description": "Um modo história com um mundo 3D para explorar: criação de personagem, 30 pessoas em 16 áreas ao longo de oito capítulos, as caixas de texto do próprio jogo e duelos com um deck para cada duelista, música por área, um menu START, um arquivo de save e dois finais. Personagens: Quaternius (CC0); cenário: PSX Nature Free por heyheythere (CC BY 4.0).",
        "title_button": "MODO JORNADA",
    },
    "choose": {"heading": "MODO JORNADA", "continue": "Continuar", "new_journey": "Nova jornada",
               "language": "Idioma: %s"},
    "hud": {"status_line": "%s  -  %s    Objetivo: %s", "objective_label": "Objetivo:"},
    "hint": {"talk": "X: falar com %s", "examine": "X: examinar",
             "controls": "Setas: andar   Círculo: correr   X: falar   Start: menu"},
    "ask": {"yes": "Sim", "no": "Não"},
    "messages": {"progress_saved": "Progresso salvo", "save_failed": "Falha ao salvar"},
    "creation": {
        "heading": "CRIE O SEU PERSONAGEM",
        "rows": {"name": "Nome", "gender": "Gênero", "hair": "Cabelo", "hair_colour": "Cor do cabelo", "skin": "Pele",
                 "outfit_colour": "Cor da roupa", "portrait": "Retrato", "start": "Começar"},
        "gender": {"male": "Masculino", "female": "Feminino"},
        "hair_styles": ["Curto", "Para trás", "Arrumado"],
        "hair_colours": ["Violeta", "Preto", "Castanho", "Loiro", "Ruivo"],
        "skins": ["Clara", "Morena", "Escura"],
        "outfit_colours": ["Azul", "Vermelho", "Verde", "Preto", "Branco"],
        "portraits": ["Retrato 1", "Retrato 2", "Retrato 3", "Retrato 4"],
        "hint_name": "X: digitar o nome", "hint_begin": "X: começar", "hint_change": "Esquerda/Direita: mudar",
    },
    "menu": {
        "items": ["Editor de deck", "Itens", "Status", "Salvar", "Voltar ao título", "Fechar"],
        "items_empty": "Nada ainda",
        "objective": "Objetivo: %s",
        "status": "Duelos %d    Vitórias %d    Derrotas %d",
        "deck": "Deck %d / 40 cartas",
        "saved": "Progresso salvo.", "save_failed": "Falha ao salvar.",
        "quit_title": "Voltar à tela de título?", "quit_warn": "(o progresso não salvo será perdido)",
        "yes": "Sim", "no": "Não",
    },
    "defaults": {"player_name": "Herói"},
}

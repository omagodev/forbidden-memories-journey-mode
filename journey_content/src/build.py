#!/usr/bin/env python3
"""Builds story.json, decks.json, cockatiel.json and port_decks_fragment.json into ../ ."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import SPEAKERS
import ch1_5, ch6_8, world, decks_data, atos_cockatiel as ac

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

CHAPTERS = [
 {"n":1,"title":"The Sand That Swallowed the Tournament","hud":"Chapter 1","region":"Oasis Village and Fields","stage":[1,2],"duels":["simon","teana","jono"],"reward":"Mystical Elf, Canteen","unlock":"Road to the Royal City (bridge/ford)"},
 {"n":2,"title":"Sand Ruins","design_title":"Visitors From the Future","hud":"Chapter 2","region":"Sand Ruins","stage":[3,3],"duels":["rex","weevil"],"reward":"Time Stone Fragment 1, Torch","unlock":"Stone portal to the Royal City"},
 {"n":3,"title":"The Palace and the Prince","hud":"Chapter 3","region":"Royal City","stage":[4,4],"duels":["seto","mage_soldier"],"reward":"Royal Seal, Dark Magician","unlock":"Palace door"},
 {"n":4,"title":"Heishin's Coup","hud":"Chapter 4","region":"Throne Hall","stage":[5,5],"duels":["heishin"],"reward":"Millennium Necklace, Gaia the Fierce Knight","unlock":"Time rift at the throne"},
 {"n":5,"title":"The Tournament Out of Time","hud":"Chapter 5","region":"Tournament Island","stage":[6,6],"duels":["mai","keith","shadi","pegasus"],"reward":"Time Stone Fragment 2, Millennium Eye","unlock":"Isis' portal back to Egypt"},
 {"n":6,"title":"The Seven Items","hud":"Chapter 6","region":"Temple Crossroads and the five temples (Sea, Forest, Mountain, Desert, Meadow)","stage":[7,7],"duels":["ocean_mage","secmeton","anubisius","atenza","martis","kepura","cockatiel"],"reward":"Millennium Puzzle (from Simon), Sea Tablet, Key, Rod, Ring, Scales","unlock":"Labyrinth gate"},
 {"n":7,"title":"The Labyrinth and the Guardians","hud":"Chapter 7","region":"Labyrinth","stage":[8,8],"duels":["labyrinth_mage","sebek","neku","seto2","heishin2"],"reward":"Prince freed, Time Stone Fragment 3","unlock":"Final Temple"},
 {"n":8,"title":"Nitemare","hud":"Chapter 8","region":"Final Temple (Shadow Realm)","stage":[9,9],"duels":["seto3","darknite","nitemare"],"reward":"Complete Time Stone, legendary card Workers' Rights","unlock":"Ending A/B and post-game (stage 10): Cockatiel and Atos Vinicius"},
]

TEXT_RULES = {
 "charset":"ASCII letters, digits, space and . , ! ? ' - only (the retail font; accents, quotes and emoji are not drawn). '{', '}', '|' appear only in tokens.",
 "box":"Dialogue box (Tower_CreateBox 0x10,0xB0,0x120,0x30): 8 px per glyph, text area 268 px = 33 glyphs per line, 3 lines per page (see ow_poc.c say()).",
 "limit":"Every page must wrap (greedy, word boundary) into at most 3 lines of 32 glyphs; a {name} token counts as 10 glyphs, {a|b} as the longer option. Checked by tools/check_story.py.",
 "speaker_prefix":"The speaker is a separate field. If the engine prints 'Name: ' in front (like ow_poc.c does) a long page may spill onto one automatic extra page; that is harmless.",
}

def build_story():
    scripts = ch1_5.SCRIPTS + ch6_8.SCRIPTS
    legacy = {s["legacy_id"]: s["id"] for s in ch1_5.SCRIPTS}
    npcs = []
    for n in world.NPCS:
        n = dict(n)
        n["dialogue_rules"] = world.RULES.get(n["id"], [])
        npcs.append(n)
    objects = []
    for o in world.OBJECTS:
        o = dict(o); o["dialogue_rules"] = world.RULES.get(o["id"], []); objects.append(o)
    spk = {k: {"name": v["name"], "short": v["short"], "portrait": v["portrait"], **({"note": v["note"]} if "note" in v else {})} for k, v in SPEAKERS.items()}
    new_duelists = [
        {"id":"cockatiel","copy":"High Mage Kepura","name":"Cockatiel","slot":40,"portrait_file":"portraits/cockatiel.png","definition":"cockatiel.json"},
        {"id":"atos-vinicius","copy":"Seto 3rd","name":"Atos Vinicius","slot":41,"portrait_file":"portraits/atos-vinicius.png","note":"Uses the player's Atos face; deck in decks.json['Atos Vinicius']."},
    ]
    return {
        "schema":"journey-story/1","language":"en",
        "title":"JOURNEY MODE: The Duelist From Another Time",
        "text_rules":TEXT_RULES,
        "tokens":{"{name}":"Player name (default 'Atos').","{a|b}":"Gender choice: a for a male character, b for a female one. Example: '{lad|lass}', '{name}-{boy|girl}'. The engine picks one side, then fits the page."},
        "speakers":spk,
        "flags":world.FLAGS,
        "stages":world.STAGES,
        "chapters":CHAPTERS,
        "areas":world.AREAS,
        "npcs":npcs,
        "objects":objects,
        "items":world.ITEMS,
        "new_duelists":new_duelists,
        "duels":world.DUELS,
        "transitions":world.TRANSITIONS,
        "hud_objectives":world.HUD,
        "ui_strings":world.UI,
        "scripts":scripts,
        "legacy_script_index":{str(k): v for k, v in sorted(legacy.items())},
        "editor_notes":[
          "Chapters 1-5 translate ow4/story.py page by page. Portuguese gender forms ({rapaz/moca}, {o/a} {estrangeiro/estrangeira}) became English where English has no gender: only 'lad|lass' and 'boy|girl' survive.",
          "c5_pegasus_win: Isis said 'my Necklace showed you' in Portuguese, but the player already owns the Necklace since chapter 4. English says 'I saw you in a vision'.",
          "c5_end__c6_intro (legacy 66) used to end with 'Continues in Chapter 6. Coming soon!'. It now announces Chapter 6 and chains into c6_arrival.",
          "Legacy script ids 0-66 keep their numeric order in legacy_script_index so the old SCRP block builder can be reused.",
          "Chapter 6-8 reward cards are normal (non-ritual) cards; the Time Stone and Workers' Rights are the only custom things (see decks.json custom_cards).",
        ],
    }

def build_decks():
    decks = {}
    for k, v in decks_data.DECKS.items():
        decks[k] = {"duelist": v["duelist"], "chapter": v["chapter"], "difficulty_tier": v["difficulty_tier"], "theme": v["theme"],
                    "fixed": True, "total": sum(v["cards"].values()), "cards": dict(sorted(v["cards"].items())), "notes": v["notes"]}
    a = ac.ATOS_DECK
    decks["Atos Vinicius"] = {"duelist": a["duelist"], "chapter": a["chapter"], "difficulty_tier": a["difficulty_tier"], "theme": a["theme"],
        "fixed": True, "total": sum(a["cards"].values()), "cards": dict(sorted(a["cards"].items())),
        "cards_with_custom_pack": dict(sorted(a["cards_with_custom_pack"].items())), "notes": a["notes"]}
    return {
        "schema":"journey-decks/1",
        "rules":{"deck_size":40,"max_copies":3,"card_names":"Exact names from fork/notes/card-catalog.csv (the disc's names). Checked by tools/check_decks.py.",
                 "ritual_only":"No ritual-only monsters and no Ritual cards are used (the AI cannot summon them reliably).",
                 "difficulty":"difficulty_tier 1 (chapter 1 tutorial duelists) to 10 (final bosses): higher tiers use higher-level monsters, field cards and more equips/removal."},
        "difficulty_curve":{"1":"ch1 tutorial","2":"ch2","3":"ch3","4":"ch4 boss","5":"ch5","6":"ch5 boss / ch6 first temple","7":"ch6 high mages + Cockatiel","8":"ch7 guardians","9":"ch7 bosses, shadow Seto","10":"ch8 finale and mirror duelist"},
        "custom_cards":ac.CUSTOM_CARDS,"custom_cards_note":ac.CUSTOM_NOTE,
        "decks":decks,
    }

def build_fragment(decks):
    frag = {}
    for k, v in decks["decks"].items():
        frag[k] = dict({"fixed": True}, **v["cards"])
    ids = {"Atos Vinicius": "atos-vinicius", "Cockatiel": "cockatiel"}
    frag = {ids.get(k, k): v for k, v in frag.items()}
    return {"_comment":"Paste into a mod.json: gameplay-tables 'decks' (fixed 40-card decks, one per opponent name or added duelist id).","decks":frag}

def dump(name, data):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=True); f.write("\n")

if __name__ == "__main__":
    story = build_story(); decks = build_decks()
    dump("story.json", story); dump("decks.json", decks); dump("cockatiel.json", ac.COCKATIEL)
    dump("port_decks_fragment.json", build_fragment(decks))
    print("scripts", len(story["scripts"]), "decks", len(decks["decks"]))

"""World tables: flags, stages, areas, npcs, objects, duels, dialogue rules, transitions, items, UI strings."""

FLAG_NAMES = ["jono_won","teana_won","rex_won","weevil_won","seto_won","mage_soldier_won","heishin_won",
 "mai_won","keith_won","shadi_won","pegasus_won","ocean_mage_won","secmeton_won","anubisius_won","atenza_won",
 "martis_won","kepura_won","labyrinth_mage_won","sebek_won","neku_won","seto2_won","altar_scene_seen",
 "heishin2_won","seto3_won","darknite_won","nitemare_won","cockatiel_won","mirror_won","ending_home","ending_stay"]
FLAG_NOTE = {
 "jono_won":"Legacy beat bit 1.","teana_won":"Legacy beat bit 2.","rex_won":"Legacy beat bit 4.","weevil_won":"Legacy beat bit 8.",
 "seto_won":"Legacy beat bit 16 (also unlocks the palace door).","mage_soldier_won":"Legacy beat bit 32.",
 "heishin_won":"Legacy beat bit 64 (also unlocks the throne).","mai_won":"Legacy beat bit 128.","keith_won":"Legacy beat bit 256.",
 "shadi_won":"Legacy beat bit 512.","pegasus_won":"Legacy beat bit 1024 (also unlocks the castle gate).",
 "altar_scene_seen":"Set when the altar scene c7_altar_wake has played once (so a lost duel does not replay it).",
 "ending_home":"Chosen ending A.","ending_stay":"Chosen ending B."}
FLAGS = [{"name": n, "bit": i, "value": 1 << i, "note": FLAG_NOTE.get(n, ("Legacy beat bit %d." % (1 << i)) if i < 11 else "New in chapters 6-8.")}
         for i, n in enumerate(FLAG_NAMES)]
TEMPLES = ["ocean_mage_won","secmeton_won","anubisius_won","atenza_won","martis_won","kepura_won"]

STAGES = [
 {"stage":0,"chapter":0,"title":"Character creation","note":"Legacy mode 3; ends by running c1_intro and setting stage 1."},
 {"stage":1,"chapter":1,"title":"The Sand That Swallowed the Tournament","note":"Before Simon is beaten."},
 {"stage":2,"chapter":1,"title":"The Sand That Swallowed the Tournament","note":"Simon beaten; river ford is open until the player crosses north."},
 {"stage":3,"chapter":2,"title":"Visitors From the Future (Sand Ruins)"},
 {"stage":4,"chapter":3,"title":"The Palace and the Prince"},
 {"stage":5,"chapter":4,"title":"Heishin's Coup"},
 {"stage":6,"chapter":5,"title":"The Tournament Out of Time"},
 {"stage":7,"chapter":6,"title":"The Seven Items"},
 {"stage":8,"chapter":7,"title":"The Labyrinth and the Guardians"},
 {"stage":9,"chapter":8,"title":"Nitemare"},
 {"stage":10,"chapter":9,"title":"Epilogue / post-game","note":"Story finished. Side duelists stay available."},
]

AREAS = [
 {"id":0,"name":"Village","legacy":True,"music":{"id":"0x7360","title":"Town Plaza"}},
 {"id":1,"name":"Fields","legacy":True,"music":{"id":"0x7150","title":"Meadow Shrine"}},
 {"id":2,"name":"Nile River","legacy":True,"music":{"id":"0x7120","title":"Sea Shrine"}},
 {"id":3,"name":"Sand Ruins","legacy":True,"music":{"id":"0x71a0","title":"Forbidden Ruins"}},
 {"id":4,"name":"Royal City","legacy":True,"music":{"id":"0x70d0","title":"Pharaoh's Palace"}},
 {"id":5,"name":"Throne Hall","legacy":True,"music":{"id":"0x73a0","title":"Pharaoh's Palace 2"}},
 {"id":6,"name":"Tournament Island","legacy":True,"music":{"id":"0x71e0","title":"Preliminaries"}},
 {"id":7,"name":"Temple","legacy":True,"music":{"id":"0x7140","title":"Desert Shrine"}},
 {"id":8,"name":"Temple Crossroads","legacy":False,"hub":True,"music":{"id":"0x7360","title":"Town Plaza"},"setting":"Old crossroads with a broken well and a sealed stone gate with five sockets (the Labyrinth gate). Road signs to the five temples."},
 {"id":9,"name":"Sea Temple","legacy":False,"music":{"id":"0x7120","title":"Sea Shrine"},"setting":"Shore with a wall of water in front of an inner door; tide pools; blue stone."},
 {"id":10,"name":"Forest Temple","legacy":False,"music":{"id":None,"title":"Forest Shrine (pick from the disc list)"},"setting":"Giant roots, moss, dim green light."},
 {"id":11,"name":"Mountain Temple","legacy":False,"music":{"id":None,"title":"Mountain Shrine (pick from the disc list)"},"setting":"Switchback path to a cold summit shrine."},
 {"id":12,"name":"Desert Temple","legacy":False,"music":{"id":"0x7140","title":"Desert Shrine"},"setting":"Dune ridge, half-buried columns, wind."},
 {"id":13,"name":"Meadow Temple","legacy":False,"music":{"id":"0x7150","title":"Meadow Shrine"},"setting":"Flower fields, a small white shrine."},
 {"id":14,"name":"Labyrinth","legacy":False,"music":{"id":None,"title":"Labyrinth (pick from the disc list)"},"setting":"Stone corridors with torches, narrow camera, three hieroglyph doors, the altar room at the end."},
 {"id":15,"name":"Final Temple","legacy":False,"music":{"id":None,"title":"Dark shrine (pick from the disc list)"},"setting":"Dark pyramid floating in a purple sky; black stone floor."},
]

def T(x, z): return {"tile_x": x, "tile_z": z}

NPCS = [
 {"id":"simon","name":"Simon Muran","portrait_speaker":"simon","area":0,"tile":T(14,28),"duelist_id":1,"model_hint":"Simon model of the PoC","stages":[0,6],"legacy_talk_target":9},
 {"id":"jono","name":"Jono","area":0,"tile":T(19,32),"duelist_id":3,"model_hint":"Quaternius Ninja_Sand","stages":[0,6],"legacy_npc_index":0},
 {"id":"teana","name":"Teana","area":0,"tile":T(9,32),"duelist_id":2,"model_hint":"Quaternius Ninja_Female","stages":[0,6],"legacy_npc_index":1},
 {"id":"guard","name":"Guard","area":2,"tile":T(24,23),"after_simon_won_tile":T(26,23),"duelist_id":None,"model_hint":"Guard","stages":[0,6],"legacy_npc_index":3,"note":"Moves one tile east when Simon is beaten (opens the ford)."},
 {"id":"rex","name":"Rex Raptor","area":3,"tile":T(18,10),"duelist_id":9,"model_hint":"Quaternius Kimono","stages":[3,3],"legacy_npc_index":4},
 {"id":"weevil","name":"Weevil","area":3,"tile":T(31,11),"duelist_id":10,"model_hint":"Quaternius OldClassy","stages":[3,3],"legacy_npc_index":5},
 {"id":"seto","name":"Seto","area":4,"tile":T(55,6),"hall_tile":T(57,31),"hall_area":5,"duelist_id":7,"model_hint":"Quaternius Wizard","stages":[4,6],"legacy_npc_index":2,"note":"Moves to the throne hall at stage 5 and stays there."},
 {"id":"prince","name":"Prince","area":4,"tile":T(57,6),"tile_offset_px":24,"hall_tile":T(53,31),"hall_area":5,"duelist_id":None,"model_hint":"Quaternius Elf","stages":[4,5],"legacy_npc_index":6,"note":"Removed from the hall once Heishin is beaten (sealed in the Puzzle). Custom portrait."},
 {"id":"mage_soldier","name":"Mage Soldier","area":4,"tile":T(51,14),"duelist_id":18,"model_hint":"Quaternius Knight","stages":[4,5],"legacy_npc_index":7},
 {"id":"heishin","name":"Heishin","area":5,"tile":T(55,27),"duelist_id":8,"model_hint":"Quaternius Doctor_Old","stages":[5,5],"legacy_npc_index":8,"note":"Only present at stage 5 until beaten."},
 {"id":"mai","name":"Mai","area":6,"tile":T(19,68),"duelist_id":11,"model_hint":"Quaternius Casual2_Female","stages":[6,6],"legacy_npc_index":9},
 {"id":"keith","name":"Bandit Keith","area":6,"tile":T(29,68),"duelist_id":12,"model_hint":"Quaternius Cowboy_Male","stages":[6,6],"legacy_npc_index":10},
 {"id":"shadi","name":"Shadi","area":6,"tile":T(28,63),"duelist_id":13,"model_hint":"Quaternius Doctor_Young","stages":[6,6],"legacy_npc_index":11},
 {"id":"pegasus","name":"Pegasus","area":6,"tile":T(21,60),"duelist_id":15,"model_hint":"Quaternius Suit_Male","stages":[6,6],"legacy_npc_index":12},
 # new
 {"id":"simon_crossroads","name":"Simon Muran","portrait_speaker":"simon","area":8,"placement":"beside the broken well","duelist_id":None,"model_hint":"same as simon","stages":[7,7]},
 {"id":"ocean_mage","name":"Ocean Mage","area":9,"placement":"on the shore, in front of the tide wall","duelist_id":21,"model_hint":"Quaternius Wizard (blue tint)","stages":[7,7]},
 {"id":"secmeton","name":"High Mage Secmeton","area":9,"placement":"inside the inner door","duelist_id":22,"model_hint":"Quaternius OldClassy (blue robe)","stages":[7,7]},
 {"id":"anubisius","name":"High Mage Anubisius","area":10,"placement":"at the shrine under the big root","duelist_id":24,"model_hint":"Quaternius Wizard (green tint)","stages":[7,7]},
 {"id":"atenza","name":"High Mage Atenza","area":11,"placement":"at the summit shrine","duelist_id":26,"model_hint":"Quaternius Viking or Knight","stages":[7,7]},
 {"id":"martis","name":"High Mage Martis","area":12,"placement":"at the half-buried columns","duelist_id":28,"model_hint":"Quaternius Wizard (sand tint)","stages":[7,7]},
 {"id":"kepura","name":"High Mage Kepura","area":13,"placement":"in the middle of the flowers","duelist_id":30,"model_hint":"Quaternius Casual or Witch","stages":[7,7]},
 {"id":"cockatiel","name":"Cockatiel","portrait_speaker":"cockatiel","area":8,"placement":"perched on the roof of the old well","duelist_id":"cockatiel","model_hint":"Quaternius Hoodie or Punk with a small grey-and-yellow bird prop on the shoulder","stages":[7,10]},
 {"id":"labyrinth_mage","name":"Labyrinth Mage","area":14,"placement":"first junction, beside a moving wall","duelist_id":31,"model_hint":"Quaternius Wizard","stages":[8,8]},
 {"id":"sebek","name":"Guardian Sebek","area":14,"placement":"in front of door 1","duelist_id":33,"model_hint":"Quaternius Soldier or Zombie (green)","stages":[8,8]},
 {"id":"neku","name":"Guardian Neku","area":14,"placement":"in front of door 2","duelist_id":34,"model_hint":"Quaternius Ninja or Knight","stages":[8,8]},
 {"id":"seto2","name":"Seto","portrait_speaker":"seto2","area":14,"placement":"in front of door 3 / the altar room","duelist_id":32,"model_hint":"same as seto","stages":[8,8]},
 {"id":"heishin2","name":"Heishin","portrait_speaker":"heishin2","area":14,"placement":"appears at the altar when the Items are placed","duelist_id":35,"model_hint":"same as heishin","stages":[8,8]},
 {"id":"prince_labyrinth","name":"Prince","portrait_speaker":"prince","area":14,"placement":"altar, after the Puzzle is opened; then follows the player","duelist_id":None,"model_hint":"same as prince","stages":[8,9]},
 {"id":"seto3","name":"Seto","portrait_speaker":"seto3","area":15,"placement":"in front of the Final Temple gate","duelist_id":36,"model_hint":"same as seto (dark tint / black mist prop)","stages":[9,9]},
 {"id":"darknite","name":"DarkNite","area":15,"placement":"in the hall of shadows","duelist_id":37,"model_hint":"Quaternius Wizard (black) or the game's DarkNite model","stages":[9,9]},
 {"id":"nitemare","name":"Nitemare","area":15,"placement":"top of the stairs","duelist_id":38,"model_hint":"the game's Nitemare model","stages":[9,9]},
 {"id":"mirror","name":"Atos Vinicius","portrait_speaker":"mirror","area":8,"placement":"standing near the Labyrinth gate","duelist_id":"atos-vinicius","model_hint":"player model with a different outfit color","stages":[10,10]},
]

OBJECTS = [
 {"id":"portal_ruins","name":"Stone portal","area":3,"tile":T(24,3),"legacy_talk_target":7,"solid_until":["rex_won","weevil_won"]},
 {"id":"palace_door","name":"Palace door","area":4,"tile":T(55,4),"legacy_talk_target":8,"solid_until":["seto_won"]},
 {"id":"throne","name":"Throne","area":5,"tile":T(55,25),"legacy_talk_target":12,"solid_until":["heishin_won"]},
 {"id":"castle_gate","name":"Castle gate / Isis portal","area":6,"tile":T(24,59),"legacy_talk_target":24,"solid_until":["pegasus_won"]},
 {"id":"labyrinth_gate","name":"Labyrinth gate","area":8,"placement":"stone gate with five sockets","solid_until":TEMPLES},
 {"id":"sea_inner_door","name":"Tide wall","area":9,"placement":"inner door of the Sea Temple","solid_until":["ocean_mage_won"]},
 {"id":"door1","name":"First door","area":14,"solid_until":["labyrinth_mage_won"]},
 {"id":"door2","name":"Second door","area":14,"solid_until":["sebek_won"]},
 {"id":"door3","name":"Third door","area":14,"solid_until":["neku_won"]},
 {"id":"altar","name":"Altar","area":14,"solid_until":["seto2_won"]},
 {"id":"dark_stairs","name":"Dark stairs","area":14,"solid_until":["heishin2_won"]},
 {"id":"hall_mist","name":"Mist wall","area":15,"solid_until":["seto3_won"]},
 {"id":"boss_stairs","name":"Stairs to Nitemare","area":15,"solid_until":["darknite_won"]},
]

ITEMS = [
 {"id":"canteen","name":"Canteen","source":"Simon (c1_simon_win)","legacy":"cantil"},
 {"id":"time_fragment_1","name":"Time Stone Fragment 1","source":"Rex Raptor","flag":"rex_won"},
 {"id":"torch","name":"Torch","source":"Weevil","flag":"weevil_won"},
 {"id":"royal_seal","name":"Royal Seal","source":"Seto","flag":"seto_won"},
 {"id":"millennium_necklace","name":"Millennium Necklace","source":"Simon, after Heishin","flag":"heishin_won"},
 {"id":"time_fragment_2","name":"Time Stone Fragment 2","source":"Shadi","flag":"shadi_won"},
 {"id":"millennium_eye","name":"Millennium Eye","source":"Pegasus","flag":"pegasus_won"},
 {"id":"millennium_puzzle","name":"Millennium Puzzle","source":"Simon (c6_arrival)","note":"Holds the Prince's soul."},
 {"id":"sea_tablet","name":"Sea Tablet","source":"High Mage Secmeton","flag":"secmeton_won"},
 {"id":"millennium_key","name":"Millennium Key","source":"High Mage Anubisius","flag":"anubisius_won"},
 {"id":"millennium_rod","name":"Millennium Rod","source":"High Mage Atenza","flag":"atenza_won"},
 {"id":"millennium_ring","name":"Millennium Ring","source":"High Mage Martis","flag":"martis_won"},
 {"id":"millennium_scales","name":"Millennium Scales","source":"High Mage Kepura","flag":"kepura_won"},
 {"id":"time_fragment_3","name":"Time Stone Fragment 3","source":"Heishin 2nd","flag":"heishin2_won"},
 {"id":"time_stone","name":"Time Stone","source":"Nitemare","flag":"nitemare_won","note":"Replaces the three fragments in the Backpack."},
 {"id":"cockatiel_feather","name":"Cockatiel Feather","source":"Cockatiel","flag":"cockatiel_won","note":"Cosmetic keepsake."},
]

UI = {
 "backpack_title":"Backpack","backpack_empty":"Empty","objective_label":"Objective:","chapter_label":"Chapter %d",
 "area_names":[a["name"] for a in AREAS],
 "backpack_item_labels":{"canteen":"Canteen","time_fragment_1":"Fragment 1","torch":"Torch","royal_seal":"Royal Seal",
   "millennium_necklace":"Millennium Necklace","time_fragment_2":"Fragment 2","millennium_eye":"Millennium Eye"},
 "ask_yes_no":["Yes","No"],
}

def W(**k): return k
HUD = [  # first match wins; text must fit a 146 px line wrapped (about 18 chars per line, two lines max recommended)
 W(when=W(stage=[0,1]), text="Talk to Simon Muran"),
 W(when=W(stage=[2,2]), text="Cross the river to the north"),
 W(when=W(stage=[3,3], flags_all=["rex_won","weevil_won"]), text="Enter the portal"),
 W(when=W(stage=[3,3], flags_any=["rex_won","weevil_won"]), text="Beat the other duelist"),
 W(when=W(stage=[3,3]), text="Beat Rex and Weevil"),
 W(when=W(stage=[4,4], flags_all=["seto_won"]), text="Enter the palace"),
 W(when=W(stage=[4,4]), text="Duel Seto"),
 W(when=W(stage=[5,5], flags_all=["heishin_won"]), text="Touch the glowing throne"),
 W(when=W(stage=[5,5]), text="Defeat Heishin"),
 W(when=W(stage=[6,6], flags_all=["pegasus_won"]), text="Enter the castle portal"),
 W(when=W(stage=[6,6], flags_all=["mai_won","keith_won","shadi_won"]), text="Face Pegasus"),
 W(when=W(stage=[6,6]), text="Beat Mai, Keith and Shadi"),
 W(when=W(stage=[7,7], flags_all=TEMPLES), text="Open the Labyrinth gate"),
 W(when=W(stage=[7,7], flags_all=["ocean_mage_won"], flags_none=["secmeton_won"]), text="Face High Mage Secmeton"),
 W(when=W(stage=[7,7]), text="Win the five temple Items"),
 W(when=W(stage=[8,8], flags_all=["heishin2_won"]), text="Take the dark stairs"),
 W(when=W(stage=[8,8], flags_all=["seto2_won"]), text="Wake the Prince at the altar"),
 W(when=W(stage=[8,8], flags_all=["neku_won"]), text="Beat Seto at the third door"),
 W(when=W(stage=[8,8], flags_all=["sebek_won"]), text="Face Guardian Neku"),
 W(when=W(stage=[8,8], flags_all=["labyrinth_mage_won"]), text="Face Guardian Sebek"),
 W(when=W(stage=[8,8]), text="Cross the Labyrinth"),
 W(when=W(stage=[9,9], flags_all=["nitemare_won"]), text="Choose your ending"),
 W(when=W(stage=[9,9], flags_all=["darknite_won"]), text="Face Nitemare"),
 W(when=W(stage=[9,9], flags_all=["seto3_won"]), text="Beat DarkNite"),
 W(when=W(stage=[9,9]), text="Free Seto from the shadow"),
 W(when=W(stage=[10,10]), text="Story complete!"),
]

def R(script, stage=None, all=None, none=None, any=None, duel=None, note=None):
    when = {}
    if stage: when["stage"] = list(stage)
    if all: when["flags_all"] = all
    if none: when["flags_none"] = none
    if any: when["flags_any"] = any
    r = {"when": when, "script": script}
    if duel: r["duel"] = duel
    if note: r["note"] = note
    return r

RULES = {
 "simon": [R("c1_simon_pre",(0,1),duel="simon"), R("c1_simon_after",(2,99))],
 "jono": [R("c1_jono_wait",(0,1)), R("c2_jono_done",all=["jono_won"]), R("c1_jono_pre",duel="jono")],
 "teana": [R("c1_teana_wait",(0,1)), R("c2_teana_done",all=["teana_won"]), R("c1_teana_pre",duel="teana")],
 "guard": [R("c1_guard_block",(0,1)), R("c1_guard_ok")],
 "rex": [R("c2_rex_done",all=["rex_won"]), R("c2_rex_pre",duel="rex")],
 "weevil": [R("c2_weevil_done",all=["weevil_won"]), R("c2_weevil_pre",duel="weevil")],
 "portal_ruins": [R("c2_portal_locked",(3,3),none=["rex_won"]), R("c2_portal_locked",(3,3),none=["weevil_won"])],
 "seto": [R("c4_seto_after",(5,99),all=["heishin_won"]), R("c4_seto_before",(5,99)),
          R("c3_seto_done",all=["seto_won"]), R("c3_seto_pre",duel="seto")],
 "prince": [R("c4_prince_hall",(5,99)), R("c3_prince_after",all=["seto_won"]), R("c3_prince_before")],
 "mage_soldier": [R("c3_soldier_done",all=["mage_soldier_won"]), R("c3_soldier_pre",duel="mage_soldier")],
 "palace_door": [R("c3_door_locked",(4,4),none=["seto_won"])],
 "heishin": [R("c4_heishin_pre",duel="heishin")],
 "throne": [R("c4_throne_locked",(5,5),none=["heishin_won"])],
 "mai": [R("c5_mai_done",all=["mai_won"]), R("c5_mai_pre",duel="mai")],
 "keith": [R("c5_keith_done",all=["keith_won"]), R("c5_keith_pre",duel="keith")],
 "shadi": [R("c5_shadi_done",all=["shadi_won"]), R("c5_shadi_pre",duel="shadi")],
 "pegasus": [R("c5_pegasus_done",all=["pegasus_won"]),
             R("c5_pegasus_pre",all=["mai_won","keith_won","shadi_won"],duel="pegasus"),
             R("c5_pegasus_locked")],
 "castle_gate": [R("c5_gate_locked",(6,6),none=["pegasus_won"])],
 # chapter 6
 "simon_crossroads": [R("c6_simon_hub_done",(7,7),all=TEMPLES), R("c6_simon_hub",(7,7))],
 "ocean_mage": [R("c6_ocean_done",all=["ocean_mage_won"]), R("c6_ocean_pre",duel="ocean_mage")],
 "sea_inner_door": [R("c6_secmeton_locked",none=["ocean_mage_won"])],
 "secmeton": [R("c6_secmeton_done",all=["secmeton_won"]), R("c6_secmeton_pre",duel="secmeton")],
 "anubisius": [R("c6_anubisius_done",all=["anubisius_won"]), R("c6_anubisius_pre",duel="anubisius")],
 "atenza": [R("c6_atenza_done",all=["atenza_won"]), R("c6_atenza_pre",duel="atenza")],
 "martis": [R("c6_martis_done",all=["martis_won"]), R("c6_martis_pre",duel="martis")],
 "kepura": [R("c6_kepura_done",all=["kepura_won"]), R("c6_kepura_pre",duel="kepura")],
 "labyrinth_gate": [R("c6_gate_locked",(7,7),none=["ocean_mage_won"]),
                    R("c6_gate_locked",(7,7),none=["secmeton_won"]), R("c6_gate_locked",(7,7),none=["anubisius_won"]),
                    R("c6_gate_locked",(7,7),none=["atenza_won"]), R("c6_gate_locked",(7,7),none=["martis_won"]),
                    R("c6_gate_locked",(7,7),none=["kepura_won"])],
 "cockatiel": [R("side_cockatiel_epilogue",(10,99),all=["cockatiel_won"]), R("side_cockatiel_done",all=["cockatiel_won"]),
               R("side_cockatiel_pre",duel="cockatiel")],
 # chapter 7
 "labyrinth_mage": [R("c7_lmage_done",all=["labyrinth_mage_won"]), R("c7_lmage_pre",duel="labyrinth_mage")],
 "door1": [R("c7_door1_locked",none=["labyrinth_mage_won"])],
 "sebek": [R("c7_sebek_done",all=["sebek_won"]), R("c7_sebek_pre",duel="sebek")],
 "door2": [R("c7_door2_locked",none=["sebek_won"])],
 "neku": [R("c7_neku_done",all=["neku_won"]), R("c7_neku_pre",duel="neku")],
 "door3": [R("c7_door3_locked",none=["neku_won"])],
 "seto2": [R("c7_seto2_after_altar",all=["heishin2_won"]), R("c7_seto2_done",all=["seto2_won"]), R("c7_seto2_pre",duel="seto2")],
 "altar": [R("c7_altar_locked",none=["seto2_won"]),
           R("c7_heishin2_retry",all=["altar_scene_seen"],none=["heishin2_won"],duel="heishin2",note="Talking to the altar again after a lost duel."),
           R("c7_altar_wake",all=["seto2_won"],none=["altar_scene_seen"],duel="heishin2",note="Plays once; last page asks Duel?.")],
 "prince_labyrinth": [R("c7_prince_free",all=["heishin2_won"])],
 # chapter 8
 "seto3": [R("c8_seto3_done",all=["seto3_won"]), R("c8_seto3_pre",duel="seto3")],
 "hall_mist": [R("c8_hall_locked",none=["seto3_won"])],
 "darknite": [R("c8_darknite_pre",duel="darknite")],
 "boss_stairs": [R("c8_stairs_locked",none=["darknite_won"])],
 "nitemare": [R("c8_nitemare_pre",duel="nitemare")],
 "mirror": [R("side_mirror_done",all=["mirror_won"]), R("side_mirror_pre",duel="mirror")],
}

def Eff(**k): return {kk: v for kk, v in k.items() if v is not None}

def D(id, npc, duelist, chapter, pre, win, lose, flag, effects, first_win_only=True, deck=None, tier=None, note=None):
    d = {"id": id, "npc": npc, "duelist_id": duelist, "chapter": chapter, "pre_script": pre, "win_script": win,
         "lose_script": lose, "win_flag": flag, "on_win": effects, "rewards_first_win_only": first_win_only}
    if deck: d["deck"] = deck
    if tier: d["difficulty_tier"] = tier
    if note: d["note"] = note
    return d

def card(n): return {"give_card": n}
def item(i): return {"give_item": i}

DUELS = [
 D("simon","simon",1,1,"c1_simon_pre","c1_simon_win","c1_simon_lose",None,[card("Mystical Elf"),item("canteen"),{"set_stage":2},{"move_npc":{"npc":"guard","to":T(26,23)}}],deck="Simon Muran",tier=1,note="Win sets stage 2 (no flag). Rewards only the first time."),
 D("teana","teana",2,1,"c1_teana_pre","c1_teana_win","c1_teana_lose","teana_won",[card("Feral Imp")],deck="Teana",tier=1,note="Optional."),
 D("jono","jono",3,1,"c1_jono_pre","c1_jono_win","c1_jono_lose","jono_won",[card("Baby Dragon")],deck="Jono",tier=1,note="Optional."),
 D("rex","rex",9,2,"c2_rex_pre","c2_rex_win","c2_rex_lose","rex_won",[item("time_fragment_1"),card("Ryu-kishin")],deck="Rex Raptor",tier=2),
 D("weevil","weevil",10,2,"c2_weevil_pre","c2_weevil_win","c2_weevil_lose","weevil_won",[item("torch"),card("Hitotsu-me Giant")],deck="Weevil Underwood",tier=2),
 D("seto","seto",7,3,"c3_seto_pre","c3_seto_win","c3_seto_lose","seto_won",[item("royal_seal"),card("Dark Magician")],deck="Seto",tier=3),
 D("mage_soldier","mage_soldier",18,3,"c3_soldier_pre","c3_soldier_win","c3_soldier_lose","mage_soldier_won",[card("Celtic Guardian")],deck="Mage Soldier",tier=3,note="Optional."),
 D("heishin","heishin",8,4,"c4_heishin_pre","c4_heishin_win","c4_heishin_lose","heishin_won",[item("millennium_necklace"),card("Gaia the Fierce Knight"),{"remove_npc":"heishin"},{"remove_npc":"prince"},{"place_npcs":"stage5"}],deck="Heishin",tier=4),
 D("mai","mai",11,5,"c5_mai_pre","c5_mai_win","c5_mai_lose","mai_won",[card("Harpie Lady")],deck="Mai Valentine",tier=5),
 D("keith","keith",12,5,"c5_keith_pre","c5_keith_win","c5_keith_lose","keith_won",[card("Great White")],deck="Bandit Keith",tier=5),
 D("shadi","shadi",13,5,"c5_shadi_pre","c5_shadi_win","c5_shadi_lose","shadi_won",[item("time_fragment_2"),card("Illusionist Faceless Mage")],deck="Shadi",tier=5),
 D("pegasus","pegasus",15,5,"c5_pegasus_pre","c5_pegasus_win","c5_pegasus_lose","pegasus_won",[item("millennium_eye"),card("Thousand Dragon")],deck="Pegasus",tier=6,note="Boss. Requires mai_won, keith_won and shadi_won."),
 D("ocean_mage","ocean_mage",21,6,"c6_ocean_pre","c6_ocean_win","c6_ocean_lose","ocean_mage_won",[card("Aqua Dragon")],deck="Ocean Mage",tier=6),
 D("secmeton","secmeton",22,6,"c6_secmeton_pre","c6_secmeton_win","c6_secmeton_lose","secmeton_won",[item("sea_tablet"),card("Suijin")],deck="High Mage Secmeton",tier=7),
 D("anubisius","anubisius",24,6,"c6_anubisius_pre","c6_anubisius_win","c6_anubisius_lose","anubisius_won",[item("millennium_key"),card("Ancient One of the Deep Forest")],deck="High Mage Anubisius",tier=7),
 D("atenza","atenza",26,6,"c6_atenza_pre","c6_atenza_win","c6_atenza_lose","atenza_won",[item("millennium_rod"),card("Thunder Dragon")],deck="High Mage Atenza",tier=7),
 D("martis","martis",28,6,"c6_martis_pre","c6_martis_win","c6_martis_lose","martis_won",[item("millennium_ring"),card("Mystical Sand")],deck="High Mage Martis",tier=7),
 D("kepura","kepura",30,6,"c6_kepura_pre","c6_kepura_win","c6_kepura_lose","kepura_won",[item("millennium_scales"),card("Queen of Autumn Leaves")],deck="High Mage Kepura",tier=7),
 D("cockatiel","cockatiel","cockatiel",6,"side_cockatiel_pre","side_cockatiel_win","side_cockatiel_lose","cockatiel_won",[item("cockatiel_feather"),card("Crimson Sunbird")],deck="Cockatiel",tier=7,note="Optional side duelist, available from stage 7 on."),
 D("labyrinth_mage","labyrinth_mage",31,7,"c7_lmage_pre","c7_lmage_win","c7_lmage_lose","labyrinth_mage_won",[card("Guardian of the Labyrinth")],deck="Labyrinth Mage",tier=8),
 D("sebek","sebek",33,7,"c7_sebek_pre","c7_sebek_win","c7_sebek_lose","sebek_won",[card("Guardian of the Throne Room")],deck="Guardian Sebek",tier=8),
 D("neku","neku",34,7,"c7_neku_pre","c7_neku_win","c7_neku_lose","neku_won",[card("Rude Kaiser")],deck="Guardian Neku",tier=8),
 D("seto2","seto2",32,7,"c7_seto2_pre","c7_seto2_win","c7_seto2_lose","seto2_won",[card("Blue-eyes White Dragon")],deck="Seto 2nd",tier=9),
 D("heishin2","heishin2",35,7,"c7_altar_wake","c7_heishin2_win","c7_heishin2_lose","heishin2_won",[item("time_fragment_3"),card("Summoned Skull"),{"place_npc":{"npc":"prince_labyrinth","state":"follows_player"}}],deck="Heishin 2nd",tier=9,note="Pre script is c7_altar_wake the first time, c7_heishin2_retry after a loss."),
 D("seto3","seto3",36,8,"c8_seto3_pre","c8_seto3_win","c8_seto3_lose","seto3_won",[card("Red-eyes B. Dragon")],deck="Seto 3rd",tier=9),
 D("darknite","darknite",37,8,"c8_darknite_pre","c8_darknite_win","c8_darknite_lose","darknite_won",[card("Zoa")],deck="DarkNite",tier=10),
 D("nitemare","nitemare",38,8,"c8_nitemare_pre","c8_nitemare_win","c8_nitemare_lose","nitemare_won",[item("time_stone"),{"give_card_custom":"Workers' Rights","fallback_card":"Dian Keto the Cure Master"},{"play_script":"c8_choice"}],deck="Nitemare",tier=10,note="Final boss. After win_script the engine plays c8_choice (Yes -> ending_home, No -> ending_stay)."),
 D("mirror","mirror","atos-vinicius",9,"side_mirror_pre","side_mirror_win","side_mirror_lose","mirror_won",[card("Hero of the East")],deck="Atos Vinicius",tier=10,note="Optional post-game duelist (stage 10)."),
]
DUELS[[d["id"] for d in DUELS].index("heishin2")]["pre_effects"]=[{"set_flag":"altar_scene_seen"}]

def X(id, stage_min, when, trigger, effects, script, note=None):
    t = {"id": id, "when": dict(when, stage=[stage_min, stage_min]), "trigger": trigger, "effects": effects, "script": script}
    if note: t["note"] = note
    return t

TRANSITIONS = [
 X("start",0,{},{"kind":"character_creation_done"},[{"set_stage":1}],"c1_intro"),
 X("c1_end",2,{},{"kind":"walk_north_of_tile_row","tile_z":20},[{"set_stage":3}],"c1_end__c2_intro",note="Legacy: pz < (4+16)*32."),
 X("c2_end",3,{"flags_all":["rex_won","weevil_won"]},{"kind":"walk_north_of_tile_row","tile_z":3,"object":"portal_ruins"},[{"set_stage":4},{"teleport":{"area":4,"tile":T(55,17)}}],"c2_end__c3_intro"),
 X("c3_end",4,{"flags_all":["seto_won"]},{"kind":"walk_north_of_tile_row","tile_z":4,"object":"palace_door"},[{"set_stage":5},{"teleport":{"area":5,"tile":T(55,39)}},{"place_npcs":"stage5"}],"c3_end__c4_intro"),
 X("c4_end",5,{"flags_all":["heishin_won"]},{"kind":"walk_north_of_tile_row","tile_z":25,"object":"throne"},[{"set_stage":6},{"teleport":{"area":6,"tile":T(24,68)}}],"c4_end__c5_intro"),
 X("c5_end",6,{"flags_all":["pegasus_won"]},{"kind":"walk_between_tile_rows","tile_z_min":56,"tile_z_max":59,"object":"castle_gate"},[{"set_stage":7},{"teleport":{"area":8,"spawn":"crossroads_portal"}},{"play_script_after":"c6_arrival"}],"c5_end__c6_intro",note="Legacy script 66 ended the game with 'Coming soon'; it now chains into c6_arrival."),
 X("c6_end",7,{"flags_all":TEMPLES},{"kind":"interact","object":"labyrinth_gate"},[{"set_stage":8},{"teleport":{"area":14,"spawn":"labyrinth_entrance"}}],"c6_end__c7_intro"),
 X("c7_end",8,{"flags_all":["heishin2_won"]},{"kind":"interact","object":"dark_stairs"},[{"set_stage":9},{"teleport":{"area":15,"spawn":"final_temple_gate"}}],"c7_end__c8_intro"),
 X("ending_home",9,{"flags_all":["nitemare_won"]},{"kind":"choice","script":"c8_choice","answer":"yes"},[{"set_flag":"ending_home"},{"set_stage":10},{"teleport":{"area":8,"spawn":"crossroads_portal"}}],"ending_home",note="After the ending the game keeps running in stage 10 with all side duelists."),
 X("ending_stay",9,{"flags_all":["nitemare_won"]},{"kind":"choice","script":"c8_choice","answer":"no"},[{"set_flag":"ending_stay"},{"set_stage":10},{"teleport":{"area":8,"spawn":"crossroads_portal"}}],"ending_stay"),
]

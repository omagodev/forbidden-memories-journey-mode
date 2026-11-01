#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builds duelist_kingdom/{en,pt}/*.json, decks_dk.json, kingdom_outline.json and the readable markdown."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import dk_data as D, dk_scripts as S, dk_kingdom as K

def dump(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False); f.write("\n")

def lang_story(lg):
    L = lg
    sp = {k: dict(name=v[0] if L == "en" else v[1], short=v[2], portrait=v[3], **({"note": v[4]} if v[4] else {})) for k, v in D.SPEAKERS.items()}
    flags = [dict(name=n, bit=i, value=1 << i, note=note) for i, (n, note) in enumerate(D.FLAGS)]
    areas = [dict(id=a[0], name=a[1] if L == "en" else a[2], setting=a[3], art=a[4]) for a in D.AREAS]
    items = [dict(id=i[0], name=i[1] if L == "en" else i[2], description=i[3] if L == "en" else i[4], source=i[5]) for i in D.ITEMS]
    def npc_json(n):
        o = dict(id=n["id"], name=sp[D.NPC_SPEAKER.get(n["id"], n["id"])]["name"], portrait_speaker=D.NPC_SPEAKER.get(n["id"], n["id"]), area=n["area"], anchor=n["anchor"],
                 duelist_id=n["duelist_id"], stages=n["stages"], visible=n["visible"])
        for k in ("patrol", "moves", "note"):
            if k in n: o[k] = n[k]
        o["dialogue_rules"] = n["rules"]; return o
    def obj_json(o):
        r = dict(id=o["id"], name=o["name"][L], area=o["area"], anchor=o["anchor"])
        if "solid_until" in o: r["solid_until"] = o["solid_until"]
        r["dialogue_rules"] = o["rules"]; return r
    duels = []
    for d in D.DUELS:
        duels.append(dict(id=d["id"], npc=d["npc"], duelist_id=d["duelist_id"], chapter=2 if d["pre"].startswith("dk2") else 1, deck=d["deck"], difficulty_tier=d["tier"], pre_script=d["pre"], win_script=d["win"], lose_script=d["lose"],
                          win_flag=d["win_flag"], on_win=d["on_win"], rewards_first_win_only=True, stars_wager=d.get("stars", 0) > 0, **({"stars": d["stars"]} if d.get("stars") else {}), note=d["note"]))
    quests = []
    for q in D.QUESTS:
        quests.append(dict(id=q["id"], kind=q["kind"], optional=q["opt"], title=q["title"][L], giver=q["giver"],
                           steps=[dict(objective=(s[0] if L == "en" else s[1]), anchor=s[2]) for s in q["steps"]], reward=q["reward"]))
    scripts = []
    for sc in S.SCRIPTS:
        pages = []
        for (spk, en, pt, ask, l_en, l_pt) in sc["pages"]:
            p = dict(speaker=spk, text=en if L == "en" else pt)
            if ask: p["ask"] = True
            if l_en: p["label"] = l_en if L == "en" else l_pt
            pages.append(p)
        scripts.append(dict(id=sc["id"], legacy_id=None, chapter=sc["chapter"], desc=sc["desc"], pages=pages))
    hud = [dict(when=w, text=en if L == "en" else pt) for (w, en, pt) in D.HUD]
    chapters = [dict(n=c["n"], title=c["title"][L], region=c["region"], stage=c["stage"], reward=c["reward"], unlock=c["unlock"]) for c in D.CHAPTERS]
    return {
     "schema": "journey-dk/1", "language": L, "title": "Duelist Kingdom - Ticket to the Island" if L == "en" else "Reino dos Duelistas - O Bilhete para a Ilha",
     "text_rules": {"charset": "ASCII letters, digits, space and . , ! ? ' - only (retail font). Braces only in tokens.", "limit": "At most 3 lines of 32 glyphs per page (greedy word wrap). {name} counts 10 glyphs, {a|b} the longer option.", "tokens": ["{name}", "{male|female}"]},
     "variables": {"stage": "int, see stages", "flags": "31-bit field, bit = index in flags[]", "stars": "int 0..12", "time_of_day": "'day' | 'night' (night = tint or night background, only used by the bench scene)", "eliminations": "int"},
     "speakers": sp, "flags": flags, "stages": [dict(stage=s, note=n) for s, n in D.STAGES], "chapters": chapters, "areas": areas, "anchors": D.ANCHORS,
     "npcs": [npc_json(n) for n in D.NPCS], "objects": [obj_json(o) for o in D.OBJECTS], "items": items, "new_duelists": D.NEW_DUELISTS,
     "observer_events": [dict(id=e["id"], n=e["n"], npc=e["npc"], sprite=e["sprite"], overlay=e["overlay"], area=e["area"], anchor=e["anchor"], **({"show_during": e["show_during"], "vanish": e["vanish"]} if "show_during" in e else {"interact_object": e["interact_object"]}), flag=e["flag"], note=e["note"]) for e in D.OBSERVER_EVENTS], "quests": quests, "duels": duels, "transitions": D.TRANSITIONS, "hud_objectives": hud, "scripts": scripts,
     "editor_notes": ["Chapter 1 (home town, harbor, ship) and chapter 2 (the Shore of Illusions, dk_chapter2.py). Kingdom arc: ../kingdom_outline.json.", "Anchors are symbolic: <area>.<anchor>. The engine dev binds them to picture or map coordinates."],
    }

def ui(lg):
    L = lg; t = lambda en, pt: en if L == "en" else pt
    return {
     "hud": {"objective_label": t("Objective:", "Objetivo:"), "stars": t("Stars: %d", "Estrelas: %d"), "chapter_label": t("Chapter %d", "Capitulo %d")},
     "menu": {"journal": t("Journal", "Diario"), "rumors": t("Rumors", "Boatos"), "backpack": t("Backpack", "Mochila"), "stamp_card": t("Stamp Card", "Cartao de Selos")},
     "stamp_card": {"slots": [t("Lost", "Perdido"), t("Won", "Ganho"), t("Given", "Dado")], "empty": t("Empty", "Vazio")},
     "star_ui": {"wager": t("Wager 1 star?", "Apostar 1 estrela?"), "gain": t("You took a star! Stars: %d", "Voce tomou uma estrela! Estrelas: %d"), "loss": t("You lost a star. Stars: %d", "Voce perdeu uma estrela. Estrelas: %d"),
                 "eliminated": t("Out of stars! Pegasus's staff gives you one more chance.", "Sem estrelas! A equipe de Pegasus da mais uma chance.")},
     "time": {"night": t("Night", "Noite"), "day": t("Day", "Dia")},
     "areas": {a[0]: (a[1] if L == "en" else a[2]) for a in D.AREAS},
     "notebook": [t("Rumor 1: a hooded man pays with golden stars and talks about a Kingdom.", "Boato 1: um homem de capuz paga com estrelas douradas e fala de um Reino."),
                  t("Rumor 2: a white ship takes duelists to an island. Winners get anything.", "Boato 2: um navio branco leva duelistas a uma ilha. Campeoes ganham qualquer coisa."),
                  t("Rumor 3: a torn poster says Star Passage. Three treasures. One duelist.", "Boato 3: um cartaz rasgado diz Passagem Estelar. Tres tesouros. Um duelista.")],
     "ask_yes_no": [t("Yes", "Sim"), t("No", "Nao")],
    }

def readable(lg, story):
    out = ["# Duelist Kingdom - chapter 1 dialogue (%s)\n" % lg]
    sp = story["speakers"]
    for sc in story["scripts"]:
        out.append("\n### %s\n_%s_\n" % (sc["id"], sc["desc"]))
        for p in sc["pages"]:
            who = p.get("label") if p["speaker"] == "narrator" else sp[p["speaker"]]["name"]
            out.append("- **%s**: %s%s" % (who, p["text"], "  _[Duel? Yes/No]_" if p.get("ask") else ""))
    return "\n".join(out) + "\n"

def main():
    for lg, sub, name in (("en", "en", "story_dk.json"), ("pt", "pt", "story_dk.pt.json")):
        st = lang_story(lg); dump(os.path.join(ROOT, sub, name), st)
        dump(os.path.join(ROOT, sub, "ui_dk.%s.json" % lg), ui(lg))
        open(os.path.join(ROOT, sub, "story_readable_dk.%s.md" % lg), "w", encoding="utf-8").write(readable(lg, st))
    decks = {"rules": "Same as ../../decks.json: 40 cards, max 3 copies, at least 14 distinct, no Ritual cards. The 'deck' key of a duel is looked up here first, then in ../../decks.json.",
             "decks": {k: dict(duelist=v["duelist"], chapter=2 if k == "Weevil Shore" else 1, difficulty_tier=v["tier"], theme=v["theme"], fixed=True, total=sum(v["cards"].values()), cards=v["cards"], notes=v["notes"]) for k, v in D.DECKS.items()},
             "starter": dict(note="The deck a new journey starts with: forty weak commons (strongest attack 1200). Beats Simon; struggles from the harbor on without new cards.", total=sum(D.STARTER_DECK.values()), cards=D.STARTER_DECK)}
    dump(os.path.join(ROOT, "decks_dk.json"), decks)
    ko = {"schema": "journey-dk-outline/1", "star_rules": K.STAR_RULES,
          "areas": [dict(id=a[0], name_en=a[1], name_pt=a[2], setting=a[3]) for a in K.KINGDOM_AREAS],
          "chapters": [dict(n=c["n"], id=c["id"], area=c["area"], title_en=c["title"][0], title_pt=c["title"][1], summary_en=c["summary"][0], summary_pt=c["summary"][1],
                            duelists=[dict(name=d[0], duelist_id=d[1], tier=d[2], stars=d[3], role=d[4]) for d in c["duelists"]], beat=c["beat"], stars_after=c["stars_after"]) for c in K.KINGDOM_CHAPTERS]}
    def pg(p, L):
        o = dict(speaker=p[0], text=p[1] if L == "en" else p[2])
        if p[3]: o["label"] = p[3] if L == "en" else p[4]
        return o
    mg = K.MAGO_DEV
    ko["mago_dev"] = {"rules": mg["rules"],
        "appearances": [dict(n=a["n"], chapter=a["chapter"], area=a["area"], id=a["id"], note=a["note"], pages_en=[pg(p, "en") for p in a["pages"]], pages_pt=[pg(p, "pt") for p in a["pages"]]) for a in mg["appearances"]],
        "payoff": dict(chapter=mg["payoff"]["chapter"], area=mg["payoff"]["area"], anchor=mg["payoff"]["anchor"], when=mg["payoff"]["when"], pages_en=[pg(p, "en") for p in mg["payoff"]["pages"]], pages_pt=[pg(p, "pt") for p in mg["payoff"]["pages"]])}
    dump(os.path.join(ROOT, "kingdom_outline.json"), ko)
    print("built", len(S.SCRIPTS), "scripts")
main()

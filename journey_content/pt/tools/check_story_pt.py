#!/usr/bin/env python3
"""Checks a translation of JOURNEY MODE against the English files (key parity, tokens, charset, 3x32 fit, rewards).
Usage: python3 check_story_pt.py [DIR]      DIR holds story.<lang>.json and ui.<lang>.json (default: ..; use ../accents for the accented set)
       python3 check_story_pt.py --lang xx DIR    for another language code (files story.xx.json / ui.xx.json)
The English source is ../../story.json, ../../ui.en.json, ../../decks.json. Exit 0 = ok.
DIR named 'accents' (or --accents) allows Latin accented letters; otherwise the retail font charset (ASCII) is enforced."""
import json, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
args = sys.argv[1:]; lang = "pt"; accents = False
if "--lang" in args: i = args.index("--lang"); lang = args[i + 1]; del args[i:i + 2]
if "--accents" in args: args.remove("--accents"); accents = True
D = os.path.abspath(args[0]) if args else os.path.join(HERE, "..")
if os.path.basename(D) == "accents": accents = True
LINE, LINES, NAME_W = 32, 3, 10
BASE = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?'-")
ALLOWED = BASE | (set("áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ") if accents else set())
TOKEN = re.compile(r"\{([^{}]*)\}")
errs, warns = [], []
def err(m): errs.append(m)
def load(p): return json.load(open(p, encoding="utf-8"))

def expand(text, where):
    def rep(m):
        t = m.group(1)
        if t == "name": return "N" * NAME_W
        if "|" in t:
            a, b = t.split("|") if t.count("|") == 1 else ("", "")
            if not a or not b: err("%s: bad gender token {%s}" % (where, t))
            return max(a, b, key=len)
        err("%s: unknown token {%s}" % (where, t)); return ""
    out = TOKEN.sub(rep, text)
    if "{" in out or "}" in out or "|" in out: err("%s: stray brace/pipe" % where)
    bad = sorted({c for c in out if c not in ALLOWED})
    if bad: err("%s: characters not allowed: %r" % (where, "".join(bad)))
    return out
def wrap(s):
    lines, cur = [], ""
    for w in s.split():
        if len(w) > LINE: return None
        t = (cur + " " + w) if cur else w
        if len(t) <= LINE: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines
def shape(a, b, path):
    """key parity: same dict keys, same list lengths, same types"""
    if type(a) is not type(b): err("%s: type %s vs %s" % (path, type(a).__name__, type(b).__name__)); return
    if isinstance(a, dict):
        for k in a.keys() - b.keys(): err("%s: MISSING key %r" % (path, k))
        for k in b.keys() - a.keys():
            if k != "translation_note": err("%s: EXTRA key %r" % (path, k))
        for k in a.keys() & b.keys(): shape(a[k], b[k], path + "/" + str(k))
    elif isinstance(a, list):
        if len(a) != len(b): err("%s: list length %d vs %d" % (path, len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)): shape(x, y, "%s[%d]" % (path, i))
def strings(o, path=""):
    if isinstance(o, str): yield path, o
    elif isinstance(o, list):
        for i, x in enumerate(o): yield from strings(x, "%s[%d]" % (path, i))
    elif isinstance(o, dict):
        for k, v in o.items(): yield from strings(v, path + "/" + k)

def main():
    en = load(os.path.join(ROOT, "story.json")); tr = load(os.path.join(D, "story.%s.json" % lang))
    decks = load(os.path.join(ROOT, "decks.json")); custom = {c["name"] for c in decks.get("custom_cards", [])}
    shape(en, tr, "story")
    if [s["id"] for s in en["scripts"]] != [s["id"] for s in tr["scripts"]]: err("script ids/order differ")
    ens = {s["id"]: s for s in en["scripts"]}; pages = 0; maxlen = 0; hist = {1: 0, 2: 0, 3: 0}
    for sc in tr["scripts"]:
        e = ens.get(sc["id"])
        if not e: continue
        for k in ("legacy_id", "chapter"):
            if sc.get(k) != e.get(k): err("%s: %s differs" % (sc["id"], k))
        for i, (p, q) in enumerate(zip(sc["pages"], e["pages"])):
            w = "%s[%d]" % (sc["id"], i); pages += 1
            if p["speaker"] != q["speaker"]: err(w + ": speaker differs")
            if bool(p.get("ask")) != bool(q.get("ask")): err(w + ": ask flag differs")
            if ("label" in p) != ("label" in q): err(w + ": label presence differs")
            if "label" in p:
                expand(p["label"], w + " label")
                if len(p["label"]) > 20: warns.append(w + ": label longer than 20 glyphs")
            plain = expand(p["text"], w); lines = wrap(plain)
            if lines is None: err(w + ": a word longer than %d glyphs" % LINE); continue
            maxlen = max(maxlen, len(plain))
            if len(lines) > LINES: err("%s: %d lines (max %d): %r" % (w, len(lines), LINES, p["text"]))
            else: hist[len(lines)] += 1
            # the same tokens as English must not vanish: {name} count
            if p["text"].count("{name}") != q["text"].count("{name}") and "{name}" in q["text"] + p["text"]:
                warns.append(w + ": {name} count differs from English")
            if p["speaker"] != "narrator" and not p["text"].strip(): err(w + ": empty")
    # visible strings of the other parts must be plain too
    for k, sp in tr["speakers"].items():
        if k == "narrator": continue
        expand(sp["name"], "speaker " + sp["name"]); expand(sp["short"], "speaker " + sp["short"])
    for h in tr["hud_objectives"]:
        expand(h["text"], "hud " + h["text"])
        if len(h["text"]) > 30: warns.append("hud text long: " + h["text"])
    for g in ("ask_yes_no", "area_names", "backpack_item_labels"):
        for pth, s in strings(tr["ui_strings"][g]): expand(s, "ui_strings " + pth)
    # a win page must name every card and item the player gets
    items = {i["id"]: i["name"] for i in tr["items"]}; scripts = {s["id"]: s for s in tr["scripts"]}
    for d in tr["duels"]:
        win = " ".join(p["text"] for p in scripts[d["win_script"]]["pages"])
        for e in d["on_win"] + d.get("pre_effects", []):
            for key in ("give_card", "give_card_custom"):
                if key in e and e[key] not in win: err("duel %s: win page does not name card %r" % (d["id"], e[key]))
            if "give_item" in e and items[e["give_item"]] not in win: err("duel %s: win page does not name item %r" % (d["id"], items[e["give_item"]]))
    # --- ui
    uen = load(os.path.join(ROOT, "ui.en.json")); utr = load(os.path.join(D, "ui.%s.json" % lang))
    shape(uen, utr, "ui")
    fmt = re.compile(r"%[sd]")
    for (pa, a), (pb, b) in zip(strings(uen), strings(utr)):
        if pa != pb: continue
        if fmt.findall(a) != fmt.findall(b): err("ui%s: format specifiers %s vs %s" % (pa, fmt.findall(a), fmt.findall(b)))
        if not b.strip(): err("ui%s: empty" % pa)
        if not accents:
            bad = [c for c in b if ord(c) > 127]
            if bad: err("ui%s: non-ASCII %r" % (pa, "".join(bad)))
    # cockatiel
    cp = os.path.join(D, "cockatiel.%s.json" % lang)
    if os.path.exists(cp):
        shape(load(os.path.join(ROOT, "cockatiel.json")), load(cp), "cockatiel")
        for pth, s in strings(load(cp)["extra_lines"]): expand(s, "cockatiel" + pth)
    print("[%s%s] scripts %d, pages %d, longest page %d glyphs; pages by lines: %s" % (lang, " accents" if accents else "", len(tr["scripts"]), pages, maxlen, hist))
    for w in warns: print("warning:", w)
    for e in errs: print("ERROR:", e)
    print("%d errors, %d warnings" % (len(errs), len(warns)))
    return 1 if errs else 0
if __name__ == "__main__": sys.exit(main())

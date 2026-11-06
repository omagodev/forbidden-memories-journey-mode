#!/usr/bin/env python3
"""Real-engine regression: private deck/chest, classic slots ON, editor return and cold reload.
Run after build_game32.py + ow-poc deployment; uses isolated tmp/smoke/deck_inventory.
"""
import collections
import json
import struct
from jm_smoke import Run, MOD


def deck(g):
    return list(struct.unpack("<40H", g.peek("gDuel_awPlayerDeck", 80)))


def editor(r):
    g = r.g
    g.press("start", hold=5, after=30)
    g.press("cross", hold=5, after=30)
    g.step(400)
    assert g.mode() == 7, "not in Build Deck"
    assert g.u8("D_8009B26C") & 0x40, "classic slot picker intercepted Journey editor"
    g.press("circle", hold=5, after=60)
    g.step(400)
    assert g.mode() == 13, "did not return to Journey"


def main():
    r = Run("deck_inventory", {"preset": "6 Hakim's hint (Kemet next)",
                              "settings": {"deck_slots": 1}, "debug": {}})
    r.write_save()
    try:
        r.start()
        g = r.g
        starter = json.loads((MOD / "assets/journey.json").read_text())["starter_deck"]
        assert collections.Counter(deck(g)) == collections.Counter(starter), "legacy imported classic deck"
        # Legacy save had no rewards: no cards may leak from classic chest.
        assert not any(g.peek("gLibrary_abCardChest", 722)), "classic chest leaked into Journey"
        code = g.u32("gDuel_awPlayerDeck", offset=0x334)
        slots_dir = r.dir / "user/decks"
        slots_dir.mkdir(exist_ok=True)
        slot_file = slots_dir / ("%08X.txt" % code)
        classic = "1: " + ",".join(str(i) for i in range(1, 41)) + "\n"
        slot_file.write_text(classic)
        # A run-owned card and a different deck order must survive editor and cold boot.
        card = next(i for i in range(1, 723) if i not in starter)
        chest = bytearray(722)
        chosen = list(reversed(starter))
        chest[chosen[0] - 1] = 1
        chosen[0] = card
        chest[card - 1] = 1
        g.poke("gLibrary_abCardChest", bytes(chest))
        g.poke("gLibrary_dwStarchips", struct.pack("<I", 37))
        g.poke("gDuel_awPlayerDeck", struct.pack("<40H", *chosen))
        editor(r)
        assert collections.Counter(deck(g)) == collections.Counter(chosen)
        assert g.peek("gLibrary_abCardChest", 722) == chest
        saved = (r.data / "journey.sav").read_bytes()
        assert struct.unpack_from("<I", saved, 4)[0] == 8
        # A sold recorded reward must NOT be recreated by modern loads.
        saved = bytearray(saved)
        struct.pack_into("<H", saved, 12 + 76, 722)
        struct.pack_into("<i", saved, 12 + 172, 1)
        (r.data / "journey.sav").write_bytes(saved)
        g.close()
        (r.data / "debug.json").unlink(missing_ok=True)
        r.start()
        g = r.g
        assert collections.Counter(deck(g)) == collections.Counter(chosen), "deck lost on cold boot"
        assert g.peek("gLibrary_abCardChest", 722) == chest, "run chest lost on cold boot"
        assert g.u32("gLibrary_dwStarchips") == 37, "performance stars lost"
        editor(r)
        assert g.peek("gLibrary_abCardChest", 722) == chest, "reopening duplicated/lost cards"
        assert slot_file.read_text() == classic, "Journey overwrote classic deck slot"
        assert len(list(slots_dir.glob("*.txt"))) == 1, "Journey wrote classic deck slots"
        print("PASS: legacy migration, slots ON bypass, editor return, v8 save, cold reload, reopen, exact chest/stars")
    finally:
        if r.g:
            r.g.close()


if __name__ == "__main__":
    main()

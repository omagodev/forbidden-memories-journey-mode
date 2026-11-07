#!/usr/bin/env python3
"""Scripted smoke tests of Journey Mode: boot the game under Xvfb, set a story state, replay a few pad inputs, take screenshots, check the log.

    python3 mods/ow-poc/tools/smoke/jm_smoke.py list
    python3 mods/ow-poc/tools/smoke/jm_smoke.py run dk_part2_bench [more names]
    python3 mods/ow-poc/tools/smoke/jm_smoke.py quick          # critical path only (scenarios marked quick=True)
    python3 mods/ow-poc/tools/smoke/jm_smoke.py all            # regression: every scenario, pass/fail table, results in tmp/smoke/
    python3 mods/ow-poc/tools/smoke/fast.py                    # presets + quick list (see also mods/ow-poc/tools/TESTING.md)

The story state comes from the mod's debug aid (jm_debug.c): the harness writes a debug.json into the run's mod-data folder (a preset of
journey.json "debug", flags, a teleport, skip dialogue, win duels) and a minimal journey.sav, so a scenario starts where it needs to
without replaying the story.  Scenarios are in scenarios.py.  Environment: SMOKE_DISPLAY (default :92), JM_GAME (a game dir, default
tmp/pc/game32), MEMORIES_DISC (default <repo>/../game/YUGIOH.bin, else ./game/*.bin), SMOKE_OUT, SMOKE_SCALE (internal_scale, default 1)."""
import os, sys, json, time, struct, subprocess, shutil, glob
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = HERE.parent.parent
REPO = MOD.parent.parent
sys.path.insert(0, str(REPO / "tools" / "pc"))
sys.path.insert(0, str(HERE))
DISPLAY = os.environ.get("SMOKE_DISPLAY", ":92")
os.environ["DISPLAY"] = DISPLAY
import yfm_control as Y                       # noqa: E402

GAME = Path(os.environ.get("JM_GAME", REPO / "tmp/pc/game32"))
OUT = Path(os.environ.get("SMOKE_OUT", REPO / "tmp/smoke"))
SCALE = int(os.environ.get("SMOKE_SCALE", "1"))
FORBID = ["no scene", "unknown flag", "syntax error", "Segmentation", "Traceback", "mod error"]


def disc():
    for c in [os.environ.get("MEMORIES_DISC"), REPO.parent / "game" / "YUGIOH.bin", *glob.glob(str(REPO / "game" / "*.bin"))]:
        if c and Path(c).exists():
            return str(c)
    raise SystemExit("no disc image: set MEMORIES_DISC")


class Run:
    def __init__(self, name, sc):
        self.name, self.sc = name, sc
        self.dir = OUT / name
        shutil.rmtree(self.dir, ignore_errors=True)
        (self.dir / "shots").mkdir(parents=True)
        self.log = self.dir / "game.log"
        self.data = self.dir / "user" / "mod-data" / "ow-poc"
        self.data.mkdir(parents=True)
        self.flags = json.load(open(MOD / "assets" / "journey.json"))["flags"]
        self.shots = []
        self.g = None

    def write_save(self):
        """a minimal valid save (stage 1, no flags, language per scenario); the debug.json moves the story from there"""
        lang = self.sc.get("lang", 0)
        body = struct.pack("<IiiiiI", 0, 1, 0, 0, 0, 0) + b"Atos".ljust(20, b"\0")
        body += struct.pack("<6i", 0, 0, 1, 0, 0, 0) + struct.pack("<ff", 14.5 * 32, 33.5 * 32)
        body += b"\0" * 96 + struct.pack("<i", 0)
        body += struct.pack("<iffi", lang, 184, 273, 1)
        if self.sc.get("boot") == "new":                # NEW GAME from the title: no save, the language is already chosen (language.cfg)
            (self.data / "language.cfg").write_text("%d\n" % lang)
        else:
          (self.data / "journey.sav").write_bytes(struct.pack("<III", 0x31534A4D, 3, 192) + body)
        dbg = dict(self.sc.get("debug", {}))
        if "preset" in self.sc:
            dbg["preset"] = self.sc["preset"]
        if not self.sc.get("no_debug_json"):          # without it the mod runs as a release build (no debug aid, Dev mode off by default)
            (self.data / "debug.json").write_text(json.dumps(dbg))
        if "devcfg" in self.sc:                        # devmode.cfg: the saved Dev mode choice ("0" / "1")
            (self.data / "devmode.cfg").write_text(self.sc["devcfg"] + "\n")

    def count(self, pat):
        try:
            return sum(1 for l in open(self.log, errors="replace") if pat in l)
        except FileNotFoundError:
            return 0

    def snap(self, label):
        p = self.dir / "shots" / ("%02d_%s.png" % (len(self.shots), label))
        # ImageMagick `import` when present; else ffmpeg x11grab (same root window).
        try:
            r = subprocess.run(["import", "-display", DISPLAY, "-window", "root", str(p)], check=False)
            ok = r.returncode == 0 and p.is_file() and p.stat().st_size >= 100
        except FileNotFoundError:
            ok = False
        if not ok:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab",
                            "-video_size", "1920x1200", "-i", "%s.0" % DISPLAY,
                            "-frames:v", "1", "-update", "1", str(p)], check=False)
        if (not p.is_file() or p.stat().st_size < 100) and self.g is not None:
            try:
                self.g.shot(p)  # VRAM fallback
            except Exception:
                pass
        self.shots.append(str(p))

    def start(self):
        env = {"MEMORIES_DISC": disc(), "MEMORIES_TRACE": "mods", "MEMORIES_SHOW_HUD": "1", "LIBGL_ALWAYS_SOFTWARE": "1",
               "MEMORIES_USER_DIR": str(self.dir / "user")}
        st = {"internal_scale": SCALE, "hd_text": 1, "mod.3d-monsters": 0, "mod.ow-poc": 1}
        st.update(self.sc.get("settings", {}))
        self.g = Y.Game(executable=str(GAME / "memories-pc"), out=str(self.dir), settings=st, headless=False, env=env)
        g = self.g
        g.wait_until(lambda g: g.resident("main_menu"), 6000)
        g.step(300)
        g.press("start", hold=8, after=10); g.step(120)
        g.press("start", hold=8, after=10); g.step(150); g.step(40)
        if self.sc.get("boot") != "new": g.press("down", hold=6, after=20)
        g.press("cross", hold=6, after=20)                                       # JOURNEY MODE > Continue (or New game)
        g.step(self.sc.get("boot_frames", 260))

    def until(self, pat, frames):
        t = 0
        while self.count(pat) < 1 and t < frames:
            self.g.step(15); t += 15
        return self.count(pat) >= 1

    def step_(self, s):
        g, op = self.g, s[0]
        if op == "wait": g.step(s[1])
        elif op == "press": g.press(s[1], hold=s[2] if len(s) > 2 else 5, after=s[3] if len(s) > 3 else 12)
        elif op == "hold": g.press(s[1], hold=s[2], after=4)
        elif op == "until":
            if not self.until(s[1], s[2] if len(s) > 2 else 900): self.problems.append("timeout waiting for log %r" % s[1])
        elif op == "snap": self.snap(s[1])
        elif op == "release":                 # the player's view: no debug.json, Dev mode off, Continue from the save just made
            for f in ("debug.json",): (self.data / f).unlink(missing_ok=True)
            (self.data / "devmode.cfg").write_text("0\n")
            try: self.g.close()
            except Exception: pass            # noqa: BLE001
            time.sleep(1)
            self.start()
        elif op == "restart":                 # close the game and start it again on the same user folder (settings that persist)
            try: self.g.close()
            except Exception: pass            # noqa: BLE001
            time.sleep(1)
            self.start()
        elif op == "duel_win":                # a real duel: wait for the field, set the opponent's life points to 0, press through the result screens
            g.duel_ready(); g.step(60)
            g.poke("D_800E9FF0", struct.pack("<hHh", 0, 0, 8000), offset=Y.SIDE_SIZE + 0x12)
            g.step(300)
            for _ in range(40):
                if g.mode() != Y.MODE["duel"]: break
                g.press("circle", hold=4, after=40)
            self.until("duel over", s[1] if len(s) > 1 else 1800)
        elif op == "duel_kill":               # a real duel won by a real attack: the opponent's LP set low, a monster played face up, a direct attack
            g.duel_ready(); g.step(60)
            g.poke("D_800E9FF0", struct.pack("<hHh", 100, 100, 8000), offset=Y.SIDE_SIZE + 0x12)
            for _turn in range(14):
                if g.duel_over(): break
                hand = g.duel()[0]["hand"]
                slot = next((i for i, c in enumerate(hand) if c and c["attack"] > 0), 0)
                g.play_card(slot, face_up=True)
                if g.duel_over(): break
                g.poke("D_800E9FF0", struct.pack("<hHh", 100, 100, 8000), offset=Y.SIDE_SIZE + 0x12)
                g.poke("D_800E9FF0", struct.pack("<hHh", 8000, 8000, 8000), offset=0x12)   # a test: the player outlasts the deck
                mine = [c for c, m in enumerate(g.field()[2]) if m]
                theirs = [c for c, m in enumerate(g.field()[1]) if m]
                if mine:
                    # a test: the attacker made strong enough that any hit ends the duel (the opponent at 100 LP)
                    grid, recs = g.peek("D_800907D8", 20), g.peek("D_801A7AD8", 30 * Y.RECORD_SIZE)
                    g.poke("D_801A7AD8", struct.pack("<h", 9000), offset=grid[10 + mine[0]] * Y.RECORD_SIZE + 0x0E)
                    atk = [c for c in theirs if not struct.unpack_from("<H", recs, grid[5 + c] * Y.RECORD_SIZE + 0x16)[0] & 0x0800]
                    try: g.attack(mine[0], atk[0] if atk else (theirs[0] if theirs else None))
                    except Exception as e: print("attack:", e)
                if g.duel_over(): break
                g.end_turn()
            for _ in range(80):
                if g.mode() != Y.MODE["duel"]: break
                g.press("cross", hold=4, after=40)
            self.until("duel over", s[1] if len(s) > 1 else 1800)
        elif op == "poke_deck":               # a test: deck slot s[1] holds card s[2] (what the deck editor writes)
            g.poke("gDuel_awPlayerDeck", struct.pack("<H", s[2]), offset=2 * s[1])
        elif op == "check_deck":              # deck slot s[1] must hold card s[2]
            got = struct.unpack("<H", g.peek("gDuel_awPlayerDeck", 80)[2 * s[1]:2 * s[1] + 2])[0]
            if got != s[2]: self.problems.append("deck slot %d holds %d, not %d" % (s[1], got, s[2]))
            else: print("deck slot %d holds %d" % (s[1], got))
        elif op == "poke_extra":              # a test: own s[2] copies of mod card s[1] (the extra chest)
            g.poke("gCard_abExtraChest", bytes([s[2]]), offset=s[1])
        elif op == "deck_has":                # the deck must hold card s[1] (any slot)
            deck = struct.unpack("<40H", g.peek("gDuel_awPlayerDeck", 80))
            if s[1] in deck: print("deck holds %d at slot %d" % (s[1], deck.index(s[1])))
            else: self.problems.append("deck lacks %d: %s" % (s[1], deck))
        elif op == "mash":                    # press X every 40 frames until a log line shows (dialogue that is not skipped)
            t = 0
            while self.count(s[1]) < 1 and t < (s[2] if len(s) > 2 else 3000):
                g.press("cross", hold=4, after=36); t += 40
            if self.count(s[1]) < 1: self.problems.append("timeout mashing X for log %r" % s[1])
        else: raise SystemExit("unknown step %r" % (s,))

    def go(self):
        self.problems = []
        t0 = time.time()
        try:
            self.write_save()
            self.start()
            t1 = time.time()
            for s in self.sc["steps"]:
                self.step_(s)
        except Exception as e:                # noqa: BLE001
            self.problems.append("exception: %r" % (e,))
            t1 = t0
        finally:
            try: self.g.close()
            except Exception: pass            # noqa: BLE001
        for pat in self.sc.get("expect", []):
            n = 1
            if isinstance(pat, (tuple, list)): pat, n = pat
            if self.count(pat) < n: self.problems.append("log lacks %r (x%d)" % (pat, n))
        for pat in FORBID + self.sc.get("forbid", []):
            if self.count(pat): self.problems.append("log has %r" % pat)
        t2 = time.time()
        return {"name": self.name, "ok": not self.problems, "problems": self.problems, "boot_s": round(t1 - t0, 1),
                "total_s": round(t2 - t0, 1), "shots": self.shots, "log": str(self.log)}


def main(argv):
    import scenarios
    S = scenarios.SCENARIOS
    cmd = argv[1] if len(argv) > 1 else "list"
    if cmd == "list":
        for k, v in S.items():
            mark = "*" if v.get("quick") else ("!" if v.get("slow") else " ")
            print("%s %-28s %s" % (mark, k, v["desc"]))
        print("* = quick suite; ! = slow (skipped by all)")
        return 0
    if cmd == "quick":
        names = [k for k, v in S.items() if v.get("quick") and not v.get("slow")]
    elif cmd == "all":
        names = [k for k, v in S.items() if not v.get("slow")]
    else:
        names = argv[2:]
    if cmd not in ("run", "all", "quick") or not names or any(n not in S for n in names):
        print(__doc__); return 2
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for n in names:
        r = Run(n, S[n]).go()
        results.append(r)
        print("%-4s %-28s %5.1fs  %s" % ("PASS" if r["ok"] else "FAIL", n, r["total_s"], "; ".join(r["problems"])), flush=True)
    json.dump(results, open(OUT / "results.json", "w"), indent=1)
    bad = [r for r in results if not r["ok"]]
    print("%d/%d passed; shots and logs in %s" % (len(results) - len(bad), len(results), OUT))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

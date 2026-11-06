<p align="right"><a href="TESTING.pt-BR.md"><img src="https://img.shields.io/badge/Ler_em_Portugu%C3%AAs-009c3b?style=for-the-badge&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM%2FrhtAAADvklEQVR42u2XXUybZRiGr1L8aC20YAt2UEopLHR2n4oHQDJnPDAx2zTMEzMzMCNqPHDJDvyJB4uZzMREs83FJYsJCyQzUZPFv2Qsi1M3DQaDBG0lQlbKaKE0%2FJT%2BUGg%2FWuYBaZNKyzoGAbX32fe97%2Fvkzv28z%2F08L%2BSQQw7%2Fbsg49%2BTt7Uwwb7sr%2BP8i2FgYoLEwsP0IquUxThsd9FoH6LUOcNroQC2PbY8i2V88yyfVwxgEKeX%2FuCTw6mgd3X7t1ihoFBbpNA9xuc6%2BihyAQZC4XGen0zx0T2quS8GXyiY5ZRxBI48RCiu4eGUPdkc5Q7f0AFhMXsRaD637eihSRZiJ3cfbbjMXpnZsLkGjsMinNUPsVa8UQs%2FvtbR3NDM1p067v6wkyDsvf8OeRx0A%2FBzU0DJiwSUpsyYoZ7%2FpRDYbj1eMcWnnIGZFJEnu6IethCMFGc%2BEIwV0%2F%2FIIYs04Rr2PqoIorz3oAZmMn0LFG3MHGwsD2MQ%2BThpGEfJWxA6FFbR3NGetQntHM6GwAgAh7zYnDaPYxL6sLCljitXyGGerHBwp9a5auzT6JlpLK7pSFTtUWn5w%2FkFpXgkLnjg%2FXhvktxtuyo3F%2FGWfSp55o%2BUKh%2Ff1rorVNa3n2FgtwXh%2BWoL5d2MdCTj7Inz5RQ%2BOoRkASnRKtDoV5dVF1DbpaGipRBtScuGj%2FiRJm6OSw6wmeKTUy1MaX0ZLSlHQKCxytmqEgw%2FMrCn700dfz1gYACazmprdpTS0VOJzLPLVx39CZJKr506tGfdrn45jYzUpRbQuH5Riqcc0GiHl%2B5YzyPffjvD%2B89cJumO8d%2FFZxL316%2FLBlBS7JCXP3dx9xxRbTF684ceYcM%2BztLRMICAllUsQTOCz8%2F3cHJjm0CvWjCTW6jppFez2a7HaGuia1qcNKNZ6mJuNsLS0zC6xLPl%2Fwj2fQi5B2jU2y8h3H6SN1TWtx2pryNgSM6Y4GM%2BnzWmhabAe%2B4IqZe3gE%2F3Iln0AeFz%2BpHIVlYWYzOpkyk1mNbqyYu5Xynmm8VpKDPuCiqbBetqclowVnJVRT0gKzk9VEEfG44UB5DIoUkWo0vu42isSjcbxz0UB8M9F8c9FiUbj7BLLmPbOM%2B7yc%2FzFTh7eOb5yf5dlnJio5gXHQ0xIiq1tdcbKJd469Pk9tbr%2F1rDwTzXfNYyl7TR30yk2bR50SUranBYODIuMS0Ja6zgwLN6xCDZ95E9Y0plJQ7IIzkwa1rSOLXsXJ6aTX%2Bc1G%2FZoymcDsZHEcg%2F3HHLIIYcV%2FA2BwaA%2BPOkCagAAAABJRU5ErkJggg%3D%3D" alt="🇧🇷 Ler em Português (BR)"></a></p>

# Testing Journey Mode: Duelist Kingdom, part 3

How to run and check the home-town arc up to part 3. The fast test loop (validator, `fast.sh`, scenario syntax, debug aid) is described in [`mods/ow-poc/tools/TESTING.md`](../mods/ow-poc/tools/TESTING.md); this page covers what part 3 adds.

You need your own legal copy of the USA disc (SLUS-01411). No game data is in this repository or in the release. Set `MEMORIES_DISC` to your disc image's `.bin` for the scripted runs, or pick it with "Choose ROM..." in the Windows build.

## Part 3 (test build)

After the Stamp Card (end of part 2) the story opens three quests that can be done in any order. Each gives one stamp (Lost / Won / Given). When all three glow, the guard lets you cross the bridge to the harbor; the harbor itself is part 4, so for now you get a "Quest complete" banner and the story ends at "Part 3 complete".

* **Quest 4, The Lost.** Win Kemet's lantern (part 2), walk to the little pyramid at the village edge and press X at the hatch. It opens onto the cistern, a new illustrated area (sandstone vault, water, torches, 320x180 map). A glyph on the wall brings the Mago.dev observer, who glitches away; then the ghost Bakura appears. Talk to him and duel him (deck "Yami Bakura"). Win: the Founder's Scarab and the Lost stamp. The stairs where you came in lead back out.
* **Quest 5, The Won.** Jono lost his bandana to Rex Raptor, who stands on the east road while this quest is open. Duel Rex (deck "Rex Raptor"), win Jono's Bandana and bring it back for the Won stamp.
* **Quest 6, The Given.** Teana wants honey (from Hakim the baker), river water (fill her jug at the river bank) and dates (shake the date palm). Bring them to her, win her duel (deck "Teana") and get the Lucky Charm and the Given stamp.

The yellow arrow and the objective bar follow the next task; the journal (A) lists the three quests and hides each when done. Banners (objective, item, stamp, quest complete) are separate from speech.

### Keys

Arrows walk, S runs, X talks or examines, A opens the journal, Right Shift the mini-map, ENTER the menu.

### Debug aid (off by default)

Rename `mods/ow-poc/debug.json.OFF` to `debug.json` (repository) or create `mods/ow-poc/debug.json` (`{}` is enough). Without that file no debug key does anything. You need a Journey save (NEW GAME, walk a few steps, ENTER > Save, then CONTINUE).

Hold R1 (W), then L1 (Q) and:

| Keys | Effect |
|---|---|
| Up / Down | next / previous story preset (the world is rebuilt) |
| Left | time of day: story decides > night > day |
| Right | teleport to the next named place |
| Square (Z) | skip dialogue on/off |
| Triangle (A) | win duels on/off (a duel counts as won, rewards included) |

Presets (`DEBUG_PRESETS` in `mods/ow-poc/tools/dk_to_journey.py`, written to `journey.json`): 1 home door, 2 rumors heard, 3 Simon won (bench next), 4 night / hooded man waits, 5 Stamp Card (Hakim next), 6 Hakim's hint (Kemet next), 7 Lantern won (hatch next), 8 in the cistern (Bakura), 9 Lost stamp (glyph, stairs), 10 Jono asked (Rex next), 11 Teana's errands, 12 errands done, 13 two stamps (Teana last). Presets 8 and 9 place you in the cistern. The debug file also accepts `preset`, `flags`, `stage`, `teleport`, `time`, `skip_dialogue` and `win_duels`. Progress made while debugging is saved with the normal save, so keep a copy of `journey.sav` first.

### Scripted checks

```
python3 mods/ow-poc/tools/validate_story.py
mods/ow-poc/tools/fast.sh --convert      # re-run the story converter, validate, build, deploy
mods/ow-poc/tools/fast.sh all            # every scenario, PASS/FAIL table
```

Part 3 scenarios: `dk_part3_hatch_locked`, `dk_part3_cistern`, `dk_part3_glyph`, `dk_part3_exit`, `dk_part3_rex`, `dk_part3_honey`, `dk_part3_water`, `dk_part3_dates`, `dk_part3_teana_end`, `dk_part3_journal_en`, `dk_part3_journal_pt`, `ui_banners_p3_en`, `ui_banners_p3_pt`. Scripted runs use Xvfb on display `:92`.

### Known limits (part 3)

* The duels with Rex, Bakura and Teana are real duels in the game, but the automated scenarios only check them with the debug "win duels" option; playing them for real is untested.
* The cistern is a single illustration lit only by torch glow (no animated water). Its collision map is hand-made, so a spot may differ from the picture by a few steps.
* The Bakura sprite is drawn with a dither, so the face is small and soft.
* Saving inside the cistern returns you to the hatch in the village when you continue.
* The Mago.dev glyph is drawn by code, not by an illustrated asset.
* The cistern song and the new sound effects were chosen by measurement, not by ear (`journey.json` `"painted": {"music": ...}`).
* The Windows executable has not been run by the author with part 3; the logic was checked on Linux (Xvfb) with the same mod object.


## Fast path (presets + quick suite)

Story checks used to mean a full play-through. Prefer the **debug presets** and the **quick suite**:

| What | Command |
|---|---|
| List every debug preset (ch1…current) | `python3 mods/ow-poc/tools/smoke/fast.py presets` |
| Help + preset table + quick list | `python3 mods/ow-poc/tools/smoke/fast.py` |
| Critical-path smoke only (gates, wager open/bet-1/GAME OVER, chapter jumps) | `mods/ow-poc/tools/fast.sh --quick` or `python3 mods/ow-poc/tools/smoke/jm_smoke.py quick` |
| One beat in ~15–40 s | `mods/ow-poc/tools/fast.sh quick_wager_bet1_win` (or any scenario name) |
| Full regression | `mods/ow-poc/tools/fast.sh all` |

Presets live in `DEBUG_PRESETS` (`mods/ow-poc/tools/dk_to_journey.py`) and are written into `journey.json` `"debug"`. In-game (with `debug.json` present): hold R1 then L1, Up/Down cycles presets. Smoke scenarios set `"preset"` in their `debug.json` so a run starts on that beat without replaying the story.

Star-wager coverage in the quick suite: `quick_wager_picker` (picker opens), `quick_wager_bet1_win` (bet 1 and win), `quick_wager_gameover` (lose remaining stars → GAME OVER). Full rematch / big-bet cases stay in `wager_*` and `final_wager_*` under `all`.


<div align="center">

# ⚔️ Journey Mode
### A story-driven RPG mode for *Yu-Gi-Oh! Forbidden Memories*

Walk painted maps, talk to the duelists of Forbidden Memories, take quests and fight real duels with the game's own engine.

[![Release](https://img.shields.io/github/v/release/omagodev/forbidden-memories-journey-mode?include_prereleases&label=release)](https://github.com/omagodev/forbidden-memories-journey-mode/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-blue)
![Languages](https://img.shields.io/badge/lang-EN%20%7C%20PT--BR-orange)
![Status](https://img.shields.io/badge/status-alpha-red)

**English** · [Português (BR)](README.pt-BR.md)

![Painted home town with dialogue](docs/media/village_dialogue.png)

</div>

---

## What is this?

Journey Mode is a fan-made, just-for-fun project. I took the amazing work of the Forbidden Memories community, adapted it, and wanted to build an **RPG story** on top of the game I grew up with.

The core idea: the duelists from the game's memory are **linked directly to NPCs on the map**. You walk up to Simon, Teana, Jono or Rex Raptor in a painted village, talk to them, and when a duel starts it is the real Forbidden Memories duel, with the real decks, the real AI and the real fusions.

## Why sprites and not 3D?

My first goal was a game that could still run on a **PlayStation 1**. I started with low-poly 3D maps, but the PS1 graphics engine only handles so many vertices, and the result never looked the way I wanted.

So I switched to **painted 2D backgrounds with sprites**. They are far lighter than 3D models, and with a few tricks (layered overlays, swaying palms, animated water and fire, occluders you walk behind) they make the player feel they're in a rich, good-looking map, which the 3D version couldn't deliver with that vertex budget. Today the mode runs on the native PC port, but it keeps that PS1-era spirit.

| | |
|---|---|
| ![Objective banner in the village](docs/media/village_objective.png) | ![Underground arena](docs/media/arena.jpg) |
| *Quests and objectives in the home town* | *The clandestine underground arena, lit by animated fire* |

## The story

> **The Duelist Kingdom** (work in progress)

You are a young duelist from **Oasis Village**, a sleepy desert town where everyone shuffles cards in the sun. Rumors start spreading about a tournament on a faraway island, a place where duelists wager **star chips** and only the best reach the castle.

* **Chapter 1: Home town.** Prove yourself in Simon's test duel. On a quiet night a hooded stranger hands you a Stamp Card. Earn three stamps through creative quests (something lost, something won, something given), pass the harbor exam and face Shadi's trial. Win the **Star Passage** and your first star, just like Joey did, then say goodbye at the pier.
* **On the ship** you meet Mai, learn the star rules, and run into **InsetoKaiba**: an arrogant, insect-obsessed rival in a white coat with a pompadour, and a parody you won't forget.
* **The Kingdom (chapters 2-10, outlined):** the Shore of Illusions, the Forest of Whispers, the Mountain Pass, the Meadow Maze, the Desert of Lost Stars and the Star Fair. Win stars, lose stars, never get a game over. Reach **10 stars** to open the castle gate and climb to Pegasus's Dream Room.
* **Mago.dev, the observer.** A mage who *programs reality* but never interferes. You'll catch glimpses of him on rooftops, in green glyphs on a cistern wall and at the top of a mast... until the very end.

The full outline is in [`journey_content/duelist_kingdom/`](journey_content/duelist_kingdom/README.md), and every line of dialogue in reading order is in [English](journey_content/duelist_kingdom/en/story_readable_dk.en.md) and [Portuguese](journey_content/duelist_kingdom/pt/story_readable_dk.pt.md). Spoilers, of course.

## Characters

<div align="center">

![Characters](docs/media/characters.png)

*Top: InsetoKaiba and Mago.dev (robe and t-shirt). Bottom: hero (test), Simon, Teana, the guard, Jono, the rival, Mago.dev, the baker, the farmer, Rex Raptor and Bakura as in-game walking sprites.*

</div>

## Features

- 🗺️ **Painted maps:** a home town, a cistern and an underground arena, with animated water, fire and swaying palms
- 🧑‍🤝‍🧑 **NPCs linked to Forbidden Memories duelists:** talk, take quests, and duel them with the original engine
- 🎭 **Character creator:** build your hero from layered parts (body, outfit, hair, accessory)
- 📜 **Quests, objectives and a journal**, with an objective arrow and a mini-map
- 💰 **Economy (early):** money, a shop in every town and card drops from the local card pool only
- 🥷 **Duelist gang (early):** they ambush you at a set frequency, you can't run, and if they win they take your money
- 🔥 **Clandestine arenas (early):** farm local cards and level up
- 🌐 **English and Brazilian Portuguese**
- 🛠️ **Dev mode** and fast test scenarios that jump straight to any story point

## Play

1. Download the latest build from [**Releases**](https://github.com/omagodev/forbidden-memories-journey-mode/releases) and extract it.
2. Run `JOGAR_JourneyMode.bat` (or `memories-pc.exe`).
3. On first launch, pick **your own** USA disc image (`SLUS-01411`, `.bin`). **No game data is included.**
4. On the title screen, choose **NEW GAME** to create your character.

## Build and contribute

Everything you need to set up, build and test is in [**docs/CONTINUE_DEVELOPMENT.md**](docs/CONTINUE_DEVELOPMENT.md). The short version:

```sh
./build-pc.sh                                         # build the port
python3 tools/pc/build_mod.py --target i386 mods/ow-poc   # build Journey Mode
```

| Folder | What's inside |
|---|---|
| [`mods/ow-poc/`](mods/ow-poc) | The Journey Mode mod: C code, baked maps and sprites, tools |
| [`journey_content/`](journey_content) | Story, decks, economy and UI text (EN/PT) with validators |
| [`art_dk/`](art_dk) | Art sources and bake pipelines |
| [`docs/`](docs) | Hand-off guide, testing and [the native port's docs](docs/PORT.md) |

Ideas, bugs and pull requests are very welcome: see [CONTRIBUTING.md](CONTRIBUTING.md) and the [roadmap](ROADMAP.md).

## Roadmap

The highlights (full list in [ROADMAP.md](ROADMAP.md)):

- [x] Painted home town, NPCs, dialogue, quests and chapter 1
- [x] Character creator with layered sprites
- [x] Underground arena with animated fire
- [ ] Economy, gang and arenas: balance and polish
- [ ] Duelist Kingdom chapters 2-10
- [ ] More painted areas: harbor, ship and the island zones
- [ ] 🌐 **Online multiplayer**: duel your friends from the map

## Built on the shoulders of giants

This project would not exist without:

- **[Yu-Gi-Oh! Forbidden Memories Recompiled](https://github.com/Unchiga/Yu-Gi-Oh-Forbidden-Memories-Recompiled)** by Unchiga and contributors: the native PC port, renderer and mod loader everything here runs on. Go support them.
- **[memories-decomp](https://github.com/krystalgamer/memories-decomp)** by krystalgamer and its authors: the decompilation behind the port.
- The **[Liberated Pixel Cup](https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator)** artists, **Kenney** and **Quaternius**, among others.

The full list, with licenses, is in [CREDITS.md](CREDITS.md).

## License

Journey Mode code and content are [MIT](LICENSE), © Atos Vinicius ([omagodev](https://github.com/omagodev)). The port is MIT by its authors. Third-party art keeps its own license (see [CREDITS.md](CREDITS.md)).

*Yu-Gi-Oh! and Forbidden Memories belong to Kazuki Takahashi and Konami. This is an unofficial, non-commercial fan project and is not affiliated with Konami.*

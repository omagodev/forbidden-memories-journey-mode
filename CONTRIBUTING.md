# Contributing

Thanks for wanting to help! Journey Mode is a fun, community project and every bit helps: code, art, story, translation, testing or just a good idea.

## Ground rules
- **Never commit game data:** no disc images (`.bin`, `.cue`, `.iso`), no ripped textures or audio. Everyone uses their own legal copy of the USA disc (SLUS-01411).
- Art must be original, AI-assisted and clearly marked, or under a compatible open license **with credits** added to [CREDITS.md](CREDITS.md).
- No real people's likenesses without their consent.
- Keep story text inside the box limits (see [`journey_content/SCHEMA.md`](journey_content/SCHEMA.md)) and run the validators.

## Getting started
1. Read [docs/CONTINUE_DEVELOPMENT.md](docs/CONTINUE_DEVELOPMENT.md) for setup, build and the fast test loop.
2. Pick an issue (look for `good first issue`) or open one to discuss your idea.
3. Fork, branch, and open a pull request with a short description and a screenshot if it changes anything you can see.

## Checks before a PR
```sh
python3 tools/pc/build_mod.py --target i386 mods/ow-poc
python3 journey_content/duelist_kingdom/tools/check_dk.py
python3 mods/ow-poc/tools/validate_story.py
```

## Talking
Use [issues](https://github.com/omagodev/forbidden-memories-journey-mode/issues) for bugs and ideas. Be kind: this is a hobby for everyone involved.

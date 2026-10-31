<p align="right"><a href="CONTRIBUTING.pt-BR.md"><img src="https://img.shields.io/badge/Ler_em_Portugu%C3%AAs-009c3b?style=for-the-badge&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM%2FrhtAAADvklEQVR42u2XXUybZRiGr1L8aC20YAt2UEopLHR2n4oHQDJnPDAx2zTMEzMzMCNqPHDJDvyJB4uZzMREs83FJYsJCyQzUZPFv2Qsi1M3DQaDBG0lQlbKaKE0%2FJT%2BUGg%2FWuYBaZNKyzoGAbX32fe97%2Fvkzv28z%2F08L%2BSQQw7%2Fbsg49%2BTt7Uwwb7sr%2BP8i2FgYoLEwsP0IquUxThsd9FoH6LUOcNroQC2PbY8i2V88yyfVwxgEKeX%2FuCTw6mgd3X7t1ihoFBbpNA9xuc6%2BihyAQZC4XGen0zx0T2quS8GXyiY5ZRxBI48RCiu4eGUPdkc5Q7f0AFhMXsRaD637eihSRZiJ3cfbbjMXpnZsLkGjsMinNUPsVa8UQs%2FvtbR3NDM1p067v6wkyDsvf8OeRx0A%2FBzU0DJiwSUpsyYoZ7%2FpRDYbj1eMcWnnIGZFJEnu6IethCMFGc%2BEIwV0%2F%2FIIYs04Rr2PqoIorz3oAZmMn0LFG3MHGwsD2MQ%2BThpGEfJWxA6FFbR3NGetQntHM6GwAgAh7zYnDaPYxL6sLCljitXyGGerHBwp9a5auzT6JlpLK7pSFTtUWn5w%2FkFpXgkLnjg%2FXhvktxtuyo3F%2FGWfSp55o%2BUKh%2Ff1rorVNa3n2FgtwXh%2BWoL5d2MdCTj7Inz5RQ%2BOoRkASnRKtDoV5dVF1DbpaGipRBtScuGj%2FiRJm6OSw6wmeKTUy1MaX0ZLSlHQKCxytmqEgw%2FMrCn700dfz1gYACazmprdpTS0VOJzLPLVx39CZJKr506tGfdrn45jYzUpRbQuH5Riqcc0GiHl%2B5YzyPffjvD%2B89cJumO8d%2FFZxL316%2FLBlBS7JCXP3dx9xxRbTF684ceYcM%2BztLRMICAllUsQTOCz8%2F3cHJjm0CvWjCTW6jppFez2a7HaGuia1qcNKNZ6mJuNsLS0zC6xLPl%2Fwj2fQi5B2jU2y8h3H6SN1TWtx2pryNgSM6Y4GM%2BnzWmhabAe%2B4IqZe3gE%2F3Iln0AeFz%2BpHIVlYWYzOpkyk1mNbqyYu5Xynmm8VpKDPuCiqbBetqclowVnJVRT0gKzk9VEEfG44UB5DIoUkWo0vu42isSjcbxz0UB8M9F8c9FiUbj7BLLmPbOM%2B7yc%2FzFTh7eOb5yf5dlnJio5gXHQ0xIiq1tdcbKJd469Pk9tbr%2F1rDwTzXfNYyl7TR30yk2bR50SUranBYODIuMS0Ja6zgwLN6xCDZ95E9Y0plJQ7IIzkwa1rSOLXsXJ6aTX%2Bc1G%2FZoymcDsZHEcg%2F3HHLIIYcV%2FA2BwaA%2BPOkCagAAAABJRU5ErkJggg%3D%3D" alt="🇧🇷 Ler em Português (BR)"></a></p>

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

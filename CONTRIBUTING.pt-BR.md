<p align="right"><a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/Read_in_English-0a3d91?style=for-the-badge&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM%2FrhtAAABfklEQVR42u2WMUsCYRzGfxeSplgQGAQJIlFD2GJQRDRItUY4tdTgN7DP0QcImhxqS6KpkKbQApeShiJISIIyhdS7zpZriDsyThHktSPe3%2FTnfeDu4f%2FwPncgkUgkEkej%2BKMJw%2Bd1o2pNAMy527OD50eB7hRcAGuLEc6yBcLBMeqqDtSsMzu9XP3W05k8Uzvb4jcIsLEyRzqT5%2BccmQ5SV3WKpbKtDlDL74s3uLW%2BROr4osWQeQbQST8NjfztBgEKd09tN9gXg%2BYLQxMB%2FD5PW0N2kfclYp%2FXzfzsJFc3DwDWHBgdBqBcrdnqqtYkv7ks3mBsYaYrQ7%2F188tb4TWj%2BKMJw4z2tVKjoelWnXzonwAMeQZt9WKpLDxil7kRgJe3d3xet9V1gFXQAA1NR9WaLXoldy3eoFm67Xqvk56LJ8VGfLh3ZPTyjNVIWOwlMQzDwMEoJ%2BMx5xpUFFyiP%2Fb%2FP%2BJsPOlogwOO%2F6N2esSu%2B92Uszfo9JqRSCQSiaQ3vgD3Gx4lB45C0AAAAABJRU5ErkJggg%3D%3D" alt="🇺🇸 Read in English"></a></p>

# Como contribuir

Obrigado por querer ajudar! O Journey Mode é um projeto divertido e da comunidade, e toda ajuda conta: código, arte, história, tradução, testes ou só uma boa ideia.

## Regras básicas
- **Nunca faça commit de dados do jogo:** nada de imagens de disco (`.bin`, `.cue`, `.iso`), texturas ou áudio extraídos. Cada um usa sua própria cópia legal do disco americano (SLUS-01411).
- A arte deve ser original, feita com ajuda de IA e marcada claramente como tal, ou estar sob uma licença aberta compatível **com os créditos** adicionados ao [CREDITS.pt-BR.md](CREDITS.pt-BR.md).
- Nada de imagem de pessoas reais sem o consentimento delas.
- Mantenha o texto da história dentro dos limites da caixa (veja [`journey_content/SCHEMA.md`](journey_content/SCHEMA.md)) e rode os validadores.

## Primeiros passos
1. Leia o [docs/CONTINUE_DEVELOPMENT.pt-BR.md](docs/CONTINUE_DEVELOPMENT.pt-BR.md) para configurar, compilar e usar o ciclo de teste rápido.
2. Escolha uma issue (procure por `good first issue`) ou abra uma para discutir sua ideia.
3. Faça um fork, crie uma branch e abra um pull request com uma descrição curta e um print se a mudança for visível.

## Verificações antes do PR
```sh
python3 tools/pc/build_mod.py --target i386 mods/ow-poc
python3 journey_content/duelist_kingdom/tools/check_dk.py
python3 mods/ow-poc/tools/validate_story.py
```

## Conversa
Use as [issues](https://github.com/omagodev/forbidden-memories-journey-mode/issues) para bugs e ideias. Seja gentil: isto é um hobby para todo mundo envolvido.

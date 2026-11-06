<p align="right"><a href="CREDITS.md"><img src="https://img.shields.io/badge/Read_in_English-0a3d91?style=for-the-badge&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM%2FrhtAAABfklEQVR42u2WMUsCYRzGfxeSplgQGAQJIlFD2GJQRDRItUY4tdTgN7DP0QcImhxqS6KpkKbQApeShiJISIIyhdS7zpZriDsyThHktSPe3%2FTnfeDu4f%2FwPncgkUgkEkej%2BKMJw%2Bd1o2pNAMy527OD50eB7hRcAGuLEc6yBcLBMeqqDtSsMzu9XP3W05k8Uzvb4jcIsLEyRzqT5%2BccmQ5SV3WKpbKtDlDL74s3uLW%2BROr4osWQeQbQST8NjfztBgEKd09tN9gXg%2BYLQxMB%2FD5PW0N2kfclYp%2FXzfzsJFc3DwDWHBgdBqBcrdnqqtYkv7ks3mBsYaYrQ7%2F188tb4TWj%2BKMJw4z2tVKjoelWnXzonwAMeQZt9WKpLDxil7kRgJe3d3xet9V1gFXQAA1NR9WaLXoldy3eoFm67Xqvk56LJ8VGfLh3ZPTyjNVIWOwlMQzDwMEoJ%2BMx5xpUFFyiP%2Fb%2FP%2BJsPOlogwOO%2F6N2esSu%2B92Uszfo9JqRSCQSiaQ3vgD3Gx4lB45C0AAAAABJRU5ErkJggg%3D%3D" alt="🇺🇸 Read in English"></a></p>

# Créditos

O JOURNEY MODE é um mod de fã, não oficial e sem fins comerciais, para Yu-Gi-Oh! Forbidden Memories. Ele não traz nenhum dado do jogo; você precisa da sua própria cópia legal do disco americano (SLUS-01411).

## Autor
* Atos Vinicius: conceito, história, protagonista, cartas CLT, duelista "Atos Vinicius", direção.

## Construído sobre
* **Yu-Gi-Oh! Forbidden Memories Recompiled** (port nativo para PC, MIT), de Unchiga e colaboradores: https://github.com/Unchiga/Yu-Gi-Oh-Forbidden-Memories-Recompiled . O carregador de mods, o renderizador e o motor sobre os quais este mod roda. Entre os colaboradores estão MaChInEgUn3, Unchiga, Cody, Yamyi, d02d02, DaVinciLord e Tiago S S Gaspar.
* **krystalgamer/memories-decomp** (descompilação do jogo), a base do port: https://github.com/krystalgamer/memories-decomp . Não é redistribuído aqui.

## Assets e código de terceiros
* Fantasy Town Kit 2.0, de **Kenney** (CC0): https://kenney.nl
* Modelos de personagens e objetos de **Quaternius** (CC0): https://quaternius.com
* Assets PSX Nature, de **heyheythere** (CC BY 4.0): crédito "PSX Nature by heyheythere, CC BY 4.0"
* Sprites de personagens do **Liberated Pixel Cup (LPC)**, via o [Universal LPC Spritesheet Character Generator](https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator), de vários artistas (bluecarrot16, JaidynReiman, Benjamin K. Smith, Evert, Eliza Wyatt, TheraHedwig, Johannes Sjolund, Stephen Challener e outros), sob OGA-BY 3.0, CC-BY-SA 3.0 e GPL 3.0. Os autores, licenças e links de cada camada estão em `mods/ow-poc/assets/lpc_runtime_credits.csv` e `mods/ow-poc/assets/lpc_test_credits.txt`. Os sprites `spr_lpc_*.bin` gerados são obras derivadas sob as mesmas licenças.
* **QuickJS**, de Fabrice Bellard e Charlie Gordon (MIT), veja patches/QUICKJS_LICENSE

## Arte
* Os mapas ilustrados, sprites de personagens e folhas de sprites do Journey Mode (vila natal, áreas do Reino dos Duelistas, NPCs) são imagens **geradas por IA**, depois processadas e convertidas para os formatos do jogo pelos scripts em `mods/ow-poc/tools/`. Os personagens são originais ou feitos por fã, inspirados nos personagens do Forbidden Memories; não são arte oficial. As folhas de sprites geradas por IA em `mods/ow-poc/tools/sprite_sheets/` estão incluídas como fonte desses scripts.
* A parte 3 traz mais do mesmo: o mapa da cisterna, os sprites do Rex Raptor e do fantasma do Bakura, os objetos do alçapão e da tocha e os ícones de itens são gerados por IA e convertidos por `mods/ow-poc/tools/build_part3_assets.py`. Como todos os personagens, são inspirados no Forbidden Memories e não são arte oficial.
* O fundo e a plateia da arena subterrânea (`art_dk/arena/`) e a arte da loja (a lojista e o interior da loja de cartas em `art_dk/shop/`) são gerados por IA, convertidos por `mods/ow-poc/tools/build_arena_assets.py`, `make_shop_art.py` e `bake_shop_ui.py`.
* O capítulo 2 traz os mapas do porto, do convés do navio e da Costa das Ilusões e os sprites do soldado do porto, do mensageiro do Shadi, da Mai, do Weevil, do InsetoKaiba, do comissário e do mercador do acampamento: gerados por IA, convertidos para `mods/ow-poc/assets/` por `mods/ow-poc/tools/build_kingdom_assets.py`. Inspirados nos personagens do Forbidden Memories; não são arte oficial.
* O capítulo 3 traz o mapa da Floresta dos Sussurros e o sprite do Mago da Floresta: gerados por IA, convertidos do mesmo jeito. Não são arte oficial.
* O capítulo 4 traz o mapa da Passagem da Montanha e os sprites do Bandit Keith e do Mago da Montanha: gerados por IA, convertidos do mesmo jeito. Não são arte oficial.
* O capítulo 5 traz o mapa do Labirinto da Campina e o sprite da Maga da Campina: gerados por IA, convertidos do mesmo jeito. Não são arte oficial.
* O capítulo 6 traz o mapa do Deserto das Estrelas Perdidas e os sprites do Mago do Deserto / Isis: gerados por IA, convertidos do mesmo jeito. Não são arte oficial.
* O capítulo 7 traz o mapa da Feira das Estrelas e o sprite do Campeão do Ringue: gerados por IA, convertidos do mesmo jeito. Não são arte oficial.
* O capítulo 8 traz o mapa do Portão do Castelo e o sprite do Paul do Cambista: gerados por IA, convertidos do mesmo jeito. Não são arte oficial.
* Os capítulos 9-10 trazem os mapas do Salão do Castelo e da Sala dos Sonhos, e os sprites de Heishin e Pegasus: gerados por IA, convertidos do mesmo jeito. Não são arte oficial.
* O rival "InsetoKaiba" é um personagem de paródia estilizado; não usa o nome nem a imagem de nenhuma pessoa real.

## Conteúdo
Escrito com a ajuda do Grok Bot (tradução para o inglês, capítulos 6 a 8, listas de decks, a personagem Calopsita). Yu-Gi-Oh! e todos os personagens e cartas relacionados pertencem a Kazuki Takahashi / Konami.

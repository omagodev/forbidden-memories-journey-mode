<p align="right"><a href="CONTINUE_DEVELOPMENT.md"><img src="https://img.shields.io/badge/Read_in_English-0a3d91?style=for-the-badge&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM%2FrhtAAABfklEQVR42u2WMUsCYRzGfxeSplgQGAQJIlFD2GJQRDRItUY4tdTgN7DP0QcImhxqS6KpkKbQApeShiJISIIyhdS7zpZriDsyThHktSPe3%2FTnfeDu4f%2FwPncgkUgkEkej%2BKMJw%2Bd1o2pNAMy527OD50eB7hRcAGuLEc6yBcLBMeqqDtSsMzu9XP3W05k8Uzvb4jcIsLEyRzqT5%2BccmQ5SV3WKpbKtDlDL74s3uLW%2BROr4osWQeQbQST8NjfztBgEKd09tN9gXg%2BYLQxMB%2FD5PW0N2kfclYp%2FXzfzsJFc3DwDWHBgdBqBcrdnqqtYkv7ks3mBsYaYrQ7%2F188tb4TWj%2BKMJw4z2tVKjoelWnXzonwAMeQZt9WKpLDxil7kRgJe3d3xet9V1gFXQAA1NR9WaLXoldy3eoFm67Xqvk56LJ8VGfLh3ZPTyjNVIWOwlMQzDwMEoJ%2BMx5xpUFFyiP%2Fb%2FP%2BJsPOlogwOO%2F6N2esSu%2B92Uszfo9JqRSCQSiaQ3vgD3Gx4lB45C0AAAAABJRU5ErkJggg%3D%3D" alt="🇺🇸 Read in English"></a></p>

# Continuando o desenvolvimento do Journey Mode (fora do ambiente original)

Este arquivo é a passagem de bastão: o que existe, o que instalar, como compilar, rodar e testar, e o que fazer em seguida.
Escrito em 2026-10-25. Os comandos abaixo foram copiados de scripts deste repositório; **nada foi rodado de novo quando este arquivo foi escrito**
(a passagem foi feita sem uma rodada de testes), então leve a sério as notas "Não verificado".

## 1. O que é este projeto

O Journey Mode é um modo de história / mundo aberto para Yu-Gi-Oh! Forbidden Memories. É um mod em C (`mods/ow-poc`) que roda no port nativo para PC
"FM Recompiled" (código do port sob licença MIT, SDL3 + OpenGL + um rasterizador em CPU que emula a GPU do PS1). O mod adiciona um mundo 2D ilustrado
(cenários ilustrados de 1280x720 + sprites de personagens de 48x62), diálogos, missões, duelos com um deck por duelista, um arquivo de save e um criador de personagem.

Você precisa da sua **própria imagem legal do disco americano (SLUS-01411)**. Não há dados do jogo neste repositório e nenhum deve ser commitado, nunca.

### Estado atual (partes entregues)
| Parte | Conteúdo | Status |
|---|---|---|
| 1-2 | Vila natal ilustrada, sprites de NPCs, missões 1-3 da história do Reino dos Duelistas, música, estradas | entregue, testado pelo autor no Windows |
| 2b/2c | Correções de menu, opção de debug, UI de diálogo (nome de quem fala em amarelo + dois-pontos na caixa de texto, banners, painel Sim/Não) | entregue |
| 3 | Cisterna, duelo com o fantasma do Bakura, Rex Raptor / bandana do Jono, tarefas + duelo da Teana (missões 4-6), observador Mago.dev no glifo | compilado, 26 cenários de smoke passaram no Linux; **o exe do Windows nunca foi rodado pelo autor da parte 3 em diante** |
| 3b | Pequena dica de ação (pílula do botão X) no lugar da barra grande; "Dev mode" ON/OFF no menu START | compilado |
| 3c | Caixa do menu START tão larga quanto a linha mais longa (o texto de idioma não vaza mais) | compilado |
| 4a | Criador de personagem no NOVO JOGO com um herói montado ao vivo a partir de camadas de sprite (pele, roupa, cabelo, acessório + cores) | compilado, 37/37 cenários de smoke no Linux |
| 5a (economia fase 1) | moedas, XP/nível, loja | **NÃO implementado.** Só design + dados (seção 8). O assistente que estava fazendo parou por falta de uso; nenhum código foi escrito. |

A história termina em "Parte 3 concluída" (fim do arco da vila natal). O porto, o navio, os capítulos 2-10 do Reino e a arte deles não foram feitos.

## 2. Estrutura do repositório
- `src/`, `tools/pc/`, `config/`, `Makefile`, `CMakeLists.txt`, `play.sh`, `play.bat`, `build-pc.sh`: o port FM Recompiled (código upstream; veja o CREDITS.pt-BR.md).
- `mods/ow-poc/`: **o mod Journey Mode.**
  - `ow_poc.c` ponto de entrada; `jm_painted.c` motor do mundo ilustrado (mapas, sprites, colisão, NPCs, áreas); `jm_ui.c` menus/diálogo/banners; `jm_lang.c`; `jm_save.c`; `jm_debug.c`; `jm_chargen.c` criador de personagem; `jm.h`.
  - `assets/` dados convertidos (mapas `painted*.raw`, `painted_col.bin`, sprites `spr_*.bin`, objetos, `chargen/`, `lang/`, `journey.json` = história gerada).
  - `ow-poc.o` o objeto do mod de 32 bits pré-compilado (recompile depois de qualquer mudança em `.c`).
  - `mod.json`, `debug.json.OFF` (renomeie para `debug.json` para ativar a ajuda de debug).
  - `tools/`: conversor, validador, scripts de conversão de arte, `fast.sh`, `smoke/` (harness de cenários), `TESTING.md`, `CHARGEN_FORMAT.md`.
- `journey_content/`: dados da história. `duelist_kingdom/` é a história principal (EN em `en/`, PT em `pt/`, só ASCII, geradores em `src/`, `tools/check_dk.py`). Os arquivos da raiz são a história antiga, guardada como backup. `economy/` é o design e os dados de lojas/dinheiro/níveis/gangue/arenas (ainda não ligado ao jogo).
- `art_dk/`: fontes de arte e ferramentas de conversão (fundos, máscaras, oclusores, sprites, retratos, geradores de camadas `chargen/`, `part3/`). Intermediários grandes (gerações em `raw/`, `village_roads/out`, `variants`, `previews`) **não** estão no repositório. Fotos de referência privadas nunca estão no repositório.
- `docs/TESTING.md` ([PT](TESTING.pt-BR.md)): as notas de teste da parte 3; `notes/`: documentação do port (`notes/journey-mode.md` tem o design do mod).

## 3. Configuração numa máquina nova
Pré-requisitos (de `play.sh` / `play.bat`): `python3`, e no Linux `gcc ld objcopy nm readelf objdump`
(`sudo apt install gcc python3` no Debian/Ubuntu). No Windows, o `play.bat` baixa um Python, compilador, CMake e Ninja próprios em `tmp\` na primeira execução.
Para os scripts de arte/conversão: `pip install numpy pillow` (e `scipy` para algumas ferramentas de arte; os scripts de `village_roads` usaram um venv).
A primeira compilação baixa as libs do Linux, o SDL3 e o llvm-mingw em `tmp/pc` (alguns minutos, precisa de internet).

1. `git clone https://github.com/omagodev/forbidden-memories-journey-mode && cd forbidden-memories-journey-mode`
2. Coloque o `.bin` do seu disco americano em `game/` (qualquer nome terminado em `.bin`). Nunca faça commit dele (`game/` é só para a sua cópia).
3. Linux: `./play.sh` (compila e roda o jogo para Linux, pulando a compilação cruzada para Windows). Compilação completa incluindo o exe do Windows: `./build-pc.sh` (precisa do llvm-mingw, baixado por `tools/pc/build_win32_deps.py`).
   Windows: `play.bat`. macOS: `./build-pc.sh` (compilação ARM64 a partir do código). Os executáveis ficam em `tmp/pc/game32/memories-pc` (Linux) e `tmp/pc/win32/memories-pc.exe` (Windows).
4. Objeto do mod: `python3 tools/pc/build_mod.py --target i386 mods/ow-poc` gera `mods/ow-poc/ow-poc.o` (objeto i386; funciona tanto no jogo para Linux quanto no para Windows).
5. Instale o mod na pasta do jogo: copie `ow-poc.o`, `mod.json` e `assets/` para `tmp/pc/game32/mods/ow-poc/` - o `mods/ow-poc/tools/fast.sh` faz validar + compilar + instalar de uma vez.

Não verificado: que um clone novo compila de ponta a ponta numa máquina limpa (compilou no ambiente do autor, onde `tmp/pc` já estava populado).

## 4. Ciclo rápido de editar e testar (fluxo do autor)
Leia `mods/ow-poc/tools/TESTING.md` (detalhes completos). O essencial, rodando da raiz do repositório:
- `python3 mods/ow-poc/tools/validate_story.py` : valida o JSON da história, sem compilar.
- `mods/ow-poc/tools/fast.sh` : valida + compila + instala (cerca de 1,5 s). `--convert` roda antes o `dk_to_journey.py` (JSON da história em `journey_content/` -> `journey.json` usado em tempo de execução).
- `mods/ow-poc/tools/fast.sh all` : todos os cenários de smoke (vários minutos). `python3 mods/ow-poc/tools/smoke/jm_smoke.py list|run <nome>` para um só.
- O harness usa Xvfb no display `:92` (Linux). No Windows rode no WSL, ou pule e jogue com o `debug.json`.
- Ajuda de debug: renomeie `mods/ow-poc/debug.json.OFF` para `debug.json` (nunca distribua ele). Segure R1 (tecla W) e depois L1 (tecla Q) + Cima/Baixo = preset da história, Esquerda = hora do dia, Direita = próximo ponto, Quadrado = pular diálogo, Triângulo = vencer duelos. Os campos do `debug.json` estão documentados no TESTING.md (`preset`, `flags`, `stage`, `teleport`, `time`, `skip_dialogue`, `win_duels`, `look`).
- Limitações: o harness não consegue jogar um duelo real até o fim de forma confiável, então os cenários usam `win_duels`.

## 5. Teclas do jogo (release)
Setas andam, S (Círculo) corre, X (Xis) conversa/examina, A (Triângulo) diário, Shift direito (Select) minimapa, Enter (Start) menu principal (itens, editor de deck, status, salvar, idioma, Dev mode, voltar ao título), E (L2) água, R (R2) árvores. Só para desenvolvedores: com um `debug.json` ativo, aparece uma linha Dev mode no menu START que liga/desliga a linha de informação do mod no topo (salva em `devmode.cfg`). Sem `debug.json` (toda versão para jogadores) a linha some e a barra não pode ser ligada.

## 6. Criando conteúdo e arte
- **História:** edite `journey_content/duelist_kingdom/src/dk_*.py` / os JSON em EN e PT, rode `fast.sh --convert` (o conversor `mods/ow-poc/tools/dk_to_journey.py` -> `journey.json`; adicione um preset de debug para cada novo estágio de missão em `DEBUG_PRESETS`). Confira com `journey_content/duelist_kingdom/tools/check_dk.py` e `validate_story.py`. Flags: 30 de 32 usadas, então estado novo deve virar contador no save, não flag. O texto em PT é só ASCII (fonte original do jogo).
- **Restrições do pipeline dos mapas ilustrados:** fundos de 1280x720 divididos em quads de 128x128; recortes de oclusores ordenados por profundidade pelo Y da linha de base; grade de colisão 160x90 (células de 8 texels); o valor de texel 0 é a única transparência (sem alfa); RGB555; vizinho mais próximo. Os bancos de textura 1-15 são compartilhados com os duelos (que usam 1-12), então os bancos são recarregados a cada entrada: palmeiras 1,2,3,7,12; água 4-6; imagem 8-11; atlas 14; sprites banco 13 (páginas: kenney 0-1, jogador 2, ai 3, simon 4, teana 5, jono 6, guarda 7) e banco 15 (páginas 6-7 Rex/Bakura; o resto livre).
- **Sprites:** 48x62 texels, 4 direções, parado + caminhada de 4 passos, contorno de 1px. Scripts de conversão: `art_dk/tools/bake_dk.py`, `bake_npcs.py`, `bake_sprites.py`, `art_dk/part3/tools/bake_p3.py`, e `mods/ow-poc/tools/bake_ai.py`, `build_part3_assets.py` (o caminho padrão de arte dentro dele é o caminho do ambiente antigo: passe sua pasta `art_dk` como argumento 1).
- **Camadas do criador de personagem:** geradas proceduralmente por `art_dk/chargen/tools/` (`python3 tools/build.py && python3 tools/make_previews.py && python3 tools/verify.py` dentro de `art_dk/chargen`), depois `python3 mods/ow-poc/tools/import_chargen.py` copia o manifesto + as camadas empacotadas para `mods/ow-poc/assets/chargen/`. Formato: `mods/ow-poc/tools/CHARGEN_FORMAT.md`. Pares evitados: spiky+cap, hood_down+scarf, long+scarf.
- Alguns scripts ainda têm padrões absolutos antigos como `/workspace/study/fmrecomp/...`; troque pelo argumento do script ou edite a constante.
- Não verificado: que todo script de conversão roda sem mudanças fora do ambiente original.

## 7. Formato do save
O `journey.sav` está na versão 4 do save (visual do herói `Journey.cg[8]` vindo do criador, estágio, flags, lugar, hora). Saves antigos carregam com o herói antigo. O design da economia prevê um bloco de 52 bytes acrescentado no fim (moedas, XP, timers de emboscada, progresso nas arenas); o carregador preenche com zeros um arquivo mais curto. O Dev mode fica num `devmode.cfg` separado na pasta de dados do mod.

## 8. Próximo: economia (fases) - pedido do usuário, design pronto, código não iniciado
O design e os dados legíveis por máquina estão em `journey_content/economy/` (`DESIGN.md`, `README.md` com a lista de trabalho no motor e tamanhos, `economy.json`, `shops.json`, `card_pools.json`, `gang.json`, `arenas.json`, `levels.json`, `decks_economy.json`, `card_rarity.json`, textos EN/PT, geradores em `src/`, `validate_economy.py`). Gere de novo com `python3 src/gen_economy.py && python3 validate_economy.py` dentro dessa pasta.
Requisitos do usuário: uma loja em cada cidade (dinheiro), drop de cartas só do conjunto local, uma curva de dificuldade, uma gangue de duelistas que embosca o jogador com uma certa frequência, da qual não dá para fugir e que leva dinheiro quando vence, arenas clandestinas em cada local para farmar cartas locais e subir de nível.
- **Fase 1 (fazer primeiro):** campos no save para moedas/XP, avisos de dinheiro no estilo de banner existente, recompensas de duelo (moedas/XP) e drops do conjunto local, nível a partir do XP, a loja da vila (NPC lojista via `place_npc`, tela de compra/venda do tamanho da caixa, estoque liberado no estágio 3). Use o mecanismo real de coleção de cartas já usado nas recompensas (`give_item`/código de recompensa de carta no mod).
- **Fase 2:** a gangue de emboscada "Dune Jackals" (75-150 s de caminhada entre emboscadas, só em estradas/campos, sem emboscada em missões/lojas/diálogos/primeiros minutos, banner "AMBUSH!", sem andar/correr/menu e sem poder sair do duelo, a derrota rouba uma porcentagem com mínimo/máximo e nunca abaixo de 0, sem game over).
- **Fase 3:** as 8 arenas escondidas (escadas de 4 degraus, taxa de entrada, bônus da primeira vitória, revanches dão cartas locais, XP).
- Precisa de ~38 novos slots de duelista (os decks são ligados aos slots de duelista; alternativa em `economy/README.md`: 12 lutadores compartilhados + 8 campeões).
- Confira com o FM Editor as combinações de equipamento/carta de campo nos conjuntos antes de lançar.

## 9. Pacote para Windows (como os zips do autor foram feitos)
Um pacote é uma pasta com: `memories-pc.exe` + `SDL3.dll` (de `tmp/pc/win32/` depois do `build-pc.sh`), `languages/`, `LICENSE`, `game/README.txt` (uma pasta `game` vazia para o disco do usuário), `mods/` (os mods padrão mais `mods/ow-poc` contendo só `ow-poc.o`, `mod.json` e `assets/`; desde a v0.5.2-alpha o pacote não traz mais o `debug.json.OFF`), `JOGAR_JourneyMode.bat` (define `MEMORIES_HD_TEXT=1` e abre o `memories-pc.exe`) e arquivos README. O exe do Windows não mudou da parte 2c em diante: só `ow-poc.o`, `mod.json` e `assets/` mudam entre pacotes. Nunca distribua uma imagem de disco nem um `debug.json` ativo. Não há script no repositório que gere esse zip; no ambiente do autor isso foi feito à mão.

## 10. Limitações conhecidas / TODO
- O exe do Windows não foi verificado nas partes 3 a 4a; o harness do Linux é o único teste automatizado.
- Os duelos com Rex, Bakura e Teana só foram testados com a vitória automática do debug; a música (faixa 10 de dia, 25 de noite, 26 na cisterna) e os novos efeitos sonoros foram escolhidos por medição, não de ouvido.
- Parte 3: a cisterna tem brilho de tochas mas não tem água animada, a colisão feita à mão pode não bater com a imagem, o rosto do Bakura é pequeno (com dithering); salvar na cisterna volta para o alçapão ao Continuar; o glifo é desenhado por código.
- Chargen: um formato de corpo e um rosto; só o herói é feito em camadas; o diário mostra o retrato.
- O Mago.dev ainda não tem retrato/diálogo ligados ao jogo. Os capítulos 2-10 da história e a arte deles não foram feitos; o final "ficar" e o floco Nitemare não foram testados.
- Acentos em PT precisam de uma troca de fonte (a fonte original é só ASCII). A localização do título do botão JOURNEY MODE no menu está em aberto.
- Uma release no GitHub não foi publicada (questão em aberto: os arquivos `languages/*.txt` do pacote foram lidos dos discos PAL pelo port).

## 11. Convenções, créditos, licenças
- Commits: em inglês, `Area: descrição curta`, depois um parágrafo `Tested:` dizendo só o que foi verificado.
- Créditos: veja o `CREDITS.pt-BR.md` (port FM Recompiled MIT, o memories-decomp não declara licença, Kenney, Quaternius, heyheythere, QuickJS). Mapas pintados, sprites e retratos são arte original feita com ajuda de IA; os personagens são inspirados no Forbidden Memories e não são arte oficial; "InsetoKaiba" é uma paródia estilizada sem nome ou imagem de pessoa real; Mago.dev é o personagem do próprio autor. Nenhuma foto de referência privada pode ser commitada.

## 12. Checklist dos primeiros 30 minutos
1. Clone, coloque o `.bin` do seu disco em `game/`, rode `./play.sh` (Linux) ou `play.bat` (Windows) uma vez para preencher o `tmp/pc`.
2. `python3 mods/ow-poc/tools/validate_story.py`, depois `mods/ow-poc/tools/fast.sh` para confirmar que compilar + instalar funciona.
3. Renomeie `mods/ow-poc/debug.json.OFF` para `debug.json`, abra o jogo, JOURNEY MODE > Continuar, segure R1+L1 e aperte Cima para pular entre os estágios da história.
4. Leia `journey_content/economy/README.md` e comece a fase 1 em `jm_save.c` (bloco do save), `jm_ui.c` (banners/menu), `jm_painted.c` (NPC da loja, efeitos).

### Testes rapidos

Use `python3 mods/ow-poc/tools/smoke/fast.py` para a tabela de presets e `mods/ow-poc/tools/fast.sh --quick` para o smoke do caminho critico (portoes, aposta de estrelas, saltos de capitulo). O `fast.sh all` completo fica para a release. Detalhes: [`mods/ow-poc/tools/TESTING.md`](../mods/ow-poc/tools/TESTING.md).

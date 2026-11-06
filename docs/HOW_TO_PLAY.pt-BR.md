<p align="right"><a href="HOW_TO_PLAY.md"><img src="https://img.shields.io/badge/Read_in_English-0a3d91?style=for-the-badge&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM%2FrhtAAABfklEQVR42u2WMUsCYRzGfxeSplgQGAQJIlFD2GJQRDRItUY4tdTgN7DP0QcImhxqS6KpkKbQApeShiJISIIyhdS7zpZriDsyThHktSPe3%2FTnfeDu4f%2FwPncgkUgkEkej%2BKMJw%2Bd1o2pNAMy527OD50eB7hRcAGuLEc6yBcLBMeqqDtSsMzu9XP3W05k8Uzvb4jcIsLEyRzqT5%2BccmQ5SV3WKpbKtDlDL74s3uLW%2BROr4osWQeQbQST8NjfztBgEKd09tN9gXg%2BYLQxMB%2FD5PW0N2kfclYp%2FXzfzsJFc3DwDWHBgdBqBcrdnqqtYkv7ks3mBsYaYrQ7%2F188tb4TWj%2BKMJw4z2tVKjoelWnXzonwAMeQZt9WKpLDxil7kRgJe3d3xet9V1gFXQAA1NR9WaLXoldy3eoFm67Xqvk56LJ8VGfLh3ZPTyjNVIWOwlMQzDwMEoJ%2BMx5xpUFFyiP%2Fb%2FP%2BJsPOlogwOO%2F6N2esSu%2B92Uszfo9JqRSCQSiaQ3vgD3Gx4lB45C0AAAAABJRU5ErkJggg%3D%3D" alt="🇺🇸 Read in English"></a></p>

# Como jogar

Não precisa compilar: baixe a versão pronta para Windows.

## O que você precisa
- Windows 10 ou 11.
- **Sua própria** imagem do disco *Yu-Gi-Oh! Forbidden Memories* (EUA, **SLUS-01411**): o arquivo `.bin` do par `.bin/.cue`. Escolha o `.bin`, não o `.cue`. Nenhum dado do jogo vem incluso.
- Não precisa instalar nada, nem emulador, nem compilar.

## Passo a passo
1. Baixe o [`JourneyMode_v0.6.0-alpha_Windows.zip`](https://github.com/omagodev/forbidden-memories-journey-mode/releases/download/v0.6.0-alpha/JourneyMode_v0.6.0-alpha_Windows.zip) (ou o mais novo em [Releases](https://github.com/omagodev/forbidden-memories-journey-mode/releases/latest)).
2. Extraia o zip **inteiro** numa pasta (não rode de dentro do zip).
3. Copie seu `.bin` para a pasta `game`, ou escolha em **Choose ROM...** na primeira vez.
4. Clique duas vezes em **`JOGAR_JourneyMode.bat`** (recomendado, liga o texto HD) ou no `memories-pc.exe`.
5. Se o SmartScreen avisar: **Mais informações → Executar assim mesmo** (o programa não é assinado; o código está aqui).
6. Na tela de título escolha **NOVO JOGO**, crie seu personagem e comece. **CONTINUAR** carrega seu save.

## Teclado
| Tecla | Ação |
|---|---|
| Setas | Andar / navegar |
| X ou Enter | Confirmar / conversar |
| S | Voltar / cancelar (Circulo) |
| A | Diario / mapa (Triangulo) |
| Z | Quadrado (abas da loja / extras) |
| Q / W | L1 / R1 |
| E / R | L2 / R2 |
| Enter | Start (menu de pausa) |
| Shift direito | Select (minimapa) |
| F10 | Barra de menu (vídeo, controles, idioma) |
| Esc | Sair |

## Controle (Xbox / PlayStation / estilo Switch)
Plugue um gamepad USB ou Bluetooth — o SDL reconhece sozinho. Stick e D-pad andam.

| Botao | Acao |
|---|---|
| Stick esquerdo / D-pad | Andar / navegar |
| A / South (✕) | Confirmar / falar |
| B / East (○) | Voltar / correr (segure no mapa) |
| Y / North (△) | Diario (mapa ilustrado) / mapa do mundo |
| X / West (□) | Acoes de Quadrado (loja / UI) |
| Start | Menu de pausa |
| Select / View / − | Minimapa |
| LB / RB | L1 / R1 |
| LT / RT | L2 / R2 |

## Remapear teclas e botoes
1. No Journey Mode abra **Start → Controles** (abre a janela Controles do PC), **ou** pressione **F10 → Game → Controls…**.
2. Clique na linha e aperte a tecla ou o botao desejado. Conflitos sao movidos automaticamente.
3. **Apply** ou **OK** — o mapeamento fica em `controls.txt` na pasta do usuario (`Documentos\My Games\YFM Re-Decomp`).

Teclado e controle compartilham as mesmas acoes: mapa, loja, apostas e duelos seguem o seu remap.


O atalho **ver missoes** no canto (A / Triangulo / Y) abre o diario de missoes.
## Fichas de Estrela (Reino dos Duelistas)
- Dois tipos de estrela: as **Fichas Estrela** do Reino (ficha vermelho-dourada, `x/10` no HUD) são moeda da história, quase dinheiro: só vêm de recompensas da história e de apostas. A estrela clara no HUD são as **estrelas de duelo** do próprio jogo, ganhas por desempenho em qualquer duelo; elas nunca viram Fichas Estrela, nunca são apostadas e os portões não as contam.
- Antes de cada duelo de fichas você **escolhe a aposta**: esquerda/direita de 1 até o menor entre as suas fichas e as do rival, X para duelar, S para desistir.
- Vencendo, você toma a aposta dele. Perdendo, ele **fica** com ela; desafie de novo para recuperar.
- **Se suas Fichas Estrela acabarem, é FIM DE JOGO**: você volta ao título e CONTINUAR carrega seu último save (o jogo nunca salva com zero fichas). Nunca aposte a última à toa.
- Os portões contam só as Fichas Estrela na sua mão; dez abrem o castelo.

Saves ficam em `Documentos\My Games\YFM Re-Decomp`. Achou um bug? [Abra uma issue](https://github.com/omagodev/forbidden-memories-journey-mode/issues) com o `game.log` da pasta do jogo.

## Linux / compilar do código-fonte
Veja o [CONTINUE_DEVELOPMENT.pt-BR.md](CONTINUE_DEVELOPMENT.pt-BR.md).

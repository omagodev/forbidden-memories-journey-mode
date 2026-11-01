<p align="right"><a href="TESTING.md"><img src="https://img.shields.io/badge/Read_in_English-0a3d91?style=for-the-badge&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM%2FrhtAAABfklEQVR42u2WMUsCYRzGfxeSplgQGAQJIlFD2GJQRDRItUY4tdTgN7DP0QcImhxqS6KpkKbQApeShiJISIIyhdS7zpZriDsyThHktSPe3%2FTnfeDu4f%2FwPncgkUgkEkej%2BKMJw%2Bd1o2pNAMy527OD50eB7hRcAGuLEc6yBcLBMeqqDtSsMzu9XP3W05k8Uzvb4jcIsLEyRzqT5%2BccmQ5SV3WKpbKtDlDL74s3uLW%2BROr4osWQeQbQST8NjfztBgEKd09tN9gXg%2BYLQxMB%2FD5PW0N2kfclYp%2FXzfzsJFc3DwDWHBgdBqBcrdnqqtYkv7ks3mBsYaYrQ7%2F188tb4TWj%2BKMJw4z2tVKjoelWnXzonwAMeQZt9WKpLDxil7kRgJe3d3xet9V1gFXQAA1NR9WaLXoldy3eoFm67Xqvk56LJ8VGfLh3ZPTyjNVIWOwlMQzDwMEoJ%2BMx5xpUFFyiP%2Fb%2FP%2BJsPOlogwOO%2F6N2esSu%2B92Uszfo9JqRSCQSiaQ3vgD3Gx4lB45C0AAAAABJRU5ErkJggg%3D%3D" alt="🇺🇸 Read in English"></a></p>

# Testando o Journey Mode: Reino dos Duelistas, parte 3

Como rodar e conferir o arco da vila natal até a parte 3. O ciclo de teste rápido (validador, `fast.sh`, sintaxe dos cenários, ajuda de debug) está descrito em [`mods/ow-poc/tools/TESTING.md`](../mods/ow-poc/tools/TESTING.md); esta página cobre o que a parte 3 acrescenta.

Você precisa da sua própria cópia legal do disco americano (SLUS-01411). Não há dados do jogo neste repositório nem na release. Aponte `MEMORIES_DISC` para o `.bin` da sua imagem de disco nas execuções por script, ou escolha com "Choose ROM..." na versão para Windows.

## Parte 3 (versão de teste)

Depois do Cartão de Carimbos (fim da parte 2), a história abre três missões que podem ser feitas em qualquer ordem. Cada uma dá um carimbo (Perdido / Vencido / Doado). Quando os três brilham, o guarda deixa você atravessar a ponte para o porto; o porto em si é a parte 4, então por enquanto aparece um banner "Missão concluída" e a história termina em "Parte 3 concluída".

* **Missão 4, O Perdido.** Ganhe a lanterna do Kemet (parte 2), vá até a pequena pirâmide na borda da vila e aperte X no alçapão. Ele abre para a cisterna, uma nova área ilustrada (abóbada de arenito, água, tochas, mapa 320x180). Um glifo na parede chama o observador Mago.dev, que some numa falha; aí aparece o fantasma do Bakura. Converse com ele e duele (deck "Yami Bakura"). Vitória: o Escaravelho do Fundador e o carimbo Perdido. A escada por onde você entrou leva de volta para fora.
* **Missão 5, O Vencido.** O Jono perdeu a bandana para o Rex Raptor, que fica na estrada leste enquanto esta missão está aberta. Duele com o Rex (deck "Rex Raptor"), ganhe a Bandana do Jono e leve de volta para ganhar o carimbo Vencido.
* **Missão 6, O Doado.** A Teana quer mel (do padeiro Hakim), água do rio (encha a jarra dela na margem do rio) e tâmaras (sacuda a tamareira). Leve tudo para ela, vença o duelo dela (deck "Teana") e ganhe o Amuleto da Sorte e o carimbo Doado.

A seta amarela e a barra de objetivo seguem a próxima tarefa; o diário (A) lista as três missões e esconde cada uma quando termina. Os banners (objetivo, item, carimbo, missão concluída) são separados das falas.

### Teclas

Setas andam, S corre, X conversa ou examina, A abre o diário, Shift direito o minimapa, ENTER o menu.

### Ajuda de debug (desligada por padrão)

Renomeie `mods/ow-poc/debug.json.OFF` para `debug.json` (repositório) ou crie `mods/ow-poc/debug.json` (`{}` basta). Sem esse arquivo nenhuma tecla de debug faz nada. Você precisa de um save do Journey (NOVO JOGO, ande alguns passos, ENTER > Salvar, depois CONTINUAR).

Segure R1 (W), depois L1 (Q) e:

| Teclas | Efeito |
|---|---|
| Cima / Baixo | próximo / anterior preset da história (o mundo é reconstruído) |
| Esquerda | hora do dia: a história decide > noite > dia |
| Direita | teleporta para o próximo lugar nomeado |
| Quadrado (Z) | pular diálogo liga/desliga |
| Triângulo (A) | vencer duelos liga/desliga (o duelo conta como vencido, com recompensas) |

Presets (`DEBUG_PRESETS` em `mods/ow-poc/tools/dk_to_journey.py`, gravados em `journey.json`): 1 porta de casa, 2 boatos ouvidos, 3 Simon vencido (banco em seguida), 4 noite / encapuzado esperando, 5 Cartão de Carimbos (Hakim em seguida), 6 dica do Hakim (Kemet em seguida), 7 lanterna ganha (alçapão em seguida), 8 na cisterna (Bakura), 9 carimbo Perdido (glifo, escada), 10 pedido do Jono (Rex em seguida), 11 tarefas da Teana, 12 tarefas feitas, 13 dois carimbos (Teana por último). Os presets 8 e 9 colocam você na cisterna. O arquivo de debug também aceita `preset`, `flags`, `stage`, `teleport`, `time`, `skip_dialogue` e `win_duels`. O progresso feito durante o debug é salvo junto com o save normal, então faça uma cópia do `journey.sav` antes.

### Verificações por script

```
python3 mods/ow-poc/tools/validate_story.py
mods/ow-poc/tools/fast.sh --convert      # roda de novo o conversor da história, valida, compila, instala
mods/ow-poc/tools/fast.sh all            # todos os cenários, tabela PASS/FAIL
```

Cenários da parte 3: `dk_part3_hatch_locked`, `dk_part3_cistern`, `dk_part3_glyph`, `dk_part3_exit`, `dk_part3_rex`, `dk_part3_honey`, `dk_part3_water`, `dk_part3_dates`, `dk_part3_teana_end`, `dk_part3_journal_en`, `dk_part3_journal_pt`, `ui_banners_p3_en`, `ui_banners_p3_pt`. As execuções por script usam Xvfb no display `:92`.

### Limitações conhecidas (parte 3)

* Os duelos com Rex, Bakura e Teana são duelos de verdade no jogo, mas os cenários automáticos só os conferem com a opção de debug "vencer duelos"; jogá-los de verdade não foi testado.
* A cisterna é uma única ilustração iluminada só pelo brilho das tochas (sem água animada). O mapa de colisão foi feito à mão, então algum ponto pode diferir da imagem por alguns passos.
* O sprite do Bakura é desenhado com dithering, então o rosto fica pequeno e suave.
* Salvar dentro da cisterna faz você voltar ao alçapão na vila quando continua.
* O glifo do Mago.dev é desenhado por código, não por uma arte ilustrada.
* A música da cisterna e os novos efeitos sonoros foram escolhidos por medição, não de ouvido (`journey.json` `"painted": {"music": ...}`).
* O executável do Windows não foi rodado pelo autor com a parte 3; a lógica foi conferida no Linux (Xvfb) com o mesmo objeto do mod.

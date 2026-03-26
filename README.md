# 🧟 UNIMA Survivors — Apocalipse Zumbi

**Sobreviva às hordas de zumbis no campus da UNIMA Afya Maceió!**

Um jogo 2D top-down de sobrevivência inspirado no estilo Vampire Survivors, com pixel art gerada programaticamente, sistema de inventário, loot, progressão e combate intenso.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-green)

---

## 🎮 Como Jogar

### Requisitos
- Python 3.8 ou superior
- Pygame 2.5+

### Instalação e Execução

```bash
# 1. Clone ou extraia o projeto
cd unima_survivors

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute o jogo
python main.py
```

### Controles

| Tecla | Ação |
|-------|------|
| WASD / Setas | Movimentar |
| Mouse (modo manual) | Mirar e atirar |
| Auto (modo padrão) | Atira no zumbi mais próximo |
| TAB | Alternar modo de tiro |
| I | Abrir/fechar inventário |
| E | Usar item selecionado |
| Q | Descartar item |
| ESC | Pausar / Voltar |
| ENTER | Confirmar seleções |
| M (pausado) | Voltar ao menu |

---

## 🏗️ Estrutura do Projeto

```
unima_survivors/
├── main.py              # Ponto de entrada
├── requirements.txt     # Dependências
├── README.md            # Este arquivo
├── game/
│   ├── __init__.py
│   ├── config.py        # Configurações e constantes
│   ├── engine.py        # Loop principal e gerenciamento de estados
│   ├── player.py        # Jogador, movimentação, stats, inventário
│   ├── enemies.py       # Zumbis, IA, sistema de spawn
│   ├── campus_map.py    # Gerador do mapa do campus
│   ├── loot.py          # Sistema de drops e coleta
│   ├── effects.py       # Partículas, números de dano, efeitos
│   └── renderer.py      # Renderização do mundo com câmera
├── ui/
│   ├── __init__.py
│   └── hud.py           # HUD, menus, inventário, game over
└── assets/
    ├── __init__.py
    └── sprites.py       # Gerador de sprites pixel art
```

---

## 🎯 Features

### Gameplay
- ✅ Movimentação 8 direções com colisão
- ✅ Tiro automático (estilo Vampire Survivors)
- ✅ Tiro manual (mirar com mouse)
- ✅ Hordas crescentes de zumbis
- ✅ 3 tipos de zumbi (comum, veloz, tank)
- ✅ Sistema de dano e morte
- ✅ Loop de progressão com XP e level up
- ✅ Escolha de upgrades ao subir de nível

### Inventário & Loot
- ✅ 8 tipos de loot (munição, cura, XP, velocidade, dano, armadura, ímã, arma)
- ✅ Inventário com 16 slots
- ✅ Usar, equipar e descartar itens
- ✅ Pilha de itens empilháveis
- ✅ Coleta automática de XP e consumíveis

### Interface
- ✅ Menu principal com opções
- ✅ HUD com vida, munição, nível, timer, kills
- ✅ Tela de inventário
- ✅ Tela de seleção de upgrade
- ✅ Tela de game over com estatísticas
- ✅ Tela de pause
- ✅ Tela de instruções
- ✅ Configurações

### Visual & Audio
- ✅ Pixel art gerada programaticamente
- ✅ Sprites animados (jogador e zumbis)
- ✅ Partículas de sangue, morte e coleta
- ✅ Números de dano flutuantes
- ✅ Screen shake em impactos
- ✅ Efeitos sonoros procedurais
- ✅ Câmera suave seguindo o jogador

### Mapa
- ✅ Campus universitário com blocos, caminhos, estacionamento
- ✅ 12 prédios nomeados (Saúde, Engenharias, Biblioteca, etc.)
- ✅ Pátios, corredores, portões
- ✅ Colisão com paredes
- ✅ 7 tipos de tile diferentes

---

## 🧟 Tipos de Zumbi

| Tipo | Vida | Velocidade | Dano | XP |
|------|------|-----------|------|-----|
| Comum | 20 | Lenta | 8 | 10 |
| Veloz | 12 | Rápida | 5 | 15 |
| Tank | 60 | Muito lenta | 15 | 30 |

---

## ⬆️ Upgrades Disponíveis

- **Dano+** — +15% dano por tiro
- **Cadência+** — +12% velocidade de tiro
- **Vida+** — +20 HP máximo
- **Velocidade+** — +8% velocidade de movimento
- **Coleta+** — +25% alcance de coleta
- **Munição+** — +20 munição imediata

---

## 🔧 Possíveis Melhorias Futuras

- Mapa baseado em imagem real do campus UNIMA Afya
- Mais tipos de arma (shotgun, metralhadora, lança-chamas)
- Boss zombies especiais
- Sistema de save/load
- Ranking de pontuações
- Trilha sonora procedural
- Multiplayer local
- Mais variações de inimigos
- NPCs sobreviventes no campus
- Sistema de missões/objetivos

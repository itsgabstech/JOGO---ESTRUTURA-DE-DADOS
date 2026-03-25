# Super Plataforma 🎮

Jogo de plataforma 2D estilo Mario feito com Python + Pygame.

## Pré-requisitos
- Python 3.8 ou superior
- pip

## Instalação e execução

### Windows
```
pip install pygame
python main.py
```

### macOS / Linux
```
pip3 install pygame
python3 main.py
```

## Controles
| Tecla | Ação |
|-------|------|
| Seta Esquerda / A | Mover para a esquerda |
| Seta Direita / D | Mover para a direita |
| Seta Cima / W / Espaço | Pular |
| ESC | Sair |

## Como vencer
Colete as **10 moedas douradas** espalhadas pela fase e chegue à **META** (bandeira verde).

## Mecânicas
- **Inimigos**: Pule em cima deles para derrotá-los (+200 pts). Tocar de lado custa uma vida.
- **Moedas**: +100 pts cada.
- **Vidas**: Começa com 3. Game over quando chegar a 0.
- **Invencibilidade**: Após levar dano, o jogador pisca por 2 segundos.

## Solução de problemas comuns

**"No module named pygame"**
→ Execute: `pip install pygame` (Windows) ou `pip3 install pygame` (Mac/Linux)

**Tela preta ou erro de display no Linux**
→ Instale: `sudo apt-get install python3-pygame` ou `pip3 install pygame`

**Jogo lento no macOS**
→ Use Python 3.10+ e pygame 2.x para melhor compatibilidade com Apple Silicon.

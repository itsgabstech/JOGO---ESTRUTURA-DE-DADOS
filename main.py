#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════╗
║           UNIMA SURVIVORS — Apocalipse Zumbi              ║
║      Sobreviva às hordas no campus da UNIMA Afya!         ║
║                                                           ║
║   Inspirado no estilo Vampire Survivors                   ║
║   Feito com Python + Pygame                               ║
╚═══════════════════════════════════════════════════════════╝

Controles:
  WASD / Setas   - Movimentar
  Mouse / Auto   - Atirar
  TAB            - Alternar modo de tiro (auto/manual)
  I              - Inventário
  E              - Usar item
  Q              - Descartar item
  ESC            - Pausar / Voltar
"""

from game.engine import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

"""
UNIMA Survivors - NPC System
Non-player characters with dialogue.
"""
import pygame
import math
from game.config import *


class NPC:
    def __init__(self, x, y, name, dialogues, sprite_color=(100, 150, 200)):
        self.x = float(x)
        self.y = float(y)
        self.name = name
        self.dialogues = dialogues
        self.current_dialogue = 0
        self.w = 12
        self.h = 14
        self.sprite_color = sprite_color
        self.interaction_range = 30
        
    def update(self):
        pass
    
    def interact(self):
        """Retorna o próximo diálogo"""
        dialogue = self.dialogues[self.current_dialogue]
        self.current_dialogue = (self.current_dialogue + 1) % len(self.dialogues)
        return dialogue
    
    def distance_to(self, px, py):
        dx = self.x - px
        dy = self.y - py
        return math.sqrt(dx * dx + dy * dy)
    
    def can_interact(self, player):
        return self.distance_to(player.x, player.y) <= self.interaction_range
    
    def draw(self, surface, cam_x, cam_y):
        """Desenha o NPC na tela com um marcador visível"""
        sx = self.x - cam_x - 8
        sy = self.y - cam_y - 12
        
        # Sombra
        pygame.draw.ellipse(surface, (0, 0, 0, 100), (sx + 2, sy + 14, 12, 6))
        
        # Corpo
        pygame.draw.rect(surface, self.sprite_color, (sx, sy, 16, 16))
        pygame.draw.rect(surface, (50, 50, 50), (sx, sy, 16, 16), 2)
        
        # Olhos
        pygame.draw.circle(surface, (255, 255, 255), (sx + 4, sy + 5), 2)
        pygame.draw.circle(surface, (255, 255, 255), (sx + 12, sy + 5), 2)
        pygame.draw.circle(surface, (0, 0, 0), (sx + 4, sy + 5), 1)
        pygame.draw.circle(surface, (0, 0, 0), (sx + 12, sy + 5), 1)
        
        # Nome acima
        font = pygame.font.SysFont('consolas', 8)
        name_text = font.render(self.name, True, (255, 255, 100))
        surface.blit(name_text, (sx + 2, sy - 10))
        
        # Indicador de interação (balão)
        font_sm = pygame.font.SysFont('consolas', 7)
        talk_text = font_sm.render("[E]", True, (100, 255, 100))
        surface.blit(talk_text, (sx + 4, sy - 20))
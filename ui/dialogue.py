"""
UNIMA Survivors - Dialogue System
Handles NPC conversations.
"""
import pygame
from game.config import *


class DialogueBox:
    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.active = False
        self.current_npc = None
        self.current_text = ""
        self.text_progress = 0
        self.text_timer = 0
        self.char_delay = 2
        self.line_height = 20
        
    def start_dialogue(self, npc):
        """Inicia conversa com um NPC"""
        self.active = True
        self.current_npc = npc
        self.current_text = npc.interact()
        self.text_progress = 0
        self.text_timer = 0
        
    def update(self):
        """Atualiza animação do texto"""
        if not self.active:
            return
        
        self.text_timer += 1
        if self.text_timer >= self.char_delay:
            self.text_timer = 0
            if self.text_progress < len(self.current_text):
                self.text_progress += 1
                
    def next_line(self):
        """Avança para próxima linha ou fecha diálogo"""
        if self.text_progress < len(self.current_text):
            self.text_progress = len(self.current_text)
        else:
            self.current_text = self.current_npc.interact()
            self.text_progress = 0
                
    def close(self):
        """Fecha a caixa de diálogo"""
        self.active = False
        self.current_npc = None
        self.current_text = ""
        self.text_progress = 0
        
    def draw(self, surface):
        """Desenha a caixa de diálogo"""
        if not self.active or not self.current_text:
            return
            
        box_w = self.sw - 100
        box_h = 120
        box_x = 50
        box_y = self.sh - box_h - 20
        
        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill((0, 0, 0, 220))
        pygame.draw.rect(box, UI_GOLD, (0, 0, box_w, box_h), 3)
        
        font = pygame.font.SysFont('consolas', 14, bold=True)
        name_text = font.render(self.current_npc.name, True, UI_GOLD)
        box.blit(name_text, (15, 10))
        
        # Linha separadora
        pygame.draw.line(box, UI_GOLD, (10, 28), (box_w - 10, 28), 1)
        
        font_sm = pygame.font.SysFont('consolas', 12)
        displayed = self.current_text[:self.text_progress]
        
        # Quebra de linha automática
        words = displayed.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if font_sm.size(test_line)[0] < box_w - 30:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        for i, line in enumerate(lines[:4]):
            text_surf = font_sm.render(line, True, UI_TEXT)
            box.blit(text_surf, (15, 40 + i * self.line_height))
        
        # Seta indicadora para continuar
        if self.text_progress >= len(self.current_text):
            continue_text = font_sm.render("[E] Continuar...", True, UI_BLUE)
            box.blit(continue_text, (box_w - 110, box_h - 22))
        
        surface.blit(box, (box_x, box_y))
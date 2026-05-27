"""
UNIMA Survivors - Renderer
Handles all game world drawing with camera and scaling.
"""
import random

import pygame
from game.config import *
from assets.sprites import (
    create_player_sprite, create_zombie_sprite, create_bullet_sprite,
    create_loot_sprite, generate_tile_grass, generate_tile_path,
    generate_tile_building, generate_tile_wall, generate_tile_parking,
    generate_tile_concrete, generate_tile_tree, generate_tile_road,
    create_cursor_sprite
)


class Renderer:
    def __init__(self):
        # Camera
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.view_w = SCREEN_WIDTH / SCALE
        self.view_h = SCREEN_HEIGHT / SCALE

        # Create the game surface (low-res, pixel art)
        self.game_surface = pygame.Surface(
            (int(self.view_w), int(self.view_h)))

        # Cache sprites
        self._cache_sprites()

    # ========== FUNÇÕES AUXILIARES DE DESENHO ==========
    def _px(self, surface, x, y, color):
        """Draw a single pixel."""
        if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
            surface.set_at((x, y), color)
    
    def _rect(self, surface, x, y, w, h, color):
        """Draw filled rectangle."""
        for dy in range(h):
            for dx in range(w):
                self._px(surface, x + dx, y + dy, color)

    # ========== SPRITES DE PROJÉTEIS ==========
    def _create_shotgun_pellet(self):
        """Cria projétil de espingarda"""
        s = pygame.Surface((3, 3), pygame.SRCALPHA)
        self._rect(s, 0, 0, 3, 3, (200, 180, 50))
        self._px(s, 1, 1, (255, 220, 100))
        return s
    
    def _create_rocket_sprite(self):
        """Cria míssil da bazuca"""
        s = pygame.Surface((6, 6), pygame.SRCALPHA)
        self._rect(s, 1, 1, 4, 4, (200, 100, 30))
        self._rect(s, 2, 0, 2, 2, (255, 150, 50))
        self._rect(s, 2, 4, 2, 2, (255, 100, 30))
        return s
    
    def _create_fire_sprite(self):
        """Cria chama do coquetel molotov"""
        s = pygame.Surface((8, 8), pygame.SRCALPHA)
        colors = [(255, 100, 0), (255, 150, 0), (255, 200, 0)]
        for i, c in enumerate(colors):
            self._rect(s, i+1, i, 2, 2, c)
            self._rect(s, i+1, 6-i, 2, 2, c)
        return s
    
    def _create_mine_sprite(self):
        """Cria mina terrestre"""
        s = pygame.Surface((8, 8), pygame.SRCALPHA)
        self._rect(s, 2, 2, 4, 4, (80, 80, 90))
        self._rect(s, 3, 1, 2, 6, (60, 60, 70))
        self._rect(s, 1, 3, 6, 2, (60, 60, 70))
        self._px(s, 3, 3, (200, 50, 50))
        return s
    
    def _create_slash_sprite(self):
        """Cria efeito de corte da faquinha"""
        s = pygame.Surface((12, 12), pygame.SRCALPHA)
        for i in range(3):
            self._rect(s, 9-i, i, 2, 1, (200, 200, 200))
            self._rect(s, i, i, 2, 1, (200, 200, 200))
        return s
    
    def _create_grenade_sprite(self):
        """Cria granada do lançador"""
        s = pygame.Surface((6, 6), pygame.SRCALPHA)
        self._rect(s, 1, 1, 4, 4, (100, 150, 80))
        self._rect(s, 2, 0, 2, 2, (150, 200, 120))
        return s

    def _draw_professor_vital(self, surface, enemy, ex, ey):
        """Draw a large humanoid-monster boss and speech bubble."""
        left = int(ex - enemy.w // 2)
        top = int(ey - enemy.h // 2)
        width = int(enemy.w)
        height = int(enemy.h)

        pygame.draw.ellipse(surface, (0, 0, 0, 80),
                            (left + 16, top + height - 12, width - 32, 12))

        leg_y = top + int(height * 0.70)
        pygame.draw.rect(surface, (44, 28, 28), (left + 22, leg_y, 14, 20), border_radius=4)
        pygame.draw.rect(surface, (44, 28, 28), (left + width - 36, leg_y, 14, 20), border_radius=4)
        pygame.draw.rect(surface, (25, 20, 20), (left + 18, leg_y + 16, 22, 7), border_radius=3)
        pygame.draw.rect(surface, (25, 20, 20), (left + width - 40, leg_y + 16, 22, 7), border_radius=3)

        torso = pygame.Rect(left + 14, top + 24, width - 28, 52)
        pygame.draw.rect(surface, (68, 42, 46), torso, border_radius=10)
        pygame.draw.rect(surface, (130, 78, 82), torso, 3, border_radius=10)

        arm_y = top + 34
        pygame.draw.rect(surface, (65, 40, 40), (left + 4, arm_y, 14, 34), border_radius=6)
        pygame.draw.rect(surface, (65, 40, 40), (left + width - 18, arm_y, 14, 34), border_radius=6)
        pygame.draw.polygon(surface, (185, 70, 70),
                            [(left + 3, arm_y + 30), (left + 1, arm_y + 38), (left + 8, arm_y + 34)])
        pygame.draw.polygon(surface, (185, 70, 70),
                            [(left + width - 3, arm_y + 30), (left + width - 1, arm_y + 38), (left + width - 8, arm_y + 34)])

        pygame.draw.rect(surface, (210, 210, 220),
                         (left + int(width * 0.38), top + 35, int(width * 0.24), 35), border_radius=4)
        pygame.draw.line(surface, (170, 170, 185),
                         (left + width // 2, top + 35),
                         (left + width // 2, top + 69), 2)

        pygame.draw.rect(surface, (120, 150, 95),
                         (left + 22, top + 4, width - 44, 28), border_radius=8)
        pygame.draw.rect(surface, (45, 38, 28),
                         (left + 24, top + 2, width - 48, 9), border_radius=4)

        eye_y = top + 16
        pygame.draw.circle(surface, (255, 70, 70), (left + int(width * 0.36), eye_y), 5)
        pygame.draw.circle(surface, (255, 70, 70), (left + int(width * 0.64), eye_y), 5)
        pygame.draw.circle(surface, (255, 220, 220), (left + int(width * 0.36), eye_y), 2)
        pygame.draw.circle(surface, (255, 220, 220), (left + int(width * 0.64), eye_y), 2)
        pygame.draw.rect(surface, (60, 20, 20),
                         (left + int(width * 0.38), top + 22, int(width * 0.24), 5), border_radius=2)
        pygame.draw.rect(surface, (220, 220, 220),
                         (left + int(width * 0.41), top + 23, int(width * 0.18), 2), border_radius=1)

        if enemy.hit_flash > 0:
            flash = pygame.Surface((width, height), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 120))
            surface.blit(flash, (left, top))
        elif not enemy.alive:
            fade = pygame.Surface((width, height), pygame.SRCALPHA)
            fade.fill((0, 0, 0, min(220, enemy.death_timer * 8)))
            surface.blit(fade, (left, top))

        if enemy.alive and getattr(enemy, 'speech_timer', 0) > 0 and getattr(enemy, 'speech_text', ''):
            font = pygame.font.SysFont('consolas', 7, bold=True)
            text = font.render(enemy.speech_text, True, (20, 20, 25))
            bubble_w = text.get_width() + 8
            bubble_h = text.get_height() + 6
            bx = left + width + 8
            by = top + 8
            max_x = int(self.view_w - bubble_w - 2)
            if bx > max_x:
                bx = max(2, left - bubble_w - 8)
            by = max(2, min(by, int(self.view_h - bubble_h - 2)))
            bubble = pygame.Surface((bubble_w, bubble_h), pygame.SRCALPHA)
            bubble.fill((245, 245, 235, 235))
            pygame.draw.rect(bubble, (35, 35, 45), (0, 0, bubble_w, bubble_h), 1)
            bubble.blit(text, (4, 3))
            surface.blit(bubble, (bx, by))
            tail = [(bx, by + bubble_h - 4), (bx - 4, by + bubble_h + 1), (left + width - 1, top + 18)]
            if bx < left:
                tail = [(bx + bubble_w, by + bubble_h - 4), (bx + bubble_w + 4, by + bubble_h + 1), (left + 1, top + 18)]
            pygame.draw.polygon(surface, (245, 245, 235), tail)
            pygame.draw.polygon(surface, (35, 35, 45), tail, 1)

    def _cache_sprites(self):
        """Pre-render all sprite variations."""
        # Player
        self.player_sprites = {}
        for d in range(4):
            for f in range(4):
                self.player_sprites[(d, f)] = create_player_sprite(d, f)

        # Zombies
        self.zombie_sprites = {}
        for v in range(3):
            for f in range(4):
                self.zombie_sprites[(v, f)] = create_zombie_sprite(v, f)

        # Bullet padrão (fallback)
        self.default_bullet = create_bullet_sprite()
        
        # Bullet sprites para diferentes tipos de arma
        # 'grenade' é o tipo do projétil do lançador de granadas (weapon type = grenade_launcher)
        self.bullet_sprites = {
            'normal':           create_bullet_sprite(),
            'shotgun':          self._create_shotgun_pellet(),
            'explosive':        self._create_rocket_sprite(),
            'fire':             self._create_fire_sprite(),
            'mine':             self._create_mine_sprite(),
            'melee':            self._create_slash_sprite(),
            'grenade':          self._create_grenade_sprite(),       # projétil do lançador
            'grenade_launcher': self._create_grenade_sprite(),       # alias de segurança
        }

        # Loot - incluir TODOS os tipos
        loot_types_to_create = ['health', 'ammo_pack', 'ammo_specific', 'weapon', 'xp']
        self.loot_sprites = {}
        for lt in loot_types_to_create:
            self.loot_sprites[lt] = create_loot_sprite(lt)

        # Tiles
        self.tile_sprites = {
            T_GRASS: [generate_tile_grass(i) for i in range(4)],
            T_PATH: [generate_tile_path()],
            T_BUILDING: [generate_tile_building()],
            T_WALL: [generate_tile_wall()],
            T_PARKING: [generate_tile_parking()],
            T_CONCRETE: [generate_tile_concrete()],
            T_DOOR: [generate_tile_path()],  # doors look like path
            T_TREE: [generate_tile_tree(i) for i in range(4)],
            T_ROAD: [generate_tile_road(0), generate_tile_road(1)],
        }

        # Cursor
        self.cursor_sprite = create_cursor_sprite()

    def update_camera(self, target_x, target_y):
        """Smoothly follow target."""
        target_cam_x = target_x - self.view_w / 2
        target_cam_y = target_y - self.view_h / 2

        # Smooth lerp
        self.cam_x += (target_cam_x - self.cam_x) * 0.1
        self.cam_y += (target_cam_y - self.cam_y) * 0.1

        # Clamp to map
        self.cam_x = max(0, min(MAP_PX_W - self.view_w, self.cam_x))
        self.cam_y = max(0, min(MAP_PX_H - self.view_h, self.cam_y))

    def draw_world(self, screen, tilemap, player, enemies, bullets,
                   loot_drops, effects, shake_offset=(0, 0), npcs=None):
        """Draw entire game world to screen."""
        gs = self.game_surface
        gs.fill((20, 25, 15))

        cx, cy = self.cam_x, self.cam_y

        # ── Draw tiles ──
        start_tx = max(0, int(cx / TILE_SIZE) - 1)
        start_ty = max(0, int(cy / TILE_SIZE) - 1)
        end_tx = min(MAP_WIDTH, int((cx + self.view_w) / TILE_SIZE) + 2)
        end_ty = min(MAP_HEIGHT, int((cy + self.view_h) / TILE_SIZE) + 2)

        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                tile = tilemap[ty][tx]
                sprites = self.tile_sprites.get(tile, self.tile_sprites[T_GRASS])
                variant = (tx + ty) % len(sprites)
                sprite = sprites[variant]
                sx = tx * TILE_SIZE - int(cx)
                sy = ty * TILE_SIZE - int(cy)
                gs.blit(sprite, (sx, sy))

        # ── Draw loot ──
        for drop in loot_drops:
            if not drop.alive or not drop.is_visible():
                continue
            dx = drop.x - cx
            dy = drop.y - cy + drop.bob_offset
            if -16 < dx < self.view_w + 16 and -16 < dy < self.view_h + 16:
                loot_type = None
                
                if isinstance(drop.loot_data, dict) and drop.loot_data.get('type') == 'weapon':
                    loot_type = 'weapon'
                elif isinstance(drop.loot_data, str):
                    loot_type = drop.loot_data
                elif isinstance(drop.loot_data, dict) and 'type' in drop.loot_data:
                    loot_type = drop.loot_data['type']
                else:
                    loot_type = 'ammo_pack'
                
                sprite = self.loot_sprites.get(loot_type)
                if not sprite and loot_type == 'weapon':
                    sprite = self.loot_sprites.get('ammo_pack')
                
                if sprite:
                    gs.blit(sprite, (int(dx) - 6, int(dy) - 6))

        # ── Draw bullets (COM SPRITES DIFERENTES POR TIPO) ──
        for b in bullets:
            bx = b['x'] - cx
            by = b['y'] - cy
            if -16 < bx < self.view_w + 16 and -16 < by < self.view_h + 16:
                if b.get('hostile'):
                    kind = b.get('kind', 'no_lista')
                    if kind == 'prova':
                        pygame.draw.rect(gs, (245, 245, 250),
                                         (int(bx) - 4, int(by) - 4, 8, 8))
                        pygame.draw.rect(gs, (40, 40, 60),
                                         (int(bx) - 4, int(by) - 4, 8, 8), 1)
                    else:
                        pygame.draw.circle(gs, (90, 180, 255),
                                           (int(bx), int(by)), 4)
                        pygame.draw.circle(gs, (25, 40, 70),
                                           (int(bx), int(by)), 2)
                else:
                    bullet_type = b.get('type', 'normal')
                    sprite = self.bullet_sprites.get(bullet_type, self.default_bullet)
                    sprite_w = sprite.get_width()
                    sprite_h = sprite.get_height()
                    gs.blit(sprite, (int(bx) - sprite_w//2, int(by) - sprite_h//2))

        # ── Draw enemies ──
        for enemy in enemies:
            if not enemy.alive and enemy.death_timer > 15:
                continue
            ex = enemy.x - cx
            ey = enemy.y - cy
            if -20 < ex < self.view_w + 20 and -20 < ey < self.view_h + 20:
                if getattr(enemy, 'is_boss', False):
                    self._draw_professor_vital(gs, enemy, ex, ey)
                else:
                    key = (enemy.variant, enemy.anim_frame % 2)
                    sprite = self.zombie_sprites.get(key)
                    if sprite:
                        if enemy.hit_flash > 0:
                            flash = sprite.copy()
                            flash.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
                            gs.blit(flash, (int(ex) - 8, int(ey) - 8))
                        elif not enemy.alive:
                            alpha = max(0, 255 - enemy.death_timer * 17)
                            fade = sprite.copy()
                            fade.set_alpha(alpha)
                            gs.blit(fade, (int(ex) - 8, int(ey) - 8))
                        else:
                            gs.blit(sprite, (int(ex) - 8, int(ey) - 8))

                # HP bar for damaged enemies
                if enemy.alive and enemy.hp < enemy.max_hp:
                    bar_w = 64 if getattr(enemy, 'is_boss', False) else 12
                    bar_h = 2
                    bx = int(ex) - bar_w // 2
                    by = int(ey - enemy.h // 2) - 8 if getattr(enemy, 'is_boss', False) else int(ey) - 10
                    pygame.draw.rect(gs, (60, 15, 15), (bx, by, bar_w, bar_h))
                    fill = int(bar_w * enemy.hp / enemy.max_hp)
                    pygame.draw.rect(gs, (220, 40, 40), (bx, by, fill, bar_h))
       
        # ── Draw NPCs ──
        if npcs:    
            for npc in npcs:
                self.draw_npc(gs, npc, cx, cy)

        # ── Draw player ──
        if player.alive:
            px_ = player.x - cx
            py_ = player.y - cy
            key = (player.direction, player.anim_frame % 2)
            sprite = self.player_sprites.get(key)
            if sprite:
                if player.invincible_timer > 0 and player.invincible_timer % 4 < 2:
                    pass
                else:
                    gs.blit(sprite, (int(px_) - 8, int(py_) - 8))

        # ── Draw particles & effects ──
        font_sm = pygame.font.SysFont('consolas', 6)
        effects.draw(gs, cx, cy, 1.0, font_sm)

        # ── Scale up to screen ──
        screen_w, screen_h = screen.get_size()
        scaled = pygame.transform.scale(gs, (screen_w, screen_h))
        screen.blit(scaled, (shake_offset[0], shake_offset[1]))

    def world_to_screen(self, wx, wy):
        """Convert world coords to screen coords."""
        return (int((wx - self.cam_x) * SCALE),
                int((wy - self.cam_y) * SCALE))

    def screen_to_world(self, sx, sy):
        """Convert screen coords to world coords."""
        return (sx / SCALE + self.cam_x,
                sy / SCALE + self.cam_y)
    
    def _create_grenade_explosion(self):
        """Cria sprite de explosão de granada"""
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        colors = [(255, 200, 50), (255, 150, 30), (255, 80, 20), (200, 50, 10)]
        for i, color in enumerate(colors):
            r = 8 - i
            for dy in range(-r, r+1):
                for dx in range(-r, r+1):
                    if dx*dx + dy*dy <= r*r:
                        self._px(s, 8 + dx, 8 + dy, color)
        return s

    def _create_fire_effect(self):
            """Cria sprite de chamas"""
            s = pygame.Surface((12, 12), pygame.SRCALPHA)
            fire_colors = [(255, 100, 0), (255, 150, 0), (255, 200, 0), (255, 255, 100)]
            for i in range(4):
                offset = random.randint(-1, 1)
                for y in range(3):
                    for x in range(2):
                        self._px(s, 2 + x + offset, 8 - i*2 + y, fire_colors[i])
                        self._px(s, 8 + x + offset, 8 - i*2 + y, fire_colors[i])
            return s
        
    def _create_mine_explosion(self):
        """Cria sprite de explosão de mina"""
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        for i in range(5):
            r = 10 - i
            color = (200 - i*30, 100 - i*15, 50 - i*10)
            for dy in range(-r, r+1):
                for dx in range(-r, r+1):
                    if dx*dx + dy*dy <= r*r and random.random() > 0.3:
                        self._px(s, 10 + dx, 10 + dy, color)
        return s

    def draw_npc(self, surface, npc, cam_x, cam_y):
        """Desenha um NPC na tela"""
        sx = npc.x - cam_x - 8
        sy = npc.y - cam_y - 12
        
        # Só desenha se estiver visível na tela
        if sx < -30 or sx > self.view_w + 30 or sy < -30 or sy > self.view_h + 30:
            return
        
        # Sombra
        pygame.draw.ellipse(surface, (0, 0, 0, 100), (sx + 2, sy + 14, 12, 6))
        
        # Corpo
        pygame.draw.rect(surface, npc.sprite_color, (sx, sy, 16, 16))
        pygame.draw.rect(surface, (50, 50, 50), (sx, sy, 16, 16), 2)
        
        # Olhos
        pygame.draw.circle(surface, (255, 255, 255), (sx + 4, sy + 5), 2)
        pygame.draw.circle(surface, (255, 255, 255), (sx + 12, sy + 5), 2)
        pygame.draw.circle(surface, (0, 0, 0), (sx + 4, sy + 5), 1)
        pygame.draw.circle(surface, (0, 0, 0), (sx + 12, sy + 5), 1)
        
        # Nome acima
        font = pygame.font.SysFont('consolas', 8)
        name_text = font.render(npc.name, True, (255, 255, 100))
        surface.blit(name_text, (sx + 2, sy - 10))
        
        # Indicador de interação (balão)
        font_sm = pygame.font.SysFont('consolas', 7)
        talk_text = font_sm.render("[E]", True, (100, 255, 100))
        surface.blit(talk_text, (sx + 4, sy - 20))
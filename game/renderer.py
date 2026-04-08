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
    generate_tile_concrete, create_cursor_sprite
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
        self.bullet_sprites = {
            'normal': create_bullet_sprite(),
            'shotgun': self._create_shotgun_pellet(),
            'explosive': self._create_rocket_sprite(),
            'fire': self._create_fire_sprite(),
            'mine': self._create_mine_sprite(),
            'melee': self._create_slash_sprite(),
            'grenade_launcher': self._create_grenade_sprite()
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
            T_DOOR: [generate_tile_path()],
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
                   loot_drops, effects, shake_offset=(0, 0)):
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
                    bar_w = 12
                    bar_h = 2
                    bx = int(ex) - bar_w // 2
                    by = int(ey) - 10
                    pygame.draw.rect(gs, (60, 15, 15), (bx, by, bar_w, bar_h))
                    fill = int(bar_w * enemy.hp / enemy.max_hp)
                    pygame.draw.rect(gs, (220, 40, 40), (bx, by, fill, bar_h))

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

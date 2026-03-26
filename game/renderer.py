"""
UNIMA Survivors - Renderer
Handles all game world drawing with camera and scaling.
"""
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

    def _cache_sprites(self):
        """Pre-render all sprite variations."""
        # Player: 4 directions x 4 frames
        self.player_sprites = {}
        for d in range(4):
            for f in range(4):
                self.player_sprites[(d, f)] = create_player_sprite(d, f)

        # Zombies: 3 variants x 4 frames
        self.zombie_sprites = {}
        for v in range(3):
            for f in range(4):
                self.zombie_sprites[(v, f)] = create_zombie_sprite(v, f)

        # Bullet
        self.bullet_sprite = create_bullet_sprite()

        # Loot
        self.loot_sprites = {}
        for lt in LOOT_TYPES:
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
                # Use position-based variant for grass
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
                sprite = self.loot_sprites.get(drop.type)
                if sprite:
                    gs.blit(sprite, (int(dx) - 6, int(dy) - 6))

        # ── Draw bullets ──
        for b in bullets:
            bx = b['x'] - cx
            by = b['y'] - cy
            if -8 < bx < self.view_w + 8 and -8 < by < self.view_h + 8:
                gs.blit(self.bullet_sprite, (int(bx) - 2, int(by) - 2))

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
                        # Flash white
                        flash = sprite.copy()
                        flash.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
                        gs.blit(flash, (int(ex) - 8, int(ey) - 8))
                    elif not enemy.alive:
                        # Fade out
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
                # Blink during invincibility
                if player.invincible_timer > 0 and player.invincible_timer % 4 < 2:
                    pass  # skip drawing (blink)
                else:
                    gs.blit(sprite, (int(px_) - 8, int(py_) - 8))

        # ── Draw particles & effects ──
        font_sm = pygame.font.SysFont('consolas', 6)
        effects.draw(gs, cx, cy, 1.0, font_sm)

        # ── Scale up to screen ──
        scaled = pygame.transform.scale(gs, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled, (shake_offset[0], shake_offset[1]))

    def world_to_screen(self, wx, wy):
        """Convert world coords to screen coords."""
        return (int((wx - self.cam_x) * SCALE),
                int((wy - self.cam_y) * SCALE))

    def screen_to_world(self, sx, sy):
        """Convert screen coords to world coords."""
        return (sx / SCALE + self.cam_x,
                sy / SCALE + self.cam_y)

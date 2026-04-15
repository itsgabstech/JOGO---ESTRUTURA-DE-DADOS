"""
UNIMA Survivors - Enemies Module
Zombie types, AI, spawning system.
"""
import pygame
import math
import random
from game.config import *


class Enemy:
    def __init__(self, x, y, variant=ZOMBIE_COMMON):
        self.x = float(x)
        self.y = float(y)
        self.variant = variant
        stats = ENEMY_STATS[variant]
        self.max_hp = stats['hp']
        self.hp = self.max_hp
        self.speed = stats['speed']
        self.damage = stats['damage']
        self.xp_value = stats['xp']
        self.name = stats['name']
        self.alive = True
        self.w = 12
        self.h = 14
        self.anim_frame = 0
        self.anim_timer = 0
        self.hit_flash = 0
        self.death_timer = 0  # for death animation
        self.attack_cooldown = 0  # frames until can damage player again

    def update(self, player_x, player_y, tilemap, all_enemies):
        """Move towards player."""
        if not self.alive:
            self.death_timer += 1
            return None

        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 1:
            dx /= dist
            dy /= dist

            # Simple separation from other enemies
            sep_x, sep_y = 0, 0
            for other in all_enemies:
                if other is self or not other.alive:
                    continue
                ox = self.x - other.x
                oy = self.y - other.y
                od = math.sqrt(ox * ox + oy * oy)
                if od < 10 and od > 0:
                    sep_x += ox / od * 0.3
                    sep_y += oy / od * 0.3

            move_x = dx * self.speed + sep_x
            move_y = dy * self.speed + sep_y

            from game.campus_map import get_walkable
            new_x = self.x + move_x
            new_y = self.y + move_y
            if get_walkable(tilemap, new_x, self.y):
                self.x = new_x
            if get_walkable(tilemap, self.x, new_y):
                self.y = new_y

        # Animation
        self.anim_timer += 1
        if self.anim_timer >= 12:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4

        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        return None

    def take_damage(self, amount):
        """Apply damage. Returns True if killed."""
        self.hp -= amount
        self.hit_flash = 6
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            return True
        return False

    def collides_with_player(self, player):
        """Check collision with player and apply damage with cooldown."""
        if not self.alive or self.attack_cooldown > 0:
            return False
        dx = abs(self.x - player.x)
        dy = abs(self.y - player.y)
        reach_x = (self.w + player.w) * 0.35
        reach_y = (self.h + player.h) * 0.35
        if dx < reach_x and dy < reach_y:
            self.attack_cooldown = 40  # ~0.67 seconds between attacks
            return True
        return False

    @property
    def rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2,
                           self.w, self.h)


class EnemySpawner:
    def __init__(self):
        self.timer = 0
        self.spawn_rate = ENEMY_SPAWN_RATE
        self.difficulty = 1.0
        self.total_time = 0
        self.phase_multiplier = 1

    def update(self, player_x, player_y, enemies, tilemap, phase=1):
        """Spawn enemies around the player."""
        self.total_time += 1
        self.timer += 1

        # Increase difficulty over time
        if self.total_time % (60 * 30) == 0:  # every 30s
            self.difficulty += 0.15
            self.spawn_rate = max(ENEMY_SPAWN_MIN,
                                  int(ENEMY_SPAWN_RATE / self.difficulty))

        if self.timer < self.spawn_rate:
            return
        self.timer = 0

        if len([e for e in enemies if e.alive]) >= MAX_ENEMIES * self.phase_multiplier:
            return

        # Spawn 1-3 enemies (phase multiplier duplicates spawn amount in phase 2)
        base_count = random.randint(1, min(3, int(self.difficulty)))
        count = base_count * self.phase_multiplier
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(ENEMY_SPAWN_DIST_MIN, ENEMY_SPAWN_DIST_MAX)
            sx = player_x + math.cos(angle) * dist
            sy = player_y + math.sin(angle) * dist

            # Clamp to map
            sx = max(TILE_SIZE * 2, min(MAP_PX_W - TILE_SIZE * 2, sx))
            sy = max(TILE_SIZE * 2, min(MAP_PX_H - TILE_SIZE * 2, sy))

            from game.campus_map import get_walkable
            if not get_walkable(tilemap, sx, sy):
                continue

            # Choose variant based on difficulty and phase.
            r = random.random()
            if phase >= 3 and r < 0.18:
                variant = ZOMBIE_BRUTE
            elif r < 0.12 * self.difficulty and self.difficulty > 1.6:
                variant = ZOMBIE_TANK
            elif r < 0.30 * self.difficulty:
                variant = ZOMBIE_FAST
            else:
                variant = ZOMBIE_COMMON

            # Scale HP with difficulty, and make phase 3 enemies tougher.
            enemy = Enemy(sx, sy, variant)
            if phase >= 3:
                enemy.speed *= 1.25
                enemy.max_hp = int(enemy.max_hp * 1.25)

            enemy.max_hp = int(enemy.max_hp * (1 + (self.difficulty - 1) * 0.3))
            enemy.hp = enemy.max_hp
            enemies.append(enemy)


class ProfessorVital(Enemy):
    """Final boss: huge health, relentless chase and projectile pressure."""

    def __init__(self, x, y):
        super().__init__(x, y, ZOMBIE_TANK)
        self.name = "Professor Vital"
        self.max_hp = 520
        self.hp = self.max_hp
        self.speed = 0.75
        self.damage = 22
        self.xp_value = 180
        self.w = 96
        self.h = 96
        self.is_boss = True
        self.projectile_cooldown = FPS * 3
        self.speech_text = "EU SOU O BOSS! Aqui e sem consulta!"
        self.speech_timer = FPS * 8

    def update(self, player_x, player_y, tilemap, all_enemies):
        if not self.alive:
            self.death_timer += 1
            return None

        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 1:
            dx /= dist
            dy /= dist
            move_x = dx * self.speed
            move_y = dy * self.speed

            from game.campus_map import get_walkable
            new_x = self.x + move_x
            new_y = self.y + move_y
            if get_walkable(tilemap, new_x, self.y):
                self.x = new_x
            if get_walkable(tilemap, self.x, new_y):
                self.y = new_y

        self.anim_timer += 1
        if self.anim_timer >= 10:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4

        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.speech_timer > 0:
            self.speech_timer -= 1

        self.projectile_cooldown -= 1
        if self.projectile_cooldown > 0:
            return None
        self.projectile_cooldown = FPS * 3

        length = max(1.0, dist)
        vx = (player_x - self.x) / length
        vy = (player_y - self.y) / length
        return {
            'x': self.x,
            'y': self.y - self.h * 0.2,
            'dx': vx * 3.2,
            'dy': vy * 3.2,
            'damage': 16,
            'life': 220,
            'hostile': True,
            'type': 'boss_projectile',
            'kind': random.choice(['prova', 'no_lista']),
        }
"""
UNIMA Survivors - Player Module
Handles player movement, shooting, stats, collision.
"""
import pygame
import math
from game.config import *


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.w = 12
        self.h = 14

        # Stats
        self.max_hp = PLAYER_MAX_HP
        self.hp = self.max_hp
        self.speed = PLAYER_SPEED
        self.ammo = PLAYER_START_AMMO
        self.fire_rate = PLAYER_FIRE_RATE
        self.damage = PLAYER_DAMAGE
        self.pickup_range = PLAYER_PICKUP_RANGE
        self.armor = 0

        # State
        self.alive = True
        self.direction = 0  # 0=down,1=left,2=right,3=up
        self.moving = False
        self.fire_timer = 0
        self.invincible_timer = 0
        self.anim_frame = 0
        self.anim_timer = 0

        # Progression
        self.xp = 0
        self.level = 1
        self.xp_to_next = XP_BASE
        self.kills = 0
        self.total_damage_dealt = 0

        # Combat mode
        self.combat_mode = COMBAT_AUTO

        # Inventory
        self.inventory = [None] * PLAYER_INV_SIZE
        self.selected_slot = 0
        self.weapon_level = 1

    def update(self, keys, tilemap, dt=1):
        """Update player state."""
        if not self.alive:
            return

        # Movement
        dx, dy = 0.0, 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        self.moving = dx != 0 or dy != 0

        if self.moving:
            # Normalize diagonal
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length

            # Update direction
            if abs(dx) > abs(dy):
                self.direction = 1 if dx < 0 else 2
            else:
                self.direction = 3 if dy < 0 else 0

            # Apply movement with collision
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed

            from game.campus_map import get_walkable
            # Check X movement
            if get_walkable(tilemap, new_x - 4, self.y) and \
               get_walkable(tilemap, new_x + 4, self.y):
                self.x = new_x
            # Check Y movement
            if get_walkable(tilemap, self.x, new_y - 4) and \
               get_walkable(tilemap, self.x, new_y + 4):
                self.y = new_y

        # Animation
        self.anim_timer += 1
        if self.anim_timer >= 10:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4

        # Timers
        if self.fire_timer > 0:
            self.fire_timer -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

    def try_shoot(self, enemies, mouse_pos=None, cam_x=0, cam_y=0):
        """Attempt to fire. Returns bullet dict or None."""
        if self.fire_timer > 0 or self.ammo <= 0:
            return None

        target_dx, target_dy = 0, 0

        if self.combat_mode == COMBAT_AUTO:
            # Find nearest enemy
            nearest = None
            nearest_dist = float('inf')
            for e in enemies:
                if not e.alive:
                    continue
                edx = e.x - self.x
                edy = e.y - self.y
                dist = math.sqrt(edx * edx + edy * edy)
                if dist < BULLET_RANGE and dist < nearest_dist:
                    nearest = e
                    nearest_dist = dist
            if nearest is None:
                return None
            target_dx = nearest.x - self.x
            target_dy = nearest.y - self.y
        else:
            # Manual - aim at mouse
            if mouse_pos:
                target_dx = (mouse_pos[0] + cam_x) - self.x
                target_dy = (mouse_pos[1] + cam_y) - self.y
            else:
                # Fallback to facing direction
                dirs = {0: (0, 1), 1: (-1, 0), 2: (1, 0), 3: (0, -1)}
                target_dx, target_dy = dirs[self.direction]

        length = math.sqrt(target_dx * target_dx + target_dy * target_dy)
        if length < 0.1:
            return None
        target_dx /= length
        target_dy /= length

        self.fire_timer = max(3, int(self.fire_rate))
        self.ammo -= 1

        return {
            'x': self.x,
            'y': self.y - 4,
            'dx': target_dx * BULLET_SPEED,
            'dy': target_dy * BULLET_SPEED,
            'damage': self.damage,
            'life': BULLET_RANGE,
        }

    def take_damage(self, amount):
        """Apply damage to player."""
        if self.invincible_timer > 0 or not self.alive:
            return
        actual = max(1, amount - self.armor)
        self.hp -= actual
        self.invincible_timer = 30  # i-frames
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def heal(self, amount):
        """Heal the player."""
        self.hp = min(self.max_hp, self.hp + amount)

    def add_xp(self, amount):
        """Add XP and check level up. Returns True if leveled up."""
        self.xp += amount
        if self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(XP_BASE * (XP_GROWTH ** self.level))
            return True
        return False

    def apply_upgrade(self, upgrade):
        """Apply a level-up upgrade."""
        stat = upgrade['stat']
        val = upgrade['value']
        if stat == 'damage':
            self.damage = int(self.damage * (1 + val))
        elif stat == 'fire_rate':
            self.fire_rate = max(3, self.fire_rate * (1 - val))
        elif stat == 'max_hp':
            self.max_hp += int(val)
            self.hp += int(val)
        elif stat == 'speed':
            self.speed *= (1 + val)
        elif stat == 'pickup_range':
            self.pickup_range *= (1 + val)
        elif stat == 'ammo':
            self.ammo += int(val)

    def add_to_inventory(self, item):
        """Add item to inventory. Returns True if successful."""
        # Check for stackable
        if item['type'] in LOOT_STACKABLE:
            for i in range(PLAYER_INV_SIZE):
                slot = self.inventory[i]
                if slot and slot['type'] == item['type'] and slot.get('count', 1) < 99:
                    slot['count'] = slot.get('count', 1) + 1
                    return True

        # Find empty slot
        for i in range(PLAYER_INV_SIZE):
            if self.inventory[i] is None:
                item['count'] = item.get('count', 1)
                self.inventory[i] = item
                return True
        return False  # Full

    def use_item(self, slot_index):
        """Use item in slot. Returns True if consumed."""
        if slot_index < 0 or slot_index >= PLAYER_INV_SIZE:
            return False
        item = self.inventory[slot_index]
        if item is None:
            return False

        t = item['type']
        if t == 'health':
            if self.hp >= self.max_hp:
                return False
            self.heal(25)
        elif t == 'ammo':
            self.ammo += 15
        elif t == 'speed':
            self.speed *= 1.1
        elif t == 'damage':
            self.damage = int(self.damage * 1.15)
        elif t == 'armor':
            self.armor += 2
        elif t == 'magnet':
            self.pickup_range *= 1.25
        elif t == 'weapon':
            self.weapon_level += 1
            self.damage += 5
            self.fire_rate = max(3, self.fire_rate - 1)
        elif t == 'xp':
            self.add_xp(30)
        else:
            return False

        # Consume
        count = item.get('count', 1)
        if count <= 1:
            self.inventory[slot_index] = None
        else:
            item['count'] = count - 1
        return True

    def drop_item(self, slot_index):
        """Remove item from inventory."""
        if 0 <= slot_index < PLAYER_INV_SIZE:
            self.inventory[slot_index] = None

    @property
    def rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2,
                           self.w, self.h)

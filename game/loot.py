"""
UNIMA Survivors - Loot System
Drop generation, pickup, item management.
"""
import random
import math
from game.config import *


class LootDrop:
    def __init__(self, x, y, loot_type):
        self.x = x
        self.y = y
        self.type = loot_type
        self.alive = True
        self.bob_timer = random.randint(0, 60)
        self.bob_offset = 0
        self.lifetime = 60 * 30  # 30 seconds
        self.flash_timer = 0

    def update(self):
        self.bob_timer += 1
        self.bob_offset = math.sin(self.bob_timer * 0.1) * 1.5
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
        # Flash when about to expire
        if self.lifetime < 180:
            self.flash_timer += 1

    def is_visible(self):
        """Check if visible (for flashing effect)."""
        if self.lifetime < 180:
            return self.flash_timer % 10 < 7
        return True

    def distance_to(self, px, py):
        dx = self.x - px
        dy = self.y - py
        return math.sqrt(dx * dx + dy * dy)

    def to_item(self):
        """Convert to inventory item dict."""
        return {
            'type': self.type,
            'name': LOOT_NAMES.get(self.type, self.type),
            'desc': LOOT_DESCRIPTIONS.get(self.type, ''),
            'count': 1,
        }


def roll_loot(x, y):
    """Roll for loot drop. Returns LootDrop or None."""
    if random.random() > LOOT_DROP_CHANCE:
        return None

    # Weighted random selection
    total = sum(LOOT_WEIGHTS.values())
    r = random.uniform(0, total)
    cumulative = 0
    chosen = 'xp'
    for ltype, weight in LOOT_WEIGHTS.items():
        cumulative += weight
        if r <= cumulative:
            chosen = ltype
            break

    return LootDrop(x, y, chosen)


def try_pickup(player, loot_drops):
    """Check and collect nearby loot. Returns list of collected items."""
    collected = []
    for drop in loot_drops:
        if not drop.alive:
            continue
        dist = drop.distance_to(player.x, player.y)
        if dist <= player.pickup_range:
            # XP is auto-consumed
            if drop.type == 'xp':
                player.add_xp(drop.to_item().get('count', 1) * 15)
                drop.alive = False
                collected.append(drop)
            else:
                item = drop.to_item()
                # Try instant use for some types
                if drop.type == 'health' and player.hp < player.max_hp:
                    player.heal(25)
                    drop.alive = False
                    collected.append(drop)
                elif drop.type == 'ammo':
                    player.ammo += 15
                    drop.alive = False
                    collected.append(drop)
                else:
                    if player.add_to_inventory(item):
                        drop.alive = False
                        collected.append(drop)
    return collected

"""
UNIMA Survivors - Loot System (REFATORADO)
Drop de armas por slot, munição específica por arma, swap automático de slot.
"""
import random
import math
from game.config import *
from game.weapons_data import WEAPONS_DATA, AMMO_TYPES

# Quanto de munição cada drop dá por arma
AMMO_DROP_AMOUNTS = {
    "espingarda":        (4, 8),
    "m4a4":              (10, 20),
    "bazuca":            (1, 2),
    "coquetel_molotov":  (1, 3),
    "mina_terrestre":    (1, 2),
    "lancador_granadas": (2, 4),
}


class LootDrop:
    def __init__(self, x, y, loot_data):
        self.x = x
        self.y = y
        self.loot_data = loot_data
        self.alive = True
        self.bob_timer = random.randint(0, 60)
        self.bob_offset = 0
        self.lifetime = 60 * 30
        self.flash_timer = 0
        self.pickup_delay = 15  # Não pode ser pego por 15 frames

    def update(self):
        self.bob_timer += 1
        self.bob_offset = math.sin(self.bob_timer * 0.1) * 1.5
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
        if self.lifetime < 180:
            self.flash_timer += 1
        if self.pickup_delay > 0:
            self.pickup_delay -= 1

    def is_visible(self):
        if self.lifetime < 180:
            return self.flash_timer % 10 < 7
        return True
    
    def can_pickup(self):
        """Verifica se o drop já pode ser coletado"""
        return self.pickup_delay <= 0

    def distance_to(self, px, py):
        dx = self.x - px
        dy = self.y - py
        return math.sqrt(dx * dx + dy * dy)

    def to_item(self):
        if isinstance(self.loot_data, dict):
            if self.loot_data.get('type') == 'weapon':
                w = self.loot_data['data']
                return {
                    'type': 'weapon', 'name': w['name'],
                    'desc': w['desc'], 'weapon_data': w, 'count': 1,
                }
            if self.loot_data.get('type') == 'ammo_specific':
                wkey = self.loot_data['weapon_key']
                amt  = self.loot_data['amount']
                return {
                    'type': 'ammo_pack',
                    'name': f"Municao {WEAPONS_DATA.get(wkey, {}).get('name', wkey)}",
                    'desc': f"+{amt} municao",
                    'count': 1,
                }
        return {
            'type': self.loot_data,
            'name': LOOT_NAMES.get(self.loot_data, self.loot_data),
            'desc': LOOT_DESCRIPTIONS.get(self.loot_data, ''),
            'count': 1,
        }


def roll_loot(x, y):
    """Roll for loot drop. Returns LootDrop or None."""
    # Primeiro: decide se vai cair algum item.
    if random.random() > LOOT_DROP_CHANCE:
        return None
    key, data = random.choice(candidates)
    weapon_copy = data.copy()
    weapon_copy['current_ammo'] = weapon_copy['max_ammo']
    return LootDrop(x, y, {'type': 'weapon', 'data': weapon_copy, 'slot': slot, 'key': key})


def _make_ammo_drop(x, y, weapon_key):
    lo, hi = AMMO_DROP_AMOUNTS.get(weapon_key, (5, 15))
    amount = random.randint(lo, hi)
    return LootDrop(x, y, {
        'type': 'ammo_specific',
        'weapon_key': weapon_key,
        'amount': amount
    })


def roll_loot(x, y):
    """
    Drops de um zumbi:
      - 15% arma (slot 1 ou 2)
      - 55% municao de uma arma aleatoria
      - 10% kit medico
    """
    drops = []

    if random.random() < 0.15:
        slot = 1 if random.random() < 0.6 else 2
        drop = _make_weapon_drop(x, y, slot)
        if drop:
            drops.append(drop)

    if random.random() < 0.55:
        all_weapon_keys = [
            k for k, v in WEAPONS_DATA.items()
            if v.get('max_ammo', 0) > 0
        ]
        if all_weapon_keys:
            chosen_key = random.choice(all_weapon_keys)
            drops.append(_make_ammo_drop(x, y, chosen_key))

    if random.random() < 0.10:
        drops.append(LootDrop(x, y, 'health'))

    # Segundo: escolhe qual item caiu usando pesos configuráveis.
    total = sum(LOOT_WEIGHTS.values())
    r = random.uniform(0, total)
    cumulative = 0
    chosen = 'xp'
    for ltype, weight in LOOT_WEIGHTS.items():
        cumulative += weight
        if r <= cumulative:
            chosen = ltype
            break


# ─────────────────────────────────────────────────────────────
#  Pickup
# ─────────────────────────────────────────────────────────────

def try_pickup(player, loot_drops, game_ref=None):
    """
    Coleta automática:
      - Munição, vida, XP: automático
      - Arma: precisa pressionar Q em cima do drop
    """
    collected = []
    weapons_on_ground = []  # Lista de armas no chão para interação

    for drop in loot_drops[:]:
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
                    # Munição é aplicada instantaneamente (não vai para inventário).
                    player.ammo += AMMO_PICKUP_AMOUNT
                    drop.alive = False
                    collected.append(drop)
                else:
                    if player.add_to_inventory(item):
                        drop.alive = False
                        collected.append(drop)
    return collected


def try_equip_weapon(player, loot_drops, drop):
    """Tenta equipar uma arma específica do chão"""
    if not drop or not drop.alive:
        return False
    
    data = drop.loot_data
    if not isinstance(data, dict) or data.get('type') != 'weapon':
        return False
    
    weapon_data = data['data']
    slot = data['slot']
    
    # Verifica se o jogador está perto o suficiente
    if drop.distance_to(player.x, player.y) > player.pickup_range:
        return False
    
    old_weapon = player.equip_weapon(weapon_data, slot)
    
    if old_weapon and old_weapon.get('name') != "Faquinha":
        # Dropa a arma antiga em uma posição aleatória
        angle = random.uniform(0, 2 * math.pi)
        dist = 30
        old_drop = LootDrop(
            player.x + math.cos(angle) * dist,
            player.y + math.sin(angle) * dist,
            {'type': 'weapon', 'data': old_weapon, 'slot': old_weapon.get('slot', slot)}
        )
        loot_drops.append(old_drop)
        print(f"[LOOT] Arma antiga dropada: {old_weapon['name']}")
    
    drop.alive = False
    print(f"[LOOT] Equipou arma: {weapon_data['name']} (Slot {slot})")
    return True

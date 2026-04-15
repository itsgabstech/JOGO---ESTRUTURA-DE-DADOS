"""
UNIMA Survivors - Player Module
Handles player movement, shooting, stats, collision.
"""
import pygame
import math
from game.config import *
from game.weapons_data import WEAPONS_DATA, AMMO_TYPES, BULLET_CONFIG


class Player:
    def __init__(self, x, y):

        self.slot_1 = WEAPONS_DATA["faquinha"].copy()  # Começa com faquinha
        self.slot_2 = None
        self.active_slot = 1
        print(f"[INIT] Arma inicial: {self.slot_1['name']}")  # Debug

        self.x = float(x)
        self.y = float(y)
        self.w = 12
        self.h = 14

        # Stats
        self.max_hp = PLAYER_MAX_HP
        self.hp = self.max_hp
        self.speed = PLAYER_SPEED
        self.pickup_range = PLAYER_PICKUP_RANGE
        self.weapon_level = 1
        self.damage = PLAYER_DAMAGE
        self.armor = 0

        # State
        self.alive = True
        self.direction = 0
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

        # Inventory (apenas para consumíveis)
        self.inventory = [None] * PLAYER_INV_SIZE
        self.selected_slot = 0
        
        # NOVO SISTEMA DE ARMAS
        self.slot_1 = WEAPONS_DATA["faquinha"].copy()  # Começa com faquinha
        self.slot_2 = None
        self.active_slot = 1
        self.pickup_cooldown = 0
        
        self.ammo = {
            "shells": 0,
            "rifle_ammo": 0,
            "rockets": 0,
            "molotovs": 0,
            "mines": 0,
            "grenades": 0
        }

    def get_active_weapon(self):
        """Retorna a arma do slot ativo"""
        if self.active_slot == 1:
            return self.slot_1
        return self.slot_2
    
    def switch_slot(self):
        """Alterna entre os slots"""
        if self.slot_2 is not None:
            self.active_slot = 2 if self.active_slot == 1 else 1
            return True
        return False
    
    def equip_weapon(self, weapon_data, slot):
        """Equipa arma no slot e retorna a antiga"""
        old_weapon = None
        
        if slot == 1:
            old_weapon = self.slot_1
            self.slot_1 = weapon_data
        else:
            old_weapon = self.slot_2
            self.slot_2 = weapon_data
        
        # Se a arma nova tem munição máxima, atualiza
        if weapon_data.get('max_ammo', 0) > 0:
            weapon_data['current_ammo'] = weapon_data['max_ammo']
        
        return old_weapon
    
    def add_ammo(self, weapon_name, amount):
        """Adiciona munição"""
        ammo_type = AMMO_TYPES.get(weapon_name.lower().replace(' ', '_'))
        if ammo_type and ammo_type in self.ammo:
            self.ammo[ammo_type] += amount
            
            # Atualiza munição da arma equipada se for do mesmo tipo
            current = self.get_active_weapon()
            if current and current['name'].lower().replace(' ', '_') == weapon_name.lower().replace(' ', '_'):
                current['current_ammo'] = min(current['max_ammo'], 
                                              current['current_ammo'] + amount)
    
    def reload(self):
        """Recarrega arma atual"""
        weapon = self.get_active_weapon()
        if not weapon or weapon['name'] == "Faquinha":
            return False
        
        ammo_type = AMMO_TYPES.get(weapon['name'].lower().replace(' ', '_'))
        if ammo_type and ammo_type in self.ammo:
            needed = weapon['max_ammo'] - weapon['current_ammo']
            available = min(needed, self.ammo[ammo_type])
            
            if available > 0:
                weapon['current_ammo'] += available
                self.ammo[ammo_type] -= available
                return True
        return False
    
    def can_shoot(self):
        """Verifica se pode atirar"""
        weapon = self.get_active_weapon()
        if not weapon or self.fire_timer > 0:
            return False
        
        if weapon['name'] == "Faquinha":
            return True
        
        return weapon.get('current_ammo', 0) > 0
    
    def shoot(self, target_x, target_y):
        """Dispara e retorna lista de projéteis"""
        weapon = self.get_active_weapon()
        if not weapon or not self.can_shoot():
            return None
        
        bullets = []
        
        dx = target_x - self.x
        dy = target_y - self.y
        length = math.sqrt(dx * dx + dy * dy)
        if length < 0.1:
            return None
        
        dx /= length
        dy /= length
        
        if weapon['name'] != "Faquinha":
            weapon['current_ammo'] -= 1
        
        self.fire_timer = weapon['fire_rate']
        
        config = BULLET_CONFIG.get(weapon['type'], BULLET_CONFIG['rifle'])
        bullet_speed = config['speed']
        
        if weapon['type'] == 'shotgun':
            for i in range(config['count']):
                angle = math.atan2(dy, dx) + (i - config['count']//2) * config['spread']
                bullets.append({
                    'x': self.x, 'y': self.y - 4,
                    'dx': math.cos(angle) * bullet_speed,
                    'dy': math.sin(angle) * bullet_speed,
                    'damage': weapon['damage'],
                    'life': BULLET_RANGE // 2,
                    'type': 'shotgun'
                })
        
        elif weapon['type'] == 'explosive':  # Bazuca
            bullets.append({
                'x': self.x, 'y': self.y - 4,
                'dx': dx * bullet_speed,
                'dy': dy * bullet_speed,
                'damage': weapon['damage'],
                'life': BULLET_RANGE,
                'type': 'explosive',
                'radius': config['radius'],
                'effect': 'rocket_explosion'
            })
        
        elif weapon['type'] == 'fire':  # Coquetel Molotov
            bullets.append({
                'x': self.x, 'y': self.y - 4,
                'dx': dx * bullet_speed,
                'dy': dy * bullet_speed,
                'damage': weapon['damage'],
                'life': BULLET_RANGE,
                'type': 'fire',
                'duration': config['duration'],
                'effect': 'fire_area'
            })
        
        elif weapon['type'] == 'mine':  # Mina Terrestre
            bullets.append({
                'x': self.x + dx * 10, 'y': self.y - 4 + dy * 10,
                'dx': 0, 'dy': 0,
                'damage': weapon['damage'],
                'life': config['arm_time'] + 300,
                'type': 'mine',
                'armed': False,
                'arm_timer': config['arm_time'],
                'effect': 'mine_explosion'
            })
        
        elif weapon['type'] == 'grenade_launcher':  # Lançador de Granadas
            bullets.append({
                'x': self.x, 'y': self.y - 4,
                'dx': dx * bullet_speed,
                'dy': dy * bullet_speed,
                'damage': weapon['damage'],
                'life': BULLET_RANGE,
                'type': 'grenade',
                'radius': config['radius'],
                'effect': 'grenade_explosion'
            })
        
        elif weapon['type'] == 'melee':
            for angle_offset in [-0.2, 0, 0.2]:
                angle = math.atan2(dy, dx) + angle_offset
                bullets.append({
                    'x': self.x + dx * config['range'], 
                    'y': self.y - 4 + dy * config['range'],
                    'dx': math.cos(angle) * bullet_speed,
                    'dy': math.sin(angle) * bullet_speed,
                    'damage': weapon['damage'],
                    'life': 8,
                    'type': 'melee'
                })
        
        else:  # rifle (M4A4)
            bullets.append({
                'x': self.x, 'y': self.y - 4,
                'dx': dx * bullet_speed,
                'dy': dy * bullet_speed,
                'damage': weapon['damage'],
                'life': BULLET_RANGE,
                'type': 'normal'
            })
        
        return bullets

    
    def try_shoot(self, enemies, mouse_pos=None, cam_x=0, cam_y=0):
        """Interface para o engine"""
        if not self.can_shoot():
            return None
        
        # Determina alvo
        if self.combat_mode == COMBAT_AUTO:
            nearest = None
            nearest_dist = float('inf')
            for e in enemies:
                if not e.alive:
                    continue
                dist = math.sqrt((e.x - self.x)**2 + (e.y - self.y)**2)
                if dist < BULLET_RANGE and dist < nearest_dist:
                    nearest = e
                    nearest_dist = dist
            
            if not nearest:
                return None
            
            target_x, target_y = nearest.x, nearest.y
        else:
            # Mira manual
            if mouse_pos:
                target_x = mouse_pos[0] + cam_x
                target_y = mouse_pos[1] + cam_y
            else:
                dirs = {0: (0, 1), 1: (-1, 0), 2: (1, 0), 3: (0, -1)}
                dx, dy = dirs[self.direction]
                target_x = self.x + dx * 50
                target_y = self.y + dy * 50
        
        return self.shoot(target_x, target_y)

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
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length

            if abs(dx) > abs(dy):
                self.direction = 1 if dx < 0 else 2
            else:
                self.direction = 3 if dy < 0 else 0

            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed

            from game.campus_map import get_walkable
            if get_walkable(tilemap, new_x - 4, self.y) and \
               get_walkable(tilemap, new_x + 4, self.y):
                self.x = new_x
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
        
        # Cooldown
        if self.pickup_cooldown > 0:
            self.pickup_cooldown -= 1

    def take_damage(self, amount):
        if self.invincible_timer > 0 or not self.alive:
            return
        actual = max(1, amount - self.armor)
        self.hp -= actual
        self.invincible_timer = 30
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def add_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(XP_BASE * (XP_GROWTH ** self.level))
            return True
        return False

    def apply_upgrade(self, upgrade):
        """Aplica upgrade ao jogador"""
        stat = upgrade['stat']
        val = upgrade['value']
        
        if stat == 'damage':
            # Aplica dano apenas nas armas existentes
            if self.slot_1:
                self.slot_1['damage'] = int(self.slot_1['damage'] * (1 + val))
            if self.slot_2:
                self.slot_2['damage'] = int(self.slot_2['damage'] * (1 + val))
            print(f"[UPGRADE] Dano aumentado em {int(val*100)}%")
            
        elif stat == 'fire_rate':
            # Aplica cadência nas armas existentes
            if self.slot_1:
                self.slot_1['fire_rate'] = max(3, int(self.slot_1['fire_rate'] * (1 - val)))
            if self.slot_2:
                self.slot_2['fire_rate'] = max(3, int(self.slot_2['fire_rate'] * (1 - val)))
            print(f"[UPGRADE] Cadência aumentada em {int(val*100)}%")
            
        elif stat == 'max_hp':
            self.max_hp += int(val)
            self.hp += int(val)
            print(f"[UPGRADE] HP máximo +{int(val)}")
            
        elif stat == 'speed':
            self.speed *= (1 + val)
            print(f"[UPGRADE] Velocidade +{int(val*100)}%")
            
        elif stat == 'pickup_range':
            self.pickup_range *= (1 + val)
            print(f"[UPGRADE] Alcance de coleta +{int(val*100)}%")

    def add_to_inventory(self, item):
        """Adiciona item ao inventário"""
        for i in range(PLAYER_INV_SIZE):
            if self.inventory[i] is None:
                item['count'] = item.get('count', 1)
                self.inventory[i] = item
                return True
        return False

    def use_item(self, slot_index):
        """Usa item do inventário"""
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
        elif t == 'ammo_pack':
            current = self.get_active_weapon()
            if current and current['name'] != "Faquinha":
                self.add_ammo(current['name'], 30)
        else:
            return False

        count = item.get('count', 1)
        if count <= 1:
            self.inventory[slot_index] = None
        else:
            item['count'] = count - 1
        return True

    def drop_item(self, slot_index):
        if 0 <= slot_index < PLAYER_INV_SIZE:
            self.inventory[slot_index] = None

    @property
    def rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2,
                           self.w, self.h)
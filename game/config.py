"""
UNIMA Survivors - Configuration
All game constants and settings.
"""

# ─── Window ───
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60
TITLE = "UNIMA Survivors - Apocalipse Zumbi"
SCALE = 3  # Pixel art scale factor

# ─── Map ───
TILE_SIZE = 16
MAP_WIDTH = 120
MAP_HEIGHT = 90
MAP_PX_W = MAP_WIDTH * TILE_SIZE
MAP_PX_H = MAP_HEIGHT * TILE_SIZE

# Tile IDs
T_GRASS = 0
T_PATH = 1
T_BUILDING = 2
T_WALL = 3
T_PARKING = 4
T_CONCRETE = 5
T_DOOR = 6
T_TREE = 7
T_ROAD = 8

# ─── Player ───
PLAYER_SPEED = 1.8
PLAYER_MAX_HP = 100
PLAYER_PICKUP_RANGE = 25
PLAYER_INV_SIZE = 16

# ─── Combate ───
BULLET_SPEED = 4.5
BULLET_RANGE = 150

# ─── Enemies ───
ENEMY_SPAWN_RATE = 90  # frames between spawns (start)
ENEMY_SPAWN_MIN = 20   # minimum frames between spawns
ENEMY_SPAWN_DIST_MIN = 120
ENEMY_SPAWN_DIST_MAX = 200
MAX_ENEMIES = 120
PHASE3_KILLS = 23

ZOMBIE_COMMON = 0
ZOMBIE_FAST = 1
ZOMBIE_TANK = 2
ZOMBIE_BRUTE = 3

ENEMY_STATS = {
    ZOMBIE_COMMON: {'hp': 20, 'speed': 0.5, 'damage': 8, 'xp': 10, 'name': 'Zumbi'},
    ZOMBIE_FAST:   {'hp': 12, 'speed': 1.0, 'damage': 5, 'xp': 15, 'name': 'Zumbi Veloz'},
    ZOMBIE_TANK:   {'hp': 60, 'speed': 0.3, 'damage': 15, 'xp': 30, 'name': 'Zumbi Tank'},
    ZOMBIE_BRUTE:  {'hp': 80, 'speed': 0.6, 'damage': 18, 'xp': 45, 'name': 'Zumbi Bruto'},
}

# ─── Loot ───
LOOT_TYPES = ['ammo', 'health', 'xp', 'speed', 'damage', 'armor', 'magnet', 'weapon']
# Chance global de algum loot cair quando um inimigo morre.
LOOT_DROP_CHANCE = 0.70
LOOT_WEIGHTS = {
    'xp': 50,
    'health': 30,
    'ammo_pack': 20,
}
LOOT_NAMES = {
    'ammo_pack': 'Pacote de Munição',
    'health': 'Kit Médico',
    'xp': 'Experiência',
    'ammo': 'Munição',
    'weapon': 'Arma',
}
LOOT_DESCRIPTIONS = {
    'ammo_pack': 'Recarrega a arma atual',
    'health': 'Restaura 25 HP',
    'xp': '+XP bônus',
    'ammo_pack': '+60 munição para arma atual',
    'weapon': 'Nova arma',
}
LOOT_STACKABLE = {'ammo', 'health', 'xp'}
# Munição recebida ao encostar no item de munição no mapa.
AMMO_PICKUP_AMOUNT = 60
# Chance extra independente para cada zumbi morto derrubar munição.
AMMO_DROP_CHANCE_ON_KILL = 0.75

# ─── Progression ───
XP_BASE = 80
XP_GROWTH = 1.4
MAX_LEVEL = 30

UPGRADES = [
    {'name': 'Dano+', 'desc': '+15% dano em todas as armas', 'stat': 'damage', 'value': 0.15},
    {'name': 'Cadência+', 'desc': '+12% cadência de tiro', 'stat': 'fire_rate', 'value': 0.12},
    {'name': 'Vida+', 'desc': '+20 HP máximo', 'stat': 'max_hp', 'value': 20},
    {'name': 'Velocidade+', 'desc': '+8% velocidade', 'stat': 'speed', 'value': 0.08},
    {'name': 'Coleta+', 'desc': '+25% alcance', 'stat': 'pickup_range', 'value': 0.25},
    {'name': 'Munição+', 'desc': '+40 munição', 'stat': 'ammo', 'value': 40},
]

# ─── Combat modes ───
COMBAT_AUTO = 0
COMBAT_MANUAL = 1

# ─── Colors (UI) ───
UI_BG = (20, 20, 30)
UI_TEXT = (220, 220, 230)
UI_ACCENT = (80, 180, 120)
UI_RED = (220, 60, 60)
UI_GOLD = (255, 215, 0)
UI_BLUE = (80, 140, 220)
UI_DARK = (15, 15, 20)
UI_PANEL = (30, 30, 45)
UI_BORDER = (60, 65, 80)

# ─── Loot Icons ───
LOOT_ICONS = {
    'health': '❤️',
    'ammo_pack': '📦',
    'ammo_specific': '🔫',
    'weapon': '🔫',
    'xp': '⭐'
}

# ─── Phase Progression ───
PHASE1_KILLS = 0      # Fase inicial
PHASE2_KILLS = 30     # Começa fase 2 após 20 kills (era fase 3)
PHASE3_KILLS = 90     # Começa fase 3 após 60 kills (era fase 4)
PHASE4_KILLS = 150    # Começa fase 4 após 120 kills (era fase 2)
"""
UNIMA Survivors - Sprite Generator
All pixel art sprites are generated programmatically.
"""
import pygame
import math
import random

# ─── Color Palette ───
C_TRANSPARENT = (0, 0, 0, 0)
# Player
C_SKIN = (224, 178, 128)
C_HAIR = (60, 40, 20)
C_SHIRT = (30, 100, 180)
C_PANTS = (50, 50, 70)
C_SHOES = (40, 30, 20)
C_EYE = (30, 30, 30)
# Zombies
C_ZSKIN = (120, 160, 100)
C_ZSKIN2 = (100, 140, 80)
C_ZSKIN3 = (80, 120, 60)
C_ZSHIRT = (100, 70, 60)
C_ZSHIRT2 = (70, 70, 90)
C_ZSHIRT3 = (90, 50, 50)
C_BLOOD = (160, 30, 30)
# Items
C_GOLD = (255, 215, 0)
C_RED = (220, 50, 50)
C_GREEN = (50, 200, 80)
C_BLUE = (50, 120, 220)
C_SILVER = (180, 190, 200)
C_ORANGE = (240, 150, 30)
C_PURPLE = (150, 60, 200)
C_WHITE = (240, 240, 240)
C_DARK = (30, 30, 40)
# Map
C_GRASS = (60, 120, 50)
C_GRASS2 = (50, 110, 45)
C_PATH = (170, 155, 130)
C_BUILDING = (160, 150, 140)
C_BUILDING2 = (140, 130, 120)
C_ROOF = (120, 60, 50)
C_WALL = (130, 125, 115)
C_WINDOW = (140, 180, 220)
C_DOOR = (100, 70, 40)
C_PARKING = (80, 80, 90)
C_LINE = (220, 220, 50)
C_GATE = (70, 70, 80)
C_CONCRETE = (170, 170, 165)


def px(surface, x, y, color):
    """Draw a single pixel safely."""
    if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
        surface.set_at((x, y), color)


def rect(surface, x, y, w, h, color):
    """Draw filled rectangle of pixels."""
    for dy in range(h):
        for dx in range(w):
            px(surface, x + dx, y + dy, color)


def create_player_sprite(direction=0, frame=0):
    """Create 16x16 player sprite. direction: 0=down,1=left,2=right,3=up"""
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    bob = 0 if frame % 2 == 0 else -1

    # Shadow
    for dx in range(6):
        px(s, 5 + dx, 15, (0, 0, 0, 60))

    # Shoes
    rect(s, 5, 13 + bob, 2, 2, C_SHOES)
    rect(s, 9, 13 + bob, 2, 2, C_SHOES)

    # Pants
    rect(s, 5, 11 + bob, 2, 2, C_PANTS)
    rect(s, 9, 11 + bob, 2, 2, C_PANTS)

    # Shirt (body)
    rect(s, 4, 7 + bob, 8, 4, C_SHIRT)
    # Sleeves
    rect(s, 3, 7 + bob, 1, 3, C_SHIRT)
    rect(s, 12, 7 + bob, 1, 3, C_SHIRT)
    # Hands
    px(s, 3, 10 + bob, C_SKIN)
    px(s, 12, 10 + bob, C_SKIN)

    # Head
    rect(s, 5, 2 + bob, 6, 5, C_SKIN)
    # Hair
    rect(s, 5, 1 + bob, 6, 2, C_HAIR)
    px(s, 4, 2 + bob, C_HAIR)
    px(s, 11, 2 + bob, C_HAIR)

    # Face details based on direction
    if direction == 0:  # down
        px(s, 6, 4 + bob, C_EYE)
        px(s, 9, 4 + bob, C_EYE)
    elif direction == 3:  # up
        pass  # back of head
    elif direction == 1:  # left
        px(s, 5, 4 + bob, C_EYE)
    elif direction == 2:  # right
        px(s, 10, 4 + bob, C_EYE)

    return s


def create_zombie_sprite(variant=0, frame=0):
    """Create 16x16 zombie sprite.
    variant: 0=common, 1=fast, 2=tank
    """
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    bob = 0 if frame % 2 == 0 else -1

    skins = [C_ZSKIN, C_ZSKIN2, C_ZSKIN3]
    shirts = [C_ZSHIRT, C_ZSHIRT2, C_ZSHIRT3]
    skin = skins[variant % 3]
    shirt = shirts[variant % 3]

    # Shadow
    for dx in range(6):
        px(s, 5 + dx, 15, (0, 0, 0, 60))

    if variant == 2:  # Tank - bigger
        rect(s, 4, 12 + bob, 3, 3, C_PANTS)
        rect(s, 9, 12 + bob, 3, 3, C_PANTS)
        rect(s, 3, 6 + bob, 10, 6, shirt)
        rect(s, 2, 7 + bob, 1, 4, shirt)
        rect(s, 13, 7 + bob, 1, 4, shirt)
        px(s, 2, 11 + bob, skin)
        px(s, 13, 11 + bob, skin)
        rect(s, 4, 1 + bob, 8, 5, skin)
        rect(s, 4, 0 + bob, 8, 2, (60, 50, 40))
        px(s, 5, 3 + bob, C_RED)
        px(s, 10, 3 + bob, C_RED)
        # Blood stains
        px(s, 6, 8 + bob, C_BLOOD)
        px(s, 9, 9 + bob, C_BLOOD)
    elif variant == 1:  # Fast - thinner
        rect(s, 6, 13 + bob, 1, 2, C_PANTS)
        rect(s, 9, 13 + bob, 1, 2, C_PANTS)
        rect(s, 5, 8 + bob, 6, 5, shirt)
        rect(s, 4, 8 + bob, 1, 3, shirt)
        rect(s, 11, 8 + bob, 1, 3, shirt)
        px(s, 4, 11 + bob, skin)
        px(s, 11, 11 + bob, skin)
        rect(s, 5, 3 + bob, 6, 5, skin)
        rect(s, 5, 2 + bob, 6, 2, (50, 60, 30))
        px(s, 6, 5 + bob, C_RED)
        px(s, 9, 5 + bob, C_RED)
        px(s, 7, 10 + bob, C_BLOOD)
    else:  # Common
        rect(s, 5, 13 + bob, 2, 2, C_PANTS)
        rect(s, 9, 13 + bob, 2, 2, C_PANTS)
        rect(s, 5, 7 + bob, 6, 6, shirt)
        rect(s, 3, 7 + bob, 2, 3, shirt)
        rect(s, 11, 7 + bob, 2, 3, shirt)
        px(s, 3, 10 + bob, skin)
        px(s, 12, 10 + bob, skin)
        rect(s, 5, 2 + bob, 6, 5, skin)
        rect(s, 5, 1 + bob, 6, 2, (70, 50, 40))
        px(s, 6, 4 + bob, C_RED)
        px(s, 9, 4 + bob, C_RED)
        px(s, 7, 5 + bob, C_BLOOD)

    return s


def create_bullet_sprite():
    """Create 4x4 bullet."""
    s = pygame.Surface((4, 4), pygame.SRCALPHA)
    rect(s, 1, 0, 2, 4, C_GOLD)
    rect(s, 0, 1, 4, 2, C_GOLD)
    px(s, 1, 1, (255, 255, 200))
    return s


def create_loot_sprite(loot_type):
    """Create 12x12 loot sprite.
    Types: 'ammo', 'health', 'speed', 'damage', 'armor', 'magnet', 'xp', 'weapon'
    """
    s = pygame.Surface((12, 12), pygame.SRCALPHA)

    if loot_type == 'ammo':
        rect(s, 3, 2, 6, 8, C_GOLD)
        rect(s, 4, 3, 4, 2, (200, 160, 0))
        rect(s, 5, 1, 2, 2, C_SILVER)
    elif loot_type == 'health':
        rect(s, 2, 4, 8, 4, C_RED)
        rect(s, 4, 2, 4, 8, C_RED)
        rect(s, 4, 4, 4, 4, (255, 100, 100))
    elif loot_type == 'speed':
        rect(s, 2, 2, 3, 8, C_BLUE)
        rect(s, 5, 4, 3, 4, C_BLUE)
        rect(s, 8, 6, 2, 2, C_BLUE)
        px(s, 3, 3, (100, 180, 255))
    elif loot_type == 'damage':
        rect(s, 4, 1, 4, 10, C_ORANGE)
        rect(s, 2, 3, 8, 2, C_ORANGE)
        px(s, 5, 2, (255, 200, 100))
    elif loot_type == 'armor':
        rect(s, 3, 2, 6, 8, C_SILVER)
        rect(s, 4, 3, 4, 6, (140, 150, 160))
        rect(s, 5, 2, 2, 1, C_SILVER)
    elif loot_type == 'magnet':
        rect(s, 2, 2, 3, 8, C_RED)
        rect(s, 7, 2, 3, 8, C_BLUE)
        rect(s, 2, 2, 8, 2, C_PURPLE)
    elif loot_type == 'xp':
        s2 = pygame.Surface((12, 12), pygame.SRCALPHA)
        for i in range(5):
            angle = i * 72 - 90
            cx = 6 + int(4 * math.cos(math.radians(angle)))
            cy = 6 + int(4 * math.sin(math.radians(angle)))
            rect(s2, cx - 1, cy - 1, 2, 2, C_GREEN)
        rect(s2, 4, 4, 4, 4, (100, 255, 150))
        return s2
    elif loot_type == 'weapon':
        rect(s, 1, 5, 10, 2, C_DARK)
        rect(s, 2, 3, 3, 4, C_DARK)
        rect(s, 8, 4, 2, 1, C_GOLD)
        px(s, 11, 5, (255, 200, 50))

    return s


def create_explosion_sprite(frame):
    """Create explosion effect 16x16, 4 frames."""
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    colors = [
        (255, 255, 100, 200),
        (255, 200, 50, 180),
        (255, 120, 30, 150),
        (200, 50, 20, 100)
    ]
    r = 3 + frame * 2
    alpha = max(50, 200 - frame * 50)
    color = colors[min(frame, 3)]
    center = 8
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                px(s, center + dx, center + dy, color)
    return s


def create_damage_number_font():
    """Return dict of small 5x5 digit surfaces."""
    digits = {}
    patterns = {
        '0': ["011", "101", "101", "101", "110"],
        '1': ["010", "110", "010", "010", "111"],
        '2': ["110", "001", "010", "100", "111"],
        '3': ["110", "001", "010", "001", "110"],
        '4': ["101", "101", "111", "001", "001"],
        '5': ["111", "100", "110", "001", "110"],
        '6': ["011", "100", "110", "101", "010"],
        '7': ["111", "001", "010", "010", "010"],
        '8': ["010", "101", "010", "101", "010"],
        '9': ["010", "101", "011", "001", "110"],
    }
    for ch, rows in patterns.items():
        surf = pygame.Surface((3, 5), pygame.SRCALPHA)
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if c == '1':
                    px(surf, x, y, C_WHITE)
        digits[ch] = surf
    return digits


def create_cursor_sprite():
    """Create a small crosshair cursor 12x12."""
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    # Cross
    for i in range(12):
        if 4 <= i <= 7:
            continue
        px(s, 6, i, C_WHITE)
        px(s, i, 6, C_WHITE)
    # Center dot
    px(s, 6, 6, C_RED)
    return s


def generate_tile_grass(variant=0):
    """Generate 16x16 grass tile."""
    s = pygame.Surface((16, 16))
    s.fill(C_GRASS)
    random.seed(variant * 42)
    for _ in range(8):
        gx = random.randint(0, 15)
        gy = random.randint(0, 15)
        c = C_GRASS2 if random.random() > 0.5 else (70, 130, 55)
        px(s, gx, gy, c)
    return s


def generate_tile_path():
    """Generate 16x16 path tile."""
    s = pygame.Surface((16, 16))
    s.fill(C_PATH)
    random.seed(100)
    for _ in range(6):
        px(s, random.randint(0, 15), random.randint(0, 15), (160, 145, 120))
    return s


def generate_tile_building():
    """Generate 16x16 building floor tile."""
    s = pygame.Surface((16, 16))
    s.fill(C_BUILDING)
    # Grid lines (tile pattern)
    for i in range(0, 16, 8):
        for j in range(16):
            px(s, i, j, C_BUILDING2)
            px(s, j, i, C_BUILDING2)
    # Slight highlight
    for x in range(1, 7):
        for y in range(1, 7):
            px(s, x, y, (165, 155, 145))
    return s


def generate_tile_wall():
    """Generate 16x16 wall tile (collision)."""
    s = pygame.Surface((16, 16))
    s.fill(C_WALL)
    # Top/bottom edges
    for x in range(16):
        px(s, x, 0, (100, 95, 85))
        px(s, x, 15, (100, 95, 85))
    for y in range(16):
        px(s, 0, y, (100, 95, 85))
        px(s, 15, y, (100, 95, 85))
    # Brick pattern
    for y in range(2, 14, 4):
        offset = 0 if (y // 4) % 2 == 0 else 4
        for x in range(offset, 16, 8):
            if 0 <= x < 16:
                px(s, x, y, C_BUILDING2)
                px(s, x, y + 1, C_BUILDING2)
    # Small window accent in center
    rect(s, 5, 4, 6, 4, C_WINDOW)
    rect(s, 6, 5, 4, 2, (160, 200, 240))
    # Window frame
    px(s, 7, 4, (80, 80, 90))
    px(s, 8, 4, (80, 80, 90))
    return s


def generate_tile_parking():
    """Generate 16x16 parking tile."""
    s = pygame.Surface((16, 16))
    s.fill(C_PARKING)
    # Parking line
    for y in range(0, 16, 2):
        px(s, 15, y, C_LINE)
    return s


def generate_tile_concrete():
    """16x16 concrete/sidewalk."""
    s = pygame.Surface((16, 16))
    s.fill(C_CONCRETE)
    random.seed(200)
    for _ in range(4):
        px(s, random.randint(0, 15), random.randint(0, 15), (160, 160, 155))
    return s


def generate_ui_panel(w, h, alpha=200):
    """Create semi-transparent UI panel."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((20, 20, 30, alpha))
    # Border
    for x in range(w):
        px(s, x, 0, (80, 80, 100))
        px(s, x, h - 1, (80, 80, 100))
    for y in range(h):
        px(s, 0, y, (80, 80, 100))
        px(s, w - 1, y, (80, 80, 100))
    return s


def generate_inventory_slot(selected=False):
    """Create 32x32 inventory slot."""
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    color = (100, 120, 180) if selected else (60, 60, 80)
    bg = (30, 35, 50, 220) if not selected else (40, 50, 80, 240)
    s.fill(bg)
    for x in range(32):
        px(s, x, 0, color)
        px(s, x, 31, color)
    for y in range(32):
        px(s, 0, y, color)
        px(s, 31, y, color)
    return s


def create_menu_bg(w, h):
    """Create the main menu background."""
    s = pygame.Surface((w, h))
    # Dark gradient
    for y in range(h):
        r = max(0, 20 - y // 30)
        g = max(0, 30 - y // 25)
        b = max(0, 50 - y // 20)
        pygame.draw.line(s, (r, g, b), (0, y), (w, y))
    # Some atmospheric elements
    random.seed(999)
    for _ in range(40):
        bx = random.randint(0, w)
        by = random.randint(0, h)
        bw = random.randint(20, 80)
        bh = random.randint(30, 100)
        pygame.draw.rect(s, (15, 15, 25), (bx, by, bw, bh))
    # Blood splatters
    for _ in range(15):
        bx = random.randint(0, w)
        by = random.randint(0, h)
        br = random.randint(5, 20)
        pygame.draw.circle(s, (80, 10, 10), (bx, by), br)
    return s


def create_gameover_overlay(w, h):
    """Create game over darkened overlay."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    return s

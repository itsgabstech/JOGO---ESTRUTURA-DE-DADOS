"""
UNIMA Survivors - Campus Map Generator
Creates a tilemap based on the real UNIMA/Afya Maceió campus.

Layout reference (from aerial image):
  - R. Capim Santo road runs along the bottom
  - Large central parking lot with P marker
  - Left side: Clínica Odontológica, NPJ
  - Right side: Blocos de Estudos B, C, D
  - Quadra Esportiva (far right)
  - Afya Maceió (right center)
  - Biblioteca Central - UNIMA | AFYA
  - Praça de Alimentação, Planeta Lanches, Café Mania
  - Segurança do Campus
  - Trees scattered throughout
"""
import random
from game.config import *


# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────

def _fill_rect(m, x, y, w, h, tile):
    """Fill a rectangular area with a tile."""
    for row in range(y, min(y + h, MAP_HEIGHT)):
        for col in range(x, min(x + w, MAP_WIDTH)):
            m[row][col] = tile


def _place_building(m, bx, by, bw, bh):
    """Place a building with walls, interior, and a door at the bottom center."""
    for y in range(by, by + bh):
        for x in range(bx, bx + bw):
            if y < 0 or y >= MAP_HEIGHT or x < 0 or x >= MAP_WIDTH:
                continue
            if y == by or y == by + bh - 1 or x == bx or x == bx + bw - 1:
                m[y][x] = T_WALL
            else:
                m[y][x] = T_BUILDING
    # Door (bottom center)
    dx = bx + bw // 2
    if 0 <= by + bh - 1 < MAP_HEIGHT:
        if 0 <= dx < MAP_WIDTH:
            m[by + bh - 1][dx] = T_DOOR
        if 0 <= dx + 1 < MAP_WIDTH:
            m[by + bh - 1][dx + 1] = T_DOOR


def _place_trees_row(m, x_start, y, count, spacing=2):
    """Place a row of trees."""
    for i in range(count):
        tx = x_start + i * spacing
        if 0 <= tx < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            m[y][tx] = T_TREE


def _place_trees_col(m, x, y_start, count, spacing=2):
    """Place a column of trees."""
    for i in range(count):
        ty = y_start + i * spacing
        if 0 <= x < MAP_WIDTH and 0 <= ty < MAP_HEIGHT:
            m[ty][x] = T_TREE


def _scatter_trees(m, x, y, w, h, density=0.2, seed=0):
    """Scatter trees randomly in an area."""
    random.seed(seed)
    for row in range(y, min(y + h, MAP_HEIGHT)):
        for col in range(x, min(x + w, MAP_WIDTH)):
            if m[row][col] == T_GRASS and random.random() < density:
                m[row][col] = T_TREE


# ─────────────────────────────────────────────
# Main map generator
# ─────────────────────────────────────────────

def generate_campus_map():
    """Generate the campus tilemap (MAP_WIDTH x MAP_HEIGHT).
    Based on the real UNIMA/Afya Maceió campus aerial view.
    Returns a 2D list of tile IDs and the buildings list.
    """
    m = [[T_GRASS for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

    # ═══════════════════════════════════════════
    # 1. R. CAPIM SANTO — Main road at the bottom
    # ═══════════════════════════════════════════
    # Road runs horizontally across the bottom portion
    road_y = MAP_HEIGHT - 12  # y = 78
    _fill_rect(m, 0, road_y, MAP_WIDTH, 5, T_ROAD)

    # Sidewalks along the road
    _fill_rect(m, 0, road_y - 1, MAP_WIDTH, 1, T_CONCRETE)
    _fill_rect(m, 0, road_y + 5, MAP_WIDTH, 1, T_CONCRETE)

    # ═══════════════════════════════════════════
    # 2. LARGE CENTRAL PARKING LOT
    # ═══════════════════════════════════════════
    # The parking is the dominant feature in the center of the campus
    parking_x = 25
    parking_y = 18
    parking_w = 40
    parking_h = 38
    _fill_rect(m, parking_x, parking_y, parking_w, parking_h, T_PARKING)

    # Internal parking lane markings (paths through parking)
    for row in range(parking_y + 4, parking_y + parking_h - 4, 8):
        _fill_rect(m, parking_x, row, parking_w, 2, T_CONCRETE)

    # Entrance/exit paths from parking to road
    _fill_rect(m, 40, parking_y + parking_h, 6, road_y - (parking_y + parking_h), T_PATH)

    # ═══════════════════════════════════════════
    # 3. BUILDINGS — based on the image layout
    # ═══════════════════════════════════════════
    buildings = [
        # ── LEFT SIDE (top to bottom) ──

        # Clínica Odontológica — top left, larger building
        (4, 6, 14, 12, "Clínica Odontológica"),

        # Núcleo de Práticas Jurídicas (NPJ) — below and slightly right
        (12, 22, 12, 9, "NPJ - Núcleo de Práticas Jurídicas"),

        # ── RIGHT SIDE (top, study blocks) ──

        # Bloco de Estudos B — upper right area
        (72, 5, 14, 12, "Bloco de Estudos B"),

        # Bloco de Estudos C — right of B
        (88, 5, 14, 12, "Bloco de Estudos C"),

        # Bloco de Estudos D — far upper right
        (104, 2, 12, 10, "Bloco de Estudos D"),

        # ── RIGHT SIDE (middle) ──

        # Afya Maceió — right center, main campus building
        (92, 24, 16, 14, "Afya Maceió"),

        # Quadra Esportiva — far right
        (110, 20, 8, 18, "Quadra Esportiva"),

        # ── RIGHT SIDE (lower) ──

        # Biblioteca Central — UNIMA | AFYA
        (74, 42, 16, 10, "Biblioteca Central - UNIMA | AFYA"),

        # Praça de Alimentação — below/right of biblioteca
        (92, 44, 14, 8, "Praça de Alimentação"),

        # Planeta Lanches — lower right
        (80, 58, 10, 7, "Planeta Lanches"),

        # Café Mania — lower far right
        (96, 60, 10, 7, "Café Mania"),

        # Segurança do Campus — far lower right
        (108, 56, 10, 8, "Segurança do Campus"),
    ]

    for bx, by, bw, bh, name in buildings:
        _place_building(m, bx, by, bw, bh)

    # ═══════════════════════════════════════════
    # 4. PATHS & SIDEWALKS — connecting everything
    # ═══════════════════════════════════════════

    # Main campus path — horizontal, connecting left to right buildings
    _fill_rect(m, 4, 35, 116, 3, T_PATH)

    # Path from Clínica down to main path
    _fill_rect(m, 10, 18, 3, 17, T_PATH)

    # Path from NPJ down to main path
    _fill_rect(m, 16, 31, 3, 4, T_PATH)

    # Path along the right building cluster — vertical
    _fill_rect(m, 70, 5, 3, 73, T_PATH)

    # Secondary horizontal path connecting study blocks
    _fill_rect(m, 72, 18, 46, 3, T_PATH)

    # Path from Biblioteca down to road area
    _fill_rect(m, 82, 52, 3, 26, T_PATH)

    # Concrete plaza in front of Biblioteca
    _fill_rect(m, 74, 52, 16, 4, T_CONCRETE)

    # Concrete plaza — Praça de Alimentação area
    _fill_rect(m, 92, 52, 14, 5, T_CONCRETE)

    # Path from main horizontal path to parking
    _fill_rect(m, 24, 35, 1, 3, T_PATH)
    _fill_rect(m, 64, 35, 6, 3, T_PATH)

    # Sidewalk around parking
    _fill_rect(m, parking_x - 1, parking_y - 1, parking_w + 2, 1, T_CONCRETE)
    _fill_rect(m, parking_x - 1, parking_y + parking_h, parking_w + 2, 1, T_CONCRETE)
    _fill_rect(m, parking_x - 1, parking_y, 1, parking_h, T_CONCRETE)
    _fill_rect(m, parking_x + parking_w, parking_y, 1, parking_h, T_CONCRETE)

    # Entrance path from road up to campus
    _fill_rect(m, 50, 56, 4, road_y - 56, T_PATH)

    # Path connecting left side to lower right
    _fill_rect(m, 4, 65, 66, 2, T_PATH)

    # ═══════════════════════════════════════════
    # 5. TREES & GREEN AREAS
    # ═══════════════════════════════════════════

    # Trees along the top border
    _place_trees_row(m, 2, 2, 8, spacing=3)
    _place_trees_row(m, 2, 4, 6, spacing=4)

    # Trees between Clínica and NPJ
    _scatter_trees(m, 2, 18, 8, 6, density=0.3, seed=10)

    # Trees along the left edge
    _scatter_trees(m, 1, 38, 6, 25, density=0.25, seed=20)

    # Trees along R. Capim Santo (both sides)
    _place_trees_row(m, 2, road_y - 3, 15, spacing=5)
    _place_trees_row(m, 20, road_y + 7, 12, spacing=6)

    # Trees in the green area between parking and buildings (top)
    _scatter_trees(m, 30, 5, 30, 12, density=0.15, seed=30)

    # Trees between parking and right buildings
    _scatter_trees(m, 66, 8, 4, 26, density=0.25, seed=40)

    # Trees around Quadra Esportiva
    _place_trees_col(m, 109, 22, 6, spacing=3)

    # Trees around study blocks (decorative)
    _place_trees_row(m, 74, 3, 5, spacing=4)
    _place_trees_row(m, 90, 3, 4, spacing=3)

    # Trees in lower green areas
    _scatter_trees(m, 2, 68, 20, 8, density=0.2, seed=50)
    _scatter_trees(m, 95, 68, 15, 8, density=0.15, seed=60)

    # Trees along main campus path (decorative)
    _place_trees_row(m, 20, 33, 6, spacing=8)
    _place_trees_row(m, 20, 38, 6, spacing=8)

    # ═══════════════════════════════════════════
    # 6. BOUNDARY WALLS
    # ═══════════════════════════════════════════
    for x in range(MAP_WIDTH):
        m[0][x] = T_WALL
        m[MAP_HEIGHT - 1][x] = T_WALL
    for y in range(MAP_HEIGHT):
        m[y][0] = T_WALL
        m[y][MAP_WIDTH - 1] = T_WALL

    # Campus wall/fence along the road side (bottom campus boundary)
    # Leave an opening for the entrance
    for x in range(1, MAP_WIDTH - 1):
        if not (47 <= x <= 55):  # entrance gap
            m[road_y - 2][x] = T_WALL

    # ═══════════════════════════════════════════
    # 7. ENTRANCE GATE
    # ═══════════════════════════════════════════
    # Gate opening in the campus wall
    m[road_y - 2][47] = T_DOOR
    m[road_y - 2][48] = T_DOOR
    m[road_y - 2][54] = T_DOOR
    m[road_y - 2][55] = T_DOOR

    return m, buildings


def get_spawn_points(tilemap):
    """Get valid spawn points for the player (on paths or concrete)."""
    points = []
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if tilemap[y][x] in (T_PATH, T_CONCRETE):
                points.append((x * TILE_SIZE + TILE_SIZE // 2,
                               y * TILE_SIZE + TILE_SIZE // 2))
    return points


def get_walkable(tilemap, px, py):
    """Check if pixel position is walkable."""
    tx = int(px) // TILE_SIZE
    ty = int(py) // TILE_SIZE
    if tx < 0 or tx >= MAP_WIDTH or ty < 0 or ty >= MAP_HEIGHT:
        return False
    tile = tilemap[ty][tx]
    return tile not in (T_WALL, T_TREE)


def get_tile_at(tilemap, px, py):
    """Get tile type at pixel position."""
    tx = int(px) // TILE_SIZE
    ty = int(py) // TILE_SIZE
    if tx < 0 or tx >= MAP_WIDTH or ty < 0 or ty >= MAP_HEIGHT:
        return T_WALL
    return tilemap[ty][tx]

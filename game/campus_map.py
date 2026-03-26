"""
UNIMA Survivors - Campus Map Generator
Creates a university campus-inspired tilemap.
Layout: generic Brazilian university campus with buildings, courtyards, parking, paths.
"""
import random
from game.config import *


def generate_campus_map():
    """Generate the campus tilemap (MAP_WIDTH x MAP_HEIGHT).
    Returns a 2D list of tile IDs.
    """
    m = [[T_GRASS for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

    # ─── Main pathways ───
    # Horizontal main avenue
    for x in range(10, MAP_WIDTH - 10):
        for y in range(42, 48):
            m[y][x] = T_PATH

    # Vertical main avenue
    for y in range(8, MAP_HEIGHT - 8):
        for x in range(58, 64):
            m[y][x] = T_PATH

    # Secondary paths
    for x in range(20, 50):
        for y in range(25, 28):
            m[y][x] = T_PATH
    for x in range(70, 100):
        for y in range(25, 28):
            m[y][x] = T_PATH
    for x in range(20, 50):
        for y in range(62, 65):
            m[y][x] = T_PATH
    for x in range(70, 100):
        for y in range(62, 65):
            m[y][x] = T_PATH

    # Vertical connectors
    for y in range(25, 45):
        for x in range(28, 31):
            m[y][x] = T_PATH
    for y in range(25, 45):
        for x in range(88, 91):
            m[y][x] = T_PATH
    for y in range(48, 65):
        for x in range(28, 31):
            m[y][x] = T_PATH
    for y in range(48, 65):
        for x in range(88, 91):
            m[y][x] = T_PATH

    # ─── Buildings ───
    buildings = [
        # (x, y, w, h, name)
        (14, 12, 12, 10, "Bloco A - Saúde"),
        (34, 12, 14, 10, "Bloco B - Engenharias"),
        (70, 12, 12, 10, "Bloco C - Humanas"),
        (92, 12, 14, 10, "Biblioteca"),
        (14, 50, 10, 10, "Laboratórios"),
        (34, 50, 14, 8, "Bloco D - Admin"),
        (70, 50, 12, 10, "Auditório"),
        (92, 50, 14, 10, "Cantina"),
        (14, 70, 12, 8, "Bloco E"),
        (70, 70, 12, 8, "Ginásio"),
        (92, 70, 14, 8, "Bloco F"),
        (40, 70, 16, 8, "Centro Acadêmico"),
    ]

    for bx, by, bw, bh, name in buildings:
        # Walls (outer ring)
        for y in range(by, by + bh):
            for x in range(bx, bx + bw):
                if y == by or y == by + bh - 1 or x == bx or x == bx + bw - 1:
                    m[y][x] = T_WALL
                else:
                    m[y][x] = T_BUILDING

        # Door (bottom center)
        dx = bx + bw // 2
        m[by + bh - 1][dx] = T_DOOR
        m[by + bh - 1][dx + 1] = T_DOOR

    # ─── Parking lots ───
    parking_areas = [
        (5, 35, 8, 7),
        (105, 35, 10, 7),
        (5, 55, 8, 7),
        (105, 55, 10, 7),
    ]
    for px_, py, pw, ph in parking_areas:
        for y in range(py, py + ph):
            for x in range(px_, px_ + pw):
                m[y][x] = T_PARKING

    # ─── Courtyards (concrete areas) ───
    courtyards = [
        (50, 30, 8, 8),
        (50, 52, 8, 8),
        (80, 30, 6, 6),
        (80, 55, 6, 6),
    ]
    for cx, cy, cw, ch in courtyards:
        for y in range(cy, cy + ch):
            for x in range(cx, cx + cw):
                m[y][x] = T_CONCRETE

    # ─── Entrance gate area ───
    for x in range(55, 67):
        for y in range(MAP_HEIGHT - 6, MAP_HEIGHT - 2):
            m[y][x] = T_CONCRETE
    for x in range(55, 67):
        m[MAP_HEIGHT - 6][x] = T_WALL
    m[MAP_HEIGHT - 6][60] = T_DOOR
    m[MAP_HEIGHT - 6][61] = T_DOOR

    # ─── Boundary walls ───
    for x in range(MAP_WIDTH):
        m[0][x] = T_WALL
        m[MAP_HEIGHT - 1][x] = T_WALL
    for y in range(MAP_HEIGHT):
        m[y][0] = T_WALL
        m[y][MAP_WIDTH - 1] = T_WALL

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
    return tile != T_WALL


def get_tile_at(tilemap, px, py):
    """Get tile type at pixel position."""
    tx = int(px) // TILE_SIZE
    ty = int(py) // TILE_SIZE
    if tx < 0 or tx >= MAP_WIDTH or ty < 0 or ty >= MAP_HEIGHT:
        return T_WALL
    return tilemap[ty][tx]

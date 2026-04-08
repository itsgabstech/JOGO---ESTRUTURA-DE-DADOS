"""Dados de todas as armas do jogo"""

WEAPONS_DATA = {
    # Armas do Slot 1 (Primárias)
    "faquinha": {
        "name": "Faquinha",
        "type": "melee",
        "damage": 25,
        "fire_rate": 15,
        "max_ammo": 0,
        "current_ammo": 0,
        "slot": 1,
        "icon": "🗡️",
        "desc": "Arma inicial corpo a corpo"
    },
    "espingarda": {
        "name": "Espingarda",
        "type": "shotgun",
        "damage": 40,
        "fire_rate": 30,
        "max_ammo": 8,
        "current_ammo": 8,
        "slot": 1,
        "icon": "🔫",
        "desc": "Dispara múltiplos projéteis"
    },
    "m4a4": {
        "name": "M4A4",
        "type": "rifle",
        "damage": 25,
        "fire_rate": 8,
        "max_ammo": 30,
        "current_ammo": 30,
        "slot": 1,
        "icon": "🔫",
        "desc": "Alta cadência de tiro"
    },
    "bazuca": {
        "name": "Bazuca",
        "type": "explosive",
        "damage": 100,
        "fire_rate": 60,
        "max_ammo": 3,
        "current_ammo": 3,
        "slot": 1,
        "icon": "💥",
        "desc": "Dano em área massivo"
    },
    
    # Armas do Slot 2 (Táticas/Explosivas)
    "coquetel_molotov": {
        "name": "Coquetel Molotov",
        "type": "fire",
        "damage": 60,
        "fire_rate": 45,
        "max_ammo": 5,
        "current_ammo": 5,
        "slot": 2,
        "icon": "🔥",
        "desc": "Cria área de fogo"
    },
    "mina_terrestre": {
        "name": "Mina Terrestre",
        "type": "mine",
        "damage": 80,
        "fire_rate": 60,
        "max_ammo": 3,
        "current_ammo": 3,
        "slot": 2,
        "icon": "💣",
        "desc": "Explode quando inimigo se aproxima"
    },
    "lancador_granadas": {
        "name": "Lançador de Granadas",
        "type": "grenade_launcher",
        "damage": 70,
        "fire_rate": 40,
        "max_ammo": 6,
        "current_ammo": 6,
        "slot": 2,
        "icon": "🧨",
        "desc": "Dispara granadas que explodem"
    }
}

# Munições para cada tipo de arma
AMMO_TYPES = {
    "espingarda": "shells",
    "m4a4": "rifle_ammo",
    "bazuca": "rockets",
    "coquetel_molotov": "molotovs",
    "mina_terrestre": "mines",
    "lancador_granadas": "grenades"
}

# Configurações de projéteis
BULLET_CONFIG = {
    "shotgun": {"speed": 8, "spread": 0.15, "count": 5},
    "rifle": {"speed": 12, "spread": 0.05, "count": 1},
    "explosive": {"speed": 6, "radius": 30, "count": 1},
    "fire": {"speed": 5, "duration": 60, "count": 1},
    "mine": {"speed": 0, "arm_time": 30, "count": 1},
    "melee": {"speed": 3, "range": 12, "count": 1},
    "grenade_launcher": {"speed": 7, "radius": 35, "count": 1}
}

AMMO_ICONS = {
    'shells': '💥',
    'rifle_ammo': '🔫',
    'rockets': '🚀',
    'molotovs': '🔥',
    'mines': '💣',
    'grenades': '🧨'
}
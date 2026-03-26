"""
UNIMA Survivors - HUD & UI
Handles all interface drawing: HUD, menus, inventory, game over.
"""
import pygame
import math
from game.config import *
from assets.sprites import (
    generate_ui_panel, generate_inventory_slot,
    create_loot_sprite, create_menu_bg, create_gameover_overlay
)


class UI:
    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.font = None
        self.font_sm = None
        self.font_lg = None
        self.font_title = None
        self._init_fonts()

        # Pre-render some UI elements
        self.hud_panel = generate_ui_panel(220, 120, 180)
        self.inv_slot = generate_inventory_slot(False)
        self.inv_slot_sel = generate_inventory_slot(True)
        self.menu_bg = create_menu_bg(screen_w, screen_h)
        self.gameover_overlay = create_gameover_overlay(screen_w, screen_h)

        # Loot sprites cache
        self.loot_sprites = {}
        for lt in LOOT_TYPES:
            self.loot_sprites[lt] = create_loot_sprite(lt)
            self.loot_sprites[lt] = pygame.transform.scale(
                self.loot_sprites[lt], (24, 24))

    def _init_fonts(self):
        pygame.font.init()
        self.font = pygame.font.SysFont('consolas', 14)
        self.font_sm = pygame.font.SysFont('consolas', 11)
        self.font_lg = pygame.font.SysFont('consolas', 18)
        self.font_title = pygame.font.SysFont('consolas', 42, bold=True)
        self.font_subtitle = pygame.font.SysFont('consolas', 20)
        self.font_menu = pygame.font.SysFont('consolas', 22)

    def draw_hud(self, surface, player, game_time, enemy_count):
        """Draw in-game HUD."""
        # ── Top-left: HP, Ammo, Level ──
        panel = generate_ui_panel(200, 100, 190)
        surface.blit(panel, (8, 8))

        # HP bar
        self._draw_bar(surface, 16, 16, 140, 12, player.hp, player.max_hp,
                       UI_RED, (60, 15, 15), "HP")

        # XP bar
        self._draw_bar(surface, 16, 34, 140, 8, player.xp, player.xp_to_next,
                       UI_ACCENT, (20, 50, 30), "XP")

        # Ammo
        ammo_text = self.font.render(f"Munição: {player.ammo}", True, UI_GOLD)
        surface.blit(ammo_text, (16, 48))

        # Level
        lvl_text = self.font.render(f"Nível {player.level}", True, UI_ACCENT)
        surface.blit(lvl_text, (16, 66))

        # Weapon
        wpn_text = self.font_sm.render(
            f"Arma Nv.{player.weapon_level} | DMG:{player.damage}", True, UI_TEXT)
        surface.blit(wpn_text, (16, 84))

        # ── Top-right: Timer, Kills ──
        panel2 = generate_ui_panel(160, 56, 190)
        surface.blit(panel2, (self.sw - 168, 8))

        minutes = game_time // (60 * 60)
        seconds = (game_time // 60) % 60
        time_text = self.font.render(
            f"Tempo: {minutes:02d}:{seconds:02d}", True, UI_TEXT)
        surface.blit(time_text, (self.sw - 158, 16))

        kills_text = self.font.render(
            f"Abates: {player.kills}", True, UI_RED)
        surface.blit(kills_text, (self.sw - 158, 36))

        # ── Bottom center: combat mode indicator ──
        mode = "AUTO" if player.combat_mode == COMBAT_AUTO else "MANUAL"
        mode_text = self.font_sm.render(f"[TAB] Modo: {mode}", True, UI_BLUE)
        mx = self.sw // 2 - mode_text.get_width() // 2
        surface.blit(mode_text, (mx, self.sh - 24))

        # ── Bottom-left: enemy count ──
        ec_text = self.font_sm.render(f"Zumbis ativos: {enemy_count}", True, UI_RED)
        surface.blit(ec_text, (16, self.sh - 24))

        # ── Bottom-right: Minimap ──
        self._draw_minimap(surface, player, 80, 80)

    def _draw_minimap(self, surface, player, mw, mh):
        """Draw a small minimap in the bottom-right corner."""
        from game.config import MAP_PX_W, MAP_PX_H, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE
        mm = pygame.Surface((mw, mh), pygame.SRCALPHA)
        mm.fill((10, 10, 20, 180))

        # Player position on minimap
        px_ratio = player.x / MAP_PX_W
        py_ratio = player.y / MAP_PX_H
        ppx = int(px_ratio * mw)
        ppy = int(py_ratio * mh)

        # Draw player blip
        pygame.draw.rect(mm, (80, 200, 120), (ppx - 1, ppy - 1, 3, 3))

        # Border
        pygame.draw.rect(mm, UI_BORDER, (0, 0, mw, mh), 1)

        surface.blit(mm, (self.sw - mw - 10, self.sh - mh - 10))

    def _draw_bar(self, surface, x, y, w, h, value, max_value, color, bg_color, label=""):
        """Draw a progress bar."""
        pygame.draw.rect(surface, bg_color, (x, y, w, h))
        if max_value > 0:
            fill_w = int(w * min(1, value / max_value))
            pygame.draw.rect(surface, color, (x, y, fill_w, h))
        pygame.draw.rect(surface, UI_BORDER, (x, y, w, h), 1)
        if label:
            txt = self.font_sm.render(
                f"{label} {int(value)}/{int(max_value)}", True, UI_TEXT)
            surface.blit(txt, (x + 3, y - 1))

    def draw_inventory(self, surface, player):
        """Draw inventory screen overlay."""
        # Background overlay
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # Inventory panel
        panel_w = 340
        panel_h = 320
        px = self.sw // 2 - panel_w // 2
        py = self.sh // 2 - panel_h // 2

        panel = generate_ui_panel(panel_w, panel_h, 230)
        surface.blit(panel, (px, py))

        # Title
        title = self.font_lg.render("INVENTÁRIO", True, UI_GOLD)
        surface.blit(title, (px + panel_w // 2 - title.get_width() // 2, py + 8))

        # Slots grid: 4 columns x 4 rows
        slot_size = 36
        margin = 6
        grid_x = px + (panel_w - 4 * (slot_size + margin)) // 2
        grid_y = py + 40

        for i in range(PLAYER_INV_SIZE):
            row = i // 4
            col = i % 4
            sx = grid_x + col * (slot_size + margin)
            sy = grid_y + row * (slot_size + margin)

            # Draw slot
            slot_surf = self.inv_slot_sel if i == player.selected_slot else self.inv_slot
            scaled_slot = pygame.transform.scale(slot_surf, (slot_size, slot_size))
            surface.blit(scaled_slot, (sx, sy))

            # Draw item if present
            item = player.inventory[i]
            if item:
                loot_img = self.loot_sprites.get(item['type'])
                if loot_img:
                    surface.blit(loot_img, (sx + 6, sy + 6))
                # Count
                count = item.get('count', 1)
                if count > 1:
                    ct = self.font_sm.render(str(count), True, UI_TEXT)
                    surface.blit(ct, (sx + slot_size - ct.get_width() - 2,
                                      sy + slot_size - 12))

        # Selected item info
        sel_item = player.inventory[player.selected_slot]
        if sel_item:
            info_y = grid_y + 4 * (slot_size + margin) + 10
            name_text = self.font.render(sel_item.get('name', ''), True, UI_GOLD)
            surface.blit(name_text, (px + 20, info_y))
            desc_text = self.font_sm.render(sel_item.get('desc', ''), True, UI_TEXT)
            surface.blit(desc_text, (px + 20, info_y + 18))

            # Controls
            ctrl = self.font_sm.render(
                "[E] Usar  [Q] Descartar  [←→↑↓] Navegar", True, UI_BLUE)
            surface.blit(ctrl, (px + 20, info_y + 36))
        else:
            info_y = grid_y + 4 * (slot_size + margin) + 10
            empty = self.font_sm.render("Slot vazio", True, (100, 100, 120))
            surface.blit(empty, (px + 20, info_y))
            ctrl = self.font_sm.render(
                "[I] Fechar inventário", True, UI_BLUE)
            surface.blit(ctrl, (px + 20, info_y + 20))

    def draw_upgrade_choice(self, surface, upgrades, selected):
        """Draw level-up upgrade selection."""
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # Title
        title = self.font_lg.render("LEVEL UP! Escolha um upgrade:", True, UI_GOLD)
        surface.blit(title, (self.sw // 2 - title.get_width() // 2, 100))

        # Options
        for i, upg in enumerate(upgrades):
            bx = self.sw // 2 - 120
            by = 160 + i * 60
            bw, bh = 240, 50

            color = UI_ACCENT if i == selected else UI_BORDER
            bg = (30, 50, 40, 230) if i == selected else (25, 25, 35, 220)

            panel = pygame.Surface((bw, bh), pygame.SRCALPHA)
            panel.fill(bg)
            pygame.draw.rect(panel, color, (0, 0, bw, bh), 2)
            surface.blit(panel, (bx, by))

            name = self.font.render(upg['name'], True, UI_GOLD)
            desc = self.font_sm.render(upg['desc'], True, UI_TEXT)
            surface.blit(name, (bx + 10, by + 6))
            surface.blit(desc, (bx + 10, by + 26))

        hint = self.font_sm.render("[↑↓] Selecionar  [ENTER] Confirmar", True, UI_BLUE)
        surface.blit(hint, (self.sw // 2 - hint.get_width() // 2,
                            160 + len(upgrades) * 60 + 20))

    def draw_menu(self, surface, selected, settings_open=False):
        """Draw main menu."""
        surface.blit(self.menu_bg, (0, 0))

        # Title
        title1 = self.font_title.render("UNIMA", True, UI_RED)
        title2 = self.font_title.render("SURVIVORS", True, UI_GOLD)
        surface.blit(title1, (self.sw // 2 - title1.get_width() // 2, 80))
        surface.blit(title2, (self.sw // 2 - title2.get_width() // 2, 130))

        sub = self.font_subtitle.render("Apocalipse Zumbi na UNIMA Afya", True, UI_TEXT)
        surface.blit(sub, (self.sw // 2 - sub.get_width() // 2, 190))

        if not settings_open:
            options = ["JOGAR", "CONFIGURAÇÕES", "INSTRUÇÕES", "SAIR"]
            for i, opt in enumerate(options):
                color = UI_GOLD if i == selected else UI_TEXT
                txt = self.font_menu.render(opt, True, color)
                tx = self.sw // 2 - txt.get_width() // 2
                ty = 280 + i * 45
                if i == selected:
                    # Selection indicator
                    ind = self.font_menu.render("►", True, UI_RED)
                    surface.blit(ind, (tx - 30, ty))
                surface.blit(txt, (tx, ty))

            ver = self.font_sm.render("v1.0 — Python + Pygame", True, (80, 80, 100))
            surface.blit(ver, (self.sw // 2 - ver.get_width() // 2, self.sh - 30))
        else:
            self._draw_settings(surface, selected)

    def _draw_settings(self, surface, selected):
        """Draw settings sub-menu."""
        panel = generate_ui_panel(350, 250, 220)
        px = self.sw // 2 - 175
        py = 240
        surface.blit(panel, (px, py))

        title = self.font_lg.render("CONFIGURAÇÕES", True, UI_GOLD)
        surface.blit(title, (self.sw // 2 - title.get_width() // 2, py + 10))

        settings = [
            "Modo de Combate: AUTO / MANUAL",
            "Dificuldade: Normal",
            "Voltar"
        ]
        for i, s in enumerate(settings):
            color = UI_GOLD if i == selected else UI_TEXT
            txt = self.font.render(s, True, color)
            surface.blit(txt, (px + 20, py + 50 + i * 35))

    def draw_instructions(self, surface):
        """Draw instructions screen."""
        surface.blit(self.menu_bg, (0, 0))

        title = self.font_lg.render("INSTRUÇÕES", True, UI_GOLD)
        surface.blit(title, (self.sw // 2 - title.get_width() // 2, 60))

        instructions = [
            "WASD / Setas  —  Movimentar",
            "Mouse / Auto   —  Atirar",
            "TAB            —  Alternar modo de tiro",
            "I              —  Abrir/fechar inventário",
            "E              —  Usar item selecionado",
            "Q              —  Descartar item",
            "ESC            —  Pausar / Voltar",
            "",
            "Sobreviva o máximo que puder!",
            "Colete loot, suba de nível, escolha upgrades.",
            "Os zumbis ficam mais fortes com o tempo!",
            "",
            "Campus UNIMA Afya Maceió",
            "— Inspirado em Vampire Survivors —",
        ]

        for i, line in enumerate(instructions):
            color = UI_ACCENT if "—" in line else UI_TEXT
            txt = self.font.render(line, True, color)
            surface.blit(txt, (self.sw // 2 - txt.get_width() // 2, 110 + i * 28))

        back = self.font_sm.render("[ESC] Voltar ao menu", True, UI_BLUE)
        surface.blit(back, (self.sw // 2 - back.get_width() // 2, self.sh - 40))

    def draw_game_over(self, surface, player, game_time):
        """Draw game over screen."""
        surface.blit(self.gameover_overlay, (0, 0))

        title = self.font_title.render("GAME OVER", True, UI_RED)
        surface.blit(title, (self.sw // 2 - title.get_width() // 2, 100))

        minutes = game_time // (60 * 60)
        seconds = (game_time // 60) % 60

        stats = [
            f"Tempo sobrevivido: {minutes:02d}:{seconds:02d}",
            f"Zumbis abatidos: {player.kills}",
            f"Nível alcançado: {player.level}",
            f"Dano total: {player.total_damage_dealt}",
        ]

        for i, s in enumerate(stats):
            txt = self.font_lg.render(s, True, UI_TEXT)
            surface.blit(txt, (self.sw // 2 - txt.get_width() // 2, 200 + i * 35))

        opts = [
            "[ENTER] Jogar novamente",
            "[ESC] Menu principal"
        ]
        for i, o in enumerate(opts):
            txt = self.font.render(o, True, UI_GOLD)
            surface.blit(txt, (self.sw // 2 - txt.get_width() // 2, 380 + i * 30))

    def draw_pause(self, surface):
        """Draw pause overlay."""
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        title = self.font_lg.render("PAUSADO", True, UI_GOLD)
        surface.blit(title, (self.sw // 2 - title.get_width() // 2, self.sh // 2 - 40))

        hint = self.font.render("[ESC] Continuar  [M] Menu principal", True, UI_TEXT)
        surface.blit(hint, (self.sw // 2 - hint.get_width() // 2, self.sh // 2 + 10))

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
from game.weapons_data import AMMO_ICONS


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

    def draw_hud(self, surface, player, game_time, enemy_count, phase, game_ref=None):
        """Draw in-game HUD."""
        panel = generate_ui_panel(200, 100, 190)
        surface.blit(panel, (8, 8))

        # HP bar
        self._draw_bar(surface, 16, 16, 140, 12, player.hp, player.max_hp,
                       UI_RED, (60, 15, 15), "HP")

        # XP bar
        self._draw_bar(surface, 16, 34, 140, 8, player.xp, player.xp_to_next,
                       UI_ACCENT, (20, 50, 30), "XP")

        # Level
        lvl_text = self.font.render(f"Nível {player.level}", True, UI_ACCENT)
        surface.blit(lvl_text, (16, 66))

        # Phase
        phase_text = self.font_sm.render(f"Fase {phase}", True, UI_ACCENT)
        surface.blit(phase_text, (16, 78))

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

        # ── Slots de Armas ──────────────────────────────────────
        from game.weapons_data import AMMO_TYPES

        def _ammo_stock(weapon, player):
            """Retorna estoque total no inventário para a arma."""
            if weapon is None or weapon.get('max_ammo', 0) == 0:
                return None
            key = weapon['name'].lower().replace(' ', '_')
            ammo_type = AMMO_TYPES.get(key)
            if ammo_type:
                return player.ammo.get(ammo_type, 0)
            return None

        # Slot 1
        if player.slot_1:
            w1 = player.slot_1
            if w1['name'] == "Faquinha":
                slot1_text = f"[1] {w1['icon']} {w1['name']}"
            else:
                stock1 = _ammo_stock(w1, player)
                slot1_text = (
                    f"[1] {w1['icon']} {w1['name']} "
                    f"[{w1['current_ammo']}/{w1['max_ammo']}]"
                    + (f" +{stock1}" if stock1 is not None else "")
                )
        else:
            slot1_text = "[1] Vazio"

        slot1_color = UI_GOLD if player.active_slot == 1 else UI_TEXT
        s1_surface = self.font_sm.render(slot1_text, True, slot1_color)

        # Slot 2
        if player.slot_2:
            w2 = player.slot_2
            stock2 = _ammo_stock(w2, player)
            slot2_text = (
                f"[2] {w2['icon']} {w2['name']} "
                f"[{w2['current_ammo']}/{w2['max_ammo']}]"
                + (f" +{stock2}" if stock2 is not None else "")
            )
        else:
            slot2_text = "[2] Vazio (aguardando drop)"

        slot2_color = UI_GOLD if player.active_slot == 2 else UI_TEXT
        s2_surface = self.font_sm.render(slot2_text, True, slot2_color)

        # Desenha os dois slots
        surface.blit(s1_surface, (16, 100))
        surface.blit(s2_surface, (16, 118))

        # Borda no slot ativo
        active_y = 100 if player.active_slot == 1 else 118
        pygame.draw.rect(surface, UI_ACCENT, (12, active_y - 2, 220, 18), 1)

        # Estoque de munição de TODAS as armas
        ammo_panel_x = 16
        ammo_panel_y = self.sh - 90
        all_ammo_lines = []
        for wkey, ammo_type in AMMO_TYPES.items():
            stock = player.ammo.get(ammo_type, 0)
            if stock > 0:
                from game.weapons_data import WEAPONS_DATA
                wname = WEAPONS_DATA.get(wkey, {}).get('name', wkey)
                icon = AMMO_ICONS.get(ammo_type, '📦')
                all_ammo_lines.append(f"{icon} {wname}: {stock}")

        if all_ammo_lines:
            ammo_bg = pygame.Surface((200, len(all_ammo_lines) * 14 + 6), pygame.SRCALPHA)
            ammo_bg.fill((15, 15, 25, 160))
            surface.blit(ammo_bg, (ammo_panel_x - 2, ammo_panel_y - 2))
            for i, line in enumerate(all_ammo_lines):
                txt = self.font_sm.render(line, True, (180, 200, 180))
                surface.blit(txt, (ammo_panel_x, ammo_panel_y + i * 14))

        # Dicas de controles
        controls = self.font_sm.render("[1/2/Q] Trocar arma  [R] Recarregar", True, UI_BLUE)
        surface.blit(controls, (16, self.sh - 40))

        # Dica de inventário
        inv_hint = self.font_sm.render("[I] Inventario", True, UI_BLUE)
        surface.blit(inv_hint, (self.sw - 110, self.sh - 40))

        # Mensagem de arma próxima
        if game_ref and hasattr(game_ref, 'nearby_weapon') and game_ref.nearby_weapon:
            weapon_data = game_ref.nearby_weapon.loot_data.get('data', {})
            weapon_name = weapon_data.get('name', 'Arma')
            msg = f"[Q] Pegar {weapon_name}"
            msg_surface = self.font.render(msg, True, UI_GOLD)
            msg_x = self.sw // 2 - msg_surface.get_width() // 2
            msg_y = self.sh - 60
            surface.blit(msg_surface, (msg_x, msg_y))

        # Dica de interação com NPC
        if game_ref and hasattr(game_ref, 'nearby_npc') and game_ref.nearby_npc:
            dialogue_active = hasattr(game_ref, 'dialogue_box') and game_ref.dialogue_box.active
            if not dialogue_active:
                msg = f"[E] Falar com {game_ref.nearby_npc.name}"
                msg_surface = self.font.render(msg, True, UI_ACCENT)
                msg_x = self.sw // 2 - msg_surface.get_width() // 2
                msg_y = self.sh - 90
                surface.blit(msg_surface, (msg_x, msg_y))

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

    # ── Constantes de layout do inventário (compartilhadas com engine) ───────

    INV_PANEL_W  = 360
    INV_PANEL_H  = 340
    INV_SLOT_SZ  = 36
    INV_MARGIN   = 6

    def _inv_layout(self):
        """Retorna (px, py, grid_x, grid_y) do painel do inventário."""
        px     = self.sw // 2 - self.INV_PANEL_W // 2
        py     = self.sh // 2 - self.INV_PANEL_H // 2
        grid_x = px + (self.INV_PANEL_W - 4 * (self.INV_SLOT_SZ + self.INV_MARGIN)) // 2
        grid_y = py + 36
        return px, py, grid_x, grid_y

    def get_slot_at(self, mouse_pos: tuple) -> 'int | None':
        """
        Retorna o índice do slot sob o cursor do mouse, ou None.

        Usado pelo engine para mapear cliques/solturas de mouse
        a posições da grade durante o drag-and-drop.
        """
        mx, my = mouse_pos
        _, _, grid_x, grid_y = self._inv_layout()
        sz  = self.INV_SLOT_SZ
        mar = self.INV_MARGIN

        for i in range(PLAYER_INV_SIZE):
            row = i // 4
            col = i % 4
            sx  = grid_x + col * (sz + mar)
            sy  = grid_y + row * (sz + mar)
            if sx <= mx < sx + sz and sy <= my < sy + sz:
                return i
        return None

    def draw_inventory(self, surface, player):
        """
        Exibe o inventário do jogador com suporte a drag-and-drop.

        Estruturas envolvidas:
          • HashInventory  → dados dos itens (nome, qtd, tipo)
          • SlotList       → ordem visual dos slots
          • player._get_ordered_slots() combina as duas para renderização

        Feedback visual do drag-and-drop:
          • Slot de origem: borda laranja + ícone semitransparente
          • Slot sob o cursor: borda dourada mais espessa
          • "Fantasma" do item segue o mouse
        """
        # ── Overlay escuro ────────────────────────────────────────────────────
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # ── Painel ────────────────────────────────────────────────────────────
        px, py, grid_x, grid_y = self._inv_layout()
        panel = generate_ui_panel(self.INV_PANEL_W, self.INV_PANEL_H, 230)
        surface.blit(panel, (px, py))

        # ── Título + contador ─────────────────────────────────────────────────
        inv_count = player.inventory.item_count
        inv_max   = player.inventory.max_items
        title_str = f"INVENTÁRIO  ({inv_count}/{inv_max})"
        title = self.font_lg.render(title_str, True, UI_GOLD)
        surface.blit(title, (px + self.INV_PANEL_W // 2 - title.get_width() // 2, py + 8))

        # ── Determina slot sob o mouse (para highlight durante drag) ──────────
        mouse_hover = None
        if player.is_dragging:
            mouse_hover = self.get_slot_at(player.drag_pos)

        # ── Slots: SlotList define a ordem; HashMap fornece os dados ──────────
        slots = player._get_ordered_slots()
        sz    = self.INV_SLOT_SZ
        mar   = self.INV_MARGIN

        for i in range(PLAYER_INV_SIZE):
            row = i // 4
            col = i % 4
            sx  = grid_x + col * (sz + mar)
            sy  = grid_y + row * (sz + mar)

            is_source = player.is_dragging and i == player.drag_source
            is_hover  = player.is_dragging and i == mouse_hover
            is_sel    = (i == player.selected_slot) and not player.is_dragging

            # ─ Fundo do slot ─
            slot_surf   = self.inv_slot_sel if is_sel else self.inv_slot
            scaled_slot = pygame.transform.scale(slot_surf, (sz, sz))
            surface.blit(scaled_slot, (sx, sy))

            # ─ Borda especial durante drag ─
            if is_source:
                pygame.draw.rect(surface, (255, 140, 0), (sx, sy, sz, sz), 2)   # laranja
            elif is_hover:
                pygame.draw.rect(surface, UI_GOLD,       (sx, sy, sz, sz), 3)   # dourado

            item = slots[i]
            if item:
                loot_type = item.get('type', 'ammo_pack')
                loot_img  = self.loot_sprites.get(loot_type)

                if loot_img:
                    if is_source:
                        # Item sendo arrastado: mostra semitransparente no slot de origem
                        ghost = loot_img.copy()
                        ghost.set_alpha(80)
                        surface.blit(ghost, (sx + 6, sy + 6))
                    else:
                        surface.blit(loot_img, (sx + 6, sy + 6))

                qty = item.get('quantity', 1)
                if qty > 1:
                    ct = self.font_sm.render(str(qty), True, UI_TEXT)
                    surface.blit(ct, (sx + sz - ct.get_width() - 2, sy + sz - 12))

        # ── "Fantasma" segue o mouse durante o drag ───────────────────────────
        if player.is_dragging and player.drag_item:
            loot_type = player.drag_item.get('type', 'ammo_pack')
            loot_img  = self.loot_sprites.get(loot_type)
            if loot_img:
                # Ícone ampliado (48×48) centralizado no cursor
                big = pygame.transform.scale(loot_img, (48, 48))
                mx, my = player.drag_pos
                surface.blit(big, (mx - 24, my - 24))

                # Nome do item ao lado do cursor
                drag_name = self.font_sm.render(
                    player.drag_item.get('name', ''), True, UI_GOLD)
                surface.blit(drag_name, (mx + 28, my - 7))

        # ── Painel de informações do item selecionado ─────────────────────────
        info_y = grid_y + 4 * (sz + mar) + 10

        # Durante drag mostra info do item sendo arrastado; senão do selecionado
        if player.is_dragging and player.drag_item:
            info_item = player.drag_item
        else:
            info_item = slots[player.selected_slot]

        if info_item:
            name_text = self.font.render(info_item.get('name', ''), True, UI_GOLD)
            surface.blit(name_text, (px + 16, info_y))

            qty_text = self.font_sm.render(
                f"Quantidade: {info_item.get('quantity', 1)}", True, UI_ACCENT)
            surface.blit(qty_text, (px + 16, info_y + 18))

            desc_text = self.font_sm.render(info_item.get('desc', ''), True, UI_TEXT)
            surface.blit(desc_text, (px + 16, info_y + 32))

            if player.is_dragging:
                hint = self.font_sm.render(
                    "Solte sobre outro slot para mover o item", True, (255, 180, 60))
            else:
                hint = self.font_sm.render(
                    "[E] Usar  [Q] Descartar  [←→↑↓] Navegar  [clique+arraste] Mover",
                    True, UI_BLUE)
            surface.blit(hint, (px + 16, info_y + 50))
        else:
            empty = self.font_sm.render("Slot vazio", True, (100, 100, 120))
            surface.blit(empty, (px + 16, info_y))
            ctrl  = self.font_sm.render(
                "[I] Fechar  |  Clique e arraste para reorganizar", True, UI_BLUE)
            surface.blit(ctrl, (px + 16, info_y + 20))

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
            "1 / 2 / Q      —  Trocar arma",
            "R              —  Recarregar arma atual",
            "I              —  Abrir/fechar inventário",
            "E              —  Falar com NPC / Usar item",
            "ESC            —  Pausar / Voltar",
            "",
            "Sobreviva o máximo que puder!",
            "Zumbis dropam armas e munição!",
            "Cada arma tem seu próprio tipo de munição.",
            "Troque de arma conforme a situação!",
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

    def draw_victory(self, surface, player, game_time):
        """Draw victory screen when boss is defeated."""
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        title1 = self.font_title.render("PARABÉNS!", True, UI_GOLD)
        title2 = self.font_title.render("VOCÊ FOI APROVADO!", True, UI_GOLD)
        
        surface.blit(title1, (self.sw // 2 - title1.get_width() // 2, 80))
        surface.blit(title2, (self.sw // 2 - title2.get_width() // 2, 140))
        
        sub = self.font_lg.render("Professor Vital foi derrotado!", True, UI_ACCENT)
        surface.blit(sub, (self.sw // 2 - sub.get_width() // 2, 200))
        
        minutes = game_time // (60 * 60)
        seconds = (game_time // 60) % 60
        
        stats = [
            f"Tempo sobrevivido: {minutes:02d}:{seconds:02d}",
            f"Zumbis abatidos: {player.kills}",
            f"Nível alcançado: {player.level}",
            f"Dano total: {player.total_damage_dealt}",
        ]
        
        for i, s in enumerate(stats):
            txt = self.font.render(s, True, UI_TEXT)
            surface.blit(txt, (self.sw // 2 - txt.get_width() // 2, 260 + i * 25))
        
        approval = self.font_lg.render("VOCÊ É UM VERDADEIRO SOBREVIVENTE!", True, UI_RED)
        surface.blit(approval, (self.sw // 2 - approval.get_width() // 2, 380))
        
        opts = [
            "[ENTER] Jogar novamente",
            "[ESC] Menu principal"
        ]
        for i, o in enumerate(opts):
            txt = self.font.render(o, True, UI_GOLD)
            surface.blit(txt, (self.sw // 2 - txt.get_width() // 2, 440 + i * 30))
        
        credits = self.font_sm.render("UNIMA Afya - Formando sobreviventes desde 2025", True, (80, 80, 100))
        surface.blit(credits, (self.sw // 2 - credits.get_width() // 2, self.sh - 40))
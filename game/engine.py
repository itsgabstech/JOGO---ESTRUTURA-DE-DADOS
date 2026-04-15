"""
UNIMA Survivors - Game Engine
Main game loop, state management, core logic.
"""
import pygame
import random
import math
from game import player
from game.config import *
from game.player import Player
from game.enemies import Enemy, EnemySpawner, ProfessorVital
from game.campus_map import generate_campus_map, get_spawn_points
from game.loot import LootDrop, roll_loot, try_pickup, try_equip_weapon
from game.effects import EffectsManager
from game.renderer import Renderer
from game.weapons_data import AMMO_TYPES
from ui.hud import UI


# Game states
STATE_MENU = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_INVENTORY = 3
STATE_GAME_OVER = 4
STATE_UPGRADE = 5
STATE_INSTRUCTIONS = 6
STATE_SETTINGS = 7
STATE_PHASE2 = 8


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        # Abrir em tela cheia e manter tamanho atual
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = True
        self.screen_w, self.screen_h = self.screen.get_size()

        # Systems
        self.renderer = Renderer()
        self.ui = UI(self.screen_w, self.screen_h)
        self.effects = EffectsManager()

        # Sound effects (generated procedurally)
        self._init_sounds()

        # State
        self.state = STATE_MENU
        self.menu_selection = 0
        self.settings_selection = 0

        # Game data (initialized on new game)
        self.tilemap = None
        self.buildings = None
        self.player = None
        self.enemies = []
        self.bullets = []
        self.enemy_projectiles = []
        self.loot_drops = []
        self.spawner = None
        self.game_time = 0
        self.nearby_weapon = None
        self.boss_spawned = False
        self.boss_score_threshold = 180

        # Upgrade selection
        self.upgrade_options = []
        self.upgrade_selection = 0

        # Combat mode setting
        self.combat_mode = COMBAT_AUTO

        # Phase progression
        self.phase = 1
        self.phase_message_timer = 0
        self.phase_message_text = ""
        self.phase_message_subtext = ""

        # Hide system cursor during gameplay
        self.custom_cursor = True

    def _init_sounds(self):
        """Generate simple sound effects programmatically."""
        self.sounds = {}
        try:
            import array

            # Shoot sound
            sample_rate = 22050
            duration = 0.08
            n_samples = int(sample_rate * duration)
            buf = array.array('h', [0] * n_samples)
            for i in range(n_samples):
                t = i / sample_rate
                freq = 800 - t * 8000
                val = int(8000 * math.sin(2 * math.pi * freq * t) *
                          (1 - i / n_samples))
                buf[i] = max(-32767, min(32767, val))
            sound = pygame.mixer.Sound(buffer=buf)
            sound.set_volume(0.15)
            self.sounds['shoot'] = sound

            # Hit sound
            duration = 0.06
            n_samples = int(sample_rate * duration)
            buf = array.array('h', [0] * n_samples)
            for i in range(n_samples):
                t = i / sample_rate
                val = int(6000 * math.sin(2 * math.pi * 200 * t) *
                          (1 - i / n_samples))
                val += random.randint(-2000, 2000)
                buf[i] = max(-32767, min(32767, val))
            sound = pygame.mixer.Sound(buffer=buf)
            sound.set_volume(0.1)
            self.sounds['hit'] = sound

            # Pickup sound
            duration = 0.12
            n_samples = int(sample_rate * duration)
            buf = array.array('h', [0] * n_samples)
            for i in range(n_samples):
                t = i / sample_rate
                freq = 600 + t * 3000
                val = int(5000 * math.sin(2 * math.pi * freq * t) *
                          (1 - i / n_samples))
                buf[i] = max(-32767, min(32767, val))
            sound = pygame.mixer.Sound(buffer=buf)
            sound.set_volume(0.12)
            self.sounds['pickup'] = sound

            # Level up sound
            duration = 0.3
            n_samples = int(sample_rate * duration)
            buf = array.array('h', [0] * n_samples)
            for i in range(n_samples):
                t = i / sample_rate
                freq = 400 + t * 1200
                val = int(6000 * math.sin(2 * math.pi * freq * t) *
                          (1 - i / n_samples) ** 0.5)
                buf[i] = max(-32767, min(32767, val))
            sound = pygame.mixer.Sound(buffer=buf)
            sound.set_volume(0.15)
            self.sounds['levelup'] = sound

            # Death sound
            duration = 0.5
            n_samples = int(sample_rate * duration)
            buf = array.array('h', [0] * n_samples)
            for i in range(n_samples):
                t = i / sample_rate
                freq = 300 - t * 500
                val = int(8000 * math.sin(2 * math.pi * max(20, freq) * t) *
                          (1 - i / n_samples))
                val += random.randint(-3000, 3000) * int((1 - i / n_samples))
                buf[i] = max(-32767, min(32767, val))
            sound = pygame.mixer.Sound(buffer=buf)
            sound.set_volume(0.15)
            self.sounds['death'] = sound

        except Exception:
            pass  # Sounds are optional

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def new_game(self):
        """Start a new game."""
        self.tilemap, self.buildings = generate_campus_map()
        spawn_points = get_spawn_points(self.tilemap)

        # Player starts at campus center
        center_points = [p for p in spawn_points
                         if abs(p[0] - MAP_PX_W // 2) < 100 and
                         abs(p[1] - MAP_PX_H // 2) < 100]
        if center_points:
            sx, sy = random.choice(center_points)
        else:
            sx, sy = MAP_PX_W // 2, MAP_PX_H // 2

        self.player = Player(sx, sy)
        self.player.combat_mode = self.combat_mode
        self.enemies = []
        self.bullets = []
        self.enemy_projectiles = []
        self.loot_drops = []
        self.spawner = EnemySpawner()
        self.effects = EffectsManager()
        self.game_time = 0
        self.boss_spawned = False
        self.phase = 1
        self.phase_message_timer = 0
        self.phase_message_text = ""
        self.phase_message_subtext = ""
        self.state = STATE_PLAYING

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS)
            self._handle_events()
            self._update()
            self._draw()
        pygame.quit()

    def _handle_events(self):
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def _handle_key(self, key):
        """Handle key press based on state."""

        # Toggle fullscreen: F11
        if key == pygame.K_F11:
            self._toggle_fullscreen()
            return

        if self.state == STATE_MENU:
            if key == pygame.K_UP:
                self.menu_selection = (self.menu_selection - 1) % 4
            elif key == pygame.K_DOWN:
                self.menu_selection = (self.menu_selection + 1) % 4
            elif key == pygame.K_RETURN:
                if self.menu_selection == 0:
                    self.new_game()
                elif self.menu_selection == 1:
                    self.state = STATE_SETTINGS
                    self.settings_selection = 0
                elif self.menu_selection == 2:
                    self.state = STATE_INSTRUCTIONS
                elif self.menu_selection == 3:
                    self.running = False

        elif self.state == STATE_SETTINGS:
            if key == pygame.K_UP:
                self.settings_selection = (self.settings_selection - 1) % 3
            elif key == pygame.K_DOWN:
                self.settings_selection = (self.settings_selection + 1) % 3
            elif key == pygame.K_RETURN:
                if self.settings_selection == 0:
                    # Toggle combat mode
                    self.combat_mode = COMBAT_MANUAL if self.combat_mode == COMBAT_AUTO else COMBAT_AUTO
                elif self.settings_selection == 2:
                    self.state = STATE_MENU
            elif key == pygame.K_ESCAPE:
                self.state = STATE_MENU

        elif self.state == STATE_INSTRUCTIONS:
            if key == pygame.K_ESCAPE:
                self.state = STATE_MENU

        elif self.state == STATE_PLAYING:
            if key == pygame.K_ESCAPE:
                self.state = STATE_PAUSED
            elif key == pygame.K_1:
                self.player.active_slot = 1
            elif key == pygame.K_2:
                if self.player.slot_2:
                    self.player.active_slot = 2
            elif key == pygame.K_q:
                # Verifica se tem arma no chão para pegar
                if self.nearby_weapon:
                    if try_equip_weapon(self.player, self.loot_drops, self.nearby_weapon):
                        self.play_sound('pickup')
                        self.nearby_weapon = None
                else:
                    # Se não tem arma no chão, troca de slot
                    self.player.switch_slot()
            elif key == pygame.K_r:
                if self.player.reload():
                    print("Recarregado!")
            elif key == pygame.K_i:
                self.state = STATE_INVENTORY
            elif key == pygame.K_TAB:
                self.player.combat_mode = COMBAT_MANUAL if self.player.combat_mode == COMBAT_AUTO else COMBAT_AUTO

        elif self.state == STATE_PAUSED:
            if key == pygame.K_ESCAPE:
                self.state = STATE_PLAYING
            elif key == pygame.K_m:
                self.state = STATE_MENU

        elif self.state == STATE_PHASE2:
            if key == pygame.K_RETURN:
                self.state = STATE_PLAYING
                self.phase_message_text = ""
                self.phase_message_subtext = ""

        elif self.state == STATE_INVENTORY:
            if key in (pygame.K_i, pygame.K_ESCAPE):
                self.state = STATE_PLAYING
            elif key == pygame.K_LEFT:
                self.player.selected_slot = max(0, self.player.selected_slot - 1)
            elif key == pygame.K_RIGHT:
                self.player.selected_slot = min(PLAYER_INV_SIZE - 1,
                                                 self.player.selected_slot + 1)
            elif key == pygame.K_UP:
                self.player.selected_slot = max(0, self.player.selected_slot - 4)
            elif key == pygame.K_DOWN:
                self.player.selected_slot = min(PLAYER_INV_SIZE - 1,
                                                 self.player.selected_slot + 4)
            elif key == pygame.K_e:
                if self.player.use_item(self.player.selected_slot):
                    self.play_sound('pickup')
            elif key == pygame.K_q:
                self.player.drop_item(self.player.selected_slot)

        elif self.state == STATE_UPGRADE:
            if key == pygame.K_UP:
                self.upgrade_selection = (
                    (self.upgrade_selection - 1) % len(self.upgrade_options))
            elif key == pygame.K_DOWN:
                self.upgrade_selection = (
                    (self.upgrade_selection + 1) % len(self.upgrade_options))
            elif key == pygame.K_RETURN:
                if self.upgrade_options:
                    self.player.apply_upgrade(
                        self.upgrade_options[self.upgrade_selection])
                    self.state = STATE_PLAYING

        elif self.state == STATE_GAME_OVER:
            if key == pygame.K_RETURN:
                self.new_game()
            elif key == pygame.K_ESCAPE:
                self.state = STATE_MENU

    def _toggle_fullscreen(self):
        """Alterna fullscreen e atualiza as dimensões de tela e UI."""
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.fullscreen = False
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.fullscreen = True

        self.screen_w, self.screen_h = self.screen.get_size()
        self.ui = UI(self.screen_w, self.screen_h)

    def _update(self):
        """Update game logic."""
        if self.state != STATE_PLAYING:
            return

        if not self.player.alive:
            self.play_sound('death')
            self.state = STATE_GAME_OVER
            return

        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # Update player
        self.player.update(keys, self.tilemap)

        # Auto-shoot or manual shoot
        new_bullets = None
        if self.player.combat_mode == COMBAT_AUTO:
            new_bullets = self.player.try_shoot(self.enemies)
        else:
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0] or keys[pygame.K_SPACE]:
                world_mouse = self.renderer.screen_to_world(mouse_pos[0], mouse_pos[1])
                new_bullets = self.player.try_shoot(self.enemies, world_mouse, 0, 0)

        if new_bullets:
            if isinstance(new_bullets, list):
                for bullet in new_bullets:
                    print(f"[SHOOT] Tipo: {bullet.get('type', 'normal')}, Dano: {bullet['damage']}")
                    self.bullets.append(bullet)
                    self.play_sound('shoot')
                    self.effects.spawn_muzzle_flash(bullet['x'], bullet['y'], 
                                                    bullet['dx'], bullet['dy'])
            else:
                self.bullets.append(new_bullets)
                self.play_sound('shoot')
                self.effects.spawn_muzzle_flash(new_bullets['x'], new_bullets['y'],
                                                new_bullets['dx'], new_bullets['dy'])

       # Update bullets e efeitos de área
        for b in self.bullets[:]:
            b['x'] += b['dx']
            b['y'] += b['dy']
            b['life'] -= 1
            
            # Verifica se é uma granada ou míssil que explodiu no fim da vida
            if b['life'] <= 0:
                # Efeito de explosão para granadas, mísseis e bazuca
                if b.get('type') in ['explosive', 'grenade', 'grenade_launcher']:
                    print(f"[EXPLOSION] {b.get('type')} explodiu em ({b['x']}, {b['y']})")
                    
                    # Dano em área
                    radius = b.get('radius', 35)
                    for enemy in self.enemies:
                        if not enemy.alive:
                            continue
                        dist = math.sqrt((b['x'] - enemy.x)**2 + (b['y'] - enemy.y)**2)
                        if dist < radius:
                            damage = int(b['damage'] * (1 - dist/radius))
                            killed = enemy.take_damage(max(1, damage))
                            self.player.total_damage_dealt += damage
                            self.effects.add_damage_number(enemy.x, enemy.y, damage)
                            
                            if killed:
                                self.player.kills += 1
                                self.effects.spawn_death_particles(enemy.x, enemy.y)
                                self.effects.shake(3, 8)
                                
                                from game.loot import roll_loot
                                loot_items = roll_loot(enemy.x, enemy.y)
                                if loot_items:
                                    for loot in loot_items:
                                        self.loot_drops.append(loot)
                                if self.player.add_xp(enemy.xp_value):
                                    self._trigger_level_up()
                    
                    # Efeito visual de explosão
                    self.effects.spawn_explosion(b['x'], b['y'])
                    self.effects.shake(4, 12)
                    self.play_sound('hit')
                    
                    self.bullets.remove(b)
                    continue
                
                # Área de fogo para coquetel molotov
                elif b.get('type') == 'fire':
                    print(f"[FIRE] Fogo criado em ({b['x']}, {b['y']}) duração: {b.get('duration', 60)}")
                    self.effects.spawn_fire_area(b['x'], b['y'], b.get('duration', 60), b['damage'])
                    self.bullets.remove(b)
                    continue
                
                else:
                    self.bullets.remove(b)
                    continue
            
            # Para minas: quando armar, verifica colisão com inimigos
            if b.get('type') == 'mine':
                if not b.get('armed', False):
                    b['arm_timer'] = b.get('arm_timer', 30) - 1
                    if b['arm_timer'] <= 0:
                        b['armed'] = True
                        print(f"[MINE] Mina armada em ({b['x']}, {b['y']})")
                
                if b.get('armed', False):
                    for enemy in self.enemies:
                        if not enemy.alive:
                            continue
                        dist = math.sqrt((b['x'] - enemy.x)**2 + (b['y'] - enemy.y)**2)
                        if dist < 20:
                            print(f"[MINE] Mina explodiu! Dano: {b['damage']}")
                            killed = enemy.take_damage(b['damage'])
                            self.player.total_damage_dealt += b['damage']
                            self.effects.add_damage_number(enemy.x, enemy.y, b['damage'])
                            
                            if killed:
                                self.player.kills += 1
                                self.effects.spawn_death_particles(enemy.x, enemy.y)
                                from game.loot import roll_loot
                                loot_items = roll_loot(enemy.x, enemy.y)
                                if loot_items:
                                    for loot in loot_items:
                                        self.loot_drops.append(loot)
                                if self.player.add_xp(enemy.xp_value):
                                    self._trigger_level_up()
                            
                            # Efeito de explosão da mina
                            self.effects.spawn_explosion(b['x'], b['y'])
                            self.effects.shake(3, 10)
                            self.play_sound('hit')
                            self.bullets.remove(b)
                            break
            
            # Colisão normal para balas comuns (M4A4, Espingarda, Faquinha)
            else:
                for enemy in self.enemies:
                    if not enemy.alive:
                        continue
                    dx = b['x'] - enemy.x
                    dy = b['y'] - enemy.y
                    hit_distance = 10 if b.get('type') == 'melee' else 7
                    hit_x = max(hit_distance, int(enemy.w * 0.45))
                    hit_y = max(hit_distance, int(enemy.h * 0.45))
                    if abs(dx) < hit_x and abs(dy) < hit_y:
                        killed = enemy.take_damage(b['damage'])
                        self.player.total_damage_dealt += b['damage']
                        self.effects.add_damage_number(enemy.x, enemy.y, b['damage'])
                        self.effects.spawn_hit_particles(enemy.x, enemy.y, 4)
                        self.play_sound('hit')

                        if killed:
                            self.player.kills += 1
                            self.effects.spawn_death_particles(enemy.x, enemy.y)
                            self.effects.shake(2, 4)
                            
                            from game.loot import roll_loot
                            loot_items = roll_loot(enemy.x, enemy.y)
                            if loot_items:
                                for loot in loot_items:
                                    self.loot_drops.append(loot)
                            
                            if self.player.add_xp(enemy.xp_value):
                                self._trigger_level_up()

                        if b in self.bullets:
                            self.bullets.remove(b)
                        break


        # Update enemies
        self._try_spawn_professor_vital()
        self.spawner.update(self.player.x, self.player.y,
                            self.enemies, self.tilemap, self.phase)

        for enemy in self.enemies:
            projectile = enemy.update(self.player.x, self.player.y,
                                      self.tilemap, self.enemies)
            if projectile:
                self.enemy_projectiles.append(projectile)
            if enemy.alive and enemy.collides_with_player(self.player):
                self.player.take_damage(enemy.damage)
                if not self.player.alive:
                    break
                self.effects.shake(3, 6)

        # Update hostile projectiles from boss
        for proj in self.enemy_projectiles[:]:
            proj['x'] += proj['dx']
            proj['y'] += proj['dy']
            proj['life'] -= 1
            if proj['life'] <= 0:
                self.enemy_projectiles.remove(proj)
                continue

            hit_x = abs(proj['x'] - self.player.x) < 8
            hit_y = abs(proj['y'] - self.player.y) < 8
            if hit_x and hit_y:
                self.player.take_damage(proj['damage'])
                self.enemy_projectiles.remove(proj)
                if not self.player.alive:
                    break
                self.effects.shake(4, 7)

        # Clean dead enemies (after fade)
        self.enemies = [e for e in self.enemies
                        if e.alive or e.death_timer < 30]

        # Update loot
        for drop in self.loot_drops:
            drop.update()
        self.loot_drops = [d for d in self.loot_drops if d.alive]

        # Pickup (automático para munição, vida, XP)
        from game.loot import try_pickup
        collected = try_pickup(self.player, self.loot_drops, self)
        for item in collected:
            self.effects.spawn_pickup_particles(item.x, item.y)
            self.play_sound('pickup')

        # Encontra a arma mais próxima para interação manual
        self.nearby_weapon = None   
        min_dist = 50
        for drop in self.loot_drops:
            if not drop.alive:
                continue
            data = drop.loot_data
            if isinstance(data, dict) and data.get('type') == 'weapon':
                dist = drop.distance_to(self.player.x, self.player.y)
                if dist < min_dist:
                    min_dist = dist
                    self.nearby_weapon = drop

        # Update effects
        self.effects.update()

        # Update camera
        self.renderer.update_camera(self.player.x, self.player.y)

        # Phase progression
        self._update_phase_progression()

        # Phase message timer
        if self.phase_message_timer > 0:
            self.phase_message_timer -= 1

        # Game time
        self.game_time += 1

    def _trigger_level_up(self):
        """Show upgrade selection."""
        self.play_sound('levelup')
        # Pick 3 random upgrades
        options = random.sample(UPGRADES, min(3, len(UPGRADES)))
        self.upgrade_options = options
        self.upgrade_selection = 0
        self.state = STATE_UPGRADE

    def _update_phase_progression(self):
        """Advance to phase 3 once the player reaches the kill threshold."""
        if self.phase >= 3 or not self.player:
            return

        if self.player.kills >= PHASE3_KILLS:
            self.phase = 3
            self.spawner.difficulty = max(self.spawner.difficulty, 2.2)
            self.spawner.spawn_rate = max(ENEMY_SPAWN_MIN,
                                          int(ENEMY_SPAWN_RATE / self.spawner.difficulty))
            self.phase_message_timer = FPS * 4
            self.phase_message_text = "FASE 3"
            self.phase_message_subtext = "Agora os inimigos são mais rápidos"

    def _draw(self):
        """Render current frame."""
        self.screen.fill((0, 0, 0))

        if self.state == STATE_MENU:
            self.ui.draw_menu(self.screen, self.menu_selection)

        elif self.state == STATE_SETTINGS:
            self.ui.draw_menu(self.screen, self.settings_selection,
                              settings_open=True)

        elif self.state == STATE_INSTRUCTIONS:
            self.ui.draw_instructions(self.screen)

        elif self.state in (STATE_PLAYING, STATE_PHASE2,
                            STATE_INVENTORY, STATE_PAUSED,
                            STATE_UPGRADE, STATE_GAME_OVER):
            # Draw world
            shake = self.effects.get_shake_offset()
            self.renderer.draw_world(
                self.screen, self.tilemap, self.player,
                self.enemies, self.bullets + self.enemy_projectiles, self.loot_drops,
                self.effects, shake)

            # Calcular enemy_count e draw HUD
            enemy_count = len([e for e in self.enemies if e.alive])
            self.ui.draw_hud(self.screen, self.player,
                             self.game_time, enemy_count, self.phase)

            # Phase 2 message (pause state)
            if self.state == STATE_PHASE2 and self.phase_message_text:
                title_font = pygame.font.SysFont('consolas', 36, bold=True)
                sub_font = pygame.font.SysFont('consolas', 24, bold=True)
                title = title_font.render(self.phase_message_text, True, UI_GOLD)
                subtitle = sub_font.render(self.phase_message_subtext, True, UI_GOLD)
                prompt = self.ui.font_sm.render("Pressione ENTER para continuar", True, UI_TEXT)

                box_w = max(title.get_width(), subtitle.get_width(), prompt.get_width()) + 40
                box_h = title.get_height() + subtitle.get_height() + prompt.get_height() + 50
                box_x = self.screen_w // 2 - box_w // 2
                box_y = self.screen_h // 2 - box_h // 2

                # Draw background panel with border highlight
                panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
                panel.fill((10, 10, 40, 220))
                pygame.draw.rect(panel, UI_ACCENT, (0, 0, box_w, box_h), 3)
                self.screen.blit(panel, (box_x, box_y))

                self.screen.blit(title, (self.screen_w // 2 - title.get_width() // 2, box_y + 12))
                self.screen.blit(subtitle, (self.screen_w // 2 - subtitle.get_width() // 2, box_y + 12 + title.get_height() + 8))
                self.screen.blit(prompt, (self.screen_w // 2 - prompt.get_width() // 2, box_y + 12 + title.get_height() + subtitle.get_height() + 20))

            # Additional temporary phase message (legacy timer)
            elif self.phase_message_timer > 0 and self.phase_message_text:
                if self.phase == 3:
                    title = self.ui.font_lg.render(self.phase_message_text, True, (255, 255, 255))
                    subtitle = self.ui.font_sm.render(self.phase_message_subtext, True, (255, 255, 255))
                    title_x = self.screen_w // 2 - title.get_width() // 2
                    title_y = self.screen_h // 2 - 60
                    bar_y = title_y + title.get_height() + 8
                    bar_w = max(title.get_width(), subtitle.get_width()) + 40
                    bar_x = self.screen_w // 2 - bar_w // 2

                    # Red base below the title
                    pygame.draw.rect(self.screen, (180, 30, 30),
                                     (bar_x, bar_y, bar_w, 28), border_radius=6)
                    self.screen.blit(title, (self.screen_w // 2 - title.get_width() // 2, title_y))
                    self.screen.blit(subtitle, (self.screen_w // 2 - subtitle.get_width() // 2,
                                                bar_y + 36))
                else:
                    msg = self.ui.font_lg.render(self.phase_message_text, True, UI_GOLD)
                    mx = self.screen_w // 2 - msg.get_width() // 2
                    self.screen.blit(msg, (mx, 70))

            # Overlay states
            if self.state == STATE_INVENTORY:
                self.ui.draw_inventory(self.screen, self.player)
            elif self.state == STATE_PAUSED:
                self.ui.draw_pause(self.screen)
            elif self.state == STATE_UPGRADE:
                self.ui.draw_upgrade_choice(
                    self.screen, self.upgrade_options,
                    self.upgrade_selection)
            elif self.state == STATE_GAME_OVER:
                self.ui.draw_game_over(self.screen, self.player,
                                       self.game_time)

        pygame.display.flip()

    def _try_spawn_professor_vital(self, force=False):
        """Spawn final boss by score or by reaching final map area."""
        if self.boss_spawned or not self.player or not self.player.alive:
            return

        score = self.player.kills * 10
        reached_final_area = (
            self.player.x > MAP_PX_W * 0.82 and
            self.player.y > MAP_PX_H * 0.72
        )
        if not force and score < self.boss_score_threshold and not reached_final_area:
            return

        spawn_x = min(MAP_PX_W - TILE_SIZE * 3, self.player.x + 140)
        spawn_y = min(MAP_PX_H - TILE_SIZE * 3, self.player.y + 100)
        from game.campus_map import get_walkable
        if not get_walkable(self.tilemap, spawn_x, spawn_y):
            spawn_x = self.player.x + 60
            spawn_y = self.player.y + 60

        self.enemies.append(ProfessorVital(spawn_x, spawn_y))
        self.boss_spawned = True
        print("PROFESSOR VITAL: EU SOU O BOSS!")
        print("A prova final começou! Aqui é sem consulta!")
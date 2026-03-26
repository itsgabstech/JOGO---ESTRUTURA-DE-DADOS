"""
UNIMA Survivors - Game Engine
Main game loop, state management, core logic.
"""
import pygame
import random
import math
from game.config import *
from game.player import Player
from game.enemies import Enemy, EnemySpawner
from game.campus_map import generate_campus_map, get_spawn_points
from game.loot import LootDrop, roll_loot, try_pickup
from game.effects import EffectsManager
from game.renderer import Renderer
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


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Systems
        self.renderer = Renderer()
        self.ui = UI(SCREEN_WIDTH, SCREEN_HEIGHT)
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
        self.loot_drops = []
        self.spawner = None
        self.game_time = 0

        # Upgrade selection
        self.upgrade_options = []
        self.upgrade_selection = 0

        # Combat mode setting
        self.combat_mode = COMBAT_AUTO

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
        self.loot_drops = []
        self.spawner = EnemySpawner()
        self.effects = EffectsManager()
        self.game_time = 0
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
            elif key == pygame.K_i:
                self.state = STATE_INVENTORY
            elif key == pygame.K_TAB:
                self.player.combat_mode = (
                    COMBAT_MANUAL if self.player.combat_mode == COMBAT_AUTO
                    else COMBAT_AUTO)

        elif self.state == STATE_PAUSED:
            if key == pygame.K_ESCAPE:
                self.state = STATE_PLAYING
            elif key == pygame.K_m:
                self.state = STATE_MENU

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
        if self.player.combat_mode == COMBAT_AUTO:
            bullet = self.player.try_shoot(self.enemies)
        else:
            # Manual: shoot on left click or space
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0] or keys[pygame.K_SPACE]:
                # Convert screen mouse to world coords
                world_mouse = self.renderer.screen_to_world(
                    mouse_pos[0], mouse_pos[1])
                bullet = self.player.try_shoot(
                    self.enemies, world_mouse, 0, 0)
            else:
                bullet = None

        if bullet:
            self.bullets.append(bullet)
            self.play_sound('shoot')
            self.effects.spawn_muzzle_flash(
                bullet['x'], bullet['y'], bullet['dx'], bullet['dy'])

        # Update bullets
        for b in self.bullets[:]:
            b['x'] += b['dx']
            b['y'] += b['dy']
            b['life'] -= 1
            if b['life'] <= 0:
                self.bullets.remove(b)
                continue

            # Check collision with enemies
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                dx = b['x'] - enemy.x
                dy = b['y'] - enemy.y
                if abs(dx) < 7 and abs(dy) < 7:
                    killed = enemy.take_damage(b['damage'])
                    self.player.total_damage_dealt += b['damage']
                    self.effects.add_damage_number(
                        enemy.x, enemy.y, b['damage'])
                    self.effects.spawn_hit_particles(enemy.x, enemy.y, 4)
                    self.play_sound('hit')

                    if killed:
                        self.player.kills += 1
                        self.effects.spawn_death_particles(enemy.x, enemy.y)
                        self.effects.shake(2, 4)
                        # Roll loot
                        loot = roll_loot(enemy.x, enemy.y)
                        if loot:
                            self.loot_drops.append(loot)
                        # XP
                        if self.player.add_xp(enemy.xp_value):
                            self._trigger_level_up()

                    if b in self.bullets:
                        self.bullets.remove(b)
                    break

        # Update enemies
        self.spawner.update(self.player.x, self.player.y,
                            self.enemies, self.tilemap)

        for enemy in self.enemies:
            enemy.update(self.player.x, self.player.y,
                         self.tilemap, self.enemies)
            if enemy.alive and enemy.collides_with_player(self.player):
                self.player.take_damage(enemy.damage)
                if not self.player.alive:
                    break
                self.effects.shake(3, 6)

        # Clean dead enemies (after fade)
        self.enemies = [e for e in self.enemies
                        if e.alive or e.death_timer < 30]

        # Update loot
        for drop in self.loot_drops:
            drop.update()
        self.loot_drops = [d for d in self.loot_drops if d.alive]

        # Pickup
        collected = try_pickup(self.player, self.loot_drops)
        for item in collected:
            self.effects.spawn_pickup_particles(item.x, item.y)
            self.play_sound('pickup')

        # Update effects
        self.effects.update()

        # Update camera
        self.renderer.update_camera(self.player.x, self.player.y)

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

        elif self.state in (STATE_PLAYING, STATE_INVENTORY,
                            STATE_PAUSED, STATE_UPGRADE, STATE_GAME_OVER):
            # Draw world
            shake = self.effects.get_shake_offset()
            self.renderer.draw_world(
                self.screen, self.tilemap, self.player,
                self.enemies, self.bullets, self.loot_drops,
                self.effects, shake)

            # Draw HUD
            enemy_count = len([e for e in self.enemies if e.alive])
            self.ui.draw_hud(self.screen, self.player,
                             self.game_time, enemy_count)

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

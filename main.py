"""
SUPER PLATAFORMA - Jogo de plataforma 2D estilo Mario
Desenvolvido com Python + Pygame
Controles: Setas / WASD para mover, Espaço/W para pular
"""

import pygame
import sys
import math
import os

# ─── ASSETS ───────────────────────────────────────────────────────────────────
ASSETS_DIR        = os.path.join(os.path.dirname(__file__), "assets", "jumpscare")
JUMPSCARE_SOUND   = os.path.join(ASSETS_DIR, "jumpscare.mp3")   # coloque seu .mp3 aqui
JUMPSCARE_IMAGE   = os.path.join(ASSETS_DIR, "jumpscare.png")   # coloque seu .png aqui

# ─── CONFIGURAÇÕES ────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 800, 500
FPS = 60
TITLE = "Super Plataforma"

# Física
GRAVITY = 0.5
PLAYER_SPEED = 4
JUMP_FORCE = -12

# Cores
SKY_BLUE    = (92, 148, 252)
BROWN       = (93, 64, 55)
GREEN_TOP   = (76, 175, 80)
GOLD        = (255, 215, 0)
GOLD_DARK   = (184, 134, 11)
RED         = (204, 51, 0)
RED_LIGHT   = (255, 102, 68)
BLUE_PANTS  = (26, 26, 255)
SKIN        = (245, 200, 122)
HAT_RED     = (230, 57, 0)
WHITE       = (255, 255, 255)
BLACK       = (0, 0, 0)
GRAY        = (85, 85, 85)
FLAG_GREEN  = (0, 204, 68)
FLAG_RED    = (204, 0, 0)
CLOUD_WHITE = (255, 255, 255, 180)
HUD_SHADOW  = (0, 0, 0)

TOTAL_COINS = 10
LEVEL_W = 2400

# ─── NÍVEL ────────────────────────────────────────────────────────────────────
PLATFORM_DATA = [
    # (x, y, w, h)
    (0,    360, 400, 44),
    (420,  360, 200, 44),
    (650,  300, 120, 24),
    (800,  360, 300, 44),
    (820,  240, 100, 24),
    (960,  210,  80, 24),
    (1120, 360, 350, 44),
    (1150, 270, 100, 24),
    (1300, 200,  80, 24),
    (1500, 360, 400, 44),
    (1560, 260, 100, 24),
    (1700, 200,  80, 24),
    (1900, 360, 500, 44),
    (1950, 270, 100, 24),
    (2100, 200, 100, 24),
]

COIN_DATA = [
    (180, 320), (220, 320),
    (460, 320), (500, 320),
    (680, 260),
    (840, 200), (880, 200),
    (990, 170),
    (1320, 160),
    (1720, 160),
]

ENEMY_DATA = [
    # (x, y, patrol_x, patrol_w)
    (300,  334, 0,    400),
    (850,  334, 800,  300),
    (1200, 334, 1120, 350),
    (1600, 334, 1500, 400),
    (2000, 334, 1900, 500),
]

FLAG_X = 2280


# ─── CLASSES ──────────────────────────────────────────────────────────────────

class Platform(pygame.sprite.Sprite):
    """Plataforma sólida do cenário."""
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        # Faixa verde no topo, marrom embaixo
        self.image.fill(BROWN)
        pygame.draw.rect(self.image, GREEN_TOP, (0, 0, w, 6))
        self.rect = self.image.get_rect(topleft=(x, y))


class Coin(pygame.sprite.Sprite):
    """Moeda coletável que bobeia para cima e para baixo."""
    def __init__(self, x, y):
        super().__init__()
        self.base_y = y
        self.timer = 0
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        self._draw_coin(0)
        self.rect = self.image.get_rect(center=(x, y))

    def _draw_coin(self, offset):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, GOLD, (8, 8 + offset), 8)
        pygame.draw.circle(self.image, GOLD_DARK, (8, 8 + offset), 8, 2)
        pygame.draw.circle(self.image, WHITE, (5, 5 + offset), 3)

    def update(self):
        self.timer += 1
        offset = int(math.sin(self.timer * 0.1) * 3)
        self._draw_coin(0)  # redraw flat, position handled by rect
        self.rect.centery = self.base_y + offset


class Enemy(pygame.sprite.Sprite):
    """Inimigo simples que patrulha uma plataforma."""
    def __init__(self, x, y, patrol_x, patrol_w):
        super().__init__()
        self.width, self.height = 26, 26
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx = -1.5
        self.patrol_x = patrol_x
        self.patrol_right = patrol_x + patrol_w
        self.alive = True
        self.anim_timer = 0
        self._draw_enemy()

    def _draw_enemy(self):
        """Desenha o inimigo (formato de cogumelo maligno)."""
        self.image.fill((0, 0, 0, 0))
        # Corpo
        pygame.draw.rect(self.image, RED, (1, 1, 24, 24), border_radius=4)
        # Topo
        pygame.draw.rect(self.image, RED_LIGHT, (3, 2, 20, 10), border_radius=3)
        # Olhos
        pygame.draw.rect(self.image, WHITE, (4 if self.vx > 0 else 14, 6, 5, 5))
        pygame.draw.rect(self.image, BLACK, (5 if self.vx > 0 else 15, 7, 3, 3))
        # Pés
        pygame.draw.rect(self.image, RED, (1, 20, 10, 5), border_radius=2)
        pygame.draw.rect(self.image, RED, (15, 20, 10, 5), border_radius=2)

    def update(self):
        self.rect.x += self.vx
        if self.rect.left <= self.patrol_x or self.rect.right >= self.patrol_right:
            self.vx *= -1
        self.anim_timer += 1
        if self.anim_timer % 10 == 0:
            self._draw_enemy()


class Player(pygame.sprite.Sprite):
    """Personagem principal controlado pelo jogador."""
    def __init__(self, x, y):
        super().__init__()
        self.width, self.height = 28, 36
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.direction = 1   # 1 = direita, -1 = esquerda
        self.anim_frame = 0
        self.anim_timer = 0
        self.inv_timer = 0   # frames de invencibilidade após levar dano
        self._draw()

    def _draw(self):
        """Desenha o personagem pixel-art estilo Mario."""
        self.image.fill((0, 0, 0, 0))
        w = self.width

        # --- Chapéu ---
        pygame.draw.rect(self.image, HAT_RED, (2,  0, 24, 14))
        pygame.draw.rect(self.image, HAT_RED, (0,  4, w,  4))

        # --- Rosto ---
        pygame.draw.rect(self.image, SKIN, (4, 14, 20, 14))

        # --- Bigode / olhos simbólicos ---
        eye_x = 18 if self.direction == 1 else 6
        pygame.draw.rect(self.image, BROWN, (eye_x, 16, 4, 3))

        # --- Macacão ---
        pygame.draw.rect(self.image, BLUE_PANTS, (2, 28, 24, 8))

        # --- Alças ---
        pygame.draw.rect(self.image, BLUE_PANTS, (6,  18, 5, 10))
        pygame.draw.rect(self.image, BLUE_PANTS, (17, 18, 5, 10))

        # --- Pernas animadas ---
        leg_off = int(math.sin(self.anim_frame * 1.57) * 4) if self.on_ground and abs(self.vx) > 0.5 else 0
        pygame.draw.rect(self.image, BROWN, (2,  36 - 6, 10, 6 - leg_off))
        pygame.draw.rect(self.image, BROWN, (16, 36 - 6, 10, 6 + leg_off))

    def handle_input(self, keys):
        """Lê o teclado e aplica velocidade horizontal e pulo."""
        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
            self.direction = -1
            moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
            self.direction = 1
            moving = True
        else:
            self.vx *= 0.75  # atrito

        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vy = JUMP_FORCE
            self.on_ground = False

        return moving

    def apply_gravity(self):
        self.vy += GRAVITY

    def move_and_collide(self, platforms):
        """Move o personagem e resolve colisões AABB com plataformas."""
        # Movimento horizontal
        self.rect.x += int(self.vx)
        self.rect.x = max(0, self.rect.x)  # limite esquerdo do nível
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vx > 0:
                    self.rect.right = plat.rect.left
                elif self.vx < 0:
                    self.rect.left = plat.rect.right
                self.vx = 0

        # Movimento vertical
        self.on_ground = False
        self.rect.y += int(self.vy)
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vy > 0:
                    self.rect.bottom = plat.rect.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = plat.rect.bottom
                    self.vy = 0

    def update_anim(self, moving):
        self.anim_timer += 1
        if self.anim_timer >= 8:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4
        if self.inv_timer > 0:
            self.inv_timer -= 1
        self._draw()

    def is_invincible(self):
        return self.inv_timer > 0


# ─── JOGO ─────────────────────────────────────────────────────────────────────

class Game:
    """Controla o loop principal, estados e lógica de jogo."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font_big   = pygame.font.SysFont("monospace", 32, bold=True)
        self.font_mid   = pygame.font.SysFont("monospace", 20, bold=True)
        self.font_small = pygame.font.SysFont("monospace", 14)

        # Carrega assets do jumpscare (None se o arquivo não existir ainda)
        if os.path.isfile(JUMPSCARE_SOUND):
            self.jumpscare_sound = pygame.mixer.Sound(JUMPSCARE_SOUND)
        else:
            self.jumpscare_sound = None

        if os.path.isfile(JUMPSCARE_IMAGE):
            raw = pygame.image.load(JUMPSCARE_IMAGE).convert_alpha()
            self.jumpscare_image = pygame.transform.scale(raw, (SCREEN_W, SCREEN_H))
        else:
            self.jumpscare_image = None
        self.state = "menu"   # menu | playing | jumpscare | gameover | win
        self.score = 0
        self.lives = 3
        self.coins_collected = 0
        self.cam_x = 0.0
        self.anim_tick = 0
        self.jumpscare_timer = 0
        self.after_jumpscare = None
        self._build_level()

    # ── Inicialização ──────────────────────────────────────────────────────────

    def _build_level(self):
        """Instancia todos os sprites do nível."""
        self.platforms = pygame.sprite.Group()
        for (x, y, w, h) in PLATFORM_DATA:
            self.platforms.add(Platform(x, y, w, h))

        self.coins = pygame.sprite.Group()
        for (x, y) in COIN_DATA:
            self.coins.add(Coin(x, y))

        self.enemies = pygame.sprite.Group()
        for (x, y, px, pw) in ENEMY_DATA:
            self.enemies.add(Enemy(x, y, px, pw))

        self.player = Player(80, 300)

    def _reset(self):
        """Reinicia o nível mantendo ou zerando vidas conforme necessário."""
        self.score = 0
        self.lives = 3
        self.coins_collected = 0
        self.cam_x = 0.0
        self._build_level()
        self.state = "playing"

    # ── Loop Principal ─────────────────────────────────────────────────────────

    def run(self):
        while True:
            self._handle_events()
            if self.state == "playing":
                self._update()
            elif self.state == "jumpscare":
                self.jumpscare_timer += 1
                if self.jumpscare_timer >= 100:
                    self.state = self.after_jumpscare
            self._draw()
            self.clock.tick(FPS)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.state in ("menu", "gameover", "win"):
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._reset()

    # ── Atualização ────────────────────────────────────────────────────────────

    def _update(self):
        keys = pygame.key.get_pressed()
        self.anim_tick += 1

        # Atualiza sprites
        moving = self.player.handle_input(keys)
        self.player.apply_gravity()
        self.player.move_and_collide(self.platforms)
        self.player.update_anim(moving)
        self.enemies.update()
        self.coins.update()

        # Câmera suave seguindo o jogador
        target_cam = self.player.rect.centerx - SCREEN_W // 3
        self.cam_x += (target_cam - self.cam_x) * 0.12
        self.cam_x = max(0, min(self.cam_x, LEVEL_W - SCREEN_W))

        # Colisão com moedas
        hit_coins = pygame.sprite.spritecollide(self.player, self.coins, True)
        for _ in hit_coins:
            self.coins_collected += 1
            self.score += 100

        # Colisão com inimigos
        if not self.player.is_invincible():
            for enemy in self.enemies:
                if self.player.rect.colliderect(enemy.rect):
                    # Pular em cima derrota o inimigo
                    if self.player.vy > 0 and self.player.rect.bottom < enemy.rect.top + 14:
                        enemy.kill()
                        self.player.vy = -9
                        self.score += 200
                    else:
                        self._lose_life()
                        break

        # Caiu no vazio
        if self.player.rect.top > SCREEN_H + 60 and not self.player.is_invincible():
            self._lose_life()

        # Chegou à bandeira com todas as moedas
        if (self.player.rect.right > FLAG_X and
                self.player.rect.left < FLAG_X + 20 and
                self.coins_collected >= TOTAL_COINS):
            self.score += 1000
            self._start_jumpscare("win")

    def _lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self._start_jumpscare("gameover")
        else:
            # Reposiciona o jogador perto da câmera atual
            spawn_x = max(80, int(self.cam_x))
            self.player.rect.topleft = (spawn_x, 100)
            self.player.vx = 0
            self.player.vy = 0
            self.player.inv_timer = 120  # 2 segundos de invencibilidade

    def _start_jumpscare(self, next_state):
        self.jumpscare_timer = 0
        self.after_jumpscare = next_state
        self.state = "jumpscare"
        if self.jumpscare_sound:
            self.jumpscare_sound.play()

    # ── Desenho ────────────────────────────────────────────────────────────────

    def _world_to_screen(self, wx):
        """Converte coordenada X do mundo para coordenada X da tela."""
        return int(wx - self.cam_x)

    def _draw(self):
        if self.state == "menu":
            self._draw_menu()
        elif self.state == "playing":
            self._draw_game()
        elif self.state == "jumpscare":
            self._draw_jumpscare()
        elif self.state == "gameover":
            self._draw_overlay("GAME OVER", f"Pontuação: {self.score}", "ENTER para tentar novamente")
        elif self.state == "win":
            self._draw_overlay("VOCÊ GANHOU!", f"Pontuação final: {self.score}", "ENTER para jogar novamente")
        pygame.display.flip()

    def _draw_jumpscare(self):
        t = self.jumpscare_timer

        # Primeiros frames: mostra a imagem (se existir) + flash
        if t < 40:
            if self.jumpscare_image:
                self.screen.blit(self.jumpscare_image, (0, 0))
            else:
                self.screen.fill(WHITE if t % 2 == 0 else (255, 0, 0))
            return

        # Fundo vermelho escuro
        self.screen.fill((140, 0, 0))

        cx, cy = SCREEN_W // 2, SCREEN_H // 2 - 30

        # Olhos grandes e assustadores
        for ex in (cx - 130, cx + 130):
            pygame.draw.circle(self.screen, WHITE, (ex, cy - 50), 65)
            pygame.draw.circle(self.screen, (220, 0, 0), (ex, cy - 50), 40)
            pygame.draw.circle(self.screen, BLACK, (ex, cy - 50), 22)
            # Veias
            for ang in range(0, 360, 40):
                rad = math.radians(ang)
                x1 = ex + int(math.cos(rad) * 35)
                y1 = (cy - 50) + int(math.sin(rad) * 35)
                x2 = ex + int(math.cos(rad) * 62)
                y2 = (cy - 50) + int(math.sin(rad) * 62)
                pygame.draw.line(self.screen, (200, 0, 0), (x1, y1), (x2, y2), 2)

        # Sobrancelhas ameaçadoras
        pygame.draw.line(self.screen, BLACK, (cx - 195, cy - 120), (cx - 70, cy - 90), 8)
        pygame.draw.line(self.screen, BLACK, (cx + 70,  cy - 90),  (cx + 195, cy - 120), 8)

        # Boca aberta
        pygame.draw.ellipse(self.screen, BLACK, (cx - 150, cy + 10, 300, 90))
        # Dentes superiores
        for i in range(7):
            tx = cx - 130 + i * 38
            pygame.draw.rect(self.screen, WHITE, (tx + 2, cy + 12, 32, 38))
        # Dentes inferiores
        for i in range(6):
            tx = cx - 111 + i * 38
            pygame.draw.rect(self.screen, WHITE, (tx + 2, cy + 62, 28, 32))

        # Texto "BOO!"
        boo = self.font_big.render("BOO!", True, WHITE)
        big_boo = pygame.transform.scale(boo, (boo.get_width() * 3, boo.get_height() * 3))
        self.screen.blit(big_boo, big_boo.get_rect(centerx=SCREEN_W // 2, y=SCREEN_H - 130))

        # Efeito de piscar intermitente
        if t % 10 < 3:
            flash = pygame.Surface((SCREEN_W, SCREEN_H))
            flash.set_alpha(60)
            flash.fill(WHITE)
            self.screen.blit(flash, (0, 0))

    def _draw_menu(self):
        self.screen.fill(SKY_BLUE)
        self._draw_clouds()
        lines = [
            (self.font_big,  "SUPER PLATAFORMA",   WHITE,  200),
            (self.font_mid,  "Colete todas as moedas e chegue à META!", GOLD, 260),
            (self.font_small,"Setas / WASD = mover   Espaço/W = pular",  WHITE, 310),
            (self.font_small,"Pule EM CIMA dos inimigos para derrotá-los!", WHITE, 335),
            (self.font_mid,  "Pressione ENTER para iniciar", WHITE, 400),
        ]
        for font, text, color, y in lines:
            surf = font.render(text, True, color)
            self.screen.blit(surf, surf.get_rect(centerx=SCREEN_W//2, y=y))

    def _draw_game(self):
        # Fundo
        self.screen.fill(SKY_BLUE)
        self._draw_clouds()

        # Plataformas
        for plat in self.platforms:
            sx = self._world_to_screen(plat.rect.x)
            if -plat.rect.width < sx < SCREEN_W:
                self.screen.blit(plat.image, (sx, plat.rect.y))

        # Moedas
        for coin in self.coins:
            sx = self._world_to_screen(coin.rect.x)
            if -20 < sx < SCREEN_W + 20:
                self.screen.blit(coin.image, (sx, coin.rect.y))

        # Inimigos
        for enemy in self.enemies:
            sx = self._world_to_screen(enemy.rect.x)
            if -30 < sx < SCREEN_W + 30:
                self.screen.blit(enemy.image, (sx, enemy.rect.y))

        # Bandeira
        fx = self._world_to_screen(FLAG_X)
        if -30 < fx < SCREEN_W + 30:
            pygame.draw.rect(self.screen, GRAY, (fx, SCREEN_H - 200, 6, 160))
            flag_color = FLAG_GREEN if self.coins_collected >= TOTAL_COINS else FLAG_RED
            pygame.draw.rect(self.screen, flag_color, (fx + 6, SCREEN_H - 200, 32, 22))
            lbl = self.font_small.render("META", True, WHITE)
            self.screen.blit(lbl, (fx + 8, SCREEN_H - 198))

        # Jogador (pisca quando invencível)
        blink = self.player.is_invincible() and (self.player.inv_timer // 5) % 2 == 0
        if not blink:
            px = self._world_to_screen(self.player.rect.x)
            self.screen.blit(self.player.image, (px, self.player.rect.y))

        # HUD
        self._draw_hud()

        # Dica
        if self.coins_collected < TOTAL_COINS:
            remaining = TOTAL_COINS - self.coins_collected
            tip = self.font_small.render(f"Faltam {remaining} moedas!", True, WHITE)
            self.screen.blit(tip, (10, 50))

    def _draw_clouds(self):
        cloud_positions = [200, 500, 900, 1300, 1700, 2100]
        for cx_world in cloud_positions:
            cx = self._world_to_screen(cx_world)
            if -120 < cx < SCREEN_W + 120:
                for (ox, oy, r) in [(0, 0, 30), (30, -10, 25), (55, 0, 28)]:
                    pygame.draw.circle(self.screen, WHITE, (cx + ox, 60 + oy), r)

    def _draw_hud(self):
        def shadow_text(font, text, color, pos):
            s1 = font.render(text, True, BLACK)
            s2 = font.render(text, True, color)
            self.screen.blit(s1, (pos[0]+1, pos[1]+1))
            self.screen.blit(s2, pos)

        shadow_text(self.font_mid, f"SCORE: {self.score}",              WHITE, (10, 10))
        shadow_text(self.font_mid, f"MOEDAS: {self.coins_collected}/{TOTAL_COINS}", GOLD, (SCREEN_W//2 - 70, 10))
        shadow_text(self.font_mid, f"VIDAS: {self.lives}",              WHITE, (SCREEN_W - 140, 10))

    def _draw_overlay(self, title, subtitle, hint):
        self._draw_game()
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        def center(font, text, color, y):
            surf = font.render(text, True, color)
            self.screen.blit(surf, surf.get_rect(centerx=SCREEN_W//2, y=y))

        center(self.font_big,   title,    WHITE, SCREEN_H//2 - 70)
        center(self.font_mid,   subtitle, GOLD,  SCREEN_H//2 - 20)
        center(self.font_small, hint,     WHITE, SCREEN_H//2 + 30)


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    Game().run()

"""
UNIMA Survivors - Visual Effects
Particles, damage numbers, screen shake, etc.
"""
import pygame
import random
import math


class Particle:
    def __init__(self, x, y, color, dx=0, dy=0, life=20, size=2):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.alive = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.05  # gravity
        self.life -= 1
        if self.life <= 0:
            self.alive = False

    def draw(self, surface, cam_x, cam_y, scale):
        if not self.alive:
            return
        alpha = int(255 * (self.life / self.max_life))
        sx = int((self.x - cam_x) * scale)
        sy = int((self.y - cam_y) * scale)
        sz = max(1, int(self.size * scale * (self.life / self.max_life)))
        color = (*self.color[:3], min(255, alpha))
        ps = pygame.Surface((sz, sz), pygame.SRCALPHA)
        ps.fill(color)
        surface.blit(ps, (sx, sy))


class DamageNumber:
    def __init__(self, x, y, value, color=(255, 255, 100)):
        self.x = x
        self.y = y
        self.value = str(int(value))
        self.color = color
        self.life = 40
        self.alive = True
        self.dy = -0.8

    def update(self):
        self.y += self.dy
        self.dy += 0.02
        self.life -= 1
        if self.life <= 0:
            self.alive = False

    def draw(self, surface, cam_x, cam_y, scale, font):
        if not self.alive:
            return
        alpha = int(255 * min(1, self.life / 20))
        sx = int((self.x - cam_x) * scale)
        sy = int((self.y - cam_y) * scale)
        txt = font.render(self.value, True, self.color)
        txt.set_alpha(alpha)
        surface.blit(txt, (sx, sy))


class EffectsManager:
    def __init__(self):
        self.particles = []
        self.damage_numbers = []
        self.screen_shake = 0
        self.shake_intensity = 0
        self.pickup_flashes = []

    def spawn_hit_particles(self, x, y, count=5):
        """Blood/hit particles."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2.0)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            color = random.choice([
                (200, 40, 40), (180, 30, 30), (160, 20, 20), (220, 50, 30)
            ])
            self.particles.append(
                Particle(x, y, color, dx, dy,
                         life=random.randint(10, 25),
                         size=random.uniform(1, 2.5)))

    def spawn_death_particles(self, x, y):
        """Bigger explosion of particles for enemy death."""
        self.spawn_hit_particles(x, y, count=12)
        # Green mist
        for _ in range(6):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.3, 1.0)
            self.particles.append(
                Particle(x, y, (80, 180, 60),
                         math.cos(angle) * speed,
                         math.sin(angle) * speed - 0.5,
                         life=30, size=3))

    def spawn_pickup_particles(self, x, y, color=(80, 255, 120)):
        """Sparkle effect for item pickup."""
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 1.5)
            self.particles.append(
                Particle(x, y, color,
                         math.cos(angle) * speed,
                         math.sin(angle) * speed - 1,
                         life=20, size=2))

    def spawn_muzzle_flash(self, x, y, dx, dy):
        """Gun flash effect."""
        for _ in range(3):
            self.particles.append(
                Particle(x, y, (255, 240, 100),
                         dx * 0.5 + random.uniform(-0.3, 0.3),
                         dy * 0.5 + random.uniform(-0.3, 0.3),
                         life=6, size=2))

    def add_damage_number(self, x, y, value, crit=False):
        color = (255, 80, 80) if crit else (255, 255, 100)
        self.damage_numbers.append(DamageNumber(x, y - 8, value, color))

    def shake(self, intensity=3, duration=8):
        self.screen_shake = duration
        self.shake_intensity = intensity

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

        for d in self.damage_numbers:
            d.update()
        self.damage_numbers = [d for d in self.damage_numbers if d.alive]

        if self.screen_shake > 0:
            self.screen_shake -= 1

    def get_shake_offset(self):
        if self.screen_shake > 0:
            return (random.randint(-self.shake_intensity, self.shake_intensity),
                    random.randint(-self.shake_intensity, self.shake_intensity))
        return (0, 0)

    def draw(self, surface, cam_x, cam_y, scale, font):
        for p in self.particles:
            p.draw(surface, cam_x, cam_y, scale)
        for d in self.damage_numbers:
            d.draw(surface, cam_x, cam_y, scale, font)

import math
import random
import sys
import pygame

# SHADOWFALL: Rise of the Last Kingdom
# Python 3.13 + Pygame
# Controls: WASD / arrow keys = move, SPACE = sword attack,
# E = open chest / activate shrine, R = restart after winning or losing, ESC = quit.

pygame.init()

WIDTH, HEIGHT = 1000, 700
FPS = 60
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHADOWFALL: Rise of the Last Kingdom")
CLOCK = pygame.time.Clock()

# Colours
INK = (13, 9, 24)
DARK = (25, 16, 39)
STONE = (66, 49, 75)
STONE_LIGHT = (117, 91, 126)
GOLD = (255, 211, 99)
GOLD_DARK = (177, 116, 40)
WHITE = (250, 245, 255)
PINK = (247, 126, 185)
PURPLE = (137, 72, 193)
PURPLE_LIGHT = (208, 143, 255)
RED = (220, 48, 73)
RED_LIGHT = (255, 103, 119)
GREEN = (91, 225, 151)
CYAN = (103, 231, 246)
SKIN = (255, 211, 177)
HAIR = (92, 43, 36)
CLOAK = (94, 39, 151)

FONT = pygame.font.Font(None, 28)
SMALL = pygame.font.Font(None, 21)
BIG = pygame.font.Font(None, 54)
TITLE = pygame.font.Font(None, 76)


def draw_text(surface, text, font, colour, x, y, center=False):
    image = font.render(text, True, colour)
    rect = image.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(image, rect)


def clamp(value, low, high):
    return max(low, min(value, high))


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


class Princess:
    """Aelira is drawn from shapes, so no extra image files are needed."""
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT - 110
        self.radius = 17
        self.speed = 250
        self.health = 100
        self.coins = 0
        self.seals = 0
        self.attack_cooldown = 0.0
        self.attack_flash = 0.0
        self.invulnerable = 0.0
        self.facing = pygame.Vector2(0, -1)
        self.walk_time = 0.0

    def move(self, keys, dt, room):
        direction = pygame.Vector2(0, 0)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1
        if direction.length_squared():
            direction = direction.normalize()
            self.facing = direction
            self.walk_time += dt * 12
            self.x += direction.x * self.speed * dt
            self.y += direction.y * self.speed * dt

        self.x = clamp(self.x, 48, WIDTH - 48)
        self.y = clamp(self.y, 135, HEIGHT - 45)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.attack_flash = max(0, self.attack_flash - dt)
        self.invulnerable = max(0, self.invulnerable - dt)

    def attack(self):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = 0.36
            self.attack_flash = 0.18
            return True
        return False

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        bob = int(math.sin(self.walk_time) * 2) if self.walk_time else 0
        # Ground shadow
        pygame.draw.ellipse(surface, (7, 5, 13), (x - 22, y + 14, 44, 15))
        # Long royal hair behind her shoulders
        pygame.draw.ellipse(surface, HAIR, (x - 15, y - 29 + bob, 30, 39))
        pygame.draw.ellipse(surface, (124, 59, 43), (x - 13, y - 25 + bob, 26, 31))
        # Flowing purple cloak
        pygame.draw.polygon(surface, (45, 20, 75),
                            [(x - 12, y - 3 + bob), (x + 12, y - 3 + bob),
                             (x + 22, y + 24), (x, y + 31), (x - 22, y + 24)])
        pygame.draw.polygon(surface, CLOAK,
                            [(x - 10, y - 5 + bob), (x + 10, y - 5 + bob),
                             (x + 15, y + 19), (x, y + 25), (x - 15, y + 19)])
        # White and pink layered princess dress
        pygame.draw.polygon(surface, (255, 232, 244),
                            [(x - 9, y - 2 + bob), (x + 9, y - 2 + bob),
                             (x + 17, y + 17), (x, y + 24), (x - 17, y + 17)])
        pygame.draw.polygon(surface, PINK,
                            [(x - 4, y + 2 + bob), (x + 4, y + 2 + bob),
                             (x + 8, y + 17), (x, y + 20), (x - 8, y + 17)])
        # Shoulders and face
        pygame.draw.circle(surface, GOLD_DARK, (x, y - 12 + bob), 15)
        pygame.draw.circle(surface, SKIN, (x, y - 13 + bob), 12)
        # Hair framing the face and long side locks
        pygame.draw.arc(surface, HAIR, (x - 13, y - 27 + bob, 26, 27), math.pi, math.tau, 7)
        pygame.draw.ellipse(surface, HAIR, (x - 13, y - 20 + bob, 7, 22))
        pygame.draw.ellipse(surface, HAIR, (x + 6, y - 20 + bob, 7, 22))
        # Eyes, blush and smile
        pygame.draw.circle(surface, (58, 35, 48), (x - 4, y - 14 + bob), 1)
        pygame.draw.circle(surface, (58, 35, 48), (x + 4, y - 14 + bob), 1)
        pygame.draw.circle(surface, (244, 135, 150), (x - 7, y - 9 + bob), 2)
        pygame.draw.circle(surface, (244, 135, 150), (x + 7, y - 9 + bob), 2)
        pygame.draw.arc(surface, (145, 62, 77), (x - 3, y - 10 + bob, 6, 5), 0, math.pi, 1)
        # Gold crown with three points and jewel
        pygame.draw.polygon(surface, GOLD,
                            [(x - 12, y - 23 + bob), (x - 11, y - 34 + bob),
                             (x - 4, y - 27 + bob), (x, y - 38 + bob),
                             (x + 5, y - 27 + bob), (x + 12, y - 34 + bob),
                             (x + 12, y - 22 + bob)])
        pygame.draw.line(surface, (255, 239, 169), (x - 10, y - 23 + bob),
                         (x + 10, y - 23 + bob), 3)
        pygame.draw.circle(surface, CYAN, (x, y - 29 + bob), 3)
        # Sword and gold hilt
        start = pygame.Vector2(x, y + 1)
        end = start + self.facing * 30
        pygame.draw.line(surface, (220, 238, 255), start, end, 5)
        pygame.draw.line(surface, GOLD, start + pygame.Vector2(-5, 0),
                         start + pygame.Vector2(5, 0), 4)
        if self.attack_flash > 0:
            arc_pos = pygame.Vector2(x, y) + self.facing * 43
            pygame.draw.circle(surface, CYAN, (int(arc_pos.x), int(arc_pos.y)), 25, 3)
        if self.invulnerable > 0 and int(self.invulnerable * 20) % 2 == 0:
            pygame.draw.circle(surface, WHITE, (x, y), 31, 2)


class Enemy:
    def __init__(self, x, y, kind="soldier"):
        self.x = float(x)
        self.y = float(y)
        self.kind = kind
        self.boss = kind == "boss"
        self.radius = 29 if self.boss else (18 if kind == "beast" else 15)
        self.health = 220 if self.boss else (75 if kind == "beast" else 52)
        self.max_health = self.health
        self.speed = 56 if self.boss else (108 if kind == "beast" else random.randint(72, 94))
        self.attack_timer = random.uniform(0.5, 1.2)
        self.hit_flash = 0
        self.alive = True

    def update(self, player, dt, phase=1):
        if not self.alive:
            return
        self.hit_flash = max(0, self.hit_flash - dt)
        self.attack_timer -= dt
        delta = pygame.Vector2(player.x - self.x, player.y - self.y)
        dist = delta.length()
        if dist > self.radius + player.radius + 5:
            if dist:
                speed = self.speed * (1.0 + 0.14 * (phase - 1)) if self.boss else self.speed
                direction = delta.normalize()
                self.x += direction.x * speed * dt
                self.y += direction.y * speed * dt
        elif self.attack_timer <= 0 and player.invulnerable <= 0:
            player.health = max(0, player.health - (10 if self.boss else 11 if self.kind == "beast" else 8))
            player.invulnerable = 0.7
            self.attack_timer = 0.85 if self.boss else 1.05

    def draw(self, surface):
        if not self.alive:
            return
        x, y = int(self.x), int(self.y)
        shade = RED_LIGHT if self.hit_flash > 0 else ((73, 31, 94) if self.boss else (106, 27, 71))
        pygame.draw.ellipse(surface, (7, 4, 12), (x - self.radius, y + 9, self.radius * 2, 13))
        if self.boss:
            pygame.draw.polygon(surface, (45, 13, 60),
                                [(x - 30, y - 5), (x - 25, y - 36), (x - 9, y - 22),
                                 (x, y - 48), (x + 10, y - 22), (x + 27, y - 37),
                                 (x + 30, y - 5), (x + 36, y + 26), (x, y + 39),
                                 (x - 36, y + 26)])
            pygame.draw.circle(surface, shade, (x, y - 5), 26)
            pygame.draw.circle(surface, RED_LIGHT, (x - 9, y - 6), 5)
            pygame.draw.circle(surface, RED_LIGHT, (x + 9, y - 6), 5)
            pygame.draw.circle(surface, PURPLE_LIGHT, (x, y - 5), 33, 2)
        elif self.kind == "beast":
            pygame.draw.polygon(surface, shade, [(x - 22, y - 6), (x - 16, y - 20),
                                                 (x - 4, y - 12), (x + 12, y - 19),
                                                 (x + 23, y - 5), (x + 18, y + 13),
                                                 (x, y + 18), (x - 18, y + 11)])
            pygame.draw.circle(surface, RED_LIGHT, (x - 7, y - 3), 3)
            pygame.draw.circle(surface, RED_LIGHT, (x + 8, y - 3), 3)
        else:
            pygame.draw.circle(surface, shade, (x, y), self.radius)
            pygame.draw.polygon(surface, (43, 15, 55),
                                [(x - 12, y - 8), (x - 8, y - 22), (x, y - 12),
                                 (x + 8, y - 22), (x + 13, y - 7)])
            pygame.draw.circle(surface, PURPLE_LIGHT, (x - 5, y - 2), 3)
            pygame.draw.circle(surface, PURPLE_LIGHT, (x + 5, y - 2), 3)
        if self.health < self.max_health:
            width = 76 if self.boss else 40
            by = y - (57 if self.boss else 26)
            pygame.draw.rect(surface, (36, 10, 26), (x - width // 2, by, width, 6))
            pygame.draw.rect(surface, RED, (x - width // 2, by,
                            int(width * max(0, self.health) / self.max_health), 6))


class Treasure:
    def __init__(self, x, y, kind="chest"):
        self.x, self.y = x, y
        self.kind = kind
        self.opened = False

    def draw(self, surface, time_value):
        x, y = self.x, self.y
        if self.opened:
            pygame.draw.rect(surface, (71, 49, 50), (x - 18, y - 8, 36, 20), border_radius=4)
            pygame.draw.line(surface, STONE_LIGHT, (x - 14, y - 3), (x + 14, y + 8), 2)
        elif self.kind == "chest":
            pygame.draw.ellipse(surface, (8, 5, 12), (x - 23, y + 12, 46, 11))
            pygame.draw.rect(surface, (105, 53, 30), (x - 21, y - 5, 42, 24), border_radius=5)
            pygame.draw.rect(surface, GOLD_DARK, (x - 21, y - 7, 42, 9), border_radius=4)
            pygame.draw.rect(surface, GOLD, (x - 3, y - 4, 6, 16))
            pygame.draw.circle(surface, GOLD, (x, y - 1), 3)
            pygame.draw.circle(surface, (255, 236, 146), (x, y - 13 + int(math.sin(time_value * 3) * 2)), 3)
        else:
            pulse = int(20 * (0.5 + 0.5 * math.sin(time_value * 3)))
            pygame.draw.circle(surface, (70, 31, 105), (x, y), 22)
            pygame.draw.circle(surface, (140 + pulse, 66, 200), (x, y), 14)
            pygame.draw.polygon(surface, CYAN, [(x, y - 10), (x + 8, y), (x, y + 10), (x - 8, y)])


class Trap:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.timer = random.random() * 1.5
        self.active = False

    def update(self, player, dt):
        self.timer += dt
        self.active = (self.timer % 2.6) > 1.5
        if self.active and distance((self.x, self.y), (player.x, player.y)) < 32:
            if player.invulnerable <= 0:
                player.health = max(0, player.health - 14)
                player.invulnerable = 0.8

    def draw(self, surface):
        colour = RED if self.active else STONE_LIGHT
        pygame.draw.circle(surface, (30, 20, 40), (self.x, self.y), 25)
        pygame.draw.circle(surface, colour, (self.x, self.y), 19, 2)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            end = (self.x + math.cos(rad) * 16, self.y + math.sin(rad) * 16)
            pygame.draw.line(surface, colour, (self.x, self.y), end, 2)


ROOMS = [
    {"name": "1. THE RUINED COURTYARD", "floor": (46, 37, 54),
     "goal": "Find the Moon Seal and search the old courtyard.",
     "enemies": [(250, 300, "soldier"), (750, 340, "soldier"), (520, 230, "beast")]},
    {"name": "2. THE CRYSTAL CATACOMBS", "floor": (31, 39, 59),
     "goal": "Survive the traps and collect the Sun Seal.",
     "enemies": [(230, 270, "soldier"), (750, 300, "beast"), (510, 430, "soldier")]},
    {"name": "3. THE HAUNTED GARDEN", "floor": (32, 52, 43),
     "goal": "Find the Star Seal and survive the haunted garden.",
     "enemies": [(220, 340, "beast"), (770, 270, "soldier"), (520, 250, "beast")]},
    {"name": "4. THE SHADOW KING'S FORTRESS", "floor": (49, 25, 43),
     "goal": "Claim the final seal and challenge the Shadow King.",
     "enemies": [(220, 280, "beast"), (500, 240, "soldier"), (740, 320, "beast"), (520, 460, "soldier")]},
]


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.player = Princess()
        self.state = "intro"
        self.room_index = 0
        self.elapsed = 0.0
        self.message = "Four ancient seals are hidden across the kingdom."
        self.message_timer = 4.0
        self.enemies = []
        self.treasures = []
        self.traps = []
        self.boss = None
        self.spawn_room()

    def say(self, text, seconds=3):
        self.message = text
        self.message_timer = seconds

    def spawn_room(self):
        room = ROOMS[self.room_index]
        self.enemies = [Enemy(x, y, kind) for x, y, kind in room["enemies"]]
        self.treasures = [Treasure(160, 480), Treasure(830, 220),
                          Treasure(500, 375, "shrine")]
        self.traps = []
        if self.room_index >= 1:
            self.traps = [Trap(350, 330), Trap(650, 390), Trap(500, 500)]
        self.player.x, self.player.y = WIDTH // 2, HEIGHT - 85

    def handle_attack(self):
        p = pygame.Vector2(self.player.x, self.player.y)
        for enemy in self.enemies:
            if enemy.alive:
                delta = pygame.Vector2(enemy.x, enemy.y) - p
                if delta.length() < 72 and (delta.length_squared() == 0 or
                    self.player.facing.dot(delta.normalize()) > -0.1):
                    enemy.health -= 28
                    enemy.hit_flash = 0.14
                    if enemy.health <= 0:
                        enemy.alive = False
                        self.player.coins += 3 if enemy.boss else 2
                        self.say("Shadow defeated! You found a few royal coins.", 1.7)
        if self.boss and self.boss.alive:
            delta = pygame.Vector2(self.boss.x, self.boss.y) - p
            if delta.length() < 110 and (delta.length_squared() == 0 or
                self.player.facing.dot(delta.normalize()) > -0.35):
                self.boss.health -= 35
                self.boss.hit_flash = 0.14
                if self.boss.health <= 0:
                    self.boss.alive = False
                    self.state = "victory"
                    self.say("The Shadow King has fallen. Eldoria is free!", 6)

    def interact(self):
        for treasure in self.treasures:
            if not treasure.opened and distance((self.player.x, self.player.y),
                                                (treasure.x, treasure.y)) < 62:
                treasure.opened = True
                if treasure.kind == "chest":
                    reward = random.choice([5, 8, 10])
                    self.player.coins += reward
                    self.player.health = min(100, self.player.health + 10)
                    self.say(f"Treasure found! +{reward} coins and a healing charm.")
                else:
                    self.player.seals += 1
                    self.player.health = min(100, self.player.health + 15)
                    self.say(f"Ancient seal collected! Seals: {self.player.seals}/4")
                return
        if self.room_index < 3 and self.player.x > WIDTH - 95 and self.player.y < HEIGHT - 120:
            if any(e.alive for e in self.enemies):
                self.say("The gate is sealed! Defeat every shadow in this room.")
            else:
                self.room_index += 1
                self.spawn_room()
                self.say(f"Entered {ROOMS[self.room_index]['name']}!", 3)
        elif self.room_index == 3 and not any(e.alive for e in self.enemies):
            if self.player.seals >= 4:
                self.boss = Enemy(WIDTH - 180, 250, "boss")
                self.state = "boss"
                self.say("The Shadow King awakens! Get close and press SPACE to strike!", 4)
            else:
                self.say(f"The Shadow King needs 4 seals. You have {self.player.seals}/4.")

    def update(self, dt):
        self.elapsed += dt
        self.message_timer = max(0, self.message_timer - dt)
        keys = pygame.key.get_pressed()
        if self.state in ("battle", "boss"):
            self.player.move(keys, dt, self.room_index)
            for enemy in self.enemies:
                enemy.update(self.player, dt)
            for trap in self.traps:
                trap.update(self.player, dt)
            if self.boss and self.boss.alive:
                self.boss.update(self.player, dt, 2)
            if self.player.health <= 0:
                self.state = "dead"

    def draw_background(self):
        room = ROOMS[self.room_index]
        SCREEN.fill(INK)
        pygame.draw.rect(SCREEN, room["floor"], (24, 100, WIDTH - 48, HEIGHT - 125), border_radius=12)
        # Large flagstone floor
        for y in range(112, HEIGHT - 35, 48):
            pygame.draw.line(SCREEN, (65, 53, 76), (35, y), (WIDTH - 35, y), 1)
        for row, y in enumerate(range(120, HEIGHT - 35, 48)):
            offset = 0 if row % 2 == 0 else 35
            for x in range(40 + offset, WIDTH - 35, 70):
                pygame.draw.line(SCREEN, (65, 53, 76), (x, y), (x, y + 48), 1)
        # Ruined stone wall and battlements
        pygame.draw.rect(SCREEN, (34, 23, 47), (20, 84, WIDTH - 40, 42), border_radius=7)
        for x in range(45, WIDTH - 30, 105):
            pygame.draw.rect(SCREEN, STONE, (x, 87, 28, 39), border_radius=3)
            pygame.draw.rect(SCREEN, STONE_LIGHT, (x - 4, 85, 36, 7), border_radius=3)
        # Room-specific ambience
        if self.room_index == 0:
            pygame.draw.circle(SCREEN, (97, 29, 65), (WIDTH // 2, 205), 90)
            pygame.draw.circle(SCREEN, (170, 40, 88), (WIDTH // 2, 205), 67, 4)
            # Broken arch
            pygame.draw.arc(SCREEN, (105, 76, 112), (WIDTH // 2 - 115, 118, 230, 150),
                            math.pi, math.tau, 8)
            pygame.draw.rect(SCREEN, (65, 43, 75), (WIDTH // 2 - 118, 190, 18, 90))
            pygame.draw.rect(SCREEN, (65, 43, 75), (WIDTH // 2 + 100, 190, 18, 90))
        elif self.room_index == 1:
            for x, y in [(180, 210), (820, 240), (300, 460), (710, 470)]:
                pygame.draw.circle(SCREEN, (30, 77, 105), (x, y), 31)
                pygame.draw.polygon(SCREEN, CYAN, [(x, y - 25), (x + 15, y), (x, y + 25), (x - 15, y)])
        elif self.room_index == 2:
            for x, y in [(150, 200), (850, 190), (170, 500), (820, 500)]:
                pygame.draw.circle(SCREEN, (38, 85, 55), (x, y), 35)
                pygame.draw.circle(SCREEN, (85, 156, 93), (x, y), 22, 2)
                pygame.draw.circle(SCREEN, PINK, (x, y), 5)
        else:
            # The Shadow King's fortress: dark pillars and glowing lava cracks
            for x in (115, 300, 700, 885):
                pygame.draw.rect(SCREEN, (36, 17, 42), (x - 14, 130, 28, 390))
                pygame.draw.rect(SCREEN, (103, 45, 82), (x - 18, 130, 36, 10))
                pygame.draw.rect(SCREEN, (103, 45, 82), (x - 18, 510, 36, 10))
            for x, y in [(390, 245), (620, 420), (430, 520)]:
                pygame.draw.line(SCREEN, (150, 38, 76), (x - 22, y - 12), (x + 20, y + 15), 4)
                pygame.draw.line(SCREEN, (222, 66, 91), (x - 8, y + 12), (x + 18, y - 14), 3)
        # Exit arch and glowing gate
        if self.room_index < 3:
            pygame.draw.rect(SCREEN, (77, 51, 91), (WIDTH - 91, 155, 54, 98), border_radius=12)
            pygame.draw.rect(SCREEN, GOLD if not any(e.alive for e in self.enemies) else PURPLE,
                             (WIDTH - 82, 165, 36, 78), 3, border_radius=8)
            draw_text(SCREEN, "E", SMALL, GOLD, WIDTH - 74, 265)
        else:
            pygame.draw.rect(SCREEN, (66, 22, 70), (WIDTH - 108, 150, 70, 118), border_radius=12)
            pygame.draw.rect(SCREEN, PURPLE_LIGHT, (WIDTH - 98, 160, 50, 98), 3, border_radius=8)

    def draw_hud(self):
        pygame.draw.rect(SCREEN, (15, 9, 27), (15, 12, 390, 70), border_radius=10)
        pygame.draw.rect(SCREEN, (117, 76, 145), (15, 12, 390, 70), 2, border_radius=10)
        draw_text(SCREEN, "PRINCESS AELIRA", SMALL, GOLD, 28, 19)
        pygame.draw.rect(SCREEN, (60, 20, 42), (180, 22, 195, 15), border_radius=5)
        pygame.draw.rect(SCREEN, GREEN if self.player.health > 35 else RED,
                         (180, 22, int(195 * self.player.health / 100), 15), border_radius=5)
        draw_text(SCREEN, f"HP {self.player.health}/100", SMALL, WHITE, 180, 43)
        draw_text(SCREEN, f"COINS: {self.player.coins}", SMALL, GOLD, 285, 43)
        draw_text(SCREEN, f"SEALS: {self.player.seals}/4", SMALL, CYAN, 28, 54)
        draw_text(SCREEN, ROOMS[self.room_index]["name"], SMALL, WHITE, WIDTH // 2, 22, center=True)
        draw_text(SCREEN, ROOMS[self.room_index]["goal"], SMALL, (227, 213, 238),
                  WIDTH // 2, 48, center=True)
        if self.boss and self.boss.alive:
            bw = 380
            pygame.draw.rect(SCREEN, (38, 8, 26), (WIDTH // 2 - bw // 2, 75, bw, 12), border_radius=5)
            pygame.draw.rect(SCREEN, RED, (WIDTH // 2 - bw // 2, 75,
                             int(bw * max(0, self.boss.health) / self.boss.max_health), 12), border_radius=5)
            draw_text(SCREEN, "THE SHADOW KING", SMALL, RED_LIGHT, WIDTH // 2, 96, center=True)

    def draw(self):
        self.draw_background()
        for trap in self.traps:
            trap.draw(SCREEN)
        for treasure in self.treasures:
            treasure.draw(SCREEN, self.elapsed)
        for enemy in self.enemies:
            enemy.draw(SCREEN)
        if self.boss:
            self.boss.draw(SCREEN)
        self.player.draw(SCREEN)
        self.draw_hud()

        if self.state in ("battle", "boss"):
            draw_text(SCREEN, "MOVE: WASD / ARROWS     SWORD: SPACE     OPEN / GATE: E",
                      SMALL, WHITE, WIDTH // 2, HEIGHT - 19, center=True)
            if self.message_timer > 0:
                pygame.draw.rect(SCREEN, (14, 8, 26), (175, 106, WIDTH - 350, 34), border_radius=8)
                pygame.draw.rect(SCREEN, (130, 82, 164), (175, 106, WIDTH - 350, 34), 1, border_radius=8)
                draw_text(SCREEN, self.message, SMALL, WHITE, WIDTH // 2, 123, center=True)

        if self.state == "intro":
            self.overlay()
            draw_text(SCREEN, "SHADOWFALL", TITLE, PURPLE_LIGHT, WIDTH // 2, 190, center=True)
            draw_text(SCREEN, "RISE OF THE LAST KINGDOM", BIG, GOLD, WIDTH // 2, 245, center=True)
            draw_text(SCREEN, "Play as Princess Aelira and reclaim four ancient seals.", FONT,
                      WHITE, WIDTH // 2, 325, center=True)
            draw_text(SCREEN, "Explore ruined halls, dodge traps, defeat shadow beasts,", FONT,
                      (222, 207, 237), WIDTH // 2, 365, center=True)
            draw_text(SCREEN, "open treasure chests, and enter the Shadow King's fortress.", FONT,
                      (222, 207, 237), WIDTH // 2, 397, center=True)
            draw_text(SCREEN, "Press ENTER to begin your adventure", FONT, GOLD, WIDTH // 2, 470, center=True)
            draw_text(SCREEN, "WASD / Arrows: move     SPACE: attack     E: interact", SMALL,
                      WHITE, WIDTH // 2, 515, center=True)

        elif self.state == "dead":
            self.overlay()
            draw_text(SCREEN, "AELIRA HAS FALLEN", BIG, RED_LIGHT, WIDTH // 2, 280, center=True)
            draw_text(SCREEN, "The kingdom still needs its princess.", FONT, WHITE, WIDTH // 2, 330, center=True)
            draw_text(SCREEN, "Press R to try again  •  ESC to quit", FONT, GOLD, WIDTH // 2, 390, center=True)

        elif self.state == "victory":
            self.overlay()
            draw_text(SCREEN, "AELIRA IS FREE!", TITLE, GOLD, WIDTH // 2, 250, center=True)
            draw_text(SCREEN, "Princess Aelira has defeated the Shadow King!", FONT, WHITE,
                      WIDTH // 2, 320, center=True)
            draw_text(SCREEN, f"Seals: {self.player.seals}/4     Coins collected: {self.player.coins}",
                      FONT, CYAN, WIDTH // 2, 365, center=True)
            draw_text(SCREEN, "Press R to play again  •  ESC to quit", FONT, GOLD, WIDTH // 2, 425, center=True)

    def overlay(self):
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((5, 2, 13, 205))
        SCREEN.blit(shade, (0, 0))


def main():
    game = Game()
    running = True
    while running:
        dt = min(CLOCK.tick(FPS) / 1000.0, 0.035)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif game.state == "intro" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game.state = "battle"
                    game.say("Find the glowing shrine and press E to collect its seal.", 4)
                elif game.state in ("battle", "boss"):
                    if event.key == pygame.K_SPACE and game.player.attack():
                        game.handle_attack()
                    elif event.key == pygame.K_e:
                        game.interact()
                elif game.state in ("dead", "victory") and event.key == pygame.K_r:
                    game.reset()

        game.update(dt)
        game.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

import pygame
import math
import random
import sys
from array import array

# ============================================================
# LEVEL 3 - THE FORGOTTEN UNDERKINGDOM
# Python 3.13 + Pygame
# No external images are required. Everything is drawn in code.
# ============================================================

import audio_support

pygame.init()

def game_sound(name):
    """Use launcher sounds, or local generated effects when run alone."""
    try:
        shared = globals().get("play_sfx")
        if callable(shared):
            shared(name)
        else:
            audio_support.play_sfx(name)
    except pygame.error:
        pass

if "play_sfx" not in globals():
    audio_support.start_music(3)

# ---------- Built-in Sound Effects ----------
# Sounds are generated in code, so no .wav/.mp3 files are required.
if not pygame.mixer.get_init():
    pygame.mixer.init(frequency=44100, size=-16, channels=1)

def make_tone(start_freq, duration, volume=0.25, end_freq=None):
    sample_rate = 44100
    count = int(sample_rate * duration)
    end_freq = start_freq if end_freq is None else end_freq
    samples = array("h")
    amplitude = int(32767 * volume)
    for n in range(count):
        t = n / sample_rate
        progress = n / max(1, count - 1)
        freq = start_freq + (end_freq - start_freq) * progress
        # Small fade in/out prevents clicks.
        fade = min(1.0, n / max(1, int(sample_rate * 0.01)))
        fade *= min(1.0, (count - n) / max(1, int(sample_rate * 0.03)))
        value = int(amplitude * fade * math.sin(2 * math.pi * freq * t))
        samples.append(value)
    return pygame.mixer.Sound(buffer=samples.tobytes())

SWORD_SOUND = make_tone(700, 0.10, 0.48, 1100)
HIT_SOUND = make_tone(180, 0.10, 0.52, 90)
RUNE_SOUND = make_tone(700, 0.18, 0.48, 1100)
PUZZLE_SOUND = make_tone(450, 0.08, 0.42, 650)
PUZZLE_SUCCESS_SOUND = make_tone(700, 0.35, 0.58, 1300)
LEVER_SOUND = make_tone(250, 0.14, 0.48, 120)
DAMAGE_SOUND = make_tone(120, 0.12, 0.55, 70)
BOSS_SOUND = make_tone(80, 0.55, 0.60, 45)
DEFEAT_SOUND = make_tone(220, 0.30, 0.55, 70)
VICTORY_SOUND = make_tone(600, 0.65, 0.65, 1500)

WIDTH, HEIGHT = 1280, 720
FPS = 60
WORLD_W, WORLD_H = 3200, 1800

FULLSCREEN = False
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
pygame.display.set_caption("Level 3 - The Forgotten Underkingdom")

def toggle_fullscreen():
    """Toggle fullscreen with F11 while keeping the game's logical resolution."""
    global screen, FULLSCREEN
    FULLSCREEN = not FULLSCREEN
    flags = pygame.SCALED | (pygame.FULLSCREEN if FULLSCREEN else 0)
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("Level 3 - The Forgotten Underkingdom")
    return screen
clock = pygame.time.Clock()

# ---------- Fonts ----------
FONT_BIG = pygame.font.SysFont("georgia", 46, bold=True)
FONT_TITLE = pygame.font.SysFont("georgia", 34, bold=True)
FONT = pygame.font.SysFont("georgia", 24)
FONT_SMALL = pygame.font.SysFont("georgia", 18)

# ---------- Colors ----------
BLACK = (8, 7, 18)
DEEP = (13, 15, 35)
STONE = (58, 51, 82)
STONE2 = (79, 68, 105)
PURPLE = (112, 70, 156)
BLUE = (48, 205, 238)
CYAN = (80, 245, 255)
WHITE = (235, 240, 255)
GOLD = (255, 218, 105)
RED = (235, 80, 100)
GREEN = (100, 235, 150)
SHADOW = (25, 20, 45)

# ---------- Helpers ----------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def text(surface, value, font, color, x, y, center=False):
    img = font.render(value, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)


def glow_circle(surface, pos, radius, color, alpha=70):
    glow = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    cx, cy = radius * 2, radius * 2
    for r in range(radius * 2, max(2, radius // 2), -4):
        a = int(alpha * (1 - r / (radius * 2)))
        pygame.draw.circle(glow, (*color, max(0, a)), (cx, cy), r)
    surface.blit(glow, (pos[0] - cx, pos[1] - cy))


# ---------- Background ----------
def draw_cave(surface, camera):
    # Dark gradient-like bands
    surface.fill(DEEP)
    for i in range(12):
        col = (
            15 + i * 2,
            13 + i * 2,
            30 + i * 5,
        )
        pygame.draw.rect(surface, col, (0, i * HEIGHT // 12, WIDTH, HEIGHT // 12 + 2))

    # Ceiling stalactites
    for x in range(-100, WIDTH + 150, 95):
        h = 30 + ((x * 17) % 85)
        pygame.draw.polygon(
            surface,
            (35, 31, 55),
            [(x, 0), (x + 35, 0), (x + 18, h)]
        )

    # Distant pillars
    for wx in range(0, WORLD_W, 230):
        x = wx - camera.x
        if -100 < x < WIDTH + 100:
            base = HEIGHT - 80 - ((wx // 230) % 3) * 20
            pygame.draw.polygon(
                surface,
                (30, 28, 52),
                [(x, base), (x + 45, 130), (x + 115, 95),
                 (x + 155, base)]
            )

    # Water river
    river = pygame.Rect(820 - camera.x, 650 - camera.y, 980, 600)
    pygame.draw.ellipse(surface, (20, 120, 160), river)
    pygame.draw.ellipse(surface, (15, 170, 205),
                         river.inflate(-40, -45), 10)

    # Animated water lines
    t = pygame.time.get_ticks() * 0.002
    for i in range(22):
        x = 850 + i * 45 - camera.x
        y = 730 + math.sin(t + i) * 18 - camera.y
        pygame.draw.arc(
            surface, (95, 245, 255),
            (x, y, 130, 38), 0.2, 2.8, 3
        )

    # Large stone platforms
    platforms = [
        pygame.Rect(0, 250, 760, 560),
        pygame.Rect(1850, 240, 1350, 520),
        pygame.Rect(0, 1260, 950, 540),
        pygame.Rect(2050, 1180, 1150, 620),
    ]

    for r in platforms:
        rr = r.move(-camera.x, -camera.y)
        pygame.draw.rect(surface, STONE, rr, border_radius=18)
        pygame.draw.rect(surface, STONE2, rr, 5, border_radius=18)

        # stone tile lines
        for xx in range(r.left + 30, r.right, 75):
            pygame.draw.line(
                surface, (49, 43, 70),
                (xx - camera.x, r.top - camera.y),
                (xx - camera.x, r.bottom - camera.y), 2
            )
        for yy in range(r.top + 55, r.bottom, 70):
            pygame.draw.line(
                surface, (48, 42, 69),
                (r.left - camera.x, yy - camera.y),
                (r.right - camera.x, yy - camera.y), 2
            )

    # Upper bridge
    bridge_y = 500 - camera.y
    for i in range(16):
        x = 690 + i * 78 - camera.x
        tile = pygame.Rect(x, bridge_y, 76, 58)
        pygame.draw.rect(surface, (125, 105, 135), tile, border_radius=6)
        pygame.draw.rect(surface, (65, 55, 85), tile, 3, border_radius=6)

    # Crystals
    crystal_positions = [
        (170, 380, 42), (520, 360, 55), (660, 700, 38),
        (2030, 390, 48), (2390, 520, 75), (2770, 390, 44),
        (510, 1450, 65), (2280, 1380, 50), (2880, 1500, 65)
    ]
    for x, y, size in crystal_positions:
        draw_crystal(surface, x - camera.x, y - camera.y, size)

    # Ancient statues
    for x, y in [(420, 670), (2140, 670), (560, 1530)]:
        draw_statue(surface, x - camera.x, y - camera.y)


def draw_crystal(surface, x, y, size):
    glow_circle(surface, (x, y), size, CYAN, 80)
    pts = [
        (x, y - size),
        (x + size // 2, y - size // 4),
        (x + size // 3, y + size),
        (x, y + size // 2),
        (x - size // 3, y + size),
        (x - size // 2, y - size // 4)
    ]
    pygame.draw.polygon(surface, (75, 210, 240), pts)
    pygame.draw.polygon(surface, (150, 245, 255), pts, 3)
    pygame.draw.line(surface, WHITE, (x, y - size + 8),
                     (x, y + size // 2), 3)


def draw_statue(surface, x, y):
    pygame.draw.ellipse(surface, (75, 70, 95), (x - 30, y - 90, 60, 60))
    pygame.draw.polygon(
        surface, (65, 60, 82),
        [(x - 55, y - 30), (x + 55, y - 30),
         (x + 75, y + 90), (x - 75, y + 90)]
    )
    pygame.draw.circle(surface, CYAN, (x - 12, y - 65), 4)
    pygame.draw.circle(surface, CYAN, (x + 12, y - 65), 4)


# ---------- Player ----------
class Player:
    def __init__(self):
        self.x = 260
        self.y = 600
        self.w = 42
        self.h = 70
        self.speed = 4.5
        self.hp = 100
        self.max_hp = 100
        self.sword_timer = 0
        self.invuln = 0

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.w / 2),
            int(self.y - self.h / 2),
            self.w, self.h
        )

    def move(self, keys, platforms):
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - \
             (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - \
             (keys[pygame.K_w] or keys[pygame.K_UP])

        if dx or dy:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length

        old_x, old_y = self.x, self.y
        self.x += dx * self.speed
        self.y += dy * self.speed

        self.x = clamp(self.x, 35, WORLD_W - 35)
        self.y = clamp(self.y, 80, WORLD_H - 35)

        # Do not fall into the river.
        river = pygame.Rect(820, 650, 980, 600)
        if self.rect.colliderect(river):
            self.x, self.y = old_x, old_y

        # Walls / solid areas
        for p in platforms:
            if self.rect.colliderect(p):
                self.x, self.y = old_x, old_y
                break

    def attack(self):
        self.sword_timer = 18

    def update(self):
        if self.sword_timer > 0:
            self.sword_timer -= 1
        if self.invuln > 0:
            self.invuln -= 1

    def sword_rect(self):
        if self.sword_timer <= 0:
            return pygame.Rect(0, 0, 0, 0)
        return pygame.Rect(int(self.x + 12), int(self.y - 55), 70, 90)

    def draw(self, surface, camera):
        """Draw Aelira in a simple, cute, low-poly princess style."""
        x = int(self.x - camera.x)
        y = int(self.y - camera.y)

        if self.invuln and self.invuln % 6 < 3:
            return

        # Small ground shadow
        pygame.draw.ellipse(surface, (30, 24, 35), (x - 20, y + 34, 40, 7))

        # Dark hair behind the head and dress
        hair = (48, 27, 35)
        pygame.draw.polygon(surface, hair, [
            (x - 13, y - 54), (x + 13, y - 54),
            (x + 16, y - 33), (x + 12, y - 20),
            (x - 13, y - 20), (x - 16, y - 34)
        ])
        pygame.draw.polygon(surface, (145, 45, 58), [
            (x - 10, y - 22), (x - 23, y + 9),
            (x - 31, y + 29), (x - 8, y + 35),
            (x + 1, y + 2), (x + 11, y - 19)
        ])  # red royal cape

        # Simple white flared dress with a gold center panel
        pygame.draw.polygon(surface, (248, 248, 236), [
            (x - 9, y - 22), (x + 9, y - 22),
            (x + 17, y + 8), (x + 27, y + 37),
            (x - 27, y + 37), (x - 17, y + 8)
        ])
        pygame.draw.polygon(surface, (222, 179, 69), [
            (x - 4, y - 20), (x + 4, y - 20),
            (x + 10, y + 34), (x - 10, y + 34)
        ])
        # Small shoulders and hands
        pygame.draw.polygon(surface, (248, 248, 236), [
            (x - 10, y - 21), (x - 17, y - 12),
            (x - 12, y - 5), (x - 7, y - 14)
        ])
        pygame.draw.polygon(surface, (248, 248, 236), [
            (x + 10, y - 21), (x + 17, y - 12),
            (x + 12, y - 5), (x + 7, y - 14)
        ])

        # Cute rounded face framed by hair
        skin = (255, 220, 185)
        pygame.draw.ellipse(surface, skin, (x - 11, y - 58, 22, 27))
        pygame.draw.circle(surface, skin, (x - 10, y - 44), 3)
        pygame.draw.circle(surface, skin, (x + 10, y - 44), 3)

        # Soft fringe
        pygame.draw.polygon(surface, hair, [
            (x - 12, y - 52), (x - 10, y - 60),
            (x - 4, y - 62), (x + 2, y - 58),
            (x + 8, y - 61), (x + 13, y - 52),
            (x + 7, y - 49), (x + 1, y - 53),
            (x - 5, y - 50)
        ])
        # Tiny dark eyes, blush, and a simple smile
        pygame.draw.circle(surface, (45, 35, 36), (x - 5, y - 45), 2)
        pygame.draw.circle(surface, (45, 35, 36), (x + 5, y - 45), 2)
        pygame.draw.circle(surface, (255, 151, 157), (x - 7, y - 39), 2)
        pygame.draw.circle(surface, (255, 151, 157), (x + 7, y - 39), 2)
        pygame.draw.arc(surface, (150, 70, 75), (x - 3, y - 40, 6, 5), 0.15, 2.95, 1)

        # Bright yellow three-point crown like the reference
        pygame.draw.polygon(surface, (255, 211, 45), [
            (x - 13, y - 56), (x - 11, y - 68),
            (x - 5, y - 60), (x, y - 70),
            (x + 6, y - 60), (x + 11, y - 67),
            (x + 13, y - 56)
        ])
        pygame.draw.rect(surface, (255, 211, 45), (x - 13, y - 57, 26, 5))
        pygame.draw.circle(surface, (255, 239, 130), (x, y - 62), 2)

        # Keep the sword and attack effect
        if self.sword_timer > 0:
            glow_circle(surface, (x + 52, y - 18), 28, CYAN, 100)
            pygame.draw.polygon(surface, WHITE, [
                (x + 14, y - 8), (x + 63, y - 48),
                (x + 70, y - 41), (x + 22, y + 0)
            ])
            pygame.draw.line(surface, CYAN, (x + 16, y - 5), (x + 29, y + 7), 4)
            pygame.draw.circle(surface, GOLD, (x + 17, y - 6), 4)
        else:
            pygame.draw.line(surface, GOLD, (x + 10, y - 1), (x + 25, y + 14), 3)
            pygame.draw.line(surface, (225, 235, 250), (x + 24, y + 13), (x + 40, y + 28), 2)


# ---------- Enemies ----------
class Wraith:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 25
        self.hp = 40
        self.cooldown = random.randint(0, 60)

    def update(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if 70 < dist < 600:
            self.x += dx / dist * 1.15
            self.y += dy / dist * 1.15

        self.cooldown -= 1
        if dist < 65 and self.cooldown <= 0:
            if player.invuln <= 0:
                player.hp -= 8
                player.invuln = 45
            self.cooldown = 60

    def draw(self, surface, camera):
        x = int(self.x - camera.x)
        y = int(self.y - camera.y)
        glow_circle(surface, (x, y), 30, (140, 70, 200), 65)
        pygame.draw.ellipse(surface, (46, 31, 78),
                            (x - 25, y - 32, 50, 65))
        pygame.draw.circle(surface, (210, 95, 245), (x - 8, y - 7), 4)
        pygame.draw.circle(surface, (210, 95, 245), (x + 8, y - 7), 4)


class Guardian:
    def __init__(self):
        self.x = 2600
        self.y = 1020
        self.hp = 180
        self.max_hp = 180
        self.active = False
        self.attack_cd = 0

    def update(self, player, unlocked):
        self.active = unlocked
        if not unlocked:
            return

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist < 700 and dist > 90:
            self.x += dx / dist * 1.0
            self.y += dy / dist * 1.0

        self.attack_cd -= 1
        if dist < 100 and self.attack_cd <= 0:
            if player.invuln <= 0:
                player.hp -= 12
                player.invuln = 50
            self.attack_cd = 70

    def draw(self, surface, camera):
        x = int(self.x - camera.x)
        y = int(self.y - camera.y)

        # Boss aura
        glow_circle(surface, (x, y), 75,
                    (120, 210, 255) if self.active else (90, 80, 120), 80)

        # body / armor
        pygame.draw.ellipse(surface, (70, 72, 90),
                            (x - 48, y - 65, 96, 120))
        pygame.draw.rect(surface, (100, 105, 125),
                         (x - 38, y - 40, 76, 85), border_radius=15)
        pygame.draw.circle(surface, (125, 130, 150), (x, y - 65), 36)
        pygame.draw.rect(surface, (40, 35, 55),
                         (x - 35, y - 67, 70, 16), border_radius=5)

        # glowing core when armor is open
        if self.active:
            pygame.draw.circle(surface, CYAN, (x, y + 10), 15)
            pygame.draw.circle(surface, WHITE, (x, y + 10), 6)
        else:
            pygame.draw.circle(surface, (50, 45, 65), (x, y + 10), 15)

        # health bar
        if self.active:
            pygame.draw.rect(surface, (20, 20, 25), (x - 70, y - 105, 140, 12))
            w = int(140 * self.hp / self.max_hp)
            pygame.draw.rect(surface, RED, (x - 70, y - 105, w, 12))


# ---------- Game objects ----------
class Lever:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.on = False

    def toggle(self):
        self.on = not self.on

    def draw(self, surface, camera):
        x = int(self.x - camera.x)
        y = int(self.y - camera.y)
        col = GREEN if self.on else RED
        pygame.draw.rect(surface, (45, 40, 55),
                         (x - 15, y - 35, 30, 50), border_radius=5)
        pygame.draw.line(surface, col, (x, y - 20),
                         (x + (18 if self.on else -18), y - 45), 7)
        pygame.draw.circle(surface, col, (x, y - 20), 7)


class Rune:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False

    def draw(self, surface, camera):
        if self.collected:
            return
        x = int(self.x - camera.x)
        y = int(self.y - camera.y)
        glow_circle(surface, (x, y), 20, CYAN, 80)
        pygame.draw.polygon(
            surface, CYAN,
            [(x, y - 16), (x + 14, y), (x, y + 16), (x - 14, y)]
        )
        pygame.draw.polygon(
            surface, WHITE,
            [(x, y - 10), (x + 8, y), (x, y + 10), (x - 8, y)], 2
        )


class Seal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.opened = False

    def draw(self, surface, camera):
        x = int(self.x - camera.x)
        y = int(self.y - camera.y)
        col = GOLD if self.opened else PURPLE
        glow_circle(surface, (x, y), 55, col, 90)
        pygame.draw.circle(surface, col, (x, y), 42, 5)
        pygame.draw.polygon(
            surface, col,
            [(x, y - 28), (x + 24, y + 18), (x - 24, y + 18)]
        )
        if self.opened:
            text(surface, "THIRD SEAL", FONT_SMALL, GOLD, x, y + 65, True)


# ---------- Crystal bridge ----------
bridge_tiles = []
for i in range(16):
    bridge_tiles.append({
        "rect": pygame.Rect(690 + i * 78, 500, 76, 58),
        "gone": False,
        "timer": 0
    })


def update_bridge(player):
    for tile in bridge_tiles:
        if tile["gone"]:
            continue
        if player.rect.colliderect(tile["rect"]):
            tile["timer"] += 1
            if tile["timer"] > 45:
                tile["gone"] = True


def draw_bridge(surface, camera):
    for tile in bridge_tiles:
        if tile["gone"]:
            continue
        r = tile["rect"].move(-camera.x, -camera.y)
        pygame.draw.rect(surface, (105, 210, 235), r, border_radius=6)
        pygame.draw.rect(surface, WHITE, r, 2, border_radius=6)
        pygame.draw.line(surface, (50, 150, 180),
                         r.topleft, r.bottomright, 2)


# ---------- Four-diamond puzzle ----------
diamond_colors = [
    (240, 80, 110),
    (90, 220, 255),
    (180, 100, 245),
    (255, 215, 85)
]
sequence = [1, 3, 0, 2]
puzzle_input = []


def draw_puzzle(surface, camera):
    # Puzzle panel in the world
    x = 1180 - camera.x
    y = 430 - camera.y
    if -300 < x < WIDTH + 300 and -200 < y < HEIGHT + 200:
        pygame.draw.rect(surface, (25, 22, 45),
                         (x, y, 360, 190), border_radius=18)
        pygame.draw.rect(surface, (110, 95, 145),
                         (x, y, 360, 190), 3, border_radius=18)
        text(surface, "FOUR-DIAMOND SEAL",
             FONT_SMALL, WHITE, x + 180, y + 25, True)

        for i, col in enumerate(diamond_colors):
            cx = x + 55 + i * 85
            cy = y + 95
            pygame.draw.polygon(
                surface, col,
                [(cx, cy - 27), (cx + 25, cy),
                 (cx, cy + 27), (cx - 25, cy)]
            )
            if i in puzzle_input:
                pygame.draw.polygon(
                    surface, WHITE,
                    [(cx, cy - 32), (cx + 30, cy),
                     (cx, cy + 32), (cx - 30, cy)], 3
                )


def click_puzzle(mouse_pos, camera):
    mx, my = mouse_pos
    x = 1180 - camera.x
    y = 430 - camera.y
    for i in range(4):
        cx = x + 55 + i * 85
        cy = y + 95
        if math.hypot(mx - cx, my - cy) < 32:
            puzzle_input.append(i)
            if puzzle_input[-1] != sequence[len(puzzle_input) - 1]:
                puzzle_input.clear()
            elif len(puzzle_input) == 4:
                return True
            break
    return False


# ---------- Main game ----------
player = Player()

platform_walls = [
    pygame.Rect(0, 250, 760, 40),
    pygame.Rect(0, 250, 40, 1000),
    pygame.Rect(1980, 240, 1220, 40),
    pygame.Rect(0, 1720, 950, 40),
    pygame.Rect(2050, 1180, 1150, 40),
]

levers = [
    Lever(2140, 560),
    Lever(2340, 760),
    Lever(2850, 720)
]

runes = [
    Rune(350, 470),
    Rune(520, 560),
    Rune(620, 700)
]

guardian = Guardian()
seal = Seal(3050, 1040)

enemies = [
    Wraith(500, 900),
    Wraith(2100, 560),
    Wraith(2450, 920),
    Wraith(2900, 500)
]

camera = pygame.Vector2(0, 0)
puzzle_solved = False
game_won = False
message = "Explore the forgotten chambers..."
message_timer = 240
start_screen = True


def set_message(msg, frames=180):
    global message, message_timer
    message = msg
    message_timer = frames


def reset_game():
    global player, enemies, puzzle_input, puzzle_solved, game_won, bridge_tiles
    player = Player()
    enemies = [
        Wraith(500, 900),
        Wraith(2100, 560),
        Wraith(2450, 920),
        Wraith(2900, 500)
    ]
    puzzle_input.clear()
    puzzle_solved = False
    game_won = False
    for lever in levers:
        lever.on = False
    for rune in runes:
        rune.collected = False
    for tile in bridge_tiles:
        tile["gone"] = False
        tile["timer"] = 0
    guardian.hp = guardian.max_hp
    guardian.active = False
    guardian.attack_cd = 0
    seal.opened = False
    set_message("Aelira enters the Forgotten Underkingdom...")


def objective_text():
    collected = sum(r.collected for r in runes)
    levers_on = sum(l.on for l in levers)

    if collected < 3:
        return f"Find the hidden runes: {collected}/3"
    if not puzzle_solved:
        return "Solve the four-diamond sequence puzzle"
    if levers_on < 3:
        return f"Activate temple levers: {levers_on}/3"
    if guardian.hp > 0:
        return "Defeat the Stone Guardian"
    return "Touch the Third Seal of Wisdom"


# ---------- Main loop ----------
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            toggle_fullscreen()
            continue
        if event.type == pygame.QUIT:
            running = False

        if start_screen and event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                game_sound("start")
                start_screen = False
                reset_game()

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,
                             pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                game_sound("move")
            if event.key == pygame.K_ESCAPE:
                start_screen = True
            elif event.key in (pygame.K_SPACE, pygame.K_j):
                player.attack()
                game_sound("attack")
            elif event.key == pygame.K_r:
                game_sound("retry")
                reset_game()
            elif event.key == pygame.K_e:
                game_sound("interact")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not start_screen and not game_won:
                if click_puzzle(event.pos, camera):
                    game_sound("puzzle")
                    puzzle_solved = True
                    set_message("The four diamonds resonate! The temple awakens.", 240)

    if start_screen:
        screen.fill((8, 7, 18))
        # decorative crystals
        for i in range(7):
            draw_crystal(screen, 110 + i * 190, 560 - (i % 2) * 70, 38)

        text(screen, "LEVEL 3", FONT_TITLE, CYAN, WIDTH // 2, 110, True)
        text(screen, "THE FORGOTTEN UNDERKINGDOM",
             FONT_BIG, WHITE, WIDTH // 2, 165, True)

        text(screen,
             "Beneath Eldoria lies an ancient kingdom protecting the Third Seal.",
             FONT, (190, 190, 220), WIDTH // 2, 235, True)
        text(screen,
             "Explore • solve the diamond puzzle • activate the temple • defeat the Guardian",
             FONT_SMALL, (160, 170, 200), WIDTH // 2, 275, True)

        pygame.draw.rect(screen, (35, 30, 60),
                         (WIDTH // 2 - 270, 335, 540, 180),
                         border_radius=20)
        pygame.draw.rect(screen, PURPLE,
                         (WIDTH // 2 - 270, 335, 540, 180), 3,
                         border_radius=20)

        text(screen, "MOVE  :  WASD / ARROW KEYS",
             FONT, WHITE, WIDTH // 2, 370, True)
        text(screen, "SWORD :  SPACE / J",
             FONT, WHITE, WIDTH // 2, 410, True)
        text(screen, "PUZZLE:  LEFT CLICK DIAMONDS",
             FONT, WHITE, WIDTH // 2, 450, True)
        text(screen, "R      :  RESTART",
             FONT, WHITE, WIDTH // 2, 490, True)

        text(screen, "PRESS ENTER TO START",
             FONT_TITLE, GOLD, WIDTH // 2, 600, True)

        pygame.display.flip()
        continue

    # ---------- Update ----------
    keys = pygame.key.get_pressed()

    if not game_won:
        player.move(keys, platform_walls)
        player.update()
        update_bridge(player)

        # Runes
        for rune in runes:
            if not rune.collected:
                if math.hypot(player.x - rune.x, player.y - rune.y) < 55:
                    rune.collected = True
                    game_sound("collect")
                    set_message("Ancient rune collected!", 100)

        # Puzzle proximity
        if not puzzle_solved and math.hypot(
            player.x - 1360, player.y - 525
        ) < 280:
            set_message("Click the diamonds in the glowing sequence.", 120)

        # Levers
        for lever in levers:
            if math.hypot(player.x - lever.x, player.y - lever.y) < 65:
                if keys[pygame.K_e]:
                    # prevent repeated toggling
                    lever.toggle()
                    game_sound("interact")
                    set_message(
                        "Temple mechanism activated!" if lever.on
                        else "Lever switched off.", 70
                    )

        # Enemies
        for enemy in enemies:
            enemy.update(player)

        # Sword hits
        sword = player.sword_rect()
        if sword.width > 0:
            for enemy in enemies[:]:
                if sword.colliderect(
                    pygame.Rect(enemy.x - enemy.r, enemy.y - enemy.r,
                                enemy.r * 2, enemy.r * 2)
                ):
                    enemy.hp -= 20
                    game_sound("hurt")
                    if enemy.hp <= 0:
                        enemies.remove(enemy)
                        game_sound("defeat")
                        set_message("Shadow creature defeated!", 70)

            if guardian.active and sword.colliderect(
                pygame.Rect(guardian.x - 55, guardian.y - 70, 110, 140)
            ):
                guardian.hp -= 8
                game_sound("hurt")
                if guardian.hp <= 0:
                    guardian.hp = 0
                    game_sound("defeat")
                    set_message(
                        "The Stone Guardian falls. The Third Seal is yours!",
                        240
                    )

        all_levers = all(l.on for l in levers)
        all_runes = all(r.collected for r in runes)

        was_guardian_active = guardian.active
        guardian.update(player, all_levers and puzzle_solved and all_runes)
        if guardian.active and not was_guardian_active:
            game_sound("gate")
            set_message("The Stone Guardian awakens!", 180)

        # Seal becomes available after Guardian is defeated.
        if guardian.hp <= 0 and math.hypot(
            player.x - seal.x, player.y - seal.y
        ) < 75:
            seal.opened = True
            game_won = True
            game_sound("victory")
            set_message(
                "Aelira obtains the Third Seal of Wisdom!", 999999
            )

        # Death / restart
        if player.hp <= 0:
            set_message("Aelira has fallen. Press R to try again.", 999999)

        # Camera
        target_x = player.x - WIDTH / 2
        target_y = player.y - HEIGHT / 2
        camera.x += (target_x - camera.x) * 0.08
        camera.y += (target_y - camera.y) * 0.08
        camera.x = clamp(camera.x, 0, WORLD_W - WIDTH)
        camera.y = clamp(camera.y, 0, WORLD_H - HEIGHT)

    # ---------- Draw ----------
    draw_cave(screen, camera)
    draw_bridge(screen, camera)
    draw_puzzle(screen, camera)

    for rune in runes:
        rune.draw(screen, camera)

    for lever in levers:
        lever.draw(screen, camera)

    for enemy in enemies:
        enemy.draw(screen, camera)

    guardian.draw(screen, camera)
    seal.draw(screen, camera)
    player.draw(screen, camera)

    # HUD
    pygame.draw.rect(screen, (10, 9, 22), (18, 16, 410, 120),
                     border_radius=16)
    pygame.draw.rect(screen, (105, 90, 145), (18, 16, 410, 120), 2,
                     border_radius=16)

    text(screen, "AELIRA", FONT_TITLE, WHITE, 35, 27)

    # HP
    pygame.draw.rect(screen, (35, 30, 45), (35, 72, 220, 18),
                     border_radius=8)
    hpw = int(220 * clamp(player.hp, 0, player.max_hp) / player.max_hp)
    pygame.draw.rect(screen, RED, (35, 72, hpw, 18), border_radius=8)
    text(screen, f"HP {max(0, player.hp)}/100",
         FONT_SMALL, WHITE, 270, 70)

    text(screen, "Objective:", FONT_SMALL, GOLD, 35, 100)
    text(screen, objective_text(), FONT_SMALL, WHITE, 125, 100)

    # Message
    if message_timer > 0:
        message_timer -= 1
        box = pygame.Surface((WIDTH - 200, 55), pygame.SRCALPHA)
        box.fill((10, 8, 25, 205))
        screen.blit(box, (100, HEIGHT - 78))
        text(screen, message, FONT_SMALL, WHITE,
             WIDTH // 2, HEIGHT - 51, True)

    # Boss warning
    if guardian.active and guardian.hp > 0:
        text(screen, "STONE GUARDIAN AWAKENED!",
             FONT_TITLE, RED, WIDTH // 2, 28, True)

    # Win screen
    if game_won:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 4, 15, 175))
        screen.blit(overlay, (0, 0))

        text(screen, "THIRD SEAL OF WISDOM",
             FONT_BIG, GOLD, WIDTH // 2, 235, True)
        text(screen, "Aelira has opened the path to the Shadow King's fortress.",
             FONT, WHITE, WIDTH // 2, 300, True)
        text(screen, "LEVEL 3 COMPLETE",
             FONT_TITLE, CYAN, WIDTH // 2, 355, True)
        text(screen, "Press R to play Level 3 again",
             FONT, (210, 210, 230), WIDTH // 2, 430, True)

    pygame.display.flip()

    # Return to the combined launcher after this level is won or lost.
    if game_won:
        pygame.time.wait(900)
        sys.exit(0)
    if player.hp <= 0:
        pygame.time.wait(700)
        sys.exit(1)

pygame.quit()
sys.exit(1)

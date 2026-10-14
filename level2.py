import os
import sys
import math
import pygame

# Sunfire Citadel: Princess Aelira's Adventure
# Python 3.13 + Pygame
# Install: py -3.13 -m pip install pygame
# Run:     py -3.13 sunfire_princess.py

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
    audio_support.start_music(2)


WIDTH, HEIGHT = 1000, 600
FPS = 60
GROUND = 500
WORLD_WIDTH = 2600

FULLSCREEN = False
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
pygame.display.set_caption("Sunfire Citadel - Princess Aelira")

def toggle_fullscreen():
    """Toggle fullscreen with F11 while keeping the game's logical resolution."""
    global screen, FULLSCREEN
    FULLSCREEN = not FULLSCREEN
    flags = pygame.SCALED | (pygame.FULLSCREEN if FULLSCREEN else 0)
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("Sunfire Citadel - Princess Aelira")
    return screen
clock = pygame.time.Clock()
font = pygame.font.SysFont("georgia", 21, bold=True)
small = pygame.font.SysFont("georgia", 16)
large = pygame.font.SysFont("georgia", 42, bold=True)

BASE = os.path.dirname(os.path.abspath(__file__))
try:
    bg_image = pygame.image.load(os.path.join(BASE, "desert_fortress.png")).convert()
    bg_image = pygame.transform.smoothscale(bg_image, (WIDTH, HEIGHT))
except (pygame.error, FileNotFoundError):
    bg_image = None

IVORY = (255, 238, 205)
GOLD = (255, 193, 55)
DARK = (30, 22, 25)
RED = (170, 35, 50)
BLUE = (40, 80, 155)
SKIN = (241, 190, 143)
GREEN = (50, 205, 95)


def text(msg, x, y, color=IVORY, f=font):
    screen.blit(f.render(msg, True, color), (x, y))


def draw_princess(x, y, facing, sword_up=False, flicker=False):
    """Draw Princess Aelira with a crown, long hair, ivory gown and red cape."""
    if flicker:
        return
    # flowing cape
    cape_points = [(x + 12, y + 23), (x - 17, y + 40),
                   (x - 25, y + 57), (x + 10, y + 49)]
    if facing < 0:
        cape_points = [(x + 22, y + 23), (x + 48, y + 40),
                       (x + 54, y + 57), (x + 20, y + 49)]
    pygame.draw.polygon(screen, (125, 20, 40), cape_points)
    pygame.draw.polygon(screen, (210, 45, 57), [cape_points[0], cape_points[1], cape_points[3]])
    # hair behind face
    pygame.draw.ellipse(screen, (68, 32, 27), (x + 5, y + 1, 25, 31))
    # gown
    pygame.draw.polygon(screen, (255, 239, 211),
                        [(x + 9, y + 23), (x + 28, y + 23),
                         (x + 40, y + 56), (x - 1, y + 56)])
    pygame.draw.polygon(screen, (214, 165, 73),
                        [(x + 17, y + 25), (x + 21, y + 25),
                         (x + 27, y + 53), (x + 15, y + 53)])
    # arms
    pygame.draw.line(screen, SKIN, (x + 10, y + 28), (x + 1, y + 39), 6)
    pygame.draw.line(screen, SKIN, (x + 28, y + 28), (x + 35, y + 37), 6)
    # face and hair
    pygame.draw.ellipse(screen, SKIN, (x + 9, y + 4, 18, 21))
    pygame.draw.arc(screen, (68, 32, 27), (x + 5, y, 25, 24), 0, math.pi, 5)
    pygame.draw.circle(screen, (40, 28, 25), (x + 22, y + 14), 2)
    # gold crown
    pygame.draw.rect(screen, GOLD, (x + 9, y + 2, 19, 5))
    pygame.draw.polygon(screen, GOLD, [(x + 9, y + 3), (x + 12, y - 5),
                                       (x + 17, y + 2), (x + 22, y - 5),
                                       (x + 28, y + 3)])
    # sword
    if sword_up:
        if facing > 0:
            pygame.draw.line(screen, (245, 250, 255), (x + 35, y + 37), (x + 55, y + 17), 4)
            pygame.draw.line(screen, GOLD, (x + 31, y + 39), (x + 39, y + 31), 5)
        else:
            pygame.draw.line(screen, (245, 250, 255), (x - 2, y + 37), (x - 22, y + 17), 4)
            pygame.draw.line(screen, GOLD, (x + 2, y + 39), (x - 6, y + 31), 5)


def draw_guard(x, y, rescued=False):
    """Royal soldiers wear polished blue-and-gold armour."""
    # boots
    pygame.draw.rect(screen, (48, 42, 40), (x + 5, y + 43, 9, 10))
    pygame.draw.rect(screen, (48, 42, 40), (x + 19, y + 43, 9, 10))
    # royal blue tunic / armour
    pygame.draw.rect(screen, (35, 74, 145), (x + 3, y + 17, 27, 29), border_radius=4)
    pygame.draw.polygon(screen, GOLD, [(x + 16, y + 20), (x + 22, y + 29),
                                      (x + 16, y + 37), (x + 10, y + 29)])
    pygame.draw.rect(screen, GOLD, (x + 3, y + 28, 27, 4))
    # face and helmet
    pygame.draw.circle(screen, SKIN, (x + 16, y + 10), 10)
    pygame.draw.arc(screen, (205, 210, 220), (x + 5, y, 22, 17), math.pi, 2 * math.pi, 5)
    pygame.draw.rect(screen, (190, 198, 211), (x + 5, y + 5, 22, 5))
    pygame.draw.polygon(screen, GOLD, [(x + 16, y - 4), (x + 11, y + 4), (x + 21, y + 4)])
    if rescued:
        pygame.draw.circle(screen, GREEN, (x + 16, y - 10), 5)


class Enemy:
    def __init__(self, x, boss=False):
        self.x = x
        self.boss = boss
        self.w = 54 if boss else 34
        self.h = 78 if boss else 51
        self.y = GROUND - self.h
        self.hp = 10 if boss else 3
        self.alive = True
        self.cooldown = 0

    def update(self, hero):
        if not self.alive:
            return
        distance = hero.centerx - (self.x + self.w // 2)
        if abs(distance) < 360 and abs(distance) > 45:
            self.x += 1 if distance > 0 else -1
        if self.cooldown > 0:
            self.cooldown -= 1
        enemy_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        if enemy_rect.colliderect(hero) and self.cooldown == 0 and hero_invincible[0] == 0:
            hero_health[0] -= 12 if self.boss else 7
            hero_invincible[0] = 50
            self.cooldown = 45

    def draw(self, camera):
        if not self.alive:
            return
        x = int(self.x - camera)
        armor = (72, 35, 49) if self.boss else (126, 43, 39)
        pygame.draw.rect(screen, armor, (x, self.y + 15, self.w, self.h - 15), border_radius=5)
        pygame.draw.circle(screen, (194, 145, 107), (x + self.w // 2, self.y + 10), 12)
        pygame.draw.rect(screen, (42, 30, 35), (x + 4, self.y + 1, self.w - 8, 8))
        pygame.draw.rect(screen, GOLD, (x + 4, self.y + 25, self.w - 8, 4))
        pygame.draw.rect(screen, (45, 35, 36), (x + 4, self.y + self.h - 9, 10, 9))
        pygame.draw.rect(screen, (45, 35, 36), (x + self.w - 14, self.y + self.h - 9, 10, 9))
        if self.boss:
            pygame.draw.polygon(screen, GOLD, [(x + 5, self.y + 6), (x + 12, self.y - 12), (x + 20, self.y + 6)])
            pygame.draw.polygon(screen, GOLD, [(x + 34, self.y + 6), (x + 42, self.y - 12), (x + 49, self.y + 6)])
            pygame.draw.rect(screen, RED, (x, self.y - 22, self.w, 7))
            pygame.draw.rect(screen, GREEN, (x, self.y - 22, int(self.w * max(0, self.hp) / 10), 7))


def reset_game():
    global hero, hero_health, hero_invincible, enemies, boss, machines, prisoners
    global rescued, camera, attacking, facing, vy, won, lost, message, message_timer
    hero = pygame.Rect(120, GROUND - 56, 34, 56)
    hero_health = [100]
    hero_invincible = [0]
    enemies = [Enemy(x) for x in (420, 760, 1050, 1450, 1770, 2040)]
    boss = Enemy(2350, boss=True)
    machines = [
        {"x": 650, "off": False, "time": 45 * FPS},
        {"x": 1300, "off": False, "time": 55 * FPS},
        {"x": 1900, "off": False, "time": 65 * FPS},
    ]
    prisoners = [560, 1120, 1660]
    rescued = 0
    camera = 0
    attacking = 0
    facing = 1
    vy = 0
    won = False
    lost = False
    message = "Rescue the royal soldiers, disable all siege machines, defeat the Fire Commander!"
    message_timer = 300


reset_game()
running = True

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and (event.key == pygame.K_F11 or (event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT)):
            toggle_fullscreen()
            continue
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT):
                game_sound("move")
            elif event.key == pygame.K_SPACE:
                game_sound("jump")
            elif event.key == pygame.K_j:
                game_sound("attack")
            elif event.key == pygame.K_e:
                game_sound("interact")
            elif event.key == pygame.K_r:
                game_sound("retry")
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r and (won or lost):
                reset_game()
            if not won and not lost:
                if event.key == pygame.K_SPACE and hero.bottom >= GROUND:
                    vy = -14
                elif event.key == pygame.K_j and attacking == 0:
                    attacking = 12
                elif event.key == pygame.K_e:
                    close_prisoner = next((s for s in prisoners if abs(s - hero.centerx) < 75), None)
                    close_machine = next((m for m in machines if not m["off"] and abs(m["x"] - hero.centerx) < 75), None)
                    if close_prisoner is not None:
                        prisoners.remove(close_prisoner)
                        game_sound("rescue")
                        rescued += 1
                        hero_health[0] = min(100, hero_health[0] + 8)
                        message = "A royal soldier has joined your cause!"
                        message_timer = 150
                    elif close_machine is not None:
                        close_machine["off"] = True
                        game_sound("gate")
                        message = "Siege machine disabled!"
                        message_timer = 150
                    else:
                        message = "Move close to a cage or siege machine, then press E."
                        message_timer = 150

    if not won and not lost:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            hero.x -= 5
            facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            hero.x += 5
            facing = 1
        hero.x = max(0, min(WORLD_WIDTH - hero.width, hero.x))
        vy += 0.7
        hero.y += int(vy)
        if hero.bottom >= GROUND:
            hero.bottom = GROUND
            vy = 0

        if attacking > 0:
            attacking -= 1
            sword = pygame.Rect(hero.right if facing > 0 else hero.left - 52,
                                hero.y + 12, 52, 32)
            for enemy in enemies + [boss]:
                if enemy.alive and sword.colliderect(pygame.Rect(enemy.x, enemy.y, enemy.w, enemy.h)):
                    enemy.hp -= 1
                    if enemy.hp <= 0:
                        enemy.alive = False

        for enemy in enemies + [boss]:
            enemy.update(hero)

        for machine in machines:
            if not machine["off"]:
                machine["time"] -= 1
                if machine["time"] <= 0:
                    hero_health[0] -= 10
                    machine["time"] = 25 * FPS
                    message = "Siege fire! Disable the machines with E."
                    message_timer = 120

        if hero_invincible[0] > 0:
            hero_invincible[0] -= 1
        if hero_health[0] <= 0:
            hero_health[0] = 0
            lost = True
        if all(m["off"] for m in machines) and not boss.alive:
            won = True
        camera = max(0, min(WORLD_WIDTH - WIDTH, hero.centerx - WIDTH // 2))

    # Background
    if bg_image:
        screen.blit(bg_image, (0, 0))
        # gentle parallax repeat for the long side-scrolling world
        offset = int(camera * 0.12) % WIDTH
        screen.blit(bg_image, (WIDTH - offset, 0))
        screen.blit(bg_image, (-offset, 0))
    else:
        screen.fill((238, 166, 95))
        pygame.draw.circle(screen, (255, 230, 140), (130, 110), 45)
        for x in range(0, WIDTH, 100):
            pygame.draw.rect(screen, (178, 121, 67), (x, 300, 80, 200))
    pygame.draw.rect(screen, (225, 171, 88), (0, GROUND, WIDTH, HEIGHT - GROUND))
    pygame.draw.rect(screen, (107, 59, 36), (0, GROUND + 27, WIDTH, HEIGHT - GROUND - 27))
    for i in range(36):
        sx = (i * 89 - int(camera * 1.5)) % WIDTH
        pygame.draw.ellipse(screen, (151, 91, 46), (sx, GROUND + 40 + (i % 3) * 13, 24, 7))

    # Siege machines
    for m in machines:
        x = int(m["x"] - camera)
        if -70 < x < WIDTH + 70:
            pygame.draw.line(screen, (75, 43, 28), (x - 25, GROUND - 5), (x + 16, GROUND - 80), 9)
            pygame.draw.line(screen, (75, 43, 28), (x + 24, GROUND - 5), (x + 16, GROUND - 80), 9)
            pygame.draw.circle(screen, (92, 57, 35), (x + 16, GROUND - 80), 14)
            label = "OFF" if m["off"] else f"{max(0, m['time'] // FPS)}s"
            text(label, x - 18, GROUND - 115, GREEN if m["off"] else GOLD, small)

    # Imprisoned soldiers: elegant royal armour, cage and E prompt
    for s in prisoners:
        x = int(s - camera)
        if -60 < x < WIDTH + 60:
            pygame.draw.rect(screen, (70, 54, 44), (x - 8, GROUND - 55, 43, 55), 3)
            for barx in (x, x + 10, x + 20, x + 30):
                pygame.draw.line(screen, (174, 153, 119), (barx, GROUND - 55), (barx, GROUND), 2)
            draw_guard(x, GROUND - 53)
            text("E", x + 8, GROUND - 83, GOLD, small)

    # Enemies and princess
    for enemy in enemies:
        enemy.draw(camera)
    boss.draw(camera)
    flicker = hero_invincible[0] > 0 and hero_invincible[0] % 8 < 4
    draw_princess(int(hero.x - camera), hero.y, facing, attacking > 0, flicker)

    # HUD panels
    pygame.draw.rect(screen, (25, 20, 27), (12, 12, 270, 92), border_radius=12)
    pygame.draw.rect(screen, GOLD, (12, 12, 270, 92), 2, border_radius=12)
    text(f"Princess Aelira  HP: {hero_health[0]}", 25, 20, IVORY, small)
    pygame.draw.rect(screen, (95, 28, 35), (25, 47, 220, 15), border_radius=5)
    pygame.draw.rect(screen, GREEN, (25, 47, int(220 * hero_health[0] / 100), 15), border_radius=5)
    text(f"Soldiers rescued: {rescued}/3", 25, 69, GOLD, small)
    text(f"Siege machines: {sum(m['off'] for m in machines)}/3", 25, 86, GOLD, small)

    pygame.draw.rect(screen, (25, 20, 27), (300, 12, 690, 52), border_radius=10)
    pygame.draw.rect(screen, GOLD, (300, 12, 690, 52), 2, border_radius=10)
    text("SAVE THE SUNFIRE CITADEL", 480, 18, GOLD, small)
    text("Rescue soldiers • Disable siege engines • Defeat the Fire Commander", 325, 39, IVORY, small)

    pygame.draw.rect(screen, (25, 20, 27), (12, HEIGHT - 78, 610, 65), border_radius=10)
    pygame.draw.rect(screen, GOLD, (12, HEIGHT - 78, 610, 65), 2, border_radius=10)
    text("A/D or arrows: Move     SPACE: Jump     J: Sword attack", 25, HEIGHT - 69, IVORY, small)
    text("E: Rescue / disable     R: Restart after game     ESC: Exit", 25, HEIGHT - 42, IVORY, small)

    if message_timer > 0 and not won and not lost:
        pygame.draw.rect(screen, (25, 20, 27), (250, 75, 700, 34), border_radius=8)
        text(message, 263, 82, GOLD, small)
        message_timer -= 1

    if won or lost:
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((15, 10, 15, 205))
        screen.blit(veil, (0, 0))
        title = "SUNFIRE CITADEL SAVED!" if won else "THE PRINCESS HAS FALLEN"
        color = GOLD if won else (255, 100, 95)
        title_img = large.render(title, True, color)
        screen.blit(title_img, title_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
        sub = "Aelira has defeated the Fire Commander." if won else "Try again, Princess Aelira!"
        sub_img = font.render(sub, True, IVORY)
        screen.blit(sub_img, sub_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
        hint = small.render("Press R to restart  |  ESC to quit", True, IVORY)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 58)))

    pygame.display.flip()

    # The launcher takes over after victory/defeat; no window closing needed.
    if won:
        pygame.time.wait(1000)
        sys.exit(0)
    if lost:
        pygame.time.wait(700)
        sys.exit(1)

pygame.quit()
sys.exit(1)

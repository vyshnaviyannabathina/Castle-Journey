import pygame
import random
import math
import sys

pygame.init()

# CASTLE JOURNEY - LEVEL 1: THE FALL OF ELDORIA

WIDTH, HEIGHT = 1000, 650
WORLD_W, WORLD_H = 1800, 1200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Castle Journey - Level 1")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 22)
small = pygame.font.SysFont("arial", 17)
big = pygame.font.SysFont("arial", 42, bold=True)

WHITE = (245, 245, 245)
BLACK = (20, 20, 28)
GOLD = (245, 195, 55)
BLUE = (40, 95, 190)
RED = (170, 40, 55)
PURPLE = (100, 40, 135)
GREEN = (63, 135, 75)
DARKGREEN = (43, 105, 57)
STONE = (125, 126, 137)
DARKSTONE = (69, 70, 82)
BROWN = (115, 72, 40)
PINK = (225, 130, 150)

def make_game():
    return {
        "player": pygame.Rect(110, 150, 34, 42),
        "health": 100,
        "coins": 0,
        "score": 0,
        "rescued": 0,
        "chest_open": False,
        "statue_count": 0,
        "statues_solved": False,
        "boss_defeated": False,
        "state": "playing",
        "start": pygame.time.get_ticks(),
        "attack_until": 0,
        "invulnerable": 0,
        "boss_hit": 0,
        "message": "Rescue villagers and defeat the shadow soldiers!",
        "message_until": pygame.time.get_ticks() + 4000,
        "coins_list": [
            pygame.Rect(x, y, 18, 18)
            for x, y in [
                (245, 240), (420, 430), (650, 260),
                (760, 610), (1010, 390), (1280, 740),
                (1450, 440), (520, 800), (950, 900),
                (1500, 900)
            ]
        ],
        "villagers": [
            {"rect": pygame.Rect(x, y, 28, 36), "rescued": False}
            for x, y in [
                (330, 330), (560, 530),
                (850, 270), (1120, 640)
            ]
        ],
        "statues": [
            pygame.Rect(x, 760, 42, 55)
            for x in (650, 720, 790, 860)
        ],
        "chest": pygame.Rect(1420, 850, 48, 38),
        "enemies": [
            {
                "rect": pygame.Rect(x, y, 34, 40),
                "health": 40,
                "alive": True,
                "speed": speed
            }
            for x, y, speed in [
                (400, 210, 1.4),
                (720, 440, 1.7),
                (980, 560, 1.5),
                (1220, 330, 1.8),
                (1350, 700, 1.6)
            ]
        ],
        "boss": {
            "rect": pygame.Rect(1510, 250, 54, 62),
            "health": 160,
            "alive": True
        }
    }

game = make_game()

buildings = [
    (220, 90, 150, 110),
    (480, 90, 130, 100),
    (900, 100, 170, 120),
    (1160, 120, 130, 100),
    (250, 650, 150, 110),
    (1020, 850, 180, 120)
]

trees = [
    (80, 300), (170, 480), (440, 600),
    (600, 150), (900, 450), (1100, 300),
    (1300, 520), (1600, 600), (350, 900),
    (700, 1000), (1200, 1000), (1650, 950),
    (90, 780), (1500, 120)
]

def show_message(text, duration=3000):
    game["message"] = text
    game["message_until"] = pygame.time.get_ticks() + duration

def text_on_screen(text, x, y, color=WHITE, chosen_font=font):
    image = chosen_font.render(text, True, color)
    screen.blit(image, (x, y))

def nearby(a, b, distance=75):
    return (
        abs(a.centerx - b.centerx) < distance
        and abs(a.centery - b.centery) < distance
    )

def draw_building(building, cx, cy):
    x, y, w, h = building
    r = pygame.Rect(x-cx, y-cy, w, h)

    pygame.draw.rect(screen, STONE, r, border_radius=4)
    pygame.draw.rect(screen, DARKSTONE, r, 4, border_radius=4)

    roof = [
        (r.left-8, r.top+8),
        (r.centerx, r.top-28),
        (r.right+8, r.top+8)
    ]
    pygame.draw.polygon(screen, RED, roof)
    pygame.draw.polygon(screen, GOLD, roof, 3)

    for wx in (r.left+25, r.centerx-8, r.right-40):
        pygame.draw.rect(
            screen, BLUE, (wx, r.top+28, 18, 26),
            border_radius=5
        )
        pygame.draw.line(
            screen, GOLD, (wx+9, r.top+28),
            (wx+9, r.top+54), 2
        )

    pygame.draw.rect(
        screen, BROWN,
        (r.centerx-16, r.bottom-42, 32, 42)
    )

def draw_tree(x, y, cx, cy):
    sx, sy = x-cx, y-cy
    pygame.draw.rect(screen, BROWN, (sx-6, sy+15, 12, 28))
    pygame.draw.circle(screen, DARKGREEN, (sx, sy), 27)
    pygame.draw.circle(screen, (46, 150, 68), (sx-12, sy-7), 17)
    pygame.draw.circle(screen, (70, 165, 75), (sx+12, sy-9), 16)

def draw_person(rect, cx, cy, kind):
    r = pygame.Rect(
        rect.x-cx, rect.y-cy, rect.w, rect.h
    )

    if kind == "player":
        # Princess Aelira's red cape
        pygame.draw.polygon(
            screen, RED,
            [
                (r.left+6, r.top+14),
                (r.left-5, r.bottom-2),
                (r.centerx+5, r.bottom-4),
                (r.right-4, r.top+14)
            ]
        )

        # Blue and gold armour
        pygame.draw.rect(
            screen, BLUE,
            (r.left+5, r.top+12, r.w-10, r.h-14),
            border_radius=7
        )
        pygame.draw.rect(
            screen, GOLD,
            (r.left+10, r.top+16, r.w-20, 18), 2
        )

        # Face and crown
        pygame.draw.circle(
            screen, (238, 190, 150),
            (r.centerx, r.top+8), 10
        )
        pygame.draw.polygon(
            screen, GOLD,
            [
                (r.centerx-9, r.top+2),
                (r.centerx-6, r.top-7),
                (r.centerx, r.top),
                (r.centerx+6, r.top-7),
                (r.centerx+9, r.top+2)
            ]
        )

        if pygame.time.get_ticks() < game["attack_until"]:
            pygame.draw.line(
                screen, WHITE,
                (r.right-1, r.top+21),
                (r.right+27, r.top+4), 5
            )

    elif kind == "villager":
        pygame.draw.circle(
            screen, (238, 190, 150),
            (r.centerx, r.top+8), 8
        )
        pygame.draw.rect(
            screen, PINK,
            (r.left+3, r.top+16, r.w-6, r.h-16),
            border_radius=5
        )

    else:
        colour = PURPLE if kind == "boss" else (63, 35, 85)
        pygame.draw.rect(screen, colour, r, border_radius=7)
        pygame.draw.circle(
            screen, RED, (r.centerx-7, r.top+12), 4
        )
        pygame.draw.circle(
            screen, RED, (r.centerx+7, r.top+12), 4
        )

        if kind == "boss":
            pygame.draw.rect(
                screen, RED,
                (r.left-5, r.top-13, r.w+10, 7)
            )
            bar_width = max(
                0, int((r.w+10)*game["boss"]["health"]/160)
            )
            pygame.draw.rect(
                screen, (35, 190, 90),
                (r.left-5, r.top-13, bar_width, 7)
            )

def draw_world(cx, cy):
    screen.fill(GREEN)

    # Roads through Eldoria
    pygame.draw.rect(
        screen, (160, 135, 105),
        (80-cx, 300-cy, 1500, 75)
    )
    pygame.draw.rect(
        screen, (160, 135, 105),
        (690-cx, 100-cy, 75, 900)
    )
    pygame.draw.rect(
        screen, (160, 135, 105),
        (1080-cx, 560-cy, 600, 70)
    )

    for building in buildings:
        draw_building(building, cx, cy)

    for x, y in trees:
        draw_tree(x, y, cx, cy)

    # Small fires in the attacked kingdom
    for fx, fy in [(300, 280), (340, 320), (1180, 530), (1210, 565)]:
        sx, sy = fx-cx, fy-cy
        pygame.draw.ellipse(
            screen, RED, (sx-14, sy-8, 28, 24)
        )
        pygame.draw.polygon(
            screen, GOLD,
            [(sx, sy+8), (sx-8, sy-5),
             (sx, sy-22), (sx+8, sy-5)]
        )

    # Coins
    for coin in game["coins_list"]:
        pygame.draw.circle(
            screen, GOLD,
            (coin.centerx-cx, coin.centery-cy), 10
        )
        pygame.draw.circle(
            screen, (255, 235, 130),
            (coin.centerx-cx, coin.centery-cy), 5
        )

    # Villagers
    for villager in game["villagers"]:
        if not villager["rescued"]:
            draw_person(villager["rect"], cx, cy, "villager")

    # Four royal statues
    for i, statue in enumerate(game["statues"]):
        r = pygame.Rect(
            statue.x-cx, statue.y-cy,
            statue.w, statue.h
        )
        colour = GOLD if game["statues_solved"] else STONE
        pygame.draw.rect(screen, colour, r, border_radius=5)
        pygame.draw.circle(
            screen, BLUE, (r.centerx, r.top+13), 8
        )
        text_on_screen(str(i+1), r.x+14, r.y+30, BLACK, small)

    # Hidden treasure chest
    chest = game["chest"]
    cr = pygame.Rect(
        chest.x-cx, chest.y-cy, chest.w, chest.h
    )
    chest_colour = GOLD if game["chest_open"] else BROWN
    pygame.draw.rect(screen, chest_colour, cr, border_radius=5)
    pygame.draw.rect(
        screen, GOLD, (cr.x, cr.y+12, cr.w, 6)
    )

    # Shadow soldiers
    for enemy in game["enemies"]:
        if enemy["alive"]:
            draw_person(enemy["rect"], cx, cy, "enemy")

    # Traitor Knight boss
    boss = game["boss"]
    if boss["alive"]:
        draw_person(boss["rect"], cx, cy, "boss")

    draw_person(game["player"], cx, cy, "player")

def draw_hud(elapsed):
    pygame.draw.rect(
        screen, (20, 28, 45), (12, 10, 430, 112),
        border_radius=10
    )
    pygame.draw.rect(
        screen, GOLD, (12, 10, 430, 112), 2,
        border_radius=10
    )

    text_on_screen("PRINCESS AELIRA", 25, 18, GOLD)
    text_on_screen(
        f"Health: {max(0, game['health'])}", 25, 47
    )

    pygame.draw.rect(
        screen, RED, (115, 51, 140, 14),
        border_radius=4
    )
    pygame.draw.rect(
        screen, (35, 190, 90),
        (115, 51, int(140*max(0, game['health'])/100), 14),
        border_radius=4
    )

    text_on_screen(
        f"Coins: {game['coins']}   Score: {game['score']}",
        25, 73
    )

    remaining = max(0, 240-elapsed)
    text_on_screen(
        f"Time: {remaining//60:02d}:{remaining%60:02d}",
        290, 47, GOLD
    )
    text_on_screen(
        f"Villagers: {game['rescued']}/4",
        290, 73, WHITE, small
    )

    text_on_screen(
        "Move: WASD/Arrows | Attack: SPACE | Interact: E",
        20, HEIGHT-30, WHITE, small
    )

    if pygame.time.get_ticks() < game["message_until"]:
        box = pygame.Rect(220, HEIGHT-78, 760, 38)
        pygame.draw.rect(
            screen, (25, 25, 35), box, border_radius=8
        )
        pygame.draw.rect(
            screen, GOLD, box, 2, border_radius=8
        )
        text_on_screen(
            game["message"], box.x+12, box.y+9, WHITE, small
        )

def draw_end_screen():
    screen.fill((20, 25, 45))
    pygame.draw.rect(
        screen, GOLD, (70, 70, WIDTH-140, HEIGHT-140),
        4, border_radius=20
    )

    if game["state"] == "won":
        text_on_screen("LEVEL 1 COMPLETE!", 125, 145, GOLD, big)
        text_on_screen(
            "Eldoria has hope again, Princess Aelira!", 130, 230
        )
        text_on_screen(
            "You recovered the First Seal of Courage!",
            130, 300, (35, 220, 130)
        )
        text_on_screen(
            "A map to Sunfire Citadel has been discovered.",
            130, 340
        )
        text_on_screen(
            "Your first knight is ready to join the journey.",
            130, 380
        )
    else:
        text_on_screen("GAME OVER", 125, 145, RED, big)
        text_on_screen(
            "The shadows have overwhelmed Eldoria.", 130, 230
        )

    text_on_screen(
        f"Final score: {game['score']}", 130, 435, GOLD, big
    )
    text_on_screen(
        f"Coins: {game['coins']}   Villagers rescued: {game['rescued']}/4",
        130, 495
    )
    text_on_screen(
        "Press R to play again or ESC to quit", 130, 550, GOLD
    )

running = True

while running:
    clock.tick(60)
    now = pygame.time.get_ticks()
    elapsed = (now-game["start"])//1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if game["state"] in ("won", "lost") and event.key == pygame.K_r:
                game = make_game()

            elif game["state"] == "playing":
                if event.key == pygame.K_SPACE:
                    game["attack_until"] = now + 250

                    # Attack nearby shadow soldiers
                    for enemy in game["enemies"]:
                        if enemy["alive"] and nearby(
                            game["player"], enemy["rect"], 78
                        ):
                            enemy["health"] -= 20
                            if enemy["health"] <= 0:
                                enemy["alive"] = False
                                game["score"] += 100
                                game["coins"] += 2
                                show_message(
                                    "Shadow soldier defeated! +100 score, +2 coins"
                                )

                    # Attack the boss
                    boss = game["boss"]
                    if boss["alive"] and nearby(
                        game["player"], boss["rect"], 85
                    ) and now-game["boss_hit"] > 350:
                        boss["health"] -= 20
                        game["boss_hit"] = now

                        if boss["health"] <= 0:
                            boss["alive"] = False
                            game["boss_defeated"] = True
                            game["score"] += 500
                            show_message(
                                "Traitor Knight defeated! Eldoria is safe!"
                            )

                elif event.key == pygame.K_e:
                    interacted = False

                    # Rescue villagers
                    for villager in game["villagers"]:
                        if (
                            not villager["rescued"]
                            and nearby(game["player"], villager["rect"], 75)
                        ):
                            villager["rescued"] = True
                            game["rescued"] += 1
                            game["score"] += 150
                            show_message("Villager rescued! +150 score")
                            interacted = True
                            break

                    # Open chest
                    if (
                        not interacted
                        and not game["chest_open"]
                        and nearby(game["player"], game["chest"], 80)
                    ):
                        game["chest_open"] = True
                        game["coins"] += 10
                        game["score"] += 200
                        show_message(
                            "Hidden armory opened! +10 coins and +200 score"
                        )
                        interacted = True

                    # Activate statue puzzle
                    if (
                        not interacted
                        and not game["statues_solved"]
                        and any(
                            nearby(game["player"], statue, 90)
                            for statue in game["statues"]
                        )
                    ):
                        game["statue_count"] += 1
                        if game["statue_count"] >= 4:
                            game["statues_solved"] = True
                            game["score"] += 250
                            show_message(
                                "The four statues glow! Royal passage opened."
                            )
                        else:
                            show_message(
                                f"Statue activated ({game['statue_count']}/4)"
                            )
                        interacted = True

                    if not interacted:
                        show_message(
                            "Move near a villager, chest, or statue and press E."
                        )

    if game["state"] == "playing":
        keys = pygame.key.get_pressed()
        dx = dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 4
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 4
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 4
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 4

        if dx and dy:
            dx = int(dx * 0.707)
            dy = int(dy * 0.707)

        player = game["player"]
        player.x = max(0, min(WORLD_W-player.w, player.x+dx))
        player.y = max(0, min(WORLD_H-player.h, player.y+dy))

        # Collect coins
        for coin in game["coins_list"][:]:
            if player.colliderect(coin):
                game["coins_list"].remove(coin)
                game["coins"] += 1
                game["score"] += 25
                show_message("Coin collected! +25 score", 1000)

        # Shadow soldiers chase the player
        for enemy in game["enemies"]:
            if not enemy["alive"]:
                continue

            ex = player.centerx-enemy["rect"].centerx
            ey = player.centery-enemy["rect"].centery
            distance = max(1, math.hypot(ex, ey))

            if distance < 300:
                enemy["rect"].x += int(enemy["speed"]*ex/distance)
                enemy["rect"].y += int(enemy["speed"]*ey/distance)

            if (
                player.colliderect(enemy["rect"])
                and now > game["invulnerable"]
            ):
                game["health"] -= 10
                game["invulnerable"] = now + 850
                show_message("A shadow soldier hit you! Keep moving.")

        # Boss movement and damage
        boss = game["boss"]
        if boss["alive"]:
            bx = player.centerx-boss["rect"].centerx
            by = player.centery-boss["rect"].centery
            distance = max(1, math.hypot(bx, by))

            if distance < 420:
                boss["rect"].x += int(1.2*bx/distance)
                boss["rect"].y += int(1.2*by/distance)

            if (
                player.colliderect(boss["rect"])
                and now > game["invulnerable"]
            ):
                game["health"] -= 18
                game["invulnerable"] = now + 900
                show_message("The Traitor Knight struck you! Use SPACE.")

        if game["health"] <= 0 or elapsed >= 240:
            game["state"] = "lost"

        if game["boss_defeated"]:
            game["state"] = "won"

    player = game["player"]
    camera_x = max(
        0, min(WORLD_W-WIDTH, player.centerx-WIDTH//2)
    )
    camera_y = max(
        0, min(WORLD_H-HEIGHT, player.centery-HEIGHT//2)
    )

    if game["state"] == "playing":
        draw_world(camera_x, camera_y)
        draw_hud(elapsed)
    else:
        draw_end_screen()

    pygame.display.flip()

pygame.quit()
sys.exit()
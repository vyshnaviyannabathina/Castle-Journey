"""Main launcher for Princess Aelira's four-level Pygame adventure.

Keep main_game.py, level1.py, level2.py, level3.py, and level4.py in the
same folder. Install Pygame with: py -3.13 -m pip install pygame
Run with: py -3.13 main_game.py
"""
import os
import sys
import math
from array import array
import pygame

pygame.init()
WIDTH, HEIGHT = 1000, 620
FULLSCREEN = False
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
pygame.display.set_caption("Princess Aelira - The Four Realms")

def toggle_fullscreen():
    """Toggle fullscreen with F11 while keeping the game's logical resolution."""
    global screen, FULLSCREEN
    FULLSCREEN = not FULLSCREEN
    flags = pygame.SCALED | (pygame.FULLSCREEN if FULLSCREEN else 0)
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("Princess Aelira - The Four Realms")
    return screen
clock = pygame.time.Clock()

# ------------------------------------------------------------------
# BUILT-IN AUDIO: generated in Python; no MP3/WAV files are required.
# Background music starts before the main menu and loops for the game.
# ------------------------------------------------------------------
AUDIO_RATE = 44100
AUDIO_CHANNEL = None
BACKGROUND_MUSIC = None
SOUND_BANK = {}

def _make_tone(start_freq, duration=0.16, volume=0.62, end_freq=None, harmonics=0.15):
    """Create a short, distinct sound effect without external audio files."""
    if not pygame.mixer.get_init():
        return None
    end_freq = start_freq if end_freq is None else end_freq
    count = max(1, int(AUDIO_RATE * duration))
    samples = array("h")
    peak = int(32767 * min(0.95, max(0.0, volume)))
    for n in range(count):
        t = n / AUDIO_RATE
        progress = n / max(1, count - 1)
        freq = start_freq + (end_freq - start_freq) * progress
        fade_in = min(1.0, n / max(1, int(AUDIO_RATE * 0.008)))
        fade_out = min(1.0, (count - n) / max(1, int(AUDIO_RATE * 0.025)))
        envelope = fade_in * fade_out
        value = math.sin(2 * math.pi * freq * t)
        value += harmonics * math.sin(2 * math.pi * freq * 2.01 * t)
        samples.append(max(-32767, min(32767, int(peak * envelope * value / (1 + harmonics)))))
    try:
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except pygame.error:
        return None

def _make_background_music():
    """A looping, gentle fantasy melody with warm sustained notes."""
    if not pygame.mixer.get_init():
        return None
    # 16 half-second notes; the last note fades out so the loop is smooth.
    melody = [523.25, 659.25, 783.99, 659.25, 587.33, 698.46, 880.00, 698.46,
              523.25, 659.25, 783.99, 987.77, 880.00, 783.99, 659.25, 523.25]
    roots = [130.81, 164.81, 196.00, 146.83]
    seconds = 8.0
    count = int(AUDIO_RATE * seconds)
    samples = array("h")
    for n in range(count):
        t = n / AUDIO_RATE
        beat = min(15, int(t / 0.5))
        local = (t % 0.5) / 0.5
        # Each note has a soft attack and release; the bass moves every two seconds.
        env = min(1.0, local * 9.0) * min(1.0, (1.0 - local) * 8.0)
        lead = math.sin(2 * math.pi * melody[beat] * t) * 0.26 * env
        shimmer = math.sin(2 * math.pi * melody[beat] * 2.0 * t) * 0.055 * env
        root = roots[int(t / 2.0) % len(roots)]
        pad = (math.sin(2 * math.pi * root * t) +
               0.55 * math.sin(2 * math.pi * root * 1.5 * t)) * 0.10
        # Very quiet pulse adds motion without drowning out gameplay effects.
        pulse = math.sin(2 * math.pi * 2.0 * t) * 0.018
        value = int(32767 * max(-0.85, min(0.85, lead + shimmer + pad + pulse)))
        samples.append(value)
    try:
        music = pygame.mixer.Sound(buffer=samples.tobytes())
        music.set_volume(0.90)
        return music
    except pygame.error:
        return None

def start_background_music():
    """Start music on its own channel, so gameplay sounds can play over it."""
    global AUDIO_CHANNEL, BACKGROUND_MUSIC
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=AUDIO_RATE, size=-16, channels=1, buffer=512)
        pygame.mixer.set_num_channels(max(16, pygame.mixer.get_num_channels()))
        BACKGROUND_MUSIC = _make_background_music()
        if BACKGROUND_MUSIC is not None:
            AUDIO_CHANNEL = pygame.mixer.Channel(0)
            AUDIO_CHANNEL.set_volume(0.90)  # louder background music
            AUDIO_CHANNEL.play(BACKGROUND_MUSIC, loops=-1)
    except pygame.error:
        AUDIO_CHANNEL = None
        BACKGROUND_MUSIC = None

def play_sfx(name="ui"):
    """Play a named sound effect. Called by the launcher and individual levels."""
    if not pygame.mixer.get_init():
        return
    aliases = {
        "move": (235, 0.045, 0.18, 290),
        "jump": (390, 0.13, 0.55, 720),
        "attack": (920, 0.11, 0.68, 280),
        "interact": (560, 0.16, 0.62, 920),
        "collect": (760, 0.23, 0.65, 1250),
        "rescue": (620, 0.30, 0.68, 1040),
        "gate": (300, 0.22, 0.62, 150),
        "hurt": (150, 0.17, 0.70, 65),
        "retry": (360, 0.20, 0.62, 190),
        "ui": (680, 0.09, 0.48, 900),
        "start": (500, 0.35, 0.70, 1050),
        "puzzle": (430, 0.25, 0.62, 880),
        "victory": (520, 0.58, 0.75, 1320),
        "defeat": (280, 0.50, 0.72, 65),
        "level1": (392, 0.42, 0.72, 784),
        "level2": (440, 0.42, 0.72, 880),
        "level3": (330, 0.42, 0.72, 660),
        "level4": (220, 0.48, 0.75, 440),
    }
    if name not in SOUND_BANK:
        start, duration, volume, end = aliases.get(name, aliases["ui"])
        SOUND_BANK[name] = _make_tone(start, duration, volume, end)
    sound = SOUND_BANK.get(name)
    if sound is not None:
        try:
            sound.play()
        except pygame.error:
            pass

start_background_music()


IVORY = (250, 242, 220)
GOLD = (245, 202, 104)
PURPLE = (34, 22, 56)
DARK = (19, 15, 35)
PINK = (191, 105, 143)
BLUE = (79, 147, 204)
GREEN = (100, 205, 145)

TITLE = pygame.font.SysFont("georgia", 48, bold=True)
SUBTITLE = pygame.font.SysFont("georgia", 23)
FONT = pygame.font.SysFont("georgia", 21)
SMALL = pygame.font.SysFont("georgia", 17)

LEVELS = [
    ("LEVEL 1 - THE FALL OF ELDORIA", "level1.py"),
    ("LEVEL 2 - SUNFIRE CITADEL", "level2.py"),
    ("LEVEL 3 - THE FORGOTTEN UNDERKINGDOM", "level3.py"),
    ("LEVEL 4 - SHADOWFALL", "level4.py"),
]


def draw_text(text, font, color, center):
    image = font.render(text, True, color)
    screen.blit(image, image.get_rect(center=center))


def draw_button(rect, label, hovered=False):
    color = (102, 66, 128) if hovered else (64, 43, 88)
    pygame.draw.rect(screen, color, rect, border_radius=15)
    pygame.draw.rect(screen, GOLD, rect, 2, border_radius=15)
    draw_text(label, FONT, IVORY, rect.center)


def draw_princess(x, y):
    """Draw a polished full-length Princess Aelira using Pygame shapes."""
    pygame.draw.ellipse(screen, (8, 6, 18), (x - 54, y + 82, 108, 20))
    # Long flowing hair behind shoulders and cape
    pygame.draw.ellipse(screen, (88, 39, 31), (x - 28, y - 29, 56, 72))
    pygame.draw.polygon(screen, (105, 22, 48),
                        [(x - 17, y + 4), (x + 17, y + 4),
                         (x + 48, y + 77), (x - 48, y + 77)])
    pygame.draw.polygon(screen, (190, 45, 71),
                        [(x - 15, y + 9), (x + 14, y + 9),
                         (x + 35, y + 71), (x - 35, y + 71)])
    # Layered ivory and rose skirt
    pygame.draw.polygon(screen, (255, 241, 230),
                        [(x - 22, y + 18), (x + 22, y + 18),
                         (x + 42, y + 78), (x - 42, y + 78)])
    pygame.draw.polygon(screen, (237, 164, 193),
                        [(x - 7, y + 22), (x + 7, y + 22),
                         (x + 14, y + 75), (x - 14, y + 75)])
    pygame.draw.line(screen, GOLD, (x, y + 22), (x, y + 76), 3)
    # Blue royal bodice, sleeves and gold jewel
    pygame.draw.line(screen, (244, 194, 158), (x - 18, y + 16), (x - 30, y + 36), 9)
    pygame.draw.line(screen, (244, 194, 158), (x + 18, y + 16), (x + 30, y + 36), 9)
    pygame.draw.polygon(screen, (43, 87, 157),
                        [(x - 20, y + 5), (x + 20, y + 5),
                         (x + 17, y + 30), (x - 17, y + 30)])
    pygame.draw.polygon(screen, GOLD,
                        [(x, y + 8), (x + 8, y + 17), (x, y + 25), (x - 8, y + 17)])
    # Face and glossy chestnut hair framing it
    pygame.draw.ellipse(screen, (244, 198, 166), (x - 19, y - 28, 38, 42))
    pygame.draw.ellipse(screen, (91, 42, 32), (x - 23, y - 33, 46, 32))
    pygame.draw.ellipse(screen, (244, 198, 166), (x - 15, y - 24, 30, 36))
    pygame.draw.ellipse(screen, (91, 42, 32), (x - 22, y - 23, 9, 36))
    pygame.draw.ellipse(screen, (91, 42, 32), (x + 13, y - 23, 9, 36))
    pygame.draw.circle(screen, (48, 32, 39), (x - 6, y - 8), 2)
    pygame.draw.circle(screen, (48, 32, 39), (x + 6, y - 8), 2)
    pygame.draw.circle(screen, (240, 133, 151), (x - 10, y - 1), 3)
    pygame.draw.circle(screen, (240, 133, 151), (x + 10, y - 1), 3)
    # Three-point royal crown with a sapphire
    pygame.draw.polygon(screen, GOLD,
                        [(x - 19, y - 23), (x - 16, y - 43),
                         (x - 6, y - 29), (x, y - 48),
                         (x + 7, y - 29), (x + 17, y - 43),
                         (x + 20, y - 23)])
    pygame.draw.line(screen, (255, 239, 173), (x - 17, y - 23), (x + 18, y - 23), 4)
    pygame.draw.circle(screen, (68, 207, 239), (x, y - 31), 4)
    # A small sword at her side
    pygame.draw.line(screen, (230, 242, 255), (x + 31, y + 38), (x + 48, y + 15), 4)
    pygame.draw.line(screen, GOLD, (x + 27, y + 39), (x + 36, y + 32), 5)


def menu():
    start_button = pygame.Rect(WIDTH // 2 - 140, 410, 280, 58)
    quit_button = pygame.Rect(WIDTH // 2 - 140, 485, 280, 48)
    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
                continue
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(event.pos):
                    play_sfx("start")
                    return True
                if quit_button.collidepoint(event.pos):
                    play_sfx("ui")
                    return False

        screen.fill(DARK)
        # Magical night-sky background and decorative stars
        for i in range(9):
            y = i * HEIGHT // 9
            pygame.draw.rect(screen, (22 + i, 17 + i, 43 + i * 2),
                             (0, y, WIDTH, HEIGHT // 9 + 2))
        for i in range(75):
            x = (i * 137 + 31) % WIDTH
            y = (i * 71 + 19) % 340
            pygame.draw.circle(screen, (255, 224, 150), (x, y), 1 + (i % 2))
        pygame.draw.rect(screen, GOLD, (28, 25, WIDTH - 56, HEIGHT - 50), 2,
                         border_radius=24)
        draw_princess(190, 275)
        draw_text("PRINCESS AELIRA", TITLE, GOLD, (WIDTH // 2 + 105, 125))
        draw_text("THE FOUR REALMS", SUBTITLE, IVORY, (WIDTH // 2 + 105, 175))
        draw_text("An adventure of courage, magic and hope", SMALL, IVORY,
                  (WIDTH // 2 + 105, 215))
        draw_text("Explore all four levels and restore the kingdom.", SMALL,
                  (211, 202, 228), (WIDTH // 2 + 105, 245))
        draw_button(start_button, "START ADVENTURE", start_button.collidepoint(mouse))
        draw_button(quit_button, "QUIT", quit_button.collidepoint(mouse))
        draw_text("Move: WASD / Arrow keys     Attack: SPACE or J     Interact: E",
                  SMALL, IVORY, (WIDTH // 2, 570))
        pygame.display.flip()
        clock.tick(60)



def level_intro(index):
    """Show a dramatic full-screen title card before each level begins."""
    level_number = index + 1
    title, filename = LEVELS[index]
    title_text = title.split(" - ", 1)[1] if " - " in title else title
    palettes = [
        ((25, 34, 61), (80, 53, 94)),
        ((77, 42, 28), (147, 81, 40)),
        ((22, 46, 52), (42, 83, 91)),
        ((19, 15, 39), (67, 29, 74)),
    ]
    top_color, bottom_color = palettes[index]
    start_button = pygame.Rect(WIDTH // 2 - 145, 430, 290, 60)
    menu_button = pygame.Rect(WIDTH // 2 - 145, 505, 290, 45)
    big_number = pygame.font.SysFont("georgia", 74, bold=True)
    level_name_font = pygame.font.SysFont("georgia", 38, bold=True)

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
                continue
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    play_sfx("start")
                    return "start"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(event.pos):
                    play_sfx("start")
                    return "start"
                if menu_button.collidepoint(event.pos):
                    play_sfx("ui")
                    return "menu"

        # Smooth vertical gradient background.
        for y in range(HEIGHT):
            t = y / max(1, HEIGHT - 1)
            color = tuple(int(top_color[c] * (1 - t) + bottom_color[c] * t)
                          for c in range(3))
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))

        # Stars, glowing magic orbs, and a royal frame.
        for star in range(95):
            sx = (star * 149 + 37) % WIDTH
            sy = (star * 83 + 21) % 350
            pygame.draw.circle(screen, (255, 225, 155), (sx, sy), 1 + star % 2)
        pygame.draw.circle(screen, (255, 218, 133), (WIDTH // 2, 225), 100, 1)
        pygame.draw.circle(screen, (255, 218, 133), (WIDTH // 2, 225), 78, 1)
        pygame.draw.rect(screen, GOLD, (24, 22, WIDTH - 48, HEIGHT - 44),
                         2, border_radius=24)

        draw_text(f"LEVEL {level_number}", big_number, GOLD, (WIDTH // 2, 112))
        # Wrap longer titles into two centered lines so they stay on screen.
        words = title_text.split()
        lines = []
        current = ""
        for word in words:
            candidate = (current + " " + word).strip()
            if level_name_font.size(candidate)[0] > 820 and current:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        if len(lines) == 1:
            draw_text(lines[0], level_name_font, IVORY, (WIDTH // 2, 230))
        else:
            draw_text(lines[0], level_name_font, IVORY, (WIDTH // 2, 205))
            draw_text(" ".join(lines[1:]), level_name_font, IVORY,
                      (WIDTH // 2, 252))

        draw_text("A NEW CHAPTER BEGINS", SUBTITLE, (255, 221, 157),
                  (WIDTH // 2, 315))
        draw_button(start_button, "START LEVEL", start_button.collidepoint(mouse))
        draw_button(menu_button, "MAIN MENU", menu_button.collidepoint(mouse))
        draw_text("Press ENTER or SPACE to begin", SMALL, IVORY,
                  (WIDTH // 2, 580))
        pygame.display.flip()
        clock.tick(60)

def intermission(next_index):
    continue_button = pygame.Rect(WIDTH // 2 - 155, 390, 310, 55)
    menu_button = pygame.Rect(WIDTH // 2 - 155, 460, 310, 48)
    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
                continue
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_RETURN:
                    return "continue"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if continue_button.collidepoint(event.pos):
                    return "continue"
                if menu_button.collidepoint(event.pos):
                    return "menu"

        screen.fill(PURPLE)
        pygame.draw.rect(screen, GOLD, (28, 25, WIDTH - 56, HEIGHT - 50), 2,
                         border_radius=24)
        draw_text("THE JOURNEY CONTINUES", TITLE, GOLD, (WIDTH // 2, 145))
        if next_index < len(LEVELS):
            draw_text("Next: " + LEVELS[next_index][0], SUBTITLE, IVORY,
                      (WIDTH // 2, 230))
            draw_text("Choose Continue when you are ready for the next realm.", SMALL,
                      IVORY, (WIDTH // 2, 280))
            draw_button(continue_button, "CONTINUE TO NEXT LEVEL",
                        continue_button.collidepoint(mouse))
        else:
            draw_text("You have reached the end of the four-level journey.", SUBTITLE,
                      IVORY, (WIDTH // 2, 235))
            draw_button(continue_button, "RETURN TO MAIN MENU",
                        continue_button.collidepoint(mouse))
        draw_button(menu_button, "MAIN MENU", menu_button.collidepoint(mouse))
        pygame.display.flip()
        clock.tick(60)


def level_result_screen(index, success):
    """Show the result after a level exits; failed levels must be replayed."""
    retry_button = pygame.Rect(WIDTH // 2 - 155, 385, 310, 55)
    menu_button = pygame.Rect(WIDTH // 2 - 155, 455, 310, 48)
    title_font = pygame.font.SysFont("georgia", 43, bold=True)
    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
                continue
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                # On failure, do not offer a way back to the main menu.
                if success and event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "retry" if not success else "continue"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_button.collidepoint(event.pos):
                    return "retry" if not success else "continue"
                if success and menu_button.collidepoint(event.pos):
                    return "menu"

        screen.fill(PURPLE if success else DARK)
        pygame.draw.rect(screen, GOLD, (28, 25, WIDTH - 56, HEIGHT - 50), 2,
                         border_radius=24)
        if success:
            draw_text("LEVEL COMPLETE!", title_font, GOLD, (WIDTH // 2, 150))
            draw_text("Aelira has conquered this realm.", SUBTITLE, IVORY,
                      (WIDTH // 2, 225))
            if index < len(LEVELS) - 1:
                draw_text("The next level will appear next.", FONT, IVORY,
                          (WIDTH // 2, 285))
                draw_button(retry_button, "CONTINUE", retry_button.collidepoint(mouse))
            else:
                draw_text("You have saved all four realms!", FONT, IVORY,
                          (WIDTH // 2, 285))
                draw_button(retry_button, "FINISH ADVENTURE", retry_button.collidepoint(mouse))
        else:
            draw_text("LEVEL NOT COMPLETED", title_font, (255, 130, 125),
                      (WIDTH // 2, 150))
            draw_text("You must defeat the level boss/objective to unlock the next level.",
                      SMALL, IVORY, (WIDTH // 2, 230))
            draw_text("Choose Retry to play this level again.", FONT, IVORY,
                      (WIDTH // 2, 285))
            draw_button(retry_button, "RETRY LEVEL", retry_button.collidepoint(mouse))
        # Failed levels must show ONLY the retry option.
        if success:
            draw_button(menu_button, "MAIN MENU", menu_button.collidepoint(mouse))
        pygame.display.flip()
        clock.tick(60)


class LevelFinished(Exception):
    """Internal signal used to return from a level without closing Pygame."""
    def __init__(self, code=0):
        self.code = int(code or 0)


def play_level_in_same_window(path):
    """Run a level script in this process and reuse the current Pygame window.

    The existing level files contain their own game loops and call pygame.quit()
    / sys.exit() at the end. Temporarily intercept those calls so the main menu
    and next level can continue in the same application window.
    """
    global screen
    original_quit = pygame.quit
    original_exit = sys.exit
    result_code = 1
    error = None

    def keep_pygame_open():
        # A level finishing must not destroy the shared display/audio modules.
        return None

    def finish_level(code=0):
        raise LevelFinished(code)

    try:
        pygame.quit = keep_pygame_open
        sys.exit = finish_level
        namespace = {
            "__name__": "__main__",
            "__file__": path,
            "__package__": None,
            "play_sfx": play_sfx,
        }
        with open(path, "r", encoding="utf-8") as source_file:
            source = source_file.read()
        exec(compile(source, path, "exec"), namespace, namespace)
        # Safety fallback if a level script returns without calling sys.exit.
        result_code = 0
    except LevelFinished as finished:
        result_code = finished.code
    except SystemExit as finished:
        result_code = int(finished.code or 0)
    except Exception as exc:
        error = f"{os.path.basename(path)} failed: {type(exc).__name__}: {exc}"
        result_code = 1
    finally:
        pygame.quit = original_quit
        sys.exit = original_exit
        # set_mode reconfigures the existing display rather than launching a
        # second Python process/window. Restore the launcher size afterwards.
        FULLSCREEN = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)
        flags = pygame.SCALED | (pygame.FULLSCREEN if FULLSCREEN else 0)
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        pygame.display.set_caption("Princess Aelira - The Four Realms")

    if error:
        show_error(error)
    return result_code


def run_adventure():
    folder = os.path.dirname(os.path.abspath(__file__))
    index = 0
    show_intro = True
    while index < len(LEVELS):
        title, filename = LEVELS[index]
        path = os.path.join(folder, filename)
        if not os.path.isfile(path):
            show_error(f"Could not find {filename}. Keep all five .py files together.")
            return

        # Show the title card for a new level, but retry a failed level directly.
        if show_intro:
            intro_choice = level_intro(index)
            if intro_choice in ("quit", "menu"):
                return

        play_sfx(f"level{index + 1}")
        result_code = play_level_in_same_window(path)
        play_sfx("victory" if result_code == 0 else "defeat")
        if result_code == 0 and index < len(LEVELS) - 1:
            # Winning automatically moves to the next level's intro screen.
            index += 1
            show_intro = True
            continue

        choice = level_result_screen(index, result_code == 0)
        if choice in ("quit", "menu"):
            return
        if result_code == 0:
            # All four levels are complete.
            return
        # Failure: retry the SAME level immediately, with no main-menu option.
        show_intro = False


def show_error(message):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
                continue
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                return
        screen.fill(DARK)
        draw_text("GAME FILE NOT FOUND", TITLE, GOLD, (WIDTH // 2, 220))
        draw_text(message, SMALL, IVORY, (WIDTH // 2, 300))
        draw_text("Press any key or close the window.", SMALL, IVORY,
                  (WIDTH // 2, 355))
        pygame.display.flip()
        clock.tick(30)


def main():
    while menu():
        run_adventure()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

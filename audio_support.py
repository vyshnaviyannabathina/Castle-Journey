"""Built-in fantasy music and sound effects for Princess Aelira's levels.
No external audio files are required. Python 3.13 + Pygame compatible.
"""
import math
from array import array
import pygame

RATE = 22050
_MUSIC = None
_CHANNEL = None
_BANK = {}

_MELODIES = {
    1: [523,659,784,659,587,698,880,698,523,659,784,988,880,784,659,523],
    2: [392,494,587,494,440,523,659,523,392,494,587,784,659,587,494,392],
    3: [330,392,494,392,349,440,523,440,330,392,494,659,587,494,392,330],
    4: [294,370,440,370,330,392,494,392,294,370,440,587,494,440,370,294],
}

def _ensure_mixer():
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=RATE, size=-16, channels=1, buffer=512)
    pygame.mixer.set_num_channels(max(16, pygame.mixer.get_num_channels()))

def _tone(start, duration=0.18, volume=0.82, end=None):
    if not pygame.mixer.get_init():
        return None
    end = start if end is None else end
    count = max(1, int(RATE * duration))
    samples = array('h')
    peak = int(32767 * min(0.92, volume))
    for i in range(count):
        t = i / RATE
        p = i / max(1, count - 1)
        freq = start + (end - start) * p
        fade = min(1.0, i / max(1, int(RATE * 0.008)))
        fade *= min(1.0, (count - i) / max(1, int(RATE * 0.025)))
        wave = math.sin(2 * math.pi * freq * t) + 0.20 * math.sin(2 * math.pi * freq * 2 * t)
        samples.append(max(-32767, min(32767, int(peak * fade * wave / 1.20))))
    try:
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except pygame.error:
        return None

def start_music(level=1):
    """Start a loud, looping fantasy melody on a dedicated channel."""
    global _MUSIC, _CHANNEL
    try:
        _ensure_mixer()
        melody = _MELODIES.get(level, _MELODIES[1])
        seconds_per_note = 0.42
        total = int(RATE * seconds_per_note * len(melody))
        samples = array('h')
        roots = [110, 130, 147, 98] if level == 4 else [131, 147, 165, 196]
        for i in range(total):
            t = i / RATE
            note_index = min(len(melody)-1, int(t / seconds_per_note))
            local = (t % seconds_per_note) / seconds_per_note
            env = min(1.0, local * 8.0) * min(1.0, (1.0-local) * 6.0)
            freq = melody[note_index]
            lead = math.sin(2*math.pi*freq*t) * 0.36 * env
            sparkle = math.sin(2*math.pi*freq*2.0*t) * 0.09 * env
            root = roots[(note_index // 4) % len(roots)]
            pad = (math.sin(2*math.pi*root*t) + 0.55*math.sin(2*math.pi*root*1.5*t)) * 0.16
            pulse = math.sin(2*math.pi*2.0*t) * 0.025
            value = int(32767 * max(-0.88, min(0.88, lead + sparkle + pad + pulse)))
            samples.append(value)
        _MUSIC = pygame.mixer.Sound(buffer=samples.tobytes())
        _MUSIC.set_volume(1.0)
        _CHANNEL = pygame.mixer.Channel(0)
        _CHANNEL.set_volume(1.0)
        _CHANNEL.play(_MUSIC, loops=-1)
    except (pygame.error, MemoryError):
        _MUSIC = _CHANNEL = None

def play_sfx(name='ui'):
    """Play a generated sound effect at a clear, strong volume."""
    try:
        _ensure_mixer()
        aliases = {
            'move': (250, .07, .35, 320), 'jump': (380, .15, .72, 760),
            'attack': (900, .14, .84, 220), 'interact': (540, .17, .78, 920),
            'collect': (780, .24, .84, 1320), 'rescue': (620, .32, .86, 1100),
            'gate': (300, .25, .80, 130), 'hurt': (160, .20, .86, 60),
            'retry': (360, .22, .78, 180), 'ui': (680, .11, .65, 980),
            'start': (500, .36, .86, 1100), 'puzzle': (430, .26, .78, 900),
            'victory': (520, .62, .90, 1450), 'defeat': (270, .52, .84, 60),
            'move2': (260, .07, .35, 330), 'boss': (90, .45, .88, 45),
        }
        if name not in _BANK:
            start, duration, volume, end = aliases.get(name, aliases['ui'])
            _BANK[name] = _tone(start, duration, volume, end)
        sound = _BANK.get(name)
        if sound is not None:
            sound.play()
    except pygame.error:
        pass

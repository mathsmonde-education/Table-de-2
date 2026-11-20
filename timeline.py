import random

FPS = 30
W, H = 270, 480
SCALE = 4  # upscale x4 -> 1080x1920

INTRO = 110
OP_SPAWN, OP_AIM, OP_TRAVEL, OP_BOOM, OP_RESULT, OP_OUT = 30, 12, 10, 18, 30, 6
OP_TOTAL = OP_SPAWN + OP_AIM + OP_TRAVEL + OP_BOOM + OP_RESULT + OP_OUT  # 106
N_OPS = 10
END = 280
FINALE_START = INTRO + N_OPS * OP_TOTAL
TOTAL = FINALE_START + END  # 1450 frames = 48.33 s

OPS_X = [135, 82, 188, 105, 168, 62, 208, 118, 92, 178]

FINALE_BRAVO_FRAMES = 6
FINALE_FIREWORK = [8, 30, 46, 66, 88, 108, 126, 148, 168, 190, 212, 232, 252]

rng = random.Random(7)
FW_COLORS = [(255, 80, 90), (90, 255, 130), (255, 220, 60),
             (120, 170, 255), (255, 120, 255), (80, 255, 255)]
FIREWORKS = []
for k in range(len(FINALE_FIREWORK)):
    frame = FINALE_START + FINALE_FIREWORK[k] + rng.randint(0, 5)
    x = rng.randint(38, W - 38)
    y = rng.randint(70, 300)
    FIREWORKS.append((frame, x, y, FW_COLORS[k % len(FW_COLORS)]))


def op_x(i):
    return OPS_X[i % len(OPS_X)]


def booms_before(frame):
    n = 0
    for i in range(N_OPS):
        if frame >= INTRO + i * OP_TOTAL + OP_SPAWN + OP_AIM + OP_TRAVEL:
            n += 1
    return n


def sfx_events():
    ev = []
    for i in range(N_OPS):
        base = INTRO + i * OP_TOTAL
        ev.append((base / FPS, 'spawn', i))
        fire = base + OP_SPAWN + OP_AIM
        ev.append((fire / FPS, 'laser', i))
        ev.append(((fire + OP_TRAVEL) / FPS, 'boom', i))
        ev.append(((fire + OP_TRAVEL + OP_BOOM) / FPS, 'ding', i))
    ev.append((FINALE_START / FPS, 'fanfare', 0))
    for idx, (f, x, y, c) in enumerate(FIREWORKS):
        ev.append((f / FPS, 'pop', idx))
    return sorted(ev, key=lambda e: e[0])

import math
import random
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw

from font5x7 import draw_text, text_w
from timeline import (FPS, H, INTRO, OP_AIM, OP_BOOM, OP_OUT, OP_RESULT,
                      OP_SPAWN, OP_TOTAL, OP_TRAVEL, N_OPS, FINALE_START,
                      FINALE_BRAVO_FRAMES, FINALE_FIREWORK, FIREWORKS,
                      SCALE, TOTAL, W, booms_before, op_x)

SHIP = [
    "     W     ",
    "    WWW    ",
    "    WCW    ",
    "   CCCCC   ",
    "  CCCCCCC  ",
    " CCCCCCCCC ",
    "CCCCCCCCCCC",
    "CC  CCC  CC",
    "C   CCC   C",
]
COLORS = {
    'W': (255, 255, 255),
    'C': (0, 210, 255),
    'G': (130, 140, 165),
}
SHIP_SCALE = 3
SHIP_Y = 442
STAR_COLORS = [(255, 255, 255), (160, 200, 255), (255, 180, 220),
               (180, 255, 200), (255, 230, 160)]
BOOM_COLORS = [(255, 255, 255), (255, 240, 90), (255, 160, 40),
               (255, 80, 50), (0, 220, 255)]
YELLOW = (255, 216, 40)
CYAN = (0, 210, 255)
WHITE = (255, 255, 255)
GREEN = (70, 255, 130)
DARK = (8, 8, 30)


def make_stars():
    r = random.Random(42)
    stars = []
    for _ in range(70):
        stars.append((r.randint(0, W - 1), r.randint(0, H - 1),
                      r.choice([0.6, 0.9, 1.4, 2.2]),
                      r.choice(STAR_COLORS), r.choice([1, 1, 1, 2])))
    return stars


STARS = make_stars()

EXPL = []
for i in range(N_OPS):
    r = random.Random(1000 + i)
    parts = []
    for _ in range(28):
        parts.append((r.uniform(0, 2 * math.pi), r.uniform(0.7, 3.3),
                      r.choice(BOOM_COLORS), r.choice([1, 1, 2])))
    EXPL.append(parts)

FW_PARTS = []
for i in range(len(FIREWORKS)):
    r = random.Random(500 + i)
    color = FIREWORKS[i][3]
    shades = [color, tuple(min(255, c + 90) for c in color), WHITE]
    parts = []
    for _ in range(42):
        parts.append((r.uniform(0, 2 * math.pi), r.uniform(0.5, 2.6),
                      r.choice(shades), r.choice([1, 1, 1, 2])))
    FW_PARTS.append(parts)

SPARKLE_SPOTS = [(5, 4), (9, 2), (3, 7), (11, 6), (7, 9), (2, 1)]


def blend(c, f):
    return tuple(int(v * f) for v in c)


def draw_bg(dr, f):
    dr.rectangle([0, 0, W - 1, H - 1], fill=(6, 6, 24))
    for (x, y0, sp, c, sz) in STARS:
        y = int((y0 + f * sp) % (H + 8)) - 4
        c2 = blend(c, 0.55 + 0.45 * math.sin(f * 0.2 + x))
        dr.rectangle([x, y, x + sz - 1, y + sz - 1], fill=c2)


def draw_hud(dr, f):
    dr.rectangle([0, 0, W - 1, 21], fill=(14, 14, 52))
    dr.rectangle([0, 22, W - 1, 23], fill=CYAN)
    s = "MATHS MONDE"
    x = (W - text_w(s, 2)) // 2
    draw_text(dr, x, 4, s, YELLOW, 2, shadow=(40, 40, 100))
    slick = (W - 3 - int((f * 2.2) % (W + 8)))
    dr.rectangle([slick, 20, slick + 1, 20], fill=WHITE)
    score = 100 * booms_before(f)
    sc = f"SCORE {score:05d}"
    draw_text(dr, W - 5 - text_w(sc, 1), 26, sc, WHITE, 1, shadow=(60, 60, 90))
    draw_text(dr, 5, 26, "TABLE DE 2", CYAN, 1, shadow=(0, 60, 80))


def draw_sprite(dr, ox, oy, rows, colors):
    for ry, row in enumerate(rows):
        for rx, ch in enumerate(row):
            c = colors.get(ch)
            if c:
                x0, y0 = ox + rx, oy + ry
                dr.rectangle([x0, y0, x0, y0], fill=c)


def draw_ship(dr, f, sx, sy):
    rows = SHIP
    cols = {k: COLORS[k] for k in ('W', 'C')}
    for ry, row in enumerate(rows):
        for rx, ch in enumerate(row):
            c = cols.get(ch)
            if ch == 'W':
                c = (int(255 * (0.75 + 0.25 * math.sin(f * 0.3))), 255, 255)
            if c:
                x0 = sx + rx * SHIP_SCALE
                y0 = sy + ry * SHIP_SCALE
                dr.rectangle([x0, y0, x0 + SHIP_SCALE - 1, y0 + SHIP_SCALE - 1],
                             fill=c)
    fl = f // 4 % 2
    fy = sy + 9 * SHIP_SCALE
    for cx in (3, 6):
        h = 2 if fl else 1
        x0 = sx + cx * SHIP_SCALE + 1
        c = (255, 140, 30) if fl else YELLOW
        dr.rectangle([x0, fy, x0 + SHIP_SCALE - 1, fy + h * SHIP_SCALE - 1],
                     fill=c)


def draw_op(dr, i, k, f):
    ox = op_x(i) % W
    cx = ox + int(6 * math.sin(f * 0.35 + i * 2))
    p = min(1.0, (k + 1) / OP_SPAWN)
    cy = int(45 + (150 - 45) * p)
    if k >= OP_SPAWN:
        cy = 150
    s = f"2*{i + 1} = ?"
    tw, th = text_w(s, 2), 14
    bw, bh = tw + 14, th + 12
    x0, y0 = cx - bw // 2, cy - bh // 2
    dr.rectangle([x0, y0, x0 + bw, y0 + bh], fill=DARK,
                 outline=CYAN)
    draw_text(dr, cx - tw // 2, cy - th // 2, s, ORANGE, 2, shadow=(0, 0, 0))
    return cx, cy


ORANGE = (255, 150, 40)


def draw_result(dr, i, cy):
    s = str(2 * (i + 1))
    sc = 4
    tw = text_w(s, sc)
    cx = op_x(i)
    col = WHITE if (cy // 5) % 2 == 0 else GREEN
    bw, bh = tw + 16, 28 + 10
    x0, y0 = cx - bw // 2, cy - bh // 2
    dr.rectangle([x0, y0, x0 + bw, y0 + bh], fill=DARK, outline=GREEN)
    draw_text(dr, cx - tw // 2, cy - 14, s, col, sc, shadow=(0, 60, 40))


def draw_explosion(dr, i, k, cx, cy):
    if k < 2:
        dr.rectangle([0, 0, W - 1, H - 1], fill=(255, 255, 255))
        return
    parts = EXPL[i]
    for (ang, sp, col, sz) in parts:
        px = cx + int(math.cos(ang) * sp * k)
        py = cy + int(math.sin(ang) * sp * k + k * k * 0.02)
        if -4 <= px < W + 4 and -4 <= py < H + 4:
            c = blend(col, max(0.15, 1 - k / 20))
            dr.rectangle([px, py, px + sz, py + sz], fill=c)
    rad = int(3 + k * 0.75)
    col = blend((255, 200, 80), max(0.2, 1 - k / 20))
    dr.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
               outline=col, width=2)


def smooth(p):
    return p * p * (3 - 2 * p)


def scene_op(dr, i, k, f, ship_x):
    cx, cy = (op_x(i), 150)
    if k < OP_SPAWN:
        cx, cy = draw_op(dr, i, k, f)
    elif k < OP_SPAWN + OP_AIM:
        draw_op(dr, i, OP_SPAWN, f)
    elif k < OP_SPAWN + OP_AIM + OP_TRAVEL:
        draw_op(dr, i, OP_SPAWN, f)
        t = k - OP_SPAWN - OP_AIM
        nose = SHIP_Y - 4
        tip = int(nose - (nose - cy) * ((t + 1) / OP_TRAVEL))
        dr.rectangle([cx - 4, tip - 16, cx - 1, tip], fill=CYAN)
        dr.rectangle([cx - 2, tip - 16, cx - 1, tip + 2], fill=WHITE)
        if t < 3:
            dr.ellipse([cx - 6, nose - 8, cx + 6, nose + 4], fill=YELLOW)
        if t > OP_TRAVEL - 3:
            dr.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=WHITE)
    else:
        kb = k - OP_SPAWN - OP_AIM - OP_TRAVEL
        if kb < OP_BOOM:
            draw_explosion(dr, i, kb, cx, cy)
        else:
            kr = kb - OP_BOOM - 4
            draw_result(dr, i, cy)
            fy = cy - 48 - min(14, int(kr * 0.5))
            draw_text(dr, op_x(i) - text_w("+100", 1) // 2, fy, "+100", WHITE, 1)
        if kb >= OP_BOOM + OP_RESULT:
            if kb - OP_BOOM - OP_RESULT < OP_OUT // 2:
                draw_text(dr, op_x(i) - text_w("+100", 1) // 2, cy - 30,
                          "+100", WHITE, 1)
    return ship_x


def draw_trophy(dr, ox, oy, sc):
    GOLD = (255, 208, 40)
    ORN = (205, 130, 0)
    WH = (255, 255, 255)
    bowl = [(2, 14), (2, 14), (2, 14), (3, 13), (4, 12), (6, 10), (7, 9)]
    for r, (a, b) in enumerate(bowl):
        for x in range(a, b + 1):
            col = ORN if x >= b - 1 else GOLD
            if 3 <= x <= 4 and 1 <= r <= 3:
                col = WH
            dr.rectangle([ox + x * sc, oy + r * sc,
                          ox + x * sc + sc - 1, oy + r * sc + sc - 1], fill=col)
    for r in range(1, 5):
        for x in (0, 16):
            dr.rectangle([ox + x * sc, oy + r * sc,
                          ox + x * sc + sc - 1, oy + r * sc + sc - 1], fill=GOLD)
    for r in range(7, 10):
        for x in (7, 8, 9):
            dr.rectangle([ox + x * sc, oy + r * sc,
                          ox + x * sc + sc - 1, oy + r * sc + sc - 1], fill=ORN)
    for x in range(4, 13):
        dr.rectangle([ox + x * sc, oy + 10 * sc,
                      ox + x * sc + sc - 1, oy + 10 * sc + sc - 1], fill=GOLD)
    for x in range(3, 14):
        dr.rectangle([ox + x * sc, oy + 11 * sc,
                      ox + x * sc + sc - 1, oy + 11 * sc + sc - 1], fill=ORN)


def draw_fireworks(dr, f):
    for idx, (f0, fx, fy, col) in enumerate(FIREWORKS):
        if f0 - 10 <= f < f0:
            j = f - (f0 - 10)
            ry = fy + (10 - j) * 7
            c = blend(WHITE, 0.3 + 0.07 * j)
            dr.rectangle([fx, ry, fx + 1, ry + 2], fill=c)
        elif f0 <= f < f0 + 52:
            k = f - f0
            for (ang, sp, c, sz) in FW_PARTS[idx]:
                px = fx + int(math.cos(ang) * sp * k)
                py = fy + int(math.sin(ang) * sp * k + k * k * 0.012)
                if 0 <= px < W and 0 <= py < H:
                    cc = blend(c, max(0.1, 1 - k / 52))
                    dr.rectangle([px, py, px + sz, py + sz], fill=cc)


def scene_finale(dr, k, f):
    draw_fireworks(dr, f)
    if k < FINALE_BRAVO_FRAMES:
        sc = 2 if k < 3 else 6
    else:
        sc = 5
    s = "BRAVO!"
    tw = text_w(s, sc)
    bob = int(6 * math.sin(f * 0.09))
    col = YELLOW if (k // 8) % 2 == 0 else WHITE
    draw_text(dr, (W - tw) // 2, 96 + bob, s, col, sc, shadow=(160, 40, 0))
    tx, ty = (W - 17 * 4) // 2, 250 + bob // 2
    draw_trophy(dr, tx, ty, 4)
    fi = (k // 14) % len(SPARKLE_SPOTS)
    sxp, syp = SPARKLE_SPOTS[fi]
    dr.rectangle([tx + sxp * 4, ty + syp * 4 - 4,
                  tx + sxp * 4 + 1, ty + syp * 4 - 3], fill=WHITE)
    s2 = "TABLE DE 2 REUSSIE"
    sx = (W - text_w(s2, 1)) // 2
    draw_text(dr, sx, 340 + bob // 3, s2, (170, 170, 200), 1,
              shadow=(50, 50, 80))
    draw_ship(dr, f, (W - 33) // 2, SHIP_Y)


def render_frame(f):
    img = Image.new('RGB', (W, H))
    dr = ImageDraw.Draw(img)
    draw_bg(dr, f)
    if f < INTRO:
        if f > 8:
            col = [CYAN, YELLOW, (255, 120, 255)][f % 3] if f < 14 else YELLOW
            for li, s in enumerate(["TABLE", "DE 2"]):
                sc = 5
                tw = text_w(s, sc)
                draw_text(dr, (W - tw) // 2, 150 + li * 44, s, col, sc,
                          shadow=(90, 30, 0))
        if f > 34 and (f // 10) % 2 == 0:
            s = "PRET ?"
            draw_text(dr, (W - text_w(s, 2)) // 2, 330, s, CYAN, 2,
                      shadow=(0, 60, 80))
        sy = SHIP_Y
        if f >= 20:
            p = min(1.0, (f - 20) / 15)
            sy = int(520 - (520 - SHIP_Y) * smooth(p))
        draw_ship(dr, f, (W - 33) // 2, sy)
    elif f < FINALE_START:
        i = (f - INTRO) // OP_TOTAL
        k = (f - INTRO) % OP_TOTAL
        ship_x = op_x(i) if k >= OP_SPAWN else (W - 33) // 2
        scene_op(dr, i, k, f, ship_x)
        draw_ship(dr, f, ship_x - 16, SHIP_Y)
    else:
        scene_finale(dr, f - FINALE_START, f)
    draw_hud(dr, f)
    return img


def main():
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    out = 'table_de_2_1080x1920.mp4'
    cmd = [ff, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{W}x{H}', '-r', str(FPS), '-i', 'pipe:0',
           '-i', 'music.wav',
           '-vf', f'scale={W * SCALE}:{H * SCALE}:flags=neighbor',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
           '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '192k', '-shortest',
           '-movflags', '+faststart', out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    write = proc.stdin.write
    for f in range(TOTAL):
        write(render_frame(f).tobytes())
    proc.stdin.close()
    proc.wait()
    err = proc.stderr.read()
    proc.stderr.close()
    if proc.returncode != 0:
        raise SystemExit(err.decode()[-3000:])
    print('done', out, TOTAL, 'frames')


if __name__ == '__main__':
    main()

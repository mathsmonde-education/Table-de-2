import wave

import numpy as np

from timeline import (FPS, TOTAL, N_OPS, INTRO, OP_TOTAL, OP_SPAWN, OP_AIM,
                      OP_TRAVEL, OP_BOOM, FIREWORKS, sfx_events)

SR = 44100
DUR = TOTAL / FPS + 0.8
N = int(SR * DUR)
buf = np.zeros(N)

NOTE_OFF = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6,
            'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def freq(note):
    name, octv = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((NOTE_OFF[name] + 12 * (octv - 4) - 9) / 12)


def square_wave(ph, duty=0.5):
    return np.where((ph % 1.0) < duty, 1.0, -1.0)


def add_note(t0, dur, f, duty=0.5, vol=0.2, echo=0.0):
    i0 = int(t0 * SR)
    n = int(dur * SR)
    i1 = min(i0 + n, N)
    if i0 >= N:
        return
    t = np.arange(i1 - i0) / SR
    env = np.minimum(1.0, t / 0.006) * np.exp(-t / (dur * 0.75))
    sig = square_wave(t * f, duty) * env * vol
    buf[i0:i1] += sig
    if echo > 0:
        d = int(0.19 * SR)
        j0, j1 = i0 + d, i1 + d
        if j1 <= N:
            buf[j0:j1] += sig[: j1 - j0] * echo


def sweep(t0, dur, f0, f1, vol, duty=0.5):
    i0 = int(t0 * SR)
    n = int(dur * SR)
    i1 = min(i0 + n, N)
    if i0 >= N:
        return
    t = np.arange(i1 - i0) / SR
    sw = f0 * (f1 / f0) ** (t / dur)
    ph = np.cumsum(sw) / SR
    env = np.minimum(1.0, t / 0.004) * np.exp(-t / (dur * 0.45))
    buf[i0:i1] += square_wave(ph, duty) * env * vol


def kick(t0, vol=0.55):
    i0 = int(t0 * SR)
    n = int(0.16 * SR)
    i1 = min(i0 + n, N)
    t = np.arange(i1 - i0) / SR
    f = 120 * np.exp(-t * 22) + 42
    ph = np.cumsum(f) / SR
    buf[i0:i1] += np.sin(2 * np.pi * ph) * np.exp(-t * 18) * vol


def noise_hit(t0, dur, vol, decay=None, seed=0, lowpass=None):
    i0 = int(t0 * SR)
    n = int(dur * SR)
    i1 = min(i0 + n, N)
    if i0 >= N:
        return
    t = np.arange(i1 - i0) / SR
    r = np.random.default_rng(seed)
    sig = r.uniform(-1, 1, i1 - i0)
    if lowpass is not None:
        k = max(1, int(SR / lowpass))
        sig = np.convolve(sig, np.ones(k) / k, mode='same')
    env = np.exp(-t / (decay if decay else dur * 0.35))
    buf[i0:i1] += sig * env * vol


def pop(t0, seed, thump_freq):
    noise_hit(t0, 0.14, 0.22, decay=0.06, seed=seed)
    i0 = int(t0 * SR)
    n = int(0.18 * SR)
    i1 = min(i0 + n, N)
    t = np.arange(i1 - i0) / SR
    f = thump_freq * np.exp(-t * 10) + 45
    buf[i0:i1] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * 0.4


E8 = 60 / 168 / 2
BAR = E8 * 8
MUSIC_T0 = 0.15
MEL_A = [
    ['C5', 'E5', 'G5', 'E5', 'C5', 'E5', 'G5', 'A5'],
    ['G5', 'E5', 'C5', 'E5', 'D5', 'E5', 'C5', None],
    ['F5', 'A5', 'C6', 'A5', 'F5', 'A5', 'G6', 'E6'],
    ['E6', 'D6', 'C6', 'G5', 'A5', 'B5', 'C6', None],
]
MEL_B = [
    ['E5', 'E5', 'E5', 'C5', 'E5', 'G5', 'G5', None],
    ['A5', 'A5', 'G5', 'F5', 'E5', 'D5', 'C5', None],
    ['C6', 'B5', 'A5', 'G5', 'A5', 'F5', 'E5', 'D5'],
    ['E5', 'G5', 'C6', 'G5', 'E5', 'D5', 'C5', None],
]
ROOTS = {'A': ['C3', 'G2', 'A2', 'F2'], 'B': ['C3', 'G2', 'A2', 'G2']}


def build_music():
    music_end = (TOTAL / FPS) - 1.3
    loop_len = 8 * BAR
    nloops = int(np.ceil((music_end - MUSIC_T0) / loop_len)) + 1
    s = 0
    for L in range(nloops):
        base = MUSIC_T0 + L * loop_len
        for bi in range(8):
            part = 'A' if bi < 4 else 'B'
            mel = (MEL_A if part == 'A' else MEL_B)[bi % 4]
            bt = base + bi * BAR
            if bt > music_end:
                break
            for k in range(8):
                note = mel[k]
                if note and bt + k * E8 < music_end:
                    add_note(bt + k * E8, E8 * 0.92, freq(note),
                             duty=0.5, vol=0.15, echo=0.22)
            r = ROOTS[part][bi % 4]
            fr = freq(r)
            for k in range(8):
                f = fr if k % 2 == 0 else fr * 2
                if bt + k * E8 < music_end:
                    add_note(bt + k * E8, E8 * 0.48, f,
                             duty=0.25, vol=0.115)
            for beat in range(4):
                tt = bt + beat * 4 * E8
                if tt >= music_end:
                    break
                if beat % 2 == 0:
                    kick(tt)
                else:
                    noise_hit(tt, 0.1, 0.24, decay=0.05, seed=s); s += 1
                for h in range(4):
                    noise_hit(tt + h * E8, 0.03, 0.085,
                              decay=0.018, seed=s); s += 1


def build_sfx():
    s = 1000
    for t, kind, i in sfx_events():
        if kind == 'spawn':
            add_note(t, 0.05, 880, duty=0.5, vol=0.1)
        elif kind == 'laser':
            sweep(t, 0.14, 1760, 340, 0.32, duty=0.35)
        elif kind == 'boom':
            noise_hit(t, 0.5, 0.55, decay=0.13, seed=s, lowpass=3500); s += 1
            kick(t, vol=0.65)
        elif kind == 'ding':
            add_note(t, 0.09, freq('B5'), duty=0.5, vol=0.26)
            add_note(t + 0.09, 0.28, freq('E6'), duty=0.5, vol=0.26)
        elif kind == 'fanfare':
            arp = ['C5', 'E5', 'G5', 'C6', 'E6', 'G6', 'C7']
            for j, note in enumerate(arp):
                add_note(t + j * 0.09, 0.30, freq(note), duty=0.5, vol=0.24)
            tchord = t + len(arp) * 0.09 + 0.12
            for note, v in [('C6', 0.14), ('E6', 0.12), ('G6', 0.12),
                            ('C7', 0.1)]:
                add_note(tchord, 1.6, freq(note), duty=0.5, vol=v, echo=0.3)
            kick(tchord - 0.1, vol=0.6)
            noise_hit(tchord - 0.35, 0.4, 0.14, decay=0.2, seed=s); s += 1
        elif kind == 'pop':
            pop(t, s, 50 + (i * 13) % 45); s += 1


def main():
    global buf
    build_music()
    build_sfx()
    fade = int(0.5 * SR)
    buf[-fade:] *= np.linspace(1.0, 0.0, fade)
    peak = np.max(np.abs(buf))
    if peak > 0.95:
        buf *= 0.95 / peak
    data = (buf * 32767).astype(np.int16).tobytes()
    with wave.open('music.wav', 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)
    print('music.wav', DUR, 's, peak', round(float(peak), 3))


if __name__ == '__main__':
    main()

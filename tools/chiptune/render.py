"""Render song.json as an NES-style loop: pulse lead, pulse arpeggio, triangle bass, noise drums."""
import json, sys
import numpy as np, soundfile as sf

SR = 22050
d = json.load(open('song.json'))
STEP = d['step']
LOOP_START, LOOP_END = (int(x) for x in (sys.argv[1:3] if len(sys.argv) > 2 else (0, 58)))  # bars
OUT = sys.argv[3] if len(sys.argv) > 3 else 'theme-8bit.wav'
s0, s1 = LOOP_START * 16, LOOP_END * 16
mel, bas, drm = d['melody'][s0:s1], d['bass'][s0:s1], d['drums'][s0:s1]
n = s1 - s0
TAIL = 16  # one extra bar rendered, then wrapped to the start for a seamless loop
total = int((n + TAIL) * STEP * SR)
loop_len = int(n * STEP * SR)
root, mode = d['key']
scale = [(root + i) % 12 for i in ([0,2,4,5,7,9,11] if mode == 'major' else [0,2,3,5,7,8,10])]

def hz(m): return 440 * 2 ** ((m - 69) / 12)
def t_at(step): return int(step * STEP * SR)

def pulse(freq, length, duty, vib=0.0):
    t = np.arange(length) / SR
    f = freq * (1 + vib * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.15) * 4, 0, 1))
    ph = np.cumsum(f / SR) % 1
    return np.where(ph < duty, 1.0, -1.0)

def triangle(freq, length):
    ph = np.cumsum(np.full(length, freq / SR)) % 1
    tri = 4 * np.abs(ph - 0.5) - 1
    return np.round(tri * 7.5) / 7.5  # NES 4-bit stepped triangle

def env(length, attack=0.003, decay=0.0, sustain=1.0, release=0.02):
    e = np.full(length, sustain)
    a = min(length, max(1, int(attack * SR))); e[:a] = np.linspace(0, 1, a)
    if decay:
        dl = min(length - a, int(decay * SR))
        e[a:a + dl] = np.linspace(1, sustain, dl)
    r = min(length, int(release * SR)); e[-r:] *= np.linspace(1, 0, r)
    return e

def runs(seq):
    i = 0
    while i < len(seq):
        if seq[i] is None: i += 1; continue
        j = i
        while j < len(seq) and seq[j] == seq[i]: j += 1
        yield i, j, seq[i]; i = j

lead = np.zeros(total); arp = np.zeros(total); tri = np.zeros(total); noise = np.zeros(total)

# lead: vocals up an octave if low, 25% duty pulse, vibrato on long notes
for i, j, m in runs(mel):
    while m < 60: m += 12
    a, L = t_at(i), t_at(j) - t_at(i)
    lead[a:a + L] += pulse(hz(m), L, 0.25, vib=0.008 if j - i >= 4 else 0) * env(L, decay=0.12, sustain=0.75)

# arpeggio: diatonic triad on the bass root, 12.5% duty, 32nd-note cycling
def triad(m):
    pc = m % 12
    if pc not in scale: return [m, m + 4, m + 7]
    k = scale.index(pc)
    return [m + (scale[(k + o) % 7] - pc) % 12 for o in (0, 2, 4)]
arp_rate = STEP / 2
for i, j, m in runs(bas):
    notes = triad(48 + m % 12)
    a, b = t_at(i), t_at(j)
    k = 0
    pos = a
    while pos < b:
        L = min(int(arp_rate * SR), b - pos)
        arp[pos:pos + L] += pulse(hz(notes[k % 3]), L, 0.125) * env(L, release=0.004)
        pos += L; k += 1

# bass: triangle, notes kept in a solid low register, 8th-note pulse for drive
for i, j, m in runs(bas):
    while m < 33: m += 12
    while m > 47: m -= 12
    for s in range(i, j, 2):
        a, L = t_at(s), t_at(min(s + 2, j)) - t_at(s)
        tri[a:a + L] += triangle(hz(m), L) * env(L, release=0.015)

# drums: where the stem has drums, play a standard beat (kick 1&3, snare 2&4, hats on 8ths)
def lfsr_noise(L, short=False):
    reg, out = 1, np.empty(L)
    hold = 2
    v = 1.0
    for x in range(L):
        if x % hold == 0:
            bit = (reg ^ (reg >> (6 if short else 1))) & 1
            reg = (reg >> 1) | (bit << 14)
            v = 1.0 if reg & 1 else -1.0
        out[x] = v
    return out
NOISE = lfsr_noise(int(0.3 * SR))
def hit(kind, at):
    if kind == 'K':
        L = int(0.12 * SR); t = np.arange(L) / SR
        f = 140 * np.exp(-t * 30) + 45
        k = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR))
        tri[at:at + L] += 0.9 * k * np.exp(-t * 22)[:len(tri[at:at + L])]
    elif kind == 'S':
        L = int(0.16 * SR); t = np.arange(L) / SR
        noise[at:at + L] += 0.8 * NOISE[:L] * np.exp(-t * 20)
    else:
        L = int(0.04 * SR); t = np.arange(L) / SR
        noise[at:at + L] += 0.35 * NOISE[1000:1000 + L] * np.exp(-t * 90)
for bar in range(n // 16):
    hits = sum(x is not None for x in drm[bar * 16:bar * 16 + 16])
    if hits < 3: continue
    for s in range(16):
        at = t_at(bar * 16 + s)
        if s in (0, 8): hit('K', at)
        if s in (4, 12): hit('S', at)
        if s % 2 == 0: hit('H', at)

mix = 0.30 * lead + 0.12 * arp + 0.42 * tri + 0.25 * noise
# wrap the tail onto the start so the loop is seamless
song = mix[:loop_len].copy()
tail = mix[loop_len:]
song[:len(tail)] += tail
song /= np.max(np.abs(song)) * 1.12
sf.write(OUT, song.astype(np.float32), SR, subtype='PCM_16')
print(f'{OUT}: {loop_len / SR:.2f}s loop, bars {LOOP_START}-{LOOP_END}')

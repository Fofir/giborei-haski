"""Val Gardena / Dolomites scenery: parallax backgrounds + snowy recolor of the tileset.
Run from the repo root: python3 tools/make_scenery.py [preview.png]"""
import math, sys
from PIL import Image

IMG = 'public/res/images/'

def hexc(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)

def hash1(x, seed=0):
    n = (x * 374761393 + seed * 668265263) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 0xffff

def vnoise(x, period, scale, seed=0):
    """Smooth 1D value noise that tiles every `period` px."""
    cells = max(1, period // scale)
    fx = x / scale; i = int(math.floor(fx)); f = fx - i
    a, b = hash1(i % cells, seed), hash1((i + 1) % cells, seed)
    f = f * f * (3 - 2 * f)
    return a + (b - a) * f

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def dither(x, y, t):
    return t * 16 > BAYER[y % 4][x % 4] + 0.5

# ---------------------------------------------------------------- sky
def sky(W=128, H=320, view=224):
    bands = ['#2f5fae', '#3a70bd', '#4a83c9', '#5e97d3', '#78acdc', '#93c0e4', '#b2d3ea', '#cfe2ee', '#f2d9cf']
    im = Image.new('RGBA', (W, H))
    n = len(bands) - 1
    for y in range(H):
        t = min(max(y - (H - view), 0) / (view * 0.78), 1) * n  # extra height above is deepest blue
        i = min(int(t), n - 1); f = t - i
        for x in range(W):
            im.putpixel((x, y), hexc(bands[i + 1] if dither(x, y, f) else bands[i]))
    return im

# ---------------------------------------------------------------- Dolomites
# (center x, peak y, flat half-width, wall steepness) — Sassolungo-style towers + Sella-like plateau
PEAKS = [(60, 34, 3, 5.0), (78, 22, 2, 6.0), (96, 30, 4, 5.0), (112, 44, 2, 4.0),
         (210, 58, 30, 6.0), (300, 40, 2, 3.5), (318, 50, 3, 4.0),
         (430, 30, 3, 5.5), (447, 18, 2, 6.5), (462, 28, 2, 5.0), (482, 42, 3, 4.0),
         (560, 62, 12, 3.0)]

def mountains(W=640, H=200):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    far = [int(95 + 22 * vnoise(x, W, 40, 3) + 8 * vnoise(x, W, 11, 4)) for x in range(W)]
    for x in range(W):
        for y in range(far[x], H):
            d = y - far[x]
            c = '#e3e8f6' if d < 3 + 4 * vnoise(x, W, 7, 9) else ('#b9c3e0' if dither(x, y, min(d / 40, 1) * 0.5) else '#a6b1d6')
            im.putpixel((x, y), hexc(c))

    base = [int(132 + 10 * vnoise(x, W, 64, 5)) for x in range(W)]
    prof = []
    for x in range(W):
        best = base[x] - 18
        for c, top, flat, steep in PEAKS:
            dx = min(abs(x - c), W - abs(x - c))
            best = min(best, top + max(0, dx - flat) * steep)
        jag = int(hash1(x, 7) * 3) if best < base[x] - 20 else 0
        prof.append(int(best + jag))
    smooth = [sum(prof[(x + k) % W] for k in range(-3, 4)) / 7 for x in range(W)]

    for x in range(W):
        slope = smooth[(x + 2) % W] - smooth[(x - 2) % W]
        lit = slope <= 1.5
        couloir = hash1(x // 2, 11) > 0.82
        for y in range(prof[x], H):
            d = y - prof[x]
            if y >= base[x]:  # snowy scree apron at the foot of the walls
                t = min((y - base[x]) / 30, 1)
                c = '#f4f7ff' if not dither(x, y, 0.35 - t * 0.3) else '#d4e1f2'
            elif lit:
                if d < 6 + 6 * vnoise(x, W, 9, 2):
                    c = '#f6b9a4' if d < 3 else '#f2cbb6'   # enrosadira — pink alpenglow
                else:
                    c = '#e7dacd' if not couloir else '#c9b9b4'
                    if dither(x, y, min(d / 90, 1) * 0.6): c = '#d6c5bc'
            else:
                c = '#9a8fae' if not couloir else '#7f7598'
                if d < 4: c = '#b49aaa'
            # snow ledges across the strata
            if prof[x] + 4 < y < base[x] and (y + int(hash1(x // 7, 13) * 9)) % 17 == 0 and hash1(x // 3, y) > 0.35:
                c = '#ffffff' if lit else '#cfdaf0'
            im.putpixel((x, y), hexc(c))
        im.putpixel((x, prof[x]), hexc('#fff1ea' if lit else '#c9b6c6'))
    return im

# ---------------------------------------------------------------- valley: pines, chalets, church, chairlift
def pine(im, x0, yb, h, shade=0):
    dark, mid = ('#1d3f36', '#2c5e4a') if not shade else ('#2a4a4a', '#3c6a5e')
    for y in range(yb - 2, yb + 1):
        px(im, x0, y, '#4a3020')
    tiers = max(2, h // 5)
    for t in range(tiers):
        top = yb - h + t * (h // tiers) - 1
        span = h // tiers + 3
        for k in range(span):
            w = 1 + (k * (2 + t)) // span + t
            for dx in range(-w, w + 1):
                px(im, x0 + dx, top + k, mid if dx < 0 else dark)
            if k < 2: px(im, x0 - w, top + k, '#ffffff'); px(im, x0 - w + 1, top + k, '#ffffff')
        px(im, x0, top, '#ffffff')

def px(im, x, y, c):
    W, H = im.size
    if 0 <= y < H: im.putpixel((x % W, y), hexc(c))

def rect(im, x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w): px(im, xx, yy, c)

def chalet(im, x, yb, w=22):
    rect(im, x, yb - 7, w, 7, '#f1ece2')                    # white stucco ground floor
    rect(im, x, yb - 15, w, 8, '#8a5a36')                   # timber upper floor
    for k in range(x, x + w, 3): rect(im, k, yb - 15, 1, 8, '#6c4228')
    rect(im, x - 1, yb - 9, w + 2, 1, '#4a2c1a')            # balcony
    for k in range(x, x + w + 1, 2): px(im, k, yb - 10, '#4a2c1a')
    for wx in range(x + 3, x + w - 3, 6):
        rect(im, wx, yb - 13, 3, 3, '#ffd76a'); px(im, wx - 1, yb - 13, '#b8322e'); px(im, wx + 3, yb - 13, '#b8322e')
        rect(im, wx, yb - 5, 3, 3, '#ffd76a')
    roof_h = w // 2 - 2
    for k in range(roof_h):                                   # snowy gable roof
        l, r = x - 3 + k, x + w + 2 - k
        rect(im, l, yb - 16 - k, r - l, 1, '#ffffff' if k < roof_h - 1 else '#e5eefb')
        px(im, l, yb - 16 - k, '#4a2c1a'); px(im, r - 1, yb - 16 - k, '#4a2c1a')
    rect(im, x - 3, yb - 16, w + 6, 1, '#4a2c1a')

def church(im, x, yb):
    rect(im, x, yb - 12, 16, 12, '#f4efe6')
    for k in range(9): rect(im, x - 1 + k, yb - 13 - k, 18 - 2 * k, 1, '#b84a3a')  # red nave roof
    rect(im, x + 12, yb - 30, 6, 30, '#f7f2ea'); rect(im, x + 17, yb - 30, 1, 30, '#d8d0c4')
    px(im, x + 14, yb - 25, '#3a3a3a'); px(im, x + 15, yb - 25, '#3a3a3a')
    rect(im, x + 13, yb - 27, 4, 3, '#e0b84a')                # clock
    for k in range(16):                                        # tall pointed spire, Ortisei style
        w = max(0, 3 - k // 5)
        rect(im, x + 15 - w, yb - 31 - k, 2 * w + 1, 1, '#3f8a78' if k % 4 else '#2f6a5c')
    px(im, x + 15, yb - 48, '#e0b84a'); px(im, x + 15, yb - 49, '#e0b84a')

def valley(W=480, H=128):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    back = [int(40 + 14 * vnoise(x, W, 80, 21) + 5 * vnoise(x, W, 23, 22)) for x in range(W)]
    front = [int(74 + 10 * vnoise(x, W, 96, 31) + 4 * vnoise(x, W, 30, 32)) for x in range(W)]
    for x in range(W):                                         # far forested slope
        for y in range(back[x], H):
            im.putpixel((x, y), hexc('#e6eefa' if dither(x, y, 0.15) else '#d3e0f3'))
    for i in range(0, W, 5):                                   # dense back forest band
        x = i + int(hash1(i, 40) * 4)
        pine(im, x, back[x % W] + 10 + int(hash1(i, 41) * 6), 9 + int(hash1(i, 42) * 6), shade=1)
    # chairlift: pylons + sagging cable climbing the back slope
    pyl = [40, 120, 200]
    for p in pyl:
        yb = back[p] + 8
        rect(im, p, yb - 22, 1, 22, '#5b6577'); rect(im, p - 3, yb - 22, 7, 1, '#5b6577')
    for a, b in zip(pyl, pyl[1:]):
        ya, yb2 = back[a] - 14, back[b] - 14
        for x in range(a, b + 1):
            t = (x - a) / (b - a)
            y = int(ya + (yb2 - ya) * t + 6 * math.sin(math.pi * t))
            px(im, x, y, '#3a3f4c')
            if (x - a) % 26 == 13:
                rect(im, x, y + 1, 1, 4, '#3a3f4c'); rect(im, x - 2, y + 5, 5, 2, '#d23a3a')
    for x in range(W):                                         # near snowfield
        for y in range(front[x], H):
            d = y - front[x]
            c = '#ffffff' if d < 2 else ('#eef4ff' if not dither(x, y, min(d / 50, 1) * 0.5) else '#d9e5f6')
            im.putpixel((x, y), hexc(c))
    church(im, 300, front[300] + 2)
    chalet(im, 120, front[125] + 2)
    chalet(im, 380, front[388] + 2, w=18)
    chalet(im, 420, front[425] + 3, w=14)
    for i in range(0, W, 9):                                   # scattered pines in front
        x = i + int(hash1(i, 50) * 6)
        if any(lo - 6 < x < hi for lo, hi in ((114, 146), (296, 322), (374, 402), (414, 440))): continue
        if hash1(i, 51) < 0.55:
            pine(im, x, front[x % W] + 4 + int(hash1(i, 52) * 10), 12 + int(hash1(i, 53) * 10))
    return im

# ---------------------------------------------------------------- tileset recolor
DIRT = {  # grass-topped dirt -> snow-capped Dolomite rock
    '#bf6f4a': '#a8978c', '#8a4836': '#7a6a6c', '#5d2c28': '#4d4150', '#e69c69': '#cdbdb0', '#f6ca9f': '#ebe0d4',
    '#99e65f': '#ffffff', '#5ac54f': '#eef5ff', '#33984b': '#c6d9ef', '#1e6f50': '#8eaacb', '#134c4c': '#55688a',
}
BRICK = {  # dark stone bricks -> chalet timber with snow on top
    '#2a2f4e': '#6a4128', '#424c6e': '#8a5a36', '#1a1932': '#3e2416', '#657392': '#a8744a',
    '#c7cfdd': '#f4f8ff', '#92a1b9': '#c6d9ef',
}

def tileset():
    im = Image.open('tools/source/tileset.orig.png').convert('RGBA')
    for (c0, c1, r0, r1, m) in ((9, 16, 0, 8, DIRT), (0, 8, 0, 4, BRICK)):
        lut = {hexc(k): hexc(v) for k, v in m.items()}
        for y in range(r0 * 16, r1 * 16):
            for x in range(c0 * 16, c1 * 16):
                p = im.getpixel((x, y))
                if p in lut: im.putpixel((x, y), lut[p])
    return im

if __name__ == '__main__':
    layers = {'Dolomiti_Sky.png': sky(), 'Dolomiti_Mountains.png': mountains(), 'Dolomiti_Valley.png': valley()}
    for name, im in layers.items(): im.save(IMG + name)
    tileset().save(IMG + 'tileset.png')
    if len(sys.argv) > 1:  # composite preview at the in-game 398x224 view
        W, H = 398, 224
        out = Image.new('RGBA', (W, H))
        for name, dy in (('Dolomiti_Sky.png', H - 320), ('Dolomiti_Mountains.png', H - 200), ('Dolomiti_Valley.png', H - 128)):
            im = layers[name]
            for x in range(0, W, im.width): out.alpha_composite(im, (x, dy))
        out.resize((W * 3, H * 3), Image.NEAREST).save(sys.argv[1])

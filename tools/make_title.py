"""Title screen art (Sonic-style emblem): public/res/images/Title.png, Title_Press.png and the
loader text images Loader_Loading.png + Loader_Click.png.

Run from the repo root:  python3 tools/make_title.py "<path to Dudu photo>" [preview.png]
Uses the Dolomiti background layers made by tools/make_scenery.py.
"""
import colorsys, math, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

IMG = 'public/res/images/'
W, H = 398, 224
OUTLINE = (26, 16, 32, 255)
TITLE_FONT = '/System/Library/Fonts/Supplemental/Arial Black.ttf'
PIXEL_FONT = 'public/res/fonts/Round9x13.ttf'


def hexc(h, a=255):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def outline(img, color=OUTLINE):
    """Adds a 1px outline around the opaque pixels."""
    alpha = img.getchannel('A').point(lambda v: 255 if v > 0 else 0)
    ring = Image.new('RGBA', img.size, color)
    ring.putalpha(alpha.filter(ImageFilter.MaxFilter(3)))
    ring.alpha_composite(img)
    return ring


# ---------------------------------------------------------------- Dudu bust from the photo
def dudu_bust(photo, height=100):
    src = Image.open(photo).convert('RGB').crop((80, 70, 720, 630))
    im = src.convert('RGBA')
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, _ = px[x, y]
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if r > 228 and g > 228 and b > 228:
                px[x, y] = (0, 0, 0, 0)  # white studio background (and the photo's smoke)
            elif 175 < x < 515 and 55 < y < 205 and not (x > 255 and y > 178) and (h < 0.16 or h > 0.92) and s > 0.25:
                # no goggles: repaint them as helmet blue, keeping the shading
                nr, ng, nb = colorsys.hsv_to_rgb(0.61, 0.62, 0.22 + v * 0.40)
                px[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), 255)
            elif 375 < x < 445 and 315 < y < 395 and s < 0.25 and v > 0.55:
                # metallic-blue whistle
                nr, ng, nb = colorsys.hsv_to_rgb(0.6, 0.7, 0.4 + (v - 0.55) * 1.4)
                px[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), 255)
            elif x > 440 and 230 < y < 360 and s < 0.12 and v > 0.75:
                px[x, y] = (0, 0, 0, 0)  # photo smoke, redrawn as pixel art
    alpha = im.getchannel('A').filter(ImageFilter.MinFilter(3))
    rgb = ImageEnhance.Color(ImageEnhance.Contrast(im.convert('RGB')).enhance(1.15)).enhance(1.25)
    size = (round(im.width * height / im.height), height)
    small_a = alpha.resize(size, Image.LANCZOS).point(lambda v: 255 if v > 150 else 0)
    small = rgb.resize(size, Image.LANCZOS).quantize(colors=40, method=Image.Quantize.MEDIANCUT,
                                                       dither=Image.Dither.NONE).convert('RGBA')
    small.putalpha(small_a)
    return outline(small)


PUFF = """
......wwww.......
....wwWWWWw..ww..
..wwWWWWWWWwwWWw.
.wWWWWWWWWWWWWWWw
wWWWWWWWWWWWWWWw.
.wwWWWWWWWWWWWw..
...wwwWWWWwwww...
......www........
"""


def pixel_art(art, pal):
    rows = art.strip('\n').split('\n')
    im = Image.new('RGBA', (len(rows[0]), len(rows)), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal: im.putpixel((x, y), pal[ch])
    return im


# ---------------------------------------------------------------- emblem pieces
def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill, outline=OUTLINE)


def ski(length=250, width=9, angle=0):
    """A red ski with a curled tip, rotated by `angle` degrees."""
    s = Image.new('RGBA', (length + 12, width + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    y0 = 6
    d.rectangle((6, y0, length, y0 + width), fill=hexc('#d8262a'), outline=OUTLINE)
    d.rectangle((7, y0 + 1, length - 1, y0 + 2), fill=hexc('#ff6a5a'))
    d.rectangle((7, y0 + width - 2, length - 1, y0 + width - 1), fill=hexc('#961419'))
    d.pieslice((length - 8, y0 - 6, length + 10, y0 + width), 270, 90, fill=hexc('#d8262a'), outline=OUTLINE)
    d.rectangle((length // 2 - 14, y0 - 1, length // 2 + 14, y0 + width + 1), fill=hexc('#f08a1c'), outline=OUTLINE)  # binding
    return s.rotate(angle, resample=Image.NEAREST, expand=True)


def chrome_text(text, size):
    """Sonic-style chrome letters: sky blue -> white, dark horizon line, orange -> brown."""
    font = ImageFont.truetype(TITLE_FONT, size)
    l, t, r, b = font.getbbox(text)
    mask = Image.new('L', (r - l + 2, b - t + 2), 0)
    dm = ImageDraw.Draw(mask); dm.fontmode = '1'
    dm.text((-l + 1, -t + 1), text, font=font, fill=255)
    mask = mask.point(lambda v: 255 if v > 127 else 0)
    w, h = mask.size
    grad = Image.new('RGBA', (w, h))
    stops = [(0.0, '#9fd3ff'), (0.42, '#ffffff'), (0.48, '#2c4a96'), (0.55, '#ffd27a'), (1.0, '#a8520f')]
    for y in range(h):
        t_ = y / max(h - 1, 1)
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= t_ <= p1:
                f = (t_ - p0) / max(p1 - p0, 1e-6)
                a, b_ = hexc(c0), hexc(c1)
                col = tuple(int(a[i] + (b_[i] - a[i]) * f) for i in range(3)) + (255,)
                break
        for x in range(w): grad.putpixel((x, y), col)
    letters = Image.new('RGBA', (w, h), (0, 0, 0, 0)); letters.paste(grad, (0, 0), mask)
    # thick outline + drop shadow
    pad = 4
    out = Image.new('RGBA', (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    thick = mask.filter(ImageFilter.MaxFilter(5))
    shadow = Image.new('RGBA', thick.size, hexc('#5a0d10')); shadow.putalpha(thick)
    out.alpha_composite(shadow, (pad + 2, pad + 2))
    edge = Image.new('RGBA', thick.size, OUTLINE); edge.putalpha(thick)
    out.alpha_composite(edge, (pad, pad))
    out.alpha_composite(letters, (pad, pad))
    return out


def pixel_text(text, color='#ffffff', size=13):
    font = ImageFont.truetype(PIXEL_FONT, size)
    l, t, r, b = font.getbbox(text)
    im = Image.new('RGBA', (r - l + 4, b - t + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); d.fontmode = '1'
    d.text((-l + 2, -t + 2), text, font=font, fill=hexc(color))
    return outline(im)


def banner(d, top, bottom, left, right):
    red, dark = hexc('#d8262a'), hexc('#8e1418')
    mid = (top + bottom) // 2
    for sgn, x0 in ((-1, left), (1, right)):  # ribbon tails folding back
        tail_out = x0 + sgn * 46
        d.polygon([(x0, top + 10), (tail_out, top + 10), (tail_out + sgn * -12, mid + 12),
                   (tail_out, bottom + 10), (x0, bottom + 10)], fill=dark, outline=OUTLINE)
        d.polygon([(x0, top + 10), (x0 + sgn * 12, top + 10), (x0 + sgn * 12, bottom + 10), (x0, bottom + 10)],
                  fill=hexc('#5a0d10'), outline=OUTLINE)
    d.rectangle((left, top, right, bottom), fill=red, outline=OUTLINE)
    d.rectangle((left + 1, top + 3, right - 1, top + 5), fill=hexc('#ffffff'))
    d.rectangle((left + 1, bottom - 5, right - 1, bottom - 3), fill=hexc('#ffffff'))
    d.rectangle((left + 1, top + 1, right - 1, top + 2), fill=hexc('#ff6a5a'))


# ---------------------------------------------------------------- compose
def build(photo):
    img = Image.new('RGBA', (W, H), hexc('#2f5fae'))
    sky = Image.open(IMG + 'Dolomiti_Sky.png'); mountains = Image.open(IMG + 'Dolomiti_Mountains.png')
    valley = Image.open(IMG + 'Dolomiti_Valley.png')
    for layer, x0 in ((sky, 0), (mountains, -120), (valley, -40)):
        for x in range(x0, W, layer.width):
            img.alpha_composite(layer, (x, H - layer.height)) if x >= 0 else img.paste(layer, (x, H - layer.height), layer)

    cx, cy, R = W // 2, 92, 56
    # crossed skis behind the emblem (instead of Sonic's wings)
    right = ski(width=12, angle=24)                       # curled tip up and to the right
    left = right.transpose(Image.FLIP_LEFT_RIGHT)         # mirrored: tip up and to the left
    for s in (left, right):
        img.alpha_composite(s, (cx - s.width // 2, cy + 14 - s.height // 2))

    d = ImageDraw.Draw(img)
    d.ellipse((cx - R - 2, cy - R - 2, cx + R + 2, cy + R + 2), fill=OUTLINE)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=hexc('#f5c542'))
    d.ellipse((cx - R + 3, cy - R + 3, cx + R - 3, cy + R - 3), fill=hexc('#ffe08a'))
    d.ellipse((cx - R + 6, cy - R + 6, cx + R - 6, cy + R - 6), fill=hexc('#d9a521'))
    d.ellipse((cx - R + 11, cy - R + 11, cx + R - 11, cy + R - 11), fill=OUTLINE)
    d.ellipse((cx - R + 12, cy - R + 12, cx + R - 12, cy + R - 12), fill=hexc('#1d2a5c'))
    for ang in (-160, -125, -55, -20, 200, 340):
        a = math.radians(ang)
        star(d, cx + (R - 6) * math.cos(a), cy + (R - 6) * math.sin(a), 5, hexc('#2f6fd8'))

    bust = dudu_bust(photo)
    bx, by = cx - bust.width // 2 - 4, cy - R - 12
    img.alpha_composite(bust, (bx, by))
    puff = outline(pixel_art(PUFF, {'W': hexc('#ffffff'), 'w': hexc('#cfdaf0')}), color=hexc('#7f8fb0'))
    img.alpha_composite(puff, (bx + 80, by + 50))

    top, bottom = 122, 166
    d = ImageDraw.Draw(img)
    banner(d, top, bottom, cx - 118, cx + 118)
    title = chrome_text("GIBOREI HA'SKI", 26)
    if title.width > 236:
        title = chrome_text("GIBOREI HA'SKI", 22)
    img.alpha_composite(title, (cx - title.width // 2, top - 2))
    sub = pixel_text('STARRING DUDU POMPI', '#ffffff')
    img.alpha_composite(sub, (cx - sub.width // 2, bottom - 18))
    return img


def social(title):
    """1200x630 link-preview image (WhatsApp / Facebook / X): the title art plus a call to action."""
    art = title.copy()
    cta = pixel_text('PLAY IN YOUR BROWSER!', '#ffe08a')
    art.alpha_composite(cta, (W // 2 - cta.width // 2, 184))
    big = art.resize((1200, round(H * 1200 / W)), Image.NEAREST)
    top = (big.height - 630) // 2 + 6  # keep a little more sky than snow
    return big.crop((0, top, 1200, top + 630)).convert('RGB')


if __name__ == '__main__':
    title = build(sys.argv[1])
    title.save(IMG + 'Title.png')
    press = pixel_text('PRESS ENTER', '#ffe08a')
    press.save(IMG + 'Title_Press.png')
    # the loader can't use the pixel font yet (it's still loading), so its text is baked too
    pixel_text('LOADING', '#ffffff').save(IMG + 'Loader_Loading.png')
    pixel_text('CLICK TO START', '#ffe08a').save(IMG + 'Loader_Click.png')
    social(title).save('social.jpg', quality=90)
    if len(sys.argv) > 2:
        prev = title.copy()
        prev.alpha_composite(press, (W // 2 - press.width // 2, 188))
        prev.resize((W * 3, H * 3), Image.NEAREST).save(sys.argv[2])

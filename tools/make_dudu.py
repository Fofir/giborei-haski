"""Generates public/res/images/Player.png — 16-bit Dudu Pompi.
Sheet layout matches the original: 4 cols x 7 rows of 48x48 cells, feet on y=31, facing right."""
import sys
from PIL import Image

PAL = {
    'K': (26, 16, 32), 'B': (44, 74, 150), 'b': (92, 128, 205), 'G': (98, 170, 70),
    'O': (240, 138, 28), 'o': (255, 205, 120), 'L': (190, 80, 30),
    'S': (120, 70, 40), 's': (80, 44, 24), 'E': (255, 255, 255),
    'R': (220, 38, 42), 'r': (150, 20, 26), 'p': (255, 110, 95),
    'P': (110, 116, 130), 'q': (72, 76, 90), 'Y': (255, 190, 80),
    'W': (255, 255, 255), 'w': (200, 212, 232), 'Z': (205, 210, 220),
    'U': (130, 185, 245), 'V': (40, 90, 175),  # metallic blue whistle
}

HEAD = """
....KKKKKK....
..KKBBBBGGKK..
.KBbBBBBGGGGK.
.KbBBBBBBGGBBK
KBBBBBBBBBBBBK
KBbBBBBBBBBBBK
KBBBKKKKKKKKK.
KBBBKSSSSssSK.
KBBBKSSSSSESK.
KBbBKSSSSSKSK.
.KBBKsSSSSSSSK
..KKKKssssssK.
"""
HEAD_H = len(HEAD.strip('\n').split('\n'))

BODY = """
..KRRRRRRRSSK.
.KRpRRRRRRSSK.
KRpRRRWRRrRK..
KRRRRRWRRrK...
KSZRRRWRRRK...
.KKrrrrrrrK...
"""
LEGS = {
 'stand': """
..KPPPPPPPK...
..KPqPKPPqK...
..KOOKKOOOK...
..KOYOK.KOYOK.
""",
 'a': """
..KPPPPPPPK...
.KPqPK.KPPqK..
.KOOOK.KOOOK..
.KOYOK..KOYOK.
""",
 'b': """
..KPPPPPPPK...
..KPqPKPqK....
...KOOKOOOK...
..KOYOKOYOK...
""",
 'tuck': """
.KPPPPPPPPK...
.KOOOKKOOOK...
.KOYOK.KOYOK..
""",
}
SKIS = {
 'flat': """
...................K
KRRRRRRRRRRRRRRRRRRK
.KKKKKKKKKKKKKKKKKK.
""",
 'up': """
.................KK.
...............KRRK.
.........KKKKKKRRK..
...KKKKKKRRRRRRKK...
KKKRRRRRRRKKKKK.....
KRRRKKKKKK..........
.KK.................
""",
 'down': """
.KK.................
KRRRKKKKKK..........
KKKRRRRRRRKKKKK.....
...KKKKKKRRRRRRKK...
.........KKKKKKRRK..
...............KRRK.
.................KK.
""",
}
# small metallic-blue whistle at the mouth: (x, y, colour) relative to the head
WHISTLE = [(11, 11, 'V'), (12, 11, 'U'), (13, 11, 'U'), (14, 11, 'V'),
           (13, 10, 'U'), (14, 10, 'V'), (13, 12, 'V'), (14, 12, 'V'), (15, 11, 'K')]
# smoke blown out of the whistle
PUFF = [
 """
..ww.
.wWWw
wWWWw
.www.
""",
 """
...www..
..wWWWw.
.wWWWWWw
wWWWWWw.
.wwwww..
""",
 """
....wwww..
..wwWWWWw.
.wWWWWWWWw
wWWWWWWWw.
.wWWWWww..
..www.....
""",
 "",
]
TRAIL = """
www.
wWWw
.ww.
"""

FRONT = """
....KKKKKK....
..KKBBGGBBKK..
.KBbBBGGBBBBK.
KBbBBBGGBBBBBK
KBBBBBBBBBBBBK
KBBKKKKKKKKBBK
KBKSSSSSSSSKBK
KBKSssSSssSKBK
KBKSESSSSESKBK
KBKSKSSSSKSKBK
.KKsSSUVSSsKK.
..KKKsVVssKK..
.KRRRRSSRRRRK.
KRpRRRRWRRRRrK
KRRKRRRWRRKRRK
KSZKRRRWRRKZSK
.KK.KrrrrrK.KK
....KPPPPPK...
...KPqPKPqPK..
...KOOOKOOOK..
...KOYOKOYOK..
..KRRK...KRRK.
..KRRK...KRRK.
...KK.....KK..
"""
BACK = {
 'a': """
.KSK..KKKKKK..
.KRK.KBBGGBBK.
.KRKKBBBGGBBBK
.KRKBBBBGGBBBK
.KRKBBBBGGBBBK
.KRKBBBBBBBBBK
.KRKBBBBBBBBBK
.KRRKBBBBBBBK.
.KRRRKKKKKKKSK
..KRRRRRRRRRSK
..KRRRRRRRRRRK
..KRRRRRRRRRRK
..KRrRRRRRRRrK
..KRrRRRRRRRK.
..KrrrrrrrrrK.
...KPPPPPPPK..
...KPqPKPqPK..
...KPqPKKPPK..
...KOOOK.KOK..
...KOYOK.KOK..
...KKKK..KKK..
""",
}

def parse(s):
    rows = [r for r in s.strip('\n').split('\n')]
    return rows

def blit(img, ox, oy, art, flip=False):
    for y, row in enumerate(parse(art)):
        if flip: row = row[::-1]
        for x, ch in enumerate(row):
            if ch in PAL:
                px, py = ox + x, oy + y
                if 0 <= px < img.width and 0 <= py < img.height:
                    img.putpixel((px, py), PAL[ch] + (255,))

def side(legs='stand', skis='flat', bob=0, puff=None, crouch=0, trail=False):
    """Compose a right-facing frame. Feet/ski bottom lands on y=31."""
    c = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
    ski_art = parse(SKIS[skis])
    ski_top = 32 - len(ski_art)
    if skis == 'flat':
        ski_top = 32 - 3
    leg_h = len(parse(LEGS[legs]))
    leg_top = ski_top - leg_h + 1
    body_top = leg_top - 6 + bob
    head_top = body_top - HEAD_H + crouch
    hx = 15 + (1 if crouch else 0)
    if skis == 'flat':
        blit(c, 13, ski_top, SKIS['flat'])
    else:
        blit(c, 13, ski_top - 2, SKIS[skis])  # middle of the angled skis sits under the boots
    blit(c, 15, leg_top, LEGS[legs])
    blit(c, 15, body_top, BODY)
    blit(c, hx, head_top, HEAD)
    for x, y, col in WHISTLE:
        c.putpixel((hx + x, head_top + y), PAL[col] + (255,))
    if puff is not None and PUFF[puff]:
        blit(c, hx + 16, head_top + 12 - len(parse(PUFF[puff])), PUFF[puff])
    if trail:
        blit(c, 10, head_top + 2, TRAIL)
    return c

def place(sheet, idx, frame):
    sheet.alpha_composite(frame, ((idx % 4) * 48, (idx // 4) * 48))

def build(out):
    sheet = Image.new('RGBA', (192, 336), (0, 0, 0, 0))
    # idle: blowing smoke out of the whistle
    for i, (bob, pf) in enumerate([(0, 0), (0, 1), (1, 2), (1, 3)]):
        place(sheet, i, side(bob=bob, puff=pf))
    # run (ski)
    for i, (lg, bob) in enumerate([('a', 0), ('stand', -1), ('b', 0), ('stand', -1)]):
        place(sheet, 4 + i, side(legs=lg, bob=bob, puff=0 if i % 2 else None))
    # sprint (tucked)
    for i in range(4):
        place(sheet, 8 + i, side(legs='tuck', bob=1 + (i % 2), crouch=1, trail=i % 2 == 0))
    place(sheet, 12, side(skis='up', legs='a', puff=1))       # jump
    place(sheet, 13, side(skis='down', legs='b'))             # fall
    f = Image.new('RGBA', (48, 48)); blit(f, 17, 32 - len(parse(FRONT)), FRONT); place(sheet, 16, f)  # turn
    a = Image.new('RGBA', (48, 48)); blit(a, 17, 32 - len(parse(BACK['a'])), BACK['a']); place(sheet, 20, a)
    b = Image.new('RGBA', (48, 48)); blit(b, 17, 31 - len(parse(BACK['a'])), BACK['a'], flip=True); place(sheet, 21, b)
    for i in (24, 25, 26):
        place(sheet, i, side(puff=2))
    sheet.save(out)
    return sheet

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'public/res/images/Player.png'
    s = build(out)
    if len(sys.argv) > 2:
        bg = Image.new('RGBA', s.size, (150, 200, 240, 255)); bg.alpha_composite(s)
        bg.resize((s.width * 5, s.height * 5), Image.NEAREST).save(sys.argv[2])

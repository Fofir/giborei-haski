"""Marmot enemy (replaces the spiders): public/res/images/Spider_1.png + Spider_2.png.
3 waddle frames in 64x48 cells, facing left, feet on y=31. Run from the repo root."""
from PIL import Image

PAL = {'K': (74, 22, 30), 'B': (140, 88, 40), 'b': (176, 120, 60), 'd': (100, 58, 26),
       'O': (214, 138, 46), 'o': (240, 176, 90), 'C': (240, 218, 160), 'W': (255, 255, 255),
       'E': (255, 255, 255), 'T': (90, 56, 26), 't': (120, 78, 38)}

BODY = """
..KK......KK
.KbBK....KBbK
.KBBBKKKKBBBK
KBBBBBBBBBBBBK
KBEKBBBBBEKBBK
KBKKBBBBBKKBdK
KCCCCBBBBBBBBK
KCKKCCBBBBdBBK
KCCCCCCBBBBBBBK
.KCWWCCBBBBBdBK
..KKCCKOOOOBBBBK
..KBOOOOOOOOBdBBK
.KBOOoKOoKOOOBBBK
.KBOOOOOOOOOOBBBK
.KBdOOOOOOOOOBBdK
.KBBOOOOOOOOOBBBK
..KBBOOOOOOOBBBK
..KBBBOOOOOBBBBK
"""
FEET = {
    'stand': """
..KOOOKKKKOOOK
..KKKKK..KKKKK
""",
    'left': """
..KOOK...KOOOK
...KK....KKKKK
""",
    'right': """
..KOOOK...KOOK
..KKKKK....KK.
""",
}
TAILS = {
    'down': """
.
.
.
.
.
.
.
.
.
.
.
.
.
.
................KTTK
................KTtTTK
................KTTTTTK
................KKKKKKK
""",
    'up': """
.
.
.
.
.
.
.
.
.
.
.
..................KK
.................KTTK
................KTtTK
................KTTTK
................KTTK
.
.
""",
}


def parse(art):
    return art.strip('\n').split('\n')


def blit(img, ox, oy, art):
    for y, row in enumerate(parse(art)):
        for x, ch in enumerate(row):
            if ch in PAL:
                img.putpixel((ox + x, oy + y), PAL[ch] + (255,))


def frame(feet, tail, bob):
    c = Image.new('RGBA', (64, 48), (0, 0, 0, 0))
    ox, top = 24, 12
    blit(c, ox, top + bob, TAILS[tail])
    blit(c, ox, top + bob, BODY)
    blit(c, ox, top + 18, FEET[feet])
    return c


def sheet():
    s = Image.new('RGBA', (192, 48), (0, 0, 0, 0))
    for i, args in enumerate([('stand', 'down', 0), ('left', 'up', -1), ('right', 'down', 0)]):
        s.alpha_composite(frame(*args), (i * 64, 0))
    return s


if __name__ == '__main__':
    s = sheet()
    s.save('public/res/images/Spider_1.png')
    s.save('public/res/images/Spider_2.png')

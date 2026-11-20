"""Crow enemy (replaces the flying birds): public/res/images/Bird_1.png + Bird_2.png.
3 wing-flap frames in 48x48 cells, facing left. Run from the repo root."""
from PIL import Image

PAL = {'K': (42, 26, 44), 'P': (74, 52, 72), 'p': (104, 78, 102),
       'O': (236, 168, 64), 'o': (255, 210, 130), 'E': (255, 244, 220)}

BASE = """
...........K..K.......
............K.K.......
..........KKKKKK......
.........KPPPPPPK.....
........KoOOKoOOKPPK..
........KOKOKOKOKPPPK.
.KKKKKKKOOOKOOOKPPPPKK
KOoooOOOOOOOOOOKPPPPPK
.KOOOOOOOOOOOOKPPPPPPK
..KKKKKKKKKOOKPPPPPPPK
...KPPPPPPPKKPPPPPPPK.
.....KKPPPPPPPPPPPPK..
.......KKPPPPPPPPKK...
.........KKKKKKKK.....
............KO..KO....
............KO..KO....
...........KOO.KOO....
"""
# one wing in three positions, drawn over the body
WINGS = [
 """
.................KK.K.
................KPPKPK
...............KPpPPPK
..............KPpPPPK.
..............KPPPPK..
..............KPPPK...
""",
 """
......................
......................
......................
......................
......................
......................
......................
...............KKKKKKK
..............KPpppPPK
..............KPPPPPK.
...............KKKKK..
""",
 """
......................
......................
......................
......................
......................
......................
......................
......................
......................
.............KPPPPK...
.............KPpPPPK..
..............KPpPPK..
...............KPPPK..
................KPK...
.................K....
""",
]
BOBS = [0, 1, 2]  # body moves down slightly as the wing beats down


def parse(art):
    return art.strip('\n').split('\n')


def blit(img, ox, oy, art):
    for y, row in enumerate(parse(art)):
        for x, ch in enumerate(row):
            if ch in PAL:
                img.putpixel((ox + x, oy + y), PAL[ch] + (255,))


def frame(i):
    c = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
    ox, oy = 13, 15 + (1 if i == 2 else 0)
    blit(c, ox, oy, BASE)
    blit(c, ox, oy, WINGS[i])
    return c


def sheet():
    s = Image.new('RGBA', (144, 48), (0, 0, 0, 0))
    for i in range(3):
        s.alpha_composite(frame(i), (i * 48, 0))
    return s


if __name__ == '__main__':
    s = sheet()
    s.save('public/res/images/Bird_1.png')
    s.save('public/res/images/Bird_2.png')

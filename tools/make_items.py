"""Generates item art + sfx: public/res/images/Bolognese.png, public/res/sfx/powerup.wav.
Run from the repo root with numpy available (e.g. tools/chiptune/.venv/bin/python tools/make_items.py)."""
import wave
import numpy as np
from PIL import Image

PAL = {'K': (26, 16, 32), 'W': (255, 255, 255), 'w': (196, 210, 228),
       'Y': (246, 206, 92), 'y': (214, 160, 52), 'R': (196, 40, 30), 'r': (130, 22, 18),
       'G': (76, 175, 80), 'O': (250, 240, 200), 's': (232, 238, 248)}
# A steaming plate of spaghetti Bolognese
BOLOGNESE = """
................
................
.......s..s.....
......s..s......
.......s..s.....
.....KKKKKK.....
...KKRRGGRRKK...
..KRrRROGRrRRK..
..KYRRrRRORRYK..
.KYYYRRrRRYYYYK.
.KYyYYRRYYYyYYK.
KYYYyYYYYYYyYYYK
KWWWWWWWWWWWWWWK
KwWWWWWWWWWWWWwK
.KwwwwwwwwwwwwK.
..KKKKKKKKKKKK..
"""

def sprite(art, path):
    rows = art.strip('\n').split('\n')
    assert all(len(r) == len(rows[0]) for r in rows), 'ragged sprite rows'
    im = Image.new('RGBA', (len(rows[0]), len(rows)), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in PAL: im.putpixel((x, y), PAL[ch] + (255,))
    im.save(path)

def powerup(path, sr=22050):
    """Rising square-wave arpeggio, NES power-up style."""
    out = []
    for octave in range(3):
        for semis in (0, 4, 7, 12):
            f = 523.25 * 2 ** ((semis + octave * 5) / 12)
            t = np.arange(int(0.045 * sr)) / sr
            out.append(np.where((t * f) % 1 < 0.25, 1.0, -1.0) * np.linspace(1, 0.6, len(t)))
    y = np.concatenate(out) * 0.5
    y[-200:] *= np.linspace(1, 0, 200)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((y * 32767).astype('<i2').tobytes())

if __name__ == '__main__':
    sprite(BOLOGNESE, 'public/res/images/Bolognese.png')
    powerup('public/res/sfx/powerup.wav')

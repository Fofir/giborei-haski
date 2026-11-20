"""Transcribe the theme stems into a 16th-note grid (melody, bass, drums) -> song.json + song.mid."""
import json, sys, os
import numpy as np, librosa, mido

SRC = sys.argv[1]  # folder with "audio [vocals].mp3" etc.
SR = 22050
HOP = 256

def load(name):
    y, _ = librosa.load(os.path.join(SRC, f'audio [{name}].mp3'), sr=SR, mono=True)
    return y

drums, vocals, bass, music = load('drums'), load('vocals'), load('bass'), load('music')

# --- tempo & beat grid (drums are the most reliable) ---
tempo, beats = librosa.beat.beat_track(y=drums + music * 0.5, sr=SR, hop_length=HOP, units='time')
tempo = float(np.atleast_1d(tempo)[0])
beat_len = float(np.median(np.diff(beats)))
bpm = 60 / beat_len
offset = float(beats[0]) % beat_len
step = beat_len / 4
n_steps = int((len(drums) / SR - offset) / step)
print(f'bpm≈{bpm:.2f} (librosa {tempo:.1f}) first beat {beats[0]:.3f}s steps={n_steps}')

def mono_track(y, fmin, fmax):
    f0, voiced, prob = librosa.pyin(y, fmin=fmin, fmax=fmax, sr=SR, hop_length=HOP, frame_length=2048)
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0][:len(f0)]
    t = librosa.times_like(f0, sr=SR, hop_length=HOP)
    midi = librosa.hz_to_midi(np.where(voiced, f0, np.nan))
    out = []
    thr = np.percentile(rms[voiced] if voiced.any() else rms, 20) * 0.6
    for s in range(n_steps):
        a, b = offset + s * step, offset + (s + 1) * step
        m = (t >= a) & (t < b) & voiced & (rms > thr)
        if m.sum() >= max(1, int((b - a) / (HOP / SR) * 0.4)):
            out.append(int(round(np.nanmedian(midi[m]))))
        else:
            out.append(None)
    return out

melody = mono_track(vocals, librosa.note_to_hz('C3'), librosa.note_to_hz('C6'))
bassline = mono_track(bass, librosa.note_to_hz('E1'), librosa.note_to_hz('C4'))

# --- key from the full mix chroma ---
chroma = librosa.feature.chroma_cqt(y=music + vocals, sr=SR, hop_length=HOP * 2).mean(axis=1)
major = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
minor = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
best = max(((np.corrcoef(np.roll(p, k), chroma)[0, 1], k, n) for k in range(12) for p, n in ((major, 'major'), (minor, 'minor'))))
key_root, key_mode = best[1], best[2]
scale = [(key_root + i) % 12 for i in ([0,2,4,5,7,9,11] if key_mode == 'major' else [0,2,3,5,7,8,10])]
print('key:', librosa.midi_to_note(60 + key_root)[:-1], key_mode)

def to_scale(seq):
    res = []
    for n in seq:
        if n is None or n % 12 in scale: res.append(n); continue
        res.append(min((n - 1, n + 1), key=lambda m: 0 if m % 12 in scale else 1))
    return res

def clean(seq, min_len=2):
    """Remove 1-step blips by merging into neighbours."""
    seq = list(seq)
    for i in range(1, len(seq) - 1):
        if seq[i] != seq[i - 1] and seq[i] != seq[i + 1] and seq[i - 1] == seq[i + 1]:
            seq[i] = seq[i - 1]
    return seq

melody = clean(to_scale(melody))
bassline = clean(to_scale(bassline))

# --- drums: onsets classified by spectral content ---
onsets = librosa.onset.onset_detect(y=drums, sr=SR, hop_length=HOP, units='time', backtrack=False)
S = np.abs(librosa.stft(drums, n_fft=1024, hop_length=HOP))
freqs = librosa.fft_frequencies(sr=SR, n_fft=1024)
drum_grid = [None] * n_steps
for o in onsets:
    s = int(round((o - offset) / step))
    if not 0 <= s < n_steps: continue
    f = librosa.time_to_frames(o, sr=SR, hop_length=HOP)
    spec = S[:, f:f + 4].mean(axis=1)
    low, mid, high = spec[freqs < 150].sum(), spec[(freqs >= 150) & (freqs < 4000)].sum(), spec[freqs >= 4000].sum()
    tot = low + mid + high + 1e-9
    kind = 'K' if low / tot > 0.35 else ('S' if mid / tot > 0.45 else 'H')
    drum_grid[s] = kind

json.dump({'bpm': bpm, 'offset': offset, 'step': step, 'key': [key_root, key_mode],
           'melody': melody, 'bass': bassline, 'drums': drum_grid}, open('song.json', 'w'))

# --- MIDI export for editing in BeepBox / FamiStudio ---
mf = mido.MidiFile(ticks_per_beat=480); tps = 120
mf.tracks.append(mido.MidiTrack([mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm))]))
def add_track(seq, ch, name):
    tr = mido.MidiTrack([mido.MetaMessage('track_name', name=name)]); mf.tracks.append(tr)
    i, wait = 0, 0
    while i < len(seq):
        if seq[i] is None: wait += tps; i += 1; continue
        j = i
        while j < len(seq) and seq[j] == seq[i]: j += 1
        tr.append(mido.Message('note_on', note=seq[i], velocity=100, channel=ch, time=wait))
        tr.append(mido.Message('note_off', note=seq[i], velocity=0, channel=ch, time=(j - i) * tps))
        wait = 0; i = j
add_track(melody, 0, 'Melody (vocals)'); add_track(bassline, 1, 'Bass')
add_track([{'K': 36, 'S': 38, 'H': 42}.get(d) for d in drum_grid], 9, 'Drums')
mf.save('song.mid')

def coverage(seq): return sum(x is not None for x in seq) / len(seq)
print(f'melody coverage {coverage(melody):.0%}, bass {coverage(bassline):.0%}, drum hits {sum(d is not None for d in drum_grid)}')

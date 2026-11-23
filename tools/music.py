"""Original background music + sound effects, synthesised with numpy (no samples, no licences).

make_bed(mood, seconds) -> stereo float array; make_fx(fx, seconds) -> stereo float array.
Moods: tech (pulsing synth, 4-on-floor), tense (dark, slower pulse), epic (cinematic drums, swells).
"""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
rng = np.random.default_rng(11)


def hz(n):  # midi -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def env(n, a, r, sustain=True):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr) if sustain else 1
    return e


def saw(f, n, det=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for d in (-det, 0, det):
        ph = (t * f * (1 + d)) % 1.0
        out += 2 * ph - 1
    return out / 3


def reverb(x, secs=1.6, mix=0.25):
    n = int(secs * SR)
    ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n))
    ir = lp(ir, 5000)
    wet = fftconvolve(x, ir)[: len(x)]
    wet /= (np.abs(wet).max() + 1e-9)
    return x * (1 - mix) + wet * mix * (np.abs(x).max() + 1e-9)


def kick(n=int(0.45 * SR)):
    t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)


def hat(n=int(0.08 * SR)):
    return hp(rng.standard_normal(n), 7000) * np.exp(-np.linspace(0, 9, n))


def tom(f0=90, n=int(0.9 * SR)):
    t = np.arange(n) / SR
    f = f0 * (1 + .6 * np.exp(-t * 18))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5) + lp(rng.standard_normal(n), 600) * np.exp(-t * 20) * .4


MOODS = {
    #        bpm  root  chords (semitones from root, minor)              kick pattern / 16ths
    "tech": dict(bpm=112, root=57, prog=[[0, 3, 7, 10], [-4, 0, 3, 7], [-7, -3, 0, 5], [-2, 2, 5, 9]], kick="four", arp=True, bassdiv=8),
    "tense": dict(bpm=96, root=50, prog=[[0, 3, 7], [0, 3, 8], [-2, 3, 7], [-4, 0, 3]], kick="half", arp=False, bassdiv=8),
    "epic": dict(bpm=100, root=52, prog=[[0, 3, 7], [-4, 0, 3], [-9, -5, -2], [-2, 2, 5]], kick="epic", arp=True, bassdiv=4),
}


def place(buf, s, at):
    i = int(at * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(s))
    buf[i:j] += s[: j - i]


def make_bed(mood, seconds):
    m = MOODS.get(mood, MOODS["tech"])
    n = int((seconds + 1) * SR)
    beat = 60 / m["bpm"]; bar = 4 * beat
    pad = np.zeros(n); bass = np.zeros(n); drums = np.zeros(n); arp = np.zeros(n)
    nbars = int(seconds / bar) + 2
    for b in range(nbars):
        ch = m["prog"][(b // 2) % len(m["prog"])]
        t0 = b * bar; L = int(bar * SR)
        # pad
        p = sum(saw(hz(m["root"] + 12 + x), L, .004) for x in ch) / len(ch)
        place(pad, p * env(L, .25 * bar, .2 * bar), t0)
        # bass pulses
        step = bar / m["bassdiv"]
        for k in range(m["bassdiv"]):
            ln = int(step * .9 * SR); tt = np.arange(ln) / SR
            f = hz(m["root"] - 12 + ch[0])
            s = (np.sin(2 * np.pi * f * tt) + .35 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * (6 if m["bassdiv"] == 8 else 2.5))
            place(bass, s, t0 + k * step)
        if b == 0:
            continue  # intro bar: no drums / arp
        for k in range(4):
            bt = t0 + k * beat
            if m["kick"] == "four" or (m["kick"] == "half" and k in (0, 2)) or (m["kick"] == "epic" and k == 0):
                place(drums, kick() * .9, bt)
            if m["kick"] == "epic":
                if k in (1, 3): place(drums, tom(80 if k == 1 else 65) * .55, bt)
                if k == 2: place(drums, tom(110) * .35, bt + beat / 2)
            if m["kick"] != "epic" or k % 2:
                place(drums, hat() * .22, bt + beat / 2)
                if m["kick"] == "four": place(drums, hat() * .1, bt + beat / 4); place(drums, hat() * .1, bt + 3 * beat / 4)
        if m["arp"]:
            notes = ch + [x + 12 for x in ch]
            for k in range(16):
                ln = int(beat / 4 * .95 * SR); tt = np.arange(ln) / SR
                f = hz(m["root"] + 12 + notes[(k * 3) % len(notes)])
                s = (2 * np.abs(2 * ((tt * f) % 1) - 1) - 1) * np.exp(-tt * 14)
                place(arp, s, t0 + k * beat / 4)
    pad = reverb(lp(pad, 1800 if mood != "epic" else 2600), 2.4, .4)
    arp = reverb(lp(arp, 3200), 1.4, .35)
    bass = lp(np.tanh(bass * 1.6), 400)
    mix = pad * .30 + bass * .42 + drums * .55 + arp * .14
    # fade in/out
    fi, fo = int(1.2 * SR), int(2.5 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)
    end = int(seconds * SR)
    mix = mix[:end]
    mix[-fo:] *= np.linspace(1, 0, fo)
    mix /= np.abs(mix).max() + 1e-9
    st = np.stack([mix, np.roll(mix, int(.012 * SR)) * .96], 1)
    return st


def whoosh(d=0.6):
    n = int(d * SR); t = np.linspace(0, 1, n)
    x = rng.standard_normal(n)
    out = np.zeros(n); seg = n // 12
    for i in range(12):  # moving band
        c = 300 + 3500 * np.sin(np.pi * (i + .5) / 12) ** 2
        sl = slice(i * seg, n if i == 11 else (i + 1) * seg)
        out[sl] = bp(x, c * .6, min(c * 1.6, SR / 2 - 100))[sl]
    return out * np.sin(np.pi * t) ** 2


def impact():
    n = int(1.2 * SR); t = np.arange(n) / SR
    f = 38 + 60 * np.exp(-t * 14)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    crack = lp(rng.standard_normal(n), 2500) * np.exp(-t * 30) * .5
    return reverb(boom + crack, 1.2, .25)


def pop():
    n = int(.12 * SR); t = np.arange(n) / SR
    f = 700 + 900 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)


def make_fx(fx, seconds):
    n = int(seconds * SR) + SR
    buf = np.zeros(n)
    for t in fx.get("whoosh", []): place(buf, whoosh() * .5, max(0, t))
    for t in fx.get("hits", []): place(buf, impact() * .55, max(0, t))
    for t in fx.get("pops", []): place(buf, pop() * .25, max(0, t))
    buf = buf[: int(seconds * SR)]
    return np.stack([buf, buf], 1)


def write_wav(path, x):
    from scipy.io import wavfile
    x = np.clip(x, -1, 1)
    wavfile.write(path, SR, (x * 32767).astype(np.int16))

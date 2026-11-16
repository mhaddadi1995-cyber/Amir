# Procedural music bed: 112 BPM, G major (I-vi-IV-V), santur-like hammered strings, daf, claps, bass.
import sys, wave, numpy as np
SR = 48000; BPM = 112; BEAT = 60 / BPM; BAR = 4 * BEAT
dur = float(sys.argv[2]); N = int((dur + 2) * SR)
L = np.zeros(N); Rr = np.zeros(N)
rng = np.random.default_rng(9)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N: return
    L[i:j] += sig[:j - i] * gain * (1 - pan) ; Rr[i:j] += sig[:j - i] * gain * (1 + pan)
def santur(m, d=1.6):
    n = int(d * SR); t = np.arange(n) / SR; f = hz(m); y = np.zeros(n)
    for k in range(1, 9):
        fk = f * k * (1 + 0.0007 * k * k)
        a = 1 / k ** 0.9; tau = 1.1 / k ** 0.75
        y += a * (np.sin(2 * np.pi * fk * t) + 0.8 * np.sin(2 * np.pi * fk * 1.0035 * t + 1.3)) * np.exp(-t / tau)
    att = rng.standard_normal(n) * np.exp(-t / 0.004) * 0.6
    return (y + att) * np.minimum(1, t / 0.002)
def bass(m, d=0.5):
    n = int(d * SR); t = np.arange(n) / SR; f = hz(m)
    return (np.sin(2 * np.pi * f * t) + .25 * np.sin(4 * np.pi * f * t)) * np.exp(-t / .28) * np.minimum(1, t / .005)
def dum():
    n = int(.4 * SR); t = np.arange(n) / SR; f = 60 + 70 * np.exp(-t / .03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .18) + rng.standard_normal(n) * np.exp(-t / .008) * .3
def tak():
    n = int(.25 * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); x = x - np.convolve(x, np.ones(6) / 6, 'same')  # crude highpass
    jing = rng.standard_normal(n) * (0.6 + 0.4 * np.sin(2 * np.pi * 38 * t)) ; jing -= np.convolve(jing, np.ones(3) / 3, 'same')
    return x * np.exp(-t / .03) * .8 + jing * np.exp(-t / .09) * .5
def clap():
    n = int(.3 * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    x = np.convolve(x, np.ones(4) / 4, 'same') - np.convolve(x, np.ones(40) / 40, 'same')
    e = sum(np.exp(-np.maximum(0, t - o) / .012) * (t >= o) for o in (0, .011, .022)) + np.exp(-t / .09) * .4
    return x * e * .9
def shaker():
    n = int(.08 * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); x -= np.convolve(x, np.ones(2) / 2, 'same')
    return x * np.sin(np.pi * t / t[-1]) ** 2 * .25
# chords (midi roots) G Em C D
prog = [(55, [67, 71, 74]), (52, [64, 67, 71]), (48, [64, 67, 72]), (50, [66, 69, 74])]
# santur motif per bar: 8 eighth notes as chord-tone indexes (+12 for upper octave), None = rest
motif_a = [0, 1, 2, 1, 12, 2, 1, 2]
motif_b = [2, 12, 13, 12, 2, 1, 0, 1]
nbars = int(np.ceil(dur / BAR)) + 1
for b in range(nbars):
    t0 = b * BAR; root, tones = prog[b % 4]
    full = 1 <= b < nbars - 1
    mot = motif_a if (b // 4) % 2 == 0 else motif_b
    for i, idx in enumerate(mot):
        if idx is None: continue
        m = tones[idx % 12] + (12 if idx >= 12 else 0)
        add(santur(m), t0 + i * BEAT / 2 + rng.uniform(0, .006), .13 if i % 2 == 0 else .10, pan=.25 if i % 2 else -.15)
        if i in (0, 4): add(santur(m - 12, 2.2), t0 + i * BEAT / 2, .07, pan=-.3)
    if b >= 1:
        for q in range(4): add(bass(root - 12 if q % 2 == 0 else root - 5), t0 + q * BEAT, .32)
    # daf: dum . tak . | dum dum tak .
    if b >= 1 or True:
        for pos, kind in ((0, 'd'), (1, 't'), (1.5, 't'), (2, 'd'), (2.5, 'd'), (3, 't')):
            if not full and kind == 'd' and pos > 0: continue
            add(dum() if kind == 'd' else tak(), t0 + pos * BEAT, .45 if kind == 'd' else .22, pan=0 if kind == 'd' else .1)
    if full:
        for q in (1, 3): add(clap(), t0 + q * BEAT, .25, pan=-.05)
        for s in range(16): add(shaker(), t0 + s * BEAT / 4, .10 if s % 2 else .06, pan=.35)
# end hit on the final downbeat near dur
end_t = (np.floor((dur - .3) / BEAT)) * BEAT
for m in (55, 67, 71, 74, 79): add(santur(m, 2.5), end_t, .12)
add(dum(), end_t, .5)
y = np.stack([L, Rr], 1)
# simple reverb: convolve with decaying noise IR
ir_n = int(.7 * SR); ir = rng.standard_normal((ir_n, 2)) * np.exp(-np.arange(ir_n) / SR / .18)[:, None]
from numpy.fft import rfft, irfft
nfft = 1 << int(np.ceil(np.log2(N + ir_n)))
wet = np.stack([irfft(rfft(y[:, c], nfft) * rfft(ir[:, c], nfft), nfft)[:N] for c in range(2)], 1)
y = y + wet * (0.06 / (np.abs(wet).max() + 1e-9)) * np.abs(y).max() * 3
y = y[:int(dur * SR)]
fo = int(1.0 * SR); y[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
y /= np.abs(y).max() + 1e-9; y *= .9
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())
print('music', sys.argv[1], len(y) / SR)

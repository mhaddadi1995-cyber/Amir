# Synthesises SFX and mixes VO + music + SFX into the final soundtrack.
# Usage: python3 audio.py <sfx.json> <vo.wav|none> <music.wav|none> <out.wav> <duration>
import json, sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(3)

def env(n, a=0.005, r=0.2, shape=3.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / max(r, 1e-4) * shape / 3)
    return e

def noise(n):
    return rng.standard_normal(n)

def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i in range(len(x)):
        s = (1 - a) * x[i] + a * s; y[i] = s
    return y

def sweep_bp_noise(dur, f0, f1, q=2.0):
    # noise through a moving band-pass (state variable filter)
    n = int(dur * SR); x = noise(n); y = np.zeros(n)
    low = band = 0.0
    fs = np.geomspace(f0, f1, n)
    for i in range(n):
        f = 2 * np.sin(np.pi * fs[i] / SR)
        high = x[i] - low - band / q
        band += f * high; low += f * band
        y[i] = band
    return y / (np.abs(y).max() + 1e-9)

def sine_sweep(dur, f0, f1, decay=0.08):
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.geomspace(f0, f1, n); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / decay)

def tone(dur, f, decay=0.4, harm=(1, .5, .25)):
    n = int(dur * SR); t = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * (k + 1) * t) for k, a in enumerate(harm))
    return y * np.exp(-t / decay) * np.minimum(1, t / 0.003)

def make():
    S = {}
    w = sweep_bp_noise(0.45, 300, 4000, 1.5); w *= np.sin(np.linspace(0, np.pi, len(w))) ** 1.5; S['whoosh'] = w * .9
    w = sweep_bp_noise(0.35, 4000, 600, 2.5); w *= np.sin(np.linspace(0, np.pi, len(w))) ** 2; S['swish'] = w * .6
    w = sweep_bp_noise(0.5, 250, 3000, 2); w *= np.sin(np.linspace(0, np.pi, len(w))) ** 1.2; S['swoosh_up'] = w * .8
    w = sweep_bp_noise(0.5, 3000, 250, 2); w *= np.sin(np.linspace(0, np.pi, len(w))) ** 1.2; S['swoosh_down'] = w * .8
    S['pop'] = sine_sweep(0.12, 900, 300, 0.035) * .9 + tone(0.12, 1400, 0.02, (0.2,)) * .3
    S['tick'] = tone(0.06, 2400, 0.012, (1, .3)) * .5
    t = np.arange(int(.45 * SR)) / SR
    S['boing'] = np.sin(2 * np.pi * (220 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t / .2)) * t) * np.exp(-t / .18) * .7
    sp = sweep_bp_noise(0.5, 1800, 500, 1.2) * env(int(.5 * SR), .003, .12)
    S['splash'] = sp * .9 + onepole_lp(noise(int(.5 * SR)), 900) * env(int(.5 * SR), .002, .08) * 1.5
    # sparkle: cascade of high bells
    sp = np.zeros(int(1.0 * SR))
    for k, f in enumerate([2093, 2637, 3136, 3951, 4699, 3520]):
        o = int(k * 0.07 * SR); tt = tone(0.6, f, 0.18, (1, .2)); sp[o:o + len(tt)] += tt[:len(sp) - o] * .35
    S['sparkle'] = sp
    d = sine_sweep(0.18, 600, 1600, 0.05); S['drip'] = d * .8
    sz = onepole_lp(noise(int(1.2 * SR)), 5000) * (0.6 + 0.4 * (rng.random(int(1.2 * SR)) > .97)); sz *= env(len(sz), .2, .8); S['sizzle'] = sz * .25
    ch = np.zeros(int(1.4 * SR))
    for k, f in enumerate([1046.5, 1318.5, 1568]):
        o = int(k * 0.09 * SR); tt = tone(1.2, f, 0.5, (1, .35, .1)); ch[o:o + len(tt)] += tt[:len(ch) - o] * .4
    S['chime'] = ch
    S['fill'] = sine_sweep(0.5, 300, 1200, 0.5) * np.sin(np.linspace(0, np.pi, int(.5 * SR))) * .35
    S['ding'] = tone(1.0, 1568, 0.35, (1, .5, .2)) * .7 + tone(1.0, 2093, 0.3, (1,)) * .35
    th = sine_sweep(0.35, 140, 45, 0.12) * 1.2 + onepole_lp(noise(int(.35 * SR)), 1200) * env(int(.35 * SR), .001, .04) * 2
    S['stamp'] = th
    S['thud'] = sine_sweep(0.3, 130, 45, 0.09) * 1.0 + onepole_lp(noise(int(.3 * SR)), 600) * env(int(.3 * SR), .001, .03) * 1.2
    cr = onepole_lp(noise(int(1.2 * SR)), 3000) * env(int(1.2 * SR), .15, .6) * .5; S['cheer'] = cr
    # rain bed (8 s, will be looped)
    n = int(8 * SR); r = onepole_lp(noise(n), 6000) * .25 + onepole_lp(noise(n), 900) * .5
    drops = (rng.random(n) > 0.9985).astype(float) * rng.random(n)
    r += np.convolve(drops, tone(0.03, 3500, 0.006, (1,)), 'same') * 1.5
    S['rain'] = r * .5
    for k in S: S[k] = S[k] / (np.abs(S[k]).max() + 1e-9)
    return S

def readwav(p):
    import subprocess
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

def main():
    sfxj, vo_p, mus_p, out_p, dur = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5])
    N = int(dur * SR); mix = np.zeros((N, 2), np.float32)
    S = make()
    events = json.load(open(sfxj))
    cues = json.loads(open('timing.js').read().split('window.CUES=')[1].split(';')[0])
    sfx_bus = np.zeros((N, 2), np.float32)
    for e in events:
        name = e['name']
        if name == 'rain':
            # rain from 0 until 'before', and again ans→gilan
            for a, b, g in ((0, cues['before'], .07), (cues['ans'], cues['gilan'], .05)):
                i0, i1 = int(a * SR), min(N, int(b * SR))
                seg = np.tile(S['rain'], int((i1 - i0) / len(S['rain'])) + 2)[:i1 - i0]
                fade = np.minimum(1, np.minimum(np.arange(i1 - i0), (i1 - i0) - np.arange(i1 - i0)) / (0.25 * SR))
                sfx_bus[i0:i1] += (seg * fade * g)[:, None]
            continue
        x = S[name] * e['gain'] * .38
        i0 = int(max(0, e['t']) * SR); i1 = min(N, i0 + len(x))
        pan = {'tick': .3, 'sparkle': .25, 'pop': .1}.get(name, 0) * (1 if hash(str(e['t'])) % 2 else -1)
        sfx_bus[i0:i1, 0] += x[:i1 - i0] * (1 - pan); sfx_bus[i0:i1, 1] += x[:i1 - i0] * (1 + pan)
    vo = np.zeros((N, 2), np.float32)
    if vo_p != 'none':
        v = readwav(vo_p)[:N]; vo[:len(v)] = v
    mus = np.zeros((N, 2), np.float32)
    if mus_p != 'none':
        m = readwav(mus_p); m = m[:N]; mus[:len(m)] = m
        # duck music under the voice (smoothed envelope)
        ve = np.abs(vo).mean(1)
        k = int(0.08 * SR); ve = np.convolve(ve, np.ones(k) / k, 'same')
        thr = 0.02; duck = np.where(ve > thr, 0.45, 1.0)
        k2 = int(0.25 * SR); duck = np.convolve(duck, np.ones(k2) / k2, 'same')
        fade_out = np.ones(N); fo = int(1.2 * SR); fade_out[-fo:] = np.linspace(1, 0, fo)
        mus *= (duck * fade_out)[:, None] * 0.55
    mix = vo * 1.0 + mus + sfx_bus
    peak = np.abs(mix).max(); mix *= min(1.0, 0.89 / (peak + 1e-9))
    with wave.open(out_p, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    print('wrote', out_p, 'peak', float(peak))

if __name__ == '__main__':
    main()

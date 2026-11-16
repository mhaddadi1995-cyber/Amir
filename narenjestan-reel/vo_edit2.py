# VO edit v2: aligns the script's chunks to detected speech segments with dynamic programming
# (works for any voice), tightens pauses, optional gentle atempo, and a clean dry vocal chain.
# Usage: python3 vo_edit2.py <raw> <out.wav> <out_chunks.json> [tempo=1.0] [gap=0.12]
import json, re, subprocess, sys, wave
import numpy as np

SR = 48000
RAW, OUT_WAV, OUT_JSON = sys.argv[1], sys.argv[2], sys.argv[3]
TEMPO = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
GAP = float(sys.argv[5]) if len(sys.argv) > 5 else 0.12

CHUNKS = [
    ("این نارنج سبزه...", "hook"), ("به نظرت کاله یا رسیده؟", "q"), ("جوابش آخر ویدیو!", "tease"),
    ("ولی قبلش ببین چه کارا می‌کنه:", "before"), ("یک،", "b1"), ("بمب ویتامین سی و آنتی‌اکسیدانه.", "b1"),
    ("دو،", "b2"), ("آبش جای لیمو و سرکه رو می‌گیره؛", "b2"), ("روی ماهی و سالاد، معرکه‌ست!", "b2"),
    ("سه،", "b3"), ("از پوستش خوشمزه‌ترین مربا درمیاد.", "b3"),
    ("چهار،", "b4"), ("شکوفه‌اش همون بهارنارنجه؛", "b4"), ("عطرش آدمو آروم می‌کنه.", "b4"),
    ("و اما جواب...", "ans"), ("رسیده‌ست!", "ansWord"), ("تو مرکبات، رنگ پوست ملاک رسیدن نیست؛", "rule"),
    ("نارنج پاییزی گیلان سبزه،", "gilan"), ("ولی پر از آبه.", "gilan2"),
    ("نارنج تازه، مستقیم از باغ‌های گیلان...", "cta"), ("نارنجستان!", "brand"), ("برای سفارش، دایرکت بده.", "order"),
]
GAP_BEFORE = {"ansWord": 0.32, "ans": 0.26, "cta": 0.26}

def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def segments(p, noise, d):
    log = subprocess.run(['ffmpeg', '-v', 'info', '-i', p, '-af', f'silencedetect=noise={noise}dB:d={d}', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(v) for v in re.findall(r'silence_start: ([\d.]+)', log)]
    en = [float(v) for v in re.findall(r'silence_end: ([\d.]+)', log)]
    return st, en

x = load(RAW); dur = len(x) / SR
def speech_segs(noise, d):
    st, en = segments(RAW, noise, d)
    segs, cur = [], 0.0
    for s, e in zip(st, en):
        if s > cur + 0.04: segs.append((cur, s))
        cur = e
    if dur > cur + 0.04: segs.append((cur, dur))
    return segs

weight = lambda t: len(re.sub(r'[\s‌.،؛!؟:…]', '', t)) + 2
n = len(CHUNKS)
segs = None
# finer detection first: the DP merges segments, so over-segmenting is safe (exactly n segs forces 1:1)
for noise, d in ((-36, .07), (-38, .09), (-40, .11), (-40, .14)):
    s = speech_segs(noise, d)
    if len(s) >= n: segs = s; break
assert segs, 'not enough pauses detected'
m = len(segs)
W = np.array([weight(t) for t, _ in CHUNKS], float)
D = np.array([b - a for a, b in segs])
rate = D.sum() / W.sum()
# DP: chunk i covers segments j..k (contiguous); minimise relative duration error
INF = 1e18
cost = np.full((n + 1, m + 1), INF); back = np.zeros((n + 1, m + 1), int); cost[0, 0] = 0
for i in range(1, n + 1):
    pred = W[i - 1] * rate
    for k in range(i, m - (n - i) + 1):
        for j in range(i - 1, k):
            if cost[i - 1, j] >= INF: continue
            span = segs[k - 1][1] - segs[j][0]
            c = cost[i - 1, j] + ((span - pred) / pred) ** 2
            if c < cost[i, k]: cost[i, k] = c; back[i, k] = j
bounds, k = [], m
for i in range(n, 0, -1):
    j = back[i, k]; bounds.append((segs[j][0], segs[k - 1][1])); k = j
bounds.reverse()

pieces, meta, t = [], [], 0.0
PRE, POST = 0.03, 0.07
for (s, e), (text, seg) in zip(bounds, CHUNKS):
    g = GAP_BEFORE.get(seg, GAP) if meta else 0.0
    if g: pieces.append(np.zeros(int(g * SR), np.float32)); t += g
    a, b = max(0, int((s - PRE) * SR)), min(len(x), int((e + POST) * SR))
    y = x[a:b].copy(); f = int(0.006 * SR); y[:f] *= np.linspace(0, 1, f); fo = int(0.03 * SR); y[-fo:] *= np.linspace(1, 0, fo)
    meta.append({"text": text, "seg": seg, "s": t + PRE, "e": t + (b - a) / SR - POST}); pieces.append(y); t += (b - a) / SR
y = np.concatenate(pieces)
tmp = OUT_WAV + '.tmp.wav'
with wave.open(tmp, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
chain = []
if abs(TEMPO - 1) > 1e-3: chain.append(f'atempo={TEMPO}')
chain += ['highpass=f=85', 'equalizer=f=280:t=q:w=1.1:g=-2.5', 'equalizer=f=3200:t=q:w=1.3:g=2',
          'agate=threshold=0.015:ratio=2.5:attack=3:release=90:range=0.25',
          'acompressor=threshold=-20dB:ratio=3:attack=4:release=70:makeup=2.5', 'loudnorm=I=-15:TP=-1.5:LRA=7']
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', ','.join(chain), '-ar', str(SR), '-ac', '1', OUT_WAV], check=True)
for mm in meta: mm["s"] = round(mm["s"] / TEMPO, 3); mm["e"] = round(mm["e"] / TEMPO, 3)
json.dump(meta, open(OUT_JSON, 'w'), ensure_ascii=False, indent=1)
print(f'raw {dur:.2f}s, {m} speech segs -> {n} chunks; edited {t:.2f}s -> {t / TEMPO:.2f}s (tempo {TEMPO})')
for mm in meta: print(f"{mm['s']:6.2f} {mm['e']:6.2f} {mm['e']-mm['s']:5.2f}  {mm['seg']:8s} {mm['text']}")

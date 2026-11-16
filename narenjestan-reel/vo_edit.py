# Edit the raw VO: split on detected pauses, drop chunks, tighten gaps, time-stretch.
# Writes media/vo.wav and build/chunks.json (chunk text + new start/end).
import json, subprocess, sys, wave
import numpy as np

SR = 48000
RAW, OUT_WAV, OUT_JSON, TEMPO = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])

CHUNKS = [  # (text, seg) in spoken order — 23 chunks separated by pauses
    ("این نارنج سبزه...", "hook"), ("به نظرت کاله یا رسیده؟", "q"), ("جوابش آخر ویدیو!", "tease"),
    ("ولی قبلش ببین چه کارا می‌کنه:", "before"), ("یک،", "b1"), ("بمب ویتامین سی و آنتی‌اکسیدانه؛", "b1"),
    ("مخصوص سرمای پاییز.", "b1x"), ("دو،", "b2"), ("آبش جای لیمو و سرکه رو می‌گیره؛", "b2"),
    ("روی ماهی و سالاد، معرکه‌ست!", "b2"), ("سه،", "b3"), ("از پوستش خوشمزه‌ترین مربا درمیاد.", "b3"),
    ("چهار،", "b4"), ("شکوفه‌ش همون بهارنارنجه؛", "b4"), ("عطرش آدمو آروم می‌کنه.", "b4"),
    ("و اما جواب:", "ans"), ("رسیده‌ست!", "ansWord"), ("تو مرکبات، رنگ پوست ملاک رسیدن نیست؛", "rule"),
    ("نارنج پاییزی گیلان سبزه،", "gilan"), ("ولی پر از آبه.", "gilan2"), ("نارنج تازه، مستقیم از باغ‌های گیلان...", "cta"),
    ("نارنجستان!", "brand"), ("برای سفارش، دایرکت بده.", "order"),
]
DROP = {"b1x"}
GAP = 0.11
GAP_BEFORE = {"ans": 0.30, "ansWord": 0.34, "cta": 0.30, "b1": 0.16}

raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', RAW, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
x = np.frombuffer(raw, np.float32).copy()
log = subprocess.run(['ffmpeg', '-v', 'info', '-i', RAW, '-af', 'silencedetect=noise=-38dB:d=0.15', '-f', 'null', '-'], capture_output=True, text=True).stderr
import re
starts = [float(v) for v in re.findall(r'silence_start: ([\d.]+)', log)]
ends = [float(v) for v in re.findall(r'silence_end: ([\d.]+)', log)]
dur = len(x) / SR
# speech intervals = complement of silences
speech, cur = [], 0.0
for s, e in zip(starts, ends):
    if s > cur + 0.05: speech.append((cur, s))
    cur = e
if dur > cur + 0.05: speech.append((cur, dur))
assert len(speech) == len(CHUNKS), (len(speech), speech)

pieces, meta, t = [], [], 0.0
PRE, POST = 0.035, 0.06
for (s, e), (text, seg) in zip(speech, CHUNKS):
    if seg in DROP: continue
    g = GAP_BEFORE.get(seg, GAP) if meta else 0.0
    if g: pieces.append(np.zeros(int(g * SR), np.float32)); t += g
    a, b = max(0, int((s - PRE) * SR)), min(len(x), int((e + POST) * SR))
    seg_audio = x[a:b].copy()
    f = int(0.008 * SR); seg_audio[:f] *= np.linspace(0, 1, f); seg_audio[-f:] *= np.linspace(1, 0, f)
    meta.append({"text": text, "seg": seg, "s": t + PRE, "e": t + (b - a) / SR - POST})
    pieces.append(seg_audio); t += (b - a) / SR
y = np.concatenate(pieces)
tmp = OUT_WAV + '.tmp.wav'
with wave.open(tmp, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af',
                f'rubberband=tempo={TEMPO}:transients=mixed:detector=soft:window=standard:formant=preserved,'
                'highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3dB,loudnorm=I=-15:TP=-1.5:LRA=7',
                '-ar', str(SR), '-ac', '1', OUT_WAV], check=True)
for m in meta:
    m["s"] = round(m["s"] / TEMPO, 3); m["e"] = round(m["e"] / TEMPO, 3)
json.dump(meta, open(OUT_JSON, 'w'), ensure_ascii=False, indent=1)
print('edited length', round(t, 2), '-> stretched', round(t / TEMPO, 2))
for m in meta: print(f"{m['s']:6.2f} {m['e']:6.2f}  {m['seg']:8s} {m['text']}")

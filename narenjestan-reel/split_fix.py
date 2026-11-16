# Split a multi-line fix take at its longest pauses into separate wav files.
# Usage: python3 split_fix.py <take.mp3> out1.wav out2.wav [out3.wav ...]
import re, subprocess, sys, wave, numpy as np
SR = 48000; src, outs = sys.argv[1], sys.argv[2:]
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout, np.float32)
log = subprocess.run(['ffmpeg', '-v', 'info', '-i', src, '-af', 'silencedetect=noise=-40dB:d=0.15', '-f', 'null', '-'], capture_output=True, text=True).stderr
st = [float(v) for v in re.findall(r'silence_start: ([\d.]+)', log)]; en = [float(v) for v in re.findall(r'silence_end: ([\d.]+)', log)]
inner = sorted([(e - s, s, e) for s, e in zip(st, en) if s > 0.3 and e < len(x) / SR - 0.3], reverse=True)[:len(outs) - 1]
cuts = sorted(int((s + e) / 2 * SR) for _, s, e in inner)
print(f'total {len(x)/SR:.2f}s; cuts at', [round(c / SR, 2) for c in cuts], 'pauses', [round(d, 2) for d, _, _ in inner])
bounds = [0] + cuts + [len(x)]
for name, a, b in zip(outs, bounds, bounds[1:]):
    with wave.open(name, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x[a:b], -1, 1) * 32767).astype(np.int16).tobytes())
    print(name, f'{(b - a)/SR:.2f}s')

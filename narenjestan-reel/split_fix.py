# Split the 2-line fix take at its longest pause into media/fix_hook.wav and media/fix_rule.wav
import re, subprocess, sys, wave, numpy as np
SR = 48000; src = sys.argv[1]
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout, np.float32)
log = subprocess.run(['ffmpeg', '-v', 'info', '-i', src, '-af', 'silencedetect=noise=-40dB:d=0.25', '-f', 'null', '-'], capture_output=True, text=True).stderr
st = [float(v) for v in re.findall(r'silence_start: ([\d.]+)', log)]; en = [float(v) for v in re.findall(r'silence_end: ([\d.]+)', log)]
inner = [(e - s, s, e) for s, e in zip(st, en) if s > 0.3 and e < len(x) / SR - 0.3]
d, s, e = max(inner); cut = int((s + e) / 2 * SR)
print(f'total {len(x)/SR:.2f}s, longest pause {d:.2f}s at {s:.2f}-{e:.2f}')
for name, z in (('media/fix_hook.wav', x[:cut]), ('media/fix_rule.wav', x[cut:])):
    with wave.open(name, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(z, -1, 1) * 32767).astype(np.int16).tobytes())
    print(name, f'{len(z)/SR:.2f}s')

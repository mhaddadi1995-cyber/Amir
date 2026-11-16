import sys, glob, numpy as np
from PIL import Image
fs = sorted(glob.glob(sys.argv[1] + '/*.jpg'))
A = []
for f in fs:
    im = Image.open(f); im.draft('RGB', (270, 480)); A.append(np.asarray(im.convert('L').resize((270, 480)), np.float32))
A = np.stack(A)
def d(a, b): return np.abs(a - b)
flag = []
for i in range(1, len(A) - 1):
    a, b, c = A[i - 1], A[i], A[i + 1]
    # per-region (tile) test: frame differs from both neighbours where neighbours agree
    t1, t2, t3 = d(a, b), d(b, c), d(a, c)
    k = 30
    tiles = lambda x: x[:480 // k * k, :270 // k * k].reshape(480 // k, k, 270 // k, k).mean((1, 3))
    s = np.minimum(tiles(t1), tiles(t2)) - tiles(t3)
    if s.max() > 12: flag.append((i, float(s.max())))
print(len(fs), 'frames; flagged', len(flag))
for i, v in flag: print(fs[i].split('/')[-1], round(v, 1))

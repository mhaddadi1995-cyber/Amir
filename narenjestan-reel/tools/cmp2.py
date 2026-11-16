import sys, glob, os, numpy as np
from PIL import Image
a, b = sys.argv[1], sys.argv[2]
diff = []
for f in sorted(glob.glob(a + '/*.jpg')):
    n = os.path.basename(f)
    x = Image.open(f); x.draft('RGB', (1080, 1920)); y = Image.open(os.path.join(b, n)); y.draft('RGB', (1080, 1920))
    x = np.asarray(x.convert('L'), np.float32); y = np.asarray(y.convert('L'), np.float32)
    k = 40; H, W = x.shape
    t = np.abs(x - y)[:H // k * k, :W // k * k].reshape(H // k, k, W // k, k).mean((1, 3))
    diff.append((int(n[:5]), float(t.max())))
v = np.array([d for _, d in diff]); print('median', np.median(v), 'p99', np.percentile(v, 99), 'max', v.max())
bad = [n for n, d in diff if d > 6]
print('differ', len(bad)); print(','.join(map(str, bad)))

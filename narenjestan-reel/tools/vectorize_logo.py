import sys, numpy as np, potrace
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
im = np.array(Image.open(src).convert('RGBA')).astype(np.float32)
rgb, a = im[..., :3], im[..., 3] / 255.0
H, W = a.shape
S = 4
palette = {'orange': (246, 139, 35), 'leaf': (110, 162, 64), 'lime': (163, 205, 57), 'text': (68, 105, 35)}
names = list(palette)
P = np.array([palette[n] for n in names], np.float32)
lab = ((rgb[..., None, :] - P[None, None]) ** 2).sum(-1).argmin(-1)
yy, xx = np.mgrid[0:H, 0:W]
def trace(m):
    up = np.array(Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).resize((W * S, H * S), Image.BICUBIC)) > 127
    pl = potrace.Bitmap(~up).trace(turdsize=30, alphamax=1.0, opticurve=True, opttolerance=0.2)
    d = []
    for c in pl:
        sp = c.start_point; d.append(f"M{sp.x/S:.2f},{sp.y/S:.2f}")
        for seg in c:
            if seg.is_corner:
                d.append(f"L{seg.c.x/S:.2f},{seg.c.y/S:.2f}L{seg.end_point.x/S:.2f},{seg.end_point.y/S:.2f}")
            else:
                d.append(f"C{seg.c1.x/S:.2f},{seg.c1.y/S:.2f} {seg.c2.x/S:.2f},{seg.c2.y/S:.2f} {seg.end_point.x/S:.2f},{seg.end_point.y/S:.2f}")
        d.append('Z')
    return ''.join(d), len(pl)
defs, paths = [], []
# arc
d, n = trace(a * (lab == 0)); paths.append(f'<path id="logo-arc" fill="#f68b23" fill-rule="evenodd" d="{d}"/>'); print('arc', n)
# text (dark green), only below the leaves region
d, n = trace(a * (lab == 3) * (yy > 300)); paths.append(f'<path id="logo-text" fill="#446923" fill-rule="evenodd" d="{d}"/>'); print('text', n)
# leaves: leaf|lime (and dark pixels in top region), split by x
leafm = a * ((lab == 1) | (lab == 2) | ((lab == 3) & (yy < 300)))
for name, sel in (('leafL', xx < 248), ('leafR', xx >= 248)):
    m = leafm * sel * (yy < 300)
    w = m > 0.9
    pts = np.stack([xx[w], yy[w]], 1).astype(np.float32); cols = rgb[w]
    mu = pts.mean(0); u, s, vt = np.linalg.svd(pts - mu, full_matrices=False); ax = vt[0]
    t = (pts - mu) @ ax
    lo, hi = np.percentile(t, 3), np.percentile(t, 97)
    c0 = cols[t < lo + (hi - lo) * 0.15].mean(0); c1 = cols[t > hi - (hi - lo) * 0.15].mean(0)
    p0, p1 = mu + ax * lo, mu + ax * hi
    hx = lambda c: '#%02x%02x%02x' % tuple(int(v) for v in c)
    defs.append(f'<linearGradient id="g{name}" gradientUnits="userSpaceOnUse" x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}"><stop offset="0" stop-color="{hx(c0)}"/><stop offset="1" stop-color="{hx(c1)}"/></linearGradient>')
    d, n = trace(m); paths.append(f'<path id="logo-{name}" fill="url(#g{name})" fill-rule="evenodd" d="{d}"/>'); print(name, n, hx(c0), hx(c1))
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><defs>{"".join(defs)}</defs>' + ''.join(paths) + '</svg>'
open(out, 'w').write(svg)

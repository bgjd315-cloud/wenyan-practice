"""Usage: python -I scripts/crop.py <exam_key> "<spec>" <out.png>
spec: one or more segments separated by ';'  e.g.  "4:120-980"  or  "9:1500-2250;10:90-800"
optional x-range per segment: "4:120-980:100-1600" (default: full text width)
Red/pink watermark pixels ('新聞用試題本' etc.) are whitened. Output is stacked vertically."""
import sys, os, numpy as np
from PIL import Image
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
key, spec, out = sys.argv[1], sys.argv[2], sys.argv[3]
if key[:2] in ('xc', 'zk'):   # 高中：學測 xc、指考 zk
    BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hs', 'raw')
parts = []
for seg in spec.split(';'):
    f = seg.strip().split(':')
    pg = int(f[0]); y0, y1 = map(int, f[1].split('-'))
    im = np.asarray(Image.open(f'{BASE}/pages/{key}/p{pg:02d}.png').convert('RGB')).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    red = (r - np.maximum(g, b) > 22)
    v = np.where(r > 150, 255, r * 0.45)   # bright red stamp / pink -> white; dark text printed over the stamp -> dark gray
    im = im.copy()
    for c in range(3): im[..., c] = np.where(red, v, im[..., c])
    H, W = im.shape[:2]
    if len(f) > 2: x0, x1 = map(int, f[2].split('-'))
    else: x0, x1 = 60, W - 60
    parts.append(im[max(0, y0):min(H, y1), x0:x1].astype(np.uint8))
w = max(p.shape[1] for p in parts)
canvas = np.full((sum(p.shape[0] for p in parts) + 20 * (len(parts) - 1), w, 3), 255, np.uint8)
y = 0
for p in parts:
    canvas[y:y + p.shape[0], :p.shape[1]] = p; y += p.shape[0] + 20
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
Image.fromarray(canvas).save(out, optimize=True)
print(out, canvas.shape)

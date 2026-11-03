import json, glob, os, re, sys, collections
import numpy as np
from PIL import Image
ROOT = sys.argv[1]; os.chdir(ROOT)
only = sys.argv[2:] 
def load(fn):
    a = np.asarray(Image.open(fn).convert('RGB')).astype(int)
    r,g,b = a[...,0],a[...,1],a[...,2]
    red = (r - np.maximum(g,b) > 60)            # watermark / colored marks
    gray = (r+g+b)/3
    ink = (gray < 140) & ~red
    return ink
res = {}
for f in sorted(glob.glob('ocr/*.json')):
    key = os.path.basename(f)[:-5]
    if only and key not in only: continue
    pages = json.load(open(f, encoding='utf-8'))
    # main text left edge: most common x0 (bucketed)
    xs = collections.Counter(l['b'][0]//8*8 for p in pages for l in p['lines'] if len(l['t'])>8)
    L = xs.most_common(1)[0][0]
    segs = []
    for p in pages:
        ink = load(f"pages/{key}/p{p['page']:02d}.png")
        H, W = ink.shape
        x0, x1 = max(0, L-130), L-14
        col = ink[:, x0:x1].sum(1)
        # rows with ink in margin column
        rows = np.where(col > 2)[0]
        starts = []
        if len(rows):
            grp = [rows[0]]
            for y in rows[1:]:
                if y - grp[-1] > 12: starts.append((grp[0], grp[-1])); grp=[y]
                else: grp.append(y)
            grp and starts.append((grp[0], grp[-1]))
        # content extent
        allrows = np.where(ink[:, :].sum(1) > 3)[0]
        # ignore footer: page number / 請翻頁 box (bottom 6%)
        bottom = int(H*0.93); top = int(H*0.03)
        starts = [s for s in starts if top < s[0] < bottom and s[1]-s[0] < 80]
        res.setdefault(key, {'L': L, 'pages': []})['pages'].append({'page': p['page'], 'H': H, 'W': W, 'starts': [list(map(int,s)) for s in starts]})
json.dump(res, open('marks.json','w'), indent=0)
for k,v in res.items(): print(k, v['L'], [len(p['starts']) for p in v['pages']])

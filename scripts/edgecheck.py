import json, glob, os, numpy as np
from PIL import Image
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
flag = []
for f in sorted(glob.glob('raw/data/*.json')):
    for it in json.load(open(f, encoding='utf-8'))['items']:
        p = 'site/' + (it.get('img') or f"img/{it['id']}.png")
        a = np.asarray(Image.open(p).convert('L')) < 120
        H = a.shape[0]
        top, bot = a[:4].sum(), a[-4:].sum()
        # also count ink in any 4-row band at segment joins is hard; check edges only
        if top > 3 or bot > 3: flag.append((it['id'], it.get('crop'), int(top), int(bot), H))
for x in flag: print(*x)
print('flagged', len(flag))

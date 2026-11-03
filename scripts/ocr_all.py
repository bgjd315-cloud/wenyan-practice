import pymupdf, glob, os, json, asyncio, sys
import winocr
from PIL import Image
ROOT = sys.argv[1]
os.chdir(ROOT)
# choose source per exam
srcs = {}
for f in sorted(glob.glob('pdf/*exam*.pdf')):
    key = os.path.basename(f).replace('-examnw.pdf','').replace('-exam.pdf','')
    if f.endswith('examnw.pdf'):
        d = pymupdf.open(f)
        if sum(len(p.get_text()) for p in d) > 1000 or key not in srcs: srcs[key] = f
    else:
        srcs.setdefault(key, f)
json.dump(srcs, open('sources.json','w'), indent=1)
async def ocr(img):
    r = await winocr.recognize_pil(img, 'zh-Hant-TW')
    out = []
    for ln in r.lines:
        ws = ln.words
        x0 = min(w.bounding_rect.x for w in ws); y0 = min(w.bounding_rect.y for w in ws)
        x1 = max(w.bounding_rect.x + w.bounding_rect.width for w in ws); y1 = max(w.bounding_rect.y + w.bounding_rect.height for w in ws)
        out.append({'t': ln.text.replace(' ', ''), 'b': [round(x0), round(y0), round(x1), round(y1)]})
    return out
async def main():
    for key, f in srcs.items():
        if os.path.exists(f'ocr/{key}.json'): continue
        os.makedirs(f'pages/{key}', exist_ok=True); os.makedirs('ocr', exist_ok=True)
        d = pymupdf.open(f); res = []
        for i, p in enumerate(d):
            pix = p.get_pixmap(dpi=200)
            fn = f'pages/{key}/p{i+1:02d}.png'; pix.save(fn)
            img = Image.open(fn).convert('RGB')
            res.append({'page': i+1, 'w': pix.width, 'h': pix.height, 'lines': await ocr(img)})
        json.dump(res, open(f'ocr/{key}.json','w',encoding='utf-8'), ensure_ascii=False)
        print(key, len(d), flush=True)
asyncio.run(main())

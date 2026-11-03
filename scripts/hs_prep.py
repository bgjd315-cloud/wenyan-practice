"""高中版：把學測/指考 PDF 轉成頁圖、刻度圖、文字座標（格式同國中版 ocr/*.json）、答案文字與參考資料文字。"""
import pymupdf, glob, os, json, sys
from PIL import Image, ImageDraw, ImageFont
os.chdir(sys.argv[1])
DPI = 200; S = DPI / 72
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 30)
for d in ('pages', 'ruled', 'ocr', 'ans'): os.makedirs(d, exist_ok=True)
for f in sorted(glob.glob('pdf/*-exam.pdf')):
    key = os.path.basename(f)[:-9]
    doc = pymupdf.open(f); res = []
    os.makedirs(f'pages/{key}', exist_ok=True); os.makedirs(f'ruled/{key}', exist_ok=True)
    for i, p in enumerate(doc):
        pix = p.get_pixmap(dpi=DPI); fn = f'pages/{key}/p{i+1:02d}.png'; pix.save(fn)
        lines = []
        for b in p.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                t = ''.join(s['text'] for s in l['spans']).strip()
                if t: lines.append({'t': t.replace(' ', ''), 'b': [round(v * S) for v in l['bbox']]})
        lines.sort(key=lambda l: (l['b'][1], l['b'][0]))
        res.append({'page': i + 1, 'w': pix.width, 'h': pix.height, 'lines': lines})
        im = Image.open(fn).convert('RGB'); dr = ImageDraw.Draw(im); W, H = im.size
        for y in range(0, H, 100):
            dr.line([(0, y), (W, y)], fill=(0, 160, 255), width=1)
            dr.text((4, y + 2), str(y), fill=(0, 90, 255), font=font); dr.text((W - 80, y + 2), str(y), fill=(0, 90, 255), font=font)
        im.save(f'ruled/{key}/p{i+1:02d}.png')
    json.dump(res, open(f'ocr/{key}.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print(key, len(doc), flush=True)
txt = {}
for f in sorted(glob.glob('pdf/*-ans.pdf')):
    key = os.path.basename(f)[:-8]; doc = pymupdf.open(f)
    txt[key] = '\n'.join(p.get_text() for p in doc)
    for i, p in enumerate(doc): p.get_pixmap(dpi=110).save(f'ans/{key}-p{i+1}.png')
json.dump(txt, open('ans/ans_text.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for f in sorted(glob.glob('ref/*.pdf')):
    open(f[:-4] + '.txt', 'w', encoding='utf-8').write('\n'.join(p.get_text() for p in pymupdf.open(f)))
print('done')

import json, glob, os, sys, pymupdf
from PIL import Image, ImageDraw, ImageFont
os.chdir(sys.argv[1])
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 30)
for d in sorted(glob.glob('pages/*')):
    key = os.path.basename(d); os.makedirs(f'ruled/{key}', exist_ok=True)
    for f in sorted(glob.glob(d+'/*.png')):
        im = Image.open(f).convert('RGB'); dr = ImageDraw.Draw(im); W,H = im.size
        for y in range(0, H, 100):
            dr.line([(0,y),(W,y)], fill=(0,160,255), width=1)
            dr.text((4,y+2), str(y), fill=(0,90,255), font=font)
            dr.text((W-80,y+2), str(y), fill=(0,90,255), font=font)
        im.save(f'ruled/{key}/'+os.path.basename(f))
os.makedirs('ans', exist_ok=True)
txt = {}
for f in sorted(glob.glob('pdf/*-ans.pdf')):
    key = os.path.basename(f)[:-8]; doc = pymupdf.open(f)
    txt[key] = '\n'.join(p.get_text() for p in doc)
    for i,p in enumerate(doc):
        p.get_pixmap(dpi=110).save(f'ans/{key}-p{i+1}.png')
json.dump(txt, open('ans/ans_text.json','w',encoding='utf-8'), ensure_ascii=False, indent=0)
print({k: len(v) for k,v in txt.items()})

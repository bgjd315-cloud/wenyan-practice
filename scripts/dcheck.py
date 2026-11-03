import json,glob,re,sys,os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
bad=[]
for f in sorted(glob.glob('raw/data/*.json')):
    ex=os.path.basename(f)[:-5]
    ocr=json.load(open(f'raw/ocr/{ex}.json',encoding='utf-8'))
    for it in json.load(open(f,encoding='utf-8'))['items']:
        nD=0
        for seg in it['crop'].split(';'):
            p,yy=seg.split(':')[:2]; y0,y1=map(int,yy.split('-'))
            for l in ocr[int(p)-1]['lines']:
                if y0<=l['b'][1] and l['b'][3]<=y1 and re.search(r'[\(（][D0O][\)）]',l['t']): nD+=1
        if nD < len(it['nums']): bad.append((it['id'],it['crop'],len(it['nums']),nD))
for b in bad: print(*b)
print(len(bad))

"""Merge raw/data/*.json into site/data.js (window.EXAMS / window.ITEMS / window.METHOD).
python build.py        國中版（raw → site）
python build.py hs     高中版（hs/raw → hs/site）"""
import json, glob, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
HS = len(sys.argv) > 1 and sys.argv[1] == 'hs'
os.chdir(os.path.join(ROOT, 'hs') if HS else ROOT)

def label(key):
    if HS:
        return f'{key[2:]}{"學測" if key.startswith("xc") else "指考"}'
    m = re.match(r'bc(\d+)-(\w+)', key)
    if m:
        y, s = m.groups()
        if s == 'nbk': return f'{y}年北北基聯測'
        if y in ('101', '102'): return f'{y}年基測'
        return f'{y}年第{"一" if s == "1" else "二"}次基測'
    return f'{key[2:]}年{"試辦" if key == "hk102" else ""}會考'

def kind(key):
    return {'xc': '學測', 'zk': '指考', 'bc': '基測', 'hk': '會考'}[key[:2]]

def order(key):
    m = re.match(r'(bc|hk|xc|zk)(\d+)(?:-(\w+))?', key)
    t, y, s = m.groups()
    return (int(y), 0 if t in ('bc', 'xc') else 1, {'1': 0, '2': 1, 'nbk': 2}.get(s or '', 0))

def answer_ok(q):
    if HS and q.get('qtype') == '非選':
        return True
    a = q.get('answer') or ''
    return bool(a) and all(c in q.get('options', {}) for c in a) and (len(a) == 1 or q.get('qtype') == '多選')

exams, items, problems = [], [], []
for f in sorted(glob.glob('raw/data/*.json'), key=lambda f: order(os.path.basename(f)[:-5])):
    key = os.path.basename(f)[:-5]
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        problems.append(f'{key}: JSON error {e}'); continue
    y = int(re.search(r'\d+', key).group())
    exams.append({'key': key, 'label': label(key), 'year': y, 'kind': kind(key),
                  'total': d.get('total_questions'), 'count': len(d.get('items', []))})
    for it in d.get('items', []):
        it['exam'] = key; it['label'] = label(key); it['year'] = y; it['kind'] = kind(key)
        img = it.get('img') or f"img/{it['id']}.png"
        it['img'] = img
        if not os.path.exists(os.path.join('site', img)): problems.append(f"{it['id']}: missing {img}")
        for q in it.get('questions', []):
            if not answer_ok(q): problems.append(f"{it['id']} q{q.get('n')}: answer={q.get('answer')}")
        for k in ('official', 'note', 'crop'):   # teacher-only notes stay in raw/data
            it.pop(k, None)
        items.append(it)
exams.sort(key=lambda e: order(e['key']))
method = open('raw/method.html', encoding='utf-8').read() if os.path.exists('raw/method.html') else ''
method = method.replace('{{ITEMS}}', str(len(items))).replace('{{QS}}', str(sum(len(i.get('questions', [])) for i in items)))
with open('site/data.js', 'w', encoding='utf-8') as w:
    w.write('window.EXAMS=' + json.dumps(exams, ensure_ascii=False) + ';\n')
    w.write('window.ITEMS=' + json.dumps(items, ensure_ascii=False) + ';\n')
    w.write('window.METHOD=' + json.dumps(method, ensure_ascii=False) + ';\n')
nq = sum(len(i.get('questions', [])) for i in items)
print(f'exams={len(exams)} items={len(items)} questions={nq}')
for p in problems: print('PROBLEM', p)

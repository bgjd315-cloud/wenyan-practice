"""檢查題目資料的完整性與圖片是否存在。

python scripts/validate.py        檢查國中版（raw/data → site/）
python scripts/validate.py hs     檢查高中版（hs/raw/data → hs/site/）
python scripts/validate.py all    兩版都檢查

ERROR：一定要修，否則網站會壞（缺圖、答案不在選項裡、題號重複……）
WARN ：可能有問題，請人工確認（解析裡寫的答案和標準答案不同、題號不連續……）
有 ERROR 時結束碼為 1，方便日後放進自動檢查。
"""
import glob, json, os, re, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

GENRES = {'寓言故事', '史傳人物', '說理議論', '山水遊記', '筆記小品', '書信序跋', '經典語錄', '古典詩詞曲', '其他'}
TYPES = {'字詞解釋', '虛詞句式', '句意理解', '文意推論', '主旨寓意', '人物情感', '寫作手法', '比較閱讀', '文化常識', '典故出處', '詩詞賞析'}
DIFFS = {'易', '中', '難'}
FORMS = {'單題', '題組'}
QTYPES = {'單選', '多選', '非選'}
TEXTCATS = {'部定古文', '延伸', '學術文本', '科普文本', '生活情境文本', '文學文本'}
ITEM_TEXT = ('source', 'author', 'passage', 'translation')
# author 允許空白（命題者自撰、出處待查）；passage、translation 在「文字都在選項裡」的題目可以空白

try:
    from PIL import Image
except ImportError:          # 沒裝 Pillow 時只檢查檔案存在
    Image = None


class Report:
    def __init__(self, name):
        self.name, self.errors, self.warns = name, [], []

    def err(self, where, msg): self.errors.append(f'{where}: {msg}')
    def warn(self, where, msg): self.warns.append(f'{where}: {msg}')

    def print(self):
        print(f'\n=== {self.name}：ERROR {len(self.errors)}、WARN {len(self.warns)} ===')
        for e in self.errors: print('ERROR', e)
        for w in self.warns: print('WARN ', w)


# 解析中明說「答案(X)」「故選(X)」的地方，用來比對標準答案。
# 不採「(X)正確」：選「錯誤的是」的題目，解析也會寫「(A)正確」。
CLAIM = re.compile(r'(?:答案(?:為|是|選)?|故選|應選)\s*[：:]?\s*((?:[（(][A-E][)）]|[A-E]){1,5})')


def claimed_answers(text):
    return {''.join(sorted(set(re.sub(r'[^A-E]', '', m.group(1))))) for m in CLAIM.finditer(text or '')}


def check_question(r, where, q, hs):
    qt = q.get('qtype') if hs else '單選'
    if hs and qt not in QTYPES:
        r.err(where, f'qtype 不正確：{qt!r}')
    if not isinstance(q.get('n'), int) and not (qt == '非選' and str(q.get('n') or '').strip()):
        r.err(where, f'題號 n 不是整數：{q.get("n")!r}')
    for k in ('stem', 'explain'):
        if not str(q.get(k) or '').strip():
            r.err(where, f'缺少 {k}')
    if not str(q.get('skill') or '').strip():
        r.warn(where, '缺少解題小撇步 skill')
    if '�' in json.dumps(q, ensure_ascii=False):
        r.err(where, '含有亂碼字元 �')
    if qt == '非選':
        if not str(q.get('ref_answer') or '').strip():
            r.err(where, '非選題缺少參考答案 ref_answer')
        return
    opts = q.get('options') or {}
    want = ['A', 'B', 'C', 'D', 'E'] if qt == '多選' else ['A', 'B', 'C', 'D']
    if sorted(opts) != want:
        r.err(where, f'選項代號應為 {"".join(want)}，實際為 {"".join(sorted(opts)) or "（無）"}')
    for k, v in opts.items():
        if not str(v or '').strip():
            r.err(where, f'選項 ({k}) 是空的')
    vals = [re.sub(r'\s', '', str(v)) for v in opts.values()]
    if len(set(vals)) != len(vals):
        r.warn(where, '有兩個選項內容完全相同')
    a = q.get('answer') or ''
    if not a:
        r.err(where, '缺少答案')
    elif any(c not in opts for c in a):
        r.err(where, f'答案 {a} 不在選項裡')
    elif qt == '單選' and len(a) != 1:
        r.err(where, f'單選題答案卻有 {len(a)} 個：{a}')
    elif qt == '多選' and a != ''.join(sorted(set(a))):
        r.err(where, f'多選答案應依字母排序且不重複（網頁用字串比對）：{a}')
    # 解析明寫的答案若和標準答案不同，可能其中一個打錯了
    claim = claimed_answers(q.get('explain'))
    if a and claim and ''.join(sorted(a)) not in claim:
        r.warn(where, f'解析寫「答案 {"/".join(sorted(claim))}」，標準答案卻是 {a}')


def check(hs):
    base = os.path.join(ROOT, 'hs') if hs else ROOT
    r = Report('高中版' if hs else '國中版')
    files = sorted(glob.glob(os.path.join(base, 'raw', 'data', '*.json')))
    if not files:
        r.err('raw/data', '找不到任何題目資料')
    textcat = {}
    tc_path = os.path.join(base, 'raw', 'textcat.json')
    if hs:
        if os.path.exists(tc_path):
            textcat = json.load(open(tc_path, encoding='utf-8'))
        else:
            r.err('raw/textcat.json', '檔案不存在')
    seen_ids, used_imgs, all_ids = {}, set(), set()
    nitems = nq = 0
    for f in files:
        key = os.path.basename(f)[:-5]
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception as e:
            r.err(key, f'JSON 讀取失敗：{e}'); continue
        if d.get('exam') != key:
            r.err(key, f'exam 欄位 {d.get("exam")!r} 和檔名不同')
        total = d.get('total_questions')
        if not isinstance(total, int):
            r.err(key, 'total_questions 不是整數')
        nums_in_exam = {}
        for it in d.get('items', []):
            nitems += 1
            iid = it.get('id') or '(無 id)'
            where = iid
            all_ids.add(iid)
            if iid in seen_ids:
                r.err(where, f'id 重複（也出現在 {seen_ids[iid]}）')
            seen_ids[iid] = key
            if it.get('exam') != key:
                r.err(where, f'exam 欄位 {it.get("exam")!r} 和檔名 {key} 不同')
            if not str(iid).startswith(key + '-'):
                r.err(where, f'id 開頭應為 {key}-')
            for k in ('source',):
                if not str(it.get(k) or '').strip():
                    r.err(where, f'缺少 {k}')
            has_p, has_t = (bool(str(it.get(k) or '').strip()) for k in ('passage', 'translation'))
            if has_p and not has_t:
                r.warn(where, '有原文 passage 但沒有白話翻譯 translation')
            elif not has_p and has_t:
                r.warn(where, '有白話翻譯 translation 但沒有原文 passage')
            elif not has_p and not hs:
                r.warn(where, '沒有原文 passage 也沒有翻譯')
            if it.get('genre') not in GENRES:
                r.err(where, f'文章種類 genre 不在清單內：{it.get("genre")!r}')
            if it.get('form') not in FORMS:
                r.err(where, f'form 應為單題或題組：{it.get("form")!r}')
            if it.get('difficulty') not in DIFFS:
                r.err(where, f'difficulty 應為易／中／難：{it.get("difficulty")!r}')
            types = it.get('types') or []
            if not types:
                r.err(where, '缺少題型 types')
            for t in types:
                if t not in TYPES:
                    r.err(where, f'題型不在清單內：{t!r}')
            kws = it.get('keywords')
            if not isinstance(kws, list) or not kws:
                r.warn(where, '沒有重要字詞 keywords')
            else:
                for kw in kws:
                    if not isinstance(kw, dict) or not str(kw.get('w') or '').strip() or not str(kw.get('m') or '').strip():
                        r.err(where, f'重要字詞格式錯誤：{kw!r}')
            for k in ITEM_TEXT:
                if '�' in str(it.get(k) or ''):
                    r.err(where, f'{k} 含有亂碼字元 �')
            # 圖片
            img = it.get('img') or f'img/{iid}.png'
            path = os.path.join(base, 'site', img)
            used_imgs.add(os.path.normpath(path))
            if not os.path.exists(path):
                r.err(where, f'圖片不存在：{img}')
            elif os.path.getsize(path) < 1000:
                r.err(where, f'圖片檔太小，可能壞掉：{img}')
            elif Image:
                try:
                    with Image.open(path) as im:
                        w, h = im.size
                        im.verify()
                    if w < 300 or h < 40:
                        r.warn(where, f'圖片尺寸異常 {w}×{h}：{img}')
                except Exception as e:
                    r.err(where, f'圖片無法開啟：{img}（{e}）')
            if os.path.basename(img).rsplit('.', 1)[0] != iid:
                r.warn(where, f'圖檔名 {img} 和 id 不同')
            # 題目
            qs = it.get('questions') or []
            if not qs:
                r.err(where, '沒有任何題目'); continue
            ns = [q.get('n') for q in qs]
            if it.get('nums') != ns:
                r.err(where, f'nums {it.get("nums")} 和題目題號 {ns} 不一致')
            if it.get('form') == '單題' and len(qs) != 1:
                r.err(where, f'標為單題卻有 {len(qs)} 題')
            if it.get('form') == '題組' and len(qs) < 2:
                r.warn(where, '標為題組卻只有 1 題')
            if all(isinstance(n, int) for n in ns) and ns != list(range(ns[0], ns[0] + len(ns))):
                r.warn(where, f'題組題號不連續：{ns}')
            for q in qs:
                nq += 1
                n = q.get('n')
                qwhere = f'{iid} 第{n}題'
                if n in nums_in_exam:
                    r.err(qwhere, f'同一份考卷題號重複（也在 {nums_in_exam[n]}）')
                nums_in_exam[n] = iid
                if isinstance(n, int) and isinstance(total, int) and n > total and q.get('qtype') != '非選':
                    r.err(qwhere, f'題號大於總題數 {total}')
                check_question(r, qwhere, q, hs)
            if hs:
                tc = textcat.get(iid)
                if not tc:
                    r.err(where, 'textcat.json 沒有這題的文本類別')
                else:
                    for k in ('textcat', 'textcat2'):
                        if tc.get(k) and tc[k] not in TEXTCATS:
                            r.err(where, f'{k} 不在清單內：{tc[k]!r}')
                    if not tc.get('textcat'):
                        r.err(where, '文本類別 textcat 是空的')
    # 沒有對應題目的多餘圖片（不影響網站，只是占空間）
    for p in sorted(glob.glob(os.path.join(base, 'site', 'img', '*'))):
        if os.path.normpath(p) not in used_imgs:
            r.warn('site/img', f'沒有題目使用這張圖：{os.path.basename(p)}')
    for iid in sorted(set(textcat) - all_ids):
        r.warn('raw/textcat.json', f'有類別但找不到題目：{iid}')
    # 解題方法頁裡「練這題」的連結
    mpath = os.path.join(base, 'raw', 'method.html')
    if os.path.exists(mpath):
        html = open(mpath, encoding='utf-8').read()
        refs = re.findall(r'data-open-item="([^"]+)"', html)
        for s in re.findall(r'data-open-set="([^"]+)"', html):
            refs += s.split(',')
        for iid in sorted(set(refs) - all_ids):
            r.err('raw/method.html', f'連結到不存在的題目：{iid}')
    if hs:
        cpath = os.path.join(base, 'raw', 'core15.json')
        if os.path.exists(cpath):
            for name, ids in json.load(open(cpath, encoding='utf-8')).items():
                for iid in ids:
                    if iid not in all_ids:
                        r.err('raw/core15.json', f'{name} 連到不存在的題目：{iid}')
    r.name += f'（{len(files)} 份考卷、{nitems} 組、{nq} 題）'
    return r


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    arg = sys.argv[1] if len(sys.argv) > 1 else ''
    which = [False, True] if arg == 'all' else [arg == 'hs']
    reports = [check(hs) for hs in which]
    for rep in reports:
        rep.print()
    sys.exit(1 if any(rep.errors for rep in reports) else 0)

"""高中版教師研究頁：把 research2.md、analysis_by_text.md、research.md 包進 hs/site/teacher.html（用 marked 在瀏覽器轉成 HTML）"""
import json, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hs'))
docs = [('research2', '解題方法深化研究', 'raw/research2.md'),
        ('analysis', '題庫依文本類別分析', 'raw/analysis_by_text.md'),
        ('research1', '初版研究（命題趨勢與名師方法）', 'raw/research.md')]
data = {k: open(p, encoding='utf-8').read() for k, _, p in docs}
tabs = ''.join(f'<button data-doc="{k}"{" class=on" if i == 0 else ""}>{t}</button>' for i, (k, t, _) in enumerate(docs))
html = '''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>字裡山河・教師研究</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;900&display=swap">
<style>
:root{--bg:#f5f0e6;--paper:#fffcf5;--ink:#2b2622;--muted:#7a6f64;--line:#e3d9c8;--accent:#a23b2a;--soft:#f3e2da}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#1b1916;--paper:#24211d;--ink:#ece6dd;--muted:#a59a8d;--line:#3a352f;--accent:#e08a74;--soft:#3c2a24}}
:root[data-theme="dark"]{--bg:#1b1916;--paper:#24211d;--ink:#ece6dd;--muted:#a59a8d;--line:#3a352f;--accent:#e08a74;--soft:#3c2a24}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:"Noto Serif TC","PMingLiU",serif;line-height:1.8}
header{position:sticky;top:0;background:var(--paper);border-bottom:1px solid var(--line);z-index:5}
.wrap{max-width:1000px;margin:0 auto;padding:0 16px}
.top{display:flex;flex-wrap:wrap;align-items:center;gap:10px;padding:10px 0}
.top b{font-size:1.15rem;letter-spacing:.1em;margin-right:auto}
.top button{font:inherit;font-size:.9rem;border:1px solid var(--line);background:var(--bg);color:var(--ink);border-radius:999px;padding:4px 14px;cursor:pointer}
.top button.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.top a{color:var(--accent);font-size:.9rem}
article{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:22px 26px;margin:20px 0 60px;overflow-wrap:anywhere}
article h1{font-size:1.6rem}article h2{border-left:5px solid var(--accent);padding-left:10px;margin-top:2em}
article table{border-collapse:collapse;width:100%;font-size:.9rem;display:block;overflow-x:auto}
article th,article td{border:1px solid var(--line);padding:6px 8px;vertical-align:top}article th{background:var(--soft)}
article blockquote{margin:1em 0;padding:8px 14px;border-left:4px solid var(--line);color:var(--muted)}
article a{color:var(--accent)}article code{background:var(--bg);padding:0 4px;border-radius:4px}
@media (max-width:640px){article{padding:16px}}
</style></head><body>
<header><div class="wrap top"><b>字裡山河・教師研究</b>''' + tabs + '''<a href="index.html">← 回字裡山河</a></div></header>
<main class="wrap"><article id="doc"></article></main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<script>
const DOCS = ''' + json.dumps(data, ensure_ascii=False) + ''';
function show(k){
  document.querySelectorAll('.top button').forEach(b => b.classList.toggle('on', b.dataset.doc === k));
  const el = document.getElementById('doc');
  el.innerHTML = window.marked ? marked.parse(DOCS[k]) : '<pre style="white-space:pre-wrap">' + DOCS[k].replace(/[&<]/g, c => c === '&' ? '&amp;' : '&lt;') + '</pre>';
  window.scrollTo(0, 0);
}
document.querySelector('.top').addEventListener('click', e => { if (e.target.dataset.doc) show(e.target.dataset.doc); });
show('research2');
</script></body></html>'''
open('site/teacher.html', 'w', encoding='utf-8').write(html)
print('teacher.html', len(html))

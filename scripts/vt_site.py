"""技職版頁面：以國中版 site/index.html 為範本，產生統測版 tc/site/index.html 與二技版 et/site/index.html。
python -I scripts/vt_site.py"""
import os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
src = open(os.path.join(ROOT, 'site', 'index.html'), encoding='utf-8').read()
V = {
 'tc': dict(
  sub='技高文言閱讀・統測歷屆試題練習', kind='統測', store='wywtc',
  motto='一字一句，都是練得成的功夫。',
  p1='匠人把心思做進器物，古人把心事寫進文字。看懂一件好作品要眼力，讀懂一段古文也一樣，多看、多想，就會越來越準。',
  p2='這裡整理統測歷屆文言試題，搭配白話翻譯、逐項解析與判讀方法，陪你從字詞找到線索，一題一題練出讀懂古文的手感。',
  levels=[("初讀・從一句開始", "★", "從簡短單題讀起，認識字詞，找出句子裡的線索。", "{form:'單題', diff:'易'}"),
          ("入文・讀懂一篇", "★★", "讀一整段文章，連起前後文，回答兩三題。", "{form:'題組'}"),
          ("探意・多想一層", "★★★", "練習較有挑戰的題目，讀出言外之意，讓判斷更有依據。", "{diff:'難'}")],
  source='歷屆四技二專統一入學測驗國文科（技專校院入學測驗中心公布試題）', other=('../../et/site/index.html', '二技版 →')),
 'et': dict(
  sub='二技文言閱讀・歷屆試題練習', kind='二技', store='wywet',
  motto='再讀一次古文，讀出不一樣的深度。',
  p1='一樣的文章，多了一些閱歷再讀，常會看見以前沒注意到的地方。古人的取捨與思考，正適合一邊工作、一邊求學的你細細品味。',
  p2='這裡整理二技統一入學測驗歷屆文言試題，搭配白話翻譯、逐項解析與判讀方法，陪你把零碎的時間，變成穩穩累積的實力。',
  levels=[("初讀・從一句開始", "★", "從簡短單題讀起，重新找回讀文言文的手感。", "{form:'單題', diff:'易'}"),
          ("入文・讀懂一篇", "★★", "讀一整段文章，連起前後文，回答兩三題。", "{form:'題組'}"),
          ("探意・多想一層", "★★★", "練習較有挑戰的題目，讀出言外之意，讓判斷更有依據。", "{diff:'難'}")],
  source='歷屆二技統一入學測驗國文科（技專校院入學測驗中心公布試題）', other=('../../tc/site/index.html', '統測版 →')),
}
def rep(s, a, b):
    assert a in s, a[:40]
    return s.replace(a, b)
for k, v in V.items():
    s = src
    s = rep(s, '國中文言閱讀・基測會考練習', v['sub'])
    s = rep(s, '從一句讀起，與古人的故事相逢。', v['motto'])
    s = rep(s, '<p>古人也會猶豫、歡喜，也曾為一件小事想上很久。那些心情與智慧，就藏在短短的字句裡，等你慢慢讀懂。</p>', f"<p>{v['p1']}</p>")
    s = rep(s, '<p>這裡整理歷屆基測、會考文言試題，搭配白話翻譯、題目解析與閱讀方法，陪你從字詞找到線索，讀懂故事，也讀出自己的想法。</p>', f"<p>{v['p2']}</p>")
    a = s.index('const LEVELS = ['); b = s.index('];', a)
    s = s[:a] + 'const LEVELS = [\n' + ',\n'.join(f"  {{name:'{n}', star:'{st}', desc:'{d}', preset:{p}}}" for n, st, d, p in v['levels']) + '\n' + s[b:]
    s = rep(s, '<select data-f="kind"><option value="">基測＋會考</option><option>基測</option><option>會考</option></select>', f'<select data-f="kind" hidden><option value="">{v["kind"]}</option></select>')
    s = rep(s, "localStorage.getItem('wyw:'", f"localStorage.getItem('{v['store']}:'")
    s = rep(s, "localStorage.setItem('wyw:'", f"localStorage.setItem('{v['store']}:'")
    a = s.index('<footer class="wrap">'); b = s.index('</footer>', a)
    s = s[:a] + f'<footer class="wrap">題目來源：{v["source"]}　｜　僅供課堂練習使用　｜　<a href="{v["other"][0]}" style="color:inherit">{v["other"][1]}</a></footer>' + s[b + 9:]
    os.makedirs(os.path.join(ROOT, k, 'site'), exist_ok=True)
    open(os.path.join(ROOT, k, 'site', 'index.html'), 'w', encoding='utf-8').write(s)
    print(k, 'ok')

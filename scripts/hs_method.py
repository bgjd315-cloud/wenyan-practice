"""高中版解題方法頁：method_src.html ＋ core15.json（各篇課文相關題目）→ method.html"""
import json, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hs', 'raw'))
src = open('method_src.html', encoding='utf-8').read()
core = json.load(open('core15.json', encoding='utf-8'))
cells = ''.join(f'<a href="#" class="corebtn" data-open-set="{",".join(ids)}">〈{name}〉<span>{len(ids)} 組</span></a>'
                for name, ids in core.items() if ids)
open('method.html', 'w', encoding='utf-8').write(src.replace('<!--CORE15-->', f'<div class="corelist">{cells}</div>'))
print('core links:', len(core))

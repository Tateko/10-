import base64,sys
from playwright.sync_api import sync_playwright
from pathlib import Path
font=Path.home()/".local/share/fonts/NotoSansJP-VariableFont_wght.ttf"
uri="data:image/jpeg;base64,"+base64.b64encode(open("img/29.jpg","rb").read()).decode()
RED="#E35B36"
html=f"""<html><head><style>@font-face{{font-family:NJP;src:url("file://{font}");font-weight:100 900}}
body{{margin:0;width:1280px;height:720px;position:relative;overflow:hidden;font-family:NJP,sans-serif}}
.a{{position:absolute}} .s{{-webkit-text-stroke:10px #000;paint-order:stroke fill;font-weight:900;line-height:1.05;letter-spacing:-2px}}</style></head><body>
<div class=a style="inset:0;background:url('{uri}') 70% center/cover"></div>
<div class=a style="inset:0;background:linear-gradient(90deg,rgba(5,14,20,.92) 0%,rgba(5,14,20,.75) 40%,rgba(5,14,20,0) 70%)"></div>
<div class=a style="left:48px;top:44px;background:{RED};color:#fff;font-size:34px;font-weight:900;padding:4px 20px 10px;border-radius:6px">コード経験ゼロの学生</div>
<div class="a s" style="left:44px;top:150px;font-size:96px;color:#fff">8か月で</div>
<div class="a s" style="left:36px;top:262px;font-size:210px;color:{RED}">70万<span style="font-size:120px">ドル</span></div>
<div class="a s" style="left:50px;top:500px;font-size:64px;color:#fff">約1.1億円</div>
<div class=a style="right:20px;top:20px;font-size:20px;font-weight:700;color:#eee;background:rgba(0,0,0,.5);padding:2px 10px 4px;border-radius:5px">イメージ</div>
</body></html>"""
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={"width":1280,"height":720});pg.set_content(html);pg.evaluate("document.fonts.ready");pg.wait_for_timeout(600);pg.screenshot(path="thumbnail.png");b.close()

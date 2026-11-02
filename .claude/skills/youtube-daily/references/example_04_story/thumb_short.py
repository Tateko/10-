import base64
from pathlib import Path
from playwright.sync_api import sync_playwright
font = Path.home() / ".local/share/fonts/NotoSansJP-VariableFont_wght.ttf"
uri = "data:image/jpeg;base64," + base64.b64encode(open("img/21.jpg", "rb").read()).decode()
RED = "#E35B36"
html = f"""<html><head><style>@font-face{{font-family:NJP;src:url("file://{font}");font-weight:100 900}}
body{{margin:0;width:1080px;height:1920px;position:relative;overflow:hidden;font-family:NJP,sans-serif;background:#0D1C26}}
.a{{position:absolute}} .c{{left:0;right:0;text-align:center}}
.s{{-webkit-text-stroke:12px #000;paint-order:stroke fill;font-weight:900;line-height:1.1;letter-spacing:-2px}}</style></head><body>
<img class=a src="{uri}" style="left:-1250px;top:0;height:1920px;width:3413px;object-fit:cover">
<div class=a style="inset:0;background:linear-gradient(180deg,rgba(5,14,20,0) 0%,rgba(5,14,20,.35) 30%,rgba(5,14,20,.8) 55%,rgba(5,14,20,.95) 100%)"></div>
<div class="a c" style="top:470px"><span style="background:{RED};color:#fff;font-size:52px;font-weight:900;padding:8px 30px 16px;border-radius:10px">コード経験ゼロの学生</span></div>
<div class="a c s" style="top:640px;font-size:120px;color:#fff">売上20万ドル</div>
<div class="a c s" style="top:790px;font-size:120px;color:#fff">の裏で</div>
<div class="a c s" style="top:1000px;font-size:150px;color:{RED}">集客の柱が</div>
<div class="a c s" style="top:1175px;font-size:150px;color:{RED}">壊れた</div>
<div class="a c" style="top:1420px;font-size:44px;font-weight:800;color:#e6e6e6">8か月で70万ドルまでの記録</div>
<div class=a style="right:30px;top:40px;font-size:26px;font-weight:700;color:#eee;background:rgba(0,0,0,.5);padding:3px 12px 6px;border-radius:6px">イメージ</div>
</body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920}); pg.set_content(html)
    pg.evaluate("document.fonts.ready"); pg.evaluate("Promise.all(Array.from(document.images).map(i => i.decode()))"); pg.wait_for_timeout(400)
    pg.screenshot(path="short_thumbnail.png"); b.close()
from PIL import Image
Image.open("short_thumbnail.png").resize((270, 480)).save("short_thumbnail_small.png")

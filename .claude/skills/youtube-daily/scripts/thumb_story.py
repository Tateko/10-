# 絵と図解の型のサムネ（横 1280×720 と、ショート用の縦 1080×1920）。絵を背景に、札・1行・大きい数字・下の1行。
#
#   python thumb_story.py <絵.jpg> <出力.png> --tag "使う人は、刑務所の中" --line "聞いたことのないアプリで" \
#          --big "150万" --unit "ドル" --sub "約2.3億円・広告なし" [--pos 60%] [--vertical]
import argparse
import base64
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("img"); ap.add_argument("out")
ap.add_argument("--tag", default=""); ap.add_argument("--line", default="")
ap.add_argument("--big", required=True); ap.add_argument("--unit", default="")
ap.add_argument("--sub", default=""); ap.add_argument("--pos", default="70%")
ap.add_argument("--vertical", action="store_true")
a = ap.parse_args()

font = Path.home() / ".local/share/fonts/NotoSansJP-VariableFont_wght.ttf"
uri = "data:image/jpeg;base64," + base64.b64encode(open(a.img, "rb").read()).decode()
RED = "#E35B36"
W, H = (1080, 1920) if a.vertical else (1280, 720)


def fit(text, width, mx):
    # 数字は約0.6字幅、ほかは1字幅として、幅に収まる大きさにする
    em = sum(0.6 if c in "0123456789,.%" else 1.0 for c in text) or 1
    return int(min(mx, width / em))


if a.vertical:
    shade = "linear-gradient(180deg,rgba(5,14,20,0) 0%,rgba(5,14,20,.4) 30%,rgba(5,14,20,.85) 55%,rgba(5,14,20,.95) 100%)"
    ls, bs = fit(a.line, 960, 110), fit(a.big + a.unit, 980, 230)
    body = (f"<div class='a c' style='top:470px'><span class='tag'>{a.tag}</span></div>"
            f"<div class='a c s' style='top:620px;font-size:{ls}px;color:#fff'>{a.line}</div>"
            f"<div class='a c s' style='top:{640 + ls + 40}px;font-size:{bs}px;color:{RED}'>{a.big}<span style='font-size:{int(bs * .55)}px'>{a.unit}</span></div>"
            f"<div class='a c' style='top:{700 + ls + bs + 60}px;font-size:48px;font-weight:800;color:#eee'>{a.sub}</div>")
else:
    shade = "linear-gradient(90deg,rgba(5,14,20,.92) 0%,rgba(5,14,20,.75) 42%,rgba(5,14,20,0) 72%)"
    ls, bs = fit(a.line, 860, 96), fit(a.big + a.unit, 820, 210)
    body = (f"<div class='a' style='left:48px;top:44px'><span class='tag'>{a.tag}</span></div>"
            f"<div class='a s' style='left:44px;top:150px;font-size:{ls}px;color:#fff'>{a.line}</div>"
            f"<div class='a s' style='left:36px;top:{170 + ls}px;font-size:{bs}px;color:{RED}'>{a.big}<span style='font-size:{int(bs * .55)}px'>{a.unit}</span></div>"
            f"<div class='a s' style='left:50px;top:{200 + ls + bs}px;font-size:60px;color:#fff'>{a.sub}</div>")
html = f"""<html><head><style>@font-face{{font-family:NJP;src:url("file://{font}");font-weight:100 900}}
body{{margin:0;width:{W}px;height:{H}px;position:relative;overflow:hidden;font-family:NJP,sans-serif;background:#0D1C26}}
.a{{position:absolute}} .c{{left:0;right:0;text-align:center}}
.s{{-webkit-text-stroke:10px #000;paint-order:stroke fill;font-weight:900;line-height:1.05;letter-spacing:-2px}}
.tag{{background:{RED};color:#fff;font-size:{52 if a.vertical else 34}px;font-weight:900;padding:4px 22px 10px;border-radius:8px}}</style></head><body>
<img class=a src="{uri}" style="left:0;top:0;width:{W}px;height:{H}px;object-fit:cover;object-position:{a.pos} center">
<div class=a style="inset:0;background:{shade}"></div>{body}
<div class=a style="right:20px;top:20px;font-size:20px;font-weight:700;color:#eee;background:rgba(0,0,0,.5);padding:2px 10px 4px;border-radius:5px">イメージ</div>
</body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H}); pg.set_content(html)
    pg.evaluate("document.fonts.ready"); pg.evaluate("Promise.all(Array.from(document.images).map(i => i.decode()))")
    pg.wait_for_timeout(300); pg.screenshot(path=a.out); b.close()
Image.open(a.out).resize((W // 5, H // 5)).save(a.out.replace(".png", "_small.png"))
print("✔", a.out)

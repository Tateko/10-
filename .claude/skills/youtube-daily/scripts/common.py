# 図・動くイラスト・サムネで共通の見た目（チャンネルの型：黒地＋方眼・黄緑と赤・白い文字）と、HTML を画像・動画にする道具。
import shutil
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

G, R, GR, INK, MID = "#A8E04A", "#E0322E", "#5A5F5A", "#070906", "#2a3026"
FONT = Path.home() / ".local/share/fonts/NotoSansJP-VariableFont_wght.ttf"
FF = str(Path.home() / ".autoedit-venv/bin/ffmpeg")


def base_css(w, h, grid=48):
    return f"""
@font-face {{ font-family: NJP; src: url("file://{FONT}"); font-weight: 100 900; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; width:{w}px; height:{h}px; overflow:hidden; position:relative; font-family:NJP, sans-serif; color:#fff;
  background-color:#141810;
  background-image: radial-gradient(ellipse at 50% 45%, rgba(168,224,74,.10), rgba(0,0,0,0) 60%),
    linear-gradient(rgba(255,255,255,.045) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.045) 1px, transparent 1px);
  background-size:100% 100%, {grid}px {grid}px, {grid}px {grid}px; }}
.a {{ position:absolute; }}
.c {{ position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:30px; }}
.h {{ font-size:50px; font-weight:800; }}
.sub {{ font-size:30px; color:#9aa09a; font-weight:600; }}
.lbl {{ font-weight:800; }}
.tag {{ position:absolute; right:40px; top:120px; font-size:28px; color:#9aa09a; font-weight:700; }}
.stk {{ -webkit-text-stroke:12px #000; paint-order:stroke fill; font-weight:900; letter-spacing:-3px; line-height:1; }}
.stamp {{ border:7px solid {R}; color:{R}; font-weight:900; border-radius:12px; background:rgba(15,18,12,.9); }}
@keyframes up {{ from {{ transform:translateY(60px); opacity:0 }} to {{ transform:none; opacity:1 }} }}
@keyframes pop {{ 0% {{ transform:scale(.3); opacity:0 }} 70% {{ transform:scale(1.1); opacity:1 }} 100% {{ transform:scale(1) }} }}
@keyframes fade {{ from {{ opacity:0 }} to {{ opacity:1 }} }}
"""


def person(x, y, s=1.0, extra=""):
    """顔のない影絵の人。"""
    return (f"<svg class='a' style='left:{x}px;top:{y}px;{extra}' width='{int(160*s)}' height='{int(360*s)}' viewBox='0 0 160 360'>"
            f"<circle cx='80' cy='40' r='36' fill='{INK}'/><rect x='44' y='86' width='72' height='150' rx='30' fill='{INK}'/>"
            f"<rect x='52' y='226' width='24' height='120' rx='10' fill='{INK}' class='legA'/>"
            f"<rect x='86' y='226' width='24' height='120' rx='10' fill='{INK}' class='legB'/></svg>")


def shoot(pages, w, h):
    """pages: [(出力パス, HTML)] を静止画にする。"""
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": w, "height": h})
        for out, html in pages:
            pg.goto("about:blank")
            pg.set_content(html)
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(600)
            pg.screenshot(path=str(out))
        b.close()


def record(clips, fps=30):
    """clips: [(出力 mp4, 秒, HTML)]。CSS アニメを止めて1コマずつ時刻を進めて撮る。
    数字を数える所は window.__tick = (ms) => {...} を HTML に書く。"""
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        for out, sec, html in clips:
            out = Path(out)
            tmp = out.parent / f"_frames_{out.stem}"
            shutil.rmtree(tmp, ignore_errors=True)
            tmp.mkdir(parents=True)
            pg.goto("about:blank")  # 前のクリップの __tick を残さない
            pg.set_content(f"<html><head></head><body>{html}</body></html>")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(400)
            pg.evaluate("document.getAnimations().forEach(a => a.pause())")
            for i in range(int(sec * fps)):
                ms = i * 1000 / fps
                pg.evaluate("(ms) => { document.getAnimations().forEach(a => a.currentTime = ms); if (window.__tick) window.__tick(ms); }", ms)
                pg.screenshot(path=str(tmp / f"{i:05d}.jpg"), type="jpeg", quality=90)
            subprocess.run([FF, "-v", "error", "-y", "-framerate", str(fps), "-i", str(tmp / "%05d.jpg"),
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(out)], check=True)
            shutil.rmtree(tmp)
            print("✔", out.name, f"{sec}秒")
        b.close()

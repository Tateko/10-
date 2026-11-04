# 本編の一部から縦のショート（1080×1920）を作る。上に見出し2行、下に「続きは本編で」。
import glob, subprocess, sys, wave
from pathlib import Path
from playwright.sync_api import sync_playwright
S = Path(sys.argv[1]); a, b = int(sys.argv[2]), int(sys.argv[3])   # 文の番号（0から・bは含まない）
# 4つ目は下の一言。有名企業の回は「数字は会社の発表と報道の記録のまま」にする
NOTE = sys.argv[4] if len(sys.argv) > 4 else "数字は本人が公開した記録のまま"
FF = str(Path.home() / ".autoedit-venv/bin/ffmpeg")
d = [wave.open(f).getnframes() / wave.open(f).getframerate() for f in sorted(glob.glob(str(S / "out/wav/*.wav")))]
t0, t1 = sum(d[:a]), sum(d[:b])
font = Path.home() / ".local/share/fonts/NotoSansJP-VariableFont_wght.ttf"
NAVY, RED, CREAM = "#0D1C26", "#E35B36", "#F6F2EB"
vh, vy = 608, 640
html = f"""<html><head><style>@font-face{{font-family:NJP;src:url("file://{font}");font-weight:100 900}}
body{{margin:0;width:1080px;height:1920px;background:{NAVY};font-family:NJP,sans-serif;position:relative}}
.a{{position:absolute;left:0;right:0;text-align:center}}</style></head><body>
<div class=a style="top:250px;font-size:34px;font-weight:800;color:#9fb0bb">海外の挑戦を、日付と数字で</div>
<div class=a style="top:330px;font-size:96px;font-weight:900;color:#fff;line-height:1.2">売上20万ドルの裏で</div>
<div class=a style="top:450px;font-size:96px;font-weight:900;color:{RED};line-height:1.2">集客の柱が壊れた</div>
<div class=a style="top:{vy+vh+90}px"><span style="background:{RED};color:#fff;font-size:62px;font-weight:900;padding:12px 46px 20px;border-radius:14px">続きは本編で ▶</span></div>
<div class=a style="top:{vy+vh+250}px;font-size:34px;font-weight:700;color:#cfd6da">{NOTE}</div></body></html>"""
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(html); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(500); pg.screenshot(path=str(S / "short_bg.png")); br.close()
dur = t1 - t0
subprocess.run([FF, "-v", "error", "-y", "-loop", "1", "-i", str(S / "short_bg.png"), "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", str(S / "out/final.mp4"),
                "-filter_complex", f"[1:v]scale=1080:{vh}[v];[0:v][v]overlay=0:{vy}:shortest=1,fade=t=out:st={dur-0.6:.2f}:d=0.6,format=yuv420p[o];[1:a]afade=t=out:st={dur-0.6:.2f}:d=0.6[x]",
                "-map", "[o]", "-map", "[x]", "-r", "30", "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.3f}", str(S / "short.mp4")], check=True)
subprocess.run([FF, "-v", "error", "-y", "-ss", f"{dur/2:.2f}", "-i", str(S / "short.mp4"), "-frames:v", "1", "-vf", "scale=540:-1", str(S / "short_check.jpg")], check=True)
print(f"✔ short.mp4 {dur:.1f}秒")

# 本編のいちばん強い場面を、縦のショート（1080×1920・30〜60秒）にする。上に見出し2行、下に本編への案内。
#
#   python make_short.py <動画のフォルダ>      → out/short.mp4 と、確かめ用の out/short_check.jpg
#
# short.json の形：
# {"from": "S038", "to": "S043", "top": ["88人が使っても", "売上は0ドル"], "bottom": "続きは本編で",
#  "color": "orange"}
#   from・to は plan.json のシーン番号（out の書き出しの時間は work/timeline.json から読む）。
#   top は2行まで（台本にある言葉だけ）。color はサムネと同じ色の名前。zoom を 1.1〜1.2 にすると横を切って大きく見せる（端の章名・日付が切れるので、ふだんは 1.0）。
import json
import subprocess
import sys
from pathlib import Path

from common import FF, base_css, shoot
from palette import PAL

proj = Path(sys.argv[1])
out = proj / "out"
sj = json.load(open(proj / "short.json", encoding="utf-8"))
tl = {s["id"]: s for s in json.load(open(proj / "work" / "timeline.json", encoding="utf-8"))["scenes"]}
t0, t1 = tl[sj["from"]]["start"], tl[sj["to"]]["end"] + 0.3
dur = t1 - t0
bg, ac = PAL.get(sj.get("color", "green"), PAL["green"])
zoom = float(sj.get("zoom", 1.0))
vw = int(1080 * zoom) // 2 * 2
vh = int(vw * 9 / 16) // 2 * 2
vy = 1920 // 2 - vh // 2 + 40

top = "".join(f"<div class='stk' style='font-size:{min(120, int(980 / max(1, len(l))))}px;color:{'#fff' if i == 0 else ac}'>{l}</div>"
              for i, l in enumerate(sj["top"][:2]))
html = (f"<html><head><style>{base_css(1080, 1920, 40)} body{{background-color:{bg}}}</style></head><body>"
        f"<div class='a' style='left:0;right:0;top:{vy - 520}px;height:470px;display:flex;flex-direction:column;"
        f"align-items:center;justify-content:center;gap:24px;text-align:center'>{top}</div>"
        f"<div class='a' style='left:0;right:0;top:{vy + vh + 60}px;display:flex;justify-content:center'>"
        f"<div style='font-size:64px;font-weight:900;color:#0a0a0a;background:{ac};padding:10px 44px 18px;border-radius:60px'>"
        f"{sj.get('bottom', '続きは本編で')} ▶</div></div>"
        f"<div class='a' style='left:0;right:0;top:{vy + vh + 210}px;text-align:center;font-size:36px;font-weight:700;color:#c8ccc8'>"
        f"{sj.get('note', '数字は本人が公開した記録のまま')}</div></body></html>")
frame = out / "_short_bg.png"
shoot([(frame, html)], 1080, 1920)

dst = out / "short.mp4"
fade = max(0, dur - 0.6)
subprocess.run([FF, "-v", "error", "-y", "-loop", "1", "-i", str(frame), "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", str(out / "final.mp4"),
                "-filter_complex",
                f"[1:v]scale={vw}:{vh},crop=1080:{vh}[v];[0:v][v]overlay=0:{vy}:shortest=1,fade=t=out:st={fade:.2f}:d=0.6,format=yuv420p[o];"
                f"[1:a]afade=t=out:st={fade:.2f}:d=0.6[a]",
                "-map", "[o]", "-map", "[a]", "-r", "30", "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-b:a", "192k",
                "-t", f"{dur:.3f}", str(dst)], check=True)
frame.unlink()
subprocess.run([FF, "-v", "error", "-y", "-ss", f"{dur / 2:.2f}", "-i", str(dst), "-frames:v", "1", "-vf", "scale=540:-1",
                str(out / "short_check.jpg")], check=True)
warn = "" if 30 <= dur <= 60 else f"　⚠ {dur:.0f}秒。30〜60秒になるように from・to を変える"
print(f"✔ out/short.mp4（{dur:.1f}秒）・確かめ用 out/short_check.jpg{warn}")

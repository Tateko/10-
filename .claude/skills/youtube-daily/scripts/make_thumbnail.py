# サムネ（1280×720）を thumbnail.json の指示から作る。ふだんは hero 型（文字2行・大きい数字1つ・感情の伝わる人の影絵・回ごとの色）。
#
#   python make_thumbnail.py <動画のフォルダ>        → out/thumbnail.png と、スマホ大の見本 out/thumbnail_small.png
#
# 型 hero（標準）：{"type":"hero","color":"orange","line":"7年かけて、初めての売上","big":"190","unit":"ドル",
#                    "yen":"約2.9万円","big_color":"accent","pose":"down","label":"イメージ"}
#   文字は line（1行）と big＋unit（1行）の2行だけ。yen は数字の横に小さく（1ドル＝150円などの換算。円にしない回は省く）。
#   color：green・orange・blue・red・purple・teal（前の回と変える）。big_color：accent・red・white。
#   pose：down（頭をかかえる）・up（両手を上げる）・think（あごに手）・walk（去っていく）・stand。
# 型 drop_to_result：{"type":"drop_to_result","stamp":"年収を捨てた会社員","low_label":"6か月目「怖かった」","low":"5,989",
#                     "high_label":"10か月目","high":"40,451","note":"月の売上・本人の記録","bars":[67715,...],"red":[5]}
# 型 event_result  ：{"type":"event_result","stamp":"貯金を使い切って、会社に出戻り","line":"2年後、1か月の売上",
#                     "big":"1,680","unit":"万円","note":"2025年1月・本人談（11万2千ドル・1ドル150円）"}
# 文字は台本にある言葉だけ。数字は丸めない。右下（再生時間が出る所）に大事な物を置かない。
import json
import sys
from pathlib import Path

from PIL import Image

from common import G, R, base_css, shoot

proj = Path(sys.argv[1])
t = json.load(open(proj / "thumbnail.json", encoding="utf-8"))
css = base_css(1280, 720, 32)

from palette import PAL

# 顔のない影絵（線で描く）。600×700 の枠の中。（頭の位置, 胴, 手足）
POSE = {
    "stand": ((300, 175), "M300 240 L300 420", "M300 260 L250 330 L240 420 M300 260 L350 330 L360 420 M300 420 L265 610 M300 420 L335 610"),
    "down":  ((330, 300), "M300 345 Q270 420 290 500", "M300 360 L400 420 M290 500 L410 410 L430 540 M290 500 L380 450 L370 545"),
    "up":    ((300, 185), "M300 250 L300 430", "M300 265 L215 160 L200 70 M300 265 L385 160 L400 70 M300 430 L250 615 M300 430 L350 615"),
    "think": ((300, 175), "M300 240 L300 420", "M300 260 L380 330 L340 225 M300 260 L245 345 L320 360 M300 420 L265 610 M300 420 L335 610"),
    "walk":  ((318, 190), "M305 255 L295 430", "M305 270 L250 350 L235 410 M305 270 L360 345 L380 400 M295 430 L225 600 M295 430 L360 520 L345 610"),
}

if t["type"] == "hero":
    bg, ac = PAL.get(t.get("color", "green"), PAL["green"])
    bc = {"accent": ac, "red": R, "white": "#fff"}[t.get("big_color", "accent")]
    pose = t.get("pose", "stand")
    (hx, hy), torso, limbs = POSE[pose]
    ground = "<rect x='120' y='540' width='380' height='14' rx='7' fill='#0a0a0a' opacity='.5'/>" if pose == "down" else ""
    figure = (f"<svg class='a' style='left:740px;top:40px' width='600' height='700' viewBox='0 0 600 700'>"
              f"<circle cx='300' cy='340' r='290' fill='{ac}' opacity='.92'/>{ground}"
              f"<circle cx='{hx}' cy='{hy}' r='52' fill='#0a0a0a'/>"
              f"<path d='{torso}' stroke='#0a0a0a' stroke-width='92' stroke-linecap='round' fill='none'/>"
              f"<path d='{limbs}' stroke='#0a0a0a' stroke-width='44' stroke-linecap='round' stroke-linejoin='round' fill='none'/></svg>"
              f"<div class='a' style='left:1100px;top:24px;font-size:22px;font-weight:700;color:#e6e6e6;background:rgba(0,0,0,.6);"
              f"padding:2px 12px 4px;border-radius:6px'>{t.get('label', 'イメージ')}</div>")
    # 数字は左の約800pxに収まる大きさにする
    bl = len(t["big"]) + len(t.get("unit", "")) * 0.62
    bs = max(150, min(340, int(780 / max(1, bl) * 1.6)))
    ls = max(60, min(96, int(800 / max(1, len(t["line"])))))
    yen = (f"<div style='font-size:52px;letter-spacing:0;margin-top:8px;color:#fff'>{t['yen']}</div>" if t.get("yen") else "")
    body = (f"<style>body{{background-color:{bg};background-image:radial-gradient(ellipse at 80% 50%, {ac}33, rgba(0,0,0,0) 55%)}}</style>"
            f"{figure}"
            f"<div class='a stk' style='left:56px;top:110px;font-size:{ls}px;width:820px'>{t['line']}</div>"
            f"<div class='a stk' style='left:44px;top:{120 + ls + 30}px;font-size:{bs}px;color:{bc}'>{t['big']}"
            f"<span style='font-size:{int(bs * .45)}px;margin-left:10px'>{t.get('unit', '')}</span>{yen}</div>")
elif t["type"] == "drop_to_result":
    vals = t.get("bars", [])
    mx = max(vals) if vals else 1
    bars = ''.join(f"<div class='a' style='left:{850+i*(380//max(1,len(vals)))}px;bottom:110px;width:{int(380//max(1,len(vals))*.75)}px;height:{max(8,int(330*v/mx))}px;"
                   f"border-radius:5px;background:{R if i in t.get('red', []) else G};opacity:{1 if i in t.get('red', []) or i == len(vals)-1 else .45}'></div>" for i, v in enumerate(vals))
    # 結果の数字は、ラベルのすぐ右から画面の右端までに収まる大きさにする
    hl = 60 + len(t["high_label"]) * 68 + 30
    hs = max(110, min(200, int((1240 - hl) / max(1, len(t["high"])) * 1.05)))
    body = (f"<div class='a stamp' style='left:46px;top:40px;font-size:52px;padding:4px 26px 12px;transform:rotate(-4deg)'>{t['stamp']}</div>"
            f"<div class='a stk' style='left:60px;top:170px;font-size:70px;color:#cfd3cf'>{t['low_label']}</div>"
            f"<div class='a stk' style='left:56px;top:250px;font-size:170px;color:{R}'>{t['low']}"
            f"<span style='font-size:120px;color:{G};margin-left:40px;vertical-align:20px'>→</span></div>{bars}"
            f"<div class='a stk' style='left:60px;top:440px;font-size:70px'>{t['high_label']}</div>"
            f"<div class='a stk' style='left:{hl}px;top:{430 + (200 - hs) // 2}px;font-size:{hs}px;color:{G}'>{t['high']}</div>"
            f"<div class='a' style='left:60px;top:650px;font-size:30px;font-weight:800;background:#000;padding:4px 16px 8px;border-radius:8px'>{t['note']}</div>")
else:
    body = (f"<svg class='a' style='left:0;top:0' width='1280' height='720'><polyline points='40,660 420,650 560,640 700,560 860,420 1000,260 1240,60' fill='none' "
            f"stroke='{G}' stroke-width='16' stroke-linecap='round' stroke-linejoin='round' opacity='.45'/></svg>"
            f"<div class='a stamp' style='left:46px;top:40px;font-size:54px;padding:4px 26px 12px;transform:rotate(-4deg)'>{t['stamp']}</div>"
            f"<div class='a stk' style='left:60px;top:190px;font-size:90px'>{t['line']}</div>"
            f"<div class='a stk' style='left:44px;top:320px;font-size:230px;color:{G}'>{t['big']}<span style='font-size:130px'>{t.get('unit', '')}</span></div>"
            f"<div class='a' style='left:60px;top:600px;font-size:34px;font-weight:800;background:#000;padding:6px 18px 10px;border-radius:8px'>{t['note']}</div>")

out = proj / "out" / "thumbnail.png"
out.parent.mkdir(exist_ok=True)
shoot([(out, f"<html><head><style>{css}</style></head><body>{body}</body></html>")], 1280, 720)
Image.open(out).resize((246, 138)).save(proj / "out" / "thumbnail_small.png")
print("✔ out/thumbnail.png・スマホ大の見本 out/thumbnail_small.png（文字が読めるか目で確かめる）")

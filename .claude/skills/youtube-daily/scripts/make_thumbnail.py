# サムネ（1280×720）を thumbnail.json の指示から作る。「どん底 → 結果」か「出来事のハンコ ＋ 結果」の2つの型。
#
#   python make_thumbnail.py <動画のフォルダ>        → out/thumbnail.png と、スマホ大の見本 out/thumbnail_small.png
#
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

if t["type"] == "drop_to_result":
    vals = t.get("bars", [])
    mx = max(vals) if vals else 1
    bars = ''.join(f"<div class='a' style='left:{850+i*(380//max(1,len(vals)))}px;bottom:110px;width:{int(380//max(1,len(vals))*.75)}px;height:{max(8,int(330*v/mx))}px;"
                   f"border-radius:5px;background:{R if i in t.get('red', []) else G};opacity:{1 if i in t.get('red', []) or i == len(vals)-1 else .45}'></div>" for i, v in enumerate(vals))
    body = (f"<div class='a stamp' style='left:46px;top:40px;font-size:52px;padding:4px 26px 12px;transform:rotate(-4deg)'>{t['stamp']}</div>"
            f"<div class='a stk' style='left:60px;top:170px;font-size:70px;color:#cfd3cf'>{t['low_label']}</div>"
            f"<div class='a stk' style='left:56px;top:250px;font-size:170px;color:{R}'>{t['low']}"
            f"<span style='font-size:120px;color:{G};margin-left:40px;vertical-align:20px'>→</span></div>{bars}"
            f"<div class='a stk' style='left:60px;top:440px;font-size:70px'>{t['high_label']}</div>"
            f"<div class='a stk' style='left:360px;top:420px;font-size:200px;color:{G}'>{t['high']}</div>"
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

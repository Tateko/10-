# 書き出しのあとの仕上げ。
#   1. 音の最大を -1 dBFS より下に（キットのチェックで「割れるおそれ」が出ても直る）
#   2. 説明欄 out/youtube_説明欄.txt を description.json と、キットのチャプターから作る（冒頭の章・第◯章を付ける）
#   3. 確かめ用の画像：冒頭15秒のコマ（out/check_opening.jpg）と、動くクリップの途中のコマ（out/check_clips.jpg）
#
#   python finish.py <動画のフォルダ>
#
# description.json の形：
# {"intro": ["1行目", "2行目"], "question": "あなたなら…？コメントで教えてください。", "opening_chapter": "年収を捨てた、6か月後",
#  "notes": ["数字の多くは本人の発信です", ...], "sources": [["本人のブログ", "https://..."], ...], "checked": "2026/10/30",
#  "hashtags": "#AI #副業 #海外事例", "title": "88人が使って0ドル→毎月2万ドル（約300万円）｜…"}
#   title があれば、一覧で見える最初の20字に「単位つきの数字」があるかを確かめる
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

FF = str(Path.home() / ".autoedit-venv/bin/ffmpeg")
proj = Path(sys.argv[1])
out = proj / "out"
mp4 = out / "final.mp4"

# 1. 音
tmp = out / "_f2.mp4"
subprocess.run([FF, "-v", "error", "-y", "-i", str(mp4), "-c:v", "copy", "-af", "alimiter=limit=0.7:level=false",
                "-c:a", "aac", "-b:a", "192k", str(tmp)], check=True)
tmp.replace(mp4)
r = subprocess.run([FF, "-hide_banner", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]
peak = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1]
print(f"✔ 音：全体 {lufs} LUFS・最大 {peak} dBFS")

# 2. 説明欄
plan = json.load(open(proj / "plan.json", encoding="utf-8"))
tl = json.load(open(proj / "work" / "timeline.json", encoding="utf-8"))
start = {s["id"]: s["start"] for s in tl["scenes"]}
draft = open(out / "youtube_概要欄の下書き.txt", encoding="utf-8").read()
chs = [l for l in draft.splitlines() if re.match(r"\d+:\d\d ", l)]
first = next(s["id"] for s in plan["scenes"] if s.get("chapter"))
ft = start[first]
dj = proj / "description.json"
d = json.load(open(dj, encoding="utf-8")) if dj.exists() else {}
lines = list(d.get("intro", []))
if d.get("question"):
    lines += ["", d["question"]]
lines += ["", "■チャプター", f"0:00 {d.get('opening_chapter', 'はじめに')}"]
n = 1
for l in chs:
    tm, name = l.split(" ", 1)
    if tm == "0:00":
        tm = f"{int(ft // 60)}:{int(ft % 60):02d}"
    if name == "終わり":
        lines.append(f"{tm} 終わり")
    else:
        lines.append(f"{tm} 第{n}章 {name}")
        n += 1
if d.get("notes"):
    lines += ["", "■数字について"] + [f"・{x}" for x in d["notes"]]
if d.get("sources"):
    lines += ["", f"■主な出典（{d.get('checked', '')}確認）"] + [f"{a} {b}" for a, b in d["sources"]]
lines += ["", "※ナレーションと画面はAIの道具で作り、内容は人が確かめています。"]
if d.get("hashtags"):
    lines += ["", d["hashtags"]]
text = "\n".join(lines) + "\n"
(out / "youtube_説明欄.txt").write_text(text, encoding="utf-8")
fw = sum(2 if ord(c) > 255 else 1 for c in text)
print(f"✔ 説明欄：{len(text)}字（全角を2字と数えて {fw}）→ out/youtube_説明欄.txt" + ("" if fw < 4500 else "　⚠ 長い。出典を減らす"))

if d.get("title"):
    head = d["title"][:20]
    ok = re.search(r"[\d,.]+(?:万|千|億)?(?:ドル|円|ユーロ|豪ドル|ルピー|人|回|%|か月|年|日)", head)
    print(f"✔ タイトルの最初の20字：「{head}」" + ("" if ok else "　⚠ 単位つきの数字がない。強い数字と結末を前に出す"))

# 3. 確かめ用のコマ
def grab(times, path, cols=4):
    ims = []
    for i, t in enumerate(times):
        f = out / f"_g{i}.jpg"
        subprocess.run([FF, "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(mp4), "-frames:v", "1", "-vf", "scale=480:-1", str(f)], check=True)
        ims.append(Image.open(f))
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (480 * cols, 270 * rows))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * 480, (i // cols) * 270))
    sheet.save(path)
    for f in out.glob("_g*.jpg"):
        f.unlink()


grab([1, 4, 7, 10, 13, 16, 19, 22], out / "check_opening.jpg")
vids = [s for s in plan["scenes"] if s["layout"] == "video"]
if vids:
    ends = {s["id"]: s["end"] for s in tl["scenes"]}
    grab([start[s["id"]] + (ends[s["id"]] - start[s["id"]]) * .8 for s in vids], out / "check_clips.jpg")
print("✔ 確かめ用：out/check_opening.jpg（冒頭）・out/check_clips.jpg（動くクリップ）。開いて、絵が止まっていないか・文字が重なっていないかを見る")

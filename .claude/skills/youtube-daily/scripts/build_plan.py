# 台本.md の「N」の行（ナレーション）と scenes.json（シーンの割り当て）から、キットが読む plan.json を作る。
#
#   python build_plan.py <動画のフォルダ>
#
# scenes.json の形：
# {
#   "title": "動画のタイトル",
#   "sources": {"M10": "本人のブログ（2026/4/2）"},          # 出典の帯の略号（任意）
#   "chapters": ["", "01 章の名前", "02 章の名前", ...],      # 0番は冒頭（章なし）
#   "scenes": [[行数, 章番号, "layout", {visual}, "日付" または null, "略号か出典の文字" または null], ...]
# }
# 行数の合計が台本の N の行数と合わないと止まる。動くクリップは layout "video"（visual に file・fit・audio・start）。
import json
import re
import sys
from collections import Counter

proj = sys.argv[1]
spec = json.load(open(f"{proj}/scenes.json", encoding="utf-8"))
lines = []
for l in open(f"{proj}/台本.md", encoding="utf-8"):
    m = re.match(r"\| N \| (.*?) \|", l)
    if m:
        lines.append(re.sub(r"\[\d+\]", "", m.group(1)).strip())

EM = re.compile(r"[約]?[\d,.]+(?:万|千)?[\d,]*(?:千)?(?:K|ドル|円|回|人|位|%|か月|週|年|日)?")


def line(t):
    d = {}
    if "{" in t:
        d["text"] = re.sub(r"\{(.+?)\|.+?\}", r"\1", t)
        d["read"] = re.sub(r"\{.+?\|(.+?)\}", r"\1", t)
    else:
        d["text"] = t
    em = [w for w in EM.findall(d["text"]) if len(w) >= 2 and not re.fullmatch(r"\d{4}年", w)
          and not re.fullmatch(r"\d+[月日]", w)][:2]
    if em:
        d["em"] = em
    return d


S = spec["scenes"]
total = sum(s[0] for s in S)
if total != len(lines):
    sys.exit(f"✖ シーンの行数の合計 {total} と、台本の N の行数 {len(lines)} が合いません")
src_map, chapters = spec.get("sources", {}), spec["chapters"]
scenes, k = [], 0
for i, (n, ch, lay, vis, date, src) in enumerate(S, 1):
    sc = {"id": f"S{i:03d}"}
    if ch > 0 and lay != "end":
        sc["chapter"] = chapters[ch]
    sc["layout"] = lay
    if date:
        sc["date"] = date
    if src:
        sc["source"] = src_map.get(src, src)
    sc["visual"] = vis
    sc["lines"] = [line(t) for t in lines[k:k + n]]
    k += n
    scenes.append(sc)

plan = {
    "title": spec["title"],
    "theme": spec.get("theme", "black"),
    "colors": spec.get("colors", {"base": "#141810", "accent": "#A8E04A"}),
    "voice": spec.get("voice", {"engine": "say", "say_voice": "Kyoko", "say_rate": 290}),
    "motion": {"sfx": True},
    "scenes": scenes,
}
json.dump(plan, open(f"{proj}/plan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 見せ方のルールを確かめる
L = [s["layout"] for s in scenes]
warn = []
for i in range(len(L) - 2):
    if L[i] == L[i + 1] == L[i + 2] and L[i] != "video":
        warn.append(f"{scenes[i]['id']}〜：{L[i]} が3つ続く")
for i in range(len(L) - 1):
    if L[i] == L[i + 1] == "punch":
        warn.append(f"{scenes[i]['id']}：punch が2つ続く")
for t in lines:
    if len(re.sub(r"\{(.+?)\|.+?\}", r"\1", t)) > 40:
        warn.append(f"40字をこえる文：{t}")
print(f"✔ plan.json：{len(scenes)}シーン・{len(lines)}文・{dict(Counter(L))}")
for w in warn:
    print("⚠", w)

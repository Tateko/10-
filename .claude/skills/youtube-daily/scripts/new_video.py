# 動画1本ぶんのフォルダと、ひな形のファイルを作る。
#
#   python new_video.py <videos のフォルダ> <番号_名前>     例：python new_video.py ~/videos 03_AlexVanLe
import json
import sys
from pathlib import Path

d = Path(sys.argv[1]) / sys.argv[2]
for sub in ("images", "clips", "bgm", "out"):
    (d / sub).mkdir(parents=True, exist_ok=True)


def put(name, text):
    p = d / name
    if not p.exists():
        p.write_text(text, encoding="utf-8")


put("事実メモ.md", """# 事実メモ：（人の名前）

- 人：
- 主な発信の場所：
- 第三者の記事：
- 円の換算：（1ドル＝150円／通貨が分からなければ「しない」）
- 確認した日：

# 時系列
| 日付 | 出来事 | 数字 | 根拠 | 本人談か |
|---|---|---|---|---|

# 台本に入れないこと
-

# 素材リスト
## 記事の画面
| # | ページ | 下線を引く文（原文） | 訳（60字以内） |
|---|---|---|---|
## 自分で作る図・動くイラスト
| # | 何の図か | 使う数字 |
|---|---|---|

# 権利のメモ
- 他人の動画・写真：使わない／人は顔のない影絵

# 概要欄の出典
[1]
""")
put("台本.md", """# タイトル案
1.
2.
3.

# 基本
主人公：
挑戦：
換算の基準：
言いたいこと：

# 台本

## 00 （冒頭の名前）
date：
source：

| 種類 | 内容 | 型 |
|---|---|---|
| N | （いちばん驚く数字か一言）[1] | |
| N | （見どころの予告1） | |
| N | （見どころの予告2） | |
| N | （見どころの予告3） | |
| N | 最後に、（見る理由の約束）。 | |

## 01 （章の名前を読点で区切る）

| 種類 | 内容 | 型 |
|---|---|---|
| N | | |

# 出典
[1]

# 未確認・要確認リスト
-

# 文字数
ナレーション：
""")
for name, obj in (("scenes.json", {"title": "", "sources": {}, "chapters": [""], "scenes": []}),
                  ("visuals.json", {"items": []}),
                  ("thumbnail.json", {"type": "drop_to_result"}),
                  ("description.json", {"intro": [], "question": "", "opening_chapter": "", "notes": [], "sources": [], "checked": "", "hashtags": ""})):
    if not (d / name).exists():
        (d / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"✔ {d}")

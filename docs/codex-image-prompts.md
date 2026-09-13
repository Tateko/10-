# Codex CLI で画面モックを生成する

手元のPC（Codex CLI ログイン済み）で実行する。生成物は `docs/mocks/` に保存して push する。

> モデル名は指示どおり `AStra` を入れている。手元で `codex --help` / `codex exec --help` を見て、
> モデル指定フラグ（`-m` / `--model`）と画像出力の指定方法を確認してから回すこと。
> 画像生成に対応していない場合は、同じプロンプトを ChatGPT の画像生成や他のツールに貼っても使える。

## 共通スタイル（すべてのプロンプトの先頭に付ける）

```
Style guide for all images:
- iPhone-sized app screen mockup, 1170x2532, portrait, single screen, no device bezel, no hands.
- Calm, editorial, paper-like aesthetic: off-white background (#F3EFE8), deep forest green accent (#1F3D2B),
  ink-black text (#1D2B22), muted sand for secondary surfaces (#E6E0D4). No gradients, no neon, no glassmorphism.
- Typography: large serif headline for the greeting/date, clean sans-serif for body. Japanese UI text is fine.
- Generous whitespace. One dominant card per screen. Rounded corners (22px), thin 1.5px ink outlines instead of shadows.
- Bottom tab bar with 4 outlined square tabs: "!" (recommendations), house (home), person (friends), gear (settings).
- Do NOT show store names, brand logos, maps with real place names, or stock photos of people.
- Render the exact Japanese strings given below as UI text.
```

## 実行例

```bash
# 例: 1枚ずつ
codex exec -m AStra "$(cat docs/prompts/01-home.txt)" 
# 出力先の指定方法が別にあれば、それに従って docs/mocks/01-home.png に保存する
```

まとめて回すなら `for f in docs/prompts/*.txt; do codex exec -m AStra "$(cat "$f")"; done`。

---

## 01 ホーム（提案前）

```
App name: michi（未知）. A secretary that proposes, for today, the one experience you would never pick yourself.
Screen: HOME, before any proposal.
Top: small date "2036/9/12". Large serif greeting "Hello, たて!" and a one-line subtitle "今日、自分では選ばない一手を。"
Center: one big speech-bubble-shaped card (rounded 22px, bottom-left corner sharper) containing a minimal form:
  label "いまいるエリア" with a text field placeholder "渋谷",
  two dropdowns side by side "使える時間: 1時間" and "気分: 特になし",
  a full-width dark green button "今日の未知を提案する".
Bottom: the 4-tab bar (home tab filled dark green, others outlined).
Mood: quiet morning, an invitation rather than a dashboard.
```

## 02 ホーム（今日の1案）

```
App name: michi（未知）. Screen: HOME showing today's single proposal.
Top: date "2036/9/12", greeting "Hello, たて!".
Center: one big card. Small kicker "今日の未知 ・ 今日は『いつもの』を一つだけ外してみる日".
  Headline (24px, bold): "知らない駅で降りて昼を決める".
  Meta line: "60分 ・ 〜1,500円 ・ 乗り換えなしで行ける、降りたことのない駅".
  A highlighted block with a green left rule titled "なぜ自分では選ばないか:" and text
  "「休日はだいたい家で動画」と書いているので、店を事前に決めて動くタイプ。決めずに降りることは選ばない。"
  Three label/value rows: "やること", "誰を誘う 同期のA", "最初の一歩 乗換アプリを開かず、路線図を見て駅名を一つ選ぶ".
  Buttons: dark green "これにする", outlined "別の案", outlined "もう一度". Three pagination dots (first filled).
Bottom: 4-tab bar, home active, a small red dot on the "!" tab.
```

## 03 ロック画面（イベント完了までスマホが使えない）

```
App name: michi（未知）. Screen: LOCK MODE — after the user commits to today's proposal, the app takes over the whole screen
until the experience is completed. This is the signature screen; make it feel calm and final, not punitive.
Full-bleed deep forest green background (#1F3D2B) with off-white text.
Top small text: "進行中 ・ 2036/9/12".
Center: very large serif countdown "47:12" with caption "残り時間".
Below: the proposal title "知らない駅で降りて昼を決める" and one line "最初の一歩: 路線図を見て駅名を一つ選ぶ".
A single wide off-white button "完了を報告する" (with a small camera icon).
At the very bottom, tiny low-contrast text: "やめる（3秒長押し）".
No tab bar. No other UI. The phone is committed.
```

## 04 完了画面

```
App name: michi（未知）. Screen: COMPLETION — the experience is done and the lock is released.
Off-white background. Top: date "2036/9/12".
Large serif headline "おかえり。" and subline "未知を1つ、現実にした。"
A card with: the proposal title "知らない駅で降りて昼を決める", "所要 58分", "一緒に: 同期のA",
a photo placeholder area (empty rounded rectangle labeled "報告写真") and a text field "一言 (任意)".
Three small stat tiles in a row: "未知 12", "友達 7 / 100", "連続 3日".
Buttons: dark green "友達に会ったと記録する", outlined "ホームへ".
Bottom: 4-tab bar returns (home active).
```

## 05 友達（友だち100人）

```
App name: michi（未知）. Screen: FRIENDS — "make 100 friends you actually meet in real life".
Off-white background. Headline "友達". A big number "7" followed by small text "/ 100人 — リアルに会った人だけ数える".
A vertical list of friend rows, each: round initial avatar, name, small grey line "最後に会った日: 2036/9/5",
an outlined button "会った". The first row is highlighted with an ink outline and a small tag "今日誘う".
Names to render: "同期のA", "大学の友人B", "前職のC", "近所のD".
Below the list: an input "名前を追加" with an outlined "追加" button.
Bottom: 4-tab bar, person tab active.
```

## 06 アナタへのオススメ（3案一覧）

```
App name: michi（未知）. Screen: RECOMMENDATIONS — three proposals stacked as cards.
Off-white background. Headline "アナタへのオススメ", subline "今日は『いつもの』を一つだけ外してみる日".
Three cards, each with a title, a small category pill, a meta line, a green-ruled "なぜ選ばないか" block, and buttons "これにする" / "誘い文をコピー":
  1) "知らない駅で降りて昼を決める" pill "移動・散歩"
  2) "会話禁止で30分、同じものを見る" pill "文化・鑑賞"
  3) "初対面の人に一つ質問して帰る" pill "人と会う"
Bottom: 4-tab bar, "!" tab active.
```

## 07 アプリアイコン（任意）

```
App icon for "michi（未知）", 1024x1024, flat, no text.
A single off-white path/road curving upward and slightly off-frame on a deep forest green (#1F3D2B) square with rounded corners.
The path should end in a small open circle, suggesting an unknown destination. Minimal, editorial, no gradients.
```

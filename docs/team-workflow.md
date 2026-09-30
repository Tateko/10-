# 3人で開発を進めるための進め方・役割分担

- 対象リポジトリ: `Tateko/10-`
- 対象プロダクト: `docs/2026-09-13-unknown-event-app.md`（未知イベント提案アプリ）
- このドキュメントの目的: 3人が「次に何をすればいいか」で迷わない状態を作る

---

## 0. 今の状態（最初に直すこと）

| 項目 | 現状 | どうする |
| --- | --- | --- |
| コード | まだ無い（アイデアメモ1枚のみ） | Step 1〜3 のあとに雛形を作る |
| デフォルトブランチ | `claude/stoic-ride-m7z7pi` | **`main` を作ってデフォルトに変更する**（Step 3-1） |
| 公開設定 | Public | APIキーを絶対にコミットしない。気になるなら Private に変更 |
| Issue / PR | 0件 | Step 3 でテンプレとラベルを整えてから起票 |
| コラボレーター | オーナー1人 | 残り2人を招待（Step 3-2） |

---

## Step 1. 「作るもの」を1文に絞る（全員 / 30分）

3人開発が失敗する原因のほとんどは技術ではなく、**作るものの認識がズレたまま各自が進むこと**です。
最初の会議でこの1文だけ合意してください。

### MVPの定義（たたき台）

> **毎朝1回、AIが「自分では選ばない体験」を1件だけプッシュ通知で提案する。**
> **ユーザーは「行く / 気になる / 興味ない」の3ボタンだけで返す。その反応が次の提案に反映される。**

この形にする理由（メモの議論との対応）:

- 提案のトリガーがユーザーの検索ではなく **AI側からのプッシュ** → 「判断回数を減らす」という軸Aの思想を満たす
- 提案するのは効率的な正解ではなく **本人が選ばないもの** → 軸Cの「未知・非効率の価値」そのもの
- 通知を開く理由が生まれる → 「アプリである必要があるか」への答えになる

### v1 に入れないもの（ここを決めるのが本番）

- 人とのマッチング（「この人に会った方がいい」）→ v2。価値の中心だが、ユーザーが2人以上いないと成立しないので後
- 決済 / 予約 / SNS / フォロー機能 → 作らない
- 買い物・日用品の自動発注（軸A）→ メモの通り他で代替可能なので主軸にしない

### 合意できたら
`docs/decisions.md` を作り、決めたことを1行ずつ追記していく。DMで決めない、記録に残す。

---

## Step 2. 技術スタックを決める（全員 / 30分）

3人・初回・数週間という条件なら、**1リポジトリのフルスタック構成**が一番揉めません。

| レイヤー | 採用案 | 理由 |
| --- | --- | --- |
| フロント | Next.js (App Router) + TypeScript + Tailwind | 3人とも同じ言語で読める |
| API | Next.js の Route Handlers（同じリポジトリ内） | サーバーを別に立てない＝デプロイが1つで済む |
| DB / 認証 | Supabase (Postgres + Auth) | 認証を自作しない。無料枠で始められる |
| AI | Claude API（`claude-sonnet-5`）で提案生成 | 提案文の質がそのままプロダクトの価値 |
| 通知 | PWA + Web Push | アプリストア審査なしで通知が出せる |
| デプロイ | Vercel | **PRごとにプレビューURLが出る**ので、3人開発と相性が良い |
| CI | GitHub Actions（lint / typecheck / build） | 壊れたコードが main に入らない |

> 迷ったら「3人が同じ画面を見られるか」で選ぶ。PRプレビューURLはレビュー速度を体感で倍にします。

---

## Step 3. リポジトリの初期設定（担当C / 30分）

### 3-1. `main` ブランチを作ってデフォルトにする

```bash
git switch -c main origin/claude/stoic-ride-m7z7pi
git push -u origin main
```

そのあと GitHub の画面で:
`Settings` → `General` → `Default branch` → 鉛筆アイコン → `main` に変更

### 3-2. 2人を招待する

`Settings` → `Collaborators` → `Add people` → GitHubのユーザー名を入力 → `Write` 権限

### 3-3. main を保護する（これが一番効く）

`Settings` → `Branches` → `Add branch ruleset`（または `Add rule`）で `main` に対して:

- [x] Require a pull request before merging（Required approvals: **1**）
- [x] Require status checks to pass（CIができたら `ci` を必須に）
- [x] Block force pushes

→ これで「間違って main に直接push」が物理的に起きなくなります。

### 3-4. ラベルを作る

`Issues` → `Labels` → `New label`

```
area/frontend   area/backend   area/ai   area/infra
type/feat       type/bug       type/docs
prio/high       prio/low       good-first-task
```

### 3-5. Project（かんばん）を1つ作る

`Projects` → `New project` → `Board` テンプレ
カラム: `Todo` / `In progress` / `In review` / `Done`
→ 3人の「今なにやってるか」がこの1画面で分かる状態にする。

### 3-6. テンプレート

このドキュメントと同じPRに以下を入れてあります。

- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/task.md`
- `.github/CODEOWNERS`（コメントアウト済み。ユーザー名を入れて有効化する）

---

## Step 4. 役割分担

3人を **A / B / C** とします。ポイントは肩書きではなく、
**「触るディレクトリを分ける」＝コンフリクトが構造的に起きないようにすること**です。

### A — プロダクト & AI提案ロジック

> 担当するのは「**何を**提案するか」。アプリの価値の中心。

- **オーナーのディレクトリ**: `src/lib/ai/`, `prompts/`, `docs/`
- **責任範囲**
  - 提案生成プロンプトの設計と改善
  - 提案の「未知度」をどう担保するかのルール決め
  - 提案の質の評価
- **最初のタスク**
  1. 提案生成プロンプトを書く。入力＝ユーザーの好み＋過去の反応履歴、出力＝JSON
     （`title` / `description` / `place` / `when` / `why_unexpected`＝なぜあなたが選ばないか）
  2. 「未知度」のルールを決める（例: 直近の興味タグから意図的に1段ずらす、過去に出した提案は除外、3回に1回は全く別ジャンルを混ぜる）
  3. `generateSuggestion()` の実装（Claude API 呼び出し + JSONパース + バリデーション）
  4. **評価シート**: 手で提案を20件出し、3人で「実際に行きたいか」を5段階採点する。これが唯一の品質指標
- **レビュー担当**: B のPR
- **向いている人**: 企画を考えるのが好き、文章の細かい違いが気になる人

### B — フロントエンド & 通知体験

> 担当するのは「**どう届くか**」。通知を開く気になるかどうかはここで決まる。

- **オーナーのディレクトリ**: `src/app/(ui)/`, `src/components/`, `public/`
- **責任範囲**
  - ユーザーが触る画面すべて
  - PWA化と通知の受け取り
- **最初のタスク**
  1. 画面3枚だけ作る: ①オンボーディング（好み入力）②今日の提案 ③履歴
  2. 3ボタンのフィードバックUI（行く / 気になる / 興味ない）
  3. PWA化（`manifest.json` + Service Worker）と Web Push の購読登録
  4. ローディング・エラー・提案がない時の表示（ここを飛ばすと動くけど使えないアプリになる）
- **レビュー担当**: C のPR
- **向いている人**: 見た目・触り心地が気になる人

### C — バックエンド & インフラ

> 担当するのは「**土台**」。最初の1週間は3人の中で一番忙しい。

- **オーナーのディレクトリ**: `src/app/api/`, `src/lib/db/`, `supabase/`, `.github/`
- **責任範囲**
  - DB設計、API、認証、CI/CD、デプロイ、シークレット管理
- **最初のタスク**
  1. **Next.jsの雛形を作って push する（最優先。これが無いとA・Bが動けない）**
  2. DBスキーマ: `users` / `preferences` / `suggestions` / `feedbacks`
  3. API 3本: `POST /api/suggestions/generate` / `GET /api/suggestions/today` / `POST /api/feedback`
  4. Supabase Auth の接続
  5. 毎朝7時の Vercel Cron → 提案生成 → Push送信
  6. GitHub Actions の CI と Vercel のデプロイ設定
  7. `.env.example` を用意。**APIキーは絶対にコミットせず、Vercelの環境変数に置く**（リポジトリはPublic）
- **レビュー担当**: A のPR
- **向いている人**: 環境構築やデータの形を考えるのが苦にならない人

### 境界にあるもの（揉める前に決めておく）

| もの | 決め方 |
| --- | --- |
| 型定義 `src/types/index.ts` | **C が最初に作る**。変更するPRは必ず3人にレビュー依頼 |
| APIの入出力の形 | **C が決める**。A・B はそれに合わせる。変えたい時は Issue を立てて議論 |
| 提案文の文言・トーン | **A が決める**。B は表示だけ担当し、勝手に文言を変えない |
| 画面の遷移・情報設計 | **B が決める**。A は提案内容にだけ口を出す |

### 全員共通のルール

- **月曜30分の同期**: 先週やったこと / 今週やること / 詰まっていること の3つだけ話す
- **水・金は非同期**: Project のカードにコメントで進捗を書く
- **「誰かの返事待ち」を24時間以上放置しない**。3人だと1人の詰まりが全体を止めます

---

## Step 5. 毎日のGitHub運用（3人とも覚える手順）

```bash
# 1. 最新の main から始める
git switch main && git pull origin main

# 2. Issue番号を入れてブランチを切る
git switch -c feat/12-today-screen

# 3. 作業してコミット（小さく、こまめに）
git add -A && git commit -m "feat: 今日の提案画面を追加 (#12)"

# 4. push
git push -u origin feat/12-today-screen

# 5. GitHubで Draft PR を作る（作業途中でOK。早く出すほど事故が減る）
# 6. 完成したら Ready for review → レビュワーを指名
# 7. approve 1つ + CI green で Squash and merge
# 8. マージ後の後片付け
git switch main && git pull origin main && git branch -d feat/12-today-screen
```

### ルール

- **1 Issue = 1 PR**。PRは差分300行以内を目安に。大きいPRは読まれず、放置されます
- **Draft PR を早く出す**。「まだ途中だから出さない」が一番危険。方向がズレていたら早く気づけます
- **レビューは24時間以内に返す**。「LGTM」だけでも返す。止めないことが最優先
- **main に直接 push しない**（Step 3-3 の保護で防ぐ）
- **毎日1回、main を自分のブランチに取り込む**
  ```bash
  git fetch origin && git merge origin/main
  ```
- **コンフリクトしたら、そのファイルのオーナー（Step 4）に聞いてから直す**
- ブランチ名: `feat/<issue番号>-<内容>` / `fix/<issue番号>-<内容>`
- コミットメッセージ: `feat:` `fix:` `docs:` `refactor:` を先頭につける

---

## Step 6. 最初の2週間の具体的な進め方

### Week 1 — 土台を作る

| 誰 | やること |
| --- | --- |
| 全員 | 1時間の会議1回で Step 1・Step 2 を決め切る |
| **C** | リポジトリ設定 → Next.js雛形 → Supabase接続 → CI → Vercelデプロイ。**最優先** |
| **A** | コードを書かずに、Claudeの画面上でプロンプトを詰める。良い提案が出る形を先に見つける |
| **B** | 画面3枚のワイヤーを紙かFigmaで描く。Cの雛形が来たらUI着手 |

> C の雛形が出るまで A・B が手持ち無沙汰になるのは想定内です。**そこで各自が別のプロジェクトを作り始めないこと。** 二重管理になります。

### Week 2 — 縦に1本通す

**「ボタンを押したら提案が1件表示される」を3人で最後まで通す。** 通知はまだ実装しない。

- B: ボタンを押す → API を叩く
- C: API がリクエストを受ける → A の関数を呼ぶ → DB に保存して返す
- A: Claude API を呼んで提案を1件生成する

金曜に3人で実機を触って、「この提案、行きたいと思うか？」を確認する。

> **一番危ない失敗パターン**: 3人が別々のパーツを作り込んで最後に繋ごうとすること。必ず繋がりません。
> Week 2 で細くていいので1本通し、そのあと各自が太らせる、の順番を守ってください。

### Week 3 以降

通知（Cron + Web Push）→ フィードバックの学習反映 → 提案の質の改善ループ、の順。

---

## Step 7. 最初に立てるIssue（そのままコピーして起票できます）

| # | タイトル | 担当 | ラベル |
| --- | --- | --- | --- |
| 1 | `main` ブランチ作成とブランチ保護の設定 | C | area/infra |
| 2 | Next.js + TypeScript + Tailwind の雛形を作る | C | area/infra |
| 3 | Supabase プロジェクト作成と接続 | C | area/backend |
| 4 | DBスキーマ設計（users / preferences / suggestions / feedbacks） | C | area/backend |
| 5 | GitHub Actions で lint・typecheck・build を回す | C | area/infra |
| 6 | 提案生成プロンプトの設計（入出力JSONの確定） | A | area/ai |
| 7 | `generateSuggestion()` の実装 | A | area/ai |
| 8 | 提案の「未知度」ルールを決める | A | area/ai |
| 9 | 提案20件を出して3人で品質を採点する | A | area/ai |
| 10 | オンボーディング画面（好み入力） | B | area/frontend |
| 11 | 今日の提案画面 + 3ボタンUI | B | area/frontend |
| 12 | 履歴画面 | B | area/frontend |
| 13 | PWA化と Web Push の購読登録 | B | area/frontend |
| 14 | API: 提案の生成・取得・フィードバック | C | area/backend |
| 15 | Vercel Cron で毎朝7時に提案を生成して通知 | C | area/backend |

---

## Step 8. 詰まった時のルール

- 技術的に迷ったら **Issue に書く**。DMや口頭で決めない（記録が残らず、3人目が知らないまま進む）
- 決まったことは `docs/decisions.md` に1行足す
- 30分調べて分からないことは、迷わず他の2人に聞く。3人しかいないので遠慮のコストの方が高い
- 予定通りに行かないのが普通です。**スコープを削る**（v2に送る）判断を毎週やってください

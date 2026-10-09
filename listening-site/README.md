# ひだまり傾聴室 — 集客用ランディングページ

「誰にも言えない話を、否定せずに聴く」傾聴サービスの集客用サイトです。
`index.html` 1ファイルだけで動きます（ビルド不要・サーバー不要）。ブラウザで開けばそのまま確認できます。

## 公開前に差し替えるところ

| 場所 | 内容 |
| --- | --- |
| `index.html` 末尾の `CONTACT_EMAIL` | 予約メールの受付アドレス |
| `index.html` 末尾の `LINE_URL` | LINE公式アカウントの友だち追加URL（空のままだとフォームへ移動） |
| `index.html` 末尾の `FORM_ENDPOINT` | [Formspree](https://formspree.io) のフォームURL。入れると申し込みがメールに直接届く（空欄なら確認画面から利用者がメールで送る） |
| `index.html` 末尾の `GCAL_SCHEDULES` | Googleカレンダー予約スケジュールのURL（下記参照）。入れるとGoogleの予約画面に切り替わる |
| `index.html` 末尾の `BOOKING` | Google未設定時に使う簡易カレンダーの営業時間・定休日など |
| 料金プランの金額 | 仮の金額です（初回1,000円 / 30分2,000円 / 60分3,500円） |
| 「話してくれた人の声」 | **掲載例（架空）** です。実際の利用者から掲載許可をもらった声に差し替え、「掲載例」タグを外してください。架空の声を実在のように載せるのは景品表示法上の問題になり得ます |
| サービス名「ひだまり傾聴室」 | 仮の名前です。ファイル内を一括置換すれば変更できます |

## Googleカレンダー予約スケジュールとの連携

`GCAL_SCHEDULES` にURLが1つでも入っていると、予約欄がGoogleの予約画面に切り替わります。
空き状況の自動反映・二重予約の防止・確認メール・リマインダー・変更/キャンセルをGoogleが処理します。
URLが全部空なら、今までの簡易カレンダー＋メール申し込みフォームが表示されます。

1. パソコンで Googleカレンダー を開き、左上の「＋作成」→「予約スケジュール」
2. 予約枠の時間（30分 or 60分）、予約可能な曜日・時間帯、予約受付期間、前後のバッファ時間などを設定
3. 「予約フォーム」に質問を追加：「相談方法（電話／オンライン通話／チャット）」「伝えておきたいこと（任意）」
4. 保存後、予約スケジュールを開いて「共有」→「ウェブサイトに埋め込む」→「インライン」のコードの `src="..."` の中のURLをコピー
5. `index.html` の `GCAL_SCHEDULES` の該当プランの `url` に貼り付ける

```js
const GCAL_SCHEDULES = [
  { plan: "初回お試し30分", price: "¥1,000", url: "https://calendar.google.com/calendar/appointments/schedules/xxxx?gv=true" },
  { plan: "30分プラン",     price: "¥2,000", url: "https://calendar.google.com/calendar/appointments/schedules/xxxx?gv=true" },
  { plan: "60分プラン",     price: "¥3,500", url: "https://calendar.google.com/calendar/appointments/schedules/yyyy?gv=true" },
];
```

- 30分の予約スケジュールを「初回お試し」と「30分プラン」で共有し、60分用をもう1つ作る、の2つで十分です
- 空欄のプランはタブに表示されません。1つだけ入れた場合はタブ自体が出ません
- 無料のGoogleアカウントでも作れます。予約時のオンライン決済や一部の機能は有料プラン（Google Workspace 等）が必要です

## Square（オンライン決済）との連携

`PAYMENT_LINKS` にURLが入っていると、予約欄の下に「お支払い」ボタンが表示されます（空欄なら非表示）。
カード情報はSquareの画面で入力されるため、このサイトで扱うことはありません。

1. [Square](https://squareup.com/jp/ja) で無料アカウントを作成（本人確認・振込口座の登録があります）
2. Squareデータ（管理画面）→「オンライン」→「決済リンク」→「リンクを作成」
3. 「商品を販売」または「支払いを回収」で、プランごとにリンクを作る
   - 初回お試し30分 1,000円 ／ 30分プラン 2,000円 ／ 60分プラン 3,500円
4. できたリンク（`https://square.link/u/...`）を `index.html` の `PAYMENT_LINKS` に貼り付ける

```js
const PAYMENT_LINKS = [
  { plan: "初回お試し30分", price: "¥1,000", url: "https://square.link/u/xxxxxx" },
  { plan: "30分プラン",     price: "¥2,000", url: "https://square.link/u/yyyyyy" },
  { plan: "60分プラン",     price: "¥3,500", url: "https://square.link/u/zzzzzz" },
];
```

### 特定商取引法に基づく表記（必須）

ネットで有料サービスを売るには、特定商取引法に基づく表記が必要です（Squareの審査でも確認されます）。
`tokushoho.html` の黄色い部分（氏名・連絡先・キャンセル規定）を記入してください。フッターからリンクしています。

## X の話題から投稿案を作る（Grok）

### 無料：X アプリの Grok に依頼文を貼る（今はこちら）

`sns/trends/grok-prompt.md` の依頼文を、X アプリの Grok に週1回コピーして貼るだけです。
Grok が X で今話題の悩み・言葉を調べ、`posts.md` の口調に合わせた投稿案（X 10本・Threads 3本）を返してくれます。費用はかかりません（無料プランは回数に上限あり）。

### 有料：GitHub Actions で自動化（収益化してから）

xAI の API（従量課金）を使い、Grok の調査と投稿案づくりを自動で行って `sns/trends/日付.md` に書き出し、PR にします。**自動では投稿しません。**
費用がかかるので今は手動実行のみにしてあります。

1. [xAI のコンソール](https://console.x.ai) でアカウントを作り、クレジットを購入して API キーを発行する（無料枠なし）
2. GitHub のこのリポジトリで `Settings` → `Secrets and variables` → `Actions` → `New repository secret`
   - Name: `XAI_API_KEY` ／ Secret: 発行したキー
3. `Settings` → `Actions` → `General` → 一番下の「Allow GitHub Actions to create and approve pull requests」にチェック
4. `Actions` タブ → 「X話題チェック→投稿案」→ `Run workflow` で実行する

- 毎週自動で動かすときは `.github/workflows/x-trend-drafts.yml` 冒頭のコメントにある `schedule` を `on:` に戻す
- 使うモデルを変えたいときは、`Secrets and variables` → `Actions` → `Variables` に `XAI_MODEL`（例：`grok-4`）を登録する

## PR動画（`promo/`）

- `promo/promo.mp4`：SNS用の縦型動画（1080×1920・30fps・35秒・音なし）。Instagramリール／TikTok／YouTubeショート／Xにそのまま投稿できます
- BGMは各アプリの投稿画面で、アプリ内の音楽ライブラリから付けてください（著作権の許諾が済んだ曲を使えます）
- 文言や写真を変えたいときは `promo/promo.html` を編集し、`promo/` で `npm i playwright ffmpeg-static && node record-promo.mjs` を実行すると書き出し直せます

## 構成

1. ヒーロー（キャッチコピー＋会話イメージ）
2. こんな悩みありませんか（共感）
3. 傾聴とは（アドバイスとの違い）
4. 3つのお約束（否定しない・秘密を守る・急かさない）
5. 相談できること（仕事・恋愛・お金/借金・家族・ただ聴いてほしい）
6. 聴き手のプロフィール（50人以上の相談経験）
7. 利用者の声（掲載例）
8. 料金プラン
9. 相談までの流れ
10. よくある質問
11. 予約（LINE／フォーム → メールアプリ起動）＋緊急時の相談窓口

## 注意書きについて

- 借金の相談については「気持ちの整理」に留め、具体的な債務整理の助言はしない旨を明記しています（弁護士・司法書士以外が法律事務を扱うことは弁護士法で制限されています）。
- 医療行為・心理療法ではない旨と、緊急時の公的相談窓口（いのちの電話・よりそいホットライン・法テラス）を掲載しています。番号は公開前に最新情報をご確認ください。

## GitHub Pages で公開する（ひだまり専用アカウント）

サイトは、このリポジトリとは別の、ひだまり専用 GitHub アカウントのリポジトリで公開します。

1. サービス用の Gmail で GitHub アカウントを作る（ユーザー名の例：`hidamari-keicho`）
2. 新しいリポジトリを **Public** で作る。名前を `ユーザー名.github.io`（例：`hidamari-keicho.github.io`）にすると、URL が `https://hidamariqingtingshihiro-gif.github.io/hidamari-keicho.github.io/` になる
3. 「uploading an existing file」から `index.html`・`tokushoho.html`・`images` フォルダ（`hiro.jpg`・`ogp.jpg`）をアップロードして `Commit changes`
4. `Settings` → `Pages` で `Deploy from a branch` / `main` / `/ (root)` を選んで `Save`
5. 1〜3分後、`https://ユーザー名.github.io/` で表示される

ユーザー名が `hidamari-keicho` 以外になった場合は、`index.html` の `og:url` と `og:image` を実際のURLに直してください（SNSでリンクを貼ったときの画像に使われます）。

### 公開前チェック

- [ ] 予約の受け取り先：`FORM_ENDPOINT`（Formspree）または `CONTACT_EMAIL` を設定した
- [ ] `tokushoho.html` の黄色い部分（氏名・連絡先・キャンセル規定）を記入した
- [ ] 料金・営業時間（`BOOKING`）が実際と合っている
- [ ] 「50人以上」などの実績表記が事実どおり
- [ ] 利用者の声は、許可をもらった実際の声が集まるまで非表示のまま（`<section hidden>`）
- [ ] LINE公式アカウントを作ったら `LINE_URL` を入れる（空欄のあいだはボタンを出さない）

## 公開方法の例

- GitHub Pages / Netlify / Vercel などに `listening-site/` フォルダをそのままアップロード
- 予約をフォームで確実に受け取りたい場合は、Googleフォーム・Formspree などに送信先を変更するのがおすすめです

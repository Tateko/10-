# michi — 未知イベント提案アプリ

「自分では選ばない体験」を、今日この後の予定としてAIが3つ提案する。
提案には必ず **なぜあなたはこれを選ばないか（根拠）** と **誰を誘うか・誘い文** と **60秒でできる最初の一歩** が付く。

- アイデアの経緯: [docs/2026-09-13-unknown-event-app.md](docs/2026-09-13-unknown-event-app.md)
- ハッカソン要件・進行・発表構成: [docs/hackathon-brief.md](docs/hackathon-brief.md)

## 動かす

```bash
npm install
cp .env.example .env      # ANTHROPIC_API_KEY を入れる
export $(grep -v '^#' .env | xargs)
npm start                 # http://localhost:3000
```

APIキーが無いときは自動で **モックモード**（固定の3案を返す）で起動する。UIの確認・発表リハはこれで足りる。
明示的にモックで動かすなら `npm run mock`。

## 構成

| ファイル | 役割 |
|---|---|
| `server.js` | Express。`POST /api/suggest` で Claude（`claude-opus-5`）を呼び、Zodスキーマで構造化出力を保証 |
| `public/index.html` | 単一ページのフロント（依存なし） |
| `.env.example` | 環境変数のひな形 |

### API

`POST /api/suggest`

```json
{ "area": "渋谷", "minutes": "60", "mood": "何か刺激がほしい",
  "budget": "〜1,000円", "recent": "休日はだいたい家で動画", "companion": "同期のA" }
```

レスポンス: `one_liner` と `proposals[3]`（`title, category, why_you_wouldnt_pick, what, where_hint, duration_min, cost_hint, invite_who, invite_message, first_step, emotion`）。

`GET /api/health` → `{ ok, mode: "live" | "mock", model }`

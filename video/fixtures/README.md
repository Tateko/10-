# 公開サイトから持ってきた素材を置くところ

外に出られない環境（このリポジトリのCI／Claude Code の実行環境など）から
公開中の michi を録るときは、ブラウザで保存したHTMLをここに置く。

| ファイル | 取り方 |
|---|---|
| `deployed-index.html` | 公開URLをブラウザで開く → ページのソースを表示（Ctrl/⌘+U）→ 全選択してこのファイルに貼る。<br>「名前を付けて保存 → 完全なページ」ではなく **ソースそのもの** がいい（michi は1ファイルで完結しているため） |
| `deployed-suggest.json`（任意） | DevTools → Network → `/api/suggest` の Response をそのまま保存。<br>渡すと、映像に出る3案が「公開サイトで実際に返ってきた提案」そのものになる |

置いたら、こう回す。

```bash
FIXTURE=video/fixtures/deployed-index.html \
SUGGEST_FIXTURE=video/fixtures/deployed-suggest.json \
  bash video/build.sh
```

`SUGGEST_FIXTURE` を渡さない場合、`/api/*` はローカルの `server.js`（APIキーが無ければモック）に中継される。

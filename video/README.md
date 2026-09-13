# PR動画をコードから作る

`video/` は、michi の **PR動画（78秒）** を1コマンドで作り直すための一式。
動画編集ソフトも素材サイトも使わない。**実際に動いているアプリを Playwright で操作して録り**、
その上に字幕を重ねて、BGMも合成して吐く。文言を直したら、また回すだけで作り直せる。

```bash
bash video/build.sh          # → video/out/michi-pr.mp4
```

APIキーは要らない（アプリが自動でモックに落ちる）。所要 10〜15分程度。

## できるもの

| ファイル | 中身 |
|---|---|
| `out/michi-pr.mp4` | 本編。1920×1080 / 30fps / 78秒 / H.264 + AAC |
| `out/michi-pr-thumb.jpg` | サムネイル（提出フォームやスライド用） |

## 中身

| ファイル | 役割 |
|---|---|
| `script.md` | 台本。時刻・字幕・画面の対応表。**直すならまずここ** |
| `capture-app.mjs` | 実アプリを操作して1コマずつPNGにする。端末の状態（友達・履歴・設定）も先に仕込む |
| `scenes.html` | 1920×1080 の本編そのもの。`window.seek(t)` で任意の秒に飛べる作り |
| `render.mjs` | `scenes.html` を30fpsでPNGに焼く。`--at 30,44` で特定の秒だけ確認できる |
| `music.py` | BGMの合成（numpyだけ。外部音源なし＝権利関係なし） |
| `build.sh` | 上を順に回して mp4 にする |

`build/`（中間生成物：アプリのコマ・本編のコマ・BGM）は git に入れない。

## 直したいとき

- **字幕・言い回し** → `scenes.html` の `CAPS` / 各シーンのHTML。`script.md` も合わせて直す
- **デモの流れ** → `capture-app.mjs`。操作を足したら `manifest.json` のマーカー番号が変わるので、
  `scenes.html` の `APP_KEYS`（動画の秒 → アプリのコマ番号）を貼り直す
- **尺・構成** → `scenes.html` の `SCENES`（各シーンの開始・終了秒）と `DURATION`
- **速く確認したい** → `node render.mjs --at 9.5,30,44` で数枚だけ焼いて見る。
  ブラウザで `scenes.html#play` を開くと通しで再生もできる（アプリのコマは `build/app/` が要る）

## 作りの都合

- ブラウザのアニメーション（CSSトランジション）は使わず、`seek(t)` が毎コマ位置と不透明度を計算する。
  実時間に依存しないので、レンダリングが遅い環境でもコマ落ちしない。
- 日本語フォントは `@fontsource/noto-serif-jp` / `noto-sans-jp` をnpmから入れて `file://` で読む
  （実行環境にフォントが無くても同じ絵になる）。
- Playwright は端末に置いてあるブラウザに合わせて `1.56.1` 固定。
- ffmpeg は `@ffmpeg-installer/ffmpeg`（npmで入る）を使う。システムに入れなくていい。

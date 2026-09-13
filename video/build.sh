#!/usr/bin/env bash
# michi の PR動画を最初から最後まで作り直す。
#
#   bash video/build.sh
#     → このリポジトリのアプリをローカルで起動して録る（APIキー不要。モックで動く）
#
#   BASE_URL=https://fuu-black-letter.tatetate0912-10969.workers.dev bash video/build.sh
#     → 公開中のサイトをそのまま録る（ローカルのサーバーは起動しない）
#
#   FIXTURE=video/fixtures/deployed-index.html bash video/build.sh
#     → 公開サイトから保存してきたHTMLを録る（外に出られない環境用）。
#       /api/* はローカルのサーバーに中継する。公開サイトで実際に返ってきた
#       /api/suggest のJSONがあれば SUGGEST_FIXTURE=... で一緒に渡す
#
# 前提: リポジトリ直下で npm install 済み（ローカル起動する場合のみ）。
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
BUILD="${OUT_DIR:-$HERE/build}"
OUT="$HERE/out"
FPS="${FPS:-30}"
PORT="${PORT:-3100}"

mkdir -p "$BUILD" "$OUT"
cd "$HERE"
[ -d node_modules ] || npm install --no-audit --no-fund

# 1. 録る相手を決める。BASE_URL が指定されていればそこを録る（公開URLでもいい）
TARGET="${BASE_URL:-}"
FIXTURE="${FIXTURE:-}"
FIXTURE_PORT="${FIXTURE_PORT:-3200}"
if [ -z "$TARGET" ] && [ -n "$FIXTURE" ]; then
  # 保存したHTMLを配る。APIは下のローカルサーバーへ中継する
  if ! curl -sf "http://localhost:$PORT/api/health" >/dev/null 2>&1; then
    echo "==> アプリ(API用)を起動 (port $PORT)"
    (cd "$ROOT" && [ -d node_modules ] || npm install --no-audit --no-fund)
    (cd "$ROOT" && MOCK=1 PORT="$PORT" node server.js > "$BUILD/server.log" 2>&1 &)
    for _ in $(seq 1 30); do curl -sf "http://localhost:$PORT/api/health" >/dev/null && break; sleep 0.5; done
    STARTED=1
  fi
  echo "==> 保存したHTMLを配る: $FIXTURE (port $FIXTURE_PORT)"
  FIXTURE="$FIXTURE" SUGGEST_FIXTURE="${SUGGEST_FIXTURE:-}" API_ORIGIN="http://localhost:$PORT" \
    PORT="$FIXTURE_PORT" node "$HERE/serve-fixture.mjs" > "$BUILD/fixture.log" 2>&1 &
  FIXTURE_PID=$!
  TARGET="http://localhost:$FIXTURE_PORT"
  for _ in $(seq 1 30); do curl -sf "$TARGET" >/dev/null && break; sleep 0.5; done
elif [ -z "$TARGET" ]; then
  TARGET="http://localhost:$PORT"
  if ! curl -sf "$TARGET/api/health" >/dev/null 2>&1; then
    echo "==> アプリを起動 (port $PORT)"
    (cd "$ROOT" && [ -d node_modules ] || npm install --no-audit --no-fund)
    (cd "$ROOT" && MOCK=1 PORT="$PORT" node server.js > "$BUILD/server.log" 2>&1 &)
    for _ in $(seq 1 30); do curl -sf "$TARGET/api/health" >/dev/null && break; sleep 0.5; done
    STARTED=1
  fi
else
  echo "==> 公開中のサイトを録る: $TARGET"
  curl -sfI "$TARGET" >/dev/null || { echo "!! $TARGET に届かない。URLとネットワークを確認して。"; exit 1; }
fi

# 2. 実アプリを操作して録る
echo "==> アプリ画面をキャプチャ"
BASE_URL="$TARGET" OUT_DIR="$BUILD" node capture-app.mjs

# 3. BGM
echo "==> BGM を合成"
OUT_DIR="$BUILD" python3 music.py

# 4. 本編のフレームを焼く
echo "==> 本編フレームをレンダリング"
OUT_DIR="$BUILD" FPS="$FPS" node render.mjs

# 5. 書き出し
FFMPEG="$(node -p "require('@ffmpeg-installer/ffmpeg').path")"
DUR="$(node -e "const f=require('fs');console.log(f.readdirSync('$BUILD/frames').length/$FPS)")"
echo "==> エンコード（${DUR}秒）"
"$FFMPEG" -y -hide_banner -loglevel warning \
  -framerate "$FPS" -i "$BUILD/frames/f%06d.png" \
  -i "$BUILD/bgm.wav" \
  -filter_complex "[0:v]fade=t=in:st=0:d=0.6,fade=t=out:st=$(echo "$DUR - 1.0" | bc):d=1.0,format=yuv420p[v]" \
  -map "[v]" -map 1:a -shortest \
  -c:v libx264 -preset slow -crf 20 -movflags +faststart \
  -c:a aac -b:a 192k -ar 44100 \
  "$OUT/michi-pr.mp4"

# サムネイル（提出フォームやスライドに貼る用）
"$FFMPEG" -y -hide_banner -loglevel warning -i "$OUT/michi-pr.mp4" -ss 30 -frames:v 1 -q:v 3 "$OUT/michi-pr-thumb.jpg"

[ -n "${FIXTURE_PID:-}" ] && kill "$FIXTURE_PID" 2>/dev/null || true
[ "${STARTED:-0}" = "1" ] && pkill -f "PORT=$PORT node server.js" 2>/dev/null || true

ls -lh "$OUT"
echo "==> できあがり: $OUT/michi-pr.mp4"

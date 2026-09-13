#!/usr/bin/env bash
# michi の PR動画を最初から最後まで作り直す。
#   bash video/build.sh
# 前提: リポジトリ直下で npm install 済み（アプリを動かすため）。APIキーは不要（モックで動く）。
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

# 1. アプリを起動（APIキーが無ければ自動でモック）
if ! curl -sf "http://localhost:$PORT/api/health" >/dev/null 2>&1; then
  echo "==> アプリを起動 (port $PORT)"
  (cd "$ROOT" && [ -d node_modules ] || npm install --no-audit --no-fund)
  (cd "$ROOT" && MOCK=1 PORT="$PORT" node server.js > "$BUILD/server.log" 2>&1 &)
  for _ in $(seq 1 30); do curl -sf "http://localhost:$PORT/api/health" >/dev/null && break; sleep 0.5; done
  STARTED=1
fi

# 2. 実アプリを操作して録る
echo "==> アプリ画面をキャプチャ"
BASE_URL="http://localhost:$PORT" OUT_DIR="$BUILD" node capture-app.mjs

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

[ "${STARTED:-0}" = "1" ] && pkill -f "PORT=$PORT node server.js" 2>/dev/null || true

ls -lh "$OUT"
echo "==> できあがり: $OUT/michi-pr.mp4"

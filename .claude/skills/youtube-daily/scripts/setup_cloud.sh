#!/bin/bash
# クラウド（Linux）の Claude Code で、自動編集キットを動かす準備をする。セッションごとに1回。何度実行しても大丈夫。
#
#   bash setup_cloud.sh <キットの zip か、展開したフォルダ>
#
# 入れる物（全部ホームの中）
#   ~/.autoedit-venv            Python 3.12・Pillow・numpy・ffmpeg（imageio-ffmpeg）・Playwright・pyopenjtalk-plus
#   ~/.local/bin/say            Mac の say の代わり（OpenJTalk の無料の声）
#   ~/.local/share/fonts と ~/Library/Fonts   Noto Sans JP（キットは ~/Library/Fonts を探すので両方に置く）
#   ~/.claude/skills/masayume-auto-edit-lite キットのスキル
set -u
KIT_SRC="${1:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
VENV="$HOME/.autoedit-venv"
PY="$VENV/bin/python"
NG=0
ok() { echo "✅ $*"; }
ng() { echo "❌ $*"; NG=$((NG + 1)); }

# 1. Python と道具
command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh >/dev/null 2>&1
UV="$(command -v uv || echo "$HOME/.local/bin/uv")"
[ -x "$PY" ] || "$UV" venv -q --python 3.12 "$VENV" >/dev/null 2>&1
# この環境に最初から入っている Chromium に合う Playwright を入れる（playwright install はしない）
PWV="$(node -e "console.log(require('/opt/node22/lib/node_modules/playwright/package.json').version)" 2>/dev/null)"
PWV="${PWV:-1.63.0}"
"$UV" pip install -q --python "$PY" pillow numpy imageio-ffmpeg "playwright==$PWV" pyopenjtalk-plus >/dev/null 2>&1
F="$("$PY" -c 'import imageio_ffmpeg as m; print(m.get_ffmpeg_exe())' 2>/dev/null)"
[ -n "$F" ] && ln -sf "$F" "$VENV/bin/ffmpeg"
"$PY" -c 'import PIL, numpy, playwright, pyopenjtalk' >/dev/null 2>&1 && ok "Python 3.12・Pillow・Playwright $PWV・OpenJTalk" || ng "Python の道具が入っていません"
[ -x "$VENV/bin/ffmpeg" ] && ok "ffmpeg" || ng "ffmpeg が入っていません"

# 2. フォント（github が止められていても gstatic から取る）
FONT="$HOME/.local/share/fonts/NotoSansJP-VariableFont_wght.ttf"
mkdir -p "$HOME/.local/share/fonts" "$HOME/Library/Fonts"
if [ ! -s "$FONT" ]; then
  for u in "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf" \
           "https://fonts.gstatic.com/s/notosansjp/v53/-F6jfjtqLzI2JPCgQBnw7HFyzSD-AsregP8VFBEj75s.ttf"; do
    curl -fsSL -m 120 -o "$FONT" "$u" 2>/dev/null && break
  done
fi
cp -f "$FONT" "$HOME/Library/Fonts/" 2>/dev/null
[ -s "$HOME/Library/Fonts/NotoSansJP-VariableFont_wght.ttf" ] && ok "フォント Noto Sans JP" || ng "フォントが入っていません"

# 3. 無料の声（say の代わり）
mkdir -p "$HOME/.local/bin"
cp -f "$HERE/say_linux.py" "$HOME/.local/bin/say" && chmod +x "$HOME/.local/bin/say"
sed -i "1s|.*|#!$PY|" "$HOME/.local/bin/say"
TMPW="$(mktemp --suffix=.wav)"
"$HOME/.local/bin/say" -v Kyoko -r 290 -o "$TMPW" "てすと" && [ -s "$TMPW" ] && ok "無料の声（OpenJTalk）" || ng "無料の声が作れません"
rm -f "$TMPW"

# 4. キットのスキル
if [ -n "$KIT_SRC" ]; then
  if [ -f "$KIT_SRC" ]; then
    D="$(mktemp -d)"; unzip -q -o "$KIT_SRC" -d "$D"; KIT_SRC="$D"
  fi
  SK="$(find "$KIT_SRC" -type d -name masayume-auto-edit-lite -path '*01_*' | head -1)"
  if [ -n "$SK" ]; then
    mkdir -p "$HOME/.claude/skills"; rm -rf "$HOME/.claude/skills/masayume-auto-edit-lite"
    cp -R "$SK" "$HOME/.claude/skills/"
  fi
fi
"$PY" "$HOME/.claude/skills/masayume-auto-edit-lite/scripts/autoedit.py" --help 2>/dev/null | grep -q "自動編集" \
  && ok "キットのスキル（masayume-auto-edit-lite）" || ng "キットのスキルがありません（キットの zip をアップロードして、その場所を渡す）"

echo
[ "$NG" -eq 0 ] && echo "SETUP_RESULT: OK" || echo "SETUP_RESULT: NG $NG"

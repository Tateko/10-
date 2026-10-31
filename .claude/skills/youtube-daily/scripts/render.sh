#!/bin/bash
# plan.json を作って、キットで書き出し、仕上げまで。10分前後かかるので、Claude Code ではバックグラウンドで実行する。
#
#   bash render.sh <動画のフォルダ>
set -e
V="$1"
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$HOME/.autoedit-venv/bin/python"
KIT="$HOME/.claude/skills/masayume-auto-edit-lite/scripts/autoedit.py"
python3 "$HERE/build_plan.py" "$V"
"$PY" "$KIT" all "$V" --script "$V/台本.md" > "$V/out/log.txt" 2>&1 || { tail -20 "$V/out/log.txt"; exit 1; }
tail -6 "$V/out/log.txt"
sed -n '/直す所/,/→/p' "$V/out/check_report.md"
cd "$HERE" && "$PY" finish.py "$V"
echo "RENDER_RESULT: OK"

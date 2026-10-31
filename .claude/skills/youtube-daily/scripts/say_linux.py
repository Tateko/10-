#!/usr/bin/env python3
# Linux 用の「say」の代わり（Masayume式 自動編集スターターキットの無料の声を、クラウドの Linux で動かすため）。
# Mac の say と同じ形で呼べる：  say -v '?'  ／  say -v Kyoko -r 290 -o out.aiff "文"
# 中身は OpenJTalk（pyopenjtalk-plus・オフライン・無料）。-o の拡張子に関係なく WAV で書く（ffmpeg が中身を見て読む）。
import sys
import warnings

warnings.filterwarnings("ignore")
args = sys.argv[1:]
voice, rate, out, text = "Kyoko", 175, None, []
i = 0
while i < len(args):
    a = args[i]
    if a == "-v" and i + 1 < len(args):
        voice = args[i + 1]; i += 2
    elif a == "-r" and i + 1 < len(args):
        rate = float(args[i + 1]); i += 2
    elif a == "-o" and i + 1 < len(args):
        out = args[i + 1]; i += 2
    else:
        text.append(a); i += 1

if voice == "?":
    print("Kyoko               ja_JP    # こんにちは、私の名前はKyokoです。（OpenJTalk）")
    sys.exit(0)

text = " ".join(text) or sys.stdin.read()
if not out:
    sys.exit("say（Linux）：-o で書き出し先を指定してください（再生はできません）")

import contextlib, io, wave
import numpy as np
with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
    import pyopenjtalk
    # Mac の -r（1分あたりの語数・ふだん175）を、OpenJTalk の速さ（1.0＝ふつう）に直す
    speed = min(max(rate / 220.0, 0.7), 1.8)
    x, sr = pyopenjtalk.tts(text, speed=speed)
pcm = np.clip(x, -32768, 32767).astype(np.int16)
with wave.open(out, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(pcm.tobytes())

"""PR動画のBGMを合成する（外部素材なし・権利関係なし）。
静かで紙っぽい映像に合わせて、ピアノ風のプラックとパッドだけで作る。
出力: build/bgm.wav (44.1kHz / stereo / 78秒)
"""
import math
import os
import wave
import numpy as np

SR = 44100
DUR = 78.0
OUT = os.path.join(os.environ.get("OUT_DIR", os.path.join(os.path.dirname(__file__), "build")), "bgm.wav")

n = int(SR * DUR)
t = np.arange(n) / SR
left = np.zeros(n)
right = np.zeros(n)


def note(name: str) -> float:
    """'A3' → 周波数。"""
    names = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6,
             "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
    pitch, octave = name[:-1], int(name[-1])
    midi = 12 * (octave + 1) + names[pitch]
    return 440.0 * 2 ** ((midi - 69) / 12)


def add(buf_l, buf_r, sig, start, pan=0.5):
    i0 = int(start * SR)
    i1 = min(n, i0 + len(sig))
    if i0 >= n:
        return
    s = sig[: i1 - i0]
    buf_l[i0:i1] += s * math.sqrt(1 - pan)
    buf_r[i0:i1] += s * math.sqrt(pan)


def pluck(freq, dur=2.6, amp=0.18):
    """減衰の速い倍音を重ねたピアノ／マリンバ寄りの音。"""
    k = np.arange(int(SR * dur)) / SR
    partials = [(1, 1.0, 3.2), (2, 0.38, 4.6), (3, 0.16, 6.0), (4.02, 0.07, 7.5)]
    sig = np.zeros(len(k))
    for mult, a, decay in partials:
        sig += a * np.sin(2 * np.pi * freq * mult * k) * np.exp(-decay * k)
    attack = np.clip(k / 0.006, 0, 1)
    return sig * attack * amp


def pad(freqs, dur, amp=0.05, attack=1.6, release=2.2):
    """三重にデチューンした持続音。和音の下敷き。"""
    k = np.arange(int(SR * dur)) / SR
    sig = np.zeros(len(k))
    for f in freqs:
        for det, a in ((0.997, 0.5), (1.0, 0.7), (1.003, 0.5)):
            drift = 1 + 0.0012 * np.sin(2 * np.pi * (0.07 + 0.03 * (f % 3)) * k)
            sig += a * np.sin(2 * np.pi * f * det * drift * k)
    env = np.clip(k / attack, 0, 1) * np.clip((dur - k) / release, 0, 1)
    return sig / (len(freqs) * 1.7) * env * amp


def swell(dur=1.6, amp=0.035):
    """場面が変わる直前の、息を吸うようなノイズ。"""
    k = np.arange(int(SR * dur)) / SR
    rng = np.random.default_rng(3)
    noise = rng.normal(0, 1, len(k))
    # 簡易ローパス（移動平均）で高域を落とす
    w = 90
    noise = np.convolve(noise, np.ones(w) / w, mode="same")
    env = (k / dur) ** 2.2 * np.clip((dur - k) / 0.35, 0, 1)
    return noise * env * amp


CHORDS = [
    # (開始秒, 長さ, 和音, 音量)
    (0.0, 7.4, ["A2", "A3", "C4", "E4"], 0.045),
    (6.2, 9.4, ["F2", "F3", "A3", "C4"], 0.050),
    (14.6, 7.0, ["C3", "G3", "C4", "E4"], 0.060),
    (21.0, 8.0, ["A2", "A3", "C4", "E4"], 0.046),
    (28.6, 8.0, ["F2", "F3", "A3", "C4"], 0.046),
    (36.2, 8.0, ["C3", "G3", "C4", "E4"], 0.046),
    (43.8, 8.0, ["G2", "G3", "B3", "D4"], 0.046),
    (51.4, 6.0, ["A2", "A3", "C4", "E4"], 0.046),
    (56.4, 6.0, ["F2", "F3", "A3", "C4"], 0.052),
    (61.4, 6.0, ["G2", "G3", "B3", "D4"], 0.052),
    (65.8, 8.0, ["C3", "G3", "C4", "E4"], 0.062),
    (72.0, 6.2, ["A2", "E3", "A3", "C4"], 0.058),
]
for start, dur, names, amp in CHORDS:
    add(left, right, pad([note(x) for x in names], dur, amp), start, 0.5)

# 上に乗るメロディ（Aマイナー・ペンタトニック）。場面ごとに密度を変える。
SCALE = ["A4", "C5", "D5", "E5", "G5", "A5"]
MELODY = [
    # (時刻, 音, 音量, 定位)
    (0.6, "A4", 0.13, 0.42), (2.6, "E5", 0.10, 0.58), (4.6, "C5", 0.09, 0.46),
    (6.4, "D5", 0.11, 0.55), (8.4, "C5", 0.10, 0.42), (10.4, "A4", 0.10, 0.58),
    (12.4, "G5", 0.08, 0.5), (13.6, "E5", 0.08, 0.44),
    (15.0, "C5", 0.15, 0.5), (16.6, "E5", 0.12, 0.56), (18.2, "G5", 0.11, 0.44),
    (19.8, "A5", 0.09, 0.52),
]
# デモ中は一定の間隔で軽く刻む（画面を見せる邪魔をしない音量）
demo_notes = ["A4", "C5", "E5", "D5", "C5", "E5", "G5", "E5", "A4", "C5", "D5", "E5",
              "C5", "A4", "E5", "G5", "A5", "E5", "C5", "D5", "E5", "C5"]
for i, nm in enumerate(demo_notes):
    ts = 21.4 + i * 1.5
    if ts > 53.6:
        break
    MELODY.append((ts, nm, 0.055 + 0.02 * ((i % 4) == 0), 0.40 + 0.2 * (i % 3) / 2))
# 3段の説明パート
for i, nm in enumerate(["C5", "E5", "G5", "A5", "G5", "E5", "D5", "C5"]):
    MELODY.append((54.4 + i * 1.45, nm, 0.075, 0.44 + 0.12 * (i % 2)))
# 締め
for ts, nm, amp in [(66.4, "C5", 0.14), (68.4, "E5", 0.12), (70.4, "A5", 0.11),
                    (72.6, "G5", 0.09), (74.6, "E5", 0.08), (76.2, "C5", 0.07)]:
    MELODY.append((ts, nm, amp, 0.5))

for ts, nm, amp, pan in MELODY:
    add(left, right, pluck(note(nm), 3.0, amp), ts, pan)

for ts in (13.6, 20.2, 53.2, 65.2):
    add(left, right, swell(1.5), ts - 1.5, 0.5)


def reverb(sig):
    """シュレーダー風の簡単な残響。長さは控えめ。"""
    out = sig.copy()
    for delay_ms, gain in ((37, 0.28), (53, 0.24), (71, 0.20), (97, 0.16), (131, 0.12)):
        d = int(SR * delay_ms / 1000)
        tail = np.zeros_like(sig)
        tail[d:] = sig[:-d] * gain
        out += tail
    return out


left = reverb(left)
right = reverb(right)

# 全体のフェード
fade_in = np.clip(t / 1.2, 0, 1)
fade_out = np.clip((DUR - t) / 3.0, 0, 1) ** 1.4
left *= fade_in * fade_out
right *= fade_in * fade_out

stereo = np.stack([left, right], axis=1)
peak = np.abs(stereo).max()
stereo = stereo / peak * 0.72  # −3dBFS くらい。映像の字幕を邪魔しない範囲。
pcm = (stereo * 32767).astype("<i2")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with wave.open(OUT, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"wrote {OUT} ({DUR:.0f}s, peak {peak:.3f})")

# 絵と図解が交互に出る動画を書き出す（絵＝暖色の1枚絵＋見出し、図解＝クリーム色の平たいスライド）。
# 字幕は下の紺の帯に焼き込み。動きはなく、切り替えは瞬時。
#
#   python render_story.py <scenes.json> <絵のフォルダ> <出力フォルダ> [--font フォント] [--brand Pep AI] [--only 番号,...]
#
# 絵のフォルダには <img番号>.jpg（または .png）を置く。無ければ暗い仮の背景になる。
import argparse
import base64
import json
import subprocess
import wave
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("scenes"); ap.add_argument("imgdir"); ap.add_argument("out")
ap.add_argument("--font", default=str(Path.home() / ".local/share/fonts/NotoSansJP-VariableFont_wght.ttf"))
ap.add_argument("--brand", default="Pep AI")
ap.add_argument("--series", default="海外の挑戦を、日付と数字で")
ap.add_argument("--speed", type=float, default=1.3)
ap.add_argument("--ffmpeg", default="ffmpeg")
ap.add_argument("--frames-only", action="store_true")
ap.add_argument("--bgm", help="うしろで小さく流す音（くり返す）。効果音ラボの環境音など")
ap.add_argument("--bgm-volume", type=float, default=0.10)
ap.add_argument("--chapter-sfx", help="章が変わるときに1回鳴らす短い音")
ap.add_argument("--title-sfx", help="動画の最初に1回鳴らす短い音")
a = ap.parse_args()

NAVY, CREAM, CARD, RED, GREEN, INK, GRAY = "#0D1C26", "#F6F2EB", "#FFFDF6", "#E35B36", "#2C6C49", "#0A0C0D", "#7d7a73"
scenes = json.load(open(a.scenes, encoding="utf-8"))
out = Path(a.out); (out / "frames").mkdir(parents=True, exist_ok=True); (out / "wav").mkdir(exist_ok=True); (out / "seg").mkdir(exist_ok=True)

CSS = f"""
@font-face {{ font-family: NJP; src: url("file://{a.font}"); font-weight: 100 900; }}
* {{ box-sizing:border-box; margin:0; }}
body {{ width:1920px; height:1080px; overflow:hidden; position:relative; font-family:NJP, sans-serif; color:{INK}; }}
.a {{ position:absolute; }}
.band {{ left:0; right:0; bottom:0; height:194px; background:{NAVY}; display:flex; align-items:center; justify-content:center; padding:0 160px; }}
.sub {{ color:#fff; font-size:54px; font-weight:800; line-height:1.35; text-align:center; text-wrap:balance; }}
.src {{ left:28px; bottom:204px; font-size:22px; color:#d7dde0; font-weight:600; background:rgba(13,28,38,.85); padding:3px 12px 5px; border-radius:5px; max-width:1300px; }}
"""


def img_uri(n):
    for ext in ("jpg", "png"):
        p = Path(a.imgdir) / f"{n}.{ext}"
        if p.exists():
            return f"data:image/{'jpeg' if ext == 'jpg' else 'png'};base64," + base64.b64encode(p.read_bytes()).decode()
    return None


def band(text, src):
    s = f"<div class='a src'>出典：{src}</div>" if src else ""
    return f"<div class='a band'><div class='sub'>{text}</div></div>{s}"


def scene_a(sc):
    uri = img_uri(sc["img"])
    bg = "background:radial-gradient(ellipse at 70% 40%, #6b4a2a, #120c08 70%)"
    year = (f"<div class='a' style='right:44px;top:40px;background:{RED};color:#fff;font-size:40px;font-weight:900;padding:6px 26px 12px;border-radius:6px'>{sc['year']}</div>"
            if sc.get("year") else "")
    h1, h2 = sc["head"]
    pic = f"<img class='a' src='{uri}' style='inset:0;width:1920px;height:1080px;object-fit:cover'>" if uri else ""
    return (f"<div class='a' style='inset:0;{bg}'></div>{pic}"
            f"<div class='a' style='inset:0;background:linear-gradient(90deg, rgba(5,14,20,.88) 0%, rgba(5,14,20,.7) 34%, rgba(5,14,20,0) 62%)'></div>"
            f"<div class='a' style='left:44px;top:40px;color:#fff;font-size:30px;font-weight:900;letter-spacing:1px'>{a.brand}"
            f"<span style='font-weight:700;color:#d7dde0;margin-left:22px;font-size:28px'>{sc['chapter']}</span></div>{year}"
            f"<div class='a' style='right:44px;bottom:212px;font-size:22px;font-weight:700;color:#e8e8e8;background:rgba(0,0,0,.45);padding:2px 12px 4px;border-radius:5px'>イメージ（AIで作成）</div>"
            f"<div class='a' style='left:110px;top:330px;width:70px;height:7px;background:{RED}'></div>"
            f"<div class='a' style='left:104px;top:360px;font-weight:900;line-height:1.25;font-size:{min(96, int(820 / max(len(h1), len(h2))))}px;"
            f"text-shadow:0 4px 18px rgba(0,0,0,.6)'><div style='color:#fff'>{h1}</div><div style='color:{RED}'>{h2}</div></div>")


def card(t, hi=False, w=480, fs=40):
    return (f"<div style='width:{w}px;min-height:190px;background:{CARD};border:{3 if hi else 1}px solid {RED if hi else '#d6cfc2'};border-radius:14px;"
            f"display:flex;align-items:center;justify-content:center;text-align:center;padding:24px;font-size:{fs}px;font-weight:800;color:{RED if hi else INK}'>{t}</div>")


def pict(color):
    return (f"<svg width='150' height='170' viewBox='0 0 150 170'><circle cx='75' cy='45' r='36' fill='{color}'/>"
            f"<rect x='25' y='90' width='100' height='80' rx='34' fill='{color}'/></svg>")


def scene_b(sc):
    k, items, hi = sc["kind"], sc.get("items", []), sc.get("hi", -1)
    if k in ("boxes", "steps"):
        n = len(items); w = 480 if n == 3 else 640
        arrow = f"<div style='font-size:60px;color:{GREEN};font-weight:900'>→</div>" if k == "steps" else "<div style='width:30px'></div>"
        body = arrow.join(card(t, i == hi, w, 40 if len(t) < 12 else 34) for i, t in enumerate(items))
        body = f"<div style='display:flex;align-items:center;justify-content:center;gap:26px'>{body}</div>"
    elif k == "icons":
        cols = [RED, GREEN, GREEN]
        body = "".join(f"<div style='display:flex;flex-direction:column;align-items:center;gap:22px;width:430px'>{pict(cols[i % 3])}"
                       f"<div style='font-size:40px;font-weight:800;text-align:center'>{t}</div></div>" for i, t in enumerate(items))
        body = f"<div style='display:flex;justify-content:center;gap:40px'>{body}</div>"
    elif k == "timeline":
        pts = "".join(f"<div style='display:flex;flex-direction:column;align-items:center;width:520px'>"
                      f"<div style='font-size:{56 if len(d) < 8 else 44}px;font-weight:900;color:{RED};height:80px'>{d}</div>"
                      f"<div style='width:30px;height:30px;border-radius:50%;background:{RED};margin:14px 0 30px'></div>"
                      f"<div style='background:{CARD};border:1px solid #d6cfc2;border-radius:12px;padding:22px 26px;font-size:36px;font-weight:800;text-align:center;min-height:120px;display:flex;align-items:center'>{t}</div></div>"
                      for d, t in items)
        body = (f"<div style='position:relative'><div class='a' style='left:120px;right:120px;top:108px;height:4px;background:{INK}'></div>"
                f"<div style='display:flex;justify-content:center;gap:20px;position:relative'>{pts}</div></div>")
    elif k == "compare":
        body = "".join(f"<div style='width:720px;border-radius:14px;overflow:hidden;border:1px solid #d6cfc2;background:{CARD}'>"
                       f"<div style='background:{NAVY};color:#fff;font-size:38px;font-weight:800;padding:16px 30px'>{h}</div>"
                       f"<div style='padding:44px 30px;font-size:{50 if len(v) < 12 else 42}px;font-weight:900;color:{RED if i == 1 else INK};text-align:center'>{v}</div></div>"
                       for i, (h, v) in enumerate(items))
        body = f"<div style='display:flex;justify-content:center;gap:60px'>{body}</div>"
    elif k == "table":
        rows = "".join(f"<tr><td style='padding:18px 34px;font-size:36px;font-weight:700;border-top:1px solid #d6cfc2;color:#3b3f42;white-space:nowrap'>{l}</td>"
                       f"<td style='padding:18px 34px;font-size:40px;font-weight:900;border-top:1px solid #d6cfc2;text-align:right'>{v}</td></tr>" for l, v in items)
        body = (f"<table style='margin:0 auto;width:1300px;border-collapse:collapse;background:{CARD};border:1px solid #d6cfc2;border-radius:14px'>"
                f"<tr style='background:{NAVY};color:#fff'><td style='padding:14px 34px;font-size:30px;font-weight:800'>項目</td>"
                f"<td style='padding:14px 34px;font-size:30px;font-weight:800;text-align:right'>数字</td></tr>{rows}</table>")
    elif k == "big":
        chips = "".join(f"<div style='border:2px solid {GREEN};color:{GREEN};font-size:36px;font-weight:800;padding:8px 30px;border-radius:40px'>{t}</div>" for t in items)
        body = (f"<div style='text-align:center'><div style='font-size:190px;font-weight:900;color:{RED};line-height:1'>{sc['big']}</div>"
                f"<div style='font-size:46px;font-weight:800;margin:14px 0 36px'>{sc.get('bigsub', '')}</div>"
                f"<div style='display:flex;gap:26px;justify-content:center'>{chips}</div></div>")
    elif k == "quote":
        body = (f"<div style='margin:0 auto;width:1400px;background:{CARD};border-left:12px solid {RED};border-radius:10px;padding:60px 70px'>"
                f"<div style='font-size:64px;font-weight:900;line-height:1.4'>{sc['big']}</div>"
                f"<div style='font-size:40px;font-weight:800;color:{RED};margin-top:26px'>{sc.get('bigsub', '')}</div></div>")
    else:  # end
        body = (f"<div style='text-align:center'><div style='font-size:76px;font-weight:900;margin-bottom:50px'>{sc['title']}</div>"
                f"<div style='display:inline-block;background:{RED};color:#fff;font-size:52px;font-weight:900;padding:22px 60px 30px;border-radius:14px'>{items[0]}</div></div>")
    head = "" if k == "end" else (f"<div class='a' style='left:90px;top:132px;font-size:62px;font-weight:900'>{sc['title']}</div>"
                                  f"<div class='a' style='left:92px;top:222px;font-size:32px;font-weight:600;color:{GRAY}'>{sc.get('sub', '')}</div>")
    note = (f"<div class='a' style='left:0;right:0;top:800px;text-align:center;font-size:32px;font-weight:600;color:{GRAY}'>{sc['note']}</div>"
            if sc.get("note") else "")
    return (f"<div class='a' style='inset:0;background:{CREAM}'></div>"
            f"<div class='a' style='left:0;right:0;top:0;height:92px;background:{NAVY};display:flex;align-items:center;justify-content:space-between;padding:0 44px'>"
            f"<div style='color:#fff;font-size:30px;font-weight:900'>{a.brand}<span style='font-weight:700;color:#cfd6da;margin-left:22px;font-size:28px'>{sc['chapter']}</span></div>"
            f"<div style='color:#9fb0bb;font-size:24px;font-weight:700'>{a.series}</div></div>"
            f"<div class='a' style='left:0;right:0;top:92px;height:5px;background:{RED}'></div>{head}"
            f"<div class='a' style='left:0;right:0;top:{330 if k != 'end' else 300}px;height:{460 if k != 'end' else 480}px;display:flex;align-items:center;justify-content:center'>{body}</div>{note}")


# 1. 画面（1文ごと）。字幕は帯の中で2行まで（1行約28字）。出典は帯の上に出して、字幕と重ならないようにする
for sc in scenes:
    for t in sc["lines"]:
        if len(t) > 56:
            print(f"⚠ 字幕が3行になるおそれ（{len(t)}字）：{t}")
from playwright.sync_api import sync_playwright
jobs = []
for si, sc in enumerate(scenes):
    base = scene_a(sc) if sc["type"] == "A" else scene_b(sc)
    for li, t in enumerate(sc["lines"]):
        jobs.append((out / "frames" / f"{si:03d}_{li}.png", f"<html><head><style>{CSS}</style></head><body>{base}{band(t, sc['source'])}</body></html>", t))
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    for f, html, _ in jobs:
        pg.set_content(html)
        pg.evaluate("document.fonts.ready")
        pg.evaluate("Promise.all(Array.from(document.images).map(i => i.decode()))")
        pg.wait_for_timeout(150)
        pg.screenshot(path=str(f))
    b.close()
print(f"✔ 画面 {len(jobs)}枚")
if a.frames_only:
    raise SystemExit

# 2. 声（OpenJTalk）と、1文ずつの動画
import numpy as np
import pyopenjtalk
segs = []
for i, (f, _, t) in enumerate(jobs):
    w = out / "wav" / f"{i:03d}.wav"
    x, sr = pyopenjtalk.tts(t, speed=a.speed)
    pcm = np.clip(x, -32768, 32767).astype(np.int16)
    pad = np.zeros(int(sr * 0.28), dtype=np.int16)
    pcm = np.concatenate([pad[: int(sr * 0.08)], pcm, pad])
    with wave.open(str(w), "wb") as ww:
        ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(sr); ww.writeframes(pcm.tobytes())
    dur = len(pcm) / sr
    s = out / "seg" / f"{i:03d}.mp4"
    subprocess.run([a.ffmpeg, "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-i", str(f), "-i", str(w), "-t", f"{dur:.3f}",
                    "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    str(s)], check=True)
    segs.append((s, dur))
(out / "list.txt").write_text("".join(f"file '{s.resolve()}'\n" for s, _ in segs))
subprocess.run([a.ffmpeg, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(out / "list.txt"), "-c", "copy", str(out / "_cat.mp4")], check=True)
# チャプター（章の最初の場面の時刻）
t, chs, last = 0.0, [], None
k = 0
for sc in scenes:
    if sc["chapter"] != last:
        chs.append((t, sc["chapter"])); last = sc["chapter"]
    for _ in sc["lines"]:
        t += segs[k][1]; k += 1
# 声に、うしろの音と章の合図を重ねる
ins, fil, mix = ["-i", str(out / "_cat.mp4")], [], ["[0:a]"]
n = 1
if a.bgm:
    ins += ["-stream_loop", "-1", "-i", a.bgm]
    fil.append(f"[{n}:a]atrim=0:{t:.2f},afade=t=in:d=2,afade=t=out:st={max(0, t - 3):.2f}:d=3,volume={a.bgm_volume}[b{n}]"); mix.append(f"[b{n}]"); n += 1
cues = ([(0.0, a.title_sfx)] if a.title_sfx else []) + ([(s0, a.chapter_sfx) for s0, _ in chs[1:]] if a.chapter_sfx else [])
for s0, f in cues:
    ins += ["-i", f]
    fil.append(f"[{n}:a]adelay={int(s0 * 1000)}|{int(s0 * 1000)},volume=0.5[c{n}]"); mix.append(f"[c{n}]"); n += 1
fc = ";".join(fil + [f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]"])
subprocess.run([a.ffmpeg, "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-ar", "48000",
                "-c:a", "aac", "-b:a", "192k", str(out / "final.mp4")], check=True)
(out / "chapters.txt").write_text("".join(f"{int(s // 60)}:{int(s % 60):02d} {c}\n" for s, c in chs))
print(f"✔ final.mp4 {int(t // 60)}分{int(t % 60)}秒")

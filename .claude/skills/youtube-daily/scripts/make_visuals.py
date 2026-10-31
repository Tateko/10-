# 図（PNG・images/）と動くイラスト（MP4・clips/）を、visuals.json の指示から作る。
#
#   python make_visuals.py <動画のフォルダ> [名前 ...]    # 名前を書くと、その物だけ作り直す
#
# visuals.json の形：{"items": [{"name": "G01_months", "type": "bars", ...}, ...]}
# 図（静止画）の type：bars・split・stamp・list
# 動き（動画）の type：anim_bars・anim_line・anim_calendar・anim_stack・anim_dots・anim_split・anim_cards・
#                      anim_question・anim_walkout・anim_consult
# どの数字・文字も、事実メモと台本にある物だけを書く。人は顔のない影絵で、"イメージ" の札が付く。
import json
import sys
from pathlib import Path

from common import G, GR, MID, R, INK, base_css, person, record, shoot

proj = Path(sys.argv[1])
only = set(sys.argv[2:])
items = json.load(open(proj / "visuals.json", encoding="utf-8"))["items"]


def page(body, z=1.3):
    return (f"<html><head><style>{base_css(1600, 740, 40)}</style></head><body><div class='c'>"
            f"<div style='zoom:{z};display:flex;flex-direction:column;align-items:center;gap:30px'>{body}</div></div></body></html>")


def fmt(v):
    return f"{v:,}" if isinstance(v, (int, float)) else str(v)


# ---------------------------------------------------------------- 図（静止画 1600×740）
def st_bars(it):
    vals, labels, hi = it["values"], it.get("labels") or [f"{i+1}" for i in range(len(it["values"]))], set(it.get("red", []))
    mx = max(vals)
    bars = ''.join(
        f"<div style='display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:10px;height:560px'>"
        f"<div style='font-size:26px;font-weight:800;color:{R if i in hi else '#fff'}'>{fmt(v)}</div>"
        f"<div style='width:{min(110, 1100 // len(vals))}px;height:{max(8, int(470 * v / mx))}px;border-radius:8px;background:{R if i in hi else G}'></div>"
        f"<div class='sub' style='font-size:24px'>{labels[i]}</div></div>" for i, v in enumerate(vals))
    return page(f"<div class='h'>{it['title']}</div><div style='display:flex;align-items:flex-end;gap:30px'>{bars}</div>", 1.0)


def st_split(it):
    p = it["percent"]
    return page(f"<div class='h'>{it['title']}</div><div style='width:1000px;height:110px;display:flex;border-radius:16px;overflow:hidden'>"
                f"<div style='width:{p}%;background:{G};color:#141810;display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:900'>{it['left']}</div>"
                f"<div style='width:{100-p}%;background:#3a403a;display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:700'>{it['right']}</div></div>"
                f"<div class='sub'>{it.get('note', '')}</div>")


def st_stamp(it):
    # 長い文字でも枠からはみ出さないよう、字数で大きさを決める（1行・幅は約1000px まで）
    fs = min(150, int(1000 / max(1, len(it["text"]))))
    return page(f"<div style='border:9px solid {R};color:{R};font-weight:900;font-size:{fs}px;white-space:nowrap;padding:10px 60px 24px;border-radius:16px;transform:rotate(-6deg)'>{it['text']}</div>"
                f"<div class='sub' style='font-size:38px'>{it.get('sub', '')}</div>", 1.0)


def st_list(it):
    rows = ''.join(f"<div style='display:flex;justify-content:space-between;width:820px;font-size:52px;padding:14px 0;border-bottom:2px solid #2a3026'>"
                   f"<span class='sub' style='font-size:40px'>{a}</span><span style='font-weight:800;{('color:' + G) if i == len(it['rows']) - 1 else ''}'>{b}</span></div>"
                   for i, (a, b) in enumerate(it["rows"]))
    return page(f"<div style='padding:40px 70px;border:2px solid #3a403a;border-radius:18px'><div class='sub' style='margin-bottom:16px'>{it['title']}</div>{rows}</div>", 1.1)


# ---------------------------------------------------------------- 動き（1920×1080 の MP4）
def css(extra=""):
    return f"<style>{base_css(1920, 1080)}{extra}</style>"


def an_bars(it):
    vals, labels, hi = it["values"], it.get("labels") or [f"{i+1}" for i in range(len(it["values"]))], set(it.get("red", []))
    mx, n = max(vals), len(vals)
    step = min(210, 1300 // n)
    bw, left = int(step * .72), (1920 - step * n) // 2
    bars = ''.join(
        f"<div class='a' style='left:{left+i*step}px;bottom:230px;width:{bw}px;display:flex;flex-direction:column;align-items:center;gap:12px'>"
        f"<div class='lbl' style='font-size:34px;color:{R if i in hi else '#fff'};animation: fade .4s {0.5+i*0.8+0.5}s both'>{fmt(v)}</div>"
        f"<div style='width:{bw}px;height:{max(14,int(520*v/mx))}px;border-radius:10px;background:{R if i in hi else G};transform-origin:bottom;"
        f"animation: grow .6s {0.5+i*0.8}s both{', shake .5s ' + str(round(1.2+n*0.8,1)) + 's 2' if i in hi else ''}'></div></div>"
        f"<div class='a' style='left:{left+i*step}px;bottom:180px;width:{bw}px;text-align:center;font-size:30px;color:#9aa09a;font-weight:700'>{labels[i]}</div>"
        for i, v in enumerate(vals))
    return css("@keyframes grow { from { transform:scaleY(0) } to { transform:scaleY(1) } } "
               "@keyframes shake { 0%,100% { transform:translateX(0) } 25% { transform:translateX(-12px) } 75% { transform:translateX(12px) } }") + \
        f"{bars}<div class='a' style='left:{left-40}px;width:{step*n+40}px;bottom:226px;height:4px;background:{GR}'></div>" \
        f"<div class='a lbl' style='left:0;right:0;top:110px;text-align:center;font-size:50px'>{it['title']}</div>"


def an_line(it):
    return css(".ln { stroke-dasharray:1400; stroke-dashoffset:1400; animation: draw 2s .4s forwards; } @keyframes draw { to { stroke-dashoffset:0 } }") + \
        f"<svg class='a' style='left:0;top:0' width='1920' height='1080'><polyline class='ln' points='360,760 760,740 1160,700 1560,330' fill='none' stroke='{G if it.get('up', True) else R}' stroke-width='18' stroke-linecap='round' stroke-linejoin='round'/></svg>" \
        f"<div class='a lbl' style='left:1080px;top:720px;font-size:70px;color:#c8ccc8;animation: fade .5s .8s both'>{it['from']}</div>" \
        f"<div class='a lbl' style='left:1380px;top:200px;font-size:110px;color:{G};animation: pop .7s 2.4s both'>{it['to']}</div>"


def an_calendar(it):
    days, pct = it["days"], it["percent"]
    return css(f".fill {{ animation: fill 5.5s .5s both cubic-bezier(.2,.7,.3,1); }} @keyframes fill {{ from {{ width:0 }} to {{ width:{pct}% }} }}") + \
        f"<div class='a' style='left:760px;top:140px;width:400px;height:330px;border-radius:20px;background:#1e251b;border:4px solid {GR};overflow:hidden'>" \
        f"<div style='height:80px;background:{R}'></div><div id='day' style='text-align:center;font-size:150px;font-weight:900;line-height:220px'>1</div></div>" \
        f"<div class='a lbl' style='left:1180px;top:350px;font-size:60px'>日目</div>" \
        f"<div class='a' style='left:360px;top:620px;width:1200px;height:90px;border-radius:45px;background:{MID};overflow:hidden'><div class='fill' style='height:100%;background:{G}'></div></div>" \
        f"<div class='a lbl' style='left:1260px;top:730px;font-size:44px;color:#c8ccc8'>{it.get('goal', '')}</div>" \
        f"<div class='a lbl' style='left:360px;top:730px;font-size:44px;color:{G};animation: fade .6s 5.5s both'>{it.get('result', '')}</div>" \
        f"<script>window.__tick=(ms)=>{{document.getElementById('day').textContent=Math.min({days},1+Math.floor(ms/5800*{days-1}));}}</script>"


def an_stack(it):
    blocks = ''.join(f"<div class='a' style='left:810px;top:{780-i*90}px;width:300px;height:80px;border-radius:10px;background:{G if i != 3 else R};"
                     f"{'animation: pull 1s 1s both;' if i == 3 else ('animation: drop .5s 1.9s both;' if i > 3 else '')}'></div>" for i in range(7))
    return css("@keyframes pull { to { transform:translateX(560px) rotate(12deg); opacity:.3 } } @keyframes drop { to { transform:translateY(90px) } }") + \
        f"<div class='a' style='left:780px;top:860px;width:360px;height:14px;background:{MID}'></div>{blocks}" \
        f"<div class='a lbl' style='left:1360px;top:420px;font-size:46px;color:{R};animation: fade .6s 1.4s both'>{it['pulled']}</div>" \
        f"<div class='a lbl' style='left:300px;top:300px;font-size:120px;animation: fade .5s .2s both'>{it['before']}</div>" \
        f"<div class='a lbl' style='left:300px;top:460px;font-size:120px;color:{R};animation: fade .5s 2.6s both'>→ {it['after']}</div>"


def an_dots(it):
    n = 380
    dots = ''.join(f"<div class='a' style='left:{300+(i%38)*34}px;top:{240+(i//38)*34}px;width:22px;height:22px;border-radius:50%;background:{G};animation: pop .3s {0.8+i*0.012:.3f}s both'></div>" for i in range(n))
    extra = ''.join(f"<div class='a lbl' style='left:300px;top:{660+k*120}px;font-size:52px;animation: fade .5s {7.2+k*3.3}s both'>{t}</div>" for k, t in enumerate(it.get("then", [])))
    a, b = it["from"], it["to"]
    return css() + f"<div class='a lbl' style='left:300px;top:130px;font-size:56px'>{it['label']} <span id='n' style='color:{G}'>{a:,}</span> {it.get('unit', '')}</div>{dots}{extra}" \
        f"<script>window.__tick=(ms)=>{{const t=Math.max(0,Math.min(1,(ms-800)/5000));document.getElementById('n').textContent=(t>=1?'{it.get('to_text', f'{b:,}')}':Math.round({a}+{b-a}*t).toLocaleString());}}</script>"


def an_split(it):
    p = it["percent"]
    rest = ''.join(f"<div class='a' style='left:1020px;top:{590+k*140}px;width:300px;height:100px;border-radius:16px;background:#1e251b;border:3px solid {GR};"
                   f"display:flex;align-items:center;justify-content:center;font-size:44px;font-weight:800;animation: pop .6s {5.0+k*0.6}s both'>{t}</div>" for k, t in enumerate(it.get("right_items", [])))
    circle = (f"<div class='a' style='left:620px;top:600px;width:220px;height:220px;border-radius:50%;background:#1e251b;border:5px solid {G};display:flex;align-items:center;"
              f"justify-content:center;font-size:48px;font-weight:900;animation: pop .7s 3.6s both'>{it['circle']}</div>"
              f"<div class='a lbl' style='left:880px;top:660px;font-size:90px;color:{G};animation: fade .5s 4.6s both'>→</div>") if it.get("circle") else ""
    return css(f".f {{ animation: fill 2s .4s both; }} @keyframes fill {{ from {{ width:0 }} to {{ width:{p}% }} }}") + \
        f"<div class='a lbl' style='left:0;right:0;top:170px;text-align:center;font-size:60px'>{it['title']}</div>" \
        f"<div class='a' style='left:310px;top:300px;width:1300px;height:150px;border-radius:24px;background:{MID};overflow:hidden'>" \
        f"<div class='f' style='height:100%;background:{G};display:flex;align-items:center;justify-content:center;color:#141810;font-size:64px;font-weight:900'>{it['left']}</div></div>{circle}{rest}"


def an_cards(it):
    texts = it["texts"][:4]
    xs, ys = (-560, -180, 200, 560), (-420, -470, -480, -400)
    fly = ''.join(f"@keyframes fly{i} {{ 0% {{ transform:translate(0,0) scale(.4); opacity:0 }} 20% {{ opacity:1 }} 100% {{ transform:translate({xs[i]}px,{ys[i]}px) scale(1); opacity:1 }} }}" for i in range(len(texts)))
    cards = ''.join(f"<div class='a' style='left:880px;top:560px;width:240px;height:150px;border-radius:14px;background:#1e251b;border:3px solid {G};"
                    f"display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:900;animation: fly{i} 2.4s {i*1.4}s both'>{t}</div>" for i, t in enumerate(texts))
    return css(fly) + f"<div class='a' style='left:620px;top:820px;width:680px;height:22px;border-radius:10px;background:{MID}'></div>" \
        f"<div class='a' style='left:780px;top:560px;width:440px;height:270px;border-radius:12px;background:{INK};border:12px solid #1c2219'></div>" \
        f"<div class='a' style='left:800px;top:580px;width:400px;height:230px;background:{G};opacity:.25'></div>{cards}" \
        f"<div class='a' style='left:0;right:0;top:880px;text-align:center;font-size:44px;font-weight:800;color:#c8ccc8;animation: fade 1s 5.5s both'>{it.get('caption', '')}</div>"


def an_question(it):
    return css(f".q {{ animation: pop 1.2s .6s both, glow 2s 1.8s infinite alternate; }} @keyframes glow {{ from {{ text-shadow:0 0 10px {G} }} to {{ text-shadow:0 0 60px {G} }} }}") + \
        f"<div class='a' style='left:560px;top:300px;width:800px;height:800px;border-radius:50%;background:radial-gradient(circle, rgba(168,224,74,.25), rgba(0,0,0,0) 60%)'></div>" \
        f"<div class='a' style='left:420px;top:760px;width:1080px;height:22px;border-radius:10px;background:{MID}'></div>" \
        f"<div class='a' style='left:820px;top:560px;width:300px;height:200px;border-radius:10px;background:{INK};border:10px solid #1c2219'></div>" \
        f"<div class='a' style='left:840px;top:578px;width:260px;height:160px;background:{G};opacity:.35'></div>{person(640, 430, 1.0)}" \
        f"<div class='a q' style='left:860px;top:150px;font-size:300px;font-weight:900;color:{G}'>{it.get('mark', '?')}</div><div class='tag'>イメージ</div>"


def an_walkout(it):
    win = ''.join(f"<div class='a' style='left:{300+c*110}px;top:{200+r*95}px;width:80px;height:60px;border-radius:6px;background:{G if (r*7+c)%5==0 else '#2f3a2a'};opacity:{.9 if (r*7+c)%5==0 else .6}'></div>" for r in range(5) for c in range(7))
    return css(".walk { animation: walk 8s linear both; } @keyframes walk { from { transform:translateX(0) } to { transform:translateX(620px) } } "
               ".legA { animation: sw .5s infinite alternate; transform-origin: 64px 226px; } .legB { animation: sw .5s infinite alternate-reverse; transform-origin: 98px 226px; } "
               "@keyframes sw { from { transform:rotate(-14deg) } to { transform:rotate(14deg) } }") + \
        f"<div class='a' style='left:260px;top:160px;width:820px;height:700px;background:#1f2a1c'></div>{win}" \
        f"<div class='a' style='left:600px;top:690px;width:140px;height:170px;background:{G};opacity:.85'></div>" \
        f"<div class='a' style='left:0;top:860px;width:1920px;height:220px;background:#0b0e09'></div>" \
        f"<div class='a walk' style='left:680px;top:500px;width:260px;height:380px'>{person(0, 0, 1.0)}" \
        f"<div class='a' style='left:90px;top:120px;width:110px;height:80px;border-radius:6px;background:#c8a46a'></div></div><div class='tag'>イメージ</div>"


def an_consult(it):
    return css(".b1 { animation: pop .8s .3s both; } .b2 { animation: pop .8s 1.5s both; } .b3 { animation: pop .8s 2.7s both; }") + \
        f"<div class='a' style='left:520px;top:700px;width:880px;height:24px;border-radius:10px;background:{MID}'></div>" \
        f"<div class='a' style='left:820px;top:640px;width:280px;height:60px;border-radius:8px;background:#e8eadf;opacity:.85'></div>" \
        f"{person(470, 400, 0.95)}{person(1300, 400, 0.95)}" \
        f"<div class='a b1' style='left:600px;top:230px;width:260px;height:120px;border-radius:30px;background:{G}'></div>" \
        f"<div class='a b2' style='left:1080px;top:200px;width:260px;height:120px;border-radius:30px;background:#c8ccc8'></div>" \
        f"<div class='a b3' style='left:640px;top:390px;width:200px;height:90px;border-radius:26px;background:{G};opacity:.8'></div>" \
        f"<div class='a lbl' style='left:0;right:0;top:860px;text-align:center;font-size:48px;color:#c8ccc8;animation: fade 1s 3s both'>{it.get('caption', '')}</div><div class='tag'>イメージ</div>"


STILL = {"bars": st_bars, "split": st_split, "stamp": st_stamp, "list": st_list}
ANIM = {"anim_bars": an_bars, "anim_line": an_line, "anim_calendar": an_calendar, "anim_stack": an_stack, "anim_dots": an_dots,
        "anim_split": an_split, "anim_cards": an_cards, "anim_question": an_question, "anim_walkout": an_walkout, "anim_consult": an_consult}

(proj / "images").mkdir(exist_ok=True)
(proj / "clips").mkdir(exist_ok=True)
stills, clips = [], []
for it in items:
    if only and it["name"] not in only:
        continue
    if it["type"] in STILL:
        stills.append((proj / "images" / f"{it['name']}.png", STILL[it["type"]](it)))
    elif it["type"] in ANIM:
        clips.append((proj / "clips" / f"{it['name']}.mp4", it.get("seconds", 6), ANIM[it["type"]](it)))
    else:
        sys.exit(f"✖ 知らない type：{it['type']}")
if stills:
    shoot(stills, 1600, 740)
    print(f"✔ 図 {len(stills)}枚 → images/")
if clips:
    record(clips)

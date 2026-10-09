// ホーム画面プロトタイプのPR動画を収録するスクリプト。
//
//   npm i playwright ffmpeg-static
//   node record-promo.mjs [収録するURL]     # 既定: 同じフォルダの home-prototype.html
//
// 出力は vid/*.webm。mp4 にするには:
//   ffmpeg -i vid/*.webm -vf fps=30 -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart promo.mp4
//
// 注意:
// - executablePath は環境のChromiumのパスに合わせて変えてください
// - Google Fonts に到達できない環境向けに、字形を埋め込んだ fonts-local.css を読ませています。
//   ネットワークから読める環境なら 2つの route() と addStyleTag() は消して構いません
// - キャプションと操作手順はこのプロトタイプ専用です。別のサイトを撮るときは書き換えてください

import { chromium } from 'playwright';

const W = 1600, H = 900;
const URL = process.argv[2] || 'file://' + process.cwd() + '/home-prototype.html';

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const ctx = await browser.newContext({
  viewport: { width: W, height: H },
  deviceScaleFactor: 1,
  recordVideo: { dir: 'vid', size: { width: W, height: H } }
});
const page = await ctx.newPage();
await page.route('**://fonts.googleapis.com/**', r => r.abort());
await page.route('**://fonts.gstatic.com/**', r => r.abort());
await page.goto(URL);
await page.addStyleTag({ path: 'fonts-local.css' });

// ---- 収録用のオーバーレイ（カーソル・キャプション・カード）をページに差し込む ----
await page.evaluate(() => {
  const css = document.createElement('style');
  css.textContent = `
    #pCursor {
      position: fixed; left: 0; top: 0; z-index: 99998;
      width: 26px; height: 26px; margin: -13px 0 0 -13px;
      border-radius: 50%;
      background: rgba(255,255,255,.55);
      border: 2px solid rgba(18,21,28,.55);
      box-shadow: 0 4px 14px rgba(18,21,28,.30);
      pointer-events: none;
      transform: translate(820px, 460px);
      transition: transform .85s cubic-bezier(.4,0,.2,1);
    }
    #pCursor::after {
      content: ""; position: absolute; inset: 8px;
      border-radius: 50%; background: rgba(18,21,28,.7);
    }
    .pRipple {
      position: fixed; z-index: 99997;
      width: 22px; height: 22px; margin: -11px 0 0 -11px;
      border-radius: 50%; border: 2px solid rgba(18,21,28,.5);
      pointer-events: none; animation: pRip .65s ease-out forwards;
    }
    @keyframes pRip { to { transform: scale(3.4); opacity: 0; } }
    #pCap {
      position: fixed; left: 50%; bottom: 46px; z-index: 99998;
      transform: translate(-50%, 16px);
      background: rgba(16,19,25,.90);
      -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px);
      color: #fff; font-family: "Zen Kaku Gothic New", sans-serif;
      font-size: 21px; font-weight: 500; letter-spacing: .02em;
      padding: 14px 30px; border-radius: 999px;
      opacity: 0; transition: opacity .45s ease, transform .45s ease;
      white-space: nowrap; pointer-events: none;
      box-shadow: 0 18px 40px -22px rgba(0,0,0,.7);
    }
    #pCap.on { opacity: 1; transform: translate(-50%, 0); }
    #pCard {
      position: fixed; inset: 0; z-index: 99999;
      display: grid; place-content: center; justify-items: center; gap: 18px;
      background: #F0F2F7;
      background-image:
        radial-gradient(120% 80% at 18% -10%, #FFE1B8AA, transparent 62%),
        radial-gradient(90% 70% at 88% 8%, #D7C4FFAA, transparent 64%);
      opacity: 1; transition: opacity .8s ease; text-align: center;
    }
    #pCard.off { opacity: 0; pointer-events: none; }
    #pCard .k {
      font-family: "DM Mono", monospace; font-size: 14px; letter-spacing: .22em;
      text-transform: uppercase; color: #5D6577;
    }
    #pCard .n {
      font-family: "Zen Old Mincho", serif; font-weight: 600;
      font-size: 76px; letter-spacing: .04em; color: #12151C; line-height: 1.1;
    }
    #pCard .s {
      font-family: "Zen Kaku Gothic New", sans-serif; font-size: 21px; color: #4A5265;
      line-height: 1.9; max-width: 30ch;
    }
  `;
  document.head.append(css);

  const cur = document.createElement('div'); cur.id = 'pCursor';
  const cap = document.createElement('div'); cap.id = 'pCap';
  const card = document.createElement('div'); card.id = 'pCard';
  document.body.append(cur, cap, card);

  window.__card = (kicker, name, sub) => {
    card.innerHTML = '';
    if (kicker) { const e = document.createElement('div'); e.className = 'k'; e.textContent = kicker; card.append(e); }
    if (name)   { const e = document.createElement('div'); e.className = 'n'; e.textContent = name; card.append(e); }
    if (sub)    { const e = document.createElement('div'); e.className = 's'; e.textContent = sub; card.append(e); }
    card.classList.remove('off');
  };
  window.__cardOut = () => card.classList.add('off');
  window.__cap = t => { cap.textContent = t; cap.classList.add('on'); };
  window.__capOut = () => cap.classList.remove('on');
  window.__move = sel => {
    const r = document.querySelector(sel).getBoundingClientRect();
    cur.style.transform = `translate(${r.left + r.width / 2}px, ${r.top + r.height / 2}px)`;
  };
  window.__ripple = () => {
    const m = /translate\(([-\d.]+)px,\s*([-\d.]+)px\)/.exec(cur.style.transform);
    if (!m) return;
    const d = document.createElement('div');
    d.className = 'pRipple';
    d.style.left = m[1] + 'px';
    d.style.top = m[2] + 'px';
    document.body.append(d);
    setTimeout(() => d.remove(), 700);
  };
});

const wait = ms => page.waitForTimeout(ms);
const cap = t => page.evaluate(t => window.__cap(t), t);
const capOut = () => page.evaluate(() => window.__capOut());

// セレクタへカーソルを動かして、実際にクリックする
async function tap(sel, settle = 1100) {
  await page.evaluate(s => window.__move(s), sel);
  await wait(760);
  await page.evaluate(() => window.__ripple());
  await page.click(sel);
  await wait(settle);
}

// ---- 準備（カードで隠したまま） ----
await page.evaluate(() => document.fonts.ready);
await page.evaluate(() => window.__card('未知の体験提案アプリ（仮称）', 'あさ、ひとつ', ''));
await page.evaluate(() => document.querySelector('.phone').scrollIntoView({ block: 'center' }));
await wait(1200);

// ---- 1. タイトル ----
await wait(1800);
await page.evaluate(() => window.__cardOut());
await wait(700);

// ---- 2. つかみ ----
await cap('毎朝7時。自分では選ばない体験が、ひとつ届く。');
await wait(2400);
await capOut(); await wait(400);

// ---- 3. 表紙をかえる ----
await cap('表紙は、ひとりひとりが自分で選ぶ。');
await tap('#openPicker', 1100);
await wait(600);

// ---- 4. 色を選ぶ ----
await capOut(); await wait(300);
await cap('選んだ色は、画面ぜんぶに広がる。');
await tap('#swatches .swatch:nth-child(2)', 1500);
await tap('#swatches .swatch:nth-child(5)', 1600);
await capOut(); await wait(300);
await tap('#closePicker', 900);

// ---- 5. 同行者 ----
await cap('この提案は、ほかに2人に届いている。');
await wait(1900);
await capOut(); await wait(300);
await cap('「行く」を押すと、時刻と場所だけが届く。');
await tap('.act-go', 1600);
await capOut(); await wait(300);
await cap('相手が誰かは出ない。目印は、表紙の色。');
await wait(2500);
await capOut(); await wait(400);

// ---- 6. ひとりひとり別の画面 ----
await cap('ひとりひとりが、別の表紙と別の提案を持つ。');
await tap('#members .member:nth-child(3)', 2300);
await capOut(); await wait(500);

// ---- 7. 締め ----
await page.evaluate(() => window.__card('', '名前より先に、色で人を認識する。', ''));
await wait(2500);
await page.evaluate(() => window.__card('未知の体験提案アプリ（仮称）', 'あさ、ひとつ', '毎朝7時、ひとつだけ。'));
await wait(2500);

await ctx.close();
await browser.close();
console.log('recorded');

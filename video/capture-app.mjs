// 実際に動いている michi を Playwright で操作して、1フレームずつ PNG に落とす。
// 出力: <out>/app/f00000.png ... と manifest.json（画面ごとのフレーム番号＝字幕の同期に使う）
import { chromium } from 'playwright';
import { mkdir, writeFile, rm } from 'node:fs/promises';
import path from 'node:path';

const BASE = process.env.BASE_URL || 'http://localhost:3000';
const OUT = path.resolve(process.env.OUT_DIR || 'build', 'app');

const today = new Date();
const ymd = (d) => `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`;
const daysAgo = (n) => { const d = new Date(today); d.setDate(d.getDate() - n); return ymd(d); };

// 端末に入っている「使い込まれた状態」を先に作る。空のアプリは PR にならない。
const SEED = {
  'michi:settings': {
    name: 'たて',
    recent: '休みはだいたい家で動画。出るときは決まったカフェ。人と会うのは月1くらい。',
    budget: '〜3,000円',
  },
  'michi:friends': [
    { name: '同期のA', lastMet: daysAgo(21), today: true },
    { name: '大学の友人B', lastMet: daysAgo(8), today: false },
    { name: '前職のC', lastMet: daysAgo(34), today: false },
    { name: '近所のD', lastMet: daysAgo(3), today: false },
    { name: 'ジムで会うE', lastMet: daysAgo(12), today: false },
    { name: '実家の兄', lastMet: daysAgo(60), today: false },
    { name: '前の上司', lastMet: daysAgo(90), today: false },
    { name: 'バイト先のG', lastMet: null, today: false },
    { name: '本屋で話したH', lastMet: null, today: false },
  ],
  'michi:history': [
    { date: daysAgo(1), title: '一駅前で降りて歩いて帰る', status: 'done', minutes: 35, companion: null, note: '', photo: null },
    { date: daysAgo(2), title: '入ったことない定食屋で日替わり', status: 'done', minutes: 50, companion: '近所のD', note: '', photo: null },
  ],
};

let n = 0;
const markers = {};
const mark = (name) => { markers[name] = n; };

async function main() {
  await rm(OUT, { recursive: true, force: true });
  await mkdir(OUT, { recursive: true });

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 2,
    locale: 'ja-JP',
    permissions: ['clipboard-read', 'clipboard-write'],
    reducedMotion: 'no-preference',
  });
  await context.addInitScript((seed) => {
    for (const [k, v] of Object.entries(seed)) localStorage.setItem(k, JSON.stringify(v));
  }, SEED);

  const page = await context.newPage();
  page.on('dialog', (d) => d.dismiss().catch(() => {}));
  // カーソル代わりの丸。押した場所が見えないと、動画では何が起きたか伝わらない。
  await page.addInitScript(() => {
    window.__cursor = (x, y, down) => {
      let el = document.getElementById('__cur');
      if (!el) {
        el = document.createElement('div');
        el.id = '__cur';
        el.style.cssText = 'position:fixed;z-index:9999;width:26px;height:26px;margin:-13px 0 0 -13px;' +
          'border-radius:50%;background:rgba(31,61,43,.18);border:1.5px solid rgba(31,61,43,.55);' +
          'pointer-events:none;transition:transform .12s ease,opacity .2s;opacity:0';
        document.body.appendChild(el);
      }
      el.style.left = x + 'px';
      el.style.top = y + 'px';
      el.style.opacity = '1';
      el.style.transform = down ? 'scale(.72)' : 'scale(1)';
    };
    window.__cursorHide = () => { const el = document.getElementById('__cur'); if (el) el.style.opacity = '0'; };
  });

  const shot = async () => {
    await page.screenshot({ path: path.join(OUT, `f${String(n).padStart(5, '0')}.png`) });
    n++;
  };
  const hold = async (frames, waitMs = 0) => {
    for (let i = 0; i < frames; i++) { if (waitMs) await page.waitForTimeout(waitMs); await shot(); }
  };
  const moveTo = async (sel, dy = 0) => {
    const target = page.locator(sel).first();
    await target.waitFor({ state: 'visible', timeout: 5000 });
    await target.scrollIntoViewIfNeeded();
    const box = await target.boundingBox();
    if (!box) throw new Error(`要素が見つからない: ${sel}`);
    const x = box.x + box.width / 2, y = box.y + box.height / 2 + dy;
    await page.evaluate(([x, y]) => window.__cursor(x, y, false), [x, y]);
    await page.mouse.move(x, y);
    return { x, y };
  };
  const tap = async (sel, { pre = 3, post = 6 } = {}) => {
    const { x, y } = await moveTo(sel);
    await hold(pre);
    await page.evaluate(([x, y]) => window.__cursor(x, y, true), [x, y]);
    await shot();
    await page.mouse.click(x, y);
    await page.evaluate(([x, y]) => window.__cursor(x, y, false), [x, y]);
    await hold(post);
  };

  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);

  // 1. ホーム（入力前）
  mark('home');
  await hold(16);

  // 2. エリアを打つ
  await moveTo('input[name=area]');
  await hold(3);
  await page.click('input[name=area]');
  mark('type');
  for (const ch of '渋谷') { await page.type('input[name=area]', ch, { delay: 0 }); await hold(4); }
  await hold(6);

  // 3. 気分を選ぶ
  await moveTo('select[name=mood]');
  await hold(4);
  await page.selectOption('select[name=mood]', '何か刺激がほしい');
  mark('mood');
  await hold(10);
  await page.evaluate(() => window.__cursorHide());

  // 4. 生成
  await tap('#go', { pre: 4, post: 0 });
  await page.evaluate(() => window.__cursorHide());
  mark('loading');
  await hold(10);
  await page.waitForSelector('#focus:not([hidden])');
  mark('proposal');
  await hold(34);

  // 5. 「なんでこれかっていうと」を読ませる
  mark('why');
  await hold(30);

  // 6. 別の案へ
  await tap('[data-act=next]', { pre: 4, post: 22 });
  mark('proposal2');
  await hold(10);
  await tap('[data-act=next]', { pre: 3, post: 22 });
  mark('proposal3');
  await hold(10);
  await tap('[data-act=next]', { pre: 3, post: 16 });
  mark('proposalBack');
  await hold(8);
  await page.evaluate(() => window.__cursorHide());

  // 7. 3案一覧
  await tap('nav.tabs button[data-tab=reco]', { pre: 4, post: 12 });
  mark('cards');
  await hold(18);
  for (let i = 0; i < 26; i++) {
    await page.evaluate(() => document.querySelector('main').scrollBy(0, 22));
    await shot();
  }
  mark('cardsScrolled');
  await hold(10);

  // 8. 誘い文をコピー
  await tap('.card:nth-child(2) [data-act=copy]', { pre: 5, post: 4 });
  mark('copied');
  await hold(26);

  // 9. 友達タブ（100人の話）
  await tap('nav.tabs button[data-tab=friends]', { pre: 4, post: 10 });
  mark('friends');
  await hold(24);
  for (let i = 0; i < 14; i++) {
    await page.evaluate(() => document.querySelector('main').scrollBy(0, 20));
    await shot();
  }
  await hold(10);

  // 10. これにする → ロック
  await tap('nav.tabs button[data-tab=home]', { pre: 4, post: 10 });
  await page.evaluate(() => { document.querySelector('main').scrollTop = 0; });
  await hold(10);
  await tap('#focus [data-act=pick]', { pre: 6, post: 2 });
  mark('lock');
  await hold(28);
  await page.evaluate(() => window.__cursorHide());
  // カウントダウンが動いているのを見せる（実時間で回して早回しにする）
  mark('lockTick');
  await hold(20, 320);
  // ここで「58分たった」ことにする。localStorage を書き換えてリロード＝
  // 実際にロックが端末に残り続けることの証明でもある。
  await page.evaluate(() => {
    const l = JSON.parse(localStorage.getItem('michi:lock'));
    l.startedAt = Date.now() - 58 * 60 * 1000;
    localStorage.setItem('michi:lock', JSON.stringify(l));
  });
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(300);
  mark('lockLate');
  await hold(18, 200);

  // 11. 完了報告
  await tap('[data-act=report]', { pre: 5, post: 10 });
  mark('report');
  await hold(8);
  await page.click('#reportNote');
  for (const ch of '知らない駅、当たりだった') { await page.type('#reportNote', ch, { delay: 0 }); await hold(2); }
  await hold(10);
  await tap('[data-act=finish]', { pre: 5, post: 2 });
  await page.evaluate(() => window.__cursorHide());
  mark('done');
  await hold(56);

  await writeFile(path.join(OUT, 'manifest.json'),
    JSON.stringify({ frames: n, width: 390, height: 844, scale: 2, markers }, null, 2));
  console.log(`captured ${n} frames -> ${OUT}`);
  console.log(JSON.stringify(markers, null, 2));
  await browser.close();
}

main().catch((e) => { console.error(e); process.exit(1); });

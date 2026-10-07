// 投稿用の画像カード（1080×1350）を書き出す。
//
//   npm i playwright
//   node render-card.mjs 出力先.jpg '{"title":"沈黙は、\n*気持ちを探す時間*。","sub":"急かさずに待っています","illus":"moon","night":true}'
//
// title の *〜* はマーカー強調、\n は改行。illus は moon / cups / bench / bubbles / sprout / sunrise。
// night: true で夜の色（紺）になる。夜の投稿や moon のイラストと合わせる。

import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execSync } from 'node:child_process';

// このフォルダに playwright が無ければ、グローバルに入っているものを使う
let chromium;
try {
  ({ chromium } = await import('playwright'));
} catch {
  const root = execSync('npm root -g').toString().trim();
  ({ chromium } = await import(path.join(root, 'playwright', 'index.mjs')));
}

const [out, json] = process.argv.slice(2);
if (!out || !json) {
  console.error('使い方: node render-card.mjs 出力先.jpg \'{"title":"...","illus":"cups"}\'');
  process.exit(1);
}
JSON.parse(json); // 書式の確認
const here = path.dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch(
  process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}
);
const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
await page.goto('file://' + path.join(here, 'card.html') + '?d=' + encodeURIComponent(json), { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: out, type: 'jpeg', quality: 90 });
await browser.close();
console.log('書き出しました: ' + out);

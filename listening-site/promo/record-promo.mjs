// ひだまり傾聴室のPR動画（縦型 1080×1920 / 30fps / 約35秒）を書き出すスクリプト。
//
//   npm i playwright ffmpeg-static
//   node record-promo.mjs            # → promo.mp4
//
// promo.html のCSSアニメーションを止め、1コマずつ時刻を進めてスクリーンショットし、
// ffmpeg で mp4 にまとめる。コマ落ちせず、何度書き出しても同じ映像になる。
// 文言や写真を変えたいときは promo.html を編集してから、もう一度実行する。

import { chromium } from 'playwright';
import ffmpeg from 'ffmpeg-static';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const FPS = 30;
const SECONDS = 35;
const frames = path.join(here, 'frames');
fs.rmSync(frames, { recursive: true, force: true });
fs.mkdirSync(frames);

const browser = await chromium.launch(
  process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}
);
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto('file://' + path.join(here, 'promo.html'), { waitUntil: 'networkidle' });
await page.evaluate(async () => {
  await document.fonts.ready;
  await Promise.all([...document.images].map((i) => i.decode()));
  document.getAnimations().forEach((a) => a.pause());
});

for (let i = 0; i < FPS * SECONDS; i++) {
  await page.evaluate((ms) => document.getAnimations().forEach((a) => (a.currentTime = ms)), (i * 1000) / FPS);
  await page.screenshot({ path: path.join(frames, String(i).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 92 });
}
await browser.close();

execFileSync(ffmpeg, [
  '-y', '-loglevel', 'error',
  '-framerate', String(FPS), '-i', path.join(frames, '%05d.jpg'),
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', '-movflags', '+faststart',
  path.join(here, 'promo.mp4'),
]);
fs.rmSync(frames, { recursive: true, force: true });
console.log('promo.mp4 を書き出しました');

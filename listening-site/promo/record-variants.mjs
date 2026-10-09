// テーマ別ショート動画（variant.html の ?v=1〜3）を mp4 に書き出す。
//
//   npm i playwright ffmpeg-static
//   node record-variants.mjs        # → short-1.mp4, short-2.mp4, short-3.mp4
//
// 仕組みは record-promo.mjs と同じ（アニメーションを止めて1コマずつ撮影）。

import { chromium } from 'playwright';
import ffmpeg from 'ffmpeg-static';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const FPS = 30;

const browser = await chromium.launch(
  process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}
);
for (const v of [1, 2, 3]) {
  const frames = path.join(here, `frames-${v}`);
  fs.rmSync(frames, { recursive: true, force: true });
  fs.mkdirSync(frames);
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(here, 'variant.html') + '?v=' + v, { waitUntil: 'networkidle' });
  const total = await page.evaluate(async () => {
    await document.fonts.ready;
    document.getAnimations().forEach((a) => a.pause());
    return window.TOTAL;
  });
  for (let i = 0; i < Math.round(total * FPS); i++) {
    await page.evaluate((ms) => document.getAnimations().forEach((a) => (a.currentTime = ms)), (i * 1000) / FPS);
    await page.screenshot({ path: path.join(frames, String(i).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 92 });
  }
  await page.close();
  execFileSync(ffmpeg, [
    '-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(frames, '%05d.jpg'),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart',
    path.join(here, `short-${v}.mp4`),
  ]);
  fs.rmSync(frames, { recursive: true, force: true });
  console.log(`short-${v}.mp4 を書き出しました（${total.toFixed(1)}秒）`);
}
await browser.close();

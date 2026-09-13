// scenes.html を 1フレームずつ PNG に焼く。
// 使い方: node render.mjs            → 全編
//         node render.mjs --at 7,22  → その秒だけ書き出して確認（build/preview/）
import { chromium } from 'playwright';
import { mkdir, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const BUILD = path.resolve(process.env.OUT_DIR || path.join(HERE, 'build'));
const FPS = Number(process.env.FPS || 30);

const args = process.argv.slice(2);
const atArg = args.includes('--at') ? args[args.indexOf('--at') + 1] : null;

async function main() {
  const outDir = path.join(BUILD, atArg ? 'preview' : 'frames');
  if (!atArg) await rm(outDir, { recursive: true, force: true });
  await mkdir(outDir, { recursive: true });

  const browser = await chromium.launch(['--force-color-profile=srgb'].length ? { args: ['--force-color-profile=srgb', '--font-render-hinting=none'] } : {});
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(HERE, 'scenes.html'), { waitUntil: 'networkidle' });
  await page.evaluate((base) => { window.__framesBase = base; }, 'file://' + path.join(BUILD, 'app'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);

  const duration = await page.evaluate(() => window.__duration);
  const times = atArg
    ? atArg.split(',').map(Number)
    : Array.from({ length: Math.round(duration * FPS) }, (_, i) => i / FPS);

  let i = 0;
  for (const t of times) {
    await page.evaluate(async (t) => {
      window.seek(t);
      await window.__loadFrame(t);
    }, t);
    const name = atArg ? `t${String(t).replace('.', '_')}.png` : `f${String(i).padStart(6, '0')}.png`;
    await page.screenshot({ path: path.join(outDir, name) });
    i++;
    if (!atArg && i % 150 === 0) console.log(`  ${i}/${times.length} frames`);
  }
  console.log(`rendered ${times.length} frames -> ${outDir}`);
  await browser.close();
}
main().catch((e) => { console.error(e); process.exit(1); });

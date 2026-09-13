// pitch.src.html の <!--P5SVG--> に P5 の挿絵を埋め込んで、1枚で完結する pitch.html を作る。
// 会場のネットが落ちても絵は出る（外部参照は Google Fonts だけ、フォールバック指定あり）。
import { readFileSync, writeFileSync } from "node:fs";
const dir = new URL("./", import.meta.url);
const read = (f) => readFileSync(new URL(f, dir), "utf8");

let svg = read("p5-unknown-encounter.svg")
  .replace(/^[\s\S]*?<svg /, "<svg ")
  .replace(/\s(width|height)="\d+"/g, "")
  .replace(/<svg /, '<svg preserveAspectRatio="xMidYMid slice" ')
  // id の衝突を避ける
  .replace(/id="([a-zA-Z]+)"/g, 'id="p5-$1"')
  .replace(/url\(#([a-zA-Z]+)\)/g, "url(#p5-$1)")
  .replace(/aria-labelledby="t d"/, 'aria-labelledby="p5-t p5-d"')
  .trim();

const out = read("pitch.src.html").replace("<!--P5SVG-->", svg);
if (out.includes("<!--P5SVG-->")) throw new Error("P5SVG placeholder not replaced");
writeFileSync(new URL("pitch.html", dir), out);
console.log("pitch.html", out.length, "bytes");

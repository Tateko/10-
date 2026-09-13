// 公開中のサイトから保存してきたHTMLを、そのまま録画できる形で出す。
//   FIXTURE=video/fixtures/deployed-index.html API_ORIGIN=http://localhost:3100 \
//     PORT=3200 node video/serve-fixture.mjs
//
// - `/` は渡されたHTMLをそのまま返す（公開サイトの画面をそっくり再現する）
// - `/api/*` は API_ORIGIN（＝このリポジトリの server.js。キーが無ければモック）へ中継する
// - `/api/suggest` の実レスポンスを保存したJSONを SUGGEST_FIXTURE で渡せば、それをそのまま返す
//   （公開サイトで実際に返ってきた提案を、そのまま映像に出したいとき用）
import http from 'node:http';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

const FIXTURE = process.env.FIXTURE;
const SUGGEST_FIXTURE = process.env.SUGGEST_FIXTURE || '';
const API_ORIGIN = process.env.API_ORIGIN || 'http://localhost:3100';
const PORT = Number(process.env.PORT || 3200);

if (!FIXTURE) {
  console.error('FIXTURE=<保存したHTMLのパス> が要る');
  process.exit(1);
}

const html = await readFile(path.resolve(FIXTURE), 'utf8');
const suggest = SUGGEST_FIXTURE ? await readFile(path.resolve(SUGGEST_FIXTURE), 'utf8') : null;

const relay = (req, res, body) => {
  const target = new URL(req.url, API_ORIGIN);
  const proxy = http.request(
    target,
    { method: req.method, headers: { ...req.headers, host: target.host } },
    (up) => { res.writeHead(up.statusCode || 502, up.headers); up.pipe(res); },
  );
  proxy.on('error', (e) => {
    res.writeHead(502, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ error: `APIに届かない (${API_ORIGIN}): ${e.message}` }));
  });
  if (body) proxy.write(body);
  proxy.end();
};

http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  if (url.pathname.startsWith('/api/')) {
    if (suggest && url.pathname === '/api/suggest') {
      res.writeHead(200, { 'content-type': 'application/json; charset=utf-8' });
      res.end(suggest);
      return;
    }
    const chunks = [];
    req.on('data', (c) => chunks.push(c));
    req.on('end', () => relay(req, res, Buffer.concat(chunks)));
    return;
  }
  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
  res.end(html);
}).listen(PORT, () => {
  console.log(`fixture: http://localhost:${PORT}  (html: ${FIXTURE}, api: ${suggest ? 'fixture' : API_ORIGIN})`);
});

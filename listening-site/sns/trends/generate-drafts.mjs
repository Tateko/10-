// X で今話題の悩み・言葉を Grok (xAI API の x_search) で調べ、
// ひだまり傾聴室の投稿案を sns/trends/YYYY-MM-DD.md に書き出す。
// GitHub Actions（.github/workflows/x-trend-drafts.yml）から週1回実行される。
// 手元で試す: XAI_API_KEY=xai-... node listening-site/sns/trends/generate-drafts.mjs

import { readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const API_KEY = process.env.XAI_API_KEY;
const API_BASE = process.env.XAI_API_BASE || "https://api.x.ai/v1";
const MODEL = process.env.XAI_MODEL || "grok-4";
const DAYS = Number(process.env.TREND_DAYS || 7);

if (!API_KEY) {
  console.error("XAI_API_KEY が設定されていません（GitHub の Settings → Secrets and variables → Actions で登録）");
  process.exit(1);
}

const here = dirname(fileURLToPath(import.meta.url));
const postsMd = await readFile(join(here, "..", "posts.md"), "utf8");

const jst = (d) => new Date(d.getTime() + 9 * 3600e3).toISOString().slice(0, 10);
const today = jst(new Date());
const since = jst(new Date(Date.now() - DAYS * 86400e3));

const instructions = `あなたは「ひだまり傾聴室」（誰にも言えない話を否定せずに聴く、有料の傾聴サービス）のSNS担当です。
x_search を使って、${since}〜${today} の日本語の X の投稿から、人が抱えている悩み・しんどさ・よく使われている言葉を調べてください。
対象テーマ：仕事・職場の人間関係、恋愛、お金や借金、家族、孤独、季節ごとの気分の落ち込み（連休明け・年末など）。

守ること：
- 個人を特定できる情報（ユーザー名・投稿の原文の引用・URL）は書かない。傾向として要約する
- 事件・事故・災害・著名人の訃報など、他人の不幸に便乗した話題は使わない
- 「死にたい」など命に関わる話題は投稿案にしない。見つけた場合は傾向メモに「扱わない」とだけ書く
- 借金は「解決します」と書かない。医療・カウンセリングのような表現をしない
- 投稿案の口調・長さ・ルールは、下の posts.md の既存投稿と運用ルールに合わせる
- 根拠が薄い話題は「話題」と書かない。確認できた範囲だけ書く

出力は次の Markdown だけにしてください（前置き不要）：

## 今週の傾向
- 話題・言葉：どんな悩みとして語られているか（1〜2行）を5〜8個

## X 投稿案（10本）
1. ...（140字以内。ハッシュタグは1〜2個まで、使わなくてもよい。リンクは入れない）

## Threads 投稿案（3本）
1. ...（改行ありの長め）

## 使わなかった話題
- 話題：理由

--- posts.md ---
${postsMd}`;

const res = await fetch(`${API_BASE}/responses`, {
  method: "POST",
  headers: { "Content-Type": "application/json", Authorization: `Bearer ${API_KEY}` },
  body: JSON.stringify({
    model: MODEL,
    input: [{ role: "user", content: instructions }],
    tools: [{ type: "x_search" }],
  }),
  signal: AbortSignal.timeout(10 * 60e3), // x_search は何周も検索するので長めに待つ
});

if (!res.ok) {
  console.error(`xAI API エラー: ${res.status} ${await res.text()}`);
  process.exit(1);
}

const data = await res.json();
const text = (data.output || [])
  .filter((item) => item.type === "message")
  .flatMap((item) => item.content || [])
  .filter((c) => c.type === "output_text")
  .map((c) => c.text)
  .join("\n")
  .trim();

if (!text) {
  console.error("Grok から本文が返ってきませんでした:", JSON.stringify(data).slice(0, 2000));
  process.exit(1);
}

const out = join(here, `${today}.md`);
await writeFile(
  out,
  `# X 話題チェックと投稿案（${since}〜${today}）

> Grok（${MODEL}）が X を検索して作った**下書き**です。そのまま投稿せず、ヒロが読んで直してから使ってください。
> 気に入った案は \`../posts.md\` に移すか、X / Threads にコピーして投稿します。

${text}
`,
);
console.log(`書き出しました: ${out}`);

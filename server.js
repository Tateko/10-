import express from "express";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { z } from "zod";
import fs from "node:fs";
import os from "node:os";

const here = path.dirname(fileURLToPath(import.meta.url));
const app = express();
app.use(express.json({ limit: "64kb" }));
app.use(express.static(path.join(here, "public")));

const MODEL = "claude-opus-5";
// MOCK=1、または認証情報が見つからないときはダミー応答で動かす（デモが止まらないように）
let client = null;
let MOCK = process.env.MOCK === "1";
const hasCredentials =
  Boolean(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN) ||
  fs.existsSync(path.join(os.homedir(), ".config", "anthropic")); // `ant auth login` のプロファイル
if (!MOCK && !hasCredentials) {
  console.warn("[michi] ANTHROPIC_API_KEY が見つかりません。MOCK モードで起動します（.env.example を参照）。");
  MOCK = true;
}
if (!MOCK) client = new Anthropic();

// ---- 提案の型（構造化出力でこの形を保証する） ----
const Proposal = z.object({
  title: z.string().describe("提案の見出し。15文字前後"),
  category: z.enum(["食", "移動・散歩", "人と会う", "文化・鑑賞", "身体を動かす", "学び", "その他"]),
  distance: z.number().int().min(1).max(5).describe("未知度。この人の普段の行動からどれだけ離れているか。1=少し外側 / 3=はっきり外側 / 5=完全に圏外。3案は異なる値にする"),
  why_you_wouldnt_pick: z.string().describe("なぜこの人は自分ではこれを選ばないのか。入力から根拠を示す"),
  what: z.string().describe("具体的に何をするか。時間・場所感を含めて2〜3文"),
  where_hint: z.string().describe("場所のヒント。固有名詞は断定せず『〜のような場所』でよい"),
  duration_min: z.number().int().describe("所要時間（分）"),
  cost_hint: z.string().describe("費用感。例: 0円 / 〜1,000円"),
  invite_who: z.string().describe("誰を誘うと感情が動くか。入力の同行者情報を踏まえる"),
  invite_message: z.string().describe("そのままLINEで送れる誘い文。50〜80文字。絵文字なし"),
  first_step: z.string().describe("今この場で60秒以内にできる最初の一歩"),
  emotion: z.string().describe("この体験でどんな感情が動くか。一言"),
});

const Proposals = z.object({
  one_liner: z.string().describe("今日のこの人への一言。30文字以内"),
  proposals: z.array(Proposal).length(3),
});

const SYSTEM = `あなたは「未知イベント提案」の秘書です。
ユーザーが自分では思いつかない・自分では選ばない体験を、今日この後の予定として提案します。

守ること:
- 3案とも、ユーザーの入力から「この人はこれを選ばないだろう」と言える根拠を持つこと。効率的・無難・いつも通りの案は出さない。
- 検索すれば出てくる定番スポットの紹介ではなく、行動の提案にする。「〜のような場所で、〜をする」と書く。
- 少なくとも1案は「人と会う／人を誘う」要素を必ず含める。感情が動くのは人が絡むときである。
- 使える時間・予算・エリアの制約は守る。時間内に終わる。
- 断定できない固有名詞（店名など）は出さない。存在しない店や施設をでっち上げない。
- 説教しない。短く、具体的に、動きたくなる文で。
- 3案の distance（未知度）はばらけさせる。1つは踏み出しやすい案、1つは明確に圏外の案にする。
- 日本語で書く。`;

function buildPrompt(input) {
  return `# ユーザーの今
- いまいるエリア: ${input.area || "不明"}
- 使える時間: ${input.minutes || "不明"}分
- 気分: ${input.mood || "特になし"}
- 予算感: ${input.budget || "こだわりなし"}
- 最近やったこと・いつもの過ごし方: ${input.recent || "（記入なし）"}
- 一緒に動ける人: ${input.companion || "（記入なし・一人でも、誰かを誘ってもよい）"}
- 現在時刻(JST): ${new Date().toLocaleString("ja-JP", { timeZone: "Asia/Tokyo" })}

この人が「自分では選ばない」体験を3つ提案してください。`;
}

// ---- APIキーなしでもUIを動かすためのダミー ----
function mockProposals(input) {
  const who = input.companion || "最近連絡していない友人";
  return {
    one_liner: "今日は『いつもの』を一つだけ外してみる日",
    proposals: [
      {
        title: "知らない駅で降りて昼を決める",
        category: "移動・散歩",
        distance: 2,
        why_you_wouldnt_pick: `「${input.recent || "いつも同じ店"}」と書いているので、店を事前に決めて動くタイプ。決めずに降りることは選ばない。`,
        what: `${input.area || "今いる場所"}から2駅先、降りたことのない駅で降りる。改札から見えた範囲で、一番人が入っていない店に入る。`,
        where_hint: "乗り換えなしで行ける、降りたことのない駅",
        duration_min: 60,
        cost_hint: "〜1,500円",
        invite_who: who,
        invite_message: "今から2駅先の知らない駅で降りて昼食べるんだけど、来ない？店は決めてない。",
        first_step: "乗換アプリを開かず、ホームの路線図を見て駅名を一つ選ぶ",
        emotion: "ちょっとした不安と、当たりを引いたときの高揚",
      },
      {
        title: "会話禁止で30分、同じものを見る",
        category: "文化・鑑賞",
        distance: 4,
        why_you_wouldnt_pick: "効率を気にする記述が多い。目的なく何かを『ただ見る』時間を自分では作らない。",
        what: "近くの公園か川沿いのベンチに二人で座り、30分間しゃべらずに同じ方向を見る。終わったら見えたものを一つずつ言う。",
        where_hint: "歩いて10分以内の、座れる屋外",
        duration_min: 40,
        cost_hint: "0円",
        invite_who: who,
        invite_message: "変な提案なんだけど、30分だけ黙って一緒に外を見る、っていうのやってみない？",
        first_step: "今いる場所から一番近い『座れる屋外』を1つ思い浮かべる",
        emotion: "退屈のあとに来る、妙な親密さ",
      },
      {
        title: "初対面の人に一つ質問して帰る",
        category: "人と会う",
        distance: 5,
        why_you_wouldnt_pick: "同行者の記述が身近な人に限られている。知らない人に自分から話しかける場面を選ばない。",
        what: "商店街や個人商店で、店の人に『この街で一番好きな場所はどこですか』と一つだけ聞く。答えの場所に実際に行く。",
        where_hint: "チェーンではない個人店が並ぶ通り",
        duration_min: 45,
        cost_hint: "〜500円（何か一つ買う）",
        invite_who: "一人で。あとで誰かに話すために",
        invite_message: "さっき店の人に聞いた場所に来てるんだけど、意外と良い。次一緒に来ない？",
        first_step: "質問の文を声に出して一回言ってみる",
        emotion: "緊張と、人の親切に触れたときの温度",
      },
    ],
  };
}

app.get("/api/health", (_req, res) => {
  res.json({ ok: true, mode: MOCK ? "mock" : "live", model: MODEL });
});

app.post("/api/suggest", async (req, res) => {
  const input = req.body ?? {};
  if (MOCK) {
    await new Promise((r) => setTimeout(r, 600));
    return res.json({ mode: "mock", ...mockProposals(input) });
  }
  try {
    const response = await client.messages.parse({
      model: MODEL,
      max_tokens: 4000,
      system: SYSTEM,
      // デモの待ち時間を抑えるため低effort。品質が足りなければ "medium" に上げる
      output_config: { effort: "low", format: zodOutputFormat(Proposals) },
      messages: [{ role: "user", content: buildPrompt(input) }],
    });
    if (response.stop_reason === "refusal") {
      return res.status(422).json({ error: "提案を生成できませんでした。入力を変えて試してください。" });
    }
    if (!response.parsed_output) {
      return res.status(502).json({ error: "応答の形式が不正でした。もう一度試してください。" });
    }
    res.json({ mode: "live", ...response.parsed_output });
  } catch (error) {
    if (error instanceof Anthropic.AuthenticationError) {
      return res.status(500).json({ error: "APIキーが無効です。ANTHROPIC_API_KEY を確認してください。" });
    }
    if (error instanceof Anthropic.RateLimitError) {
      return res.status(429).json({ error: "混雑しています。少し待ってから再実行してください。" });
    }
    if (error instanceof Anthropic.APIError) {
      return res.status(502).json({ error: `API error ${error.status}: ${error.message}` });
    }
    console.error(error);
    res.status(500).json({ error: `サーバーエラー: ${error.message}` });
  }
});

const port = Number(process.env.PORT) || 3000;
app.listen(port, () => {
  console.log(`michi: http://localhost:${port}  (mode: ${MOCK ? "mock" : "live"}, model: ${MODEL})`);
});

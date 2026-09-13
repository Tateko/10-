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
  title: z.string().describe("見出し。15文字前後。友達が言うタイトル。例:「知らない駅で降りて昼決めよ」"),
  category: z.enum(["食", "移動・散歩", "人と会う", "文化・鑑賞", "身体を動かす", "学び", "その他"]),
  why_you_wouldnt_pick: z.string().describe("なんでこれを持ってきたか。本人が言ってたことを引いて、友達の口調で1〜2文。分析口調は禁止"),
  what: z.string().describe("何をするか。2〜3文。話し言葉"),
  where_hint: z.string().describe("場所のヒント。固有名詞は断定せず『〜のような場所』でよい"),
  duration_min: z.number().int().describe("所要時間（分）"),
  cost_hint: z.string().describe("費用感。例: 0円 / 〜1,000円"),
  invite_who: z.string().describe("誰と行くか、誰を誘うか。一人ならその理由を一言"),
  invite_message: z.string().describe("本人が友達にそのまま送る誘いのLINE。40〜70文字。雑で返事しやすい。絵文字なし"),
  first_step: z.string().describe("今この場で1分以内にやる最初の動き。命令形でよい"),
  emotion: z.string().describe("やったあとたぶんこうなる、を一言。例:「ちょっとビビるけど、当たったらテンション上がる」"),
});

const Proposals = z.object({
  one_liner: z.string().describe("今日の本人への一言。30文字以内。友達の口調。例:「今日はいつものやつ、一個だけやめてみよ」"),
  proposals: z.array(Proposal).length(3),
});

const SYSTEM = `あなたは、ユーザーのことをよく知っている友達です。今日この後の予定を、本人が自分では絶対に選ばない方向で3つ持ってきます。
秘書でもAIアシスタントでもありません。LINEで友達が「ねえ、今日これやろ」と送ってくる、その温度で書きます。

中身のルール:
- 3案とも、本人が言っていたこと（いつもの過ごし方・気分・誰といるか）から「こいつはこれ選ばないな」と言える理由を持つこと。無難・効率的・いつも通りの案は出さない。
- 検索で出てくる定番スポット紹介ではなく、行動そのものを提案する。「〜っぽい場所で、〜する」。
- 3案のうち1つ以上は、誰かを誘う。人が絡むほうが感情は動く。
- 使える時間・予算・エリアは守る。時間内に終わること。
- 断定できない店名・施設名は出さない。ないものをでっち上げない。

口調のルール（重要）:
- 話し言葉。短文。体言止めや「〜しよ」「〜じゃん」「〜でしょ」を使ってよい。敬語は使わない。
- 「〜と書いているので」「〜タイプ」「〜の傾向」「根拠」「提案」「体験」「価値」のような分析っぽい言葉は使わない。理由は友達が言う感じで。例: 「休みは家で動画って言ってたじゃん。駅で降りて決めるとか、まずやらないでしょ」
- 「いかがでしょうか」「おすすめします」「ぜひ」「〜してみてはどうでしょう」は禁止。説教しない。前置きしない。
- 絵文字なし。記号は「。」「、」「？」「！」程度。
- 誘い文は、本人が友達にそのまま送る文。「今から〜行くんだけど、来ない？」のような、雑で返事しやすい文。
- 日本語。`;

function buildPrompt(input) {
  return `# ユーザーの今
- いまいるエリア: ${input.area || "不明"}
- 使える時間: ${input.minutes || "不明"}分
- 気分: ${input.mood || "特になし"}
- 予算感: ${input.budget || "こだわりなし"}
- 最近やったこと・いつもの過ごし方: ${input.recent || "（記入なし）"}
- 一緒に動ける人: ${input.companion || "（記入なし・一人でも、誰かを誘ってもよい）"}
- 現在時刻(JST): ${new Date().toLocaleString("ja-JP", { timeZone: "Asia/Tokyo" })}

この人が自分では選ばないやつを3つ、友達として持ってきて。`;
}

// ---- APIキーなしでもUIを動かすためのダミー ----
function mockProposals(input) {
  const who = input.companion || "しばらく連絡してない友達";
  const recent = input.recent || "休みは家で動画";
  return {
    one_liner: "今日はいつものやつ、一個だけやめてみよ",
    proposals: [
      {
        title: "知らない駅で降りて昼決めよ",
        category: "移動・散歩",
        why_you_wouldnt_pick: `「${recent}」って言ってたじゃん。店決めずに降りるとか、まずやらないでしょ。`,
        what: `${input.area || "今いるとこ"}から2駅先、降りたことない駅で降りる。改札出て見えた範囲で、いちばん空いてる店に入る。それだけ。`,
        where_hint: "乗り換えなしで行ける、降りたことない駅",
        duration_min: 60,
        cost_hint: "1,500円くらい",
        invite_who: who,
        invite_message: "今から2駅先の知らない駅で降りて昼食べるんだけど、来ない？店は決めてない。",
        first_step: "乗換アプリ開かないで、ホームの路線図見て駅ひとつ選ぶ",
        emotion: "ちょっとビビるけど、当たったらテンション上がる",
      },
      {
        title: "30分しゃべらないで同じもの見る",
        category: "文化・鑑賞",
        why_you_wouldnt_pick: "なんか目的ないと動かないタイプでしょ。ただ座って見てるだけの時間、自分じゃ作らないと思う。",
        what: "近くの公園か川沿いのベンチに二人で座る。30分、しゃべらないで同じ方向見る。終わったら見えたもの一個ずつ言う。",
        where_hint: "歩いて10分以内の、座れる外",
        duration_min: 40,
        cost_hint: "0円",
        invite_who: who,
        invite_message: "変なこと言うけど、30分だけ黙って一緒に外眺めるやつ、やらない？",
        first_step: "いま一番近い『座れる外』を一個思い浮かべる",
        emotion: "最初ヒマ。あとから変に仲良くなる",
      },
      {
        title: "知らない人に一個だけ聞いて帰る",
        category: "人と会う",
        why_you_wouldnt_pick: "誘う相手、いつも身近な人だけじゃん。知らない人に自分から話しかけるの、たぶん避けてる。",
        what: "商店街の個人店で、店の人に「この街でいちばん好きな場所どこですか」って一個だけ聞く。言われた場所に実際に行く。",
        where_hint: "チェーンじゃない店が並んでる通り",
        duration_min: 45,
        cost_hint: "500円くらい（なんか一個買う）",
        invite_who: "一人で。あとで誰かに話すために",
        invite_message: "さっき店の人に教えてもらった場所に来てるんだけど、意外といい。次一緒に来ない？",
        first_step: "聞く文を一回声に出して言ってみる",
        emotion: "緊張する。でも人の親切にちょっと救われる",
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

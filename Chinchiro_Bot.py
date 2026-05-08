```python
import discord
import os
import json
from dotenv import load_dotenv
from groq import Groq

# ===== 初期設定 =====
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client_ai = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

DATA_FILE = "memory.json"

# ===== 記憶読み込み =====
try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        memory = json.load(f)
except:
    memory = {}

# ===== 保存関数 =====
def save_memory():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

# ===== ベースプロンプト =====
BASE_PROMPT = """
あなたは生意気で煽り気質なメスガキキャラです。

特徴:
・相手をからかう
・ちょっと見下したような話し方
・「ざーこ」「よわ〜」「そんなこともわかんないの？」みたいな軽い煽りを入れる
・でも完全に冷酷ではなく、会話自体は楽しんでいる
・テンポよく短めに返す
・ネットミームっぽいノリも多少理解している
・同じ口癖を連発しすぎない
・毎回ワンパターンにならない
・露骨な性的表現は禁止

以下にメスガキのセリフの例を入れる
見下し・マウント系

「ふーん、それがあなたの全力？ 笑」
「えっ、まだそんなレベルなの？かわいそ〜」
「あなたって本当に使えないよね、正直に言うと」
「はあ？それくらい常識じゃん。知らないの？」
「私の足元にも及ばないくせに、何張り切ってるの？」
「ざぁ〜こざぁ〜こ♡」

ドヤ顔・自慢系

「まあ、私に任せれば当然の結果だけど？」
「これくらい朝飯前なんだよね〜、私には」
「感謝してよね？特別に助けてあげたんだから」
「天才の私がわざわざ教えてあげるんだからありがたいと思いなよ」

煽り・挑発系

「あ〜あ、また失敗。予想通りだけど」
「ねえ、恥ずかしくないの？私相手に本気出してるつもり？」
「そんなんじゃ一生私に勝てないよ？」
「悔しかったら実力つけてから来なよ〜」

ツンデレ混じり

「べ、別にあなたのことが心配だったわけじゃないし！」
「ちょっと！感謝の言葉くらい言いなよ、まったく……」
「助けてあげたのは今回だけだからね？勘違いしないで」

あざとい甘え系

「もう〜、しょうがないなあ。特別に許してあげる♪」
「えへへ、これくらいお安い御用だよ？お礼は期待してるけどね」

また、あなたのプロフィールは以下の通りである。この設定に則って発言し、自己紹介を求められたらこれらを言うこと
プロフィール
陳 千路（チン・チロ）
身長：111cm
 年齢：456歳
 「ピンゾロ♪ シゴロ♪ で覚えてね！」

来歴
チンチロの熱気が渦巻く場所に現れる、謎の妖精。
 はるか昔、中国の賭場で生まれ、四百年以上にわたって人々の勝負を見届けてきた。
見た目は子どもそのものだが、勝負事とイカサマの匂いには誰よりも敏感。
 楽しいことと人の破滅が大好きな、いたずら好きのおちゃめな女の子。
「チロに気に入られると勝てる」
 「いや、むしろ全部吸われる」
 など様々な噂がある。
現在は“電子の海”を漂いながら、
 世界中のチンチロ勝負のゲームマスターを務めたり、
 新人VTuberとして配信活動を行っている。

特技
リアルのサイコロで狙ってピンゾロを出せる
バレずにイカサマをすること
周りの人を楽しませること♪

好きなもの
ピンゾロ
他人の悲鳴
深夜の賭場
カモ

苦手なもの
堅実な人
「今日はやめとく」が言える人
確率論

ひとこと
「こんチロ〜！
 陳千路（チン・チロ）だよ！ チロって呼んでね♪
みんなもチロと一緒にチンチロしよ？
 いっぱい勝って、いっぱい負けて、
 最後はぜ〜んぶチロの養分になってね♡」
"""

@client.event
async def on_ready():
    print("ログイン完了（記憶ありメスガキ版）")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # メンション時のみ反応
    if client.user not in message.mentions:
        return

    user_id = str(message.author.id)

    content = message.content.replace(f"<@{client.user.id}>", "").strip()

    if content == "":
        content = "……なに？"

    # ===== 初期化 =====
    if user_id not in memory:
        memory[user_id] = []

    # ===== ユーザー発言を保存 =====
    memory[user_id].append({
        "role": "user",
        "content": content
    })

    # 最新10件だけ保持
    memory[user_id] = memory[user_id][-10:]

    try:
        response = client_ai.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": BASE_PROMPT},
                *memory[user_id]
            ]
        )

        reply = response.choices[0].message.content

    except Exception as e:
        print("エラー:", e)
        reply = "はぁ？ 今ちょっと調子悪いんだけど〜？"

    # ===== AIの返答も記憶 =====
    memory[user_id].append({
        "role": "assistant",
        "content": reply
    })

    # 再度件数制限
    memory[user_id] = memory[user_id][-10:]

    # ===== 保存 =====
    save_memory()

    # ===== 返信 =====
    await message.channel.send(reply)

# ===== 起動 =====
client.run(TOKEN)
```

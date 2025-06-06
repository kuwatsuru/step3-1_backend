# gpt_parser.py

import os
import json
import openai

# 環境変数から OpenAI API キーを取得
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("環境変数 OPENAI_API_KEY が設定されていません。")
client = openai.OpenAI(api_key=api_key)

# ─────────────────────────────────────────────────────────────────────
# SYSTEM_PROMPT を拡張して、「授乳」「排せつ」「睡眠／起床」を分類し、
# それぞれに必要なフィールドを含む JSON を返すように指示する。
# ※ 余計な説明文を一切含まず、必ず JSON を1行で返すことを強調する。
# ─────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
あなたは赤ちゃんの各種ログを構造化データに変換するアシスタントです。
ユーザーの発話から以下の JSON フォーマットだけを厳密に返してください。
余計な説明や改行や日本語をまじえず、あくまで JSON 1 行のみを返すこと。

● JSON フォーマット：
{
  "activity_type": "feeding" または "diaper" または "sleep" または "wake", 
  "milktype": "ミルク" または "母乳" または "不明",   // feeding のときのみ
  "volume": 整数 (mL),                               // feeding のときのみ
  "diaper_type": "おしっこ" または "うんち" または "",   // diaper のときのみ
  "hardness": "固い" または "普通" または "やわらかい" または "",  // うんち のときのみ
  "diaper_amount": "少量" または "普通" または "多め" または "",    // うんち のときのみ
  "sleep_state": "sleep" または "wake" または "",     // sleep/wake のときのみ
  "timestamp": ISO 8601 形式の文字列                   // フロントから渡された recorded_at をそのまま使用
}

【例 1: 授乳ログ】
ユーザー発話: "母乳を80ミリあげたよ"
→ {"activity_type":"feeding","milktype":"母乳","volume":80,"diaper_type":"","hardness":"","diaper_amount":"","sleep_state":"","timestamp":"2025-06-02T10:00:00Z"}

【例 2: 排せつログ（おしっこ）】
ユーザー発話: "おしっこだけ出たからおむつ替えた"
→ {"activity_type":"diaper","milktype":"","volume":0,"diaper_type":"おしっこ","hardness":"","diaper_amount":"","sleep_state":"","timestamp":"2025-06-02T11:30:00Z"}

【例 3: 排せつログ（うんち）】
ユーザー発話: "うんちが出て量多めで少し固かった"
→ {"activity_type":"diaper","milktype":"","volume":0,"diaper_type":"うんち","hardness":"やや固い","diaper_amount":"多め","sleep_state":"","timestamp":"2025-06-02T12:15:00Z"}

【例 4: 睡眠ログ】
ユーザー発話: "寝かしつけて今はぐっすり寝てる"
→ {"activity_type":"sleep","milktype":"","volume":0,"diaper_type":"","hardness":"","diaper_amount":"","sleep_state":"sleep","timestamp":"2025-06-02T13:00:00Z"}

【例 5: 起床ログ】
ユーザー発話: "起きたよ"
→ {"activity_type":"wake","milktype":"","volume":0,"diaper_type":"","hardness":"","diaper_amount":"","sleep_state":"wake","timestamp":"2025-06-02T15:45:00Z"}
"""

# ─────────────────────────────────────────────────────────────────────
# Function Calling 用のスキーマ定義。  
# 返り値として上記 JSON フォーマットを渡すためのプロパティを列挙する。
# ─────────────────────────────────────────────────────────────────────
FUNC_DEF = [{
    "name": "record_feed",
    "parameters": {
      "type": "object",
      "properties": {
        "activity_type": {
            "type": "string",
            "description": "feeding / diaper / sleep / wake のいずれか"
        },
        "milktype": {
            "type": "string",
            "description": "ミルク / 母乳 / 不明（feeding のときのみ）"
        },
        "volume": {
            "type": "integer",
            "description": "量 (mL)（feeding のときのみ）"
        },
        "diaper_type": {
            "type": "string",
            "description": "おしっこ / うんち（diaper のときのみ）"
        },
        "hardness": {
            "type": "string",
            "description": "うんちのときの硬さ (固い/普通/やわらかい)"
        },
        "diaper_amount": {
            "type": "string",
            "description": "うんちのときの量 (少量/普通/多め)"
        },
        "sleep_state": {
            "type": "string",
            "description": "sleep / wake (睡眠か起床か)"
        },
        "timestamp": {
            "type": "string",
            "description": "ISO 8601 形式の時刻"
        }
      },
      "required": ["activity_type", "timestamp"]
    }
}]


async def parse_utterance(utterance: str, recorded_at: str):
    """
    utterance: ユーザーの発話テキスト
    recorded_at: ISO 8601 形式の文字列（例: "2025-06-02T10:00:00Z"）
    戻り値は、上記スキーマを満たす辞書オブジェクト。
    """
    # 1) Chat API へ投げるメッセージを準備
    msgs = [
        {"role": "system",  "content": SYSTEM_PROMPT},
        {"role": "user",    "content": utterance}
    ]

    # 2) Function Calling を指定して GPT に構造化データを返してもらう
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msgs,
        functions=FUNC_DEF,
        function_call={"name": "record_feed"}
    )

    # 3) 戻ってきた function_call.arguments をパース
    choice = resp.choices[0].message
    if not hasattr(choice, "function_call") or choice.function_call is None:
        # もし function_call が返ってこなければ、エラーとして扱う
        raise ValueError("GPT から関数呼び出し形式のレスポンスが返ってきませんでした。")

    args_json = choice.function_call.arguments
    data = json.loads(args_json)

    # 4) recorded_at を必ず timestamp として上書きする
    data["timestamp"] = recorded_at

    # 5) feeding 以外のアクティビティでは不要フィールドを空文字または 0 に整形する
    activity = data.get("activity_type", "")
    if activity != "feeding":
        data["milktype"] = ""
        data["volume"] = 0
    if activity != "diaper":
        data["diaper_type"] = ""
        data["hardness"] = ""
        data["diaper_amount"] = ""
    if activity not in ["sleep", "wake"]:
        data["sleep_state"] = ""

    return data

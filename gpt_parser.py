import os, json, datetime as dt, openai

# 環境変数からAPIキー取得
api_key = os.getenv("OPENAI_API_KEY")
# OpenAIクライアント作成
client = openai.OpenAI(api_key=api_key)

SYSTEM_PROMPT = """
あなたは赤ちゃんの授乳ログを構造化データに変換するアシスタントです。
以下の JSON フォーマットだけを厳密に返してください。余計な文章や説明を入れず、あくまで JSON 1 行のみを返すこと。

フォーマット：
{
  "milktype": "ミルク" または "母乳" または "不明",
  "volume": 整数 (mL),

}

例：
{"milktype":"ミルク","volume":200}
"""

FUNC_DEF = [{
    "name": "record_feed",
    "parameters": {
      "type": "object",
      "properties": {
        "milktype": {"type": "string"},
        "volume": {"type": "integer"},
      },
      "required":[ "milktype", "volume" ]
    }
}]


async def parse_utterance(utterance: str, recorded_at: str):
    msgs = [
        {"role":"system", "content": SYSTEM_PROMPT},
        {"role":"user",   "content": utterance}
    ]
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msgs,
        functions=FUNC_DEF,
        function_call={"name":"record_feed"}
    )
    args = resp.choices[0].message.function_call.arguments
    data = json.loads(args)
    # recorded_at を使用  
    data["timestamp"] = recorded_at
    return data  
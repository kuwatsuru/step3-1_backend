import os, json, datetime as dt, openai

# 環境変数からAPIキー取得
api_key = os.getenv("OPENAI_API_KEY")
# OpenAIクライアント作成
client = openai.OpenAI(api_key=api_key)

SYSTEM_PROMPT = """
あなたは赤ちゃんの授乳ログを構造化データに変換するアシスタントです。
出力は必ず JSON 1 行のみ:
{
  "volume": int (mL),
  "timestamp": ISO 8601 文字列
}
"""

FUNC_DEF = [{
    "name": "record_feed",
    "parameters": {
      "type": "object",
      "properties": {
        "volume": {"type": "integer"},
        "timestamp": {"type": "string", "description":"ISO 8601"},
      },
      "required":[ "volume", "timestamp" ]
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
    # GPT が timestamp を返さなかった場合は recorded_at を使用
    ts = data.get("timestamp") or recorded_at
    data["timestamp"] = ts
    return data  # {"volume":200,"timestamp":"..."}

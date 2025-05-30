#
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
#from db_control import crud, mymodels
from db_control import crud, mymodels_MySQL as mymodels
import openai
#from google import genai
import os
from dotenv import load_dotenv
from datetime import datetime
from gpt_parser import parse_utterance

class Customer(BaseModel):
    customer_id: str
    customer_name: str
    age: int
    gender: str

# .env を読み込む
load_dotenv()

# 環境変数からAPIキー取得
api_key = os.getenv("OPENAI_API_KEY")
# OpenAIクライアント作成
client = openai.OpenAI(api_key=api_key)


# # 環境変数からGemini APIキー取得
# gemini_api_key = os.getenv("GEMINI_API_KEY")
# # OpenAIクライアント作成
# client_gemini = genai.Client(api_key="GEMINI_YOUR_API_KEY")

app = FastAPI()

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#音声認識の方
class RecordIn(BaseModel):
    utterance: str
    recorded_at: datetime


@app.get("/")
def index():
    return {"message": "FastAPI top page!"}


@app.post("/customers")
def create_customer(customer: Customer):
    values = customer.dict()
    tmp = crud.myinsert(mymodels.Customers, values)
    result = crud.myselect(mymodels.Customers, values.get("customer_id"))

    if result:
        result_obj = json.loads(result)
        return result_obj if result_obj else None
    return None


@app.get("/customers")
def read_one_customer(customer_id: str = Query(...)):
    result = crud.myselect(mymodels.Customers, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None


@app.get("/allcustomers")
def read_all_customer():
    result = crud.myselectAll(mymodels.Customers)
    # 結果がNoneの場合は空配列を返す
    if not result:
        return []
    # JSON文字列をPythonオブジェクトに変換
    return json.loads(result)


@app.put("/customers")
def update_customer(customer: Customer):
    values = customer.dict()
    values_original = values.copy()
    tmp = crud.myupdate(mymodels.Customers, values)
    result = crud.myselect(mymodels.Customers, values_original.get("customer_id"))
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None


@app.delete("/customers")
def delete_customer(customer_id: str = Query(...)):
    result = crud.mydelete(mymodels.Customers, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"customer_id": customer_id, "status": "deleted"}


@app.get("/fetchtest")
def fetchtest():
    response = requests.get('https://jsonplaceholder.typicode.com/users')
    return response.json()

#オウム返し機能(リクエストボディをそのまま返す)
@app.post("/echo")
async def echo(request: Request):
    data = await request.json()
    message = data.get("message", "")
    return {"echo": message}

#AIで内容を要約し、本人のやりたいこと、Willを提案する
@app.post("/ai_gpt")
async def ask_openai(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    prompt = f"""
        今日の日記や気持ちを「{user_message}」として記しました。
        この内容から、以下の項目を日本語で1～2行で出力してください：
        - 潜在的にやりたいこと、気持ちが向いているもの（Will Can MustのWillにあたるもの）
        """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは相手の文章から気持ちや秘めたる意思を汲み取るプロフェッショナルです"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        ai_reply = response.choices[0].message.content.strip()
        return {"ai_response": ai_reply}

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/record")
async def record_feed(body: RecordIn):
    # ここでGPTに飛ばしてパース
    parsed = await parse_utterance(body.utterance, None)
    # parsed には {"volume":200,"timestamp":"..."} のような dict が返る
    return {"parsed": parsed}





#         #AIで内容を要約し、本人のやりたいこと、Willを提案する
# @app.post("/ai_gemini")
# async def ask_gemini(request: Request):
#     data = await request.json()
#     user_message = data.get("message", "")
#     prompt = f"""
#         あなたは相手の文章から気持ちや秘めたる意思を汲み取るプロフェッショナルです。
#         今日の日記や気持ちを「{user_message}」として記しました。
#         この内容から、以下の項目を日本語で1～2行で出力してください：
#         - 潜在的にやりたいこと、気持ちが向いているもの（Will Can MustのWillにあたるもの）
#         """
    
#     try:
#         response = client_gemini.models.generate_content(
#             model="gemini-2.0-flash",
#             contents=prompt
#         )
#         return {"ai_response": response.text.strip()}

#     except Exception as e:
#         return {"error": str(e)}
    

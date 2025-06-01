
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from connect_MySQL import engine  # Core 用の Engine を読み込む

router = APIRouter()

# ── リクエストボディ用 Pydantic モデル ──────────────────────────────────
class RecordParsed(BaseModel):
    milktype: str = Field(..., description="ミルク または 母乳 または 不明")
    volume: int = Field(..., ge=0, description="量 (mL)")


# ── /api/save_log エンドポイント定義 ───────────────────────────────────
@router.post("/save_milklog")
def save_milklog(record: RecordParsed):
    conn = None
    try:
        # 1) Connection を取得
        conn = engine.connect()

        # 2) トランザクション開始
        trans = conn.begin()

        # 3) 生の SQL 文を準備 (text() を使うとパラメータバインドが安全)
        sql = text("""
            INSERT INTO feeding_logs (milktype, volume)
            VALUES (:milktype, :volume)
        """)

        # 4) パラメータを渡して実行
        conn.execute(sql, {
            "milktype": record.milktype,
            "volume": record.volume
        })

        # 5) コミット（トランザクション確定）
        trans.commit()

        return {"status": "success"}
    except Exception as e:
        # 例外時はロールバック
        if conn:
            trans.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 最後に必ず接続を閉じる
        if conn:
            conn.close()

from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# データベース接続情報
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')



# MySQLのURL構築
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SSL_CA_PATH = os.getenv('SSL_CA_PATH')
# エンジンの作成
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "ssl_ca": SSL_CA_PATH
    }
)

print("----- ✅ 環境変数の読み込み確認 -----")
print("DB_USER:", DB_USER)
print("DB_PASSWORD:", "(非表示)" if DB_PASSWORD else "None")
print("DB_HOST:", DB_HOST)
print("DB_PORT:", DB_PORT)
print("DB_NAME:", DB_NAME)
print("SSL_CA_PATH:", SSL_CA_PATH)
print("DATABASE_URL:", DATABASE_URL)
print("----------------------------------")

__all__ = ["engine"]
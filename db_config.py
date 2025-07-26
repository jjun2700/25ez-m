import os
from dotenv import load_dotenv

# .env 파일 로드 (로컬 전용)
load_dotenv()

# Streamlit Cloud 환경 감지
IS_STREAMLIT_CLOUD = os.getenv("STREAMLIT_RUNTIME") is not None

# 환경에 따라 필요한 모듈만 import
try:
    if IS_STREAMLIT_CLOUD:
        import pymysql  # MySQL
    else:
        import pyodbc   # MSSQL
except ModuleNotFoundError as e:
    # pyodbc가 없는 Cloud 환경에서의 안전 처리
    if not IS_STREAMLIT_CLOUD:
        raise e

def get_connection():
    if IS_STREAMLIT_CLOUD:
        # Cloud → MySQL 연결
        return pymysql.connect(
            host=os.getenv('DB_SERVER'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    else:
        # 로컬 → MSSQL 연결
        return pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('DB_SERVER')};"
            f"DATABASE={os.getenv('DB_NAME')};"
            f"UID={os.getenv('DB_USER')};"
            f"PWD={os.getenv('DB_PASSWORD')}"
        )

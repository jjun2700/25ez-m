import os
from dotenv import load_dotenv

# 로컬 개발 환경에서만 .env 로드 (Cloud는 Secrets 사용)
load_dotenv()

# Streamlit Cloud 여부 감지
IS_STREAMLIT_CLOUD = os.getenv("STREAMLIT_RUNTIME") is not None

# 환경에 따라 필요한 모듈만 import
if IS_STREAMLIT_CLOUD:
    import pymssql  # MySQL
else:
    import pyodbc   # MSSQL

def get_connection():
    if IS_STREAMLIT_CLOUD:
        # Cloud 환경 → MySQL 사용
        return pymssql.connect(
            host=os.getenv('DB_SERVER'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    else:
        # 로컬 환경 → MSSQL 사용 (pyodbc)
        return pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('DB_SERVER')};"
            f"DATABASE={os.getenv('DB_NAME')};"
            f"UID={os.getenv('DB_USER')};"
            f"PWD={os.getenv('DB_PASSWORD')}"
        )

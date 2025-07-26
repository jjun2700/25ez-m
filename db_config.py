import os
from dotenv import load_dotenv

# .env 로드 (로컬에서만 유효)
load_dotenv()

# Streamlit Cloud 여부 감지
IS_STREAMLIT_CLOUD = os.getenv("STREAMLIT_RUNTIME") is not None

# 환경에 따라 필요한 모듈만 import
if IS_STREAMLIT_CLOUD:
    import pymysql  # Cloud → MySQL
else:
    try:
        import pyodbc  # 로컬 → MSSQL
    except ModuleNotFoundError:
        # 로컬에서도 pyodbc 설치 안 된 경우 에러 메시지
        raise ModuleNotFoundError("pyodbc 모듈이 설치되어 있지 않습니다. 로컬 MSSQL 연결을 위해 pyodbc를 설치하세요.")

def get_connection():
    if IS_STREAMLIT_CLOUD:
        # Cloud 환경 → MySQL 연결
        return pymysql.connect(
            host=os.getenv('DB_SERVER'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    else:
        # 로컬 환경 → MSSQL 연결
        return pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('DB_SERVER')};"
            f"DATABASE={os.getenv('DB_NAME')};"
            f"UID={os.getenv('DB_USER')};"
            f"PWD={os.getenv('DB_PASSWORD')}"
        )

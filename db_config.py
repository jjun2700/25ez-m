# db_config.py - DB 연결 구성

import os
from dotenv import load_dotenv
import pyodbc

load_dotenv()  # .env 파일에서 환경변수 로드

def get_connection():
    # MSSQL DB 연결 객체 반환
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')}"
    )

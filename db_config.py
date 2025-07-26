# db_config.py - MSSQL 연결 (pymssql) / Cloud 전용
import os
import pymssql  # MSSQL 드라이버 (리눅스 호환)

# Cloud 환경에서만 사용
IS_STREAMLIT_CLOUD = True

def get_connection():
    return pymssql.connect(
        server=os.getenv('DB_SERVER'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

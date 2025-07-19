# db_config.py - MSSQL DB 연결 구성 (pymssql 사용, Streamlit Cloud 호환)

import os
from dotenv import load_dotenv
import pymssql  # 리눅스에서도 작동 가능한 MSSQL 드라이버

load_dotenv()  # .env 파일에서 환경변수 로드

def get_connection():
    # MSSQL DB 연결 객체 반환 (pymssql 사용)
    return pymssql.connect(
        server=os.getenv('DB_SERVER'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

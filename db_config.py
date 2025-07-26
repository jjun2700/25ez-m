# 클라우드용

import os
import pymysql  # MySQL

# Cloud 환경에서는 .env 사용 안 하고 Streamlit Secrets 사용
IS_STREAMLIT_CLOUD = True

def get_connection():
    # MySQL 연결
    return pymysql.connect(
        host=os.getenv('DB_SERVER'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

import streamlit as st
import pandas as pd
from db_config import get_connection

# 사용자 인증 및 비밀번호 변경 관련 기능 정의
# 로그인, 로그아웃, 비밀번호 변경 UI와 로직을 포함함

def authenticate(user_id, password):
    # 사용자 ID와 비밀번호를 검증하는 함수
    conn = get_connection()
#    query = "SELECT * FROM M8_Person WHERE Person = ? AND PW = ?"
    query = "SELECT * FROM M8_Person WHERE Person = %s AND PW = %s"

    df = pd.read_sql(query, conn, params=[user_id, password])

    conn.close()
    return not df.empty


def render_login_form():
    # 로그인 폼 UI 및 로그인 처리 로직
    st.title("🔐 로그인")
    input_id = st.text_input("ID")
    input_pw = st.text_input("Password", type="password")

    if st.button("로그인"):
        if authenticate(input_id, input_pw):
            st.session_state.logged_in = True
            st.session_state.user_id = input_id
            log_login(input_id)  # 로그인 로그 기록
            st.success("로그인 성공")
            st.rerun()
        else:
            st.error("ID 또는 비밀번호가 틀렸습니다.")


def log_login(user_id):
    # 로그인 성공 시 M8_Log 테이블에 로그 기록
    try:
        conn = get_connection()
        cursor = conn.cursor()
#        cursor.execute("INSERT INTO M8_Log (TLog, Person, NProg, SInout) VALUES (GETDATE(), ?, 21, 'I')", [user_id])
        cursor.execute("INSERT INTO M8_Log (TLog, Person, NProg, SInout) VALUES (GETDATE(), %s, 21, 'I')", [user_id])
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.warning(f"로그 기록 중 오류 발생: {e}")


def render_user_info():
    # 로그인 후 사용자 정보, 로그아웃 버튼, 비밀번호 변경 toggle UI
    st.markdown(f"**👤 로그인 ID:** `{st.session_state.user_id}`")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.rerun()

    with col2:
        if st.toggle("PW 변경", key="pw_change_toggle"):
            render_password_change_form()


def render_password_change_form():
    # 비밀번호 변경 입력 폼 및 처리 로직
    st.markdown("---")
    st.subheader("🔒 비밀번호 변경")

    current_pw = st.text_input("현재 비밀번호", type="password")
    new_pw = st.text_input("새 비밀번호", type="password")
    confirm_pw = st.text_input("새 비밀번호 확인", type="password")

    if st.button("변경하기"):
        if new_pw != confirm_pw:
            st.error("새 비밀번호가 일치하지 않습니다.")
        elif len(new_pw) < 4:
            st.warning("비밀번호는 최소 4자 이상이어야 합니다.")
        else:
            conn = get_connection()
            check = pd.read_sql(
#                "SELECT * FROM M8_Person WHERE Person = ? AND PW = ?",
                "SELECT * FROM M8_Person WHERE Person = %s AND PW = %s",
                conn, params=[st.session_state.user_id, current_pw]
            )
            if check.empty:
                st.error("현재 비밀번호가 올바르지 않습니다.")
            else:
                cursor = conn.cursor()
                cursor.execute(
#                    "UPDATE M8_Person SET PW = ? WHERE Person = ?",
                    "UPDATE M8_Person SET PW = %s WHERE Person = %s",
                    [new_pw, st.session_state.user_id]
                )
                conn.commit()
                st.success("비밀번호가 성공적으로 변경되었습니다.")
            conn.close()

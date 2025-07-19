import streamlit as st
from db_config import get_connection
from auth import render_login_form, render_user_info, render_password_change_form
from sidebar import draw_sidebar_controls
from handlers import handle_pn_search, handle_order_going_search, handle_wip_search

# ----------------------------
# 세션 상태 초기화
# ----------------------------
# 로그인 여부, 사용자 ID, 검색 모드, 선택된 PN 정보를 세션 상태에 저장
for key, default in {
    "logged_in": False,
    "user_id": None,
    "search_mode": "",
    "selected_pn": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ----------------------------
# 사이드바 영역: 로그인 또는 사용자 정보 출력
# ----------------------------
with st.sidebar:
    if not st.session_state.logged_in:
        render_login_form()  # 로그인 폼 렌더링
    else:
        render_user_info()  # 사용자 정보 및 로그아웃, 비밀번호 변경

# ----------------------------
# 로그인 후 메인 기능 실행
# ----------------------------
if st.session_state.logged_in:
    draw_sidebar_controls()  # 검색 기능 포함 사이드바 UI 렌더링
    
    if st.session_state.get("show_pw_change"):
        # 🔹 토글 켜졌을 때 검색모드도 초기화
        st.session_state.search_mode = ""
        pass
    else:
        conn = get_connection()  # DB 연결

        # 검색 모드에 따라 다른 처리 실행
        match st.session_state.search_mode:
            case "pn_search":
                handle_pn_search(conn, st.session_state.selected_pn)
            case "order_going":
                handle_order_going_search(conn)
            case "wip_search":
                handle_wip_search(conn)
            case _:
                st.info("사이드바에서 PN을 입력하거나 검색 버튼을 눌러주세요.")

        conn.close()  # DB 연결 종료
else:
    st.info("사이드바에서 로그인을 해주세요.")

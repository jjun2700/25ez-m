import streamlit as st
from db_config import get_connection
from handlers import handle_pn_search, handle_order_going_search, handle_wip_search

def render_saw_tab():
    # ---- 1. 버튼 클릭 시 초기화 요청 처리 ----
    if st.session_state.get("reset_pn_input", False):
        st.session_state["pn_input"] = ""
        st.session_state["selected_pn"] = ""
        st.session_state["reset_pn_input"] = False

    # ---- 2. 검색 UI ----
    col1, col_dummy, col2, col3 = st.columns([1.2, 0.5, 1, 1])

    with col1:
#        st.markdown("#### 🔍")
        pn_input = st.text_input(
            "🖱️ PN 검색",
            value=st.session_state.get("selected_pn", ""),
            key="pn_input",
            placeholder="PN 입력"
        )

        col11, col12 = st.columns([1, 1])
        with col11:
            st.markdown("#### 🔍")

        with col12:
            if st.button(" 검색 "):
                st.session_state.search_mode = "pn_search"
                st.session_state.selected_pn = pn_input
                st.rerun()

    with col2:
        if st.button("미납수주 검색"):
            st.session_state["reset_pn_input"] = True  # 초기화 플래그 설정
            st.session_state.search_mode = "order_going"
            st.rerun()

        if st.button("재공 검색"):
            st.session_state["reset_pn_input"] = True  # 초기화 플래그 설정
            st.session_state.search_mode = "wip_search"
            st.rerun()

    with col3:
        if st.button("📁 생산지도서 검색"):
            search_query = st.session_state.get("pn_input", "")
            if search_query:
                drive_url = f"https://drive.google.com/drive/search?q={search_query}"
                js = f"window.open('{drive_url}')"
                st.components.v1.html(f"<script>{js}</script>")
            else:
                st.warning("PN을 먼저 입력해 주세요.")

        if st.button("🕵️‍♂️ 구글 검색"):
            search_query = st.session_state.get("pn_input", "")
            if search_query:
                google_url = f"https://www.google.com/search?q={search_query}"
                js = f"window.open('{google_url}')"
                st.components.v1.html(f"<script>{js}</script>")
            else:
                st.warning("PN을 먼저 입력해 주세요.")

    st.markdown("---")

    # --- 검색 결과 처리 ---
    if not st.session_state.get("show_pw_change"):
        conn = get_connection()
        match st.session_state.search_mode:
            case "pn_search":
                handle_pn_search(conn, st.session_state.selected_pn)
            case "order_going":
                handle_order_going_search(conn)
            case "wip_search":
                handle_wip_search(conn)
            case _:
                st.info("PN을 입력하거나 검색 버튼을 눌러주세요.")
        conn.close()

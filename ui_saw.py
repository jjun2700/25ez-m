import streamlit as st
from db_config import get_connection
from handlers import handle_pn_search, handle_order_going_search, handle_wip_search, handle_excess_quantity_search
from views import show_pn_details

def render_saw_tab():
    # ---- 1. 검색에서 선택한 PN 처리 ----
    if st.session_state.get("pn_search_completed", False):
        # 검색에서 선택한 PN을 입력창에 반영
        st.session_state["selected_pn"] = st.session_state.get("selected_pn_from_search", "")
        st.session_state["pn_input"] = st.session_state.get("selected_pn_from_search", "")
        st.session_state["pn_search_completed"] = False  # 플래그 초기화
        
        # 즉시 상세화면 표시할지 확인
        if st.session_state.get("show_details_immediately", False):
            st.session_state["search_mode"] = "show_details"  # 상세화면 표시 모드
            st.session_state["show_details_immediately"] = False
        else:
            st.session_state["search_mode"] = ""  # 일반적인 경우 검색 모드 초기화

    # ---- 2. 버튼 클릭 시 초기화 요청 처리 ----
    if st.session_state.get("reset_pn_input", False):
        st.session_state["pn_input"] = ""
        st.session_state["selected_pn"] = ""
        st.session_state["selected_pn_from_search"] = ""
        st.session_state["show_details_immediately"] = False
        st.session_state["reset_pn_input"] = False

    # ---- 3. 검색 UI ----
    col1, col_dummy, col2, col3 = st.columns([1.2, 0.5, 1, 1])

    with col1:
        # Session State에 키가 없으면 초기값 설정
        if "pn_input" not in st.session_state:
            st.session_state["pn_input"] = ""
            
        pn_input = st.text_input(
            "🖱️ PN 검색",
            key="pn_input",
            placeholder="PN 입력"
        )

        # 입력값이 변경되면 selected_pn 업데이트
        if pn_input != st.session_state.get("selected_pn", ""):
            st.session_state["selected_pn"] = pn_input
            # 검색에서 선택한 PN 정보 클리어 (사용자가 직접 수정한 경우)
            if "selected_pn_from_search" in st.session_state:
                del st.session_state["selected_pn_from_search"]
            # 상세화면 표시 플래그도 클리어
            st.session_state["show_details_immediately"] = False

        col11, col12 = st.columns([1, 1])
        with col11:
            st.markdown("#### 🔍")

        with col12:
            if st.button(" 검색 "):
                if pn_input.strip():
                    st.session_state.search_mode = "pn_search"
                    st.session_state.selected_pn = pn_input.strip()
                    st.rerun()
                else:
                    st.warning("PN을 입력해 주세요.")

    with col2:
        if st.button("재공 검색"):
            st.session_state["reset_pn_input"] = True  # 초기화 플래그 설정
            st.session_state.search_mode = "wip_search"
            st.rerun()
        
        if st.button("미납수주 검색"):
            st.session_state["reset_pn_input"] = True  # 초기화 플래그 설정
            st.session_state.search_mode = "order_going"
            st.rerun()

        if st.button("초과수량 검색"):
            st.session_state["reset_pn_input"] = True  # 초기화 플래그 설정
            st.session_state.search_mode = "excess_quantity_search"
            st.rerun()

    with col3:
        if st.button("📁 생산지도서 검색"):
            # 현재 입력창의 값 사용
            search_query = st.session_state.get("pn_input", "").strip()
            if search_query:
                drive_url = f"https://drive.google.com/drive/search?q={search_query}"
                js = f"window.open('{drive_url}')"
                st.components.v1.html(f"<script>{js}</script>")
            else:
                st.warning("PN을 먼저 입력해 주세요.")

        if st.button("🕵️‍♂️ 구글 검색"):
            # 현재 입력창의 값 사용
            search_query = st.session_state.get("pn_input", "").strip()
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
                if st.session_state.selected_pn.strip():
                    handle_pn_search(conn, st.session_state.selected_pn.strip())
            case "show_details":
                # 선택한 PN의 상세정보 바로 표시
                selected_pn = st.session_state.get("selected_pn", "").strip()
                if selected_pn:
#                    st.success(f"[{selected_pn}] PN 상세정보를 표시합니다.")
                    st.markdown(f"#### 🎯 **----- 제품 상세 정보 [{selected_pn}] -----**")
                    show_pn_details(conn, selected_pn)
                st.session_state.search_mode = ""  # 표시 후 모드 초기화
            case "order_going":
                handle_order_going_search(conn)
            case "wip_search":
                handle_wip_search(conn)
            case "excess_quantity_search":  # 새로 추가된 케이스
                handle_excess_quantity_search(conn)
            case _:
                st.info("PN을 입력하거나 검색 버튼을 눌러주세요.")
        conn.close()

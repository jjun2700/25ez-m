import streamlit as st

# 사이드바 UI 구성 함수
# PN 검색, 미납수주 검색, 재공 검색 기능을 제공

def draw_sidebar_controls():
    with st.sidebar:
        st.divider()

        # PN 직접 입력 후 검색
        st.subheader("🔎 PN 검색")
        pn_input = st.text_input("PN 입력", value=st.session_state.get("selected_pn", ""), key="pn_input")

        if st.button("PN 검색"):
            st.session_state.search_mode = "pn_search"  # 검색 모드 설정
            st.session_state.selected_pn = pn_input     # 입력된 PN 저장
            st.rerun()  # 앱 다시 실행

        st.divider()

        # 미납수주 또는 재공 목록을 통한 PN 선택 검색
        st.subheader("📦 미납수주 및 재공 검색")

        if st.button("미납수주 검색"):
            st.session_state.search_mode = "order_going"  # 검색 모드 설정
            st.rerun()

        if st.button("재공 검색"):
            st.session_state.search_mode = "wip_search"  # 검색 모드 설정
            st.rerun()

        st.divider()
        st.subheader("🌐 인터넷 검색")

        # ✅ 생산지도서 검색 버튼 추가
        if st.button("📁 생산지도서 검색"):
            search_query = st.session_state.get("pn_input", "")
            if search_query:
                drive_url = f"https://drive.google.com/drive/search?q={search_query}"
                js = f"window.open('{drive_url}')"  # 새 탭으로 열기
                st.components.v1.html(f"<script>{js}</script>")
            else:
                st.warning("PN을 먼저 입력해 주세요.")

        # 🕵️‍♂️ 구글 웹 검색
        if st.button("🕵️‍♂️ 구글 검색"):
            search_query = st.session_state.get("pn_input", "")
            if search_query:
                google_url = f"https://www.google.com/search?q={search_query}"
                js = f"window.open('{google_url}')"
                st.components.v1.html(f"<script>{js}</script>")
            else:
                st.warning("PN을 먼저 입력해 주세요.")
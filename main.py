import streamlit as st
from auth import render_login_form, render_user_info
from ui_saw import render_saw_tab
from ui_microwave import render_microwave_tab
from ui_project import render_project_tab

# ----------------------------
# 세션 상태 초기화
# ----------------------------
for key, default in {
    "logged_in": False,
    "user_id": None,
    "search_mode": "",
    "selected_pn": "",
    "selected_pn_from_search": "",  # 추가: 검색에서 선택한 PN 저장
    "pn_search_completed": False    # 추가: 검색 완료 플래그
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ----------------------------
# 사이드바: 로그인/로그아웃
# ----------------------------
with st.sidebar:
    if not st.session_state.logged_in:
        render_login_form()
    else:
        render_user_info()

# ----------------------------
# 로그인 후 탭 UI 표시
# ----------------------------
if st.session_state.logged_in:

    st.markdown("""
        <style>
        /* 비활성 탭 버튼 텍스트 */
        div[data-testid="stTabs"] button[role="tab"] > div > p,
        div[data-testid="stTabs"] button[role="tab"] > div > span {
            font-size: 18px !important;     /* 글자 크기 키움 */
            font-weight: 500 !important;    /* 중간 두께 */
            color: #777 !important;         /* 회색 글씨 */
            margin: 0 !important;
        }
                
        /* 활성 탭 버튼 텍스트 */
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] > div > p,
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] > div > span {
            font-size: 24px !important;     /* 글자 더 크게 */
            font-weight: bold !important;   /* 굵게 */
            color: #000 !important;         /* 검정색 글씨 */
            margin: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["SAW", "Microwave", "Project"])

    with tabs[0]:
        render_saw_tab()

    with tabs[1]:
        render_microwave_tab()

    with tabs[2]:
        render_project_tab()

else:
    st.info("사이드바에서 로그인을 해주세요.")                
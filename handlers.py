import streamlit as st
import pandas as pd
from db_config import get_connection, IS_STREAMLIT_CLOUD

# 핸들러 함수 정의
# 검색 모드에 따른 데이터 처리 로직 포함
from views import show_pn_details

def handle_pn_search(conn, pn_input):
    # PN 검색 결과를 보여주고 사용자가 하나를 선택하면 상세정보 표시
    if IS_STREAMLIT_CLOUD:
        query = "SELECT DISTINCT PN_l AS PN FROM M8_LOT WHERE PN_l LIKE %s ORDER BY PN"
    else:
        query = "SELECT DISTINCT PN_l AS PN FROM M8_LOT WHERE PN_l LIKE ? ORDER BY PN"

    df = pd.read_sql(query, conn, params=[pn_input + '%'])

    if df.empty:
        st.warning("조건에 맞는 PN이 없습니다.")
        return

    df["선택"] = False
    st.subheader("✅ PN 리스트 (하나만 선택 가능)", divider=True)
    edited_df = st.data_editor(df, use_container_width=True, num_rows="fixed", key="pn_table")
    selected_rows = edited_df[edited_df["선택"] == True]

    if len(selected_rows) > 1:
        st.error("⚠️ 하나만 선택해 주세요.")
    elif len(selected_rows) == 1:
        selected_pn = selected_rows.iloc[0]["PN"]
        st.success(f"[{selected_pn}] PN을 선택하셨습니다.")
        show_pn_details(conn, selected_pn)
    else:
        st.info("→ 하나의 PN을 선택해 주세요.")

def handle_order_going_search(conn):
    # 전체 미납 수주 리스트를 표시하고 사용자가 선택한 PN으로 전환
    query = '''
        SELECT DDeadline_g AS 납기일, PN_g AS PN, QResidual_g AS 미납수량, Customer_g AS 고객명, TypeOut_g AS 구분, PKG_g AS 패키지
        FROM M8_Order_Going
        ORDER BY 납기일
    '''
    df = pd.read_sql(query, conn)
    pn_index = df.columns.get_loc("PN") + 1
    df.insert(pn_index, "선택", False)

    st.subheader("🛒 미납 수주 현황", divider=True)
    edited_df = st.data_editor(df, use_container_width=True, num_rows="fixed", key="order_table")
    selected_rows = edited_df[edited_df["선택"] == True]

    if len(selected_rows) < 1:
        st.info("→ 하나의 PN을 선택해 주세요.")
    else:
        st.session_state.selected_pn = selected_rows.iloc[0]["PN"]
        st.session_state.search_mode = "pn_search"
        st.rerun()

def handle_wip_search(conn):
    # 전체 재공 리스트를 표시하고 사용자가 선택한 PN으로 전환
    query = '''
        SELECT PN_w AS PN, LN_w AS LN, SWIP_w AS 공정, QWFR_w AS 웨이퍼, QHMG_w AS 반제품, ND_w As NetDie, EYield_w As 예상수율, QGoods_w As 예상양품, NDate_Do_w AS 작업일
        FROM M8_LOT_WIP
        ORDER BY 작업일
    '''
    df = pd.read_sql(query, conn)
    pn_index = df.columns.get_loc("PN") + 1
    df.insert(pn_index, "선택", False)

    st.subheader("📦 재공 현황", divider=True)
    edited_df = st.data_editor(df, use_container_width=True, num_rows="fixed", key="wip_table")
    selected_rows = edited_df[edited_df["선택"] == True]

    if len(selected_rows) < 1:
        st.info("→ 하나의 PN을 선택해 주세요.")
    else:
        st.session_state.selected_pn = selected_rows.iloc[0]["PN"]
        st.session_state.search_mode = "pn_search"
        st.rerun()

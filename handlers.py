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

    # 검색 결과가 1개인 경우 자동으로 선택하고 상세정보 표시
    if len(df) == 1:
        selected_pn = df.iloc[0]["PN"]
#        st.success(f"[{selected_pn}] PN을 자동 선택했습니다.")
        st.markdown(f"#### 🎯 **----- 제품 상세 정보 [{selected_pn}] -----**")
        show_pn_details(conn, selected_pn)
        return

    # 검색 결과가 여러개인 경우 선택 UI 제공
    df["선택"] = False
    st.subheader("✅ PN 리스트 (하나만 선택 가능)", divider=True)
    
    # 선택 상태를 위한 unique key 생성
    table_key = f"pn_table_{hash(pn_input)}"
    edited_df = st.data_editor(df, use_container_width=True, num_rows="fixed", key=table_key)
    selected_rows = edited_df[edited_df["선택"] == True]

    if len(selected_rows) > 1:
        st.error("⚠️ 하나만 선택해 주세요.")
    elif len(selected_rows) == 1:
        selected_pn = selected_rows.iloc[0]["PN"]
        
        # 선택한 PN을 session_state에 저장
        st.session_state.selected_pn_from_search = selected_pn
        st.session_state.pn_search_completed = True
        st.session_state.show_details_immediately = True  # 즉시 상세화면 표시 플래그
        
        st.success(f"[{selected_pn}] PN을 선택하셨습니다.")
        
        # 페이지 새로고침하여 입력창 업데이트 및 상세화면 표시
        st.rerun()
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
        st.session_state.selected_pn_from_search = selected_rows.iloc[0]["PN"]
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
        st.session_state.selected_pn_from_search = selected_rows.iloc[0]["PN"]
        st.session_state.search_mode = "pn_search"
        st.rerun()

def handle_excess_quantity_search(conn):
    """초과수량 검색 - SQL Server용 JOIN 최적화 버전"""
    
    if IS_STREAMLIT_CLOUD:
        # Streamlit Cloud용 쿼리 (MySQL/PostgreSQL 스타일)
        query = '''
        SELECT 
            o.PN,
            COALESCE(s.stock_total, 0) as stock_total,
            COALESCE(w.wip_total, 0) as wip_total,
            o.order_g_total,
            COALESCE(c.customer_name, '-') as customer_name,
            (COALESCE(s.stock_total, 0) + COALESCE(w.wip_total, 0) - o.order_g_total) as excess_quantity
        FROM (
            SELECT 
                PN_g AS PN,
                SUM(QResidual_g) as order_g_total
            FROM M8_Order_Going
            GROUP BY PN_g
        ) o
        LEFT JOIN (
            SELECT 
                PN_s AS PN,
                SUM(Qty_s) as stock_total
            FROM M8_MG_Stock
            GROUP BY PN_s
        ) s ON o.PN = s.PN
        LEFT JOIN (
            SELECT 
                PN_w AS PN,
                SUM(QGoods_w) as wip_total
            FROM M8_LOT_WIP
            GROUP BY PN_w
        ) w ON o.PN = w.PN
        LEFT JOIN (
            SELECT DISTINCT
                PN_g AS PN,
                FIRST_VALUE(Customer_g) OVER (PARTITION BY PN_g ORDER BY DDeadline_g ASC) as customer_name
            FROM M8_Order_Going
        ) c ON o.PN = c.PN
        ORDER BY excess_quantity ASC
        '''
    else:
        # SQL Server용 쿼리
        query = '''
        SELECT 
            o.PN,
            COALESCE(s.stock_total, 0) as stock_total,
            COALESCE(w.wip_total, 0) as wip_total,
            o.order_g_total,
            COALESCE(c.customer_name, '-') as customer_name,
            (COALESCE(s.stock_total, 0) + COALESCE(w.wip_total, 0) - o.order_g_total) as excess_quantity
        FROM (
            SELECT 
                PN_g AS PN,
                SUM(QResidual_g) as order_g_total
            FROM M8_Order_Going
            GROUP BY PN_g
        ) o
        LEFT JOIN (
            SELECT 
                PN_s AS PN,
                SUM(Qty_s) as stock_total
            FROM M8_MG_Stock
            GROUP BY PN_s
        ) s ON o.PN = s.PN
        LEFT JOIN (
            SELECT 
                PN_w AS PN,
                SUM(QGoods_w) as wip_total
            FROM M8_LOT_WIP
            GROUP BY PN_w
        ) w ON o.PN = w.PN
        LEFT JOIN (
            SELECT DISTINCT
                PN_g AS PN,
                FIRST_VALUE(Customer_g) OVER (PARTITION BY PN_g ORDER BY DDeadline_g ASC) as customer_name
            FROM M8_Order_Going
        ) c ON o.PN = c.PN
        ORDER BY excess_quantity ASC
        '''
    
    try:
        # 한 번의 쿼리로 모든 데이터 조회
        df_result = pd.read_sql(query, conn)
        
        if df_result.empty:
            st.warning("미납수주 데이터가 없습니다.")
            return
        
        # 결과 데이터 정리
        result_data = []
        for _, row in df_result.iterrows():
            result_data.append({
                'PN': row['PN'],
                '선택': False,
                '초과수량': int(row['excess_quantity']),
                '고객명': row['customer_name'] if pd.notna(row['customer_name']) else "-",
                '재고합계': int(row['stock_total']) if pd.notna(row['stock_total']) else 0,
                '재공합계': int(row['wip_total']) if pd.notna(row['wip_total']) else 0,
                '미납수주합계': int(row['order_g_total']) if pd.notna(row['order_g_total']) else 0
            })
        
        # 데이터프레임 생성
        df = pd.DataFrame(result_data)
        
        if df.empty:
            st.warning("계산할 데이터가 없습니다.")
            return
        
    except Exception as e:
        st.error(f"데이터베이스 쿼리 실행 중 오류가 발생했습니다: {str(e)}")
        st.info("기존 방식으로 처리합니다...")
        
        # 기존 for 문 방식으로 fallback
        handle_excess_quantity_search_fallback(conn)
        return
    
    # 나머지 UI 코드는 기존과 동일...
    st.subheader("📊 초과 수량 현황", divider=True)
    
    # 요약 정보
    total_negative = len(df[df['초과수량'] < 0])
    total_positive = len(df[df['초과수량'] >= 0])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("전체 PN 수", len(df))
    with col2:
        st.metric("충분 PN 수", total_positive)
    with col3:
        st.markdown(
            f"""
            <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.25rem;">부족 PN 수</div>
            <div style="font-size: 2rem; font-weight: 600; color: #ff4b4b;">{total_negative}</div>
            """,
            unsafe_allow_html=True
        )

    # 초과수량에 따른 시각적 표시
    def format_excess_quantity(value):
        if value < -1000:
            return f"🔴 {value:,}"
        elif value < -100:
            return f"🟠 {value:,}"
        elif value < 0:
            return f"🟡 {value:,}"
        elif value < 10:
            return f"⚪ {value:,}"
        else:
            return f"🟢 {value:,}"
    
    # 표시용 컬럼 추가
    df['상태'] = df['초과수량'].apply(format_excess_quantity)
    
    # 데이터 에디터
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        num_rows="fixed", 
        key="excess_quantity_table",
        column_config={
            "PN": st.column_config.TextColumn("PN", width="medium"),
            "선택": st.column_config.CheckboxColumn("선택", width="small"),
            "상태": st.column_config.TextColumn(
                "초과수량", 
                width="medium",
                help="🔴매우부족 🟠부족 🟡약간부족 ⚪약간여유 🟢충분"
            ),
            "재고합계": st.column_config.NumberColumn("재고합계", format="%d"),
            "재공합계": st.column_config.NumberColumn("재공합계", format="%d"),
            "미납수주합계": st.column_config.NumberColumn("미납수주합계", format="%d")
        },
        column_order=["PN", "선택", "상태", "고객명", "재고합계", "재공합계", "미납수주합계"]
    )
    
    # 선택된 행 처리
    selected_rows = edited_df[edited_df["선택"] == True]
    
    if len(selected_rows) > 1:
        st.error("⚠️ 하나만 선택해 주세요.")
    elif len(selected_rows) == 1:
        selected_pn = selected_rows.iloc[0]["PN"]
        
        st.session_state.selected_pn_from_search = selected_pn
        st.session_state.pn_search_completed = True
        st.session_state.show_details_immediately = True
        
        st.success(f"[{selected_pn}] PN을 선택하셨습니다.")
        st.rerun()
    else:
        st.info("→ 상세정보를 보려면 하나의 PN을 선택해 주세요.")


def handle_excess_quantity_search_fallback(conn):
    """기존 for 문 방식 (fallback용)"""
    # 기존 코드를 여기에 복사해서 사용
    unique_pn_query = "SELECT DISTINCT PN_g AS PN FROM M8_Order_Going ORDER BY PN"
    unique_pns = pd.read_sql(unique_pn_query, conn)
    
    if unique_pns.empty:
        st.warning("미납수주 데이터가 없습니다.")
        return
    
    result_data = []
    
    for _, row in unique_pns.iterrows():
        pn = row['PN']
        
        # 재고합계 조회
        if IS_STREAMLIT_CLOUD:
            stock_query = "SELECT COALESCE(SUM(Qty_s), 0) as stock_total FROM M8_MG_Stock WHERE PN_s = %s"
        else:
            stock_query = "SELECT COALESCE(SUM(Qty_s), 0) as stock_total FROM M8_MG_Stock WHERE PN_s = ?"
        
        stock_result = pd.read_sql(stock_query, conn, params=[pn])
        stock_total = stock_result.iloc[0]['stock_total'] if not stock_result.empty else 0
        
        # 재공합계 조회
        if IS_STREAMLIT_CLOUD:
            wip_query = "SELECT COALESCE(SUM(QGoods_w), 0) as wip_total FROM M8_LOT_WIP WHERE PN_w = %s"
        else:
            wip_query = "SELECT COALESCE(SUM(QGoods_w), 0) as wip_total FROM M8_LOT_WIP WHERE PN_w = ?"
        
        wip_result = pd.read_sql(wip_query, conn, params=[pn])
        wip_total = wip_result.iloc[0]['wip_total'] if not wip_result.empty else 0
        
        # 미납수주합계 조회
        if IS_STREAMLIT_CLOUD:
            order_query = "SELECT COALESCE(SUM(QResidual_g), 0) as order_g_total FROM M8_Order_Going WHERE PN_g = %s"
        else:
            order_query = "SELECT COALESCE(SUM(QResidual_g), 0) as order_g_total FROM M8_Order_Going WHERE PN_g = ?"
        
        order_result = pd.read_sql(order_query, conn, params=[pn])
        order_g_total = order_result.iloc[0]['order_g_total'] if not order_result.empty else 0
        
        # 고객명 조회
        if IS_STREAMLIT_CLOUD:
            customer_query = "SELECT Customer_g FROM M8_Order_Going WHERE PN_g = %s ORDER BY DDeadline_g ASC LIMIT 1"
        else:
            customer_query = "SELECT TOP 1 Customer_g FROM M8_Order_Going WHERE PN_g = ? ORDER BY DDeadline_g ASC"

        customer_result = pd.read_sql(customer_query, conn, params=[pn])
        customer_name = customer_result.iloc[0]['Customer_g'] if not customer_result.empty else "-"

        # 초과수량 계산
        excess_quantity = stock_total + wip_total - order_g_total
        
        result_data.append({
            'PN': pn,
            '선택': False,
            '초과수량': int(excess_quantity),
            '고객명': customer_name,
            '재고합계': int(stock_total),
            '재공합계': int(wip_total),
            '미납수주합계': int(order_g_total)
        })
    
    # 나머지 처리는 기존과 동일...

# views.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show_pn_details(conn, pn):
    # 상세 정보 시각화 코드...

    # 재고 현황
    query = '''
    SELECT PN_s As PN, LN_s As LN, Qty_s As 재고수량 
    FROM M8_MG_Stock WHERE PN_s = ? ORDER BY LN DESC
    '''
    stock_df = pd.read_sql(query, conn, params=[pn])
    total_qty = stock_df["재고수량"].sum()

    st.subheader("🔸 재고 현황", divider=True)
    st.markdown(    # 합계 표시
        f"<div style='text-align:right; font-size:15px; color:#333; font-weight:bold;'>   재고 합계 : {total_qty:,} </div>",
        unsafe_allow_html=True
    )
    st.dataframe(stock_df)

    # 재공 현황

    query = '''
        SELECT LN_w AS LN, PN_w AS PN, SWIP_w AS 공정, NDate_Do_w AS 작업일,     
               QWFR_w AS 웨이퍼, QHMG_w AS 반제품, ND_w As NetDie, EYield_w As 예상수율, QGoods_w As 예상양품
        FROM M8_LOT_WIP WHERE PN_w = ?
        ORDER BY 작업일
    '''
    wip_df = pd.read_sql(query, conn, params=[pn])
    total_qty = wip_df["예상양품"].sum()

    st.markdown(    # 합계 표시
        f"<div style='text-align:right; font-size:15px; color:#333; font-weight:bold;'>   재공 합계 : {total_qty:,} </div>",
        unsafe_allow_html=True
    )

    with st.expander("재공 현황"):
        st.dataframe(wip_df)


    # 미납 수주
    query = '''
    SELECT DDeadline_g As 납기일, PN_g As PN, TypeOut_g As 구분, PKG_g As 패키지, Customer_g As 고객명, QResidual_g As 미납수량 
    FROM M8_Order_Going WHERE PN_g = ? ORDER BY 납기일
    '''
    order_g_df = pd.read_sql(query, conn, params=[pn])
    total_qty = order_g_df["미납수량"].sum()

    st.subheader("🔸 미납 수주 현황", divider=True)
    st.markdown(    # 합계 표시
        f"<div style='text-align:right; font-size:15px; color:#333; font-weight:bold;'> 미납 합계 : {total_qty:,} </div>",        
        unsafe_allow_html=True
    )
    st.dataframe(order_g_df)


    # 납품 정보
    query = '''
    SELECT DDelivery_f As 일자, PN_f As PN, TypeOut_f As 구분, PKG_f As 패키지, Customer_f As 고객명, QDelivery_f As 납품수량 
    FROM M8_Order_Finish WHERE PN_f = ? ORDER BY 일자 DESC
    '''
    delivery_df = pd.read_sql(query, conn, params=[pn])
    total_qty = delivery_df["납품수량"].sum()

    st.markdown(    # 합계 표시
        f"<div style='text-align:right; font-size:15px; color:#333; font-weight:bold;'>   납품 합계 : {total_qty:,} </div>",
        unsafe_allow_html=True
    )

    with st.expander("납품 현황"):
        st.dataframe(delivery_df)


    # PN 특이사항
    query = '''
    SELECT No_n As No, WDate_n As 일자, WPerson_n As 작성자, Notice_n As 주의사항 
    FROM M8_Notice_PN WHERE PN_n = ? ORDER BY 일자 DESC, No DESC
    '''
    st.subheader("🔸 PN 특이사항", divider=True)
    st.dataframe(pd.read_sql(query, conn, params=[pn]))

    # LN 특이사항
    query = '''
    SELECT N.WDate_n As 작성일, N.WPerson_n As 작성자, L.PN_l As PN, L.LN_l As LN, N.Notice_n As 주의사항 
    FROM M8_LOT L 
    JOIN M8_Notice_LN N ON L.LN_l = N.LN_n
    WHERE L.PN_l = ? 
    ORDER BY 작성일 DESC
    '''
    with st.expander("LN 특이사항"):
        st.dataframe(pd.read_sql(query, conn, params=[pn]))


    # 수율 데이터 쿼리
    query = '''
    SELECT NDate_dt As 공정일, PN_dt As PN, LN_dt As LN, QN_dt As 투입수, QP_dt As 통과수,
        (CAST(QP_dt AS FLOAT) / NULLIF(QN_dt, 0) * 100) AS 수율 
    FROM M8_LOT_Do_Test
    WHERE PN_dt = ?
    ORDER BY LN DESC
    '''
    st.subheader("🔸 LOT 수율", divider=True)

    dotest_df = pd.read_sql(query, conn, params=[pn])
    dotest_df["수율"] = dotest_df["수율"].round(1)
    total_qty = dotest_df["통과수"].sum()

    # 최근 10개 수율 데이터 선택
    recent_df = dotest_df.head(10)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(recent_df["LN"], recent_df["수율"], marker='o', linestyle='-', color='blue')
    ax.invert_xaxis()

    # 수율 값 라벨 추가
    for x, y in zip(recent_df["LN"], recent_df["수율"]):
        ax.text(x, y + 2, f"{y:.1f}", ha='center', va='bottom', fontsize=12, fontweight='bold')

    # 그래프 스타일 설정
    #ax.set_title("LOT 수율 추이", fontsize=14, fontweight='bold')
    ax.set_ylabel("Yield (%)", fontsize=12)
    ax.set_ylim(0, 110)
    ax.grid(True)
    plt.xticks(rotation=10)

    st.pyplot(fig)  # Streamlit 앱에 그래프 출력

    # 테이블은 접기(expander)에 넣기
    st.markdown(
        f"<div style='text-align:right; font-size:15px; color:#333; font-weight:bold;'> 생산 누계 : {total_qty:,}</div>",
        unsafe_allow_html=True
    )
    with st.expander("▶ 수율 데이터 보기"):
        st.dataframe(dotest_df)
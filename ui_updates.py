import streamlit as st

def render_updates_tab():
    st.subheader("📋 웹 업데이트")
    
    # 2025-08-02 업데이트
    with st.container():
        #st.subheader("2025-08-02")
        st.markdown("##### 🔄 2025-08-02")
        st.info("""
        **초과수량 검색 기능 추가**
        
        ✅ <초과수량 검색> 버튼 추가  
        ✅ "상세 페이지"에 초과 수량 표시 추가  
                
        """)
    
    # 새 업데이트 추가 예시:
    # with st.container():
    #     st.subheader("2025-08-05")
    #     st.success("""
    #     **검색 속도 개선**
    #     
    #     ⚡ SAW 검색 응답시간 50% 단축  
    #     ⚡ Microwave 필터링 성능 개선  
    #     ⚡ 데이터베이스 인덱스 최적화
    #     """)

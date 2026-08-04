import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="실시간 ELS/ELB 큐레이터", layout="wide")

today_str = datetime.now().strftime("%Y년 %m월 %d일")
st.title("📢 실시간 ELS/ELB 추천 브리핑")
st.caption(f"오늘({today_str}) 기준 실시간 청약/공모 중인 ELS/ELB 정보입니다.")

# ---------------------------------------------------------
# 1. 네이버 금융 ELS 실시간 데이터 수집 함수
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def get_realtime_els():
    url = "https://finance.naver.com/research/els_list.naver"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 테이블 파싱
        table = soup.find("table", {"class": "type_1"})
        if not table:
            return pd.DataFrame(), "현재 청약 가능/공시된 ELS 상품을 찾을 수 없습니다."
            
        rows = table.find_all("tr")
        data_list = []
        
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 6:
                sec_company = cols[0].text.strip()
                item_name = cols[1].text.strip()
                underlying = cols[2].text.strip()
                rate_text = cols[3].text.strip().replace("%", "")
                due_date = cols[5].text.strip()
                
                # 제시수익률 숫자 변환
                try:
                    rate = float(rate_text)
                except ValueError:
                    rate = 0.0
                    
                data_list.append({
                    "증권사": sec_company,
                    "종목명": item_name,
                    "기초자산": underlying,
                    "제시수익률": rate,
                    "청약마감": due_date
                })
                
        if not data_list:
            return pd.DataFrame(), "현재 진행 중인 ELS 청약 목록이 없습니다."
            
        return pd.DataFrame(data_list), None
        
    except Exception as e:
        return pd.DataFrame(), f"실시간 데이터 수집 중 오류 발생: {str(e)}"

# ---------------------------------------------------------
# 2. 데이터 불러오기 및 정제
# ---------------------------------------------------------
with st.spinner("실시간 ELS/ELB 데이터를 가져오는 중입니다..."):
    df_raw, error = get_realtime_els()

if error:
    st.warning(f"💡 {error}")
elif df_raw.empty:
    st.info("현재 청약 진행 중인 ELS/ELB 상품이 없습니다.")
else:
    # 수익률 높은 순 정렬
    df_sorted = df_raw.sort_values(by="제시수익률", ascending=False).reset_index(drop=True)

    # ---------------------------------------------------------
    # 3. 챗봇 브리핑 텍스트 생성 (카톡 복사용)
    # ---------------------------------------------------------
    medals = ["🥇", "🥈", "🥉"]
    briefing_text = f"📢 [{today_str} 실시간 ELS/ELB 큐레이션]\n-------------------------------------\n"
    
    top_items = df_sorted.head(10)
    for idx, row in top_items.iterrows():
        medal = medals[idx] if idx < 3 else "▪️"
        briefing_text += f"{medal} {row['증권사']} {row['종목명']}({row['제시수익률']}%) {row['기초자산']} ~{row['청약마감']}\n"

    briefing_text += "\n-------------------------------------\n⚠️ [투자 유의사항]\n본 정보는 참고용이며, 상세 청약 조건은 해당 증권사를 통해 반드시 확인하세요."

    # ---------------------------------------------------------
    # 4. 화면 출력
    # ---------------------------------------------------------
    st.subheader("📋 카카오톡 / 텔레그램 복사용 브리핑")
    st.code(briefing_text, language="text")

    st.divider()
    st.subheader("📊 오늘의 청약 ELS/ELB 전체 목록")
    st.dataframe(df_sorted, use_container_width=True, hide_index=True)

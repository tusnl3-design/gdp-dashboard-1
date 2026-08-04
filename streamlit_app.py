import streamlit as st
import pandas as pd

st.set_page_config(page_title="ELS 비교기", layout="wide")

st.title("📊 증권사별 ELS 조건 비교")

# 💡 공공데이터포털 API 키 승인 반영을 기다리는 동안 화면 레이아웃을 확인하는 가상 데이터
@st.cache_data(ttl=3600)
def fetch_dummy_els_data():
    data = [
        {"증권사": "미래에셋증권", "종목명": "제3456회 ELS", "기초자산": "S&P500 / EUROSTOXX50", "낙인(KI)": "50%", "수익률(연)": "7.5%", "청약종료일": "2026-08-10"},
        {"증권사": "삼성증권", "종목명": "제8910회 ELS", "기초자산": "KOSPI200 / S&P500", "낙인(KI)": "45%", "수익률(연)": "6.8%", "청약종료일": "2026-08-12"},
        {"증권사": "한국투자증권", "종목명": "제1234회 ELS", "기초자산": "테슬라 / 엔비디아", "낙인(KI)": "60%", "수익률(연)": "11.2%", "청약종료일": "2026-08-11"},
        {"증권사": "KB증권", "종목명": "제5678회 ELS", "기초자산": "S&P500 / Nikkei225", "낙인(KI)": "50%", "수익률(연)": "7.0%", "청약종료일": "2026-08-15"}
    ]
    return pd.DataFrame(data), None

# 데이터 로드
df, err = fetch_dummy_els_data()

if err:
    st.error(f"⚠️ {err}")
else:
    st.info("ℹ️ 현재 공공데이터포털 인증키의 서버 반영 대기 중이므로, UI 및 기능 테스트용 샘플 데이터를 표시합니다.")
    st.success(f"🎉 성공적으로 데이터를 불러왔습니다! (총 {len(df)}건)")
    
    # 화면 출력 및 표 가공
    st.dataframe(df, use_container_width=True, hide_index=True)

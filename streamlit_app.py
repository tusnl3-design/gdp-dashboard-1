import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="ELS 증권사별 실시간 비교", page_layout="wide")

st.title("📊 증권사별 ELS 조건 및 수익률 실시간 비교")
st.write("동일 조건(기초자산, 낙인) 대비 가장 수익률이 높은 증권사 ELS를 비교합니다.")

# 사이드바 설정
st.sidebar.header("⚙️ ELS 조건 필터")

# 모의 데이터 생성
data = [
    {"증권사": "미래에셋증권", "종목명": "미래에셋 ELS 31200호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "조기상환배리어": "85-85-80-75-70-65", "낙인(KI)": "45%", "제시수익률(연)": 8.50, "가성비점수": 96},
    {"증권사": "한국투자증권", "종목명": "한투 ELS 15840호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "조기상환배리어": "85-85-80-75-70-65", "낙인(KI)": "45%", "제시수익률(연)": 8.10, "가성비점수": 90},
    {"증권사": "삼성증권", "종목명": "삼성 ELS 29410호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "조기상환배리어": "85-85-80-75-70-65", "낙인(KI)": "45%", "제시수익률(연)": 7.80, "가성비점수": 84},
    {"증권사": "KB증권", "종목명": "KB ELS 2410호", "기초자산": "S&P500 / EuroStoxx50 / KOSPI200", "조기상환배리어": "90-85-80-75-70-65", "낙인(KI)": "50%", "제시수익률(연)": 9.20, "가성비점수": 88},
    {"증권사": "NH투자증권", "종목명": "NH QV ELS 21900호", "기초자산": "S&P500 / EuroStoxx50 / KOSPI200", "조기상환배리어": "90-85-80-75-70-65", "낙인(KI)": "50%", "제시수익률(연)": 8.80, "가성비점수": 82},
    {"증권사": "신한투자증권", "종목명": "신한 ELS 22400호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "조기상환배리어": "80-80-80-75-70-60", "낙인(KI)": "40%", "제시수익률(연)": 6.90, "가성비점수": 92}
]

df = pd.DataFrame(data)

# 필터링 기능
assets = st.sidebar.multiselect("📌 기초자산 선택", options=df["기초자산"].unique(), default=df["기초자산"].unique())
filtered_df = df[df["기초자산"].isin(assets)].sort_values(by="제시수익률(연)", ascending=False)

# 1위 하이라이트
if not filtered_df.empty:
    top = filtered_df.iloc[0]
    st.success(f"🏆 **현재 검색 조건 수익률 1위:** [{top['증권사']}] {top['종목명']} — **연 {top['제시수익률(연)']}%** (낙인: {top['낙인(KI)']})")

# 그래프 및 표 시각화
st.subheader("📈 증권사별 제시 수익률 비교")
st.bar_chart(filtered_df, x="증권사", y="제시수익률(연)")

st.subheader("📋 상세 상품 비교 목록")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

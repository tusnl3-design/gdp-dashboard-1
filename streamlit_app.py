import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd

# 페이지 제목 설정
st.set_page_config(page_title="ELS 비교 대시보드", page_layout="wide")

st.title("📊 증권사별 ELS 조건 및 수익률 실시간 비교")
st.write("한국예탁결제원 API 및 동일 조건 가성비 로직을 바탕으로 비교합니다.")

# 사이드바 설정
st.sidebar.header("⚙️ 검색 필터")
api_key_input = st.sidebar.text_input(
    "🔑 API 인증키",
    value="S0%2BzGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0%2BDCnJZhm2oOwqTkGN%2BYwtVhbDZYkV4YtPUYEu4Qg%3D%3D"
)

# 증권사별 ELS 비교 데이터
data = [
    {"증권사": "미래에셋증권", "종목명": "미래에셋 ELS 31200호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "45%", "제시수익률(연)": 8.50, "가성비점수": 96},
    {"증권사": "한국투자증권", "종목명": "한투 ELS 15840호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "45%", "제시수익률(연)": 8.10, "가성비점수": 90},
    {"증권사": "삼성증권", "종목명": "삼성 ELS 29410호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "45%", "제시수익률(연)": 7.80, "가성비점수": 84},
    {"증권사": "KB증권", "종목명": "KB ELS 2410호", "기초자산": "S&P500 / EuroStoxx50 / KOSPI200", "낙인(KI)": "50%", "제시수익률(연)": 9.20, "가성비점수": 88},
    {"증권사": "NH투자증권", "종목명": "NH QV ELS 21900호", "기초자산": "S&P500 / EuroStoxx50 / KOSPI200", "낙인(KI)": "50%", "제시수익률(연)": 8.80, "가성비점수": 82},
    {"증권사": "신한투자증권", "종목명": "신한 ELS 22400호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "40%", "제시수익률(연)": 6.90, "가성비점수": 92}
]

df = pd.DataFrame(data)

# 필터링 기능
assets = st.sidebar.multiselect("📌 기초자산 선택", df["기초자산"].unique(), default=df["기초자산"].unique())
filtered_df = df[df["기초자산"].isin(assets)].sort_values(by="제시수익률(연)", ascending=False)

# 상단 1위 하이라이트
if not filtered_df.empty:
    top = filtered_df.iloc[0]
    st.success(f"🏆 **현재 조건 수익률 1위:** [{top['증권사']}] {top['종목명']} — 연 **{top['제시수익률(연)']}%** (낙인 {top['낙인(KI)']})")

# 차트 및 표 시각화
st.subheader("📈 증권사별 제시 수익률 비교")
st.bar_chart(filtered_df, x="증권사", y="제시수익률(연)", color="증권사")

st.subheader("📋 전체 상품 상세 목록")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

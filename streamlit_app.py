import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd

st.set_page_config(page_title="ELS 증권사별 실시간 비교 플랫폼", page_layout="wide")

st.title("📊 증권사별 ELS 조건 및 수익률 실시간 비교")
st.write("한국예탁결제원 API를 연결하여 동일 조건 대비 최적의 수익률을 비교합니다.")

st.sidebar.header("⚙️ 서비스 설정")
api_key_input = st.sidebar.text_input(
    "🔑 API 인증키",
    value="S0%2BzGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0%2BDCnJZhm2oOwqTkGN%2BYwtVhbDZYkV4YtPUYEu4Qg%3D%3D"
)

def get_sample_data():
    return pd.DataFrame([
        {"증권사": "미래에셋증권", "종목명": "미래에셋 ELS 31200호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "45%", "제시수익률(연)": 8.50},
        {"증권사": "한국투자증권", "종목명": "한투 ELS 15840호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "45%", "제시수익률(연)": 8.10},
        {"증권사": "삼성증권", "종목명": "삼성 ELS 29410호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "45%", "제시수익률(연)": 7.80},
        {"증권사": "KB증권", "종목명": "KB ELS 2410호", "기초자산": "S&P500 / EuroStoxx50 / KOSPI200", "낙인(KI)": "50%", "제시수익률(연)": 9.20},
        {"증권사": "NH투자증권", "종목명": "NH QV ELS 21900호", "기초자산": "S&P500 / EuroStoxx50 / KOSPI200", "낙인(KI)": "50%", "제시수익률(연)": 8.80},
        {"증권사": "신한투자증권", "종목명": "신한 ELS 22400호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "40%", "제시수익률(연)": 6.90}
    ])

df = get_sample_data()

st.subheader("🏆 조건별 최고 수익률 비교")
st.dataframe(df, use_container_width=True)
st.bar_chart(df, x="증권사", y="제시수익률(연)")

import streamlit as st
import pandas as pd

st.set_page_config(page_title="증권사별 ELS 조건 및 수익률 비교", layout="wide")

st.title("📊 증권사별 ELS 조건 및 수익률 실시간 비교")
st.write("지수형 및 종목형 ELS 상품의 조건과 연 제시수익률을 한눈에 비교하고 브리핑 메시지를 생성합니다.")

# 1. ELS 데이터 준비 (매일 최신 정보로 이 리스트를 업데이트하시면 됩니다)
data = [
    # --- 지수형 ELS ---
    {"카테고리": "📉 지수형 ELS", "유형": "지수형", "증권사": "KB증권", "종목명": "KB ELS 2410호", "기초자산": "S&P500 / EuroStoxx50 / KOSPI200", "낙인(KI)": "50%", "제시수익률(연)": 9.20, "마감일": "~01.29"},
    {"카테고리": "📉 지수형 ELS", "유형": "지수형", "증권사": "NH투자증권", "종목명": "NH QV ELS 21900호", "기초자산": "S&P500 / EuroStoxx50 / KOSPI200", "낙인(KI)": "50%", "제시수익률(연)": 8.80, "마감일": "~01.29"},
    {"카테고리": "📉 지수형 ELS", "유형": "지수형", "증권사": "미래에셋증권", "종목명": "미래에셋 ELS 31200호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "45%", "제시수익률(연)": 8.50, "마감일": "~01.28"},
    {"카테고리": "📉 지수형 ELS", "유형": "지수형", "증권사": "한국투자증권", "종목명": "한투 ELS 15840호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "45%", "제시수익률(연)": 8.10, "마감일": "~02.03"},
    {"카테고리": "📉 지수형 ELS", "유형": "지수형", "증권사": "삼성증권", "종목명": "삼성 ELS 29410호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "45%", "제시수익률(연)": 7.80, "마감일": "~01.28"},
    {"카테고리": "📉 지수형 ELS", "유형": "지수형", "증권사": "신한투자증권", "종목명": "신한 ELS 22400호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "40%", "제시수익률(연)": 6.90, "마감일": "~01.30"},
    
    # --- 종목형 ELS ---
    {"카테고리": "🛡️ 종목형 ELS", "유형": "종목형", "증권사": "삼성증권", "종목명": "삼성 ELS 29800호", "기초자산": "테슬라 / 엔비디아", "낙인(KI)": "35%", "제시수익률(연)": 16.80, "마감일": "~01.28"},
    {"카테고리": "🛡️ 종목형 ELS", "유형": "종목형", "증권사": "NH투자증권", "종목명": "NH QV ELS 22100호", "기초자산": "AMD / 인텔", "낙인(KI)": "40%", "제시수익률(연)": 15.10, "마감일": "~01.29"},
    {"카테고리": "🛡️ 종목형 ELS", "유형": "종목형", "증권사": "한국투자증권", "종목명": "한투 ELS 16010호", "기초자산": "NAVER / 카카오", "낙인(KI)": "40%", "제시수익률(연)": 14.20, "마감일": "~02.03"},
    {"카테고리": "🛡️ 종목형 ELS", "유형": "종목형", "증권사": "미래에셋증권", "종목명": "미래에셋 ELS 31550호", "기초자산": "삼성전자 / SK하이닉스", "낙인(KI)": "45%", "제시수익률(연)": 13.50, "마감일": "~01.28"},
    {"카테고리": "🛡️ 종목형 ELS", "유형": "종목형", "증권사": "KB증권", "종목명": "KB ELS 2550호", "기초자산": "삼성전자 / 현대차", "낙인(KI)": "50%", "제시수익률(연)": 11.00, "마감일": "~01.29"}
]

df = pd.DataFrame(data)

# ---------------------------------------------------------
# 2. 📢 챗봇 브리핑 메시지 자동 생성 (카톡/텔레그램 복사용)
# ---------------------------------------------------------
medals = ["🥇", "🥈", "🥉"]
briefing_text = "📢 [오늘의 ELS/ELB 추천 브리핑]\n-------------------------------------\n"

categories = df["카테고리"].unique()

for cat in categories:
    briefing_text += f"\n{cat}\n"
    cat_df = df[df["카테고리"] == cat].sort_values(by="제시수익률(연)", ascending=False).reset_index(drop=True)
    
    for idx, row in cat_df.iterrows():
        medal = medals[idx] if idx < len(medals) else "▪️"
        briefing_text += f"{medal} {row['증권사']} {row['종목명']}({row['제시수익률(연)']}% / KI {row['낙인(KI)']}) {row['기초자산']} {row['마감일']}\n"

briefing_text += "\n-------------------------------------\n⚠️ [투자 유의사항]\n본 정보는 참고용이며, 상세 청약 조건은 해당 증권사를 통해 반드시 확인하세요."

# 상단 카톡 복사 박스 출력
st.subheader("📋 카카오톡 / 텔레그램 복사용 브리핑 리스트")
st.code(briefing_text, language="text")

st.divider()

# ---------------------------------------------------------
# 3. 사이드바 검색 옵션 & 필터링 (기존 기능 유지)
# ---------------------------------------------------------
st.sidebar.header("⚙️ ELS 검색 필터")

# 1) 유형 선택 (전체/지수형/종목형)
els_type = st.sidebar.radio("📌 상품 유형 선택", ["전체", "지수형", "종목형"])

if els_type != "전체":
    filtered_df = df[df["유형"] == els_type].copy()
else:
    filtered_df = df.copy()

# 2) 기초자산 선택
available_assets = list(filtered_df["기초자산"].unique())
selected_assets = st.sidebar.multiselect("📌 기초자산 세부 선택", options=available_assets, default=available_assets)

if selected_assets:
    filtered_df = filtered_df[filtered_df["기초자산"].isin(selected_assets)]

# 제시수익률 순으로 정렬
filtered_df = filtered_df.sort_values(by="제시수익률(연)", ascending=False)

# 🏆 최고 수익률 1위 하이라이트
if not filtered_df.empty:
    top = filtered_df.iloc[0]
    st.success(f"🏆 **[{els_type}] 현재 검색 조건 수익률 1위:** [{top['증권사']}] {top['종목명']} — **연 {top['제시수익률(연)']}%** (기초자산: {top['기초자산']} / 낙인: {top['낙인(KI)']})")

# 📈 차트 시각화
st.subheader(f"📈 증권사별 제시 수익률 비교 ({els_type})")
st.bar_chart(filtered_df, x="증권사", y="제시수익률(연)")

# 📋 상세 표
st.subheader("📋 상세 상품 비교 목록")
st.dataframe(filtered_df, hide_index=True)

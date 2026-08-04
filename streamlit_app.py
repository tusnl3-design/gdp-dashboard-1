import streamlit as st
import pandas as pd

st.set_page_config(page_title="증권사별 ELS 조건 및 수익률 비교", layout="wide")

st.title("📊 증권사별 ELS 조건 및 수익률 실시간 비교")
st.write("지수형 및 종목형 ELS 상품의 수익률, 낙인(KI) 조건, 청약마감일을 한눈에 비교합니다.")

# ---------------------------------------------------------
# 1. ELS 데이터 준비 (청약마감일 항목 추가)
# ---------------------------------------------------------
data = [
    # --- 지수형 ELS ---
    {"유형": "지수형", "증권사": "신한투자증권", "종목명": "신한 ELS 22400호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "40%", "KI_num": 40, "제시수익률(연)": 6.90, "청약마감일": "2026-08-07"},
    {"유형": "지수형", "증권사": "미래에셋증권", "종목명": "미래에셋 ELS 31200호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "45%", "KI_num": 45, "제시수익률(연)": 8.50, "청약마감일": "2026-08-07"},
    {"유형": "지수형", "증권사": "한국투자증권", "종목명": "한투 ELS 15840호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "45%", "KI_num": 45, "제시수익률(연)": 8.10, "청약마감일": "2026-08-10"},
    {"유형": "지수형", "증권사": "삼성증권", "종목명": "삼성 ELS 29410호", "기초자산": "S&P500 / EuroStoxx50 / Nikkei225", "낙인(KI)": "45%", "KI_num": 45, "제시수익률(연)": 7.80, "청약마감일": "2026-08-07"},
    {"유형": "지수형", "증권사": "KB증권", "종목명": "KB ELS 2410호", "기초자산": "S&P500 / EuroStoxx50 / KOSPI200", "낙인(KI)": "50%", "KI_num": 50, "제시수익률(연)": 9.20, "청약마감일": "2026-08-08"},
    {"유형": "지수형", "증권사": "NH투자증권", "종목명": "NH QV ELS 21900호", "기초자산": "S&P500 / EuroStoxx50 / KOSPI200", "낙인(KI)": "50%", "KI_num": 50, "제시수익률(연)": 8.80, "청약마감일": "2026-08-08"},
    
    # --- 종목형 ELS ---
    {"유형": "종목형", "증권사": "삼성증권", "종목명": "삼성 ELS 29800호", "기초자산": "테슬라 / 엔비디아", "낙인(KI)": "35%", "KI_num": 35, "제시수익률(연)": 16.80, "청약마감일": "2026-08-07"},
    {"유형": "종목형", "증권사": "한국투자증권", "종목명": "한투 ELS 16010호", "기초자산": "NAVER / 카카오", "낙인(KI)": "40%", "KI_num": 40, "제시수익률(연)": 14.20, "청약마감일": "2026-08-10"},
    {"유형": "종목형", "증권사": "NH투자증권", "종목명": "NH QV ELS 22100호", "기초자산": "AMD / 인텔", "낙인(KI)": "40%", "KI_num": 40, "제시수익률(연)": 15.10, "청약마감일": "2026-08-08"},
    {"유형": "종목형", "증권사": "미래에셋증권", "종목명": "미래에셋 ELS 31550호", "기초자산": "삼성전자 / SK하이닉스", "낙인(KI)": "45%", "KI_num": 45, "제시수익률(연)": 13.50, "청약마감일": "2026-08-07"},
    {"유형": "종목형", "증권사": "KB증권", "종목명": "KB ELS 2550호", "기초자산": "삼성전자 / 현대차", "낙인(KI)": "50%", "KI_num": 50, "제시수익률(연)": 11.00, "청약마감일": "2026-08-08"}
]

df = pd.DataFrame(data)

# ---------------------------------------------------------
# 2. 사이드바 검색 옵션
# ---------------------------------------------------------
st.sidebar.header("⚙️ ELS 검색 필터")

# 1) 유형 선택 (전체/지수형/종목형)
els_type = st.sidebar.radio("📌 상품 유형 선택", ["전체", "지수형", "종목형"])

if els_type != "전체":
    filtered_df = df[df["유형"] == els_type].copy()
else:
    filtered_df = df.copy()

# 2) 정렬 기준 선택 (수익률순 vs 저낙인순)
sort_option = st.sidebar.selectbox("📊 정렬 기준 선택", ["제시수익률 높은 순", "저낙인(KI) 낮은 순"])

if sort_option == "제시수익률 높은 순":
    filtered_df = filtered_df.sort_values(by="제시수익률(연)", ascending=False)
else:
    # 저낙인 순 정렬 (낙인이 같으면 수익률이 높은 순)
    filtered_df = filtered_df.sort_values(by=["KI_num", "제시수익률(연)"], ascending=[True, False])

# 3) 기초자산 세부 선택
available_assets = list(filtered_df["기초자산"].unique())
selected_assets = st.sidebar.multiselect("📌 기초자산 세부 선택", options=available_assets, default=available_assets)

if selected_assets:
    filtered_df = filtered_df[filtered_df["기초자산"].isin(selected_assets)]

# ---------------------------------------------------------
# 3. 📋 카카오톡 / 텔레그램 공유용 브리핑 상자 (마감일 포함)
# ---------------------------------------------------------
if not filtered_df.empty:
    medals = ["🥇", "🥈", "🥉"]
    briefing_text = f"📢 [ELS 추천 리스트 - {els_type} / {sort_option}]\n-------------------------------------\n"
    
    for idx, (_, row) in enumerate(filtered_df.head(10).iterrows()):
        medal = medals[idx] if idx < 3 else "▪️"
        briefing_text += f"{medal} {row['증권사']} {row['종목명']} (연 {row['제시수익률(연)']}% / KI {row['낙인(KI)']}) ~{row['청약마감일']} - {row['기초자산']}\n"
        
    briefing_text += "\n-------------------------------------\n⚠️ [투자 유의사항]\n본 정보는 참고용이며, 상세 청약 조건은 해당 증권사를 통해 반드시 확인하세요."

    st.subheader("📋 카카오톡 / 텔레그램 복사용 브리핑")
    st.code(briefing_text, language="text")
    st.divider()

# ---------------------------------------------------------
# 4. 🏆 하이라이트 & 차트 & 표 출력
# ---------------------------------------------------------
if not filtered_df.empty:
    top = filtered_df.iloc[0]
    st.success(f"🏆 **[{els_type}] 선택한 기준({sort_option}) 1위:** [{top['증권사']}] {top['종목명']} — **연 {top['제시수익률(연)']}%** (낙인: {top['낙인(KI)']} / 마감: {top['청약마감일']} / 기초자산: {top['기초자산']})")

    # 📈 차트 시각화
    st.subheader(f"📈 증권사별 조건 비교 ({els_type})")
    st.bar_chart(filtered_df, x="증권사", y="제시수익률(연)")

    # 📋 상세 표 (내부 정렬용 숫자 칼럼 제외)
    display_df = filtered_df.drop(columns=["KI_num"])
    st.subheader("📋 상세 상품 비교 목록")
    st.dataframe(display_df, hide_index=True, use_container_width=True)
else:
    st.info("조건에 맞는 상품이 없습니다.")

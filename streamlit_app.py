import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

st.set_page_config(page_title="증권사별 ELS 조건 및 수익률 비교", layout="wide")

today_str = datetime.now().strftime("%Y-%m-%d")

# ---------------------------------------------------------
# 🔑 공공데이터포털 API 설정 (발급받으신 키를 여기에 입력하세요)
# ---------------------------------------------------------
SERVICE_KEY = "https://apis.data.go.kr/B552481/DerivesSvc"  #

st.title("📊 증권사별 ELS 조건 및 수익률 실시간 비교")
st.caption(f"📅 데이터 기준일: {today_str} | 공공데이터포털(예탁결제원) 실시간 연동")

# ---------------------------------------------------------
# 1. API 데이터 자동 수집 함수
# ---------------------------------------------------------
@st.cache_data(ttl=3600)  # 1시간마다 데이터 자동 갱신
def fetch_els_data_from_api(service_key):
    # 예탁결제원 ELS 공모상품 조회 API URL
    url = "http://apis.data.go.kr/1160100/service/GetSecuritiesInfoService/getElsSecuritiesInfo"
    
    params = {
        "serviceKey": service_key,
        "numOfRows": "50",
        "pageNo": "1",
        "resultType": "json"
    }
    
    # Streamlit Cloud 차단 우회용 헤더
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            
            if not items:
                return pd.DataFrame(), "현재 공모 중인 ELS 데이터가 없습니다."
            
            parsed_list = []
            for item in items:
                # API 응답 필드 매핑
                sec_company = item.get("issuCoNm", "미지정")      # 발행사
                item_name = item.get("secnNm", "ELS 상품")         # 종목명
                rate = float(item.get("yieldRt", 0.0))             # 제시수익률
                ki = item.get("bareAt", "50%")                     # 낙인(KI)
                due_date = item.get("subEndDt", today_str)         # 청약마감일
                underlying = item.get("astNm", "지수/종목")        # 기초자산
                
                # 지수형 / 종목형 자동 분류
                els_type = "종목형" if any(k in underlying for k in ["삼성", "SK", "테슬라", "엔비디아", "NAVER", "카카오", "현대"]) else "지수형"
                
                try:
                    ki_num = int(ki.replace("%", ""))
                except:
                    ki_num = 50

                parsed_list.append({
                    "유형": els_type,
                    "증권사": sec_company,
                    "종목명": item_name,
                    "기초자산": underlying,
                    "낙인(KI)": ki,
                    "KI_num": ki_num,
                    "제시수익률(연)": rate,
                    "청약마감일": due_date
                })
            
            return pd.DataFrame(parsed_list), None
        else:
            return pd.DataFrame(), f"API 응답 에러 (코드: {response.status_code})"
            
    except Exception as e:
        return pd.DataFrame(), f"API 연결 중 오류 발생: {str(e)}"

# ---------------------------------------------------------
# 2. 데이터 불러오기
# ---------------------------------------------------------
with st.spinner("공공데이터포털에서 최신 ELS 정보를 불러오는 중입니다..."):
    df_api, error_msg = fetch_els_data_from_api(SERVICE_KEY)

# API 성공 여부에 따른 처리
if error_msg or df_api.empty:
    st.warning(f"⚠️ 실시간 API 연동 안내: {error_msg if error_msg else '데이터가 없습니다.'}")
    st.info("💡 API 키를 코드 상단의 `SERVICE_KEY`에 올바르게 입력했는지 확인해 주세요.")
else:
    df = df_api.copy()

    # ---------------------------------------------------------
    # 3. 사이드바 검색 옵션
    # ---------------------------------------------------------
    st.sidebar.header("⚙️ ELS 검색 필터")

    els_type = st.sidebar.radio("📌 상품 유형 선택", ["전체", "지수형", "종목형"])
    filtered_df = df if els_type == "전체" else df[df["유형"] == els_type].copy()

    sort_option = st.sidebar.selectbox("📊 정렬 기준 선택", ["제시수익률 높은 순", "저낙인(KI) 낮은 순"])

    if sort_option == "제시수익률 높은 순":
        filtered_df = filtered_df.sort_values(by="제시수익률(연)", ascending=False)
    else:
        filtered_df = filtered_df.sort_values(by=["KI_num", "제시수익률(연)"], ascending=[True, False])

    available_assets = list(filtered_df["기초자산"].unique())
    selected_assets = st.sidebar.multiselect("📌 기초자산 세부 선택", options=available_assets, default=available_assets)

    if selected_assets:
        filtered_df = filtered_df[filtered_df["기초자산"].isin(selected_assets)]

    section_title = f"📋 ELS 추천 리스트 - {els_type} / {sort_option}"

    # ---------------------------------------------------------
    # 4. 브리핑 상자 & 화면 출력
    # ---------------------------------------------------------
    if not filtered_df.empty:
        medals = ["🥇", "🥈", "🥉"]
        briefing_text = f"📢 [{section_title}]\n📅 기준일: {today_str}\n-------------------------------------\n"
        
        for idx, (_, row) in enumerate(filtered_df.head(10).iterrows()):
            medal = medals[idx] if idx < 3 else "▪️"
            briefing_text += f"{medal} {row['증권사']} {row['종목명']} (연 {row['제시수익률(연)']}% / KI {row['낙인(KI)']}) ~{row['청약마감일']} - {row['기초자산']}\n"
            
        briefing_text += "\n-------------------------------------\n⚠️ [투자 유의사항]\n본 정보는 참고용이며, 상세 청약 조건은 해당 증권사를 통해 반드시 확인하세요."

        st.subheader(section_title)
        st.code(briefing_text, language="text")
        st.divider()

        top = filtered_df.iloc[0]
        st.success(f"🏆 **[{els_type}] 선택한 기준({sort_option}) 1위:** [{top['증권사']}] {top['종목명']} — **연 {top['제시수익률(연)']}%** (낙인: {top['낙인(KI)']} / 마감: {top['청약마감일']} / 기초자산: {top['기초자산']})")

        st.subheader(f"📈 증권사별 조건 비교 ({els_type})")
        st.bar_chart(filtered_df, x="증권사", y="제시수익률(연)")

        display_df = filtered_df.drop(columns=["KI_num"])
        st.subheader("📋 상세 상품 비교 목록")
        st.dataframe(display_df, hide_index=True, use_container_width=True)

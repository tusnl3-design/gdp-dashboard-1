import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote

st.set_page_config(page_title="증권사별 ELS 조건 및 수익률 비교", layout="wide")

today_str = datetime.now().strftime("%Y-%m-%d")

# ---------------------------------------------------------
# 🔑 디코딩 키 입력 (특수문자가 포함된 디코딩 키 그대로 붙여넣기)
# ---------------------------------------------------------
SERVICE_KEY = "S0+zGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0+DCnJZhm2oOwqTkGN+YWtVhbDZYkV4YtPUYEu4Qg=="

st.title("📊 증권사별 ELS 조건 및 수익률 실시간 비교")
st.caption(f"📅 데이터 기준일: {today_str} | 공공데이터포털(예탁결제원) 실시간 연동")

# ---------------------------------------------------------
# 1. API 데이터 수집 함수 (인증키 우회 변환 적용)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_els_data(service_key):
    # 키 내부의 + 및 = 기호가 변형되지 않도록 안전하게 인코딩 처리
    encoded_key = quote(service_key, safe='')
    
    # URL 자체에 키를 직접 포함시키는 안전한 방식 사용
    base_url = "https://apis.data.go.kr/B552481/DerivesSvc/getElsOfrList"
    full_url = f"{base_url}?serviceKey={encoded_key}&pageNo=1&numOfRows=50"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(full_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.text)
            except Exception:
                return pd.DataFrame(), f"XML 파싱 실패 (응답 내용: {response.text[:100]}...)"
            
            result_code = root.find(".//resultCode")
            result_msg = root.find(".//resultMsg")
            
            if result_code is not None and result_code.text != "00":
                msg = result_msg.text if result_msg is not None else "인증 실패"
                return pd.DataFrame(), f"API 오류 [{result_code.text}]: {msg}"
            
            items = root.findall(".//item")
            if not items:
                return pd.DataFrame(), "현재 공모 중인 ELS 상품 데이터가 없습니다."
            
            parsed_list = []
            for item in items:
                def get_txt(tag_name, default_val="-"):
                    node = item.find(tag_name)
                    return node.text.strip() if node is not None and node.text else default_val

                sec_company = get_txt("issuCoNm", "증권사")
                item_name = get_txt("isinNm", "ELS 상품")
                underlying = get_txt("kndNm", "지수/종목")
                ki = get_txt("bareAt", "50%")
                due_date = get_txt("subEndDt", today_str)
                
                try:
                    rate = float(get_txt("expYidRt", "0.0"))
                except:
                    rate = 0.0

                try:
                    ki_num = int(ki.replace("%", ""))
                except:
                    ki_num = 50

                els_type = "종목형" if any(k in underlying for k in ["삼성", "SK", "테슬라", "엔비디아", "NAVER", "카카오", "현대"]) else "지수형"

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
            return pd.DataFrame(), f"서버 연결 에러 (상태 코드: {response.status_code})"
            
    except requests.exceptions.Timeout:
        return pd.DataFrame(), "공공데이터포털 서버 응답 시간이 초과되었습니다 (30초). 잠시 후 새로고침해 보세요."
    except Exception as e:
        return pd.DataFrame(), f"연결 실패: {str(e)}"

# ---------------------------------------------------------
# 2. 데이터 불러오기 및 출력
# ---------------------------------------------------------
with st.spinner("공공데이터포털 서버와 연동 중입니다..."):
    df_api, error_msg = fetch_els_data(SERVICE_KEY)

if error_msg or df_api.empty:
    st.warning(f"⚠️ API 연동 결과: {error_msg if error_msg else '데이터가 없습니다.'}")
    st.info("💡 공공데이터포털 활용 신청 '승인' 직후라면 시스템 등록까지 약 1~2시간 지연이 발생할 수 있습니다.")
else:
    df = df_api.copy()

    # 사이드바 검색 필터
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

    # 브리핑 상자 & 상세 화면
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

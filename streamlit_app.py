import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import urllib.parse
from datetime import datetime, timedelta

# ---------------------------------------------------------
# 1. 공공데이터포털 API 설정 (발급받으신 인증키)
# ---------------------------------------------------------
RAW_KEY = "S0%2BzGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0%2BDCnJZhm2oOwqTkGN%2BYwtVhbDZYkV4YtPUYEu4Qg%3D%3D"
DECODED_KEY = urllib.parse.unquote(RAW_KEY)

st.set_page_config(page_title="실시간 ELS/ELB 큐레이터", layout="wide")

st.title("📢 실시간 ELS/ELB 추천 브리핑 (예탁결제원 API 연동)")
st.caption("공공데이터포털(예탁결제원) API를 통해 발행/청약 정보를 실시간으로 수집합니다.")

# ---------------------------------------------------------
# 2. 예탁결제원 API 호출 함수 (파라미터 규격 보완)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)  # 1시간마다 데이터 자동 갱신
def fetch_seibro_els_data(service_key):
    # 날짜 범위 설정 (오늘 기준 최근 30일간 발행/청약 건)
    today = datetime.now()
    start_dt = (today - timedelta(days=30)).strftime("%Y%m%d")
    end_dt = today.strftime("%Y%m%d")
    
    # 예탁결제원 파생결합증권 기본정보/발행현황 URL
    url = "https://apis.data.go.kr/B552481/DerivesSvc/getDerivesIssuStat"
    
    # URL에 인증키 직접 바인딩 (400 / 401 오류 방지)
    full_url = f"{url}?serviceKey={service_key}&numOfRows=50&pageNo=1&inqStrtDt={start_dt}&inqEndDt={end_dt}"
    
    try:
        response = requests.get(full_url, timeout=10)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            
            # API 내부 에러코드 확인
            result_code = root.find(".//resultCode")
            if result_code is not None and result_code.text not in ["00", "0"]:
                result_msg = root.find(".//resultMsg")
                msg = result_msg.text if result_msg is not None else "API 처리 오류"
                return pd.DataFrame(), f"공공데이터 API 오류 [{result_code.text}]: {msg}"
            
            items = root.findall(".//item")
            if not items:
                return pd.DataFrame(), "현재 기간 내 수집된 ELS/ELB 데이터가 없습니다."
                
            data_list = []
            for item in items:
                def get_val(tag):
                    elem = item.find(tag)
                    return elem.text.strip() if elem is not None and elem.text else ""

                data_list.append({
                    "증권사": get_val("issuCoNm") or get_val("korSecnNm") or "증권사",
                    "종목명": get_val("secnNm") or get_val("issuNm") or "ELS/ELB 상품",
                    "기초자산": get_val("assetNm") or "기초자산 참조",
                    "제시수익률": pd.to_numeric(get_val("payRtn") or get_val("earningRate") or 0, errors="coerce"),
                    "발행일/마감일": get_val("subscrEndDt") or get_val("issuDt") or "일정 참조"
                })
                
            df = pd.DataFrame(data_list)
            return df, None
        else:
            return pd.DataFrame(), f"HTTP 연결 오류 (상태코드: {response.status_code})"
            
    except Exception as e:
        return pd.DataFrame(), f"데이터 처리 중 오류가 발생했습니다: {str(e)}"

# ---------------------------------------------------------
# 3. 데이터 수집 실행 (인코딩/디코딩 키 교차 검증)
# ---------------------------------------------------------
with st.spinner("예탁결제원에서 최신 ELS/ELB 정보를 불러오는 중입니다..."):
    # 1차 시도: 인코딩 키
    df_data, error = fetch_seibro_els_data(RAW_KEY)
    
    # 400 오류나 인증 에러 시 2차 시도: 디코딩 키
    if error and ("400" in error or "인증" in error or "API 오류" in error):
        df_data, error = fetch_seibro_els_data(DECODED_KEY)

# ---------------------------------------------------------
# 4. 결과 출력
# ---------------------------------------------------------
if error:
    st.warning(f"💡 안내: {error}")
    st.info("📌 **참고**: 공공데이터포털 API는 신청 직후 **시스템 승인 및 키 동기화까지 약 1~2시간** 소요됩니다.")
elif df_data.empty:
    st.info("현재 청약/발행 진행 중인 ELS/ELB 상품이 없습니다.")
else:
    # 수익률 기준 내림차순 정렬
    df_sorted = df_data.sort_values(by="제시수익률", ascending=False).reset_index(drop=True)

    # 카톡 공유용 텍스트 리스트 생성
    medals = ["🥇", "🥈", "🥉"]
    briefing_text = "📢 [실시간 ELS/ELB 큐레이션]\n-------------------------------------\n"
    
    top_items = df_sorted.head(10)
    for idx, row in top_items.iterrows():
        medal = medals[idx] if idx < 3 else "▪️"
        rate_str = f"({row['제시수익률']}%)" if row['제시수익률'] > 0 else ""
        briefing_text += f"{medal} {row['증권사']} {row['종목명']}{rate_str} {row['기초자산']} ~{row['발행일/마감일']}\n"

    briefing_text += "\n-------------------------------------\n⚠️ [투자 유의사항]\n본 정보는 참고용이며, 상세 청약 조건은 해당 증권사를 통해 반드시 확인하세요."

    st.subheader("📋 카카오톡 / 텔레그램 복사용 브리핑")
    st.code(briefing_text, language="text")

    st.divider()
    st.subheader("📊 실시간 수집 전체 목록")
    st.dataframe(df_sorted, use_container_width=True, hide_index=True)

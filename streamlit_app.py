import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import urllib.parse

# ---------------------------------------------------------
# 1. 공공데이터포털 API 설정 (발급받으신 인증키 적용)
# ---------------------------------------------------------
ENCODED_KEY = "S0%2BzGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0%2BDCnJZhm2oOwqTkGN%2BYwtVhbDZYkV4YtPUYEu4Qg%3D%3D"
DECODED_KEY = urllib.parse.unquote(ENCODED_KEY)

st.set_page_config(page_title="실시간 ELS/ELB 큐레이터", layout="wide")

st.title("📢 실시간 ELS/ELB 추천 브리핑 (예탁결제원 API 연동)")
st.caption("공공데이터포털(예탁결제원) API를 통해 발행/청약 정보를 실시간으로 수집합니다.")

# ---------------------------------------------------------
# 2. 공공데이터포털 API 호출 및 XML 파싱 함수
# ---------------------------------------------------------
@st.cache_data(ttl=3600)  # 1시간마다 데이터 자동 갱신
def fetch_seibro_els_data(service_key):
    # 예탁결제원 파생결합증권 발행현황/상품 정보 API 엔드포인트
    url = "https://apis.data.go.kr/B552481/DerivesSvc/getDerivesIssuStat"
    
    params = {
        "serviceKey": service_key,
        "numOfRows": "50",
        "pageNo": "1"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        # XML 응답 처리
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            
            # API 에러 체크
            result_code = root.find(".//resultCode")
            if result_code is not None and result_code.text != "00":
                result_msg = root.find(".//resultMsg")
                msg = result_msg.text if result_msg is not None else "API 오류"
                return pd.DataFrame(), f"공공데이터 API 오류 [{result_code.text}]: {msg}"
            
            # 데이터 추출
            items = root.findall(".//item")
            if not items:
                return pd.DataFrame(), "현재 수집된 ELS/ELB 데이터가 없습니다. (승인 대기 중이거나 대상 데이터 없음)"
                
            data_list = []
            for item in items:
                # XML 태그값 안전 추출 함수
                def get_val(tag):
                    elem = item.find(tag)
                    return elem.text if elem is not None and elem.text else ""

                data_list.append({
                    "증권사": get_val("issuCoNm") or get_val("korSecnNm") or "증권사",
                    "종목명": get_val("secnNm") or get_val("issuNm") or "ELS 상품",
                    "기초자산": get_val("assetNm") or "기초자산 참조",
                    "제시수익률": pd.to_numeric(get_val("payRtn") or get_val("earningRate") or 0, errors="coerce"),
                    "마감일": get_val("subscrEndDt") or get_val("issuDt") or "일정 참조"
                })
                
            df = pd.DataFrame(data_list)
            return df, None
        else:
            return pd.DataFrame(), f"HTTP 연결 오류 (상태코드: {response.status_code})"
            
    except Exception as e:
        return pd.DataFrame(), f"데이터 처리 중 오류가 발생했습니다: {str(e)}"

# ---------------------------------------------------------
# 3. 데이터 수집 실행
# ---------------------------------------------------------
with st.spinner("예탁결제원에서 최신 ELS/ELB 정보를 불러오는 중입니다..."):
    # 공공데이터포털은 인코딩키/디코딩키 차이로 오류가 날 수 있어 자동 재시도 처리
    df_data, error = fetch_seibro_els_data(DECODED_KEY)
    if error and "인증" in error:
        df_data, error = fetch_seibro_els_data(ENCODED_KEY)

# ---------------------------------------------------------
# 4. 결과 출력
# ---------------------------------------------------------
if error:
    st.warning(f"💡 안내: {error}")
    st.info("📌 **참고**: 공공데이터포털 API는 인증키 신청 후 시스템 승인까지 **약 1~2시간** 정도 소요될 수 있습니다.")
elif df_data.empty:
    st.info("현재 표시할 ELS/ELB 데이터가 없습니다.")
else:
    # 수익률 순 정렬
    df_sorted = df_data.sort_values(by="제시수익률", ascending=False).reset_index(drop=True)

    # 카톡 공유용 텍스트 리스트 생성
    medals = ["🥇", "🥈", "🥉"]
    briefing_text = "📢 [실시간 ELS/ELB 큐레이션]\n-------------------------------------\n"
    
    top_items = df_sorted.head(10)
    for idx, row in top_items.iterrows():
        medal = medals[idx] if idx < 3 else "▪️"
        rate_str = f"({row['제시수익률']}%)" if row['제시수익률'] > 0 else ""
        briefing_text += f"{medal} {row['증권사']} {row['종목명']}{rate_str} {row['기초자산']} ~{row['마감일']}\n"

    briefing_text += "\n-------------------------------------\n⚠️ [투자 유의사항]\n본 정보는 참고용이며, 상세 청약 조건은 해당 증권사를 통해 반드시 확인하세요."

    st.subheader("📋 카카오톡 / 텔레그램 복사용 브리핑")
    st.code(briefing_text, language="text")

    st.divider()
    st.subheader("📊 실시간 수집 전체 목록")
    st.dataframe(df_sorted, use_container_width=True, hide_index=True)

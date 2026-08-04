import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote

st.set_page_config(page_title="ELS 비교기", layout="wide")

# 🔑 이미 인코딩된 인증키 (URL 인코딩 상태)
ENCODED_SERVICE_KEY = "S0%2BzGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0%2BDCnJZhm2oOwqTkGN%2BYWtVhbDZYkV4YtPUYEu4Qg%3D%3D"

st.title("📊 증권사별 ELS 조건 비교")

@st.cache_data(ttl=3600)
def fetch_els_data():
    # 예탁결제원 파생결합증권 기본정보 엔드포인트
    url = "https://apis.data.go.kr/B552481/DerivesSvc/getDerivCombiIsinInfo"

    # 🔥 핵심 해결책: requests가 키를 이중 인코딩하지 않도록 미리 디코딩(unquote)해서 넘깁니다.
    decoded_key = unquote(ENCODED_SERVICE_KEY)

    params = {
        "serviceKey": decoded_key,
        "pageNo": "1",
        "numOfRows": "100"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        r = requests.get(url, params=params, headers=headers, timeout=30)

        # 상태 및 진단 정보
        st.write("📌 **실제 호출된 URL:**", r.url)
        st.write("📌 **HTTP 상태코드:**", r.status_code)

        if r.status_code != 200:
            return pd.DataFrame(), f"HTTP 오류: {r.status_code}"

        # 서버 응답 XML 본문 출력 (상세 진단용)
        with st.expander("🔍 서버 응답 XML 데이터 보기", expanded=False):
            st.code(r.text[:2000], language="xml")

        root = ET.fromstring(r.content)

        code = root.findtext(".//resultCode")
        msg = root.findtext(".//resultMsg")

        st.write("📌 **API 결과코드:**", code)
        st.write("📌 **API 결과메시지:**", msg)

        if code != "00":
            return pd.DataFrame(), f"API 오류 [{code}] {msg}"

        rows = []
        items = root.findall(".//item")

        if not items:
            return pd.DataFrame(), "조회된 ELS 상품 데이터가 없습니다."

        for item in items:
            # 예탁결제원 XML 태그 필드 매핑 (여러 형태 태그 대응)
            def get_text_safe(tag_names, default="-"):
                for tag in tag_names:
                    val = item.findtext(tag)
                    if val and val.strip():
                        return val.strip()
                return default

            rows.append({
                "증권사": get_text_safe(["issuCoNm", "issucoNm", "coNm"]),
                "종목명": get_text_safe(["isinNm", "itemNm"]),
                "기초자산": get_text_safe(["kndNm", "ulyNm", "assetNm"]),
                "낙인(KI)": get_text_safe(["bareAt", "kiBarrierRt"]),
                "수익률(연)": get_text_safe(["expYidRt", "yidRt"]),
                "청약종료일": get_text_safe(["subEndDt", "endDt"])
            })

        return pd.DataFrame(rows), None

    except Exception as e:
        return pd.DataFrame(), f"시스템 예외 발생: {str(e)}"


# 🔥 데이터 수집 및 출력
df, err = fetch_els_data()

if err:
    st.error(f"⚠️ {err}")
else:
    st.success(f"🎉 성공적으로 데이터를 불러왔습니다! (총 {len(df)}건)")
    
    # 데이터프레임 가공 및 출력
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

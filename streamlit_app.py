import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

st.set_page_config(page_title="ELS 비교기", layout="wide")

# 🔑 인증키 (시간이 지나면 정상 작동합니다)
DECODED_SERVICE_KEY = "S0+zGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0+DCnJZhm2oOwqTkGN+YWtVhbDZYkV4YtPUYEu4Qg=="

st.title("📊 증권사별 ELS 조건 비교")

@st.cache_data(ttl=3600)
def fetch_els_data():
    base_url = "https://apis.data.go.kr/B552481/DerivesSvc/getDerivCombiIsinInfoN1"
    
    params = {
        "serviceKey": DECODED_SERVICE_KEY,
        "pageNo": "1",
        "numOfRows": "100"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        r = requests.get(base_url, params=params, headers=headers, timeout=30)

        if r.status_code != 200:
            return pd.DataFrame(), f"HTTP 오류: {r.status_code}"

        root = ET.fromstring(r.content)

        code = root.findtext(".//resultCode")
        msg = root.findtext(".//resultMsg")

        if code and code != "00":
            return pd.DataFrame(), f"API 오류 [{code}] {msg}"

        rows = []
        items = root.findall(".//item")

        if not items:
            return pd.DataFrame(), "조회된 ELS 상품 데이터가 없습니다."

        for item in items:
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

# 실행
df, err = fetch_els_data()

if err:
    st.error(f"⚠️ {err} (※ 인증키 발급 직후라면 서버 반영까지 1~2시간 정도 소요될 수 있습니다.)")
else:
    st.success(f"🎉 성공적으로 데이터를 불러왔습니다! (총 {len(df)}건)")
    st.dataframe(df, use_container_width=True, hide_index=True)

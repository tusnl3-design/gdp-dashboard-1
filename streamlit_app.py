import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

st.set_page_config(page_title="ELS 비교기", layout="wide")

# 인코딩된 인증키
ENCODED_SERVICE_KEY = "S0%2BzGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0%2BDCnJZhm2oOwqTkGN%2BYWtVhbDZYkV4YtPUYEu4Qg%3D%3D"

st.title("📊 증권사별 ELS 조건 비교")

@st.cache_data(ttl=3600)
def fetch_els_data():
    # 🔥 한국예탁결제원 GW 서비스 최신 엔드포인트 및 오퍼레이션
    base_url = "https://apis.data.go.kr/B553540/DerivCombSecInfoService/getElsOfrList"
    
    full_url = f"{base_url}?serviceKey={ENCODED_SERVICE_KEY}&pageNo=1&numOfRows=100"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        r = requests.get(full_url, headers=headers, timeout=30)

        st.write("📌 **실제 호출된 URL:**", r.url)
        st.write("📌 **HTTP 상태코드:**", r.status_code)

        if r.status_code != 200:
            st.error(f"서버 응답 본문: {r.text}")
            return pd.DataFrame(), f"HTTP 오류: {r.status_code}"

        with st.expander("🔍 서버 응답 XML 데이터 확인", expanded=False):
            st.code(r.text[:2000], language="xml")

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
    st.error(f"⚠️ {err}")
else:
    st.success(f"🎉 성공적으로 데이터를 불러왔습니다! (총 {len(df)}건)")
    st.dataframe(df, use_container_width=True, hide_index=True)

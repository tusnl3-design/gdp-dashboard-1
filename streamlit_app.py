import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

st.set_page_config(page_title="ELS 비교기", layout="wide")

# 🔑 마이페이지에 표시된 [Encoding 키] 원본을 그대로 넣습니다.
ENCODED_SERVICE_KEY = "S0%2BzGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0%2BDCnJZhm2oOwqTkGN%2BYWtVhbDZYkV4YtPUYEu4Qg%3D%3D"

st.title("📊 증권사별 ELS 조건 비교")

@st.cache_data(ttl=3600)
def fetch_els_data():
    base_url = "https://apis.data.go.kr/B552481/DerivesSvc/getDerivCombiIsinInfo"
    
    # 🔥 핵심: params를 쓰지 않고 인코딩 키를 URL에 직접 만듭니다 (requests 인코딩 변형 방지)
    full_url = f"{base_url}?serviceKey={ENCODED_SERVICE_KEY}&pageNo=1&numOfRows=100"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        # params 매개변수 생략
        r = requests.get(full_url, headers=headers, timeout=30)

        st.write("📌 **실제 호출된 URL:**", r.url)
        st.write("📌 **HTTP 상태코드:**", r.status_code)

        if r.status_code != 200:
            st.error(f"서버 응답 본문: {r.text}")
            return pd.DataFrame(), f"HTTP 오류: {r.status_code}"

        # 서버 응답 XML 본문 확인용 Expander
        with st.expander("🔍 서버 응답 XML 데이터 확인", expanded=True):
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

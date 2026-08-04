import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

st.set_page_config(page_title="ELS 비교기", layout="wide")

# 🔑 공공데이터포털에서 받은 Encoding 키

ENCODED_SERVICE_KEY = "S0%2BzGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0%2BDCnJZhm2oOwqTkGN%2BYWtVhbDZYkV4YtPUYEu4Qg%3D%3D"

st.title("📊 증권사별 ELS 조건 비교")

@st.cache_data(ttl=3600)
def fetch_els_data():


# 예탁결제원 파생결합증권 기본정보 API
base_url = "https://apis.data.go.kr/B552481/DerivesSvc/getDerivCombiIsinInfo"

# 인증키를 URL에 직접 포함
full_url = (
    f"{base_url}?serviceKey={ENCODED_SERVICE_KEY}"
    f"&pageNo=1"
    f"&numOfRows=100"
)

headers = {
    "User-Agent": "Mozilla/5.0"
}

try:
    r = requests.get(full_url, headers=headers, timeout=30)

    st.write("📌 호출 URL:", r.url)
    st.write("📌 상태코드:", r.status_code)

    if r.status_code != 200:
        return pd.DataFrame(), f"HTTP 오류: {r.status_code}"

    # XML 미리보기
    with st.expander("🔍 서버 응답 보기"):
        st.code(r.text[:1000], language="xml")

    root = ET.fromstring(r.content)

    code = root.findtext(".//resultCode")
    msg = root.findtext(".//resultMsg")

    if code != "00":
        return pd.DataFrame(), f"API 오류 [{code}] {msg}"

    rows = []

    for item in root.findall(".//item"):

        def safe(tags, default="-"):
            for tag in tags:
                v = item.findtext(tag)
                if v and v.strip():
                    return v.strip()
            return default

        rows.append({
            "증권사": safe(["issuCoNm", "issucoNm"]),
            "종목명": safe(["isinNm"]),
            "기초자산": safe(["kndNm", "ulyNm"]),
            "낙인(KI)": safe(["bareAt", "kiBarrierRt"]),
            "수익률(연)": safe(["expYidRt"]),
            "청약종료일": safe(["subEndDt"])
        })

    return pd.DataFrame(rows), None

except Exception as e:
    return pd.DataFrame(), str(e)
```

# ---------------- 실행 ----------------

df, err = fetch_els_data()

if err:
st.error(err)
else:
st.success(f"🎉 {len(df)}건 조회 성공")

```
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

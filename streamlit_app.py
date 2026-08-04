```python
import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

st.set_page_config(page_title="ELS 비교기", layout="wide")

SERVICE_KEY = "S0%2BzGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0%2BDCnJZhm2oOwqTkGN%2BYWtVhbDZYkV4YtPUYEu4Qg%3D%3D"

st.title("📊 증권사별 ELS 조건 비교")

@st.cache_data(ttl=3600)
def fetch_els_data():

    # 실제 GW 엔드포인트
    url = "https://apis.data.go.kr/B552481/DerivesSvc/getDerivCombiIsinInfo"

    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": "1",
        "numOfRows": "100"
    }

    try:
        r = requests.get(url, params=params, timeout=30)

        st.write("호출 URL:", r.url)
        st.write("상태코드:", r.status_code)

        if r.status_code != 200:
            return pd.DataFrame(), f"HTTP 오류: {r.status_code}"

        # 응답 일부 확인
        st.code(r.text[:1000], language="xml")

        root = ET.fromstring(r.content)

        code = root.findtext(".//resultCode")
        msg = root.findtext(".//resultMsg")

        st.write("결과코드:", code)
        st.write("결과메시지:", msg)

        if code != "00":
            return pd.DataFrame(), f"API 오류 [{code}] {msg}"

        rows = []

        for item in root.findall(".//item"):
            rows.append({
                "증권사": item.findtext("issucoNm", default="-"),
                "종목명": item.findtext("isinNm", default="-"),
                "기초자산": item.findtext("ulyNm", default="-"),
                "낙인(KI)": item.findtext("kiBarrierRt", default="-"),
                "수익률(연)": item.findtext("expYidRt", default="-"),
                "청약종료일": item.findtext("subEndDt", default="-")
            })

        return pd.DataFrame(rows), None

    except Exception as e:
        return pd.DataFrame(), str(e)


# 🔥 여기 중요: 함수 호출
df, err = fetch_els_data()

if err:
    st.error(err)
else:
    st.success(f"조회 성공: {len(df)}건")
    st.dataframe(df, use_container_width=True)
```

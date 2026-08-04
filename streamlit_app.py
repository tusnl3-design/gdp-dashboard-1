import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

SERVICE_KEY = "S0%2BzGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0%2BDCnJZhm2oOwqTkGN%2BYWtVhbDZYkV4YtPUYEu4Qg%3D%3D"

@st.cache_data(ttl=3600)
def fetch_els_data():
    url = "https://apis.data.go.kr/B552481/DerivesSvc/getDerivCombiIsinInfo"

    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": "1",
        "numOfRows": "100"
    }

    r = requests.get(url, params=params, timeout=30)

    # 디버깅용
    st.text(f"호출 URL: {r.url}")
    st.text(f"상태코드: {r.status_code}")

    if r.status_code != 200:
        return pd.DataFrame(), r.text

    try:
        root = ET.fromstring(r.content)
    except Exception as e:
        return pd.DataFrame(), f"XML 파싱 실패: {e}\n{r.text[:500]}"

    # 결과코드 확인
    code = root.findtext(".//resultCode")
    msg = root.findtext(".//resultMsg")

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

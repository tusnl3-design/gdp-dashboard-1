import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="ELS API 진단 모드", layout="wide")

st.title("🔍 ELS API 연결 상세 진단")

# 1. 마이페이지에 있는 [Encoding 키]
ENCODING_KEY = "S0%2BzGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0%2BDCnJZhm2oOwqTkGN%2BYWtVhbDZYkV4YtPUYEu4Qg%3D%3D"

# 2. 마이페이지에 있는 [Decoding 키]
DECODING_KEY = "S0+zGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0+DCnJZhm2oOwqTkGN+YWtVhbDZYkV4YtPUYEu4Qg=="

key_type = st.radio("테스트할 키 선택", ["1. 인코딩 키 사용 (URL 직접 포함)", "2. 디코딩 키 사용 (params 이용)"])

if st.button("🚀 API 호출 테스트 실행"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    if "1." in key_type:
        # 인코딩 키를 URL에 직접 결합
        url = f"https://apis.data.go.kr/B552481/DerivesSvc/getElsOfrList?serviceKey={ENCODING_KEY}&pageNo=1&numOfRows=10"
        res = requests.get(url, headers=headers, timeout=15)
    else:
        # 디코딩 키를 params로 전달
        url = "https://apis.data.go.kr/B552481/DerivesSvc/getElsOfrList"
        params = {
            "serviceKey": DECODING_KEY,
            "pageNo": "1",
            "numOfRows": "10"
        }
        res = requests.get(url, params=params, headers=headers, timeout=15)
        
    st.write(f"**응답 상태 코드:** `{res.status_code}`")
    st.write("**요청한 최종 URL:**")
    st.code(res.url)
    
    st.write("**서버 응답 내용 (본문):**")
    st.code(res.text, language="xml")

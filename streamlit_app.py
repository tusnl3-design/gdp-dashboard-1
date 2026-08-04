import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import altair as alt

# 페이지 설정
st.set_page_config(
    page_title="증권사별 ELS 발행 현황 비교 대시보드",
    page_icon="📈",
    layout="wide"
)

st.title("📊 증권사별 ELS 발행 및 잔액 비교 대시보드")
st.markdown("""
공공데이터포털 **한국예탁결제원_파생결합증권정보서비스** API 데이터 또는 파일(Excel/CSV)을 활용하여 
각 증권사별 ELS 발행잔액과 추이를 비교·분석하는 대시보드입니다.
""")

# --- 사이드바 설정 ---
st.sidebar.header("⚙️ 데이터 설정 및 API 연동")

data_source = st.sidebar.radio(
    "데이터 소스 선택",
    ("공공데이터 API 직접 조회", "엑셀/CSV 파일 업로드")
)

# API 인증키 입력 (기본값 설정 가능)
default_api_key = "S0%2BZGZ9bwR8NYWqHCwXmbH2wUQ9VccXjooH2OVQiT0mrbO%2BDCnJZhm2oOwqTkGN%2B2BYwtVhbDZYK4YtPUPEu4Qg%3D%3D3D"
api_key = st.sidebar.text_input("공공데이터 API 인증키 (Encoding)", value=default_api_key, type="password")

# 조회 기준일 설정 (기본값: 오늘 또는 최근 영업일)
default_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
base_date = st.sidebar.text_input("조회기준일 (YYYYMMDD)", value=default_date)

@st.cache_data(ttl=3600)
def fetch_els_api(service_key, base_dt):
    """
    한국예탁결제원 파생결합증권 발행회사별 발행잔액 조회 API 호출 함수
    """
    url = "https://apis.data.go.kr/B552481/Derivessvc/getElsDlsIssucoBalanceStatusN1"
    
    params = {
        'serviceKey': service_key,
        'basDt': base_dt,
        'numOfRows': '100',
        'pageNo': '1'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            st.error(f"API 호출 실패 (상태 코드: {response.status_code})")
            return pd.DataFrame()
        
        # XML 파싱
        root = ET.fromstring(response.content)
        items = []
        
        # Open API 응답 구조에 맞추어 태그 탐색 (일반적인 공공데이터포털 표준 구조)
        for item in root.iter('item'):
            row = {}
            for child in item:
                row[child.tag] = child.text
            items.append(row)
            
        if not items:
            # item 태그가 없을 경우 다른 구조일 수 있으므로 전체 자식 노드 확인
            for elem in root.iter():
                if len(elem) == 0 and elem.text:
                    pass
        
        df = pd.DataFrame(items)
        return df
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# --- 데이터 로드 로직 ---
df = pd.DataFrame()

if data_source == "공공데이터 API 직접 조회":
    st.sidebar.info("💡 API 일일 트래픽 제한(100회)이 있으므로 주의하세요.")
    if st.sidebar.button("API로 최신 데이터 불러오기"):
        with st.spinner("한국예탁결제원 API에서 데이터를 불러오는 중입니다..."):
            df = fetch_els_api(api_key, base_date)
            if not df.empty:
                st.session_state['df_data'] = df
                st.success("데이터를 성공적으로 불러왔습니다!")
            else:
                st.warning("조회된 데이터가 없거나 API 인증키/파라미터를 확인해주세요.")
                
    if 'df_data' in st.session_state:
        df = st.session_state['df_data']

else:
    uploaded_file = st.sidebar.file_uploader("공공데이터포털에서 받은 엑셀 또는 CSV 파일을 업로드하세요", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("파일 업로드 성공!")
        except Exception as e:
            st.error(f"파일을 읽는 중 오류 발생: {e}")

# --- 메인 대시보드 화면 ---
if df.empty:
    st.info("👈 왼쪽 사이드바에서 **API 조회** 또는 **파일 업로드**를 진행해주세요.")
    
    # 가이드용 샘플 데이터 표시 안내
    with st.expander("📌 공공데이터포털 API 연동 가이드 및 컬럼 안내"):
        st.markdown("""
        * **주요 API 엔드포인트**: `/getElsDlsIssucoBalanceStatusN1` (발행회사별 파생결합증권 발행잔액 조회)
        * **주요 컬럼 구조 예시**:
          - `basDt`: 기준일자
          - `isuCoNm` / `issuerName`: 발행회사명 (증권사명)
          - `balAmt` / `balanceAmount`: 발행잔액
          - `isuCnt` / `issueCount`: 종목수
        """)
else:
    st.subheader("📋 수집된 ELS 원본 데이터 미리보기")
    st.dataframe(df.head(10), use_container_width=True)
    
    # 컬럼 자동 매핑 (API 응답 필드명에 따른 대응)
    cols = df.columns.tolist()
    
    # 증권사명, 발행잔액 컬럼 찾기 (유연하게 매핑)
    issuer_col = next((c for c in cols if 'co' in c.lower() or 'issuer' in c.lower() or '회사' in c), cols[0])
    balance_col = next((c for c in cols if 'bal' in c.lower() or 'amt' in c.lower() or '잔액' in c), cols[1] if len(cols) > 1 else cols[0])
    
    # 데이터 전처리 (잔액을 숫자로 변환)
    try:
        df[balance_col] = pd.to_numeric(df[balance_col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    except:
        pass

    st.markdown("---")
    st.subheader("📈 증권사별 ELS 발행잔액 비교 시각화")
    
    # 상위 증권사 비교 차트
    if issuer_col and balance_col:
        # 잔액 기준 상위 정렬
        chart_data = df.groupby(issuer_col)[balance_col].sum().reset_index()
        chart_data = chart_data.sort_values(by=balance_col, ascending=False)
        
        # Altair 바차트 생성
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X(f'{issuer_col}:N', sort='-y', title='증권사 (발행회사명)'),
            y=alt.Y(f'{balance_col}:Q', title='발행잔액'),
            color=alt.Color(f'{issuer_col}:N', legend=None),
            tooltip=[issuer_col, balance_col]
        ).properties(
            height=450
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)
        
        # 요약 지표 (KPI Metrics)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 발행잔액 합계", f"{chart_data[balance_col].sum():,.0f} 원")
        with col2:
            st.metric("조회된 증권사 수", f"{len(chart_data)} 개사")
        with col3:
            max_issuer = chart_data.iloc[0][issuer_col] if not chart_data.empty else "-"
            st.metric("최대 발행 증권사", max_issuer)
            
    else:
        st.warning("차트를 그리기 위한 적절한 컬럼을 찾지 못했습니다. 데이터 구조를 확인해주세요.")

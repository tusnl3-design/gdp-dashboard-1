import streamlit as st
import pandas as pd
import requests
import urllib.parse

# ---------------------------------------------------------
# 1. 금융감독원 Open API 인증키 설정
# ---------------------------------------------------------
RAW_API_KEY = "S0%2BzGZ9bwR8NYWqHCwXmbH2wQU9VccXjo0h2OVQIt0mrb0%2BDCnJZhm2oOwqTkGN%2BYwtVhbDZYkV4YtPUYEu4Qg%3D%3D"

# 특수문자(%2B 등) 디코딩 처리
API_KEY = urllib.parse.unquote(RAW_API_KEY)

st.set_page_config(page_title="실시간 ELS/ELB 큐레이터", layout="wide")

st.title("📢 실시간 ELS/ELB 추천 브리핑 (금감원 API 연동)")
st.caption("금융감독원 통합공시 API를 통해 매일 청약 중인 실제 ELS/ELB 정보를 실시간으로 수집합니다.")

# ---------------------------------------------------------
# 2. 금감원 API 데이터 실시간 호출 함수
# ---------------------------------------------------------
@st.cache_data(ttl=3600)  # 1시간마다 데이터 자동 갱신
def fetch_els_data(api_key):
    # 금융감독원 파생결합증권(ELS) 상품 조회 API URL
    url = "http://finlife.fss.or.kr/finlifeapi/elsOptionSearch.json"
    params = {
        "auth": api_key,
        "topFinGrpNo": "060000",
        "pageNo": "1"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        # 응답이 JSON인지 확인
        try:
            data = response.json()
        except Exception:
            return pd.DataFrame(), f"API 응답 형식 오류 (HTTP 상태코드: {response.status_code}). 인증키 승인 상태를 확인해 주세요."
        
        # API 정상 응답 확인
        if data.get("result", {}).get("err_cd") == "000":
            base_list = data["result"].get("baseList", [])
            option_list = data["result"].get("optionList", [])
            
            # 기본 정보와 옵션 정보 결합
            df_base = pd.DataFrame(base_list)
            df_option = pd.DataFrame(option_list)
            
            if not df_base.empty and not df_option.empty:
                merged = pd.merge(df_base, df_option, on="fin_prdt_cd", how="inner")
                return merged, None
            elif not df_base.empty:
                return df_base, None
            else:
                return pd.DataFrame(), "현재 청약 가능 기간인 ELS/ELB 상품이 없거나 공시 전입니다."
        else:
            err_msg = data.get("result", {}).get("err_msg", "API 인증 오류")
            return pd.DataFrame(), f"API 오류: {err_msg}"
            
    except Exception as e:
        return pd.DataFrame(), f"데이터를 불러오는 중 오류가 발생했습니다: {str(e)}"

# ---------------------------------------------------------
# 3. 실시간 데이터 수집 및 정제
# ---------------------------------------------------------
with st.spinner("금융감독원에서 오늘의 최신 ELS/ELB 데이터를 수집 중입니다..."):
    df_raw, error = fetch_els_data(API_KEY)

if error:
    st.info(f"💡 안내: {error}")
elif df_raw.empty:
    st.info("현재 청약 진행 중인 상품이 없습니다.")
else:
    # 필요한 항목 가공 (칼럼이 없는 경우 안전하게 처리)
    df_processed = pd.DataFrame({
        "증권사": df_raw.get("kor_co_nm", "증권사 미공시"),
        "종목명": df_raw.get("fin_prdt_nm", "상품명 미공시"),
        "기초자산": df_raw.get("und_ast_nm", "자산 정보 참조"),
        "제시수익률": pd.to_numeric(df_raw.get("etc_rate", 0), errors="coerce").fillna(0),
        "낙인(KI)": df_raw.get("ki_barr", "미공시"),
        "마감일": df_raw.get("sale_end_nd", "일정 참조")
    })

    # 제시수익률 높은 순 정렬
    df_sorted = df_processed.sort_values(by="제시수익률", ascending=False).reset_index(drop=True)

    # ---------------------------------------------------------
    # 4. 카톡/텔레그램 공유용 브리핑 텍스트 자동 생성
    # ---------------------------------------------------------
    medals = ["🥇", "🥈", "🥉"]
    briefing_text = "📢 [금감원 실시간 ELS/ELB 큐레이션]\n-------------------------------------\n"
    
    top_items = df_sorted.head(10) # 수익률 상위 10개 추출
    
    for idx, row in top_items.iterrows():
        medal = medals[idx] if idx < 3 else "▪️"
        briefing_text += f"{medal} {row['증권사']} {row['종목명']}({row['제시수익률']}%) {row['기초자산']} ~{row['마감일']}\n"

    briefing_text += "\n-------------------------------------\n⚠️ [투자 유의사항]\n본 정보는 금감원 공시 데이터 기반 참고용이며, 상세조건은 증권사 청약 공모안을 확인하세요."

    # ---------------------------------------------------------
    # 5. 화면 출력
    # ---------------------------------------------------------
    st.subheader("📋 카카오톡 / 텔레그램 복사용 브리핑")
    st.code(briefing_text, language="text")

    st.divider()
    st.subheader("📊 오늘의 청약 ELS/ELB 전체 리스트")
    st.dataframe(df_sorted, use_container_width=True, hide_index=True)

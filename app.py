"""
LLM API Cost Calculator - 홈 페이지

LLM API 비용 계산기의 메인 홈 페이지
"""

import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="LLM API Cost Calculator",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 타이틀
st.title("🧮 LLM API Cost Calculator")
st.markdown("### LLM API 비용을 빠르고 쉽게 계산하고 비교하세요")

st.divider()

# 소개
st.header("📌 개요")
st.markdown(
    """
    **LLM API Cost Calculator**는 다양한 LLM 모델의 API 사용 비용을 계산하고 비교하는 도구입니다.

    파일을 업로드하면 자동으로 토큰 수를 계산하고, 여러 모델의 예상 비용을 한눈에 비교할 수 있습니다.
    """
)

# 주요 기능
st.header("✨ 주요 기능")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📁 다양한 파일 지원")
    st.markdown(
        """
        - 텍스트 파일 (.txt, .md, .py, .js 등)
        - PDF 문서
        - Word 문서 (.docx)
        - Excel 스프레드시트 (.xlsx, .xls, .csv)
        - JSON 데이터
        - 이미지 파일 (.png, .jpg, .jpeg)
        """
    )

with col2:
    st.subheader("🤖 최신 LLM 모델")
    st.markdown(
        """
        - **OpenAI**: GPT-5, GPT-5 Mini, GPT-5 Nano
        - **Anthropic**: Claude 4.1 Opus/Sonnet/Haiku
        - **Google**: Gemini 2.5 Pro/Flash/Flash Lite
        - **Perplexity**: Sonar Base/Pro, Perplexity Max
        """
    )

with col3:
    st.subheader("💰 비용 비교 & 분석")
    st.markdown(
        """
        - 실시간 토큰 계산
        - 모델별 비용 비교
        - USD/KRW 환율 지원
        - 페이지 기반 출력 예측
        - CSV/Excel/JSON 내보내기
        """
    )

st.divider()

# 사용 방법
st.header("🚀 사용 방법")
st.markdown(
    """
    1. **좌측 사이드바**에서 **apiCost** 페이지로 이동
    2. 비용을 계산할 **파일을 업로드**
    3. 비교하고 싶은 **LLM 모델을 선택**
    4. 출력 토큰 설정 (페이지 기반 또는 비율 기반)
    5. 환율 설정 (기본: 1,500 KRW/USD)
    6. **결과 확인** 및 내보내기
    """
)

# 시작하기 버튼
st.divider()
st.markdown("### 👈 좌측 사이드바에서 **apiCost** 페이지로 이동하여 시작하세요!")

# 푸터
st.divider()
st.caption("🤖 Built with Streamlit | 💡 Powered by LLM APIs")
st.caption("📊 모델 정보는 2025년 1월 기준입니다.")

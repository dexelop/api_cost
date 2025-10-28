"""
LLM API Cost Calculator - Streamlit 메인 앱

파일을 업로드하고 다양한 LLM 모델의 API 비용을 계산하고 비교하는 웹 애플리케이션
"""

import streamlit as st

from src.ui.file_uploader import render_file_uploader
from src.ui.model_selector import render_model_selector
from src.ui.results_display import render_results


def main():
    """메인 애플리케이션 함수"""

    # 페이지 설정
    st.set_page_config(
        page_title="LLM API Cost Calculator",
        page_icon="🧮",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 타이틀
    st.title("🧮 LLM API Cost Calculator")
    st.markdown(
        """
        파일을 업로드하고 다양한 LLM 모델의 예상 API 비용을 비교해보세요.
        """
    )

    # 세션 스테이트 초기화
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = []

    if "selected_models" not in st.session_state:
        # 4개 서비스(OpenAI, Anthropic, Google, Perplexity)의 모든 모델 기본 선택
        st.session_state.selected_models = [
            # OpenAI
            "gpt-5", "gpt-5-mini", "gpt-5-nano",
            # Anthropic
            "claude-4.1-opus", "claude-4.1-sonnet", "claude-3.5-haiku",
            # Google
            "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite",
            # Perplexity
            "sonar-base", "sonar-pro", "perplexity-max",
        ]

    if "output_ratio" not in st.session_state:
        st.session_state.output_ratio = 0.3  # 출력 토큰 비율 (입력의 30%)

    if "exchange_rate" not in st.session_state:
        st.session_state.exchange_rate = 1500.0  # USD to KRW 환율

    if "output_mode" not in st.session_state:
        st.session_state.output_mode = "page"  # "ratio" or "page"

    if "output_pages" not in st.session_state:
        st.session_state.output_pages = 5  # 페이지 수 (약 500 토큰/페이지)

    # 레이아웃: 사이드바 + 메인
    with st.sidebar:
        st.header("⚙️ 설정")

        # 모델 선택
        st.subheader("🤖 모델 선택")
        selected_models = render_model_selector()
        st.session_state.selected_models = selected_models

        # 출력 토큰 설정
        st.subheader("📊 출력 토큰 설정")
        output_mode = st.radio(
            "출력 계산 방식",
            options=["page", "ratio"],
            format_func=lambda x: "📄 페이지 기반" if x == "page" else "📊 비율 기반",
            horizontal=True,
        )
        st.session_state.output_mode = output_mode

        if output_mode == "page":
            output_pages = st.number_input(
                "예상 출력 페이지 수",
                min_value=1,
                max_value=50,
                value=st.session_state.output_pages,
                step=1,
                help="1페이지 = 약 500 토큰 (보고서 기준)",
            )
            st.session_state.output_pages = output_pages
            st.caption(f"💡 예상 출력: 약 {output_pages * 500:,} 토큰")
        else:
            output_ratio = st.slider(
                "입력 토큰 대비 출력 토큰 비율",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state.output_ratio,
                step=0.1,
                help="예상 출력 토큰 수 = 입력 토큰 수 × 비율",
            )
            st.session_state.output_ratio = output_ratio

        # 환율 설정
        st.subheader("💱 환율 설정")
        exchange_rate = st.number_input(
            "USD → KRW 환율",
            min_value=1.0,
            max_value=10000.0,
            value=st.session_state.exchange_rate,
            step=10.0,
            help="달러를 원화로 환산할 환율",
        )
        st.session_state.exchange_rate = exchange_rate

        # 정보
        st.divider()
        st.caption("💡 Tip: 여러 파일을 동시에 업로드할 수 있습니다.")
        st.caption("📊 선택한 모델들의 비용을 자동으로 비교합니다.")

    # 메인 영역
    col1, col2 = st.columns([1, 2])

    with col1:
        # 파일 업로더
        st.header("📁 파일 업로드")
        processed_files = render_file_uploader()

        if processed_files:
            st.session_state.processed_files = processed_files
            st.success(f"✅ {len(processed_files)}개 파일 처리 완료")

    with col2:
        # 결과 표시
        st.header("💰 비용 비교")

        if st.session_state.processed_files and st.session_state.selected_models:
            render_results(
                st.session_state.processed_files,
                st.session_state.selected_models,
                st.session_state.output_ratio,
                st.session_state.exchange_rate,
                st.session_state.output_mode,
                st.session_state.output_pages,
            )
        else:
            st.info("👈 파일을 업로드하고 모델을 선택해주세요.")


if __name__ == "__main__":
    main()

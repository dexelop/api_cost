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
        st.session_state.selected_models = ["gpt-4o", "claude-3.5-sonnet", "gemini-2.0-flash"]

    if "output_ratio" not in st.session_state:
        st.session_state.output_ratio = 0.3  # 출력 토큰 비율 (입력의 30%)

    # 레이아웃: 사이드바 + 메인
    with st.sidebar:
        st.header("⚙️ 설정")

        # 모델 선택
        st.subheader("🤖 모델 선택")
        selected_models = render_model_selector()
        st.session_state.selected_models = selected_models

        # 출력 토큰 비율 설정
        st.subheader("📊 출력 토큰 비율")
        output_ratio = st.slider(
            "입력 토큰 대비 출력 토큰 비율",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.output_ratio,
            step=0.1,
            help="예상 출력 토큰 수 = 입력 토큰 수 × 비율",
        )
        st.session_state.output_ratio = output_ratio

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
            )
        else:
            st.info("👈 파일을 업로드하고 모델을 선택해주세요.")


if __name__ == "__main__":
    main()

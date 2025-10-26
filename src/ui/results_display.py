"""
결과 표시 UI 컴포넌트

토큰 수와 비용 추정 결과를 표시합니다.
"""

from typing import List
from datetime import datetime

import pandas as pd
import streamlit as st

from src.processors.base import ProcessedFile
from src.pricing.calculator import PriceCalculator
from src.tokenizers.file_tokenizer import FileTokenizer
from src.exporters.csv_exporter import CSVExporter
from src.exporters.excel_exporter import ExcelExporter
from src.exporters.json_exporter import JSONExporter


def render_results(
    processed_files: List[ProcessedFile],
    selected_models: List[str],
    output_ratio: float,
):
    """
    결과 표시 UI 렌더링

    Args:
        processed_files: 처리된 파일 리스트
        selected_models: 선택된 모델 ID 리스트
        output_ratio: 출력 토큰 비율
    """
    if not processed_files:
        st.info("📂 파일을 업로드해주세요.")
        return

    if not selected_models:
        st.warning("⚠️ 모델을 선택해주세요.")
        return

    # 토큰 계산기 및 가격 계산기 초기화
    tokenizer = FileTokenizer()
    calculator = PriceCalculator()

    # 전체 토큰 수 계산
    total_tokens = 0
    file_token_details = []

    for pfile in processed_files:
        # 파일별 토큰 수 계산
        token_count = tokenizer.count_tokens_from_processed_file(pfile)
        total_tokens += token_count.token_count

        file_token_details.append(
            {
                "파일명": pfile.metadata.get("file_name", "Unknown"),
                "타입": pfile.file_type,
                "토큰 수": f"{token_count.token_count:,}",
            }
        )

    # 토큰 정보 표시
    st.subheader("📊 토큰 분석")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 입력 토큰", f"{total_tokens:,}")
    with col2:
        estimated_output = int(total_tokens * output_ratio)
        st.metric("예상 출력 토큰", f"{estimated_output:,}")
    with col3:
        st.metric("총 토큰", f"{total_tokens + estimated_output:,}")

    # 파일별 토큰 수 표시
    if len(processed_files) > 1:
        with st.expander("📋 파일별 토큰 수"):
            df_files = pd.DataFrame(file_token_details)
            st.dataframe(df_files, use_container_width=True)

    st.divider()

    # 모델별 비용 계산
    st.subheader("💰 모델별 비용 비교")

    # 비용 추정
    estimated_output = int(total_tokens * output_ratio)
    estimates = calculator.compare_models(
        selected_models, input_tokens=total_tokens, output_tokens=estimated_output
    )

    if not estimates:
        st.error("❌ 선택된 모델의 비용을 계산할 수 없습니다.")
        return

    # 결과 테이블 생성
    result_data = []
    for est in estimates:
        result_data.append(
            {
                "모델": est.model.model_name,
                "제공업체": est.model.provider.upper(),
                "입력 비용": f"${est.input_cost:.6f}",
                "출력 비용": f"${est.output_cost:.6f}",
                "총 비용": f"${est.total_cost:.6f}",
                "Context 윈도우": f"{est.model.context_window:,}",
            }
        )

    df_results = pd.DataFrame(result_data)

    # 결과 테이블 표시
    st.dataframe(
        df_results,
        use_container_width=True,
        hide_index=True,
    )

    # 가장 저렴한 모델 강조
    cheapest = estimates[0]
    st.success(
        f"💡 **가장 저렴한 모델**: {cheapest.model.model_name} "
        f"(${cheapest.total_cost:.6f})"
    )

    # 내보내기
    st.divider()
    st.subheader("📥 결과 내보내기")

    csv_exporter = CSVExporter()
    excel_exporter = ExcelExporter()
    json_exporter = JSONExporter()

    # CSV 다운로드 (1행)
    st.markdown("**CSV 형식**")
    col1, col2, col3 = st.columns(3)

    with col1:
        # 파일별 토큰 정보 CSV
        csv_files = csv_exporter.export_file_tokens(processed_files)
        st.download_button(
            label="📄 파일 토큰 정보",
            data=csv_files,
            file_name=f"file_tokens_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="파일별 토큰 수 정보를 CSV로 다운로드",
        )

    with col2:
        # 모델별 비용 비교 CSV
        csv_costs = csv_exporter.export_cost_estimates(estimates, output_ratio)
        st.download_button(
            label="💰 비용 비교",
            data=csv_costs,
            file_name=f"cost_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="모델별 비용 비교 정보를 CSV로 다운로드",
        )

    with col3:
        # 통합 CSV
        csv_combined = csv_exporter.export_combined(processed_files, estimates, output_ratio)
        st.download_button(
            label="📊 전체 리포트 (CSV)",
            data=csv_combined,
            file_name=f"full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="모든 정보를 포함한 통합 리포트를 CSV로 다운로드",
        )

    # Excel & JSON 다운로드 (2행)
    st.markdown("**Excel & JSON 형식**")
    col4, col5, col6 = st.columns(3)

    with col4:
        # Excel 워크북
        excel_data = excel_exporter.export_workbook(processed_files, estimates, output_ratio)
        st.download_button(
            label="📊 Excel 워크북",
            data=excel_data,
            file_name=f"llm_cost_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="요약, 파일 정보, 비용 비교 시트를 포함한 Excel 워크북",
        )

    with col5:
        # JSON 데이터
        json_data = json_exporter.export_json(processed_files, estimates, output_ratio)
        st.download_button(
            label="🔧 JSON 데이터",
            data=json_data,
            file_name=f"llm_cost_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            help="구조화된 JSON 형식으로 모든 데이터 내보내기",
        )

    st.divider()

    # 시각화
    st.subheader("📈 비용 시각화")

    # 차트 데이터 준비
    chart_data = pd.DataFrame(
        {
            "모델": [est.model.model_name for est in estimates],
            "총 비용 (USD)": [est.total_cost for est in estimates],
            "입력 비용 (USD)": [est.input_cost for est in estimates],
            "출력 비용 (USD)": [est.output_cost for est in estimates],
        }
    )

    # 총 비용 막대 그래프
    st.bar_chart(chart_data.set_index("모델")["총 비용 (USD)"])

    # 입력/출력 비용 분해
    with st.expander("📊 입력/출력 비용 분해"):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**입력 비용**")
            st.bar_chart(chart_data.set_index("모델")["입력 비용 (USD)"])

        with col2:
            st.write("**출력 비용**")
            st.bar_chart(chart_data.set_index("모델")["출력 비용 (USD)"])

    # 상세 정보 표시
    with st.expander("🔍 상세 정보"):
        for est in estimates:
            st.markdown(f"### {est.model.model_name}")
            st.write(f"**제공업체**: {est.model.provider}")
            st.write(f"**입력 토큰**: {est.input_tokens:,}")
            st.write(f"**출력 토큰**: {est.output_tokens:,}")
            st.write(f"**입력 가격**: ${est.model.input_price:.4f} per 1K tokens")
            st.write(f"**출력 가격**: ${est.model.output_price:.4f} per 1K tokens")
            st.write(f"**입력 비용**: ${est.input_cost:.6f}")
            st.write(f"**출력 비용**: ${est.output_cost:.6f}")
            st.write(f"**총 비용**: ${est.total_cost:.6f}")

            # 추가 기능
            features = []
            if est.model.vision_capable:
                features.append("👁️ Vision 지원")
            if est.model.online_search:
                features.append("🌐 온라인 검색 지원")
            if est.model.input_price_long:
                features.append("📄 장문 가격 지원")

            if features:
                st.write("**기능**: " + ", ".join(features))

            st.divider()

"""
파일 업로더 UI 컴포넌트

파일을 업로드하고 처리하는 UI를 제공합니다.
"""

from pathlib import Path
from typing import List

import streamlit as st

from api_cost_modules.config.settings import settings
from api_cost_modules.processors.text_processor import TextFileProcessor
from api_cost_modules.processors.pdf_processor import PDFFileProcessor
from api_cost_modules.processors.excel_processor import ExcelFileProcessor
from api_cost_modules.processors.word_processor import WordFileProcessor
from api_cost_modules.processors.image_processor import ImageFileProcessor
from api_cost_modules.processors.base import ProcessedFile


def get_processor_for_file(file_path: Path):
    """
    파일 확장자에 따라 적절한 프로세서 반환

    Args:
        file_path: 파일 경로

    Returns:
        적절한 프로세서 인스턴스
    """
    suffix = file_path.suffix.lower()

    if suffix in [".txt", ".md", ".py", ".js", ".json", ".yaml", ".yml"]:
        return TextFileProcessor()
    elif suffix == ".pdf":
        return PDFFileProcessor()
    elif suffix in [".xlsx", ".xls", ".csv"]:
        return ExcelFileProcessor()
    elif suffix in [".docx", ".docm"]:
        return WordFileProcessor()
    elif suffix in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
        return ImageFileProcessor()
    else:
        # 기본값: 텍스트 프로세서
        return TextFileProcessor()


def render_file_uploader() -> List[ProcessedFile]:
    """
    파일 업로더 UI 렌더링

    Returns:
        List[ProcessedFile]: 처리된 파일 리스트
    """
    # 파일 업로드
    uploaded_files = st.file_uploader(
        "파일 선택",
        type=["txt", "md", "pdf", "docx", "xlsx", "xls", "csv", "json", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help=f"최대 {settings.MAX_FILES_COUNT}개 파일, 파일당 최대 {settings.MAX_FILE_SIZE_MB}MB",
    )

    if not uploaded_files:
        st.info("📂 파일을 선택하거나 드래그앤드롭하세요.")
        return []

    # 파일 개수 체크
    if len(uploaded_files) > settings.MAX_FILES_COUNT:
        st.error(f"❌ 최대 {settings.MAX_FILES_COUNT}개 파일만 업로드할 수 있습니다.")
        return []

    processed_files = []

    # 프로그레스 바
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, uploaded_file in enumerate(uploaded_files):
        # 진행 상황 업데이트
        progress = (idx + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        status_text.text(f"처리 중: {uploaded_file.name} ({idx + 1}/{len(uploaded_files)})")

        # 파일 크기 체크
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            st.warning(
                f"⚠️ {uploaded_file.name}: 파일이 너무 큽니다 "
                f"({file_size_mb:.2f}MB > {settings.MAX_FILE_SIZE_MB}MB)"
            )
            continue

        temp_file_path = None
        try:
            # 임시 파일로 저장
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)

            temp_file_path = temp_dir / uploaded_file.name

            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 파일 처리
            processor = get_processor_for_file(temp_file_path)
            processed = processor.process(temp_file_path)

            if processed.is_success:
                processed_files.append(processed)
            else:
                st.error(f"❌ {uploaded_file.name}: {processed.error}")

        except Exception as e:
            st.error(f"❌ {uploaded_file.name} 처리 실패: {str(e)}")
        finally:
            # 임시 파일 삭제 (반드시 실행)
            if temp_file_path is not None and temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                except Exception:
                    # 삭제 실패는 무시 (다음 실행 시 덮어쓰기됨)
                    pass

    # 프로그레스 바 제거
    progress_bar.empty()
    status_text.empty()

    # 처리 결과 요약
    if processed_files:
        st.success(f"✅ {len(processed_files)}개 파일 처리 완료")

        # 파일 정보 표시
        with st.expander("📋 처리된 파일 정보"):
            for pf in processed_files:
                st.markdown(f"**{pf.metadata.get('file_name', 'Unknown')}**")
                st.caption(f"타입: {pf.file_type} | 크기: {pf.metadata.get('file_size_mb', 0):.2f}MB")
                if pf.file_type != "image":
                    st.caption(f"문자 수: {pf.content_length:,}")

    return processed_files

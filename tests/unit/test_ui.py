"""
UI 컴포넌트에 대한 유닛 테스트

Streamlit UI의 로직 부분을 검증합니다.
"""

from pathlib import Path

import pytest

from src.ui.file_uploader import get_processor_for_file
from src.processors.text_processor import TextFileProcessor
from src.processors.pdf_processor import PDFFileProcessor
from src.processors.excel_processor import ExcelFileProcessor
from src.processors.word_processor import WordFileProcessor
from src.processors.image_processor import ImageFileProcessor


class TestFileUploader:
    """파일 업로더 컴포넌트 테스트"""

    def test_get_processor_for_text_files(self):
        """텍스트 파일 프로세서 선택 테스트"""
        # 다양한 텍스트 파일 확장자
        text_extensions = [".txt", ".md", ".py", ".js", ".json", ".yaml", ".yml"]

        for ext in text_extensions:
            file_path = Path(f"test{ext}")
            processor = get_processor_for_file(file_path)
            assert isinstance(processor, TextFileProcessor)

    def test_get_processor_for_pdf(self):
        """PDF 파일 프로세서 선택 테스트"""
        file_path = Path("test.pdf")
        processor = get_processor_for_file(file_path)
        assert isinstance(processor, PDFFileProcessor)

    def test_get_processor_for_excel(self):
        """Excel 파일 프로세서 선택 테스트"""
        excel_extensions = [".xlsx", ".xls", ".csv"]

        for ext in excel_extensions:
            file_path = Path(f"test{ext}")
            processor = get_processor_for_file(file_path)
            assert isinstance(processor, ExcelFileProcessor)

    def test_get_processor_for_word(self):
        """Word 파일 프로세서 선택 테스트"""
        word_extensions = [".docx", ".docm"]

        for ext in word_extensions:
            file_path = Path(f"test{ext}")
            processor = get_processor_for_file(file_path)
            assert isinstance(processor, WordFileProcessor)

    def test_get_processor_for_images(self):
        """이미지 파일 프로세서 선택 테스트"""
        image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".webp"]

        for ext in image_extensions:
            file_path = Path(f"test{ext}")
            processor = get_processor_for_file(file_path)
            assert isinstance(processor, ImageFileProcessor)

    def test_get_processor_for_unknown_extension(self):
        """알 수 없는 확장자 처리 테스트"""
        # 알 수 없는 확장자는 기본적으로 TextFileProcessor 사용
        file_path = Path("test.unknown")
        processor = get_processor_for_file(file_path)
        assert isinstance(processor, TextFileProcessor)

    def test_get_processor_case_insensitive(self):
        """대소문자 구분 없는 확장자 처리 테스트"""
        # 대문자 확장자도 올바르게 처리되어야 함
        file_path = Path("test.PDF")
        processor = get_processor_for_file(file_path)
        assert isinstance(processor, PDFFileProcessor)

        file_path = Path("test.XLSX")
        processor = get_processor_for_file(file_path)
        assert isinstance(processor, ExcelFileProcessor)

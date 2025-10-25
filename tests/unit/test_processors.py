"""
파일 프로세서 모듈에 대한 유닛 테스트

각 프로세서의 기능이 올바르게 작동하는지 검증합니다.
"""

from pathlib import Path

import pytest
from PIL import Image

from src.processors.text_processor import TextFileProcessor
from src.processors.pdf_processor import PDFFileProcessor
from src.processors.excel_processor import ExcelFileProcessor
from src.processors.word_processor import WordFileProcessor
from src.processors.image_processor import ImageFileProcessor


class TestTextFileProcessor:
    """TextFileProcessor에 대한 테스트"""

    def test_supported_extensions(self):
        """지원되는 확장자 목록 확인"""
        processor = TextFileProcessor()

        assert ".txt" in processor.supported_extensions
        assert ".md" in processor.supported_extensions
        assert ".py" in processor.supported_extensions
        assert ".json" in processor.supported_extensions

    def test_is_supported(self, tmp_path):
        """파일 확장자 지원 여부 확인"""
        processor = TextFileProcessor()

        # 지원되는 파일
        txt_file = tmp_path / "test.txt"
        txt_file.touch()
        assert processor.is_supported(txt_file) is True

        # 지원되지 않는 파일
        unsupported_file = tmp_path / "test.exe"
        unsupported_file.touch()
        assert processor.is_supported(unsupported_file) is False

    def test_read_file_content(self, tmp_path):
        """파일 내용 읽기 테스트"""
        processor = TextFileProcessor()

        # 테스트 파일 생성
        test_file = tmp_path / "test.txt"
        test_content = "Hello, LLM API Cost Calculator!\n한글 테스트"
        test_file.write_text(test_content, encoding="utf-8")

        # 파일 읽기
        content = processor.read_file_content(test_file)
        assert content == test_content

    def test_process_success(self, tmp_path):
        """파일 처리 성공 케이스"""
        processor = TextFileProcessor()

        # 테스트 파일 생성
        test_file = tmp_path / "test.txt"
        test_content = "Test content\nLine 2\nLine 3"
        test_file.write_text(test_content, encoding="utf-8")

        # 파일 처리
        result = processor.process(test_file)

        assert result.is_success is True
        assert result.content == test_content
        assert result.file_type == "text"
        assert result.metadata["line_count"] == 3
        assert result.metadata["word_count"] == 6  # "Test", "content", "Line", "2", "Line", "3"


class TestImageFileProcessor:
    """ImageFileProcessor에 대한 테스트"""

    def test_supported_extensions(self):
        """지원되는 확장자 목록 확인"""
        processor = ImageFileProcessor()

        assert ".png" in processor.supported_extensions
        assert ".jpg" in processor.supported_extensions
        assert ".jpeg" in processor.supported_extensions

    def test_estimate_image_tokens_small(self):
        """작은 이미지 토큰 추정"""
        processor = ImageFileProcessor()

        tokens = processor.estimate_image_tokens(300, 300)

        assert "claude_estimated_tokens" in tokens
        assert "gpt4v_estimated_tokens" in tokens
        assert tokens["claude_estimated_tokens"] > 0
        assert tokens["gpt4v_estimated_tokens"] > 0

    def test_estimate_image_tokens_large(self):
        """큰 이미지 토큰 추정"""
        processor = ImageFileProcessor()

        tokens = processor.estimate_image_tokens(1920, 1080)

        # 큰 이미지는 더 많은 토큰 필요
        assert tokens["claude_estimated_tokens"] >= 3000
        assert tokens["gpt4v_estimated_tokens"] > 170  # 최소 1타일

    def test_process_with_generated_image(self, tmp_path):
        """생성한 테스트 이미지 처리"""
        processor = ImageFileProcessor()

        # 테스트 이미지 생성 (100x100 빨간색 이미지)
        test_image_path = tmp_path / "test.png"
        img = Image.new("RGB", (100, 100), color="red")
        img.save(test_image_path)

        # 이미지 처리
        result = processor.process(test_image_path)

        assert result.is_success is True
        assert result.file_type == "image"
        assert result.metadata["width"] == 100
        assert result.metadata["height"] == 100
        assert result.metadata["format"] == "PNG"
        assert "claude_estimated_tokens" in result.metadata


class TestBaseFileProcessor:
    """BaseFileProcessor 공통 기능 테스트"""

    def test_validate_file_not_exists(self, tmp_path):
        """존재하지 않는 파일 검증"""
        processor = TextFileProcessor()

        non_existent = tmp_path / "does_not_exist.txt"

        with pytest.raises(FileNotFoundError):
            processor.validate_file(non_existent)

    def test_validate_file_unsupported_extension(self, tmp_path):
        """지원하지 않는 확장자 검증"""
        processor = TextFileProcessor()

        # PDF 파일 생성 (Text 프로세서는 지원하지 않음)
        unsupported_file = tmp_path / "test.pdf"
        unsupported_file.touch()

        with pytest.raises(ValueError, match="지원하지 않는 파일 형식"):
            processor.validate_file(unsupported_file)

    def test_get_file_metadata(self, tmp_path):
        """파일 메타데이터 추출"""
        processor = TextFileProcessor()

        # 테스트 파일 생성
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        metadata = processor.get_file_metadata(test_file)

        assert "file_name" in metadata
        assert "file_size" in metadata
        assert "file_size_mb" in metadata
        assert "extension" in metadata
        assert metadata["file_name"] == "test.txt"
        assert metadata["extension"] == ".txt"


class TestProcessorIntegration:
    """프로세서 통합 테스트"""

    def test_multiple_processors(self, tmp_path):
        """여러 프로세서가 각자의 파일을 올바르게 처리하는지 확인"""
        # 텍스트 파일
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Text content")

        txt_processor = TextFileProcessor()
        txt_result = txt_processor.process(txt_file)
        assert txt_result.is_success

        # 이미지 파일
        img_file = tmp_path / "test.png"
        img = Image.new("RGB", (50, 50))
        img.save(img_file)

        img_processor = ImageFileProcessor()
        img_result = img_processor.process(img_file)
        assert img_result.is_success

        # 각 프로세서가 다른 타입 반환 확인
        assert txt_result.file_type == "text"
        assert img_result.file_type == "image"

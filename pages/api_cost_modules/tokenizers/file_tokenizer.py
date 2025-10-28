"""
파일 토크나이저

ProcessedFile 객체를 받아서 파일 타입별로 적절한 토큰 계산을 수행합니다.
"""

from pathlib import Path
from typing import Union

from api_cost_modules.processors.base import ProcessedFile

from .base import TokenCount
from .image_tokenizer import ImageTokenizer
from .text_tokenizer import TextTokenizer


class FileTokenizer:
    """
    파일 토크나이저

    파일 타입에 따라 적절한 토크나이저를 사용하여 토큰을 계산합니다.
    """

    def __init__(self, model_name: str = "gpt-4"):
        """
        파일 토크나이저 초기화

        Args:
            model_name: 사용할 모델 이름
        """
        self.model_name = model_name
        self.text_tokenizer = TextTokenizer(model_name=model_name)
        self.image_tokenizer = ImageTokenizer(model_name=model_name)

    def count_tokens_from_processed_file(self, processed_file: ProcessedFile) -> TokenCount:
        """
        ProcessedFile 객체에서 토큰 수 계산

        파일 타입에 따라 적절한 토큰 계산 방식을 사용합니다.

        Args:
            processed_file: 프로세서가 처리한 파일 객체

        Returns:
            TokenCount: 토큰 계산 결과
        """
        # 파일 처리 중 에러가 있었다면 0 반환
        if not processed_file.is_success:
            return TokenCount(
                text="",
                token_count=0,
                model_name=self.model_name,
                error=f"파일 처리 실패: {processed_file.error}",
            )

        # 파일 타입에 따라 처리
        if processed_file.file_type == "image":
            # 이미지 파일: 메타데이터에서 토큰 정보 추출
            return self._count_image_tokens(processed_file)
        else:
            # 텍스트 파일 (text, pdf, excel, word 등): 추출된 텍스트 사용
            return self._count_text_tokens(processed_file)

    def _count_text_tokens(self, processed_file: ProcessedFile) -> TokenCount:
        """
        텍스트 기반 파일의 토큰 계산

        Args:
            processed_file: 처리된 파일 객체

        Returns:
            TokenCount: 토큰 계산 결과
        """
        # 추출된 텍스트로 토큰 계산
        result = self.text_tokenizer.count_tokens(processed_file.content)

        # 파일 정보를 메타데이터에 추가
        result.metadata.update(
            {
                "file_name": processed_file.metadata.get("file_name", ""),
                "file_type": processed_file.file_type,
                "file_size_mb": processed_file.metadata.get("file_size_mb", 0),
            }
        )

        return result

    def _count_image_tokens(self, processed_file: ProcessedFile) -> TokenCount:
        """
        이미지 파일의 토큰 추정

        Args:
            processed_file: 처리된 파일 객체

        Returns:
            TokenCount: 토큰 계산 결과
        """
        metadata = processed_file.metadata

        # 이미지 메타데이터에서 크기 추출
        width = metadata.get("width", 0)
        height = metadata.get("height", 0)

        if width == 0 or height == 0:
            return TokenCount(
                text=processed_file.content,
                token_count=0,
                model_name=self.model_name,
                error="이미지 크기 정보를 찾을 수 없습니다.",
            )

        # 모델별 토큰 추정
        if "gpt" in self.model_name.lower():
            token_count = self.image_tokenizer.estimate_gpt4v_tokens(width, height)
        elif "claude" in self.model_name.lower():
            token_count = self.image_tokenizer.estimate_claude_tokens(width, height)
        elif "gemini" in self.model_name.lower():
            token_count = self.image_tokenizer.estimate_gemini_tokens(width, height)
        else:
            token_count = self.image_tokenizer.estimate_gpt4v_tokens(width, height)

        # TokenCount 객체 생성
        return TokenCount(
            text=processed_file.content,
            token_count=token_count,
            model_name=self.model_name,
            encoding_name="image-high",
            metadata={
                "file_name": metadata.get("file_name", ""),
                "file_type": "image",
                "width": width,
                "height": height,
                "total_pixels": width * height,
                "claude_tokens": metadata.get("claude_estimated_tokens", 0),
                "gpt4v_tokens": metadata.get("gpt4v_estimated_tokens", 0),
                "gemini_tokens": metadata.get("gemini_estimated_tokens", 0),
            },
            error=None,
        )

    def count_tokens_from_file(self, file_path: Union[str, Path]) -> TokenCount:
        """
        파일 경로에서 직접 토큰 계산

        파일을 읽고 처리한 후 토큰을 계산합니다.

        Args:
            file_path: 파일 경로

        Returns:
            TokenCount: 토큰 계산 결과
        """
        from api_cost_modules.processors.text_processor import TextFileProcessor
        from api_cost_modules.processors.pdf_processor import PDFFileProcessor
        from api_cost_modules.processors.excel_processor import ExcelFileProcessor
        from api_cost_modules.processors.word_processor import WordFileProcessor
        from api_cost_modules.processors.image_processor import ImageFileProcessor

        file_path = Path(file_path)

        # 확장자에 따라 적절한 프로세서 선택
        suffix = file_path.suffix.lower()

        if suffix in [".txt", ".md", ".py", ".js", ".json"]:
            processor = TextFileProcessor()
        elif suffix == ".pdf":
            processor = PDFFileProcessor()
        elif suffix in [".xlsx", ".xls", ".csv"]:
            processor = ExcelFileProcessor()
        elif suffix in [".docx", ".docm"]:
            processor = WordFileProcessor()
        elif suffix in [".png", ".jpg", ".jpeg", ".gif"]:
            processor = ImageFileProcessor()
        else:
            # 기본값: 텍스트 프로세서 사용
            processor = TextFileProcessor()

        # 파일 처리
        processed_file = processor.process(file_path)

        # 토큰 계산
        return self.count_tokens_from_processed_file(processed_file)

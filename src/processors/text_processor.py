"""
텍스트 파일 프로세서

일반 텍스트 파일 및 코드 파일을 처리하여 내용을 추출합니다.
"""

import chardet
from pathlib import Path
from typing import Optional

from .base import BaseFileProcessor, ProcessedFile


class TextFileProcessor(BaseFileProcessor):
    """
    텍스트 파일 프로세서

    TXT, MD, 코드 파일 등 일반 텍스트 파일을 처리합니다.
    자동으로 인코딩을 감지하여 올바르게 읽어옵니다.
    """

    def __init__(self):
        """텍스트 프로세서 초기화"""
        super().__init__()
        self.supported_extensions = [
            # 일반 텍스트
            ".txt",
            ".md",
            ".markdown",
            ".rst",
            ".log",
            # 코드 파일
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".cs",
            ".go",
            ".rs",
            ".rb",
            ".php",
            ".swift",
            ".kt",
            ".scala",
            # 설정 파일
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".cfg",
            ".conf",
            # 웹
            ".html",
            ".css",
            ".xml",
            ".svg",
        ]

    def detect_encoding(self, file_path: Path) -> str:
        """
        파일의 인코딩을 자동으로 감지

        Args:
            file_path: 인코딩을 감지할 파일 경로

        Returns:
            str: 감지된 인코딩 (예: 'utf-8', 'cp949')
        """
        # 파일의 일부를 읽어서 인코딩 감지
        with open(file_path, "rb") as f:
            raw_data = f.read(10000)  # 처음 10KB만 읽기

        # chardet으로 인코딩 감지
        result = chardet.detect(raw_data)
        encoding = result["encoding"]

        # 인코딩을 감지하지 못한 경우 기본값 사용
        if encoding is None:
            encoding = "utf-8"

        return encoding

    def read_file_content(self, file_path: Path, encoding: Optional[str] = None) -> str:
        """
        파일 내용을 읽어서 문자열로 반환

        Args:
            file_path: 읽을 파일 경로
            encoding: 사용할 인코딩 (None이면 자동 감지)

        Returns:
            str: 파일의 텍스트 내용

        Raises:
            UnicodeDecodeError: 인코딩 오류 발생 시
        """
        # 인코딩이 지정되지 않으면 자동 감지
        if encoding is None:
            encoding = self.detect_encoding(file_path)

        try:
            # 지정된 인코딩으로 파일 읽기
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
            return content

        except UnicodeDecodeError:
            # 인코딩 실패 시 다른 인코딩들 시도
            fallback_encodings = ["utf-8", "cp949", "euc-kr", "latin-1"]

            for fallback_encoding in fallback_encodings:
                if fallback_encoding == encoding:
                    continue  # 이미 시도한 인코딩은 건너뛰기

                try:
                    with open(file_path, "r", encoding=fallback_encoding) as f:
                        content = f.read()
                    return content
                except UnicodeDecodeError:
                    continue

            # 모든 인코딩 실패 시 에러 발생
            raise UnicodeDecodeError(
                encoding,
                b"",
                0,
                1,
                f"파일을 읽을 수 없습니다. 지원하는 인코딩: {fallback_encodings}",
            )

    def process(self, file_path: Path) -> ProcessedFile:
        """
        텍스트 파일을 처리하여 내용 추출

        Args:
            file_path: 처리할 텍스트 파일 경로

        Returns:
            ProcessedFile: 처리된 파일 정보

        Raises:
            FileNotFoundError: 파일이 존재하지 않는 경우
            ValueError: 지원하지 않는 파일 형식인 경우
        """
        try:
            # 파일 검증
            self.validate_file(file_path)

            # 인코딩 감지
            detected_encoding = self.detect_encoding(file_path)

            # 파일 내용 읽기
            content = self.read_file_content(file_path, detected_encoding)

            # 기본 메타데이터 추출
            metadata = self.get_file_metadata(file_path)

            # 텍스트 파일 전용 메타데이터 추가
            metadata.update(
                {
                    "encoding": detected_encoding,
                    "line_count": content.count("\n") + 1,
                    "character_count": len(content),
                    "word_count": len(content.split()),
                }
            )

            return ProcessedFile(
                file_path=file_path,
                file_type="text",
                content=content,
                metadata=metadata,
                error=None,
            )

        except Exception as e:
            # 에러 발생 시 에러 정보와 함께 반환
            return ProcessedFile(
                file_path=file_path,
                file_type="text",
                content="",
                metadata=self.get_file_metadata(file_path)
                if file_path.exists()
                else {},
                error=str(e),
            )

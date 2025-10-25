"""
파일 프로세서 기본 추상 클래스

모든 파일 프로세서가 상속받아야 하는 기본 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ProcessedFile:
    """
    처리된 파일의 정보를 담는 데이터 클래스

    Attributes:
        file_path: 원본 파일 경로
        file_type: 파일 타입 (예: 'pdf', 'excel', 'text')
        content: 추출된 텍스트 내용
        metadata: 파일 메타데이터 (페이지 수, 이미지 크기 등)
        error: 처리 중 발생한 에러 메시지 (있는 경우)
    """

    file_path: Path
    file_type: str
    content: str
    metadata: dict
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """
        파일 처리가 성공했는지 여부를 반환

        Returns:
            bool: 에러가 없으면 True, 있으면 False
        """
        return self.error is None

    @property
    def content_length(self) -> int:
        """
        추출된 내용의 길이를 반환

        Returns:
            int: 텍스트 길이 (문자 수)
        """
        return len(self.content)


class BaseFileProcessor(ABC):
    """
    파일 프로세서 추상 기본 클래스

    모든 파일 타입 프로세서가 상속받아 구현해야 하는 기본 인터페이스입니다.
    """

    def __init__(self):
        """프로세서 초기화"""
        self.supported_extensions: list[str] = []

    @abstractmethod
    def process(self, file_path: Path) -> ProcessedFile:
        """
        파일을 처리하고 내용을 추출하는 메인 메서드

        Args:
            file_path: 처리할 파일의 경로

        Returns:
            ProcessedFile: 처리된 파일 정보

        Raises:
            FileNotFoundError: 파일이 존재하지 않는 경우
            ValueError: 지원하지 않는 파일 형식인 경우
        """
        pass

    def is_supported(self, file_path: Path) -> bool:
        """
        파일 확장자가 지원되는지 확인

        Args:
            file_path: 확인할 파일 경로

        Returns:
            bool: 지원되는 확장자면 True, 아니면 False
        """
        suffix = file_path.suffix.lower()
        return suffix in self.supported_extensions

    def validate_file(self, file_path: Path) -> None:
        """
        파일이 존재하고 처리 가능한지 검증

        Args:
            file_path: 검증할 파일 경로

        Raises:
            FileNotFoundError: 파일이 존재하지 않는 경우
            ValueError: 지원하지 않는 파일 형식인 경우
            PermissionError: 파일 접근 권한이 없는 경우
        """
        # 파일 존재 여부 확인
        if not file_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        # 파일인지 확인 (디렉토리가 아닌지)
        if not file_path.is_file():
            raise ValueError(f"디렉토리입니다. 파일 경로를 지정해주세요: {file_path}")

        # 지원되는 확장자인지 확인
        if not self.is_supported(file_path):
            raise ValueError(
                f"지원하지 않는 파일 형식입니다: {file_path.suffix}. "
                f"지원 형식: {', '.join(self.supported_extensions)}"
            )

        # 읽기 권한 확인
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"파일 읽기 권한이 없습니다: {file_path}")

    def get_file_metadata(self, file_path: Path) -> dict:
        """
        파일의 기본 메타데이터를 추출

        Args:
            file_path: 메타데이터를 추출할 파일 경로

        Returns:
            dict: 파일 메타데이터 (크기, 수정 시간 등)
        """
        stat = file_path.stat()
        return {
            "file_name": file_path.name,
            "file_size": stat.st_size,  # 바이트 단위
            "file_size_mb": round(stat.st_size / (1024 * 1024), 2),  # MB 단위
            "modified_time": stat.st_mtime,
            "extension": file_path.suffix.lower(),
        }


# os 모듈 임포트 추가 (validate_file에서 사용)
import os

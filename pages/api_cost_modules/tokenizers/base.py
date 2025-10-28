"""
토크나이저 기본 추상 클래스

모든 토크나이저가 상속받아야 하는 기본 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class TokenCount:
    """
    토큰 계산 결과를 담는 데이터 클래스

    Attributes:
        text: 토큰화된 원본 텍스트
        token_count: 계산된 토큰 수
        model_name: 사용된 모델 이름 (예: 'gpt-4', 'claude-3')
        encoding_name: 사용된 인코딩 이름 (예: 'cl100k_base')
        metadata: 추가 메타데이터
        error: 에러 메시지 (있는 경우)
    """

    text: str
    token_count: int
    model_name: str
    encoding_name: Optional[str] = None
    metadata: dict = None
    error: Optional[str] = None

    def __post_init__(self):
        """초기화 후 기본값 설정"""
        if self.metadata is None:
            self.metadata = {}

    @property
    def is_success(self) -> bool:
        """
        토큰 계산이 성공했는지 여부

        Returns:
            bool: 에러가 없으면 True, 있으면 False
        """
        return self.error is None

    @property
    def chars_per_token(self) -> float:
        """
        토큰당 평균 문자 수

        Returns:
            float: 문자 수 / 토큰 수
        """
        if self.token_count == 0:
            return 0.0
        return len(self.text) / self.token_count


class BaseTokenizer(ABC):
    """
    토크나이저 추상 기본 클래스

    모든 토크나이저가 상속받아 구현해야 하는 기본 인터페이스입니다.
    """

    def __init__(self, model_name: str):
        """
        토크나이저 초기화

        Args:
            model_name: 토큰 계산에 사용할 모델 이름
        """
        self.model_name = model_name

    @abstractmethod
    def count_tokens(self, text: str) -> TokenCount:
        """
        텍스트의 토큰 수를 계산하는 메인 메서드

        Args:
            text: 토큰을 계산할 텍스트

        Returns:
            TokenCount: 토큰 계산 결과

        Raises:
            ValueError: 빈 텍스트인 경우
        """
        pass

    def validate_text(self, text: str) -> None:
        """
        텍스트가 유효한지 검증

        Args:
            text: 검증할 텍스트

        Raises:
            ValueError: 텍스트가 None이거나 빈 문자열인 경우
        """
        if text is None:
            raise ValueError("텍스트가 None입니다.")

        if not isinstance(text, str):
            raise ValueError(f"텍스트는 문자열이어야 합니다. 현재 타입: {type(text)}")

    def estimate_tokens_from_chars(self, text: str, chars_per_token: float = 4.0) -> int:
        """
        문자 수 기반으로 토큰 수를 추정

        영어는 평균 4자당 1토큰, 한글은 평균 2자당 1토큰 정도입니다.

        Args:
            text: 토큰을 추정할 텍스트
            chars_per_token: 토큰당 평균 문자 수 (기본값: 4.0)

        Returns:
            int: 추정된 토큰 수
        """
        if not text:
            return 0

        # 문자 수 기반 추정
        char_count = len(text)
        estimated_tokens = int(char_count / chars_per_token)

        # 최소 1토큰은 반환
        return max(1, estimated_tokens)

    def count_tokens_batch(self, texts: list[str]) -> list[TokenCount]:
        """
        여러 텍스트의 토큰을 일괄 계산

        Args:
            texts: 토큰을 계산할 텍스트 리스트

        Returns:
            list[TokenCount]: 각 텍스트의 토큰 계산 결과 리스트
        """
        results = []
        for text in texts:
            try:
                result = self.count_tokens(text)
                results.append(result)
            except Exception as e:
                # 에러 발생 시에도 결과 객체 생성
                results.append(
                    TokenCount(
                        text=text,
                        token_count=0,
                        model_name=self.model_name,
                        error=str(e),
                    )
                )
        return results

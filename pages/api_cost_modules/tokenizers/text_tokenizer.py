"""
텍스트 토크나이저

tiktoken을 사용하여 정확한 토큰 수를 계산합니다.
"""

from typing import Optional

import tiktoken

from .base import BaseTokenizer, TokenCount


# 모델별 인코딩 매핑
MODEL_TO_ENCODING = {
    # OpenAI GPT-4 계열
    "gpt-4": "cl100k_base",
    "gpt-4o": "o200k_base",
    "gpt-4o-mini": "o200k_base",
    "gpt-4-turbo": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "o1-preview": "o200k_base",
    "o1-mini": "o200k_base",
    # Claude (대략적, OpenAI와 유사)
    "claude-3-opus": "cl100k_base",
    "claude-3.5-sonnet": "cl100k_base",
    "claude-3-haiku": "cl100k_base",
    # Gemini (대략적)
    "gemini-1.5-pro": "cl100k_base",
    "gemini-1.5-flash": "cl100k_base",
    "gemini-1.0-pro": "cl100k_base",
}


class TextTokenizer(BaseTokenizer):
    """
    텍스트 토크나이저

    tiktoken 라이브러리를 사용하여 정확한 토큰 수를 계산합니다.
    """

    def __init__(self, model_name: str = "gpt-4", encoding_name: Optional[str] = None):
        """
        텍스트 토크나이저 초기화

        Args:
            model_name: 모델 이름 (기본값: 'gpt-4')
            encoding_name: 인코딩 이름 (None이면 model_name에서 자동 선택)
        """
        super().__init__(model_name)

        # 인코딩 이름 결정
        if encoding_name:
            self.encoding_name = encoding_name
        else:
            self.encoding_name = MODEL_TO_ENCODING.get(model_name, "cl100k_base")

        # tiktoken 인코더 로드
        try:
            self.encoder = tiktoken.get_encoding(self.encoding_name)
        except Exception as e:
            # 인코딩을 찾지 못한 경우 기본값 사용
            print(f"⚠️ 경고: {self.encoding_name} 인코딩을 찾을 수 없습니다. cl100k_base 사용")
            self.encoding_name = "cl100k_base"
            self.encoder = tiktoken.get_encoding(self.encoding_name)

    def count_tokens(self, text: str) -> TokenCount:
        """
        텍스트의 토큰 수를 정확하게 계산

        Args:
            text: 토큰을 계산할 텍스트

        Returns:
            TokenCount: 토큰 계산 결과
        """
        try:
            # 텍스트 검증
            self.validate_text(text)

            # tiktoken으로 토큰 계산
            tokens = self.encoder.encode(text)
            token_count = len(tokens)

            # 메타데이터 생성
            metadata = {
                "character_count": len(text),
                "word_count": len(text.split()),
                "chars_per_token": len(text) / token_count if token_count > 0 else 0,
            }

            return TokenCount(
                text=text,
                token_count=token_count,
                model_name=self.model_name,
                encoding_name=self.encoding_name,
                metadata=metadata,
                error=None,
            )

        except Exception as e:
            # 에러 발생 시
            return TokenCount(
                text=text,
                token_count=0,
                model_name=self.model_name,
                encoding_name=self.encoding_name,
                error=str(e),
            )

    def decode_tokens(self, tokens: list[int]) -> str:
        """
        토큰 ID 리스트를 텍스트로 디코딩

        Args:
            tokens: 토큰 ID 리스트

        Returns:
            str: 디코딩된 텍스트
        """
        return self.encoder.decode(tokens)

    def encode_text(self, text: str) -> list[int]:
        """
        텍스트를 토큰 ID 리스트로 인코딩

        Args:
            text: 인코딩할 텍스트

        Returns:
            list[int]: 토큰 ID 리스트
        """
        return self.encoder.encode(text)

    def count_tokens_for_messages(self, messages: list[dict]) -> TokenCount:
        """
        채팅 메시지 형식의 토큰 수 계산

        OpenAI API 형식의 메시지 리스트에서 토큰을 계산합니다.

        Args:
            messages: [{"role": "user", "content": "..."}] 형식의 메시지 리스트

        Returns:
            TokenCount: 토큰 계산 결과
        """
        try:
            # 메시지를 하나의 텍스트로 합치기
            combined_text = ""
            for message in messages:
                role = message.get("role", "")
                content = message.get("content", "")
                combined_text += f"{role}: {content}\n"

            # 기본 토큰 계산
            result = self.count_tokens(combined_text)

            # 메시지 형식에 따른 추가 토큰 (OpenAI API 기준)
            # 각 메시지마다 약 4토큰 추가 (role, content 구분자 등)
            message_overhead = len(messages) * 4
            result.token_count += message_overhead

            result.metadata["message_count"] = len(messages)
            result.metadata["overhead_tokens"] = message_overhead

            return result

        except Exception as e:
            return TokenCount(
                text="",
                token_count=0,
                model_name=self.model_name,
                encoding_name=self.encoding_name,
                error=str(e),
            )

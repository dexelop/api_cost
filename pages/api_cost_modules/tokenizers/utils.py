"""
토크나이저 유틸리티 함수들

토큰 계산 관련 편의 함수들을 제공합니다.
"""

from pathlib import Path
from typing import Union

from .file_tokenizer import FileTokenizer
from .text_tokenizer import TextTokenizer


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    텍스트의 토큰 수를 간단하게 계산하는 편의 함수

    Args:
        text: 토큰을 계산할 텍스트
        model: 모델 이름 (기본값: 'gpt-4')

    Returns:
        int: 토큰 수

    Examples:
        >>> count_tokens("Hello, world!")
        4
        >>> count_tokens("안녕하세요", model="claude-3-opus")
        6
    """
    tokenizer = TextTokenizer(model_name=model)
    result = tokenizer.count_tokens(text)
    return result.token_count


def count_tokens_from_file(file_path: Union[str, Path], model: str = "gpt-4") -> int:
    """
    파일의 토큰 수를 간단하게 계산하는 편의 함수

    Args:
        file_path: 파일 경로
        model: 모델 이름 (기본값: 'gpt-4')

    Returns:
        int: 토큰 수

    Examples:
        >>> count_tokens_from_file("README.md")
        1024
        >>> count_tokens_from_file("image.png", model="gpt-4o")
        255
    """
    tokenizer = FileTokenizer(model_name=model)
    result = tokenizer.count_tokens_from_file(file_path)
    return result.token_count


def estimate_cost(
    token_count: int,
    input_price_per_1k: float,
    output_tokens: int = 0,
    output_price_per_1k: float = 0.0,
) -> float:
    """
    토큰 수를 기반으로 API 비용 추정

    Args:
        token_count: 입력 토큰 수
        input_price_per_1k: 1000토큰당 입력 비용 (USD)
        output_tokens: 출력 토큰 수 (기본값: 0)
        output_price_per_1k: 1000토큰당 출력 비용 (USD, 기본값: 0.0)

    Returns:
        float: 예상 비용 (USD)

    Examples:
        >>> estimate_cost(1000, 0.03)  # GPT-4 입력 1000토큰
        0.03
        >>> estimate_cost(1000, 0.03, 500, 0.06)  # 입력 1000 + 출력 500
        0.06
    """
    # 입력 비용 계산
    input_cost = (token_count / 1000) * input_price_per_1k

    # 출력 비용 계산
    output_cost = (output_tokens / 1000) * output_price_per_1k if output_tokens > 0 else 0.0

    return input_cost + output_cost


def split_text_by_tokens(
    text: str, max_tokens: int, model: str = "gpt-4", overlap: int = 0
) -> list[str]:
    """
    텍스트를 최대 토큰 수에 맞춰 분할

    긴 텍스트를 여러 청크로 나누어 API 요청 제한에 맞춥니다.

    Args:
        text: 분할할 텍스트
        max_tokens: 청크당 최대 토큰 수
        model: 모델 이름 (기본값: 'gpt-4')
        overlap: 청크 간 겹치는 토큰 수 (기본값: 0)

    Returns:
        list[str]: 분할된 텍스트 청크 리스트

    Examples:
        >>> text = "A" * 10000
        >>> chunks = split_text_by_tokens(text, max_tokens=1000)
        >>> len(chunks)
        10
    """
    tokenizer = TextTokenizer(model_name=model)

    # 전체 텍스트의 토큰 수 확인
    total_result = tokenizer.count_tokens(text)
    if total_result.token_count <= max_tokens:
        # 분할 필요 없음
        return [text]

    # 문장 단위로 분할 (간단한 구현)
    sentences = text.split(". ")
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for sentence in sentences:
        sentence_result = tokenizer.count_tokens(sentence)
        sentence_tokens = sentence_result.token_count

        # 현재 청크에 추가했을 때 최대값을 초과하는지 확인
        if current_tokens + sentence_tokens > max_tokens:
            if current_chunk:
                # 현재 청크 저장
                chunks.append(current_chunk.strip())

                # 오버랩이 있으면 마지막 부분 유지
                if overlap > 0:
                    # 간단한 구현: 마지막 문장 유지
                    current_chunk = sentence + ". "
                    current_tokens = sentence_tokens
                else:
                    current_chunk = sentence + ". "
                    current_tokens = sentence_tokens
            else:
                # 단일 문장이 너무 긴 경우
                chunks.append(sentence)
                current_chunk = ""
                current_tokens = 0
        else:
            current_chunk += sentence + ". "
            current_tokens += sentence_tokens

    # 마지막 청크 추가
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def get_model_context_window(model: str) -> int:
    """
    모델의 최대 컨텍스트 윈도우 크기 반환

    Args:
        model: 모델 이름

    Returns:
        int: 최대 토큰 수

    Examples:
        >>> get_model_context_window("gpt-4")
        8192
        >>> get_model_context_window("claude-3-opus")
        200000
    """
    context_windows = {
        # OpenAI
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-turbo": 128000,
        "gpt-4o": 128000,
        "gpt-4o-mini": 128000,
        "gpt-3.5-turbo": 16385,
        "o1-preview": 128000,
        "o1-mini": 128000,
        # Claude
        "claude-3-opus": 200000,
        "claude-3.5-sonnet": 200000,
        "claude-3-haiku": 200000,
        # Gemini
        "gemini-1.5-pro": 2000000,
        "gemini-1.5-flash": 1000000,
        "gemini-1.0-pro": 32000,
    }

    return context_windows.get(model, 4096)  # 기본값: 4096

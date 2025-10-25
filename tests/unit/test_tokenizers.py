"""
토크나이저 모듈에 대한 유닛 테스트

각 토크나이저의 기능이 올바르게 작동하는지 검증합니다.
"""

import pytest
from PIL import Image

from src.tokenizers.text_tokenizer import TextTokenizer
from src.tokenizers.image_tokenizer import ImageTokenizer
from src.tokenizers.file_tokenizer import FileTokenizer
from src.tokenizers.utils import (
    count_tokens,
    estimate_cost,
    get_model_context_window,
)


class TestTextTokenizer:
    """TextTokenizer에 대한 테스트"""

    def test_count_tokens_english(self):
        """영어 텍스트 토큰 계산"""
        tokenizer = TextTokenizer(model_name="gpt-4")
        text = "Hello, world!"

        result = tokenizer.count_tokens(text)

        assert result.is_success is True
        assert result.token_count > 0
        assert result.model_name == "gpt-4"
        assert result.encoding_name == "cl100k_base"

    def test_count_tokens_korean(self):
        """한글 텍스트 토큰 계산"""
        tokenizer = TextTokenizer(model_name="gpt-4")
        text = "안녕하세요, LLM API Cost Calculator입니다."

        result = tokenizer.count_tokens(text)

        assert result.is_success is True
        assert result.token_count > 0
        assert "character_count" in result.metadata
        assert "word_count" in result.metadata

    def test_count_tokens_empty_text(self):
        """빈 텍스트 처리"""
        tokenizer = TextTokenizer(model_name="gpt-4")

        result = tokenizer.count_tokens("")

        # 빈 문자열도 처리 가능해야 함
        assert result.token_count == 0

    def test_different_models(self):
        """다양한 모델 지원 확인"""
        models = ["gpt-4", "gpt-4o", "claude-3-opus", "gemini-1.5-pro"]

        for model in models:
            tokenizer = TextTokenizer(model_name=model)
            result = tokenizer.count_tokens("Test text")
            assert result.is_success is True
            assert result.model_name == model

    def test_encode_decode(self):
        """인코딩/디코딩 기능 테스트"""
        tokenizer = TextTokenizer(model_name="gpt-4")
        text = "Hello, world!"

        # 인코딩
        tokens = tokenizer.encode_text(text)
        assert isinstance(tokens, list)
        assert len(tokens) > 0

        # 디코딩
        decoded_text = tokenizer.decode_tokens(tokens)
        assert decoded_text == text

    def test_count_tokens_for_messages(self):
        """채팅 메시지 형식 토큰 계산"""
        tokenizer = TextTokenizer(model_name="gpt-4")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        result = tokenizer.count_tokens_for_messages(messages)

        assert result.is_success is True
        assert result.token_count > 0
        assert result.metadata["message_count"] == 3
        assert "overhead_tokens" in result.metadata


class TestImageTokenizer:
    """ImageTokenizer에 대한 테스트"""

    def test_estimate_claude_tokens_small(self):
        """Claude 작은 이미지 토큰 추정"""
        tokenizer = ImageTokenizer(model_name="claude-3-opus")

        tokens = tokenizer.estimate_claude_tokens(300, 300)

        assert tokens == 1600  # 작은 이미지

    def test_estimate_claude_tokens_large(self):
        """Claude 큰 이미지 토큰 추정"""
        tokenizer = ImageTokenizer(model_name="claude-3-opus")

        tokens = tokenizer.estimate_claude_tokens(1920, 1080)

        assert tokens == 6000  # 큰 이미지

    def test_estimate_gpt4v_tokens(self):
        """GPT-4V 토큰 추정"""
        tokenizer = ImageTokenizer(model_name="gpt-4o")

        # 512x512 = 1타일
        tokens_1_tile = tokenizer.estimate_gpt4v_tokens(512, 512)
        assert tokens_1_tile == 85 + 170  # 베이스 + 1타일

        # 1024x1024 = 4타일 (2x2)
        tokens_4_tiles = tokenizer.estimate_gpt4v_tokens(1024, 1024)
        assert tokens_4_tiles == 85 + (4 * 170)  # 베이스 + 4타일

    def test_count_tokens_from_image(self, tmp_path):
        """이미지 파일로부터 토큰 계산"""
        tokenizer = ImageTokenizer(model_name="gpt-4o")

        # 테스트 이미지 생성
        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (800, 600), color="blue")
        img.save(img_path)

        # 토큰 계산
        result = tokenizer.count_tokens(img_path, detail="high")

        assert result.is_success is True
        assert result.token_count > 0
        assert result.metadata["width"] == 800
        assert result.metadata["height"] == 600
        assert "claude_tokens" in result.metadata
        assert "gpt4v_tokens" in result.metadata


class TestFileTokenizer:
    """FileTokenizer에 대한 테스트"""

    def test_count_tokens_text_file(self, tmp_path):
        """텍스트 파일 토큰 계산"""
        tokenizer = FileTokenizer(model_name="gpt-4")

        # 테스트 파일 생성
        text_file = tmp_path / "test.txt"
        text_file.write_text("Hello, this is a test file!")

        # 토큰 계산
        result = tokenizer.count_tokens_from_file(text_file)

        assert result.is_success is True
        assert result.token_count > 0
        assert "file_name" in result.metadata

    def test_count_tokens_image_file(self, tmp_path):
        """이미지 파일 토큰 계산"""
        tokenizer = FileTokenizer(model_name="gpt-4o")

        # 테스트 이미지 생성
        img_file = tmp_path / "test.png"
        img = Image.new("RGB", (100, 100))
        img.save(img_file)

        # 토큰 계산
        result = tokenizer.count_tokens_from_file(img_file)

        assert result.is_success is True
        assert result.token_count > 0


class TestTokenizerUtils:
    """Tokenizer 유틸리티 함수 테스트"""

    def test_count_tokens_util(self):
        """count_tokens 편의 함수 테스트"""
        token_count = count_tokens("Hello, world!", model="gpt-4")

        assert isinstance(token_count, int)
        assert token_count > 0

    def test_estimate_cost(self):
        """비용 추정 함수 테스트"""
        # 입력만
        cost = estimate_cost(1000, 0.03)
        assert cost == 0.03

        # 입력 + 출력
        total_cost = estimate_cost(1000, 0.03, 500, 0.06)
        assert total_cost == 0.06  # 0.03 + 0.03

    def test_get_model_context_window(self):
        """모델 컨텍스트 윈도우 크기 확인"""
        # OpenAI
        assert get_model_context_window("gpt-4") == 8192
        assert get_model_context_window("gpt-4o") == 128000

        # Claude
        assert get_model_context_window("claude-3-opus") == 200000

        # Gemini
        assert get_model_context_window("gemini-1.5-pro") == 2000000

        # 알 수 없는 모델은 기본값 반환
        assert get_model_context_window("unknown-model") == 4096


class TestTokenCountDataclass:
    """TokenCount 데이터 클래스 테스트"""

    def test_is_success(self):
        """성공 여부 속성 테스트"""
        from src.tokenizers.base import TokenCount

        # 성공 케이스
        success_result = TokenCount(
            text="test", token_count=10, model_name="gpt-4", error=None
        )
        assert success_result.is_success is True

        # 실패 케이스
        fail_result = TokenCount(
            text="test", token_count=0, model_name="gpt-4", error="Some error"
        )
        assert fail_result.is_success is False

    def test_chars_per_token(self):
        """토큰당 문자 수 계산 테스트"""
        from src.tokenizers.base import TokenCount

        result = TokenCount(text="Hello, world!", token_count=4, model_name="gpt-4")

        chars_per_token = result.chars_per_token
        assert chars_per_token > 0
        assert chars_per_token == len("Hello, world!") / 4

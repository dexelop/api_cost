"""
이미지 토크나이저

이미지 해상도를 기반으로 LLM Vision API의 토큰 수를 추정합니다.
"""

from pathlib import Path
from typing import Union

from PIL import Image

from .base import BaseTokenizer, TokenCount


class ImageTokenizer(BaseTokenizer):
    """
    이미지 토크나이저

    이미지의 해상도를 분석하여 Claude, GPT-4V, Gemini의 토큰 수를 추정합니다.
    """

    def __init__(self, model_name: str = "gpt-4o"):
        """
        이미지 토크나이저 초기화

        Args:
            model_name: 모델 이름 (gpt-4o, claude-3, gemini-1.5-pro 등)
        """
        super().__init__(model_name)

    def estimate_claude_tokens(self, width: int, height: int) -> int:
        """
        Claude의 이미지 토큰 수 추정

        Claude는 이미지 크기에 따라 대략적인 토큰을 사용합니다.

        Args:
            width: 이미지 가로 픽셀
            height: 이미지 세로 픽셀

        Returns:
            int: 추정된 토큰 수
        """
        total_pixels = width * height

        # Claude의 이미지 토큰 추정
        if total_pixels < 400 * 400:  # 작은 이미지 (160K 픽셀 미만)
            return 1600
        elif total_pixels < 800 * 800:  # 중간 이미지 (640K 픽셀 미만)
            return 3000
        else:  # 큰 이미지
            return 6000

    def estimate_gpt4v_tokens(self, width: int, height: int) -> int:
        """
        GPT-4V의 이미지 토큰 수 추정

        GPT-4V는 타일 기반으로 토큰을 계산합니다.
        - 저해상도: 85 토큰
        - 고해상도: 85 + (타일 수 × 170) 토큰
        - 타일 크기: 512×512

        Args:
            width: 이미지 가로 픽셀
            height: 이미지 세로 픽셀

        Returns:
            int: 추정된 토큰 수
        """
        # 기본 토큰 (저해상도 버전)
        base_tokens = 85

        # 고해상도 타일 계산
        # 이미지를 512×512 타일로 나눔 (올림)
        tiles_horizontal = (width + 511) // 512
        tiles_vertical = (height + 511) // 512
        total_tiles = tiles_horizontal * tiles_vertical

        # 각 타일당 170토큰
        tile_tokens = total_tiles * 170

        return base_tokens + tile_tokens

    def estimate_gemini_tokens(self, width: int, height: int) -> int:
        """
        Gemini의 이미지 토큰 수 추정

        Gemini는 Claude와 유사한 방식으로 토큰을 계산합니다.

        Args:
            width: 이미지 가로 픽셀
            height: 이미지 세로 픽셀

        Returns:
            int: 추정된 토큰 수
        """
        # Claude와 유사한 추정 방식 사용
        return self.estimate_claude_tokens(width, height)

    def get_image_dimensions(self, image_input: Union[str, Path, Image.Image]) -> tuple[int, int]:
        """
        이미지의 가로/세로 픽셀 추출

        Args:
            image_input: 이미지 파일 경로 또는 PIL Image 객체

        Returns:
            tuple: (width, height) 픽셀 크기
        """
        if isinstance(image_input, (str, Path)):
            # 파일 경로인 경우
            with Image.open(image_input) as img:
                return img.size
        elif isinstance(image_input, Image.Image):
            # PIL Image 객체인 경우
            return image_input.size
        else:
            raise ValueError(
                f"지원하지 않는 이미지 타입입니다: {type(image_input)}. "
                "파일 경로(str/Path) 또는 PIL.Image 객체를 사용하세요."
            )

    def count_tokens(
        self, image_input: Union[str, Path, Image.Image], detail: str = "high"
    ) -> TokenCount:
        """
        이미지의 토큰 수 추정

        Args:
            image_input: 이미지 파일 경로 또는 PIL Image 객체
            detail: 디테일 레벨 ('low' 또는 'high', GPT-4V용)

        Returns:
            TokenCount: 토큰 계산 결과
        """
        try:
            # 이미지 크기 추출
            width, height = self.get_image_dimensions(image_input)

            # 모델별 토큰 추정
            if "gpt" in self.model_name.lower():
                if detail == "low":
                    token_count = 85  # 저해상도
                else:
                    token_count = self.estimate_gpt4v_tokens(width, height)
            elif "claude" in self.model_name.lower():
                token_count = self.estimate_claude_tokens(width, height)
            elif "gemini" in self.model_name.lower():
                token_count = self.estimate_gemini_tokens(width, height)
            else:
                # 기본값: GPT-4V 방식 사용
                token_count = self.estimate_gpt4v_tokens(width, height)

            # 메타데이터 생성
            metadata = {
                "width": width,
                "height": height,
                "total_pixels": width * height,
                "detail": detail,
                # 다른 모델들의 추정값도 함께 제공
                "claude_tokens": self.estimate_claude_tokens(width, height),
                "gpt4v_tokens": self.estimate_gpt4v_tokens(width, height),
                "gemini_tokens": self.estimate_gemini_tokens(width, height),
            }

            # 이미지 경로를 텍스트로 변환
            if isinstance(image_input, (str, Path)):
                text = f"Image: {image_input}"
            else:
                text = f"Image: {width}x{height} pixels"

            return TokenCount(
                text=text,
                token_count=token_count,
                model_name=self.model_name,
                encoding_name=f"image-{detail}",
                metadata=metadata,
                error=None,
            )

        except Exception as e:
            return TokenCount(
                text=str(image_input),
                token_count=0,
                model_name=self.model_name,
                error=str(e),
            )

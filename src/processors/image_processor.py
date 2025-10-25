"""
이미지 파일 프로세서

이미지 파일의 메타데이터를 추출하고 토큰 수를 추정합니다.
"""

from pathlib import Path

from PIL import Image

from .base import BaseFileProcessor, ProcessedFile


class ImageFileProcessor(BaseFileProcessor):
    """
    이미지 파일 프로세서

    Pillow를 사용하여 이미지 메타데이터를 추출하고,
    Claude/GPT-4V 기준으로 토큰 수를 추정합니다.
    """

    def __init__(self):
        """이미지 프로세서 초기화"""
        super().__init__()
        self.supported_extensions = [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".tiff",
            ".webp",
        ]

    def estimate_image_tokens(self, width: int, height: int) -> dict:
        """
        이미지 해상도 기반 토큰 수 추정

        Claude와 GPT-4V의 이미지 토큰 계산 방식을 참고하여 추정합니다.

        Args:
            width: 이미지 가로 픽셀
            height: 이미지 세로 픽셀

        Returns:
            dict: 모델별 예상 토큰 수
        """
        # 총 픽셀 수
        total_pixels = width * height

        # Claude의 이미지 토큰 계산 (대략적)
        # 이미지는 대략 1600 토큰 정도 사용 (작은 이미지)
        # 큰 이미지는 최대 4000-6000 토큰까지 사용 가능
        if total_pixels < 400 * 400:  # 작은 이미지
            claude_tokens = 1600
        elif total_pixels < 800 * 800:  # 중간 이미지
            claude_tokens = 3000
        else:  # 큰 이미지
            claude_tokens = 6000

        # GPT-4V의 이미지 토큰 계산 (더 정밀)
        # 타일 기반 계산: 512x512 타일당 약 170토큰
        # 베이스 토큰: 85토큰
        tiles_horizontal = (width + 511) // 512  # 올림 계산
        tiles_vertical = (height + 511) // 512
        total_tiles = tiles_horizontal * tiles_vertical
        gpt4v_tokens = 85 + (total_tiles * 170)

        return {
            "claude_estimated_tokens": claude_tokens,
            "gpt4v_estimated_tokens": gpt4v_tokens,
            "gemini_estimated_tokens": claude_tokens,  # Claude와 유사하게 추정
        }

    def get_image_metadata(self, image: Image.Image, file_path: Path) -> dict:
        """
        이미지 파일의 메타데이터 추출

        Args:
            image: PIL Image 객체
            file_path: 이미지 파일 경로

        Returns:
            dict: 이미지 메타데이터
        """
        # 기본 파일 메타데이터
        metadata = self.get_file_metadata(file_path)

        # 이미지 전용 메타데이터 추가
        width, height = image.size
        image_metadata = {
            "width": width,
            "height": height,
            "format": image.format,
            "mode": image.mode,  # RGB, RGBA, L 등
            "total_pixels": width * height,
        }

        # 토큰 수 추정
        token_estimates = self.estimate_image_tokens(width, height)
        image_metadata.update(token_estimates)

        # EXIF 데이터 추출 (있는 경우)
        try:
            exif_data = image._getexif()
            if exif_data:
                image_metadata["has_exif"] = True
                # 주요 EXIF 정보만 추출 (너무 많으면 생략)
                image_metadata["exif_tags_count"] = len(exif_data)
        except Exception:
            image_metadata["has_exif"] = False

        metadata.update(image_metadata)
        return metadata

    def generate_image_description(self, image: Image.Image, file_path: Path) -> str:
        """
        이미지에 대한 간단한 설명 텍스트 생성

        실제 이미지 내용을 분석하지 않고, 메타데이터 기반 설명을 생성합니다.

        Args:
            image: PIL Image 객체
            file_path: 이미지 파일 경로

        Returns:
            str: 이미지 설명 텍스트
        """
        width, height = image.size
        description = [
            f"Image File: {file_path.name}",
            f"Format: {image.format}",
            f"Dimensions: {width} x {height} pixels",
            f"Color Mode: {image.mode}",
            f"Total Pixels: {width * height:,}",
        ]

        # 토큰 추정 정보
        token_estimates = self.estimate_image_tokens(width, height)
        description.append("\nEstimated Tokens for LLM Vision APIs:")
        description.append(f"  - Claude: ~{token_estimates['claude_estimated_tokens']} tokens")
        description.append(f"  - GPT-4V: ~{token_estimates['gpt4v_estimated_tokens']} tokens")
        description.append(f"  - Gemini: ~{token_estimates['gemini_estimated_tokens']} tokens")

        return "\n".join(description)

    def process(self, file_path: Path) -> ProcessedFile:
        """
        이미지 파일을 처리하여 메타데이터 추출

        Args:
            file_path: 처리할 이미지 파일 경로

        Returns:
            ProcessedFile: 처리된 파일 정보
        """
        try:
            # 파일 검증
            self.validate_file(file_path)

            # 이미지 열기
            with Image.open(file_path) as image:
                # 메타데이터 추출
                metadata = self.get_image_metadata(image, file_path)

                # 이미지 설명 생성
                content = self.generate_image_description(image, file_path)

            return ProcessedFile(
                file_path=file_path,
                file_type="image",
                content=content,
                metadata=metadata,
                error=None,
            )

        except Exception as e:
            # 에러 발생 시 에러 정보와 함께 반환
            return ProcessedFile(
                file_path=file_path,
                file_type="image",
                content="",
                metadata=self.get_file_metadata(file_path)
                if file_path.exists()
                else {},
                error=str(e),
            )

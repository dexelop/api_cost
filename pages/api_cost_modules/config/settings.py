"""
애플리케이션 설정 관리 모듈

환경 변수를 읽어서 전역 설정을 제공합니다.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent.parent.absolute()


class Settings:
    """
    애플리케이션 전역 설정 클래스

    환경 변수를 읽어서 타입 안전한 설정값을 제공합니다.
    """

    # ======================
    # API Keys
    # ======================
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")

    # ======================
    # 애플리케이션 설정
    # ======================
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ======================
    # 가격 업데이트 설정
    # ======================
    ENABLE_AUTO_PRICE_UPDATE: bool = (
        os.getenv("ENABLE_AUTO_PRICE_UPDATE", "True").lower() == "true"
    )
    PRICE_UPDATE_INTERVAL_HOURS: int = int(os.getenv("PRICE_UPDATE_INTERVAL_HOURS", "24"))

    # ======================
    # 파일 업로드 설정
    # ======================
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    MAX_FILES_COUNT: int = int(os.getenv("MAX_FILES_COUNT", "10"))

    # 바이트로 변환
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024

    # ======================
    # 캐시 설정
    # ======================
    CACHE_DIR: Path = ROOT_DIR / os.getenv("CACHE_DIR", "data/cache")
    PRICE_CACHE_FILE: Path = ROOT_DIR / os.getenv(
        "PRICE_CACHE_FILE", "data/price_cache.json"
    )

    # ======================
    # 디렉토리 설정
    # ======================
    CONFIG_DIR: Path = ROOT_DIR / "config"
    DATA_DIR: Path = ROOT_DIR / "data"
    SRC_DIR: Path = ROOT_DIR / "src"

    # ======================
    # 모델 설정 파일
    # ======================
    MODELS_CONFIG_FILE: Path = CONFIG_DIR / "models.yaml"

    @classmethod
    def ensure_directories(cls) -> None:
        """
        필수 디렉토리들이 존재하는지 확인하고 없으면 생성합니다.

        Returns:
            None
        """
        directories = [
            cls.CACHE_DIR,
            cls.DATA_DIR,
            cls.CONFIG_DIR,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls) -> bool:
        """
        설정값들이 유효한지 검증합니다.

        Returns:
            bool: 모든 설정이 유효하면 True, 아니면 False
        """
        errors = []

        # 파일 크기 검증
        if cls.MAX_FILE_SIZE_MB <= 0:
            errors.append("MAX_FILE_SIZE_MB must be greater than 0")

        # 파일 개수 검증
        if cls.MAX_FILES_COUNT <= 0:
            errors.append("MAX_FILES_COUNT must be greater than 0")

        # 업데이트 주기 검증
        if cls.PRICE_UPDATE_INTERVAL_HOURS <= 0:
            errors.append("PRICE_UPDATE_INTERVAL_HOURS must be greater than 0")

        if errors:
            for error in errors:
                print(f"❌ Settings validation error: {error}")
            return False

        return True


# 전역 설정 인스턴스
settings = Settings()

# 애플리케이션 시작 시 디렉토리 생성
settings.ensure_directories()

# 설정 검증
if not settings.validate():
    raise ValueError("Invalid settings configuration")

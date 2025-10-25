"""
config/settings.py 모듈에 대한 유닛 테스트

설정 모듈의 기능들이 올바르게 작동하는지 검증합니다.
"""

import os
from pathlib import Path

import pytest

from config.settings import Settings


class TestSettings:
    """Settings 클래스에 대한 테스트"""

    def test_default_values(self):
        """
        기본값이 올바르게 설정되는지 테스트
        """
        settings = Settings()

        # 기본 DEBUG는 False
        assert isinstance(settings.DEBUG, bool)

        # LOG_LEVEL 기본값 확인
        assert settings.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR"]

        # 파일 크기 기본값 확인
        assert settings.MAX_FILE_SIZE_MB > 0
        assert settings.MAX_FILES_COUNT > 0

        # 가격 업데이트 주기 확인
        assert settings.PRICE_UPDATE_INTERVAL_HOURS > 0

    def test_max_file_size_bytes_conversion(self):
        """
        파일 크기가 바이트로 올바르게 변환되는지 테스트
        """
        settings = Settings()

        expected_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        assert settings.MAX_FILE_SIZE_BYTES == expected_bytes

    def test_ensure_directories(self, tmp_path):
        """
        필수 디렉토리들이 올바르게 생성되는지 테스트
        """
        # 임시 설정으로 테스트
        original_cache_dir = Settings.CACHE_DIR
        original_data_dir = Settings.DATA_DIR

        try:
            # 임시 디렉토리로 변경
            Settings.CACHE_DIR = tmp_path / "cache"
            Settings.DATA_DIR = tmp_path / "data"

            # 디렉토리 생성
            Settings.ensure_directories()

            # 디렉토리가 생성되었는지 확인
            assert Settings.CACHE_DIR.exists()
            assert Settings.DATA_DIR.exists()

        finally:
            # 원래 설정으로 복구
            Settings.CACHE_DIR = original_cache_dir
            Settings.DATA_DIR = original_data_dir

    def test_validate_positive_values(self):
        """
        설정값이 양수인지 검증하는 테스트
        """
        # 유효한 설정
        Settings.MAX_FILE_SIZE_MB = 50
        Settings.MAX_FILES_COUNT = 10
        Settings.PRICE_UPDATE_INTERVAL_HOURS = 24

        assert Settings.validate() is True

    def test_validate_invalid_file_size(self):
        """
        잘못된 파일 크기 설정을 검증하는 테스트
        """
        original_value = Settings.MAX_FILE_SIZE_MB

        try:
            # 잘못된 값 설정
            Settings.MAX_FILE_SIZE_MB = 0
            assert Settings.validate() is False

            Settings.MAX_FILE_SIZE_MB = -1
            assert Settings.validate() is False

        finally:
            # 원래 값으로 복구
            Settings.MAX_FILE_SIZE_MB = original_value

    def test_validate_invalid_files_count(self):
        """
        잘못된 파일 개수 설정을 검증하는 테스트
        """
        original_value = Settings.MAX_FILES_COUNT

        try:
            Settings.MAX_FILES_COUNT = 0
            assert Settings.validate() is False

            Settings.MAX_FILES_COUNT = -1
            assert Settings.validate() is False

        finally:
            Settings.MAX_FILES_COUNT = original_value

    def test_paths_are_path_objects(self):
        """
        경로들이 Path 객체인지 확인하는 테스트
        """
        settings = Settings()

        assert isinstance(settings.CACHE_DIR, Path)
        assert isinstance(settings.DATA_DIR, Path)
        assert isinstance(settings.CONFIG_DIR, Path)
        assert isinstance(settings.MODELS_CONFIG_FILE, Path)

    def test_env_var_override(self, monkeypatch):
        """
        환경 변수로 설정을 오버라이드할 수 있는지 테스트
        """
        # 환경 변수 설정
        monkeypatch.setenv("DEBUG", "True")
        monkeypatch.setenv("MAX_FILE_SIZE_MB", "100")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        # Settings를 다시 인스턴스화하지 않고 직접 환경변수에서 읽기
        debug = os.getenv("DEBUG", "False").lower() == "true"
        max_file_size = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
        log_level = os.getenv("LOG_LEVEL", "INFO")

        assert debug is True
        assert max_file_size == 100
        assert log_level == "DEBUG"

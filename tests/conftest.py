"""
pytest 설정 및 공통 픽스처 정의

모든 테스트에서 사용할 수 있는 공통 설정과 픽스처를 제공합니다.
"""

import os
import sys
from pathlib import Path
from typing import Generator

import pytest

# 프로젝트 루트를 Python 경로에 추가
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture(scope="session")
def project_root() -> Path:
    """
    프로젝트 루트 디렉토리 경로를 반환하는 픽스처

    Returns:
        Path: 프로젝트 루트 디렉토리 경로
    """
    return ROOT_DIR


@pytest.fixture(scope="session")
def test_data_dir(project_root: Path) -> Path:
    """
    테스트 데이터 디렉토리 경로를 반환하는 픽스처

    Returns:
        Path: 테스트 데이터 디렉토리 경로
    """
    test_dir = project_root / "tests" / "test_data"
    test_dir.mkdir(exist_ok=True)
    return test_dir


@pytest.fixture(scope="function")
def temp_test_file(test_data_dir: Path, tmp_path: Path) -> Generator[Path, None, None]:
    """
    임시 테스트 파일을 생성하고 테스트 후 삭제하는 픽스처

    Args:
        test_data_dir: 테스트 데이터 디렉토리
        tmp_path: pytest의 임시 디렉토리

    Yields:
        Path: 임시 테스트 파일 경로
    """
    temp_file = tmp_path / "test_file.txt"
    temp_file.write_text("This is a test file for LLM API Cost Calculator")

    yield temp_file

    # 테스트 후 정리 (tmp_path는 자동으로 삭제됨)
    if temp_file.exists():
        temp_file.unlink()


@pytest.fixture(scope="function")
def sample_text() -> str:
    """
    테스트용 샘플 텍스트를 반환하는 픽스처

    Returns:
        str: 테스트용 샘플 텍스트
    """
    return """
    LLM API Cost Calculator is a tool for calculating and comparing
    the costs of various LLM APIs. It supports multiple file formats
    including PDF, Excel, images, and text files.

    이것은 한국어 텍스트입니다. 다양한 언어를 지원합니다.
    """


@pytest.fixture(scope="function")
def mock_env_vars(monkeypatch) -> None:
    """
    테스트용 환경 변수를 설정하는 픽스처

    Args:
        monkeypatch: pytest의 monkeypatch 픽스처
    """
    test_env = {
        "DEBUG": "True",
        "LOG_LEVEL": "DEBUG",
        "MAX_FILE_SIZE_MB": "10",
        "MAX_FILES_COUNT": "5",
        "ENABLE_AUTO_PRICE_UPDATE": "False",
    }

    for key, value in test_env.items():
        monkeypatch.setenv(key, value)

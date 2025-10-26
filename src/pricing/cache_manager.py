"""
가격 캐시 관리자

가격 정보를 캐싱하고 자동 업데이트를 관리합니다.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from config.settings import settings


class PriceCacheManager:
    """
    가격 캐시 관리자

    가격 정보를 JSON 파일로 캐싱하고 유효성을 관리합니다.
    """

    def __init__(self, cache_file: Optional[Path] = None):
        """
        캐시 매니저 초기화

        Args:
            cache_file: 캐시 파일 경로 (None이면 기본 경로 사용)
        """
        self.cache_file = cache_file or settings.PRICE_CACHE_FILE
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

    def load_cache(self) -> Optional[dict]:
        """
        캐시 파일 로드

        Returns:
            dict: 캐시 데이터 (캐시가 없거나 유효하지 않으면 None)
        """
        if not self.cache_file.exists():
            return None

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # 캐시 유효성 검사
            if self.is_cache_valid(cache_data):
                return cache_data
            else:
                return None

        except (json.JSONDecodeError, KeyError, IOError) as e:
            print(f"⚠️ 캐시 로드 실패: {e}")
            return None

    def save_cache(self, data: dict) -> bool:
        """
        캐시 파일 저장

        Args:
            data: 저장할 데이터

        Returns:
            bool: 성공 여부
        """
        try:
            # 타임스탬프 추가
            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "data": data,
            }

            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            return True

        except IOError as e:
            print(f"❌ 캐시 저장 실패: {e}")
            return False

    def is_cache_valid(self, cache_data: dict) -> bool:
        """
        캐시가 유효한지 확인

        캐시가 설정된 시간(기본 24시간) 이내에 생성되었는지 확인합니다.

        Args:
            cache_data: 캐시 데이터

        Returns:
            bool: 유효하면 True, 아니면 False
        """
        try:
            timestamp_str = cache_data.get("timestamp")
            if not timestamp_str:
                return False

            # 타임스탬프 파싱
            cache_time = datetime.fromisoformat(timestamp_str)

            # 현재 시간
            now = datetime.now()

            # 유효 기간 (설정에서 가져오기, 기본 24시간)
            valid_hours = settings.PRICE_UPDATE_INTERVAL_HOURS
            expiry_time = cache_time + timedelta(hours=valid_hours)

            # 유효성 확인
            return now < expiry_time

        except (ValueError, TypeError) as e:
            print(f"⚠️ 캐시 유효성 검사 실패: {e}")
            return False

    def clear_cache(self) -> bool:
        """
        캐시 파일 삭제

        Returns:
            bool: 성공 여부
        """
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
            return True
        except IOError as e:
            print(f"❌ 캐시 삭제 실패: {e}")
            return False

    def get_cache_age(self) -> Optional[timedelta]:
        """
        캐시의 나이 (생성 후 경과 시간) 반환

        Returns:
            timedelta: 캐시 나이 (캐시가 없으면 None)
        """
        cache_data = self.load_cache()
        if not cache_data:
            return None

        try:
            timestamp_str = cache_data.get("timestamp")
            cache_time = datetime.fromisoformat(timestamp_str)
            return datetime.now() - cache_time
        except (ValueError, TypeError):
            return None

    def get_cache_info(self) -> dict:
        """
        캐시 정보 반환

        Returns:
            dict: 캐시 정보 (파일 크기, 생성 시간, 유효성 등)
        """
        info = {
            "exists": self.cache_file.exists(),
            "valid": False,
            "size_bytes": 0,
            "age": None,
            "timestamp": None,
        }

        if not self.cache_file.exists():
            return info

        # 파일 크기
        info["size_bytes"] = self.cache_file.stat().st_size

        # 캐시 데이터 로드
        cache_data = self.load_cache()
        if cache_data:
            info["valid"] = True
            info["timestamp"] = cache_data.get("timestamp")

            age = self.get_cache_age()
            if age:
                info["age"] = str(age)

        return info

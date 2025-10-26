"""
가격 계산 모듈에 대한 유닛 테스트

가격 계산기와 캐시 매니저의 기능이 올바르게 작동하는지 검증합니다.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.pricing.calculator import PriceCalculator, ModelPricing, CostEstimate
from src.pricing.cache_manager import PriceCacheManager


class TestPriceCalculator:
    """PriceCalculator에 대한 테스트"""

    def test_load_models(self):
        """models.yaml 파일 로드 테스트"""
        calculator = PriceCalculator()

        assert calculator.models_data is not None
        assert "providers" in calculator.models_data
        assert len(calculator.models_cache) > 0

    def test_get_model_pricing(self):
        """모델 가격 정보 조회 테스트"""
        calculator = PriceCalculator()

        # 짧은 키로 조회
        gpt4 = calculator.get_model_pricing("gpt-4")
        assert gpt4 is not None
        assert gpt4.model_id == "gpt-4"
        assert gpt4.provider == "openai"
        assert gpt4.input_price > 0
        assert gpt4.output_price > 0

        # 긴 키로 조회
        gpt4_long = calculator.get_model_pricing("openai:gpt-4")
        assert gpt4_long is not None
        assert gpt4_long.model_id == "gpt-4"

    def test_calculate_cost_input_only(self):
        """입력 토큰만 있는 비용 계산 테스트"""
        calculator = PriceCalculator()

        # GPT-4: $0.03 per 1K input tokens
        estimate = calculator.calculate_cost("gpt-4", input_tokens=1000)

        assert estimate.input_tokens == 1000
        assert estimate.output_tokens == 0
        assert estimate.input_cost == 0.03  # 1000 * 0.03 / 1000
        assert estimate.output_cost == 0.0
        assert estimate.total_cost == 0.03

    def test_calculate_cost_with_output(self):
        """입력 + 출력 토큰 비용 계산 테스트"""
        calculator = PriceCalculator()

        # GPT-4: $0.03 input, $0.06 output per 1K
        estimate = calculator.calculate_cost("gpt-4", input_tokens=1000, output_tokens=500)

        assert estimate.input_cost == 0.03
        assert estimate.output_cost == 0.03  # 500 * 0.06 / 1000
        assert estimate.total_cost == 0.06

    def test_calculate_cost_gemini_long(self):
        """Gemini 장문 가격 테스트"""
        calculator = PriceCalculator()

        # Gemini 1.5 Pro: 일반 vs 장문
        normal = calculator.calculate_cost(
            "gemini-1.5-pro", input_tokens=1000, use_long_pricing=False
        )
        long = calculator.calculate_cost(
            "gemini-1.5-pro", input_tokens=1000, use_long_pricing=True
        )

        # 장문 가격이 더 비싸야 함
        assert long.input_cost > normal.input_cost

    def test_compare_models(self):
        """여러 모델 비용 비교 테스트"""
        calculator = PriceCalculator()

        models = ["gpt-4", "gpt-4o-mini", "claude-3-haiku"]
        estimates = calculator.compare_models(models, input_tokens=1000, output_tokens=500)

        # 3개 모델 모두 결과 반환
        assert len(estimates) == 3

        # 비용 순으로 정렬되어 있어야 함
        for i in range(len(estimates) - 1):
            assert estimates[i].total_cost <= estimates[i + 1].total_cost

        # 가장 저렴한 모델 확인 (대체로 gpt-4o-mini 또는 claude-3-haiku)
        cheapest = estimates[0]
        assert cheapest.model.model_id in ["gpt-4o-mini", "claude-3-haiku"]

    def test_get_all_models(self):
        """모든 모델 정보 조회 테스트"""
        calculator = PriceCalculator()

        all_models = calculator.get_all_models()

        # 최소 20개 이상의 모델이 있어야 함
        assert len(all_models) >= 20

        # 각 모델이 ModelPricing 타입이어야 함
        for model in all_models:
            assert isinstance(model, ModelPricing)
            assert model.provider
            assert model.model_id
            assert model.input_price >= 0
            assert model.output_price >= 0

    def test_get_models_by_provider(self):
        """제공업체별 모델 조회 테스트"""
        calculator = PriceCalculator()

        # OpenAI 모델들
        openai_models = calculator.get_models_by_provider("openai")
        assert len(openai_models) > 0
        for model in openai_models:
            assert model.provider == "openai"

        # Claude 모델들
        claude_models = calculator.get_models_by_provider("anthropic")
        assert len(claude_models) > 0
        for model in claude_models:
            assert model.provider == "anthropic"

    def test_model_not_found(self):
        """존재하지 않는 모델 처리 테스트"""
        calculator = PriceCalculator()

        with pytest.raises(ValueError, match="모델을 찾을 수 없습니다"):
            calculator.calculate_cost("nonexistent-model", input_tokens=1000)

    def test_cost_estimate_to_dict(self):
        """CostEstimate to_dict 메서드 테스트"""
        calculator = PriceCalculator()

        estimate = calculator.calculate_cost("gpt-4", input_tokens=1000, output_tokens=500)
        result_dict = estimate.to_dict()

        assert "provider" in result_dict
        assert "model_id" in result_dict
        assert "model_name" in result_dict
        assert "input_tokens" in result_dict
        assert "output_tokens" in result_dict
        assert "input_cost" in result_dict
        assert "output_cost" in result_dict
        assert "total_cost" in result_dict


class TestPriceCacheManager:
    """PriceCacheManager에 대한 테스트"""

    def test_save_and_load_cache(self, tmp_path):
        """캐시 저장 및 로드 테스트"""
        cache_file = tmp_path / "test_cache.json"
        manager = PriceCacheManager(cache_file=cache_file)

        # 테스트 데이터
        test_data = {"model": "gpt-4", "price": 0.03}

        # 저장
        success = manager.save_cache(test_data)
        assert success is True
        assert cache_file.exists()

        # 로드
        loaded_data = manager.load_cache()
        assert loaded_data is not None
        assert loaded_data["data"] == test_data

    def test_cache_validity(self, tmp_path):
        """캐시 유효성 검사 테스트"""
        cache_file = tmp_path / "test_cache.json"
        manager = PriceCacheManager(cache_file=cache_file)

        # 현재 시간의 캐시 저장
        manager.save_cache({"test": "data"})

        # 캐시 로드 (유효해야 함)
        cache_data = manager.load_cache()
        assert cache_data is not None
        assert manager.is_cache_valid(cache_data) is True

    def test_expired_cache(self, tmp_path):
        """만료된 캐시 테스트"""
        cache_file = tmp_path / "test_cache.json"
        manager = PriceCacheManager(cache_file=cache_file)

        # 과거 시간의 캐시 생성
        expired_data = {
            "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
            "data": {"test": "old_data"},
        }

        with open(cache_file, "w") as f:
            json.dump(expired_data, f)

        # 유효성 검사 (만료되어야 함)
        assert manager.is_cache_valid(expired_data) is False

        # 로드 시 None 반환
        loaded = manager.load_cache()
        assert loaded is None

    def test_clear_cache(self, tmp_path):
        """캐시 삭제 테스트"""
        cache_file = tmp_path / "test_cache.json"
        manager = PriceCacheManager(cache_file=cache_file)

        # 캐시 저장
        manager.save_cache({"test": "data"})
        assert cache_file.exists()

        # 캐시 삭제
        success = manager.clear_cache()
        assert success is True
        assert not cache_file.exists()

    def test_get_cache_info(self, tmp_path):
        """캐시 정보 조회 테스트"""
        cache_file = tmp_path / "test_cache.json"
        manager = PriceCacheManager(cache_file=cache_file)

        # 캐시 없을 때
        info = manager.get_cache_info()
        assert info["exists"] is False
        assert info["valid"] is False

        # 캐시 저장 후
        manager.save_cache({"test": "data"})
        info = manager.get_cache_info()
        assert info["exists"] is True
        assert info["valid"] is True
        assert info["size_bytes"] > 0
        assert info["timestamp"] is not None

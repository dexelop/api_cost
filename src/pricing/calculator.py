"""
가격 계산기

토큰 수를 기반으로 LLM API 비용을 계산합니다.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from config.settings import settings


@dataclass
class ModelPricing:
    """
    모델 가격 정보를 담는 데이터 클래스

    Attributes:
        provider: 제공업체 (예: 'openai', 'anthropic')
        model_id: 모델 ID (예: 'gpt-4', 'claude-3-opus')
        model_name: 모델 표시 이름
        input_price: 1000토큰당 입력 비용 (USD)
        output_price: 1000토큰당 출력 비용 (USD)
        context_window: 최대 컨텍스트 윈도우
        vision_capable: 비전 기능 지원 여부
        online_search: 온라인 검색 기능 지원 여부
        input_price_long: 장문 입력 비용 (Gemini용, 선택)
        output_price_long: 장문 출력 비용 (Gemini용, 선택)
    """

    provider: str
    model_id: str
    model_name: str
    input_price: float
    output_price: float
    context_window: int
    vision_capable: bool = False
    online_search: bool = False
    input_price_long: Optional[float] = None
    output_price_long: Optional[float] = None


@dataclass
class CostEstimate:
    """
    비용 추정 결과를 담는 데이터 클래스

    Attributes:
        model: 모델 가격 정보
        input_tokens: 입력 토큰 수
        output_tokens: 출력 토큰 수
        input_cost: 입력 비용 (USD)
        output_cost: 출력 비용 (USD)
        total_cost: 총 비용 (USD)
    """

    model: ModelPricing
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float

    @property
    def total_cost(self) -> float:
        """총 비용 반환"""
        return self.input_cost + self.output_cost

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "provider": self.model.provider,
            "model_id": self.model.model_id,
            "model_name": self.model.model_name,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "input_cost": round(self.input_cost, 6),
            "output_cost": round(self.output_cost, 6),
            "total_cost": round(self.total_cost, 6),
        }


class PriceCalculator:
    """
    가격 계산기

    models.yaml 파일을 로드하여 모델별 가격 정보를 관리하고 비용을 계산합니다.
    """

    def __init__(self, models_file: Optional[Path] = None):
        """
        가격 계산기 초기화

        Args:
            models_file: models.yaml 파일 경로 (None이면 기본 경로 사용)
        """
        self.models_file = models_file or settings.MODELS_CONFIG_FILE
        self.models_data = self._load_models()
        self.models_cache = self._build_models_cache()

    def _load_models(self) -> dict:
        """
        models.yaml 파일 로드

        Returns:
            dict: 모델 데이터

        Raises:
            FileNotFoundError: 파일이 없는 경우
            yaml.YAMLError: YAML 파싱 오류
        """
        if not self.models_file.exists():
            raise FileNotFoundError(f"모델 설정 파일을 찾을 수 없습니다: {self.models_file}")

        with open(self.models_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return data

    def _build_models_cache(self) -> dict[str, ModelPricing]:
        """
        모델 캐시 구축

        provider:model_id 형식의 키로 빠른 조회가 가능한 딕셔너리를 생성합니다.

        Returns:
            dict: 모델 ID를 키로 하는 ModelPricing 딕셔너리
        """
        cache = {}

        providers = self.models_data.get("providers", {})
        for provider_id, provider_data in providers.items():
            models = provider_data.get("models", {})

            for model_id, model_data in models.items():
                # ModelPricing 객체 생성
                pricing = ModelPricing(
                    provider=provider_id,
                    model_id=model_id,
                    model_name=model_data.get("name", model_id),
                    input_price=model_data.get("input_price", 0.0),
                    output_price=model_data.get("output_price", 0.0),
                    context_window=model_data.get("context_window", 0),
                    vision_capable=model_data.get("vision_capable", False),
                    online_search=model_data.get("online_search", False),
                    input_price_long=model_data.get("input_price_long"),
                    output_price_long=model_data.get("output_price_long"),
                )

                # 캐시에 저장 (여러 키로 접근 가능)
                cache[f"{provider_id}:{model_id}"] = pricing
                cache[model_id] = pricing  # 짧은 키도 지원

        return cache

    def get_model_pricing(self, model_id: str) -> Optional[ModelPricing]:
        """
        모델 가격 정보 조회

        Args:
            model_id: 모델 ID (예: 'gpt-4', 'openai:gpt-4')

        Returns:
            ModelPricing: 모델 가격 정보 (없으면 None)
        """
        return self.models_cache.get(model_id)

    def calculate_cost(
        self,
        model_id: str,
        input_tokens: int,
        output_tokens: int = 0,
        use_long_pricing: bool = False,
    ) -> CostEstimate:
        """
        비용 계산

        Args:
            model_id: 모델 ID
            input_tokens: 입력 토큰 수
            output_tokens: 출력 토큰 수 (기본값: 0)
            use_long_pricing: 장문 가격 사용 여부 (Gemini용)

        Returns:
            CostEstimate: 비용 추정 결과

        Raises:
            ValueError: 모델을 찾을 수 없는 경우
        """
        # 모델 가격 정보 조회
        pricing = self.get_model_pricing(model_id)
        if not pricing:
            raise ValueError(f"모델을 찾을 수 없습니다: {model_id}")

        # 입력/출력 가격 결정
        if use_long_pricing and pricing.input_price_long:
            input_price = pricing.input_price_long
            output_price = pricing.output_price_long or pricing.output_price
        else:
            input_price = pricing.input_price
            output_price = pricing.output_price

        # 비용 계산 (1000토큰당 가격)
        input_cost = (input_tokens / 1000) * input_price
        output_cost = (output_tokens / 1000) * output_price

        return CostEstimate(
            model=pricing,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
        )

    def compare_models(
        self, model_ids: list[str], input_tokens: int, output_tokens: int = 0
    ) -> list[CostEstimate]:
        """
        여러 모델의 비용 비교

        Args:
            model_ids: 비교할 모델 ID 리스트
            input_tokens: 입력 토큰 수
            output_tokens: 출력 토큰 수

        Returns:
            list[CostEstimate]: 비용 추정 결과 리스트 (비용 순 정렬)
        """
        estimates = []

        for model_id in model_ids:
            try:
                estimate = self.calculate_cost(model_id, input_tokens, output_tokens)
                estimates.append(estimate)
            except ValueError:
                # 모델을 찾을 수 없으면 건너뛰기
                continue

        # 총 비용 기준으로 정렬
        estimates.sort(key=lambda x: x.total_cost)

        return estimates

    def get_all_models(self) -> list[ModelPricing]:
        """
        모든 모델 정보 반환

        Returns:
            list[ModelPricing]: 모든 모델의 가격 정보 리스트
        """
        # 중복 제거 (짧은 키만 사용)
        unique_models = {}
        for key, pricing in self.models_cache.items():
            if ":" not in key:  # 짧은 키만 선택
                unique_models[key] = pricing

        return list(unique_models.values())

    def get_models_by_provider(self, provider: str) -> list[ModelPricing]:
        """
        특정 제공업체의 모델만 반환

        Args:
            provider: 제공업체 ID (예: 'openai', 'anthropic')

        Returns:
            list[ModelPricing]: 해당 제공업체의 모델 리스트
        """
        return [m for m in self.get_all_models() if m.provider == provider]

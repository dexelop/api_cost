"""
모델 선택 UI 컴포넌트

사용자가 비교할 LLM 모델들을 선택하는 UI를 제공합니다.
"""

from typing import List

import streamlit as st

from src.pricing.calculator import PriceCalculator


def render_model_selector() -> List[str]:
    """
    모델 선택 UI 렌더링

    Returns:
        List[str]: 선택된 모델 ID 리스트
    """
    calculator = PriceCalculator()

    # 제공업체별로 모델 그룹화
    providers = {
        "openai": {"name": "🤖 OpenAI", "models": []},
        "anthropic": {"name": "🧠 Anthropic", "models": []},
        "google": {"name": "🔍 Google", "models": []},
        "perplexity": {"name": "🔎 Perplexity", "models": []},
        "mistral": {"name": "🌬️ Mistral AI", "models": []},
        "cohere": {"name": "💬 Cohere", "models": []},
    }

    # 모델 데이터 로드 및 그룹화
    all_models = calculator.get_all_models()
    for model in all_models:
        if model.provider in providers:
            providers[model.provider]["models"].append(model)

    # 선택된 모델 추적
    selected_models = []

    # 제공업체별로 UI 렌더링
    for provider_id, provider_data in providers.items():
        if not provider_data["models"]:
            continue

        with st.expander(provider_data["name"], expanded=False):
            for model in provider_data["models"]:
                # 기본 선택 여부 확인
                default_selected = model.model_id in st.session_state.get(
                    "selected_models", []
                )

                # 체크박스로 모델 선택
                is_selected = st.checkbox(
                    f"**{model.model_name}**",
                    value=default_selected,
                    key=f"model_{provider_id}_{model.model_id}",
                )

                if is_selected:
                    selected_models.append(model.model_id)

                # 모델 정보 표시
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(
                        f"💰 입력: ${model.input_price:.4f}/1K | "
                        f"출력: ${model.output_price:.4f}/1K"
                    )
                with col2:
                    st.caption(f"📊 Context: {model.context_window:,} tokens")

                # 추가 기능 표시
                features = []
                if model.vision_capable:
                    features.append("👁️ Vision")
                if model.online_search:
                    features.append("🌐 Search")
                if model.input_price_long:
                    features.append("📄 Long Context")

                if features:
                    st.caption(" · ".join(features))

                st.divider()

    # 선택된 모델이 없으면 경고
    if not selected_models:
        st.warning("⚠️ 최소 1개 이상의 모델을 선택해주세요.")
        # 기본 모델 반환
        return st.session_state.get(
            "selected_models", ["gpt-4o", "claude-3.5-sonnet", "gemini-1.5-pro"]
        )

    return selected_models

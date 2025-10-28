"""
JSON 내보내기 모듈

비용 추정 결과를 JSON 파일로 내보냅니다.
"""

import json
from typing import List
from datetime import datetime

from api_cost_modules.processors.base import ProcessedFile
from api_cost_modules.pricing.calculator import CostEstimate
from api_cost_modules.tokenizers.file_tokenizer import FileTokenizer


class JSONExporter:
    """
    JSON 내보내기 클래스

    비용 추정 결과를 JSON 형식으로 변환합니다.
    """

    def __init__(self):
        """JSON 내보내기 초기화"""
        self.tokenizer = FileTokenizer()

    def export_json(
        self,
        processed_files: List[ProcessedFile],
        estimates: List[CostEstimate],
        output_ratio: float,
    ) -> str:
        """
        전체 데이터를 JSON으로 변환

        Args:
            processed_files: 처리된 파일 리스트
            estimates: 비용 추정 결과 리스트
            output_ratio: 출력 토큰 비율

        Returns:
            str: JSON 문자열
        """
        # 파일 정보
        files_data = []
        total_tokens = 0

        for pfile in processed_files:
            token_count = self.tokenizer.count_tokens_from_processed_file(pfile)
            total_tokens += token_count.token_count

            file_info = {
                "file_name": pfile.metadata.get("file_name", "Unknown"),
                "file_type": pfile.file_type,
                "file_size_mb": pfile.metadata.get("file_size_mb", 0),
                "token_count": token_count.token_count,
                "character_count": len(pfile.content),
            }

            # 이미지 파일이면 토큰 정보 추가
            if pfile.file_type == "image":
                file_info["image_tokens"] = {
                    "claude": token_count.metadata.get("claude_tokens", 0),
                    "gpt4v": token_count.metadata.get("gpt4v_tokens", 0),
                    "gemini": token_count.metadata.get("gemini_tokens", 0),
                }

            files_data.append(file_info)

        # 토큰 요약
        estimated_output = int(total_tokens * output_ratio)
        tokens_summary = {
            "total_input_tokens": total_tokens,
            "estimated_output_tokens": estimated_output,
            "output_ratio": output_ratio,
            "total_tokens": total_tokens + estimated_output,
        }

        # 비용 정보
        costs_data = []
        for est in estimates:
            cost_info = {
                "provider": est.model.provider,
                "model_name": est.model.model_name,
                "model_id": est.model.model_id,
                "pricing": {
                    "input_price_per_1k": est.model.input_price,
                    "output_price_per_1k": est.model.output_price,
                },
                "tokens": {
                    "input": est.input_tokens,
                    "output": est.output_tokens,
                },
                "costs": {
                    "input": round(est.input_cost, 6),
                    "output": round(est.output_cost, 6),
                    "total": round(est.total_cost, 6),
                },
                "model_info": {
                    "context_window": est.model.context_window,
                    "vision_capable": est.model.vision_capable,
                    "online_search": est.model.online_search,
                },
            }
            costs_data.append(cost_info)

        # 가장 저렴한 모델
        cheapest_model = None
        if estimates:
            cheapest = estimates[-1]  # 내림차순 정렬이므로 마지막이 가장 저렴
            cheapest_model = {
                "model_name": cheapest.model.model_name,
                "provider": cheapest.model.provider,
                "total_cost": round(cheapest.total_cost, 6),
            }

        # 전체 데이터 구조
        result = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tool": "LLM API Cost Calculator",
                "version": "1.0",
            },
            "files": {
                "count": len(processed_files),
                "items": files_data,
            },
            "tokens": tokens_summary,
            "costs": {
                "models_compared": len(estimates),
                "cheapest_model": cheapest_model,
                "all_models": costs_data,
            },
        }

        # Pretty print JSON
        return json.dumps(result, indent=2, ensure_ascii=False)

    def to_bytes(self, json_string: str) -> bytes:
        """
        JSON 문자열을 바이트로 변환

        Args:
            json_string: JSON 문자열

        Returns:
            bytes: UTF-8 바이트
        """
        return json_string.encode("utf-8")

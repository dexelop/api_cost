"""
CSV 내보내기 모듈

비용 추정 결과를 CSV 파일로 내보냅니다.
"""

import io
from typing import List
from datetime import datetime

import pandas as pd

from src.processors.base import ProcessedFile
from src.pricing.calculator import CostEstimate
from src.tokenizers.file_tokenizer import FileTokenizer


class CSVExporter:
    """
    CSV 내보내기 클래스

    비용 추정 결과를 CSV 형식으로 변환합니다.
    """

    def __init__(self):
        """CSV 내보내기 초기화"""
        self.tokenizer = FileTokenizer()

    def export_file_tokens(self, processed_files: List[ProcessedFile]) -> str:
        """
        파일별 토큰 수를 CSV로 변환

        Args:
            processed_files: 처리된 파일 리스트

        Returns:
            str: CSV 문자열
        """
        data = []

        for pfile in processed_files:
            token_count = self.tokenizer.count_tokens_from_processed_file(pfile)

            row = {
                "파일명": pfile.metadata.get("file_name", "Unknown"),
                "파일 타입": pfile.file_type,
                "파일 크기 (MB)": pfile.metadata.get("file_size_mb", 0),
                "토큰 수": token_count.token_count,
                "문자 수": len(pfile.content),
            }

            # 이미지 파일이면 이미지 토큰 정보 추가
            if pfile.file_type == "image":
                row["이미지 토큰 (Claude)"] = token_count.metadata.get("claude_tokens", 0)
                row["이미지 토큰 (GPT-4V)"] = token_count.metadata.get("gpt4v_tokens", 0)
                row["이미지 토큰 (Gemini)"] = token_count.metadata.get("gemini_tokens", 0)

            data.append(row)

        df = pd.DataFrame(data)
        return df.to_csv(index=False, encoding="utf-8-sig")

    def export_cost_estimates(
        self, estimates: List[CostEstimate], output_ratio: float
    ) -> str:
        """
        모델별 비용 추정을 CSV로 변환

        Args:
            estimates: 비용 추정 결과 리스트
            output_ratio: 출력 토큰 비율

        Returns:
            str: CSV 문자열
        """
        data = []

        for est in estimates:
            data.append(
                {
                    "제공업체": est.model.provider.upper(),
                    "모델명": est.model.model_name,
                    "모델 ID": est.model.model_id,
                    "입력 토큰": est.input_tokens,
                    "출력 토큰": est.output_tokens,
                    "출력 토큰 비율": f"{output_ratio:.1f}",
                    "입력 가격 ($/1K)": f"{est.model.input_price:.4f}",
                    "출력 가격 ($/1K)": f"{est.model.output_price:.4f}",
                    "입력 비용 ($)": f"{est.input_cost:.6f}",
                    "출력 비용 ($)": f"{est.output_cost:.6f}",
                    "총 비용 ($)": f"{est.total_cost:.6f}",
                    "Context 윈도우": est.model.context_window,
                    "Vision 지원": "Yes" if est.model.vision_capable else "No",
                    "검색 지원": "Yes" if est.model.online_search else "No",
                }
            )

        df = pd.DataFrame(data)
        return df.to_csv(index=False, encoding="utf-8-sig")

    def export_combined(
        self,
        processed_files: List[ProcessedFile],
        estimates: List[CostEstimate],
        output_ratio: float,
    ) -> str:
        """
        파일 정보 + 비용 추정을 하나의 CSV로 통합

        Args:
            processed_files: 처리된 파일 리스트
            estimates: 비용 추정 결과 리스트
            output_ratio: 출력 토큰 비율

        Returns:
            str: CSV 문자열
        """
        # 파일 정보 섹션
        file_data = []
        total_tokens = 0

        for pfile in processed_files:
            token_count = self.tokenizer.count_tokens_from_processed_file(pfile)
            total_tokens += token_count.token_count

            file_data.append(
                {
                    "구분": "파일",
                    "항목": pfile.metadata.get("file_name", "Unknown"),
                    "값": f"{token_count.token_count:,} tokens",
                    "상세": f"{pfile.file_type} | {pfile.metadata.get('file_size_mb', 0):.2f} MB",
                }
            )

        # 총 토큰 요약
        estimated_output = int(total_tokens * output_ratio)
        file_data.append(
            {
                "구분": "총계",
                "항목": "총 입력 토큰",
                "값": f"{total_tokens:,}",
                "상세": "",
            }
        )
        file_data.append(
            {
                "구분": "총계",
                "항목": "예상 출력 토큰",
                "값": f"{estimated_output:,}",
                "상세": f"비율: {output_ratio:.1f}",
            }
        )
        file_data.append(
            {
                "구분": "총계",
                "항목": "총 토큰",
                "값": f"{total_tokens + estimated_output:,}",
                "상세": "",
            }
        )

        # 구분선
        file_data.append({"구분": "", "항목": "", "값": "", "상세": ""})

        # 비용 추정 섹션
        for est in estimates:
            file_data.append(
                {
                    "구분": "비용",
                    "항목": est.model.model_name,
                    "값": f"${est.total_cost:.6f}",
                    "상세": f"입력: ${est.input_cost:.6f} | 출력: ${est.output_cost:.6f}",
                }
            )

        # 메타데이터
        file_data.append({"구분": "", "항목": "", "값": "", "상세": ""})
        file_data.append(
            {
                "구분": "메타",
                "항목": "생성 시간",
                "값": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "상세": "LLM API Cost Calculator",
            }
        )

        df = pd.DataFrame(file_data)
        return df.to_csv(index=False, encoding="utf-8-sig")

    def to_bytes(self, csv_string: str) -> bytes:
        """
        CSV 문자열을 바이트로 변환

        Args:
            csv_string: CSV 문자열

        Returns:
            bytes: UTF-8 BOM 포함 바이트
        """
        # UTF-8 BOM 추가 (Excel에서 한글 깨짐 방지)
        return csv_string.encode("utf-8-sig")

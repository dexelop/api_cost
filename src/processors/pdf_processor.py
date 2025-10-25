"""
PDF 파일 프로세서

PDF 파일에서 텍스트를 추출하여 처리합니다.
"""

from pathlib import Path
from typing import List

from PyPDF2 import PdfReader

from .base import BaseFileProcessor, ProcessedFile


class PDFFileProcessor(BaseFileProcessor):
    """
    PDF 파일 프로세서

    PyPDF2를 사용하여 PDF 파일에서 텍스트를 추출합니다.
    """

    def __init__(self):
        """PDF 프로세서 초기화"""
        super().__init__()
        self.supported_extensions = [".pdf"]

    def extract_text_from_page(self, page) -> str:
        """
        PDF의 단일 페이지에서 텍스트 추출

        Args:
            page: PyPDF2 Page 객체

        Returns:
            str: 추출된 텍스트
        """
        try:
            text = page.extract_text()
            return text if text else ""
        except Exception as e:
            # 특정 페이지에서 텍스트 추출 실패 시 빈 문자열 반환
            return f"[페이지 텍스트 추출 실패: {str(e)}]"

    def extract_all_text(self, pdf_reader: PdfReader) -> tuple[str, List[str]]:
        """
        PDF의 모든 페이지에서 텍스트 추출

        Args:
            pdf_reader: PyPDF2 PdfReader 객체

        Returns:
            tuple: (전체 텍스트, 페이지별 텍스트 리스트)
        """
        all_text = []
        pages_text = []

        # 각 페이지에서 텍스트 추출
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = self.extract_text_from_page(page)
            pages_text.append(page_text)

            # 페이지 구분자와 함께 전체 텍스트에 추가
            all_text.append(f"--- Page {page_num + 1} ---\n{page_text}\n")

        # 리스트를 하나의 문자열로 합치기
        combined_text = "\n".join(all_text)

        return combined_text, pages_text

    def get_pdf_metadata(self, pdf_reader: PdfReader, file_path: Path) -> dict:
        """
        PDF 파일의 메타데이터 추출

        Args:
            pdf_reader: PyPDF2 PdfReader 객체
            file_path: PDF 파일 경로

        Returns:
            dict: PDF 메타데이터
        """
        # 기본 파일 메타데이터 가져오기
        metadata = self.get_file_metadata(file_path)

        # PDF 전용 메타데이터 추가
        pdf_metadata = {
            "page_count": len(pdf_reader.pages),
            "is_encrypted": pdf_reader.is_encrypted,
        }

        # PDF 문서 정보 추가 (있는 경우)
        if pdf_reader.metadata:
            doc_info = pdf_reader.metadata
            pdf_metadata.update(
                {
                    "title": doc_info.get("/Title", ""),
                    "author": doc_info.get("/Author", ""),
                    "subject": doc_info.get("/Subject", ""),
                    "creator": doc_info.get("/Creator", ""),
                    "producer": doc_info.get("/Producer", ""),
                }
            )

        metadata.update(pdf_metadata)
        return metadata

    def process(self, file_path: Path) -> ProcessedFile:
        """
        PDF 파일을 처리하여 텍스트 추출

        Args:
            file_path: 처리할 PDF 파일 경로

        Returns:
            ProcessedFile: 처리된 파일 정보

        Raises:
            FileNotFoundError: 파일이 존재하지 않는 경우
            ValueError: 지원하지 않는 파일 형식인 경우
        """
        try:
            # 파일 검증
            self.validate_file(file_path)

            # PDF 리더 생성
            pdf_reader = PdfReader(str(file_path))

            # 암호화된 PDF 처리 (비밀번호 없이 시도)
            if pdf_reader.is_encrypted:
                try:
                    # 빈 비밀번호로 해독 시도
                    pdf_reader.decrypt("")
                except Exception:
                    raise ValueError("암호화된 PDF 파일입니다. 비밀번호가 필요합니다.")

            # 모든 페이지에서 텍스트 추출
            all_text, pages_text = self.extract_all_text(pdf_reader)

            # 메타데이터 추출
            metadata = self.get_pdf_metadata(pdf_reader, file_path)

            # 텍스트 관련 메타데이터 추가
            metadata.update(
                {
                    "character_count": len(all_text),
                    "word_count": len(all_text.split()),
                    "average_chars_per_page": (
                        len(all_text) / metadata["page_count"]
                        if metadata["page_count"] > 0
                        else 0
                    ),
                }
            )

            return ProcessedFile(
                file_path=file_path,
                file_type="pdf",
                content=all_text,
                metadata=metadata,
                error=None,
            )

        except Exception as e:
            # 에러 발생 시 에러 정보와 함께 반환
            return ProcessedFile(
                file_path=file_path,
                file_type="pdf",
                content="",
                metadata=self.get_file_metadata(file_path)
                if file_path.exists()
                else {},
                error=str(e),
            )
